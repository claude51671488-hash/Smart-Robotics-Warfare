-- Append srw_ weapons to the existing Weapons table here.
Sprites=Sprites or {}
local hasKolokolIcon=false
for _,sprite in ipairs(Sprites) do if sprite.Name=="srw-kolokol-icon" then hasKolokolIcon=true end end
if not hasKolokolIcon then
    local state={Frames={{texture=path.."/ui/textures/weapons/kolokol/icon.png"},mipmap=true}}
    table.insert(Sprites,{Name="srw-kolokol-icon",States={Normal=state,Idle=state,
        Rollover=state,Pressed=state,Disabled=state}})
end
local function register(definition)
    for _, weapon in ipairs(Weapons) do
        if weapon.SaveName == definition.SaveName then return end
    end
    table.insert(Weapons, definition)
end
register({
    SaveName="srw_hound", FileName=path.."/weapons/hound.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=0, EnergyRepairCost=0,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_kolokol", FileName=path.."/weapons/kolokol.lua",
    Icon="srw-kolokol-icon", Detail="srw-kolokol-icon", GroupButton="srw-kolokol-icon",
    Enabled=true, Prerequisite="workshop",
    BuildTimeComplete=20, ScrapPeriod=10,
    MetalCost=350, EnergyCost=2200, MetalRepairCost=70, EnergyRepairCost=1000,
    MaxSpotterAssistance=1, MaxUpAngle=StandardMaxUpAngle,
    BuildOnGroundOnly=false, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_siege_bot", FileName=path.."/weapons/siege_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=50, EnergyRepairCost=500,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})
register({
    SaveName="srw_aa_bot", FileName=path.."/weapons/aa_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=40, EnergyRepairCost=400,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_emp_bot", FileName=path.."/weapons/emp_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=40, EnergyRepairCost=400,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_laser_bot", FileName=path.."/weapons/laser_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=60, EnergyRepairCost=600,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_rocket_bot", FileName=path.."/weapons/rocket_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=50, EnergyRepairCost=500,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_hunter_bot", FileName=path.."/weapons/hunter_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=60, EnergyRepairCost=600,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_bastion_bot", FileName=path.."/weapons/bastion_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=150, EnergyRepairCost=1500,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_heavy_aa_bot", FileName=path.."/weapons/heavy_aa_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=100, EnergyRepairCost=1000,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

register({
    SaveName="srw_heavy_siege_bot", FileName=path.."/weapons/heavy_siege_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=120, EnergyRepairCost=1200,
    MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
})

for _,kind in ipairs({"srw_tank_bot","srw_tank_turret","srw_tank_rockets"}) do
    register({
        SaveName=kind, FileName=path.."/weapons/"..string.sub(kind,5)..".lua",
        Icon="srw-kega-icon", Detail="srw-kega-icon",
        Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
        BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
        MetalCost=0, EnergyCost=0, MetalRepairCost=80, EnergyRepairCost=800,
        MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons",
    })
end

for _,kind in ipairs({"srw_colossus_bot","srw_colossus_laser"}) do
    register({SaveName=kind, FileName=path.."/weapons/"..string.sub(kind,5)..".lua",
        Icon="srw-kega-icon", Detail="srw-kega-icon", Enabled=false, ExcludeUnlockAll=true,
        dlc2_BuildAnywhere=true, BuildOnGroundOnly=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
        MetalCost=0, EnergyCost=0, MetalRepairCost=150, EnergyRepairCost=1500,
        MaxUpAngle=90, SelectEffect="ui/hud/weapons/ui_weapons"})
end

for _,kind in ipairs({"srw_sentry_bot","srw_sentry_rockets","srw_hound_machinegun","srw_hunter_rockets","srw_hunter_interceptor","srw_psalm_turret","srw_smith_bot","srw_smith_flame","srw_smith_rockets","srw_sieve_turret","srw_pike_bot","srw_pike_turret","srw_emp_turret","srw_regent_rockets","srw_regent_turret","srw_executioner_bot","srw_executioner_gun","srw_executioner_rockets","srw_storm_bot","srw_storm_rockets","srw_storm_interceptor","srw_heavy_aa_gun","srw_heavy_aa_rockets","srw_heavy_aa_defence"}) do
    register({SaveName=kind,FileName=path.."/weapons/"..string.sub(kind,5)..".lua",
        Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,
        dlc2_BuildAnywhere=true,BuildOnGroundOnly=true,BuildTimeComplete=0.2,ScrapPeriod=0.2,
        MetalCost=0,EnergyCost=0,MetalRepairCost=50,EnergyRepairCost=500,
        MaxUpAngle=90,SelectEffect="ui/hud/weapons/ui_weapons"})
end

for _,name in ipairs({"vault_bot","vault_gun","vault_laser","vault_rockets","censer_mortar","censer_laser","tempest_bot","tempest_gun","tempest_defence","mlrs_bot","mlrs_launcher","mlrs_defence"}) do
 register({SaveName="srw_"..name,FileName=path.."/weapons/"..name..".lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,
 dlc2_BuildAnywhere=true,BuildOnGroundOnly=true,BuildTimeComplete=.2,ScrapPeriod=.2,
 MetalCost=0,EnergyCost=0,MetalRepairCost=50,EnergyRepairCost=500,MaxUpAngle=90,
 SelectEffect="ui/hud/weapons/ui_weapons"})
end

for _,kind in ipairs({"hornet_bot","hornet_rockets","sledge_bot","skat_bot","skat_rockets","lantern_bot","parcel_bot","archangel_bot","archangel_turret","archangel_rockets"}) do
 register({SaveName="srw_"..kind,FileName=path.."/weapons/"..kind..".lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,
 dlc2_BuildAnywhere=true,BuildOnGroundOnly=true,BuildTimeComplete=.2,ScrapPeriod=.2,
 MetalCost=0,EnergyCost=0,MetalRepairCost=0,EnergyRepairCost=0,MaxUpAngle=90,
 SelectEffect="ui/hud/weapons/ui_weapons"})
end

for _,kind in ipairs({"bunker_cannon","bunker_machinegun","bunker_cannon_left","bunker_machinegun_left"}) do
 register({SaveName="srw_"..kind,FileName=path.."/weapons/"..kind..".lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,
 dlc2_BuildAnywhere=true,BuildOnGroundOnly=true,BuildTimeComplete=.2,ScrapPeriod=.2,
 MetalCost=0,EnergyCost=0,MetalRepairCost=0,EnergyRepairCost=0,MaxUpAngle=90,
 SelectEffect="ui/hud/weapons/ui_weapons"})
end
