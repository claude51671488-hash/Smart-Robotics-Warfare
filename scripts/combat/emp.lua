-- EMP impacts use the confirmed destruction cause, never inferred disappearance.
-- Score once per firing opportunity. Mounted weapons never inflate a cluster.
function SRW.RankEMPTargets(candidates,radius)
    local roots,buckets={},{}
    local function key(x,y) return x..":"..y end
    for _,c in ipairs(candidates) do
        if not (data.srw.MountedWeapons or {})[c.Id] then
            roots[#roots+1]=c
            local x,y=math.floor(c.Position.x/radius),math.floor(c.Position.y/radius)
            local k=key(x,y); buckets[k]=buckets[k] or {}
            buckets[k][#buckets[k]+1]=c
        end
    end
    for _,c in ipairs(roots) do
        local x,y=math.floor(c.Position.x/radius),math.floor(c.Position.y/radius)
        local count=0
        for dx=-1,1 do for dy=-1,1 do
            for _,other in ipairs(buckets[key(x+dx,y+dy)] or {}) do
                if (c.Position.x-other.Position.x)^2+(c.Position.y-other.Position.y)^2<=radius^2 then count=count+1 end
            end
        end end
        local kind=GetDeviceType(c.Id)
        local cfg=SRW.Config.Robots[kind] or {}
        local shield=cfg.ShieldHP or kind=="srw_shield_generator"
        local aa=cfg.AntiAir or kind=="srw_aa_bot" or kind=="srw_heavy_aa_bot" or kind=="srw_sentry_bot"
        c.EMPScore=count*10+(shield and 3 or 0)+(aa and 2 or 0)
    end
    return roots
end

function SRW.EMPImpact(nodeId,team,name,cause)
    if (name~="srw_emp_shell" and name~="srw_tempest_emp") or not team or team<=0 then return end
    if cause~=DESTROYTYPE_HITDEVICE and cause~=DESTROYTYPE_HITSTRUCTURE
        and cause~=DESTROYTYPE_HITTERRAIN then return end
    local p=NodePosition(nodeId)
    local cfg=SRW.Config.Robots[name=="srw_tempest_emp" and "srw_tempest_bot" or "srw_emp_bot"]
    local enemy=team%100==1 and 2 or 1
    for i=0,GetDeviceCountSide(enemy)-1 do
        local id=GetDeviceIdSide(enemy,i)
        if DeviceExists(id) and GetDeviceTeamIdActual(id)%100==enemy then
            local q=GetDeviceCentrePosition(id)
            if (q.x-p.x)^2+(q.y-p.y)^2<=cfg.EMPRadius^2 then
                local bot=data.srw.Robots[id] or (data.srw.MountedWeapons and data.srw.MountedWeapons[id])
                local target=bot and SRW.Config.Robots[bot.Kind]
                if target and (target.Tier or 1)>=2 then
                    bot.EMPRemaining=math.max(bot.EMPRemaining or 0,cfg.EMPSeconds)
                else EMPDevice(id,cfg.EMPSeconds) end
            end
        end
    end
end

function SRW.UpdateEMP(dt)
    for _,id in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local bot=data.srw.Robots[id] or (data.srw.MountedWeapons and data.srw.MountedWeapons[id])
        if bot.EMPRemaining then
            bot.EMPRemaining=math.max(0,bot.EMPRemaining-dt)
            if bot.EMPRemaining==0 then bot.EMPRemaining=nil end
        end
    end
end

function SRW.EMPAim(id,bot,target)
    if not bot.EMPRemaining or bot.EMPRemaining<=0 then return target end
    local p=GetDeviceCentrePosition(id)
    local dx,dy=target.x-p.x,target.y-p.y
    local angle=GetRandomFloat(-0.07,0.07,"SRW EMP aim")
    return Vec3(p.x+dx*math.cos(angle)-dy*math.sin(angle),
        p.y+dx*math.sin(angle)+dy*math.cos(angle),0)
end
