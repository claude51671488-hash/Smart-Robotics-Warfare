#!/usr/bin/env python3
"""Assemble imagegen RGBA parts into a rigid-pivot concept GIF using ImageMagick.

Python supplies timing and transforms; ImageMagick composites the generated art.
Requires ImageMagick 7. No game files or external resources are read.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import math
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SIZE = (1200, 760)
FPS = 20
FRAMES = 160
SCALE = 0.62
ORIGIN = (50, 180)
PARTS = {
    "hull": (1774, 525, 0, 0),
    "laser": (585, 345, 0, 535),
    "gun": (400, 180, 590, 635),
    "left": (310, 110, 1000, 680),
    "right": (300, 110, 1325, 680),
    "hatch_panel": (240, 65, 1050, 709),
    "missile": (110, 350, 1640, 525),
}


def run(args):
    command = ["magick"]
    if args[0] == "montage":
        command.append("montage")
        args = args[1:]
    subprocess.run([*command, "-limit", "thread", "1", *map(str, args)], check=True)


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def world(x, y):
    return ORIGIN[0] + SCALE * x, ORIGIN[1] + SCALE * y


def sprite(path, pivot, target, scale, angle):
    """Fixed viewport affine transform: the declared pivot never translates."""
    radians = math.radians(angle)
    a, b = scale * math.cos(radians), scale * math.sin(radians)
    px, py = pivot
    tx, ty = target
    matrix = f"{a},{b},{-b},{a},{tx-a*px+b*py},{ty-b*px-a*py}"
    return ["(", path, "+repage", "-virtual-pixel", "transparent",
            "-background", "none", "-define", f"distort:viewport={SIZE[0]}x{SIZE[1]}+0+0",
            "-distort", "AffineProjection", matrix, "+repage", ")"]


def hatch(path, side, opening):
    """Project a generated armored plate around a fixed hinge along deck depth."""
    angle = math.radians(108 * opening)
    hx, hy = world(978 if side == "left" else 1179, 196)
    direction = 1 if side == "left" else -1
    reach = 201 * SCALE / 2
    dx = direction * reach * math.cos(angle)
    dy = -reach * math.sin(angle) * 1.3
    # This deck projection is a parallelogram. Use an affine transform:
    # a perspective solve becomes unstable when the lid is nearly edge-on.
    matrix = f"{dx/239},{dy/239},{10/64},{33/64},{hx},{hy}"
    return ["(", path, "+repage", "-virtual-pixel", "transparent", "-background", "none",
            "-define", f"distort:viewport={SIZE[0]}x{SIZE[1]}+0+0",
            "-distort", "AffineProjection", matrix, "+repage", ")"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "archangel-ii-v2.gif")
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="srw-archangel-") as tmp:
        tmp = Path(tmp)
        for name, (w, h, x, y) in PARTS.items():
            run([HERE / "archangel-ii-parts-v2.png", "-crop", f"{w}x{h}+{x}+{y}",
                 "+repage", tmp / f"{name}.png"])
        run(["-size", f"{SIZE[0]}x{SIZE[1]}", "xc:#eeede7",
             "-font", "DejaVu-Sans-Bold", "-pointsize", "26", "-fill", "#343932",
             "-annotate", "+50+59", "АРХАНГЕЛ II",
             "-font", "DejaVu-Sans", "-pointsize", "16", "-fill", "#666c61",
             "-annotate", "+50+88", "Наведение орудий • верхние ракетные люки",
             "-pointsize", "13", "-annotate", "+50+725", "КОНЦЕПТ АНИМАЦИИ / SMART ROBOTICS WARFARE",
             tmp / "background.png"])
        run([*sprite(tmp / "hull.png", (0, 0), ORIGIN, SCALE, 0), tmp / "hull-placed.png"])
        hull = [tmp / "hull-placed.png"]

        def frame(index):
            t = index / FPS
            phase = 2 * math.pi * t / (FRAMES / FPS)
            opening = smooth((t - 0.8) / 1.0) * (1 - smooth((t - 5.3) / 1.1))
            cmd = [tmp / "background.png"]
            for part, pivot, target, scale, angle in [
                ("laser", (146, 160), world(955, 517), 0.55, 4 + 22 * (1-math.cos(phase))),
                ("gun", (106, 91), world(560, 515), 0.43, 8 + 28 * (1-math.cos(phase))),
                ("gun", (106, 91), world(1325, 515), 0.43, 12 + 23 * (1-math.cos(phase+1.2))),
            ]:
                cmd += sprite(tmp / f"{part}.png", pivot, target, scale, angle)
                cmd += ["-compose", "over", "-composite"]
            cmd += hull + ["-compose", "over", "-composite"]
            # Clip the emerging missile below deck: it starts inside the launch well.
            if 2.2 <= t <= 4.3:
                flight = t - 2.2
                target = (world(1080, 196)[0], 420 - 90 * flight - 250 * flight * flight)
                missile = sprite(tmp / "missile.png", (55, 204), target, 0.44, 0)
                cmd += ["(", *missile, "-crop", "1200x302+0+0", "+repage",
                        "-background", "none", "-gravity", "northwest", "-extent", "1200x760", ")",
                        "-compose", "over", "-composite"]
            cmd += hatch(tmp / "hatch_panel.png", "left", opening)
            cmd += ["-compose", "over", "-composite"]
            cmd += hatch(tmp / "hatch_panel.png", "right", opening)
            cmd += ["-compose", "over", "-composite", "-define", "png:compression-level=1",
                    tmp / f"frame-{index:03d}.png"]
            run(cmd)

        sample_indices = (0, 35, 58, 90, 125, 159)
        indices = sample_indices if args.preview_only else range(FRAMES)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(frame, indices))
        run(["montage", *[tmp / f"frame-{i:03d}.png" for i in sample_indices],
             "-thumbnail", "600x380", "-tile", "2x3", "-geometry", "+0+0",
             args.output.with_name("archangel-ii-v2-contact.png")])
        if not args.preview_only:
            # One shared palette avoids color flickering between frames.
            files = [tmp / f"frame-{i:03d}.png" for i in range(FRAMES)]
            run([*files[::8], "-append", "-colors", "256", "-unique-colors", tmp / "palette.png"])
            run(["-delay", str(100 // FPS), *files, "-dither", "None", "-remap", tmp / "palette.png",
                 "-loop", "0", "-layers", "Optimize", args.output])
            print(f"Rendered {FRAMES} frames, {FPS} fps, {FRAMES/FPS:g} seconds: {args.output}")


if __name__ == "__main__":
    main()
