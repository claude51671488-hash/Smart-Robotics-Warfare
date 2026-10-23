"""New ground assemblies, rollback, tier gates and immediate threats; engine mocked."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
for module in ('factories/squads.lua','robots/aa.lua','combat/emp.lua','shields.lua','robots/shield.lua'):
    lua.execute((r/'scripts'/module).read_text(encoding='utf-8'))
lua.execute('''
function EnableWeapon() end
function DeleteDeviceById(id) devices[id]=nil end
local serial=2000;local fail
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(angle==90)
 if kind==fail then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=kind,pos=p,built=true};return serial
end
function SetDeviceAngle() error('do not mix angle units after creation') end
for index,kind in pairs({[13]='srw_heavy_siege_bot',[21]='srw_vault_bot',[22]='srw_tempest_bot',[23]='srw_mlrs_bot'}) do
 for _,team in ipairs({101,102}) do
  devices={[50]={team=team,kind='srw_factory_ground_2',built=true,pos=Vec3(0,0,0)}}
  data.srw.Robots={};data.srw.MountedWeapons={}
  local f={Team=team,Tier=2,Queue=0,Reserve=0,Remaining=0}
  data.srw.Factories={[50]=f};balances[team]={metal=100000,energy=1000000}
  assert(SRW.RobotKinds[index]==kind)
  SRW_OrderIndividual(team,50,index);assert(not f[kind..'Queue'])
  f.Tier=3;devices[50].kind='srw_factory_ground_3'
  SRW_OrderIndividual(team,50,index);SRW.UpdateFactories(.04)
  assert(f.CurrentType==kind)
  for i=1,1200 do SRW.UpdateFactories(.04) end
  assert(f[kind..'Reserve']==1)
  fail=SRW.Config.Robots[kind].Mounts[1].Kind
  SRW_ReleaseIndividual(team,50,index)
  assert(f[kind..'Reserve']==1 and next(data.srw.Robots)==nil and next(data.srw.MountedWeapons)==nil)
  fail=nil;SRW_ReleaseIndividual(team,50,index)
  local roots=SRW.SortedIds(data.srw.Robots);assert(#roots==1)
  local root=roots[1];local cfg=SRW.Config.Robots[kind]
  assert(f[kind..'Reserve']==0 and #SRW.SortedIds(data.srw.MountedWeapons)==#cfg.Mounts)
  for child,part in pairs(data.srw.MountedWeapons) do assert(part.Root==root and part.Team==team) end
  if kind=='srw_vault_bot' then
   local s=SRW.NewMobileShield(team,kind);assert(s.HP==8500 and #s.Arc==65)
  end
 end
end
-- A close robot must not suppress a valid artillery shot further away.
devices={[1]={team=101,kind='srw_heavy_siege_bot',built=true,pos=Vec3(0,0,0)},
 [2]={team=102,kind='srw_hound',built=true,pos=Vec3(300,0,0)},
 [3]={team=102,kind='mine',built=true,pos=Vec3(6000,0,0)}}
data.srw.Robots={[1]={Team=101,Kind='srw_heavy_siege_bot',Direction=1}};data.srw.MountedWeapons={}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,i) return i+2 end
function AimWeapon() return true end
local shots=0;function FireWeapon(id,p) shots=shots+1;return 0 end
SRW.UpdateHound(1,data.srw.Robots[1],.04)
assert(shots==1 and data.srw.Robots[1].Target==3)
-- A fixed-angle silo points vertically while its seeker receives the real target.
local painted
function SetWeaponPaintTarget(id,p) painted=p end
local launch=SRW.LaunchAim(1,{Guided=true},Vec3(6000,-200,0))
assert(launch.x==0 and launch.y==-5000 and painted.x==6000 and painted.y==-200)
''')
print('PASS: four complete ground loadouts on both sides, tier gates, atomic rollback, individual release, Vault dome, close-threat artillery and independent silo paint/launch aim')
