"""Run with Python + lupa. Engine adapters are mocked; Forts still needs testing."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent / '.srw-tools'))
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
def read_lua(path):
    b = path.read_bytes()
    return b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8-sig')
compile_lua = lua.eval('function(s,n) local f,e=load(s,n); if not f then error(e) end end')
for path in root.rglob('*.lua'):
    # Forts adds L"..." wide strings to Lua. Remove only that prefix for stock Lua parsing.
    text = re.sub(r'\bL(?=["\'])', '', read_lua(path))
    compile_lua(text, str(path.relative_to(root)))
print('PASS: all Lua files parse (Forts wide-string prefixes normalized)')

registration = LuaRuntime()
registration.execute('Devices = {{SaveName="mine"}}; Sprites={}; path="mods/srw"')
source = (root / 'devices/device_list.lua').read_text(encoding='utf-8')
registration.execute(source)
registration.execute(source)
registration.execute('assert(#Sprites == 2 and Devices[2].Icon == "srw-kega-icon" and Devices[4].Detail == "srw-kega-icon")')
registration.execute('assert(Devices[4].dlc2_BuildAnywhere and Devices[4].BuildOnGroundOnly, "floating bot requires ground-device registration")')
registration.execute('assert(#Devices == 18 and Devices[1].SaveName == "mine" and Devices[2].PopulationCap == 1)')
registration.globals().dofile=lambda name: registration.execute((root/name.replace('mods/srw/','')).read_text()) if name.startswith('mods/srw/') else None
registration.execute((root / 'devices/factory_ground_1.lua').read_text())
registration.execute('assert(#Sprites == 0 and Root.Sprite == "srw-factory-animation")')
print('PASS: repeated registration and shared factory animation')

lua.execute('''
SRW = {}; data = {}; devices = {}; balances = {}; spawnId = -1; calls = 0; path="mods/srw"
function Log(...) end
function Vec3(x,y,z) return {x=x,y=y,z=z} end
function DeviceExists(id) return devices[id] ~= nil end
function GetDeviceTeamId(id) return devices[id].team % 100 end
function GetDeviceTeamIdActual(id) return devices[id].team end
function GetDeviceType(id) return devices[id].kind end
function IsDeviceFullyBuilt(id) return devices[id].built end
function DeviceDisabled(id) return devices[id].disabled end
function GetTeamResources(team) return balances[team] end
function AddResources(team,v) balances[team].metal=balances[team].metal+v.metal;
    balances[team].energy=balances[team].energy+v.energy; calls=calls+1 end
function GetDevicePosition(id) return devices[id].pos or Vec3(0,0,0) end
function GetDeviceCentrePosition(id) return GetDevicePosition(id) end
function EnableDevice(...) end
function dlc2_CreateFloatingDevice(team,kind,pos,angle)
    assert(pos.y==-(SRW.Config.Robots[kind].RootLift or 0), "root must preserve its ground-anchor clearance")
    if spawnId < 0 then return spawnId end
    devices[spawnId]={team=team,kind=kind,built=true,pos=pos}; return spawnId
end
function GetRandomFloat(a,b,description)
    assert(type(a)=="number" and type(b)=="number" and a<=b)
    assert(type(description)=="string" and #description>0, "Forts requires a random value description")
    return a
end
function GetDeviceCountSide(side) return 0 end
beamFixtures={}
function NodePosition(id) return beamFixtures[id] end
function EnumerateStructureLinks(side,structure,callback,matchSide)
    assert(structure==-1 and matchSide==true)
    if beamFixtures.side==side then _G[callback](1,2,Vec3(0,0,0),"bracing",0) end
end
function CastGroundRay(...) return groundResult end
function GetRayHitPosition() return Vec3(160,0,0) end
function CastRay(...) error("movement must use a device-aware ray") end
function CastRayFromDevice(id,destination,hp,flags,fields)
    assert(DeviceExists(id) and type(destination.x)=="number" and hp==0 and fields==0)
    return rayResult
end
function GetRayHitDeviceId() return -1 end
function GetRayHitTeamId() return 2 end
function dlc2_SetDevicePosition(id,p) devices[id].pos=p end
function ApplyDamageToDevice(id,v) devices[id]=nil end
RAY_HIT_TERRAIN=1; RAY_HIT_NOTHING=0; RAY_HIT_STRUCTURE=2; RAY_EXCLUDE_BG_MATERIALS=4
groundResult=1; rayResult=0
''')
for name in ['config.lua','robots/layout.lua','state.lua','factories/production.lua','robots/movement.lua']:
    lua.execute((root / 'scripts' / name).read_text(encoding='utf-8'))
lua.execute('''
SRW.EnsureState()
devices[1]={team=1,kind="srw_factory_ground_1",built=true}
data.srw.Factories[1]={Team=1,Queue=0,Reserve=0,Remaining=0,Status="ready"}
balances[1]={metal=200,energy=2000}
local f=data.srw.Factories[1]
SRW.Order(2,1); assert(f.Queue==0, "foreign owner order")
SRW.Order(1,1); assert(f.Queue==1)
SRW.UpdateFactories(0.04); assert(calls==1 and f.Remaining==7)
for i=1,174 do SRW.UpdateFactories(0.04) end
assert(f.Reserve==0, "early production")
SRW.UpdateFactories(0.04); assert(f.Reserve==1 and calls==1)
SRW.Order(1,1); SRW.UpdateFactories(0.04)
assert(f.Queue==1 and f.Remaining==0 and calls==1, "insufficient funds")
balances[1]={metal=1000,energy=10000}; f.Reserve=20
SRW.UpdateFactories(0.04); assert(calls==1, "full reserve charged")
f.Reserve=1
SRW.Release(2,1); assert(f.Reserve==1)
SRW.Release(1,1); assert(f.Reserve==1 and f.Status=="exit_blocked", "failed spawn loses reserve")
spawnId=100; SRW.Release(1,1); assert(f.Reserve==0 and data.srw.Robots[100])
assert(data.srw.Robots[100].Trigger==0.5*SRW.Config.Units.MineWidth)
for i=1,25 do SRW.UpdateRobots(0.04) end
assert(devices[100] and data.srw.Robots[100], "bot detonated without an enemy")
local oldX=devices[100].pos.x; SRW.UpdateRobots(0.04)
assert(devices[100].pos.x>oldX, "robot does not advance")
groundResult=0; oldX=devices[100].pos.x; SRW.UpdateRobots(0.04)
assert(devices[100].pos.x==oldX, "robot crossed cliff")
assert(data.srw.Robots[100].MoveStatus=="no ground within step height")
groundResult=1
for id=101,109 do devices[id]={team=1,kind="srw_dynamit_bot",built=true}; data.srw.Robots[id]={Team=1} end
f.Reserve=1; spawnId=110; SRW.Release(1,1)
assert(f.Reserve==1 and f.Status=="limit", "active cap bypass")
devices[109]=nil; SRW.Release(1,1); assert(f.Reserve==1 and f.Status=="exit_wait", "exit delay bypass")
f.Queue=0
for i=1,75 do SRW.UpdateFactories(0.04) end
SRW.Release(1,1); assert(f.Reserve==0, "dead bot keeps slot after exit delay")
f.Queue=0; for i=1,25 do SRW.Order(1,1) end
assert(f.Queue==20, "queue unbounded")
local state=data.srw; SRW.EnsureState(); assert(data.srw==state and f.Queue==20, "state reset on load")
devices[1]=nil; SRW.ScanFactories(); assert(data.srw.Factories[1]==nil, "dead factory retained")
''')
print('PASS: ownership, production timing, one-time charging, shortages, capacity, failed spawn, movement, cliffs, active cap, queue bound, state preservation, cleanup')

lua.execute('''
devices={ [50]={team=101,kind="srw_factory_ground_1",built=true} }
data.srw.Factories={}; data.srw.Robots={}
function GetDeviceCountSide(side) return side==1 and 1 or 0 end
function GetDeviceIdSide(side,index) assert(side==1 and index==0); return 50 end
SRW.ScanFactories()
local f=data.srw.Factories[50]
assert(f.Team==101, "factory registered to side instead of owner")
SRW.Order(1,50); SRW.Order(201,50); assert(f.Queue==0, "other fort can order")
SRW.Order(101,50); assert(f.Queue==1, "actual owner cannot order")
balances[101]={metal=200,energy=2000}; SRW.UpdateFactories(0.04)
assert(balances[101].metal==0 and f.Remaining==7)
f.Reserve=1; spawnId=500; SRW.Release(101,50)
assert(data.srw.Robots[500].Team==101)
function GetDeviceCountSide(side) return 0 end
SRW.UpdateRobots(0.04); assert(data.srw.Robots[500], "bot removed due to side/owner mismatch")
visible={}; texts={}; selectedId=50; localTeam=101
function Language() return "Russian" end
function GetLocalSelectedDeviceId() return selectedId end
function GetLocalTeamId() return localTeam end
function AddTextControl(parent,name,value,anchor,pos,relative,style)
    assert(parent=="srw_factory_window" and type(name)=="string" and type(value)=="string")
    assert(type(anchor)=="number" and type(pos)=="table" and type(relative)=="boolean" and style=="Readout")
    visible[name]=true; texts[name]=value
end
AddTextButtonControl=AddTextControl
function AddButtonControl(parent,name,sprite,anchor,size,pos,style)
    assert(parent=="srw_factory_window" and type(name)=="string" and sprite==path.."/ui/textures/HUD/kega.png")
    assert(type(anchor)=="number" and size.x==36 and size.y==22 and type(pos)=="table" and style=="Normal")
    visible[name]=true
end
function AddStrings(...) end
function ControlExists(parent,name) return visible[name] ~= nil end
function ShowControl(parent,name,value)
    assert(parent=="srw_factory_window" and type(name)=="string" and type(value)=="boolean")
    visible[name]=value
end
function SetControlText(parent,name,value) texts[name]=value end
function SendScriptEvent(handler,args,file,self) sent={handler,args} end
ANCHOR_TOP_LEFT=0
''')
lua.execute((root / 'scripts/ui/factory.lua').read_text(encoding='utf-8'))
lua.execute('''
SRW.CreateUI(); SRW.RefreshUI()
assert(visible.srw_order and visible.srw_release, "owner 101 UI hidden")
SRW.ClickUI("srw_order"); assert(sent[1]=="SRW_Order" and sent[2]=="101,50")
localTeam=201; SRW.RefreshUI(); assert(not visible.srw_order, "ally UI shown")
sent=nil; SRW.ClickUI("srw_order"); assert(sent==nil)
localTeam=101; selectedId=-1; SRW.RefreshUI(); assert(not visible.srw_release and not visible.srw_title, "panel remains after deselection")
sent=nil; SRW.ClickUI("srw_release"); assert(sent==nil)
selectedId=50; SRW.RefreshUI(); assert(visible.srw_release, "panel did not reopen")
devices[50]=nil; SRW.RefreshUI(); assert(not visible.srw_release and not visible.srw_title, "missing factory state")
assert(texts.srw_status == "$SRW_UI.no_factory")
visible={}; SRW.RefreshUI(); assert(visible.srw_title==false, "HUD recreation must remain hidden")
''')
print('PASS: team 101 registration, spending, bot tracking, owner UI, ally rejection, deselection')

lua.execute('''
devices={ [900]={team=101,kind="srw_dynamit_bot",built=true,pos=Vec3(160,0,0)},
    [901]={team=201,kind="mine",built=true,pos=Vec3(160,0,0)} }
data.srw.Robots={ [900]={Team=101,Direction=1,Age=0,Trigger=300} }
function GetDeviceCountSide(side) return 1 end
function GetDeviceIdSide(side,index) return 901 end
function GetRayHitTeamId() return 201 end
rayResult=RAY_HIT_STRUCTURE
SRW.UpdateRobots(0.04)
assert(devices[900], "allied device or structure triggered detonation")
devices[901].team=102; devices[901].kind="srw_dynamit_bot"
rayResult=RAY_HIT_NOTHING
SRW.UpdateRobots(0.04)
assert(devices[900], "enemy Dynamit Bot triggered detonation")
devices[901].kind="mine"
SRW.UpdateRobots(0.04)
assert(devices[900] and data.srw.Robots[900].FuseRemaining==0.1)
local stoppedX=devices[900].pos.x
devices[901].pos.x=100000
SRW.UpdateRobots(0.04); SRW.UpdateRobots(0.04)
assert(devices[900] and devices[900].pos.x==stoppedX, "activated bot moved or exploded early")
SRW.UpdateRobots(0.04)
assert(not devices[900], "enemy device failed to trigger detonation")
''')
print('PASS: ground attachment, allied targets and structures ignored, enemy bot ignored, enemy device triggers')

lua.execute('''
assert(SRW_PointSegmentDistanceSquared(Vec3(0,0,0),Vec3(100,-500,0),Vec3(100,500,0))==10000)
assert(SRW_PointSegmentDistanceSquared(Vec3(0,0,0),Vec3(3,4,0),Vec3(3,4,0))==25)
assert(SRW_PointSegmentDistanceSquared(Vec3(0,0,0),Vec3(10,0,0),Vec3(0,10,0))==50)
function GetDeviceCountSide(side) return 0 end
for _, threshold in ipairs({0.5*127.5,2.3*127.5}) do
    devices={[900]={team=101,kind="srw_dynamit_bot",built=true,pos=Vec3(0,0,0)}}
    data.srw.Robots={[900]={Team=101,Direction=1,Age=0,Trigger=threshold}}
    beamFixtures={side=1,[1]=Vec3(threshold,-500,0),[2]=Vec3(threshold,500,0)}
    rayResult=RAY_HIT_STRUCTURE
    SRW.UpdateRobots(0.04); assert(devices[900], "allied beam triggered")
    beamFixtures.side=2
    beamFixtures[1].x=threshold+1; beamFixtures[2].x=threshold+1
    SRW.UpdateRobots(0.04); assert(devices[900], "beam triggered outside radius")
    beamFixtures[1].x=threshold; beamFixtures[2].x=threshold
    SRW.UpdateRobots(0.04)
    assert(devices[900] and data.srw.Robots[900].FuseRemaining==0.1, "beam failed to activate fuse")
    beamFixtures={}
    local stoppedX=devices[900].pos.x
    SRW.UpdateRobots(0.04); SRW.UpdateRobots(0.04)
    assert(devices[900] and devices[900].pos.x==stoppedX, "bot chased departing vehicle")
    SRW.UpdateRobots(0.04); assert(not devices[900], "beam fuse cancelled when vehicle departed")
end
''')
print('PASS: beam segment distance, diagonal/degenerate beams, allied beam rejection, both trigger-radius boundaries')
