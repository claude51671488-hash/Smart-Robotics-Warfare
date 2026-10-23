function SRW.UpdateSentry(id,bot,dt)
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then return end
    local p=GetDeviceCentrePosition(id)
    local enemy=bot.Team%100==1 and 2 or 1
    local close=false
    for i=0,GetDeviceCountSide(enemy)-1 do
        local target=GetDeviceIdSide(enemy,i)
        if DeviceExists(target) and GetDeviceTeamIdActual(target)%100==enemy then
            local q=GetDeviceCentrePosition(target)
            if (q.x-p.x)*bot.Direction>=0 and (q.x-p.x)^2+(q.y-p.y)^2<=1200^2 then close=true; break end
        end
    end
    -- Autocannon defends against nearby ground enemies; rockets remain independent.
    if close or (bot.BeamRemaining or 0)>0 then SRW.UpdateHound(id,bot,dt)
    else SRW.UpdateAABot(id,bot,dt) end
end
