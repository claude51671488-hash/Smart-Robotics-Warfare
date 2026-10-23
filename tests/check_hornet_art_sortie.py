"""Actual Hornet controller: no stationary reload, both sides, EMP and art states."""
from pathlib import Path
import runpy,json,struct
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hornet.py'))['lua']
for file in ('robots/sortie.lua','robots/hornet_art.lua'):
 lua.execute((r/'scripts'/file).read_text())
lua.execute('''
local shots={};local sprites={}
function SetDeviceAngle(id,a)
 assert(devices[id].kind=='srw_hornet_bot','rotated an independent silo or ground unit')
 devices[id].angle=a
end
function GetDeviceAngle(id) return devices[id].angle or math.pi/2 end
function GetWeaponBarrelPosition(id) return devices[id].pos end
function GetWeaponHardpointPosition(id)
 local d=devices[id];local p=d.pos
 if d.kind~='srw_hornet_bot' then return p end
 local bot=data.srw.Robots[id]
 local a=(d.team%100==1 and 0 or math.pi)+(bot and bot.FlightPitch or 0)
 return Vec3(p.x+88*math.cos(a),p.y+88*math.sin(a),0)
end
function SetDeviceSpriteState(id,state) sprites[id]=state end
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide() return 800 end
function NodeExists() return false end
function SRW.FireRobotWeapon(id,cfg,aim,spread)
 shots[#shots+1]=id;SRW.HornetShot(id);return 0
end
for _,team in ipairs({101,102}) do
 local dir=team==101 and 1 or -1;local enemy=team==101 and 102 or 101
 devices={[50]={team=team,kind='srw_factory_air_1',built=true,pos=Vec3(-dir*2500,0,0)},
 [800]={team=enemy,kind='srw_hornet_bot',built=true,pos=Vec3(dir*2000,-900,0)}}
 data.srw.Robots={};data.srw.MountedWeapons={};shots={}
 local ok,id=SRW.SpawnAirRobot(team,50,'srw_hornet_bot');assert(ok)
 local bot=data.srw.Robots[id];local cfg=SRW.Config.Robots.srw_hornet_bot
 function SRW.DeviceTargets(side)
  return {{Id=800,Kind='srw_hornet_bot',Position=devices[800].pos}}
 end
 local seen={};local moved=0
 for i=1,1000 do
  local p=devices[id].pos;local previous=bot.SortieHeading
  SRW.UpdateAirRobot(id,bot,.04);SRW.UpdateMountedWeapons(.04)
  seen[bot.SortiePhase]=true
  local q=devices[id].pos;local step=math.sqrt((q.x-p.x)^2+(q.y-p.y)^2)
  assert(math.abs(step-cfg.SpeedMinesPerSecond*127.5*.04)<.001,'hovering during reload')
  if previous then assert(math.abs(bot.SortieHeading-previous)<=cfg.SortieTurnRate*.04+.0001,'instant turn') end
  moved=moved+step
 end
 assert(seen.attack and seen.egress and seen.orbit and seen.approach,'missing sortie stage')
 assert((bot.HornetGunSerial or 0)>0 and (bot.HornetRocketSerial or 0)>0,'missing weapon')
 local p=devices[id].pos;devices[id].disabled=true
 SRW.UpdateAirRobot(id,bot,.04);assert(devices[id].pos==p,'EMP did not arrest flight')
 SRW.RefreshHornetVisuals(.016);assert(sprites[id]==(bot.ArtFacing<0 and 'IdleLeft' or 'IdleRight'))
 devices[id].disabled=false;SRW.RefreshHornetVisuals(.3)
 for child,part in pairs(data.srw.MountedWeapons) do SRW.HornetShot(child) end
 SRW.RefreshHornetVisuals(.016);assert(sprites[id]:find('Launch'),'bay animation not triggered')
 SRW.RefreshHornetVisuals(.3);assert(not sprites[id]:find('Launch'),'bay animation did not expire')
 devices[id]=nil;data.srw.Robots[id]=nil;SRW.RefreshHornetVisuals(.016)
end
''')
geo=json.loads((r/'ui/textures/robots/hornet/geometry.json').read_text())
mount=lua.globals().SRW.Config.Robots.srw_hornet_bot.Mounts[1]
assert (mount.X,mount.Y)==(geo['MountX'],geo['MountY'])
for p in (r/'ui/textures/robots/hornet').glob('*.png'):
 if p.name=='muzzle_flash.png':continue
 b=p.read_bytes();assert struct.unpack('>II',b[16:24])==(384,192) and b[25]==6,p.name
print('PASS: continuous speed, bounded turns, attack/egress/orbit, both salvos, EMP, launch animation and fixed texture geometry')
