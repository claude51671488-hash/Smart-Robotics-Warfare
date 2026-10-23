from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
lua.execute((r/'scripts/factories/squads.lua').read_text())
lua.execute("""
devices={[50]={team=101,kind="srw_factory_ground_3",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.MountedWeapons={}
local f={Team=101,Tier=3,Queue=0,Reserve=0,Remaining=0,
 SquadDraft={"srw_hound","srw_hound","srw_colossus_bot"}}
data.srw.Factories={[50]=f}; balances[101]={metal=10000,energy=100000}
SRW_SquadStart(101,50)
assert(math.abs(f.Squad.Speed-(5.95/3))<.000001,'mean must count duplicate robots')
f.SquadDraft={"srw_hunter_bot"}
balances[101].metal=219; SRW.UpdateFactories(.04)
assert(f.Status=="resources" and not f.CurrentType and balances[101].metal==219)
balances[101].metal=10000
SRW.UpdateFactories(.04)
assert(balances[101].metal==9780 and balances[101].energy==97800)
for i=1,1600 do SRW.UpdateFactories(.04) end
assert(f.Squad.Produced==3 and balances[101].metal==7800 and balances[101].energy==80200)
local nextId=1000
function EnableWeapon() end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 nextId=nextId+1; devices[nextId]={team=team,kind=kind,pos=p,built=true}; return nextId
end
function DeleteDeviceById(id) devices[id]=nil end
SRW_SquadRelease(101,50)
for i=1,300 do SRW.UpdateFactories(.04) end
assert(f.Squad.Released==3)
local ids=SRW.SortedIds(data.srw.Robots)
assert(#ids==3)
function GetDeviceCountSide() return 0 end
for _,id in ipairs(ids) do
 local bot=data.srw.Robots[id]
 assert(bot.SquadSpeed==(5.95/3))
 assert(bot.SquadId==f.Squad.Id and bot.SquadId>0)
 local x=devices[id].pos.x
 SRW.UpdateHound(id,bot,.04)
 assert(math.abs(devices[id].pos.x-x-(5.95/3)*127.5*.04)<.000001)
end
devices[ids[1]]=nil; data.srw.Robots[ids[1]]=nil
assert(data.srw.Robots[ids[3]].SquadSpeed==(5.95/3))
-- Individual orders keep base price and their original movement speed.
f.ExitRemaining=0; f.srw_hunter_botQueue=1
local metal,energy=balances[101].metal,balances[101].energy
SRW.UpdateFactories(.04)
assert(balances[101].metal==metal-350 and balances[101].energy==energy-3000)
for i=1,310 do SRW.UpdateFactories(.04) end
SRW_ReleaseIndividual(101,50,10)
local hunter
for id,bot in pairs(data.srw.Robots) do if bot.Kind=="srw_hunter_bot" then hunter=id end end
assert(hunter and not data.srw.Robots[hunter].SquadSpeed)
local x=devices[hunter].pos.x; SRW.UpdateHound(hunter,data.srw.Robots[hunter],.04)
assert(math.abs(devices[hunter].pos.x-x-2.4*127.5*.04)<.000001)
""")
print('PASS: weighted squad mean, fixed speed after casualties, exact surcharge/resource gate, single-order costs and actual movement')
