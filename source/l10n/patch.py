from pathlib import Path
from shutil import copyfile
def apply(root,source,edit):
 pkg=root/'MdeModulePkg';eng=pkg/'Universal/DisplayEngineDxe';lib=pkg/'Library/CustomizedDisplayLib'
 def rep(p,a,b):
  def op(s):
   assert s.count(a)==1,(p,a[:70],s.count(a))
   return s.replace(a,b)
  edit(p,op)
 for n in ['SlateZhTable.h','SlateZhGlyphs.h','SlateZh.inc']:copyfile(source/n,eng/n)
 rep(eng/'FormDisplay.c','String = HiiGetString (HiiHandle, Token, NULL);','String = SlateText (HiiGetString (HiiHandle, Token, SlateEnabled () ? "en-US" : NULL));')
 rep(lib/'CustomizedDisplayLibInternal.c','String = HiiGetString (HiiHandle, Token, NULL);','String = SlateText (HiiGetString (HiiHandle, Token, SlateEnabled () ? "en-US" : NULL));')
 rep(eng/'Popup.c','gMessageString = HiiGetString (HiiHandle, Message, NULL);','gMessageString = SlateText (HiiGetString (HiiHandle, Message, SlateEnabled () ? "en-US" : NULL));')
 # Comparison uses original raw option values, never their presentation labels.
 for i in '12':
  rep(eng/'ProcessOptions.c',f'Str{i} = GetToken (Value{i}->Value.string, HiiHandle);',f'Str{i} = HiiGetString (HiiHandle, Value{i}->Value.string, NULL);')
 rep(lib/'CustomizedDisplayLibInternal.c','  FreePool (mSpaceBuffer);\n}', '''  FreePool (mSpaceBuffer);
}

VOID SlateRefreshLibStrings (VOID) {
  FreeLibStrings ();
  InitializeLibStrings ();
}''')
 rep(eng/'FormDisplay.c','CHAR16 *\nGetToken (','STATIC BOOLEAN mSlateRedraw;\nSTATIC BOOLEAN mSlateTextWasZh;\n\nCHAR16 *\nGetToken (')
 rep(eng/'FormDisplay.c','  SlateBegin (FormData->ScreenDimensions == NULL);','''SlateRedisplay:
  SlateBegin (FormData->ScreenDimensions == NULL);
  if (mSlateTextWasZh != SlateZh ()) {
    FreeDisplayStrings ();
    InitializeDisplayStrings ();
    SlateRefreshLibStrings ();
    mSlateTextWasZh = SlateZh ();
  }''')
 rep(eng/'FormDisplay.c','                ScreenOperation = UiHotKey;\n              }','''                ScreenOperation = UiHotKey;
              } else if (SlateEnabled () && Key.ScanCode == SCAN_F2) {
                SlateSwitchView ();
                mSlateRedraw = TRUE;
                ControlFlag = CfExit;
              }''')
 rep(eng/'FormDisplay.c','  FreeMenuOptionData (&gMenuOption);\n\n  return Status;','''  FreeMenuOptionData (&gMenuOption);
  if (mSlateRedraw) {
    mSlateRedraw = FALSE;
    goto SlateRedisplay;
  }
  return Status;''')
 # Some AMD forms give this option a shared, empty help token. Scope the explanation to its prompt.
 anchor='          RowCount      = BottomRow - TopRow + 1;'
 rep(eng/'FormDisplay.c',anchor,'''          if (SlateZh () && MenuOption && IsSelectable (MenuOption)) {
            CHAR16 *RawPrompt = HiiGetString (gFormData->HiiHandle, GetPrompt (MenuOption->ThisTag->OpCode), "en-US");
            if (RawPrompt && StrCmp (RawPrompt, L"Gear Down Mode") == 0) {
              CHAR16 *Original = HelpInfo ? HiiGetString (gFormData->HiiHandle, HelpInfo, "en-US") : NULL;
              if (!Original || !*Original || StrCmp(Original,L"No help string")==0) {
              CHAR16 *Help = AllocateCopyPool (sizeof (L"Slate:GearDownHelp"), L"Slate:GearDownHelp");
              if (Help) { if (StringPtr) {FreePool (StringPtr);} StringPtr = SlateText (Help); }
              }
              if (Original) {FreePool(Original);}
            }
            if (RawPrompt) { FreePool (RawPrompt); }
          }
'''+anchor)
 # The original return value counts printable code units, not screen cells.
 rep(eng/'FormDisplay.c','  PrintStringAtWithWidth (Col + Length, Row, L"", Width - Length);','''  if (SlateZh ()) { Length = GetStringWidth (String) / sizeof (CHAR16) - 1; }
  if (Length < Width) { PrintStringAtWithWidth (Col + Length, Row, L"", Width - Length); }''')
 rep(eng/'InputHandler.c','    if (StrLen (StringPtr) > PopUpWidth) {\n      PopUpWidth = StrLen (StringPtr);','''    if ((SlateZh () ? GetStringWidth (StringPtr) / sizeof (CHAR16) - 1 : StrLen (StringPtr)) > PopUpWidth) {
      PopUpWidth = SlateZh () ? GetStringWidth (StringPtr) / sizeof (CHAR16) - 1 : StrLen (StringPtr);''')
 anchor='      if (StrLen (StringPtr) > (PopUpWidth - 1)) {'
 rep(eng/'InputHandler.c',anchor,'''      if (SlateZh () && GetStringWidth (StringPtr) / sizeof (CHAR16) - 1 > PopUpWidth - 1) {
        UINTN Pos=0, Cells=0, Step=1;
        while (StringPtr[Pos]) {
          if (StringPtr[Pos] == WIDE_CHAR) {Step=2;}
          else if (StringPtr[Pos] == NARROW_CHAR) {Step=1;}
          else {if (Cells+Step>PopUpWidth-4) {break;} Cells+=Step;}
          Pos++;
        }
        TempStringPtr=AllocateZeroPool ((Pos+5)*sizeof(CHAR16));
        if (TempStringPtr) {
          CopyMem(TempStringPtr,StringPtr,Pos*sizeof(CHAR16));
          TempStringPtr[Pos++]=NARROW_CHAR;
          CopyMem(TempStringPtr+Pos,L"...",4*sizeof(CHAR16));
          FreePool(StringPtr); StringPtr=TempStringPtr;
        }
      } else if (!SlateZh () && StrLen (StringPtr) > (PopUpWidth - 1)) {''')

 # These two help strings may have been registered before the graphical view was active.
 anchor="    BakChar = L'\\0';"
 rep(lib/'CustomizedDisplayLibInternal.c',anchor,'''    if (SlateZh () && SetState && (StrCmp(HotKey->HelpString,L"F9=Reset to Defaults")==0 || StrCmp(HotKey->HelpString,L"F10=Save")==0)) {
      CHAR16 *Localized=SlateText(AllocateCopyPool(StrSize(HotKey->HelpString),HotKey->HelpString));
      if (Localized) {
        PrintStringAtWithWidth(CurrentCol,CurrentRow,Localized,ColumnIndexWidth);
        FreePool(Localized); Link=GetNextNode(&FormData->HotKeyListHead,Link); Index++; continue;
      }
    }
'''+anchor)
 # Han ideographs are legal word boundaries even when no ASCII spaces separate them.
 anchor='        if ((InputString[*Index + StrOffset] == CHAR_SPACE) && (GlyphOffset <= LineWidth)) {'
 rep(eng/'FormDisplay.c',anchor,'''        if (SlateZh () && *GlyphWidth==2 && GlyphOffset<=LineWidth &&
            InputString[*Index+StrOffset] >= 0x3400 && InputString[*Index+StrOffset] <= 0x9fff) {
          LastSpaceOffset = StrOffset;
          LastGlyphWidth = *GlyphWidth;
        }
'''+anchor)
 # Reuse the saved option/scroll anchor across a language-only repaint, not across forms.
 rep(eng/'FormDisplay.c','STATIC BOOLEAN mSlateRedraw;', 'STATIC BOOLEAN mSlateRedraw;\nSTATIC BOOLEAN mSlateRestoreHighlight;')
 rep(eng/'FormDisplay.c','  if (gMisMatch && (gFormData->HiiHandle', '  if ((gMisMatch || (mSlateRestoreHighlight && !IsListEmpty (&gMenuOption))) && (gFormData->HiiHandle')
 rep(eng/'FormDisplay.c','  OUT USER_INPUT                *UserInputData\n  )\n{\n  EFI_STATUS  Status;', '  OUT USER_INPUT                *UserInputData\n  )\n{\n  BOOLEAN SlateReturning = FALSE;\n  EFI_STATUS  Status;')
 rep(eng/'FormDisplay.c','  Status = UiDisplayMenu (FormData);', '  mSlateRestoreHighlight = SlateReturning;\n  Status = UiDisplayMenu (FormData);\n  mSlateRestoreHighlight = FALSE;')
 rep(eng/'FormDisplay.c','    goto SlateRedisplay;', '    SlateReturning = TRUE;\n    goto SlateRedisplay;')
