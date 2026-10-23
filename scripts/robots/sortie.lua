-- Fast aircraft keep flying through a bounded turn: pass, climb, orbit, repeat.
-- Pilotable Planes' lift/elevator model was inspected as a movement reference;
-- this is an independent device controller, not a copy of its projectile physics.
local function angle(x,y)
    if math.atan2 then return math.atan2(y,x) end
    if x==0 then return y>=0 and math.pi/2 or -math.pi/2 end
    local a=math.atan(y/x)
    if x<0 then a=a+(y>=0 and math.pi or -math.pi) end
    return a
end
local function difference(a,b) return (a-b+math.pi)%(2*math.pi)-math.pi end
local function clamp(v,n) return math.max(-n,math.min(n,v)) end
local function phase(bot,name)
    bot.SortiePhase=name;bot.SortieTime=0
    bot.AirPhase=name=="attack" and "attack" or "egress"
end
local function targetFor(bot,p,cfg)
    local best,rank,near
    local side=bot.Team%100==1 and 2 or 1
    for _,entry in ipairs(SRW.DeviceTargets(side)) do
        if not data.srw.MountedWeapons[entry.Id] then
            local dx,dy=entry.Position.x-p.x,entry.Position.y-p.y
            local distance=dx*dx+dy*dy
            if distance<=(cfg.Range*1.5)^2 then
                local other=SRW.Config.Robots[entry.Kind]
                local priority=other and (other.Air and 0 or 1) or 2
                if other and distance<=(cfg.ThreatRange or 3000)^2 then priority=priority-10 end
                if not rank or priority<rank or (priority==rank and (distance<near
                    or (distance==near and entry.Id<best.Id))) then
                    best,rank,near=entry,priority,distance
                end
            end
        end
    end
    return best
end
function SRW.SortieRocketsReady(id)
    local found=false
    for child,part in pairs(data.srw.MountedWeapons) do
        if part.Root==id and part.Kind=="srw_hornet_rockets" and DeviceExists(child) then
            found=true
            if (part.FireWait or 0)>0 or part.BurstRemaining or (part.EMPRemaining or 0)>0 then return false end
        end
    end
    return found
end

function SRW.UpdateSortieFlight(id,bot,dt)
    local cfg=SRW.Config.Robots[bot.Kind]
    bot.Age=(bot.Age or 0)+dt
    bot.AirVelocity={x=0,y=0}
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then
        bot.BurstRemaining=nil
        return
    end
    local p=GetDevicePosition(id)
    bot.SortieHeading=bot.SortieHeading or (bot.Direction<0 and math.pi or 0)
    if not bot.SortiePhase then phase(bot,"approach") end
    bot.SortieTime=(bot.SortieTime or 0)+dt
    local target=targetFor(bot,p,cfg)
    bot.SortieTarget=target and target.Id or nil
    local point=target and target.Position
    local goal
    local ready=SRW.SortieRocketsReady(id)
    if not point then
        if bot.SortiePhase~="orbit" then phase(bot,"orbit") end
        bot.SortieOrbitX=bot.HomeX or p.x
        bot.SortieOrbitY=bot.CruiseY or p.y
    elseif bot.SortiePhase=="approach" then
        bot.SortieRunDirection=bot.SortieRunDirection or (p.x<=point.x and 1 or -1)
        local dir=bot.SortieRunDirection
        goal=Vec3(point.x-dir*cfg.RunInDistance,point.y-cfg.PassAltitude,0)
        local dx,dy=point.x-p.x,point.y-p.y
        local distance=math.sqrt(dx*dx+dy*dy)
        local aligned=distance>1 and (dx*math.cos(bot.SortieHeading)+dy*math.sin(bot.SortieHeading))/distance>.92
        if (goal.x-p.x)^2+(goal.y-p.y)^2<300^2
            or (aligned and distance<cfg.PassRange and math.abs(dy)<cfg.PassAltitude*2) then
            phase(bot,"attack")
            bot.SortieGunOnly=not ready
            bot.SortieRocketStart=bot.HornetRocketSerial or 0
            bot.SortieGunStart=bot.HornetGunSerial or 0
        end
    elseif bot.SortiePhase=="attack" then
        local dir=bot.SortieRunDirection or bot.Direction
        goal=Vec3(point.x+dir*cfg.RunOutDistance,point.y-cfg.PassAltitude,0)
        local gunDone=(bot.HornetGunSerial or 0)~=bot.SortieGunStart and not bot.BurstRemaining
        local rocketsDone=(bot.HornetRocketSerial or 0)~=bot.SortieRocketStart
        for _,part in pairs(data.srw.MountedWeapons) do
            if part.Root==id and part.BurstRemaining then rocketsDone=false end
        end
        if bot.SortieTime>=cfg.AttackSeconds or dir*(p.x-point.x)>cfg.RunOutDistance
            or (bot.SortieTime>=.4 and gunDone and (bot.SortieGunOnly or rocketsDone)) then
            phase(bot,"egress")
            bot.SortieEgressX=p.x+math.cos(bot.SortieHeading)*cfg.RunOutDistance
            bot.SortieEgressY=p.y-cfg.BreakClimb
            bot.Target=nil;bot.BurstRemaining=nil
        end
    elseif bot.SortiePhase=="egress" then
        goal=Vec3(bot.SortieEgressX or p.x,bot.SortieEgressY or p.y-400,0)
        if bot.SortieTime>=cfg.EgressSeconds then
            phase(bot,"orbit")
            bot.SortieOrbitX=point.x-(bot.SortieRunDirection or bot.Direction)*cfg.OrbitStandOff
            bot.SortieOrbitY=point.y-cfg.OrbitAltitude
            bot.SortieOrbitAngle=angle((p.x-bot.SortieOrbitX)/cfg.OrbitRadiusX,
                (p.y-bot.SortieOrbitY)/cfg.OrbitRadiusY)
        end
    end
    if bot.SortiePhase=="orbit" then
        local cx,cy=bot.SortieOrbitX or p.x,bot.SortieOrbitY or bot.CruiseY or p.y
        bot.SortieOrbitAngle=(bot.SortieOrbitAngle or 0)+bot.Direction*cfg.OrbitRate*dt
        local a=bot.SortieOrbitAngle+bot.Direction*.4
        goal=Vec3(cx+cfg.OrbitRadiusX*math.cos(a),cy+cfg.OrbitRadiusY*math.sin(a),0)
        if point and ((ready and bot.SortieTime>=cfg.MinimumOrbitSeconds)
            or bot.SortieTime>=cfg.GunDiveSeconds) then
            phase(bot,"approach");bot.SortieRunDirection=nil
        end
    end
    goal=goal or Vec3(p.x+math.cos(bot.SortieHeading)*500,p.y+math.sin(bot.SortieHeading)*500,0)
    -- Steer above terrain before the short movement ray can reach it.
    if CastGroundRay(Vec3(goal.x,p.y-1000,0),Vec3(goal.x,p.y+5000,0),0)==RAY_HIT_TERRAIN then
        goal.y=math.min(goal.y,GetRayHitPosition().y-cfg.TerrainClearance)
    end
    local desired=angle(goal.x-p.x,goal.y-p.y)
    bot.SortieHeading=bot.SortieHeading+clamp(difference(desired,bot.SortieHeading),cfg.SortieTurnRate*dt)
    local speed=SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth
    local q=Vec3(p.x+math.cos(bot.SortieHeading)*speed*dt,p.y+math.sin(bot.SortieHeading)*speed*dt,0)
    local centre=GetDeviceCentrePosition(id)
    local destination=Vec3(centre.x+q.x-p.x,centre.y+q.y-p.y,0)
    if CastGroundRay(p,q,0)==RAY_HIT_TERRAIN
        or (SRW.MovementRay or CastRayFromDevice)(id,destination,0,RAY_EXCLUDE_BG_MATERIALS,0)~=RAY_HIT_NOTHING then
        bot.SortieHeading=bot.SortieHeading+clamp(difference(-math.pi/2,bot.SortieHeading),cfg.SortieTurnRate*dt)
        return
    end
    dlc2_SetDevicePosition(id,q)
    bot.AirVelocity={x=(q.x-p.x)/dt,y=(q.y-p.y)/dt}
    if math.abs(bot.AirVelocity.x)>speed*.1 then bot.ArtFacing=bot.AirVelocity.x<0 and -1 or 1 end
    bot.AirHeading=bot.ArtFacing or bot.Direction
    -- Guns only fire on an aligned pass. Root/mount cooldowns keep ticking while
    -- orbiting; no position lock is introduced for these individually fired rounds.
    local aligned=false
    if point then
        local dx,dy=point.x-q.x,point.y-q.y
        local distance=math.sqrt(dx*dx+dy*dy)
        aligned=distance>1 and (dx*math.cos(bot.SortieHeading)+dy*math.sin(bot.SortieHeading))/distance>.35
    end
    bot.AirPhase=bot.SortiePhase=="attack" and aligned and "attack" or "egress"
    if bot.AirPhase=="attack" then SRW.UpdateAirWeapon(id,bot,dt)
    else
        bot.Target=nil;bot.BurstRemaining=nil
        bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
    end
end
