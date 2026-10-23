from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
for name in ['factories/squads.lua','robots/tank.lua','robots/aa.lua','combat/emp.lua']:
 lua.execute((root/'scripts'/name).read_text())
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
data.srw.Factories={[50]={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,14,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
for i=1,625 do SRW.UpdateFactories(.04) end
assert(f.Squad.Produced==1 and SRW.FactoryReserve(f)==1)
local failChild=true; local failRockets=false
function EnableWeapon(name,enabled,side) assert(side==1) end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind=="srw_tank_turret" and failChild then return -1 end
 if kind=="srw_tank_rockets" and failRockets then return -1 end
 local id=kind=="srw_tank_bot" and 900 or (kind=="srw_tank_turret" and 901 or 904)
 devices[id]={team=team,kind=kind,pos=p,built=true}; return id
end
function DeleteDeviceById(id) devices[id]=nil end
groundResult=1; rayResult=0
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==0 and not devices[900] and not data.srw.Robots[900])
failChild=false; failRockets=true; f.ExitRemaining=0; SRW.UpdateFactories(.04)
assert(f.Squad.Released==0 and not devices[900] and not devices[901] and next(data.srw.MountedWeapons)==nil)
failRockets=false; f.ExitRemaining=0; SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and f.ExitRemaining==5)
assert(SRW.ActiveCount(101,"srw_tank_bot")==1 and not data.srw.Robots[901])
local part=data.srw.MountedWeapons[901]; assert(part.Root==900 and part.Mounted)
devices[902]={team=102,kind="mine",built=true,pos=Vec3(1800,0,0)}
devices[903]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return 902+index end
local shots={}; canAim=true
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId(side,index) return 3000 end
function NodeExists(id) return true end
function NodeTeam(id) return 102 end
function NodePosition(id) return Vec3(1000,-500,0) end
function NodeVelocity(id) return Vec3(-500,0,0) end
function GetNodeProjectileSaveName(id) return "mortar2" end
function GetProjectileParamFloat(name,team,param,default) return 15 end
function FireWeapon(id,p,error,flags) shots[id]=(shots[id] or 0)+1; return 0 end
SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04)
assert(data.srw.Robots[900].Target==903 and part.Target==903)
assert(shots[900]==1 and shots[901]==1 and shots[904]==1)
assert(data.srw.MountedWeapons[904].Target==3000)
devices[900].pos=Vec3(300,20,0); SRW.UpdateMountedWeapons(.04)
assert(devices[901].pos.x==189.5 and devices[901].pos.y==-167)
assert(devices[904].pos.x==-210 and devices[904].pos.y<=-405)
devices[900].disabled=true; part.BeamRemaining=0; part.FireWait=0
SRW.UpdateMountedWeapons(.04); assert(shots[901]==1)
devices[900].disabled=false; data.srw.Robots[900].EMPRemaining=4
SRW.UpdateMountedWeapons(.04); assert(part.EMPRemaining==4)
devices[901]=nil; SRW.UpdateMountedWeapons(.04)
assert(devices[900] and not data.srw.MountedWeapons[901],"turret loss destroyed hull or respawned turret")
assert(SRW.SpawnTank(101,50)); devices[900]=nil
SRW.UpdateMountedWeapons(.04); assert(not devices[901] and not devices[904] and next(data.srw.MountedWeapons)==nil)
''')
print('PASS: tank production, transactional spawn, independent targeting, mounted movement, EMP, part loss and orphan cleanup')
