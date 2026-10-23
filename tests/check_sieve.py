from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_aa.py'))['lua']
lua.execute("""
devices={[900]={team=101,kind="srw_aa_bot",built=true,pos=Vec3(0,0,0)},
 [901]={team=101,kind="srw_sieve_turret",built=true,pos=Vec3(30,-55,0)}}
data.srw.Robots={[900]={Team=101,Kind="srw_aa_bot",Direction=1}}
data.srw.MountedWeapons={[901]={Team=101,Root=900,Kind="srw_sieve_turret",Direction=1,Mounted=true,AntiAir=true}}
local enemy=102; local name="srw_sieve_flak";local shots={};local fuse
function NodeExists(id) return true end
function NodeTeam(id) return id==3000 and enemy or 101 end
function NodePosition(id) return id==3000 and Vec3(3000,-500,0) or Vec3(0,0,0) end
function NodeVelocity(id) return id==3000 and Vec3(-1000,0,0) or Vec3(10000,0,0) end
function GetNodeProjectileSaveName(id) return id==3000 and "mortar2" or name end
function GetProjectileParamFloat() return 15 end
function FireWeapon(id,p,e,flags) shots[id]=(shots[id] or 0)+1;return 0 end
function SetNodeProjectileAgeTrigger(id,t) fuse=t end
SRW.UpdateAABot(900,data.srw.Robots[900],.04);SRW.UpdateMountedWeapons(.04)
assert(shots[900]==1 and shots[901]==1)
SRW.SieveLaunch(101,900,4000);assert(fuse>.25 and fuse<.31)
fuse=nil;SRW.SieveLaunch(102,900,4000);assert(fuse==nil)
name="cannon";SRW.SieveLaunch(101,900,4000);assert(fuse==nil)
name="srw_sieve_flak";enemy=101;SRW.SieveLaunch(101,901,4000);assert(fuse==.6)
local flak,fragment
for _,p in ipairs(Projectiles) do
 if p.SaveName=="srw_sieve_flak" then flak=p end
 if p.SaveName=="srw_sieve_fragment" then fragment=p end
end
assert(flak.Effects.Age.t200.Terminate and flak.Effects.Age.t200.Projectile.Type=="srw_sieve_fragment")
assert(fragment.AntiAirDamage==40 and fragment.MaxAge==.06)
""")
print('PASS: twin AA fire, moving-target fuse, ownership/non-flak isolation, lost target fallback and bounded fragments')
