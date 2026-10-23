-- KS30 hierarchy: fixed Base -> elevating Head (50) -> recoiling Barrel (100).
local kind=assert(SRWBunkerArtKind)
local cannon=kind=="cannon"
local left=SRWBunkerArtLeft==true
local directory=path.."/ui/textures/engineering/rig/"
dofile(directory.."geometry.lua")
local g=assert(SRWBunkerRigGeometry)[kind]
local suffix=left and "_left" or ""
local prefix="srw-bunker-rig-"..kind..suffix
local function still(file) return {Frames={{texture=directory..file..".png"},mipmap=true}} end
local base=still(kind.."_base"..suffix)
local head=still(kind.."_head"..suffix)
local barrel=still(kind.."_barrel"..suffix)
Sprites={
 {Name=prefix.."-base",States={Normal=base,Idle=base,Reload=base,ReloadEnd=base}},
 {Name=prefix.."-barrel",States={Normal=barrel,Idle=barrel,Reload=barrel,ReloadEnd=barrel}},
 {Name=prefix.."-head",States={Normal=head,Idle=head,Reload=head,ReloadEnd=head}},
}
if not cannon then
 Sprites[#Sprites+1]={Name=prefix.."-flash",InitialState="Null",States={Null={},Flash={
  Frames={{texture=directory.."machinegun_flash.png"},
   {texture=directory.."machinegun_flash.png",colour={1,1,1,.2}},
   {texture=directory.."machinegun_flash.png"},
   {texture=directory.."machinegun_flash.png",colour={1,1,1,0}},
   duration=.0375,blendColour=true,blendCoordinates=false},
  NextState="Flash",LoopLength=4,LoopExitState="Null"}}}
end
MinFireSpeed=cannon and 12500 or 6500
MaxFireSpeed=MinFireSpeed+.1
Scale=g.Scale
SelectionWidth=cannon and 330 or 190
SelectionHeight=cannon and 110 or 75
SelectionOffset={0,-SelectionHeight/2}
-- Native BarrelLength shifts the aim/clearance origin along the current barrel.
-- Our stable trunnion hardpoint already defines the ballistic origin.
BarrelLength=0
BarrelRecoilLimit=cannon and -.035 or -.03
BarrelRecoilSpeed=cannon and -.7 or -.5
BarrelReturnForce=cannon and .08 or .12
DefaultFireAngle=left and 180 or 0
-- Rapier/MT-12's narrow traverse prevents the breech crossing the roof.
local depression=cannon and 3 or 7
local elevation=cannon and 7 or 20
MinFireAngle=left and 180-elevation or -depression
MaxFireAngle=left and 180+depression or elevation
CanFlip=false
-- SRW supplies distance-based dispersion in the fire call. Native spread would
-- add a second error (especially the machinegun's wide manual spread).
FireStdDev=0
FireStdDevAuto=0
NodeEffects={}
FireEffect=path.."/effects/bunker_"..kind.."_fire.lua"
ShellEffect=""
ReloadEffect=""
local function vector(x,y) return {x/g.Width-.5,y/g.Height-.5} end
local rigScale=g.Scale/.375
local footX=left and g.Width-g.FootX or g.FootX
local jointX=left and g.Width-g.JointX or g.JointX
local artJointY=left and g.Height-g.JointY or g.JointY
local artMuzzleY=left and g.Height-g.MuzzleY or g.MuzzleY
-- Native Root.Scale scales the sprite, but does not scale Root.Pivot's
-- translation. Compensate explicitly or its painted foot drifts off the roof.
Root={Name="BunkerFixedBase",Angle=0,Scale=rigScale,
 Pivot={(.5-footX/g.Width)*rigScale,(.5-g.FootY/g.Height)*rigScale},PivotOffset={0,0},
 Sprite=prefix.."-base",UserData=0,
 ChildrenBehind={{Name="Head",Angle=0,Pivot=vector(jointX,g.JointY),
  PivotOffset={0,0},Sprite=directory.."empty.png",UserData=50,
  -- The aiming origin must stay at the trunnion. Putting it on the muzzle
  -- translates the whole native aiming wedge whenever the barrel elevates.
  ChildrenBehind=cannon and {{Name="Hardpoint0",Angle=90,Pivot={0,0},PivotOffset={0,0}}} or nil,
  ChildrenInFront={
   {Name="Barrel",Angle=0,Pivot={0,0},
    PivotOffset={.5-g.JointX/g.Width,.5-artJointY/g.Height},
    Sprite=prefix.."-barrel",UserData=100,
    ChildrenInFront={
     {Name=cannon and "Muzzle" or "Hardpoint0",Angle=90,Pivot=vector(g.MuzzleX,artMuzzleY),PivotOffset={0,0}},
    }},
   not cannon and {Name="MuzzleFlash",Angle=0,
    Pivot={(g.MuzzleX-g.JointX)/g.Width,(artMuzzleY-artJointY)/g.Height},
    PivotOffset={0,0},Scale=.65,Sprite=prefix.."-flash",Visible=false} or nil,
  }}},
  ChildrenInFront={
  {Name="TurretArmour",Angle=0,Pivot={0,0},PivotOffset={0,0},
   Sprite=prefix.."-head",UserData=0},

 },
}
SRWBunkerArtKind=nil
SRWBunkerArtLeft=nil
