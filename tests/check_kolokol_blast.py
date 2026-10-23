"""Actual native effect definitions and repeated-load ammunition isolation."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
env=runpy.run_path(str(r/'tests/check_native_weapons.py'))['environment']
lua,load=env()
load('weapons/projectile_list.lua')
load('mod/weapons/projectile_list.lua');load('mod/weapons/projectile_list.lua')
p={p.SaveName:p for _,p in lua.globals().Projectiles.items()}
assert p['srw_kolokol_he'].ProjectileSplashDamageMaxRadius==675
assert p['srw_kolokol_incendiary'].ProjectileSplashDamageMaxRadius==562.5
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
g=lua.globals();assert g.LifeSpan==15 and len(g.Effects)==5
cap=g.Effects[3]
assert (cap.Keyframes[1].ScaleMean,cap.Keyframes[1].SpeedMean,cap.Keyframes[1].AgeMean)==dimensions
for _,e in g.Effects.items():
 assert e.Type=='sparks' and not e.Additive and e.TrailEffect is None
 assert e.Sprite=='effects/media/ExplosionMedium'
 assert e.SparkCount<=8 and e.SparksPerBurst<=8
 latest=(e.TimeToStop or e.TimeToTrigger or 0)+max(k.AgeMean+(k.AgeStdDev or 0) for _,k in e.Keyframes.items())
 assert latest<=g.LifeSpan
print('PASS: reactor-sized native smoke envelope, bounded emitters, no nuclear flash/shake, isolated x1.5 radii, repeat load and incendiary gameplay preserved')
