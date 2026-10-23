from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.21.0-formation-ui','0.22.0-colossus-formation')
edit('scripts/config.lua','        srw_tank_bot =','''        srw_colossus_bot = { Tier=3, ExitDelay=8, Health=6000, SpeedMinesPerSecond=0.65,
            MetalCost=1600, EnergyCost=14000, ProductionSeconds=45, ActiveLimit=1,
            Range=4800, ReloadSeconds=6, PreferStructures=true, Spacing=280,
            ShieldRadius=320, ShieldHP=9000, ShieldRegen=180,
            Mounts={{Kind="srw_colossus_laser",X=0,Y=-85},
                {Kind="srw_tank_rockets",X=-65,Y=-125,AntiAir=true}} },
        srw_colossus_laser = { Tier=3, Range=3300, ReloadSeconds=8, BeamHoldSeconds=2 },
        srw_tank_bot =''')
edit('scripts/robots/tank.lua','function SRW.SpawnTank(team,factory)\n    local ok,root=SRW.SpawnHound(team,factory,"srw_tank_bot")','function SRW.SpawnTank(team,factory,kind)\n    kind=kind or "srw_tank_bot"\n    local ok,root=SRW.SpawnHound(team,factory,kind)')
edit('scripts/robots/tank.lua','for _,mount in ipairs({{Kind="srw_tank_turret",X=0,Y=-50},','for _,mount in ipairs(SRW.Config.Robots[kind].Mounts or {{Kind="srw_tank_turret",X=0,Y=-50},')
# A mounted laser also requires a stationary parent for the duration of its beam.
edit('scripts/robots/hound.lua','    if (bot.BeamRemaining or 0)>0 then','    if not bot.Mounted then\n        for _,part in pairs(data.srw.MountedWeapons or {}) do\n            if part.Root==id and part.Kind=="srw_colossus_laser" and (part.BeamRemaining or 0)>0 then return end\n        end\n    end\n    if (bot.BeamRemaining or 0)>0 then')
edit('scripts/robots/movement.lua','or bot.Kind=="srw_tank_bot" then','or bot.Kind=="srw_tank_bot" or bot.Kind=="srw_colossus_bot" then')
edit('scripts/factories/squads.lua','"srw_heavy_siege_bot","srw_tank_bot"}','"srw_heavy_siege_bot","srw_tank_bot","srw_colossus_bot"}')
edit('scripts/factories/squads.lua','elseif kind=="srw_tank_bot" then success=SRW.SpawnTank(f.Team,id)','elseif kind=="srw_tank_bot" or kind=="srw_colossus_bot" then success=SRW.SpawnTank(f.Team,id,kind)')
edit('scripts/shields.lua','or GetDeviceType(id)=="srw_bastion_bot")','or GetDeviceType(id)=="srw_bastion_bot" or GetDeviceType(id)=="srw_colossus_bot")')
edit('scripts/shields.lua','and GetDeviceType(id)~="srw_bastion_bot")','and GetDeviceType(id)~="srw_bastion_bot" and GetDeviceType(id)~="srw_colossus_bot")')
p=r/'weapons/weapon_list.lua'; s=p.read_text(); s+='''
for _,kind in ipairs({"srw_colossus_bot","srw_colossus_laser"}) do
    register({SaveName=kind, FileName=path.."/weapons/"..string.sub(kind,5)..".lua",
        Icon="srw-kega-icon", Detail="srw-kega-icon", Enabled=false, ExcludeUnlockAll=true,
        dlc2_BuildAnywhere=true, BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
        MetalCost=0, EnergyCost=0, MetalRepairCost=150, EnergyRepairCost=1500,
        MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons"})
end
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==14','#Weapons==16')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType15 = L"'+('+ Колосс III' if ru else '+ Colossus III')+'"\n'; p.write_text(s,encoding='utf-16')
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_colossus_bot = L"'+('Колосс III' if ru else 'Colossus III')+'"\n'
 s+='Weapon.srw_colossus_laser = L"'+('Лазер Колосса' if ru else 'Colossus laser')+'"\n'; p.write_text(s,encoding='utf-16')
