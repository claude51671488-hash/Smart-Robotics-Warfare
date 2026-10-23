-- Skycleaver: a single root owns deployment, all AA mounts share its readiness.
-- Only scalar state/current anchor is retained; air enumeration uses the tick cache.
local function reset(bot)
    bot.Braced=false; bot.BraceActive=false; bot.BraceProgress=0
    bot.BraceQuiet=0; bot.BracePosition=nil; bot.BraceThreat=false; bot.BraceScan=0
    bot.Target=nil
end

local function threatNear(id,bot,cfg)
    local origin=GetDeviceCentrePosition(id)
    local feet=SRW.RobotGroundPosition(id,bot)
    local side=bot.Team%100==1 and 2 or 1
    for _,entry in ipairs(SRW.AirTargets(side)) do
        local node,p=entry.Id,entry.Position
        local dx,dy=p.x-origin.x,p.y-origin.y
        if SRW.AirTargetAlive(entry,side) and p.y<feet.y-30
            and dx*dx+dy*dy<=cfg.Range^2
            and (entry.IsDevice or GetProjectileParamFloat(GetNodeProjectileSaveName(node),NodeTeam(node),
                "ProjectileShootDownRadius",0)>0) then return true end
    end
    return false
end

function SRW.UpdateHeavyAA(id,bot,dt)
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then reset(bot); return end
    local cfg=SRW.Config.Robots[bot.Kind]
    local p=GetDevicePosition(id)
    local anchor=bot.BracePosition
    -- Physics/teleport movement invalidates stability, including after save restore.
    if anchor and (p.x-anchor.x)^2+(p.y-anchor.y)^2>1 then reset(bot) end
    bot.BraceScan=math.max(0,(bot.BraceScan or 0)-dt)
    if bot.BraceScan==0 then
        bot.BraceThreat=threatNear(id,bot,cfg)
        bot.BraceScan=0.12
    end
    if bot.BraceThreat then bot.BraceQuiet=0
    else bot.BraceQuiet=(bot.BraceQuiet or 0)+dt end
    if bot.BraceThreat or (bot.BraceActive and bot.BraceQuiet<cfg.BraceHoldSeconds) then
        local wasBraced=bot.Braced
        bot.BraceActive=true
        bot.BracePosition=bot.BracePosition or {x=p.x,y=p.y}
        bot.BraceProgress=math.min(cfg.BraceSeconds,(bot.BraceProgress or 0)+dt)
        bot.Braced=bot.BraceProgress>=cfg.BraceSeconds
        if bot.Braced and not wasBraced then bot.FireWait=0 end
    else
        bot.BraceActive=false; bot.Braced=false; bot.BraceProgress=0; bot.BracePosition=nil
    end
    SRW.UpdateAABot(id,bot,dt)
end
