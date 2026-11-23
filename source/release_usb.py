"""Package a matched Slate sidecar set for USB without embedding a local build path."""
import argparse
from pathlib import Path
import struct
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent

def portable_renderer(data):
    # The pinned EDK II toolchain stores a CodeView NB10 debug-file name.
    pe, = struct.unpack_from('<I', data, 60)
    opt = pe + 24
    if data[pe:pe+4] != b'PE\0\0' or struct.unpack_from('<H', data, opt)[0] != 0x20B:
        raise ValueError('Expected x64 PE32+ image')
    if any(struct.unpack_from('<II', data, opt + 112 + 4 * 8)):
        raise ValueError('Expected unsigned renderer')
    rva, size = struct.unpack_from('<II', data, opt + 112 + 6 * 8)
    sections = opt + struct.unpack_from('<H', data, pe + 20)[0]
    count = struct.unpack_from('<H', data, pe + 6)[0]
    for i in range(count):
        sec = sections + i * 40
        va, length, raw = struct.unpack_from('<III', data, sec + 12)
        if va <= rva and rva + size <= va + length:
            debug = raw + rva - va
            break
    else:
        raise ValueError('Missing debug directory')
    kind, length, _, pos = struct.unpack_from('<IIII', data, debug + 12)
    if size != 28 or kind != 2 or data[pos:pos+4] != b'NB10' or pos + length > len(data):
        raise ValueError('Unexpected CodeView layout')
    start, end = pos + 16, pos + length
    path = data[start:end].rstrip(b'\0')
    name = path.replace(b'\\', b'/').split(b'/')[-1]
    if name != b'DisplayEngine.dll' or data[start:end] != path + b'\0':
        raise ValueError('Unexpected debug name')
    return data[:start] + name.ljust(end-start, b'\0') + data[end:]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sidecars', type=Path)
    p.add_argument('zip', type=Path)
    args = p.parse_args()
    files = {'SL/' + n: (args.sidecars/n).read_bytes() for n in ('B.efi', 'D.efi', 'Slate.efi', 'U.efi')}
    files['SL/D.efi'] = portable_renderer(files['SL/D.efi'])
    files['EFI/BOOT/BOOTX64.EFI'] = files['SL/Slate.efi']
    for n in ('EDK2.txt', 'Noto-OFL.txt', 'NotoSansCJK-OFL.txt', 'OpenSans-OFL.txt'):
        files['licenses/'+n] = (ROOT/'licenses'/n).read_bytes()
    files['README.txt'] = (ROOT/'docs/USB.txt').read_bytes()
    with ZipFile(args.zip, 'w') as z:
        for name, content in files.items():
            info = ZipInfo(name)  # fixed timestamp; exclude local file attributes
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, content, compress_type=ZIP_DEFLATED, compresslevel=9)

if __name__ == '__main__':
    main()
