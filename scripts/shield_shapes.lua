-- Connected-structure outline and squad shields. All state is synchronized.
local collecting
function SRW_ShieldLink(nodeA,nodeB)
    if collecting then
        if nodeA and nodeA>0 then collecting[nodeA]=true end
        if nodeB and nodeB>0 then collecting[nodeB]=true end
    end
    return true
end
local function nodes(id)
    if not GetDeviceStructureId or not EnumerateStructureLinks then return nil end
    local sid=GetDeviceStructureId(id)
    if not sid or sid<0 then return nil end
    collecting={}
    EnumerateStructureLinks(GetStructureTeam(sid),sid,"SRW_ShieldLink",false)
    local result=collecting; collecting=nil
    return result,sid
end
local function cross(a,b,c) return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x) end
function SRW.ConvexHull(points)
    table.sort(points,function(a,b) return a.x<b.x or (a.x==b.x and a.y<b.y) end)
    local lower,upper={},{}
    local function push(t,p)
        while #t>=2 and cross(t[#t-1],t[#t],p)<=0 do t[#t]=nil end
        t[#t+1]=p
    end
    for _,p in ipairs(points) do push(lower,p) end
    for i=#points,1,-1 do push(upper,points[i]) end
    lower[#lower]=nil; upper[#upper]=nil
    for _,p in ipairs(upper) do lower[#lower+1]=p end
    return lower
end
function SRW.StructureShieldArc(id,s,initial)
    local current,sid=nodes(id)
    if not current then return nil,"invalid" end
    local origin=GetDeviceCentrePosition(id); local points={}
    for _,node in ipairs(SRW.SortedIds(current)) do
        -- Removed nodes vanish immediately. New nodes need a second reading.
        if initial or (s.StructureNodes and s.StructureNodes[node]) then
            if NodeExists(node) then
                local p=NodePosition(node)
                -- Four corners give the outline a 40-unit clearance, even on straight edges.
                for _,dx in ipairs({-40,40}) do for _,dy in ipairs({-40,40}) do
                    points[#points+1]={x=p.x-origin.x+dx,y=p.y-origin.y+dy}
                end end
            end
        end
    end
    s.StructureNodes=current; s.StructureId=sid
    if #points<3 then return nil,"invalid" end
    local arc=SRW.ConvexHull(points)
    for _,p in ipairs(arc) do
        if p.x*p.x+p.y*p.y>(s.Radius or SRW.Shield.Radius)^2 then return nil,"radius" end
    end
    arc[#arc+1]={x=arc[1].x,y=arc[1].y}
    return arc
end
function SRW_ShieldHull(team,id)
    team,id=tonumber(team),tonumber(id)
    local s=data.srw.Shields[id]
    if not s or s.Mobile or s.Active or s.Team~=team or not DeviceExists(id)
        or GetDeviceTeamIdActual(id)~=team or not IsDeviceFullyBuilt(id) or DeviceDisabled(id) then return end
    local arc,err=SRW.StructureShieldArc(id,s,true)
    if not arc then s.Status=err; return end
    if s.HP<=0 then s.Status="empty"; return end
    if GetTeamResources(team).energy<SRW.Shield.ActivationCost then s.Status="energy"; return end
    AddResources(team,{metal=0,energy=-SRW.Shield.ActivationCost},false,Vec3(0,0,0))
    s.AutoHull=true; s.Active=true; s.Arc=arc; s.Status="active"; s.ShapeWait=0
end
local function groupArc(radius)
    local arc={}
    for i=0,64 do
        local a=math.rad(-210+240*i/64)
        arc[#arc+1]={x=radius*math.cos(a),y=radius*math.sin(a)}
    end
    return arc
end
function SRW.UpdateShieldShapes(dt)
    local groups={}
    for _,id in ipairs(SRW.SortedIds(data.srw.Shields)) do
        local s=data.srw.Shields[id]; s.Pooled=nil
        if s.AutoHull and s.Active then
            s.ShapeWait=(s.ShapeWait or 0)-dt
            if s.ShapeWait<=0 then
                s.ShapeWait=0.5
                local arc,err=SRW.StructureShieldArc(id,s,false)
                if arc then s.Arc=arc else s.Active=false; s.Status=err end
            end
        end
    end
    for _,id in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local b=data.srw.Robots[id]
        if b.SquadId and DeviceExists(id) and GetDeviceTeamIdActual(id)==b.Team then
            local g=groups[b.SquadId] or {Ids={},Members={},HP=0,MaxHP=0,Team=b.Team,Mobile=true}
            groups[b.SquadId]=g; g.Ids[#g.Ids+1]=id
            local s=data.srw.Shields[id]
            if s and not DeviceDisabled(id) and IsDeviceFullyBuilt(id) then
                g.Members[#g.Members+1]=id; g.HP=g.HP+s.HP; g.MaxHP=g.MaxHP+s.MaxHP
                if b.Kind=="srw_shield_bot" then g.Support=true; g.Active=g.Active or s.Active end
            end
        end
    end
    local result={}
    for _,key in ipairs(SRW.SortedIds(groups)) do
        local g=groups[key]
        if g.Support then
            local minx,maxx,maxy=math.huge,-math.huge,-math.huge
            local positions,memberSet={},{}
            local function include(p)
                positions[#positions+1]=p
                minx=math.min(minx,p.x); maxx=math.max(maxx,p.x); maxy=math.max(maxy,p.y)
            end
            for _,id in ipairs(g.Ids) do
                memberSet[id]=true
                include(GetDeviceCentrePosition(id))
            end
            -- Low front mounts also determine the bottom of the formation;
            -- increasing radius alone cannot protect them through the opening.
            for _,id in ipairs(SRW.SortedIds(data.srw.MountedWeapons or {})) do
                local mount=data.srw.MountedWeapons[id]
                if memberSet[mount.Root] and DeviceExists(id) and GetDeviceTeamIdActual(id)==g.Team then
                    include(GetDeviceCentrePosition(id))
                end
            end
            local origin={x=(minx+maxx)/2,y=maxy+40,z=0}; local radius=300
            for _,p in ipairs(positions) do
                radius=math.max(radius,math.sqrt((p.x-origin.x)^2+(p.y-origin.y)^2)+80)
            end
            local previous=(data.srw.SquadShields or {})[-key]
            g.Origin=origin; g.Radius=radius
            -- Moving a formation does not change its relative collision arc.
            g.Arc=previous and previous.Radius==radius and previous.Arc or groupArc(radius)
            for _,id in ipairs(g.Members) do data.srw.Shields[id].Pooled=true end
            result[-key]=g
        end
    end
    data.srw.SquadShields=result
end
function SRW.CombatShields()
    local result={}
    for id,s in pairs(data.srw.Shields) do if not s.Pooled then result[id]=s end end
    for id,s in pairs(data.srw.SquadShields or {}) do result[id]=s end
    return result
end
