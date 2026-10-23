from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
lua.execute('''
local facing=Vec3(1,0,0);local rotated
function GetDeviceForward() return facing end
function SetDeviceAngle(id,angle) rotated={id,angle} end
SRW.OrientRobotWeapon(900,1);assert(not rotated)
SRW.OrientRobotWeapon(900,-1);assert(not rotated)
facing=Vec3(-1,0,0);SRW.OrientRobotWeapon(900,-1);assert(not rotated)
-- Enemy bare beams are valid secondary targets, friendly ones never are.
devices={[900]={team=101,kind="srw_hound",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={[900]={Team=101,Kind="srw_hound",Direction=1}}
data.srw.MountedWeapons={}
function GetDeviceCountSide() return 0 end
local points={[1]=Vec3(2000,-100,0),[2]=Vec3(2000,100,0)}
local enemy=true
function EnumerateStructureLinks(side,sid,cb,match)
 if side==(enemy and 2 or 1) then _G[cb](1,2,Vec3(2000,0,0),"bracing",0) end
end
function NodePosition(id) return points[id] end
function NodeVelocity() return Vec3(0,0,0) end
local shots=0
function FireWeapon(id,p,error,flags)
 assert(error==0 and p.x==2000);shots=shots+1;return 0
end
SRW.UpdateRobots(.04);assert(shots==1 and data.srw.Robots[900].Target<0)
enemy=false;data.srw.Robots[900].FireWait=0;SRW.UpdateRobots(.04);assert(shots==1)
-- A barrel with a short randomly selected trigger still detects an overhead chassis.
enemy=true;points={[1]=Vec3(-100,-180,0),[2]=Vec3(100,-180,0)}
devices[900].kind="srw_dynamit_bot";devices[900].pos=Vec3(0,0,0)
data.srw.Robots[900]={Team=101,Direction=1,Age=0,Trigger=64}
SRW.UpdateRobots(.04);assert(data.srw.Robots[900].FuseRemaining==.1)
local x=devices[900].pos.x;SRW.UpdateRobots(.04);assert(devices[900].pos.x==x)
-- A fast chassis crossing the entire zone within one tick is predicted.
points={[1]=Vec3(300,-150,0),[2]=Vec3(400,-150,0)}
function NodeVelocity() return Vec3(-20000,0,0) end
data.srw.Robots[900]={Team=101,Direction=1,Age=0,Trigger=64}
SRW.UpdateRobots(.04);assert(data.srw.Robots[900].FuseRemaining==.1)
Projectiles={{SaveName="cannon",Effects={Impact={foundations="old"}}},{SaveName="mortar2"}}
''')
lua.execute((r/'weapons/projectile_list.lua').read_text())
lua.execute('''
for _,p in ipairs(Projectiles) do
 if p.SaveName=="srw_cathedral_shell" or p.SaveName=="srw_heavy_siege_he" then
  assert(p.ExplodeOnTouch and p.ProjectileSplashDamage>0)
  assert(p.Effects.Impact.foundations=="effects/impact_heavy.lua")
 end
end
assert(Projectiles[1].Effects.Impact.foundations=="old")
''')
print('PASS: side-aware facing correction, bare/enemy beam fallback, zero scripted spread, overhead/fast chassis proximity, stopped fuse, isolated terrain explosions')

lua.execute((r/'scripts/combat/impacts.lua').read_text())
lua.execute("""
DESTROYTYPE_HITTERRAIN=3
local circles=0
function GetProjectileParamFloat() return 280 end
function NodePosition() return Vec3(100,200,0) end
function SpawnCircle(p,r,c,t) assert(p.x==100 and r==280 and t==.35);circles=circles+1 end
SRW.TerrainBlastVisual(1,101,"srw_cathedral_shell",3);assert(circles==1)
SRW.TerrainBlastVisual(1,101,"srw_cathedral_shell",4)
SRW.TerrainBlastVisual(1,101,"srw_emp_shell",3);assert(circles==1)
SRW.TerrainBlastVisual(1,101,"srw_kolokol_he",3)
SRW.TerrainBlastVisual(1,101,"srw_kolokol_incendiary",3);assert(circles==1)
""")
print('PASS: terrain blast radius visual only on artillery terrain impacts')
