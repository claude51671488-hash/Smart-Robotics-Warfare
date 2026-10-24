-- Terrain-confirmed delivery, with a bounded contact/disappearance fallback.
-- One short log per lifecycle transition; no per-frame/per-bullet trace.
local function trace(event,details)
    Log("[SRW][Matryoshka] event="..event.." "..details)
end
function SRW.PredictCapsuleLanding(team,p,v)
    if not v then return end
    local gravity=GetProjectileParamFloat and GetProjectileParamFloat("srw_kolokol_capsule",team,"Gravity",981) or 981
    local previous=Vec3(p.x,p.y,0)
    for i=1,600 do
        local time=i*.1
        local point=Vec3(p.x+v.x*time,p.y+v.y*time+.5*gravity*time*time,0)
        if CastGroundRay(previous,point,0)==RAY_HIT_TERRAIN then
            local hit=GetRayHitPosition()
            local length=math.sqrt((point.x-previous.x)^2+(point.y-previous.y)^2)
            local fraction=length>0 and math.sqrt((hit.x-previous.x)^2+(hit.y-previous.y)^2)/length or 0
            return {x=hit.x,y=hit.y,At=(i-1+fraction)*.1}
        end
        previous=point
    end
end
function SRW.TrackCapsule(team,node,weapon)
    if NodeExists(node) and GetNodeProjectileSaveName(node)=="srw_kolokol_capsule" then
        local p=NodePosition(node)
        local plan=NodeVelocity and SRW.PredictCapsuleLanding(team,p,NodeVelocity(node))
        data.srw.CapsuleFlights[node]={Team=team,Age=0,Position={x=p.x,y=p.y},Landing=plan}
        trace("launched","node="..node.." team="..team.." weapon="..tostring(weapon))
    end
end
function SRW.CapsuleImpact(node,team,name,cause,cachedGround)
    if name~="srw_kolokol_capsule" then return end
    local flight=data.srw.CapsuleFlights[node]
    if flight and flight.Consumed then return end
    trace("impact","node="..node.." team="..tostring(team).." cause="..tostring(cause)
        .." terrain="..tostring(cause==DESTROYTYPE_HITTERRAIN).." tracked="..tostring(flight~=nil))
    -- The native destruction event identifies the projectile and its final
    -- owner. Its delivery must not depend on receiving an earlier fired event
    -- (for example after restoring an in-flight shell from a save).
    data.srw.CapsuleFlights[node]={Team=team,Age=0,Consumed=true}
    if not team or team<=0 or cause~=DESTROYTYPE_HITTERRAIN then return end
    local p=cachedGround or NodePosition(node)
    -- Collision callbacks can report the end of a fast physics step below
    -- the surface. A walking robot's 25-unit step ray misses such impacts.
    local ground=cachedGround
    if not ground and flight and flight.Position then
        local previous=Vec3(flight.Position.x,flight.Position.y,0)
        if CastGroundRay(previous,p,0)==RAY_HIT_TERRAIN then
            local hit=GetRayHitPosition();ground=Vec3(hit.x,hit.y,0)
        end
    end
    if not ground then
        -- Covers a restored in-flight projectile without a cached previous
        -- position: max launch speed 9000 * .04 seconds is 360 units per tick.
        local above=math.min(p.y,flight and flight.Position and flight.Position.y or p.y)-512
        if CastGroundRay(Vec3(p.x,above,0),Vec3(p.x,p.y+300,0),0)==RAY_HIT_TERRAIN then
            local hit=GetRayHitPosition();ground=Vec3(hit.x,hit.y,0)
        end
    end
    if not ground and flight and flight.Landing then
        local at=flight.Landing
        if (p.x-at.x)^2+(p.y-at.y)^2<=512^2 and math.abs(flight.Age-at.At)<1 then
            ground=Vec3(at.x,at.y,0)
        end
    end
    if not ground then
        trace("placement_failed","node="..node.." reason=no_surface")
        return
    end
    EnableDevice("srw_matryoshka_deploying",true,team%100)
    local id=dlc2_CreateFloatingDevice(team,"srw_matryoshka_deploying",ground,90)
    EnableDevice("srw_matryoshka_deploying",false,team%100)
    if not id or id<0 then
        trace("placement_failed","node="..node.." reason=create_failed result="..tostring(id))
        return
    end
    data.srw.CapsuleTurrets[id]={Team=team,Direction=team%100==1 and 1 or -1,
        Kind="srw_matryoshka_deploying",Mounted=true,DeployAge=0,FireWait=0}
    trace("placed","node="..node.." turret="..id.." team="..team.." x="..ground.x.." y="..ground.y)
end

-- Create the weapon only after the non-weapon opening finishes. The old
-- visual is deleted in the same simulation tick, without a wreck or explosion.
local function finishOpening(id,bot)
    local p=GetDevicePosition(id)
    local health=math.max(0,math.min(500,GetDeviceHitpoints(id)))
    EnableWeapon("srw_matryoshka_turret",true,bot.Team%100)
    local ready=dlc2_CreateFloatingDevice(bot.Team,"srw_matryoshka_turret",p,90)
    EnableWeapon("srw_matryoshka_turret",false,bot.Team%100)
    if not ready or ready<0 then return end
    if not DeleteDeviceById(id) then DeleteDeviceById(ready);return end
    data.srw.CapsuleTurrets[id]=nil
    bot.Kind="srw_matryoshka_turret"
    data.srw.CapsuleTurrets[ready]=bot
    if health<500 then ApplyDamageToDevice(ready,500-health) end
    trace("unfolded","pod="..id.." turret="..ready.." team="..bot.Team.." hp="..health)
    return ready
end

local function updateGun(id,bot,cfg,dt)
    bot.CombatClock=(bot.CombatClock or 0)+dt
    bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
    local enemy=bot.Team%100==1 and 2 or 1
    local p=SRW.ShotOrigin(id)
    local candidates={}
    for _,entry in ipairs(SRW.DeviceTargets(enemy)) do
        local distance=(entry.Position.x-p.x)^2+(entry.Position.y-p.y)^2
        if distance<=cfg.Range^2 then
            candidates[#candidates+1]={Id=entry.Id,Position=entry.Position,Distance=distance,
                Priority=IsWeapon(entry.Id) and 0 or 1}
        end
    end
    table.sort(candidates,function(a,b)
        if a.Priority~=b.Priority then return a.Priority<b.Priority end
        if a.Distance~=b.Distance then return a.Distance<b.Distance end
        return a.Id<b.Id
    end)
    bot.Target=nil
    local track,ranging=bot.AimTrack,bot.RangingShots
    -- An obstructed group must not hide every reachable target behind it.
    -- The sorted list still gives all enemy weapons priority over devices.
    for _,target in ipairs(candidates) do
        -- AimSolution updates tracking. A rejected candidate must not erase
        -- the selected target's previous position before its own calculation.
        bot.AimTrack=track;bot.RangingShots=ranging
        local aim,spread,worthwhile=SRW.AimSolution(id,bot,cfg,target,dt,false)
        if worthwhile and SRW.ShotClearsTerrain(id,cfg,aim) and SRW.CanAimRobotWeapon(id,cfg,aim) then
            bot.Target=target.Id
            if bot.FireWait<=0 then
                aim,spread=SRW.AimSolution(id,bot,cfg,target,dt,true)
                local result=SRW.FireRobotWeapon(id,cfg,aim,spread)
                local previous=bot.LastFireResult
                bot.LastFireResult=result
                if result==(FIRE_SUCCESS or 0) then
                    if not bot.FirstFireLogged then
                        trace("first_fire","turret="..id.." team="..bot.Team.." target="..target.Id)
                        bot.FirstFireLogged=true
                    end
                    bot.BurstRemaining=(bot.BurstRemaining or cfg.BurstCount)-1
                    if bot.BurstRemaining>0 then bot.FireWait=cfg.BurstPeriod
                    else bot.BurstRemaining=nil;bot.FireWait=cfg.ReloadSeconds end
                else
                    if previous~=result then
                        trace("fire_failed","turret="..id.." target="..target.Id.." result="..tostring(result))
                    end
                    bot.FireWait=.2
                end
            end
            return
        end
    end
    bot.AimTrack=nil;bot.RangingShots=0
    bot.BurstRemaining=nil
end

function SRW.UpdateCapsules(dt)
    local cfg=SRW.Config.Matryoshka
    for node,flight in pairs(data.srw.CapsuleFlights) do
        flight.Age=flight.Age+dt
        if not flight.Consumed and NodeExists(node) then
            local p=NodePosition(node)
            if flight.Position then
                local previous=Vec3(flight.Position.x,flight.Position.y,0)
                if CastGroundRay(previous,p,0)==RAY_HIT_TERRAIN then
                    local hit=GetRayHitPosition();flight.Contact={x=hit.x,y=hit.y}
                end
            end
            flight.Position={x=p.x,y=p.y}
        elseif not flight.Consumed then
            flight.MissingAge=flight.MissingAge or flight.Age
            if flight.Age-flight.MissingAge>=.12 then
                local at=flight.Contact
                local plan=flight.Landing
                -- Allow a delayed/missing callback only at a witnessed crossing
                -- or within 32 units of the predicted surface at arrival time.
                -- Merely disappearing elsewhere, expiring or being shot down
                -- must not grant a turret.
                if not at and plan and flight.Position and math.abs(flight.MissingAge-plan.At)<=.24
                    and (flight.Position.x-plan.x)^2+(flight.Position.y-plan.y)^2<=32^2 then at=plan end
                if at then
                    trace("contact_fallback","node="..node.." x="..at.x.." y="..at.y)
                    SRW.CapsuleImpact(node,flight.Team,"srw_kolokol_capsule",DESTROYTYPE_HITTERRAIN,Vec3(at.x,at.y,0))
                end
            end
        end
        -- Node removal and the confirmed destruction callback need not arrive
        -- in the same tick. Keep the bounded record until that callback (or
        -- the projectile's maximum lifetime plus two seconds), without ever
        -- treating disappearance itself as a landing.
        if flight.Age>(flight.Consumed and 2 or 62) then
            if not flight.Consumed then
                trace("flight_expired","node="..node.." team="..flight.Team.." age="..flight.Age)
            end
            data.srw.CapsuleFlights[node]=nil
        end
    end
    for _,id in ipairs(SRW.SortedIds(data.srw.CapsuleTurrets)) do
        local bot=data.srw.CapsuleTurrets[id]
        if not DeviceExists(id) then
            trace("removed","turret="..id.." team="..bot.Team)
            data.srw.CapsuleTurrets[id]=nil
        else
            -- A captured turret follows its actual owner. No stale allied fire.
            local team=GetDeviceTeamIdActual(id)
            if team~=bot.Team then trace("captured","turret="..id.." from="..bot.Team.." team="..team) end
            bot.Team=team;bot.Direction=bot.Team%100==1 and 1 or -1
            if not DeviceDisabled(id) and IsDeviceFullyBuilt(id) then
                bot.DeployAge=math.min(cfg.DeploySeconds,bot.DeployAge+dt)
                if bot.DeployAge>=cfg.DeploySeconds then
                    if bot.Kind=="srw_matryoshka_deploying" then
                        local ready=finishOpening(id,bot)
                        if ready then id=ready else bot.DeployAge=cfg.DeploySeconds-.0001 end
                    end
                    if bot.Kind~="srw_matryoshka_deploying" and not bot.Deployed then
                        bot.Deployed=true
                        SetWeaponReloadTime(id,GetWeaponReloadPeriodById(id))
                        trace("ready","turret="..id.." team="..bot.Team.." age="..bot.DeployAge)
                    end
                    if bot.Deployed then updateGun(id,bot,cfg,dt) end
                end
            end

        end
    end
end

-- A client clock interpolates the fixed deployment poses between 25 Hz ticks.
-- Gun mirroring is selected independently from the stationary shell supports.
local shown={}
function SRW.RefreshCapsuleVisuals(delta)
    if not data.srw then return end
    local cfg=SRW.Config.Matryoshka
    for id,bot in pairs(data.srw.CapsuleTurrets) do
        if DeviceExists(id) then
            local cache=shown[id] or {Age=bot.DeployAge,Time=0}
            if cache.Age~=bot.DeployAge then cache.Age=bot.DeployAge;cache.Time=0 end
            if not DeviceDisabled(id) then cache.Time=math.min(.04,cache.Time+math.max(0,delta or 0)) end
            local side=bot.Direction<0 and "Left" or "Right"
            local state
            if bot.DeployAge<cfg.DeploySeconds then
                local age=math.min(cfg.DeploySeconds-.0001,bot.DeployAge+cache.Time)
                state="Deploy"..side..math.min(47,math.floor(age/cfg.DeploySeconds*48))
            else
                state="Ready"
            end
            -- Restore opening poses after native idle events/EMP. Once ready,
            -- every native state uses the same parts; never resubmit facing
            -- snapshots or reset an animation each rendering frame.
            if state~="Ready" or cache.State~=state then SetDeviceSpriteState(id,state) end
            cache.State=state
            shown[id]=cache
        end
    end
    for id in pairs(shown) do
        if not data.srw.CapsuleTurrets[id] or not DeviceExists(id) then shown[id]=nil end
    end
end
