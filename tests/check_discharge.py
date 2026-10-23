from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_emp.py'))['lua']
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={};data.srw.MountedWeapons={}
local f={Team=101,Tier=2,Reserve=0,Queue=0,Remaining=0,srw_emp_botReserve=1}
data.srw.Factories={[50]=f}
local fail=true
function EnableWeapon() end
function DeleteDeviceById(id) devices[id]=nil end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind=="srw_emp_turret" and fail then return -1 end
 local id=kind=="srw_emp_bot" and 900 or 901
 devices[id]={team=team,kind=kind,built=true,pos=p};return id
end
SRW_ReleaseIndividual(201,50,7);assert(not devices[900])
SRW_ReleaseIndividual(101,50,7)
assert(f.srw_emp_botReserve==1 and not devices[900] and not data.srw.Robots[900])
fail=false;SRW_ReleaseIndividual(101,50,7)
assert(f.srw_emp_botReserve==0 and devices[900] and devices[901])
local ids={1001,1002,1003,1004,1005,1006}
devices[1001]={team=102,kind="srw_hound",built=true,pos=Vec3(700,0,0)}
devices[1002]={team=102,kind="srw_hound",built=true,pos=Vec3(1700,0,0)}
devices[1003]={team=102,kind="srw_aa_bot",built=true,pos=Vec3(1800,0,0)}
devices[1004]={team=102,kind="srw_shield_bot",built=true,pos=Vec3(1900,0,0)}
devices[1005]={team=102,kind="srw_hound_machinegun",built=true,pos=Vec3(700,0,0)}
devices[1006]={team=201,kind="srw_shield_bot",built=true,pos=Vec3(1900,0,0)}
data.srw.MountedWeapons[1005]={Team=102,Root=1001,Kind="srw_hound_machinegun"}
function GetDeviceCountSide(side) return side==2 and #ids or 0 end
function GetDeviceIdSide(side,i) return ids[i+1] end
function AimWeapon(id,p) return true end
local shots={}
function FireWeapon(id,p,error,flags) shots[id]=(shots[id] or 0)+1;return 0 end
local bot=data.srw.Robots[900];bot.FireWait=0
SRW.UpdateHound(900,bot,.04)
assert(bot.Target==1004 and shots[900]==1,'EMP must select shield carrier in cluster')
SRW.UpdateHound(901,data.srw.MountedWeapons[901],.04)
assert(data.srw.MountedWeapons[901].Target==1001 and shots[901]==1,'defence gun must select close attacker')
-- If the preferred carrier is obstructed, try the next reachable priority target.
bot.FireWait=0
function AimWeapon(id,p) return p.x~=1900 end
SRW.UpdateHound(900,bot,.04);assert(bot.Target==1003)
-- One tank with several mounts must not outweigh several independent robots.
local candidates={}
for _,id in ipairs({1001,1002,1003,1004,1005}) do
 candidates[#candidates+1]={Id=id,Position=devices[id].pos}
end
local ranked=SRW.RankEMPTargets(candidates,240)
assert(#ranked==4 and ranked[1].EMPScore==10 and ranked[4].EMPScore==33)
-- Reloading does not recompute cluster scores every simulation tick.
local score=SRW.RankEMPTargets;local calls=0
SRW.RankEMPTargets=function(...) calls=calls+1;return score(...) end
bot.FireWait=5;SRW.UpdateHound(900,bot,.04);assert(calls==0)
bot.EMPRemaining=3;bot.FireWait=0
SRW.UpdateHound(900,bot,.04);assert(shots[900]==3 and calls==1)
devices[900]=nil;data.srw.Robots[900]=nil;SRW.UpdateMountedWeapons(.04)
assert(not devices[901], 'orphaned defence gun')
Projectiles={{SaveName="machinegun",ProjectileDamage=1}}
''')
lua.execute((r/'weapons/projectile_list.lua').read_text(encoding='utf-8'))
lua.execute('''
local bullet
for _,p in ipairs(Projectiles) do if p.SaveName=="srw_emp_defence_bullet" then bullet=p end end
assert(bullet and bullet.ProjectileDamage==50 and bullet.ProjectileSplashDamage==0)
''')
print('PASS: Discharge atomic release, ownership, independent weapons, cluster/support priority, blocked target fallback, mount deduplication, reload cost and EMP')
