"""Air cannon stabilization, target changes, EMP recovery and factory integration."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hornet.py'))['lua']
lua.execute(r'''
local kind='srw_sledge_bot'
local cfg=SRW.Config.Robots[kind]
assert(SRW.RobotKinds[25]==kind and cfg.Air and cfg.Domain=='air' and cfg.Tier==1)
assert(not cfg.Mounts and cfg.Range==9600 and cfg.HoverFire)
function GetLinkMaterialSaveName() return 'srw_air_platform' end
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return index==0 and 802 or 803 end
for _,team in ipairs({101,102}) do
 local enemy=team==101 and 102 or 101
 local direction=team==101 and 1 or -1
 devices={
  [50]={team=team,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)},
  [51]={team=team,kind='srw_factory_ground_3',built=true,pos=Vec3(0,0,0)},
  [802]={team=enemy,kind='srw_colossus_bot',built=true,pos=Vec3(direction*2400,-900,0)},
  [803]={team=enemy,kind='srw_hound',built=true,pos=Vec3(direction*2000,-900,0)}}
 function GetDeviceCountSide(side) return side==enemy%100 and 2 or 0 end
 data.srw.Robots={};data.srw.MountedWeapons={};data.srw.Factories={}
 balances[team]={metal=100000,energy=1000000}
 SRW.FactoryCreated(team,50,'srw_factory_air_1',0)
 SRW.FactoryCreated(team,51,'srw_factory_ground_3',0)
 SRW_OrderIndividual(team,51,25);assert(not data.srw.Factories[51][kind..'Queue'])
 SRW_OrderIndividual(team,50,25);SRW.UpdateFactories(.04)
 assert(balances[team].metal==99550 and balances[team].energy==995800)
 for i=1,500 do SRW.UpdateFactories(.04) end
 SRW_ReleaseIndividual(team,50,25)
 local id=next(data.srw.Robots);local bot=data.srw.Robots[id]
 assert(bot.Kind==kind and not next(data.srw.MountedWeapons),'unexpected defence gun')
 local shots=fireCalls
 SRW.UpdateAirRobot(id,bot,.04)
 assert(bot.Target==802 and fireCalls==shots,'heavy target preference or initial stabilization failed')
 local anchor=devices[id].pos
 for i=1,12 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(devices[id].pos==anchor and fireCalls==shots,'aircraft drifted or fired before stable')
 devices[802].team=team
 SRW.UpdateAirRobot(id,bot,.04)
 assert(bot.Target==803 and bot.DeployRemaining>.9 and fireCalls==shots,'target change bypassed stability')
 devices[id].disabled=true;SRW.UpdateAirRobot(id,bot,.04)
 assert(not bot.DeployPosition and not bot.DeployRemaining and bot.AirVelocity.x==0)
 devices[id].disabled=false
 for i=1,12 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(fireCalls==shots,'EMP recovery reused old stabilization')
 for i=1,20 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(fireCalls==shots+1,'single AP shot not fired after full stabilization')
 local x=devices[id].pos.x
 for i=1,20 do SRW.UpdateAirRobot(id,bot,.04) end
 assert((devices[id].pos.x-x)*direction~=0 and fireCalls==shots+1,'reload did not permit reposition')
 -- Mix both air types: mean speed and +10% charge use the common squad path.
 local f=data.srw.Factories[50]
 f.ExitRemaining=0
 SRW_SquadEdit(team,50,24,1);SRW_SquadEdit(team,50,25,1)
 SRW_SquadStart(team,50)
 assert(math.abs(f.Squad.Speed-3.3)<.00001 and #f.Squad.Items==2)
 local balance=balances[team].metal
 SRW.UpdateFactories(.04)
 assert(balance-balances[team].metal==385,'squad surcharge lost')
end
SRW.SquadEditorOpen=false;localTeam=102;selectedId=50;SRW.RefreshUI()
assert(visible.srw_single25_order and visible.srw_single24_order and not visible.srw_order)
''')
print('PASS: Sledge both sides, single production, heavy target priority, stable aim, target switch, EMP reset, reload movement, mixed air squad and menu')

# The engine loads device strings before the custom UI table exists.
from lupa import LuaRuntime
for language in ('Russian','English'):
 loc=LuaRuntime();loc.execute('Device={};Weapon={}')
 base=r/'mods'/('language-'+language)
 for file in ('devices/strings.lua','weapons/strings.lua','srw_ui.lua'):
  loc.execute((base/file).read_text(encoding='utf-16').replace('L"','"'))
 assert loc.globals().SRW_UI.SingleType25 and loc.globals().Weapon.srw_sledge_bot
print('PASS: both languages load device/weapon strings before custom UI initialization')
