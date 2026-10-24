"""Exported ready support cannot contain a second gun; stand has no air gap."""
from pathlib import Path
import sys,os,subprocess
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
try:
 from PIL import Image
except ImportError:
 art_python=os.environ.get('SRW_ART_PYTHON')
 if not art_python: raise RuntimeError('Install Pillow or set SRW_ART_PYTHON to a Python with Pillow')
 sys.exit(subprocess.run([art_python,__file__],check=False).returncode)
d=r/'ui/textures/weapons/matryoshka'
for side in ('right','left'):
 body=Image.open(d/f'ready_{side}.png').convert('RGBA')
 gun=Image.open(d/f'ready_barrel_{side}.png').convert('RGBA')
 assert body.getchannel('A').crop((250,110,345,150)).getbbox() is None, 'gun baked into support'
 assert gun.getchannel('A').crop((250,110,345,150)).getbbox(), 'separate gun missing'
 # Each row through the telescoping column must touch the next section.
 a=body.getchannel('A')
 for y in range(148,279):
  assert a.crop((177,y,207,y+1)).getbbox(), f'stand air gap at {side} row {y}'
 for i in range(48):
  base=Image.open(d/f'deploy_{i:02d}_{side}.png').convert('RGBA')
  assert base.getchannel('A').crop((250,110,345,150)).getbbox() is None, 'gun baked into opening support'
  assert (d/f'deploy_barrel_{i:02d}_{side}.png').is_file()
print('PASS: connected column, fixed symmetric housing, separate native barrel in every state')
