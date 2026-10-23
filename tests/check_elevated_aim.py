from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
lua.execute((r/'scripts/combat/aiming.lua').read_text())
lua.execute('''
devices={[900]={team=101,kind='srw_hound',built=true,pos=Vec3(0,0,0)},
 [901]={team=102,kind='mine',built=true,pos=Vec3(3000,-800,0)}}
data.srw.Robots={[900]={Team=101,Kind='srw_hound',Direction=1,Age=0}}
data.srw.MountedWeapons={};beamFixtures={}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide() return 901 end
local terrain=false;local shots=0;local aim
function CastGroundRay(a,b)
 rayGroundX=a.x
 if a.x~=b.x then return terrain and RAY_HIT_TERRAIN or RAY_HIT_NOTHING end
 return RAY_HIT_TERRAIN
end
function AimWeapon(id,p) aim=p;return true end
function FireWeapon(id,p,spread)
 shots=shots+1;aim=p;assert(spread>0);return 0
end
SRW.UpdateRobots(.04)
local t=SRW.BallisticFlight(Vec3(0,0,0),devices[901].pos,6000,981)
assert(shots==1 and math.abs(aim.y-(-800-.5*981*t*t))<.001,
 'direct gun lost target elevation or compensated gravity twice')
terrain=true;data.srw.Robots[900].FireWait=0
SRW.UpdateRobots(.04);assert(shots==1,'direct gun fired into hillside')
terrain=false;devices[901].kind='wheel';devices[901].pos=Vec3(2000,0,0)
beamFixtures={{Vec3(1950,-200,0),Vec3(2200,-200,0),team=2}}
-- Use an explicit chassis target to isolate selection from engine enumeration.
SRW.BeamTargets=function() return {{Id=-1,Beam=true,Position=Vec3(2000,-200,0),Distance=4040000,Priority=2}} end
SRW.UpdateRobots(.04)
assert(data.srw.Robots[900].Target==-1 and aim.y<0,'wheel won over raised chassis')
''')
print('PASS: integrated aiming retains target elevation, refuses hillside shot, prefers chassis over wheels')
