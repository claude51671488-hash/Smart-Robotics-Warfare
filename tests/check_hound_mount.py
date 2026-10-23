from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
local f={Team=101,Tier=1,Queue=0,Reserve=0,HoundReserve=1,Remaining=0}
data.srw.Factories={[50]=f}
local fail=true
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind=="srw_hound_machinegun" and fail then return -1 end
 local id=kind=="srw_hound" and 900 or 901
 devices[id]={team=team,kind=kind,pos=p,built=true}; return id
end
SRW_ReleaseHound(101,50)
assert(f.HoundReserve==1 and not devices[900] and not data.srw.Robots[900])
fail=false; SRW_ReleaseHound(101,50)
assert(f.HoundReserve==0 and devices[900] and devices[901] and SRW.ActiveCount(101,"srw_hound")==1)
devices[902]={team=102,kind="srw_hound",built=true,pos=Vec3(9000,0,0)}
devices[903]={team=102,kind="mine",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,i) return 902+i end
local shots={}; canAim=true
function FireWeapon(id,p,e,flags) shots[id]=(shots[id] or 0)+1; return 0 end
SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04)
assert(data.srw.Robots[900].Target==902 and data.srw.MountedWeapons[901].Target==903)
assert(shots[900]==1 and shots[901]==1)
devices[900].disabled=true
for i=1,20 do SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04) end
assert(shots[900]==1 and shots[901]==1)
devices[900].disabled=false; devices[901]=nil; SRW.UpdateMountedWeapons(.04)
assert(devices[900] and not data.srw.MountedWeapons[901])
f.HoundReserve=1; f.ExitRemaining=0; SRW_ReleaseHound(101,50)
devices[900]=nil; SRW.UpdateMountedWeapons(.04); assert(not devices[901])
''')
print('PASS: Hound full-body release, rollback, independent targets, EMP, mount loss and root cleanup')
