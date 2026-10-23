-- Append srw_ projectiles to the existing Projectiles table here.
-- The scaffold does not modify vanilla projectile damage.
local function copy(value)
    if type(value)~="table" then return value end
    local result={}; for k,v in pairs(value) do result[k]=copy(v) end; return result
end
local base
local existingHound=false
for _,projectile in ipairs(Projectiles) do
    if projectile.SaveName=="srw_hound_shell" then existingHound=true end
    if projectile.SaveName=="cannon" then base=projectile end
end
if base and not existingHound then
    local shell=copy(base)
    shell.SaveName="srw_hound_shell"
    -- Temporary vanilla cannon damage; retain the tested contact fuse.
    shell.ProjectileDamage=700
    shell.ProjectileSplashDamage=30
    shell.ProjectileSplashDamageMaxRadius=200
    -- Forts uses Gravity, not ProjectileGravity.
    shell.Gravity=0
    shell.ProjectileGravity=nil
    shell.ExplodeOnTouch=true
    shell.DestroyShields=false
    shell.ProjectileSplashMaxForce=0
    shell.MomentumThreshold={}
    shell.DamageMultiplier={}
    table.insert(Projectiles,shell)
end

local function clone(baseName, name, overrides)
    local source
    for _, projectile in ipairs(Projectiles) do
        if projectile.SaveName==name then return end
        if projectile.SaveName==baseName then source=projectile end
    end
    if not source then return end
    local shell=copy(source)
    shell.SaveName=name
    for k,v in pairs(overrides) do shell[k]=v end
    table.insert(Projectiles,shell)
end
-- Native contact explosions; layered blast is a later prototype.
clone("cannon", "srw_hammer_shell", {
    ProjectileDamage=850, ProjectileSplashDamage=100, ProjectileSplashDamageMaxRadius=180,
    Gravity=981, ProjectileDrag=0, MaxAge=30, ExplodeOnTouch=true, DestroyShields=false,
    ProjectileSplashMaxForce=0, MomentumThreshold={}, DamageMultiplier={},
})
clone("machinegun", "srw_aa_bullet", {
    ProjectileDamage=12, AntiAirDamage=40, Gravity=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})
clone("mortar2", "srw_kolokol_he", {
    ProjectileDamage=135, ProjectileSplashDamage=270,
    ProjectileSplashDamageMaxRadius=180, DisableShields=false,
})
-- Preserve native incendiary effects and background ignition.
clone("mortar", "srw_kolokol_incendiary", {
    ProjectileDamage=30, ProjectileSplashDamage=105,
    ProjectileSplashDamageMaxRadius=150,
})

-- Script applies tier-specific EMP at confirmed contact. No native area EMP:
-- that would fully disable tier-II robots before their partial debuff applies.
clone("cannon", "srw_emp_shell", {
    ProjectileDamage=1, ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
    Gravity=0, ExplodeOnTouch=true, DestroyShields=false,
    ProjectileSplashMaxForce=0, MomentumThreshold={}, DamageMultiplier={},
    EMPRadius=0, EMPDuration=0, SRWShieldDamage=500,
})

-- Native missile steering, with target updates owned by SRW.
-- No dependency on the optional weapon_pack mod and no spotter required.
clone("missile", "srw_salvo_rocket", {
    ProjectileType="missile", Gravity=0, ProjectileDrag=0,
    LCIgnoreMissileGuidance=true, sm_is_config=false,
    ProjectileDamage=80, ProjectileSplashDamage=120, ProjectileSplashDamageMaxRadius=180,
    ProjectileSplashMaxForce=15000, ProjectileIncendiary=false,
    IgnitesBackgroundMaterials=false, IgnitesBackgroundMaterialsPassing=false,
    ExplodeOnTouch=true, MaxAge=4, EMPSensitivity=0, DamageMultiplier={},
})

clone("machinegun", "srw_hunter_bullet", {
    ProjectileDamage=65, WeaponDamageBonus=0, Gravity=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
    DamageMultiplier={},
})

clone("machinegun", "srw_heavy_aa_bullet", {
    ProjectileDamage=20, AntiAirDamage=100, Gravity=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})

clone("mortar2", "srw_heavy_siege_he", {
    ProjectileDamage=200, ProjectileSplashDamage=650,
    ProjectileSplashDamageMaxRadius=300, DisableShields=false,
    Gravity=981, ProjectileDrag=0, MaxAge=30,
})

clone("srw_salvo_rocket", "srw_tank_aa_rocket", {
    ProjectileDamage=30, AntiAirDamage=130,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})
for _,p in ipairs(Projectiles) do
    if p.SaveName=="srw_salvo_rocket" or p.SaveName=="srw_tank_aa_rocket" then
        p.Missile=p.Missile or {}
        p.Missile.MaxSteerPerSecond=p.SaveName=="srw_tank_aa_rocket" and 200 or 120
        p.Missile.MaxSteerPerSecondErratic=0
        p.Missile.ErraticAngleExtentStdDev=0
        p.Missile.ErraticAngleExtentMax=0
        p.Missile.ErraticThrust=0
        p.Missile.LaunchThrust=0
        p.Missile.RocketThrust=0
        p.Missile.RocketThrustChange=0
        p.Missile.CruiseTargetDistance=0
        p.Missile.CruiseTargetDuration=0
        p.Missile.TargetRearOffsetDistance=0
        p.Missile.MinTargetUpdateDistance=0
    end
end

clone("srw_aa_bullet", "srw_sentry_bullet", {ProjectileDamage=25, AntiAirDamage=30})
clone("machinegun", "srw_hound_machinegun_bullet", {
    ProjectileDamage=12, AntiAirDamage=0, Gravity=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0, DamageMultiplier={},
})
clone("srw_tank_aa_rocket", "srw_sentry_rocket", {
    ProjectileDamage=15, AntiAirDamage=65,
})

-- Trapper: fast kinetic penetrator using native cannon penetration; no HE splash.
clone("cannon", "srw_hunter_apfsds", {
    ProjectileDamage=550, ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
    ProjectileSplashMaxForce=0, Gravity=0, ExplodeOnTouch=false,
    DestroyShields=false, DamageMultiplier={}, ProjectileIncendiary=false,
    IgnitesBackgroundMaterials=false, IgnitesBackgroundMaterialsPassing=false,
})
clone("srw_salvo_rocket", "srw_hunter_at_rocket", {
    ProjectileDamage=450, ProjectileSplashDamage=40, ProjectileSplashDamageMaxRadius=90,
    AntiAirDamage=0,
})
clone("laser", "srw_hunter_intercept_beam", {
    ProjectileDamage=0, AntiAirDamage=100, ProjectileSplashDamage=0,
    ProjectileSplashDamageMaxRadius=0, ProjectileIncendiary=false,
    IgnitesBackgroundMaterials=false, IgnitesBackgroundMaterialsPassing=false,
    DamageMultiplier={}, Impact=0, ProjectileThickness=2,
})

-- Dedicated ballistic shell: never change the Hound's direct-fire ammunition.
clone("srw_hound_shell", "srw_bastion_shell", {
    Gravity=981, ProjectileDrag=0, MaxAge=30,
})

clone("srw_hound_shell", "srw_smith_he", {
    ProjectileDamage=180, ProjectileSplashDamage=260, ProjectileSplashDamageMaxRadius=180,
    Gravity=0, MaxAge=2, AntiAirDamage=0,
})
clone("mortar", "srw_smith_flame", {
    ProjectileDamage=8, ProjectileSplashDamage=8, ProjectileSplashDamageMaxRadius=45,
    Gravity=0, ProjectileDrag=0, ProjectileMass=0.1, MaxAge=0.85,
    AntiAirDamage=0, ProjectileSplashMaxForce=0, Impact=0,
    ProjectileIncendiary=true, IgnitesBackgroundMaterials=true,
    IgnitesBackgroundMaterialsPassing=false, ExplodeOnTouch=true,
})
-- A ballistic rocket body: no missile seeker and no guidance callback registration.
clone("srw_salvo_rocket", "srw_smith_rocket", {
    ProjectileType="mortar", Missile={}, Gravity=0, MaxAge=2,
    ProjectileDamage=100, ProjectileSplashDamage=100, ProjectileSplashDamageMaxRadius=110,
    AntiAirDamage=0,
})

local sieveBurst={Effect="effects/mortar_air_burst.lua",Terminate=true,
    Projectile={Count=8,Type="srw_sieve_fragment",Speed=2500,StdDev=0.4}}
clone("machinegun", "srw_sieve_fragment", {
    ProjectileDamage=2, AntiAirDamage=20, Gravity=0, MaxAge=0.06,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0, DamageMultiplier={},
})
clone("machinegun", "srw_sieve_flak", {
    ProjectileDamage=4, AntiAirDamage=20, Gravity=0, MaxAge=2,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
    Effects={Age={t200=sieveBurst},Impact={default=sieveBurst}},DamageMultiplier={},
})

clone("srw_tank_aa_rocket", "srw_pike_rocket", {
    ProjectileDamage=90, AntiAirDamage=350, MaxAge=5,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})

clone("srw_pike_rocket", "srw_heavy_aa_rocket", {
    ProjectileDamage=120, AntiAirDamage=450,
})

clone("srw_hunter_bullet", "srw_emp_defence_bullet", {
    ProjectileDamage=25, AntiAirDamage=0,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})

clone("srw_bastion_shell", "srw_cathedral_shell", {
    ProjectileDamage=1400, ProjectileSplashDamage=800, ProjectileSplashDamageMaxRadius=280,
    Gravity=981, ProjectileDrag=0, MaxAge=30,
})

for _,shell in ipairs(Projectiles) do
    if shell.SaveName=="srw_hammer_shell" or shell.SaveName=="srw_bastion_shell"
        or shell.SaveName=="srw_cathedral_shell" or shell.SaveName=="srw_heavy_siege_he"
        or shell.SaveName=="srw_kolokol_he" then
        shell.ExplodeOnTouch=true
        shell.Effects=shell.Effects or {}; shell.Effects.Impact=shell.Effects.Impact or {}
        shell.Effects.Impact.foundations="effects/impact_heavy.lua"
        shell.Effects.Impact.rocks01="effects/impact_heavy.lua"
    end
end

clone("srw_hunter_apfsds","srw_executioner_ap",{ProjectileDamage=950})
clone("srw_hunter_at_rocket","srw_executioner_at",{ProjectileDamage=800,ProjectileSplashDamage=80})

-- Storm ammunition stays independent of every existing robot's balance.
clone("srw_hunter_bullet","srw_storm_bullet",{ProjectileDamage=80,AntiAirDamage=0,MaxAge=3})
clone("srw_smith_rocket","srw_storm_rocket",{ProjectileDamage=150,ProjectileSplashDamage=180,
    ProjectileSplashDamageMaxRadius=140,MaxAge=4,ProjectileType="mortar",Missile={}})
clone("srw_hunter_intercept_beam","srw_storm_intercept_beam",{AntiAirDamage=140})

clone("srw_emp_shell","srw_tempest_emp",{Gravity=981,MaxAge=60,SRWShieldDamage=1000})
clone("srw_storm_rocket","srw_mlrs_rocket",{ProjectileDamage=240,ProjectileSplashDamage=300,
 ProjectileSplashDamageMaxRadius=220,Gravity=981,MaxAge=60})

-- Shared user artwork and explicit, idempotent balance pass. Vanilla ammo is untouched.
clone("srw_hunter_bullet","srw_hornet_bullet",{ProjectileDamage=30,AntiAirDamage=20,MaxAge=8})
clone("srw_sentry_rocket","srw_hornet_rocket",{ProjectileDamage=60,ProjectileSplashDamage=90})
clone("srw_hunter_apfsds","srw_sledge_ap",{ProjectileDamage=650,MaxAge=12})

clone("srw_hunter_bullet","srw_skat_bullet",{ProjectileDamage=20,AntiAirDamage=5,MaxAge=8})
clone("srw_storm_rocket","srw_skat_rocket",{ProjectileDamage=80,ProjectileSplashDamage=110,
    ProjectileSplashDamageMaxRadius=100,MaxAge=8})

clone("srw_hunter_intercept_beam","srw_lantern_beam",{ProjectileDamage=45,AntiAirDamage=120})

clone("srw_hammer_shell","srw_parcel_bomb",{ProjectileDamage=450,ProjectileSplashDamage=600,
 ProjectileSplashDamageMaxRadius=220,Gravity=981,ProjectileDrag=0,MaxAge=20,ExplodeOnTouch=true})

clone("srw_hunter_intercept_beam","srw_archangel_beam",{ProjectileDamage=130,AntiAirDamage=0})
clone("srw_hunter_bullet","srw_archangel_bullet",{ProjectileDamage=50,AntiAirDamage=20,MaxAge=8})
clone("srw_tank_aa_rocket","srw_archangel_rocket",{AntiAirDamage=180,MaxAge=8})

local artillery={srw_parcel_bomb=true,srw_hammer_shell=true,srw_bastion_shell=true,srw_cathedral_shell=true,
    srw_heavy_siege_he=true,srw_mlrs_rocket=true,srw_tempest_emp=true,srw_kolokol_he=true,srw_kolokol_incendiary=true}
for _,p in ipairs(Projectiles) do
    if p.SaveName and string.sub(p.SaveName,1,4)=="srw_" and not p.SRWRebalanced then
        local multiplier=artillery[p.SaveName] and 3 or 2
        for _,field in ipairs({"ProjectileDamage","ProjectileSplashDamage","AntiAirDamage"}) do
            if type(p[field])=="number" then p[field]=p[field]*multiplier end
        end
        if p.ProjectileSplashDamageMaxRadius then p.ProjectileSplashDamageMaxRadius=p.ProjectileSplashDamageMaxRadius*2.5 end
        if artillery[p.SaveName] then p.MaxAge=60
        elseif p.ProjectileType=="missile" then p.MaxAge=8 end
        p.SRWRebalanced=true
    end
end

-- Physical arcs, separate from the balance pass (no second damage multiplier).
-- Native AimWeapon sees this same gravity, rather than compensating a different
-- trajectory from the one that the shell actually flies. Lasers stay instant.
local rockets={srw_archangel_rocket=true,srw_skat_rocket=true,srw_hornet_rocket=true,srw_salvo_rocket=true,srw_tank_aa_rocket=true,srw_sentry_rocket=true,
 srw_hunter_at_rocket=true,srw_pike_rocket=true,srw_executioner_at=true,
 srw_smith_rocket=true,srw_storm_rocket=true,srw_mlrs_rocket=true,srw_heavy_aa_rocket=true}
local cruiseSpeeds={srw_archangel_rocket=5000,srw_hornet_rocket=3500,srw_salvo_rocket=2500,srw_tank_aa_rocket=5000,srw_sentry_rocket=3500,
 srw_hunter_at_rocket=3000,srw_pike_rocket=6000,srw_executioner_at=3000,srw_heavy_aa_rocket=6000}
local rocketArt
for _,p in ipairs(Projectiles) do if p.SaveName=="missile2" then rocketArt=p end end
for _,p in ipairs(Projectiles) do
    if p.SaveName and string.sub(p.SaveName,1,4)=="srw_" and p.SaveName~="srw_beam_barrier"
        and p.ProjectileType~="beam" then
        if rockets[p.SaveName] then
            -- Latest author request: native upgraded Swarm/warhead damage.
            -- Assign after SRW's balance multipliers, so repeated loads stay exact.
            p.ProjectileDamage=300
            p.ProjectileSplashDamage=140
            -- Retain the native smoke trail; the body is the author's new artwork.
            if rocketArt then
                p.TrailEffect=rocketArt.TrailEffect
            end
            p.Gravity=p.ProjectileType=="missile" and 0 or 981
        else
            p.Gravity=981
        end
        p.ProjectileDrag=0
        if cruiseSpeeds[p.SaveName] then
            -- Native steering rotates thrust, not an inert projectile's velocity.
            -- Zero thrust sent the missile straight upwards despite valid locks.
            -- Linear drag balances thrust at the configured cruise speed.
            p.ProjectileDrag=48
            p.Missile.RocketThrust=48*cruiseSpeeds[p.SaveName]
            p.Missile.RocketThrustChange=0
        end
        -- The doubled reach must fit the actual lifetime, including flight in an arc.
        if p.SaveName=="srw_smith_flame" then p.MaxAge=1.7 end
    end
end

-- Apply artwork after cloning/physics on every load, including older definitions.
-- The PNGs are direct exports embedded in the author's Krita documents.
-- Both noses face right; native projectiles point up at zero rotation.
for _,p in ipairs(Projectiles) do
    if p.SaveName and string.sub(p.SaveName,1,4)=="srw_"
        and p.SaveName~="srw_beam_barrier" and p.ProjectileType~="beam" then
        local rocket=rockets[p.SaveName] or p.ProjectileType=="missile"
        local texture=path.."/ui/textures/projectiles/"..(rocket and "smart_missile" or "artillery_shell")
        -- Use the same hierarchical render path as missile2 and mod 5's KS-30.
        p.ProjectileSprite=nil
        p.ProjectileSpriteMipMap=true
        p.DrawBlurredProjectile=false
        p.Projectile={Root={Name="Root",Sprite=texture..".png",Angle=-90,
            -- Visible length: missile2 alpha bounds 297 px at scale 1;
            -- KS-30 HE130 alpha bounds 486 px at scale .5. Preserve author's aspect.
            Scale=rocket and (297/636) or (243/245)}}
        -- Author selected distinct Kolokol HE-B / incendiary-A concepts.
        -- Render-only assignment; keep each round's physics and impact tables.
        local kolokol=p.SaveName=="srw_kolokol_he" and "he"
            or (p.SaveName=="srw_kolokol_incendiary" and "incendiary")
        if kolokol then
            p.Projectile.Root.Sprite=path.."/ui/textures/weapons/kolokol/"..kolokol..".png"
            p.Projectile.Root.Scale=48/(256*.375)
        end
    end
end

local hasBarrier=false
for _,p in ipairs(Projectiles) do if p.SaveName=="srw_beam_barrier" then hasBarrier=true end end
if not hasBarrier then
 table.insert(Projectiles,{SaveName="srw_beam_barrier",ProjectileType="mortar",ProjectileSprite="",
 Gravity=0,ProjectileDrag=1,ProjectileMass=1,ProjectileDamage=0,ProjectileSplashDamage=0,
 FieldType=4,FieldRadius=50,CollidesWithBeams=true,CollidesWithProjectiles=false,
 CollidesWithStructure=false,CollidesWithOwnSide=false,AntiAirDamage=0,AntiAirHitpoints=100000,
 ProjectileShootDownRadius=0,ProjectileThickness=0,CanBeShotDown=false,
 ExplodeOnTouch=false,MaxAge=.5,Effects={},SRWRebalanced=true})
end

-- Engineer bunker: native flight; requested HE shell and doubled MG damage.
-- Rebuild after the general SRW balance/art pass
-- so repeated definition loads cannot apply robot multipliers to these rounds.
for _,spec in ipairs({{"cannon","srw_bunker_shell",85},{"machinegun","srw_bunker_bullet",22}}) do
    local native,index
    for i,p in ipairs(Projectiles) do
        if p.SaveName==spec[1] then native=p end
        if p.SaveName==spec[2] then index=i end
    end
    if native then
        local p=copy(native)
        p.SaveName=spec[2];p.SRWRebalanced=true
        p.ProjectileSprite=nil;p.ProjectileSpriteMipMap=true;p.DrawBlurredProjectile=false
        if spec[1]=="machinegun" then
            p.ProjectileDamage=p.ProjectileDamage*2
            p.WeaponDamageBonus=(p.WeaponDamageBonus or 0)*2
            p.Projectile=nil
            p.ProjectileSprite=native.ProjectileSprite
            p.ProjectileSpriteMipMap=native.ProjectileSpriteMipMap
            p.DrawBlurredProjectile=native.DrawBlurredProjectile
            p.TrailEffect=native.TrailEffect
            p.ProjectileDrag=0
        else
            p.ProjectileSplashDamage=300
            p.ProjectileSplashDamageMaxRadius=350
            p.ExplodeOnTouch=true
            -- Terrain must terminate in an actual blast, not just impact dust.
            p.Effects=p.Effects or {};p.Effects.Impact=p.Effects.Impact or {}
            for _,material in ipairs({"foundations","rocks01"}) do
                p.Effects.Impact[material]={Effect="effects/impact_heavy_ground.lua",Splash=true,Terminate=true}
            end
            p.Projectile={Root={Name="Root",Sprite=path.."/ui/textures/engineering/animated/tracer.png",
                Angle=-90,Scale=spec[3]/(586*.375)}}
        end
        if index then Projectiles[index]=p else table.insert(Projectiles,p) end
    end
end
