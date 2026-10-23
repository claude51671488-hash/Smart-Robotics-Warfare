-- Native Swarm silo and launch effects; SRW ammunition and salvo balance.
dofile("weapons/missileswarm.lua")
Sprites={}
RecessionBox=nil
Repairable=true
BarrelLength=0
MinFireClearance=0
FireDelay=0
FireEffect="effects/missile_swarm_launch.lua"
RetriggerFireEffect=true
RetriggerFireEffectOnce=false
EnergyFireCost=0
MetalFireCost=0
Recoil=0
KickbackMean=0
KickbackStdDev=0
DeviceSplashDamage=0
StructureSplashDamage=0
IncendiaryRadius=0
IncendiaryRadiusHeated=0
IgnitePlatformOnDestruct=false
ShowFireAngle=false
ShowAimingGizmo=false
-- Remove the native trajectory overlay, even when another mod shows silo arcs.
if Root then
    for i=#Root.ChildrenInFront,1,-1 do
        if Root.ChildrenInFront[i].Name=="Flightpath" then table.remove(Root.ChildrenInFront,i) end
    end
end
Scale=0.5
HitPoints=1000
Projectile="srw_salvo_rocket"
ReloadTime=9
ReloadTimeIncludesBurst=false
RoundsEachBurst=4
RoundPeriod=0.25
MinFireSpeed=2500
MaxFireSpeed=2500.1
MinFireRadius=0
MaxFireRadius=17600.0
FireStdDev=0
FireStdDevAuto=0
