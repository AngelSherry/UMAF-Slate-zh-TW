/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef UMAF_SLATE_H
#define UMAF_SLATE_H
#include <Uefi.h>
EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *SlateOut(VOID);
VOID SlateBegin(BOOLEAN FullView);
VOID SlateDrop(VOID);
BOOLEAN SlateEnabled(VOID);
BOOLEAN SlateZh(VOID);
VOID SlateSwitchView(VOID);
VOID SlateRefreshLibStrings(VOID);
CHAR16 *SlateText(CHAR16 *owned);
#endif
