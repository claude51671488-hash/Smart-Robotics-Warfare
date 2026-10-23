from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute((root/'scripts/robots/aa.lua').read_text(encoding='utf-8'))
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; balances[101]={metal=10000,energy=100000}
data.srw.Factories={[50]={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0,Status="ready"}}
local f=data.srw.Factories[50]
SRW_OrderAA(201,50); assert(not f.AAQueue)
SRW_OrderAA(101,50); SRW.UpdateFactories(0.04)
assert(f.CurrentType=="srw_aa_bot" and balances[101].metal==9750)
for i=1,250 do SRW.UpdateFactories(0.04) end
assert(f.AAReserve==1)
function EnableWeapon(name,enabled,side) assert((name=="srw_aa_bot" or name=="srw_sieve_turret") and side==1) end
local oldCreate=dlc2_CreateFloatingDevice
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind=="srw_sieve_turret" then devices[1900]={team=team,kind=kind,built=true,pos=p}; return 1900 end
 return oldCreate(team,kind,p,angle)
end
spawnId=-1; SRW_ReleaseAA(101,50); assert(f.AAReserve==1)
spawnId=1000; SRW_ReleaseAA(101,50); assert(f.AAReserve==0)
devices[1000].pos=Vec3(0,0,0); local bot=data.srw.Robots[1000]
local team=102; local alive=true; local radius=15
local p=Vec3(1000,-500,0); local v=Vec3(-1000,0,0)
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId(side,index) return 3000 end
function NodeExists(id) return alive end
function NodeTeam(id) return team end
function NodePosition(id) return p end
function NodeVelocity(id) return v end
function GetNodeProjectileSaveName(id) return "mortar2" end
function GetProjectileParamFloat(name,owner,param,default) return radius end
local firedAt; fireCalls=0
function FireWeapon(id,pos,error,flags) fireCalls=fireCalls+1; firedAt=pos; return 0 end
SRW.UpdateAABot(1000,bot,0.04)
assert(bot.Target==3000 and fireCalls==1 and firedAt.x<p.x, "intercept lead missing")
for i=1,3 do SRW.UpdateAABot(1000,bot,0.04) end
assert(fireCalls==1, "scan/fire throttle failed")
bot.FireWait=0; team=201; SRW.UpdateAABot(1000,bot,0.04); assert(fireCalls==1)
bot.FireWait=0; team=102; radius=0; SRW.UpdateAABot(1000,bot,0.04); assert(fireCalls==1)
bot.FireWait=0; radius=15; alive=false; SRW.UpdateAABot(1000,bot,0.04); assert(fireCalls==1)
bot.FireWait=0; alive=true; devices[1000].disabled=true
SRW.UpdateAABot(1000,bot,0.04); assert(fireCalls==1)
devices[1000].disabled=false; p.x=13000
SRW.UpdateAABot(1000,bot,0.04); assert(fireCalls==1 and devices[1000].pos.x==0)
devices[1001]={team=101,kind="srw_hound",built=true,pos=Vec3(800,0,0)}
data.srw.Robots[1001]={Team=101,Kind="srw_hound",Direction=1}
bot.FireWait=0; SRW.UpdateAABot(1000,bot,0.04); assert(devices[1000].pos.x>0, "no escort")
assert(not SRW.InterceptPoint(Vec3(0,0,0),Vec3(100,0,0),Vec3(20000,0,0),10000))
f.Reserve=49; f.AAReserve=1; f.AAQueue=1
local energy=balances[101].energy; SRW.UpdateFactories(0.04)
assert(f.Status=="reserve_full" and balances[101].energy==energy)
f.Queue=19; SRW_OrderAA(101,50); assert(SRW.FactoryQueue(f)==20)
selectedId=50; localTeam=101; SRW.RefreshUI()
assert(not visible.srw_aa_order and visible.srw_order)
SRW.ClickUI("srw_page"); assert(visible.srw_aa_order and not visible.srw_order)
SRW.ClickUI("srw_aa_order"); assert(sent[1]=="SRW_OrderAA")
sent=nil; SRW.ClickUI("srw_order"); assert(sent==nil, "hidden page button active")
selectedId=-1; SRW.RefreshUI(); assert(not visible.srw_page and not visible.srw_aa_order)
Projectiles={{SaveName="machinegun",ProjectileDamage=1,Effects={test=1}}}
''')
lua.execute((root/'weapons/projectile_list.lua').read_text(encoding='utf-8'))
lua.execute('assert(#Projectiles==16 and Projectiles[2].AntiAirDamage==80 and Projectiles[2].Gravity==981 and Projectiles[1].ProjectileDamage==1)')
print('PASS: AA production, lead, cooldown, allied/dead/non-interceptable targets, EMP, range, escort, capacity and menu pages')
