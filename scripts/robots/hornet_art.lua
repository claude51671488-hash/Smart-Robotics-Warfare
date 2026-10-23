-- Flight mode is simulated; all sprite switching and transient clocks are local.
local shown={}
function SRW.HornetShot(weaponId)
    local bot=data.srw and (data.srw.Robots[weaponId] or data.srw.MountedWeapons[weaponId])
    if not bot then return end
    if bot.Kind=="srw_hornet_bot" then bot.HornetGunSerial=((bot.HornetGunSerial or 0)+1)%256
    elseif bot.Kind=="srw_hornet_rockets" then
        local root=data.srw.Robots[bot.Root]
        if root then root.HornetRocketSerial=((root.HornetRocketSerial or 0)+1)%256 end
    end
end
function SRW.RefreshHornetVisuals(delta)
    if not data.srw then return end
    for id,bot in pairs(data.srw.Robots) do
        if bot.Kind=="srw_hornet_bot" and DeviceExists(id) then
            local cache=shown[id] or {Serial=bot.HornetRocketSerial or 0,LaunchAge=1}
            local launch=(bot.HornetRocketSerial or 0)~=cache.Serial
            cache.Serial=bot.HornetRocketSerial or 0
            cache.LaunchAge=launch and 0 or math.min(1,cache.LaunchAge+math.max(0,delta or .04))
            local velocity=bot.AirVelocity or {x=0,y=0}
            local direction=bot.ArtFacing or bot.Direction
            local mode="Cruise"
            if bot.SortiePhase=="egress" or (bot.EvadeRemaining or 0)>0 then mode="Boost"
            elseif velocity.y< -80 then mode="Climb"
            elseif velocity.y>80 then mode="Dive" end
            if DeviceDisabled(id) then mode="Idle";cache.LaunchAge=1 end
            local state=mode..(direction<0 and "Left" or "Right")
            if cache.LaunchAge<.28 then state=state.."Launch" end
            -- Hull pitch and gun traverse are independent. Select the gun art
            -- from the actual barrel's direction in the hull frame, so rotating
            -- the aircraft cannot invert its independently aimed lower turret.
            local gunSide=direction
            if GetWeaponBarrelPosition and GetWeaponHardpointPosition then
                local head=GetWeaponBarrelPosition(id)
                local muzzle=GetWeaponHardpointPosition(id)
                local pitch=bot.FlightPitch or 0
                local dx=(muzzle.x-head.x)*math.cos(pitch)+(muzzle.y-head.y)*math.sin(pitch)
                if math.abs(dx)>.01 then gunSide=dx<0 and -1 or 1 end
            end
            if gunSide~=direction then state=state..(gunSide<0 and "GunLeft" or "GunRight") end
            if cache.State~=state or launch then SetDeviceSpriteState(id,state);cache.State=state end
            shown[id]=cache
        end
    end
    for id in pairs(shown) do
        if not data.srw.Robots[id] or not DeviceExists(id) then shown[id]=nil end
    end
end
