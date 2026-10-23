dofile("effects/barrel_explode.lua")
local frames={duration=.09,mipmap=true,blendCoordinates=false}
for i=2,8 do
    frames[#frames+1]={texture=path.."/ui/textures/engineering/animated/mine_"..string.format("%02d",i)..".png"}
end
Sprites={{Name="srw-field-mine-detonation",States={Normal={Frames=frames}}}}
Effects[1]={Type="sprite",TimeToTrigger=0,LocalPosition={x=0,y=-55,z=-10},
    LocalVelocity={x=0,y=0,z=0},Acceleration={x=0,y=0,z=0},Drag=0,
    Sprite="srw-field-mine-detonation",Additive=false,TimeToLive=.63,
    InitialSize=.30,ExpansionRate=0,Angle=-90,AngularVelocity=0,
    RandomAngularVelocityMagnitude=0,Colour1={255,255,255,255},Colour2={255,255,255,0},
    KillParticleOnEffectExpire=true,KillParticleOnEffectCancel=true}
