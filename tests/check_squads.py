from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute((root/'scripts/factories/squads.lua').read_text(encoding='utf-8'))
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.SquadTemplates={}
function resetFactory()
 data.srw.Factories={[50]={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0,Status="ready"}}
 balances[101]={metal=10000,energy=100000}
 return data.srw.Factories[50]
end
local f=resetFactory()
SRW_SquadEdit(201,50,2,1); assert(not f.SquadDraft)
SRW_SquadEdit(101,50,999,1); assert(not f.SquadDraft)
SRW_SquadEdit(101,50,2,1); SRW_SquadEdit(101,50,3,1); SRW_SquadEdit(101,50,2,1)
assert(#f.SquadDraft==3 and f.SquadDraft[2]=="srw_repair_bot")
SRW_SquadSave(101,50); SRW_SquadClear(101,50); assert(#f.SquadDraft==0)
SRW_SquadLoad(101,50); assert(#f.SquadDraft==3)
SRW_SquadStart(101,50); local job=f.Squad
assert(job and SRW.FactoryQueue(f)==3 and SRW.FactoryReserve(f)==0)
assert(SRW.SquadEstimate(f)==22)
SRW_SquadStart(101,50); assert(f.Squad==job)
SRW_OrderHound(101,50); assert(not f.HoundQueue, "single order inserted into squad")
SRW_SquadClear(101,50); assert(#job.Items==3, "draft edits mutate production")
balances[101].energy=0; SRW.UpdateFactories(0.04)
assert(job.Produced==0 and f.Remaining==0 and f.Status=="resources")
assert(SRW.SquadEstimate(f)==22)
balances[101].energy=100000
SRW.UpdateFactories(0.04); assert(f.CurrentSquad and f.CurrentType=="srw_hound")
local charged=balances[101].energy
SRW.UpdateFactories(1); assert(f.Remaining==6 and balances[101].energy==charged)
local remaining,progress=SRW.SquadEstimate(f); assert(remaining==21 and progress>0)
devices[50].disabled=true; SRW.UpdateFactories(1); assert(f.Remaining==6)
devices[50].disabled=false
for i=1,540 do SRW.UpdateFactories(0.04) end
assert(job.Produced==3 and SRW.FactoryReserve(f)==3 and SRW.FactoryQueue(f)==0)
assert(SRW.SquadEstimate(f)==0 and not f.HoundReserve and f.Reserve==0)
SRW_ReleaseHound(101,50); assert(job.Released==0, "individual release stole squad member")
local spawned={}; local fail=false
function SRW.SpawnTank(team,id,kind) return SRW.SpawnHound(team,id,kind) end
function SRW.SpawnHound(team,id,kind)
 if fail then return false end
 spawned[#spawned+1]=kind or "srw_hound"; return true
end
function SRW.SpawnRepairBot(team,id)
 if fail then return false end
 spawned[#spawned+1]="srw_repair_bot"; return true
end
-- Previous unit determines exit time, not the next one.
SRW.Config.Robots.srw_hound.ExitDelay=8
SRW_SquadRelease(201,50); assert(not job.Releasing)
SRW_SquadRelease(101,50); SRW.UpdateFactories(0.04)
assert(job.Released==1 and SRW.FactoryReserve(f)==2 and f.ExitRemaining==8)
SRW_SquadRelease(101,50); SRW.UpdateFactories(7.96); assert(job.Released==1)
fail=true; SRW.UpdateFactories(0.04)
assert(job.Released==1 and SRW.FactoryReserve(f)==2)
fail=false; SRW.UpdateFactories(0.5)
assert(job.Released==2 and spawned[2]=="srw_repair_bot" and f.ExitRemaining==3)
f.HoundReserve=1; SRW_ReleaseHound(101,50)
assert(f.HoundReserve==1 and job.Released==2, "manual release bypassed shared timer")
SRW.UpdateFactories(3)
assert(job.Released==3 and not job.Releasing and SRW.FactoryReserve(f)==1)
assert(spawned[1]=="srw_hound" and spawned[3]=="srw_hound")
SRW.Config.Robots.srw_hound.ExitDelay=3
-- Existing queue is included in reserved space and ETA.
f=resetFactory(); f.Queue=2; f.Remaining=4; f.CurrentType="srw_dynamit_bot"
f.SquadDraft={"srw_hound"}; SRW_SquadStart(101,50)
assert(SRW.SquadEstimate(f)==25)
f=resetFactory(); f.Reserve=19; f.Queue=1; f.SquadDraft={"srw_hound"}
SRW_SquadStart(101,50); assert(not f.Squad and f.Status=="squad_full")
-- Snapshot is preserved by upgrade transfer, including release cooldown.
f=resetFactory(); f.SquadDraft={"srw_hound"}; SRW_SquadStart(101,50)
f.ExitRemaining=2
devices[51]={team=101,kind="srw_factory_ground_2",built=false,pos=Vec3(0,0,0)}
SRW.FactoryCreated(101,51,"srw_factory_ground_2",50)
assert(data.srw.Factories[51]==f and f.Squad and f.ExitRemaining==2)
-- Saved template belongs to the owner and survives replacing the factory.
assert(#data.srw.SquadTemplates[101]==3 and not data.srw.SquadTemplates[201])
devices[50].built=true; data.srw.Factories[50]=f; data.srw.Factories[51]=nil
selectedId=50; localTeam=101
''')
lua.execute((root/'scripts/ui/squads.lua').read_text(encoding='utf-8'))
lua.execute('''
SRW.RefreshUI(); assert(visible.srw_squad_mode and not visible.srw_squad_add1)
SRW.ClickUI("srw_squad_mode")
assert(visible.srw_squad_add1 and visible.srw_squad_Release and not visible.srw_order)
local f=data.srw.Factories[50]; local count=#f.SquadDraft
SRW.ClickUI("srw_squad_add2"); assert(sent[1]=="SRW_SquadEdit" and sent[2]=="101,50,2,1")
assert(#f.SquadDraft==count, "UI mutated simulation directly")
SRW.ClickUI("srw_squad_Release"); assert(sent[1]=="SRW_SquadRelease")
assert(not visible.srw_squad_add10)
SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==2)
assert(visible.srw_squad_add10 and not visible.srw_squad_add1)
SRW.ClickUI("srw_squad_add10"); assert(sent[2]=="101,50,10,1")
SRW.ClickUI("srw_squad_add1"); assert(sent[2]=="101,50,10,1", "hidden row accepted")
SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==3 and not visible.srw_squad_add11)
f.Tier=3; SRW.RefreshUI(); assert(visible.srw_squad_add11)
SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==4 and visible.srw_squad_add16)
SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==5 and visible.srw_squad_add21)
SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==1 and visible.srw_squad_add1)
selectedId=-1; SRW.RefreshUI(); assert(not visible.srw_squad_Release and not visible.srw_squad_mode)
''')
print('PASS: squad ownership, template, queue, ETA, resource/EMP pauses, reserved inventory, ordered one-click release, 8/3 second intervals, failures, manual cooldown, upgrade and UI events')
