"""Storm factory and three-system combat integration with mocked Forts adapters."""
from pathlib import Path
import runpy
r = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(r / 'tests/check_hound.py'))['lua']
for module in ('factories/squads.lua', 'robots/aa.lua', 'combat/emp.lua'):
    lua.execute((r / 'scripts' / module).read_text())
lua.execute("""
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={};data.srw.MountedWeapons={}
local f={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0}
data.srw.Factories={[50]=f};balances[101]={metal=10000,energy=100000}
assert(SRW.RobotKinds[20]=="srw_storm_bot")
assert(not SRW.Config.Robots.srw_storm_bot.ShieldHP)
SRW_OrderIndividual(101,50,20);assert(not f.srw_storm_botQueue)
SRW_SquadEdit(101,50,20,1);assert(#f.SquadDraft==0)
f.Tier=3;devices[50].kind="srw_factory_ground_3"
SRW_OrderIndividual(201,50,20);assert(not f.srw_storm_botQueue)
SRW_OrderIndividual(101,50,20);SRW.UpdateFactories(.04)
assert(balances[101].metal==8800 and balances[101].energy==90000)
for i=1,850 do SRW.UpdateFactories(.04) end
assert(f.srw_storm_botReserve==1)
local fail=true
function EnableWeapon() end
function DeleteDeviceById(id) devices[id]=nil end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if fail and kind=="srw_storm_interceptor" then return -1 end
 local ids={srw_storm_bot=900,srw_storm_rockets=901,srw_storm_interceptor=902}
 local id=assert(ids[kind]);devices[id]={team=team,kind=kind,pos=p,built=true};return id
end
SRW_ReleaseIndividual(101,50,20)
assert(f.srw_storm_botReserve==1 and not devices[900] and not devices[901])
assert(next(data.srw.MountedWeapons)==nil and not data.srw.Robots[900])
fail=false;SRW_ReleaseIndividual(101,50,20)
assert(f.srw_storm_botReserve==0 and devices[900] and devices[901] and devices[902])
assert(f.ExitRemaining==8 and not data.srw.Robots[900].SquadSpeed)
assert(data.srw.MountedWeapons[902].AntiAir)
devices[910]={team=102,kind="mine",built=true,pos=Vec3(1500,0,0)}
devices[911]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,i) return 910+i end
local airTeam=102;local airAlive=true
function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId(side,i) return 3000 end
function NodeExists(id) return airAlive end
function NodeTeam(id) return airTeam end
function NodePosition(id) return Vec3(1800,-600,0) end
function NodeVelocity(id) return Vec3(-1500,0,0) end
function GetNodeProjectileSaveName(id) return "missile" end
function GetProjectileParamFloat(name,team,param,default) return 20 end
local shots={};local aims={}
function FireWeapon(id,p,e,flags) shots[id]=(shots[id] or 0)+1;aims[id]=p;return 0 end
SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04)
assert(shots[900]==1 and shots[901]==1 and shots[902]==1)
assert(data.srw.Robots[900].Target==911 and data.srw.MountedWeapons[901].Target==911)
assert(data.srw.MountedWeapons[902].Target==3000)
assert(aims[902].x==1800,'pulse laser should use the instantaneous projectile position')
local laser=data.srw.MountedWeapons[902]
local x=devices[900].pos.x;devices[910]=nil;devices[911]=nil
SRW.UpdateRobots(.04);assert(devices[900].pos.x==x,'hull moved during laser pulse')
laser.FireWait=0;laser.BeamRemaining=0;airTeam=201
SRW.UpdateAABot(902,laser,.04);assert(shots[902]==1 and not laser.Target)
-- With no enemy robots, ground weapons must also engage fort devices.
airAlive=false;devices[910]={team=102,kind="mine",built=true,pos=Vec3(1600,0,0)}
local root=data.srw.Robots[900];local rockets=data.srw.MountedWeapons[901]
root.FireWait=0;root.BeamRemaining=0;rockets.FireWait=0;rockets.BeamRemaining=0
SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04)
assert(root.Target==910 and rockets.Target==910 and shots[900]==2 and shots[901]==2)
-- Tier-III EMP degrades all three aiming systems; these unguided rockets remain usable.
root.EMPRemaining=3;root.FireWait=0;root.BeamRemaining=0
rockets.FireWait=0;rockets.BeamRemaining=0;laser.FireWait=0;laser.BeamRemaining=0
airAlive=true;airTeam=102
SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04)
assert(shots[900]==3 and shots[901]==3 and shots[902]==2)
assert(rockets.EMPRemaining==3 and laser.EMPRemaining==3)
assert(aims[900].y~=0 and aims[902].x~=1800,'EMP must perturb both ground and interception aim')
-- Native disabling blocks the whole platform even if mounted weapons are ready.
devices[900].disabled=true;rockets.BeamRemaining=0;rockets.FireWait=0
laser.BeamRemaining=0;laser.FireWait=0
SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04)
assert(shots[900]==3 and shots[901]==3 and shots[902]==2)
devices[900]=nil;data.srw.Robots[900]=nil;SRW.UpdateMountedWeapons(.04)
assert(not devices[901] and not devices[902] and next(data.srw.MountedWeapons)==nil)
f.ExitRemaining=0;f.SquadDraft={"srw_storm_bot"};SRW_SquadStart(101,50)
local m,e=balances[101].metal,balances[101].energy;SRW.UpdateFactories(.04)
assert(balances[101].metal==m-1320 and balances[101].energy==e-11000)
for i=1,850 do SRW.UpdateFactories(.04) end
assert(f.Squad.Produced==1 and SRW.FactoryReserve(f)==1)
SRW_SquadRelease(101,50);SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and math.abs(data.srw.Robots[900].SquadSpeed-3.3)<.000001)
Projectiles={{SaveName="cannon"},{SaveName="machinegun",ProjectileDamage=6,WeaponDamageBonus=6},{SaveName="missile",Missile={}},
 {SaveName="laser",ProjectileType="beam"}}
""")
source = (r / 'weapons/projectile_list.lua').read_text()
lua.execute(source)
lua.execute(source)
lua.execute("""
local p={};for _,v in ipairs(Projectiles) do assert(not p[v.SaveName]);p[v.SaveName]=v end
assert(p.srw_storm_bullet.ProjectileDamage==160 and p.srw_storm_bullet.MaxAge*10000>=14400)
assert(p.srw_storm_rocket.ProjectileDamage==300 and p.srw_storm_rocket.ProjectileSplashDamage==140)
assert(p.srw_storm_rocket.ProjectileSplashDamageMaxRadius==350)
assert(p.srw_storm_rocket.ProjectileType=="mortar" and next(p.srw_storm_rocket.Missile)==nil)
assert(p.srw_storm_rocket.MaxAge*4500>=16800)
assert(p.srw_storm_intercept_beam.AntiAirDamage==280 and p.srw_storm_intercept_beam.ProjectileDamage==0)
assert(p.srw_storm_intercept_beam.ProjectileType=="beam" and not p.srw_storm_intercept_beam.ProjectileIncendiary)
assert(p.srw_storm_bullet.ProjectileSprite==nil and p.srw_storm_bullet.Projectile.Root.Sprite==path.."/ui/textures/projectiles/artillery_shell.png")
""")
print('PASS: Storm tier/owner gates, solo and squad costs, atomic three-system spawn, independent targets, building fallback, EMP, beam hold and cleanup')
