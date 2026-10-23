from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
for name in ['robots/repair.lua','robots/shield.lua','factories/squads.lua']:
 lua.execute((root/'scripts'/name).read_text(encoding='utf-8'))
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_1",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.Factories={[50]={Team=101,Tier=1,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]
balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,6,1); assert(not f.SquadDraft or #f.SquadDraft==0)
f.Tier=2; devices[50].kind="srw_factory_ground_2"
SRW_SquadEdit(101,50,6,1); assert(f.SquadDraft[1]=="srw_shield_bot")
f.Tier=1; SRW_SquadStart(101,50); assert(not f.Squad)
f.Tier=2; SRW_SquadStart(101,50)
SRW.UpdateFactories(.04); assert(f.CurrentType=="srw_shield_bot")
for i=1,375 do SRW.UpdateFactories(.04) end
assert(f.Squad.Produced==1 and SRW.FactoryReserve(f)==1)
function EnableDevice(name,enabled,side) assert(name=="srw_shield_bot" and side==1) end
groundResult=1; rayResult=0; spawnId=900
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and data.srw.Robots[900].Kind=="srw_shield_bot")
local bot=data.srw.Robots[900]; devices[900].pos=Vec3(0,0,0)
SRW.UpdateShieldBot(900,bot,.2); assert(devices[900].pos.x==0)
devices[901]={team=102,kind="srw_hound",built=true,pos=Vec3(600,0,0)}
data.srw.Robots[901]={Team=102,Kind="srw_hound"}
SRW.UpdateShieldBot(900,bot,.2); assert(devices[900].pos.x==0)
devices[901].team=201; data.srw.Robots[901].Team=201
SRW.UpdateShieldBot(900,bot,.2); assert(devices[900].pos.x>0)
local x=devices[900].pos.x; devices[900].disabled=true
SRW.UpdateShieldBot(900,bot,.2); assert(devices[900].pos.x==x)
devices[900].disabled=false; groundResult=0
SRW.UpdateShieldBot(900,bot,.2); assert(devices[900].pos.x==x)
''')
print('PASS: shield escort tier gate, production/reserve/release, allied escort, solo wait, EMP and cliff')
