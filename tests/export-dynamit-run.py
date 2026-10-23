"""Mechanical animation of the approved sprite, using Pillow only.

Rigid parts are cut from run_01.png and transformed about fixed joints.
No painting, generated art, optical flow or cross-fading of legs is used.
The source remains untouched; output has 48 poses and exact mirrored copies.
"""
from pathlib import Path
import argparse
import math
from PIL import Image, ImageDraw, ImageChops


SIZE = 444
FRAMES = 48

def cut(source, polygon):
    mask = Image.new('L', source.size)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    part = source.copy()
    part.putalpha(ImageChops.multiply(source.getchannel('A'), mask))
    return part

def transform(part, origin, destination, angle=0):
    c, s = math.cos(angle), math.sin(angle)
    ox, oy = origin
    x, y = destination
    return part.transform(part.size, Image.Transform.AFFINE,
        (c, s, ox-c*x-s*y, -s, c, oy+s*x-c*y), Image.Resampling.BICUBIC)


def segment(canvas, part, source_a, source_b, target_a, target_b):
    angle = math.atan2(target_b[1]-target_a[1], target_b[0]-target_a[0])
    angle -= math.atan2(source_b[1]-source_a[1], source_b[0]-source_a[0])
    canvas.alpha_composite(transform(part, source_a, target_a, angle))


def knee(hip, ankle, upper, lower):
    dx, dy = ankle[0]-hip[0], ankle[1]-hip[1]
    length = math.hypot(dx, dy)
    along = (upper*upper-lower*lower+length*length)/(2*length)
    bend = math.sqrt(max(0, upper*upper-along*along))
    return (hip[0]+along*dx/length-bend*dy/length,
            hip[1]+along*dy/length+bend*dx/length)


def foot(phase, hip_x, stride, ground):
    # At least one foot planted; zero velocity at touchdown/liftoff and seam.
    phase %= 1
    x = hip_x + stride*math.cos(2*math.pi*phase)
    lift = 0 if phase < .5 else 34*math.sin(2*math.pi*(phase-.5))**2
    return (x, ground-lift)


def export(root, preview):
    folder = root/'ui/textures/robots/dynamit'
    source = Image.open(folder/'run_01.png').convert('RGBA')
    body = cut(source, [(75,0),(430,0),(430,245),(344,273),(291,278),(249,267),
        (244,243),(233,217),(199,207),(170,221),(156,252),(124,262),(75,243)])
    near_upper = cut(source, [(169,214),(204,207),(234,220),(250,254),
        (232,288),(150,335),(96,331),(81,308),(91,289),(151,250)])
    near_lower = cut(source, [(91,292),(121,290),(153,336),(181,364),
        (163,387),(127,383),(112,348),(87,325)])
    near_foot = cut(source, [(97,355),(176,352),(208,374),(245,404),
        (245,430),(64,430),(64,404),(86,379)])
    far_upper = cut(source, [(259,254),(299,254),(326,292),(313,335),
        (277,339),(255,300)])
    far_lower = cut(source, [(270,305),(301,300),(325,331),(364,351),
        (378,381),(346,395),(318,368),(283,342)])
    far_foot = cut(source, [(321,354),(377,350),(412,374),(443,398),
        (443,429),(284,429),(284,402),(310,375)])
    frames = []
    for i in range(FRAMES):
        phase = i/FRAMES
        bob = 1.5*(1-math.cos(4*math.pi*phase))
        image = Image.new('RGBA', (SIZE,SIZE))
        for far in (True,False):
            hip = (281,259+bob) if far else (190,245+bob)
            ankle = foot(phase+(.5 if far else 0), hip[0], 43 if far else 58, 370)
            if far:
                origin_hip, origin_knee, origin_ankle = (281,259),(290,316),(350,370)
                parts = far_upper,far_lower,far_foot
            else:
                origin_hip, origin_knee, origin_ankle = (190,245),(111,307),(147,370)
                parts = near_upper,near_lower,near_foot
            joint = knee(hip, ankle, math.dist(origin_hip,origin_knee),math.dist(origin_knee,origin_ankle))
            segment(image,parts[1],origin_knee,origin_ankle,joint,ankle)
            segment(image,parts[0],origin_hip,origin_knee,hip,joint)
            image.alpha_composite(transform(parts[2],origin_ankle,ankle))
            if far:
                image.alpha_composite(transform(body,(0,0),(0,bob)))
        number = i+1
        image.save(folder/f'run_smooth_{number:02}.png',optimize=True)
        image.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(folder/f'run_smooth_{number:02}_left.png',optimize=True)
        frames.append(image)
    if preview:
        clips = []
        for frame in frames:
            canvas = Image.new('RGB', (480, 260), '#393a3b')
            for x, sprite in ((0, frame), (240, frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT))):
                sprite = sprite.resize((240, 240), Image.Resampling.LANCZOS)
                canvas.paste(sprite, (x, 10), sprite)
            clips.append(canvas)
        clips[0].save(preview, save_all=True, append_images=clips[1:], duration=20, loop=0)
    print('Exported 48 rigid-joint poses in both directions (96 RGBA PNGs).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', type=Path)
    args = parser.parse_args()
    export(Path(__file__).resolve().parents[1], args.preview)
