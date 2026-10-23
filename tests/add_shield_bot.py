from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.10.0-squad-production','0.11.0-shield-bot')
edit('script.lua','dofile(path .. "/scripts/robots/repair.lua")','dofile(path .. "/scripts/robots/repair.lua")\ndofile(path .. "/scripts/robots/shield.lua")')
edit('scripts/config.lua','        srw_aa_bot =', '''        srw_shield_bot = { Tier=2, ExitDelay=3, Health=1000, SpeedMinesPerSecond=1.6,
            MetalCost=400, EnergyCost=3000, ProductionSeconds=15, ActiveLimit=3,
            FollowDistance=180, ShieldRadius=300, ShieldHP=5000, ShieldRegen=100 },
        srw_aa_bot =''')
edit('scripts/robots/repair.lua','function SRW.SpawnRepairBot(team,factory)','function SRW.SpawnRepairBot(team,factory,kind)\n    kind=kind or "srw_repair_bot"')
p=r/'scripts/robots/repair.lua'; s=p.read_text(); a,b=s.split('function SRW.UpdateRepairBot',1); a=a.replace('"srw_repair_bot",','kind,').replace('Kind="srw_repair_bot"','Kind=kind'); p.write_text(a+'function SRW.UpdateRepairBot'+b)
edit('scripts/robots/movement.lua','        elseif bot.Kind=="srw_repair_bot" then','        elseif bot.Kind=="srw_shield_bot" then\n            SRW.UpdateShieldBot(id,bot,dt)\n        elseif bot.Kind=="srw_repair_bot" then')
edit('scripts/factories/squads.lua','"srw_siege_bot","srw_aa_bot"}','"srw_siege_bot","srw_aa_bot","srw_shield_bot"}')
edit('scripts/factories/squads.lua','    if delta==1 then','    if delta==1 then\n        if (SRW.Config.Robots[kind].Tier or 1)>(f.Tier or 1) then f.Status="tier_required"; return end')
edit('scripts/factories/squads.lua','        counts[kind]=(counts[kind] or 0)+1','        if (cfg.Tier or 1)>(f.Tier or 1) then f.Status="tier_required"; return end\n        counts[kind]=(counts[kind] or 0)+1')
edit('scripts/factories/squads.lua','    elseif kind=="srw_repair_bot" then','    elseif kind=="srw_shield_bot" then success=SRW.SpawnShieldBot(f.Team,id)\n    elseif kind=="srw_repair_bot" then')
edit('scripts/ui/squads.lua','20,425','20,475'); edit('scripts/ui/squads.lua','650,425','650,475')
edit('scripts/shields.lua','            if GetDeviceType(id)=="srw_shield_generator" and IsDeviceFullyBuilt(id) then','''            if GetDeviceType(id)=="srw_shield_bot" and data.srw.Robots[id] then
                local team=GetDeviceTeamIdActual(id)
                if not shields[id] or shields[id].Team~=team then shields[id]=SRW.NewMobileShield(team) end
            end
            if GetDeviceType(id)=="srw_shield_generator" and IsDeviceFullyBuilt(id) then''')
edit('scripts/shields.lua','if not DeviceExists(id) or GetDeviceType(id)~="srw_shield_generator" then','if not DeviceExists(id) or (GetDeviceType(id)~="srw_shield_generator" and\n            (GetDeviceType(id)~="srw_shield_bot" or not data.srw.Robots[id] or data.srw.Robots[id].Team~=GetDeviceTeamIdActual(id))) then')
edit('scripts/shields.lua','    if s and DeviceExists(id)','    if s and not s.Mobile and DeviceExists(id)')
edit('scripts/shields.lua','        if DeviceDisabled(id) then s.Active=false; s.Status="disabled"','        if s.Mobile then SRW.UpdateMobileShield(id,s,dt)\n        elseif DeviceDisabled(id) then s.Active=false; s.Status="disabled"')
edit('scripts/ui/shield.lua','selected=s and s.Team==GetLocalTeamId() and id or nil','selected=s and not s.Mobile and s.Team==GetLocalTeamId() and id or nil')
edit('scripts/ui/shield.lua','shield.HP/SRW.Shield.MaxHP','shield.HP/(shield.MaxHP or SRW.Shield.MaxHP)')
p=r/'devices/shield_bot.lua'; p.write_text('dofile(path.."/devices/repair_bot.lua")\nScale=0.55\nHitPoints=1000\nMass=120\n')
p=r/'devices/device_list.lua'; s=p.read_text(); s+='''
RegisterSRWDevice({
    SaveName="srw_shield_bot", FileName=path.."/devices/shield_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, NoReclaim=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=50, EnergyRepairCost=500,
    SelectEffect="ui/hud/devices/ui_devices",
})
'''; p.write_text(s)
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 s+='\nSRW_UI.SquadType6 = L"'+('+ Щитоносец II' if ru else '+ Shield escort II')+'"\n'
 s+='SRW_UI.tier_required = L"'+('Требуется фабрика II уровня' if ru else 'Requires factory tier II')+'"\n'
 p.write_text(s,encoding='utf-16')
