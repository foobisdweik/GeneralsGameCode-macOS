import json,os,sys
from PIL import Image
from collections import Counter
B='/Users/iphoobis/Documents/GeneralsZH-HD-Infantry'
m=json.load(open(B+'/work/terrain/manifest.json'))
c=Counter(); bad=[]
for k,v in m.items():
    up=Image.open(f'{B}/upscaled/TERRAIN__{k}.png')
    src=Image.open(f'{B}/for-topaz-2x/TERRAIN__{k}.png')
    al=Image.open(f'{B}/work/terrain/alpha/{k}.png')
    w,h=v['size']
    c[(up.mode,src.mode,al.mode)]+=1
    if up.size!=(2*w,2*h): bad.append((k,v['size'],up.size,src.size))
print(c); print(len(bad), bad[:10])
