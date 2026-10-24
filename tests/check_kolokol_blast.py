"""Actual native effect definitions and repeated-load ammunition isolation."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
env=runpy.run_path(str(r/'tests/check_native_weapons.py'))['environment']
lua,load=env()
load('weapons/projectile_list.lua')
load('mod/weapons/projectile_list.lua');load('mod/weapons/projectile_list.lua')
p={p.SaveName:p for _,p in lua.globals().Projectiles.items()}
assert p['srw_kolokol_he'].ProjectileSplashDamageMaxRadius==1350
assert p['srw_kolokol_incendiary'].ProjectileSplashDamageMaxRadius==1125
assert p['srw_kolokol_he'].ProjectileDamage==405 and p['srw_kolokol_he'].ProjectileSplashDamage==810
assert p['srw_kolokol_incendiary'].ProjectileDamage==90 and p['srw_kolokol_incendiary'].ProjectileSplashDamage==315
assert p['srw_kolokol_incendiary'].ProjectileIncendiary
assert p['srw_kolokol_incendiary'].IgnitesBackgroundMaterials
for name in ('srw_kolokol_he','srw_kolokol_incendiary'):
 for _,entry in p[name].Effects.Impact.items():
  effect=entry.Effect if hasattr(entry,'items') else entry
  assert effect=='mod/effects/kolokol_mushroom.lua'
assert p['mortar2'].ProjectileSplashDamageMaxRadius==130
assert p['mortar'].ProjectileSplashDamageMaxRadius==120
assert p['mortar'].Effects.Impact.bracing=='effects/impact_mortar_incendiary.lua'
assert p['srw_kolokol_capsule'].ProjectileSplashDamageMaxRadius==0
load('effects/mushroom_cloud.lua')
native=lua.globals().Effects[4]
dimensions=(native.Keyframes[1].ScaleMean,native.Keyframes[1].SpeedMean,native.Keyframes[1].AgeMean)
load('mod/effects/kolokol_mushroom.lua')
g=lua.globals();assert g.LifeSpan==15 and len(g.Effects)==9
sparks=0;waves=0
for _,e in g.Effects.items():
 assert e.TimeToTrigger==0 and e.TrailEffect is None
 if e.Type=='sprite':
  waves+=1;assert e.Sprite=='srw-kolokol-pressure-front' and e.TimeToLive<1 and e.ExpansionRate>0
  assert e.Colour2[4]==0
 else:
  sparks+=1;assert e.Type=='sparks' and e.Sprite=='effects/media/ExplosionMedium'
  assert e.TimeToStop==0 and e.SparkCount<=8
  for _,k in e.Keyframes.items():
   assert k.SpeedMean==0 and k.SpeedStdDev==0
   assert k.ScaleKeys[1]==0 and k.AlphaKeys[1]==0, 'mushroom still grows/fades in'
   assert k.AgeMean>=10 and k.AlphaKeys[2]<=.2, 'no slow dissipation'
 assert e.Projectile is None, 'visual shockwave added a second damage source'
assert sparks==8 and waves==1
assert len(g.Sprites)==1 and g.Sprites[1].Name=='srw-kolokol-pressure-front'
frames=g.Sprites[1].States.Normal.Frames
assert len(frames)==9
game=runpy.run_path(str(r/'tests/check_native_weapons.py'))['game']
for i in range(1,10):
 assert (game/(frames[i].texture+'.tga')).is_file(), 'pressure front uses a missing texture'

print('PASS: instantly formed mushroom, slow native smoke fade, short visual pressure front, x2 isolated radii, unchanged peak damage and incendiary gameplay')
