-- Temporary built-in mine model. Costs/health are prototype balancing values.
dofile("devices/mine.lua")
-- The base mine already registers these sprites. Reuse its names in Root,
-- but do not register miner_anim, wheel_anim and mine-base a second time.
Sprites = {}
HitPoints = 1000
Mass = 400
EnergyProductionRate = 0
MetalProductionRate = 0
EnergyStorageCapacity = 0
MetalStorageCapacity = 0

dofile(path.."/devices/factory_art.lua")
