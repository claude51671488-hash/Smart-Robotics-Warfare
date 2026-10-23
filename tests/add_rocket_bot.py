from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.13.0-laser-bot','0.14.0-rocket-bot')
edit('scripts/config.lua','        srw_laser_bot =','''        srw_rocket_bot = { Tier=2, ExitDelay=3, Health=1000, SpeedMinesPerSecond=1.4,
            MetalCost=400, EnergyCost=3500, ProductionSeconds=14, ActiveLimit=3,
            Range=4000, ReloadSeconds=10, BeamHoldSeconds=1.5, PreferStructures=true },
        srw_laser_bot =''')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_laser_bot" then','or bot.Kind=="srw_laser_bot" or bot.Kind=="srw_rocket_bot" then')
edit('scripts/factories/squads.lua','"srw_emp_bot","srw_laser_bot"}','"srw_emp_bot","srw_laser_bot","srw_rocket_bot"}')
# Keep all nine rows above the usual bottom HUD. Page layout will replace this as the roster grows.
edit('scripts/ui/squads.lua','20,565','20,595'); edit('scripts/ui/squads.lua','650,565','650,595')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_rocket_bot", FileName=path.."/weapons/rocket_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=50, EnergyRepairCost=500,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
p=r/'weapons/projectile_list.lua'; s=p.read_text(); s+='''
-- Use vanilla missile artwork/effects, but an unguided ballistic projectile.
-- No dependency on the optional weapon_pack mod and no spotter required.
clone("missile", "srw_salvo_rocket", {
    ProjectileType="bullet", Missile={}, Gravity=0, ProjectileDrag=0,
    ProjectileDamage=80, ProjectileSplashDamage=120, ProjectileSplashDamageMaxRadius=180,
    ProjectileSplashMaxForce=15000, ProjectileIncendiary=false,
    IgnitesBackgroundMaterials=false, IgnitesBackgroundMaterialsPassing=false,
    ExplodeOnTouch=true, MaxAge=4, EMPSensitivity=0, DamageMultiplier={},
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==6','#Weapons==7')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType9 = L"'+('+ Залповик II' if ru else '+ Rocket salvo II')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_rocket_bot = L"'+('Залповик II' if ru else 'Rocket salvo II')+'"\n'; p.write_text(s,encoding='utf-16')
