dofile("devices/factory.lua")
-- Own names are required: the native factory's sprites are not guaranteed to
-- be registered before this technology is loaded in every mod combination.
local spriteNames={}
for _,sprite in ipairs(Sprites) do
    local old=sprite.Name
    sprite.Name="srw-robotics-"..old
    spriteNames[old]=sprite.Name
end
local function renameNode(node)
    if node.Sprite and spriteNames[node.Sprite] then node.Sprite=spriteNames[node.Sprite] end
    for _,key in ipairs({"Children","ChildrenInFront","ChildrenBehind"}) do
        for _,child in ipairs(node[key] or {}) do renameNode(child) end
    end
end
renameNode(Root)
Scale=1
Mass=400
HitPoints=1000
EnergyProductionRate=-350
MetalProductionRate=-8
EnergyStorageCapacity=0
MetalStorageCapacity=0
MinWindEfficiency=1
MaxWindHeight=0
MaxRotationalSpeed=0
DrawBracket=false
DrawBehindTerrain=true
NoReclaim=false
TeamOwned=true
IgnitePlatformOnDestruct=true
