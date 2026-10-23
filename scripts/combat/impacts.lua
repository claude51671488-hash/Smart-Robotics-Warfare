-- Visual radius only: native projectile splash remains the sole damage source.
local shells={srw_parcel_bomb=true,srw_hammer_shell=true,srw_bastion_shell=true,srw_cathedral_shell=true,
    srw_heavy_siege_he=true,srw_mlrs_rocket=true}
function SRW.TerrainBlastVisual(node,team,name,cause)
    if cause~=DESTROYTYPE_HITTERRAIN or not shells[name] then return end
    local radius=GetProjectileParamFloat(name,team,"ProjectileSplashDamageMaxRadius",0)
    if radius<=0 then return end
    local p=NodePosition(node)
    SpawnCircle(Vec3(p.x,p.y,-110),radius,{r=255,g=175,b=70,a=160},0.35)
end
