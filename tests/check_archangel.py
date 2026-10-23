"""Tier-II air upgrade and independent cruiser weapon integration."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hornet.py'))['lua']
lua.execute(r'''
local cfg=SRW.Config.Robots.srw_archangel_bot
assert(SRW.RobotKinds[29]=='srw_archangel_bot' and cfg.Tier==2 and #cfg.Mounts==3)
function GetLinkMaterialSaveName() return 'srw_air_platform' end
function GetWeaponHardpointPosition(id) return devices[id].pos end
function NodeExists() return false end
local serial=10000;local failed=false
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(angle==90)
 if failed and kind=='srw_archangel_rockets' then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=kind,built=true,pos=p};return serial
end
function GetDeviceCountSide(side)
 local n=0;for _,d in pairs(devices) do if d.team%100==side then n=n+1 end end;return n
end
function GetDeviceIdSide(side,index)
 local ids={};for id,d in pairs(devices) do if d.team%100==side then ids[#ids+1]=id end end
 table.sort(ids);return ids[index+1]
end
function SRW.BeamTargets() return {} end
local shots={}
function SRW.FireRobotWeapon(id,cfg,aim,spread) shots[id]=(shots[id] or 0)+1;return 0 end
for _,team in ipairs({101,102}) do
 local enemy=team==101 and 102 or 101;local dir=team==101 and 1 or -1
 devices={[50]={team=team,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)},
 [60]={team=team,kind='srw_factory_ground_3',built=true,pos=Vec3(0,0,0)}}
 data.srw.Robots={};data.srw.MountedWeapons={};data.srw.Factories={};shots={}
 balances[team]={metal=100000,energy=1000000}
 SRW.FactoryCreated(team,50,'srw_factory_air_1',0);SRW.FactoryCreated(team,60,'srw_factory_ground_3',0)
 local f=data.srw.Factories[50]
 SRW_OrderIndividual(team,50,29);assert(not f.srw_archangel_botQueue,'tier I admitted cruiser')
 SRW_OrderIndividual(team,60,29);assert(not data.srw.Factories[60].srw_archangel_botQueue)
 f.srw_hornet_botReserve=1;f.CurrentType='srw_hornet_bot';f.Remaining=3
 f.SquadDraft={'srw_hornet_bot'};f.ExitRemaining=2
 devices[51]={team=team,kind='srw_factory_air_2',built=false,pos=Vec3(0,0,0)}
 SRW.FactoryCreated(team,51,'srw_factory_air_2',50);devices[50]=nil
 SRW.FactoryCreated(team,51,'srw_factory_air_2',50)
 assert(data.srw.Factories[51]==f and not data.srw.Factories[50] and f.Tier==2 and f.Domain=='air')
 assert(SRW.FactoryCapacity(f)==50 and #f.SquadDraft==1)
 SRW.UpdateFactories(1);assert(f.Remaining==3 and f.srw_hornet_botReserve==1)
 devices[51].built=true;SRW.UpdateFactories(3);assert(f.srw_hornet_botReserve==2)
 SRW_OrderIndividual(team+100,51,29);assert(not f.srw_archangel_botQueue)
 SRW_OrderIndividual(team,51,29);SRW.UpdateFactories(.04)
 assert(balances[team].metal==98900 and balances[team].energy==990000)
 for i=1,875 do SRW.UpdateFactories(.04) end
 assert(f.srw_archangel_botReserve==1)
 failed=true;SRW_ReleaseIndividual(team,51,29)
 assert(f.srw_archangel_botReserve==1 and not next(data.srw.Robots) and not next(data.srw.MountedWeapons),'partial launch consumed reserve')
 failed=false;SRW_ReleaseIndividual(team,51,29)
 local id=next(data.srw.Robots);local b=data.srw.Robots[id]
 assert(b.Kind=='srw_archangel_bot' and #SRW.SortedIds(data.srw.MountedWeapons)==3)
 local guns={};local aa
 for child,part in pairs(data.srw.MountedWeapons) do
  if part.AntiAir then aa=child else guns[#guns+1]=child end
  assert(devices[child].pos.y<devices[id].pos.y,'module obscures lower laser')
 end
 assert(aa and #guns==2,'AA role not propagated on air launch')
 devices[800]={team=enemy,kind='reactor',built=true,pos=Vec3(dir*5000,-900,0)}
 devices[801]={team=enemy,kind='srw_hound',built=true,pos=Vec3(dir*2400,-400,0)}
 devices[802]={team=enemy,kind='srw_hornet_bot',built=true,pos=Vec3(dir*3000,-1300,0)}
 -- Register enemy aircraft for the normal AirTargets snapshot.
 data.srw.Robots[802]={Team=enemy,Kind='srw_hornet_bot',AirVelocity={x=0,y=0}}
 for i=1,80 do SRW.UpdateAirRobot(id,b,.04);SRW.UpdateMountedWeapons(.04) end
 assert((shots[id] or 0)>0 and (shots[guns[1]] or 0)>0 and (shots[guns[2]] or 0)>0 and (shots[aa] or 0)>0,'one weapon never fired')
 assert(data.srw.MountedWeapons[aa].Target==802 and data.srw.MountedWeapons[aa].TargetIsDevice,'AA targets ground or wrong identity')
 b.BeamRemaining=1;b.FireWait=8;b.AirPhase='attack';local p=devices[id].pos
 SRW.UpdateAirRobot(id,b,.04)
 assert(devices[id].pos==p and b.BeamRemaining<1 and b.AirVelocity.x==0,'beam drift')
 local missileShots=shots[aa];b.EMPRemaining=2
 data.srw.MountedWeapons[aa].FireWait=0;data.srw.MountedWeapons[aa].BeamRemaining=0
 SRW.UpdateMountedWeapons(.04);assert(shots[aa]==missileShots,'EMP failed to stop guided launcher')
 f.ExitRemaining=0;f.SquadDraft={'srw_archangel_bot','srw_hornet_bot'}
 SRW_SquadStart(team,51);assert(math.abs(f.Squad.Speed-2.9)<.00001)
 local money=balances[team].metal;SRW.UpdateFactories(.04)
 assert(money-balances[team].metal==1210,'squad surcharge lost')
 devices[id]=nil;SRW.UpdateMountedWeapons(.04)
 assert(not next(data.srw.MountedWeapons),'orphaned cruiser guns')
end
-- Factory title and both purchase paths follow the upgraded tier.
SRW.SquadEditorOpen=false;localTeam=102;selectedId=51
local f=data.srw.Factories[51]
SRW.RefreshUI();assert(texts.srw_title=='$SRW_UI.AirFactoryTier2')
for i=1,3 do
 if visible.srw_single29_order then break end
 SRW.ClickUI('srw_page')
end
assert(visible.srw_single29_order and visible.srw_single29_release and visible.srw_price29)
f.Tier=1;SRW.RefreshUI();assert(not visible.srw_single29_order and not visible.srw_price29)
f.Tier=2;SRW.ClickUI('srw_squad_mode');SRW.RefreshUI()
for i=1,3 do
 if visible.srw_squad_add29 then break end
 SRW.ClickUI('srw_squad_page')
end
assert(visible.srw_squad_add29)
Devices={};Sprites={}
''')
lua.execute((r/'devices/device_list.lua').read_text())
lua.execute('''
local defs={};for _,d in ipairs(Devices) do defs[d.SaveName]=d end
assert(defs.srw_factory_air_1.Upgrades.srw_factory_air_2.MetalCost==1000)
assert(not defs.srw_factory_air_2.Enabled and defs.srw_factory_air_2.BuildTimeComplete==30)
assert(not defs.srw_factory_air_2.Upgrades)
''')
print('PASS: Archangel both sides, tier/domain gates, upgrade state/pause/reserve, four independent guns, mirrored layout, hover, EMP missiles, squad cost/speed, failed spawn rollback and cleanup')
