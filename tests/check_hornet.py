"""Air factory isolation, flight state, transactional launch and real AA identities."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
for file in ('factories/squads.lua','combat/aiming.lua','robots/air.lua','robots/aa.lua','robots/air_weapon.lua','combat/guidance.lua','robots/heavy_aa.lua','ui/squads.lua'):
 lua.execute((r/'scripts'/file).read_text())
lua.execute(r'''
function EnableWeapon() end
function GetWeaponHardpointPosition(id)
 local d=devices[id];local p=d.pos
 if d.kind=='srw_hornet_bot' then return Vec3(p.x+(d.team%100==1 and 88 or -88),p.y,0) end
 return p
end
function GetDevicePlatformA() return 1 end
function GetDevicePlatformB() return 2 end
local material='srw_air_platform'
function GetLinkMaterialSaveName() return material end
function GetDeviceCost() return {metal=500,energy=4000} end
function DeleteDeviceById(id) devices[id]=nil;return true end
function CastGroundRay() return RAY_HIT_NOTHING end
function CastRayFromDevice() return RAY_HIT_NOTHING end
function ProjectileCount() return 0 end
function GetDeviceCountSide() return 0 end
function EnumerateStructureLinks() end
local serial=3000;local fail=false
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(angle==90 and p.y<0,'air launch snapped to ground')
 if fail and kind=='srw_hornet_rockets' then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=kind,built=true,pos=p};return serial
end
local function reset(team)
 devices={[50]={team=team,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)},
 [51]={team=team,kind='srw_factory_ground_3',built=true,pos=Vec3(0,0,0)}}
 data.srw.Robots={};data.srw.MountedWeapons={};data.srw.Factories={}
 balances[team]={metal=100000,energy=1000000}
 SRW.FactoryCreated(team,50,'srw_factory_air_1',0)
 SRW.FactoryCreated(team,51,'srw_factory_ground_3',0)
 assert(devices[50] and devices[51],'air factory displaced ground factory')
 local f=data.srw.Factories[50]
 assert(f.Domain=='air' and SRW.FactoryCapacity(f)==20)
 return f
end
for _,team in ipairs({101,102}) do
 local f=reset(team)
 SRW_OrderIndividual(team,51,24);assert(not data.srw.Factories[51].srw_hornet_botQueue)
 SRW.Order(team,50);SRW_OrderHound(team,50);assert(f.Queue==0 and not f.HoundQueue)
 SRW_SquadEdit(team,50,1,1);assert(#f.SquadDraft==0,'ground squad admitted to air factory')
 SRW_OrderIndividual(team+100,50,24);assert(not f.srw_hornet_botQueue,'ally ordered foreign aircraft')
 SRW_OrderIndividual(team,50,24)
 SRW.UpdateFactories(.04);assert(f.CurrentType=='srw_hornet_bot')
 assert(balances[team].metal==99650)
 for i=1,375 do SRW.UpdateFactories(.04) end
 assert(f.srw_hornet_botReserve==1)
 fail=true;SRW_ReleaseIndividual(team,50,24)
 assert(f.srw_hornet_botReserve==1 and not next(data.srw.Robots) and not next(data.srw.MountedWeapons))
 fail=false;SRW_ReleaseIndividual(team,50,24)
 assert(f.srw_hornet_botReserve==0)
 local id=next(data.srw.Robots);local b=data.srw.Robots[id];local p=devices[id].pos
 assert(b.Kind=='srw_hornet_bot' and b.Mounted and b.AirPhase=='cruise')
 for i=1,25 do SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04) end
 assert((devices[id].pos.x-p.x)*b.Direction>0 and devices[id].pos.y<p.y,'no flight/climb')
 p=devices[id].pos;devices[id].disabled=true
 SRW.UpdateRobots(.5);assert(devices[id].pos==p and b.AirVelocity.x==0,'EMP did not hold aircraft')
 devices[id].disabled=false
 SRW_SquadEdit(team,50,24,1);SRW_SquadSave(team,50)
 assert(data.srw.SquadTemplates[tostring(team)..':air'][1]=='srw_hornet_bot')
 SRW_SquadStart(team,50);assert(f.Squad.Speed==4)
 SRW.UpdateFactories(.04);assert(balances[team].metal==99265,'air squad lost 10% surcharge')
 for i=1,375 do SRW.UpdateFactories(.04) end
 SRW_SquadRelease(team,50);SRW.UpdateFactories(.04)
 assert(f.Squad.Released==1 and not f.Squad.Releasing)
 local grouped
 for _,air in pairs(data.srw.Robots) do if air.SquadId then grouped=air end end
 assert(grouped and grouped.SquadSpeed==4 and grouped.Kind=='srw_hornet_bot')
end
local f=reset(101);material='bracing'
SRW.FactoryCreated(101,50,'srw_factory_air_1',0)
assert(not devices[50] and balances[101].metal==100500,'invalid platform not refunded')
material='srw_air_platform';f=reset(101)
SRW_OrderIndividual(101,50,24);SRW.UpdateFactories(.04)
for i=1,375 do SRW.UpdateFactories(.04) end
SRW_ReleaseIndividual(101,50,24)
local id=next(data.srw.Robots);local b=data.srw.Robots[id]
devices[7000]={team=102,kind='srw_hornet_bot',built=true,pos=Vec3(2000,-900,0)}
data.srw.Robots[7000]={Team=102,Kind='srw_hornet_bot',AirVelocity={x=-100,y=0}}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide() return 7000 end
local sharedHound=SRW.UpdateHound
local lastX=devices[id].pos.x
function SRW.UpdateHound(airId,bot,dt)
 if airId==id and (bot.BeamRemaining or 0)<=0 then
  assert(devices[id].pos.x~=lastX,'fire ran before aircraft movement; fresh bullet can self-hit')
  lastX=devices[id].pos.x
 end
 return sharedHound(airId,bot,dt)
end
for i=1,64 do SRW.UpdateAirRobot(id,b,.04) end
SRW.UpdateHound=sharedHound
local oldPosition=devices[id].pos
b.BeamRemaining=.25
SRW.UpdateAirRobot(id,b,.04)
assert(devices[id].pos==oldPosition and b.BeamRemaining<.25 and b.AirVelocity.x==0,
 'native burst stabilization lost: moving gun can hit its own hull')
assert(b.AirPhase=='egress','aircraft did not break off its attack')
local shots=fireCalls;SRW.UpdateMountedWeapons(.04);assert(fireCalls==shots,'egress launcher kept firing')
local entries=SRW.AirTargets(2);assert(#entries==1 and entries[1].IsDevice)
assert(SRW.AirTargetAlive(entries[1],2) and SRW.AirTargetVelocity(entries[1]).x==-100)
devices[8000]={team=101,kind='srw_aa_bot',built=true,pos=Vec3(0,0,0)}
data.srw.Robots[8000]={Team=101,Kind='srw_aa_bot',Direction=1}
function NodeExists(id) return id==9000 end
function NodeTeam(id) assert(id==9000);return 101 end
function NodePosition(id) return Vec3(0,-400,0) end
function NodeVelocity(id) return Vec3(0,-5000,0) end
function GetNodeProjectileSaveName() return 'srw_tank_aa_rocket' end
SRW.UpdateAABot(8000,data.srw.Robots[8000],.04)
assert(data.srw.Robots[8000].Target==7000 and data.srw.Robots[8000].TargetIsDevice,'AA missed aircraft')
local aimed
function SetMissileTarget(id,p) aimed=p end
SRW.GuidedLaunch(101,8000,9000);SRW.UpdateGuidance(.2)
assert(data.srw.GuidedMissiles[9000].Target==7000 and aimed.x>0,'AA missile treated device ID as node ID')
-- Both factory interfaces expose Hornet on their first page, without ground rows.
selectedId=50;localTeam=101;SRW.RefreshUI()
assert(visible.srw_single24_order and not visible.srw_order and not visible.srw_hound_order)
SRW.ClickUI('srw_squad_mode');SRW.RefreshUI()
assert(visible.srw_squad_add24 and not visible.srw_squad_add1)
''')
print('PASS: both sides, factory separation/platform/refund, single/squad costs, rollback, flight/EMP/egress, AA devices and guided identity, filtered menus')

from lupa import LuaRuntime
mat=LuaRuntime()
mat.execute('Materials={{SaveName="bracing",SupportsDevices=true,HitPoints=150,Node={Mass=1}}};Sprites={};path="srw"')
code=(r/'materials/building_materials.lua').read_text()
mat.execute(code);mat.execute(code)
mat.execute('assert(#Materials==2 and #Sprites==1);Materials[2].Node.Mass=2;assert(Materials[1].Node.Mass==1)')
print('PASS: aviation platform is registered once and does not mutate vanilla bracing')
