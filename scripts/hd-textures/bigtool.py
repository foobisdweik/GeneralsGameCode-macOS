"""BIG archive reading/writing and W3D texture-name scanning for the
infantry texture upscale workflow."""
import os, re, struct

GAME = os.environ.get('GZH_GAME_DIR', os.path.expanduser(
    '~/Games/SteamLibrary/steamapps/common/Command & Conquer Generals - Zero Hour'))
# Later entries win (ZH overrides the base game).
ARCHIVE_DIRS = [os.path.join(GAME, 'ZH_Generals'), GAME]


def read_index(path):
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic not in (b'BIGF', b'BIG4'):
            return {}
        f.read(4)
        count, _hdr = struct.unpack('>II', f.read(8))
        out = {}
        for _ in range(count):
            off, size = struct.unpack('>II', f.read(8))
            name = b''
            while (c := f.read(1)) != b'\0':
                name += c
            out[name.decode('latin-1').replace('\\', '/').lower()] = (path, off, size)
        return out


def game_index():
    idx = {}
    for d in ARCHIVE_DIRS:
        for n in sorted(os.listdir(d)):
            if n.lower().endswith('.big'):
                idx.update(read_index(os.path.join(d, n)))
    return idx


def read_entry(entry):
    path, off, size = entry
    with open(path, 'rb') as f:
        f.seek(off)
        return f.read(size)


def w3d_texture_names(data):
    names = set()

    def walk(buf, start, end):
        p = start
        while p + 8 <= end:
            ctype, csize = struct.unpack_from('<II', buf, p)
            has_sub = csize & 0x80000000
            csize &= 0x7FFFFFFF
            body = p + 8
            if body + csize > end:
                return
            if ctype == 0x32:  # W3D_CHUNK_TEXTURE_NAME
                names.add(buf[body:body + csize].split(b'\0')[0].decode('latin-1').lower())
            elif has_sub:
                walk(buf, body, body + csize)
            p = body + csize

    walk(data, 0, len(data))
    return names


def write_big(path, files):
    """files: list of (archive name with backslashes, bytes)."""
    header = 16 + sum(8 + len(n) + 1 for n, _ in files)
    off = header
    entries = b''
    for n, d in files:
        entries += struct.pack('>II', off, len(d)) + n.encode('latin-1') + b'\0'
        off += len(d)
    with open(path, 'wb') as f:
        f.write(b'BIGF' + struct.pack('<I', off) + struct.pack('>II', len(files), header))
        f.write(entries)
        for _, d in files:
            f.write(d)
