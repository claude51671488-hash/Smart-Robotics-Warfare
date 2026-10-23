"""Prepared controller only; selective engine visibility/collision is NOT validated."""
from pathlib import Path
import sys
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime
l=LuaRuntime()
l.execute('''
SRW={};energy=100000;devices={
 [1]={Team=101,Kind='srw_cloak_generator',Structure=10},
 [2]={Team=201,Kind='mine',Structure=10},
 [3]={Team=101,Kind='mine',Structure=11},
 [4]={Team=102,Kind='mine',Structure=12}}
function DeviceExists(id) return devices[id]~=nil end
function GetDeviceType(id) return devices[id].Kind end
function GetDeviceTeamIdActual(id) return devices[id].Team end
function GetDeviceStructureId(id) return devices[id].Structure end
function GetDeviceCountSide() return 4 end
function GetDeviceIdSide(side,index) return index+1 end
function IsDeviceFullyBuilt() return true end
function DeviceDisabled(id) return devices[id].Disabled end
function GetTeamResources() return {energy=energy} end
function AddResources(team,cost) energy=energy+cost.energy end
function SetSideVisible() error('must never hide whole side') end
function GhostStructure() error('unverified cutscene API is not a backend') end
''')
l.execute((r/'experimental/cloak.lua').read_text())
l.execute('''
local C=SRW.Cloak
assert(C.Contains(1,2) and not C.Contains(1,3) and not C.Contains(1,4))
local s=C.New(101,1)
local ok,why=C.Start(101,1,s,nil)
assert(not ok and why=='native_backend_unverified' and energy==100000)
local restored=0
local adapter={SelectiveVisibility=true,SelectiveProjectileCollision=true,
 Apply=function(id,sid,tier) assert(sid==10);return {id=id,sid=sid} end,
 Refresh=function(token,id,sid) token.sid=sid;return true end,
 Restore=function(token) restored=restored+1 end}
assert(not C.Start(201,1,s,adapter),'ally may not spend owner resources')
assert(C.Start(101,1,s,adapter) and energy==92000 and s.Remaining==5)
assert(not C.TargetBlocked(1,s,102,2),'tier I has no targeting jammer')
assert(not C.Start(101,1,s,adapter) and energy==92000)
C.Update(1,s,6,adapter);assert(s.Remaining==0 and s.Cooldown==19 and restored==1)
devices[1].Kind='srw_cloak_generator_2';s=C.New(101,2)
assert(C.Start(101,1,s,adapter) and energy==74000)
assert(C.TargetBlocked(1,s,102,2) and not C.TargetBlocked(1,s,201,2))
devices[2].Structure=99
assert(not C.TargetBlocked(1,s,102,2),'detached structure remains hidden')
devices[3].Structure=10;assert(C.TargetBlocked(1,s,102,3))
devices[1].Disabled=true;C.Update(1,s,.04,adapter)
assert(s.Token==nil and s.Cooldown==15 and restored==2)
devices[1].Disabled=false;devices[1].Kind='srw_cloak_generator_3';s=C.New(101,3)
adapter.SelectiveProjectileCollision=false
assert(not C.Start(101,1,s,adapter) and energy==74000)
adapter.SelectiveProjectileCollision=true
devices[2].Kind='srw_cloak_generator_2'
assert(C.CountSide(101,1)==1 and not C.Start(101,1,s,adapter),'upgraded allied generator not counted')
devices[2].Kind='mine';assert(C.Start(101,1,s,adapter) and energy==54000)
devices[1]=nil;C.Update(1,s,.04,adapter)
assert(s.Token==nil and restored==3)
''')
print('PASS: strict connected scope, allied side limit, backend gating, timing/energy and restoration controller (native effect still unavailable)')
