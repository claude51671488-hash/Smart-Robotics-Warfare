"""Shield regression tests with strict engine stubs; not an in-game test."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'.srw-tools'))
from lupa import LuaRuntime
lua=LuaRuntime()
lua.execute('''
SRW={}; data={}; energy=50000; spent=0; dead={}; disabled=false
function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function GetDeviceCountSide(side) return side==1 and 1 or 0 end
function GetDeviceIdSide(side,index) assert(side==1 and index==0); return 10 end
function DeviceExists(id) return id==10 or id==11 end
function GetDeviceType(id) return "srw_shield_generator" end
function GetDeviceTeamIdActual(id) return 101 end
function IsDeviceFullyBuilt(id) return true end
function DeviceDisabled(id) return disabled end
function GetDeviceCentrePosition(id) return Vec3(0,0,0) end
function GetTeamResources(team) return {energy=energy,metal=0} end
function AddResources(team,value,hasPos,pos)
 assert(team==101 and value.metal==0 and hasPos==false)
 energy=energy+value.energy; spent=spent-value.energy
end
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId(side,index) assert(side==2 and index==0); return 100 end
function NodeExists(id) return not dead[id] end
projectilePos=Vec3(300,0,0); projectileVelocity=Vec3(-10000,0,0); projectileTeam=102
function NodePosition(id) return projectilePos end
function NodeVelocity(id) return projectileVelocity end
function NodeTeam(id) return projectileTeam end
function GetNodeProjectileSaveName(id) return "test_shell" end
function GetProjectileParamFloat(name,team,param,default)
 if param=="ProjectileDamage" then return 100 end
 if param=="ProjectileSplashDamage" then return 200 end
 return default
end
function DestroyProjectile(id) assert(not dead[id]); dead[id]=true end
''')
for name in ['config.lua','state.lua','factories/production.lua','shields.lua']:
    lua.execute((root/'scripts'/name).read_text(encoding='utf-8'))
lua.execute('''
SRW.EnsureState(); SRW.ScanShields()
local s=data.srw.Shields[10]
assert(s.HP==4000 and not s.Active)
local a,b,m=Vec3(100,-100,0),Vec3(100,100,0),Vec3(200,0,0)
local arc,err,length=SRW.ShieldArc(a,b,m)
assert(arc and #arc==65 and length>200 and length<640)
assert(math.abs(arc[33].x-200)<1e-8)
assert(not SRW.ShieldArc(a,b,Vec3(0,0,0)), "inward bend accepted")
assert(not SRW.ShieldArc(a,a,m), "zero chord accepted")
assert(not SRW.ShieldArc(Vec3(950,-100,0),Vec3(950,100,0),Vec3(980,0,0)), "outside radius accepted")
assert(not SRW.ShieldArc(Vec3(100,-400,0),Vec3(100,400,0),Vec3(200,0,0)), "excess length accepted")
assert(not SRW.ShieldArc(Vec3(0/0,0,0),b,m), "NaN accepted")
SRW_ShieldActivate(201,10,100,-100,100,100,200,0)
assert(energy==50000 and not s.Active, "foreign player activation")
SRW_ShieldActivate(101,10,100,-100,100,100,0,0)
assert(energy==50000, "invalid placement charged")
energy=9999; SRW_ShieldActivate(101,10,100,-100,100,100,200,0)
assert(not s.Active and energy==9999)
energy=50000; SRW_ShieldActivate(101,10,100,-100,100,100,200,0)
assert(s.Active and energy==40000)
SRW_ShieldActivate(101,10,100,-100,100,100,200,0)
assert(energy==40000, "duplicate command charged")
SRW.UpdateShieldPower(0.04); assert(energy==39980)
projectileTeam=201; SRW.InterceptShieldProjectiles(0.04)
assert(not dead[100] and s.HP==4000, "friendly shell blocked")
projectileTeam=102; SRW.InterceptShieldProjectiles(0.04)
assert(dead[100] and s.HP==3700, "fast enemy shell not intercepted or wrong damage")
SRW_ShieldDeactivate(101,10); local before=energy
s.QuietSeconds=10; SRW.UpdateShieldPower(1); assert(s.HP==3740 and energy==before-500)
s.HP=4000; before=energy; SRW.UpdateShieldPower(1); assert(energy==before)
SRW.ShieldDamage(s,20000); assert(s.HP==0 and s.ColdRecovery and not s.Active)
energy=0; SRW.UpdateShieldPower(1); assert(s.HP==0)
energy=50000; SRW.UpdateShieldPower(1); assert(s.HP==20)
SRW.UpdateShieldPower(1); assert(s.HP==40)
local hp=s.HP; SRW_ShieldActivate(101,10,100,-100,100,100,200,0)
assert(s.Active and s.HP==hp, "activation reset health")
energy=0; SRW.UpdateShieldPower(0.04); assert(not s.Active)
disabled=true; SRW.UpdateShieldPower(0.04); assert(s.Status=="disabled")
disabled=false
-- Overlapping shields: only the first hit shield takes damage.
energy=50000; s.HP=4000; SRW_ShieldActivate(101,10,100,-100,100,100,200,0)
data.srw.Shields[11]={Team=101,HP=4000,Active=true,Arc=arc}
dead={}; data.srw.ShieldProjectiles={}; SRW.InterceptShieldProjectiles(0.04)
assert(s.HP==3700 and data.srw.Shields[11].HP==4000)
-- Damage that breaks the shield is still fully intercepted.
s.HP=1; dead={}; data.srw.ShieldProjectiles={}; SRW.InterceptShieldProjectiles(0.04)
assert(dead[100] and s.HP==0 and not s.Active)
data.srw.Shields[11]=nil
function DeviceExists(id) return false end
SRW.ScanShields(); assert(next(data.srw.Shields)==nil)
''')
print('PASS: geometry, bounds, ownership, activation cost, energy use, regeneration, EMP, friendly passage, swept interception, shared HP, overlapping shields, cleanup')

# Input must only send events, never spend energy or mutate simulation state.
lua.execute('''
path="mods/srw"; ANCHOR_TOP_LEFT=0; controls={}; mouse=Vec3(800,200,0)
world=Vec3(100,-100,0); sent={}; selected=10
data.srw.Shields={[10]={Team=101,HP=4000,Active=false,Status="off"}}
function DeviceExists(id) return id==10 end
function Language() return "Russian" end
function AddStrings(file) assert(file==path.."/mods/language-Russian/shield_ui.lua") end
function AddTextControl(parent,name,text,anchor,pos,relative,style)
 assert(parent=="" and type(name)=="string" and type(text)=="string" and style=="Readout")
 controls[name]={visible=true,text=text,pos=pos}
end
function AddButtonControl(parent,name,sprite,anchor,size,pos,style)
 assert(size.x==36 and size.y==22 and sprite==path.."/ui/textures/HUD/kega.png")
 controls[name]={visible=true,pos=pos}
end
function ShowControl(parent,name,value) assert(controls[name]); controls[name].visible=value end
function SetControlText(parent,name,value) assert(controls[name]); controls[name].text=value end
function ControlExists(parent,name) return controls[name]~=nil end
function GetLocalTeamId() return 101 end
function GetLocalSelectedDeviceId() return selected end
function GetMousePos() return mouse end
function ScreenToWorld(pos) return world end
function EnableGrid(value) grid=value end
function SendScriptEvent(name,args,file,toSelf)
 assert(file=="" and toSelf==true); sent[#sent+1]={name=name,args=args}
end
function SpawnLine(a,b,c,d) assert(a.z<=-100 and b.z<=-100 and d>0) end
function SpawnCircle(p,r,c,d) assert(p.z<=-100 and r>0 and d>0) end
function GetDeviceHealth(id) return 1 end
''')
lua.execute((root/'scripts/ui/shield.lua').read_text(encoding='utf-8'))
lua.execute('''
SRW.CreateShieldUI(); SRW.RefreshShieldUI(0.06)
assert(controls.srw_shield_on.visible)
assert(controls.srw_shield_on.pos.y==220 and controls.srw_shield_off.pos.y==250)
local before=energy
SRW.ClickShieldUI("srw_shield_on"); assert(grid)
SRW.ShieldKey("mouse left",true)
world=Vec3(100,100,0); SRW.ShieldKey("mouse left",true)
world=Vec3(0,0,0); SRW.ShieldKey("mouse left",true)
assert(#sent==0, "invalid local shape sent")
world=Vec3(200,0,0); SRW.RefreshShieldUI(0.06); SRW.ShieldKey("mouse left",true)
assert(#sent==1 and sent[1].name=="SRW_ShieldActivate")
local expected={101,10,100,-100,100,100,200,0}; local count=0
for value in string.gmatch(sent[1].args,"[^,]+") do count=count+1; assert(tonumber(value)==expected[count]) end
assert(count==8)
assert(not grid and energy==before and not data.srw.Shields[10].Active)
SRW.ClickShieldUI("srw_shield_on"); SRW.ShieldKey("escape",true)
assert(not grid and #sent==1)
SRW.ClickShieldUI("srw_shield_off"); assert(sent[2].name=="SRW_ShieldDeactivate")
selected=-1; SRW.RefreshShieldUI(0.06); assert(not controls.srw_shield_on.visible)
''')
print('PASS: shield UI creation, three-point input, validation, event payloads, cancellation, selection, local/simulation separation')

lua.execute('''
-- Long-run tracking must retain only the current tick, not every shot ever seen.
local s=data.srw.Shields[10]
s.Active=true; s.Arc=SRW.ShieldArc(Vec3(100,-100,0),Vec3(100,100,0),Vec3(200,0,0))
projectilePos=Vec3(10000,10000,0); projectileVelocity=Vec3(1,0,0)
local tick=0; local narrowCalls=0
local intersection=SRW.ShieldIntersection
SRW.ShieldIntersection=function(...) narrowCalls=narrowCalls+1; return intersection(...) end
function GetProjectileId(side,index) return tick end
function NodeExists(id) return true end
for i=1,10000 do
 tick=1000+i; SRW.InterceptShieldProjectiles(0.04)
 assert(#SRW.SortedIds(data.srw.ShieldProjectiles)==1)
end
assert(narrowCalls==0, "far shots entered expensive segment tests")
s.Active=false; SRW.InterceptShieldProjectiles(0.04)
assert(next(data.srw.ShieldProjectiles)==nil)
-- One second of one active arc: 16 segments at 10 Hz, not 64 at 20 Hz.
s.Active=true; selected=-1
local lines=0
function SpawnLine(...) lines=lines+1 end
for i=1,100 do SRW.RefreshShieldUI(0.01) end
assert(lines<=416 and lines>=384, "unexpected effect creation rate")
''')
print('PASS: 10000 ticks retain bounded projectile history; distant shots culled; bounded visual effect rate')
