from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/check_shields.py'))['lua']
for name in ['config.lua','robots/shield.lua']:
 lua.execute((root/'scripts'/name).read_text(encoding='utf-8'))
lua.execute('''
local origin=Vec3(1000,0,0)
function GetProjectileId(side,index) return 100 end
function NodeExists(id) return not dead[id] end
function GetDeviceCentrePosition(id) return origin end
function GetDevicePosition(id) return GetDeviceCentrePosition(id) end
function GetDeviceType(id) return "srw_shield_bot" end
data.srw.Robots={[10]={Team=101,Kind="srw_shield_bot"}}
data.srw.Shields={}; disabled=false
SRW.ScanShields(); local s=data.srw.Shields[10]
assert(s.Mobile and s.HP==5000 and #s.Arc==65)
assert(math.abs(s.Arc[1].y-150)<0.001 and math.abs(s.Arc[65].y-150)<0.001)
assert(math.abs(s.Arc[33].y+300)<0.001)
SRW.UpdateShieldPower(.04); assert(s.Active)
SRW_ShieldDeactivate(101,10); assert(s.Active,"manual control affected mobile shield")
local function shot(x,y,vx,vy,team)
 dead={}; data.srw.ShieldProjectiles={}
 projectilePos=Vec3(x,y,0); projectileVelocity=Vec3(vx,vy,0); projectileTeam=team
 SRW.InterceptShieldProjectiles(.04)
 return dead[100]
end
assert(shot(1400,0,-5000,0,102) and s.HP==4700)
assert(not shot(1400,0,-5000,0,201),"friendly projectile blocked")
assert(not shot(1000,400,0,-5000,102),"lower opening closed")
origin=Vec3(2000,0,0)
assert(not shot(1400,0,-5000,0,102),"shield stayed at old position")
assert(shot(2400,0,-5000,0,102),"shield did not follow robot")
disabled=true; SRW.UpdateShieldPower(.04); assert(not s.Active)
assert(not shot(2400,0,-5000,0,102))
disabled=false; SRW.UpdateShieldPower(.04); assert(s.Active)
SRW.ShieldDamage(s,10000); assert(s.HP==0 and not s.Active)
SRW.UpdateShieldPower(49); assert(s.HP==4900 and not s.Active)
SRW.UpdateShieldPower(1); SRW.UpdateShieldPower(.04); assert(s.HP==5000 and s.Active)
data.srw.Robots={}; SRW.ScanShields(); assert(not data.srw.Shields[10])
''')
print('PASS: mobile 240-degree shield, moving origin, friendly passage, bottom opening, EMP, recovery, cleanup')
