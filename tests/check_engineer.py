"""Distance placement, ownership, autonomous bunker, native loadout and asset provenance."""
from pathlib import Path
from zipfile import ZipFile
import runpy
r=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(r/'tests/check_hound.py'))['lua']
for name in ('robots/repair.lua','robots/engineer.lua','factories/squads.lua'):
    lua.execute((r/'scripts'/name).read_text())
lua.execute('''
assert(SRW.RobotKinds[30]=='srw_engineer_bot')
assert(not SRW.FactoryCanProduce({Tier=1},'srw_engineer_bot'))
assert(SRW.FactoryCanProduce({Tier=2},'srw_engineer_bot'))
assert(not SRW.FactoryCanProduce({Tier=2,Domain='air'},'srw_engineer_bot'))
function GetWorldExtents() return {MinX=-20000,MaxX=20000} end
function EnableWeapon() end
function EnableDevice() end
local serial=1000;local fail;local shots={};local noGround=false
function SRW.GroundAt(x,y,reach) if not noGround then return Vec3(x,0,0) end end
function SRW.MovementRay() return RAY_HIT_NOTHING end
function dlc2_CreateFloatingDevice(team,kind,p,angle)
 if kind:gsub('_left$','')==fail then return -1 end
 serial=serial+1;devices[serial]={team=team,kind=kind,pos=p,built=true,hp=5000};return serial
end
function GetDeviceHitpoints(id) return devices[id].hp end
function ApplyDamageToDevice(id,n)
 devices[id].hp=devices[id].hp-n;if devices[id].hp<=0 then devices[id]=nil end
end
function GetDeviceCountSide(side)
 local n=0;for _,d in pairs(devices) do if d.team%100==side then n=n+1 end end;return n
end
function GetDeviceIdSide(side,index)
 local ids={};for id,d in pairs(devices) do if d.team%100==side then ids[#ids+1]=id end end
 table.sort(ids);return ids[index+1]
end
function FireWeapon(id,p,e,f) shots[id]=(shots[id] or 0)+1;return 0 end
function SRW.BeamTargets() return {} end
for _,team in ipairs({101,102}) do
 devices={[50]={team=team,kind='srw_factory_ground_2',built=true,pos=Vec3(0,0,0)}}
 data.srw.Robots={};data.srw.MountedWeapons={};data.srw.FieldMines={};shots={}
 local ok,id=SRW.SpawnEngineer(team,50);assert(ok)
 local bot=data.srw.Robots[id];local dir=bot.Direction
 assert(bot.BunkerSpacing==10000 and bot.NextMine==2880)
 for i=1,10 do SRW.UpdateEngineer(id,bot,.04) end
 assert(not next(data.srw.FieldMines))
 devices[id].disabled=true;local p=devices[id].pos
 SRW.UpdateEngineer(id,bot,10);assert(devices[id].pos==p)
 devices[id].disabled=false
 devices[id].pos=Vec3(bot.StartX+dir*2900,0,0);bot.BuildWait=0
 SRW.UpdateEngineer(id,bot,.04);local mine=next(data.srw.FieldMines)
 assert(mine and data.srw.FieldMines[mine].Team==team)
 assert((devices[id].pos.x-devices[mine].pos.x)*dir==180)
 devices[id].pos=Vec3(bot.StartX,0,0);bot.BuildWait=0
 SRW.UpdateEngineer(id,bot,.04);assert(#SRW.SortedIds(data.srw.FieldMines)==1,'retreat duplicates mine')
 devices[id].pos=Vec3(bot.StartX+dir*10010,0,0);bot.BuildWait=0
 SRW.UpdateEngineer(id,bot,.04)
 local bunker;for k,b in pairs(data.srw.Robots) do if b.Stationary then bunker=k end end
 assert(bunker and #SRW.SortedIds(data.srw.MountedWeapons)==2)
 local nextBunker=bot.NextBunker;assert(nextBunker>20000)
 devices[id]=nil;data.srw.Robots[id]=nil
 local bp=devices[bunker].pos
 local enemy=team==101 and 102 or 101
 devices[9000]={team=enemy,kind='srw_hound',built=true,pos=Vec3(bp.x+dir*800,bp.y-200,0)}
 SRW.UpdateRobots(.04);SRW.UpdateMountedWeapons(.04)
 assert(devices[bunker].pos==bp,'stationary bunker moved')
 for child in pairs(data.srw.MountedWeapons) do assert(shots[child],'bunker gun never fired') end
 -- One shared 5000 HP pool, including hits on either turret.
 local gun=next(data.srw.MountedWeapons);devices[gun].hp=4500
 SRW.UpdateMountedWeapons(.04);assert(devices[bunker].hp==4500 and devices[gun].hp==5000)
 devices[gun].hp=4600;SRW.UpdateMountedWeapons(.04);assert(devices[bunker].hp==4100)
 devices[bunker]=nil;SRW.UpdateMountedWeapons(.04);assert(not next(data.srw.MountedWeapons))
 -- Allied presence, arming delay, enemy activation and latched fuse.
 local mp=devices[mine].pos
 devices[9000].pos=Vec3(mp.x+5000,0,0)
 devices[9001]={team=team,kind='srw_hound',built=true,pos=mp}
 SRW.UpdateFieldMines(2);assert(not data.srw.FieldMines[mine].FuseRemaining)
 devices[9000].pos=mp;SRW.UpdateFieldMines(.04);assert(data.srw.FieldMines[mine].FuseRemaining==.1)
 devices[9000].pos=Vec3(mp.x+5000,0,0);SRW.UpdateFieldMines(.11);assert(not devices[mine] and not data.srw.FieldMines[mine])
 -- Atomic rollback if second gun fails, and placement rejection on cliffs.
 data.srw.Robots={};data.srw.MountedWeapons={};fail='srw_bunker_machinegun'
 local before=GetDeviceCountSide(team%100)
 assert(not SRW.BuildFieldBunker(team,Vec3(20000,0,0),dir))
 assert(GetDeviceCountSide(team%100)==before and not next(data.srw.MountedWeapons))
 fail=nil;noGround=true;assert(not SRW.BuildFieldBunker(team,Vec3(20000,0,0),dir));noGround=false
end
''')
# Actual stock weapon inheritance, rather than mock numbers.
env=runpy.run_path(str(r/'tests/check_native_weapons.py'))['environment']
for kind,native in [('bunker_cannon','cannon'),('bunker_machinegun','machinegun')]:
    l,inc=env();inc('weapons/'+native+'.lua')
    before={k:l.globals()[k] for k in ('Projectile','ReloadTime','MinFireSpeed','MaxFireSpeed','MinFireRadius','MaxFireRadius','RoundsEachBurst','RoundPeriod')}
    inc('mod/weapons/'+kind+'.lua')
    for k,v in before.items():
        if k not in ('Projectile','MinFireSpeed','MaxFireSpeed'): assert l.globals()[k]==v,(kind,k)
    assert l.globals().MinFireSpeed==(12500 if native=='cannon' else 6500)
    assert l.globals().Projectile==('srw_bunker_shell' if native=='cannon' else 'srw_bunker_bullet')
l,inc=env();inc('mod/devices/robotics.lua')
l.execute('''
local names={};for _,s in ipairs(Sprites) do names[s.Name]=true end
local function check(n)
 if n.Sprite then assert(names[n.Sprite], 'robotics references an unregistered sprite: '..n.Sprite) end
 for _,key in ipairs({'Children','ChildrenInFront','ChildrenBehind'}) do
  for _,c in ipairs(n[key] or {}) do check(c) end
 end
end
check(Root)
''')
for n in range(1,51):
    with ZipFile(Path(r'C:\Users\pasha\Documents\Forts mods')/f'завод кадр {n}.kra') as z:
        assert (r/f'ui/textures/engineering/factory_{n:02}.png').read_bytes()==z.read('mergedimage.png')
with ZipFile(r'C:\Users\pasha\Pictures\готовый бункер.kra') as z:
    assert (r/'ui/textures/engineering/bunker.png').read_bytes()==z.read('mergedimage.png')
print('PASS: engineer both sides, distance milestones, EMP, persistence, both guns, shared HP, enemy-only fuse, rollback, native weapons and 51 exact Krita exports')
