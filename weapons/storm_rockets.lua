-- Unguided six-rocket cassette; it keeps firing under missile-seeker EMP.
dofile(path.."/weapons/smith_rockets.lua")
Scale=.35
HitPoints=900
NoReclaim=true
Projectile="srw_storm_rocket"
RoundsEachBurst=6
RoundPeriod=.16
ReloadTime=6
ReloadTimeIncludesBurst=false
MinFireSpeed=4500
MaxFireSpeed=4500.1
MaxFireRadius=17600
FireStdDev=0
FireStdDevAuto=0
