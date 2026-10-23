-- Prepared gameplay controller, deliberately NOT loaded by script.lua.
-- A verified native adapter for ONE connected structure is still required.
-- Never implement this adapter with SetSideVisible or an untested GhostStructure.
SRW.Cloak = {
    LimitPerSide=1, Prerequisite="factory", BuildMetal=5000, BuildEnergy=15000,
    Levels={
        {Duration=5,Energy=8000,Cooldown=20},
        {Duration=12,Energy=18000,Cooldown=15,UpgradeMetal=3500,UpgradeEnergy=10000,UpgradeSeconds=30},
        {Duration=16,Energy=20000,Cooldown=12,UpgradeMetal=8000,UpgradeEnergy=18000,UpgradeSeconds=50},
    },
}
local C=SRW.Cloak
local kinds={srw_cloak_generator=1,srw_cloak_generator_2=2,srw_cloak_generator_3=3}
function C.Tier(kind) return kinds[kind] end

function C.CountSide(team,exclude)
    local count=0
    for index=0,GetDeviceCountSide(team%100)-1 do
        local id=GetDeviceIdSide(team%100,index)
        if id~=exclude and DeviceExists(id) and GetDeviceTeamIdActual(id)%100==team%100
            and C.Tier(GetDeviceType(id)) then count=count+1 end
    end
    return count
end

function C.Structure(id)
    if not DeviceExists(id) then return end
    local sid=GetDeviceStructureId(id)
    if sid and sid>=0 then return sid end
end

function C.Contains(generator,target)
    if not DeviceExists(generator) or not DeviceExists(target)
        or GetDeviceTeamIdActual(generator)%100~=GetDeviceTeamIdActual(target)%100 then return false end
    local sid=C.Structure(generator)
    return sid~=nil and C.Structure(target)==sid
end

function C.New(team,tier)
    return {Team=team,Tier=tier,Remaining=0,Cooldown=0}
end

-- Adapter contract: Apply(generator, structureId, tier) returns a token or nil;
-- Refresh(token, generator, currentStructureId) follows splits/merges, removing
-- the effect from detached parts; Restore(token) restores visibility/collision.
-- Every method is synchronized. Ownership must never be changed to emulate it.
function C.Start(team,id,s,adapter)
    if not DeviceExists(id) or team~=s.Team or GetDeviceTeamIdActual(id)~=team
        or not IsDeviceFullyBuilt(id) or DeviceDisabled(id) then return false,"owner_or_device" end
    if C.Tier(GetDeviceType(id))~=s.Tier then return false,"tier" end
    if s.Remaining>0 or s.Cooldown>0 then return false,"busy" end
    local cfg=C.Levels[s.Tier]
    if not cfg then return false,"tier" end
    local sid=C.Structure(id)
    if not sid then return false,"structure" end
    if not adapter or adapter.SelectiveVisibility~=true or type(adapter.Apply)~="function"
        or type(adapter.Refresh)~="function" or type(adapter.Restore)~="function"
        or (s.Tier==3 and adapter.SelectiveProjectileCollision~=true) then
        return false,"native_backend_unverified"
    end
    if C.CountSide(team,id)>=C.LimitPerSide then return false,"side_limit" end
    if GetTeamResources(team).energy<cfg.Energy then return false,"energy" end
    local token=adapter.Apply(id,sid,s.Tier)
    if not token then return false,"native_backend_failed" end
    AddResources(team,{metal=0,energy=-cfg.Energy})
    s.Token=token;s.Remaining=cfg.Duration;s.Structure=sid
    return true
end

function C.Stop(s,adapter)
    if s.Token then adapter.Restore(s.Token) end
    s.Token=nil;s.Structure=nil;s.Remaining=0
    s.Cooldown=C.Levels[s.Tier].Cooldown
end

function C.Update(id,s,dt,adapter)
    if s.Remaining<=0 then s.Cooldown=math.max(0,s.Cooldown-dt);return end
    if not DeviceExists(id) or GetDeviceTeamIdActual(id)~=s.Team or DeviceDisabled(id)
        or not IsDeviceFullyBuilt(id) or C.Tier(GetDeviceType(id))~=s.Tier then C.Stop(s,adapter);return end
    local sid=C.Structure(id)
    if not sid or not adapter.Refresh(s.Token,id,sid) then C.Stop(s,adapter);return end
    s.Structure=sid
    if dt>=s.Remaining then
        local excess=dt-s.Remaining
        C.Stop(s,adapter);s.Cooldown=math.max(0,s.Cooldown-excess)
    else s.Remaining=s.Remaining-dt end
end

-- For SRW robot targeting, guided target retention and structure-proximity fuses.
-- This cannot suppress targeting/fuses owned by arbitrary third-party mods.
function C.TargetBlocked(generator,s,observerTeam,target)
    return s.Token~=nil and s.Remaining>0 and s.Tier>=2 and s.Team%100~=observerTeam%100
        and DeviceExists(generator) and GetDeviceTeamIdActual(generator)==s.Team
        and C.Contains(generator,target)
end
