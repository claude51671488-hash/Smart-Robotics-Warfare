-- Lower machine-gun turret; temporary native art.
dofile(path.."/weapons/aa_bot.lua")
Scale=.3
HitPoints=1100
Projectile="srw_skat_bullet"
RoundsEachBurst=4
RoundPeriod=.08
ReloadTime=.8
ReloadTimeIncludesBurst=false
MaxFireRadius=8000

-- Script schedules rounds against the current moving hardpoint.
RoundsEachBurst=1
ReloadTime=.04
ReloadTimeIncludesBurst=false
