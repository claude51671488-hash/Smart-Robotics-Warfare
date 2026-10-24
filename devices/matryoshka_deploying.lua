-- Opening is a non-weapon device: native gun reload/aim states cannot
-- replace its animation with an already unfolded, turned turret.
dofile("devices/battery.lua")
HitPoints=500;Mass=100;ClaimsStructures=false;NoReclaim=true;Repairable=true
EnergyProductionRate=0;MetalProductionRate=0;EnergyStorageCapacity=0;MetalStorageCapacity=0
DeviceSplashDamage=0;StructureSplashDamage=0;IgnitePlatformOnDestruct=false
IncendiaryRadius=0;IncendiaryRadiusHeated=0
ConstructEffect="";CompleteEffect="";DestroyEffect="effects/machinegun_explode.lua"
local directory=path.."/ui/textures/weapons/matryoshka/"
dofile(directory.."geometry.lua")
local g=SRWMatryoshkaGeometry
local states={}
for _,side in ipairs({"Right","Left"}) do
 for i=0,47 do
  states["Deploy"..side..i]={Frames={{texture=directory.."opening_"..string.format("%02d",i).."_"..side:lower()..".png"},mipmap=true}}
 end
end
states.Normal=states.DeployRight0;states.Idle=states.Normal
Sprites={{Name="srw-matryoshka-opening",States=states}}
Scale=g.Scale;SelectionWidth=110;SelectionHeight=110;SelectionOffset={0,-55}
local scale=g.Scale/.375
Root={Name="MatryoshkaOpening",Angle=0,Scale=scale,
 Pivot={(.5-g.FootX/g.Width)*scale,(.5-g.FootY/g.Height)*scale},
 PivotOffset={0,0},Sprite="srw-matryoshka-opening",UserData=0}
