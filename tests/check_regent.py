from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_colossus.py'))['lua']
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_3",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={};data.srw.MountedWeapons={}
local f={Team=101,Tier=3,Reserve=0,Queue=0,Remaining=0,srw_colossus_botReserve=1}
data.srw.Factories={[50]=f}
local fail=true;local created=0
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 created=created+1
 if fail and created==5 then return -1 end
 local id=899+created
 devices[id]={team=team,kind=kind,built=true,pos=p};return id
end
SRW_ReleaseIndividual(101,50,15)
assert(f.srw_colossus_botReserve==1 and not devices[900] and not devices[901] and not devices[903])
assert(next(data.srw.MountedWeapons)==nil and next(data.srw.Robots)==nil)
created=0;fail=false;SRW_ReleaseIndividual(101,50,15)
assert(f.srw_colossus_botReserve==0 and #SRW.SortedIds(data.srw.MountedWeapons)==4)
local bot=data.srw.Robots[900];local laser=data.srw.MountedWeapons[901]
devices[1000]={team=102,kind="mine",built=true,pos=Vec3(2500,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide() return 1000 end
function AimWeapon() return true end
local shots={};local result=FIRE_SUCCESS or 0
function FireWeapon(id,p,e,flags) shots[id]=(shots[id] or 0)+1;return result end
SRW.UpdateWeaponPower(.04);assert(bot.WeaponPower==100)
result=FIRE_RELOADING or 5
SRW.UpdateHound(900,bot,.04);assert(bot.WeaponPower==100,'failed shot charged power')
result=FIRE_SUCCESS or 0;bot.FireWait=0
SRW.UpdateHound(900,bot,.04);assert(bot.WeaponPower==65 and bot.BeamRemaining==.6)
SRW.UpdateHound(901,laser,.04);assert(not shots[901],'laser overlapped main burst')
SRW.UpdateHound(900,bot,.61);SRW.UpdateWeaponPower(.61)
SRW.UpdateHound(901,laser,.04)
assert(shots[901]==1 and bot.WeaponPower<6.1 and laser.BeamRemaining==2)
local count=shots[900];bot.FireWait=0
SRW.UpdateHound(900,bot,.04);assert(shots[900]==count,'main gun overlapped laser')
-- Defence has its own targets/reload and does not spend the main reactor reserve.
local reserve=bot.WeaponPower
SRW.UpdateHound(903,data.srw.MountedWeapons[903],.04)
SRW.UpdateHound(904,data.srw.MountedWeapons[904],.04)
assert(shots[903]==1 and shots[904]==1 and bot.WeaponPower==reserve)
laser.BeamRemaining=0;bot.BeamRemaining=0
SRW.UpdateHound(900,bot,.04);assert(shots[900]==count,'insufficient power ignored')
SRW.UpdateWeaponPower(2);SRW.UpdateHound(900,bot,.04)
assert(shots[900]==count+1 and bot.WeaponPower<8)
devices[900].disabled=true;reserve=bot.WeaponPower
SRW.UpdateWeaponPower(10);assert(bot.WeaponPower==reserve)
devices[900].disabled=false;SRW.UpdateWeaponPower(100);assert(bot.WeaponPower==100)
-- Rocket battery is a tier III guided AA mount: EMP inhibits its launch.
local rockets=data.srw.MountedWeapons[902];rockets.EMPRemaining=3
SRW.UpdateAABot(902,rockets,.04);assert(not shots[902])
devices[900]=nil;data.srw.Robots[900]=nil;SRW.UpdateMountedWeapons(.04)
assert(next(data.srw.MountedWeapons)==nil and not devices[901] and not devices[904])
''')
print('PASS: Regent five-part rollback/release, failed-shot accounting, shared reserve, burst exclusion, independent defence, recharge cap, disable, EMP and cleanup')
