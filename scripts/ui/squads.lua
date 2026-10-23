-- Presentation only: all edits and commands go through synchronized events.
SRW.SquadEditorOpen=false
SRW.SquadPage=1
local names={}; local cache={}
local function text(name,value)
    if cache[name]~=value then SetControlText("srw_factory_window",name,value); cache[name]=value end
end
local function label(name,value,x,y)
    AddTextControl("srw_factory_window",name,value,ANCHOR_TOP_LEFT,Vec3(x,y,-101),false,"Readout")
    names[#names+1]=name
end
local function button(name,value,x,y)
    AddButtonControl("srw_factory_window",name,path.."/ui/textures/HUD/kega.png",ANCHOR_TOP_LEFT,Vec3(36,22,0),Vec3(x,y,-101),"Normal")
    names[#names+1]=name
    label(name.."_label",value,x+42,y+5)
end
function SRW.CreateSquadUI()
    names={}; cache={}
    button("srw_squad_mode","$SRW_UI.SquadMode",430,10)
    for i=1,#SRW.RobotKinds do
        local y=66+select(2,SRW.RobotListPosition(i,5))*28
        button("srw_squad_add"..i,"$SRW_UI.SquadType"..i,12,y)
        button("srw_squad_remove"..i,"-",250,y)
        label("srw_squad_count"..i,"",310,y+5)
        label("srw_squad_price"..i,"",54,y+17)
    end
    for i,action in ipairs({"Save","Load","Start","Clear","Release"}) do
        button("srw_squad_"..action,"$SRW_UI.Squad"..action,430,66+(i-1)*28)
    end
    button("srw_squad_page","",430,214)
    label("srw_squad_legend","",12,256)
    label("srw_squad_progress","",12,274)
    for _,name in ipairs(names) do ShowControl("srw_factory_window",name,false) end
end
function SRW.RefreshSquadUI(f,id)
    if not ControlExists("srw_factory_window","srw_squad_mode") then SRW.CreateSquadUI() end
    local visible=f~=nil and GetLocalTeamId()>0
    for _,name in ipairs(names) do
        local mode=name=="srw_squad_mode" or name=="srw_squad_mode_label"
        local row=tonumber(name:match("^srw_squad_add(%d+)") or name:match("^srw_squad_remove(%d+)") or name:match("^srw_squad_count(%d+)$") or name:match("^srw_squad_price(%d+)$"))
        local onPage=not row or SRW.RobotListPosition(row,5)==SRW.SquadPage
        local unlocked=not row or not f or SRW.FactoryCanProduce(f,SRW.RobotKinds[row])
        ShowControl("srw_factory_window",name,visible and (mode or SRW.SquadEditorOpen) and onPage and unlocked)
    end
    if not visible then return end
    local pageCount=1;local pageAllowed={}
    for i,kind in ipairs(SRW.RobotKinds) do
        if SRW.FactoryCanProduce(f,kind) then
            local n=SRW.RobotListPosition(i,5);pageCount=math.max(pageCount,n);pageAllowed[n]=true
        end
    end
    if not pageAllowed[SRW.SquadPage] then SRW.SquadPage=1;SRW.RefreshUI();return end
    SRW.SquadPageCount=pageCount
    text("srw_squad_page_label",SRW.SquadPage.." / "..pageCount.." >")
    text("srw_squad_mode_label",SRW.SquadEditorOpen and "$SRW_UI.SquadBack" or "$SRW_UI.SquadMode")
    local counts={}; local work,metal,energy,speed=0,0,0,0
    for _,kind in ipairs(f.SquadDraft or {}) do
        counts[kind]=(counts[kind] or 0)+1
        local c=SRW.Config.Robots[kind]
        local m,e=SRW.RobotCost(c,true)
        work=work+c.ProductionSeconds; metal=metal+m; energy=energy+e; speed=speed+c.SpeedMinesPerSecond
    end
    for i,kind in ipairs(SRW.RobotKinds) do
        text("srw_squad_count"..i,tostring(counts[kind] or 0))
        local m,e=SRW.RobotCost(SRW.Config.Robots[kind],true)
        text("srw_squad_price"..i,string.format("%d M / %d E",m,e))
    end
    local s=f.Squad
    if s then
        local remaining,progress=SRW.SquadEstimate(f)
        text("srw_squad_legend","$SRW_UI.SquadProgressHeader")
        local value=string.format("%d/%d | %d%% | ~%.1f | %d | %.1f | %.2f",
            s.Produced,#s.Items,math.floor(progress*100),remaining,s.Released,f.ExitRemaining or 0,s.Speed or 0)
        text("srw_squad_progress",value)
    else
        text("srw_squad_legend","$SRW_UI.SquadDraftHeader")
        text("srw_squad_progress",string.format("%d | %d / %d | ~%d | %.2f",#(f.SquadDraft or {}),metal,energy,work,speed/math.max(1,#(f.SquadDraft or {}))))
    end
end
function SRW.ClickSquadUI(name,id)
    if name=="srw_squad_mode" then SRW.SquadEditorOpen=not SRW.SquadEditorOpen; SRW.RefreshUI(); return true end
    if not SRW.SquadEditorOpen then return false end
    if name=="srw_squad_page" then
        SRW.SquadPage=SRW.SquadPage%(SRW.SquadPageCount or 1)+1
        SRW.RefreshUI(); return true
    end
    local index=name:match("^srw_squad_add(%d+)$")
    local delta=1
    if not index then index=name:match("^srw_squad_remove(%d+)$"); delta=-1 end
    local args=GetLocalTeamId()..","..id
    if index then
        if SRW.RobotListPosition(tonumber(index),5)~=SRW.SquadPage then return true end
        local f=data.srw.Factories[id]
        local kind=SRW.RobotKinds[tonumber(index)]
        if not f or not kind or not SRW.FactoryCanProduce(f,kind) then return true end
        SendScriptEvent("SRW_SquadEdit",args..","..index..","..delta,"",true)
        return true
    end
    for _,action in ipairs({"Save","Load","Start","Clear","Release"}) do
        if name=="srw_squad_"..action then SendScriptEvent("SRW_Squad"..action,args,"",true); return true end
    end
    return false
end
