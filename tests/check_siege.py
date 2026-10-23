from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; balances[101]={metal=10000,energy=100000}
data.srw.Factories={[50]={Team=101,Queue=0,Reserve=0,Remaining=0,Status="ready"}}
local f=data.srw.Factories[50]
SRW_OrderSiege(201,50); assert(not f.SiegeQueue)
SRW_OrderSiege(101,50); SRW.UpdateFactories(0.04)
assert(f.CurrentType=="srw_siege_bot" and balances[101].metal==9700)
for i=1,300 do SRW.UpdateFactories(0.04) end
assert(f.SiegeReserve==1)
function EnableWeapon(name,enabled,side) assert(name=="srw_siege_bot" and side==1) end
spawnId=-1; SRW_ReleaseSiege(101,50); assert(f.SiegeReserve==1)
spawnId=900; SRW_ReleaseSiege(101,50)
assert(f.SiegeReserve==0 and data.srw.Robots[900].Kind=="srw_siege_bot")
local bot=data.srw.Robots[900]; devices[900].pos=Vec3(0,0,0)
devices[901]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
devices[902]={team=102,kind="battery",built=true,pos=Vec3(4000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return 901+index end
fireCalls=0
SRW.UpdateRobots(0.04)
assert(bot.Target==901 and fireCalls==0 and devices[900].pos.x==0,"aiming delay missing")
for i=1,29 do SRW.UpdateRobots(.04) end
assert(bot.Target==901 and fireCalls==1 and devices[900].pos.x==0, "immediate threat or stop failed")
for i=1,100 do SRW.UpdateRobots(0.04) end
assert(fireCalls==1, "reload bypass")
devices[901].pos.x=100; SRW.UpdateRobots(0.04)
assert(bot.Target==902 and fireCalls==1, "close target blocked another valid firing solution")
devices[900].disabled=true; local x=devices[900].pos.x
SRW.UpdateRobots(0.04); assert(devices[900].pos.x==x)
devices[900].disabled=false; devices[901].team=201; devices[902].team=201
SRW.UpdateRobots(0.04); assert(not bot.Target and fireCalls==1, "friendly target attacked")
devices[902].team=102; devices[902].pos.x=devices[900].pos.x+40100
x=devices[900].pos.x; SRW.UpdateRobots(0.04)
assert(not bot.Target and devices[900].pos.x>x, "out of range target fired on")
-- No ground behind: do not retreat into a cliff.
devices[901].team=102; devices[901].pos.x=devices[900].pos.x+100
groundResult=0; x=devices[900].pos.x; SRW.UpdateRobots(0.04)
assert(devices[900].pos.x==x)
groundResult=1
f.Reserve=19; f.SiegeReserve=1; f.SiegeQueue=1
local energy=balances[101].energy; SRW.UpdateFactories(0.04)
assert(f.Status=="reserve_full" and balances[101].energy==energy)
f.Queue=19; SRW_OrderSiege(101,50); SRW_OrderRepair(101,50)
assert(SRW.FactoryQueue(f)==20)
for id=903,906 do
 devices[id]={team=101,kind="srw_siege_bot",built=true,pos=Vec3(0,0,0)}
 data.srw.Robots[id]={Team=101,Kind="srw_siege_bot",Direction=1}
end
SRW_ReleaseSiege(101,50); assert(f.Status=="limit" and f.SiegeReserve==1)
selectedId=50; localTeam=101; SRW.RefreshUI()
SRW.ClickUI("srw_page")
assert(visible.srw_siege_order)
SRW.ClickUI("srw_siege_order"); assert(sent[1]=="SRW_OrderSiege")
selectedId=-1; SRW.RefreshUI(); assert(not visible.srw_siege_order)
function dofile(name) assert(name=="weapons/cannon.lua"); Root={Sprite="cannon-base"} end
local shell
for _,p in ipairs(Projectiles) do if p.SaveName=="srw_hammer_shell" then shell=p end end
assert(shell and shell.ProjectileDamage==2550 and shell.ProjectileSplashDamage==300 and shell.Gravity==981 and shell.ExplodeOnTouch)
-- Reacquisition must start the setup delay again, rather than instantly firing.
devices[901].team=201; devices[902].team=102
devices[902].pos.x=devices[900].pos.x+3000; bot.FireWait=0
local shots=fireCalls; SRW.UpdateRobots(.04)
assert(fireCalls==shots and bot.AimRemaining>1)
devices[902].team=201; SRW.UpdateRobots(.04); assert(not bot.AimTarget)
''')
lua.execute((root/'weapons/siege_bot.lua').read_text(encoding='utf-8'))
lua.execute('assert(Projectile=="srw_hammer_shell" and MinFireAngle==45 and MaxFireAngle==135 and Repairable and ReloadTime==8 and MinFireRadius==500)')
print('PASS: Hammer production, isolated shell, aiming/reacquisition delay, reload, retreat, cliffs, EMP, allies, range and cannon configuration')
