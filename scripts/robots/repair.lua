function SRW.SpawnRepairBot(team,factory,kind)
    kind=kind or "srw_repair_bot"
    local p=GetDevicePosition(factory)
    local direction=team%100==1 and 1 or -1
    local ground=SRW.GroundAt(p.x+direction*SRW.Config.Prototype.ExitOffset,p.y,100)
    if not ground then return false end
    EnableDevice(kind,true,team%100)
    local id=dlc2_CreateFloatingDevice(team,kind,ground,90)
    EnableDevice(kind,false,team%100)
    if not id or id<0 then return false end
    data.srw.Robots[id]={Team=team,Direction=direction,Age=0,Kind=kind}
    Log("[SRW] Repair bot "..id.." spawned, owner "..team)
    return true,id
end

function SRW.UpdateRepairBot(id,bot,dt)
    if not DeviceExists(id) or GetDeviceTeamIdActual(id)~=bot.Team
        or DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then bot.Target=nil; return end
    local cfg=SRW.Config.Robots.srw_repair_bot
    local p=GetDevicePosition(id)
    local centre=GetDeviceCentrePosition(id)
    local target,health,distance,escort,escortDistance
    -- Only SRW robots; deterministic health/distance/id priority.
    for _,other in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local candidate=data.srw.Robots[other]
        if other~=id and candidate.Team%100==bot.Team%100 and DeviceExists(other)
            and GetDeviceTeamIdActual(other)%100==bot.Team%100
            and IsDeviceFullyBuilt(other) and not candidate.FuseRemaining then
            local q=GetDeviceCentrePosition(other)
            local d=(q.x-centre.x)^2+(q.y-centre.y)^2
            local hp=GetDeviceHealth(other)
            if d<=cfg.SearchRange^2 and hp>0 and hp<1 then
                if not health or hp<health or (hp==health and d<distance) then
                    target,health,distance=other,hp,d
                end
            end
            if candidate.Kind~="srw_repair_bot" and (q.x-centre.x)*bot.Direction>=0
                and (not escortDistance or d<escortDistance) then
                escort,escortDistance=other,d
            end
        end
    end
    bot.RepairWait=math.max(0,(bot.RepairWait or 0)-dt)
    bot.Target=target
    if target and distance<=cfg.RepairRange^2 then
        if bot.RepairWait<=0.000001 then
            local before=GetDeviceHitpoints(target)
            local fraction=GetDeviceHealth(target)
            local missing=fraction>0 and before/fraction-before or 0
            local amount=math.min(cfg.RepairHPPerSecond*cfg.RepairInterval,missing)
            local balance=GetTeamResources(bot.Team)
            amount=math.min(amount,math.max(0,balance.metal)/cfg.RepairMetalPerHP,
                math.max(0,balance.energy)/cfg.RepairEnergyPerHP)
            if amount>0.000001 then
                -- Negative damage is used for healing by existing Forts mods.
                -- Measure the actual gain; never charge for a rejected repair.
                ApplyDamageToDevice(target,-amount)
                local restored=DeviceExists(target) and math.max(0,math.min(amount,GetDeviceHitpoints(target)-before)) or 0
                if restored>0 then
                    AddResources(bot.Team,{metal=-restored*cfg.RepairMetalPerHP,
                        energy=-restored*cfg.RepairEnergyPerHP},false,Vec3(0,0,0))
                end
            end
            bot.RepairWait=cfg.RepairInterval
        end
        return
    end
    local destinationId=target or escort
    -- Wait for the squad rather than walking into the enemy alone.
    if not destinationId or (not target and escortDistance<=cfg.FollowDistance^2) then return end
    local q=GetDeviceCentrePosition(destinationId)
    local direction=q.x>=centre.x and 1 or -1
    local step=math.min(math.abs(q.x-centre.x),SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth*dt)
    local ground=SRW.GroundAt(p.x+direction*step,p.y,SRW.Config.Prototype.StepHeight)
    if not ground then return end
    local destination=Vec3(centre.x+ground.x-p.x,centre.y+ground.y-p.y,0)
    if (SRW.MovementRay or CastRayFromDevice)(id,destination,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING then
        dlc2_SetDevicePosition(id,ground)
    end
end
