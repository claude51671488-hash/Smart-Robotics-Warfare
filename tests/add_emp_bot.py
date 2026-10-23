from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.11.0-shield-bot','0.12.0-emp-bot')
edit('script.lua','dofile(path .. "/scripts/config.lua")','dofile(path .. "/scripts/config.lua")\ndofile(path .. "/scripts/combat/emp.lua")')
edit('script.lua','    SRW.UpdateRobots(0.04)','    SRW.UpdateEMP(0.04)\n    SRW.UpdateRobots(0.04)')
p=r/'script.lua'; s=p.read_text(); s+='\nfunction OnProjectileDestroyed(nodeId,teamId,saveName,structureIdHit,destroyType)\n    SRW.EMPImpact(nodeId,teamId,saveName,destroyType)\nend\n'; p.write_text(s)
edit('scripts/config.lua','        srw_shield_bot =','''        srw_emp_bot = { Tier=2, ExitDelay=3, Health=850, SpeedMinesPerSecond=1.8,
            MetalCost=300, EnergyCost=3000, ProductionSeconds=12, ActiveLimit=3,
            Range=2800, ReloadSeconds=6, EMPRadius=240, EMPSeconds=5 },
        srw_shield_bot =''')
edit('scripts/config.lua','srw_aa_bot = { ExitDelay','srw_aa_bot = { Tier=2, ExitDelay')
edit('scripts/robots/movement.lua','bot.Kind=="srw_hound" or bot.Kind=="srw_siege_bot"','bot.Kind=="srw_hound" or bot.Kind=="srw_siege_bot" or bot.Kind=="srw_emp_bot"')
edit('scripts/robots/hound.lua','local result=FireWeapon(id,target.Position,0.2,FIREFLAG_NORMAL)','local aim=SRW.EMPAim and SRW.EMPAim(id,bot,target.Position) or target.Position\n                local result=FireWeapon(id,aim,0.2,FIREFLAG_NORMAL)')
edit('scripts/robots/aa.lua','FireWeapon(id,target.Aim,0.1,FIREFLAG_NORMAL)','local aim=SRW.EMPAim and SRW.EMPAim(id,bot,target.Aim) or target.Aim\n            FireWeapon(id,aim,0.1,FIREFLAG_NORMAL)')
edit('scripts/factories/squads.lua','"srw_aa_bot","srw_shield_bot"}','"srw_aa_bot","srw_shield_bot","srw_emp_bot"}')
edit('scripts/ui/squads.lua','20,475','20,525'); edit('scripts/ui/squads.lua','650,475','650,525')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
register({
    SaveName="srw_emp_bot", FileName=path.."/weapons/emp_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=40, EnergyRepairCost=400,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
'''; p.write_text(s)
p=r/'weapons/projectile_list.lua'; s=p.read_text(); s+='''
-- Script applies tier-specific EMP at confirmed contact. No native area EMP:
-- that would fully disable tier-II robots before their partial debuff applies.
clone("cannon", "srw_emp_shell", {
    ProjectileDamage=1, ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
    Gravity=0, ExplodeOnTouch=true, DestroyShields=false,
    ProjectileSplashMaxForce=0, MomentumThreshold={}, DamageMultiplier={},
    EMPRadius=0, EMPDuration=0, SRWShieldDamage=500,
})
'''; p.write_text(s)
edit('tests/check_hound.py','#Weapons==4','#Weapons==5')
edit('tests/check_hound.py','#Projectiles==2','#Projectiles==3')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType7 = L"'+('+ Подавитель II' if ru else '+ EMP suppressor II')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_emp_bot = L"'+('Подавитель II' if ru else 'EMP suppressor II')+'"\n'; p.write_text(s,encoding='utf-16')
