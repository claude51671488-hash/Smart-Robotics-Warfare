"""Gunship factory/reserve, independent armament, burst holds and self-clearance."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hornet.py'))['lua']
lua.execute(r'''
local kind='srw_skat_bot'
local cfg=SRW.Config.Robots[kind]
assert(SRW.RobotKinds[26]==kind and cfg.Air and cfg.Tier==1 and #cfg.Mounts==2)
assert(not SRW.Config.Robots.srw_skat_rockets.Guided)
local serial=10000;local failing=false;local created=0
function dlc2_CreateFloatingDevice(team,name,p,angle)
 created=created+1
 if failing and created==3 then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=name,built=true,pos=p};return serial
end
function NodeExists() return true end
function GetNodeProjectileSaveName() return 'srw_skat_rocket' end
function GetDeviceIdSide(side,index) return index==0 and 802 or 803 end
function GetLinkMaterialSaveName() return 'srw_air_platform' end
local fired={}
local nativeFire=FireWeaponWithPower
function FireWeaponWithPower(id,...)
 fired[id]=(fired[id] or 0)+1;return nativeFire(id,...)
end
for _,team in ipairs({101,102}) do
 local enemy=team==101 and 102 or 101
 local dir=team==101 and 1 or -1
 devices={
  [50]={team=team,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)},
  [51]={team=team,kind='srw_factory_ground_3',built=true,pos=Vec3(0,0,0)},
  [802]={team=enemy,kind='srw_hound',built=true,pos=Vec3(dir*3200,-250,0)},
  [803]={team=enemy,kind='srw_hornet_bot',built=true,pos=Vec3(dir*2800,-900,0)}}
 function GetDeviceCountSide(side) return side==enemy%100 and 2 or 0 end
 data.srw.Robots={};data.srw.MountedWeapons={};data.srw.Factories={};data.srw.GuidedMissiles={}
 balances[team]={metal=100000,energy=1000000}
 SRW.FactoryCreated(team,50,'srw_factory_air_1',0)
 SRW.FactoryCreated(team,51,'srw_factory_ground_3',0)
 SRW_OrderIndividual(team,51,26);assert(not data.srw.Factories[51][kind..'Queue'])
 SRW_OrderIndividual(team+100,50,26);assert(not data.srw.Factories[50][kind..'Queue'])
 SRW_OrderIndividual(team,50,26);SRW.UpdateFactories(.04)
 assert(balances[team].metal==99600 and balances[team].energy==996400)
 for i=1,450 do SRW.UpdateFactories(.04) end
 local f=data.srw.Factories[50]
 assert(f[kind..'Reserve']==1)
 created=0;failing=true;SRW_ReleaseIndividual(team,50,26)
 assert(f[kind..'Reserve']==1 and not next(data.srw.Robots) and not next(data.srw.MountedWeapons),'partial aircraft escaped rollback')
 created=0;failing=false;SRW_ReleaseIndividual(team,50,26)
 local id=next(data.srw.Robots);local bot=data.srw.Robots[id];local children={}
 for child,part in pairs(data.srw.MountedWeapons) do
  children[#children+1]=child;assert(part.Root==id and part.OffsetY<0,'turret must be below the pods')
 end
 assert(#children==2 and f[kind..'Reserve']==0)
 SRW.UpdateAirRobot(id,bot,.04);SRW.UpdateMountedWeapons(.04)
 assert(bot.Target==802 and fired[id],'ground support target missing')
 for _,child in ipairs(children) do assert(fired[child],'one rocket pod never fired') end
 SRW.GuidedLaunch(team,children[1],70000);assert(not next(data.srw.GuidedMissiles),'unguided rocket acquired seeker')
 -- End the root burst first: a child burst alone must still hold the aircraft.
 bot.BeamRemaining=0;bot.FireWait=3
 local part=data.srw.MountedWeapons[children[1]];part.BeamRemaining=.4
 local p=devices[id].pos
 SRW.UpdateAirRobot(id,bot,.04)
 assert(devices[id].pos==p and bot.AirVelocity.x==0,'airframe moved through its rocket salvo')
 bot.AirPhase='egress';bot.AirRemaining=2
 local shots=fireCalls
 for i=1,15 do SRW.UpdateAirRobot(id,bot,.04);SRW.UpdateMountedWeapons(.04) end
 assert(fireCalls==shots and devices[id].pos~=p and part.BeamRemaining==0,'egress stalled or fired')
 devices[id].disabled=true;p=devices[id].pos;shots=fireCalls
 for i=1,10 do SRW.UpdateAirRobot(id,bot,.04);SRW.UpdateMountedWeapons(.04) end
 assert(devices[id].pos==p and fireCalls==shots,'native EMP missed a module')
 devices[id].disabled=false
 -- A pod aimed straight through the lower turret is rejected on either side.
 local pod=children[1];local podCfg=SRW.Config.Robots.srw_skat_rockets
 devices[pod].pos=Vec3(-dir*400,-400,0);devices[id].pos=Vec3(0,0,0)
 devices[children[2]].pos=Vec3(-dir*800,-800,0)
 assert(not SRW.ShotClearsAircraft(pod,part,podCfg,Vec3(dir*800,800,0)))
 assert(SRW.ShotClearsAircraft(pod,part,podCfg,Vec3(dir*3200,-400,0)))
 f.ExitRemaining=0
 SRW_SquadEdit(team,50,24,1);SRW_SquadEdit(team,50,26,1);SRW_SquadStart(team,50)
 assert(math.abs(f.Squad.Speed-3.4)<.00001)
 assert(select(1,SRW.RobotCost(cfg,true))==440 and select(2,SRW.RobotCost(cfg,true))==3960)
 selectedId=50;localTeam=team;SRW.SquadEditorOpen=false;SRW.RefreshUI()
 assert(visible.srw_single26_order and visible.srw_single24_order)
 SRW.SquadEditorOpen=true;SRW.RefreshUI();assert(visible.srw_squad_add26)
 DeleteDeviceById(id);SRW.UpdateMountedWeapons(.04)
 assert(not next(data.srw.MountedWeapons) and not devices[children[1]] and not devices[children[2]],'orphan pods leaked')
end
''')
from lupa import LuaRuntime
for language in ('Russian','English'):
 loc=LuaRuntime();loc.execute('Device={};Weapon={}')
 base=r/'mods'/('language-'+language)
 for f in ('devices/strings.lua','weapons/strings.lua','srw_ui.lua'):
  loc.execute((base/f).read_text(encoding='utf-16').replace('L"','"'))
 assert loc.globals().SRW_UI.SingleType26 and loc.globals().Weapon.srw_skat_bot
print('PASS: Skat both sides, factory gates/costs/reserve rollback, three weapons, ground preference, no guidance, child burst hold/egress/EMP, own-module clearance, mixed squad, UI/localization and cleanup')
