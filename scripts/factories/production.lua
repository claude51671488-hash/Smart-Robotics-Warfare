SRW.RobotKinds={"srw_dynamit_bot","srw_hound","srw_repair_bot","srw_siege_bot","srw_aa_bot","srw_shield_bot","srw_emp_bot","srw_laser_bot","srw_rocket_bot","srw_hunter_bot","srw_bastion_bot","srw_heavy_aa_bot","srw_heavy_siege_bot","srw_tank_bot","srw_colossus_bot","srw_sentry_bot","srw_smith_bot","srw_pike_bot","srw_executioner_bot","srw_storm_bot","srw_vault_bot","srw_tempest_bot","srw_mlrs_bot","srw_hornet_bot","srw_sledge_bot","srw_skat_bot","srw_lantern_bot","srw_parcel_bot","srw_archangel_bot","srw_engineer_bot"}
function SRW.FactoryDomain(name)
    return name and string.find(name,"^srw_factory_air_") and "air" or "ground"
end
function SRW.FactoryCanProduce(f,kind)
    local cfg=SRW.Config.Robots[kind]
    return cfg and (cfg.Domain or "ground")== (f.Domain or "ground") and (cfg.Tier or 1)<=(f.Tier or 1)
end
function SRW.RobotListPosition(index,size)
    local domain=SRW.Config.Robots[SRW.RobotKinds[index]].Domain or "ground"
    local count=0
    for i=1,index do
        if (SRW.Config.Robots[SRW.RobotKinds[i]].Domain or "ground")==domain then count=count+1 end
    end
    return math.floor((count-1)/size)+1,(count-1)%size
end
function SRW.FactoryPlatformValid(id,name)
    if SRW.FactoryDomain(name)~="air" then return true end
    return GetLinkMaterialSaveName(GetDevicePlatformA(id),GetDevicePlatformB(id))=="srw_air_platform"
end
function SRW.SpawnFactoryRobot(team,id,kind)
    if (SRW.Config.Robots[kind] or {}).Air then return SRW.SpawnAirRobot(team,id,kind) end
    if kind=="srw_engineer_bot" then return SRW.SpawnEngineer(team,id) end
    if kind=="srw_dynamit_bot" then return SRW.SpawnRobot(team,id) end
    if SRW.Config.Robots[kind].Mounts then return SRW.SpawnTank(team,id,kind) end
    if kind=="srw_shield_bot" then return SRW.SpawnShieldBot(team,id) end
    if kind=="srw_repair_bot" then return SRW.SpawnRepairBot(team,id) end
    return SRW.SpawnHound(team,id,kind)
end

function SRW.ExtraCount(f,suffix)
    local count=0
    for i=6,#SRW.RobotKinds do count=count+(f[SRW.RobotKinds[i]..suffix] or 0) end
    return count
end
function SRW_OrderIndividual(team,id,index)
    team,id,index=tonumber(team),tonumber(id),tonumber(index)
    local f=SRW.ValidFactory(team,id); local kind=index and SRW.RobotKinds[index]
    if not f or not kind or index<6 then return end
    if not SRW.FactoryCanProduce(f,kind) then f.Status="tier_required"; return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f)>=SRW.Config.Prototype.QueueLimit then f.Status="queue_full"; return end
    f[kind.."Queue"]=(f[kind.."Queue"] or 0)+1; f.Status="queued"
end
function SRW_ReleaseIndividual(team,id,index)
    team,id,index=tonumber(team),tonumber(id),tonumber(index)
    local f=SRW.ValidFactory(team,id); local kind=index and SRW.RobotKinds[index]
    if not f or not kind or index<6 then return end
    if not SRW.FactoryCanProduce(f,kind) then f.Status="tier_required";return end
    if (f[kind.."Reserve"] or 0)<1 then f.Status="empty"; return end
    if SRW.ActiveCount(team,kind)>=SRW.Config.Robots[kind].ActiveLimit then f.Status="limit"; return end
    if not SRW.CanExit(f) then return end
    local ok=SRW.SpawnFactoryRobot(team,id,kind)
    if ok then f[kind.."Reserve"]=f[kind.."Reserve"]-1; SRW.MarkExit(f,kind)
    else f.Status="exit_blocked" end
end
function SRW.SortedIds(t)
    local ids = {}
    for id in pairs(t) do ids[#ids + 1] = id end
    table.sort(ids)
    return ids
end

function SRW.FactoryTier(name)
    local tiers={srw_factory_ground_1=1,srw_factory_ground_2=2,srw_factory_ground_3=3,srw_factory_air_1=1,srw_factory_air_2=2}
    return tiers[name]
end

function SRW.FactoryCapacity(f)
    return SRW.Config.FactoryReserveByTier[f.Tier or 1]
end

function SRW.FactoryCreated(team,id,name,upgradedId)
    local tier=SRW.FactoryTier(name); if not tier then return end
    SRW.EnsureState()
    local domain=SRW.FactoryDomain(name)
    if not SRW.FactoryPlatformValid(id,name) then
        local cost=GetDeviceCost(name)
        if DeleteDeviceById(id) then AddResources(team,cost,false,Vec3(0,0,0)) end
        Log("[SRW] Air factory requires an aviation platform; refunded")
        return
    end
    local factories=data.srw.Factories
    if factories[id] and factories[id].Team==team then
        factories[id].Tier=tier;factories[id].Domain=domain
        return
    end
    local previous=upgradedId and factories[upgradedId]
    if previous and previous.Team==team then
        factories[id]=previous
        if id~=upgradedId then factories[upgradedId]=nil end
        previous.Tier=tier;previous.Domain=domain
        previous.Status="disabled"
        return
    end
    -- Upgrades replace a device; a separately placed second factory is rejected.
    if not upgradedId or upgradedId==0 then
        for index=0,GetDeviceCountSide(team%100)-1 do
            local other=GetDeviceIdSide(team%100,index)
            if other~=id and DeviceExists(other) and GetDeviceTeamIdActual(other)==team
                and SRW.FactoryTier(GetDeviceType(other)) and SRW.FactoryDomain(GetDeviceType(other))==domain then
                local cost=GetDeviceCost(name)
                if DeleteDeviceById(id) then
                    AddResources(team,cost,false,Vec3(0,0,0))
                    Log("[SRW] Duplicate factory rejected and refunded, owner "..team)
                end
                return
            end
        end
    end
    factories[id]={Team=team,Tier=tier,Domain=domain,Queue=0,Reserve=0,Remaining=0,Status="disabled"}
end

function SRW.ScanFactories()
    local factories = data.srw.Factories
    for side = 1, 2 do
        for index = 0, GetDeviceCountSide(side) - 1 do
            local id = GetDeviceIdSide(side, index)
            local tier=SRW.FactoryTier(GetDeviceType(id))
            if tier and IsDeviceFullyBuilt(id) then
                local team = GetDeviceTeamIdActual(id)
                if not factories[id] or factories[id].Team ~= team then
                    factories[id] = { Team = team, Queue = 0, Reserve = 0, Remaining = 0, Status = "ready" }
                    Log("[SRW] Factory " .. tostring(id) .. " ready, owner " .. tostring(team))
                end
                factories[id].Tier=tier;factories[id].Domain=SRW.FactoryDomain(GetDeviceType(id))
            end
        end
    end
    for _, id in ipairs(SRW.SortedIds(factories)) do
        if not DeviceExists(id) or not SRW.FactoryTier(GetDeviceType(id)) then
            factories[id] = nil
        end
    end
end

function SRW.ValidFactory(team, id)
    local f = data.srw.Factories[id]
    if f and DeviceExists(id) and GetDeviceTeamIdActual(id) == team and f.Team == team
        and IsDeviceFullyBuilt(id) and not DeviceDisabled(id)
        and SRW.FactoryPlatformValid(id,GetDeviceType(id)) then return f end
end

function SRW.NormalFactoryQueue(f)
    return SRW.ExtraCount(f,"Queue")+f.Queue+(f.HoundQueue or 0)+(f.RepairQueue or 0)+(f.SiegeQueue or 0)+(f.AAQueue or 0)
end
function SRW.FactoryQueue(f)
    return SRW.NormalFactoryQueue(f)+(SRW.SquadPending and SRW.SquadPending(f) or 0)
end
function SRW.FactoryReserve(f)
    return SRW.ExtraCount(f,"Reserve")+f.Reserve+(f.HoundReserve or 0)+(f.RepairReserve or 0)+(f.SiegeReserve or 0)+(f.AAReserve or 0)
        +(SRW.SquadStored and SRW.SquadStored(f) or 0)
end
function SRW.CanExit(f)
    if (f.ExitRemaining or 0)>0 then f.Status="exit_wait"; return false end
    return true
end
function SRW.MarkExit(f,kind)
    f.ExitRemaining=SRW.Config.Robots[kind].ExitDelay or 3
    f.Status="released"
end

function SRW.Order(team, id)
    local f = SRW.ValidFactory(team, id)
    if f and not SRW.FactoryCanProduce(f,"srw_dynamit_bot") then return end
    if not f then return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f) >= SRW.Config.Prototype.QueueLimit then f.Status = "queue_full"; return end
    f.Queue = f.Queue + 1
    f.Status = "queued"
end

function SRW.UpdateFactories(dt)
    for _, id in ipairs(SRW.SortedIds(data.srw.Factories)) do
        local f = data.srw.Factories[id]
        f.ExitRemaining=math.max(0,(f.ExitRemaining or 0)-dt)
        if f.ExitRemaining<0.000001 then f.ExitRemaining=0 end
        if not SRW.ValidFactory(f.Team, id) then
            f.Status = "disabled"
        elseif f.Remaining > 0 then
            f.Remaining = math.max(0, f.Remaining - dt)
            f.Status = "building"
            if f.Remaining < 0.000001 then
                f.Remaining = 0
                if f.CurrentSquad and f.Squad then f.Squad.Produced=f.Squad.Produced+1
                elseif f.CurrentType=="srw_hound" then f.HoundReserve=(f.HoundReserve or 0)+1
                elseif f.CurrentType=="srw_repair_bot" then f.RepairReserve=(f.RepairReserve or 0)+1
                elseif f.CurrentType=="srw_siege_bot" then f.SiegeReserve=(f.SiegeReserve or 0)+1
                elseif f.CurrentType=="srw_aa_bot" then f.AAReserve=(f.AAReserve or 0)+1
                elseif f.CurrentType and f.CurrentType~="srw_dynamit_bot" then
                    local field=f.CurrentType.."Reserve"; f[field]=(f[field] or 0)+1
                else f.Reserve = f.Reserve + 1 end
                f.LastType=f.CurrentType; f.CurrentType=nil
                f.CurrentSquad=nil
                f.Status = "ready"
            end
        elseif SRW.FactoryQueue(f)>0 then
            if SRW.FactoryReserve(f) >= SRW.FactoryCapacity(f) then
                f.Status = "reserve_full"
            else
                local balance = GetTeamResources(f.Team)
                local kinds={"srw_dynamit_bot","srw_hound","srw_repair_bot","srw_siege_bot","srw_aa_bot"}
                local fields={"Queue","HoundQueue","RepairQueue","SiegeQueue","AAQueue"}
                for i=6,#SRW.RobotKinds do kinds[i]=SRW.RobotKinds[i]; fields[i]=kinds[i].."Queue" end
                local previous=1
                for i,k in ipairs(kinds) do if f.LastType==k then previous=i end end
                local kind,field
                for offset=1,#kinds do
                    local i=(previous+offset-1)%#kinds+1
                    if (f[fields[i]] or 0)>0 then kind=kinds[i]; field=fields[i]; break end
                end
                if not kind and SRW.SquadPending and SRW.SquadPending(f)>0 then
                    kind=f.Squad.Items[f.Squad.Produced+1]
                end
                local cfg=SRW.Config.Robots[kind]
                if not SRW.FactoryCanProduce(f,kind) then
                    f.Status="tier_required"
                else
                local metal,energy=SRW.RobotCost(cfg,not field)
                if balance.metal >= metal and balance.energy >= energy then
                    AddResources(f.Team, { metal = -metal, energy = -energy }, false, Vec3(0, 0, 0))
                    if field then f[field]=f[field]-1 else f.CurrentSquad=true end
                    f.CurrentType=kind
                    f.Remaining = cfg.ProductionSeconds
                    f.Status = "building"
                else
                    f.Status = "resources"
                end
                end
            end
        end
        if SRW.UpdateSquadRelease then SRW.UpdateSquadRelease(f,id) end
    end
end

function SRW.ActiveCount(team,kind)
    local count = 0
    for id, bot in pairs(data.srw.Robots) do
        if bot.Team == team and DeviceExists(id) and (not kind or (bot.Kind or "srw_dynamit_bot")==kind) then count = count + 1 end
    end
    return count
end

function SRW.Release(team, id)
    local f = SRW.ValidFactory(team, id)
    if f and not SRW.FactoryCanProduce(f,"srw_dynamit_bot") then return end
    if not f then return end
    if f.Reserve < 1 then f.Status = "empty"; return end
    if SRW.ActiveCount(team,"srw_dynamit_bot") >= SRW.Config.Robots.srw_dynamit_bot.ActiveLimit then
        f.Status = "limit"; return
    end
    if not SRW.CanExit(f) then return end
    if SRW.SpawnRobot(team, id) then
        f.Reserve = f.Reserve - 1
        SRW.MarkExit(f,"srw_dynamit_bot")
    else
        f.Status = "exit_blocked"
    end
end

function SRW_OrderHound(team,id)
    local f=SRW.ValidFactory(tonumber(team),tonumber(id)); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_hound") then f.Status="tier_required";return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f)>=SRW.Config.Prototype.QueueLimit then f.Status="queue_full"; return end
    f.HoundQueue=(f.HoundQueue or 0)+1; f.Status="queued"
end

function SRW_ReleaseHound(team,id)
    team,id=tonumber(team),tonumber(id)
    local f=SRW.ValidFactory(team,id); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_hound") then f.Status="tier_required";return end
    if (f.HoundReserve or 0)<1 then f.Status="empty"; return end
    if SRW.ActiveCount(team,"srw_hound")>=SRW.Config.Robots.srw_hound.ActiveLimit then f.Status="limit"; return end
    if not SRW.CanExit(f) then return end
    if SRW.SpawnTank(team,id,"srw_hound") then f.HoundReserve=f.HoundReserve-1; SRW.MarkExit(f,"srw_hound")
    else f.Status="exit_blocked" end
end

function SRW_OrderRepair(team,id)
    local f=SRW.ValidFactory(tonumber(team),tonumber(id)); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_repair_bot") then f.Status="tier_required";return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f)>=SRW.Config.Prototype.QueueLimit then f.Status="queue_full"; return end
    f.RepairQueue=(f.RepairQueue or 0)+1; f.Status="queued"
end
function SRW_ReleaseRepair(team,id)
    team,id=tonumber(team),tonumber(id)
    local f=SRW.ValidFactory(team,id); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_repair_bot") then f.Status="tier_required";return end
    if (f.RepairReserve or 0)<1 then f.Status="empty"; return end
    if SRW.ActiveCount(team,"srw_repair_bot")>=SRW.Config.Robots.srw_repair_bot.ActiveLimit then
        f.Status="limit"; return
    end
    if not SRW.CanExit(f) then return end
    if SRW.SpawnRepairBot(team,id) then f.RepairReserve=f.RepairReserve-1; SRW.MarkExit(f,"srw_repair_bot")
    else f.Status="exit_blocked" end
end

function SRW_OrderSiege(team,id)
    local f=SRW.ValidFactory(tonumber(team),tonumber(id)); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_siege_bot") then f.Status="tier_required";return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f)>=SRW.Config.Prototype.QueueLimit then f.Status="queue_full"; return end
    f.SiegeQueue=(f.SiegeQueue or 0)+1; f.Status="queued"
end
function SRW_ReleaseSiege(team,id)
    team,id=tonumber(team),tonumber(id)
    local f=SRW.ValidFactory(team,id); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_siege_bot") then f.Status="tier_required";return end
    if (f.SiegeReserve or 0)<1 then f.Status="empty"; return end
    if SRW.ActiveCount(team,"srw_siege_bot")>=SRW.Config.Robots.srw_siege_bot.ActiveLimit then
        f.Status="limit"; return
    end
    if not SRW.CanExit(f) then return end
    if SRW.SpawnHound(team,id,"srw_siege_bot") then f.SiegeReserve=f.SiegeReserve-1; SRW.MarkExit(f,"srw_siege_bot")
    else f.Status="exit_blocked" end
end

function SRW_OrderAA(team,id)
    local f=SRW.ValidFactory(tonumber(team),tonumber(id)); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_aa_bot") then f.Status="tier_required";return end
    if (f.Tier or 1)<2 then f.Status="tier_required"; return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f)>=SRW.Config.Prototype.QueueLimit then f.Status="queue_full"; return end
    f.AAQueue=(f.AAQueue or 0)+1; f.Status="queued"
end
function SRW_ReleaseAA(team,id)
    team,id=tonumber(team),tonumber(id)
    local f=SRW.ValidFactory(team,id); if not f then return end
    if not SRW.FactoryCanProduce(f,"srw_aa_bot") then f.Status="tier_required";return end
    if (f.AAReserve or 0)<1 then f.Status="empty"; return end
    if SRW.ActiveCount(team,"srw_aa_bot")>=SRW.Config.Robots.srw_aa_bot.ActiveLimit then
        f.Status="limit"; return
    end
    if not SRW.CanExit(f) then return end
    if SRW.SpawnTank(team,id,"srw_aa_bot") then f.AAReserve=f.AAReserve-1; SRW.MarkExit(f,"srw_aa_bot")
    else f.Status="exit_blocked" end
end
