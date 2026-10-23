from pathlib import Path
import re
r=Path(__file__).resolve().parents[1]
p=r/'scripts/factories/production.lua'; s=p.read_text()
roster=re.search(r'SRW.RobotKinds=([^\n]+)',(r/'scripts/factories/squads.lua').read_text()).group(0)
s=roster+'\n'+'''function SRW.ExtraCount(f,suffix)
    local count=0
    for i=6,#SRW.RobotKinds do count=count+(f[SRW.RobotKinds[i]..suffix] or 0) end
    return count
end
function SRW_OrderIndividual(team,id,index)
    team,id,index=tonumber(team),tonumber(id),tonumber(index)
    local f=SRW.ValidFactory(team,id); local kind=index and SRW.RobotKinds[index]
    if not f or not kind or index<6 then return end
    if (SRW.Config.Robots[kind].Tier or 1)>(f.Tier or 1) then f.Status="tier_required"; return end
    if SRW.SquadBusy and SRW.SquadBusy(f) then f.Status="squad_busy"; return end
    if SRW.FactoryQueue(f)>=SRW.Config.Prototype.QueueLimit then f.Status="queue_full"; return end
    f[kind.."Queue"]=(f[kind.."Queue"] or 0)+1; f.Status="queued"
end
function SRW_ReleaseIndividual(team,id,index)
    team,id,index=tonumber(team),tonumber(id),tonumber(index)
    local f=SRW.ValidFactory(team,id); local kind=index and SRW.RobotKinds[index]
    if not f or not kind or index<6 then return end
    if (f[kind.."Reserve"] or 0)<1 then f.Status="empty"; return end
    if SRW.ActiveCount(team,kind)>=SRW.Config.Robots[kind].ActiveLimit then f.Status="limit"; return end
    if not SRW.CanExit(f) then return end
    local ok
    if kind=="srw_tank_bot" or kind=="srw_colossus_bot" then ok=SRW.SpawnTank(team,id,kind)
    elseif kind=="srw_shield_bot" then ok=SRW.SpawnShieldBot(team,id)
    else ok=SRW.SpawnHound(team,id,kind) end
    if ok then f[kind.."Reserve"]=f[kind.."Reserve"]-1; SRW.MarkExit(f,kind)
    else f.Status="exit_blocked" end
end
''' +s
s=s.replace('return f.Queue+(f.HoundQueue','return SRW.ExtraCount(f,"Queue")+f.Queue+(f.HoundQueue')
s=s.replace('return f.Reserve+(f.HoundReserve','return SRW.ExtraCount(f,"Reserve")+f.Reserve+(f.HoundReserve')
s=s.replace('else f.Reserve = f.Reserve + 1 end','elseif f.CurrentType and f.CurrentType~="srw_dynamit_bot" then\n                    local field=f.CurrentType.."Reserve"; f[field]=(f[field] or 0)+1\n                else f.Reserve = f.Reserve + 1 end')
s=s.replace('local previous=1','for i=6,#SRW.RobotKinds do kinds[i]=SRW.RobotKinds[i]; fields[i]=kinds[i].."Queue" end\n                local previous=1')
p.write_text(s)
p=r/'scripts/factories/squads.lua'; s=p.read_text(); s=s.replace('    return remaining,progress','    if s.Produced<#s.Items and not f.CurrentSquad then\n        for i=6,#SRW.RobotKinds do\n            local kind=SRW.RobotKinds[i]\n            remaining=remaining+(f[kind.."Queue"] or 0)*SRW.Config.Robots[kind].ProductionSeconds\n        end\n    end\n    return remaining,progress'); p.write_text(s)
p=r/'scripts/ui/factory.lua'; s=p.read_text()
s=s.replace('local texts = {}','''local texts = {}
for i=6,#SRW.RobotKinds do
    for _,suffix in ipairs({"order","release","order_label","release_label","counts"}) do
        controls[#controls+1]="srw_single"..i.."_"..suffix
    end
end''')
s=s.replace('    for i,row in ipairs(rows) do','''    for i=6,#SRW.RobotKinds do
        rows[i]={"srw_single"..i.."_order","srw_single"..i.."_release","SingleType"..i,"SingleRelease"}
        local name="srw_single"..i.."_counts"
        AddTextControl("",name,"",ANCHOR_TOP_LEFT,Vec3(480,239+((i-1)%3)*30,-101),false,"Readout")
        controlPages[name]=math.floor((i-1)/3)+1
    end
    for i,row in ipairs(rows) do''')
s=s.replace('and (not name:match("^srw_aa_") or (f.Tier or 1)>=2))','''and (not name:match("^srw_aa_") or (f.Tier or 1)>=2)
            and (not name:match("^srw_single(%d+)_") or (SRW.Config.Robots[SRW.RobotKinds[tonumber(name:match("^srw_single(%d+)_"))]].Tier or 1)<=(f.Tier or 1)))''')
s=s.replace('tostring(page).." / 2   >"','tostring(page).." / "..math.ceil(#SRW.RobotKinds/3).."   >"')
s=s.replace('    Text("srw_hound_counts",','''    for i=6,#SRW.RobotKinds do
        local kind=SRW.RobotKinds[i]; local cfg=SRW.Config.Robots[kind]
        Text("srw_single"..i.."_counts",string.format("%d | %d | %d/%d",f[kind.."Reserve"] or 0,f[kind.."Queue"] or 0,SRW.ActiveCount(f.Team,kind),cfg.ActiveLimit))
    end
    Text("srw_hound_counts",''')
s=s.replace('page=3-page','page=page%math.ceil(#SRW.RobotKinds/3)+1')
s=s.replace('    local handler =','''    local index,action=name:match("^srw_single(%d+)_(%a+)$")
    if index and (action=="order" or action=="release") then
        index=tonumber(index)
        local kind=SRW.RobotKinds[index]; local f=data.srw.Factories[selectedFactory]
        if not kind or (SRW.Config.Robots[kind].Tier or 1)>(f.Tier or 1) then return end
        SendScriptEvent(action=="order" and "SRW_OrderIndividual" or "SRW_ReleaseIndividual",
            GetLocalTeamId()..","..selectedFactory..","..index,"",true)
        return
    end
    local handler =''')
p.write_text(s)
for lang in ['Russian','English']:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 ru=lang=='Russian'
 for i in range(6,16):
  name=re.search(r'SRW_UI.SquadType'+str(i)+r' = L"\+ (.*?)"',s).group(1)
  s+=f'\nSRW_UI.SingleType{i} = L"{name}"\n'
 s+='\nSRW_UI.SingleRelease = L"'+('Выпустить 1' if ru else 'Release 1')+'"\n'
 s=re.sub(r'SRW_UI.SquadMode = L".*?"','SRW_UI.SquadMode = L"'+('Редактор отряда' if ru else 'Squad editor')+'"',s)
 s=re.sub(r'SRW_UI.SquadBack = L".*?"','SRW_UI.SquadBack = L"'+('Одиночные заказы' if ru else 'Individual orders')+'"',s)
 for i in range(1,4):
  s=re.sub(r'SRW_UI.FactoryTier'+str(i)+r' = L".*?"',f'SRW_UI.FactoryTier{i} = L"'+(f'Фабрика: уровень {i}' if ru else f'Factory: level {i}')+'"',s)
 p.write_text(s,encoding='utf-16')
p=r/'script.lua'; p.write_text(p.read_text().replace('0.22.0-colossus-formation','0.23.0-individual-production'))
