#!/usr/bin/env python
"""
YAML→XKB Keymap Generator

```bash
$ ./xkbgen.py YAML_FILE > mymap.xkb
$ xkbcomp mymap.xkb $DISPLAY
```
"""

# ─────────────────────────────────────────────────────────────────────────────
#  ↑↑↑  END OF USER‑EDITABLE AREA  ↑↑↑
# ─────────────────────────────────────────────────────────────────────────────

import sys, re, textwrap, yaml, unicodedata as ud
import logging
from typing import Any, Self, Iterator
from dataclasses import dataclass, field
import string

KEYCODE_RE = re.compile(r"^<[A-Z0-9]{2,4}>$")
KEYSPEC_RE = re.compile(r'^(?P<mods>(?:\w+\s*\+\s*)*)(?:(?P<key><[A-Z0-9+-]{2,4}>|\S)|(?P<lmod>\w+))$')
MOD_RE = re.compile(r'\w+')
INDENT = "  "  # two‑space indent in generated XKB

# ───────────────────────── helpers ─────────────────────────

def islist(x: Any) -> bool:
  return isinstance(x, (list, tuple))
def isstr(x: Any) -> bool:
  return isinstance(x, str)
def ensure_list(x: Any) -> list|tuple:
  return x if islist(x) else (x,)

logging.basicConfig(level=logging.WARNING, format="%(relativeCreated)6.1f %(levelname)s: %(message)s")
log = logging.getLogger()

@dataclass(slots=True)
class KeySym():
  keycode: str = ''
  group: int = 0
  level: int = 0
  symbol: str = ''
  action: str = ''

  @property
  def index(self):
    return (self.keycode, self.group, self.level)
  def __hash__(self):
    return hash(self.index)
  def __eq__(self, other: Self):
    return self.index == other.index
  def add_level(self, lvl: int):
    return KeySym(self.keycode, self.group, self.level + lvl, self.symbol, self.action)
  def with_keycode(self, keycode: str):
    if self.keycode:
      raise ValueError(f"can't assign keycode {keycode}: {self} already has a keycode")
    return KeySym(keycode, self.group, self.level, self.symbol, self.action)

  def __str__(self):
    return f"{self.keycode or '<unknown>'}@group{self.group+1}[{self.level+1}](sym={repr(self.symbol) or '<notset>'}, action={self.action or '<notset>'})"


class KeymapBuilder():
  def __init__(self, ROWS=None):
    self._modbit = {'none': 0}
    self._xkb_literals = [[], []] # start and end literals.
    self._groups = {'BASE': 0}
    self._keys = {}
    self._basemap = {}
    self._ROWS = ROWS

  def get_group(self, name: str, default=None):
    if (grp := self._groups.get(name)) is None:
      if default is None:
        raise ValueError(f"unknown group {name!r}")
      return default
    return grp

  def get_level(self, modstr: str):
    lvl, key = self.split_shortcut(modstr)
    if key:
      raise ValueError(f"can't specify a key here ({modstr!r})")
    return lvl

  def split_shortcut(self, keyspec: str) -> tuple[int, str|None]:
    if not (m := KEYSPEC_RE.match(keyspec.strip())):
      raise ValueError(f"invalid mod/key spec: {keyspec!r}")
    modstr = m['mods'] or ''
    if m['key'] is None:
      modstr += m['lmod']
    key = m['key'] or ''
    lvl = 0
    for m in MOD_RE.findall(modstr.lower()):
      if m not in self._modbit:
        raise ValueError(f"no modifier named {m!r}")
      lvl += self._modbit[m]
    return (lvl, key)

  def add_mod(self, name, data):
    name = name.lower()
    if not MOD_RE.fullmatch(name):
      raise ValueError(f"{name!r} has to be an identifier")
    mod = data.get('mod')
    match mod:
      case 'Shift':
        self._modbit[name] = 1<<0
      case 'LevelThree':
        self._modbit[name] = 1<<1
      case 'LevelFive':
        self._modbit[name] = 1<<2

    kcs = ensure_list(data['keycodes'])
    syms = ensure_list(data['keysyms'])
    if len(syms) == 1:
      syms = syms * len(kcs)

    action = '' if mod is None else f'SetMods(modifiers={mod}, clearLocks)'
    for kc, sym in zip(kcs, syms):
      modkey = KeySym(kc, 0, 0, symbol=sym, action=action)
      log.info(f'Setting key {modkey} to modifier {name!r} ({mod}).')
      self.make_canonical(modkey)

    if x11mod := data.get('x11'):
      self._xkb_literals[-1].append(f'modifier_map {x11mod} {{ {", ".join(kcs)} }};\n')
  
  def add_latch(self, name, keystr):
    lvl, kc = self.split_shortcut(keystr)
    if not kc or not KEYCODE_RE.match(kc):
      raise ValueError(f"latch group {name!r} is missing a XKB key code")
    grpnr = self._groups[name] = len(self._groups)
    latch = KeySym(kc, 0, lvl, symbol='', action=f'LatchGroup(group={grpnr+1})')
    log.info(f'Setting latch key {latch} for accessing group {name!r}.')
    self.make_canonical(latch)

  def make_canonical(self, keysym: KeySym):
    if keysym.index not in self._keys:
      self._keys[keysym.index] = keysym
      return keysym
    extant = self._keys[keysym.index]
    if extant.symbol and extant.symbol != keysym.symbol:
      log.warning(f"Replacing symbol for {extant} with {keysym.symbol!r}.")
    if extant.action and extant.action != keysym.action:
      log.warning(f"Replacing action for {extant} with {keysym.action!r}.")
    extant.symbol = keysym.symbol
    extant.action = keysym.action
    return extant

  def set_key_symbol(self, keysym: KeySym, symbol: str):
    if not keysym.keycode:
      raise ValueError(f"attempting to assign a symbol to an unknown key {keysym}")
    if not symbol:
      log.info(f"Ignoring empty symbol for {keysym}.")
      return
    if not KEYCODE_RE.match(keysym.keycode):
      if keysym.keycode not in self._basemap:
        raise ValueError(f"can't interpret inderect bind to {keysym.keycode} because it wasn't mapped in the BASE layer")
      keysym.keycode = self._basemap[keysym.keycode]
    if len(symbol) == 2 or (len(symbol) == 3 and symbol[1] in ' /:,'):
      self.set_key_symbol(keysym, symbol[0])
      self.set_key_symbol(keysym.add_level(1), symbol[0])
      return
    # Make sure there's only one canonical KeySym for each keycode×group×level.
    try:
      keysym.symbol = ud.lookup(symbol.upper())
    except KeyError:
      keysym.symbol = symbol
    assert keysym.symbol or keysym.action, "no action or symbol set"
    keysym = self.make_canonical(keysym)
    log.info("Symbol defined: %s", keysym)
    if keysym.level == 0 and keysym.group == 0:
      self._basemap[keysym.symbol] = keysym.keycode

  def set_key_action(self, keysym: KeySym, action: str):
    if keysym.action:
      raise ValueError(f"can't set action {action!r}: {keysym} already has an action")
    # Make sure there's only one canonical KeySym for each keycode×group×level.
    keysym.action = action
    keysym = self.make_canonical(keysym)
    log.info("Action defined: %s", keysym)

  def set_key_list(self, keysym: KeySym, data: list):
    if not data:
      log.warning(f"Ignoring empty list leaf for {keysym}.")
    if keysym.keycode:
      if not all(isinstance(x, str) for x in data):
        raise ValueError(f"A list leaf with a defined keycode ({keysym}) can only contain strings.")
      for l, sym in enumerate(''.join(data)):
        self.add_spec(keysym.add_level(l), sym)
      return

    # assert not keysym.keycode:
    if self._ROWS is None:
      raise ValueError(f"can't specify a row-by-row layout when you didn't use a 'ROWS' section")
    for keys, syms in zip(self._ROWS, data):
      self.set_key_row(keysym, keys, syms)

  def set_key_row(self, keysym: KeySym, keycodes, symbols):
    if len(symbols) > len(keycodes):
      raise ValueError(f"row has too many symbols {symbols} (row only specified {len(keycodes)} keyscodes)")
    for kc, sym in zip(keycodes, symbols):
      self.set_key_symbol(keysym.with_keycode(kc), sym or '')

  def set_key_dict(self, keysym: KeySym, data: dict):
    keysym.group = self.get_group(data.get('group', ''), keysym.group)
    keysym.level += self.get_level(data.get('mods', 'none'))
    for kspec, subdata in data.items():
      if kspec in ('group', 'mods'):
        continue
      sublvl, subkey = self.split_shortcut(kspec)
      subsym = keysym.add_level(sublvl)
      if subkey:
        subsym = subsym.with_keycode(subkey)
      self.add_spec(subsym, subdata)

  def set_key_string(self, keysym: KeySym, data: str):
    if not keysym.keycode:
      if len(data) == 26:
        self.set_key_row(keysym, string.ascii_lowercase, data)
      elif len(data) == 10:
        self.set_key_row(keysym, string.digits, data)
      else:
        raise ValueError(f"only bare strings of length 26 (a-z) or 10 (0-9) are supported")
    else:
      self.set_key_symbol(keysym, data)

  def add_spec(self, keysym: KeySym, data):
    if isinstance(data, dict):
      return self.set_key_dict(keysym, data)
    elif isinstance(data, list):
      self.set_key_list(keysym, data)
    elif isinstance(data, str):
      self.set_key_string(keysym, data)
    else:
      raise ValueError(f"specification for key {keysym} has unknown type {type(data).__name__}")

  def xkb_keymap(self):
    by_keycode = {}
    for ks in self._keys.values():
      by_keycode.setdefault(ks.keycode, []).append(ks)

    prologue, epilogue = map(''.join, self._xkb_literals)
    key_str = ''.join(
      map(''.join, (xkb_key(kc, syms) for kc, syms in by_keycode.items()))
    )
    return f"""// Generated by xkbgen.py (YAML→XKB config).
xkb_keymap {{
{INDENT}xkb_keycodes  {{ include "evdev" }};
{INDENT}xkb_types     {{ include "complete" }};
{INDENT}xkb_compat    {{ include "complete" }};
{INDENT}xkb_symbols   {{
{INDENT}{INDENT}// Prologue literal.
{ textwrap.indent(prologue, INDENT*2) }
{INDENT}{INDENT}// Keys.
{ textwrap.indent(key_str, INDENT*2) }
{INDENT}{INDENT}// Epilogue literals.
{ textwrap.indent(epilogue, INDENT*2) }
{INDENT}}};
{INDENT}xkb_geometry  {{ include "pc(pc105)" }};
}};
  """


def xkb_key(keycode: str, keysyms: list[KeySym]) -> Iterator[str]:
  assert keysyms, "internal error, shouldn't get an empty list"
  lvlbits = max(x.level for x in keysyms).bit_length()
  keytype = ['ONE_LEVEL', 'TWO_LEVEL', 'FOUR_LEVEL', 'EIGHT_LEVEL'][lvlbits]
  lvls = 1 << lvlbits

  groups: dict[int, list[None|KeySym]] = dict()
  for k in keysyms:
    groups.setdefault(k.group, [None] * lvls)[k.level] = k

  yield f'replace key {keycode} {{\n' # }}
  yield f'{INDENT}type="{keytype}"'
  for g, symlist in groups.items():
    syms = [k.symbol if k else '' for k in symlist]
    if any(syms):
      yield f',\n{INDENT}symbols[Group{g+1}] = [' # ]
      yield textwrap.indent(''.join(xkb_list(map(xkb_symbol, syms))), 2*INDENT)
      yield f'\n{INDENT}]'
    acts = [k.action if k else '' for k in symlist]
    if any(acts):
      yield f',\n{INDENT}actions[Group{g+1}] = [' # ]
      yield textwrap.indent(''.join(xkb_list(map(xkb_action, acts))), 2*INDENT)
      yield f'\n{INDENT}]'
  yield f'}};\n'

def xkb_list(lst: Iterator[str]):
  comma = ' '
  for el in lst:
    yield f'\n{comma} {el}'
    comma = ','

def xkb_action(act: str):
  return 'NoAction()' if not act else act

def xkb_symbol(sym: str):
  if not sym:
    return 'NoSymbol'
  if len(sym) == 1:
    uname = '?'
    try:
      uname = ud.name(sym)
    except KeyError:
      log.warning(f"failed to look up Unicode name: {sym} (U{ord(sym):04x})")
    return f"U{ord(sym):04X} // {uname}\n"
  else:
    return sym


if len(sys.argv) != 2:
  print(f'usage: {sys.argv[0]} <YAML_FILE>')
  sys.exit(0)

with open(sys.argv[1], 'r') as fil:
  yaml_doc = yaml.safe_load(fil)

if not isinstance(yaml_doc, dict):
  raise ValueError("YAML top level must be a mapping")
if any(x not in yaml_doc for x in ['BASE', 'MODIFIERS']):
  raise ValueError(f"BASE and MODIFIERS sections are mandatory")

km = KeymapBuilder(yaml_doc.pop('ROWS', None))

for name, text in yaml_doc.pop('LITERALS', {}).items():
  km._xkb_literals[0].append(text)

log.info(f"Adding modifiers…")
for name, moddata in yaml_doc.pop('MODIFIERS').items():
  km.add_mod(name, moddata)

for name, keystr in yaml_doc.pop('GROUPS', {}).items():
  km.add_latch(name, keystr)

basedata = yaml_doc.pop('BASE')
log.info(f"Processing [BASE]…")
km.add_spec(KeySym(), basedata)

for name, spec in yaml_doc.items():
  log.info(f"Merging [%s]", name)
  km.add_spec(KeySym(), spec)

print(km.xkb_keymap())
