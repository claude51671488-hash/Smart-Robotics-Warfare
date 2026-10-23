from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
for name in ['factories/squads.lua','robots/shield.lua','shields.lua']:
 lua.execute((root/'scripts'/name).read_text())
lua.execute('''
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.Shields={}
data.srw.Factories={[50]={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,11,1); assert(#f.SquadDraft==0)
f.Tier=3; devices[50].kind="srw_factory_ground_3"
SRW_SquadEdit(101,50,11,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
assert(f.CurrentType=="srw_bastion_bot" and balances[101].metal==8900)
for i=1,750 do SRW.UpdateFactories(.04) end
assert(SRW.FactoryReserve(f)==1)
function EnableWeapon(name,enabled,side) assert(name=="srw_bastion_bot" and side==1) end
groundResult=1; rayResult=0; spawnId=900
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and f.ExitRemaining==8)
function GetDeviceCountSide(side) return side==1 and 1 or 0 end
function GetDeviceIdSide(side,index) return 900 end
SRW.ScanShields(); local s=data.srw.Shields[900]; local bot=data.srw.Robots[900]
assert(s.Kind=="srw_bastion_bot" and s.MaxHP==6000 and math.abs(s.Arc[33].y+240)<.001)
SRW.UpdateShieldPower(.04); assert(s.Active)
SRW.ShieldDamage(s,100); assert(s.HP==5900)
bot.EMPRemaining=5; SRW.UpdateShieldPower(.04)
assert(s.EMPWeakened); SRW.ShieldDamage(s,100); assert(s.HP==5750)
SRW.ShieldDamage(s,10000); SRW.UpdateShieldPower(1); assert(s.HP==75 and not s.Active)
bot.EMPRemaining=nil; SRW.UpdateShieldPower(1); assert(s.HP==225 and not s.EMPWeakened)
devices[900].disabled=true; SRW.UpdateShieldPower(1); assert(s.HP==225 and not s.Active)
devices[900].disabled=false
devices[901]={team=102,kind="mine",built=true,pos=Vec3(3000,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide(side,index) return 901 end
canAim=true; fireCalls=0; SRW.UpdateRobots(.04)
assert(bot.Target==901 and fireCalls==0)
for i=1,126 do SRW.UpdateRobots(.04) end
assert(fireCalls==1 and bot.FireWait>11)
devices[900]=nil; SRW.ScanShields(); assert(not data.srw.Shields[900])
function dofile(name) assert(name==path.."/weapons/hound.lua") end
''')
lua.execute((root/'weapons/bastion_bot.lua').read_text())
lua.execute('assert(HitPoints==3500 and Scale==.8 and ReloadTime==12 and MaxFireRadius==51200)')
print('PASS: Bastion tier III, production/release, 8s exit, personal shield, EMP weakening/recovery, native disable, firing and cleanup')
