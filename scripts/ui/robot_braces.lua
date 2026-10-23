-- Temporary outrigger drawing. Short-lived lines never enter simulation/save data.
local elapsed=0
function SRW.RefreshRobotBraces(delta)
    if not data.srw or not SpawnLine then return end
    elapsed=elapsed+(delta or 0.016)
    if elapsed<0.04 then return end
    elapsed=0
    for _,id in ipairs(SRW.SortedIds(data.srw.Robots)) do
        local bot=data.srw.Robots[id]
        if bot.BraceActive and DeviceExists(id) and not DeviceDisabled(id)
            and not (IsCloaked and IsCloaked(id))
            and GetDeviceTeamIdActual(id)==bot.Team then
            local cfg=SRW.Config.Robots[bot.Kind]
            local p=SRW.RobotGroundPosition(id,bot)
            local ratio=math.min(1,(bot.BraceProgress or 0)/(cfg.BraceSeconds or 1))
            local color=bot.Braced and {r=120,g=200,b=235,a=255} or {r=210,g=180,b=110,a=220}
            for _,side in ipairs({-1,1}) do
                local foot=Vec3(p.x+side*(40+140*ratio),p.y,-110)
                SpawnLine(Vec3(p.x+side*40,p.y-70,-110),foot,color,0.045)
                SpawnLine(Vec3(foot.x-22,foot.y,-110),Vec3(foot.x+22,foot.y,-110),color,0.045)
            end
        end
    end
end
