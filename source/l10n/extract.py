"""Extract static English HII strings and pair other languages from matching string packages (read only)."""
import re,struct,json,collections,sys
from pathlib import Path
def blocks(b,i,n,o):
 j=i+o; end=i+n; ids={}; k=1
 while j<end:
  op=b[j];j+=1
  if op==0:return ids
  if op in [0x14,0x15,0x16,0x17,0x10,0x11,0x12,0x13]:
   if op%2:j+=1
   count=1
   if op in (0x16,0x17,0x12,0x13):count=int.from_bytes(b[j:j+2],'little');j+=2
   for _ in range(count):
    if op>=0x14:
     z=j
     while z+1<end and b[z:z+2]!=b'\0\0':z+=2
     assert z+1<end
     s=b[j:z].decode('utf-16-le');j=z+2
    else:
     z=b.index(0,j,end);s=b[j:z].decode('ascii');j=z+1
    ids[k]=s;k+=1
  elif op==0x20:ids[k]=ids[int.from_bytes(b[j:j+2],'little')];k+=1;j+=2
  elif op in [0x21,0x22]:
   step=2 if op==0x21 else 1;k+=int.from_bytes(b[j:j+step],'little');j+=step
  elif op in (0x30,0x31,0x32):
   ln=int.from_bytes(b[j+1:j+1+(1<<(op-0x30))],'little');assert ln>2;j+=ln-1
  else:raise ValueError((j,op))
 raise ValueError('no end')
def packages(f):
 b=f.read_bytes();result=[]
 for m in re.finditer(rb'(?=(?:[a-z]{2,3}(?:-[a-zA-Z]{2,4})?\x00))',b):
  i=m.start()-46
  if i<0 or b[i+3]!=4:continue
  n=int.from_bytes(b[i:i+3],'little');hd,off=struct.unpack_from('<II',b,i+4)
  if not 46<hd<=off<n<=len(b)-i:continue
  l=b[i+46:b.index(0,i+46)].decode()
  if l.lower() not in ('en-us','en','zh-hant','zh-tw','zh-cn','zh-hans'):continue
  result.append((l,blocks(b,i,n,off)))
 return result
if __name__=='__main__':
 root=Path(sys.argv[1]); rel=Path(sys.argv[2]);out={}
 for f in [*sorted(root.glob('**/*PE32 image section/body.bin')),*sorted((rel/'SL').glob('*.efi'))]:
  name=f.parent.parent.name if f.name=='body.bin' else f.name;sets=packages(f)
  if sets:
   out.setdefault(name,[]).extend([{k:v} for k,v in sets])
 Path(sys.argv[3]).write_text(json.dumps(out,ensure_ascii=False))
