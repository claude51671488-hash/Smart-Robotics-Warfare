-- Concept 24: one falling charge, then a physical trip back to an air factory.
local function clamp(v,n) return math.max(-n,math.min(n,v)) end
local function home(bot,p)
    local best,distance
    for _,entry in ipairs(SRW.DeviceTargets(bot.Team%100)) do
        if string.find(entry.Kind,"^srw_factory_air_") and IsDeviceFullyBuilt(entry.Id) then
            local d=(entry.Position.x-p.x)^2+(entry.Position.y-p.y)^2
            if entry.Id==bot.HomeFactory then return entry end
            if not distance or d<distance then best,distance=entry,d end
        end
    end
    if best then bot.HomeFactory=best.Id end
    return best
end

function SRW.UpdateParcel(id,bot,dt)
    local cfg=SRW.Config.Robots[bot.Kind]
    bot.Age=(bot.Age or 0)+dt
    local p=GetDevicePosition(id)
    bot.AirVelocity={x=0,y=0}
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then return end
    if bot.BombReady==nil then bot.BombReady=true end
    local base=home(bot,p)
    local goal={x=bot.HomeX or p.x,y=bot.CruiseY or p.y}
    if base then goal={x=base.Position.x,y=base.Position.y-cfg.CruiseAltitude} end
    local target
    if bot.BombReady then
        local bestDistance
        for _,entry in ipairs(SRW.DeviceTargets(bot.Team%100==1 and 2 or 1)) do
            local d=(entry.Position.x-p.x)^2+(entry.Position.y-p.y)^2
            if not (SRW.Config.Robots[entry.Kind] or {}).Air and d<=cfg.Range^2
                and not (IsCloaked and IsCloaked(entry.Id)) and (not bestDistance or d<bestDistance) then
                target,bestDistance=entry,d
            end
        end
    end
    if target then
        if bot.Target~=target.Id then bot.BombHeading=target.Position.x>=p.x and 1 or -1 end
        bot.AirPhase="bomb_run";bot.Target=target.Id
        local vx,vy=0,0
        local old=bot.BombTrack
        if old and old.Id==target.Id then
            vx=clamp((target.Position.x-old.X)/dt,2000)
            vy=clamp((target.Position.y-old.Y)/dt,2000)
        end
        bot.BombTrack={Id=target.Id,X=target.Position.x,Y=target.Position.y}
        goal={x=target.Position.x,y=math.min(bot.CruiseY or p.y,target.Position.y-cfg.CruiseAltitude)}
        local speed=SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth
        local direction=bot.BombHeading
        local drop=Vec3(p.x,p.y+cfg.DropOffset,0)
        local height=target.Position.y-drop.y
        if height>120 then
            local down=cfg.DropSpeed-vy
            local t=(-down+math.sqrt(down*down+2*981*height))/981
            local releaseX=target.Position.x+vx*t-direction*speed*t
            goal.x=releaseX
            -- Don't reverse at the release point: fly through it and drop once.
            if math.abs(p.x-releaseX)<=math.max(90,speed*dt*1.5)
                and math.abs(p.y-goal.y)<150
                and CastGroundRay(p,drop,0)~=RAY_HIT_TERRAIN then
                local node=dlc2_CreateProjectile("srw_parcel_bomb","mortar",bot.Team,drop,
                    Vec3(direction*speed,cfg.DropSpeed,0),cfg.BombLifetime)
                if node and node>=0 then
                    bot.BombReady=false;bot.BombReload=cfg.RearmSeconds;bot.BombTrack=nil
                    bot.Target=nil;bot.AirPhase="return"
                    Log("[SRW] Parcel "..id.." dropped bomb "..node)
                end
            end
        end
    else
        bot.Target=nil;bot.BombTrack=nil
        bot.AirPhase=bot.BombReady and "patrol" or (base and "return" or "waiting_factory")
    end
    if not bot.BombReady then
        goal=base and {x=base.Position.x,y=base.Position.y-cfg.CruiseAltitude}
            or {x=bot.HomeX or p.x,y=bot.CruiseY or p.y}
        if base and math.abs(p.x-goal.x)<100 and math.abs(p.y-goal.y)<100
            and not DeviceDisabled(base.Id) then
            bot.AirPhase="rearming"
            bot.BombReload=math.max(0,(bot.BombReload or cfg.RearmSeconds)-dt)
            if bot.BombReload==0 then bot.BombReady=true;bot.AirPhase="patrol" end
            return
        end
    end
    local speed=SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth
    local x=p.x+clamp(goal.x-p.x,speed*dt)
    local y=goal.y
    if CastGroundRay(Vec3(x,p.y-1500,0),Vec3(x,p.y+5000,0),0)==RAY_HIT_TERRAIN then
        y=math.min(y,GetRayHitPosition().y-cfg.CruiseAltitude)
    end
    local q=Vec3(x,p.y+clamp(y-p.y,cfg.ClimbSpeed*dt),0)
    if CastGroundRay(p,q,0)==RAY_HIT_TERRAIN then return end
    if (SRW.MovementRay or CastRayFromDevice)(id,q,0,RAY_EXCLUDE_BG_MATERIALS,0)~=RAY_HIT_NOTHING then return end
    dlc2_SetDevicePosition(id,q)
    bot.AirVelocity={x=(q.x-p.x)/dt,y=(q.y-p.y)/dt}
end
