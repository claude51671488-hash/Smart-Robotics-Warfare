"""Repair bot adapter tests. Native healing is verified separately in Forts."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute((root/'scripts/robots/repair.lua').read_text(encoding='utf-8'))
lua.execute('''
devices={
 [50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)},
}
data.srw.Robots={}
data.srw.Factories={[50]={Team=101,Queue=0,Reserve=0,Remaining=0,Status="ready"}}
balances[101]={metal=1000,energy=10000}
local f=data.srw.Factories[50]
SRW_OrderRepair(201,50); assert(not f.RepairQueue)
SRW_OrderRepair(101,50); SRW.UpdateFactories(0.04)
assert(f.CurrentType=="srw_repair_bot" and balances[101].metal==850 and balances[101].energy==8500)
for i=1,200 do SRW.UpdateFactories(0.04) end
assert(f.RepairReserve==1 and f.Reserve==0)
function EnableDevice(name,enabled,side) assert(name=="srw_repair_bot" and side==1) end
spawnId=-1; SRW_ReleaseRepair(101,50); assert(f.RepairReserve==1)
spawnId=800; SRW_ReleaseRepair(101,50)
assert(f.RepairReserve==0 and data.srw.Robots[800].Kind=="srw_repair_bot")
local bot=data.srw.Robots[800]
devices[800].pos=Vec3(0,0,0)
repairs={}; health={[800]=0.1}
function GetDeviceHealth(id) return health[id] or 1 end
function RepairDevice(id) error("persistent native repair must not be started") end
function GetDeviceHitpoints(id) return GetDeviceHealth(id)*1200 end
function ApplyDamageToDevice(id,damage)
 assert(damage<0)
 repairs[#repairs+1]=id; health[id]=math.min(1,GetDeviceHealth(id)-damage/1200)
end
local function update() SRW.UpdateRepairBot(800,bot,0.04) end
update(); assert(#repairs==0 and devices[800].pos.x==0, "self repair or solo advance")
devices[801]={team=102,kind="srw_hound",built=true,pos=Vec3(100,0,0)}
data.srw.Robots[801]={Team=102,Kind="srw_hound",Direction=-1}; health[801]=0.1
update(); assert(#repairs==0, "enemy repair")
devices[801].team=201; data.srw.Robots[801].Team=201
update(); assert(repairs[1]==801 and devices[800].pos.x==0, "allied repair or stop failed")
for i=1,20 do update() end
assert(#repairs==5, "repair pulse rate incorrect")
health[801]=1; update(); assert(not bot.Target)
devices[801].pos=Vec3(600,0,0); update(); assert(devices[800].pos.x>0, "escort failed")
devices[800].disabled=true
local x=devices[800].pos.x; local calls=#repairs; health[801]=0.1
update(); assert(devices[800].pos.x==x and #repairs==calls, "EMP ignored")
devices[800].disabled=false; devices[801].pos=Vec3(x-500,0,0)
update(); assert(devices[800].pos.x<x, "did not approach damaged robot behind")
data.srw.Robots[801].FuseRemaining=0.1; update(); assert(not bot.Target, "armed kamikaze selected")
data.srw.Robots[801].FuseRemaining=nil
devices[801].team=102; update(); assert(not bot.Target, "captured robot selected")
-- Range loss, absent healer and resource shortage must stop healing.
devices[801].team=201; health[801]=0.5
devices[801].pos=Vec3(devices[800].pos.x+800,0,0)
calls=#repairs; update(); assert(#repairs==calls)
devices[801].pos=Vec3(devices[800].pos.x+100,0,0); bot.RepairWait=0
balances[101]={metal=0,energy=0}; update(); assert(#repairs==calls)
balances[101]={metal=10,energy=100}; bot.RepairWait=0
health[801]=1199/1200; update()
assert(health[801]==1 and math.abs(balances[101].metal-9.95)<0.00001)
local healer=devices[800]; devices[800]=nil; calls=#repairs
update(); assert(#repairs==calls); devices[800]=healer
local apply=ApplyDamageToDevice; ApplyDamageToDevice=function() end
health[801]=0.5; bot.RepairWait=0; local metal=balances[101].metal
update(); assert(balances[101].metal==metal,"charged for rejected healing")
ApplyDamageToDevice=apply
-- Shared reserve and queue limits include repair units; no duplicate spending.
f.Reserve=19; f.RepairReserve=1; f.RepairQueue=1
local energy=balances[101].energy; SRW.UpdateFactories(0.04)
assert(f.Status=="reserve_full" and balances[101].energy==energy)
f.Queue=19; f.HoundQueue=0; f.RepairQueue=1
SRW_OrderRepair(101,50); SRW_OrderHound(101,50); SRW.Order(101,50)
assert(SRW.FactoryQueue(f)==20)
for id=802,805 do
 devices[id]={team=101,kind="srw_repair_bot",built=true,pos=Vec3(0,0,0)}
 data.srw.Robots[id]={Team=101,Kind="srw_repair_bot",Direction=1}
end
SRW_ReleaseRepair(101,50); assert(f.Status=="limit" and f.RepairReserve==1)
-- Mixed production rotates among all waiting types.
f.Queue=1; f.HoundQueue=1; f.RepairQueue=1
f.Reserve=0; f.HoundReserve=0; f.RepairReserve=0; f.Remaining=0; f.LastType=nil
balances[101]={metal=10000,energy=100000}
for i=1,560 do SRW.UpdateFactories(0.04) end
assert(f.Reserve==1 and f.HoundReserve==1 and f.RepairReserve==1)
selectedId=50; localTeam=101; SRW.RefreshUI()
assert(visible.srw_repair_order and visible.srw_repair_release)
SRW.ClickUI("srw_repair_order"); assert(sent[1]=="SRW_OrderRepair" and sent[2]=="101,50")
selectedId=-1; SRW.RefreshUI(); assert(not visible.srw_repair_order)
''')
print('PASS: repair production, shared limits, failed spawn, allied targets, self/enemy/fuse exclusions, escort, EMP, command throttling, mixed queue and UI')
