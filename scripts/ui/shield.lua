-- Local input/preview only. Commands are revalidated in the simulation.
local selected,placing,points,message
local elapsed=0
local textCache={}
local function text(name,value)
    if textCache[name]~=value then SetControlText("",name,value); textCache[name]=value end
end
local names={"srw_shield_title","srw_shield_status","srw_shield_on","srw_shield_off","srw_shield_on_label","srw_shield_off_label","srw_shield_hull","srw_shield_hull_label"}
local function stopPlacement()
    if placing then EnableGrid(false) end
    placing=nil; points=nil
end
function SRW.CreateShieldUI()
    textCache={}
    local language=Language()=="Russian" and "Russian" or "English"
    AddStrings(path.."/mods/language-"..language.."/shield_ui.lua")
    AddTextControl("",names[1],"$SRW_SHIELD.Title",ANCHOR_TOP_LEFT,Vec3(12,166,-101),false,"Readout")
    AddTextControl("",names[2],"",ANCHOR_TOP_LEFT,Vec3(12,190,-101),false,"Readout")
    for i,action in ipairs({"on","off","hull"}) do
        local y=220+(i-1)*30
        AddButtonControl("","srw_shield_"..action,path.."/ui/textures/HUD/kega.png",ANCHOR_TOP_LEFT,Vec3(36,22,0),Vec3(12,y,-101),"Normal")
        AddTextControl("","srw_shield_"..action.."_label","$SRW_SHIELD."..(action=="off" and "deactivate" or action),ANCHOR_TOP_LEFT,Vec3(54,y+5,-101),false,"Readout")
    end
    for _,name in ipairs(names) do ShowControl("",name,false) end
end
function SRW.ClickShieldUI(name)
    if name=="srw_shield_on" and selected then
        local s=data.srw.Shields[selected]
        if not s or s.Active then return end
        placing=selected; points={}; message=nil; EnableGrid(true)
    elseif name=="srw_shield_hull" and selected then
        stopPlacement(); message=nil
        SendScriptEvent("SRW_ShieldHull",GetLocalTeamId()..","..selected,"",true)
    elseif name=="srw_shield_off" and selected then
        stopPlacement(); message=nil
        SendScriptEvent("SRW_ShieldDeactivate",GetLocalTeamId()..","..selected,"",true)
    end
end
local function cursorPoint()
    local p=ScreenToWorld(GetMousePos()); local origin=GetDeviceCentrePosition(placing)
    local grid=SRW.Shield.BatteryWidth/4
    return {x=math.floor((p.x-origin.x)/grid+0.5)*grid,y=math.floor((p.y-origin.y)/grid+0.5)*grid}
end
function SRW.ShieldKey(key,down)
    if not placing then return false end
    if key=="escape" or key=="mouse right" then if down then stopPlacement() end; return true end
    if key~="mouse left" then return false end
    local mouse=GetMousePos()
    if mouse.x<700 and mouse.y>=180 and mouse.y<=350 then return false end
    if down then
        if not DeviceExists(placing) then stopPlacement(); return true end
        local p=cursorPoint()
        if p.x^2+p.y^2>(data.srw.Shields[placing].Radius or SRW.Shield.Radius)^2 then message="radius"; return true end
        if #points<2 then points[#points+1]=p; message=nil
        else
            local arc,err=SRW.ShieldArc(points[1],points[2],p,data.srw.Shields[placing].Radius)
            if not arc then message=err; return true end
            local args={GetLocalTeamId(),placing,points[1].x,points[1].y,points[2].x,points[2].y,p.x,p.y}
            SendScriptEvent("SRW_ShieldActivate",table.concat(args,","),"",true)
            stopPlacement(); message=nil
        end
    end
    return true
end
local function line(a,b,color)
    SpawnLine(Vec3(a.x,a.y,-110),Vec3(b.x,b.y,-110),color,0.035)
end
local function drawArc(arc,origin,color,step)
    -- Visual detail is independent of the 64-segment collision curve.
    for i=1,#arc-1,step or 4 do
        local j=math.min(i+(step or 4),#arc)
        line({x=arc[i].x+origin.x,y=arc[i].y+origin.y},
            {x=arc[j].x+origin.x,y=arc[j].y+origin.y},color)
    end
end
function SRW.RefreshShieldUI(delta)
    if not data.srw then return end
    if not ControlExists("","srw_shield_title") then SRW.CreateShieldUI() end
    if placing and (not DeviceExists(placing) or GetDeviceTeamIdActual(placing)~=GetLocalTeamId()) then stopPlacement() end
    local id=placing or GetLocalSelectedDeviceId()
    local s=data.srw.Shields[id]
    selected=s and not s.Mobile and s.Team==GetLocalTeamId() and id or nil
    for _,name in ipairs(names) do ShowControl("",name,selected~=nil) end
    if selected then
        text("srw_shield_title",string.format("SRW | %d / %d HP",math.floor(s.HP),s.MaxHP or SRW.Shield.MaxHP))
        local status=placing and (message or "point"..(#points+1)) or s.Status
        text("srw_shield_status","$SRW_SHIELD."..status)
    end
    elapsed=elapsed+(delta or 0.016)
    if elapsed<0.033 then return end
    elapsed=0
    local shields=SRW.CombatShields and SRW.CombatShields() or data.srw.Shields
    for _,sid in ipairs(SRW.SortedIds(shields)) do
        local shield=shields[sid]
        if shield.Origin or DeviceExists(sid) then
            local p=SRW.ShieldOrigin(sid,shield); local ratio=shield.HP/(shield.MaxHP or SRW.Shield.MaxHP)
            if shield.Active and shield.Arc then
                drawArc(shield.Arc,p,{r=60,g=220,b=255,a=math.floor(100+155*ratio)},shield.AutoHull and 1 or 4)
                -- A single short-lived contour avoids doubled moving arcs.
            end
            if sid==selected or shield.Mobile then
                -- Two local bars under the selected generator: body, then shared arc HP.
                for row,value in ipairs({shield.Members and ratio or GetDeviceHealth(sid),ratio}) do
                    local y=p.y+50+row*8
                    line({x=p.x-40,y=y},{x=p.x+40,y=y},{r=60,g=60,b=60,a=255})
                    line({x=p.x-40,y=y},{x=p.x-40+80*value,y=y},{r=60,g=200,b=row==1 and 70 or 255,a=255})
                end
            end
        end
    end
    if placing then
        local p=GetDeviceCentrePosition(placing)
        SpawnCircle(Vec3(p.x,p.y,-110),data.srw.Shields[placing].Radius or SRW.Shield.Radius,{r=80,g=150,b=220,a=130},0.12)
        for _,q in ipairs(points) do SpawnCircle(Vec3(p.x+q.x,p.y+q.y,-110),5,{r=255,g=255,b=255,a=255},0.12) end
        if #points==2 then
            local arc=SRW.ShieldArc(points[1],points[2],cursorPoint(),data.srw.Shields[placing].Radius)
            if arc then drawArc(arc,p,{r=60,g=255,b=130,a=255})
            else line({x=p.x+points[1].x,y=p.y+points[1].y},{x=p.x+points[2].x,y=p.y+points[2].y},{r=255,g=60,b=60,a=255}) end
        end
    end
end
function SRW.CleanupShieldUI() stopPlacement() end
