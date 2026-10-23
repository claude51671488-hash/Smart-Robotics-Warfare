from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_hound.py'))['lua']
lua.execute((root/'scripts/factories/squads.lua').read_text())
lua.execute('table.insert(Projectiles,{SaveName="mortar2",ProjectileDamage=1,DisableShields=true})')
lua.execute((root/'weapons/projectile_list.lua').read_text())
lua.execute('''
local shell;for _,p in ipairs(Projectiles) do if p.SaveName=="srw_heavy_siege_he" then shell=p end end
assert(shell.SaveName=="srw_heavy_siege_he" and shell.ProjectileSplashDamage==1950 and not shell.DisableShields)
devices={[50]={team=101,kind="srw_factory_ground_2",built=true,pos=Vec3(0,0,0)}}
data.srw.Robots={}; data.srw.Factories={[50]={Team=101,Tier=2,Queue=0,Reserve=0,Remaining=0}}
local f=data.srw.Factories[50]; balances[101]={metal=10000,energy=100000}
SRW_SquadEdit(101,50,13,1); assert(#f.SquadDraft==0)
f.Tier=3; devices[50].kind="srw_factory_ground_3"
SRW_SquadEdit(101,50,13,1); SRW_SquadStart(101,50); SRW.UpdateFactories(.04)
assert(f.CurrentType=="srw_heavy_siege_bot" and balances[101].metal==8790)
for i=1,875 do SRW.UpdateFactories(.04) end
assert(SRW.FactoryReserve(f)==1)
function EnableWeapon(name,enabled,side) assert((name=="srw_heavy_siege_bot" or name=="srw_censer_mortar" or name=="srw_censer_laser") and side==1) end
local oldCreate=dlc2_CreateFloatingDevice
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind~="srw_heavy_siege_bot" then
  local id=kind=="srw_censer_mortar" and 910 or 911
  devices[id]={team=team,kind=kind,pos=p,built=true};return id
 end
 return oldCreate(team,kind,p,angle)
end
groundResult=1; rayResult=0; spawnId=900
SRW_SquadRelease(101,50); SRW.UpdateFactories(.04)
assert(f.Squad.Released==1 and f.ExitRemaining==8)
local bot=data.srw.Robots[900]; devices[900].pos=Vec3(0,0,0)
devices[901]={team=102,kind="mine",built=true,pos=Vec3(6500,0,0)}
function GetDeviceCountSide(side) return side==2 and 1 or 0 end
function GetDeviceIdSide(side,index) return 901 end
canAim=true; fireCalls=0; SRW.UpdateRobots(.04)
assert(bot.Target==901 and fireCalls==1 and bot.FireWait==12)
devices[901].pos.x=800; SRW.UpdateRobots(.04)
assert(devices[900].pos.x<0 and fireCalls==1,"close target must force retreat")
local x=devices[900].pos.x; groundResult=0; SRW.UpdateRobots(.04)
assert(devices[900].pos.x==x,"retreated over cliff")
groundResult=1; devices[900].disabled=true; SRW.UpdateRobots(.04)
assert(devices[900].pos.x==x and fireCalls==1)
devices[900].disabled=false; devices[901].team=201; SRW.UpdateRobots(.04)
assert(not bot.Target and fireCalls==1)
function dofile(name) assert(name==path.."/weapons/siege_bot.lua") end
''')
lua.execute((root/'weapons/heavy_siege_bot.lua').read_text())
lua.execute('assert(HitPoints==2200 and MinFireSpeed==1000 and MaxFireSpeed==15000 and ReloadTime==12 and Projectile=="srw_heavy_siege_he")')
print('PASS: Thunder tier gate, production/release, range, retreat, cliffs, native EMP, allies and heavy shell')
