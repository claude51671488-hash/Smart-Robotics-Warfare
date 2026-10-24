-- Fixed connected support/housing; one native elevating and recoiling barrel.
local directory=path.."/ui/textures/weapons/matryoshka/"
dofile(directory.."geometry.lua")
local g=SRWMatryoshkaGeometry
local function still(name) return {Frames={{texture=directory..name..".png"},mipmap=true}} end
local body,gun,hidden={},{},{}
local empty=still("empty")
-- Native reload/idle transitions use the identical two parts, never a gun
-- baked into Root or an image of the whole turret facing to the right.
for _,state in ipairs({"Normal","Idle","Reload","ReloadEnd","Ready"}) do
    body[state]=still("ready_right");gun[state]=still("ready_barrel_right");hidden[state]=empty
end
Sprites={{Name="srw-matryoshka-base",States=body},
    {Name="srw-matryoshka-barrel",States=gun},
    {Name="srw-matryoshka-pivot",States=hidden}}
Scale=g.Scale
SelectionWidth=110;SelectionHeight=110;SelectionOffset={0,-55}
BarrelLength=0;BarrelRecoilLimit=-.02;BarrelRecoilSpeed=-.5;BarrelReturnForce=.12
local scale=g.Scale/.375
Root={Name="MatryoshkaFixedBase",Angle=0,Scale=scale,
    Pivot={(.5-g.FootX/g.Width)*scale,(.5-g.FootY/g.Height)*scale},
    PivotOffset={0,0},Sprite="srw-matryoshka-base",UserData=0,
    ChildrenInFront={{Name="Head",Angle=0,
        Pivot={g.JointX/g.Width-.5,g.JointY/g.Height-.5},PivotOffset={0,0},
        Sprite="srw-matryoshka-pivot",UserData=50,
        ChildrenBehind={{Name="Barrel",Angle=0,Pivot={0,0},
            PivotOffset={.5-g.JointX/g.Width,.5-g.JointY/g.Height},
            Sprite="srw-matryoshka-barrel",UserData=100,
            ChildrenInFront={{Name="Hardpoint0",Angle=90,
                Pivot={g.MuzzleX/g.Width-.5,g.MuzzleY/g.Height-.5},PivotOffset={0,0}}}},
        }}},
}
