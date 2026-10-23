dofile("devices/battery.lua")
Sprites={}
Scale=900/1753
HitPoints=5000
Mass=1000
ClaimsStructures=false
NoReclaim=true
Repairable=true
SelectionWidth=876.5
SelectionHeight=197.5
SelectionOffset={0,-197.5}
EnergyStorageCapacity=0
MetalStorageCapacity=0
EnergyProductionRate=0
MetalProductionRate=0
DeviceSplashDamage=0
StructureSplashDamage=0
IncendiaryRadius=0
IncendiaryRadiusHeated=0
IgnitePlatformOnDestruct=false
NodeEffects={}
local dir=path.."/ui/textures/engineering/animated/"
local right={Frames={{texture=dir.."body.png"},mipmap=true}}
local left={Frames={{texture=dir.."body_left.png"},mipmap=true}}
if SRWBunkerBodyLeft then right=left end
Sprites={{Name="srw-field-bunker-body",States={Normal=right,Idle=right,Right=right,Left=left}}}
Root={Name="Bunker",Sprite="srw-field-bunker-body",Scale=Scale/.375,Pivot={0,-.5*Scale/.375},PivotOffset={0,0},Angle=0}
if SRWBunkerBodyLeft then Sprites[1].Name="srw-field-bunker-body-left";Root.Sprite=Sprites[1].Name end
SRWBunkerBodyLeft=nil
