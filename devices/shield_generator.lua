dofile("devices/battery.lua")
Sprites = {} -- Reuse the base game's battery sprites.
HitPoints = 200
EnergyStorageCapacity = 0
EnergyProductionRate = 0 -- Charged by shield simulation only when in use.
DeviceSplashDamage = 0
StructureSplashDamage = 0
IgnitePlatformOnDestruct = false
