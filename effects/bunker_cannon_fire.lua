-- Painted flash follows the actual muzzle; audio comes from the native weapon.
local kind="cannon"
dofile(kind=="cannon" and "effects/fire_cannon.lua" or "effects/fire_machinegun.lua")
local retained={}
for _,e in ipairs(Effects or {}) do if e.Type=="sound" or e.Type=="shake" then retained[#retained+1]=e end end
local name="srw-bunker-rig-flash-"..kind
local texture=path.."/ui/textures/engineering/rig/"..kind.."_flash.png"
Sprites={{Name=name,States={Normal={Frames={
 {texture=texture,colour={1,1,1,1},duration=.035},
 {texture=texture,colour={1,1,1,.6},duration=.035},
 {texture=texture,colour={1,1,1,0},duration=.035},
 mipmap=true,blendColour=true}}}}}
retained[#retained+1]={Type="sprite",TimeToTrigger=0,LocalPosition={x=0,y=-284.96,z=-1},
 LocalVelocity={x=0,y=0,z=0},Acceleration={x=0,y=0,z=0},Drag=0,Sprite=name,
 Additive=false,TimeToLive=.105,InitialSize=kind=="cannon" and .18 or .12,
 ExpansionRate=0,Angle=-90,AngularVelocity=0,RandomAngularVelocityMagnitude=0,
 Colour1={255,255,255,255},Colour2={255,255,255,0},KillParticleOnEffectExpire=true}
Effects=retained
LifeSpan=kind=="cannon" and 3 or .2
SRWBunkerFlashKind=nil
