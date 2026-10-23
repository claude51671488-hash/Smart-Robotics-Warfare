-- Reuse Forts' reactor plume shapes and native textures, without bundling them.
-- Only a bounded smoke plume is emitted: no reactor flash, shake or streamers.
dofile("effects/mushroom_cloud.lua")
LifeSpan=15
IgnoreHidden=false
local smoke="effects/media/ExplosionMedium"
local function stem(delay,duration,age,depth,colour)
    local e=Stem(delay,duration,age,depth,colour)
    e.Sprite=smoke
    e.SparkCount=1;e.BurstPeriod=.35;e.SparksPerBurst=1
    return e
end
Sprites={}
Effects={
    stem(0,4,9,-1,{100,93,82,220}),
    stem(1,3,8,-1.2,{135,127,111,190}),
    -- Same dimensions/speeds as the native reactor's main cap and lower cap.
    Cloud(0,22,8,125,-10,{67,65,60,235},14,9,-2,.1,1,.2,.8,smoke),
    Cloud(0,15,6,80,7,{85,80,70,210},14,8,-.25,.1,1,.2,.8,smoke),
    Cloud(0,85,5,-10,30,{105,94,75,180},10,8,-4,.3,1,.1,.7,smoke),
}
