from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.14.0-rocket-bot','0.15.0-hunter-bot')
edit('scripts/config.lua','        srw_rocket_bot =','''        srw_hunter_bot = { Tier=2, ExitDelay=3, Health=1400, SpeedMinesPerSecond=2.4,
            MetalCost=350, EnergyCost=3000, ProductionSeconds=12, ActiveLimit=5,
            Range=2400, ReloadSeconds=2.2, BeamHoldSeconds=0.8 },
        srw_rocket_bot =''')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_rocket_bot" then','or bot.Kind=="srw_rocket_bot" or bot.Kind=="srw_hunter_bot" then')
edit('scripts/factories/squads.lua','"srw_laser_bot","srw_rocket_bot"}','"srw_laser_bot","srw_rocket_bot","srw_hunter_bot"}')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_hunter_bot", FileName=path.."/weapons/hunter_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=60, EnergyRepairCost=600,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
p=r/'weapons/projectile_list.lua'; s=p.read_text(); s+='''
clone("machinegun", "srw_hunter_bullet", {
    ProjectileDamage=65, WeaponDamageBonus=0, Gravity=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
    DamageMultiplier={},
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==7','#Weapons==8')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType10 = L"'+('+ Охотник II' if ru else '+ Hunter II')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_hunter_bot = L"'+('Охотник II' if ru else 'Hunter II')+'"\n'; p.write_text(s,encoding='utf-16')
