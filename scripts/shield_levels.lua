function SRW.ShieldCreated(team,id,name,upgraded)
    local tier=SRW.ShieldTier(name)
    if not tier then return end
    SRW.EnsureState()
    local previous=upgraded and data.srw.Shields[upgraded]
    if previous and previous.Team==team then
        if id~=upgraded then data.srw.Shields[upgraded]=nil end
        local cfg=SRW.ShieldLevels[tier]
        previous.HP=math.min(previous.HP,cfg.HP)
        previous.Tier=tier;previous.MaxHP=cfg.HP;previous.Radius=cfg.Radius
        previous.Active=false;previous.Status="off"
        data.srw.Shields[id]=previous
        return
    end
    local count=0
    for i=0,GetDeviceCountSide(team%100)-1 do
        local other=GetDeviceIdSide(team%100,i)
        if other~=id and other~=upgraded and DeviceExists(other)
            and SRW.ShieldTier(GetDeviceType(other)) then count=count+1 end
    end
    if count>=2 then
        local cost=GetDeviceCost(name)
        if DeleteDeviceById(id) then AddResources(team,cost,false,Vec3(0,0,0)) end
        Log("[SRW] Shield limit: two generators per allied side")
    end
end

-- Native beam-only fields; projectile interception stays with the swept arc.
function SRW.UpdateBeamBarriers(dt)
    data.srw.BeamBarriers=data.srw.BeamBarriers or {}
    local barriers=data.srw.BeamBarriers
    local function clear(b)
        for _,node in ipairs(b.Nodes) do if NodeExists(node) then DestroyProjectile(node) end end
    end
    for _,id in ipairs(SRW.SortedIds(barriers)) do
        local s=data.srw.Shields[id]
        if not s or s.Tier~=3 or not s.Active or not DeviceExists(id) then
            clear(barriers[id]);barriers[id]=nil
        end
    end
    if not dlc2_CreateProjectile then return end
    for _,id in ipairs(SRW.SortedIds(data.srw.Shields)) do
        local s=data.srw.Shields[id]
        if s.Tier==3 and s.Active and s.Arc and DeviceExists(id) then
            local p=GetDeviceCentrePosition(id)
            local b=barriers[id]
            if b then b.Wait=b.Wait-dt end
            if not b or b.Wait<=0 or (b.X-p.x)^2+(b.Y-p.y)^2>100 then
                if b then clear(b) end
                b={Nodes={},Wait=.4,X=p.x,Y=p.y};barriers[id]=b
                local gap=0
                local function spawn(x,y)
                    local node=dlc2_CreateProjectile("srw_beam_barrier","cannon",s.Team,
                        Vec3(p.x+x,p.y+y,0),Vec3(0,0,0),.5)
                    if node and node>=0 then b.Nodes[#b.Nodes+1]=node end
                end
                for i=1,#s.Arc-1 do
                    local a,c=s.Arc[i],s.Arc[i+1]
                    local length=math.sqrt((a.x-c.x)^2+(a.y-c.y)^2)
                    if length>0 then
                        while gap<=length do
                            local t=gap/length
                            spawn(a.x+(c.x-a.x)*t,a.y+(c.y-a.y)*t)
                            gap=gap+80
                        end
                        gap=gap-length
                    end
                end
                if gap<40 then local last=s.Arc[#s.Arc];spawn(last.x,last.y) end
            end
        end
    end
end

function OnFieldHitBeam(node,field,weapon,team,beam)
    if field~="srw_beam_barrier" then return end
    for id,b in pairs(data.srw.BeamBarriers or {}) do
        for _,n in ipairs(b.Nodes) do
            if n==node then
                local s=data.srw.Shields[id]
                if s and s.Active and team%100~=s.Team%100 then
                    local dps=GetProjectileParamFloat(beam,team,"ProjectileDamage",1000)
                    if dps<=0 then dps=1000 end -- function-driven vanilla beam damage
                    SRW.ShieldDamage(s,math.max(1,dps)*.04)
                end
                return
            end
        end
    end
end
