from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
for name in ['combat/emp.lua','factories/squads.lua']:
 lua.execute((root/'scripts'/name).read_text(encoding='utf-8'))
lua.execute('''
local shell; for _,p in ipairs(Projectiles) do if p.SaveName=="srw_emp_shell" then shell=p end end
assert(shell.SaveName=="srw_emp_shell" and shell.ExplodeOnTouch and shell.Gravity==981)
assert(shell.ProjectileDamage==2 and shell.EMPDuration==0 and shell.EMPRadius==0)
assert(shell.SRWShieldDamage==500)
DESTROYTYPE_HITDEVICE=1; DESTROYTYPE_HITSTRUCTURE=2; DESTROYTYPE_HITTERRAIN=3
DESTROYTYPE_SCRIPT=4; DESTROYTYPE_EXPIRED=5; DESTROYTYPE_HITPROJECTILE=6
local empCalls={}
function EMPDevice(id,duration) empCalls[id]=duration end
function NodePosition(id) assert(id==100); return Vec3(0,0,0) end
devices={
 [1]={team=102,kind="srw_hound",built=true,pos=Vec3(100,0,0)},
 [2]={team=102,kind="srw_emp_bot",built=true,pos=Vec3(150,0,0)},
 [3]={team=201,kind="srw_hound",built=true,pos=Vec3(100,0,0)},
 [4]={team=102,kind="mine",built=true,pos=Vec3(50,0,0)},
 [5]={team=102,kind="mine",built=true,pos=Vec3(500,0,0)},
}
data.srw.Robots={[1]={Team=102,Kind="srw_hound"},[2]={Team=102,Kind="srw_emp_bot"}}
function GetDeviceCountSide(side) return 5 end
function GetDeviceIdSide(side,index) return index+1 end
for cause=4,6 do SRW.EMPImpact(100,101,"srw_emp_shell",cause) end
assert(next(empCalls)==nil and not data.srw.Robots[2].EMPRemaining)
SRW.EMPImpact(100,101,"srw_hound_shell",1); assert(next(empCalls)==nil)
SRW.EMPImpact(100,101,"srw_emp_shell",1)
assert(empCalls[1]==5 and empCalls[4]==5)
assert(not empCalls[2] and not empCalls[3] and not empCalls[5])
assert(data.srw.Robots[2].EMPRemaining==5)
SRW.UpdateEMP(2); assert(data.srw.Robots[2].EMPRemaining==3)
SRW.EMPImpact(100,101,"srw_emp_shell",2); assert(data.srw.Robots[2].EMPRemaining==5)
local target=Vec3(1000,0,0)
function GetRandomFloat(a,b,key) assert(key=="SRW EMP aim"); return b end
local aim=SRW.EMPAim(2,data.srw.Robots[2],target); assert(aim.y~=target.y)
SRW.UpdateEMP(5); assert(not data.srw.Robots[2].EMPRemaining)
assert(SRW.EMPAim(2,data.srw.Robots[2],target)==target)
-- End-to-end squad production and existing mobile weapon AI.
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.Factories={[50]={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,7,1); assert(#f.SquadDraft==0)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_SquadEdit(101,50,7,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
assert(f.CurrentType=="srw_emp_bot")
for i=1,300 do SRW.UpdateFactories(.04) end
assert(SRW.FactoryReserve(f)==1 and f.Squad.Produced==1)
function EnableWeapon(name,enabled,side) assert((name=="srw_emp_bot" or name=="srw_emp_turret") and side==1) end
local oldCreate=dlc2_CreateFloatingDevice
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind=="srw_emp_turret" then devices[1900]={team=team,kind=kind,built=true,pos=p};return 1900 end
 return oldCreate(team,kind,p,angle)
end
groundResult=1; rayResult=0; spawnId=900
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and data.srw.Robots[900].Kind=="srw_emp_bot")
devices[901]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide(side,index) return 901 end
canAim=true; fireCalls=0; SRW.UpdateRobots(.04)
assert(fireCalls==1 and data.srw.Robots[900].FireWait==6)
SRW.UpdateRobots(.04); assert(fireCalls==1)
''')
print('PASS: EMP impact causes, allies/radius, tier effects, refresh/expiry, aim disruption, factory gate, production, release and firing')
