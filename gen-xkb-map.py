
import unicodedata as unidata
import re

# key normal shift alt alt-shift

c_above = {
'grave': 'U0300',
'acute': 'U0301',
'caret': 'U0302',
'tilde': 'U0303',
'macron': 'U0304',
'overline': 'U0305',
'breve': 'U0306',
'dot': 'U0307',
'umlaut': 'U0308',
'hook': 'U0309',
'ring': 'U030A',
'caron': 'U030C',
}
c_below = {
'cedilla': 'U0327',
'underline': 'U0332',
'dot': 'U0323',
}
c_around = {
'circle': 'U20DD',
'square': 'U20DE',
'forbidden': 'U20E0',
}
c_over = {
'strike': 'U0336',
'ssolidus': 'U0337',
}


# greek       η ικ μνξο ρ τυφχψ
# greek ΑΒΓΔΕΖΗ ΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨ
# ∊∋∌∍∖√∣∤⊄⊅⊉⊊⊋⊓⊔⊖⊘⇐⇒ℍℂℙ
# ☽☾☿♁♃♄♅♆♇
#
# ⇐⇑⇓⇔ ↔
# —‖†‡≅•‣…‧⁋≃≄
# ¦'¥'×÷
# ⊢⊣⊤⊥

keymap = [
[ # ~1234567890+'
['<TLDE>', '‘', '’',              '“',                '”',                  '±',      '÷'],
['<AE01>', '1', '§',              '♀',                '☹',                  0,        0,         '♒',  0],
['<AE02>', '2', '¶',              '♂',                '☺',                  0,        0,         '♓'],
['<AE03>', '3', '£',              c_around['circle'], 0,                    0,        0,         '♈'],
['<AE04>', '4', 'µ',              c_around['square'], '😘',                 0,        0,         '♉'],
['<AE05>', '5', '™',              '♩',                '♬',                  0,        0,         '♊'],
['<AE06>', '6', 0,                '♪',                '♫',                  0,        0,         '♋'],
['<AE07>', '7', '∝',              '≺',                '≼',                  0,        0,         '♌'],
['<AE08>', '8', '∞',              '⊏',                '⊑',                  '⊂',      '⊆',       '♍'],
['<AE09>', '9', c_over['strike'], '⊐',                '⊒',                  '⊃',      '⊇',       '♎'],
['<AE10>', '0', '∅',              '≻',                '≽',                  0,        0,         '♏'],
['<AE11>', '∑', '∏',              '✓',                0,                    0,        0,         '♑'],
['<AE12>', '©', '®',              '✗',                '∐',                  '´',      0,         0],
],         [ # qwertyuiopå"
['<AD01>', 'q', 'Q',              '?',                '¿',                  '∎',      'ℚ'],
['<AD02>', 'w', 'W',              '!',                '¡'],
['<AD03>', 'f', 'F',              '$',                '¢',                  '∫',      '𝔽'],
['<AD04>', 'p', 'P',              '+',                '⊕',                  0,        'ℙ',       'π'],
['<AD05>', 'g', 'G',              '&',                0,                    '∇',     '∆',        'γ'],
['<AD06>', 'j', 'J',              0],
['<AD07>', 'l', 'L',              '%',                c_over['ssolidus'],   0,        0,         'λ'],
['<AD08>', 'u', 'U',              '_',                c_below['underline'], '≈',      '≉'],
['<AD09>', 'y', 'Y',              '=',                '≠',                  '<HOME>', '<HOME>'],
['<AD10>', 'ø', 'Ø',              c_above['umlaut'],  c_above['caron'],     '<UP>',   '<UP>',    '↑'],
['<AD11>', 'å', 'Å',              c_above['ring'],    '°',                  '<END>',  '<END>'],
['<AD12>', 'æ', 'Æ',              c_above['macron'],  c_above['overline'],  '<PGUP>', '<PGUP>'],
],         [ # asdfghjkløæ
['<AC01>', 'a', 'A',              '@',                0,                    '∀',      0,         'α'],
['<AC02>', 'r', 'R',              '{',                0,                    0,        'ℝ'],
['<AC03>', 's', 'S',              '[',                '⟦',                  '≅',      '≆',       'σ'],
['<AC04>', 't', 'T',              '(',                0,                    0,        0,         'θ',   'Θ'],
['<AC05>', 'd', 'D',              '<',                '≤',                  '≫',      '∂',       'δ'],
['<AC06>', 'h', 'H',              '>',                '≥',                  '≪'],
['<AC07>', 'n', 'N',              ')',                0,                    '¬',      'ℕ'],
['<AC08>', 'e', 'E',              ']',                '⟧',                  '∃',      '∄',       'ε'],
['<AC09>', 'i', 'I',              '}',                0,                    '<LEFT>', '<LEFT>',  '←'],
['<AC10>', 'o', 'O',              '~',                c_above['tilde'],     '<DOWN>', '<DOWN>',  '↓'],
['<AC11>', "'", '"',              c_above['acute'],   'ʻ',                  '<RGHT>', '<RGHT>',  '→',   '⇒'],
['<BKSL>', '`', c_above['grave'], '«',                '»',                  '<PGDN>', '<PGDN>',  '↔'],
],         [ #<zxcvbnm,.-
['<LSGT>', '/', '|',              '\\',               '‖'],
['<AB01>', 'z', 'Z',              '∈',                '∉',                  0,        'ℤ',       'ζ'],
['<AB02>', 'x', 'X',              '×',                '⊗'],
['<AB03>', 'c', 'C',              '^',                c_above['caret']],
['<AB04>', 'v', 'V',              '∧',                '∨',                  '∩',      '∪'],
['<AB05>', 'b', 'B',              '#',                0,                    0,        0,         'β'],
['<AB06>', 'k', 'K',              '≡',                0,                    0,        '𝕂'],
['<AB07>', 'm', 'M',              '*',                '∘',                  0,        0,         'ω',   'Ω'],
['<AB08>', ',', ';',              c_below['cedilla'], c_below['dot']],
['<AB09>', '.', ':',              '⋅',                '∙',                  '⊙'],
['<AB10>', '-', '—',              '…',                '⋯'],
]
]


# "«» 1a 2a 3a 4e 5a 6∞ 7⟨ 8⟦ 9⟧ 0⟩ ∑∎ aa"
# "qQ wW fF pP gG jJ lL uU yY øØ åÅ æÆ"
#"aA rR sS tT dD hH nN eE iI oO '\" _"
# "/| zZ xX cC vV bB kK mM ,; .: -…"



template = """
partial default alphanumeric_keys
xkb_symbols "basic" {{
  include "no(basic)" // Based on Norwegian layout.
  include "capslock(backspace)" // Make Caps Lock act as Backspace.

  name[Group1] = "FSH Colemak (Norwegian)";

  // Use LWIN for XMonad/i3.
  key <LWIN> {{ type="ONE_LEVEL", [Super_L] }};

  // Why doesn't MENU = RWIN work?
  // Fucking MENU key.
  alias <MENU> = <COMP>;
  alias <RWIN> = <COMP>;

  // Make AltGr select group +1 and RWIN select group +2.
  replace key <RALT> {{ type="ONE_LEVEL", [ Mode_switch, Mode_switch ] }};
  replace key <COMP> {{
    type="ONE_LEVEL",
    symbols[Group1] = [NoSymbol],
    symbols[Group2] = [NoSymbol],
    symbols[Group3] = [NoSymbol],
    symbols[Group4] = [NoSymbol],
    actions[Group1] = [ SetGroup(group=3), SetGroup(group=3) ],
    actions[Group2] = [ SetGroup(group=4), SetGroup(group=4) ]
  }};

{keys}
}};
"""

def chrToStr(k):
    if not isinstance(k, str):
        return ('NoSymbol', '---')
    if len(k) > 1:
        if re.fullmatch('U[0-9]*', k):
            return (k, unidata.name(chr(int(k[1:], 16))))
        elif re.fullmatch('<.+>', k):
            return ('NoSymbol', 'Redirect({})'.format(k))
        else:
            return (k, k)
    n = ord(k)
    if n > 0xffff:
        s = 'U{:08X}'.format(n)
    else:
        s = 'U{:04X}'.format(n)
    return (s, unidata.name(k))

def formatGroup(a, b):
    s, c = zip(chrToStr(a), chrToStr(b))
    return "[ {} ] // {}".format(
        ', '.join(s), ', '.join(c))

def isRedirect(k):
    return isinstance(k, str) and re.fullmatch('<.+>', k) is not None

def chrToRedirect(k):
    if not re.fullmatch('<.+>', k):
        return 'NoAction()'
    return 'RedirectKey(key={})'.format(k)

def chrToComment(k):
    if not isinstance(k, str):
        return '<none>'
    if len(k) == 1:
        return unidata.name(k)
    if re.fullmatch('U[0-9]*', k):
        return unidata.name(chr(int(k[1:], 16)))
    elif re.fullmatch('<.+>', k):
        return 'Redirect({})'.format(k)
    else:
        return k

def chrToXKB(k):
    if not isinstance(k, str):
        return 'NoSymbol'
    if len(k) == 1:
        n = ord(k)
        if n > 0xffff:
            return 'U{:08X}'.format(n)
        else:
            return 'U{:04X}'.format(n)
    if re.fullmatch('U[0-9]*', k):
        return k
    elif re.fullmatch('<.+>', k):
        return 'NoSymbol'
    else:
        return k


def processGroup(*keys):
    want_redirect = False
    symbols = []
    comments = []
    redirects = []
    for k in keys:
        if isRedirect(k):
            want_redirect = True
        symbols.append(chrToXKB(k))
        comments.append(chrToComment(k))
    if want_redirect:
        for k in keys:
            redirects.append(chrToRedirect(k))

    return (symbols, comments, redirects)

def formatKey(k, *keys, indent='  '):
    # Normalize to 8 keys.
    keys += (0,) * (8 - len(keys))

    lines = []
    for G in [1,2,3,4]:
        (syms, cmts, redirs) = processGroup(keys[2*G - 2], keys[2*G - 1])
        lines.append('symbols[Group{}] = [ {} ] // {}'.format(G, ', '.join(syms), ', '.join(cmts)))
        if redirs:
            lines.append('actions[Group{}] = [ {} ]'.format(G, ', '.join(redirs)))

    pre = '{}key {} {{ '.format(indent, k)
    sep = '\n{}, '.format(' ' * (len(pre) - 2))

    return pre + sep.join(lines) + '\n{}}};'.format(indent)

def formatKeymap(keymap):
    for row in keymap:
        for k in row:
            yield formatKey(*k)
        yield ''

print(template.format(keys='\n'.join(formatKeymap(keymap))))
