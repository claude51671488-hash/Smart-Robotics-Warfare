-- One emitter is shared between protection and ground attack. A live ground
-- beam cannot also intercept; it must finish before evaluating fresh threats.
function SRW.UpdateAirWeapon(id,bot,dt)
    local cfg=SRW.Config.Robots[bot.Kind]
    if not cfg.AirDefenceLaser then return SRW.UpdateHound(id,bot,dt) end
    if (bot.BeamRemaining or 0)>0 then
        bot.BeamRemaining=math.max(0,bot.BeamRemaining-dt)
        bot.FireWait=math.max(0,(bot.FireWait or 0)-dt)
        return
    end
    if (bot.FireWait or 0)>dt then
        bot.FireWait=bot.FireWait-dt
        return
    end
    bot.Target=nil
    bot.FireWait=0
    SRW.UpdateAABot(id,bot,dt)
    if bot.Target then bot.LaserMode="air";return end
    bot.FireWait=0
    SRW.UpdateHound(id,bot,dt)
    if bot.Target then bot.LaserMode="ground" end
end
