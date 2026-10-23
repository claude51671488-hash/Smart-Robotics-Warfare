from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
for name in ['combat/emp.lua','factories/squads.lua']:
 lua.execute((root/'scripts'/name).read_text(encoding='utf-8'))
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.Factories={[50]={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,8,1); assert(#f.SquadDraft==0)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_SquadEdit(101,50,8,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
assert(f.CurrentType=="srw_laser_bot" and balances[101].metal==9505)
for i=1,400 do SRW.UpdateFactories(.04) end
assert(SRW.FactoryReserve(f)==1)
function EnableWeapon(name,enabled,side) assert(name=="srw_laser_bot" and side==1) end
groundResult=1; rayResult=0; spawnId=-1
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04); assert(f.Squad.Released==0)
spawnId=900; f.ExitRemaining=0; SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and data.srw.Robots[900].Kind=="srw_laser_bot")
local bot=data.srw.Robots[900]; local x=devices[900].pos.x
devices[901]={team=102,kind="srw_hound",built=true,pos=Vec3(500,0,0)}
devices[902]={team=102,kind="mine",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 2 or 0 end
function GetDeviceIdSide(side,index) return 901+index end
local aimCalls=0; local firedAt
function AimWeapon(id,p) aimCalls=aimCalls+1; return true end
function FireWeapon(id,p,error,flags) fireCalls=fireCalls+1; firedAt=p; return 0 end
fireCalls=0; SRW.UpdateRobots(.04)
assert(bot.Target==901 and fireCalls==1 and bot.BeamRemaining==2)
assert(devices[900].pos.x==x)
devices[902]=nil; devices[901]=nil; local oldAim=aimCalls
for i=1,50 do SRW.UpdateRobots(.04) end
assert(devices[900].pos.x==x and fireCalls==1 and aimCalls==oldAim,"moving/retargeting during beam")
SRW.UpdateRobots(.04); assert(devices[900].pos.x>x)
devices[902]={team=102,kind="mine",built=true,pos=Vec3(1000,0,0)}
bot.FireWait=0; bot.EMPRemaining=5
function GetRandomFloat(a,b,key) return b end
SRW.UpdateRobots(.04); assert(firedAt.y~=0,"EMP aim perturbation lost")
devices[900].disabled=true; x=devices[900].pos.x
local shots=fireCalls; SRW.UpdateRobots(.04)
assert(devices[900].pos.x==x and fireCalls==shots)
function dofile(name)
 assert(name=="weapons/beamlaser.lua")
 Projectile="laser"; BeamDuration=1.5; Root={Sprite="laser-base"}; Sprites={{Name="laser-base"}}
end
''')
lua.execute((root/'weapons/laser_bot.lua').read_text(encoding='utf-8'))
lua.execute('''
assert(Projectile=="laser" and BeamDuration==1.5 and #Sprites==0)
assert(HitPoints==1100 and ReloadTime==8 and EnergyFireCost==0 and MinFireClearance==0)
assert(SRW.Config.Robots.srw_laser_bot.BeamHoldSeconds>BeamDuration)
''')
print('PASS: laser tier gate, production, failed/successful release, structure priority, beam hold, target loss, EMP and native configuration')
