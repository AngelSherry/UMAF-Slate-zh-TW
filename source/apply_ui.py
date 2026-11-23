"""Apply ONLY to a clean edk2-stable202205 source tree for building DisplayEngineDxe."""
from pathlib import Path
from shutil import copyfile
import sys
root=Path(sys.argv[1]); source=Path(__file__).resolve().parent
pkg=root/'MdeModulePkg'
engine=pkg/'Universal/DisplayEngineDxe'; lib=pkg/'Library/CustomizedDisplayLib'
if (engine/'Slate.c').exists(): raise SystemExit('Use a clean edk2-stable202205 tree.')
def edit(p,fn):
    s=p.read_bytes(); a=s.decode().replace('\r\n','\n'); b=fn(a)
    assert a!=b, p
    p.write_bytes(b.replace('\n','\r\n' if b'\r\n' in s else '\n').encode())
for p in [*engine.glob('*.c'),*lib.glob('*.c')]:
    if 'gST->ConOut' in p.read_text():
        edit(p,lambda s:s.replace('gST->ConOut','SlateOut ()').replace('#include ', '#include <Library/Slate.h>\n#include ',1))
p=engine/'FormDisplay.c'
def begin(s):
    start='  gUserInput = UserInputData;'
    assert s.count(start)==1
    s=s.replace(start,'  SlateBegin (FormData->ScreenDimensions == NULL);\n  if (SlateEnabled ()) { mIsFirstForm = TRUE; }\n'+start)
    at=s.index('UnloadDisplayEngine (')
    assert 'HiiRemovePackages (' in s[at:]
    return s[:at]+s[at:].replace('  HiiRemovePackages (','  SlateDrop ();\n  HiiRemovePackages (',1)
edit(p,begin)
edit(lib/'CustomizedDisplayLib.c',lambda s:s.replace('  return PcdGet8 (PcdBrowserFieldTextHighlightColor)', '  if (SlateEnabled ()) { return EFI_TEXT_ATTR (EFI_BLACK, EFI_CYAN); }\n  return PcdGet8 (PcdBrowserFieldTextHighlightColor)'))
edit(engine/'DisplayEngineDxe.inf',lambda s:s.replace('  FormDisplay.c','  Slate.c\n  FormDisplay.c').replace('  gEfiHiiPopupProtocolGuid   ', '  gEfiGraphicsOutputProtocolGuid\n  gEfiHiiFontProtocolGuid\n  gEfiHiiPopupProtocolGuid   '))
for name in ['Slate.c','Slate.h','SlateAtlas.h','SlateBrand.h']: copyfile(source/name,engine/name)
copyfile(source/'Slate.h',pkg/'Include/Library/Slate.h')
from soft_chrome import soft
edit(lib/'CustomizedDisplayLibInternal.c',soft)
from l10n.patch import apply
apply(root,source,edit)

from l10n.help_patch import apply as apply_help
apply_help(root,source,edit)
