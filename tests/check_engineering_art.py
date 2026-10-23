"""Native KS30-style rig: fixed mount, bounded elevation, separate recoil and loader."""
from pathlib import Path
import runpy,struct,math
r=Path(__file__).resolve().parents[1]
env=runpy.run_path(str(r/'tests/check_native_weapons.py'))['environment']
for kind in ('cannon','machinegun'):
 for left in (False,True):
  lua,load=env()
  load('mod/weapons/bunker_'+kind+('_left' if left else '')+'.lua')
  g=lua.globals();root=g.Root
  assert root.Name=='BunkerFixedBase' and root.UserData==0
  head=root.ChildrenBehind[1];barrel=head.ChildrenInFront[1]
  assert head.UserData==50 and barrel.Name=='Barrel' and barrel.UserData==100
  assert root.Sprite!=head.Sprite and root.Sprite!=barrel.Sprite
  assert g.BarrelRecoilLimit<0 and g.BarrelRecoilSpeed<0 and g.BarrelReturnForce>0
  depression,elevation=(3,7) if kind=='cannon' else (7,20)
  assert (g.MinFireAngle,g.MaxFireAngle)==((180-elevation,180+depression) if left else (-depression,elevation))
  assert g.MaxFireAngle-g.MinFireAngle==depression+elevation
  assert g.FireStdDev==0 and g.FireStdDevAuto==0
  if kind=='cannon':
   origin=head.ChildrenBehind[1]
   assert origin.Name=='Hardpoint0' and origin.Pivot[1]==0 and origin.Pivot[2]==0
   assert barrel.ChildrenInFront[1].Name=='Muzzle'
  else:
   assert barrel.ChildrenInFront[1].Name=='Hardpoint0'
  assert g.ShellEffect=='' and g.ReloadEffect==''
  assert len(g.Sprites)==(3 if kind=='cannon' else 4)
  assert all('load_' not in str(sprite) for _,sprite in g.Sprites.items())
  # Native hardpoint must sit on the visible muzzle in either facing.
  load('mod/ui/textures/engineering/rig/geometry.lua')
  geo=g.SRWBunkerRigGeometry[kind]
  # Native Root.Pivot translation is not multiplied by Root.Scale. A foot
  # anchored with the unscaled pivot floats when the image size is changed.
  foot_x=geo.Width-geo.FootX if left else geo.FootX
  assert abs(root.Pivot[1]*geo.Width*.375+(foot_x-geo.Width/2)*geo.Scale)<1e-6
  assert abs(root.Pivot[2]*geo.Height*.375+(geo.FootY-geo.Height/2)*geo.Scale)<1e-6
  armour=root.ChildrenInFront[1]
  assert armour.Name=='TurretArmour' and armour.UserData==0
  assert 'head' in armour.Sprite
  assert armour.Pivot[1]==0 and armour.Pivot[2]==0
  assert (r/f'ui/textures/engineering/rig/{kind}_head{"_left" if left else ""}.png').exists()
  if kind=='machinegun':
   flash=head.ChildrenInFront[2]
   assert flash.Name=='MuzzleFlash' and flash.Visible==False
   assert g.Sprites[4].InitialState=='Null' and g.Sprites[4].States.Flash.LoopExitState=='Null'
  x=geo.MuzzleX-geo.JointX;y=geo.MuzzleY-geo.JointY
  if left: y=-y
  for elevation in (-depression,0,elevation):
   theta=math.radians((180-elevation) if left else -elevation)
   muzzle=(math.cos(theta)*x-math.sin(theta)*y,math.sin(theta)*x+math.cos(theta)*y)
   assert muzzle[0]*(-1 if left else 1)>0
   # Joint is above its foot; only descendants of Head rotate.
   assert geo.FootY>geo.JointY and root.UserData==0
  assert g.BarrelLength==0,'native aiming origin shifts with the barrel'
lua,load=env()
lua.execute('data={srw={MountedWeapons={[1]={Direction=1},[2]={Direction=-1}}}};function GetWeaponHardpointPosition() return Vec3(0,0,0) end')
load('mod/scripts/combat/aiming.lua')
lua.execute("""
local cfg={LimitedElevation=true}
assert(SRW.BarrelInSector(1,cfg,Vec3(1000,0,0)))
assert(SRW.BarrelInSector(2,cfg,Vec3(-1000,0,0)))
assert(not SRW.BarrelInSector(1,cfg,Vec3(-1000,0,0)))
assert(not SRW.BarrelInSector(2,cfg,Vec3(1000,0,0)))
assert(not SRW.BarrelInSector(1,cfg,Vec3(100,-1000,0)))
assert(not SRW.BarrelInSector(1,cfg,Vec3(100,1000,0)))
""")
print('PASS: fixed supports, bounded elevation, no reload/case animations and native MG flash')
