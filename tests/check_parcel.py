"""Bomber lifecycle and drop lead on both teams; no replenishment away from base."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hornet.py'))['lua']
lua.execute((r/'scripts/robots/parcel.lua').read_text())
lua.execute(r'''
local cfg=SRW.Config.Robots.srw_parcel_bot
assert(SRW.RobotKinds[28]=='srw_parcel_bot' and cfg.Bomber)
function CastGroundRay() return RAY_HIT_NOTHING end
function CastRayFromDevice() return RAY_HIT_NOTHING end
SRW.MovementRay=CastRayFromDevice
function IsCloaked() return false end
for _,team in ipairs({101,102}) do
 local enemy=team==101 and 102 or 101
 local dir=team==101 and 1 or -1
 devices={[50]={team=team,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)},
 [51]={team=team,kind='srw_factory_ground_3',built=true,pos=Vec3(0,0,0)},
 [800]={team=enemy,kind='mine',built=true,pos=Vec3(dir*3000,0,0)}}
 function SRW.DeviceTargets(side)
  local t={};for id,d in pairs(devices) do if d.team%100==side then
   t[#t+1]={Id=id,Kind=d.kind,Position=d.pos} end end;return t
 end
 data.srw.Robots={};data.srw.MountedWeapons={};data.srw.Factories={}
 balances[team]={metal=100000,energy=1000000}
 SRW.FactoryCreated(team,50,'srw_factory_air_1',0)
 SRW.FactoryCreated(team,51,'srw_factory_ground_3',0)
 SRW_OrderIndividual(team,51,28);assert(not data.srw.Factories[51].srw_parcel_botQueue)
 SRW_OrderIndividual(team,50,28);SRW.UpdateFactories(.04)
 assert(balances[team].metal==99500 and balances[team].energy==995500)
 for i=1,550 do SRW.UpdateFactories(.04) end
 SRW_ReleaseIndividual(team,50,28)
 local id=next(data.srw.Robots);local bot=data.srw.Robots[id]
 assert(bot.Kind=='srw_parcel_bot' and not next(data.srw.MountedWeapons))
 local drops=0;local fail=true;local rearmed=false
 function dlc2_CreateProjectile(name,weapon,owner,p,v,age)
  assert(name=='srw_parcel_bomb' and owner==team and v.x*dir>0 and age==20)
  if fail then return -1 end
  drops=drops+1
  local h=devices[800].pos.y-p.y
  local t=(-v.y+math.sqrt(v.y*v.y+2*981*h))/981
  assert(math.abs(p.x+v.x*t-devices[800].pos.x)<110,'drop missed its stationary target')
  return 9000+drops
 end
 for i=1,600 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(drops==0 and bot.BombReady,'failed projectile consumed payload')
 fail=false
 for i=1,1300 do
  SRW.UpdateAirRobot(id,bot,.04)
  if bot.AirPhase=='rearming' then rearmed=true end
  if drops==2 then break end
 end
 assert(drops==2 and rearmed and not bot.BombReady,'no full drop-return-rearm-drop cycle')
 devices[50]=nil
 for i=1,500 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(drops==2 and not bot.BombReady and bot.AirPhase=='waiting_factory','remote ammo regeneration')
 devices[52]={team=team+100,kind='srw_factory_air_1',built=true,pos=Vec3(0,0,0)}
 devices[id].disabled=true;local p=devices[id].pos;local wait=bot.BombReload
 for i=1,100 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(devices[id].pos==p and bot.BombReload==wait,'EMP did not freeze aircraft')
 devices[id].disabled=false
 for i=1,300 do SRW.UpdateAirRobot(id,bot,.04) end
 assert(bot.HomeFactory==52 and bot.BombReady,'allied replacement factory not used')
end
devices={[900]={team=101,kind='srw_parcel_bot',built=true,pos=Vec3(-2500,-1200,0)},
 [800]={team=102,kind='mine',built=true,pos=Vec3(0,0,0)}}
local movingBot={Team=101,Kind='srw_parcel_bot',Direction=1,CruiseY=-1200,HomeX=-2500}
data.srw.Robots={[900]=movingBot}
local movingDrop=false
function dlc2_CreateProjectile(name,weapon,team,p,v,age)
 local t=(-v.y+math.sqrt(v.y*v.y+2*981*(devices[800].pos.y-p.y)))/981
 assert(math.abs(p.x+v.x*t-(devices[800].pos.x+60*t))<110,'moving target lead lost')
 movingDrop=true;return 9500
end
for i=1,800 do
 devices[800].pos.x=devices[800].pos.x+60*.04
 SRW.UpdateAirRobot(900,movingBot,.04)
 if movingDrop then break end
end
assert(movingDrop,'moving vehicle was never bombed')
''')
print('PASS: Parcel factory gating, exact cost/reserve, failed drop retained, two full sorties both teams, destroyed factory, allied replacement and EMP')
