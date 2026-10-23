-- Keep the native barrel's light, sparks and camera shake; replace its artwork.
dofile("effects/barrel_explode.lua")
local frames={duration=.1,mipmap=true,blendCoordinates=false}
for i=3,8 do
    frames[#frames+1]={texture=path.."/ui/textures/robots/dynamit/detonation_"..string.format("%02d",i)..".png"}
end
Sprites={{Name="srw-dynamit-detonation",States={Normal={Frames=frames}}}}
Effects[1]={Type="sprite",TimeToTrigger=0,LocalPosition={x=0,y=0,z=-10},
    LocalVelocity={x=0,y=0,z=0},Acceleration={x=0,y=0,z=0},Drag=0,
    Sprite="srw-dynamit-detonation",Additive=false,TimeToLive=.6,
    InitialSize=.25,ExpansionRate=0,Angle=-90,AngularVelocity=0,
    RandomAngularVelocityMagnitude=0,Colour1={255,255,255,255},Colour2={255,255,255,255},
    KillParticleOnEffectExpire=true,KillParticleOnEffectCancel=true}
