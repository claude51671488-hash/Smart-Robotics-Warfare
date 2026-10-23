local directory=path.."/ui/textures/weapons/matryoshka/"
dofile(directory.."geometry.lua")
local g=SRWMatryoshkaGeometry
local function still(name) return {Frames={{texture=directory..name..".png"},mipmap=true}} end
local body,head,barrel={},{},{}
for _,side in ipairs({"Right","Left"}) do
    local suffix=side=="Right" and "right" or "left"
    for i=0,g.Frames-1 do
        local state="Deploy"..side..i
        body[state]=still("deploy_"..string.format("%02d",i).."_"..suffix)
        head[state]=still("empty");barrel[state]=still("empty")
    end
    for _,gun in ipairs({"Right","Left"}) do
        local state="Ready"..side..gun
        body[state]=still("ready_"..suffix)
        head[state]=still(gun=="Left" and "head_left" or "head")
        barrel[state]=still(gun=="Left" and "barrel_left" or "barrel")
    end
end
for _,states in ipairs({body,head,barrel}) do
    -- Native idle/reload transitions must never fold a deployed gun back into
    -- a projectile. Deployment is selected explicitly by the client below.
    states.Normal=states.ReadyRightRight;states.Idle=states.Normal
    states.Reload=states.Normal;states.ReloadEnd=states.Normal
end
Sprites={{Name="srw-matryoshka-base",States=body},
    {Name="srw-matryoshka-head",States=head},{Name="srw-matryoshka-barrel",States=barrel}}
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
            Sprite="srw-matryoshka-barrel",UserData=100,
            ChildrenInFront={{Name="Hardpoint0",Angle=90,
                Pivot={g.MuzzleX/g.Width-.5,g.MuzzleY/g.Height-.5},PivotOffset={0,0}}}},
            {Name="GunBreech",Angle=0,Pivot={0,0},
                PivotOffset={.5-g.JointX/g.Width,.5-g.JointY/g.Height},
                Sprite="srw-matryoshka-head",UserData=0},
        }}},
}
