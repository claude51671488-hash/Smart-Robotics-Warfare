from pathlib import Path
import sys
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime
lua=LuaRuntime()
lua.execute('''
SRW={};data={};devices={};nodes={};energy=100000;nextNode=1000
function Vec3(x,y,z) return {x=x,y=y,z=z or 0} end
function Log() end
function DeviceExists(id) return devices[id]~=nil end
function GetDeviceType(id) return devices[id].Kind end
function GetDeviceTeamIdActual(id) return devices[id].Team end
function GetDeviceCentrePosition(id) return Vec3(0,0,0) end
function DeviceDisabled() return false end
function IsDeviceFullyBuilt() return true end
function GetTeamResources() return {energy=energy} end
function AddResources(team,cost) energy=energy+cost.energy end
function GetDeviceCost() return {energy=10000,metal=3000} end
function DeleteDeviceById(id) devices[id]=nil;return true end
function GetDeviceCountSide(side) return #ids end
function GetDeviceIdSide(side,i) return ids[i+1] end
function GetRandomFloat(a,b) return b end
function NodeExists(id) return nodes[id]~=nil end
function DestroyProjectile(id) nodes[id]=nil end
function dlc2_CreateProjectile(name,weapon,team,p,v,life)
 nextNode=nextNode+1;nodes[nextNode]={Name=name,Team=team};return nextNode
end
function GetProjectileParamFloat(name,team,key,default) return 1000 end
''')
for f in ['config.lua','state.lua','factories/production.lua','shields.lua','shield_levels.lua','combat/aiming.lua']:
    lua.execute((r/'scripts'/f).read_text())
lua.execute('''
SRW.EnsureState()
assert(SRW.Config.Robots.srw_siege_bot.Range==40000)
assert(SRW.Config.Robots.srw_hound.Range==14000)
assert(math.abs(SRW.Config.Robots.srw_colossus_bot.SpeedMinesPerSecond-1.95)<1e-8)
local bot={CombatClock=1};local cfg=SRW.Config.Robots.srw_siege_bot
local target={Id=50,Position=Vec3(10000,-400,0),Distance=100000000}
SRW.AimSolution(1,bot,cfg,target,.04,false)
local first=SRW.AimSolution(1,bot,cfg,target,.04,true)
bot.RangingShots=8
local last=SRW.AimSolution(1,bot,cfg,target,.04,true)
assert(first.x>last.x and last.x>10000 and last.y==-400)
bot.CombatClock=1.04;target.Position.x=10004
local lead=SRW.AimSolution(1,bot,cfg,target,.04,false)
assert(lead.x>target.Position.x,'no lead for receding target')
bot.CombatClock=1.08;target.Position.x=9990
lead=SRW.AimSolution(1,bot,cfg,target,.04,false)
assert(lead.x<target.Position.x and bot.RangingShots==0,'reversal must lose ranging')
local direct={Range=18000,ReloadSeconds=5}
target.Id=51;target.Position=Vec3(17000,-300,0);target.Distance=17000^2
local q,far,fire=SRW.AimSolution(1,bot,direct,target,.04,false)
assert(not fire and q.y==-300,'distant slow cannon should approach, retaining elevation')
target.Position=Vec3(2000,-300,0);target.Distance=2000^2;target.Id=52
q,near,fire=SRW.AimSolution(1,bot,direct,target,.04,false)
assert(fire and near<far)
devices={[1]={Kind='srw_shield_generator',Team=101},[2]={Kind='srw_shield_generator_2',Team=201},[3]={Kind='srw_shield_generator',Team=101}}
ids={1,2,3};SRW.ShieldCreated(101,3,'srw_shield_generator',0)
assert(not devices[3],'combined allied-side cap must include upgraded allied generators')
data.srw.Shields[1]={Team=101,Tier=1,HP=3000,MaxHP=4000,Radius=640,Active=true}
devices[4]={Kind='srw_shield_generator_2',Team=101}
SRW.ShieldCreated(101,4,'srw_shield_generator_2',1)
assert(not data.srw.Shields[1] and data.srw.Shields[4].HP==3000 and data.srw.Shields[4].MaxHP==8000)
for tier=1,3 do
 local cfg=SRW.ShieldLevels[tier]
 local s={Team=101,Tier=tier,HP=0,ColdRecovery=true,Active=false}
 data.srw.Shields={[4]=s};local before=energy;SRW.UpdateShieldPower(1)
 assert(s.HP==cfg.BrokenRegen and energy==before-cfg.Energy)
 s.HP=cfg.HP-500;s.ColdRecovery=false;s.Active=true;s.QuietSeconds=0
 SRW.UpdateShieldPower(9);assert(s.HP==cfg.HP-500)
 SRW.UpdateShieldPower(1);assert(s.HP==cfg.HP-500+cfg.IdleRegen)
end
local s=data.srw.Shields[4];s.Tier=3;s.Active=true
s.Arc={Vec3(100,-100,0),Vec3(100,100,0)}
SRW.UpdateBeamBarriers(.04)
local b=data.srw.BeamBarriers[4];assert(b and #b.Nodes==3)
local hp=s.HP;OnFieldHitBeam(b.Nodes[1],'srw_beam_barrier',20,102,'laser')
assert(s.HP==hp-40 and s.QuietSeconds==0)
s.Active=false;SRW.UpdateBeamBarriers(.04)
assert(next(nodes)==nil and next(data.srw.BeamBarriers)==nil)
assert(SRW.RobotKinds[19]=='srw_executioner_bot')
assert(#SRW.Config.Robots.srw_executioner_bot.Mounts==2)
assert(not SRW.Config.Robots.srw_executioner_bot.ShieldHP)
''')
print('PASS: balance, ranging, moving targets, direct-fire restraint, shield tiers/regen/upgrade/cap, laser fields cleanup, Executioner roster')
