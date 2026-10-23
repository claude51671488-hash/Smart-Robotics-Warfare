-- Constant-velocity interception; homing/gravity can change the actual path.
function SRW.InterceptPoint(origin,p,v,speed)
    local x,y=p.x-origin.x,p.y-origin.y
    local a=v.x*v.x+v.y*v.y-speed*speed
    local b=2*(x*v.x+y*v.y); local c=x*x+y*y
    local t
    if math.abs(a)<0.000001 then
        if math.abs(b)>0.000001 then t=-c/b end
    else
        local discriminant=b*b-4*a*c
        if discriminant<0 then return end
        local r=math.sqrt(discriminant)
        local t1,t2=(-b-r)/(2*a),(-b+r)/(2*a)
        if t1>0 then t=t1 end
        if t2>0 and (not t or t2<t) then t=t2 end
    end
    if not t or t<=0 or t>2 then return end
    return Vec3(p.x+v.x*t,p.y+v.y*t,0)
end

function SRW.UpdateAABot(id,bot,dt)
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then bot.Target=nil; return end
    if (bot.Kind=="srw_tank_rockets" or bot.Kind=="srw_sentry_rockets") and (bot.EMPRemaining or 0)>0 then bot.Target=nil; return end
    local cfg=SRW.Config.Robots[bot.Kind or "srw_aa_bot"]
    if cfg.Guided and (bot.EMPRemaining or 0)>0 then bot.Target=nil; return end
    local origin=GetWeaponHardpointPosition and GetWeaponHardpointPosition(id) or GetDeviceCentrePosition(id)
    local root=bot.Root and data.srw.Robots[bot.Root] or bot
    if bot.Mounted and cfg.RequiresBrace and not (root and root.Braced) then bot.Target=nil; return end
    local rootId=bot.Root or id
    local groundY=GetDevicePosition(rootId).y+(root and root.GroundLift or 0)
    bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
    if (bot.BeamRemaining or 0)>0 then
        bot.BeamRemaining=math.max(0,bot.BeamRemaining-dt)
        return
    end
    if bot.FireWait>0 then return end
    bot.FireWait=cfg.ScanInterval or cfg.FireInterval -- native reload also gates actual shots
    bot.Target=nil
    local side=bot.Team%100==1 and 2 or 1
    local targets={}
    for _,entry in ipairs(SRW.AirTargets(side)) do
        local node=entry.Id
        if SRW.AirTargetAlive(entry,side) then
            local p=entry.Position
            local dx,dy=p.x-origin.x,p.y-origin.y
            local distance=dx*dx+dy*dy
            -- A high rear launcher can be above an airborne threat. Classify
            -- altitude from the robot's feet, not from this elevated hardpoint.
            if distance<=cfg.Range^2 and (cfg.Air or p.y<groundY-30) then
                local name=not entry.IsDevice and GetNodeProjectileSaveName(node)
                if entry.IsDevice or GetProjectileParamFloat(name,NodeTeam(node),"ProjectileShootDownRadius",0)>0 then
                    local v=SRW.AirTargetVelocity(entry)
                    -- Guided missiles acquire at full sensor range; a two-second
                    -- gun intercept limit must not truncate their launch range.
                    local aim=(cfg.InstantBeam or cfg.Guided) and p or (SRW.BallisticIntercept
                        and SRW.BallisticIntercept(origin,p,v,cfg.BulletSpeed,981,2))
                        or SRW.InterceptPoint(origin,p,v,cfg.BulletSpeed)
                    local threat=0
                    if cfg.PrioritizeDamage and not entry.IsDevice then
                        threat=GetProjectileParamFloat(name,NodeTeam(node),"ProjectileDamage",0)
                            +GetProjectileParamFloat(name,NodeTeam(node),"ProjectileSplashDamage",0)
                    end
                    if aim then targets[#targets+1]={Id=node,IsDevice=entry.IsDevice,Aim=aim,Distance=distance,Threat=threat,
                        Priority=dx*v.x+dy*v.y<0 and 0 or 1} end
                end
            end
        end
    end
    table.sort(targets,function(a,b)
        if a.Priority~=b.Priority then return a.Priority<b.Priority end
        if a.Threat~=b.Threat then return a.Threat>b.Threat end
        if a.Distance~=b.Distance then return a.Distance<b.Distance end
        return a.Id<b.Id
    end)
    for _,target in ipairs(targets) do
        if cfg.RequiresBrace and not (root and root.Braced) then return end
        local canAim=SRW.CanAimRobotWeapon and SRW.CanAimRobotWeapon(id,cfg,target.Aim)
            or (not SRW.CanAimRobotWeapon and AimWeapon(id,SRW.LaunchAim(id,cfg,target.Aim)))
        if canAim then
            bot.Target=target.Id;bot.TargetIsDevice=target.IsDevice==true
            local aim=SRW.EMPAim and SRW.EMPAim(id,bot,target.Aim) or target.Aim
            local spread=cfg.InstantBeam and 0 or 0.1
            local result=SRW.FireRobotWeapon and SRW.FireRobotWeapon(id,cfg,aim,spread)
                or FireWeapon(id,SRW.LaunchAim(id,cfg,aim),spread,FIREFLAG_NORMAL)
            if result==(FIRE_SUCCESS or 0) and cfg.BeamHoldSeconds then
                bot.BeamRemaining=cfg.BeamHoldSeconds
                bot.FireWait=cfg.FireInterval
            end
            return
        end
    end
    if bot.Mounted or bot.SpacingThisTick or bot.BraceActive then return end
    -- The escort may already be inside an enemy base. Stay outside it and let
    -- the independent defence guns engage ground threats.
    local feet=SRW.RobotGroundPosition and SRW.RobotGroundPosition(id,bot) or GetDevicePosition(id)
    local wall=SRW.EnemyBeamDistance and SRW.EnemyBeamDistance(feet,side)
    if wall and wall<(cfg.GroundStandoff or 900) then return end
    for _,entry in ipairs(SRW.DeviceTargets(side)) do
        if (entry.Position.x-feet.x)^2+(entry.Position.y-feet.y)^2<(cfg.GroundStandoff or 900)^2 then return end
    end
    -- Follow a friendly combat robot; do not attack ground targets in this prototype.
    local escort,distance
    for _,other in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local r=data.srw.Robots[other]
        if other~=id and r.Kind~="srw_pike_bot" and r.Kind~="srw_sentry_bot" and r.Kind~="srw_aa_bot" and r.Kind~="srw_heavy_aa_bot" and r.Kind~="srw_shield_bot" and r.Kind~="srw_repair_bot"
            and r.Team%100==bot.Team%100 and DeviceExists(other)
            and GetDeviceTeamIdActual(other)%100==bot.Team%100 then
            local q=GetDeviceCentrePosition(other)
            local dx=q.x-origin.x
            if dx*bot.Direction>cfg.FollowDistance and (not distance or math.abs(dx)<distance) then
                escort=other; distance=math.abs(dx)
            end
        end
    end
    if not escort then return end
    local p=GetDevicePosition(id)
    local step=math.min(distance-cfg.FollowDistance,SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth*cfg.FireInterval)
    local x=p.x+bot.Direction*step
    local ground=SRW.RobotGroundStep and SRW.RobotGroundStep(id,bot,x)
        or (not SRW.RobotGroundStep and SRW.GroundAt(x,p.y,SRW.Config.Prototype.StepHeight))
    if not ground then return end
    local destination=Vec3(origin.x+ground.x-p.x,origin.y+ground.y-p.y,0)
    if (SRW.MovementRay or CastRayFromDevice)(id,destination,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING then dlc2_SetDevicePosition(id,ground) end
end

-- Program each fuse at launch; no global per-frame shell scans.
function SRW.SieveLaunch(team,weapon,node)
    if not NodeExists(node) or GetNodeProjectileSaveName(node)~="srw_sieve_flak" then return end
    local bot=data.srw.Robots[weapon] or data.srw.MountedWeapons[weapon]
    if not bot or bot.Team~=team then return end
    local p=NodePosition(node); local v=NodeVelocity(node)
    local speed=math.sqrt(v.x*v.x+v.y*v.y)
    local delay=0.6
    local entry={Id=bot.Target,IsDevice=bot.TargetIsDevice}
    if speed>1 and bot.Target and SRW.AirTargetAlive(entry,team%100==1 and 2 or 1) then
        local q=entry.IsDevice and GetDeviceCentrePosition(entry.Id) or NodePosition(entry.Id)
        local aim=SRW.InterceptPoint(p,q,SRW.AirTargetVelocity(entry),speed)
        if aim then delay=math.sqrt((aim.x-p.x)^2+(aim.y-p.y)^2)/speed end
    end
    SetNodeProjectileAgeTrigger(node,math.max(0.03,math.min(1.5,delay)))
end
