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
-- One rigid flight frame for hull and hatch positions. Keep the selected team
-- silhouette through the whole loop; swapping mirrors at vertical flight would
-- snap the upper/lower surfaces and move the gun to the other side of the hull.
function SRW.HornetRigPoint(bot,p,x,y)
    local pitch=bot.FlightPitch or 0
    local c,s=math.cos(pitch),math.sin(pitch)
    x=x*bot.Direction
    return Vec3(p.x+x*c-y*s,p.y+x*s+y*c,0)
end
local function orientHull(id,bot)
    if bot.Kind~="srw_hornet_bot" then return end
    local pitch=bot.SortieHeading-(bot.Direction<0 and math.pi or 0)
    -- Native probe: angle 0 -> forward (0,1), pi/2 -> (1,0), for both teams.
    -- SetDeviceAngle takes radians, unlike floating-device creation (degrees).
    if not bot.FlightPitch or math.abs(pitch-bot.FlightPitch)>.000001 then
        SetDeviceAngle(id,math.pi/2-pitch)
    end
    bot.FlightPitch=pitch
    bot.ArtFacing=bot.Direction
end
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

local function startOrbit(bot,p,cfg,cx,cy)
    phase(bot,"orbit")
    bot.SortieOrbitX=cx;bot.SortieOrbitY=cy
    bot.SortieOrbitDirection=-(bot.SortieEscapeDirection or bot.SortieRunDirection or bot.Direction)
    bot.SortieOrbitObserved=angle((p.x-cx)/cfg.OrbitRadiusX,(p.y-cy)/cfg.OrbitRadiusY)
    bot.SortieOrbitSweep=0
end

-- Restore the projectile look-ahead that the new sortie path used to bypass.
-- Only closing hostile rounds count; an enemy aircraft is not itself a shot.
local function incomingFire(bot,p,cfg,dt,velocity)
    bot.EvadeScan=math.max(0,(bot.EvadeScan or 0)-dt)
    bot.EvadeRemaining=math.max(0,(bot.EvadeRemaining or 0)-dt)
    if not cfg.EvasiveFlight or bot.EvadeScan>0 then return false end
    bot.EvadeScan=.2
    local side=bot.Team%100==1 and 2 or 1
    local seen=0
    for _,entry in ipairs(SRW.AirTargets(side)) do
        if not entry.IsDevice and SRW.AirTargetAlive(entry,side) then
            seen=seen+1;if seen>128 then break end
            local v=SRW.AirTargetVelocity(entry)
            local dx,dy=entry.Position.x-p.x,entry.Position.y-p.y
            local vx,vy=v.x-velocity.x,v.y-velocity.y
            local v2=vx*vx+vy*vy
            local t=v2>1 and -(dx*vx+dy*vy)/v2 or -1
            if t>0 and t<.85 and (dx+vx*t)^2+(dy+vy*t)^2<260^2 then
                bot.EvadeRemaining=cfg.EgressSeconds
                bot.EvadeSign=dy+vy*t>=0 and -1 or 1
                return true
            end
        end
    end
    return false
end

local function startEgress(bot,p,cfg)
    phase(bot,"egress")
    bot.SortieEgressX=p.x+math.cos(bot.SortieHeading)*cfg.RunOutDistance
    bot.SortieEgressY=p.y-cfg.BreakClimb
    bot.Target=nil;bot.BurstRemaining=nil
end

function SRW.UpdateSortieFlight(id,bot,dt)
    local cfg=SRW.Config.Robots[bot.Kind]
    bot.Age=(bot.Age or 0)+dt
    local previousVelocity=bot.AirVelocity or {x=0,y=0}
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
    local incoming=incomingFire(bot,p,cfg,dt,previousVelocity)
    if incoming then
        -- The last attack target is a conservative keep-out anchor, not a claim
        -- that the snapshot identifies which gun fired an incoming projectile.
        if not bot.SortieDangerX then
            bot.SortieDangerX=point and point.x or p.x
            bot.SortieDangerY=point and point.y or p.y
            bot.SortieEscapeDirection=p.x==bot.SortieDangerX
                and (math.cos(bot.SortieHeading)>=0 and 1 or -1)
                or (p.x>bot.SortieDangerX and 1 or -1)
        end
        bot.SortieSafetyExtra=math.min(cfg.OrbitStandOff,
            (bot.SortieSafetyExtra or 0)+(cfg.WeaveHeight or 300))
        local dx,dy=p.x-bot.SortieDangerX,p.y-bot.SortieDangerY
        local clearance=cfg.OrbitStandOff+bot.SortieSafetyExtra
        if bot.SortiePhase~="egress" and (bot.SortiePhase~="orbit" or dx*dx+dy*dy<clearance^2) then
            startEgress(bot,p,cfg)
        end
    end
    if not point and bot.SortiePhase~="egress" and bot.SortiePhase~="orbit" then
        startOrbit(bot,p,cfg,bot.HomeX or p.x,bot.CruiseY or p.y)
    end
    if point and bot.SortiePhase=="approach" then
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
            startEgress(bot,p,cfg)
        end
    end
    if bot.SortiePhase=="egress" then
        goal=Vec3(bot.SortieEgressX or p.x,bot.SortieEgressY or p.y-400,0)
        local clear=true
        local anchor=point or {x=bot.HomeX or p.x,y=bot.CruiseY or p.y}
        local outward=bot.SortieRunDirection or bot.Direction
        local extra=0
        if bot.SortieDangerX then
            anchor={x=bot.SortieDangerX,y=bot.SortieDangerY}
            outward=bot.SortieEscapeDirection
            extra=bot.SortieSafetyExtra or 0
            local separation=cfg.OrbitStandOff+extra
            local dx,dy=p.x-anchor.x,p.y-anchor.y
            clear=dx*dx+dy*dy>=separation^2
            goal=Vec3(anchor.x+outward*(separation+cfg.OrbitRadiusX),
                math.min(p.y,anchor.y-cfg.OrbitAltitude)-cfg.BreakClimb,0)
        end
        if bot.SortieTime>=cfg.EgressSeconds and clear then
            -- Keep the waiting loop on the side just exited. The previous minus
            -- sign sent aircraft back through the defended target to reach it.
            startOrbit(bot,p,cfg,anchor.x+outward*(cfg.OrbitStandOff+extra),
                anchor.y-cfg.OrbitAltitude-extra*.25)
        end
    end
    if bot.SortiePhase=="orbit" then
        local cx,cy=bot.SortieOrbitX or p.x,bot.SortieOrbitY or bot.CruiseY or p.y
        local a=angle((p.x-cx)/cfg.OrbitRadiusX,(p.y-cy)/cfg.OrbitRadiusY)
        local direction=bot.SortieOrbitDirection or -(bot.SortieRunDirection or bot.Direction)
        -- Count actual signed progress, not a clock advancing a disconnected
        -- waypoint. Reversals subtract progress instead of completing a loop.
        bot.SortieOrbitSweep=math.max(0,(bot.SortieOrbitSweep or 0)
            +difference(a,bot.SortieOrbitObserved or a)*direction)
        bot.SortieOrbitObserved=a
        local lookahead=a+direction*.55
        goal=Vec3(cx+cfg.OrbitRadiusX*math.cos(lookahead),cy+cfg.OrbitRadiusY*math.sin(lookahead),0)
        if point and bot.SortieOrbitSweep>=2*math.pi and bot.EvadeRemaining==0
            and ((ready and bot.SortieTime>=cfg.MinimumOrbitSeconds)
                or bot.SortieTime>=cfg.GunDiveSeconds) then
            phase(bot,"approach");bot.SortieRunDirection=nil
            bot.SortieDangerX=nil;bot.SortieDangerY=nil
            bot.SortieEscapeDirection=nil;bot.SortieSafetyExtra=nil
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
    orientHull(id,bot)
    bot.AirHeading=bot.AirVelocity.x<0 and -1 or 1
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
