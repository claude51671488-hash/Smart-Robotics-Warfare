"""Rigid atlas assembly for the approved low-tech capsule, no frame repainting."""
from pathlib import Path
import math,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ui/textures/weapons/matryoshka'
SIZE=(384,320);FOOT=(192,296);JOINT=(192,132)

def trim(im):
    # Generated sheets can bleed a neighbouring cell's outline into an empty
    # margin. Keep the largest connected silhouette, rather than a stray line.
    mask=im.getchannel('A').point(lambda a:255 if a>48 else 0)
    pixels=mask.load();seen=set();largest=[]
    for y in range(im.height):
        for x in range(im.width):
            if pixels[x,y] and (x,y) not in seen:
                stack=[(x,y)];seen.add((x,y));component=[]
                while stack:
                    p=stack.pop();component.append(p)
                    for q in ((p[0]-1,p[1]),(p[0]+1,p[1]),(p[0],p[1]-1),(p[0],p[1]+1)):
                        if 0<=q[0]<im.width and 0<=q[1]<im.height and q not in seen and pixels[q[0],q[1]]:
                            seen.add(q);stack.append(q)
                if len(component)>len(largest):largest=component
    xs=[p[0] for p in largest];ys=[p[1] for p in largest]
    return im.crop((min(xs),min(ys),max(xs)+1,max(ys)+1))
def fit(im,width):return im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
def place(im,anchor,at,angle=0):
    c,s=math.cos(angle),math.sin(angle);px,py=anchor;x,y=at
    return im.transform(SIZE,Image.Transform.AFFINE,(c,s,px-c*x-s*y,-s,c,py+s*x-c*y),Image.Resampling.BICUBIC)
def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def export():
    OUT.mkdir(parents=True,exist_ok=True)
    atlas=Image.open(ROOT/'art/kolokol/matryoshka-parts.png').convert('RGBA')
    names=('capsule','left','right','rear','base','lower','upper','head','barrel')
    parts={}
    for index,name in enumerate(names):
        x=index%3*atlas.width//3;y=index//3*atlas.height//3
        parts[name]=trim(atlas.crop((x,y,(index%3+1)*atlas.width//3,(index//3+1)*atlas.height//3)))
    widths=dict(capsule=82,left=28,right=28,rear=46,base=100,lower=66,upper=48,head=92,barrel=100)
    parts={k:fit(v,widths[k]) for k,v in parts.items()}
    # Flight uses the exact approved capsule, not the reassembled atlas version.
    capsule=trim(Image.open(ROOT/'docs/concepts/kolokol/turret-pods/images/capsule-v4-proposed.png').convert('RGBA'))
    capsule=capsule.resize((round(capsule.width*256/capsule.height),256),Image.Resampling.LANCZOS)
    capsule.save(OUT/'capsule.png',optimize=True)
    empty=Image.new('RGBA',SIZE);empty.save(OUT/'empty.png')
    base=parts['base'];lower=parts['lower'];upper=parts['upper']
    head=parts['head'];barrel=parts['barrel']
    head_anchor=(head.width*.86,head.height*.68)
    barrel_anchor=(barrel.width*.08,barrel.height*.5)
    head_layer=place(head,head_anchor,JOINT)
    barrel_layer=place(barrel,barrel_anchor,JOINT)
    for name,im in [('head',head_layer),('barrel',barrel_layer)]:
        im.save(OUT/f'{name}.png',optimize=True)
        im.transform(SIZE,Image.Transform.AFFINE,(1,0,0,0,-1,2*JOINT[1]),
            Image.Resampling.BICUBIC).save(OUT/f'{name}_left.png',optimize=True)
    frames=[]
    for i in range(49):
        t=i/48;opening=ease(t/.5);extension=ease((t-.45)/.55)
        canvas=Image.new('RGBA',SIZE)
        rear=parts['rear'];left=parts['left'];right=parts['right']
        canvas.alpha_composite(place(rear,(rear.width/2,rear.height*.9),(192,286),math.radians(88)*opening))
        canvas.alpha_composite(place(lower,(lower.width/2,lower.height),(192,288-24*extension)))
        canvas.alpha_composite(place(upper,(upper.width/2,upper.height),(192,280-93*extension)))
        for panel,x,sign,delay in [(left,172,-1,0),(right,212,1,.08)]:
            a=ease((t-delay)/.48)
            canvas.alpha_composite(place(panel,(panel.width/2,panel.height*.9),(x,286),sign*math.radians(84)*a))
        canvas.alpha_composite(place(base,(base.width/2,base.height),FOOT))
        if i<48:
            joint=(192,268-136*extension)
            fold=-math.pi/2*(1-ease((t-.65)/.35))
            canvas.alpha_composite(place(head,head_anchor,joint,-fold))
            canvas.alpha_composite(place(barrel,barrel_anchor,joint,fold))
            # Opening starts with the same compact closed silhouette. The panels
            # are revealed continuously; no per-frame effect/device allocation.
            alpha=1-ease(t/.18)
            reveal=ease(t/.18)
            canvas.putalpha(canvas.getchannel('A').point(lambda a:round(a*reveal)))
            if alpha>0:
                cover=fit(capsule,44);cover.putalpha(cover.getchannel('A').point(lambda a:round(a*alpha)))
                canvas.alpha_composite(place(cover,(cover.width/2,cover.height),FOOT))
        for side in ('right','left'):
            image=canvas if side=='right' else canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            name=f'deploy_{i:02d}_{side}.png' if i<48 else f'ready_{side}.png'
            image.save(OUT/name,optimize=True)
        if i in (0,12,24,36,47):
            bg=Image.new('RGBA',SIZE,'#e6e2d8');bg.alpha_composite(canvas);frames.append(bg)
    final=Image.open(OUT/'ready_right.png').convert('RGBA')
    final.alpha_composite(head_layer);final.alpha_composite(barrel_layer)
    bg=Image.new('RGBA',SIZE,'#e6e2d8');bg.alpha_composite(final);frames.append(bg)
    preview=Image.new('RGBA',(SIZE[0]*6,SIZE[1]))
    for i,im in enumerate(frames):preview.alpha_composite(im,(i*SIZE[0],0))
    preview.convert('RGB').save(ROOT/'art/kolokol/matryoshka-deployment.jpg',quality=92)
    # Only Root is visible in game. Native Head/Barrel remain collision/aiming
    # pivots with empty textures; no static gun can overlay a deployment frame.
    # Fixed supports are composed with one rigid, independently rotated gun.
    for side in ('right','left'):
        support=Image.open(OUT/f'ready_{side}.png').convert('RGBA')
        for pose in range(180):
            angle=pose*2*math.pi/180
            a=head_anchor;b=barrel_anchor;h=head;bar=barrel
            if math.cos(angle)<0:
                h=head.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                bar=barrel.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                a=(a[0],h.height-a[1]);b=(b[0],bar.height-b[1])
            canvas=support.copy()
            canvas.alpha_composite(place(h,a,JOINT,angle))
            canvas.alpha_composite(place(bar,b,JOINT,angle))
            canvas.save(OUT/f'aim_{pose:03d}_{side}.png',optimize=True)
    geometry=dict(AimFrames=180,Width=SIZE[0],Height=SIZE[1],Scale=.55,FootX=192,FootY=296,
        JointX=JOINT[0],JointY=JOINT[1],MuzzleX=JOINT[0]+barrel.width-barrel_anchor[0],MuzzleY=JOINT[1],Frames=48)
    (OUT/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    (OUT/'geometry.lua').write_text('SRWMatryoshkaGeometry={'+','.join(f'{k}={v}' for k,v in geometry.items())+'}\n')
    print('Matryoshka: 48 rigid deployment poses per side, independent gun, exact approved flight capsule')
if __name__=='__main__':export()
