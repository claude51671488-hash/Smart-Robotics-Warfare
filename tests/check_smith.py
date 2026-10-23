from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
lua.execute((r/'scripts/factories/squads.lua').read_text())
lua.execute("""
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
local f={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}
data.srw.Factories={[50]=f}; balances[101]={metal=10000,energy=100000}
assert(SRW.RobotKinds[17]=="srw_smith_bot")
SRW_OrderIndividual(101,50,17); assert(not f.srw_smith_botQueue)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_OrderIndividual(201,50,17); assert(not f.srw_smith_botQueue)
SRW_OrderIndividual(101,50,17); SRW.UpdateFactories(.04)
assert(balances[101].metal==9450 and balances[101].energy==95500)
for i=1,510 do SRW.UpdateFactories(.04) end
assert(f.srw_smith_botReserve==1)
local fail=true
function EnableWeapon() end
function DeleteDeviceById(id) devices[id]=nil end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if fail and kind=="srw_smith_rockets" then return -1 end
 local ids={srw_smith_bot=900,srw_smith_flame=901,srw_smith_rockets=902}
 local id=assert(ids[kind]);devices[id]={team=team,kind=kind,pos=p,built=true};return id
end
SRW_ReleaseIndividual(101,50,17)
assert(f.srw_smith_botReserve==1 and not devices[900] and not devices[901])
fail=false; SRW_ReleaseIndividual(101,50,17)
assert(f.srw_smith_botReserve==0 and devices[900] and devices[901] and devices[902])
assert(not data.srw.Robots[900].SquadSpeed)
devices[910]={team=102,kind="mine",built=true,pos=Vec3(1500,0,0)}
devices[911]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,i) return 910+i end
local shots={}
function FireWeapon(id,p,e,flags) shots[id]=(shots[id] or 0)+1;return 0 end
SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04)
assert(data.srw.Robots[900].Target==911,'nearby hostile robot is the immediate threat')
assert(data.srw.MountedWeapons[901].Target==911 and data.srw.MountedWeapons[902].Target==911)
assert(shots[900]==1 and shots[901]==1 and shots[902]==1)
-- Unguided rockets can fire under tier-II EMP; their aim is degraded normally.
local rocket=data.srw.MountedWeapons[902];rocket.EMPRemaining=3;rocket.FireWait=0;rocket.BeamRemaining=0
SRW.UpdateHound(902,rocket,.04);assert(shots[902]==2)
devices[900]=nil;data.srw.Robots[900]=nil;SRW.UpdateMountedWeapons(.04)
assert(not devices[901] and not devices[902])
f.ExitRemaining=0;f.SquadDraft={"srw_smith_bot"};SRW_SquadStart(101,50)
local m=balances[101].metal;SRW.UpdateFactories(.04);assert(balances[101].metal==m-605)
for i=1,510 do SRW.UpdateFactories(.04) end
SRW_SquadRelease(101,50);SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and data.srw.Robots[900].SquadSpeed==1.8)
Projectiles={{SaveName="cannon"},{SaveName="missile",Missile={}},{SaveName="mortar",Effects={Impact={bracing="native-fire"}}}}
""")
lua.execute((r/'weapons/projectile_list.lua').read_text())
lua.execute("""
local p={};for _,v in ipairs(Projectiles) do p[v.SaveName]=v end
assert(p.srw_smith_he.ProjectileSplashDamage==520)
assert(p.srw_smith_flame.ProjectileIncendiary and p.srw_smith_flame.MaxAge==1.7)
assert(p.srw_smith_flame.Effects.Impact.bracing=="native-fire")
assert(p.srw_smith_rocket.ProjectileType=="mortar" and next(p.srw_smith_rocket.Missile)==nil)
""")
print('PASS: Smith tier/ownership, individual and squad prices/release, three-part rollback, independent targets, unguided EMP and incendiary ammunition')
