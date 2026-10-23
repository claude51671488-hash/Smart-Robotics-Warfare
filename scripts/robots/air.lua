-- Concept 20: strafing hunter. Keep only finite, serializable flight state.
local function clamp(v,limit) return math.max(-limit,math.min(limit,v)) end
local function sign(v,fallback) return v>1 and 1 or (v< -1 and -1 or fallback) end
local function moveClear(id,p,q)
    if CastGroundRay(p,q,0)==RAY_HIT_TERRAIN then return false end
    return (SRW.MovementRay or CastRayFromDevice)(id,q,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING
end

function SRW.SpawnAirRobot(team,factory,kind)
    local cfg=SRW.Config.Robots[kind]
    local direction=team%100==1 and 1 or -1
    local p=GetDeviceCentrePosition(factory)
    local root
    -- A blocked launch consumes neither reserve nor squad member. No ground snap.
    for _,height in ipairs({350,600,900}) do
        local q=Vec3(p.x+direction*200,p.y-height,0)
        if CastGroundRay(p,q,0)~=RAY_HIT_TERRAIN
            and (SRW.MovementRay or CastRayFromDevice)(factory,q,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING then
            EnableWeapon(kind,true,team%100)
            root=dlc2_CreateFloatingDevice(team,kind,q,90)
            EnableWeapon(kind,false,team%100)
            if root and root>=0 then break end
        end
    end
    if not root or root<0 then return false end
    local pos=GetDevicePosition(root)
    data.srw.Robots[root]={Team=team,Kind=kind,Direction=direction,Age=0,Mounted=true,
        HomeFactory=factory,AirPhase="cruise",CruiseY=p.y-cfg.CruiseAltitude,HomeX=p.x,AirVelocity={x=0,y=0}}
    local created={}
    for _,mount in ipairs(cfg.Mounts or {}) do
        EnableWeapon(mount.Kind,true,team%100)
        local child=dlc2_CreateFloatingDevice(team,mount.Kind,Vec3(pos.x+direction*mount.X,pos.y+mount.Y,0),90)
        EnableWeapon(mount.Kind,false,team%100)
        if not child or child<0 then
            for _,id in ipairs(created) do DeleteDeviceById(id);data.srw.MountedWeapons[id]=nil end
            data.srw.Robots[root]=nil;DeleteDeviceById(root);return false
        end
        created[#created+1]=child
        data.srw.MountedWeapons[child]={Root=root,Team=team,Kind=mount.Kind,Direction=direction,
            Mounted=true,OffsetX=mount.X,OffsetY=mount.Y,AntiAir=mount.AntiAir}
    end
    Log("[SRW] "..kind.." "..root.." launched, owner "..team)
    return true,root
end

-- Check the short outgoing arc against this aircraft's other modules. A rear
-- pod must not shoot through the lower turret when aiming steeply downwards.
function SRW.ShotClearsAircraft(id,bot,cfg,target)
    local rootId=bot.Root or id
    local root=data.srw.Robots[rootId]
    if not root or not (SRW.Config.Robots[root.Kind] or {}).Air or cfg.Guided then return true end
    local origin=SRW.ShotOrigin(id)
    local speed=SRW.RobotShotSpeed(id,cfg)
    local gravity=cfg.BeamWeapon and 0 or 981
    local time=SRW.BallisticFlight(origin,target,speed,gravity)
    if not time or time<.00001 then return false end
    local vx=(target.x-origin.x)/time
    local vy=(target.y-origin.y)/time-.5*gravity*time
    local parts={}
    if rootId~=id and DeviceExists(rootId) then parts[#parts+1]=GetDeviceCentrePosition(rootId) end
    for child,part in pairs(data.srw.MountedWeapons or {}) do
        if child~=id and part.Root==rootId and DeviceExists(child) then parts[#parts+1]=GetDeviceCentrePosition(child) end
    end
    local previous=origin
    for i=1,6 do
        local t=math.min(time,.3)*i/6
        local next=Vec3(origin.x+vx*t,origin.y+vy*t+.5*gravity*t*t,0)
        local dx,dy=next.x-previous.x,next.y-previous.y
        local d2=dx*dx+dy*dy
        for _,p in ipairs(parts) do
            local a=d2>0 and math.max(0,math.min(1,((p.x-previous.x)*dx+(p.y-previous.y)*dy)/d2)) or 0
            if (p.x-previous.x-a*dx)^2+(p.y-previous.y-a*dy)^2<90^2 then return false end
        end
        previous=next
    end
    return true
end

function SRW.UpdateAirRobot(id,bot,dt)
    local cfg=SRW.Config.Robots[bot.Kind]
    if cfg.SortieFlight and SRW.UpdateSortieFlight then return SRW.UpdateSortieFlight(id,bot,dt) end
    if cfg.Bomber then return SRW.UpdateParcel(id,bot,dt) end
    bot.Age=(bot.Age or 0)+dt
    local previousVelocity=bot.AirVelocity or {x=0,y=0}
    bot.AirVelocity={x=0,y=0}
    -- Native tier-I EMP disables every gun and holds the aircraft in place.
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then
        bot.DeployPosition=nil;bot.DeployRemaining=nil;bot.DeployTarget=nil
        bot.ChargeRemaining=nil;bot.ChargeTarget=nil;bot.BurstRemaining=nil
        return
    end
    local p=GetDevicePosition(id)
    bot.CruiseY=bot.CruiseY or p.y
    if bot.AirPhase=="egress" then
        bot.BurstRemaining=nil
        bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
        bot.AirRemaining=math.max(0,(bot.AirRemaining or 0)-dt)
        bot.Target=nil
        if bot.AirRemaining==0 then bot.AirPhase="cruise" end
    else
        if bot.Target and DeviceExists(bot.Target) then
            local target=GetDeviceCentrePosition(bot.Target)
            bot.AirTargetX=target.x
            if bot.AirPhase~="attack" then
                bot.AirPhase="attack";bot.AirRemaining=cfg.AttackSeconds
                bot.AirHeading=sign(target.x-p.x,bot.Direction)
            end
        end
        if bot.AirPhase=="attack" then
            bot.AirRemaining=math.max(0,(bot.AirRemaining or 0)-dt)
            if bot.AirRemaining==0 or not bot.Target then
                bot.AirPhase="egress";bot.AirRemaining=cfg.EgressSeconds
                bot.AirHeading=sign(p.x-(bot.AirTargetX or p.x),-(bot.AirHeading or bot.Direction))
                bot.Target=nil
            end
        end
    end
    -- Native bursts retain their firing transform. Briefly stabilize until all
    -- rounds have cleared; teleporting that gun mid-burst can hit its own hull.
    local childBurst=false
    for _,part in pairs(data.srw.MountedWeapons or {}) do
        if part.Root==id and (part.BeamRemaining or 0)>0 then childBurst=true;break end
    end
    if childBurst then
        -- The mount controller drains its own burst timer after the root update.
        if bot.AirPhase~="egress" then SRW.UpdateAirWeapon(id,bot,dt)
        else
            bot.BeamRemaining=math.max(0,(bot.BeamRemaining or 0)-dt)
            bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
        end
        return
    end
    if (bot.BeamRemaining or 0)>0 then
        SRW.UpdateAirWeapon(id,bot,dt)
        return
    end
    -- Heavy aircraft arrest their movement for a fresh firing solution. The
    -- shared gun controller rechecks target, terrain and deployment each tick.
    -- Reloading aircraft may reposition; the next shot needs stabilization again.
    if cfg.HoverFire and bot.AirPhase~="egress" and bot.Target
        and (DeviceExists(bot.Target) or bot.TargetPoint) and (bot.FireWait or 0)<=dt then
        SRW.UpdateAirWeapon(id,bot,dt)
        return
    end
    local heading=bot.AirHeading or bot.Direction
    if bot.AirPhase=="cruise" then
        local nearest,goal
        for _,entry in ipairs(SRW.DeviceTargets(bot.Team%100==1 and 2 or 1)) do
            local d=(entry.Position.x-p.x)^2+(entry.Position.y-p.y)^2
            if not nearest or d<nearest then nearest=d;goal=entry.Position end
        end
        -- Patrol around launch location when no enemy remains, instead of exiting the map.
        local x=goal and goal.x or (bot.HomeX or p.x)+heading*600
        if not goal and math.abs(p.x-(bot.HomeX or p.x))>700 then heading=-heading
        else heading=sign(x-p.x,heading) end
        bot.AirHeading=heading
    end
    local speed=SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth
    local steer=heading
    local y=bot.CruiseY
    if cfg.EvasiveFlight then
        -- Bounded steering preserves a curved reversal instead of flipping velocity.
        bot.AirSteer=(bot.AirSteer or heading)+clamp(heading-(bot.AirSteer or heading),(cfg.TurnRate or 2.2)*dt)
        steer=bot.AirSteer
        local wave=math.sin(bot.Age*2.2+id%7)*(cfg.WeaveHeight or 300)
        if bot.AirPhase=="egress" then wave=-350-math.abs(wave) end
        y=y+wave
        bot.EvadeScan=math.max(0,(bot.EvadeScan or 0)-dt)
        bot.EvadeRemaining=math.max(0,(bot.EvadeRemaining or 0)-dt)
        if bot.EvadeScan==0 then
            bot.EvadeScan=.2
            local side=bot.Team%100==1 and 2 or 1
            local seen=0
            for _,entry in ipairs(SRW.AirTargets(side)) do
                if not entry.IsDevice and SRW.AirTargetAlive(entry,side) then
                    seen=seen+1;if seen>128 then break end
                    local v=SRW.AirTargetVelocity(entry)
                    local dx,dy=entry.Position.x-p.x,entry.Position.y-p.y
                    local vx,vy=v.x-previousVelocity.x,v.y-previousVelocity.y
                    local v2=vx*vx+vy*vy
                    local t=v2>1 and -(dx*vx+dy*vy)/v2 or -1
                    if t>0 and t<.85 and (dx+vx*t)^2+(dy+vy*t)^2<260^2 then
                        bot.EvadeRemaining=.65
                        bot.EvadeSign=(dy+vy*t)>=0 and -1 or 1
                        break
                    end
                end
            end
        end
        if bot.EvadeRemaining>0 then y=p.y+(bot.EvadeSign or -1)*650 end
    end
    local x=p.x+steer*speed*dt
    -- Look ahead to climb over terrain; the short segment check prevents tunnelling.
    local probeX=x+heading*400
    if CastGroundRay(Vec3(probeX,p.y-1500,0),Vec3(probeX,p.y+5000,0),0)==RAY_HIT_TERRAIN then
        y=math.min(y,GetRayHitPosition().y-cfg.CruiseAltitude)
    end
    local q=Vec3(x,p.y+clamp(y-p.y,cfg.ClimbSpeed*dt),0)
    local centre=GetDeviceCentrePosition(id)
    local destination=Vec3(centre.x+q.x-p.x,centre.y+q.y-p.y,0)
    if not moveClear(id,centre,destination) then
        q=Vec3(p.x,math.max(bot.CruiseY-4000,p.y-cfg.ClimbSpeed*dt),0)
        destination=Vec3(centre.x,centre.y+q.y-p.y,0)
        if not moveClear(id,centre,destination) then return end
    end
    dlc2_SetDevicePosition(id,q)
    bot.AirVelocity={x=(q.x-p.x)/dt,y=(q.y-p.y)/dt}
    -- Move before spawning bullets. Otherwise the floating hull can teleport
    -- across a fresh muzzle projectile before the engine advances its physics.
    if bot.AirPhase~="egress" then
        SRW.UpdateAirWeapon(id,bot,dt)
        if bot.Target and DeviceExists(bot.Target) then
            local target=GetDeviceCentrePosition(bot.Target)
            bot.AirTargetX=target.x
            if bot.AirPhase~="attack" then
                bot.AirPhase="attack";bot.AirRemaining=cfg.AttackSeconds
                bot.AirHeading=sign(target.x-q.x,bot.Direction)
            end
        end
    end
end
