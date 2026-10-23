"""Bounded Lua state and repeated engine reads; not a Forts process profiler."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'.srw-tools'))
from lupa import LuaRuntime
lua=LuaRuntime()
lua.execute('''
SRW={Config={Robots={}}};data={}; count=200; reads=0; airReads=0
function Vec3(x,y,z) return {x=x,y=y,z=z} end
function GetDeviceCountSide() return count end
function GetDeviceIdSide(side,i) reads=reads+1;return i+1 end
function DeviceExists(id) return id<=count end
function GetDeviceTeamIdActual() return 102 end
function GetDeviceType() return 'mine' end
function GetDeviceCentrePosition(id) return Vec3(id,0,0) end
function ProjectileCount() return count end
function GetProjectileId(side,i) airReads=airReads+1;return i+1 end
function NodeExists(id) return id<=count end
function NodePosition(id) return Vec3(id,0,0) end
function NodeTeam() return 102 end
function GetNodeProjectileSaveName() return 'srw_hunter_at_rocket' end
function NodeVelocity() return Vec3(100,0,0) end
function SetMissileTarget() end
function SRW.SortedIds(t) local ids={};for id in pairs(t) do ids[#ids+1]=id end;table.sort(ids);return ids end
''')
for f in ['state.lua','combat/guidance.lua','shields.lua']:
    lua.execute((root/'scripts'/f).read_text(encoding='utf-8'))
lua.execute('''
SRW.EnsureState()
SRW.BeginCombatSnapshot()
for gun=1,80 do assert(#SRW.DeviceTargets(2)==200 and #SRW.AirTargets(2)==200) end
assert(reads==200 and airReads==200, 'each side is enumerated once per combat tick')
SRW.EndCombatSnapshot()
count=0
assert(#SRW.DeviceTargets(2)==0 and #SRW.AirTargets(2)==0, 'no cached destroyed entities outside tick')
-- Many battles/waves with unique IDs: obsolete snapshots and guided shots must die.
collectgarbage('collect');local baseline=collectgarbage('count')
for wave=1,10000 do
 count=40; SRW.BeginCombatSnapshot(); SRW.DeviceTargets(2); SRW.AirTargets(2)
 SRW.EndCombatSnapshot()
 data.srw.GuidedMissiles[wave+100]={Team=102,Name='srw_hunter_at_rocket',Age=0}
 SRW.UpdateGuidance(.04)
 assert(next(data.srw.GuidedMissiles)==nil)
end
collectgarbage('collect')
assert(collectgarbage('count')-baseline<128, 'retained Lua memory grows with wave history')
-- Segment math must not allocate vectors for every projectile/segment pair.
local a,b,c,d=Vec3(0,0,0),Vec3(10,0,0),Vec3(5,-5,0),Vec3(5,5,0)
collectgarbage('collect');local before=collectgarbage('count');collectgarbage('stop')
for i=1,100000 do assert(SRW.ShieldIntersection(a,b,c,d)==.5) end
local allocated=collectgarbage('count')-before;collectgarbage('restart')
assert(allocated<128, 'intersection allocates temporary tables')
''')
print('PASS: 80 consumers share 200 reads, 10000 waves retain <128 KiB, 100000 shield tests allocate <128 KiB')
