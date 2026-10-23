from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_bastion.py'))['lua']
lua.execute('''
devices={[900]={team=101,kind="srw_bastion_bot",built=true,pos=Vec3(0,0,0)},
 [1000]={team=102,kind="mine",built=true,pos=Vec3(3000,0,0)},
 [1001]={team=102,kind="mine",built=true,pos=Vec3(3500,0,0)}}
local target=1000;local visible=true
function GetDeviceCountSide(side) return side==2 and visible and 1 or 0 end
function GetDeviceIdSide() return target end
local bot={Kind="srw_bastion_bot",Team=101,Direction=1}
data.srw.Robots={[900]=bot};data.srw.MountedWeapons={}
local shots=0;local result=FIRE_SUCCESS or 0
function FireWeapon() shots=shots+1;return result end
function AimWeapon() return true end
local function tick(n) for i=1,n do SRW.UpdateHound(900,bot,.04) end end
tick(100);assert(shots==0 and devices[900].pos.x==0)
target=1001;tick(30);assert(shots==0,'target switch reused old charge')
tick(21);assert(shots==1 and bot.FireWait>11)
tick(299);assert(shots==1,'reload bypassed')
tick(25);assert(shots==1,'charge must follow reload')
tick(30);assert(shots==2)
-- Moving the platform invalidates its firing setup.
bot.FireWait=0;devices[900].pos.x=20;tick(100);assert(shots==2)
tick(30);assert(shots==3)
-- Losing every reachable target clears setup and charge, then movement resumes.
bot.FireWait=0;visible=false;tick(1)
assert(bot.DeployPosition==nil and bot.ChargeTarget==nil and devices[900].pos.x>20)
visible=true;tick(100);assert(shots==3)
-- Disable cancels preparation; recovery must deploy again.
devices[900].disabled=true;tick(1);assert(not bot.DeployPosition)
devices[900].disabled=false;tick(100);assert(shots==3)
tick(30);assert(shots==4)
-- Targets in the dead zone cause retreat instead of an instant close-range shot.
bot.FireWait=0;devices[1001].pos=Vec3(devices[900].pos.x+400,0,0)
local x=devices[900].pos.x;tick(1)
assert(shots==4 and not bot.DeployPosition and devices[900].pos.x<x)
Projectiles={{SaveName="cannon",ProjectileDamage=999}}
''')
lua.execute((r/'weapons/projectile_list.lua').read_text(encoding='utf-8'))
lua.execute('''
local shells={};for _,p in ipairs(Projectiles) do shells[p.SaveName]=p end
assert(shells.srw_cathedral_shell.ProjectileDamage==4200 and shells.srw_cathedral_shell.ProjectileSplashDamage==2400)
assert(shells.srw_cathedral_shell.Gravity==981 and shells.srw_cathedral_shell.MaxAge==60)
assert(shells.srw_bastion_shell.ProjectileDamage==2100 and shells.srw_bastion_shell.ProjectileSplashDamage==90)
''')
print('PASS: Cathedral deployment, per-shot charge, reload, target switch, displacement, target loss, disable, dead-zone retreat and isolated siege shell')
