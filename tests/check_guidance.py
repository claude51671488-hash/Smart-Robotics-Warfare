from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_rocket.py'))['lua']
for name in ['robots/aa.lua','combat/guidance.lua']:
 lua.execute((r/'scripts'/name).read_text())
lua.execute('''
SRW.EnsureState()
local nodes={
 [100]={team=101,name="srw_salvo_rocket",pos=Vec3(0,0,0),vel=Vec3(2500,0,0)},
 [101]={team=101,name="srw_tank_aa_rocket",pos=Vec3(0,0,0),vel=Vec3(5000,0,0)},
 [200]={team=102,name="cannon",pos=Vec3(1000,-100,0),vel=Vec3(-100,0,0)}}
function NodeExists(id) return nodes[id]~=nil end
function NodeTeam(id) return nodes[id].team end
function NodePosition(id) return nodes[id].pos end
function NodeVelocity(id) return nodes[id].vel end
function GetNodeProjectileSaveName(id) return nodes[id].name end
local targets={}
function SetMissileTarget(id,p) targets[id]=p end
function SpawnLine(...) error("guidance must not draw lines") end
function SpawnCircle(...) error("guidance must not draw trackers") end
devices={[1]={team=101,kind="srw_rocket_bot",built=true,pos=Vec3(0,0,0)},
 [2]={team=102,kind="mine",built=true,pos=Vec3(1000,0,0)},
 [3]={team=101,kind="srw_tank_rockets",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={[1]={Team=101,Kind="srw_rocket_bot",Target=2,Direction=1}}
data.srw.MountedWeapons={[3]={Team=101,Kind="srw_tank_rockets",Target=200,AntiAir=true,Root=1}}
SRW.GuidedLaunch(201,1,100); assert(not data.srw.GuidedMissiles[100])
SRW.GuidedLaunch(101,1,100); SRW.UpdateGuidance(.04); assert(targets[100].x==1000)
devices[2].pos=Vec3(1200,50,0); SRW.UpdateGuidance(.04); assert(targets[100].x==1200)
SRW.GuidedLaunch(101,3,101); SRW.UpdateGuidance(.04)
assert(targets[101].x<1000 and targets[101].x>900 and targets[101].y==-100)
nodes[200].team=101; SRW.UpdateGuidance(.04)
assert(not data.srw.GuidedMissiles[101].Target and targets[101].x==50000)
devices[2].pos=Vec3(-500,0,0); SRW.UpdateGuidance(.04)
assert(not data.srw.GuidedMissiles[100].Target and targets[100].x==25000)
devices[2].pos=Vec3(1000,0,0)
data.srw.Robots[1].EMPRemaining=2
SRW.GuidedLaunch(101,1,100); assert(not data.srw.GuidedMissiles[100].Target)
fireCalls=0; SRW.UpdateHound(1,data.srw.Robots[1],.04); assert(fireCalls==0)
data.srw.MountedWeapons[3].EMPRemaining=2
SRW.UpdateAABot(3,data.srw.MountedWeapons[3],.04); assert(fireCalls==0)
data.srw.Robots[1].EMPRemaining=nil
SRW.GuidedLaunch(101,1,100); devices[2]=nil; SRW.UpdateGuidance(.04)
assert(not data.srw.GuidedMissiles[100].Target)
nodes[100]=nil; SRW.UpdateGuidance(.04); assert(not data.srw.GuidedMissiles[100])
nodes[101].team=102; SRW.UpdateGuidance(.04); assert(not data.srw.GuidedMissiles[101])
-- A native silo launches vertically: it must turn onto its assigned target
-- before applying the forward seeker cone, instead of losing lock immediately.
nodes[100]={team=102,name='srw_salvo_rocket',pos=Vec3(1000,-400),vel=Vec3(0,-2500)}
devices[1].team=102;devices[2]={team=101,kind='mine',built=true,pos=Vec3(0,-100)}
data.srw.Robots[1]={Team=102,Kind='srw_rocket_bot',Direction=-1,Target=2}
SRW.GuidedLaunch(102,1,100);SRW.UpdateGuidance(.04)
assert(targets[100].y<-400 and data.srw.GuidedMissiles[100].Target==2)
SRW.UpdateGuidance(.12)
assert(targets[100].x==0 and data.srw.GuidedMissiles[100].Target==2)
nodes[100].vel=Vec3(-2500,0);SRW.UpdateGuidance(.04)
assert(not data.srw.GuidedMissiles[100].Acquiring)
devices[2].pos=Vec3(2000,-100);SRW.UpdateGuidance(.04)
assert(not data.srw.GuidedMissiles[100].Target,'missile reacquired behind its seeker')
''')
print('PASS: guided ground/air targets, lead, enemy checks, sector loss, EMP gates, cleanup and no tracker graphics')
