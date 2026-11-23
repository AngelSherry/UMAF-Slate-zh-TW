"""Build-time UI change, restricted to rendering and moving focus to documented readouts."""
from shutil import copyfile
def apply(root,source,edit):
 e=root/'MdeModulePkg/Universal/DisplayEngineDxe'; c=e/'FormDisplay.c'
 def sub(p,a,b):
  def op(s):
   assert s.count(a)==1,(p,a)
   return s.replace(a,b)
  edit(p,op)
 copyfile(source/'SlateHelpTable.h',e/'SlateHelpTable.h')
 sub(e/'FormDisplay.h','  BOOLEAN    ReadOnly;', '  BOOLEAN    ReadOnly;\n  BOOLEAN    SlateInfo;\n  CONST CHAR16 *SlateNote;')
 a='STATIC BOOLEAN mSlateRedraw;'
 sub(c,a,'''#include "SlateHelpTable.h"
// Match BOTH OEM strings. A blank or reused help token has no meaning on its own.
STATIC CONST CHAR16 *
SlateFindHelp (EFI_HII_HANDLE H, EFI_IFR_OP_HEADER *Op) {
  EFI_IFR_STATEMENT_HEADER *Sh;
  CHAR16 *P, *Original; CONST CHAR16 *Note = NULL; UINTN Lo=0, Hi=ARRAY_SIZE (SlateHelp), M, I;
  if (!SlateEnabled () || Op->Length < sizeof(*Op)+sizeof(*Sh)) {return NULL;}
  switch (Op->OpCode) {
    case EFI_IFR_TEXT_OP: case EFI_IFR_NUMERIC_OP: case EFI_IFR_ONE_OF_OP:
    case EFI_IFR_STRING_OP: case EFI_IFR_REF_OP: break;
    default: return NULL;
  }
  Sh=(EFI_IFR_STATEMENT_HEADER *)(Op+1);
  P=HiiGetString (H,Sh->Prompt,"en-US"); if (!P) {return NULL;}
  while (Lo<Hi) {M=Lo+(Hi-Lo)/2; if (StrCmp (SlateHelp[M].Prompt,P)<0) {Lo=M+1;} else {Hi=M;}}
  if (Lo<ARRAY_SIZE (SlateHelp) && StrCmp (SlateHelp[Lo].Prompt,P)==0) {
    Original = Sh->Help ? HiiGetString(H,Sh->Help,"en-US") : NULL;
    // A missing language string is not equivalent to a real blank help token.
    if (!Sh->Help || Original) {
      for (I=Lo; I<ARRAY_SIZE (SlateHelp) && StrCmp(SlateHelp[I].Prompt,P)==0; I++) {
        if (StrCmp(SlateHelp[I].Original,Original ? Original : L"")==0) {Note=SlateHelp[I].Note;break;}
      }
    }
    if (Original) {FreePool(Original);}
  }
  FreePool(P);return Note;
}
'''+a)
 a='    MenuOption->Sequence = Index;'
 sub(c,a,a+'''
    MenuOption->SlateNote = SlateFindHelp (gFormData->HiiHandle,Statement->OpCode);
    MenuOption->SlateInfo = MenuOption->SlateNote != NULL &&
      ((Statement->OpCode->OpCode == EFI_IFR_TEXT_OP &&
        ((EFI_IFR_TEXT *)Statement->OpCode)->TextTwo != 0) ||
       ((Statement->Attribute & HII_DISPLAY_READONLY) != 0 &&
        (Statement->OpCode->OpCode == EFI_IFR_NUMERIC_OP || Statement->OpCode->OpCode == EFI_IFR_STRING_OP)));
''')
 a='  if ((MenuOption->ThisTag->OpCode->OpCode == EFI_IFR_SUBTITLE_OP) ||'
 sub(c,a,'  if (MenuOption->SlateInfo && PrintableMenu (MenuOption)) {return TRUE;}\n'+a)
 # Preserve factory GrayOut/ReadOnly and refuse editing of focus-only information rows.
 for a in ['if ((MenuOption == NULL) || MenuOption->GrayOut || MenuOption->ReadOnly)', 'if (IsListEmpty (&gMenuOption) || MenuOption->GrayOut || MenuOption->ReadOnly)']:
  sub(c,a,a[:-1]+' || MenuOption->SlateInfo)')
 a='        if (Statement->OpCode->OpCode == EFI_IFR_TEXT_OP) {\n          break;'
 sub(c,a,a.replace('if (Statement','if (MenuOption->SlateInfo || Statement'))
 a='          RowCount      = BottomRow - TopRow + 1;'
 sub(c,a,'''          if (SlateZh () && !IsListEmpty (&gMenuOption) && MenuOption != NULL && MenuOption->SlateNote != NULL &&
              IsSelectable (MenuOption)) {
            CHAR16 *Note = AllocateCopyPool (StrSize (MenuOption->SlateNote),MenuOption->SlateNote);
            if (Note != NULL) {if (StringPtr != NULL) {FreePool (StringPtr);} StringPtr = Note;}
          }
'''+a)
