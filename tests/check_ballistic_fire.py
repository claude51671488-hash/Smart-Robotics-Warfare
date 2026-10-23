"""Numerical impact positions, moving lead and bounded trajectory obstruction."""
from pathlib import Path
import sys
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime
l=LuaRuntime()
l.execute('''
SRW={}; function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function GetDeviceCentrePosition() return Vec3(0,0,0) end
function GetWeaponHardpointPosition() return Vec3(130,-85,0) end
function GetRandomFloat(a,b,context) return 0 end
RAY_HIT_NOTHING=0;RAY_HIT_TERRAIN=1
''')
l.execute((r/'scripts/combat/aiming.lua').read_text())
l.execute('''
local origin=Vec3(130,-85)
local function near(a,b) assert(math.abs(a-b)<.001,tostring(a).." != "..tostring(b)) end
for _,side in ipairs({-1,1}) do
 for _,distance in ipairs({250,2000,8000,11000}) do
  for _,height in ipairs({-900,0,300}) do
   local target=Vec3(origin.x+side*distance,origin.y+height)
   local speed=6000
   local t=assert(SRW.BallisticFlight(origin,target,speed,981))
   local vx=(target.x-origin.x)/t
   local vy=(target.y-origin.y)/t-.5*981*t
   near(math.sqrt(vx*vx+vy*vy),speed)
   near(origin.x+vx*t,target.x)
   near(origin.y+vy*t+.5*981*t*t,target.y)
   assert(vy<height/t,'missing upward compensation')
  end
 end
end
assert(not SRW.BallisticFlight(origin,Vec3(50000,-1000),3500,981))
for _,vx in ipairs({-150,150}) do
 local target=Vec3(4000,-400)
 local q,t=SRW.BallisticIntercept(origin,target,Vec3(vx,20),6000,981,5)
 near(q.x,target.x+vx*t);near(q.y,target.y+20*t)
 local actual=SRW.BallisticFlight(origin,q,6000,981)
 assert(math.abs(actual-t)<.001)
end
local count=0;local obstacle=false
function CastGroundRay(a,b)
 count=count+1
 if count==1 then assert(a.x==130 and a.y==-85,'not using muzzle') end
 if obstacle and count==3 then return RAY_HIT_TERRAIN end
 return RAY_HIT_NOTHING
end
assert(SRW.ShotClearsTerrain(1,{BulletSpeed=6000},Vec3(4000,-500)))
assert(count==6)
count=0;obstacle=true
assert(not SRW.ShotClearsTerrain(1,{BulletSpeed=6000},Vec3(4000,-500)))
assert(count==3)
-- An instantaneous beam must never lead a moving target.
local bot={CombatClock=1}
local target={Id=99,Position=Vec3(1000,-200),Distance=1040000}
local cfg={BeamWeapon=true}
SRW.AimSolution(1,bot,cfg,target,.04,false)
bot.CombatClock=1.04;target.Position=Vec3(1004,-198)
local q,spread=SRW.AimSolution(1,bot,cfg,target,.04,false)
near(q.x,1004);near(q.y,-198);assert(spread==0)
''')
print('PASS: both-side/elevated ballistic impacts, moving intercept, muzzle origin, terrain arc and instant beam')
