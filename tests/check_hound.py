from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
suite=runpy.run_path(str(root/'tests/check_prototype.py'))
lua=suite['lua']
lua.execute('''
Weapons={}; Projectiles={{SaveName="cannon",ProjectileDamage=999,Impact={test=1}}}
''')
for name in ['weapons/weapon_list.lua','weapons/projectile_list.lua']:
    code=(root/name).read_text(encoding='utf-8')
    lua.execute(code); lua.execute(code)
lua.execute('''
assert(#Weapons==67 and Weapons[1].BuildOnGroundOnly and Weapons[1].dlc2_BuildAnywhere)
assert(#Projectiles==14 and Projectiles[1].ProjectileDamage==999 and Projectiles[2].ProjectileDamage==1400)
assert(Projectiles[2].Gravity==981 and Projectiles[2].ExplodeOnTouch)
assert(Projectiles[2].ProjectileSplashDamage==60 and Projectiles[2].ProjectileSplashDamageMaxRadius==500)
Projectiles[2].Impact.test=2; assert(Projectiles[1].Impact.test==1)
function EnableWeapon(name,enabled,side) assert((name=="srw_hound" or name=="srw_hound_machinegun") and side==1) end
FIREFLAG_NORMAL=0; fireCalls=0; canAim=true
FIREFLAG_DIRECTAIM=32
function AimWeapon(id,p) return canAim end
function FireWeapon(id,p,error,flags) assert(flags==0); fireCalls=fireCalls+1; return 0 end
function FireWeaponWithPower(id,p,error,testError,flags,power)
 assert(flags==FIREFLAG_DIRECTAIM and testError==-1 and power==1)
 return FireWeapon(id,p,error,FIREFLAG_NORMAL)
end
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Factories={[50]={Team=101,Queue=0,Reserve=0,Remaining=0,Status="ready"}}
data.srw.Robots={}; balances[101]={metal=1000,energy=10000}
groundResult=1; rayResult=0; beamFixtures={}
function CastGroundRay(a,b,flags) rayGroundX=a.x; return groundResult end
function GetRayHitPosition() return Vec3(rayGroundX,0,0) end
''')
lua.execute((root/'scripts/robots/hound.lua').read_text(encoding='utf-8'))
lua.execute((root/'scripts/robots/tank.lua').read_text())
lua.execute('''
local oldCreate=dlc2_CreateFloatingDevice
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind=="srw_hound_machinegun" then
  devices[1700]={team=team,kind=kind,pos=p,built=true}; return 1700
 end
 return oldCreate(team,kind,p,angle)
end
function DeleteDeviceById(id) devices[id]=nil end
SRW_OrderHound(201,50); assert(not data.srw.Factories[50].HoundQueue)
SRW_OrderHound(101,50); SRW.Order(101,50)
SRW.UpdateFactories(0.04)
local f=data.srw.Factories[50]
assert(f.CurrentType=="srw_hound" and balances[101].metal==800)
for i=1,175 do SRW.UpdateFactories(0.04) end
assert(f.HoundReserve==1 and f.Reserve==0)
SRW.UpdateFactories(0.04); assert(f.CurrentType=="srw_dynamit_bot")
spawnId=-1; SRW_ReleaseHound(101,50); assert(f.HoundReserve==1)
spawnId=700; SRW_ReleaseHound(101,50)
assert(f.HoundReserve==0 and data.srw.Robots[700].Kind=="srw_hound")
function GetDeviceCountSide(side) return 0 end
local p=devices[700].pos.x; SRW.UpdateRobots(0.04)
assert(devices[700].pos.x>p and fireCalls==0)
devices[701]={team=102,kind="mine",built=true,pos=Vec3(500,0,0)}
devices[702]={team=102,kind="srw_dynamit_bot",built=true,pos=Vec3(700,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return 701+index end
p=devices[700].pos.x; SRW.UpdateRobots(0.04)
assert(data.srw.Robots[700].Target==702 and devices[700].pos.x==p and fireCalls==1)
devices[700].disabled=true; SRW.UpdateRobots(0.4)
assert(fireCalls==1 and devices[700].pos.x==p)
devices[700].disabled=false; devices[701].team=201; devices[702].team=201
SRW.UpdateRobots(0.04); assert(devices[700].pos.x>p and fireCalls==1)
assert(SRW.ActiveCount(101,"srw_hound")==1 and SRW.ActiveCount(101,"srw_dynamit_bot")==0)
f.Queue=19; f.HoundQueue=1; SRW_OrderHound(101,50); SRW.Order(101,50)
assert(f.Queue==19 and f.HoundQueue==1)
f.Remaining=0; f.Reserve=19; f.HoundReserve=1
local energy=balances[101].energy; SRW.UpdateFactories(0.04)
assert(balances[101].energy==energy and f.Status=="reserve_full")
devices[702].team=102; devices[702].pos.x=devices[700].pos.x+3400
data.srw.Robots[700].FireWait=0
SRW.UpdateRobots(0.04)
assert(data.srw.Robots[700].Target==702, "new long-range target not acquired")
local shots=fireCalls
for i=1,20 do SRW.UpdateRobots(0.04) end
assert(fireCalls==shots, "fire commands repeated during reload")
''')
print('PASS: hound registration, isolated projectile, shared production/capacity, failed spawn, movement, target priority, stop/fire, EMP, friendly rejection, separate active caps')
