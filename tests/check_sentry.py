from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
for name in ['factories/squads.lua','robots/tank.lua','robots/aa.lua','robots/sentry.lua']:
 lua.execute((r/'scripts'/name).read_text())
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
local f={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}
data.srw.Factories={[50]=f}; balances[101]={metal=10000,energy=100000}
SRW_OrderIndividual(101,50,16); SRW.UpdateFactories(.04); SRW.UpdateFactories(11)
assert(f.srw_sentry_botReserve==1 and balances[101].metal==9750)
local fail=true
function EnableWeapon(...) end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if fail and kind=="srw_sentry_rockets" then return -1 end
 local id=kind=="srw_sentry_bot" and 900 or 901
 devices[id]={team=team,kind=kind,pos=p,built=true}; return id
end
function DeleteDeviceById(id) devices[id]=nil end
groundResult=1; rayResult=0
SRW_ReleaseIndividual(101,50,16)
assert(f.srw_sentry_botReserve==1 and not devices[900] and not data.srw.Robots[900])
fail=false; SRW_ReleaseIndividual(101,50,16)
assert(f.srw_sentry_botReserve==0 and f.ExitRemaining==3 and devices[901])
devices[902]={team=102,kind="srw_hound",built=true,pos=Vec3(900,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide(side,i) return 902 end
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId(side,i) return 3000 end
function NodeExists(id) return id==3000 end
function NodeTeam(id) return 102 end
function NodePosition(id) return Vec3(1000,-300,0) end
function NodeVelocity(id) return Vec3(-300,0,0) end
function GetNodeProjectileSaveName(id) return "mortar2" end
function GetProjectileParamFloat(...) return 15 end
local shots={}; canAim=true
function FireWeapon(id,p,error,flags) shots[id]=(shots[id] or 0)+1; return 0 end
SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04)
assert(shots[900]==1 and shots[901]==1)
assert(data.srw.Robots[900].Target==902 and data.srw.MountedWeapons[901].Target==3000)
devices[900].disabled=true
for i=1,100 do SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04) end
assert(shots[900]==1 and shots[901]==1)
devices[900]=nil; SRW.UpdateMountedWeapons(.04); assert(not devices[901])
-- Tier-I squad production uses the same whole-body spawn.
data.srw.Robots={}; f.ExitRemaining=0
SRW_SquadEdit(101,50,16,1); SRW_SquadStart(101,50)
SRW.UpdateFactories(.04); SRW.UpdateFactories(11); SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and devices[900] and devices[901])
''')
print('PASS: Watchman tier-I individual/squad production, rollback, independent weapons, EMP and cleanup')
