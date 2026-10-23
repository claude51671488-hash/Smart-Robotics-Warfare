-- Shared temporary artwork supplied by the author.
local placeholderExists = false
for _, sprite in ipairs(Sprites) do
    if sprite.Name == "srw-kega-icon" then placeholderExists = true end
end
if not placeholderExists then
    local states = {}
    for _, state in ipairs({"Normal", "Rollover", "Pressed", "Disabled"}) do
        states[state] = { Frames = {{ texture = path .. "/ui/textures/HUD/kega.png" }} }
    end
    table.insert(Sprites, { Name = "srw-kega-icon", States = states })
end

-- Registration may run more than once; preserve existing entries and other mods.
local function RegisterSRWDevice(definition)
    for _, device in ipairs(Devices) do
        if device.SaveName == definition.SaveName then return end
    end
    table.insert(Devices, definition)
end


RegisterSRWDevice(
{
    SaveName = "srw_factory_ground_1",
    FileName = path .. "/devices/factory_ground_1.lua",
    Icon = "srw-kega-icon", Detail = "srw-kega-icon",
    Prerequisite = "factory",
    PopulationCap = 1,
    Upgrades = { srw_factory_ground_2 = { Enabled=true, SaveName="srw_factory_ground_2", MetalCost=500, EnergyCost=3500 } },
    BuildTimeComplete = 15, ScrapPeriod = 8,
    MetalCost = 300, EnergyCost = 2000,
    MetalRepairCost = 150, EnergyRepairCost = 1000,
    BuildOnGroundOnly = true, BuildOnOreOnly = false,
    MaxUpAngle = 15, AlignToCursorNormal = false,
    SelectEffect = "ui/hud/devices/ui_devices",
})

RegisterSRWDevice(
{
    SaveName = "srw_shield_generator",
    PopulationCap=2,
    Upgrades={srw_shield_generator_2={Enabled=true,SaveName="srw_shield_generator_2",MetalCost=3000,EnergyCost=15000}},
    FileName = path .. "/devices/shield_generator.lua",
    Icon = "srw-kega-icon", Detail = "srw-kega-icon",
    BuildTimeComplete = 30, ScrapPeriod = 8,
    MetalCost = 3000, EnergyCost = 10000,
    MetalRepairCost = 1500, EnergyRepairCost = 5000,
    BuildOnGroundOnly = false, MaxUpAngle = 45,
    SelectEffect = "ui/hud/devices/ui_devices",
})

RegisterSRWDevice(
{
    SaveName = "srw_dynamit_bot",
    FileName = path .. "/devices/dynamit_bot.lua",
    Icon = "srw-kega-icon", Detail = "srw-kega-icon",
    Enabled = false, dlc2_BuildAnywhere = true,
    BuildTimeComplete = 0.1, ScrapPeriod = 0.1,
    MetalCost = 0, EnergyCost = 0, MetalRepairCost = 0, EnergyRepairCost = 0,
    -- Floating devices use ground-device attachment, not a supporting beam.
    NoReclaim = true, BuildOnGroundOnly = true,
    SelectEffect = "ui/hud/devices/ui_devices",
})

RegisterSRWDevice({
    SaveName="srw_repair_bot", FileName=path.."/devices/repair_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, NoReclaim=true,
    BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=30, EnergyRepairCost=300,
    SelectEffect="ui/hud/devices/ui_devices",
})

for tier=2,3 do
    local definition={
        SaveName="srw_factory_ground_"..tier,
        FileName=path.."/devices/factory_ground_"..tier..".lua",
        Icon="srw-kega-icon", Detail="srw-kega-icon",
        Enabled=false, ExcludeUnlockAll=true, PopulationCap=1,
        BuildTimeComplete=tier==2 and 20 or 30, ScrapPeriod=8,
        MetalCost=tier==2 and 800 or 1600, EnergyCost=tier==2 and 5500 or 11500,
        MetalRepairCost=150, EnergyRepairCost=1000,
        BuildOnGroundOnly=true, BuildOnOreOnly=false,
        MaxUpAngle=15, AlignToCursorNormal=false,
        SelectEffect="ui/hud/devices/ui_devices",
    }
    if tier==2 then
        definition.Upgrades={srw_factory_ground_3={Enabled=true, SaveName="srw_factory_ground_3", MetalCost=800, EnergyCost=6000}}
    end
    RegisterSRWDevice(definition)
end

RegisterSRWDevice({
    SaveName="srw_shield_bot", FileName=path.."/devices/shield_bot.lua",
    Icon="srw-kega-icon", Detail="srw-kega-icon",
    Enabled=false, ExcludeUnlockAll=true, dlc2_BuildAnywhere=true,
    BuildOnGroundOnly=true, NoReclaim=true, BuildTimeComplete=0.2, ScrapPeriod=0.2,
    MetalCost=0, EnergyCost=0, MetalRepairCost=50, EnergyRepairCost=500,
    SelectEffect="ui/hud/devices/ui_devices",
})

for tier=2,3 do
 local d={SaveName="srw_shield_generator_"..tier,FileName=path.."/devices/shield_generator.lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,PopulationCap=2,
 BuildTimeComplete=tier==2 and 23 or 60,ScrapPeriod=8,MetalCost=tier==2 and 6000 or 11000,
 EnergyCost=tier==2 and 25000 or 45000,MetalRepairCost=1500,EnergyRepairCost=5000,
 BuildOnGroundOnly=false,MaxUpAngle=45,SelectEffect="ui/hud/devices/ui_devices"}
 if tier==2 then d.Upgrades={srw_shield_generator_3={Enabled=true,SaveName="srw_shield_generator_3",MetalCost=5000,EnergyCost=20000}} end
 RegisterSRWDevice(d)
end

RegisterSRWDevice({SaveName="srw_robotics",FileName=path.."/devices/robotics.lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Prerequisite="factory",Tech=true,
 BuildTimeComplete=30,ScrapPeriod=10,MetalCost=800,EnergyCost=8000,
 MetalRepairCost=100,EnergyRepairCost=1000,MaxUpAngle=45,BuildOnGroundOnly=false,
 SelectEffect="ui/hud/technology/ui_technology",PopulationCap=1,ObserverBuildEvent=true})
RegisterSRWDevice({SaveName="srw_factory_air_1",FileName=path.."/devices/factory_air_1.lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Prerequisite="srw_robotics",PopulationCap=1,
 Upgrades={srw_factory_air_2={Enabled=true,SaveName="srw_factory_air_2",MetalCost=1000,EnergyCost=8000}},
 BuildTimeComplete=20,ScrapPeriod=8,MetalCost=500,EnergyCost=4000,
 MetalRepairCost=150,EnergyRepairCost=1000,MaxUpAngle=15,BuildOnGroundOnly=false,
 SelectEffect="ui/hud/devices/ui_devices"})


RegisterSRWDevice({SaveName="srw_factory_air_2",FileName=path.."/devices/factory_air_2.lua",
 Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,PopulationCap=1,
 BuildTimeComplete=30,ScrapPeriod=8,MetalCost=1500,EnergyCost=12000,
 MetalRepairCost=300,EnergyRepairCost=2000,MaxUpAngle=15,BuildOnGroundOnly=false,
 SelectEffect="ui/hud/devices/ui_devices"})

local artFound=false
for _,s in ipairs(Sprites) do if s.Name=="srw-factory-animation" then artFound=true end end
if not artFound then
    local frames={duration=.08,mipmap=true,blendColour=false,blendCoordinates=false}
    for i=1,50 do frames[#frames+1]={texture=path.."/ui/textures/engineering/factory_"..string.format("%02d",i)..".png"} end
    table.insert(Sprites,{Name="srw-factory-animation",States={
        Normal={Frames=frames,NextState="Normal"},
        Idle={Frames={{texture=path.."/ui/textures/engineering/factory_01.png"},mipmap=true}}}})
end
for _,name in ipairs({"engineer_bot","field_bunker","field_bunker_left","field_mine"}) do
    RegisterSRWDevice({SaveName="srw_"..name,FileName=path.."/devices/"..name..".lua",
        Icon="srw-kega-icon",Detail="srw-kega-icon",Enabled=false,ExcludeUnlockAll=true,
        dlc2_BuildAnywhere=true,BuildOnGroundOnly=true,NoReclaim=true,
        BuildTimeComplete=.2,ScrapPeriod=.2,MetalCost=0,EnergyCost=0,
        MetalRepairCost=50,EnergyRepairCost=500,SelectEffect="ui/hud/devices/ui_devices"})
end
