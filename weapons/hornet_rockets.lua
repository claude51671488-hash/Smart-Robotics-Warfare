dofile(path.."/weapons/rocket_bot.lua")
Scale=.25
HitPoints=250
Projectile="srw_hornet_rocket"
RoundsEachBurst=2
RoundPeriod=.2
ReloadTime=5
MinFireSpeed=3500
MaxFireSpeed=3500.1
MaxFireRadius=10000

-- Script schedules rounds against the current moving hardpoint.
RoundsEachBurst=1
ReloadTime=.04
ReloadTimeIncludesBurst=false
SRWHornetArtKind="bay"
dofile(path.."/scripts/hornet_weapon_art.lua")
