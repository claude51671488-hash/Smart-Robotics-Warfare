"""Shared laser, transactional production, bounded evasive flight and moving bursts."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_skat.py'))['lua']
lua.execute(r'''
local cfg=SRW.Config.Robots.srw_lantern_bot
assert(SRW.RobotKinds[27]=='srw_lantern_bot' and cfg.AirDefenceLaser and cfg.Range==7200)
devices={[50]={team=101,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)},
 [51]={team=101,kind='srw_factory_ground_3',built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={};data.srw.MountedWeapons={};data.srw.Factories={}
balances[101]={metal=100000,energy=1000000}
SRW.FactoryCreated(101,50,'srw_factory_air_1',0)
SRW.FactoryCreated(101,51,'srw_factory_ground_3',0)
SRW_OrderIndividual(101,51,27);assert(not data.srw.Factories[51].srw_lantern_botQueue)
SRW_OrderIndividual(101,50,27);SRW.UpdateFactories(.04)
assert(balances[101].metal==99580 and balances[101].energy==996000)
for i=1,450 do SRW.UpdateFactories(.04) end
SRW_ReleaseIndividual(101,50,27)
local id=next(data.srw.Robots);local bot=data.srw.Robots[id]
assert(bot.Kind=='srw_lantern_bot' and not next(data.srw.MountedWeapons))
local aa,ground=0,0
local threat=true
function SRW.UpdateAABot(id,b,dt) aa=aa+1;if threat then b.Target=700;b.BeamRemaining=1.25;b.FireWait=1.5 end end
function SRW.UpdateHound(id,b,dt) ground=ground+1;b.Target=800;b.BeamRemaining=1.25;b.FireWait=1.5 end
SRW.UpdateAirWeapon(id,bot,.04)
assert(aa==1 and ground==0 and bot.LaserMode=='air')
for i=1,30 do SRW.UpdateAirWeapon(id,bot,.04) end
assert(aa==1 and ground==0,'beam switched while still active')
bot.BeamRemaining=0;bot.FireWait=.2;bot.Target=800;threat=false
SRW.UpdateAirWeapon(id,bot,.04);assert(aa==1 and math.abs(bot.FireWait-.16)<.00001)
bot.FireWait=0;SRW.UpdateAirWeapon(id,bot,.04)
assert(aa==2 and ground==1 and bot.LaserMode=='ground','stale target prevented fallback')
-- Exercise movement separately from gun selection.
function SRW.UpdateAirWeapon() end
function SRW.DeviceTargets() return {} end
function CastGroundRay() return RAY_HIT_NOTHING end
function CastRayFromDevice() return RAY_HIT_NOTHING end
SRW.MovementRay=CastRayFromDevice
local incoming=true
function SRW.AirTargets()
 local p=devices[id].pos
 return {{Id=900,IsDevice=false,Position=Vec3(p.x+400,p.y,0)}}
end
function SRW.AirTargetAlive() return true end
function SRW.AirTargetVelocity() return {x=incoming and -1000 or 1000,y=0} end
bot.BeamRemaining=0;bot.FireWait=0;bot.Target=nil;bot.AirPhase='cruise';bot.AirSteer=1
bot.AirHeading=-1;bot.Direction=-1;bot.HomeX=devices[id].pos.x
bot.AirVelocity={x=0,y=0};bot.EvadeScan=0
local p=devices[id].pos
SRW.UpdateAirRobot(id,bot,.04)
assert(bot.AirSteer>0 and bot.AirSteer<1,'instant velocity reversal')
assert(bot.EvadeRemaining>0 and devices[id].pos.y<p.y,'approaching shot did not trigger evasion')
assert(math.abs(devices[id].pos.y-p.y)<=cfg.ClimbSpeed*.04+.00001)
incoming=false;bot.EvadeRemaining=0;bot.EvadeScan=0;bot.AirVelocity={x=0,y=0}
SRW.UpdateAirRobot(id,bot,.04);assert(bot.EvadeRemaining==0,'fleeing shot triggered dodge')
devices[id].disabled=true;p=devices[id].pos
SRW.UpdateAirRobot(id,bot,.04);assert(devices[id].pos==p,'EMP aircraft moved')
''')
print('PASS: Lantern production/cost/domain, shared emitter priority/cooldown, ground fallback, curved reversal, incoming/receding shot evasion, bounded climb and EMP')
