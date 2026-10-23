from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.srw-tools'))
from lupa import LuaRuntime
r=Path(__file__).resolve().parents[1]
lua=LuaRuntime()
lua.execute("""
SRW={};FIREFLAG_NORMAL=0;FIREFLAG_DIRECTAIM=32
function Vec3(x,y,z) return {x=x,y=y,z=z} end
function GetWeaponHardpointPosition(id) return Vec3(0,0,0) end
function GetDeviceTeamIdActual(id) return 102 end
function GetDeviceType(id) return 'test' end
function GetWeaponMaxFireSpeed(team,kind) assert(team==102 and kind=='test');return 6000 end
function AimWeapon(id,p) aimCalls=(aimCalls or 0)+1;return true end
function FireWeaponWithPower(id,p,spread,testSpread,flags,power)
 assert(flags==32 and power==1 and testSpread==-1);last=p;return 0
end
function FireWeapon(id,p,spread,flags) assert(flags==0);last=p;return 0 end
function SRW.LaunchAim(id,cfg,p) return p end
""")
lua.execute((r/'scripts/combat/aiming.lua').read_text())
lua.execute("""
local cfg={BulletSpeed=1}
for _,dx in ipairs({-6000,-3500,3500,6000}) do
 for _,dy in ipairs({-700,0,700}) do
  local target=Vec3(dx,dy,0)
  assert(SRW.CanAimRobotWeapon(1,cfg,target))
  assert(SRW.FireRobotWeapon(1,cfg,target,.1)==0)
  local length=math.sqrt(last.x^2+last.y^2)
  local vx,vy=last.x/length*6000,last.y/length*6000
  local t=dx/vx
  assert(t>0 and math.abs(vy*t+.5*981*t*t-dy)<.001,'trajectory misses target')
 end
end
assert(not aimCalls,'direct guns re-entered native ballistic search')
assert(not SRW.CanAimRobotWeapon(1,cfg,Vec3(1000000,0,0)))
assert(SRW.CanAimRobotWeapon(1,{Artillery=true},Vec3(-3500,0,0)))
assert(aimCalls==1)
SRW.FireRobotWeapon(1,{Artillery=true},Vec3(-3500,0,0),0)
assert(last.x==-3500 and last.y==0,'artillery was compensated twice')
SRW.FireRobotWeapon(1,{BeamWeapon=true},Vec3(-3500,700,0),0)
assert(last.y==700,'laser received shell drop')
""")
print('PASS: native speed, mirrored low arcs, high/low targets, unreachable target, no double drop, artillery/laser isolation')
