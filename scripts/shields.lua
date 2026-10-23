-- Shield simulation: all mutations run in Update or synchronized script events.
SRW.Shield = { BatteryWidth=80, Radius=640, MaxLength=640, MaxHP=4000,
    ActivationCost=10000, EnergyPerSecond=500, Segments=64 }
SRW.ShieldLevels={
 {Radius=640,HP=4000,Energy=500,BrokenRegen=20,IdleRegen=40},
 {Radius=960,HP=8000,Energy=800,BrokenRegen=40,IdleRegen=80},
 {Radius=1280,HP=15000,Energy=1600,BrokenRegen=100,IdleRegen=200}}
function SRW.ShieldTier(name)
 return ({srw_shield_generator=1,srw_shield_generator_2=2,srw_shield_generator_3=3})[name]
end
local C = SRW.Shield
local function cross(a,b) return a.x*b.y-a.y*b.x end
local function sub(a,b) return {x=a.x-b.x,y=a.y-b.y} end
local function finite(v) return type(v)=="number" and v==v and math.abs(v)<10000000 end

-- Mobile roots can be raised to leave room for lower front weapons. The dome
-- follows their ground anchor, not the raised weapon's visual centre.
function SRW.ShieldOrigin(id,s)
    if s.Origin then return s.Origin end
    if s.Mobile then
        local p=GetDevicePosition(id)
        local bot=data.srw.Robots[id]
        return Vec3(p.x,p.y+(bot and bot.GroundLift or 0),p.z or 0)
    end
    return GetDeviceCentrePosition(id)
end

-- A and B are endpoints; M is the point halfway along the curve parameter.
function SRW.ShieldArc(a,b,m,radius)
    radius=radius or C.Radius
    for _,p in ipairs({a,b,m}) do
        if not finite(p.x) or not finite(p.y) then return nil,"invalid" end
    end
    local chord=sub(b,a)
    if chord.x^2+chord.y^2<25 then return nil,"invalid" end
    if cross(chord,sub(m,a))*cross(chord,{x=-a.x,y=-a.y})>=-0.001 then return nil,"bend" end
    local control={x=2*m.x-(a.x+b.x)/2,y=2*m.y-(a.y+b.y)/2}
    local arc,length={},0
    for i=0,C.Segments do
        local t=i/C.Segments; local u=1-t
        local p={x=u*u*a.x+2*u*t*control.x+t*t*b.x,y=u*u*a.y+2*u*t*control.y+t*t*b.y}
        if p.x^2+p.y^2>radius^2 then return nil,"radius" end
        if i>0 then local q=arc[#arc]; length=length+math.sqrt((p.x-q.x)^2+(p.y-q.y)^2) end
        arc[#arc+1]=p
    end
    if length>C.MaxLength then return nil,"length" end
    return arc,nil,length
end

function SRW.ShieldIntersection(a,b,c,d)
    -- This narrow phase runs for every nearby projectile/arc segment.
    -- Scalars avoid three temporary tables for each intersection test.
    local rx,ry=b.x-a.x,b.y-a.y
    local sx,sy=d.x-c.x,d.y-c.y
    local den=rx*sy-ry*sx
    if math.abs(den)<0.000001 then return nil end
    local qx,qy=c.x-a.x,c.y-a.y
    local t,u=(qx*sy-qy*sx)/den,(qx*ry-qy*rx)/den
    if t>=0 and t<=1 and u>=0 and u<=1 then return t end
end

function SRW.ScanShields()
    local shields=data.srw.Shields
    for side=1,2 do
        for index=0,GetDeviceCountSide(side)-1 do
            local id=GetDeviceIdSide(side,index)
            if (SRW.Config.Robots[GetDeviceType(id)] or {}).ShieldHP and data.srw.Robots[id] then
                local team=GetDeviceTeamIdActual(id)
                if not shields[id] or shields[id].Team~=team then shields[id]=SRW.NewMobileShield(team,GetDeviceType(id)) end
            end
            if SRW.ShieldTier(GetDeviceType(id)) and IsDeviceFullyBuilt(id) then
                local team=GetDeviceTeamIdActual(id)
                if not shields[id] or shields[id].Team~=team then
                    local tier=SRW.ShieldTier(GetDeviceType(id));local cfg=SRW.ShieldLevels[tier]
                    shields[id]={Team=team,Tier=tier,HP=cfg.HP,MaxHP=cfg.HP,Radius=cfg.Radius,Active=false,Status="off"}
                end
            end
        end
    end
    for _,id in ipairs(SRW.SortedIds(shields)) do
        if not DeviceExists(id) or (not SRW.ShieldTier(GetDeviceType(id)) and
            (not (SRW.Config.Robots[GetDeviceType(id)] or {}).ShieldHP or not data.srw.Robots[id] or data.srw.Robots[id].Team~=GetDeviceTeamIdActual(id))) then shields[id]=nil end
    end
end

local function valid(team,id)
    local s=data.srw.Shields[id]
    if s and not s.Mobile and DeviceExists(id) and s.Team==team and GetDeviceTeamIdActual(id)==team
        and IsDeviceFullyBuilt(id) then return s end
end

function SRW_ShieldActivate(team,id,ax,ay,bx,by,mx,my)
    team,id=tonumber(team),tonumber(id)
    local s=valid(team,id); if not s or s.Active then return end
    if DeviceDisabled(id) then s.Status="disabled"; return end
    local arc,err=SRW.ShieldArc({x=tonumber(ax),y=tonumber(ay)},
        {x=tonumber(bx),y=tonumber(by)},{x=tonumber(mx),y=tonumber(my)},s.Radius)
    if not arc then s.Status=err; return end
    if s.HP<=0 then s.Status="empty"; return end
    if GetTeamResources(team).energy<C.ActivationCost then s.Status="energy"; return end
    AddResources(team,{metal=0,energy=-C.ActivationCost},false,Vec3(0,0,0))
    s.AutoHull=false; s.Arc=arc; s.Active=true; s.Status="active"
end

function SRW_ShieldDeactivate(team,id)
    local s=valid(tonumber(team),tonumber(id))
    if s then s.AutoHull=false; s.Active=false; s.Status="off" end
end

function SRW.ShieldDamage(s,damage)
    if s.Members then
        local total=math.max(1,s.HP)
        for _,id in ipairs(s.Members) do
            local part=data.srw.Shields[id]
            if part then SRW.ShieldDamage(part,damage*part.HP/total) end
        end
        s.HP=0
        for _,id in ipairs(s.Members) do s.HP=s.HP+data.srw.Shields[id].HP end
        if s.HP<=0 then s.Active=false end
        return
    end
    s.QuietSeconds=0
    s.HP=math.max(0,s.HP-math.max(0,damage)*(s.EMPWeakened and 1.5 or 1))
    if s.HP==0 then s.Active=false; s.ColdRecovery=true; s.Status="broken" end
end

function SRW.UpdateShieldPower(dt)
    for _,id in ipairs(SRW.SortedIds(data.srw.Shields)) do
        local s=data.srw.Shields[id]
        if s.Mobile then SRW.UpdateMobileShield(id,s,dt)
        else
            local cfg=SRW.ShieldLevels[s.Tier or 1]
            s.MaxHP=cfg.HP;s.Radius=cfg.Radius;s.HP=math.min(s.HP,cfg.HP)
            s.QuietSeconds=(s.QuietSeconds or 10)+dt
            if DeviceDisabled(id) or not IsDeviceFullyBuilt(id) then s.Active=false;s.Status="disabled"
            elseif s.Active or s.HP<cfg.HP then
                local cost=cfg.Energy*dt
                if GetTeamResources(s.Team).energy<cost then s.Active=false;s.Status="energy"
                else
                    AddResources(s.Team,{metal=0,energy=-cost},false,Vec3(0,0,0))
                    if s.ColdRecovery or s.QuietSeconds>=10 then
                        s.HP=math.min(cfg.HP,s.HP+(s.ColdRecovery and cfg.BrokenRegen or cfg.IdleRegen)*dt)
                    end
                    if s.ColdRecovery then
                        s.Status="recovering"
                        if s.HP>=cfg.HP then s.ColdRecovery=false;s.Status="off" end
                    else s.Status=s.Active and "active" or "off" end
                end
            end
        end
    end
end

-- Swept path + one-step prediction: fast projectiles cannot simply jump over a
-- sampled curve. Prediction is approximate for homing/teleporting projectiles.
function SRW.InterceptShieldProjectiles(dt)
    local shields=SRW.CombatShields and SRW.CombatShields() or data.srw.Shields
    local active=false
    for _,s in pairs(shields) do if s.Active then active=true; break end end
    if not active then data.srw.ShieldProjectiles={}; return end
    local ids={}
    for side=1,2 do
        for index=0,ProjectileCount(side)-1 do ids[#ids+1]=GetProjectileId(side,index) end
    end
    table.sort(ids)
    local previous=data.srw.ShieldProjectiles; local nextPrevious={}
    local shieldIds=SRW.SortedIds(shields)
    for _,id in ipairs(ids) do
        if NodeExists(id) then
            local p=NodePosition(id); local v=NodeVelocity(id); local team=NodeTeam(id)
            local start=previous[id] or {x=p.x,y=p.y}
            local finish={x=p.x+v.x*dt,y=p.y+v.y*dt}
            local best,bestT
            for _,sid in ipairs(shieldIds) do
                local s=shields[sid]
                if s.Active and s.Arc and team%100~=s.Team%100 then
                    local origin=SRW.ShieldOrigin(sid,s)
                    local radius=s.Radius or C.Radius
                    local a,b=sub(start,origin),sub(finish,origin)
                    -- Reject swept paths outside the generator's bounding square.
                    -- Test both ends so fast crossing shots still reach narrow phase.
                    if math.min(a.x,b.x)<=radius and math.max(a.x,b.x)>=-radius
                        and math.min(a.y,b.y)<=radius and math.max(a.y,b.y)>=-radius then
                        for n=1,#s.Arc-1 do
                            local t=SRW.ShieldIntersection(a,b,s.Arc[n],s.Arc[n+1])
                            if t and (not bestT or t<bestT) then best,bestT=s,t end
                        end
                    end
                end
            end
            if best then
                local name=GetNodeProjectileSaveName(id)
                local direct=GetProjectileParamFloat(name,team,"ProjectileDamage",0)
                local splash=GetProjectileParamFloat(name,team,"ProjectileSplashDamage",0)
                -- Override for special ammunition; default is direct + splash damage.
                local damage=GetProjectileParamFloat(name,team,"SRWShieldDamage",math.max(1,direct+splash))
                SRW.ShieldDamage(best,damage)
                DestroyProjectile(id)
            else nextPrevious[id]={x=p.x,y=p.y} end
        end
    end
    data.srw.ShieldProjectiles=nextPrevious
end
