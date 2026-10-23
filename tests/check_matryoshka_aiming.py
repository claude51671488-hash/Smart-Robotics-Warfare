"""Real SRW aiming and capsule AI with engine fixtures; not a Forts playtest."""
from pathlib import Path
import sys

r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime

lua=LuaRuntime()
lua.execute('''
SRW={};data={};devices={};FIREFLAG_DIRECTAIM=32;FIRE_SUCCESS=0
FIREFLAG_TEST=1;FIREFLAG_IGNORERELOADING=2
function Log() end
function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function DeviceExists(id) return devices[id]~=nil end
function GetDeviceTeamIdActual(id) return devices[id].Team end
function GetDeviceType(id) return 'srw_matryoshka_turret' end
function DeviceDisabled(id) return devices[id].Disabled end
function IsDeviceFullyBuilt() return true end
function GetWeaponBarrelPosition(id) return devices[id].Head end
function GetWeaponHardpointPosition(id) return devices[id].Muzzle end
function GetWeaponMaxFireSpeed() return 5000 end
function SetWeaponReloadTime() end
function GetWeaponReloadPeriodById() return .04 end
function IsWeapon(id) return devices[id].Weapon end
function SRW.SortedIds(t)
 local ids={};for id in pairs(t) do ids[#ids+1]=id end;table.sort(ids);return ids
end
function FireWeaponWithPower(id,p,spread,testSpread,flags,power)
 assert(testSpread==-1 and power==1)
 if flags==35 then
  clearanceTests=(clearanceTests or 0)+1
  return nativeBlocked and nativeBlocked(p) and 11 or FIRE_SUCCESS
 end
 assert(flags==32)
 last=p;shots=shots+1;return FIRE_SUCCESS
end
''')
for filename in ('config.lua','state.lua','combat/aiming.lua','matryoshka.lua'):
    lua.execute((r/'scripts'/filename).read_text())

lua.execute('''
SRW.EnsureState()
local cfg=SRW.Config.Matryoshka
devices[100]={Team=101,Head=Vec3(300,-90)}
local gun=devices[100]
-- DIRECTAIM measures its vector from Head, but bullets leave Hardpoint0.
-- Check both traversals, short shots and targets above/below the head.
for _,direction in ipairs({1,-1}) do
 gun.Muzzle=Vec3(gun.Head.x+direction*50,gun.Head.y-10)
 for _,dx in ipairs({120,700,3000}) do
  for _,dy in ipairs({-120,0,120}) do
   local target=Vec3(gun.Head.x+direction*dx,gun.Head.y+dy)
   local barrel=SRW.DirectBarrelTarget(100,cfg,target)
   local ax,ay=barrel.x-gun.Head.x,barrel.y-gun.Head.y
   local length=math.sqrt(ax*ax+ay*ay)
   local vx,vy=5000*ax/length,5000*ay/length
   local time=(target.x-gun.Muzzle.x)/vx
   local impactY=gun.Muzzle.y+vy*time+.5*981*time*time
   assert(time>0 and math.abs(impactY-target.y)<.001,
    'Matryoshka DIRECTAIM lost its muzzle-to-head offset')
  end
 end
end
''')

lua.execute('''
local cfg=SRW.Config.Matryoshka
local entries={};local blocked={}
function SRW.DeviceTargets(side) return entries end
function SRW.ShotClearsTerrain(id,cfg,p) return not blocked[p.x] end
for _,team in ipairs({101,102}) do
 devices[100].Team=team;devices[100].Muzzle=Vec3(350,-90)
 local bot={Team=team,Direction=1,DeployAge=cfg.DeploySeconds,Deployed=true,FireWait=0}
 data.srw.CapsuleTurrets={[100]=bot};shots=0;entries={};blocked={}
 -- Eight obstructed weapons must not hide the ninth clear weapon forever.
 for i=1,9 do
  devices[i]={Weapon=true}
  entries[#entries+1]={Id=i,Position=Vec3(500+i*100,-90)}
  if i<9 then blocked[500+i*100]=true end
 end
 devices[10]={Weapon=false}
 entries[#entries+1]={Id=10,Position=Vec3(400,-90)}
 SRW.UpdateCapsules(.04)
 assert(bot.Target==9 and shots==1,'eight blocked weapons starved a clear ninth weapon')
 -- Only after every weapon is unavailable may a nearer non-weapon be chosen.
 blocked[1400]=true;bot.FireWait=0;SRW.UpdateCapsules(.04)
 assert(bot.Target==10 and shots==2,'blocked weapons starved a clear non-weapon')
 blocked[400]=true;bot.FireWait=0;SRW.UpdateCapsules(.04)
 assert(bot.Target==nil and shots==2,'turret fired through terrain')
 -- A newly reachable weapon takes priority again on the very next tick.
 blocked[600]=nil;SRW.UpdateCapsules(.04)
 assert(bot.Target==1 and shots==3,'turret did not reacquire the newly clear weapon')
end
-- Rejected candidates must not overwrite the selected target's motion history.
for _,direction in ipairs({1,-1}) do
 local team=direction==1 and 101 or 102
 local near,far=300+direction*300,300+direction*1100
 entries={{Id=1,Position=Vec3(near,-90)},{Id=9,Position=Vec3(far,-90)}}
 blocked={[near]=true};devices[100].Team=team
 devices[100].Muzzle=Vec3(300+direction*50,-90)
 local bot={Team=team,Direction=direction,DeployAge=cfg.DeploySeconds,Deployed=true,FireWait=0}
 data.srw.CapsuleTurrets={[100]=bot};shots=0
 SRW.UpdateCapsules(.04)
 entries[2].Position=Vec3(far+direction*20,-90);bot.FireWait=0
 SRW.UpdateCapsules(.04)
 assert(bot.AimTrack.Id==9 and math.abs(bot.AimTrack.VX-direction*500)<.001,
  'blocked candidate erased the moving target velocity')
 local static=SRW.DirectBarrelTarget(100,cfg,entries[2].Position)
 assert((last.x-static.x)*direction>0,'turret did not lead a moving weapon behind a blocked candidate')
 entries={};SRW.UpdateCapsules(.04)
 assert(bot.AimTrack==nil,'lost target retained motion history')
end
-- A clear terrain arc is not sufficient when Forts itself refuses the shot.
-- Native clearance tests must ignore reload and must never fire real bullets.
entries={{Id=1,Position=Vec3(1000,-90)},{Id=9,Position=Vec3(-1400,-90)}}
blocked={};devices[100].Team=101;devices[100].Muzzle=Vec3(350,-90)
local bot={Team=101,Direction=1,DeployAge=cfg.DeploySeconds,Deployed=true,FireWait=0}
data.srw.CapsuleTurrets={[100]=bot};shots=0;clearanceTests=0
nativeBlocked=function(p) return p.x>devices[100].Head.x end
SRW.UpdateCapsules(.04)
assert(bot.Target==9 and shots==1 and clearanceTests==2,
 'engine-rejected weapon hid the clear rear target')
nativeBlocked=function() return true end;bot.FireWait=0
SRW.UpdateCapsules(.04)
assert(bot.Target==nil and shots==1,'failed clearance fired a real bullet')
nativeBlocked=nil;bot.FireWait=.12;local tests=clearanceTests
SRW.UpdateCapsules(.04)
assert(bot.Target==1 and shots==1 and clearanceTests==tests+1 and bot.FireWait>0,
 'test fire spent a shot or bypassed the scripted cooldown')
''')
print('PASS: Matryoshka muzzle/head rebasing, close/elevated rear shots, ninth-target acquisition, blocked-weapon fallback, moving-target lead, native clearance and reload-safe test shots')
