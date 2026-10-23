-- Native explosion is temporary: layered damage and armour are not enabled yet.
dofile("devices/explosivebarrel.lua")
-- Approved two-legged orange capsule; each frame has the same transparent canvas.
Scale = 0.25
HitPoints = 4000
Mass = 100
ClaimsStructures = false
NoReclaim = true
Repairable = true
EnergyProductionRate = 0
MetalProductionRate = 0
EnergyStorageCapacity = 0
MetalStorageCapacity = 0
DeviceSplashDamage = 4000
DeviceSplashDamageMaxRadius = 796.875
StructureSplashDamage = 2400
StructureSplashDamageMaxRadius = 796.875
DeviceSplashDamageDelay = 0
IgnitePlatformOnDestruct = false
IncendiaryRadius = 0
IncendiaryRadiusHeated = 0
SelectionWidth = 180
SelectionHeight = 200
SelectionOffset = {0,-200}
DestroyEffect = path .. "/effects/dynamit_explode.lua"
local states={}
local function frames(name,first,last,left,duration)
    local result={duration=duration,mipmap=true,blendCoordinates=false}
    for i=first,last do
        result[#result+1]={texture=path.."/ui/textures/robots/dynamit/"..name.."_"..string.format("%02d",i)..(left and "_left" or "")..".png"}
    end
    return result
end
for _,left in ipairs({false,true}) do
    local side=left and "Left" or "Right"
    states["Run"..side]={Frames=frames("run_smooth",1,48,left,.44/2/48),NextState="Run"..side}
    for i=1,48 do states["Run"..side..i]={Frames=frames("run_smooth",i,i,left,1)} end
    states["Idle"..side]={Frames=frames("detonation",1,1,left,1)}
    states["Armed"..side]={Frames=frames("detonation",2,2,left,.1)}
end
states.Normal=states.RunRight
states.Idle=states.IdleRight
Sprites={{Name="srw-dynamit-body",States=states}}
Root={Name="barrel",Angle=0,Pivot={0,-.45},PivotOffset={0,0},
    Sprite="srw-dynamit-body",UserData=100}
