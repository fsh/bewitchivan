
import csv
import re
import sys
from dataclasses import dataclass


if len(sys.argv) <= 1:
  print(f"""
usage: {sys.argv[0]} [-c] [-n] [-#] [[-][.]<regex> [-][.][regex] ...]

  -c sort by character
  -n sort by name
  -# sort by code point (number)

Lists all the Unicode characters whose name is matched
by (all) the given regular expressions.

  regex : normal search (include ^ or $ to anchor it if needed).
 -regex : filters away any characters that matches this.
 .regex : match full word (essentially just adds \\b to both ends).
-.regex : guess.

Uses case insensitive matching.

""")
  sys.exit(0)


@dataclass
class Char():
  chr: str
  name: str
  cat: str
  ord: int

dia = csv.unix_dialect()
dia.delimiter = ';'
reader = csv.reader(open('UnicodeData.txt', 'r'), dia)

headers = 'Code_Point;Name;General_Category;Canonical_Combining_Class;Bidi_Class;Decomposition_Type_and_Decomposition_Mapping;Numeric_Type;Numeric_Value_for_Type_Digit;Numeric_Value_for_Type_Numeric;Bidi_Mirrored;Unicode_1_Name;ISO_Comment;Simple_Uppercase_Mapping;Simple_Lowercase_Mapping;Simple_Titlecase_Mapping'.split(';')
fields = { name.lower(): i for i, name in enumerate(headers) }

cnames = [ Char(chr(int(c, 16)), name, cat, int(c, 16))
          for (c, name, cat, *_) in reader ]
nnames = { c.name: c for c in cnames }

def grep(*regexes):
  ms = [re.compile(x, re.I) for x in regexes]
  for n, v in nnames.items():
    if all(m.search(n) for m in ms):
      yield v

left = list(nnames.keys())
sort = None

for arg in sys.argv[1:]:
  if arg == '-n':
    sort = 'name'
    continue
  if arg == '-c':
    sort = 'chr'
    continue
  if arg == '-#':
    sort = 'ord'
    continue
  invert = False
  if '>' in arg:
    l, r = arg.upper().split('>', maxsplit=1)
    ls = set((x, x.replace(l, r)) for x in left if l in x)
    ls = [(x, y) for x, y in ls if y in nnames]
    ls, rs = zip(*ls)
    left = ls + rs
  elif arg.startswith(':'):
    arg = arg[1:]
    left = [x for x in left if nnames[x].cat.startswith(arg)]
  else:
    if arg[:1] in '-!':
      invert = True
      arg = arg[1:]
    if arg[:1] in '.':
      arg = fr'\b{arg[1:]}\b'
    regex = re.compile(arg, re.I)
    left = [x for x in left if bool(regex.search(x)) ^ invert]
  if not left:
    print('no matches!')
    break

if sort is not None:
  left = sorted(left, key=lambda n: getattr(nnames[n], sort))
for k in left:
  print(nnames[k].chr, nnames[k].cat, k)


