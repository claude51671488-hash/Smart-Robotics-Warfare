"""Rigid pitched aircraft, continuous vertical turns and independent gun art.

Engine rotation convention is backed by the earlier native probe (0 -> down,
pi/2 -> right). These regressions do not replace a new Forts visual inspection.
"""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hornet_art_sortie.py'))['lua']
lua.execute('''
local pi=math.pi
local function close(a,b,message) assert(math.abs(a-b)<.00001,message) end
function SRW.DeviceTargets() return {} end
function SRW.AirTargets() return {} end
local lastState
function SetDeviceSpriteState(id,state) lastState=state end
for _,team in ipairs({101,102}) do
 local dir=team==101 and 1 or -1
 devices={[500]={team=team,kind='srw_hornet_bot',built=true,pos=Vec3(dir*1200,-1800,0)},
          [501]={team=team,kind='srw_hornet_rockets',built=true,pos=Vec3(0,0,0)}}
 local b={Team=team,Kind='srw_hornet_bot',Direction=dir,Mounted=true,HomeX=0,CruiseY=-1800,
          SortiePhase='orbit',SortieOrbitX=0,SortieOrbitY=-1800,SortieOrbitDirection=1,
          SortieHeading=dir<0 and pi or 0,AirPhase='egress'}
 data.srw.Robots={[500]=b}
 local part={Root=500,Kind='srw_hornet_rockets',Team=team,Direction=dir,
             Mounted=true,OffsetX=-23.5,OffsetY=-85}
 data.srw.MountedWeapons={[501]=part}
 local previous,minimum,maximum
 for i=1,1500 do
  local p=devices[500].pos
  SRW.UpdateSortieFlight(500,b,.04);SRW.UpdateMountedWeapons(.04)
  local a=GetDeviceAngle(500)
  -- This mirrors the measured engine convention, not the implementation's
  -- angle subtraction: the selected silhouette's nose must follow real motion.
  close(dir*math.sin(a),b.AirVelocity.x/510,'nose not aligned with horizontal flight')
  close(dir*math.cos(a),b.AirVelocity.y/510,'nose not aligned with vertical flight')
  if previous then assert(math.abs(a-previous)<=.072001,'body snapped at vertical turn') end
  previous=a;minimum=math.min(minimum or a,a);maximum=math.max(maximum or a,a)
  assert(b.ArtFacing==dir,'silhouette mirrored halfway through loop')
  local q=devices[500].pos;local m=devices[501].pos
  close((m.x-q.x)^2+(m.y-q.y)^2,23.5^2+85^2,'hatch detached during turn')
  -- Inverse engine frame: attachment remains at the same local hull coordinates.
  local c,s=math.cos(b.FlightPitch),math.sin(b.FlightPitch)
  close((m.x-q.x)*c+(m.y-q.y)*s,-23.5*dir,'hatch moved along hull')
  close(-(m.x-q.x)*s+(m.y-q.y)*c,-85,'hatch moved across hull')
  SRW.RefreshHornetVisuals(.04)
 end
 assert(maximum-minimum>2*pi,'test failed to exercise a complete body rotation')
 local frozen=GetDeviceAngle(500);local at=devices[500].pos
 devices[500].disabled=true;b.SortieHeading=b.SortieHeading+1
 SRW.UpdateSortieFlight(500,b,.04);SRW.UpdateMountedWeapons(.04)
 close(GetDeviceAngle(500),frozen,'EMP changed body orientation')
 assert(devices[500].pos==at,'EMP moved hull')
 -- A gun aimed opposite to its local hull axis needs the other gun art, but
 -- the hull, engine and hatch sprite must retain their selected silhouette.
 local head=at
 local function gun(localSide)
  local c,s=math.cos(b.FlightPitch),math.sin(b.FlightPitch)
  function GetWeaponHardpointPosition(id)
   return Vec3(head.x+88*localSide*c,head.y+88*localSide*s,0)
  end
  SRW.RefreshHornetVisuals(.3)
 end
 gun(dir);assert(lastState==(dir<0 and 'IdleLeft' or 'IdleRight'))
 gun(-dir);assert(lastState==(dir<0 and 'IdleLeftGunRight' or 'IdleRightGunLeft'))
end
''')
# Every dynamically selected combined state must exist in every sprite. No new
# bitmap copies are required for independent hull/gun facing.
lua.execute((root/'ui/textures/robots/hornet/geometry.lua').read_text())
lua.execute('path="srw";function dofile() end')
lua.execute((root/'scripts/hornet_weapon_art.lua').read_text())
lua.execute('''
for _,sprite in ipairs(Sprites) do
 for _,side in ipairs({'Right','Left'}) do
  for _,mode in ipairs({'Cruise','Climb','Dive','Boost','Idle'}) do
   local suffix=side=='Right' and 'GunLeft' or 'GunRight'
   assert(sprite.States[mode..side] and sprite.States[mode..side..suffix])
   if mode~='Idle' then assert(sprite.States[mode..side..'Launch'..suffix]) end
  end
 end
end
''')
print('PASS: both flight frames follow velocity through full loops, attached hatch, EMP freeze, independent turret art and complete sprite states')
