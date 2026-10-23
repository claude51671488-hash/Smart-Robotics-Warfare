-- Low ballistic arc in Forts coordinates (+Y down). Use a stable quadratic in
-- flight-time squared, avoiding cancellation on nearly horizontal short shots.
function SRW.BallisticFlight(origin,target,speed,gravity)
    local dx,dy=target.x-origin.x,target.y-origin.y
    local d2=dx*dx+dy*dy
    if speed<=0 then return end
    if gravity<=0 then return math.sqrt(d2)/speed end
    local b=speed*speed+gravity*dy
    local disc=b*b-gravity*gravity*d2
    if b<=0 or disc<0 then return end
    return math.sqrt(2*d2/(b+math.sqrt(disc)))
end

function SRW.BallisticIntercept(origin,target,velocity,speed,gravity,maxTime)
    local q=Vec3(target.x,target.y,0)
    local t
    for i=1,6 do
        t=SRW.BallisticFlight(origin,q,speed,gravity)
        if not t or t>(maxTime or 30) then return end
        q=Vec3(target.x+velocity.x*t,target.y+velocity.y*t,0)
    end
    return q,t
end

function SRW.ShotOrigin(id)
    return GetWeaponHardpointPosition and GetWeaponHardpointPosition(id) or GetDeviceCentrePosition(id)
end

function SRW.RobotShotSpeed(id,cfg)
    if GetWeaponMaxFireSpeed then
        local speed=GetWeaponMaxFireSpeed(GetDeviceTeamIdActual(id),GetDeviceType(id))
        if speed and speed>0 then return speed end
    end
    return cfg.BulletSpeed or 6000
end

-- The native ballistic search assumes a forward-facing sector. Across a full
-- turn it can report a vertical solution for a target on the left. Solve the
-- low arc once, then ask the engine to fire along that barrel direction.
function SRW.DirectBarrelTarget(id,cfg,target)
    if cfg.InstantBeam or cfg.BeamWeapon then return target end
    local origin=SRW.ShotOrigin(id)
    local time=SRW.BallisticFlight(origin,target,SRW.RobotShotSpeed(id,cfg),981)
    if not time or time>30 then return end
    local point=Vec3(target.x,target.y-.5*981*time*time,0)
    if (cfg.LimitedElevation or cfg.MuzzleAim) and GetWeaponBarrelPosition then
        -- DIRECTAIM measures direction from Head, although the projectile can
        -- spawn at a forward Hardpoint0. Rebase the muzzle solution onto Head.
        local head=GetWeaponBarrelPosition(id)
        -- A distant direction point makes the native clearance/recoil origin
        -- irrelevant to the requested angle; target flight is still solved above.
        return Vec3(head.x+(point.x-origin.x)*1000,head.y+(point.y-origin.y)*1000,0)
    end
    return point
end

function SRW.CanAimRobotWeapon(id,cfg,target)
    if cfg.NativeBallistics then
        if not AimWeapon(id,target) then return false end
        if FIREFLAG_TEST and FIREFLAG_IGNORERELOADING then
            return FireWeapon(id,target,0,FIREFLAG_TEST+FIREFLAG_IGNORERELOADING)==FIRE_SUCCESS
        end
        return true
    end
    if cfg.Artillery or cfg.Guided then return AimWeapon(id,SRW.LaunchAim(id,cfg,target)) end
    local barrel=SRW.DirectBarrelTarget(id,cfg,target)
    if not barrel or not SRW.BarrelInSector(id,cfg,barrel) then return false end
    if cfg.LimitedElevation and FIREFLAG_TEST and FIREFLAG_IGNORERELOADING then
        -- Do not lock onto the first enemy if its firing line is obstructed by
        -- the bunker itself. Test without spending ammo or changing reload.
        local flags=FIREFLAG_DIRECTAIM+FIREFLAG_TEST+FIREFLAG_IGNORERELOADING
        return FireWeaponWithPower(id,barrel,0,-1,flags,1)==FIRE_SUCCESS
    end
    return true
end

function SRW.BarrelInSector(id,cfg,barrel)
    if not cfg.LimitedElevation then return true end
    local part=data.srw.MountedWeapons[id]
    local direction=part and part.Direction or (GetDeviceTeamIdActual(id)%100==1 and 1 or -1)
    local origin=GetWeaponBarrelPosition and GetWeaponBarrelPosition(id) or SRW.ShotOrigin(id)
    local dx=(barrel.x-origin.x)*direction
    if dx<=0 then return false end
    local elevation=math.deg(math.atan((origin.y-barrel.y)/dx))
    return elevation>=(cfg.MinElevation or -7) and elevation<=(cfg.MaxElevation or 20)
end

function SRW.FireRobotWeapon(id,cfg,target,spread)
    if cfg.NativeBallistics then return FireWeapon(id,target,spread,FIREFLAG_NORMAL) end
    if cfg.Artillery or cfg.Guided then
        return FireWeapon(id,SRW.LaunchAim(id,cfg,target),spread,FIREFLAG_NORMAL)
    end
    local barrel=SRW.DirectBarrelTarget(id,cfg,target)
    if not barrel or not SRW.BarrelInSector(id,cfg,barrel) then return FIRE_NOSOLUTION or 11 end
    local result=FireWeaponWithPower(id,barrel,spread,-1,FIREFLAG_DIRECTAIM,1)
    if result==FIRE_SUCCESS and cfg.LimitedElevation and cfg.BeamHoldSeconds and ReserveWeaponAim then
        ReserveWeaponAim(id,cfg.BeamHoldSeconds)
    end
    return result
end

function SRW.ShotClearsTerrain(id,cfg,target)
    -- Artillery and vertical homing launchers retain their native trajectory solver.
    if cfg.Artillery or cfg.Guided or not CastGroundRay then return true end
    local p=SRW.ShotOrigin(id)
    if cfg.BeamWeapon then return CastGroundRay(p,target,0)~=RAY_HIT_TERRAIN end
    local gravity=981
    local t=SRW.BallisticFlight(p,target,SRW.RobotShotSpeed(id,cfg),gravity)
    if not t or t<.00001 then return false end
    local vx=(target.x-p.x)/t
    local vy=(target.y-p.y)/t-.5*gravity*t
    local previous=p
    for i=1,6 do
        local at=t*i/6
        local next=Vec3(p.x+vx*at,p.y+vy*at+.5*gravity*at*at,0)
        if CastGroundRay(previous,next,0)==RAY_HIT_TERRAIN then return false end
        previous=next
    end
    return true
end

-- Bounded per-weapon tracking; cleaned up with its owning robot.
function SRW.AimSolution(id,bot,cfg,target,dt,randomize)
    local old=bot.AimTrack
    local vx,vy=0,0
    if not randomize then
        if old and old.Id==target.Id then
            dt=math.max(dt,(bot.CombatClock or dt)-(old.Time or 0))
            vx=(target.Position.x-old.X)/math.max(.001,dt)
            vy=(target.Position.y-old.Y)/math.max(.001,dt)
            if math.abs(vx-old.VX)+math.abs(vy-old.VY)>150 then bot.RangingShots=0 end
        else bot.RangingShots=0 end
        if vx*vx+vy*vy>4000000 then vx,vy=0,0;bot.RangingShots=0 end
        bot.AimTrack={Id=target.Id,X=target.Position.x,Y=target.Position.y,VX=vx,VY=vy,Time=bot.CombatClock or dt}
    elseif old then vx,vy=old.VX,old.VY end
    if cfg.BeamWeapon then return Vec3(target.Position.x,target.Position.y,0),0,true end
    local distance=math.sqrt(target.Distance)
    local flight=cfg.Artillery and math.min(12,math.sqrt(2*distance/981))
        or distance/(cfg.BulletSpeed or 6000)
    local q=Vec3(target.Position.x+vx*flight,target.Position.y+vy*flight,0)
    if cfg.Artillery then
        local spread=math.max(25,distance*.035)/(1+math.min(8,bot.RangingShots or 0)*.45)
        if randomize then q.x=q.x+GetRandomFloat(-spread,spread,"SRW artillery dispersion") end
        return q,0,true
    end
    if cfg.Guided or cfg.BeamWeapon then return q,0,true end
    local origin=SRW.ShotOrigin(id)
    local predicted=SRW.BallisticIntercept(origin,target.Position,{x=vx,y=vy},SRW.RobotShotSpeed(id,cfg),981,30)
    if not predicted then return target.Position,0,false end
    q=predicted
    local ratio=math.min(1,distance/math.max(1,cfg.Range))
    local degrees=cfg.Precise and 0 or (.08+1.2*ratio*ratio)
    local errorRadius=distance*math.tan(math.rad(degrees))
    local targetRadius=target.Beam and 90 or 65
    local worthwhile=(cfg.ReloadSeconds or 2)<4 or errorRadius<=targetRadius*2
    return q,degrees,worthwhile
end
