from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_shields.py'))['lua']
for name in ['config.lua','robots/shield.lua','shield_shapes.lua']:
    lua.execute((r/'scripts'/name).read_text(encoding='utf-8'))
lua.execute('''
local positions={[10]=Vec3(0,0,0),[20]=Vec3(800,0,0),[30]=Vec3(-800,0,0)}
function DeviceExists(id) return positions[id]~=nil end
function GetDeviceCentrePosition(id) return positions[id] end
function GetDevicePosition(id) return GetDeviceCentrePosition(id) end
function GetDeviceTeamIdActual() return 101 end
function DeviceDisabled() return false end
function IsDeviceFullyBuilt() return true end
data.srw.Robots={
 [10]={Team=101,Kind="srw_shield_bot",SquadId=1},
 [20]={Team=101,Kind="srw_colossus_bot",SquadId=1},
 [30]={Team=101,Kind="srw_hound",SquadId=1}}
data.srw.Shields={[10]=SRW.NewMobileShield(101,"srw_shield_bot"),
 [20]=SRW.NewMobileShield(101,"srw_colossus_bot")}
SRW.UpdateShieldPower(.04); SRW.UpdateShieldShapes(.04)
local g=data.srw.SquadShields[-1]
assert(g and g.Active and g.MaxHP==14000 and g.HP==14000 and g.Radius>880)
assert(data.srw.Shields[10].Pooled and not SRW.CombatShields()[10])
SRW.ShieldDamage(g,1400)
assert(math.abs(g.HP-12600)<.001)
assert(data.srw.Shields[10].HP==4500 and data.srw.Shields[20].HP==8100)
-- An unrelated squad's built-in shield is never pooled.
data.srw.Robots[20].SquadId=2; SRW.UpdateShieldShapes(.04)
assert(data.srw.SquadShields[-1].HP==4500 and SRW.CombatShields()[20])
data.srw.Robots[20].SquadId=1
positions[30]=Vec3(-3000,0,0); SRW.UpdateShieldShapes(.04)
g=data.srw.SquadShields[-1];assert(g.Radius>1900)
-- Large squad broad phase and friendly passage.
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId() return 100 end
function NodeExists() return true end
function NodePosition() return Vec3(g.Origin.x,g.Origin.y-g.Radius-100,0) end
function NodeVelocity() return Vec3(0,5000,0) end
local team=201
function NodeTeam() return team end
dead={};data.srw.ShieldProjectiles={};SRW.InterceptShieldProjectiles(.04)
assert(not dead[100])
team=102;SRW.InterceptShieldProjectiles(.04);assert(dead[100])
-- Losing support restores individual shields without refilling them.
local remaining=data.srw.Shields[20].HP
positions[10]=nil;data.srw.Shields[10]=nil;SRW.UpdateShieldShapes(.04)
assert(not data.srw.SquadShields[-1] and SRW.CombatShields()[20].HP==remaining)
-- Structure outline uses only connected nodes; detached and temporary nodes do not count.
positions[10]=Vec3(0,0,0)
local points={[1]=Vec3(-100,-100,0),[2]=Vec3(100,-100,0),[3]=Vec3(100,100,0),[4]=Vec3(-100,100,0)}
local included={1,2,3,4};local sid=7
function GetDeviceStructureId() return sid end
function GetStructureTeam() return 101 end
function EnumerateStructureLinks(team,structure,callback,flag)
 assert(team==101 and structure==sid and flag==false)
 for i=1,#included-1 do _G[callback](included[i],included[i+1]) end
end
function NodePosition(id) return points[id] end
data.srw.Shields={[10]={Team=101,HP=1000,MaxHP=15000,Active=false}}
local s=data.srw.Shields[10];energy=50000
SRW_ShieldHull(201,10);assert(not s.Active and energy==50000)
SRW_ShieldHull(101,10);assert(s.Active and s.AutoHull and #s.Arc==5 and energy==40000)
assert(s.Arc[1].x==-140 and s.Arc[1].y==-140)
points[5]=Vec3(500,0,0);included={1,2,3,4,5}
SRW.UpdateShieldShapes(.5);assert(#s.Arc==5)
SRW.UpdateShieldShapes(.5);assert(#s.Arc>5 and s.HP==1000)
included={1,2,3,4};sid=8;SRW.UpdateShieldShapes(.5)
assert(#s.Arc==5 and s.HP==1000)
points[5]=Vec3(2000,0,0);included={1,2,3,4,5}
SRW.UpdateShieldShapes(.5);SRW.UpdateShieldShapes(.5)
assert(not s.Active and s.Status=="radius", "out-of-range envelope accepted")
SRW_ShieldDeactivate(101,10);assert(not s.AutoHull)
''')
print('PASS: pooled HP, membership, support loss, large/friendly interception, connected hull, growth confirmation, split and radius limits')
