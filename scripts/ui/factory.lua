-- Local presentation; production commands only enter via SendScriptEvent.
local selectedFactory = nil
local page=1
local function Pages(f)
    local result={}; local seen={}
    for i,kind in ipairs(SRW.RobotKinds) do
        local n=SRW.RobotListPosition(i,3)
        if SRW.FactoryCanProduce(f,kind) and not seen[n] then
            result[#result+1]=n; seen[n]=true
        end
    end
    return result,seen
end
local controlPages={}
local controlKinds={}
local controls = {"srw_title", "srw_status", "srw_counts_label", "srw_counts", "srw_order", "srw_release", "srw_order_label", "srw_release_label"}
local texts = {}
for i=1,#SRW.RobotKinds do controls[#controls+1]="srw_price"..i end
for i=6,#SRW.RobotKinds do
    for _,suffix in ipairs({"order","release","order_label","release_label","counts"}) do
        controls[#controls+1]="srw_single"..i.."_"..suffix
    end
end
for _,name in ipairs({"srw_aa_order","srw_aa_release","srw_aa_order_label","srw_aa_release_label","srw_aa_counts","srw_page","srw_page_label"}) do controls[#controls+1]=name end
for _,name in ipairs({"srw_siege_order","srw_siege_release","srw_siege_order_label","srw_siege_release_label","srw_siege_counts"}) do controls[#controls+1]=name end
for _,name in ipairs({"srw_hound_order","srw_hound_release","srw_hound_order_label","srw_hound_release_label","srw_hound_counts"}) do controls[#controls+1]=name end
for _,name in ipairs({"srw_repair_order","srw_repair_release","srw_repair_order_label","srw_repair_release_label","srw_repair_counts"}) do controls[#controls+1]=name end
local function Text(name, value)
    if texts[name] ~= value then
        SetControlText("srw_factory_window", name, value)
        texts[name] = value
    end
end

function SRW.CreateUI()
    local language = Language() == "Russian" and "Russian" or "English"
    AddStrings(path .. "/mods/language-" .. language .. "/srw_ui.lua")
    texts = {}
    if SRW.CreateFactoryWindow then SRW.CreateFactoryWindow() end
    AddTextControl("srw_factory_window", "srw_title", "$SRW_UI.Title", ANCHOR_TOP_LEFT, Vec3(12,16,-101), false,"Readout")
    AddTextControl("srw_factory_window", "srw_status", "$SRW_UI.no_factory", ANCHOR_TOP_LEFT, Vec3(12,36,-101), false,"Readout")
    AddTextControl("srw_factory_window", "srw_counts_label", "$SRW_UI.Counts", ANCHOR_TOP_LEFT, Vec3(12,56,-101), false,"Readout")
    AddTextControl("srw_factory_window", "srw_counts", "", ANCHOR_TOP_LEFT, Vec3(280,56,-101), false,"Readout")
    local texture = path .. "/ui/textures/HUD/kega.png"
    local rows={
        {"srw_order","srw_release","Order","Release"},
        {"srw_hound_order","srw_hound_release","HoundOrder","HoundRelease"},
        {"srw_repair_order","srw_repair_release","RepairOrder","RepairRelease"},
        {"srw_siege_order","srw_siege_release","SiegeOrder","SiegeRelease"},
        {"srw_aa_order","srw_aa_release","AAOrder","AARelease"},
    }
    for i=6,#SRW.RobotKinds do
        rows[i]={"srw_single"..i.."_order","srw_single"..i.."_release","SingleType"..i,"SingleRelease"}
        local name="srw_single"..i.."_counts"
        AddTextControl("srw_factory_window",name,"",ANCHOR_TOP_LEFT,Vec3(480,89+select(2,SRW.RobotListPosition(i,3))*30,-101),false,"Readout")
        controlPages[name]=SRW.RobotListPosition(i,3);controlKinds[name]=SRW.RobotKinds[i]
    end
    for i,row in ipairs(rows) do
        local y=84+select(2,SRW.RobotListPosition(i,3))*30
        local price="srw_price"..i
        controlPages[price]=SRW.RobotListPosition(i,3);controlKinds[price]=SRW.RobotKinds[i]
        AddTextControl("srw_factory_window",price,"",ANCHOR_TOP_LEFT,Vec3(54,y+17,-101),false,"Readout")
        for _,name in ipairs({row[1],row[2],row[1].."_label",row[2].."_label"}) do
            controlPages[name]=SRW.RobotListPosition(i,3);controlKinds[name]=SRW.RobotKinds[i]
        end
        AddButtonControl("srw_factory_window",row[1],texture,ANCHOR_TOP_LEFT,Vec3(36,22,0),Vec3(12,y,-101),"Normal")
        AddTextControl("srw_factory_window",row[1].."_label","$SRW_UI."..row[3],ANCHOR_TOP_LEFT,Vec3(54,y+5,-101),false,"Readout")
        AddButtonControl("srw_factory_window",row[2],texture,ANCHOR_TOP_LEFT,Vec3(36,22,0),Vec3(240,y,-101),"Normal")
        AddTextControl("srw_factory_window",row[2].."_label","$SRW_UI."..row[4],ANCHOR_TOP_LEFT,Vec3(282,y+5,-101),false,"Readout")
    end
    AddTextControl("srw_factory_window","srw_hound_counts","",ANCHOR_TOP_LEFT,Vec3(480,119,-101),false,"Readout")
    AddTextControl("srw_factory_window","srw_repair_counts","",ANCHOR_TOP_LEFT,Vec3(480,149,-101),false,"Readout")
    AddTextControl("srw_factory_window","srw_siege_counts","",ANCHOR_TOP_LEFT,Vec3(480,89,-101),false,"Readout")
    AddTextControl("srw_factory_window","srw_aa_counts","",ANCHOR_TOP_LEFT,Vec3(480,119,-101),false,"Readout")
    controlPages.srw_hound_counts=1; controlPages.srw_repair_counts=1
    controlPages.srw_siege_counts=2; controlPages.srw_aa_counts=2
    controlKinds.srw_hound_counts="srw_hound";controlKinds.srw_repair_counts="srw_repair_bot"
    controlKinds.srw_siege_counts="srw_siege_bot";controlKinds.srw_aa_counts="srw_aa_bot"
    AddButtonControl("srw_factory_window","srw_page",texture,ANCHOR_TOP_LEFT,Vec3(36,22,0),Vec3(12,182,-101),"Normal")
    AddTextControl("srw_factory_window","srw_page_label","",ANCHOR_TOP_LEFT,Vec3(54,187,-101),false,"Readout")
    for _, name in ipairs(controls) do
        ShowControl("srw_factory_window", name, false)
    end
end

local function OwnedFactories()
    local ids = {}
    if not data.srw then return ids end
    for _, id in ipairs(SRW.SortedIds(data.srw.Factories)) do
        local f = data.srw.Factories[id]
        if DeviceExists(id) and f.Team == GetLocalTeamId()
            and GetDeviceTeamIdActual(id) == GetLocalTeamId() then ids[#ids+1] = id end
    end
    return ids
end

function SRW.RefreshUI()
    -- HUD can be rebuilt by the game after Load. Recreate our controls if needed.
    if not ControlExists("srw_factory_window", "srw_title") then SRW.CreateUI() end
    local ids = OwnedFactories()
    local selected = GetLocalSelectedDeviceId()
    selectedFactory = nil
    for _, id in ipairs(ids) do
        if id == selected then selectedFactory = id; break end
    end
    local f = selectedFactory and data.srw.Factories[selectedFactory]
    local pages,available
    if f then
        pages,available=Pages(f)
        if not available[page] then page=pages[1] end
    end
    if SRW.FactoryWindowVisible and not SRW.FactoryWindowVisible(selectedFactory) then f=nil end
    local localTeam = GetLocalTeamId()
    if SRW.RefreshSquadUI then SRW.RefreshSquadUI(f,selectedFactory) end
    for _, name in ipairs(controls) do
        local main=name=="srw_title" or name=="srw_status"
        ShowControl("srw_factory_window", name, localTeam > 0 and f ~= nil and (main or not SRW.SquadEditorOpen)
            and (not controlKinds[name] or SRW.FactoryCanProduce(f,controlKinds[name]))
            and (not controlPages[name] or controlPages[name]==page)
            and (not name:match("^srw_price(%d+)$") or (SRW.Config.Robots[SRW.RobotKinds[tonumber(name:match("^srw_price(%d+)$"))]].Tier or 1)<=(f.Tier or 1))
            and (not name:match("^srw_aa_") or (f.Tier or 1)>=2)
            and (not name:match("^srw_single(%d+)_") or (SRW.Config.Robots[SRW.RobotKinds[tonumber(name:match("^srw_single(%d+)_"))]].Tier or 1)<=(f.Tier or 1)))
    end
    if not f then Text("srw_status", "$SRW_UI.no_factory"); return end
    for i,kind in ipairs(SRW.RobotKinds) do
        local m,e=SRW.RobotCost(SRW.Config.Robots[kind],false)
        Text("srw_price"..i,string.format("%d M / %d E",m,e))
    end
    Text("srw_title",f.Domain=="air" and "$SRW_UI.AirFactoryTier"..(f.Tier or 1) or "$SRW_UI.FactoryTier"..(f.Tier or 1))
    Text("srw_status", "$SRW_UI." .. (f.Status or "ready"))
    local pageIndex=1
    for i,n in ipairs(pages) do if n==page then pageIndex=i end end
    Text("srw_page_label", tostring(pageIndex).." / "..#pages.."   >")
    Text("srw_counts", string.format("%d/%d | %d | %.1f", SRW.FactoryReserve(f), SRW.FactoryCapacity(f), SRW.FactoryQueue(f), f.Remaining))
    for i=6,#SRW.RobotKinds do
        local kind=SRW.RobotKinds[i]; local cfg=SRW.Config.Robots[kind]
        Text("srw_single"..i.."_counts",string.format("%d | %d | %d/%d",f[kind.."Reserve"] or 0,f[kind.."Queue"] or 0,SRW.ActiveCount(f.Team,kind),cfg.ActiveLimit))
    end
    Text("srw_hound_counts", string.format("Hound: %d | %d | %d/10", f.HoundReserve or 0, f.HoundQueue or 0, SRW.ActiveCount(f.Team,"srw_hound")))
    Text("srw_repair_counts", string.format("%d | %d | %d/5", f.RepairReserve or 0, f.RepairQueue or 0, SRW.ActiveCount(f.Team,"srw_repair_bot")))
    Text("srw_siege_counts", string.format("%d | %d | %d/5", f.SiegeReserve or 0, f.SiegeQueue or 0, SRW.ActiveCount(f.Team,"srw_siege_bot")))
    Text("srw_aa_counts", string.format("%d | %d | %d/5", f.AAReserve or 0, f.AAQueue or 0, SRW.ActiveCount(f.Team,"srw_aa_bot")))
end

function SRW.ClickUI(name)
    if not selectedFactory or GetLocalSelectedDeviceId() ~= selectedFactory then return end
    if name=="srw_window_close" and SRW.CloseFactoryWindow then SRW.CloseFactoryWindow(selectedFactory); SRW.RefreshUI(); return end
    if SRW.FactoryWindowVisible and not SRW.FactoryWindowVisible(selectedFactory) then return end
    if SRW.ClickSquadUI and SRW.ClickSquadUI(name,selectedFactory) then return end
    if SRW.SquadEditorOpen then return end
    if name=="srw_page" then
        local pages=Pages(data.srw.Factories[selectedFactory])
        for i,n in ipairs(pages) do if n==page then page=pages[i%#pages+1]; break end end
        SRW.RefreshUI(); return
    end
    if controlPages[name] and controlPages[name]~=page then return end
    local f=data.srw.Factories[selectedFactory]
    if controlKinds[name] and not SRW.FactoryCanProduce(f,controlKinds[name]) then return end
    local index,action=name:match("^srw_single(%d+)_(%a+)$")
    if index and (action=="order" or action=="release") then
        index=tonumber(index)
        local kind=SRW.RobotKinds[index]; local f=data.srw.Factories[selectedFactory]
        if not kind or not SRW.FactoryCanProduce(f,kind) then return end
        SendScriptEvent(action=="order" and "SRW_OrderIndividual" or "SRW_ReleaseIndividual",
            GetLocalTeamId()..","..selectedFactory..","..index,"",true)
        return
    end
    local handler = name == "srw_order" and "SRW_Order" or name == "srw_release" and "SRW_Release"
        or name=="srw_hound_order" and "SRW_OrderHound" or name=="srw_hound_release" and "SRW_ReleaseHound"
        or name=="srw_repair_order" and "SRW_OrderRepair" or name=="srw_repair_release" and "SRW_ReleaseRepair"
        or name=="srw_siege_order" and "SRW_OrderSiege" or name=="srw_siege_release" and "SRW_ReleaseSiege"
        or name=="srw_aa_order" and "SRW_OrderAA" or name=="srw_aa_release" and "SRW_ReleaseAA"
    if handler then
        SendScriptEvent(handler, tostring(GetLocalTeamId()) .. "," .. tostring(selectedFactory), "", true)
    end
end
