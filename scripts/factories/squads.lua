-- Serializable squad state stays on the factory; templates belong to its owner.
SRW.RobotKinds={"srw_dynamit_bot","srw_hound","srw_repair_bot","srw_siege_bot","srw_aa_bot","srw_shield_bot","srw_emp_bot","srw_laser_bot","srw_rocket_bot","srw_hunter_bot","srw_bastion_bot","srw_heavy_aa_bot","srw_heavy_siege_bot","srw_tank_bot","srw_colossus_bot","srw_sentry_bot","srw_smith_bot","srw_pike_bot","srw_executioner_bot","srw_storm_bot","srw_vault_bot","srw_tempest_bot","srw_mlrs_bot","srw_hornet_bot","srw_sledge_bot","srw_skat_bot","srw_lantern_bot","srw_parcel_bot","srw_archangel_bot","srw_engineer_bot"}
local function copy(items)
    local result={}; for i,kind in ipairs(items) do result[i]=kind end; return result
end
local function owned(team,id)
    team,id=tonumber(team),tonumber(id)
    return SRW.ValidFactory(team,id),team,id
end
function SRW.SquadPending(f)
    return f.Squad and math.max(0,#f.Squad.Items-f.Squad.Produced-(f.CurrentSquad and 1 or 0)) or 0
end
function SRW.SquadStored(f)
    return f.Squad and f.Squad.Produced-f.Squad.Released or 0
end
function SRW.SquadBusy(f) return f.Squad and f.Squad.Released<#f.Squad.Items end

function SRW_SquadEdit(team,id,index,delta)
    local f=owned(team,id); index,delta=tonumber(index),tonumber(delta)
    local kind=index and SRW.RobotKinds[index]
    if not f or not kind or (delta~=1 and delta~=-1) then return end
    f.SquadDraft=f.SquadDraft or {}
    if delta==1 then
        if not SRW.FactoryCanProduce(f,kind) then f.Status="tier_required"; return end
        if #f.SquadDraft>=SRW.FactoryCapacity(f) then f.Status="squad_full"; return end
        local count=0; for _,k in ipairs(f.SquadDraft) do if k==kind then count=count+1 end end
        if count>=SRW.Config.Robots[kind].ActiveLimit then f.Status="limit"; return end
        f.SquadDraft[#f.SquadDraft+1]=kind
    else
        for i=#f.SquadDraft,1,-1 do
            if f.SquadDraft[i]==kind then table.remove(f.SquadDraft,i); break end
        end
    end
end
function SRW_SquadClear(team,id)
    local f=owned(team,id); if f then f.SquadDraft={} end
end
function SRW_SquadSave(team,id)
    local f,owner=owned(team,id); if not f then return end
    data.srw.SquadTemplates=data.srw.SquadTemplates or {}
    data.srw.SquadTemplates[(f.Domain=="air" and tostring(owner)..":air" or owner)]=copy(f.SquadDraft or {})
    f.Status="squad_saved"
end
function SRW_SquadLoad(team,id)
    local f,owner=owned(team,id); if not f then return end
    local saved=data.srw.SquadTemplates and data.srw.SquadTemplates[(f.Domain=="air" and tostring(owner)..":air" or owner)]
    if not saved then f.Status="squad_no_template"; return end
    if #saved>SRW.FactoryCapacity(f) then f.Status="squad_full"; return end
    f.SquadDraft=copy(saved)
end
function SRW_SquadStart(team,id)
    local f=owned(team,id); if not f then return end
    if SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    local items=f.SquadDraft or {}
    if #items==0 then f.Status="squad_empty"; return end
    local occupied=SRW.FactoryReserve(f)+SRW.NormalFactoryQueue(f)+(f.Remaining>0 and 1 or 0)
    if occupied+#items>SRW.FactoryCapacity(f) then f.Status="squad_full"; return end
    local work,speed=0,0; local counts={}
    for _,kind in ipairs(items) do
        local cfg=SRW.Config.Robots[kind]; if not cfg then return end
        if not SRW.FactoryCanProduce(f,kind) then f.Status="tier_required"; return end
        counts[kind]=(counts[kind] or 0)+1
        if counts[kind]>cfg.ActiveLimit then f.Status="limit"; return end
        work=work+cfg.ProductionSeconds; speed=speed+cfg.SpeedMinesPerSecond
    end
    data.srw.NextSquadId=(data.srw.NextSquadId or 0)+1
    f.Squad={Id=data.srw.NextSquadId,Items=copy(items),Produced=0,Released=0,TotalWork=work,Speed=speed/#items,Releasing=false}
    f.Status="squad_started"
end
function SRW_SquadRelease(team,id)
    local f=owned(team,id); if not f or not f.Squad then return end
    if f.Squad.Produced<#f.Squad.Items then f.Status="squad_not_ready"; return end
    f.Squad.Releasing=f.Squad.Released<#f.Squad.Items
end
function SRW.SquadEstimate(f)
    local s=f.Squad; if not s then return 0,0 end
    local remaining=f.CurrentSquad and f.Remaining or 0
    local first=s.Produced+1+(f.CurrentSquad and 1 or 0)
    for i=first,#s.Items do remaining=remaining+SRW.Config.Robots[s.Items[i]].ProductionSeconds end
    local progress=s.TotalWork>0 and math.max(0,math.min(1,1-remaining/s.TotalWork)) or 1
    -- Existing individual orders finish before this squad. Resource pauses have no finite ETA.
    if s.Produced<#s.Items and not f.CurrentSquad then
        remaining=remaining+(f.Remaining or 0)
        for i,field in ipairs({"Queue","HoundQueue","RepairQueue","SiegeQueue","AAQueue"}) do
            remaining=remaining+(f[field] or 0)*SRW.Config.Robots[SRW.RobotKinds[i]].ProductionSeconds
        end
    end
    if s.Produced<#s.Items and not f.CurrentSquad then
        for i=6,#SRW.RobotKinds do
            local kind=SRW.RobotKinds[i]
            remaining=remaining+(f[kind.."Queue"] or 0)*SRW.Config.Robots[kind].ProductionSeconds
        end
    end
    return remaining,progress
end
function SRW.UpdateSquadRelease(f,id)
    local s=f.Squad
    if not s or not s.Releasing or s.Produced<#s.Items or not SRW.ValidFactory(f.Team,id) then return end
    if (f.ExitRemaining or 0)>0 then return end
    if s.Released>=#s.Items then s.Releasing=false; return end
    local kind=s.Items[s.Released+1]
    if SRW.ActiveCount(f.Team,kind)>=SRW.Config.Robots[kind].ActiveLimit then f.Status="limit"; return end
    if not SRW.FactoryCanProduce(f,kind) then f.Status="tier_required";return end
    local success,root=SRW.SpawnFactoryRobot(f.Team,id,kind)
    if success then
        -- Older saves have no cached mean; derive it once from the original roster.
        if not s.Speed then
            local total=0
            for _,item in ipairs(s.Items) do total=total+SRW.Config.Robots[item].SpeedMinesPerSecond end
            s.Speed=total/#s.Items
        end
        if root and data.srw.Robots[root] then
            if not s.Id then data.srw.NextSquadId=(data.srw.NextSquadId or 0)+1; s.Id=data.srw.NextSquadId end
            data.srw.Robots[root].SquadSpeed=s.Speed
            data.srw.Robots[root].SquadId=s.Id
        end
        s.Released=s.Released+1; SRW.MarkExit(f,kind)
        if s.Released==#s.Items then s.Releasing=false; f.Status="squad_released" end
    else
        f.Status="exit_blocked"
        f.ExitRemaining=0.5 -- retry bounded, without consuming the waiting robot
    end
end
