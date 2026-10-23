-- Independent native-missile steering; intentionally no tracker/sector rendering.
local names={srw_archangel_rocket=true,srw_hornet_rocket=true,srw_heavy_aa_rocket=true,srw_executioner_at=true,srw_pike_rocket=true,srw_salvo_rocket=true,srw_tank_aa_rocket=true,srw_sentry_rocket=true,srw_hunter_at_rocket=true}
function SRW.GuidedLaunch(team,weapon,node)
    if not NodeExists(node) or not names[GetNodeProjectileSaveName(node)] then return end
    SRW.EnsureState()
    local bot=data.srw.Robots[weapon] or data.srw.MountedWeapons[weapon]
    if not bot or bot.Team~=team then return end
    local root=bot.Root and data.srw.Robots[bot.Root]
    local disabled=(bot.EMPRemaining or 0)>0 or (root and (root.EMPRemaining or 0)>0)
    local velocity=NodeVelocity(node)
    local vertical=velocity.y<0 and math.abs(velocity.y)>math.abs(velocity.x)*2
    data.srw.GuidedMissiles[node]={Team=team,Name=GetNodeProjectileSaveName(node),
        Target=not disabled and bot.Target or nil,Air=bot.AntiAir==true or (SRW.Config.Robots[bot.Kind] or {}).AntiAir==true,
        TargetPoint=not disabled and bot.TargetPoint or nil,TargetIsDevice=bot.TargetIsDevice,
        VerticalLaunch=vertical,Acquiring=vertical,Age=0}
end
function SRW.UpdateGuidance(dt)
    for _,id in ipairs(SRW.SortedIds(data.srw.GuidedMissiles)) do
        local m=data.srw.GuidedMissiles[id]
        m.Age=m.Age+dt
        if not NodeExists(id) or NodeTeam(id)%100~=m.Team%100
            or GetNodeProjectileSaveName(id)~=m.Name or m.Age>8 then
            data.srw.GuidedMissiles[id]=nil
        else
            local p=NodePosition(id); local v=NodeVelocity(id)
            local speed=math.sqrt(v.x*v.x+v.y*v.y)
            local aim
            if m.Target then
                if not m.TargetIsDevice and m.Air and NodeExists(m.Target) and NodeTeam(m.Target)%100~=m.Team%100 then
                    local q=NodePosition(m.Target)
                    aim=SRW.InterceptPoint(p,q,NodeVelocity(m.Target),math.max(1,speed)) or q
                elseif (not m.Air or m.TargetIsDevice) and DeviceExists(m.Target) and GetDeviceTeamIdActual(m.Target)%100~=m.Team%100 then
                    aim=GetDeviceCentrePosition(m.Target)
                    local targetBot=data.srw.Robots[m.Target]
                    if targetBot and targetBot.AirVelocity then
                        aim=SRW.InterceptPoint(p,aim,targetBot.AirVelocity,math.max(1,speed)) or aim
                    end
                end
            end
            if not aim and not m.Air and m.Target and m.Target<0 and m.TargetPoint then
                aim=Vec3(m.TargetPoint.x,m.TargetPoint.y,0)
            end
            if aim then
                local dx,dy=aim.x-p.x,aim.y-p.y; local distance=math.sqrt(dx*dx+dy*dy)
                -- A forward 120-degree seeker; no U-turns after missing a target.
                local inCone=distance<=1 or speed<=1 or dx*v.x+dy*v.y>=0.5*distance*speed
                if m.Acquiring and (inCone or m.Age>1.5) then m.Acquiring=false end
                if distance>24000 or (not m.Acquiring and not inCone) then aim=nil end
            end
            if not aim then
                m.Target=nil
                aim=Vec3(p.x+v.x*10,p.y+v.y*10,0)
            end
            -- A short native-style vertical departure before turning onto the
            -- assigned target. Speed and maximum turn rate remain unchanged.
            if m.VerticalLaunch and m.Age<.12 then aim=Vec3(p.x+v.x,p.y+v.y,0) end
            SetMissileTarget(id,aim)
        end
    end
end
