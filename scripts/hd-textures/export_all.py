"""Export every texture in Art/Textures as PNG for Topaz Photo AI.

Layout in OUT:
  for-topaz-4x/<name>.png            Art/Textures, opaque RGB, upscale 4x
  for-topaz-2x/TERRAIN__<name>.png   Art/Terrain, opaque RGB, upscale 2x
                                     (terrain/tree tile atlas, TILE_SCALE 2)
  upscaled/                          Topaz output for both sets goes here
  work[/terrain]/alpha/<name>.png    alpha channel (house-color mask / transparency)
  work[/terrain]/original/<file>     untouched source file from the .big archive
  work[/terrain]/manifest.json       source archive, path, format, size, alpha range
"""
import io, json, os, struct, sys
from multiprocessing import Pool
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bigtool

OUT = os.path.expanduser(sys.argv[1])
SETS = {
    'textures': ('art/textures/', 'for-topaz-4x', '', 'work'),
    'terrain':  ('art/terrain/',  'for-topaz-2x', 'TERRAIN__', 'work/terrain'),
}


def dds_fourcc(data):
    if data[:4] != b'DDS ':
        return ''
    flags, fourcc, bits = struct.unpack_from('<I4sI', data, 80)
    return fourcc.decode('latin-1') if flags & 4 else 'RGB%d' % bits


def one(item):
    key, entry, (prefix, topaz, tag, work) = item
    base, ext = key[len(prefix):].rsplit('.', 1)
    try:
        data = bigtool.read_entry(entry)
        with open(os.path.join(OUT, work, 'original', base + '.' + ext), 'wb') as f:
            f.write(data)
        im = Image.open(io.BytesIO(data))
        im.load()
        src_mode = im.mode
        im = im.convert('RGBA')
        a = im.getchannel('A')
        im.convert('RGB').save(os.path.join(OUT, topaz, tag + base + '.png'))
        a.save(os.path.join(OUT, work, 'alpha', base + '.png'))
        return base, {'archive': os.path.basename(entry[0]), 'path': key, 'ext': ext,
                      'format': dds_fourcc(data) if ext == 'dds' else 'TGA:' + src_mode,
                      'size': list(im.size), 'alpha': list(a.getextrema())}, None
    except Exception as e:
        return base, None, '%s: %s' % (key, e)


if __name__ == '__main__':
    which = sys.argv[2:] or list(SETS)
    idx = bigtool.game_index()
    for name in which:
        prefix, topaz, tag, work = SETS[name]
        for d in (topaz, 'upscaled', work + '/alpha', work + '/original'):
            os.makedirs(os.path.join(OUT, d), exist_ok=True)
        items = sorted((k, v, SETS[name]) for k, v in idx.items() if k.startswith(prefix))
        manifest, errors = {}, []
        with Pool() as pool:
            for base, info, err in pool.imap_unordered(one, items, chunksize=16):
                if err:
                    errors.append(err)
                else:
                    manifest[base] = info
        with open(os.path.join(OUT, work, 'manifest.json'), 'w') as f:
            json.dump(dict(sorted(manifest.items())), f, indent=1)
        with open(os.path.join(OUT, work, 'export-errors.txt'), 'w') as f:
            f.write('\n'.join(sorted(errors)) + '\n')
        print(name, len(manifest), 'exported,', len(errors), 'failed ->', os.path.join(OUT, topaz))
