#!/usr/bin/env python3
"""Self-contained xar archive extractor. No pip packages needed."""
import struct, gzip, zlib, xml.etree.ElementTree as ET, os, sys

def extract_xar(xar_path, out_dir):
    with open(xar_path, 'rb') as f:
        magic = f.read(4)
        assert magic == b'xar!', f'Not a xar archive: {magic}'
        header_size = struct.unpack('>H', f.read(2))[0]
        f.read(2)  # version
        toc_csize = struct.unpack('>Q', f.read(8))[0]
        toc_size  = struct.unpack('>Q', f.read(8))[0]
        f.read(4)  # checksum algorithm
        f.seek(header_size)

        toc_compressed = f.read(toc_csize)
        # xar TOC uses either gzip or raw zlib (deflate)
        if toc_compressed[:2] == b'\x1f\x8b':
            toc_xml = gzip.decompress(toc_compressed).decode('utf-8')
        else:
            toc_xml = zlib.decompress(toc_compressed).decode('utf-8')
        root = ET.fromstring(toc_xml)
        heap_offset = header_size + toc_csize

        ns = {'x': 'http://xar.org/1.0.1/'}
        for file_elem in root.findall('.//x:file', ns):
            name = file_elem.find('x:name', ns)
            if name is None or not name.text or name.text == '.':
                continue
            path = name.text.lstrip('/')
            data = file_elem.find('x:data', ns)
            if data is None:
                continue
            length = int(data.find('x:length', ns).text)
            offset = int(data.find('x:offset', ns).text)
            encoding = data.find('x:encoding', ns)

            f.seek(heap_offset + offset)
            raw = f.read(length)

            if encoding is not None and encoding.text == 'gzip':
                try:
                    raw = gzip.decompress(raw)
                except Exception:
                    try:
                        raw = zlib.decompress(raw)
                    except Exception:
                        pass

            out_path = os.path.join(out_dir, path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'wb') as out:
                out.write(raw)
            size_mb = len(raw) / 1024 / 1024
            print(f'  {path}  ({size_mb:.1f} MB)')

if __name__ == '__main__':
    extract_xar(sys.argv[1], sys.argv[2])