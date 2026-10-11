"""Export infantry textures as PNG for Topaz Photo AI.

Writes into OUT:
  for-topaz/<name>.png   opaque RGB (what Topaz upscales)
  upscaled/              empty; Topaz output goes here
  work/alpha/<name>.png  alpha channel (house-color mask / transparency)
  work/original/<file>   the untouched source file from the .big archive
  work/manifest.json     source path, format, size, alpha range per texture
"""
import io, json, os, re, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bigtool

OUT = os.path.expanduser(sys.argv[1])

CIVILIAN = {'cinfciv01', 'cinmciv01', 'ciufciv01', 'ciumciv01', 'ciumciv02',
            'ciumciv02_s', 'ciumciv03_s', 'civendor01'}
EXTRAS = {'z_infxtras', 'z_aipthfindr2', 'z_niagentcash'}


def wanted(base):
    # Every texture an infantry model references, including the vehicle,
    # muzzle-flash and cinematic textures those models share.
    return True


idx = bigtool.game_index()
bases = set()
for k in idx:
    if k.startswith('art/w3d/') and re.match(r'[a-z]i[a-z0-9]', k[8:]):
        for t in bigtool.w3d_texture_names(bigtool.read_entry(idx[k])):
            bases.add(t.rsplit('.', 1)[0])

for d in ('for-topaz', 'upscaled', 'work/alpha', 'work/original'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

manifest = {}
for base in sorted(b for b in bases if wanted(b)):
    for ext in ('tga', 'dds'):
        key = 'art/textures/%s.%s' % (base, ext)
        if key in idx:
            break
    else:
        print('missing', base)
        continue
    data = bigtool.read_entry(idx[key])
    with open(os.path.join(OUT, 'work/original', base + '.' + ext), 'wb') as f:
        f.write(data)
    im = Image.open(io.BytesIO(data))
    fmt = im.format + ':' + (im.info.get('fourcc', b'').decode() if isinstance(im.info.get('fourcc'), bytes) else str(im.mode))
    im = im.convert('RGBA')
    a = im.getchannel('A')
    im.convert('RGB').save(os.path.join(OUT, 'for-topaz', base + '.png'))
    a.save(os.path.join(OUT, 'work/alpha', base + '.png'))
    manifest[base] = {
        'archive': os.path.basename(idx[key][0]),
        'path': key, 'ext': ext, 'format': fmt,
        'size': list(im.size), 'alpha': list(a.getextrema()),
    }
    print('%-22s %-4s %-14s %4dx%-4d alpha=%s' % (base, ext, fmt, im.size[0], im.size[1], a.getextrema()))

with open(os.path.join(OUT, 'work/manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=1)
print(len(manifest), 'textures ->', OUT)
