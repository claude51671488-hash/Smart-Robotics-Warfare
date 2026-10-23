// Render an art preview from an image-generated transparent layer sheet.
// Requires Node.js and ImageMagick 7 (magick). No game engine is involved.
import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const work = process.argv[2];
if (!work) throw new Error('Usage: node render.mjs /path/to/scratch-directory');
mkdirSync(work, { recursive: true });
const magick = (...args) => {
  const r = spawnSync('magick', args, { encoding: 'utf8' });
  if (r.status !== 0) throw new Error(r.stderr || `ImageMagick exited ${r.status}`);
};
const config = {
  canvas: [1200, 1000], sheet: [1536, 1024],
  barrelCrop: [1536, 500, 0, 0], baseCrop: [1536, 504, 0, 520],
  barrelPivot: [300, 305], basePivotInSheet: [677, 700],
  baseScale: 0.55, baseOffset: [80, 640],
  pivot: [452.35, 739], angleMin: 10, angleMax: 90, sweepDegrees: 80,
  durationCentiseconds: 5, movementFramesEachWay: 33, endpointHoldFrames: 10,
  description: 'Independent static concrete base and barrel rotated about a fixed pivot. Art motion study, not an in-game animation.'
};
const barrel = join(here, 'barrel.png');
const base = join(here, 'base.png');
magick(join(here, 'layers.png'), '-crop', '1536x500+0+0', '+repage', barrel);
magick(join(here, 'layers.png'), '-crop', '1536x504+0+520', '+repage', base);
const scaledBase = join(work, 'scaled-base.png');
magick(base, '-resize', '55%', scaledBase);
const ease = t => (1 - Math.cos(Math.PI * t)) / 2;
const forward = Array.from({ length: 33 }, (_, i) => 10 + 80 * ease(i / 32));
const angles = [...Array(10).fill(10), ...forward, ...Array(10).fill(90), ...forward.slice(1, -1).reverse()];
const frames = [];
for (let i = 0; i < angles.length; i++) {
  const a = angles[i];
  const rotated = join(work, 'rotated.png');
  const frame = join(work, `frame-${String(i).padStart(3, '0')}.png`);
  // A negative image-coordinate angle raises the tube towards the top.
  magick(barrel, '-virtual-pixel', 'transparent', '-background', 'none',
    '-set', 'option:distort:viewport', '1200x1000+0+0',
    '-distort', 'SRT', `300,305 0.55 ${-a} 452.35,739`, '+repage', rotated);
  magick('-size', '1200x1000', 'canvas:#e6e2d8', rotated, '-composite',
    scaledBase, '-geometry', '+80+640', '-composite',
    '-font', 'DejaVu-Sans-Bold', '-fill', '#333630', '-pointsize', '34',
    '-gravity', 'NorthWest', '-annotate', '+38+30', 'KOLOKOL / BASTION V3',
    '-font', 'DejaVu-Sans', '-pointsize', '24',
    '-annotate', '+38+83', `ELEVATION ${a.toFixed(1)} deg  |  SWEEP 80 deg`,
    '-fill', '#885c3d', '-stroke', '#885c3d', '-strokewidth', '2',
    '-draw', 'fill none circle 452.35,739 464.35,739',
    '-font', 'DejaVu-Sans', '-fill', '#55564f', '-stroke', 'none', '-pointsize', '20',
    '-gravity', 'SouthWest', '-annotate', '+38+22', 'MOTION STUDY / FIXED PIVOT / 10-90 DEG', frame);
  frames.push(frame);
}
magick('-delay', '5', '-loop', '0', ...frames, '-layers', 'Optimize', join(here, 'bastion_v3_elevation_80deg.gif'));
magick(frames[10], frames[26], frames[42], '+append', '-resize', '1800x', join(here, 'elevation_keyframes.png'));
config.frameCount = frames.length;
config.loopSeconds = frames.length * 0.05;
writeFileSync(join(here, 'motion.json'), JSON.stringify(config, null, 2) + '\n');
console.log(JSON.stringify({ gif: join(here, 'bastion_v3_elevation_80deg.gif'), frames: frames.length, seconds: config.loopSeconds }));
