"""Mechanical export of approved painted layers; no procedural repainting.

The tube's middle straight section is lengthened, keeping the breech, trunnion
and muzzle at their original diameter. The existing native gun hierarchy does
the rotation at runtime; no per-frame devices or effects are created.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ui/textures/weapons/kolokol'
CANVAS=(768,384)
UNIT=.5

def place(image,pivot,destination,scale=1,angle=0,size=CANVAS):
    c,s=math.cos(angle),math.sin(angle)
    # Inverse rigid transform: destination pixel -> original painted layer.
    a,b=c/scale,s/scale
    d,e=-s/scale,c/scale
    x,y=destination;px,py=pivot
    return image.transform(size,Image.Transform.AFFINE,
        (a,b,px-a*x-b*y,d,e,py-d*x-e*y),Image.Resampling.BICUBIC)

def export():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'docs/concepts/kolokol/animation'
    base=Image.open(source/'base.png').convert('RGBA')
    tube=Image.open(source/'barrel.png').convert('RGBA')
    old_pivot=(300,305);old_muzzle=(1457,260)
    # Extend only the straight section: do not ovalise the circular trunnion.
    extension=round((old_muzzle[0]-old_pivot[0])*.25)
    split,end=520,1220
    long=Image.new('RGBA',(tube.width+extension,tube.height))
    long.alpha_composite(tube.crop((0,0,split,tube.height)),(0,0))
    middle=tube.crop((split,0,end,tube.height)).resize((end-split+extension,tube.height),Image.Resampling.LANCZOS)
    long.alpha_composite(middle,(split,0))
    long.alpha_composite(tube.crop((end,0,tube.width,tube.height)),(end+extension,0))
    muzzle=(old_muzzle[0]+extension,old_muzzle[1])
    # Align the painted bore with native +X before the engine elevates it.
    angle=math.atan2(old_pivot[1]-muzzle[1],muzzle[0]-old_pivot[0])
    base_origin=(64,240);ratio=.25
    joint=(base_origin[0]+677*ratio,base_origin[1]+180*ratio)
    foot=(base_origin[0]+765*ratio,base_origin[1]+454*ratio)
    base_layer=place(base,(0,0),base_origin,ratio)
    tube_layer=place(long,old_pivot,joint,ratio,angle)
    length=math.dist(muzzle,old_pivot)*ratio
    geometry=dict(Width=CANVAS[0],Height=CANVAS[1],Scale=UNIT,
        JointX=joint[0],JointY=joint[1],FootX=foot[0],FootY=foot[1],
        MuzzleX=joint[0]+length,MuzzleY=joint[1],
        OriginalBoreLength=math.dist(old_muzzle,old_pivot)*ratio,
        BoreLength=length,ExtensionRatio=length/(math.dist(old_muzzle,old_pivot)*ratio))
    base_layer.save(OUT/'base.png',optimize=True)
    tube_layer.save(OUT/'barrel.png',optimize=True)
    Image.new('RGBA',CANVAS).save(OUT/'empty.png',optimize=True)
    (OUT/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    (OUT/'geometry.lua').write_text('SRWKolokolGeometry={'+','.join(f'{k}={v}' for k,v in geometry.items())+'}\n')
    # Three independently rendered native-style poses, fixed base in each.
    tiles=[]
    for elevation in (45,65,85):
        tile=Image.new('RGBA',(820,640),'#e6e2d8')
        destination=(260,560)
        tube_pose=place(tube_layer,joint,destination,1,math.radians(-elevation),(820,640))
        base_pose=place(base_layer,joint,destination,1,0,(820,640))
        tile.alpha_composite(tube_pose);tile.alpha_composite(base_pose)
        ImageDraw.Draw(tile).text((30,30),f'KOLOKOL / {elevation} DEG',fill='#30332d',font_size=24)
        tiles.append(tile)
    preview=Image.new('RGBA',(2460,640))
    for i,tile in enumerate(tiles):preview.alpha_composite(tile,(i*820,0))
    preview.convert('RGB').save(ROOT/'art/kolokol/long-barrel-preview.jpg',quality=92)
    # Dedicated ammo art. Consistent 48-world-unit body length, no balance edit.
    for name in ('he','incendiary'):
        image=Image.open(ROOT/f'art/kolokol/{name}-transparent.png').convert('RGBA')
        bounds=image.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
        image=image.crop(bounds)
        image=image.resize((256,round(image.height*256/image.width)),Image.Resampling.LANCZOS)
        image.save(OUT/f'{name}.png',optimize=True)
    # Current weapon icon is derived from the assembled, approved gun layers.
    assembled=Image.new('RGBA',(820,640))
    assembled.alpha_composite(place(tube_layer,joint,(260,560),1,-math.pi/4,(820,640)))
    assembled.alpha_composite(place(base_layer,joint,(260,560),1,0,(820,640)))
    bounds=assembled.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    icon=assembled.crop(bounds);icon.thumbnail((96,64),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(96,64));canvas.alpha_composite(icon,((96-icon.width)//2,(64-icon.height)//2))
    canvas.save(OUT/'icon.png',optimize=True)
    print(f'Kolokol: fixed base, bore +{(geometry["ExtensionRatio"]-1)*100:.1f}%, 2 selected ammo textures')

if __name__=='__main__':export()
