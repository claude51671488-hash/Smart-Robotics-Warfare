from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_squads.py'))['lua']
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_3",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}
local function reset(tier)
 local f={Team=101,Tier=tier,Queue=0,Reserve=0,Remaining=0}
 data.srw.Factories={[50]=f}; balances[101]={metal=100000,energy=1000000}
 return f
end
local spawned
function SRW.SpawnHound(team,id,kind) spawned=kind; return not fail end
function SRW.SpawnShieldBot(team,id) spawned="srw_shield_bot"; return not fail end
function SRW.SpawnTank(team,id,kind) spawned=kind; return not fail end
for i=6,15 do
 local kind=SRW.RobotKinds[i]; local cfg=SRW.Config.Robots[kind]
 local f=reset(1)
 SRW_OrderIndividual(101,50,i); assert(not f[kind.."Queue"])
 f.Tier=3
 SRW_OrderIndividual(201,50,i); assert(not f[kind.."Queue"])
 SRW_OrderIndividual(101,50,i); assert(f[kind.."Queue"]==1 and not f.Squad)
 SRW.UpdateFactories(.04); assert(f.CurrentType==kind and not f.CurrentSquad)
 assert(balances[101].metal==100000-cfg.MetalCost)
 SRW.UpdateFactories(cfg.ProductionSeconds)
 assert(f[kind.."Reserve"]==1 and f.Reserve==0 and SRW.FactoryReserve(f)==1)
 assert(balances[101].metal==100000-cfg.MetalCost)
 fail=true; SRW_ReleaseIndividual(101,50,i); assert(f[kind.."Reserve"]==1)
 fail=false; f.ExitRemaining=1; SRW_ReleaseIndividual(101,50,i); assert(f[kind.."Reserve"]==1)
 f.ExitRemaining=0; SRW_ReleaseIndividual(101,50,i)
 assert(spawned==kind and f[kind.."Reserve"]==0 and f.ExitRemaining>0)
 -- An individual release must never consume a completed squad member.
 f.Squad={Items={kind},Produced=1,Released=0,TotalWork=cfg.ProductionSeconds}
 SRW_ReleaseIndividual(101,50,i); assert(f.Squad.Released==0)
end
local f=reset(3); f.srw_tank_botQueue=2; f.SquadDraft={"srw_hound"}
SRW_SquadStart(101,50)
assert(SRW.SquadEstimate(f)==SRW.Config.Robots.srw_hound.ProductionSeconds+2*SRW.Config.Robots.srw_tank_bot.ProductionSeconds)
f=reset(3); f.srw_colossus_botReserve=100; SRW_OrderIndividual(101,50,14)
SRW.UpdateFactories(.04); assert(f.Status=="reserve_full" and f.srw_tank_botQueue==1)
f=reset(3); selectedId=50; localTeam=101; SRW.SquadEditorOpen=false
SRW.RefreshUI()
for i=1,4 do SRW.ClickUI("srw_page") end
assert(visible.srw_single14_order and visible.srw_single15_release)
SRW.ClickUI("srw_single14_order"); assert(sent[1]=="SRW_OrderIndividual" and sent[2]=="101,50,14")
SRW.ClickUI("srw_single15_release"); assert(sent[1]=="SRW_ReleaseIndividual" and sent[2]=="101,50,15")
sent=nil; SRW.ClickUI("srw_single6_order"); assert(not sent)
SRW.ClickUI("srw_squad_mode"); assert(not visible.srw_single14_order)
''')
print('PASS: all advanced individual orders, tier/owner checks, charging, reserve, failed release, cooldown, squad isolation, ETA, capacity and UI events')
