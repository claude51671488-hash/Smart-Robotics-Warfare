"""Actual mod entry callbacks and simulation with engine fixtures, not Forts."""
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'.srw-tools'))
from lupa import LuaRuntime

lua=LuaRuntime()
lua.execute('''
path='mod';data={};devices={};nodes={};logs={};shots={};sprites={}
FIRE_SUCCESS=0;FIREFLAG_NORMAL=0;FIREFLAG_DIRECTAIM=32
FIREFLAG_TEST=1;FIREFLAG_IGNORERELOADING=2
RAY_HIT_NOTHING=0;RAY_HIT_TERRAIN=1
DESTROYTYPE_HITTERRAIN=3;DESTROYTYPE_HITDEVICE=4
DESTROYTYPE_HITSTRUCTURE=5;DESTROYTYPE_EXPIRED=6
local serial=1000;local enabled={};local hit
noSurface=false;failSpawn=false;fireFailure=nil
function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function Log(message) logs[#logs+1]=message end
function DeviceExists(id) return devices[id]~=nil end
function GetDeviceTeamIdActual(id) return devices[id].Team end
function GetDeviceType(id) return devices[id].Kind end
function IsDeviceFullyBuilt(id) return devices[id].Built end
function DeviceDisabled(id) return devices[id].Disabled end
function GetDevicePosition(id) return devices[id].Position end
function GetDeviceCentrePosition(id) return GetDevicePosition(id) end
function IsWeapon(id) return true end
local function sideIds(side)
 local ids={}
 for id,d in pairs(devices) do if d.Team%100==side then ids[#ids+1]=id end end
 table.sort(ids);return ids
end
function GetDeviceCountSide(side) return #sideIds(side) end
function GetDeviceIdSide(side,i) return sideIds(side)[i+1] end
function NodeExists(id) return nodes[id]~=nil and not nodes[id].Retired end
function NodePosition(id) assert(nodes[id].Position,'invalid destroyed-node position read');return nodes[id].Position end
function GetNodeProjectileSaveName(id) return nodes[id].Name end
function ProjectileCount() return 0 end
function CastGroundRay(a,b)
 if not noSurface and a.x==b.x and a.y<=0 and b.y>=0 then
  hit=Vec3(a.x,0);return RAY_HIT_TERRAIN
 end
 return RAY_HIT_NOTHING
end
function GetRayHitPosition() return hit end
function EnableWeapon(kind,on,side)
 assert(kind=='srw_matryoshka_turret');enabled[side]=on
end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(enabled[team%100] and kind=='srw_matryoshka_turret' and angle==90)
 if failSpawn then return -1 end
 serial=serial+1
 devices[serial]={Team=team,Kind=kind,Position=p,Built=true,Reload=0}
 OnGroundDeviceCreated(team,serial,kind,p,0)
 return serial
end
function GetWeaponReloadPeriodById() return .04 end
function SetWeaponReloadTime(id,elapsed)
 assert(elapsed>=0 and elapsed<=.04);devices[id].Reload=elapsed
end
function GetWeaponBarrelPosition(id)
 local p=devices[id].Position;return Vec3(p.x,p.y-90)
end
function GetWeaponHardpointPosition(id)
 local p=GetWeaponBarrelPosition(id)
 return Vec3(p.x+(devices[id].Team%100==1 and 50 or -50),p.y)
end
function GetWeaponMaxFireSpeed() return 5000 end
function FireWeaponWithPower(id,p,spread,testSpread,flags,power)
 assert(testSpread==-1 and power==1)
 if flags==35 then return FIRE_SUCCESS end
 assert(flags==32 and devices[id].Reload==.04 and not devices[id].Disabled)
 assert(data.srw.CapsuleTurrets[id].Deployed,'fired before deployment')
 if fireFailure then return fireFailure end
 shots[#shots+1]={Team=devices[id].Team,Id=id,Point=p}
 devices[id].Reload=0;return FIRE_SUCCESS
end
function SetDeviceSpriteState(id,state) sprites[id]=state end
function GetRandomFloat(a,b,description) return a end
function traceCount(event)
 local count=0
 for _,line in ipairs(logs) do
  if line:find('[SRW][Matryoshka] event='..event..' ',1,true) then count=count+1 end
 end
 return count
end
function tick(count)
 for i=1,count do
  for _,d in pairs(devices) do
   if d.Reload and not d.Disabled then d.Reload=math.min(.04,d.Reload+.04) end
  end
  Update(i)
 end
end
function launch(node,team,name)
 nodes[node]={Name=name or 'srw_kolokol_capsule',Position=Vec3(300,-500)}
 OnWeaponFired(team,'srw_kolokol',50,node,0)
end
function assertMenuClosed(team) assert(not enabled[team%100],'temporary weapon enable leaked') end
''')

def include(name):
    if name=='scripts/forts.lua':
        return  # Native bootstrap/engine API is represented by the fixture above.
    assert name.startswith('mod/'),name
    lua.execute((root/name[4:]).read_text(encoding='utf-8-sig'))

lua.globals().dofile=include
lua.execute((root/'script.lua').read_text())
lua.execute('''
-- UI construction is outside this combat/entry-callback test.
SRW.CreateUI=function() end;SRW.CreateShieldUI=function() end
local capsule='srw_kolokol_capsule'
for _,team in ipairs({101,102}) do
 local enemy=team==101 and 102 or 101;local direction=team==101 and 1 or -1
 data={};devices={};nodes={};logs={};shots={};sprites={}
 devices[50]={Team=team,Kind='srw_kolokol',Position=Vec3(-1000*direction,0),Built=true}
 devices[60]={Team=enemy,Kind='cannon',Position=Vec3(1800*direction,-90),Built=true}
 Load(true)
 launch(900,team);assert(data.srw.CapsuleFlights[900].Team==team)
 assert(not next(data.srw.GuidedMissiles),'capsule entered missile guidance')
 tick(5);assert(not next(data.srw.CapsuleTurrets),'flight created a turret')
 nodes[900].Position=Vec3(300,0);nodes[900].Retired=true
 -- Use the real five-argument entry point, including the structure-hit slot.
 OnProjectileDestroyed(900,team,capsule,-1,DESTROYTYPE_HITTERRAIN)
 local id,bot=next(data.srw.CapsuleTurrets)
 assert(id and bot.Team==team and devices[id].Reload==0)
 assertMenuClosed(team)
 OnProjectileDestroyed(900,team,capsule,-1,DESTROYTYPE_HITTERRAIN)
 assert(#SRW.SortedIds(data.srw.CapsuleTurrets)==1,'callback duplicated delivery')
 tick(12);assert(#shots==0)
 SRW.RefreshCapsuleVisuals(.04);local frozen=sprites[id];local age=bot.DeployAge
 devices[id].Disabled=true;tick(30);sprites[id]='Normal'
 SRW.RefreshCapsuleVisuals(.04)
 assert(bot.DeployAge==age and sprites[id]==frozen and #shots==0)
 devices[id].Disabled=false;tick(49)
 assert(bot.Deployed and #shots>0 and traceCount('ready')==1)
 assert(traceCount('launched')==1 and traceCount('impact')==1 and traceCount('placed')==1)
 tick(110);assert(#shots>=14 and traceCount('first_fire')==1,'bullet-by-bullet logging')
 local clock=bot.CombatClock;local count=#shots;local lines=#logs
 for i=1,100 do SRW.RefreshCapsuleVisuals(.01) end
 assert(clock==bot.CombatClock and #shots==count and #logs==lines,'rendering mutated combat/trace')
 Load(false);assert(data.srw.CapsuleTurrets[id]==bot,'Load discarded restored turret')
 tick(1);assert(traceCount('first_fire')==1)
 count=#shots;fireFailure=11;bot.FireWait=0;tick(30)
 assert(#shots==count and traceCount('fire_failed')==1,'same fire refusal flooded the log')
 fireFailure=nil;tick(6);assert(#shots>count and traceCount('first_fire')==1)
 devices[id].Team=enemy;bot.FireWait=0;tick(1)
 assert(bot.Team==enemy and bot.Target==50 and shots[#shots].Team==enemy)
 assert(traceCount('captured')==1)
 devices[id]=nil;tick(1);SRW.RefreshCapsuleVisuals(.04)
 assert(not next(data.srw.CapsuleTurrets) and traceCount('removed')==1)
 -- Rejection causes never read a retired node's missing position or spawn.
 for i,cause in ipairs({DESTROYTYPE_HITDEVICE,DESTROYTYPE_HITSTRUCTURE,DESTROYTYPE_EXPIRED}) do
  launch(910+i,team);nodes[910+i].Position=nil;nodes[910+i].Retired=true
  OnProjectileDestroyed(910+i,team,capsule,123,cause)
  assert(not next(data.srw.CapsuleTurrets),'non-terrain event deployed a turret')
 end
 local lines=#logs
 launch(920,team,'srw_kolokol_he')
 OnProjectileDestroyed(920,team,'srw_kolokol_he',123,DESTROYTYPE_HITDEVICE)
 assert(#logs==lines,'unrelated projectile entered capsule trace')
 noSurface=true;launch(921,team);nodes[921].Position=Vec3(300,0)
 OnProjectileDestroyed(921,team,capsule,-1,DESTROYTYPE_HITTERRAIN)
 noSurface=false;failSpawn=true;launch(922,team);nodes[922].Position=Vec3(300,0)
 OnProjectileDestroyed(922,team,capsule,-1,DESTROYTYPE_HITTERRAIN)
 failSpawn=false;assertMenuClosed(team)
 assert(not next(data.srw.CapsuleTurrets) and traceCount('placement_failed')==2)
 launch(923,team);nodes[923]=nil;tick(1551)
 assert(not data.srw.CapsuleFlights[923] and traceCount('flight_expired')==1)
 -- A restored in-flight capsule may have no launch callback in this instance.
 nodes[924]={Name=capsule,Position=Vec3(300,0),Retired=true}
 OnProjectileDestroyed(924,team,capsule,-1,DESTROYTYPE_HITTERRAIN)
 assert(next(data.srw.CapsuleTurrets) and traceCount('placed')==2)
end
''')
print('PASS: real entry callbacks/full simulation, both owners, launch/terrain/deploy/fire, EMP, reload preservation, capture, duplicate/rejected/late events, placement failures and bounded lifecycle logs')
