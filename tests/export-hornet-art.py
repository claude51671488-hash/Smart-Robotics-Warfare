"""Mechanical atlas export: rigid hull, jet pulse, gun parts and launch flash.

The source atlas was created with the built-in imagegen tool. This script only
crops, scales, mirrors and assembles its parts; it does not paint new artwork.
Requires Pillow. Runtime sprites never allocate effects for animation frames.
"""
from pathlib import Path
import argparse
import json
import math
from PIL import Image, ImageChops, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SIZE=(768,384)


def trim(atlas,box):
    image=atlas.crop(box)
    alpha=image.getchannel('A').point(lambda a:255 if a>32 else 0)
    return image.crop(alpha.getbbox())


def fit_width(image,width):
    return image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS)


def layer(image,position):
    canvas=Image.new('RGBA',SIZE)
    canvas.alpha_composite(image,(round(position[0]),round(position[1])))
    return canvas


def save(image,folder,name):
    # 384x192 is sufficient at this aircraft's in-game size. All variants share
    # these textures across devices; no full-resolution atlases enter runtime.
    image.resize((384,192),Image.Resampling.LANCZOS).save(folder/name,optimize=True)


def export(preview):
    atlas=Image.open(ROOT/'art/hornet/source-atlas.png').convert('RGBA')
    folder=ROOT/'ui/textures/robots/hornet';folder.mkdir(parents=True,exist_ok=True)
    hull_source=trim(atlas,(0,130,740,610))
    hull=fit_width(hull_source,430)
    gun=fit_width(trim(atlas,(740,295,1254,545)),210)
    pod=fit_width(trim(atlas,(90,730,615,1090)),150)
    jet=fit_width(trim(atlas,(635,835,1254,1095)),100)
    # The gun attachment stays on the vertical mirror axis of the hull. Both
    # sides therefore share the same fixed joint without rotating the aircraft.
    hull_xy=(104,40)
    body=layer(hull,hull_xy)
    joint=(384,280)
    region=atlas.crop((0,130,740,610))
    box=region.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    source_x,source_y=box[0],box[1]+130
    ratio=430/hull_source.width
    def mapped(p):return (round(hull_xy[0]+(p[0]-source_x)*ratio),round(hull_xy[1]+(p[1]-source_y)*ratio))
    panel_shapes=[[(279,261),(392,265),(414,296),(299,296)],
                  [(406,266),(507,270),(536,296),(421,296)]]
    panels=[];bay_mask=Image.new('L',SIZE)
    for points in panel_shapes:
        mask=Image.new('L',SIZE);ImageDraw.Draw(mask).polygon([mapped(p) for p in points],fill=255)
        panel=body.copy();panel.putalpha(ImageChops.multiply(body.getchannel('A'),mask));panels.append(panel)
        bay_mask=ImageChops.lighter(bay_mask,mask)
    # A crop of the existing dark engine interior supplies the exposed bay.
    dark=atlas.crop((30,360,43,420)).resize(SIZE)
    dark.putalpha(bay_mask)
    open_body=Image.alpha_composite(body,dark)
    gun_joint=(round(gun.width*.15),round(gun.height*.5))
    gun_xy=(384-gun_joint[0],192-gun_joint[1])
    fixed=gun.copy();mask=Image.new('L',gun.size)
    split=round(gun.width*.56)
    mask.paste(255,(0,0,split,gun.height))
    fixed.putalpha(ImageChops.multiply(fixed.getchannel('A'),mask))
    moving=gun.copy();moving.putalpha(ImageChops.multiply(moving.getchannel('A'),ImageChops.invert(mask)))
    fixed=layer(fixed,gun_xy);moving=layer(moving,gun_xy)
    # Counter the native 180-degree left gun traverse with a vertical art flip.
    # The fixed aircraft is mirrored horizontally instead.
    for name,image in (('gun_head',fixed),('gun_barrel',moving)):
        save(image,folder,name+'.png')
        save(image.transpose(Image.Transpose.FLIP_TOP_BOTTOM),folder,name+'_left.png')
    save(Image.new('RGBA',SIZE),folder,'empty.png')
    pod_layer=layer(pod,(384-pod.width/2,192-pod.height))
    save(pod_layer,folder,'pod_right.png')
    save(pod_layer.transpose(Image.Transpose.FLIP_LEFT_RIGHT),folder,'pod_left.png')
    save(body,folder,'idle_right.png')
    save(body.transpose(Image.Transpose.FLIP_LEFT_RIGHT),folder,'idle_left.png')
    jet_anchor=(hull_xy[0]+17,hull_xy[1]+hull.height*.55)
    frames={}
    for mode,thrust,angle in (('cruise',.75,0),('boost',1.15,0),('climb',1,12),('dive',1,-12)):
        frames[mode]=[]
        for i in range(8):
            pulse=1+.09*math.sin(2*math.pi*i/8)
            flame=jet.resize((round(jet.width*thrust*pulse),round(jet.height*(.9+.1*pulse))),Image.Resampling.LANCZOS)
            if angle:flame=flame.rotate(angle,Image.Resampling.BICUBIC,expand=True)
            canvas=layer(flame,(jet_anchor[0]-flame.width,jet_anchor[1]-flame.height/2))
            canvas.alpha_composite(body)
            # Lift nozzle has its own smaller, downward jet.
            lift=jet.resize((round(55*pulse),18),Image.Resampling.LANCZOS).rotate(90,expand=True)
            canvas.alpha_composite(lift,(round(hull_xy[0]+hull.width*.43-lift.width/2),hull_xy[1]+hull.height-5))
            frames[mode].append(canvas)
            for side,frame in (('right',canvas),('left',canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT))):
                save(frame,folder,f'{mode}_{i+1:02}_{side}.png')
            opening=math.sin(math.pi*i/7)
            launch=canvas.copy()
            launch.alpha_composite(dark)
            for panel,sign in zip(panels,(-1,1)):
                moved=Image.new('RGBA',SIZE)
                moved.alpha_composite(panel,(round(sign*11*opening),0))
                moved.putalpha(ImageChops.multiply(moved.getchannel('A'),bay_mask))
                launch.alpha_composite(moved)
            flash=jet.resize((max(1,round(55*opening)),18),Image.Resampling.LANCZOS).rotate(-90,expand=True)
            hatch=mapped((350 if i<4 else 470,269))
            if opening>.1:launch.alpha_composite(flash,(hatch[0]-flash.width//2,hatch[1]-flash.height+4))
            for side,frame in (('right',launch),('left',launch.transpose(Image.Transpose.FLIP_LEFT_RIGHT))):
                save(frame,folder,f'{mode}_launch_{i+1:02}_{side}.png')
    launch_flame=jet.resize((46,20),Image.Resampling.LANCZOS).rotate(-90,expand=True)
    for i in range(1,7):
        canvas=pod_layer.copy()
        flash=launch_flame.copy()
        flash.putalpha(flash.getchannel('A').point(lambda a:round(a*(1-(i-1)/6))))
        canvas.alpha_composite(flash,(374,round(192-pod.height-28)))
        save(canvas,folder,f'launch_{i:02}_right.png')
        save(canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT),folder,f'launch_{i:02}_left.png')
    flash=jet.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((84,32),Image.Resampling.LANCZOS)
    flash.save(folder/'muzzle_flash.png')
    geo=dict(Width=SIZE[0]/2,Height=SIZE[1]/2,Scale=1,JointX=joint[0]/2,JointY=joint[1]/2,
        MuzzleX=(gun_xy[0]+gun.width-2)/2,MuzzleY=96,PodTopY=(192-pod.height)/2,PodFootY=96,
        MountX=(mapped((405,270))[0]-joint[0])*.5,
        MountY=(mapped((405,270))[1]-joint[1])*.5,
        FrameCount=8,FrameSeconds=.035)
    (folder/'geometry.json').write_text(json.dumps(geo,indent=2)+'\n')
    (folder/'geometry.lua').write_text('SRWHornetGeometry={'+','.join(f'{k}={v}' for k,v in geo.items())+'}\n')
    if preview:
        clips=[]
        for n in range(64):
            mode=('cruise','climb','boost','dive')[n//16]
            whole=frames[mode][n%8].copy()
            gun_frame=Image.alpha_composite(fixed,moving)
            whole.alpha_composite(gun_frame,(0,joint[1]-192))
            canvas=Image.new('RGB',(960,310),'#443f35')
            right=whole.resize((480,240),Image.Resampling.LANCZOS)
            canvas.paste(right,(0,0),right)
            left=right.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            canvas.paste(left,(480,0),left)
            clips.append(canvas)
        clips[0].save(preview,save_all=True,append_images=clips[1:],duration=35,loop=0)
        still=clips[8];still.save(ROOT/'art/hornet/assembled-preview.png')
    print(f'Exported Hornet atlas: {len(list(folder.glob("*.png")))} RGBA textures, fixed anchors.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',type=Path)
    export(parser.parse_args().preview)
