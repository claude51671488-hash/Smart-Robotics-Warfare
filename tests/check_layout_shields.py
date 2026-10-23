"""Raised weapon layouts keep personal/group shields and minimap on their anchors."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent / '.srw-tools'))
from lupa import LuaRuntime

lua = LuaRuntime()
lua.execute('''
SRW={}; path='test'; data={srw={Robots={},MountedWeapons={},Shields={},ShieldProjectiles={}}}
function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function SRW.SortedIds(t)
 local result={};for id in pairs(t) do result[#result+1]=id end
 table.sort(result);return result
end
devices={
 [10]={team=101,pos=Vec3(1000,-240),centre=Vec3(1000,-300)},
 [11]={team=101,pos=Vec3(850,-550),centre=Vec3(850,-580)},
 [12]={team=101,pos=Vec3(1300,0),centre=Vec3(1300,-30)},
 [20]={team=101,pos=Vec3(600,-200),centre=Vec3(600,-220)},
 [50]={team=101,pos=Vec3(0,0),centre=Vec3(0,-50)}}
function DeviceExists(id) return devices[id]~=nil end
function GetDevicePosition(id) return devices[id].pos end
function GetDeviceCentrePosition(id) return devices[id].centre end
function GetDeviceTeamIdActual(id) return devices[id].team end
function IsDeviceFullyBuilt() return true end
function DeviceDisabled() return false end
function GetDeviceHealth() return 1 end
function GetLocalTeamId() return 101 end
function GetLocalSelectedDeviceId() return 0 end
function GetDeviceCountSide() return 0 end
function ControlExists() return true end
function ShowControl() end
function SpawnLine(a,b,color,age) lines[#lines+1]={a,b} end
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId() return 100 end
function NodeExists() return not dead end
function NodePosition() return shotPos end
function NodeVelocity() return shotVelocity end
function NodeTeam() return shotTeam end
function GetNodeProjectileSaveName() return 'shell' end
function GetProjectileParamFloat(name,team,key,default)
 if key=='ProjectileDamage' then return 10 end
 return default
end
function DestroyProjectile() dead=true end
''')
for name in ['config.lua', 'shields.lua', 'robots/shield.lua', 'shield_shapes.lua', 'ui/shield.lua']:
    lua.execute((root / 'scripts' / name).read_text(encoding='utf-8'))

lua.execute('''
data.srw.Robots={[10]={Team=101,Kind='srw_colossus_bot',GroundLift=240}}
data.srw.MountedWeapons={[11]={Root=10},[12]={Root=10}}
local s=SRW.NewMobileShield(101,'srw_colossus_bot')
data.srw.Shields={[10]=s}
SRW.UpdateShieldPower(.04)
local origin=SRW.ShieldOrigin(10,s)
assert(origin.x==1000 and origin.y==0,'personal shield followed raised gun instead of feet')
assert(s.Radius>=680 and #s.Arc==65 and s.HP==9000 and s.MaxHP==9000)
local function hitPoint(shield,p,team)
 local o=SRW.ShieldOrigin(10,shield)
 local dx,dy=p.x-o.x,p.y-o.y
 local length=math.sqrt(dx*dx+dy*dy)
 local scale=(shield.Radius+150)/length
 shotPos=Vec3(o.x+dx*scale,o.y+dy*scale)
 shotVelocity=Vec3((p.x-shotPos.x)/.04,(p.y-shotPos.y)/.04)
 shotTeam=team or 102;dead=false;data.srw.ShieldProjectiles={}
 SRW.InterceptShieldProjectiles(.04)
 return dead
end
-- Actual collision pass protects every gun, including rear high and front low.
for _,id in ipairs({10,11,12}) do
 assert(hitPoint(s,GetDeviceCentrePosition(id)), 'weapon centre outside personal dome')
end
local hp=s.HP
assert(not hitPoint(s,GetDeviceCentrePosition(12),201) and s.HP==hp)
-- Both sides of the lower 120-degree opening remain open.
shotPos=Vec3(origin.x,origin.y+s.Radius+150)
shotVelocity=Vec3(0,-(s.Radius+200)/.04);shotTeam=102;dead=false
data.srw.ShieldProjectiles={};SRW.InterceptShieldProjectiles(.04)
assert(not dead,'layout envelope closed mobile shield bottom')
-- Renderer uses the exact collision origin and arc.
lines={};SRW.RefreshShieldUI(.04)
assert(lines[1][1].x==s.Arc[1].x+origin.x and lines[1][1].y==s.Arc[1].y+origin.y)
-- Translation retains the arc table; no history or per-frame arc accumulation.
local arc=s.Arc
for _,id in ipairs({10,11,12}) do
 local d=devices[id]
 d.pos=Vec3(d.pos.x+64,d.pos.y+16)
 d.centre=Vec3(d.centre.x+64,d.centre.y+16)
end
SRW.UpdateShieldPower(.04);assert(s.Arc==arc and s.HP==hp)
origin=SRW.ShieldOrigin(10,s);assert(origin.x==1064 and origin.y==16)
lines={};SRW.RefreshShieldUI(.04)
assert(lines[1][1].x==s.Arc[1].x+origin.x and lines[1][1].y==s.Arc[1].y+origin.y)
-- A captured or destroyed child is not permanently retained in the envelope.
devices[11].team=102;SRW.UpdateShieldPower(.04)
assert(s.Radius<680)
devices[11]=nil;devices[12]=nil;SRW.UpdateShieldPower(.04)
assert(s.Radius==SRW.Config.Robots.srw_colossus_bot.ShieldRadius)
-- Legacy roots retain their actual anchor, regardless of the new profile.
data.srw.Robots[10].GroundLift=nil
SRW.Config.Robots.srw_colossus_bot.RootLift=999
assert(SRW.ShieldOrigin(10,s).y==devices[10].pos.y)
data.srw.Robots[10].GroundLift=240
assert(SRW.ShieldOrigin(50,{Mobile=false}).y==-50,'stationary origin changed')

-- A low front child must lower the formation origin, not just increase radius.
devices[12]={team=101,pos=Vec3(1400,0),centre=Vec3(1400,-20)}
data.srw.Robots[10].SquadId=1
data.srw.Robots[20]={Team=101,Kind='srw_shield_bot',SquadId=1}
data.srw.Shields[20]=SRW.NewMobileShield(101,'srw_shield_bot')
SRW.UpdateShieldPower(.04);SRW.UpdateShieldShapes(.04)
local g=data.srw.SquadShields[-1]
assert(g and g.Active and g.Origin.y==20 and g.Origin.x==1000)
assert(g.MaxHP==14000 and g.HP==s.HP+5000)
for _,id in ipairs({10,12,20}) do
 assert(hitPoint(g,GetDeviceCentrePosition(id)),'formation weapon below group dome')
end
local groupArc=g.Arc
SRW.UpdateShieldShapes(.04);assert(data.srw.SquadShields[-1].Arc==groupArc)
local savedHP=s.HP
devices[20]=nil;data.srw.Shields[20]=nil;data.srw.Robots[20]=nil
SRW.UpdateShieldShapes(.04)
assert(not data.srw.SquadShields[-1] and not s.Pooled and s.HP==savedHP)
''')

lua.execute((root / 'scripts/ui/window.lua').read_text(encoding='utf-8'))
lua.execute('''
function LoadControl() end
function AddTextButtonControl() end
function AddTextControl() end
function SetControlColour() end
function AddSpriteControl() end
function SetControlSpriteByParent() end
function SetControlRelativePos(parent,name,p) dots[name]=p end
local bounds={MinX=0,MaxX=2000,MinY=-1000,MaxY=1000}
SRW.MapBounds=function(anchors) return bounds end
dots={};SRW.CreateFactoryWindow();SRW.FactoryWindowVisible(50);SRW.RefreshFactoryMap(.2)
local ground=GetDevicePosition(10)
local expected=SRW.MapPosition(Vec3(ground.x,ground.y+240),bounds)
assert(dots.srw_map_dot1.x==expected.x-4 and dots.srw_map_dot1.y==expected.y-4,
 'factory minimap shows elevated gun rather than ground robot')
data.srw.Robots[10].GroundLift=nil;SRW.RefreshFactoryMap(.2)
expected=SRW.MapPosition(ground,bounds)
assert(dots.srw_map_dot1.y==expected.y-4,'legacy minimap anchor changed')
''')
print('PASS: personal/group mount coverage, shared render/collision origins, bounded reusable arcs, legacy anchors and minimap feet')
