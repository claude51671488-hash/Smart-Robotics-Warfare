-- The walking phase follows distance, so squad speed changes cannot make the
-- feet cycle at an unrelated speed. These fields are simulation data only.
function SRW.RefreshDynamitAnimation(id,bot)
    if not DeviceExists(id) then return end
    local p=GetDevicePosition(id)
    local distance=bot.AnimationX and math.abs(p.x-bot.AnimationX) or 0
    local moving=distance>.01
    local state=bot.FuseRemaining~=nil and "Armed"
        or (not DeviceDisabled(id) and moving and "Run" or "Idle")
    local stride=SRW.Config.Robots.srw_dynamit_bot.AnimationStride or 70
    if moving and not DeviceDisabled(id) and bot.FuseRemaining==nil then
        bot.AnimationTravel=((bot.AnimationTravel or 0)+distance)%stride
    end
    bot.AnimationDistance=moving and distance or 0
    bot.AnimationStep=(bot.AnimationStep or 0)+1
    state=state..(bot.Direction<0 and "Left" or "Right")
    local frames=SRW.Config.Robots.srw_dynamit_bot.AnimationFrames or 48
    if state:sub(1,3)=="Run" then state=state..(1+math.floor((bot.AnimationTravel or 0)*frames/stride)) end
    bot.AnimationX=p.x
    bot.AnimationState=state
end

-- Sprite changes belong to the client rendering callback, not the simulation
-- world. Keeping this cache local also prevents visual state from entering saves.
local shown={}
function SRW.RefreshDynamitVisuals(delta)
    if not data.srw then return end
    for id,bot in pairs(data.srw.Robots) do
        if (not bot.Kind or bot.Kind=="srw_dynamit_bot") and bot.AnimationState and DeviceExists(id) then
            local cache=shown[id] or {}
            local state=bot.AnimationState
            if state:sub(1,3)=="Run" then
                local cfg=SRW.Config.Robots.srw_dynamit_bot
                local stride=cfg.AnimationStride or 70
                if cache.Step~=bot.AnimationStep or cache.Travel==nil then
                    cache.Step=bot.AnimationStep
                    cache.Travel=(bot.AnimationTravel or 0)-(bot.AnimationDistance or 0)
                    cache.Distance=bot.AnimationDistance or 0
                    cache.Elapsed=0
                end
                -- Interpolate the last simulation step on the rendering clock.
                -- At most one tick of delay; never extrapolate feet after a stop.
                cache.Elapsed=math.min(.04,(cache.Elapsed or 0)+math.max(0,delta or .04))
                local travel=(cache.Travel+cache.Distance*cache.Elapsed/.04)%stride
                state="Run"..(bot.Direction<0 and "Left" or "Right")
                    ..(1+math.floor(travel*(cfg.AnimationFrames or 48)/stride))
            else
                cache.Step=nil
            end
            if cache.State~=state then
                SetDeviceSpriteState(id,state)
                cache.State=state
            end
            shown[id]=cache
        end
    end
    for id in pairs(shown) do
        local bot=data.srw.Robots[id]
        if not bot or not DeviceExists(id) then shown[id]=nil end
    end
end
