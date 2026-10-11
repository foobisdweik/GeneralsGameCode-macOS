# HD texture workflow

These scripts export the Zero Hour textures for upscaling in Topaz Photo AI, and then install the upscaled art as loose files in the game data folder. The engine loads loose files in `Art/Textures` and `Art/Terrain` in place of the copies in the `.big` archives. So deleting the loose files restores the original textures.

The scripts were recovered from the Claude Code session transcripts that first wrote them. They need Python 3 and Pillow. `bigtool.py` reads the game folder from `GZH_GAME_DIR`, or from the Steam library default if that variable is not set.

## Steps

1. Export the textures. `WORK` is the workspace folder (for example `~/Documents/GeneralsZH-HD-Infantry`).
   ```bash
   python3 export_all.py WORK             # both sets
   python3 export_all.py WORK terrain     # one set: textures or terrain
   ```
   - `for-topaz-4x/` gets the `Art/Textures` images, as opaque RGB.
   - `for-topaz-2x/` gets the `Art/Terrain` images, with the prefix `TERRAIN__`.
   - `work/` and `work/terrain/` get the alpha masks, the original files, and `manifest.json`.
2. Upscale in Topaz: the `for-topaz-4x` set at 4x and the `for-topaz-2x` set at 2x. Save all output PNGs in `WORK/upscaled/`.
3. Install the upscaled art into the game data folder `DATA`:
   ```bash
   python3 inject_textures.py WORK DATA   # 4x DDS/TGA into DATA/Art/Textures
   python3 inject_terrain.py WORK DATA    # 2x TGA into DATA/Art/Terrain
   ```
   `inject_textures.py` keeps each texture's original format, but it writes DXT3 as DXT5, because Pillow's DXT3 alpha is wrong. It also writes the full mip chain. `inject_terrain.py` tags each TGA with the image ID `GZH_TILE128`. The engine's `TILE_SCALE` code (`TileData.h`) uses tagged art at full size. Untagged art is upsampled.

## Other files

- `export.py` is the first, infantry-only version of `export_all.py`. `export_all.py` replaces it.
- `check.py` is a one-off check of the terrain upscales against `work/terrain/manifest.json`.
