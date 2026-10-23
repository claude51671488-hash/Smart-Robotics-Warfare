-- Three unguided rounds from each independently aimed Swarm-model pod.
dofile(path.."/weapons/storm_rockets.lua")
Scale=.25
HitPoints=250
Projectile="srw_skat_rocket"
RoundsEachBurst=3
RoundPeriod=.15
ReloadTime=4
MaxFireRadius=8400

-- Script schedules rounds against the current moving hardpoint.
RoundsEachBurst=1
ReloadTime=.04
ReloadTimeIncludesBurst=false
