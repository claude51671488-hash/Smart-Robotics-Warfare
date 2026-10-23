from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute((root/'scripts/robots/spacing.lua').read_text())
lua.execute("""
RAY_HIT_DEVICE=3; RAY_HIT_WEAPON=4
local hit=1; local ray=RAY_HIT_WEAPON; local ground=true; local gx
function CastGroundRay(a,b,flags) gx=a.x; return ground and RAY_HIT_TERRAIN or RAY_HIT_NOTHING end
function GetRayHitPosition() return Vec3(gx,0,0) end
function CastRayFromDevice(id,p,hp,flags,fields) return ray end
function GetRayHitDeviceId() return hit end
function GetDeviceCountSide(side) return 0 end
for _,team in ipairs({101,102}) do
 local direction=team%100==1 and 1 or -1
 devices={[1]={team=team,kind="srw_tank_bot",built=true,pos=Vec3(100*direction,0,0)},
          [2]={team=team,kind="srw_hunter_bot",built=true,pos=Vec3(0,0,0)}}
 data.srw.Robots={[1]={Team=team,Kind="srw_tank_bot",Direction=direction},
                 [2]={Team=team,Kind="srw_hunter_bot",Direction=direction,SpacingThisTick=true}}
 data.srw.MountedWeapons={}; beamFixtures={}
 for i=1,100 do
  SRW.SeparateRobots(.04)
  SRW.UpdateHound(1,data.srw.Robots[1],.04)
  SRW.UpdateHound(2,data.srw.Robots[2],.04)
 end
 assert(devices[2].pos.x*direction>devices[1].pos.x*direction+400,'fast robot cannot overtake')
 assert(not data.srw.Robots[2].SpacingThisTick)
 -- A deployed unit is passable too.
 local x=devices[2].pos.x; SRW.SeparateRobots(.04); SRW.UpdateHound(2,data.srw.Robots[2],.04)
 assert((devices[2].pos.x-x)*direction>0)
end
-- Both enemy robot hulls and their mounted weapons are passable.
devices[1].team=101
assert(SRW.MovementRay(2,Vec3(8,0,0),0,0,0)==RAY_HIT_NOTHING)
data.srw.Robots[1]=nil; data.srw.MountedWeapons[1]={Root=3}
assert(SRW.MovementRay(2,Vec3(8,0,0),0,0,0)==RAY_HIT_NOTHING)
-- Ordinary devices, terrain and foreground beams must still block.
data.srw.MountedWeapons={}
assert(SRW.MovementRay(2,Vec3(8,0,0),0,0,0)==RAY_HIT_WEAPON)
data.srw.Robots[1]={Team=101,Kind="srw_tank_bot"}
ray=RAY_HIT_DEVICE
assert(SRW.MovementRay(2,Vec3(8,0,0),0,0,0)==RAY_HIT_NOTHING)
ray=RAY_HIT_TERRAIN
assert(SRW.MovementRay(2,Vec3(8,0,0),0,0,0)==RAY_HIT_TERRAIN)
ray=RAY_HIT_DEVICE; devices[2].pos=Vec3(0,0,0)
beamFixtures={side=1,[1]=Vec3(4,-100,0),[2]=Vec3(4,100,0)}
SRW.SeparateRobots(.04)
assert(SRW.MovementRay(2,Vec3(8,0,0),0,0,0)==RAY_HIT_DEVICE)
beamFixtures={}; ground=false; SRW.SeparateRobots(.04)
local x=devices[2].pos.x; SRW.UpdateHound(2,data.srw.Robots[2],.04)
assert(devices[2].pos.x==x,'robot crossed missing ground')
-- No forced separation even for overlapping bodies or stale saved flags.
devices[1].pos=Vec3(0,0,0); data.srw.Robots[2].SpacingThisTick=true
SRW.SeparateRobots(.04)
assert(devices[1].pos.x==0 and devices[2].pos.x==0 and not data.srw.Robots[2].SpacingThisTick)
""")
print('PASS: overtaking both directions, no repulsion, hull/mount pass-through, ordinary devices/walls/terrain preserved')
