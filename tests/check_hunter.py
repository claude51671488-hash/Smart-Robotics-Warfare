from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_tank.py'))['lua']
lua.execute((root/'scripts/combat/guidance.lua').read_text())
lua.execute("""
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
data.srw.Factories={[50]={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,10,1); assert(#f.SquadDraft==0)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_SquadEdit(101,50,10,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
for i=1,300 do SRW.UpdateFactories(.04) end
assert(SRW.FactoryReserve(f)==1)
local fail=true
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if fail and kind=="srw_hunter_interceptor" then return -1 end
 local ids={srw_hunter_bot=900,srw_hunter_rockets=901,srw_hunter_interceptor=902}
 local id=assert(ids[kind]); devices[id]={team=team,kind=kind,pos=p,built=true}; return id
end
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==0 and not devices[900] and not devices[901])
assert(next(data.srw.MountedWeapons)==nil)
fail=false; f.ExitRemaining=0; SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and data.srw.Robots[900].Kind=="srw_hunter_bot")
assert(data.srw.MountedWeapons[901].Root==900 and data.srw.MountedWeapons[902].AntiAir)
devices[910]={team=102,kind="mine",built=true,pos=Vec3(500,0,0)}
devices[911]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return 910+index end
local shots={}
function FireWeapon(id,p,error,flags) shots[id]=(shots[id] or 0)+1; return 0 end
SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04)
assert(data.srw.Robots[900].Target==911 and data.srw.MountedWeapons[901].Target==911)
assert(shots[900]==1 and shots[901]==1 and shots[902]==1)
assert(data.srw.MountedWeapons[902].Target==3000)
local x=devices[900].pos.x; devices[910]=nil; devices[911]=nil
SRW.UpdateRobots(.04); assert(devices[900].pos.x==x,'hull moved during interceptor pulse')
local rocket=data.srw.MountedWeapons[901]
rocket.EMPRemaining=4; rocket.FireWait=0
SRW.UpdateHound(901,rocket,.04); assert(shots[901]==1 and rocket.Target==nil)
devices[911]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
rocket.EMPRemaining=0; SRW.UpdateHound(901,rocket,.04); assert(shots[901]==2)
function GetNodeProjectileSaveName(id) return "srw_hunter_at_rocket" end
function NodeTeam(id) return id==4000 and 101 or 102 end
SRW.GuidedLaunch(101,901,4000)
assert(data.srw.GuidedMissiles[4000].Target==911 and not data.srw.GuidedMissiles[4000].Air)
local aim
function SetMissileTarget(id,p) aim=p end
function NodePosition(id) return Vec3(0,0,0) end
function NodeVelocity(id) return Vec3(3000,0,0) end
SRW.UpdateGuidance(.04); assert(aim.x==1000)
devices[911].team=101; SRW.UpdateGuidance(.04)
assert(data.srw.GuidedMissiles[4000].Target==nil and aim.x==30000)
devices[900]=nil; SRW.UpdateMountedWeapons(.04)
assert(not devices[901] and not devices[902])
data.srw.Robots[900]=nil; f.ExitRemaining=0; f.srw_hunter_botReserve=1
SRW_ReleaseIndividual(101,50,10)
assert(f.srw_hunter_botReserve==0 and devices[900] and devices[901] and devices[902])
assert(f.ExitRemaining==3)
Projectiles={{SaveName="cannon",ProjectileDamage=700,MomentumThreshold={armour={Penetrate=4000}}},
 {SaveName="missile",Missile={}}, {SaveName="laser",ProjectileIncendiary=true,DamageMultiplier={{AntiAir=0}}}}
""")
lua.execute((root/'weapons/projectile_list.lua').read_text())
lua.execute("""
local p={}; for _,v in ipairs(Projectiles) do p[v.SaveName]=v end
assert(p.srw_hunter_apfsds.ProjectileSplashDamage==0 and not p.srw_hunter_apfsds.ExplodeOnTouch)
assert(p.srw_hunter_apfsds.MomentumThreshold.armour.Penetrate==4000)
assert(p.srw_hunter_at_rocket.Missile.MaxSteerPerSecond==120)
assert(p.srw_hunter_intercept_beam.AntiAirDamage==200 and p.srw_hunter_intercept_beam.ProjectileDamage==0)
assert(not p.srw_hunter_intercept_beam.ProjectileIncendiary)
assert(next(p.srw_hunter_intercept_beam.DamageMultiplier)==nil)
""")
print('PASS: Trapper tier/production, atomic three-part spawn, independent targets, pulse hold, EMP, guidance, cleanup and isolated ammunition')
