local beamSearch
local beamCache
local collectingBeams

-- Measure to the full segment, including the middle of long/diagonal beams.
function SRW_PointSegmentDistanceSquared(p, a, b)
    local dx, dy = b.x-a.x, b.y-a.y
    local length2 = dx*dx + dy*dy
    local t = length2 > 0 and ((p.x-a.x)*dx + (p.y-a.y)*dy)/length2 or 0
    t = math.max(0, math.min(1, t))
    return (p.x-a.x-t*dx)^2 + (p.y-a.y-t*dy)^2
end

function SRW_VisitEnemyBeam(nodeA, nodeB, position, saveName, deviceId)
    if saveName=="backbracing" then return true end
    if collectingBeams then
        collectingBeams[#collectingBeams+1]={NodePosition(nodeA),NodePosition(nodeB),A=nodeA,B=nodeB}
        return true
    end
    local distance2 = SRW_PointSegmentDistanceSquared(beamSearch.Position, NodePosition(nodeA), NodePosition(nodeB))
    if not beamSearch.Distance2 or distance2 < beamSearch.Distance2 then
        beamSearch.Distance2 = distance2
    end
    return true
end

function SRW.EnemyBeams(side)
    beamCache=beamCache or {}
    if not beamCache[side] then
        collectingBeams={}
        EnumerateStructureLinks(side,-1,"SRW_VisitEnemyBeam",true)
        beamCache[side]=collectingBeams; collectingBeams=nil
    end
    return beamCache[side]
end

-- A chassis above the barrel is also a valid contact, even without blocking travel.
-- Include its next-tick sweep so a fast vehicle cannot skip the proximity zone.
function SRW.VehicleNear(position,side,trigger,dt)
    local height=SRW.Config.Robots.srw_dynamit_bot.TriggerDistanceMines.Max*SRW.Config.Units.MineWidth
    for _,beam in ipairs(SRW.EnemyBeams(side)) do
        local a,b=beam[1],beam[2]
        local va=NodeVelocity and NodeVelocity(beam.A) or {x=0,y=0}
        local vb=NodeVelocity and NodeVelocity(beam.B) or {x=0,y=0}
        local ax,ay=a.x+va.x*dt,a.y+va.y*dt
        local bx,by=b.x+vb.x*dt,b.y+vb.y*dt
        local minx,maxx=math.min(a.x,b.x,ax,bx),math.max(a.x,b.x,ax,bx)
        local miny,maxy=math.min(a.y,b.y,ay,by),math.max(a.y,b.y,ay,by)
        if position.x>=minx-trigger and position.x<=maxx+trigger
            and position.y>=miny-trigger and position.y<=maxy+height then return true end
    end
    return false
end

function SRW.BeamTargets(position,side,range,direction)
    local targets={}
    for index,beam in ipairs(SRW.EnemyBeams(side)) do
        local a,b=beam[1],beam[2]
        local dx,dy=b.x-a.x,b.y-a.y; local length=dx*dx+dy*dy
        local t=length>0 and ((position.x-a.x)*dx+(position.y-a.y)*dy)/length or 0
        t=math.max(.05,math.min(.95,t))
        local q=Vec3(a.x+t*dx,a.y+t*dy,0)
        local d=(q.x-position.x)^2+(q.y-position.y)^2
        if d<=range^2 and (q.x-position.x)*direction>=0 then
            targets[#targets+1]={Id=-index,Position=q,Distance=d,Priority=2,Beam=true}
        end
    end
    return targets
end

function SRW.EnemyBeamDistance(position, side)
    if beamCache then
        if not beamCache[side] then
            collectingBeams={}
            EnumerateStructureLinks(side, -1, "SRW_VisitEnemyBeam", true)
            beamCache[side]=collectingBeams
            collectingBeams=nil
        end
        local nearest
        for _,beam in ipairs(beamCache[side]) do
            local d=SRW_PointSegmentDistanceSquared(position,beam[1],beam[2])
            if not nearest or d<nearest then nearest=d end
        end
        return nearest and math.sqrt(nearest)
    end
    beamSearch = { Position = position }
    EnumerateStructureLinks(side, -1, "SRW_VisitEnemyBeam", true)
    local distance2 = beamSearch.Distance2
    beamSearch = nil
    return distance2 and math.sqrt(distance2)
end

function SRW.GroundAt(x, y, reach)
    if CastGroundRay(Vec3(x, y - SRW.Config.Prototype.StepHeight, 0),
        Vec3(x, y + reach, 0), 0) == RAY_HIT_TERRAIN then
        local hit = GetRayHitPosition()
        return Vec3(hit.x, hit.y, 0)
    end
end

function SRW.SpawnRobot(team, factory)
    local p = GetDevicePosition(factory)
    local direction = team % 100 == 1 and 1 or -1
    local ground = SRW.GroundAt(p.x + direction * SRW.Config.Prototype.ExitOffset, p.y, 100)
    if not ground then return false end
    -- Device position is its attachment point, not its visual centre.
    local pos = Vec3(ground.x, ground.y, 0)
    -- Prepare state before creating the device: an error must not orphan a live bot.
    local range = SRW.Config.Robots.srw_dynamit_bot.TriggerDistanceMines
    local trigger = GetRandomFloat(range.Min, range.Max, "SRW Dynamit Bot trigger distance") * SRW.Config.Units.MineWidth
    -- Temporarily enable only during a synchronous spawn; no build menu entry.
    EnableDevice("srw_dynamit_bot", true, team % 100)
    local id = dlc2_CreateFloatingDevice(team, "srw_dynamit_bot", pos, 90)
    EnableDevice("srw_dynamit_bot", false, team % 100)
    if not id or id < 0 then return false end
    data.srw.Robots[id] = { Team = team, Direction = direction, Age = 0,
        Trigger = trigger }
    if SRW.RefreshDynamitAnimation then SRW.RefreshDynamitAnimation(id,data.srw.Robots[id]) end
    Log("[SRW] Bot " .. tostring(id) .. " spawned, owner " .. tostring(team))
    return true,id
end

local function MovementStatus(id, bot, status)
    -- Report state transitions only, so a stopped robot cannot flood the log.
    if bot.MoveStatus ~= status then
        bot.MoveStatus = status
        Log("[SRW] Bot " .. tostring(id) .. " movement: " .. status)
    end
end

local function Activate(id, bot, reason)
    bot.FuseRemaining = SRW.Config.Robots.srw_dynamit_bot.ActivationSeconds
    MovementStatus(id, bot, "activated: " .. reason)
end

function SRW.UpdateRobots(dt)
    -- Snapshot positions only within this simulation tick; moving vehicles stay current.
    beamCache={}
    local cfg = SRW.Config.Robots.srw_dynamit_bot
    for _, id in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local bot = data.srw.Robots[id]
        if not DeviceExists(id) then
            Log("[SRW] Bot " .. tostring(id) .. " removed externally, last age " .. tostring(bot.Age))
            data.srw.Robots[id] = nil
        elseif GetDeviceTeamIdActual(id) ~= bot.Team then
            Log("[SRW] Bot " .. tostring(id) .. " ownership changed to " .. tostring(GetDeviceTeamIdActual(id)))
            data.srw.Robots[id] = nil
        elseif bot.Kind=="srw_engineer_bot" then
            SRW.UpdateEngineer(id,bot,dt)
        elseif bot.Stationary then
            -- Bunker guns use the ordinary mounted robot AI; the body never walks.
        elseif (SRW.Config.Robots[bot.Kind] or {}).Air then
            SRW.UpdateAirRobot(id,bot,dt)
        elseif bot.Kind=="srw_sentry_bot" then
            SRW.UpdateSentry(id,bot,dt)
        elseif bot.Kind=="srw_hound" or bot.Kind=="srw_siege_bot" or bot.Kind=="srw_emp_bot" or bot.Kind=="srw_laser_bot" or bot.Kind=="srw_rocket_bot" or bot.Kind=="srw_hunter_bot" or bot.Kind=="srw_bastion_bot" or bot.Kind=="srw_heavy_siege_bot" or bot.Kind=="srw_tank_bot" or bot.Kind=="srw_colossus_bot" or bot.Kind=="srw_smith_bot" or bot.Kind=="srw_executioner_bot" or bot.Kind=="srw_storm_bot" or bot.Kind=="srw_tempest_bot" or bot.Kind=="srw_mlrs_bot" then
            SRW.UpdateHound(id,bot,dt)
        elseif bot.SpacingThisTick and bot.FuseRemaining==nil then
            -- Support movement was already handled, but armed fuses keep ticking.
        elseif bot.Kind=="srw_shield_bot" then
            SRW.UpdateShieldBot(id,bot,dt)
        elseif bot.Kind=="srw_repair_bot" then
            SRW.UpdateRepairBot(id,bot,dt)
        elseif bot.Kind=="srw_heavy_aa_bot" then
            SRW.UpdateHeavyAA(id,bot,dt)
        elseif bot.Kind=="srw_pike_bot" or bot.Kind=="srw_aa_bot" or bot.Kind=="srw_vault_bot" then
            SRW.UpdateAABot(id,bot,dt)
        elseif bot.FuseRemaining ~= nil then
            -- Latched fuse: do not move or reacquire a vehicle that has driven away.
            bot.FuseRemaining = math.max(0, bot.FuseRemaining - dt)
            if bot.FuseRemaining <= 0.000001 then
                data.srw.Robots[id] = nil
                Log("[SRW] Bot " .. tostring(id) .. " detonating: fuse complete")
                ApplyDamageToDevice(id, 1000000)
            end
        else
            bot.Age = bot.Age + dt
            local p = GetDevicePosition(id)
            local targetNear = false
            local enemySide = bot.Team % 100 == 1 and 2 or 1
            local beamDistance = SRW.EnemyBeamDistance(GetDeviceCentrePosition(id), enemySide)
            for index = 0, GetDeviceCountSide(enemySide) - 1 do
                local target = GetDeviceIdSide(enemySide, index)
                if DeviceExists(target) and GetDeviceTeamIdActual(target) % 100 == enemySide
                    and GetDeviceType(target) ~= "srw_dynamit_bot" then
                    local q = GetDeviceCentrePosition(target)
                    if (q.x-p.x)^2 + (q.y-p.y)^2 <= bot.Trigger^2 then targetNear = true; break end
                end
            end
            if targetNear or (beamDistance and beamDistance <= bot.Trigger)
                or SRW.VehicleNear(GetDeviceCentrePosition(id),enemySide,bot.Trigger,dt) then
                Activate(id, bot,
                    ((beamDistance and beamDistance <= bot.Trigger) and ("enemy beam distance=" .. tostring(beamDistance) .. " trigger=" .. tostring(bot.Trigger)) or "enemy device in range"))
            elseif not DeviceDisabled(id) then
                local x = p.x + bot.Direction * SRW.RobotSpeed(bot,cfg) * SRW.Config.Units.MineWidth * dt
                local feetY = p.y
                local ground = SRW.GroundAt(x, feetY, SRW.Config.Prototype.StepHeight)
                if ground then
                    local nextPos = Vec3(x, ground.y, 0)
                    -- Foreground links block the bot; background links are ignored.
                    -- Start from this device through the engine's device-aware ray.
                    -- A generic ray can start inside the barrel and hit the bot itself.
                    local centre = GetDeviceCentrePosition(id)
                    local destination = Vec3(centre.x + nextPos.x-p.x, centre.y + nextPos.y-p.y, 0)
                    local collision = (SRW.MovementRay or CastRayFromDevice)(id, destination, 0, RAY_EXCLUDE_BG_MATERIALS, 0)
                    if collision == RAY_HIT_NOTHING then
                        dlc2_SetDevicePosition(id, nextPos)
                        local moved = GetDevicePosition(id)
                        if math.abs(moved.x-p.x) > 0.01 then
                            MovementStatus(id, bot, "moving")
                        else
                            MovementStatus(id, bot, "position unchanged after SetDevicePosition")
                        end
                    elseif collision == RAY_HIT_STRUCTURE and GetRayHitTeamId() % 100 == enemySide then
                        Activate(id, bot, "enemy structure contact")
                    else
                        MovementStatus(id, bot, "blocked ray=" .. tostring(collision) .. " team=" .. tostring(GetRayHitTeamId()) .. " device=" .. tostring(GetRayHitDeviceId()))
                    end
                else
                    MovementStatus(id, bot, "no ground within step height")
                end
            else
                MovementStatus(id, bot, "EMP disabled")
            end
        end
        if (not bot.Kind or bot.Kind=="srw_dynamit_bot") and SRW.RefreshDynamitAnimation then
            SRW.RefreshDynamitAnimation(id,bot)
        end
    end
    if SRW.UpdateFieldMines then SRW.UpdateFieldMines(dt) end
    beamCache=nil
end
