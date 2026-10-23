from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.12.0-emp-bot','0.13.0-laser-bot')
edit('scripts/config.lua','        srw_emp_bot =','''        srw_laser_bot = { Tier=2, ExitDelay=3, Health=1100, SpeedMinesPerSecond=1.3,
            MetalCost=450, EnergyCost=4000, ProductionSeconds=16, ActiveLimit=3,
            Range=3300, ReloadSeconds=8, BeamHoldSeconds=2, PreferStructures=true },
        srw_emp_bot =''')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_emp_bot" then','or bot.Kind=="srw_emp_bot" or bot.Kind=="srw_laser_bot" then')
edit('scripts/robots/hound.lua','    local enemy=bot.Team%100==1 and 2 or 1','''    -- Freeze position and aim until the continuous beam and its firing delay finish.
    if (bot.BeamRemaining or 0)>0 then
        bot.BeamRemaining=math.max(0,bot.BeamRemaining-dt)
        bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
        return
    end
    local enemy=bot.Team%100==1 and 2 or 1''')
edit('scripts/robots/hound.lua','                bot.FireWait=result==','                if result==(FIRE_SUCCESS or 0) and cfg.BeamHoldSeconds then bot.BeamRemaining=cfg.BeamHoldSeconds end\n                bot.FireWait=result==')
edit('scripts/factories/squads.lua','"srw_shield_bot","srw_emp_bot"}','"srw_shield_bot","srw_emp_bot","srw_laser_bot"}')
edit('scripts/ui/squads.lua','20,525','20,565'); edit('scripts/ui/squads.lua','650,525','650,565')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_laser_bot", FileName=path.."/weapons/laser_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=60, EnergyRepairCost=600,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==5','#Weapons==6')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType8 = L"'+('+ Лучник II' if ru else '+ Laser walker II')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_laser_bot = L"'+('Лучник II' if ru else 'Laser walker II')+'"\n'; p.write_text(s,encoding='utf-16')
