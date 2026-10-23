from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_individual.py'))['lua']
lua.execute((r/'ui/factory_window.lua').read_text())
lua.execute('''
ui={}; visible={}; texts={}; extentCalls=0
function LoadControl(filename,parent)
 assert(filename:match('/ui/factory_window.lua$') and parent=='')
 local function add(node,owner)
  assert(node.Type=='Static')
  for i=1,4 do assert(node.Colour[i]==node.ColourLower[i]) end
  local p=node.Control.Position; local s=node.Control.Size; local c=node.Colour
  ui[node.Name]={parent=owner,pos=Vec3(p[1],p[2],p[3]),size=Vec3(s[1],s[2],0),
   colour={r=c[1],g=c[2],b=c[3],a=c[4]}}
  visible[node.Name]=true
  for _,child in ipairs(node.Control.Children or {}) do add(child,node.Name) end
 end
 add(Root,parent)
end
function AddTextControl(parent,name,text,anchor,pos,relative,style)
 assert(parent=="srw_factory_window")
 ui[name]={parent=parent,pos=pos}; visible[name]=true; texts[name]=text
end
AddTextButtonControl=AddTextControl
function AddButtonControl(parent,name,texture,anchor,size,pos,style)
 assert(parent=="srw_factory_window" or name=="srw_factory_window")
 ui[name]={parent=parent,pos=pos,size=size}; visible[name]=true
end
AddSpriteControl=AddButtonControl
function SetControlSpriteByParent(parent,name,sprite) ui[name].sprite=sprite end
function ShowControl(parent,name,value) visible[name]=value end
function SetControlColour(parent,name,colour) ui[name].colour=colour end
function SetControlRelativePos(parent,name,pos) ui[name].pos=pos end
function GetWorldExtents() extentCalls=extentCalls+1; return {MinX=0,MaxX=10000,MinY=0,MaxY=3000} end
devices={[50]={team=101,kind="srw_factory_ground_3",built=true,pos=Vec3(0,0,0)},
 [1]={team=101,kind="srw_hound",built=true,pos=Vec3(1000,1000,0)},
 [2]={team=201,kind="srw_hound",built=true,pos=Vec3(2000,1000,0)},
 [3]={team=102,kind="srw_hound",built=true,pos=Vec3(8000,1000,0)},
 [4]={team=102,kind="reactor",built=true,pos=Vec3(9000,1000,0)}}
data.srw.Robots={[1]={Team=101},[2]={Team=201},[3]={Team=102}}
data.srw.Factories={[50]={Team=101,Tier=3,Queue=0,Reserve=0,Remaining=0}}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,i) return i==0 and 3 or 4 end
selectedId=50; localTeam=101
''')
lua.execute((r/'scripts/ui/window.lua').read_text())
lua.execute('''
SRW.CreateUI(); SRW.RefreshUI(); SRW.RefreshFactoryMap(.01)
assert(texts.srw_price1=="200 M / 2000 E")
assert(ui.srw_factory_window.colour.r==24 and ui.srw_factory_window.colour.a==255)
assert(ui.srw_map_background.colour.r==9 and ui.srw_map_background.colour.a==255)
assert(visible.srw_factory_window and visible.srw_map_dot3 and not ui.srw_map_dot4)
assert(ui.srw_map_dot1.sprite:match("map_ally.png$") and ui.srw_map_dot3.sprite:match("map_enemy.png$"))
assert(extentCalls==0 and ui.srw_map_dot3.pos.x-ui.srw_map_dot1.pos.x>120)
assert(ui.srw_map_dot3.pos.x>ui.srw_map_dot1.pos.x)
local x=ui.srw_map_dot1.pos.x
local initialBounds=SRW.MapBounds({})
local left=initialBounds.MinX
assert(SRW.MapBounds({Vec3(4000,0,0)}).MinX==left,"map shrank after casualties")
devices[1].pos.x=3000; SRW.RefreshFactoryMap(.1); assert(ui.srw_map_dot1.pos.x==x)
SRW.RefreshFactoryMap(.11); assert(ui.srw_map_dot1.pos.x>x)
devices[4]=nil; SRW.RefreshFactoryMap(.2); assert(not visible.srw_map_dot3)
SRW.SquadEditorOpen=true; SRW.RefreshUI()
assert(texts.srw_squad_price1=="220 M / 2200 E")
assert(not visible.srw_price1)
assert(ui.srw_squad_progress.pos.y+ui.srw_factory_window.pos.y<350)
for name,c in pairs(ui) do
 if c.parent=="srw_factory_window" then assert(c.pos.y>=0 and c.pos.y<300,name) end
end
SRW.ClickUI("srw_window_close"); local count=extentCalls
SRW.RefreshFactoryMap(1); assert(not visible.srw_factory_window and extentCalls==count)
selectedId=-1; SRW.RefreshUI(); selectedId=50; SRW.RefreshUI()
assert(visible.srw_factory_window)
localTeam=201; SRW.RefreshUI(); assert(not visible.srw_factory_window)
''')
print('PASS: factory window bounds, close/reopen, ownership, map colours/coordinates, rate limit and removed markers')
