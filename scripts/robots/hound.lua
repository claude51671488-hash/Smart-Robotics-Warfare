-- CreateFloatingDevice already receives the upright platform normal in degrees.
-- Native trial: creation(90) -> GetDeviceAngle=pi/2. SetDeviceAngle takes radians.
-- The weapon's own traverse covers both teams; never rotate its whole platform.
function SRW.OrientRobotWeapon(id,direction)
    -- Keep the platform upright; aiming rotates the barrel independently.
end

function SRW.LaunchAim(id,cfg,target)
    if not cfg.Guided then return target end
    if SetWeaponPaintTarget then SetWeaponPaintTarget(id,target) end
    -- Swarm launchers have a fixed vertical launch arc. The painted destination
    -- belongs to the seeker; it is not a reachable barrel angle for the silo.
    local p=GetWeaponHardpointPosition and GetWeaponHardpointPosition(id) or GetDeviceCentrePosition(id)
    return Vec3(p.x,p.y-5000,0)
end

function SRW.SpawnHound(team,factory,kind)
    kind=kind or "srw_hound"
    local p=GetDevicePosition(factory); local direction=team%100==1 and 1 or -1
    local ground=SRW.GroundAt(p.x+direction*SRW.Config.Prototype.ExitOffset,p.y,100)
    if not ground then return false end
    local lift=SRW.Config.Robots[kind].RootLift or 0
    local position=Vec3(ground.x,ground.y-lift,0)
    EnableWeapon(kind,true,team%100)
    local id=dlc2_CreateFloatingDevice(team,kind,position,90)
    EnableWeapon(kind,false,team%100)
    if not id or id<0 then return false end
    SRW.OrientRobotWeapon(id,direction)
    data.srw.Robots[id]={Team=team,Direction=direction,Age=0,Kind=kind,GroundLift=lift}
    Log("[SRW] "..kind.." "..id.." spawned, owner "..team)
    return true,id
end

function SRW.UpdateHound(id,bot,dt)
    bot.CombatClock=(bot.CombatClock or 0)+dt
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then
        bot.DeployRemaining=nil; bot.DeployPosition=nil; bot.ChargeRemaining=nil; bot.ChargeTarget=nil; bot.BurstRemaining=nil
        return
    end
    local cfg=SRW.Config.Robots[bot.Kind or "srw_hound"]
    if (bot.Kind=="srw_rocket_bot" or cfg.Guided) and (bot.EMPRemaining or 0)>0 then bot.Target=nil; return end
    local p=GetDevicePosition(id); local centre=GetDeviceCentrePosition(id)
    -- Freeze position and aim until the continuous beam and its firing delay finish.
    if not bot.Mounted then
        for _,part in pairs(data.srw.MountedWeapons or {}) do
            local partCfg=SRW.Config.Robots[part.Kind] or {}
            if part.Root==id and (part.Kind=="srw_colossus_laser" or partCfg.LockRootDuringBeam)
                and (part.BeamRemaining or 0)>0 then return end
        end
    end
    if (bot.BeamRemaining or 0)>0 then
        bot.BeamRemaining=math.max(0,bot.BeamRemaining-dt)
        bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
        return
    end
    local enemy=bot.Team%100==1 and 2 or 1
    local candidates={}
    local retreat=false
    for _,entry in ipairs(SRW.DeviceTargets(enemy)) do
        local target=entry.Id
        if DeviceExists(target) and GetDeviceTeamIdActual(target)%100==enemy then
            local q=entry.Position
            local distance=(q.x-centre.x)^2+(q.y-centre.y)^2
            if distance<=cfg.Range^2 then
                if cfg.MinimumRange and distance<cfg.MinimumRange^2 then
                    retreat=true
                else
                    local isRobot=SRW.Config.Robots[entry.Kind]~=nil
                    local runningGear=string.find(entry.Kind,"wheel") or string.find(entry.Kind,"track")
                    local priority=isRobot and 0 or 1
                    if cfg.PreferStructures then priority=isRobot and 1 or 0 end
                    if cfg.PreferHeavyRobots and isRobot then priority=-(SRW.Config.Robots[entry.Kind].Tier or 1) end
                    if cfg.PreferAirRobots and isRobot and SRW.Config.Robots[entry.Kind].Air then priority=-1 end
                    if cfg.PreferGroundRobots and isRobot and not SRW.Config.Robots[entry.Kind].Air then priority=-1 end
                    if runningGear then priority=4 end
                    -- A nearby combat robot outranks the preferred siege target.
                    -- Wheel/track parts are still a last resort.
                    local immediate=isRobot and not runningGear and distance<=(cfg.ThreatRange or 2400)^2
                    candidates[#candidates+1]={Id=target,Position=q,Distance=distance,Priority=priority,
                        Immediate=immediate and 1 or 0}
                end
            end
        end
    end
    if cfg.EMPRadius and SRW.RankEMPTargets and (bot.FireWait or 0)<=dt then
        candidates=SRW.RankEMPTargets(candidates,cfg.EMPRadius)
    end
    local onlyRunningGear=#candidates>0
    for _,candidate in ipairs(candidates) do if candidate.Priority<4 then onlyRunningGear=false end end
    if (#candidates==0 or onlyRunningGear) and SRW.BeamTargets then
        for _,target in ipairs(SRW.BeamTargets(centre,enemy,cfg.Range,bot.Direction)) do
            if not cfg.MinimumRange or target.Distance>=cfg.MinimumRange^2 then
                candidates[#candidates+1]=target
            end
        end
    end
    table.sort(candidates,function(a,b)
        if (a.Immediate or 0)~=(b.Immediate or 0) then return (a.Immediate or 0)>(b.Immediate or 0) end
        if (a.EMPScore or 0)~=(b.EMPScore or 0) then return (a.EMPScore or 0)>(b.EMPScore or 0) end
        if a.Priority~=b.Priority then return a.Priority<b.Priority end
        if a.Distance~=b.Distance then return a.Distance<b.Distance end
        return a.Id<b.Id
    end)
    bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
    for index,target in ipairs(candidates) do
        -- Do not trace six terrain segments against every device on a large fort.
        -- The next tick re-evaluates the nearest/highest-priority candidates.
        if index>8 then break end
        local aimPoint,spread,worthwhile=target.Position,0,true
        if SRW.AimSolution then aimPoint,spread,worthwhile=SRW.AimSolution(id,bot,cfg,target,dt,false) end
        local clear=true
        if SRW.ShotClearsTerrain then
            clear=SRW.ShotClearsTerrain(id,cfg,aimPoint)
        elseif SRW.AimSolution and not cfg.Artillery and CastGroundRay then
            clear=CastGroundRay(centre,aimPoint,0)~=RAY_HIT_TERRAIN
        end
        if clear and SRW.ShotClearsAircraft then clear=SRW.ShotClearsAircraft(id,bot,cfg,aimPoint) end
        local launch=SRW.LaunchAim(id,cfg,aimPoint)
        local canAim=SRW.CanAimRobotWeapon and SRW.CanAimRobotWeapon(id,cfg,aimPoint)
            or (not SRW.CanAimRobotWeapon and AimWeapon(id,launch))
        if worthwhile and clear and canAim then
            bot.Target=target.Id
            bot.TargetIsDevice=not target.Beam
            bot.TargetPoint=target.Beam and {x=target.Position.x,y=target.Position.y} or nil
            if cfg.DeploySeconds then
                local prev=bot.DeployPosition
                if not prev or (p.x-prev.x)^2+(p.y-prev.y)^2>1
                    or (cfg.HoverFire and bot.DeployTarget~=target.Id) then
                    bot.DeployRemaining=cfg.DeploySeconds
                    bot.DeployPosition={x=p.x,y=p.y}
                    bot.DeployTarget=target.Id
                    bot.ChargeRemaining=nil; bot.ChargeTarget=nil
                end
                if (bot.DeployRemaining or 0)>0 then
                    bot.DeployRemaining=math.max(0,bot.DeployRemaining-dt)
                    return
                end
                if bot.FireWait>0 then return end
                if bot.ChargeTarget~=target.Id then
                    bot.ChargeTarget=target.Id; bot.ChargeRemaining=cfg.ChargeSeconds
                end
                bot.ChargeRemaining=math.max(0,(bot.ChargeRemaining or 0)-dt)
                if bot.ChargeRemaining>0.000001 then return end
            end
            if cfg.AimSeconds then
                if bot.AimTarget~=target.Id then
                    bot.AimTarget=target.Id; bot.AimRemaining=cfg.AimSeconds
                end
                bot.AimRemaining=math.max(0,(bot.AimRemaining or 0)-dt)
                if bot.AimRemaining>0.000001 then return end
            end
            if bot.FireWait==0 then
                if SRW.CanPowerWeapon and not SRW.CanPowerWeapon(bot,cfg) then return end
                if SRW.AimSolution then aimPoint,spread=SRW.AimSolution(id,bot,cfg,target,dt,true) end
                local aim=SRW.EMPAim and SRW.EMPAim(id,bot,aimPoint) or aimPoint
                local result=SRW.FireRobotWeapon and SRW.FireRobotWeapon(id,cfg,aim,spread)
                    or FireWeapon(id,SRW.LaunchAim(id,cfg,aim),spread,FIREFLAG_NORMAL)
                if result==(FIRE_SUCCESS or 0) then bot.RangingShots=math.min(8,(bot.RangingShots or 0)+1) end
                if result==(FIRE_SUCCESS or 0) and cfg.DeploySeconds then
                    bot.ChargeTarget=nil; bot.ChargeRemaining=nil
                end
                if result==(FIRE_SUCCESS or 0) and SRW.UseWeaponPower then SRW.UseWeaponPower(bot,cfg) end
                if result==(FIRE_SUCCESS or 0) and cfg.BeamHoldSeconds then bot.BeamRemaining=cfg.BeamHoldSeconds end
                bot.FireWait=result==(FIRE_SUCCESS or 0) and (cfg.ReloadSeconds or 2) or 0.2
                if result==(FIRE_SUCCESS or 0) and cfg.BurstCount then
                    bot.BurstRemaining=(bot.BurstRemaining or cfg.BurstCount)-1
                    if bot.BurstRemaining>0 then bot.FireWait=cfg.BurstPeriod
                    else bot.BurstRemaining=nil end
                end
                -- Normal reload/success cycling is not an error and used to flood logs.
                if result~=(FIRE_SUCCESS or 0) and result~=(FIRE_RELOADING or 5)
                    and bot.LastFireResult~=result then
                    Log("[SRW] "..(bot.Kind or "srw_hound").." "..id.." fire result="..tostring(result))
                    bot.LastFireResult=result
                end
            end
            return -- Stop while engaging, including during native reload.
        end
    end
    bot.Target=nil
    bot.DeployPosition=nil; bot.DeployRemaining=nil; bot.ChargeTarget=nil; bot.ChargeRemaining=nil
    bot.AimTarget=nil; bot.AimRemaining=nil
    if bot.Mounted or bot.SpacingThisTick then return end
    local direction=retreat and -bot.Direction or bot.Direction
    local x=p.x+direction*SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth*dt
    local ground=SRW.RobotGroundStep and SRW.RobotGroundStep(id,bot,x)
        or (not SRW.RobotGroundStep and SRW.GroundAt(x,p.y,SRW.Config.Prototype.StepHeight))
    if not ground then return end
    local destination=Vec3(centre.x+ground.x-p.x,centre.y+ground.y-p.y,0)
    if (SRW.MovementRay or CastRayFromDevice)(id,destination,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING then
        dlc2_SetDevicePosition(id,ground)
    end
end
