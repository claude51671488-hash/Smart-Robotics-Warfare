-- Reactor smoke textures, already arranged as a mushroom on the first frame.
-- Native projectile splash is the only damage source; this file is visual only.
dofile("effects/mushroom_cloud.lua")
LifeSpan=15
IgnoreHidden=false
local smoke="effects/media/ExplosionMedium"
local function instant(e,height)
    e.TimeToTrigger=0;e.TimeToStop=0;e.BurstPeriod=20
    e.Sprite=smoke
    for _,k in ipairs(e.Keyframes) do
        k.SpeedMean=0;k.SpeedStdDev=0;k.Drag=0
        k.RadialOffsetMin=height;k.RadialOffsetMax=height
        k.ScaleKeys={0,.85};k.AlphaKeys={0,.2}
    end
    return e
end
local function stem(height)
    local e=Stem(0,0,14,-1,{110,103,90,200})
    e.SparkCount=1;e.SparksPerBurst=1
    return instant(e,height)
end
local waveFrames={duration=.055,mipmap=true}
for i=1,9 do waveFrames[#waveFrames+1]={texture="effects/media/ShockWave"..string.format("%02d",i)} end
Sprites={{Name="srw-kolokol-pressure-front",States={Normal={Frames=waveFrames}}}}
Effects={
    stem(60),stem(180),stem(300),stem(420),stem(540),
    instant(Cloud(0,22,8,0,0,{67,65,60,235},14,9,-2,0,.85,0,.2,smoke),740),
    instant(Cloud(0,15,6,0,0,{85,80,70,210},14,8,-.25,0,.85,0,.2,smoke),520),
    instant(Cloud(0,85,5,0,0,{105,94,75,180},10,8,-4,0,.85,0,.2,smoke),20),
    -- A brief animated pressure front, not a radius indicator or extra damage.
    {Type="sprite",TimeToTrigger=0,TimeToLive=.55,
        LocalPosition={x=0,y=0,z=-10},LocalVelocity={x=0,y=0,z=0},
        Acceleration={x=0,y=0,z=0},Drag=0,Sprite="srw-kolokol-pressure-front",Additive=false,
        InitialSize=2,ExpansionRate=1.5,Angle=0,AngularVelocity=0,
        RandomAngularVelocityMagnitude=0,Colour1Time=0,Colour2Time=.55,
        Colour1={210,200,175,150},Colour2={210,200,175,0}},
}
