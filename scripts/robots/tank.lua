-- Internal reactor reserve belongs to the root; never charge the player's economy.
function SRW.UpdateWeaponPower(dt)
    for _,id in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local bot=data.srw.Robots[id]
        local cfg=SRW.Config.Robots[bot.Kind] or {}
        if cfg.PowerCapacity and DeviceExists(id) then
            bot.WeaponPower=bot.WeaponPower or cfg.PowerCapacity
            if not DeviceDisabled(id) and IsDeviceFullyBuilt(id) then
                bot.WeaponPower=math.min(cfg.PowerCapacity,bot.WeaponPower+cfg.PowerRegen*dt)
            end
        end
    end
end
local function powerSource(bot)
    local root=bot.Root and data.srw.Robots[bot.Root] or bot
    local cfg=root and SRW.Config.Robots[root.Kind]
    if root and cfg and cfg.PowerCapacity then return root,cfg end
end
function SRW.CanPowerWeapon(bot,cfg)
    if not cfg.PowerCost then return true end
    local root,source=powerSource(bot)
    if not root then return false end
    -- Main gun and continuous laser cannot start overlapping bursts.
    if bot.Root then
        if (root.BeamRemaining or 0)>0 then return false end
    else
        for _,part in pairs(data.srw.MountedWeapons or {}) do
            if data.srw.Robots[part.Root]==root and (part.BeamRemaining or 0)>0
                and (SRW.Config.Robots[part.Kind] or {}).PowerCost then return false end
        end
    end
    return (root.WeaponPower or source.PowerCapacity)>=cfg.PowerCost
end
function SRW.UseWeaponPower(bot,cfg)
    if not cfg.PowerCost then return end
    local root,source=powerSource(bot)
    if root then root.WeaponPower=math.max(0,(root.WeaponPower or source.PowerCapacity)-cfg.PowerCost) end
end

function SRW.SpawnTank(team,factory,kind)
    kind=kind or "srw_tank_bot"
    local ok,root=SRW.SpawnHound(team,factory,kind)
    if not ok then return false end
    local p=GetDevicePosition(root)
    data.srw.MountedWeapons=data.srw.MountedWeapons or {}
    local created={}
    for _,mount in ipairs(SRW.Config.Robots[kind].Mounts or {}) do
        local direction=team%100==1 and 1 or -1
        EnableWeapon(mount.Kind,true,team%100)
        local child=dlc2_CreateFloatingDevice(team,mount.Kind,Vec3(p.x+mount.X*direction,p.y+mount.Y,0),90)
        EnableWeapon(mount.Kind,false,team%100)
        if not child or child<0 then
            for _,id in ipairs(created) do DeleteDeviceById(id); data.srw.MountedWeapons[id]=nil end
            data.srw.Robots[root]=nil; DeleteDeviceById(root); return false
        end
        SRW.OrientRobotWeapon(child,direction)
        created[#created+1]=child
        data.srw.MountedWeapons[child]={Root=root,Team=team,Direction=direction,
            Kind=mount.Kind,Mounted=true,OffsetX=mount.X,OffsetY=mount.Y,AntiAir=mount.AntiAir}
    end
    return true,root
end

function SRW.UpdateMountedWeapons(dt)
    for _,id in ipairs(SRW.SortedIds(data.srw.MountedWeapons)) do
        local part=data.srw.MountedWeapons[id]
        local root=data.srw.Robots[part.Root]
        if SRW.ShareBunkerDamage then SRW.ShareBunkerDamage(id,part) end
        if not DeviceExists(id) then data.srw.MountedWeapons[id]=nil
        elseif not root or not DeviceExists(part.Root) or GetDeviceTeamIdActual(part.Root)~=part.Team
            or GetDeviceTeamIdActual(id)~=part.Team then
            DeleteDeviceById(id); data.srw.MountedWeapons[id]=nil
        else
            local p=GetDevicePosition(part.Root)
            if root.Kind=="srw_hornet_bot" then part.Direction=root.ArtFacing or root.Direction end
            local mount=Vec3(p.x+(part.OffsetX or 0)*part.Direction,p.y+(part.OffsetY or -50),0)
            if root.Kind=="srw_hornet_bot" and SRW.HornetRigPoint then
                mount=SRW.HornetRigPoint(root,p,part.OffsetX or 0,part.OffsetY or -50)
            end
            -- The invisible missile silo keeps its native vertical launch arc;
            -- its world hardpoint follows the rotating hatch on the rigid hull.
            dlc2_SetDevicePosition(id,mount)
            part.EMPRemaining=math.max(0,(part.EMPRemaining or 0)-dt,root.EMPRemaining or 0)
            -- A burst already in flight must expire even during egress or root EMP.
            -- Otherwise aircraft can remain frozen forever waiting on this mount.
            if root.AirPhase=="egress" or DeviceDisabled(part.Root) then
                part.BurstRemaining=nil
                part.BeamRemaining=math.max(0,(part.BeamRemaining or 0)-dt)
                part.FireWait=math.max(0,(part.FireWait or 0)-dt)
            end
            if not DeviceDisabled(part.Root) and IsDeviceFullyBuilt(part.Root)
                and root.AirPhase~="egress"
                and not (root.SortieGunOnly and part.Kind=="srw_hornet_rockets") then
                if part.AntiAir then SRW.UpdateAABot(id,part,dt)
                else SRW.UpdateHound(id,part,dt) end
            end
        end
    end
end
