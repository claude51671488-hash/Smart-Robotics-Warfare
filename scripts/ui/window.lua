-- Local HUD only. No minimap data enters synchronized simulation state.
local parent="srw_factory_window"
local elapsed=0
local pool=0
local selected=nil
local closed=nil
local mapBounds=nil
function SRW.CreateFactoryWindow()
    LoadControl(path .. "/ui/factory_window.lua", "")
    AddTextButtonControl(parent,"srw_window_close","X",ANCHOR_TOP_LEFT,Vec3(856,10,-101),false,"Readout")
    AddTextControl(parent,"srw_map_title","$SRW_UI.MapTitle",ANCHOR_TOP_LEFT,Vec3(660,48,-101),false,"Readout")
    AddTextControl(parent,"srw_map_blue","$SRW_UI.MapRobots",ANCHOR_TOP_LEFT,Vec3(660,234,-101),false,"Readout")
    SetControlColour(parent,"srw_map_blue",{r=70,g=170,b=255,a=255})
    AddTextControl(parent,"srw_map_red","$SRW_UI.MapReactors",ANCHOR_TOP_LEFT,Vec3(660,252,-101),false,"Readout")
    SetControlColour(parent,"srw_map_red",{r=255,g=80,b=70,a=255})
    pool=0; elapsed=1; mapBounds=nil
    ShowControl("",parent,false)
end
function SRW.FactoryWindowVisible(id)
    if selected~=id then selected=id; closed=nil; elapsed=1 end
    local visible=id~=nil and closed~=id
    ShowControl("",parent,visible)
    return visible
end
function SRW.CloseFactoryWindow(id)
    closed=id; ShowControl("",parent,false)
end
function SRW.MapPosition(p,b)
    local width=math.max(1,b.MaxX-b.MinX); local height=math.max(1,b.MaxY-b.MinY)
    -- Preserve aspect ratio, with padding so edge markers remain visible.
    local scale=math.min(188/width,138/height)
    return Vec3(666+(188-width*scale)/2+(p.x-b.MinX)*scale,
        76+(138-height*scale)/2+(p.y-b.MinY)*scale,-102)
end
-- Fit the battle, not artificial world limits introduced by other mods.
-- Keep extents until the HUD is rebuilt; deaths must not make the map jump.
function SRW.MapBounds(anchors)
    local minX,maxX,minY,maxY
    for _,p in ipairs(anchors) do
        minX=minX and math.min(minX,p.x) or p.x; maxX=maxX and math.max(maxX,p.x) or p.x
        minY=minY and math.min(minY,p.y) or p.y; maxY=maxY and math.max(maxY,p.y) or p.y
    end
    if not minX then return mapBounds or {MinX=-1000,MaxX=1000,MinY=-750,MaxY=750} end
    if not mapBounds or minX<mapBounds.MinX or maxX>mapBounds.MaxX or minY<mapBounds.MinY or maxY>mapBounds.MaxY then
        local padx=math.max(500,(maxX-minX)*0.08); local pady=math.max(500,(maxY-minY)*0.08)
        local b={MinX=minX-padx,MaxX=maxX+padx,MinY=minY-pady,MaxY=maxY+pady}
        if mapBounds then
            b.MinX=math.min(b.MinX,mapBounds.MinX); b.MaxX=math.max(b.MaxX,mapBounds.MaxX)
            b.MinY=math.min(b.MinY,mapBounds.MinY); b.MaxY=math.max(b.MaxY,mapBounds.MaxY)
        end
        mapBounds=b
    end
    return mapBounds
end
function SRW.RefreshFactoryMap(dt)
    if not selected or closed==selected then return end
    elapsed=elapsed+(dt or 0)
    if elapsed<0.2 then return end
    elapsed=0
    local side=GetLocalTeamId()%100
    local points={}
    for _,id in ipairs(SRW.SortedIds(data.srw.Robots)) do
        if DeviceExists(id) and GetDeviceTeamIdActual(id)%100==side then
            local p=GetDevicePosition(id)
            local lift=data.srw.Robots[id].GroundLift or 0
            points[#points+1]={Position=Vec3(p.x,p.y+lift,p.z or 0),Enemy=false}
        end
    end
    local anchors={}
    if DeviceExists(selected) then anchors[#anchors+1]=GetDevicePosition(selected) end
    for _,point in ipairs(points) do anchors[#anchors+1]=point.Position end
    local enemy=side==1 and 2 or 1
    for teamSide=1,2 do
        for i=0,GetDeviceCountSide(teamSide)-1 do
            local id=GetDeviceIdSide(teamSide,i)
            if DeviceExists(id) and (GetDeviceType(id)=="reactor"
                or (GetDeviceCanClaimStructures and GetDeviceCanClaimStructures(id))) then
                local p=GetDevicePosition(id); anchors[#anchors+1]=p
                if GetDeviceTeamIdActual(id)%100==enemy then points[#points+1]={Position=p,Enemy=true} end
            end
        end
    end
    local bounds=SRW.MapBounds(anchors)
    for i,point in ipairs(points) do
        local name="srw_map_dot"..i
        if i>pool then
            AddSpriteControl(parent,name,path.."/ui/textures/HUD/map_ally.png",ANCHOR_TOP_LEFT,Vec3(8,8,0),Vec3(0,0,-102),false)
            pool=i
        end
        local pos=SRW.MapPosition(point.Position,bounds)
        SetControlRelativePos(parent,name,Vec3(pos.x-4,pos.y-4,pos.z))
        SetControlSpriteByParent(parent,name,path.."/ui/textures/HUD/"..(point.Enemy and "map_enemy.png" or "map_ally.png"))
        ShowControl(parent,name,true)
    end
    for i=#points+1,pool do ShowControl(parent,"srw_map_dot"..i,false) end
end
