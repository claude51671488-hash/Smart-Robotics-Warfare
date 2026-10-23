from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
function GetDeviceCountSide(side)
 local n=0; for _,d in pairs(devices) do if d.team%100==side then n=n+1 end end; return n
end
function GetDeviceIdSide(side,index)
 local ids={}; for id,d in pairs(devices) do if d.team%100==side then ids[#ids+1]=id end end
 table.sort(ids); return ids[index+1]
end
data.srw.Factories={[50]={Team=101,Tier=1,Queue=2,Reserve=5,HoundQueue=1,HoundReserve=3,
 RepairReserve=2,SiegeQueue=1,AAReserve=1,CurrentType="srw_hound",Remaining=3,Status="building"}}
local original=data.srw.Factories[50]
devices[51]={team=101,kind="srw_factory_ground_2",built=false,pos=Vec3(0,0,0)}
SRW.FactoryCreated(101,51,"srw_factory_ground_2",50)
assert(data.srw.Factories[51]==original and not data.srw.Factories[50])
devices[50]=nil
SRW.FactoryCreated(101,51,"srw_factory_ground_2",50) -- duplicate callback is harmless
SRW.ScanFactories(); SRW.UpdateFactories(1)
assert(original.Remaining==3 and original.Queue==2 and original.HoundReserve==3)
assert(not SRW.ValidFactory(101,51) and SRW.FactoryCapacity(original)==50)
devices[51].built=true; SRW.ScanFactories(); SRW.UpdateFactories(1)
assert(original.Remaining==2)
SRW.UpdateFactories(2); assert(original.HoundReserve==4 and original.Reserve==5)
devices[52]={team=101,kind="srw_factory_ground_3",built=false,pos=Vec3(0,0,0)}
SRW.FactoryCreated(101,52,"srw_factory_ground_3",51); devices[51]=nil
assert(data.srw.Factories[52]==original and SRW.FactoryCapacity(original)==100)
devices[52].built=true; SRW.ScanFactories()
original.Queue=1; original.HoundQueue=0; original.SiegeQueue=0
original.Reserve=93; original.HoundReserve=4; original.RepairReserve=2; original.AAReserve=1
original.Remaining=0
balances[101]={metal=10000,energy=100000}
SRW.UpdateFactories(0.04); assert(original.Status=="reserve_full")
original.Reserve=92; SRW.UpdateFactories(0.04)
assert(original.CurrentType=="srw_dynamit_bot")
-- A second separately placed factory is rejected regardless of existing tier.
devices[60]={team=101,kind="srw_factory_ground_1",built=false,pos=Vec3(500,0,0)}
function GetDeviceCountSide(side) return side==1 and 2 or 0 end
function GetDeviceIdSide(side,index) return index==0 and 52 or 60 end
function GetDeviceCost(name) return {metal=300,energy=2000} end
function DeleteDeviceById(id) devices[id]=nil; return true end
local energy=balances[101].energy
SRW.FactoryCreated(101,60,"srw_factory_ground_1",0)
assert(not devices[60] and balances[101].energy==energy+2000 and not data.srw.Factories[60])
-- Destruction removes the upgraded factory's reserve.
devices[52]=nil
function GetDeviceCountSide(side) return 0 end
SRW.ScanFactories(); assert(not data.srw.Factories[52])
Devices={}; Sprites={}
''')
lua.execute((root/'devices/device_list.lua').read_text(encoding='utf-8'))
lua.execute('''
local types={}; for _,d in ipairs(Devices) do types[d.SaveName]=d end
assert(types.srw_factory_ground_1.Upgrades.srw_factory_ground_2.Enabled)
assert(types.srw_factory_ground_2.Upgrades.srw_factory_ground_3.Enabled)
assert(not types.srw_factory_ground_2.Enabled and not types.srw_factory_ground_3.Enabled)
assert(not types.srw_factory_ground_3.Upgrades)
''')
print('PASS: native upgrade chain, state migration, duplicate callbacks, pause/resume, tier capacity and one-factory guard')
