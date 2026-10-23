-- Construction follows forward progress, never elapsed time or a retreat loop.
local function create(team,kind,p,weapon)
    local enable=weapon and EnableWeapon or EnableDevice
    enable(kind,true,team%100)
    local id=dlc2_CreateFloatingDevice(team,kind,p,90)
    enable(kind,false,team%100)
    if id and id>=0 then return id end
end
local function count(kind,side)
    local n=0
    local source=kind=="srw_field_mine" and data.srw.FieldMines or data.srw.Robots
    for id,b in pairs(source) do
        if (b.Kind==kind or kind=="srw_field_mine") and b.Team%100==side and DeviceExists(id) then n=n+1 end
    end
    return n
end

function SRW.SpawnEngineer(team,factory)
    local ok,id=SRW.SpawnRepairBot(team,factory,"srw_engineer_bot")
    if not ok then return false end
    local b=data.srw.Robots[id];local cfg=SRW.Config.Engineering
    b.StartX=GetDevicePosition(id).x;b.Progress=0;b.NextMine=cfg.MineSpacing
    local bounds=GetWorldExtents()
    b.BunkerSpacing=math.max(cfg.BunkerWidth,(bounds.MaxX-bounds.MinX)/4)
    b.NextBunker=b.BunkerSpacing
    return true,id
end

function SRW.BuildFieldBunker(team,p,direction)
    local cfg=SRW.Config.Engineering
    if count("srw_field_bunker",team%100)>=cfg.BunkerLimitPerSide then return false end
    -- A large bunker needs support at both edges, not just a ray at its centre.
    local left=SRW.GroundAt(p.x-cfg.BunkerWidth*.42,p.y,150)
    local right=SRW.GroundAt(p.x+cfg.BunkerWidth*.42,p.y,150)
    if not left or not right or math.abs(left.y-right.y)>120 then return false end
    for id,b in pairs(data.srw.Robots) do
        if b.Kind=="srw_field_bunker" and DeviceExists(id)
            and math.abs(GetDevicePosition(id).x-p.x)<cfg.BunkerWidth then return false end
    end
    local root=create(team,"srw_field_bunker"..(direction<0 and "_left" or ""),p,false)
    if not root then return false end
    local made={}
    -- Attachment feet match the generated roof and forward concrete ledge.
    local mounts={{"srw_bunker_cannon",-180,-195},{"srw_bunker_machinegun",340,-98}}
    for _,m in ipairs(mounts) do
        local kind=m[1]..(direction<0 and "_left" or "")
        local id=create(team,kind,Vec3(p.x+m[2]*direction,p.y+m[3],0),true)
        if not id then
            for _,child in ipairs(made) do DeleteDeviceById(child);data.srw.MountedWeapons[child]=nil end
            DeleteDeviceById(root);return false
        end
        made[#made+1]=id
        data.srw.MountedWeapons[id]={Root=root,Team=team,Direction=direction,Kind=m[1],
            Mounted=true,OffsetX=m[2],OffsetY=m[3]}
    end
    data.srw.Robots[root]={Kind="srw_field_bunker",Team=team,Direction=direction,Age=0,Stationary=true}
    Log("[SRW] Engineer bunker "..root.." built, owner "..team)
    return true,root
end

function SRW.LayFieldMine(team,p)
    if count("srw_field_mine",team%100)>=SRW.Config.Engineering.MineLimitPerSide then return false end
    local id=create(team,"srw_field_mine",p,false)
    if not id then return false end
    data.srw.FieldMines[id]={Team=team,ArmRemaining=1}
    return true,id
end

-- Both weapon hitboxes consume the bunker's single 5000-HP pool.
function SRW.ShareBunkerDamage(id,part)
    local root=data.srw.Robots[part.Root]
    if not root or root.Kind~="srw_field_bunker" or not DeviceExists(part.Root) then return end
    local damage=DeviceExists(id) and math.max(0,5000-GetDeviceHitpoints(id)) or 5000
    if damage>0 then
        if DeviceExists(id) then ApplyDamageToDevice(id,-damage) end
        ApplyDamageToDevice(part.Root,damage)
    end
end

function SRW.UpdateEngineer(id,bot,dt)
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then return end
    local cfg=SRW.Config.Robots.srw_engineer_bot
    local p=GetDevicePosition(id)
    local x=p.x+bot.Direction*SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth*dt
    local ground=SRW.GroundAt(x,p.y,SRW.Config.Prototype.StepHeight)
    if ground then
        local c=GetDeviceCentrePosition(id)
        local dest=Vec3(c.x+ground.x-p.x,c.y+ground.y-p.y,0)
        if (SRW.MovementRay or CastRayFromDevice)(id,dest,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING then
            dlc2_SetDevicePosition(id,ground)
        end
    end
    p=GetDevicePosition(id)
    bot.Progress=math.max(bot.Progress or 0,(p.x-bot.StartX)*bot.Direction)
    bot.BuildWait=math.max(0,(bot.BuildWait or 0)-dt)
    if bot.BuildWait>0 then return end
    -- At most one placement attempt of each type per second, also on steep ground.
    bot.BuildWait=1
    if bot.Progress>=bot.NextMine then
        local behind=SRW.GroundAt(p.x-bot.Direction*180,p.y,150)
        if behind and SRW.LayFieldMine(bot.Team,behind) then
            bot.NextMine=bot.Progress+SRW.Config.Engineering.MineSpacing
        end
    end
    if bot.Progress>=bot.NextBunker then
        local behind=SRW.GroundAt(p.x-bot.Direction*(SRW.Config.Engineering.BunkerWidth/2+180),p.y,200)
        if behind and SRW.BuildFieldBunker(bot.Team,behind,bot.Direction) then
            bot.NextBunker=bot.Progress+bot.BunkerSpacing
        end
    end
end

function SRW.UpdateFieldMines(dt)
    local cfg=SRW.Config.Engineering
    for _,id in ipairs(SRW.SortedIds(data.srw.FieldMines)) do
        local m=data.srw.FieldMines[id]
        if not DeviceExists(id) then data.srw.FieldMines[id]=nil
        else
            -- Follow actual ownership after capture; never trigger on its own side.
            m.Team=GetDeviceTeamIdActual(id)
            m.ArmRemaining=math.max(0,(m.ArmRemaining or 0)-dt)
            if m.FuseRemaining then
                m.FuseRemaining=m.FuseRemaining-dt
                if m.FuseRemaining<=0 then data.srw.FieldMines[id]=nil;ApplyDamageToDevice(id,1000000) end
            elseif m.ArmRemaining==0 and not DeviceDisabled(id) then
                local p=GetDeviceCentrePosition(id);local enemy=m.Team%100==1 and 2 or 1
                for _,target in ipairs(SRW.DeviceTargets(enemy)) do
                    if not (SRW.Config.Robots[target.Kind] or {}).Air then
                        local q=target.Position
                        if math.abs(q.x-p.x)<=cfg.MineTrigger and math.abs(q.y-p.y)<=cfg.MineHeight then
                            m.FuseRemaining=.1;break
                        end
                    end
                end
                -- Chassis beams above a mine count, even when the wheel isn't near it.
                if not m.FuseRemaining and SRW.VehicleNear(p,enemy,cfg.MineTrigger,dt) then m.FuseRemaining=.1 end
            end
        end
    end
end
