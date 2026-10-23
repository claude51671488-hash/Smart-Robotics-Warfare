from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
lua.execute((r/'scripts/factories/squads.lua').read_text())
lua.execute((r/'scripts/robots/aa.lua').read_text())
lua.execute((r/'scripts/combat/guidance.lua').read_text())
lua.execute("""
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
local f={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}
data.srw.Factories={[50]=f}; balances[101]={metal=10000,energy=100000}
assert(SRW.RobotKinds[18]=="srw_pike_bot")
SRW_OrderIndividual(101,50,18); assert(not f.srw_pike_botQueue)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_OrderIndividual(201,50,18); assert(not f.srw_pike_botQueue)
SRW_OrderIndividual(101,50,18); SRW.UpdateFactories(.04)
assert(balances[101].metal==9500 and balances[101].energy==96000)
for i=1,510 do SRW.UpdateFactories(.04) end
assert(f.srw_pike_botReserve==1)
local fail=true
function EnableWeapon() end
function DeleteDeviceById(id) devices[id]=nil end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if fail and kind=="srw_pike_turret" then return -1 end
 local ids={srw_pike_bot=900,srw_pike_turret=901}
 local id=assert(ids[kind]);devices[id]={team=team,kind=kind,pos=p,built=true};return id
end
SRW_ReleaseIndividual(101,50,18)
assert(f.srw_pike_botReserve==1 and not devices[900] and not devices[901])
fail=false; SRW_ReleaseIndividual(101,50,18)
assert(f.srw_pike_botReserve==0 and devices[900] and devices[901])
assert(not data.srw.Robots[900].SquadSpeed)

function ProjectileCount(side) return side==2 and 1 or 0 end
function GetProjectileId() return 3000 end
function NodeExists() return true end
function NodeTeam(id) return id==3000 and 102 or 101 end
function NodePosition(id) return id==3000 and Vec3(8000,-500,0) or Vec3(0,0,0) end
function NodeVelocity(id) return id==3000 and Vec3(-500,0,0) or Vec3(6000,-300,0) end
function GetNodeProjectileSaveName(id) return id==3000 and "missile" or "srw_pike_rocket" end
function GetProjectileParamFloat() return 20 end
local shots={}
function FireWeapon(id,p,e,flags) shots[id]=(shots[id] or 0)+1;return 0 end
SRW.UpdateRobots(.04)
assert(shots[900]==1 and data.srw.Robots[900].Target==3000)
SRW.GuidedLaunch(101,900,4000)
assert(data.srw.GuidedMissiles[4000].Air and data.srw.GuidedMissiles[4000].Target==3000)
local bot=data.srw.Robots[900];bot.EMPRemaining=3;bot.FireWait=0
SRW.UpdateAABot(900,bot,.04);assert(shots[900]==1 and not bot.Target)
SRW.GuidedLaunch(101,900,4001);assert(not data.srw.GuidedMissiles[4001].Target)
-- Secondary gun remains available under tier-II EMP, and attacks ground independently.
devices[910]={team=102,kind="mine",built=true,pos=Vec3(1000,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide() return 910 end
SRW.UpdateMountedWeapons(.04);assert(shots[901]==1)
devices[900]=nil;data.srw.Robots[900]=nil;SRW.UpdateMountedWeapons(.04)
assert(not devices[901])
""")
print('PASS: Pike tier, ownership, price, rollback, distant AA target, guided root missile, EMP and independent defensive gun')
