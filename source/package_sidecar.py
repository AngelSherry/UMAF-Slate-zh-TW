"""Make a side-by-side visual edition. Only change resource filenames and display binding."""
from pathlib import Path
from hashlib import sha256
from uuid import UUID
import sys
base,renderer,target=map(Path,sys.argv[1:]);target.mkdir(exist_ok=True)
def original(rel,h):
 b=(base/rel).read_bytes()
 if sha256(b).hexdigest()!=h:raise SystemExit('Unknown UMAF component: '+rel)
 return b
def once(b,a,c):
 if b.count(a)!=1:raise SystemExit('Unexpected resource layout')
 assert len(a)==len(c)
 return b.replace(a,c)
loader=original('EFI/Boot/Bootx64.efi','94fa8ac7f668bf4c6db1982b1a3a436a16a3f59e4d58dc56ba8ef3d5adb0af76')
for old,new in [('SetupBrowser.efi',r'\SL\B.efi'),('DisplayEngine.efi',r'\SL\D.efi'),('UiApp.efi',r'\SL\U.efi')]:
 # The standard loader uses names relative to the filesystem root.
 a=(old+'\0').encode('utf-16-le'); c=(new+'\0').encode('utf-16-le')
 loader=once(loader,a,c.ljust(len(a),b'\0'))
browser=original('SetupBrowser.efi','c1b37e11367abae594bf5e656d85ad634dabd8109fcf6cae8e9922ba9ec38b49')
ui=original('UiApp.efi','a624c3160c9f7d763dfed273fef7c6fea247cb7246c162e878e44e710170140b')
standard=UUID('9bbe29e9-fda1-41ec-ad52-452213742d2e').bytes_le
slate=UUID('a15a16ec-65cf-45c3-8ff5-2314bf761fd2').bytes_le
for name,blob in [('Slate.efi',loader),('B.efi',once(browser,standard,slate)),('D.efi',once(renderer.read_bytes(),standard,slate)),('U.efi',ui)]:
 (target/name).write_bytes(blob)
