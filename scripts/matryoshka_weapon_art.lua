local directory=path.."/ui/textures/weapons/matryoshka/"
dofile(directory.."geometry.lua")
local g=SRWMatryoshkaGeometry
local function still(name) return {Frames={{texture=directory..name..".png"},mipmap=true}} end
local body={}
for _,side in ipairs({"Right","Left"}) do
    local suffix=side=="Right" and "right" or "left"
    for i=0,g.Frames-1 do
        body["Deploy"..side..i]=still("deploy_"..string.format("%02d",i).."_"..suffix)
    end
    for i=0,g.AimFrames-1 do
        body["Ready"..side.."Aim"..i]=still("aim_"..string.format("%03d",i).."_"..suffix)
    end
end
-- Native firing/idle transitions also have an open, single-silhouette fallback.
body.Normal=body.ReadyRightAim0;body.Idle=body.Normal
body.Reload=body.Normal;body.ReloadEnd=body.Normal
Sprites={{Name="srw-matryoshka-base",States=body}}
Scale=g.Scale
SelectionWidth=110;SelectionHeight=110;SelectionOffset={0,-55}
BarrelLength=0;BarrelRecoilLimit=-.02;BarrelRecoilSpeed=-.5;BarrelReturnForce=.12
local scale=g.Scale/.375
Root={Name="MatryoshkaFixedBase",Angle=0,Scale=scale,
    Pivot={(.5-g.FootX/g.Width)*scale,(.5-g.FootY/g.Height)*scale},
    PivotOffset={0,0},Sprite="srw-matryoshka-base",UserData=0,
    ChildrenInFront={{Name="Head",Angle=0,
        Pivot={g.JointX/g.Width-.5,g.JointY/g.Height-.5},PivotOffset={0,0},
        Sprite=directory.."empty.png",UserData=50,
        ChildrenInFront={{Name="Barrel",Angle=0,Pivot={0,0},
            PivotOffset={.5-g.JointX/g.Width,.5-g.JointY/g.Height},
            Sprite=directory.."empty.png",UserData=100,
            ChildrenInFront={{Name="Hardpoint0",Angle=90,
                Pivot={g.MuzzleX/g.Width-.5,g.MuzzleY/g.Height-.5},PivotOffset={0,0}}}},
        }}},
}
