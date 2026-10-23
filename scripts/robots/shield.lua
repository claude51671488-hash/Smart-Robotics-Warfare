-- Unarmed escort. Its bubble shares the stationary shield interception pass.
function SRW.SpawnShieldBot(team,factory)
    return SRW.SpawnRepairBot(team,factory,"srw_shield_bot")
end

function SRW.UpdateShieldBot(id,bot,dt)
    local cfg=SRW.Config.Robots.srw_shield_bot
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then return end
    bot.EscortWait=math.max(0,(bot.EscortWait or 0)-dt)
    if bot.EscortWait>0 then return end
    bot.EscortWait=0.2
    local p=GetDevicePosition(id); local centre=GetDeviceCentrePosition(id)
    local target,distance
    for _,other in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local candidate=data.srw.Robots[other]
        if other~=id and candidate.Team%100==bot.Team%100 and DeviceExists(other)
            and GetDeviceTeamIdActual(other)%100==bot.Team%100
            and IsDeviceFullyBuilt(other) and not candidate.FuseRemaining
            and candidate.Kind~="srw_shield_bot" and candidate.Kind~="srw_repair_bot"
            and candidate.Kind~="srw_aa_bot" and candidate.Kind~="srw_heavy_aa_bot" then
            local q=GetDeviceCentrePosition(other)
            local d=(q.x-centre.x)^2+(q.y-centre.y)^2
            if (q.x-centre.x)*bot.Direction>=0 and (not distance or d<distance) then
                target,distance=other,d
            end
        end
    end
    if not target or distance<=cfg.FollowDistance^2 then return end
    local step=SRW.RobotSpeed(bot,cfg)*SRW.Config.Units.MineWidth*0.2
    local ground=SRW.GroundAt(p.x+bot.Direction*step,p.y,SRW.Config.Prototype.StepHeight)
    if ground then
        local destination=Vec3(centre.x+ground.x-p.x,centre.y+ground.y-p.y,0)
        if (SRW.MovementRay or CastRayFromDevice)(id,destination,0,RAY_EXCLUDE_BG_MATERIALS,0)==RAY_HIT_NOTHING then
            dlc2_SetDevicePosition(id,ground)
        end
    end
end

function SRW.UpdateMobileShield(id,s,dt)
    local cfg=SRW.Config.Robots[s.Kind or "srw_shield_bot"]
    local bot=data.srw.Robots[id]
    SRW.UpdateMobileShieldShape(id,s,cfg)
    s.EMPWeakened=(cfg.Tier or 1)>=3 and bot and (bot.EMPRemaining or 0)>0 or false
    if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then s.Active=false; return end
    if s.ColdRecovery then
        s.Active=false
        s.HP=math.min(cfg.ShieldHP,s.HP+cfg.ShieldRegen*dt*(s.EMPWeakened and 0.5 or 1))
        if s.HP>=cfg.ShieldHP then s.ColdRecovery=false end
    else s.Active=true end
end

function SRW.MobileShieldArc(radius)
    local arc={}
    for i=0,64 do
        -- Screen Y points down: leave the lower 120 degrees open.
        local angle=math.rad(-210+240*i/64)
        arc[#arc+1]={x=radius*math.cos(angle),y=radius*math.sin(angle)}
    end
    return arc
end

function SRW.UpdateMobileShieldShape(id,s,cfg)
    local origin=SRW.ShieldOrigin(id,s)
    local radius=cfg.ShieldRadius
    local function include(p)
        local dx,dy=p.x-origin.x,p.y-origin.y
        -- Round only the extra envelope to avoid reallocating an arc because of
        -- tiny floating point differences while translating the same assembly.
        radius=math.max(radius,math.ceil((math.sqrt(dx*dx+dy*dy)+80)/8)*8)
    end
    include(GetDeviceCentrePosition(id))
    for child,part in pairs(data.srw.MountedWeapons or {}) do
        if part.Root==id and DeviceExists(child) and GetDeviceTeamIdActual(child)==s.Team then
            include(GetDeviceCentrePosition(child))
        end
    end
    if s.Radius~=radius or not s.Arc then s.Arc=SRW.MobileShieldArc(radius) end
    s.Radius=radius
end

function SRW.NewMobileShield(team,kind)
    kind=kind or "srw_shield_bot"
    local cfg=SRW.Config.Robots[kind]
    return {Team=team,Kind=kind,HP=cfg.ShieldHP,MaxHP=cfg.ShieldHP,Mobile=true,
        Active=false,Radius=cfg.ShieldRadius,Arc=SRW.MobileShieldArc(cfg.ShieldRadius)}
end
