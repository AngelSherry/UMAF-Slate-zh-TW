def soft(s):
    # In PrintFramework only. Keep the unmodified text-console paths below.
    start = s.index('\nPrintFramework (')
    anchor = '  if (gClassOfVfr != FORMSET_CLASS_PLATFORM_SETUP) {'
    pos = s.index(anchor, start)
    assert pos < s.index('  Buffer = AllocateZeroPool (0x10000);', start)
    return s[:pos] + '''  if (SlateEnabled ()) {
    if (gClassOfVfr == FORMSET_CLASS_PLATFORM_SETUP) {
      ClearLines (gScreenDimensions.LeftColumn, gScreenDimensions.RightColumn,
                  gScreenDimensions.TopRow, gScreenDimensions.TopRow + NONE_FRONT_PAGE_HEADER_HEIGHT - 1,
                  TITLE_TEXT | TITLE_BACKGROUND);
      TitleStr = LibGetToken (FormData->FormTitle, FormData->HiiHandle);
      if (TitleStr != NULL) {
        PrintStringAtWithWidth (gScreenDimensions.LeftColumn + 2, gScreenDimensions.TopRow + 1,
                                TitleStr, gScreenDimensions.RightColumn - gScreenDimensions.LeftColumn - 4);
        FreePool (TitleStr);
      }
    }

    // Include the reserved status row in the footer. UpdateStatusBar only
    // draws or erases its two message spans, not the rest of that row.
    ClearLines (gScreenDimensions.LeftColumn, gScreenDimensions.RightColumn,
                gScreenDimensions.BottomRow - STATUS_BAR_HEIGHT - gFooterHeight,
                gScreenDimensions.BottomRow - 1, KEYHELP_TEXT | KEYHELP_BACKGROUND);
    return;
  }

''' + s[pos:]
