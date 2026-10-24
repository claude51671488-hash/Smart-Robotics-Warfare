-- Approved Bastion V3: static concrete/armour, independent elevating tube.
local directory=path.."/ui/textures/weapons/kolokol/"
dofile(directory.."geometry.lua")
local g=SRWKolokolGeometry
local function still(file)
    local state={Frames={{texture=directory..file..".png"},mipmap=true}}
    return {Normal=state,Idle=state,Reload=state,ReloadEnd=state}
end
Sprites={
    {Name="srw-kolokol-base",States=still("base")},
    {Name="srw-kolokol-barrel",States=still("barrel")},
}
Scale=1 -- Same native selection scale as KS30; art has its own measured scale.
SelectionWidth=390;SelectionHeight=95;SelectionOffset={0,-95.5}
local rigScale=g.Scale/.375
BarrelLength=0
BarrelRecoilLimit=-.018;BarrelRecoilSpeed=-.45;BarrelReturnForce=.1
ReloadEffect=""
Root={Name="KolokolFixedBase",Angle=0,Scale=rigScale,
    Pivot={(.5-g.FootX/g.Width)*rigScale,(.5-g.FootY/g.Height)*rigScale},
    PivotOffset={0,0},Sprite="srw-kolokol-base",UserData=0,
    ChildrenBehind={{Name="Head",Angle=0,
        Pivot={g.JointX/g.Width-.5,g.JointY/g.Height-.5},PivotOffset={0,0},
        Sprite=directory.."empty.png",UserData=50,
        -- Pivot zero keeps the sector origin on the fixed trunnion. The Head
        -- supplies firing orientation; Root-level hardpoints fire horizontally.
        ChildrenBehind={{Name="Hardpoint0",Angle=90,Pivot={0,0},PivotOffset={0,0}}},
        ChildrenInFront={{Name="Barrel",Angle=0,Pivot={0,0},
            PivotOffset={.5-g.JointX/g.Width,.5-g.JointY/g.Height},
            Sprite="srw-kolokol-barrel",UserData=100,
            ChildrenInFront={{Name="Muzzle",Angle=90,
                Pivot={g.MuzzleX/g.Width-.5,g.MuzzleY/g.Height-.5},PivotOffset={0,0}}}},
            {Name="Chamber",Angle=0,Pivot={0,0},PivotOffset={0,0}},
        }}},
}
