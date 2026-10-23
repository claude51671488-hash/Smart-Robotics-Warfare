"""Recorded-flight regressions: closing AA fire, complete loops and target loss."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hornet_art_sortie.py'))['lua']
lua.execute('''
function SRW.UpdateAirWeapon() end
local incoming=false
function SRW.AirTargets(side)
 local p=devices[500].pos
 local toward=p.x<0 and 1 or -1
 return {{Id=900,Position=Vec3(p.x+toward*300,p.y,0)}}
end
function SRW.AirTargetAlive() return true end
function SRW.AirTargetVelocity()
 local p=devices[500].pos;local toward=p.x<0 and 1 or -1
 return {x=(incoming and -1 or 1)*toward*3000,y=0}
end
function SRW.DeviceTargets() return {{Id=800,Kind='gun',Position=Vec3(0,0,0)}} end
local cfg=SRW.Config.Robots.srw_hornet_bot
for _,team in ipairs({101,102}) do
 local dir=team==101 and 1 or -1
 devices={[500]={team=team,kind='srw_hornet_bot',built=true,pos=Vec3(-dir*900,-1000,0)},
          [800]={team=team==101 and 102 or 101,kind='gun',built=true,pos=Vec3(0,0,0)}}
 local b={Team=team,Kind='srw_hornet_bot',Direction=dir,Mounted=true,
          HomeX=-dir*5000,CruiseY=-900,AirVelocity={x=dir*510,y=0}}
 data.srw.Robots={[500]=b};data.srw.MountedWeapons={}
 incoming=false
 SRW.UpdateSortieFlight(500,b,.04)
 assert((b.EvadeRemaining or 0)==0,'receding round triggered a dodge')
 incoming=true;b.EvadeScan=0
 local p=devices[500].pos;local original=math.sqrt(p.x*p.x+p.y*p.y)
 SRW.UpdateSortieFlight(500,b,.04)
 assert(b.SortiePhase=='egress' and b.EvadeRemaining>0,'closing round ignored')
 local maximum=original
 for i=1,250 do
  local p=devices[500].pos;local heading=b.SortieHeading
  SRW.UpdateSortieFlight(500,b,.04)
  local q=devices[500].pos
  assert(math.abs(math.sqrt((q.x-p.x)^2+(q.y-p.y)^2)-20.4)<.001,'hover during evasion')
  assert(math.abs(b.SortieHeading-heading)<=cfg.SortieTurnRate*.04+.00001,'snap dodge')
  assert(b.SortiePhase~='attack','attacked into continuing AA fire')
  maximum=math.max(maximum,math.sqrt(q.x*q.x+q.y*q.y))
 end
 assert(maximum>original+1500,'AA dodge did not open distance')
 assert(b.SortieSafetyExtra<=cfg.OrbitStandOff,'unbounded safety distance')
 incoming=false
 local entered=false;local complete=false;local centreX,centreY
 for i=1,3000 do
  local previous=b.SortiePhase
  SRW.UpdateSortieFlight(500,b,.04)
  if b.SortiePhase=='orbit' then
   entered=true
   if centreX then assert(b.SortieOrbitX==centreX and b.SortieOrbitY==centreY,'orbit centre moved') end
   centreX,centreY=b.SortieOrbitX,b.SortieOrbitY
  end
  if previous=='orbit' and b.SortiePhase=='approach' then
   assert(b.SortieOrbitSweep>=2*math.pi,'loop abandoned before one revolution')
   complete=true;break
  end
 end
 assert(entered and complete,'no return after fire ceased')
end
-- Device targets and the 129th projectile must not trigger an unbounded scan.
local originalTargets=SRW.AirTargets
local originalVelocity=SRW.AirTargetVelocity
local velocityQueries=0
function SRW.AirTargets()
 local p=devices[500].pos;local entries={{Id=1000,IsDevice=true,Position=p}}
 for i=1,129 do entries[#entries+1]={Id=i,Position=Vec3(p.x+300,p.y,0)} end
 return entries
end
function SRW.AirTargetVelocity(entry)
 velocityQueries=velocityQueries+1
 return {x=entry.Id==129 and -3000 or 3000,y=0}
end
local b=data.srw.Robots[500]
b.EvadeScan=0;b.EvadeRemaining=0;b.AirVelocity={x=0,y=0}
SRW.UpdateSortieFlight(500,b,.04)
assert(velocityQueries==128 and b.EvadeRemaining==0,'unbounded scan or aircraft treated as projectile')
SRW.AirTargets=originalTargets;SRW.AirTargetVelocity=originalVelocity
-- Losing the attack target must preserve the established waiting loop.
b.SortiePhase='orbit';b.SortieOrbitX=1234;b.SortieOrbitY=-2345
b.SortieOrbitObserved=nil;b.SortieOrbitSweep=nil
function SRW.DeviceTargets() return {} end
for i=1,20 do SRW.UpdateSortieFlight(500,b,.04) end
assert(b.SortieOrbitX==1234 and b.SortieOrbitY==-2345,'target loss snapped orbit back home')
''')
print('PASS: both teams reject receding shots, evade closing fire, increase range, complete a loop and return after AA clears')
