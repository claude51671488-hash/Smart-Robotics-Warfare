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
function EnableDevice() end
function GetDeviceHitpoints(id) return devices[id].hp or 500 end
function DeleteDeviceById(id) devices[id]=nil;return true end
function ApplyDamageToDevice(id,n) devices[id].hp=500-n end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert((kind=='srw_matryoshka_turret' or kind=='srw_matryoshka_deploying') and angle==90)
 if failed then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=kind,pos=p,built=true};return serial
end
function GetWeaponReloadPeriodById(id) return .04 end
function SetWeaponReloadTime(id,time) assert(time>=0 and time<=.04);devices[id].reload=time end
RAY_HIT_TERRAIN=3;RAY_HIT_NOTHING=0
local rayHit
function CastGroundRay(a,b)
 if a.y<=0 and b.y>=0 and b.y>a.y then
  local t=-a.y/(b.y-a.y);rayHit=Vec3(a.x+(b.x-a.x)*t,0,0);return RAY_HIT_TERRAIN
 end
 return RAY_HIT_NOTHING
end
function GetRayHitPosition() return rayHit end
function SRW.GroundAt(x,y,reach)
 if CastGroundRay(Vec3(x,y-25,0),Vec3(x,y+reach,0),0)==RAY_HIT_TERRAIN then return rayHit end
end
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
  local current=next(data.srw.CapsuleTurrets)
  assert(side==(devices[current].team%100==1 and 2 or 1))
  return {{Id=1,Kind='reactor',Position=Vec3(340,-90,0)},
          {Id=2,Kind='enemy_gun',Position=Vec3(-300,-90,0)}}
 end
 devices[1]={kind='reactor'};devices[2]={kind='enemy_gun'}
 SRW.UpdateCapsules(.5);assert(#shots==0,'fired before opening')
 assert(devices[id].kind=='srw_matryoshka_deploying' and devices[id].reload==nil,'opening still uses a reloadable weapon')
 SRW.RefreshCapsuleVisuals(.04);local frozen=sprites[id];local age=bot.DeployAge
 devices[id].disabled=true
 SRW.UpdateCapsules(3);SRW.RefreshCapsuleVisuals(.04)
 assert(bot.DeployAge==age and #shots==0 and sprites[id]==frozen,'EMP did not freeze deployment')
 -- Native idle/reload requests must not reveal a ready turret during EMP.
 sprites[id]='Normal';SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]==frozen,'native fallback bypassed the EMP-frozen deployment pose')
 devices[id].disabled=false
 for i=1,60 do SRW.UpdateCapsules(.04) end
 id=next(data.srw.CapsuleTurrets)
 assert(bot.Target==2 and #shots>0,'near reactor outranked enemy weapon behind turret')
 assert(shots[1].Aim.x<devices[id].pos.x,'rear target was filtered out')
 assert(devices[id].pos.x==300 and devices[id].pos.y==0,'turret walked')
 gunLeft=true;SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]=='Ready','ready pose still depends on facing')
 gunLeft=false;SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]=='Ready')
 -- Forts may request Normal/Idle again at the end of a native reload. A
 -- completed capsule must repair that change even when our desired state has
 -- not changed since the previous rendering callback.
 sprites[id]='Normal';SRW.RefreshCapsuleVisuals(.04)
 assert(sprites[id]=='Normal','ready renderer still replaces native gun motion with facing snapshots')
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
 -- Native collision coordinates were observed 53-58 units inside the ground.
 -- Reproduce a fast oblique final step, rather than a slow vertical QA drop.
 nodes[906]={name='srw_kolokol_capsule',pos=Vec3(300,-200,0)};SRW.TrackCapsule(team,906)
 nodes[906].pos=Vec3(320,57,0);nodes[906].retired=true
 SRW.CapsuleImpact(906,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 local impactId=next(data.srw.CapsuleTurrets)
 assert(impactId,'fast terrain impact failed to deploy')
 local at=devices[impactId].pos
 assert(at.y==0 and math.abs(at.x-(300+20*200/257))<.001,'landing ignored final flight segment')
 data.srw.CapsuleTurrets={}
 nodes[907]={name='srw_kolokol_capsule',pos=Vec3(300,58,0)}
 SRW.CapsuleImpact(907,team,'srw_kolokol_capsule',DESTROYTYPE_HITTERRAIN)
 assert(next(data.srw.CapsuleTurrets),'restored untracked fast impact failed')
 data.srw.CapsuleTurrets={}
 flight(904,team);nodes[904]=nil;SRW.UpdateCapsules(63)
 assert(not data.srw.CapsuleFlights[904],'expired capsule leaked flight state')
end
assert(SRW.Config.Matryoshka.Health==500 and SRW.Config.Matryoshka.MetalFireCost==600
 and SRW.Config.Matryoshka.EnergyFireCost==6000)
''')
native_checks=runpy.run_path(str(r/'tests/check_native_weapons.py'))
env=native_checks['environment']
native,load=env();load('mod/weapons/matryoshka_turret.lua')
g=native.globals();assert g.HitPoints==500 and g.MinFireAngle==-180 and g.MaxFireAngle==180
assert g.Root.Name=='MatryoshkaFixedBase' and g.Root.UserData==0
geo=json.loads((r/'ui/textures/weapons/matryoshka/geometry.json').read_text())
head=g.Root.ChildrenInFront[1];barrel=head.ChildrenBehind[1]
assert head.UserData==50 and barrel.UserData==100
assert abs((head.Pivot[2]+barrel.PivotOffset[2])*geo['Height'])<1e-6
assert len(g.Sprites)==3
assert head.Sprite=='srw-matryoshka-pivot' and barrel.Sprite=='srw-matryoshka-barrel'
assert len(head.ChildrenBehind)==1 and head.ChildrenInFront is None
assert geo.get('AimFrames') is None, 'ready renderer still quantizes native rotation'
for index,sprite in g.Sprites.items():
 for state in ('Normal','Idle','Reload','ReloadEnd','Ready'):
  texture=sprite.States[state].Frames[1].texture
  assert texture==sprite.States['Normal'].Frames[1].texture, 'native idle creates a second facing'
  assert (r/texture.removeprefix('mod/')).is_file()
 assert sprite.States.DeployRight0 is None, 'weapon still owns opening frames'
opening,podload=env();podload('mod/devices/matryoshka_deploying.lua')
pod=opening.globals()
assert pod.HitPoints==500 and pod.Root.Name=='MatryoshkaOpening'
assert len(pod.Sprites)==1 and pod.Root.ChildrenInFront is None
for side in ('Right','Left'):
 for i in range(48):
  assert pod.Sprites[1].States[f'Deploy{side}{i}'] is not None
# Check the actual shipped native 20mm baseline, independent of SRW scaling.
source=(native_checks['game']/'mods/weapon_pack/weapons/projectile_list.lua').read_text(encoding='utf-8-sig')
section=source[source.index('\n\tSaveName = "cannon20mm",\n'):];section=section[:section.index('DamageMultiplier')]
assert float(re.search(r'ProjectileDamage\s*=\s*([\d.]+)',section)[1])*.5==45
assert float(re.search(r'ProjectileSplashDamage\s*=\s*([\d.]+)',section)[1])*.5==10
print('PASS: tracked terrain-only delivery, ownership, duplicate/failure cleanup, EMP, opening lock, weapons-first rear targeting, 360-degree rig, 500 HP and half native 20mm damage')
