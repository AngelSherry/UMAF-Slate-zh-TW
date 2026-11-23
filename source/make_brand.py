from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
import sys
font=ImageFont.truetype(sys.argv[1],42);txt='Firmware settings';a,b,c,d=font.getbbox(txt);im=Image.new('L',(c-a,d-b));ImageDraw.Draw(im).text((-a,-b),txt,font=font,fill=255)
Path(sys.argv[2]).write_text('/* Open Sans SemiBold; SIL OFL, see licenses. */\n#define BRAND_W %d\n#define BRAND_H %d\nstatic CONST UINT8 Brand[] = {'%im.size+','.join(str((v+8)//17) for v in im.getdata())+'};\n')
