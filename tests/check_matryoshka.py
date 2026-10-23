"""Capsule lifecycle, ownership, terrain-only deployment and 360-degree gun AI."""
from pathlib import Path
import runpy,json,re
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hornet.py'))['lua']
lua.execute((r/'scripts/matryoshka.lua').read_text())
lua.execute('''
SRW.EnsureState()
local nodes={};local serial=10000;local failed=false;local shots={};local sprites={}
function NodeExists(n) return nodes[n]~=nil and not nodes[n].retired end
function NodePosition(n) return nodes[n].pos end
function GetNodeProjectileSaveName(n) return nodes[n].name end
function EnableWeapon() end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(kind=='srw_matryoshka_turret' and angle==90)
 if failed then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=kind,pos=p,built=true};return serial
end
function GetWeaponReloadPeriodById(id) return .04 end
function SetWeaponReloadTime(id,time) assert(time>=0 and time<=.04);devices[id].reload=time end
function SRW.GroundAt(x,y) return Vec3(x,0,0) end
function GetWeaponBarrelPosition(id) return Vec3(devices[id].pos.x,-90,0) end
local gunLeft=false
function GetWeaponHardpointPosition(id)
 local p=GetWeaponBarrelPosition(id);return Vec3(p.x+(gunLeft and -50 or 50),p.y,0)
end
function IsWeapon(id) return devices[id].kind=='enemy_gun' end
function SRW.ShotOrigin(id) return GetWeaponHardpointPosition(id) end
function SRW.AimSolution(id,bot,cfg,target) return target.Position,0,true end
function SRW.ShotClearsTerrain() return true end
function SRW.CanAimRobotWeapon() return true end
function SRW.FireRobotWeapon(id,cfg,aim) shots[#shots+1]={Id=id,Aim=aim};return 0 end
function SetDeviceSpriteState(id,state) sprites[id]=state end
local function flight(node,team)
 nodes[node]={name='srw_kolokol_capsule',pos=Vec3(300,0,0)};SRW.TrackCapsule(team,node)
end
DESTROYTYPE_HITTERRAIN=3;DESTROYTYPE_HITDEVICE=4
for _,team in ipairs({101,102}) do
 data.srw.CapsuleTurrets={};data.srw.CapsuleFlights={};devices={};shots={}
 flight(900,team);SRW.CapsuleImpact(900,team,'srw_kolokol_capsule',DESTROYTYPE_HITDEVICE)
 assert(not next(data.srw.CapsuleTurrets),'capsule spawned in midair/on enemy hull')
 flight(901,team);SRW.CapsuleImpact(901,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 local id,bot=next(data.srw.CapsuleTurrets);assert(id and devices[id].team==team)
 local count=serial;SRW.CapsuleImpact(901,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 assert(serial==count,'duplicate destroy event created a second turret')
 function SRW.DeviceTargets(side)
  assert(side==(devices[id].team%100==1 and 2 or 1))
  return {{Id=1,Kind='reactor',Position=Vec3(340,-90,0)},
          {Id=2,Kind='enemy_gun',Position=Vec3(-300,-90,0)}}
 end
 devices[1]={kind='reactor'};devices[2]={kind='enemy_gun'}
 SRW.UpdateCapsules(.5);assert(#shots==0,'fired before opening')
 assert(devices[id].reload==0,'opening did not hold native reload progress at zero')
 SRW.RefreshCapsuleVisuals(.04);local frozen=sprites[id];local age=bot.DeployAge
 devices[id].disabled=true
 SRW.UpdateCapsules(3);SRW.RefreshCapsuleVisuals(.04)
 assert(bot.DeployAge==age and #shots==0 and sprites[id]==frozen,'EMP did not freeze deployment')
 devices[id].disabled=false
 for i=1,60 do SRW.UpdateCapsules(.04) end
 assert(bot.Target==2 and #shots>0,'near reactor outranked enemy weapon behind turret')
 assert(shots[1].Aim.x<devices[id].pos.x,'rear target was filtered out')
 assert(devices[id].pos.x==300 and devices[id].pos.y==0,'turret walked')
 gunLeft=true;SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]==(team==101 and 'ReadyRightLeft' or 'ReadyLeftLeft'),'left gun state inverted')
 gunLeft=false;SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]==(team==101 and 'ReadyRightRight' or 'ReadyLeftRight'))
 -- Forts may request Normal/Idle again at the end of a native reload. A
 -- completed capsule must repair that change even when our desired state has
 -- not changed since the previous rendering callback.
 sprites[id]='Normal';SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]==(team==101 and 'ReadyRightRight' or 'ReadyLeftRight'),
  'native idle/reload reset left the turret closed')
 -- Capture changes the target side on the next tick; no stale owner survives.
 devices[id].team=team==101 and 102 or 101;SRW.UpdateCapsules(.04)
 assert(bot.Team==devices[id].team)
 devices[id]=nil;SRW.UpdateCapsules(.04);SRW.RefreshCapsuleVisuals(.04)
 assert(not next(data.srw.CapsuleTurrets),'destroyed turret retained simulation state')
 failed=true;flight(902,team);SRW.CapsuleImpact(902,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 assert(not next(data.srw.CapsuleTurrets),'failed spawn retained a ghost')
 failed=false;flight(903,team);nodes[903].retired=true;SRW.UpdateCapsules(.04)
 -- Destruction can be delivered after the node leaves the live node list.
 SRW.CapsuleImpact(903,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 assert(next(data.srw.CapsuleTurrets),'late terrain callback lost its flight record')
 data.srw.CapsuleTurrets={}
 -- A genuine native terrain event is sufficient even when a saved in-flight
 -- projectile had no fired callback in this script instance.
 nodes[905]={name='srw_kolokol_capsule',pos=Vec3(300,0,0)}
 SRW.CapsuleImpact(905,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 assert(next(data.srw.CapsuleTurrets),'untracked native terrain impact was discarded')
 data.srw.CapsuleTurrets={}
 flight(904,team);nodes[904]=nil;SRW.UpdateCapsules(63)
 assert(not data.srw.CapsuleFlights[904],'expired capsule leaked flight state')
end
assert(SRW.Config.Matryoshka.Health==500 and SRW.Config.Matryoshka.MetalFireCost==600
 and SRW.Config.Matryoshka.EnergyFireCost==6000)
''')
env=runpy.run_path(str(r/'tests/check_native_weapons.py'))['environment']
native,load=env();load('mod/weapons/matryoshka_turret.lua')
g=native.globals();assert g.HitPoints==500 and g.MinFireAngle==-180 and g.MaxFireAngle==180
assert g.Root.Name=='MatryoshkaFixedBase' and g.Root.UserData==0
geo=json.loads((r/'ui/textures/weapons/matryoshka/geometry.json').read_text())
head=g.Root.ChildrenInFront[1];barrel=head.ChildrenInFront[1]
assert head.UserData==50 and barrel.UserData==100
assert abs((head.Pivot[2]+barrel.PivotOffset[2])*geo['Height'])<1e-6
for side in ('Right','Left'):
 for index in range(48):
  state=f'Deploy{side}{index}'
  for _,sprite in g.Sprites.items():assert sprite.States[state] is not None
  assert g.Sprites[2].States[state].Frames[1].texture.endswith('/empty.png')
for _,sprite in g.Sprites.items():
 for state in ('Normal','Idle','Reload','ReloadEnd'):
  texture=sprite.States[state].Frames[1].texture
  assert not texture.endswith(('/deploy_00_right.png','/empty.png')), 'native fallback closes capsule'
# Check the actual shipped native 20mm baseline, independent of SRW scaling.
source=Path('C:/Program Files (x86)/Steam/steamapps/common/Forts/data/mods/weapon_pack/weapons/projectile_list.lua').read_text()
section=source[source.index('\n\tSaveName = "cannon20mm",\n'):];section=section[:section.index('DamageMultiplier')]
assert float(re.search(r'ProjectileDamage\s*=\s*([\d.]+)',section)[1])*.5==45
assert float(re.search(r'ProjectileSplashDamage\s*=\s*([\d.]+)',section)[1])*.5==10
print('PASS: tracked terrain-only delivery, ownership, duplicate/failure cleanup, EMP, opening lock, weapons-first rear targeting, 360-degree rig, 500 HP and half native 20mm damage')
