from pathlib import Path
r=Path(__file__).resolve().parents[1]
for name in ['scripts/factories/production.lua','scripts/factories/squads.lua']:
 p=r/name;s=p.read_text().replace('"srw_colossus_bot"}', '"srw_colossus_bot","srw_sentry_bot"}',1)
 s=s.replace('kind=="srw_tank_bot" or kind=="srw_colossus_bot"','kind=="srw_tank_bot" or kind=="srw_colossus_bot" or kind=="srw_sentry_bot"')
 p.write_text(s)
p=r/'scripts/combat/guidance.lua';s=p.read_text().replace('srw_tank_aa_rocket=true','srw_tank_aa_rocket=true,srw_sentry_rocket=true');p.write_text(s)
p=r/'weapons/projectile_list.lua';s=p.read_text()+'''
clone("srw_aa_bullet", "srw_sentry_bullet", {ProjectileDamage=25, AntiAirDamage=30})
clone("srw_tank_aa_rocket", "srw_sentry_rocket", {
    ProjectileDamage=15, AntiAirDamage=65,
})
''';p.write_text(s)
p=r/'weapons/weapon_list.lua';s=p.read_text()+'''
for _,kind in ipairs({"srw_sentry_bot","srw_sentry_rockets"}) do
    register({SaveName=kind,FileName=path.."/weapons/"..string.sub(kind,5)..".lua",
        Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,
        dlc2_BuildAnywhere=true,BuildOnGroundOnly=true,BuildTimeComplete=0.2,ScrapPeriod=0.2,
        MetalCost=0,EnergyCost=0,MetalRepairCost=50,EnergyRepairCost=500,
        MaxUpAngle=90,SelectEffect="ui/hud/weapons/ui_weapons"})
end
''';p.write_text(s)
p=r/'script.lua';s=p.read_text().replace('0.26.0-concept-names','0.27.0-sentry');s=s.replace('dofile(path .. "/scripts/robots/aa.lua")','dofile(path .. "/scripts/robots/aa.lua")\ndofile(path .. "/scripts/robots/sentry.lua")');p.write_text(s)
for lang in ['Russian','English']:
 base=r/f'mods/language-{lang}'; name='Караульный I' if lang=='Russian' else 'Watchman I'
 p=base/'srw_ui.lua';s=p.read_text(encoding='utf-16')+f'\nSRW_UI.SquadType16 = L"+ {name}"\nSRW_UI.SingleType16 = L"{name}"\n';p.write_text(s,encoding='utf-16')
 p=base/'weapons/strings.lua';s=p.read_text(encoding='utf-16')+f'\nWeapon.srw_sentry_bot = L"{name} [prototype]"\nWeapon.srw_sentry_rockets = L"{name}: AA"\n';p.write_text(s,encoding='utf-16')
for name in ['check_hound.py','check_kolokol.py']:
 p=r/'tests'/name;s=p.read_text().replace('#Weapons==16','#Weapons==18')
 if name=='check_kolokol.py':s=s.replace('#Projectiles==8','#Projectiles==9')
 p.write_text(s)
p=r/'tests/check_individual.py';s=p.read_text().replace('for i=6,#SRW.RobotKinds do','for i=6,15 do');p.write_text(s)
p=r/'tests/check_squads.py';s=p.read_text().replace('SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==1 and visible.srw_squad_add1)','SRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==4 and visible.srw_squad_add16)\nSRW.ClickUI("srw_squad_page"); assert(SRW.SquadPage==1 and visible.srw_squad_add1)');p.write_text(s)
