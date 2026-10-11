"""Inject 4x Topaz Art/Textures art into <data>/Art/Textures.

DDS: same BC format as the original (DXT3 -> DXT5, Pillow's DXT3 alpha is wrong),
full mip chain like the originals. TGA: uncompressed, original bit depth.
Alpha: original alpha upscaled 4x bicubic; DXT1 alpha is thresholded to 1 bit.
"""
import io, json, os, struct, sys
from multiprocessing import Pool
from PIL import Image

B, DATA = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3:]
DST = os.path.join(DATA, 'Art', 'Textures')
FOURCC = {'DXT1': b'DXT1', 'DXT5': b'DXT5'}


def bc_level(im, fmt):
    b = io.BytesIO()
    im.save(b, 'DDS', pixel_format=fmt)
    d = b.getvalue()
    bw, bh = (im.width + 3) // 4, (im.height + 3) // 4
    n = bw * bh * (8 if fmt == 'DXT1' else 16)
    assert len(d) == 128 + n, (len(d), n)
    return d[128:]


def write_dds(path, im, fmt):
    levels, cur = [], im
    while True:
        if fmt == 'DXT1':
            a = cur.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
            cur = cur.copy(); cur.putalpha(a)
        levels.append(bc_level(cur, fmt))
        if cur.width == 1 and cur.height == 1:
            break
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.BOX)
    hdr = struct.pack('<4sIIIIIII44x', b'DDS ', 124, 0xA1007, im.height, im.width,
                      len(levels[0]), 0, len(levels))
    hdr += struct.pack('<II4s20x', 32, 4, FOURCC[fmt])
    hdr += struct.pack('<IIII4x', 0x401008, 0, 0, 0)
    assert len(hdr) == 128
    with open(path, 'wb') as f:
        f.write(hdr)
        for l in levels:
            f.write(l)


def one(item):
    k, v = item
    try:
        w, h = v['size']
        im = Image.open(f'{B}/upscaled/{k}.png').convert('RGB')
        if im.size != (4 * w, 4 * h):
            return k, f'size {im.size} != 4x{v["size"]}'
        if v['alpha'] != [255, 255]:
            a = Image.open(f'{B}/work/alpha/{k}.png').convert('L').resize(im.size, Image.BICUBIC)
        else:
            a = Image.new('L', im.size, 255)
        im.putalpha(a)
        out = os.path.join(DST, os.path.basename(v['path']))
        if v['ext'] == 'dds':
            write_dds(out, im, 'DXT1' if v['format'] == 'DXT1' else 'DXT5')
        else:
            (im if v['format'] == 'TGA:RGBA' else im.convert('RGB')).save(out, format='TGA', compression=None)
        return k, None
    except Exception as e:
        return k, repr(e)


if __name__ == '__main__':
    m = json.load(open(f'{B}/work/manifest.json'))
    items = [(k, m[k]) for k in (ONLY or m)]
    os.makedirs(DST, exist_ok=True)
    errs, done = [], []
    with Pool(9) as p:
        for k, e in p.imap_unordered(one, items, chunksize=8):
            (errs.append(f'{k}: {e}') if e else done.append(os.path.basename(m[k]['path'])))
    if not ONLY:
        json.dump(sorted(done), open(os.path.join(DST, '_hd_textures_injected.json'), 'w'), indent=1)
    print(len(done), 'written,', len(errs), 'errors'); print('\n'.join(errs[:30]))
