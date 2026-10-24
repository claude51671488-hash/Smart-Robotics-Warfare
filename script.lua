-- Forts loads this entry point for an enabled mod.
dofile("scripts/forts.lua")

SRW = { Version = "0.54.9-isolated-opening" }
dofile(path .. "/scripts/config.lua")
dofile(path .. "/scripts/robots/layout.lua")
dofile(path .. "/scripts/combat/aiming.lua")
dofile(path .. "/scripts/combat/emp.lua")
dofile(path .. "/scripts/combat/impacts.lua")
dofile(path .. "/scripts/combat/guidance.lua")
dofile(path .. "/scripts/state.lua")
dofile(path .. "/scripts/factories/production.lua")
dofile(path .. "/scripts/factories/squads.lua")
dofile(path .. "/scripts/robots/dynamit_art.lua")
dofile(path .. "/scripts/robots/hornet_art.lua")
dofile(path .. "/scripts/robots/movement.lua")
dofile(path .. "/scripts/robots/spacing.lua")
dofile(path .. "/scripts/robots/hound.lua")
dofile(path .. "/scripts/robots/tank.lua")
dofile(path .. "/scripts/robots/air.lua")
dofile(path .. "/scripts/robots/sortie.lua")
dofile(path .. "/scripts/robots/parcel.lua")
dofile(path .. "/scripts/robots/repair.lua")
dofile(path .. "/scripts/robots/engineer.lua")
dofile(path .. "/scripts/robots/engineering_art.lua")
dofile(path .. "/scripts/matryoshka.lua")
dofile(path .. "/scripts/robots/shield.lua")
dofile(path .. "/scripts/robots/aa.lua")
dofile(path .. "/scripts/robots/heavy_aa.lua")
dofile(path .. "/scripts/robots/air_weapon.lua")
dofile(path .. "/scripts/robots/sentry.lua")
dofile(path .. "/scripts/ui/window.lua")
dofile(path .. "/scripts/ui/factory.lua")
dofile(path .. "/scripts/ui/squads.lua")
dofile(path .. "/scripts/shields.lua")
dofile(path .. "/scripts/shield_levels.lua")
dofile(path .. "/scripts/shield_shapes.lua")
dofile(path .. "/scripts/ui/shield.lua")
dofile(path .. "/scripts/ui/robot_braces.lua")

function Load(gameStart)
    -- Preserve restored state when loading replays or joining a running game.
    SRW.EnsureState()
    SRW.CreateUI()
    SRW.CreateShieldUI()
    Log("[Smart Robotics Warfare] " .. SRW.Version .. " loaded")
end

function Update(frame)
    SRW.EnsureState()
    SRW.ScanFactories()
    SRW.UpdateFactories(0.04)
    SRW.UpdateEMP(0.04)
    SRW.SeparateRobots(0.04)
    SRW.UpdateWeaponPower(0.04)
    SRW.BeginCombatSnapshot()
    SRW.UpdateRobots(0.04)
    SRW.UpdateMountedWeapons(0.04)
    SRW.UpdateCapsules(0.04)
    SRW.EndCombatSnapshot()
    SRW.UpdateGuidance(0.04)
    SRW.ScanShields()
    SRW.UpdateShieldPower(0.04)
    SRW.UpdateShieldShapes(0.04)
    SRW.UpdateBeamBarriers(0.04)
    SRW.InterceptShieldProjectiles(0.04)
    if frame % 1500 == 0 then
        Log("[SRW] health frame="..frame.." robots="..#SRW.SortedIds(data.srw.Robots)
            .." shields="..#SRW.SortedIds(data.srw.Shields)
            .." trackedShots="..#SRW.SortedIds(data.srw.ShieldProjectiles)
            .." mounts="..#SRW.SortedIds(data.srw.MountedWeapons)
            .." guided="..#SRW.SortedIds(data.srw.GuidedMissiles)
            .." squadShields="..#SRW.SortedIds(data.srw.SquadShields or {}))
    end
end

function OnUpdate(delta)
    SRW.RefreshDynamitVisuals(delta)
    SRW.RefreshHornetVisuals(delta)
    SRW.RefreshCapsuleVisuals(delta)
    SRW.RefreshUI()
    SRW.RefreshFactoryMap(delta)
    SRW.RefreshShieldUI(delta)
    SRW.RefreshRobotBraces(delta)
end

function OnControlActivated(name, code, doubleClick)
    SRW.ClickUI(name)
    SRW.ClickShieldUI(name)
end

function OnKey(key, down) return SRW.ShieldKey(key, down) end
function OnExit() SRW.CleanupShieldUI() end

function OnGroundDeviceCreated(teamId,deviceId,saveName,pos,upgradedId)
    SRW.ShieldCreated(teamId,deviceId,saveName,upgradedId)
    SRW.FactoryCreated(teamId,deviceId,saveName,upgradedId)
end
function OnDeviceCreated(teamId,deviceId,saveName,nodeA,nodeB,t,upgradedId)
    SRW.ShieldCreated(teamId,deviceId,saveName,upgradedId)
    SRW.FactoryCreated(teamId,deviceId,saveName,upgradedId)
end

-- These handlers are called through SendScriptEvent, never directly by the UI.
function SRW_Order(team, id)
    SRW.Order(tonumber(team), tonumber(id))
end

function SRW_Release(team, id)
    SRW.Release(tonumber(team), tonumber(id))
end

function OnProjectileDestroyed(nodeId,teamId,saveName,structureIdHit,destroyType)
    SRW.CapsuleImpact(nodeId,teamId,saveName,destroyType)
    SRW.EMPImpact(nodeId,teamId,saveName,destroyType)
    SRW.TerrainBlastVisual(nodeId,teamId,saveName,destroyType)
    if data.srw and data.srw.GuidedMissiles then data.srw.GuidedMissiles[nodeId]=nil end
end

function OnWeaponFired(teamId,saveName,weaponId,projectileNodeId,projectileNodeIdFrom)
    SRW.TrackCapsule(teamId,projectileNodeId,weaponId)
    SRW.EngineeringShot(weaponId)
    SRW.HornetShot(weaponId)
    SRW.GuidedLaunch(teamId,weaponId,projectileNodeId)
    SRW.SieveLaunch(teamId,weaponId,projectileNodeId)
end
