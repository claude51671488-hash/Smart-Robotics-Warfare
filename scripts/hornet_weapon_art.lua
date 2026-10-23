-- Approved flush-bay Hornet. The hull never inherits the gun's aiming rotation.
local bay=SRWHornetArtKind=="bay"
local directory=path.."/ui/textures/robots/hornet/"
dofile(directory.."geometry.lua")
local g=SRWHornetGeometry
local scale=g.Scale/.375
local function still(file) return {Frames={{texture=directory..file..".png"},mipmap=true}} end
local function sequence(stem,side)
    local frames={duration=g.FrameSeconds,mipmap=true,blendCoordinates=false}
    for i=1,g.FrameCount do frames[#frames+1]={texture=directory..stem.."_"..string.format("%02d",i).."_"..side..".png"} end
    return frames
end
local function modes(kind)
    local states={}
    for _,side in ipairs({"right","left"}) do
        local suffix=side=="right" and "Right" or "Left"
        local gun=kind and still(kind..(side=="left" and "_left" or ""))
        for _,mode in ipairs({"cruise","boost","climb","dive"}) do
            local name=mode:sub(1,1):upper()..mode:sub(2)..suffix
            states[name]=gun or {Frames=sequence(mode,side),NextState=name}
            states[name.."Launch"]=gun or {Frames=sequence(mode.."_launch",side),NextState=name}
        end
        states["Idle"..suffix]=gun or still("idle_"..side)
    end
    states.Normal=states.CruiseRight;states.Idle=states.Normal
    states.Reload=states.Normal;states.ReloadEnd=states.Normal
    return states
end
Scale=g.Scale
CanFlip=false
BarrelLength=0
NodeEffects={}
ShellEffect=""
ReloadEffect=""
ShowFireAngle=false
ShowAimingGizmo=false
if bay then
    Sprites={{Name="srw-hornet-integrated-bay",States={Normal=still("empty"),Idle=still("empty")}}}
    SelectionWidth=85;SelectionHeight=22;SelectionOffset={0,0}
    Root={Name="HornetIntegratedBay",Angle=0,Scale=scale,Pivot={0,0},PivotOffset={0,0},
        Sprite="srw-hornet-integrated-bay",UserData=0,
        ChildrenInFront={{Name="Hardpoint0",Angle=0,Pivot={0,0},PivotOffset={0,0}}}}
else
    Sprites={
        {Name="srw-hornet-hull",States=modes()},
        {Name="srw-hornet-gun-head",States=modes("gun_head")},
        {Name="srw-hornet-gun-barrel",States=modes("gun_barrel")},
    }
    SelectionWidth=245;SelectionHeight=165;SelectionOffset={0,-55}
    BarrelRecoilLimit=-.025;BarrelRecoilSpeed=-1.2;BarrelReturnForce=.4
    FireEffect=path.."/effects/hornet_autocannon_fire.lua"
    Root={Name="HornetFixedHull",Angle=0,Scale=scale,
        Pivot={(.5-g.JointX/g.Width)*scale,(.5-g.JointY/g.Height)*scale},
        PivotOffset={0,0},Sprite="srw-hornet-hull",UserData=0,
        ChildrenInFront={{Name="Head",Angle=0,
            Pivot={g.JointX/g.Width-.5,g.JointY/g.Height-.5},PivotOffset={0,0},
            Sprite=directory.."empty.png",UserData=50,
            ChildrenInFront={
                {Name="Barrel",Angle=0,Pivot={0,0},PivotOffset={0,0},
                    Sprite="srw-hornet-gun-barrel",UserData=100,
                    ChildrenInFront={{Name="Hardpoint0",Angle=90,
                        Pivot={g.MuzzleX/g.Width-.5,g.MuzzleY/g.Height-.5},PivotOffset={0,0}}}},
                {Name="GunBreech",Angle=0,Pivot={0,0},PivotOffset={0,0},
                    Sprite="srw-hornet-gun-head",UserData=0},
            }}}}
end
SRWHornetArtKind=nil
