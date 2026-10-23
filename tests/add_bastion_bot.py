from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.15.0-hunter-bot','0.16.0-bastion-bot')
edit('scripts/config.lua','        srw_hunter_bot =','''        srw_bastion_bot = { Tier=3, ExitDelay=8, Health=3500, SpeedMinesPerSecond=0.8,
            MetalCost=1000, EnergyCost=8000, ProductionSeconds=30, ActiveLimit=2,
            Range=4800, ReloadSeconds=6, PreferStructures=true,
            ShieldRadius=240, ShieldHP=6000, ShieldRegen=150 },
        srw_hunter_bot =''')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_hunter_bot" then','or bot.Kind=="srw_hunter_bot" or bot.Kind=="srw_bastion_bot" then')
edit('scripts/factories/squads.lua','"srw_rocket_bot","srw_hunter_bot"}','"srw_rocket_bot","srw_hunter_bot","srw_bastion_bot"}')
edit('scripts/robots/shield.lua','function SRW.NewMobileShield(team)\n    local cfg=SRW.Config.Robots.srw_shield_bot','function SRW.NewMobileShield(team,kind)\n    kind=kind or "srw_shield_bot"\n    local cfg=SRW.Config.Robots[kind]')
edit('scripts/robots/shield.lua','return {Team=team,HP=cfg.ShieldHP','return {Team=team,Kind=kind,HP=cfg.ShieldHP')
edit('scripts/robots/shield.lua','function SRW.UpdateMobileShield(id,s,dt)\n    local cfg=SRW.Config.Robots.srw_shield_bot','''function SRW.UpdateMobileShield(id,s,dt)
    local cfg=SRW.Config.Robots[s.Kind or "srw_shield_bot"]
    local bot=data.srw.Robots[id]
    s.EMPWeakened=(cfg.Tier or 1)>=3 and bot and (bot.EMPRemaining or 0)>0 or false''')
edit('scripts/robots/shield.lua','s.HP+cfg.ShieldRegen*dt','s.HP+cfg.ShieldRegen*dt*(s.EMPWeakened and 0.5 or 1)')
edit('scripts/shields.lua','if GetDeviceType(id)=="srw_shield_bot" and data.srw.Robots[id] then','if (GetDeviceType(id)=="srw_shield_bot" or GetDeviceType(id)=="srw_bastion_bot") and data.srw.Robots[id] then')
edit('scripts/shields.lua','SRW.NewMobileShield(team)','SRW.NewMobileShield(team,GetDeviceType(id))')
edit('scripts/shields.lua','(GetDeviceType(id)~="srw_shield_bot" or not data.srw.Robots[id]','((GetDeviceType(id)~="srw_shield_bot" and GetDeviceType(id)~="srw_bastion_bot") or not data.srw.Robots[id]')
edit('scripts/shields.lua','s.HP-math.max(0,damage)','s.HP-math.max(0,damage)*(s.EMPWeakened and 1.5 or 1)')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_bastion_bot", FileName=path.."/weapons/bastion_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=150, EnergyRepairCost=1500,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==8','#Weapons==9')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s=s.replace('Требуется фабрика II уровня','Недостаточный уровень фабрики').replace('Requires factory tier II','Factory tier is too low')
 s+='\nSRW_UI.SquadType11 = L"'+('+ Бастион III' if ru else '+ Bastion III')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_bastion_bot = L"'+('Бастион III' if ru else 'Bastion III')+'"\n'; p.write_text(s,encoding='utf-16')
