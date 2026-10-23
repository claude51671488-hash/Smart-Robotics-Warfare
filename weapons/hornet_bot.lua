-- Concept 20: approved Hornet hull pitches with flight; gun traverses separately.
dofile(path.."/weapons/aa_bot.lua")
Scale=.3
HitPoints=800
Projectile="srw_hornet_bullet"
RoundsEachBurst=3
RoundPeriod=.08
ReloadTime=.6
ReloadTimeIncludesBurst=false
SRWHornetArtKind="body"
dofile(path.."/scripts/hornet_weapon_art.lua")
MinFireSpeed=10000
MaxFireSpeed=10000.1
MaxFireRadius=8000

-- Script schedules rounds against the current moving hardpoint.
RoundsEachBurst=1
ReloadTime=.04
ReloadTimeIncludesBurst=false
