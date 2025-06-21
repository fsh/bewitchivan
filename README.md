# YAML → XKB Config Generator

A utility script used to create custom XKB keyboard layouts from YAML configuration files.

I use a heavily modified Colemak layout with lots of math (∑⋅∘∇∃∄∂∫×∈…), alphabets (𝑎𝑏𝑐, 𝔸𝔹ℂ, αβγ,
ℯℰ¹²³₁₂₃…), accents (e̊ëěẹėȩẽê…) and and miscellaneous symbols (←↑⇐⇑☹✓©…). Maintaining it with some
kind of GUI layout editor was a nightmare.

## Contents

- `xkbgen.py` – Converts a YAML description of a keyboard layout into an XKB
  keymap.
- `franksh.yaml` – Sample YAML file describing a layout that
  makes use of multiple modifier layers and latch groups.
- `unigrep.py` – Small utility that greps `UnicodeData.txt` so you can search
  for characters by name when editing the YAML.
- `UnicodeData.txt` – Copy of the Unicode database used by `unigrep.py`.

## Generating a Layout

Generate an XKB keymap from a YAML specification with:

```bash
python xkbgen.py franksh.yaml > mymap.xkb
```

The resulting `mymap.xkb` file can then be loaded with `xkbcomp`:

```bash
xkbcomp mymap.xkb $DISPLAY
```

## Searching Unicode

`unigrep.py` helps find Unicode characters by name.  Provide one or more
regular expressions and it prints matching characters along with their names:

```bash
python unigrep.py greek dollar
```

Use the `-` prefix to exclude matches and `.` to match whole words.  Searches
are case-insensitive.

## License

This code does not specify a license and is provided as-is.
