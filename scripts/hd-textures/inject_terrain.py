"""Inject 2x Topaz terrain/tree art as hi-res TGAs (image ID GZH_TILE128) into <data>/Art/Terrain."""
import json, os, sys
from PIL import Image

B, DATA = sys.argv[1], sys.argv[2]
ID = b'GZH_TILE128'
m = json.load(open(f'{B}/work/terrain/manifest.json'))
dst = os.path.join(DATA, 'Art', 'Terrain')
os.makedirs(dst, exist_ok=True)
written = []
for k, v in m.items():
    w, h = v['size']
    rgb = Image.open(f'{B}/upscaled/TERRAIN__{k}.png').convert('RGB')
    assert rgb.size == (2*w, 2*h), (k, rgb.size)
    if v['format'] == 'TGA:RGBA':
        a = Image.open(f'{B}/work/terrain/alpha/{k}.png').convert('L').resize(rgb.size, Image.BICUBIC)
        rgb.putalpha(a)
        out = rgb
    else:
        out = rgb
    name = os.path.basename(v['path'])
    p = os.path.join(dst, name)
    out.save(p, format='TGA', id_section=ID, compression=None)
    written.append(name)
json.dump(sorted(written), open(os.path.join(dst, '_hd_terrain_injected.json'), 'w'), indent=1)
print(len(written), 'written to', dst)
