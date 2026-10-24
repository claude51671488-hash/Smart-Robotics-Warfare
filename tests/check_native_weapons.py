"""Load actual installed native Lua definitions, then SRW overrides. Not a render test."""
from pathlib import Path
import os,sys
r=Path(__file__).resolve().parents[1]
game=Path(os.environ.get('FORTS_DATA_ROOT','C:/Program Files (x86)/Steam/steamapps/common/Forts/data'))
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime

def environment():
    lua=LuaRuntime()
    lua.execute('SRW={};path="mod"; function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end')
    def include(name):
        p=r/name[4:] if name.startswith('mod/') else game/name
        # Forts dofile exposes globals but discards a chunk's return value.
        lua.execute(p.read_text(encoding='utf-8-sig'))
    lua.globals().dofile=include
    return lua,include

lua,inc=environment()
inc('weapons/projectile_list.lua')
lua.execute('nativeCannon=FindProjectile and FindProjectile("cannon")')
inc('mod/weapons/projectile_list.lua')
inc('mod/weapons/projectile_list.lua')
ammo={p.SaveName:p for _,p in lua.globals().Projectiles.items()}
rockets={'srw_skat_rocket','srw_hornet_rocket','srw_salvo_rocket','srw_tank_aa_rocket','srw_sentry_rocket','srw_hunter_at_rocket',
         'srw_heavy_aa_rocket','srw_pike_rocket','srw_executioner_at','srw_smith_rocket','srw_storm_rocket'}
for name in rockets:
    p=ammo[name]
    assert p.Projectile.Root.Sprite=='mod/ui/textures/projectiles/smart_missile.png'
    assert p.TrailEffect==ammo['missile2'].TrailEffect
    assert abs(p.Projectile.Root.Scale*636-297)<.00001 and p.Projectile.Root.Angle==-90, name
    assert p.ProjectileDamage==ammo['missile2'].ProjectileDamage==300
    assert p.ProjectileSplashDamage==ammo['missile2'].ProjectileSplashDamage==140
    if p.ProjectileType=='missile':
        assert p.ProjectileDrag==48 and p.Missile.RocketThrust>0
    else:
        assert p.ProjectileDrag==0
assert ammo['missile'].Missile.RocketThrust==120000
assert ammo['cannon'].Gravity is None
assert ammo['srw_storm_rocket'].ProjectileType=='mortar'
assert ammo['srw_sledge_ap'].ProjectileDamage==1300
assert ammo['srw_sledge_ap'].ProjectileSplashDamage==0 and ammo['srw_sledge_ap'].Gravity==981
assert ammo['srw_sledge_ap'].ExplodeOnTouch==False
assert ammo['srw_parcel_bomb'].ProjectileDamage==1350
assert ammo['srw_parcel_bomb'].ProjectileSplashDamage==1800
assert ammo['srw_parcel_bomb'].ProjectileSplashDamageMaxRadius==550
assert ammo['srw_parcel_bomb'].Gravity==981 and ammo['srw_parcel_bomb'].ExplodeOnTouch
assert ammo['srw_salvo_rocket'].Missile.RocketThrust==120000

for file in (r/'weapons').glob('*.lua'):
    if file.name.endswith('_list.lua'):continue
    env,load=environment()
    load('mod/scripts/config.lua')
    load('mod/weapons/'+file.name)
    g=env.globals()
    assert g.Root is not None,file.name
    if g.Projectile in rockets:
        def nodes(n):
            yield n
            for key in ('ChildrenInFront','ChildrenBehind'):
                if n[key]:
                    for _,child in n[key].items():yield from nodes(child)
        ns=list(nodes(g.Root))
        expected='srw-hornet-integrated-bay' if file.stem=='hornet_rockets' else 'missile_swarm-base'
        assert any(n.Sprite==expected for n in ns),file.name
        assert not any(n.Name=='Flightpath' for n in ns),file.name
        assert g.MinFireClearance==0 and g.FireDelay==0 and g.EnergyFireCost==0
        guided=ammo[g.Projectile].ProjectileType=='missile'
        assert (g.ForceFireAngle==90)==guided,file.name
    kind='srw_'+file.stem
    cfg=g.SRW.Config.Robots[kind]
    if cfg and cfg.BulletSpeed and not cfg.Artillery and not cfg.BeamWeapon:
        assert abs(g.MinFireSpeed-cfg.BulletSpeed)<1,(kind,g.MinFireSpeed,cfg.BulletSpeed)
    if kind in ('srw_heavy_aa_bot','srw_heavy_aa_gun','srw_heavy_aa_rockets','srw_heavy_aa_defence'):
        assert g.MaxFireRadius>=cfg.Range,kind
        assert g.MinFireClearance==0 and g.EnergyFireCost==0 and g.Recoil==0,kind
        if kind=='srw_heavy_aa_rockets':
            assert g.RoundsEachBurst==2 and g.ReloadTime==6 and g.Projectile=='srw_heavy_aa_rocket'
for name,p in ammo.items():
    if not name.startswith('srw_') or name=='srw_beam_barrier' or p.ProjectileType=='beam':continue
    if name in ('srw_bunker_shell','srw_bunker_bullet'):
        native=ammo['cannon' if name=='srw_bunker_shell' else 'machinegun']
        for key in ('ProjectileDamage','ProjectileSplashDamage','ProjectileSplashDamageMaxRadius','Gravity','ProjectileDrag','MaxAge'):
            multiplier=2 if name=='srw_bunker_bullet' and key=='ProjectileDamage' else 1
            expected={'ProjectileSplashDamage':300,'ProjectileSplashDamageMaxRadius':350}.get(key) if name=='srw_bunker_shell' else None
            if name=='srw_bunker_bullet' and key=='ProjectileDrag': expected=0
            elif expected is None: expected=native[key]*multiplier if native[key] is not None else None
            assert p[key]==expected,(name,key)
        if name=='srw_bunker_shell':
            assert p.ExplodeOnTouch and p.Effects.Impact.foundations.Splash and p.Effects.Impact.rocks01.Splash
            assert p.Projectile.Root.Sprite=='mod/ui/textures/engineering/animated/tracer.png'
            assert abs(p.Projectile.Root.Scale*586*.375-85)<.00001
        else:
            assert p.WeaponDamageBonus==native.WeaponDamageBonus*2
            assert p.Projectile is None
            assert p.ProjectileSprite==native.ProjectileSprite
            assert p.TrailEffect==native.TrailEffect
        continue
    if name=='srw_kolokol_capsule':
        assert p.Projectile.Root.Sprite=='mod/ui/textures/weapons/matryoshka/capsule.png'
        assert p.Projectile.Root.Angle==0 and p.ProjectileDamage==0 and p.ProjectileSplashDamage==0
        assert abs(p.Projectile.Root.Scale*256*.375-64)<.00001
        continue
    if name=='srw_matryoshka_bullet':
        assert p.ProjectileDamage==45 and p.ProjectileSplashDamage==10 and p.WeaponDamageBonus==0
        assert p.Projectile is None and p.ProjectileSprite==ammo['machinegun'].ProjectileSprite
        continue
    if name in ('srw_kolokol_he','srw_kolokol_incendiary'):
        kind='he' if name=='srw_kolokol_he' else 'incendiary'
        assert p.Projectile.Root.Sprite=='mod/ui/textures/weapons/kolokol/'+kind+'.png'
        assert p.Projectile.Root.Angle==-90 and abs(p.Projectile.Root.Scale*256*.375-48)<.00001
        assert p.ProjectileSprite is None and p.Gravity==981
        continue
    rocket=name in rockets or name=='srw_mlrs_rocket' or p.ProjectileType=='missile'
    expected='smart_missile' if rocket else 'artillery_shell'
    assert p.Projectile.Root.Sprite=='mod/ui/textures/projectiles/'+expected+'.png',name
    assert p.Projectile.Root.Angle==-90 and p.Projectile.Root.Scale>0,name
    assert p.ProjectileSprite is None,name
    assert abs(p.Projectile.Root.Scale*(636 if rocket else 245)-(297 if rocket else 243))<.00001,name
    if rocket:
        assert p.ProjectileDamage==300 and p.ProjectileSplashDamage==140,name
import struct
for name,size in [('artillery_shell',(245,84)),('smart_missile',(636,134))]:
    b=(r/'ui/textures/projectiles'/(name+'.png')).read_bytes()
    assert b[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',b[16:24])==size
    assert b[25]==6, 'texture lost RGBA transparency'
print('PASS: native weapon inheritance, all Swarm launchers, user shell/missile artwork, RGBA exports, native trails, balance isolation and launch speeds')
