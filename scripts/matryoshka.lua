-- A terrain-only delivery lifecycle. No disappearance/mid-air spawn heuristic.
function SRW.TrackCapsule(team,node)
    if NodeExists(node) and GetNodeProjectileSaveName(node)=="srw_kolokol_capsule" then
        data.srw.CapsuleFlights[node]={Team=team,Age=0}
    end
end
function SRW.CapsuleImpact(node,team,name,cause)
    if name~="srw_kolokol_capsule" then return end
    local flight=data.srw.CapsuleFlights[node]
    if flight and flight.Consumed then return end
    -- The native destruction event identifies the projectile and its final
    -- owner. Its delivery must not depend on receiving an earlier fired event
    -- (for example after restoring an in-flight shell from a save).
    data.srw.CapsuleFlights[node]={Team=team,Age=0,Consumed=true}
    if not team or team<=0 or cause~=DESTROYTYPE_HITTERRAIN then return end
    local p=NodePosition(node)
    local ground=SRW.GroundAt(p.x,p.y,300)
    if not ground then
        Log("[SRW] Capsule terrain impact has no placement surface: node="..node)
        return
    end
    EnableWeapon("srw_matryoshka_turret",true,team%100)
    local id=dlc2_CreateFloatingDevice(team,"srw_matryoshka_turret",ground,90)
    EnableWeapon("srw_matryoshka_turret",false,team%100)
    if not id or id<0 then
        Log("[SRW] Capsule turret creation failed: node="..node.." result="..tostring(id))
        return
    end
    data.srw.CapsuleTurrets[id]={Team=team,Direction=team%100==1 and 1 or -1,
        Kind="srw_matryoshka_turret",Mounted=true,DeployAge=0,FireWait=0}
    SetWeaponReloadTime(id,0)
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
                bot.LastFireResult=result
                if result==(FIRE_SUCCESS or 0) then
                    bot.BurstRemaining=(bot.BurstRemaining or cfg.BurstCount)-1
                    if bot.BurstRemaining>0 then bot.FireWait=cfg.BurstPeriod
                    else bot.BurstRemaining=nil;bot.FireWait=cfg.ReloadSeconds end
                else bot.FireWait=.2 end
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
        -- Node removal and the confirmed destruction callback need not arrive
        -- in the same tick. Keep the bounded record until that callback (or
        -- the projectile's maximum lifetime plus two seconds), without ever
        -- treating disappearance itself as a landing.
        if flight.Age>(flight.Consumed and 2 or 62) then data.srw.CapsuleFlights[node]=nil end
    end
    for _,id in ipairs(SRW.SortedIds(data.srw.CapsuleTurrets)) do
        local bot=data.srw.CapsuleTurrets[id]
        if not DeviceExists(id) then data.srw.CapsuleTurrets[id]=nil
        else
            -- A captured turret follows its actual owner. No stale allied fire.
            bot.Team=GetDeviceTeamIdActual(id);bot.Direction=bot.Team%100==1 and 1 or -1
            if not DeviceDisabled(id) and IsDeviceFullyBuilt(id) then
                bot.DeployAge=math.min(cfg.DeploySeconds,bot.DeployAge+dt)
                if bot.DeployAge>=cfg.DeploySeconds then
                    if not bot.Deployed then
                        bot.Deployed=true
                        SetWeaponReloadTime(id,GetWeaponReloadPeriodById(id))
                    end
                    updateGun(id,bot,cfg,dt)
                end
            end
            if bot.DeployAge<cfg.DeploySeconds then
                -- This API sets elapsed reload progress, not time remaining.
                SetWeaponReloadTime(id,0)
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
                local head=GetWeaponBarrelPosition(id);local muzzle=GetWeaponHardpointPosition(id)
                local gun=muzzle.x<head.x and "Left" or "Right"
                state="Ready"..side..gun
            end
            -- Native idle/reload can override any pose, including a deployment
            -- frozen by EMP. Every state is a single still frame, so restoring
            -- it has no animation to restart and allocates no devices/effects.
            SetDeviceSpriteState(id,state)
            shown[id]=cache
        end
    end
    for id in pairs(shown) do
        if not data.srw.CapsuleTurrets[id] or not DeviceExists(id) then shown[id]=nil end
    end
end
