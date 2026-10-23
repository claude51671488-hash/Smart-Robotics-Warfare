from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
for name in ['factories/squads.lua','robots/tank.lua','robots/aa.lua','robots/shield.lua','shields.lua','robots/spacing.lua']:
 lua.execute((root/'scripts'/name).read_text())
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}; data.srw.Shields={}
data.srw.Factories={[50]={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,15,1); assert(#f.SquadDraft==0)
f.Tier=3; devices[50].kind="srw_factory_ground_3"
SRW_SquadEdit(101,50,15,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
for i=1,1125 do SRW.UpdateFactories(.04) end
assert(f.Squad.Produced==1 and balances[101].metal==8240)
function EnableWeapon(name,enabled,side) assert(side==1) end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 local id=kind=="srw_colossus_bot" and 900 or (kind=="srw_colossus_laser" and 901 or (kind=="srw_regent_rockets" and 904 or (devices[906] and 907 or 906)))
 devices[id]={team=team,kind=kind,pos=p,built=true}; return id
end
function DeleteDeviceById(id) devices[id]=nil end
groundResult=1; rayResult=0
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and f.ExitRemaining==8 and #SRW.SortedIds(data.srw.MountedWeapons)==4)
function GetDeviceCountSide(side) return side==1 and devices[900] and 1 or 0 end
function GetDeviceIdSide(side,index) return 900 end
SRW.ScanShields(); SRW.UpdateShieldPower(.04)
assert(data.srw.Shields[900].HP==9000 and data.srw.Shields[900].Active)
local laser=data.srw.MountedWeapons[901]; laser.BeamRemaining=1
local x=devices[900].pos.x
SRW.UpdateHound(900,data.srw.Robots[900],.04); assert(devices[900].pos.x==x)
devices[905]={team=101,kind="srw_hound",built=true,pos=Vec3(x,0,0)}
data.srw.Robots[905]={Team=101,Kind="srw_hound",Direction=1}
SRW.SeparateRobots(.04); assert(devices[900].pos.x==x,"separation moved a firing laser parent")
data.srw.Robots[900].EMPRemaining=5; SRW.UpdateShieldPower(.04)
SRW.ShieldDamage(data.srw.Shields[900],100); assert(data.srw.Shields[900].HP==8850)
devices[900]=nil; SRW.UpdateMountedWeapons(.04); SRW.ScanShields()
assert(not devices[901] and not devices[904] and not data.srw.Shields[900])
''')
print('PASS: Colossus tier III/production, mounts, personal shield, laser parent hold, spacing exclusion, EMP and cleanup')
