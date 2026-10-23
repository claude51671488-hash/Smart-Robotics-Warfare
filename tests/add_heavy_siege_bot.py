from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.17.0-heavy-aa-bot','0.18.0-heavy-siege-bot')
edit('scripts/config.lua','        srw_heavy_aa_bot =','''        srw_heavy_siege_bot = { Tier=3, ExitDelay=8, Health=2200, SpeedMinesPerSecond=0.7,
            MetalCost=1100, EnergyCost=9000, ProductionSeconds=35, ActiveLimit=2,
            Range=7000, MinimumRange=1000, ReloadSeconds=12, PreferStructures=true },
        srw_heavy_aa_bot =''')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_bastion_bot" then','or bot.Kind=="srw_bastion_bot" or bot.Kind=="srw_heavy_siege_bot" then')
edit('scripts/factories/squads.lua','"srw_bastion_bot","srw_heavy_aa_bot"}','"srw_bastion_bot","srw_heavy_aa_bot","srw_heavy_siege_bot"}')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_heavy_siege_bot", FileName=path.."/weapons/heavy_siege_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=120, EnergyRepairCost=1200,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
p=r/'weapons/projectile_list.lua'; s=p.read_text(); s+='''
clone("mortar2", "srw_heavy_siege_he", {
    ProjectileDamage=200, ProjectileSplashDamage=650,
    ProjectileSplashDamageMaxRadius=300, DisableShields=false,
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==10','#Weapons==11')
edit('tests/check_kolokol.py','#Projectiles==7','#Projectiles==8')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType13 = L"'+('+ Гром III' if ru else '+ Thunder III')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_heavy_siege_bot = L"'+('Гром III' if ru else 'Thunder III')+'"\n'; p.write_text(s,encoding='utf-16')
