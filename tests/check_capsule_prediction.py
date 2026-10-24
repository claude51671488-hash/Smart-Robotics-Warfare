"""Prediction fallback must be local, timely, deduplicated and cancelled by AA."""
from pathlib import Path
import sys
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime
lua=LuaRuntime()
lua.execute("""
SRW={Config={Matryoshka={DeploySeconds=2.4}},SortedIds=function(t)
 local keys={};for k in pairs(t) do keys[#keys+1]=k end;table.sort(keys);return keys end}
data={srw={CapsuleFlights={},CapsuleTurrets={}}};nodes={};devices={};serial=100
RAY_HIT_TERRAIN=1;DESTROYTYPE_HITTERRAIN=3;DESTROYTYPE_HITDEVICE=4;DESTROYTYPE_EXPIRED=6
function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function Log() end
local hit
function CastGroundRay(a,b)
 if a.y<=0 and b.y>=0 and b.y>a.y then
  local t=-a.y/(b.y-a.y);hit=Vec3(a.x+(b.x-a.x)*t,0);return 1
 end
 return 0
end
function GetRayHitPosition() return hit end
function NodeExists(id) return nodes[id] and not nodes[id].Retired end
function NodePosition(id) assert(nodes[id],'read missing node');return nodes[id].Position end
function NodeVelocity(id) return nodes[id].Velocity end
function GetNodeProjectileSaveName() return 'srw_kolokol_capsule' end
function EnableWeapon() end
function EnableDevice() end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 serial=serial+1;devices[serial]={Team=team,Position=p};return serial
end
function DeviceExists(id) return devices[id]~=nil end
function GetDeviceTeamIdActual(id) return devices[id].Team end
function DeviceDisabled() return false end
function IsDeviceFullyBuilt() return false end
function SetWeaponReloadTime(id,progress) assert(progress==0) end
function launch(id)
 data.srw.CapsuleFlights={};data.srw.CapsuleTurrets={};devices={}
 nodes[id]={Position=Vec3(300,-500),Velocity=Vec3(0,5000)}
 SRW.TrackCapsule(101,id)
end
function waitMissing() for i=1,6 do SRW.UpdateCapsules(.04) end end
""")
lua.execute((r/'scripts/matryoshka.lua').read_text())
lua.execute("""
launch(1)
local plan=data.srw.CapsuleFlights[1].Landing
local exact=(-5000+math.sqrt(5000^2+2*981*500))/981
assert(plan and plan.x==300 and plan.y==0 and math.abs(plan.At-exact)<.001)
nodes[1].Position=Vec3(300,-10);SRW.UpdateCapsules(.1)
nodes[1].Retired=true;waitMissing()
local id=next(data.srw.CapsuleTurrets)
assert(id and devices[id].Position.y==0,'near-ground timed disappearance lost delivery')
local count=serial
SRW.CapsuleImpact(1,101,'srw_kolokol_capsule',3,Vec3(300,0))
assert(serial==count,'late native callback duplicated predicted delivery')
launch(2);nodes[2].Position=Vec3(300,-10);SRW.UpdateCapsules(.1)
nodes[2].Retired=true;SRW.CapsuleImpact(2,101,'srw_kolokol_capsule',4)
waitMissing();assert(not next(data.srw.CapsuleTurrets),'AA destruction granted a turret')
launch(3);nodes[3].Position=Vec3(300,-200);SRW.UpdateCapsules(.03)
nodes[3].Retired=true;waitMissing();assert(not next(data.srw.CapsuleTurrets),'midair disappearance granted a turret')
launch(4);nodes[4].Position=Vec3(330,30);SRW.UpdateCapsules(.1)
assert(data.srw.CapsuleFlights[4].Contact,'last segment failed to witness terrain')
nodes[4]=nil;waitMissing();id=next(data.srw.CapsuleTurrets)
assert(id and devices[id].Position.y==0,'witnessed contact required reading a deleted node')
launch(5);nodes[5].Retired=true;SRW.CapsuleImpact(5,101,'srw_kolokol_capsule',6)
waitMissing();assert(not next(data.srw.CapsuleTurrets),'expiry granted a turret')
""")
print('PASS: ballistic arrival, short-range missing callback fallback, witnessed contact, no invalid node read, late deduplication, AA/expiry/midair cancellation')
