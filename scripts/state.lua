function SRW.EnsureState()
    -- Only serializable simulation state belongs in data.
    data.srw = data.srw or {}
    local state = data.srw
    state.SchemaVersion = state.SchemaVersion or 1
    state.FieldMines = state.FieldMines or {}
    state.MountedWeapons = state.MountedWeapons or {}
    state.Robots = state.Robots or {}
    state.Factories = state.Factories or {}
    state.Projectiles = state.Projectiles or {}
    state.GuidedMissiles = state.GuidedMissiles or {}
    state.Shields = state.Shields or {}
    state.ShieldProjectiles = state.ShieldProjectiles or {}
    return state
end

-- Short-lived combat snapshot, never serialized in data or retained across ticks.
local combatTargets,airTargets
function SRW.BeginCombatSnapshot() combatTargets={}; airTargets={} end
function SRW.EndCombatSnapshot() combatTargets=nil; airTargets=nil end
function SRW.DeviceTargets(side)
    if combatTargets and combatTargets[side] then return combatTargets[side] end
    local targets={}
    for i=0,GetDeviceCountSide(side)-1 do
        local id=GetDeviceIdSide(side,i)
        if DeviceExists(id) and GetDeviceTeamIdActual(id)%100==side then
            targets[#targets+1]={Id=id,Position=GetDeviceCentrePosition(id),Kind=GetDeviceType(id)}
        end
    end
    if combatTargets then combatTargets[side]=targets end
    return targets
end

function SRW.AirTargets(side)
    if airTargets and airTargets[side] then return airTargets[side] end
    local targets={}
    for i=0,ProjectileCount(side)-1 do
        local id=GetProjectileId(side,i)
        if NodeExists(id) and NodeTeam(id)%100==side then
            targets[#targets+1]={Id=id,Position=NodePosition(id)}
        end
    end
    for _,entry in ipairs(SRW.DeviceTargets(side)) do
        if (SRW.Config.Robots[entry.Kind] or {}).Air then
            targets[#targets+1]={Id=entry.Id,Position=entry.Position,IsDevice=true}
        end
    end
    if airTargets then airTargets[side]=targets end
    return targets
end

function SRW.AirTargetAlive(entry,side)
    if entry.IsDevice then return DeviceExists(entry.Id) and GetDeviceTeamIdActual(entry.Id)%100==side end
    return NodeExists(entry.Id) and NodeTeam(entry.Id)%100==side
end
function SRW.AirTargetVelocity(entry)
    if entry.IsDevice then
        local bot=data.srw.Robots[entry.Id]
        return bot and bot.AirVelocity or {x=0,y=0}
    end
    return NodeVelocity(entry.Id)
end
