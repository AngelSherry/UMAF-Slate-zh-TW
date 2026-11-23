"""Compile exact HII string matches, EFI narrow/wide markers and the TC glyph subset."""
import json,sys,unicodedata as U, re, hashlib
from pathlib import Path
from font import make
src=Path(__file__).resolve().parent.parent
catalog=json.loads((src/'l10n/catalog.json').read_text())
def wide(c):return U.east_asian_width(c) in ('F','W')
def marked(s):
 w=False;r=''
 for c in s:
  if c in '\n\r':r+='\ufff0' if w else '';w=False;r+=c;continue
  v=wide(c)
  if w!=v:r+=('\ufff1' if v else '\ufff0');w=v
  r+=c
 if w:r+='\ufff0'
 return r
def lit(s):
 return 'L"'+''.join('\\\\' if c=='\\' else '\\"' if c=='"' else ('\\u%04x'%ord(c) if ord(c)>126 else '\\%03o'%ord(c) if ord(c)<32 else c) for c in s)+'"'
table={k:v for k,v in catalog.items() if v!=k}
assert all(all(ord(c)<65536 for c in k+v) for k,v in table.items())
with (src/'SlateZhTable.h').open('w') as f:
 f.write('static CONST struct {CONST CHAR16 *En,*Tw;} ZhTable[]={\n')
 for k,v in sorted(table.items()):f.write('{'+lit(k)+','+lit(marked(v))+'},\n')
 f.write('};\n')
from help_edit import make as help_rules
notes=help_rules()
with (src/'SlateHelpTable.h').open('w') as f:
 f.write('static CONST struct {CONST CHAR16 *Prompt,*Original,*Note;} SlateHelp[]={\n')
 for (k,h),v in sorted(notes.items()):f.write('{'+lit(k)+','+lit(h)+','+lit(marked(v))+'},\n')
 f.write('};\n')
codes=sorted(set(ord(c) for s in ['韌體設定',*table.values(),*notes.values()] for c in s if ord(c)>127 and c not in '\ufff0\ufff1'))
make(codes,src/'SlateZhGlyphs.h',sys.argv[1])
print('entries',len(table),'glyphs',len(codes))
