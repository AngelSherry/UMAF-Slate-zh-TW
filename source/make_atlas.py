from PIL import Image, ImageFont, ImageDraw
import sys
from pathlib import Path
font=ImageFont.truetype(sys.argv[1],39)
codes=sorted(set(range(32,127))|set(range(0x2500,0x2580))|set(map(ord,'·×▸▴▾▹◂◆●○✓↵←↑→↓▲▼◄►…−•□')))
with Path(sys.argv[2]).open('w') as f:
 f.write('/* Generated from Noto Sans Mono; see licenses/Noto-OFL.txt. */\n#define ATLAS_W 27\n#define ATLAS_H 54\n')
 f.write('static CONST CHAR16 Code[] = {'+','.join(hex(v) for v in codes)+'};\n')
 f.write('static CONST UINT8 Atlas[][ATLAS_W*ATLAS_H] = {\n')
 for c in codes:
  im=Image.new('L',(27,54));dr=ImageDraw.Draw(im); dr.text((13,41),chr(c),font=font,fill=255,anchor='ms')
  a=im.tobytes(); f.write('{'+','.join(map(str,a))+'},\n')
 f.write('};\n')
