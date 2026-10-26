#!/usr/bin/env python3
"""Assemble generated Spear II cutouts into a concept GIF with ImageMagick 7.

Only the lower defensive laser and the shoulder missile move. Animation timing
and launch/replenishment motion are illustrative, not Forts gameplay settings.
Python supplies transforms; all artwork comes from the imagegen parts atlas.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import math
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
FPS, COUNT = 20, 160
SIZE = (1200, 600)
ORIGIN = (50, 140)
SCALE = 0.56


def run(args):
    command = ["magick"]
    if args[0] == "montage":
        command.append("montage")
        args = args[1:]
    subprocess.run([*command, "-limit", "thread", "1", *map(str, args)], check=True)


def world(x, y):
    return ORIGIN[0] + SCALE*x, ORIGIN[1] + SCALE*y


def smooth(t):
    t = max(0, min(1, t))
    return t*t*(3-2*t)


def part(path, pivot, target, scale, angle, tile=320):
    """Rotate a generated cutout inside a small tile around its fixed pivot."""
    center = tile//2
    x, y = target
    return ["(", path, "+repage", "-virtual-pixel", "transparent", "-background", "none",
            "-define", f"distort:viewport={tile}x{tile}+0+0", "-distort", "SRT",
            f"{pivot[0]},{pivot[1]} {scale} {angle} {center},{center}", "+repage", ")",
            "-geometry", f"{round(x-center):+d}{round(y-center):+d}",
            "-compose", "over", "-composite"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE / "spear-ii-v3.gif")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="srw-spear-") as directory:
        tmp = Path(directory)
        for name, crop in {
            "hull": "1983x460+0+0", "turret": "540x220+750+520",
            "missile": "405x140+225+550", "powered": "550x140+80+550",
        }.items():
            run([HERE / "spear-ii-parts-v3.png", "-crop", crop, "+repage", tmp/f"{name}.png"])
        run([tmp/"hull.png", "-resize", "56%", tmp/"hull-scaled.png"])
        run(["-size", "1200x600", "xc:#eeede7", "-font", "DejaVu-Sans-Bold",
             "-pointsize", "26", "-fill", "#343932", "-annotate", "+50+58", "КОПЬЁ II",
             "-font", "DejaVu-Sans", "-pointsize", "16", "-fill", "#666c61",
             "-annotate", "+50+86", "Наведение защитного лазера • пуск ракеты",
             "-pointsize", "13", "-annotate", "+50+565", "КОНЦЕПТ АНИМАЦИИ / SMART ROBOTICS WARFARE",
             tmp/"background.png"])

        def frame(i):
            t = i/FPS
            angle = 30*(1-math.cos(2*math.pi*t/(COUNT/FPS)))
            cmd = [tmp/"background.png"]
            cmd += part(tmp/"turret.png", (60, 95), world(1114, 404), 0.27, angle)
            cmd += [tmp/"hull-scaled.png", "-geometry", "+50+140", "-compose", "over", "-composite"]
            x, y = world(730, 237)
            if t < 2:
                cmd += part(tmp/"missile.png", (10, 65), (x, y), 0.30, 0)
            elif t < 2.6:
                # Eject clear of the shoulder before motor ignition.
                lift = smooth((t-2)/0.6)
                cmd += part(tmp/"missile.png", (10, 65), (x+20*lift, y-85*lift), 0.30, 0)
            elif t < 4.2:
                flight = t-2.6
                cmd += part(tmp/"powered.png", (155, 65),
                            (x+20+450*flight+400*flight*flight, y-85-35*flight), 0.30, 0)
            elif t >= 5.8:
                # Show replenishment inside the recess to return to the first pose.
                loaded = smooth((t-5.8)/1.0)
                cmd += ["(", "-size", "1200x600", "xc:none"]
                cmd += part(tmp/"missile.png", (10, 65), (x-130*(1-loaded), y), 0.30, 0)
                cmd += ["-crop", "135x48+448+249", "+repage", ")", "-geometry", "+448+249",
                        "-compose", "over", "-composite"]
            cmd += ["-define", "png:compression-level=1", tmp/f"frame-{i:03d}.png"]
            run(cmd)

        samples = (0, 44, 57, 66, 110, 159)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(frame, samples if args.preview_only else range(COUNT)))
        run(["montage", *[tmp/f"frame-{i:03d}.png" for i in samples],
             "-thumbnail", "600x300", "-tile", "2x3", "-geometry", "+0+0",
             args.output.with_name("spear-ii-v3-contact.png")])
        if not args.preview_only:
            frames = [tmp/f"frame-{i:03d}.png" for i in range(COUNT)]
            run([*frames[::8], "-append", "-colors", "256", "-unique-colors", tmp/"palette.png"])
            run(["-delay", str(100//FPS), *frames, "-dither", "None", "-remap", tmp/"palette.png",
                 "-loop", "0", "-layers", "Optimize", args.output])
            print(f"Rendered {COUNT} frames, {FPS} fps, {COUNT/FPS:g} seconds: {args.output}")


if __name__ == "__main__":
    main()
