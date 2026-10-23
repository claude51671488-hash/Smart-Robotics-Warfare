dofile("effects/fire_machinegun.lua")
local retained={}
for _,effect in ipairs(Effects or {}) do
    if effect.Type=="sound" then retained[#retained+1]=effect end
end
local texture=path.."/ui/textures/robots/hornet/muzzle_flash.png"
Sprites={{Name="srw-hornet-muzzle",States={Normal={Frames={
    {texture=texture,colour={1,1,1,1},duration=.025},
    {texture=texture,colour={1,1,1,.4},duration=.025},
    {texture=texture,colour={1,1,1,0},duration=.025},mipmap=true,blendColour=true}}}}}
retained[#retained+1]={Type="sprite",TimeToTrigger=0,LocalPosition={x=0,y=0,z=-1},
    LocalVelocity={x=0,y=0,z=0},Acceleration={x=0,y=0,z=0},Drag=0,
    Sprite="srw-hornet-muzzle",Additive=true,TimeToLive=.075,InitialSize=.5,
    ExpansionRate=0,Angle=-90,AngularVelocity=0,RandomAngularVelocityMagnitude=0,
    Colour1={255,255,255,255},Colour2={255,255,255,0},KillParticleOnEffectExpire=true}
Effects=retained
LifeSpan=.2
