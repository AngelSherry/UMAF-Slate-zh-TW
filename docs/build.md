# 維護翻譯與建置

## 修改譯文
選項和說明的最後校訂在 `source/l10n/copyedits.txt` 與 `source/l10n/help-notes.txt`，共用說明在 `source/l10n/help_edit.py`。請保留英文索引，編輯對應的繁體中文。從專案根目錄執行下列命令（需要 Python 3、Pillow 與 Noto Sans CJK Medium 字型）：

```sh
python3 source/l10n/author.py
python3 source/l10n/compile.py /usr/share/fonts/noto-cjk/NotoSansCJK-Medium.ttc
```

## 建置顯示元件
準備一份乾淨的 [EDK II edk2-stable202205](https://github.com/tianocore/edk2/tree/edk2-stable202205) 原始碼，初始化子模組並準備好 BaseTools、GCC、nasm 與建置環境。將 `EDK2` 指向該目錄，從本專案根目錄執行：

```sh
python3 source/apply_ui.py "$EDK2"
cp source/DisplayTest.dsc "$EDK2/"
(cd "$EDK2" && . ./edksetup.sh && build -p DisplayTest.dsc -a X64 -b RELEASE -t GCC5)
```

將 [原版標準包](https://github.com/DavidS95/Smokeless_UMAF) 的 `UniversalAMDFormBrowser.zip` 解壓到獨立目錄，將 `UMAF` 指向該目錄。下列指令會核對原版元件，並在新資料夾配對選單、啟動程式和顯示元件：

```sh
mkdir -p dist/usb
python3 source/package_sidecar.py "$UMAF" "$EDK2/Build/MdeModule/RELEASE_GCC5/X64/DisplayEngine.efi" dist/usb/SL
python3 source/release_usb.py dist/usb/SL dist/UMAF-Slate-1.2.2-zh-TW-FAT32-USB.zip
```

本專案保留 EDK II、Noto 與 Open Sans 的[授權聲明](../licenses/)。選單截圖取自 QEMU 測試表單。
