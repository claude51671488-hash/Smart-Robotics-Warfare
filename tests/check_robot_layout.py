"""Ground anchoring and mirrored whole-platform layout, using Forts adapters."""
from pathlib import Path
import runpy

r = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(r/'tests/check_hound.py'))['lua']
for name in ('robots/aa.lua', 'robots/spacing.lua'):
    lua.execute((r/'scripts'/name).read_text())
lua.execute('''
function EnableWeapon() end
function GetDeviceCountSide() return 0 end
function EnumerateStructureLinks() end
function ProjectileCount() return 0 end
function AimWeapon() return false end
function SRW.BeamTargets() return {} end
function DeleteDeviceById(id) devices[id]=nil end
local serial=1000
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(angle==90,'platform normal inverted')
 serial=serial+1;devices[serial]={team=team,kind=kind,pos=p,built=true};return serial
end
function SetDeviceAngle(id,angle) error('creation already assigns platform orientation') end
local probeY
function SRW.GroundAt(x,y,reach) probeY=y;return Vec3(x,x*.02,0) end
local function near(a,b) assert(math.abs(a-b)<.00001,tostring(a).." != "..tostring(b)) end
local covered=0
for _,kind in ipairs(SRW.RobotKinds) do
 local cfg=SRW.Config.Robots[kind]
 if cfg.Mounts and not cfg.Air then
  covered=covered+1
  for _,team in ipairs({101,102}) do
   devices={[50]={team=team,kind="srw_factory_ground_3",pos=Vec3(0,0,0),built=true}}
   data.srw.Robots={};data.srw.MountedWeapons={};SRW.SeparateRobots(.04)
   local ok,id=SRW.SpawnTank(team,50,kind);assert(ok)
   local bot=data.srw.Robots[id];local p=devices[id].pos
   near(p.y+bot.GroundLift,p.x*.02)
   local parts={{Role=cfg.WeaponRole,x=0,y=-bot.GroundLift}}
   local ids=SRW.SortedIds(data.srw.MountedWeapons)
   assert(#ids==#cfg.Mounts)
   for i,child in ipairs(ids) do
    local mount=cfg.Mounts[i];local q=devices[child].pos
    near(q.x,p.x+mount.X*bot.Direction);near(q.y,p.y+mount.Y)
    assert(q.y<=p.y+bot.GroundLift+.00001,"mount below ground: "..kind)
    parts[#parts+1]={Role=mount.Role,x=mount.X,y=mount.Y-bot.GroundLift}
   end
   for _,a in ipairs(parts) do
    for _,b in ipairs(parts) do
     if a~=b then
      assert((a.x-b.x)^2+(a.y-b.y)^2>50^2,"overlapping mount origins")
      if a.Role=="rockets" and b.Role~="rockets" then
       assert(a.x<b.x and a.y<b.y,"rockets must be rear/top")
      end
      if a.Role=="artillery" and b.Role=="direct" then
       assert(a.x<b.x and a.y<b.y,"artillery must be behind/above direct guns")
      end
      if a.Role=="aa" and b.Role=="direct" then assert(a.y<b.y,"AA must sit above direct guns") end
      if a.Role=="direct" and b.Role=="direct" and a.y<b.y then
       assert(a.x<b.x,'upper direct gun must be behind the lower gun muzzle')
      end
      if a.Role=="aa" and b.Role=="aa" and a.y<b.y then
       assert(a.x<b.x,'upper AA gun must be behind the lower gun muzzle')
      end
     end
    end
   end
   -- Both movement paths must raycast at feet height, preserving lift on slopes.
   local old=p
   SRW.UpdateHound(id,bot,.04)
   near(probeY,old.y+bot.GroundLift)
   p=devices[id].pos;assert((p.x-old.x)*bot.Direction>0);near(p.y+bot.GroundLift,p.x*.02)
   SRW.UpdateMountedWeapons(.04)
   for i,child in ipairs(ids) do near(devices[child].pos.y,p.y+cfg.Mounts[i].Y) end
   if cfg.WeaponRole=="aa" then
    devices[900]={team=team,kind="srw_hound",pos=Vec3(p.x+bot.Direction*2000,p.y,0),built=true}
    data.srw.Robots[900]={Team=team,Kind="srw_hound",Direction=bot.Direction}
    bot.FireWait=0;old=p;SRW.UpdateAABot(id,bot,.1)
    near(probeY,old.y+bot.GroundLift);p=devices[id].pos
    assert((p.x-old.x)*bot.Direction>0);near(p.y+bot.GroundLift,p.x*.02)
   end
  end
 end
end
assert(covered==17,"a multi-weapon platform was missed")
-- A legacy save's zero lift must stay zero, even if its current config is lifted.
devices={[1]={team=101,kind="srw_rocket_bot",pos=Vec3(0,0,0),built=true}}
local old={Team=101,Kind="srw_rocket_bot",Direction=1}
local next=SRW.RobotGroundStep(1,old,10);near(probeY,0);near(next.y,.2)
-- Low foreground beams still stop raised roots even when the gun ray passes above.
devices[1].pos=Vec3(0,-255,0);old.GroundLift=255
data.srw.Robots={[1]=old};data.srw.MountedWeapons={}
local material="bracing"
function NodePosition(node) return node==1 and Vec3(5,-20,0) or Vec3(5,0,0) end
function EnumerateStructureLinks(side,structure,callback,match)
 if side==2 then _G[callback](1,2,Vec3(5,-10,0),material) end
end
function CastRayFromDevice() return RAY_HIT_NOTHING end
SRW.SeparateRobots(.04)
assert(SRW.MovementRay(1,Vec3(10,-255,0),0,4,0)==RAY_HIT_STRUCTURE)
material="backbracing";SRW.SeparateRobots(.04)
assert(SRW.MovementRay(1,Vec3(10,-255,0),0,4,0)==RAY_HIT_NOTHING)
''')
print('PASS: all multi-weapon layouts, mirrored teams, independent mount clearance, sloped Hound/AA ground tracking, legacy lift and low-wall collision')
