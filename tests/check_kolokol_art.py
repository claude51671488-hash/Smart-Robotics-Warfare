"""Load real native controls plus selected mortar rig and render-only ammo art."""
from pathlib import Path
import runpy,json,math,struct
r=Path(__file__).resolve().parents[1]
env=runpy.run_path(str(r/'tests/check_native_weapons.py'))['environment']
lua,load=env()
load('weapons/mortar.lua')
g=lua.globals()
unchanged={key:g[key] for key in ('MinFireAngle','MaxFireAngle','MinFireSpeed','MinFireClearance','Recoil')}
load('mod/weapons/kolokol.lua')
for key,value in unchanged.items():assert g[key]==value,key
assert g.HitPoints==250 and g.WeaponMass==100 and g.ReloadTime==10 and g.MaxFireSpeed==9000
assert g.EnergyFireCost==500 and g.MetalFireCost==30
geo=json.loads((r/'ui/textures/weapons/kolokol/geometry.json').read_text())
assert 1.248<geo['ExtensionRatio']<1.251
assert geo['Scale']==.65 and g.Scale==.65
root=g.Root;head=root.ChildrenBehind[1];barrel=head.ChildrenInFront[1]
assert root.UserData==0 and root.Name=='KolokolFixedBase'
assert head.UserData==50 and barrel.UserData==100
assert root.Sprite=='srw-kolokol-base' and barrel.Sprite=='srw-kolokol-barrel'
assert head.Sprite.endswith('empty.png') and g.ReloadEffect==''
assert g.BarrelRecoilLimit<0 and g.BarrelRecoilSpeed<0 and g.BarrelReturnForce>0
for axis,size in ((1,'Width'),(2,'Height')):
    foot=geo['FootX' if axis==1 else 'FootY']
    assert abs(root.Pivot[axis]*geo[size]*.375+(foot-geo[size]/2)*geo['Scale'])<1e-6
    joint=geo['JointX' if axis==1 else 'JointY']
    assert abs((head.Pivot[axis]+barrel.PivotOffset[axis])*geo[size])<1e-6
muzzle=barrel.ChildrenInFront[1]
assert muzzle.Name=='Hardpoint0' and muzzle.Angle==90 and g.BarrelLength==0
assert abs((muzzle.Pivot[1]+barrel.PivotOffset[1])*geo['Width']-geo['BoreLength'])<1e-6
assert abs(muzzle.Pivot[2]+barrel.PivotOffset[2])<1e-6
for facing in (1,-1):
    for elevation in (45,65,85):
        angle=math.radians(elevation)
        x=facing*geo['BoreLength']*math.cos(angle);y=-geo['BoreLength']*math.sin(angle)
        assert x*facing>0 and y<0
assert len(g.dlc2_Ammunition)==3
for name in ('base','barrel','empty','he','incendiary','icon'):
    b=(r/'ui/textures/weapons/kolokol'/f'{name}.png').read_bytes()
    assert b[:8]==b'\x89PNG\r\n\x1a\n' and b[25]==6,name
print('PASS: fixed Kolokol base, isolated elevating/recoiling barrel, +25% bore, native controls and chosen HE/incendiary art')
