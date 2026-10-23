from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.16.0-bastion-bot','0.17.0-heavy-aa-bot')
edit('scripts/config.lua','        srw_bastion_bot =','''        srw_heavy_aa_bot = { Tier=3, ExitDelay=8, Health=2400, SpeedMinesPerSecond=1.1,
            MetalCost=800, EnergyCost=6500, ProductionSeconds=24, ActiveLimit=2,
            Range=4500, BulletSpeed=12000, FireInterval=0.35, FollowDistance=260,
            PrioritizeDamage=true },
        srw_bastion_bot =''')
edit('scripts/robots/movement.lua','elseif bot.Kind=="srw_aa_bot" then','elseif bot.Kind=="srw_aa_bot" or bot.Kind=="srw_heavy_aa_bot" then')
edit('scripts/factories/squads.lua','"srw_hunter_bot","srw_bastion_bot"}','"srw_hunter_bot","srw_bastion_bot","srw_heavy_aa_bot"}')
edit('scripts/robots/aa.lua','local cfg=SRW.Config.Robots.srw_aa_bot','local cfg=SRW.Config.Robots[bot.Kind or "srw_aa_bot"]')
edit('scripts/robots/aa.lua','if aim then targets[#targets+1]={Id=node,Aim=aim,Distance=distance,','''local threat=0
                    if cfg.PrioritizeDamage then
                        threat=GetProjectileParamFloat(name,NodeTeam(node),"ProjectileDamage",0)
                            +GetProjectileParamFloat(name,NodeTeam(node),"ProjectileSplashDamage",0)
                    end
                    if aim then targets[#targets+1]={Id=node,Aim=aim,Distance=distance,Threat=threat,''')
edit('scripts/robots/aa.lua','        if a.Distance~=b.Distance then','        if a.Threat~=b.Threat then return a.Threat>b.Threat end\n        if a.Distance~=b.Distance then')
edit('scripts/robots/aa.lua','r.Kind~="srw_aa_bot" and r.Kind~="srw_repair_bot"','r.Kind~="srw_aa_bot" and r.Kind~="srw_heavy_aa_bot" and r.Kind~="srw_shield_bot" and r.Kind~="srw_repair_bot"')
edit('scripts/robots/shield.lua','and candidate.Kind~="srw_aa_bot" then','and candidate.Kind~="srw_aa_bot" and candidate.Kind~="srw_heavy_aa_bot" then')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_heavy_aa_bot", FileName=path.."/weapons/heavy_aa_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=100, EnergyRepairCost=1000,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
p=r/'weapons/projectile_list.lua'; s=p.read_text(); s+='''
clone("machinegun", "srw_heavy_aa_bullet", {
    ProjectileDamage=20, AntiAirDamage=100, Gravity=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==9','#Weapons==10')
edit('tests/check_aa.py','#Projectiles==3','#Projectiles==4')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType12 = L"'+('+ Страж III' if ru else '+ Guardian III')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_heavy_aa_bot = L"'+('Страж III' if ru else 'Guardian III')+'"\n'; p.write_text(s,encoding='utf-16')
