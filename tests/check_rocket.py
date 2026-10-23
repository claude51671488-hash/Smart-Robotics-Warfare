from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute((root/'scripts/factories/squads.lua').read_text())
lua.execute('''
table.insert(Projectiles,{SaveName="missile",ProjectileType="missile",Missile={RocketThrust=100},Projectile={Root={Sprite="native"}}})
''')
source=(root/'weapons/projectile_list.lua').read_text()
lua.execute(source); lua.execute(source)
lua.execute('''
local count=0
for _,p in ipairs(Projectiles) do
 if p.SaveName=="srw_salvo_rocket" then
  count=count+1; assert(p.ProjectileType=="missile" and p.Missile.RocketThrust==120000 and p.ProjectileDrag==48)
  assert(p.Projectile.Root.Sprite==path.."/ui/textures/projectiles/smart_missile.png" and p.ProjectileDamage==300 and p.ProjectileSplashDamage==140)
  assert(p.ProjectileShootDownRadius==nil) -- omitted by the stub; inherited from vanilla in game
 end
 if p.SaveName=="missile" then assert(p.Missile.RocketThrust==100) end
end
assert(count==1)
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}; data.srw.Factories={[50]={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,9,1); assert(#f.SquadDraft==0)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_SquadEdit(101,50,9,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
assert(f.CurrentType=="srw_rocket_bot" and balances[101].metal==9560)
for i=1,350 do SRW.UpdateFactories(.04) end
assert(SRW.FactoryReserve(f)==1)
function EnableWeapon(name,enabled,side) assert((name=="srw_rocket_bot" or name=="srw_psalm_turret") and side==1) end
local childCount=0; local failSecond=true
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 local id=900
 if kind=="srw_psalm_turret" then
  childCount=childCount+1
  if childCount==2 and failSecond then return -1 end
  id=909+childCount
 else childCount=0 end
 devices[id]={team=team,kind=kind,built=true,pos=p}; return id
end
function DeleteDeviceById(id) devices[id]=nil end
groundResult=1; rayResult=0; spawnId=900
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==0 and not devices[900] and not devices[910])
assert(next(data.srw.MountedWeapons)==nil)
failSecond=false; f.ExitRemaining=0; SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and data.srw.Robots[900].Kind=="srw_rocket_bot")
assert(devices[910] and devices[911] and not data.srw.Robots[910])
devices[901]={team=102,kind="mine",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide(side,index) return 901 end
canAim=true; fireCalls=0; SRW.UpdateRobots(.04)
local bot=data.srw.Robots[900]; local x=devices[900].pos.x
assert(fireCalls==1 and bot.BeamRemaining==1.5 and bot.FireWait==10)
devices[901]=nil
for i=1,38 do SRW.UpdateRobots(.04) end
assert(devices[900].pos.x==x and fireCalls==1)
SRW.UpdateRobots(.04); assert(devices[900].pos.x>x)
-- The rocket salvo chooses a structure while both defensive guns select a robot.
devices[901]={team=102,kind="mine",built=true,pos=Vec3(6000,0,0)}
devices[902]={team=102,kind="srw_hound",built=true,pos=Vec3(1500,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return 901+index end
local shots={}
function FireWeapon(id,p,error,flags) shots[id]=(shots[id] or 0)+1; return 0 end
bot.FireWait=0; bot.BeamRemaining=0
SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04)
assert(bot.Target==902 and shots[900]==1,'nearby robot must outrank siege preference')
assert(data.srw.MountedWeapons[910].Target==902 and data.srw.MountedWeapons[911].Target==902)
assert(shots[910]==1 and shots[911]==1)
-- Tier-II EMP blocks rockets but allows inaccurate autocannon fire.
bot.EMPRemaining=5; bot.FireWait=0
for _,id in ipairs({910,911}) do
 data.srw.MountedWeapons[id].FireWait=0; data.srw.MountedWeapons[id].BeamRemaining=0
end
SRW.UpdateRobots(.04); SRW.UpdateMountedWeapons(.04)
assert(shots[900]==1 and shots[910]==2 and shots[911]==2)
devices[910]=nil; SRW.UpdateMountedWeapons(.04)
assert(devices[900] and not data.srw.MountedWeapons[910])
devices[900]=nil; data.srw.Robots[900]=nil; SRW.UpdateMountedWeapons(.04)
assert(not devices[911] and next(data.srw.MountedWeapons)==nil)
-- Individual release uses the same complete assembly.
f.srw_rocket_botReserve=1; f.ExitRemaining=0
SRW_ReleaseIndividual(101,50,9)
assert(f.srw_rocket_botReserve==0 and devices[900] and devices[910] and devices[911])
function dofile(name) assert(name=="weapons/missileswarm.lua") end
''')
lua.execute((root/'weapons/rocket_bot.lua').read_text())
lua.execute('assert(RoundsEachBurst==4 and RoundPeriod==.25 and ReloadTime==9 and Projectile=="srw_salvo_rocket")')
print('PASS: rocket registration/isolation, tier gate, production, release, salvo configuration and stationary firing hold')
