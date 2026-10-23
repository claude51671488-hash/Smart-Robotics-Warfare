local links
function SRW_CollectMovementLink(a,b,p,material)
    if material~="backbracing" then links[#links+1]={NodePosition(a),NodePosition(b)} end
    return true
end
local function crosses(a,b,c,d)
    local rx,ry=b.x-a.x,b.y-a.y
    local sx,sy=d.x-c.x,d.y-c.y
    local den=rx*sy-ry*sx
    local qx,qy=c.x-a.x,c.y-a.y
    if math.abs(den)<0.000001 then
        if math.abs(qx*ry-qy*rx)>0.000001 then return false end
        return math.max(math.min(a.x,b.x),math.min(c.x,d.x))<=math.min(math.max(a.x,b.x),math.max(c.x,d.x))
            and math.max(math.min(a.y,b.y),math.min(c.y,d.y))<=math.min(math.max(a.y,b.y),math.max(c.y,d.y))
    end
    local t=(qx*sy-qy*sx)/den; local u=(qx*ry-qy*rx)/den
    return t>=0 and t<=1 and u>=0 and u<=1
end
local function movementLinks()
    if not links then
        links={}
        for side=1,2 do EnumerateStructureLinks(side,-1,"SRW_CollectMovementLink",true) end
    end
    return links
end
-- SRW bodies and mounted weapons do not block robot movement, on either side.
-- Foreground links are checked separately so a robot cannot hide a wall.
function SRW.MovementRay(id,destination,hp,flags,fields)
    local result=CastRayFromDevice(id,destination,hp,flags,fields)
    local other=GetRayHitDeviceId()
    local bot=data.srw.Robots[id]
    if bot and (bot.GroundLift or 0)>0 then
        -- A raised gun must not let the robot walk over low foreground walls.
        local p=GetDevicePosition(id)
        local centre=GetDeviceCentrePosition(id)
        local feet={x=p.x,y=p.y+bot.GroundLift-10}
        local nextFeet={x=feet.x+destination.x-centre.x,y=feet.y+destination.y-centre.y}
        for _,beam in ipairs(movementLinks()) do
            if crosses(feet,nextFeet,beam[1],beam[2]) then return RAY_HIT_STRUCTURE end
        end
    end
    if result~=RAY_HIT_DEVICE and result~=RAY_HIT_WEAPON then return result end
    local robot=data.srw.Robots[other] or (data.srw.MountedWeapons and data.srw.MountedWeapons[other])
    if not robot or not DeviceExists(other) then return result end
    local origin=GetDeviceCentrePosition(id)
    for _,beam in ipairs(movementLinks()) do if crosses(origin,destination,beam[1],beam[2]) then return result end end
    return RAY_HIT_NOTHING
end
-- Retain the tick hook for existing callers and clear flags restored from saves.
-- Robots no longer push neighbours backwards or reserve a personal movement gap.
function SRW.SeparateRobots(dt)
    links=nil
    for _,bot in pairs(data.srw.Robots) do bot.SpacingThisTick=false end
end
