"""Skycleaver assembly and deployment integration; Forts adapters are mocked."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_aa.py'))['lua']
for module in ('factories/squads.lua','combat/aiming.lua','combat/emp.lua','combat/guidance.lua','robots/heavy_aa.lua','ui/robot_braces.lua'):
    lua.execute((r/'scripts'/module).read_text(encoding='utf-8'))
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={};data.srw.MountedWeapons={}
local f={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0}
data.srw.Factories={[50]=f};balances[101]={metal=10000,energy=100000}
assert(SRW.RobotKinds[12]=="srw_heavy_aa_bot" and #SRW.RobotKinds==30)
assert(not SRW.Config.Robots.srw_heavy_aa_bot.ShieldHP)
SRW_OrderIndividual(101,50,12);assert(not f.srw_heavy_aa_botQueue)
SRW_SquadEdit(101,50,12,1);assert(#f.SquadDraft==0)
f.Tier=3;devices[50].kind="srw_factory_ground_3"
SRW_OrderIndividual(201,50,12);assert(not f.srw_heavy_aa_botQueue)
SRW_OrderIndividual(101,50,12);SRW.UpdateFactories(.04)
assert(balances[101].metal==9200 and balances[101].energy==93500)
for i=1,600 do SRW.UpdateFactories(.04) end
assert(f.srw_heavy_aa_botReserve==1)
local ids={srw_heavy_aa_bot=900,srw_heavy_aa_gun=901,srw_heavy_aa_rockets=902,srw_heavy_aa_defence=903}
local fail
function EnableWeapon(name,enabled,side) assert(ids[name] and side==1) end
function DeleteDeviceById(id) devices[id]=nil end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 assert(angle==90)
 if kind==fail then return -1 end
 local id=assert(ids[kind]);devices[id]={team=team,kind=kind,pos=p,built=true};return id
end
for _,kind in ipairs({"srw_heavy_aa_gun","srw_heavy_aa_rockets","srw_heavy_aa_defence"}) do
 fail=kind;SRW_ReleaseIndividual(101,50,12)
 assert(f.srw_heavy_aa_botReserve==1 and next(data.srw.MountedWeapons)==nil)
 for _,id in pairs(ids) do assert(not devices[id]) end
 assert(next(data.srw.Robots)==nil)
end
fail=nil;SRW_ReleaseIndividual(101,50,12)
assert(f.srw_heavy_aa_botReserve==0 and f.ExitRemaining==8)
for _,id in pairs(ids) do assert(devices[id]) end
local bot=data.srw.Robots[900]
assert(not bot.SquadSpeed and bot.GroundLift==320)
local count=2;local side=102;local radius=15
function ProjectileCount(s) return s==2 and count or 0 end
function GetProjectileId(s,index) return 100+index end
function NodeExists(id) return id==100 or id==101 or id==3000 end
function NodeTeam(id) return id==3000 and 101 or side end
function NodePosition(id)
 if id==3000 then return Vec3(0,-700,0) end
 return Vec3(id==100 and 1000 or 15000,-800,0)
end
function NodeVelocity(id) return id==3000 and Vec3(0,-6000,0) or Vec3(-1000,0,0) end
function GetNodeProjectileSaveName(id) return id==3000 and "srw_heavy_aa_rocket" or tostring(id) end
function GetProjectileParamFloat(name,team,param,default)
 if param=="ProjectileShootDownRadius" then return radius end
 if param=="ProjectileDamage" then return name=="100" and 10 or 700 end
 return default
end
function GetDeviceCountSide(s) return s==2 and 2 or 0 end
function GetDeviceIdSide(s,i) return 910+i end
devices[910]={team=102,kind="mine",built=true,pos=Vec3(1500,0,0)}
devices[911]={team=102,kind="srw_hound",built=true,pos=Vec3(1000,0,0)}
function SRW.BeamTargets() return {} end
function SRW.GroundAt(x,y,reach) return Vec3(x,0,0) end
function CastGroundRay() return RAY_HIT_NOTHING end
function AimWeapon() return true end
local shots,aims={},{}
function FireWeapon(id,p,error,flags) shots[id]=(shots[id] or 0)+1;aims[id]=p;return 0 end
local paint
function SetWeaponPaintTarget(id,p) paint=p end
local function tick()
 SRW.BeginCombatSnapshot();SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04);SRW.EndCombatSnapshot()
end
local initial=devices[900].pos.x
for i=1,37 do tick() end
assert(bot.BraceActive and not bot.Braced and not shots[900] and not shots[901] and not shots[902])
assert(shots[903] and data.srw.MountedWeapons[903].Target==911,'defence unavailable during deployment')
assert(devices[900].pos.x==initial)
tick()
assert(bot.Braced and shots[900]==1 and shots[901]==1 and shots[902]==1)
assert(bot.Target==101 and data.srw.MountedWeapons[901].Target==101)
assert(data.srw.MountedWeapons[902].Target==101 and paint.x==15000,'long-range guided acquisition truncated')
assert(aims[900].x<15000,'AA gun does not lead the moving threat')
local missileAim
function SetMissileTarget(id,p) assert(id==3000);missileAim=p end
SRW.GuidedLaunch(101,902,3000)
assert(data.srw.GuidedMissiles[3000].Air and data.srw.GuidedMissiles[3000].Target==101)
SRW.UpdateGuidance(.04);assert(missileAim.x==0 and missileAim.y<-700)
SRW.UpdateGuidance(.12);assert(missileAim.x>10000)
SRW.UpdateGuidance(8);assert(next(data.srw.GuidedMissiles)==nil)
local oldY=aims[900].y;local rockets=shots[902]
function GetRandomFloat(a,b,key) return b end
bot.EMPRemaining=3;bot.FireWait=0
for _,part in pairs(data.srw.MountedWeapons) do part.FireWait=0 end
tick()
assert(shots[900]==2 and shots[901]==2 and shots[902]==rockets and aims[900].y~=oldY)
assert(data.srw.MountedWeapons[902].EMPRemaining==3 and not data.srw.MountedWeapons[902].Target)
devices[911]=nil;data.srw.MountedWeapons[903].FireWait=0;tick()
assert(data.srw.MountedWeapons[903].Target==910)
devices[900].pos.x=devices[900].pos.x+20;bot.FireWait=0
local gunShots=shots[900];tick();assert(not bot.Braced and shots[900]==gunShots)
devices[900].disabled=true;tick();assert(not bot.BraceActive and bot.BraceProgress==0)
devices[900].disabled=false;bot.EMPRemaining=0
for _,part in pairs(data.srw.MountedWeapons) do part.EMPRemaining=0 end
for i=1,38 do tick() end
assert(bot.Braced)
local lines=0;local cloaked=false
function IsCloaked() return cloaked end
function SpawnLine(a,b,c,life) assert(life<=.05);lines=lines+1 end
SRW.RefreshRobotBraces(.04);assert(lines==4)
cloaked=true;SRW.RefreshRobotBraces(.04);assert(lines==4);cloaked=false
side=201;radius=0
devices[920]={team=101,kind="srw_hound",built=true,pos=Vec3(2000,0,0)}
data.srw.Robots[920]={Team=101,Kind="srw_hound",Direction=1}
local x=devices[900].pos.x
for i=1,10 do tick() end
assert(bot.BraceActive and devices[900].pos.x==x)
for i=1,35 do tick() end
assert(not bot.BraceActive and devices[900].pos.x>x,'escort did not resume')
devices[900].team=102;tick()
assert(not data.srw.Robots[900] and next(data.srw.MountedWeapons)==nil)
for _,id in ipairs({901,902,903}) do assert(not devices[id]) end
lines=0;SRW.RefreshRobotBraces(.04);assert(lines==0)
data.srw.Robots={};devices[900]=nil;devices[920]=nil
f.ExitRemaining=0;f.SquadDraft={"srw_heavy_aa_bot"};SRW_SquadStart(101,50)
local m,e=balances[101].metal,balances[101].energy;SRW.UpdateFactories(.04)
assert(balances[101].metal==m-880 and balances[101].energy==e-7150)
for i=1,600 do SRW.UpdateFactories(.04) end
assert(f.Squad.Produced==1 and SRW.FactoryReserve(f)==1)
SRW_SquadRelease(101,50);SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and f.ExitRemaining==8 and #SRW.SortedIds(data.srw.MountedWeapons)==3)
assert(math.abs(data.srw.Robots[900].SquadSpeed-3.3)<.000001)
Projectiles={{SaveName="machinegun",ProjectileDamage=6,WeaponDamageBonus=6},{SaveName="missile",Missile={}}}
''')
source=(r/'weapons/projectile_list.lua').read_text(encoding='utf-8')
lua.execute(source);lua.execute(source)
lua.execute('''
local p={};for _,v in ipairs(Projectiles) do assert(not p[v.SaveName]);p[v.SaveName]=v end
assert(p.srw_heavy_aa_bullet.AntiAirDamage==200 and p.srw_heavy_aa_bullet.Gravity==981)
assert(p.srw_heavy_aa_rocket.AntiAirDamage==900 and p.srw_heavy_aa_rocket.ProjectileDamage==300)
assert(p.srw_heavy_aa_rocket.Gravity==0 and p.srw_heavy_aa_rocket.MaxAge==8)
assert(p.srw_heavy_aa_rocket.ProjectileSplashDamage==140 and p.srw_pike_rocket.AntiAirDamage==700)
''')
print('PASS: Skycleaver solo/squad, atomic four-weapon assembly, deployment/escort, long-range AA, ground fallback, EMP, guidance, cloak-safe visuals and capture cleanup')
