-- Local X points towards the enemy; negative Y is up. Based on the user's
-- arrangement.bmp: rockets rear/top, artillery middle, AA front/high,
-- lasers and direct fire front/low. Positions are attachment points, not muzzles.
local roles={
    srw_archangel_bot="direct",srw_archangel_turret="direct",srw_archangel_rockets="rockets",
    srw_hornet_bot="direct",srw_hornet_rockets="rockets",srw_sledge_bot="direct",srw_skat_bot="direct",srw_lantern_bot="direct",srw_parcel_bot="direct",srw_skat_rockets="rockets",
    srw_vault_bot="aa",srw_vault_gun="aa",srw_vault_laser="aa",srw_vault_rockets="rockets",
    srw_censer_mortar="artillery",srw_censer_laser="direct",
    srw_tempest_bot="artillery",srw_tempest_gun="direct",srw_tempest_defence="direct",
    srw_mlrs_bot="rockets",srw_mlrs_launcher="rockets",srw_mlrs_defence="direct",

    srw_hound="direct", srw_hound_machinegun="direct",
    srw_siege_bot="artillery", srw_aa_bot="aa", srw_sieve_turret="aa",
    srw_sentry_bot="aa", srw_sentry_rockets="rockets",
    srw_tank_bot="direct", srw_tank_turret="direct", srw_tank_rockets="rockets",
    srw_hunter_bot="direct", srw_hunter_rockets="rockets", srw_hunter_interceptor="direct",
    srw_rocket_bot="rockets", srw_psalm_turret="direct",
    srw_smith_bot="direct", srw_smith_flame="direct", srw_smith_rockets="rockets",
    srw_pike_bot="rockets", srw_pike_turret="direct",
    srw_emp_bot="direct", srw_emp_turret="direct", srw_laser_bot="direct",
    srw_colossus_bot="artillery", srw_colossus_laser="direct",
    srw_regent_rockets="rockets", srw_regent_turret="direct",
    srw_bastion_bot="artillery", srw_heavy_siege_bot="artillery", srw_heavy_aa_bot="aa",
    srw_heavy_aa_gun="aa", srw_heavy_aa_rockets="rockets", srw_heavy_aa_defence="direct",
    srw_executioner_bot="direct", srw_executioner_gun="direct", srw_executioner_rockets="rockets",
    srw_storm_bot="direct", srw_storm_rockets="rockets", srw_storm_interceptor="direct",
}
local slots={rockets={-180,-500},artillery={0,-300},aa={300,-320},direct={420,0}}
local function slot(role,index,scale,roof,tops)
    local base=slots[role]
    -- Upper direct guns step BACK, leaving the lower gun's rising trajectory
    -- clear. Front/upper stairs used to put another gun directly in that path.
    local dx=(role=="direct" or role=="aa") and -130 or (role=="rockets" and -130 or 130)
    local y=role=="rockets" and roof or (tops and tops[role] or base[2])
    return (base[1]+dx*index)*scale,(y-220*index)*scale
end

-- Make the old implicit Bastion loadout explicit so every mount uses the layout.
SRW.Config.Robots.srw_tank_bot.Mounts={
    {Kind="srw_tank_turret"}, {Kind="srw_tank_rockets",AntiAir=true},
}
for kind,cfg in pairs(SRW.Config.Robots) do
    cfg.WeaponRole=roles[kind]
    if cfg.Mounts then
        local role=assert(roles[kind],"Missing root weapon role: "..kind)
        local scale=cfg.Tier==1 and 0.7 or (cfg.Tier==2 and 0.85 or 1)
        local totals={[role]=1}
        for _,mount in ipairs(cfg.Mounts) do
            local childRole=assert(roles[mount.Kind],"Missing mounted weapon role: "..mount.Kind)
            totals[childRole]=(totals[childRole] or 0)+1
        end
        local directTop=-220*math.max(0,(totals.direct or 0)-1)
        local tops={direct=0,artillery=math.min(-300,directTop-220),aa=math.min(-320,directTop-240)}
        local ordinals={[role]=1}
        local roof=-500
        if role~="rockets" then local _,y=slot(role,0,1,nil,tops);roof=math.min(roof,y-220) end
        for _,mount in ipairs(cfg.Mounts) do
            local childRole=roles[mount.Kind]
            local ordinal=ordinals[childRole] or 0
            if childRole~="rockets" then local _,y=slot(childRole,ordinal,1,nil,tops);roof=math.min(roof,y-220) end
            ordinals[childRole]=ordinal+1
        end
        local rootX,rootY=slot(role,0,scale,roof,tops)
        cfg.RootLift=-rootY
        local counts={[role]=1}
        for index,mount in ipairs(cfg.Mounts) do
            local childRole=assert(roles[mount.Kind],"Missing mounted weapon role: "..mount.Kind)
            local ordinal=counts[childRole] or 0
            local x,y=slot(childRole,ordinal,scale,roof,tops)
            mount.X,mount.Y=x-rootX,y-rootY
            mount.Role=childRole
            counts[childRole]=ordinal+1
        end
    end
end

function SRW.RobotGroundPosition(id,bot)
    local p=GetDevicePosition(id)
    return Vec3(p.x,p.y+(bot.GroundLift or 0),0)
end

-- The approved Hornet's missiles are inside the hull, not a rear floating silo.
-- Both visual and native launch origin come from the same exported geometry.
SRW.Config.Robots.srw_hornet_bot.Mounts[1].X=-23.5
SRW.Config.Robots.srw_hornet_bot.Mounts[1].Y=-85

function SRW.RobotGroundStep(id,bot,x)
    local p=SRW.RobotGroundPosition(id,bot)
    local ground=SRW.GroundAt(x,p.y,SRW.Config.Prototype.StepHeight)
    if ground then return Vec3(ground.x,ground.y-(bot.GroundLift or 0),0) end
end
