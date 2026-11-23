"""Index the option/help pairs in the English FA506QR.414 form packages (read only).
Usage: python3 help_inventory.py EXTRACTED_FIRMWARE [output.json]
Pairs with unresolved string IDs are skipped; no inference from neighboring strings."""
from pathlib import Path
import sys,re,json,collections
from extract import packages
def read(root):
 rows=[];seen=set()
 for f in root.rglob('*PE32 image section/body.bin'):
  b=f.read_bytes()
  if b'\x02\x0e' not in b:continue
  try:langs=[dd for lang,dd in packages(f) if lang.lower() in ['en','en-us']]
  except (ValueError,IndexError,UnicodeError):continue
  if len(langs)!=1:continue
  d=langs[0];mod=f.parent.parent.name
  for m in re.finditer(b'\x02\x0e',b):
   pos=m.start()+1;p=pos-4
   if p<0:continue
   end=p+int.from_bytes(b[p:p+3],'little')
   if end>len(b) or end<pos+24 or b[pos+1]&127<23:continue
   ops=[];stack=[]
   while pos+2<=end:
    op=b[pos];sz=b[pos+1]&127
    if sz<2 or pos+sz>end:break
    opb=b[pos:pos+sz]
    def u(i):return int.from_bytes(opb[i:i+2],'little')
    if op in [3,5,6,7,8,0xc,0xf,0x1a,0x1b,0x1c,0x23] and u(2) in d:
     z=dict(module=mod,op=op,prompt=d[u(2)],help=d.get(u(4),''),value=d.get(u(6),'') if op==3 else '',choices=[]);ops.append(z)
    if op==9 and u(2) in d:
     active=next((x for x in reversed(stack) if isinstance(x,dict)),None)
     if active:active['choices'].append(d[u(2)])
    if opb[1]&128:stack.append(ops[-1] if op in [5,0x23] and u(2) in d else None)
    if op==0x29 and stack:stack.pop()
    pos+=sz
   if pos==end:
    for z in ops:
     key=json.dumps(z,sort_keys=True)
     if key not in seen:rows.append(z);seen.add(key)
 return rows
if __name__=='__main__':
 rows=read(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(rows,ensure_ascii=False,indent=1));print(collections.Counter(x['module'] for x in rows))
