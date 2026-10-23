from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.18.0-heavy-siege-bot','0.19.0-tank-bot')
edit('script.lua','dofile(path .. "/scripts/robots/hound.lua")','dofile(path .. "/scripts/robots/hound.lua")\ndofile(path .. "/scripts/robots/tank.lua")')
edit('script.lua','    SRW.UpdateRobots(0.04)','    SRW.UpdateRobots(0.04)\n    SRW.UpdateMountedWeapons(0.04)')
edit('scripts/state.lua','    state.Robots =','    state.MountedWeapons = state.MountedWeapons or {}\n    state.Robots =')
edit('scripts/robots/hound.lua','    return true\nend','    return true,id\nend')
edit('scripts/robots/hound.lua','    bot.Target=nil\n    local direction=','    bot.Target=nil\n    if bot.Mounted then return end\n    local direction=')
edit('scripts/config.lua','        srw_heavy_siege_bot =','''        srw_tank_bot = { Tier=2, ExitDelay=5, Health=2000, SpeedMinesPerSecond=1.2,
            MetalCost=750, EnergyCost=6000, ProductionSeconds=25, ActiveLimit=3,
            Range=3300, ReloadSeconds=8, BeamHoldSeconds=2, PreferStructures=true },
        srw_tank_turret = { Tier=2, Range=2200, ReloadSeconds=2.2, BeamHoldSeconds=0.8 },
        srw_heavy_siege_bot =''')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_heavy_siege_bot" then','or bot.Kind=="srw_heavy_siege_bot" or bot.Kind=="srw_tank_bot" then')
edit('scripts/factories/squads.lua','"srw_heavy_aa_bot","srw_heavy_siege_bot"}','"srw_heavy_aa_bot","srw_heavy_siege_bot","srw_tank_bot"}')
edit('scripts/factories/squads.lua','    elseif kind=="srw_shield_bot" then','    elseif kind=="srw_tank_bot" then success=SRW.SpawnTank(f.Team,id)\n    elseif kind=="srw_shield_bot" then')
edit('scripts/combat/emp.lua','local bot=data.srw.Robots[id]','local bot=data.srw.Robots[id] or (data.srw.MountedWeapons and data.srw.MountedWeapons[id])')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
for _,kind in ipairs({"srw_tank_bot","srw_tank_turret"}) do
    register({
        SaveName=kind, FileName=path.."/weapons/"..(kind=="srw_tank_bot" and "tank_bot" or "tank_turret")..".lua",
        Icon="srw-kega-icon", Detail="srw-kega-icon",
        Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
        BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
        MetalCost=0, EnergyCost=0, MetalRepairCost=80, EnergyRepairCost=800,
        MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
    })
end
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==11','#Weapons==13')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType14 = L"'+('+ Танк II' if ru else '+ Tank II')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_tank_bot = L"'+('Танк II' if ru else 'Tank II')+'"\n'
 s+='Weapon.srw_tank_turret = L"'+('Автопушка танка' if ru else 'Tank autocannon')+'"\n'; p.write_text(s,encoding='utf-16')
