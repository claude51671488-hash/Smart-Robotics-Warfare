-- A distinct supporting beam. Reuse native bracing artwork until final art.
local found=false
for _,m in ipairs(Materials) do if m.SaveName=="srw_air_platform" then found=true end end
if not found then
    for _,source in ipairs(Materials) do
        if source.SaveName=="bracing" then
            local function copy(v)
                if type(v)~="table" then return v end
                local r={};for k,x in pairs(v) do r[k]=copy(x) end;return r
            end
            local platform=copy(source)
            platform.SaveName="srw_air_platform"
            platform.HitPoints=400
            platform.SupportsDevices=true
            platform.RecessionTargetSaveName=nil
            platform.Conversions={}
            platform.MetalBuildCost=.6
            platform.EnergyBuildCost=2
            -- Icons are registered here too: materials can load before devices.
            local states={}
            for _,s in ipairs({"Normal","Rollover","Pressed","Disabled"}) do
                states[s]={Frames={{texture=path.."/ui/textures/HUD/kega.png"}}}
            end
            table.insert(Sprites,{Name="srw-air-platform-icon",States=states})
            platform.Icon="srw-air-platform-icon";platform.Detail="srw-air-platform-icon"
            table.insert(Materials,platform)
            break
        end
    end
end
