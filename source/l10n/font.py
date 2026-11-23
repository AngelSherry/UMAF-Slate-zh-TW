"""Compile a subset of the TC face as lossless RLE, preserving the original 8-bit coverage."""
import itertools,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
def make(codes,path,fontfile):
 font=ImageFont.truetype(fontfile,41,index=3)
 assert 'TC' in font.getname()[0]
 offsets=[]; buf=bytearray()
 for c in codes:
  im=Image.new('L',(54,54));ImageDraw.Draw(im).text((27,42),chr(c),anchor='ms',font=font,fill=255)
  raw=im.tobytes();assert any(raw) or c==0x3000,hex(c)
  offsets.append(len(buf));i=0
  while i<len(raw):
   j=i+1
   while j<min(len(raw),i+128) and raw[j]==raw[i]:j+=1
   if j-i>=3:buf.extend([127+j-i,raw[i]]);i=j;continue
   j=i+1
   while j<min(len(raw),i+128) and not(j+2<len(raw) and raw[j]==raw[j+1]==raw[j+2]):j+=1
   buf.append(j-i-1);buf.extend(raw[i:j]);i=j
  out=bytearray();i=offsets[-1]
  while i<len(buf):
   n=buf[i];i+=1
   if n>=128:out.extend([buf[i]]*(n-127));i+=1
   else:out.extend(buf[i:i+n+1]);i+=n+1
  assert out==raw
 with path.open('w') as f:
  for ctype,name,x in [('CHAR16','ZhCodes',codes),('UINT32','ZhOff',offsets),('UINT8','ZhRle',buf)]:
   f.write('static CONST '+ctype+' '+name+'[] = {\n')
   for i in range(0,len(x),64):f.write(','.join(map(str,x[i:i+64]))+',\n')
   f.write('};\n')
