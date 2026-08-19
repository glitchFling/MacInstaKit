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
        cksum_algo = struct.unpack('>I', f.read(4))[0]
        f.seek(header_size)

        toc_compressed = f.read(toc_csize)
        if toc_compressed[:2] == b'\x1f\x8b':
            toc_xml = gzip.decompress(toc_compressed).decode('utf-8')
        else:
            toc_xml = zlib.decompress(toc_compressed).decode('utf-8')

        root = ET.fromstring(toc_xml)
        heap_offset = header_size + toc_csize

        # xar can have no namespace, or use xar.org namespace
        namespaces = ['', 'http://xar.org/1.0.1/']
        found_any = False

        for ns_url in namespaces:
            ns = {'x': ns_url} if ns_url else {}
            tag = 'x:file' if ns_url else 'file'
            for file_elem in root.findall(f'.//{tag}', ns):
                found_any = True
                name_tag = 'x:name' if ns_url else 'name'
                name = file_elem.find(name_tag, ns)
                if name is None:
                    continue
                path_text = name.text or ''
                if path_text == '.' or not path_text.strip():
                    continue
                path = path_text.lstrip('/')

                data_tag = 'x:data' if ns_url else 'data'
                data = file_elem.find(data_tag, ns)
                if data is None:
                    continue

                length_e = data.find('x:length' if ns_url else 'length', ns)
                offset_e = data.find('x:offset' if ns_url else 'offset', ns)
                if length_e is None or offset_e is None:
                    continue

                length = int(length_e.text)
                offset = int(offset_e.text)

                encoding = None
                enc_elem = data.find('x:encoding' if ns_url else 'encoding', ns)
                if enc_elem is not None:
                    if enc_elem.text and enc_elem.text.strip():
                        encoding = enc_elem.text.strip()
                    else:
                        style = enc_elem.find('x:style' if ns_url else 'style', ns)
                        if style is not None and style.text:
                            st = style.text.strip()
                            if 'gzip' in st or 'zlib' in st or 'compress' in st:
                                encoding = 'gzip'

                f.seek(heap_offset + offset)
                raw = f.read(length)

                if encoding and 'gzip' in encoding:
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
                print(f'  {path} ({size_mb:.1f} MB)')

        if not found_any:
            print(f'WARNING: No files found in xar TOC (root={root.tag})')

if __name__ == '__main__':
    extract_xar(sys.argv[1], sys.argv[2])