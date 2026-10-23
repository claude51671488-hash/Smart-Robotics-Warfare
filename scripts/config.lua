-- Prototype values. Custom combat/armour fields are reserved for the next stage.
-- false marks an unresolved value; do not interpret it as numeric zero.
SRW.Config =
{
    Units = { MineWidth = 127.5 }, -- Prototype: mine selection width 2 * 85 * 0.75.
    Prototype = { QueueLimit = 20, StepHeight = 25, BodyHeight = 22, ExitOffset = 160 },
    Combat =
    {
        StructureHitFraction = 0.40,
        PenetrationSpeedMultiplier = 0.95,
    },
    FactoryReserveByTier = { 20, 50, 100 },
    Robots =
    {
        srw_pike_bot = { Tier=2, ExitDelay=5, Health=1300, SpeedMinesPerSecond=1.5,
            MetalCost=500, EnergyCost=4000, ProductionSeconds=18, ActiveLimit=4,
            Range=9000, BulletSpeed=6000, FireInterval=5, ScanInterval=0.15,
            FollowDistance=240, PrioritizeDamage=true, Guided=true, AntiAir=true,
            Mounts={{Kind="srw_pike_turret",X=25,Y=-45}} },
        srw_pike_turret = { Tier=2, Range=3200, ReloadSeconds=0.6 },
        srw_smith_bot = { Tier=2, ExitDelay=5, Health=1800, SpeedMinesPerSecond=1.8,
            MetalCost=550, EnergyCost=4500, ProductionSeconds=20, ActiveLimit=4,
            Range=1800, ReloadSeconds=4, PreferStructures=true,
            Mounts={{Kind="srw_smith_flame",X=120,Y=-60},
                {Kind="srw_smith_rockets",X=-70,Y=-190}} },
        srw_smith_flame = { Tier=2, Range=2200, ReloadSeconds=2.5, BeamHoldSeconds=0.7 },
        srw_smith_rockets = { Tier=2, Range=3200, ReloadSeconds=5, BeamHoldSeconds=0.4 },
        srw_sentry_bot = { Tier=1, ExitDelay=3, Health=850, SpeedMinesPerSecond=1.8,
            MetalCost=250, EnergyCost=2200, ProductionSeconds=11, ActiveLimit=5,
            Range=4400, ReloadSeconds=1.2, BeamHoldSeconds=0.4,
            BulletSpeed=10000, FireInterval=0.3, ScanInterval=0.12, FollowDistance=200,
            Mounts={{Kind="srw_sentry_rockets",X=-25,Y=-55,AntiAir=true}} },
        srw_sentry_rockets = { Tier=1, Range=5200, BulletSpeed=3500,
            FireInterval=4, ScanInterval=0.15 },
        srw_colossus_bot = { Tier=3, ExitDelay=8, Health=6000, SpeedMinesPerSecond=0.65,
            MetalCost=1600, EnergyCost=14000, ProductionSeconds=45, ActiveLimit=1,
            Range=9600, ReloadSeconds=3, BeamHoldSeconds=0.6, PreferStructures=true, Spacing=280,
            PowerCapacity=100, PowerRegen=18, PowerCost=35,
            ShieldRadius=420, ShieldHP=9000, ShieldRegen=180,
            Mounts={{Kind="srw_colossus_laser",X=230,Y=-85},
                {Kind="srw_regent_rockets",X=-100,Y=-300,AntiAir=true},
                {Kind="srw_regent_turret",X=340,Y=-40},
                {Kind="srw_regent_turret",X=300,Y=-125}} },
        srw_colossus_laser = { Tier=3, Range=6600, ReloadSeconds=8, BeamHoldSeconds=2, PowerCost=70, PreferStructures=true },
        srw_regent_rockets = { Tier=3, Range=8000, BulletSpeed=5000, FireInterval=4, ScanInterval=0.15, Guided=true, PrioritizeDamage=true },
        srw_regent_turret = { Tier=3, Range=4000, ReloadSeconds=2.2, BeamHoldSeconds=0.8 },
        srw_tank_bot = { Tier=2, ExitDelay=5, Health=2000, SpeedMinesPerSecond=1.2,
            MetalCost=750, EnergyCost=6000, ProductionSeconds=25, ActiveLimit=3,
            Range=6600, ReloadSeconds=8, BeamHoldSeconds=2, PreferStructures=true },
        srw_tank_rockets = { Tier=2, Range=6600, BulletSpeed=5000, FireInterval=3, ScanInterval=0.1,
            PrioritizeDamage=true },
        srw_tank_turret = { Tier=2, Range=4400, ReloadSeconds=2.2, BeamHoldSeconds=0.8 },
        srw_heavy_siege_bot = { Tier=3, ExitDelay=8, Health=2200, SpeedMinesPerSecond=0.7,
            MetalCost=1100, EnergyCost=9000, ProductionSeconds=35, ActiveLimit=2,
            Range=14000, MinimumRange=1000, ReloadSeconds=12, PreferStructures=true },
        srw_heavy_aa_bot = { Tier=3, ExitDelay=8, Health=2400, SpeedMinesPerSecond=1.1,
            MetalCost=800, EnergyCost=6500, ProductionSeconds=24, ActiveLimit=2,
            Range=9000, BulletSpeed=12000, FireInterval=0.35, FollowDistance=260,
            PrioritizeDamage=true, RequiresBrace=true, BraceSeconds=1.5, BraceHoldSeconds=1,
            Mounts={{Kind="srw_heavy_aa_gun",AntiAir=true},
                {Kind="srw_heavy_aa_rockets",AntiAir=true},{Kind="srw_heavy_aa_defence"}} },
        srw_heavy_aa_gun = { Tier=3, Range=9000, BulletSpeed=12000, FireInterval=0.35,
            PrioritizeDamage=true, RequiresBrace=true },
        srw_heavy_aa_rockets = { Tier=3, Range=9000, BulletSpeed=6000, FireInterval=6,
            ScanInterval=0.15, Guided=true, AntiAir=true, PrioritizeDamage=true, RequiresBrace=true },
        srw_heavy_aa_defence = { Tier=3, Range=4000, ReloadSeconds=2.2, BulletSpeed=10000 },
        srw_bastion_bot = { Tier=3, ExitDelay=8, Health=3500, SpeedMinesPerSecond=0.8,
            MetalCost=1000, EnergyCost=8000, ProductionSeconds=30, ActiveLimit=2,
            Range=12000, MinimumRange=900, ReloadSeconds=12, DeploySeconds=3, ChargeSeconds=2, PreferStructures=true,
            ShieldRadius=240, ShieldHP=6000, ShieldRegen=150 },
        srw_hunter_bot = { Tier=2, ExitDelay=3, Health=1400, SpeedMinesPerSecond=2.4,
            MetalCost=350, EnergyCost=3000, ProductionSeconds=12, ActiveLimit=5,
            Range=6400, ReloadSeconds=4,
            Mounts={{Kind="srw_hunter_rockets",X=-70,Y=-220},
                {Kind="srw_hunter_interceptor",X=110,Y=-110,AntiAir=true}} },
        srw_hunter_rockets = { Tier=2, Range=7200, ReloadSeconds=6, Guided=true },
        srw_hunter_interceptor = { Tier=2, Range=2800, BulletSpeed=10000,
            FireInterval=1.5, ScanInterval=0.1, InstantBeam=true,
            BeamHoldSeconds=0.25, LockRootDuringBeam=true },
        srw_rocket_bot = { Tier=2, ExitDelay=3, Health=1000, SpeedMinesPerSecond=1.4,
            MetalCost=400, EnergyCost=3500, ProductionSeconds=14, ActiveLimit=3,
            Range=8000, ReloadSeconds=10, BeamHoldSeconds=1.5, PreferStructures=true,
            Mounts={{Kind="srw_psalm_turret",X=130,Y=-60},
                {Kind="srw_psalm_turret",X=130,Y=-130}} },
        srw_psalm_turret = { Tier=2, Range=3600, ReloadSeconds=2.2, BeamHoldSeconds=0.8 },
        srw_laser_bot = { Tier=2, ExitDelay=3, Health=1100, SpeedMinesPerSecond=1.3,
            MetalCost=450, EnergyCost=4000, ProductionSeconds=16, ActiveLimit=3,
            Range=6600, ReloadSeconds=8, BeamHoldSeconds=2, PreferStructures=true },
        srw_emp_bot = { Tier=2, ExitDelay=3, Health=850, SpeedMinesPerSecond=1.8,
            MetalCost=300, EnergyCost=3000, ProductionSeconds=12, ActiveLimit=3,
            Range=5600, ReloadSeconds=6, EMPRadius=240, EMPSeconds=5,
            Mounts={{Kind="srw_emp_turret",X=25,Y=-45}} },
        srw_emp_turret = { Tier=2, Range=3200, ReloadSeconds=2, BeamHoldSeconds=0.4 },
        srw_shield_bot = { Tier=2, ExitDelay=3, Health=1000, SpeedMinesPerSecond=1.6,
            MetalCost=400, EnergyCost=3000, ProductionSeconds=15, ActiveLimit=3,
            FollowDistance=180, ShieldRadius=300, ShieldHP=5000, ShieldRegen=100 },
        srw_aa_bot = { Tier=2, ExitDelay=3, Health=800, SpeedMinesPerSecond=1.8, MetalCost=250,
            EnergyCost=2000, ProductionSeconds=10, ActiveLimit=5, Range=6000,
            BulletSpeed=10000, FireInterval=0.2, FollowDistance=220,
            Mounts={{Kind="srw_sieve_turret",X=30,Y=-55,AntiAir=true}} },
        srw_sieve_turret = { Tier=2, Range=6000, BulletSpeed=10000, FireInterval=0.2 },
        srw_siege_bot = { Tier=1, ExitDelay=3, Health=900, SpeedMinesPerSecond=1.2,
            MetalCost=300, EnergyCost=2500, ProductionSeconds=12, ActiveLimit=5,
            Range=10000, MinimumRange=500, ReloadSeconds=8, AimSeconds=1.2, PreferStructures=true },
        srw_repair_bot = { Tier=1, ExitDelay=3, Health=700, SpeedMinesPerSecond=2,
            MetalCost=150, EnergyCost=1500, ProductionSeconds=8, ActiveLimit=5,
            RepairRange=220, SearchRange=1200, FollowDistance=180,
            RepairInterval=0.2, RepairHPPerSecond=40, RepairMetalPerHP=0.05, RepairEnergyPerHP=0.5 },
        srw_hound = { Tier=1, ExitDelay=3, Health=1200, SpeedMinesPerSecond=2, MetalCost=200,
            EnergyCost=2000, ProductionSeconds=7, ActiveLimit=10, Range=7000,
            Mounts={{Kind="srw_hound_machinegun",X=20,Y=-45}} },
        srw_hound_machinegun = {Tier=1,Range=3600,ReloadSeconds=0.35},
        srw_dynamit_bot =
        {
            Enabled = true, -- Animated walker body; custom armour is pending.
            Tier = 1,
            ExitDelay = 3,
            Health = 4000,
            Armour = 100,
            PenetrationThreshold = false,
            SpeedMinesPerSecond = 2.5,
            AnimationStride = 70, -- 2x the approved initial gait; movement speed is unchanged.
            AnimationFrames = 48,
            BlastRadiusMines = 2.5,
            StructureBlastDamage = 1200,
            RobotBlastDamage = 2000,
            TriggerDistanceMines = { Min = 0.5, Max = 2.3 },
            ActivationSeconds = 0.1,
            MetalCost = 200,
            EnergyCost = 2000,
            ProductionSeconds = 7,
            ActiveLimit = 10,
            ActiveLimitScope = "teamId",
            IgnoredTargetTypes = { "srw_dynamit_bot" },
        },
    },
}

function SRW.RobotSpeed(bot,cfg)
    return bot.SquadSpeed or cfg.SpeedMinesPerSecond
end
function SRW.RobotCost(cfg,squad)
    local rate=squad and 110 or 100
    return math.ceil(cfg.MetalCost*rate/100),math.ceil(cfg.EnergyCost*rate/100)
end

SRW.Config.Robots.srw_executioner_bot={Tier=3,ExitDelay=8,Health=4200,SpeedMinesPerSecond=.85,
 MetalCost=1300,EnergyCost=11000,ProductionSeconds=38,ActiveLimit=2,Range=9000,ReloadSeconds=5,PreferHeavyRobots=true,BulletSpeed=12000,
 Mounts={{Kind="srw_executioner_gun",X=200,Y=-95},{Kind="srw_executioner_rockets",X=-100,Y=-220}}}
SRW.Config.Robots.srw_executioner_gun={Tier=3,Range=9000,ReloadSeconds=5,PreferHeavyRobots=true,BulletSpeed=12000}
SRW.Config.Robots.srw_executioner_rockets={Tier=3,Range=10000,ReloadSeconds=7,Guided=true,PreferHeavyRobots=true,BulletSpeed=3000}

-- Storm: ground suppression plus a separate short-pulse interception laser.
SRW.Config.Robots.srw_storm_bot={Tier=3,ExitDelay=8,Health=3600,SpeedMinesPerSecond=1.1,
 MetalCost=1200,EnergyCost=10000,ProductionSeconds=34,ActiveLimit=2,
 Range=7200,ReloadSeconds=2.4,BeamHoldSeconds=.8,BulletSpeed=10000,
 Mounts={{Kind="srw_storm_rockets",X=-100,Y=-240},{Kind="srw_storm_interceptor",X=160,Y=-130,AntiAir=true}}}
SRW.Config.Robots.srw_storm_rockets={Tier=3,Range=8400,ReloadSeconds=7,BeamHoldSeconds=1,BulletSpeed=4500}
SRW.Config.Robots.srw_storm_interceptor={Tier=3,Range=3500,BulletSpeed=10000,
 FireInterval=1.2,ScanInterval=.1,InstantBeam=true,BeamHoldSeconds=.2,LockRootDuringBeam=true}

-- Remaining approved ground platforms. Values precede the shared balance pass.
SRW.Config.Robots.srw_vault_bot={Tier=3,ExitDelay=8,Health=3400,SpeedMinesPerSecond=.9,
 MetalCost=1300,EnergyCost=11000,ProductionSeconds=38,ActiveLimit=2,
 Range=8500,BulletSpeed=10000,FireInterval=.2,FollowDistance=350,AntiAir=true,
 ShieldRadius=480,ShieldHP=8500,ShieldRegen=160,
 Mounts={{Kind="srw_vault_gun",AntiAir=true},{Kind="srw_vault_laser",AntiAir=true},
 {Kind="srw_vault_laser",AntiAir=true},{Kind="srw_vault_rockets",AntiAir=true}}}
SRW.Config.Robots.srw_vault_gun={Tier=3,Range=8500,BulletSpeed=10000,FireInterval=.2}
SRW.Config.Robots.srw_vault_laser={Tier=3,Range=4500,BulletSpeed=10000,FireInterval=1.2,
 ScanInterval=.1,InstantBeam=true,BeamHoldSeconds=.2}
SRW.Config.Robots.srw_vault_rockets={Tier=3,Range=8500,BulletSpeed=5000,FireInterval=4,
 ScanInterval=.15,Guided=true,AntiAir=true}
SRW.Config.Robots.srw_heavy_siege_bot.Mounts={{Kind="srw_censer_mortar"},{Kind="srw_censer_laser",AntiAir=true}}
SRW.Config.Robots.srw_censer_mortar={Tier=3,Range=14000,MinimumRange=1000,ReloadSeconds=12,PreferStructures=true}
SRW.Config.Robots.srw_censer_laser={Tier=3,Range=3500,BulletSpeed=10000,FireInterval=1.5,
 ScanInterval=.1,InstantBeam=true,BeamHoldSeconds=.25}
SRW.Config.Robots.srw_tempest_bot={Tier=3,ExitDelay=8,Health=3800,SpeedMinesPerSecond=.85,
 MetalCost=1400,EnergyCost=12000,ProductionSeconds=40,ActiveLimit=2,
 Range=12000,MinimumRange=700,ReloadSeconds=9,EMPRadius=480,EMPSeconds=7,
 Mounts={{Kind="srw_tempest_gun"},{Kind="srw_tempest_defence"},{Kind="srw_tempest_defence"}}}
SRW.Config.Robots.srw_tempest_gun={Tier=3,Range=9000,ReloadSeconds=5,PreferHeavyRobots=true,BulletSpeed=12000}
SRW.Config.Robots.srw_tempest_defence={Tier=3,Range=4000,ReloadSeconds=2.2,BulletSpeed=10000,BeamHoldSeconds=.8}
SRW.Config.Robots.srw_mlrs_bot={Tier=3,ExitDelay=8,Health=3200,SpeedMinesPerSecond=.9,
 MetalCost=1350,EnergyCost=11500,ProductionSeconds=40,ActiveLimit=2,
 Range=12000,MinimumRange=900,ReloadSeconds=10,BeamHoldSeconds=1.2,PreferStructures=true,
 Mounts={{Kind="srw_mlrs_launcher"},{Kind="srw_mlrs_launcher"},{Kind="srw_mlrs_defence"}}}
SRW.Config.Robots.srw_mlrs_launcher={Tier=3,Range=12000,MinimumRange=900,ReloadSeconds=10,
 BeamHoldSeconds=1.2,PreferStructures=true}
SRW.Config.Robots.srw_mlrs_defence={Tier=3,Range=4000,ReloadSeconds=2.2,BulletSpeed=10000,BeamHoldSeconds=.8}

-- Approved concept 20. Air units have independent flight and a separate factory.
SRW.Config.Robots.srw_hornet_bot={Domain="air",Air=true,Tier=1,ExitDelay=3,
 Health=800,SpeedMinesPerSecond=4,MetalCost=350,EnergyCost=3000,ProductionSeconds=15,ActiveLimit=8,
 Range=4000,BulletSpeed=10000,ReloadSeconds=.6,BeamHoldSeconds=.25,
 PreferAirRobots=true,CruiseAltitude=900,ClimbSpeed=650,AttackSeconds=2.5,EgressSeconds=2,ThreatRange=3000,
 Mounts={{Kind="srw_hornet_rockets"}}}
SRW.Config.Robots.srw_hornet_rockets={Tier=1,Domain="air",Range=5000,BulletSpeed=3500,
 ReloadSeconds=5,Guided=true,BeamHoldSeconds=.5}
-- Approved flight behaviour: launch a salvo, break off, orbit and make gun runs
-- while the missile bay reloads. These are steering timings, not weapon buffs.
local hornet=SRW.Config.Robots.srw_hornet_bot
hornet.SortieFlight=true;hornet.MuzzleAim=true
hornet.RunInDistance=1200;hornet.RunOutDistance=900;hornet.PassAltitude=500
hornet.PassRange=3200;hornet.BreakClimb=500;hornet.SortieTurnRate=1.8
hornet.OrbitStandOff=2000;hornet.OrbitAltitude=1500
hornet.OrbitRadiusX=1000;hornet.OrbitRadiusY=500;hornet.OrbitRate=.55
hornet.MinimumOrbitSeconds=1.2;hornet.GunDiveSeconds=2.2;hornet.TerrainClearance=350

-- Approved concept 21: one heavy AP gun, no secondary defensive armament.
SRW.Config.Robots.srw_sledge_bot={Domain="air",Air=true,Tier=1,ExitDelay=3,
 Health=1200,SpeedMinesPerSecond=2.6,MetalCost=450,EnergyCost=4200,ProductionSeconds=20,ActiveLimit=6,
 Range=4800,BulletSpeed=9000,ReloadSeconds=5,BeamHoldSeconds=.12,
 PreferHeavyRobots=true,HoverFire=true,DeploySeconds=1,ChargeSeconds=0,
 CruiseAltitude=1100,ClimbSpeed=550,AttackSeconds=6,EgressSeconds=2,ThreatRange=3000}

-- Approved concept 22: ground-support gunship, lower machine gun and two unguided pods.
SRW.Config.Robots.srw_skat_bot={Domain="air",Air=true,Tier=1,ExitDelay=3,
 Health=1100,SpeedMinesPerSecond=2.8,MetalCost=400,EnergyCost=3600,ProductionSeconds=18,ActiveLimit=6,
 Range=4000,BulletSpeed=10000,ReloadSeconds=.8,BeamHoldSeconds=.36,PreferGroundRobots=true,
 CruiseAltitude=800,ClimbSpeed=550,AttackSeconds=5,EgressSeconds=2,ThreatRange=2600,
 Mounts={{Kind="srw_skat_rockets"},{Kind="srw_skat_rockets"}}}
SRW.Config.Robots.srw_skat_rockets={Tier=1,Domain="air",Range=4200,BulletSpeed=4500,
 ReloadSeconds=4,BeamHoldSeconds=.4,PreferGroundRobots=true}

-- Light aircraft fire each burst round from their current moving hardpoint.
for _,kind in ipairs({"srw_hornet_bot","srw_skat_bot"}) do
 local c=SRW.Config.Robots[kind];c.EvasiveFlight=true;c.WeaveHeight=300;c.TurnRate=2.2
 c.BurstCount=kind=="srw_hornet_bot" and 3 or 4;c.BurstPeriod=.08;c.BeamHoldSeconds=nil
end
for _,kind in ipairs({"srw_hornet_rockets","srw_skat_rockets"}) do
 local c=SRW.Config.Robots[kind];c.BurstCount=kind=="srw_hornet_rockets" and 2 or 3
 c.BurstPeriod=kind=="srw_hornet_rockets" and .2 or .16;c.BeamHoldSeconds=nil
end
-- Approved concept 23: one shared laser; engaging ground temporarily occupies it.
SRW.Config.Robots.srw_lantern_bot={Domain="air",Air=true,Tier=1,ExitDelay=3,
 Health=850,SpeedMinesPerSecond=3.6,MetalCost=420,EnergyCost=4000,ProductionSeconds=18,ActiveLimit=6,
 Range=3600,BulletSpeed=10000,ReloadSeconds=1.5,FireInterval=1.5,ScanInterval=.12,
 InstantBeam=true,BeamHoldSeconds=1.25,AirDefenceLaser=true,EvasiveFlight=true,WeaveHeight=250,TurnRate=2.2,
 CruiseAltitude=1000,ClimbSpeed=650,AttackSeconds=5,EgressSeconds=2,ThreatRange=2600}

-- Approved concept 24: a single bomb, rearmed only after returning to a factory.
SRW.Config.Robots.srw_parcel_bot={Domain="air",Air=true,Bomber=true,Tier=1,ExitDelay=3,
 Health=1000,SpeedMinesPerSecond=3,MetalCost=500,EnergyCost=4500,ProductionSeconds=22,ActiveLimit=6,
 Range=8000,CruiseAltitude=1200,ClimbSpeed=650,DropOffset=180,DropSpeed=100,BombLifetime=20,RearmSeconds=8}

-- Approved concept 25: lower siege laser, two independent autocannons and AA rockets.
SRW.Config.Robots.srw_archangel_bot={Domain="air",Air=true,Tier=2,ExitDelay=5,
 Health=3200,SpeedMinesPerSecond=1.8,MetalCost=1100,EnergyCost=10000,ProductionSeconds=35,ActiveLimit=3,
 Range=6000,BulletSpeed=10000,ReloadSeconds=8,InstantBeam=true,BeamHoldSeconds=2.25,
 PreferStructures=true,HoverFire=true,DeploySeconds=.6,ChargeSeconds=.4,
 CruiseAltitude=1500,ClimbSpeed=450,AttackSeconds=12,EgressSeconds=3,ThreatRange=3200,
 Mounts={{Kind="srw_archangel_turret"},{Kind="srw_archangel_turret"},{Kind="srw_archangel_rockets",AntiAir=true}}}
SRW.Config.Robots.srw_archangel_turret={Domain="air",Tier=2,Range=4500,BulletSpeed=10000,
 ReloadSeconds=1.5,BurstCount=4,BurstPeriod=.08,PreferGroundRobots=true,ThreatRange=3200}
SRW.Config.Robots.srw_archangel_rockets={Domain="air",Air=true,Tier=2,Range=6000,BulletSpeed=5000,
 Guided=true,AntiAir=true,ReloadSeconds=4,FireInterval=4,ScanInterval=.15,BeamHoldSeconds=.45}

-- Agreed multipliers, relative to 0.39.2; evaluated once with the configuration.
local artillery={srw_siege_bot=true,srw_bastion_bot=true,srw_heavy_siege_bot=true,srw_colossus_bot=true,srw_censer_mortar=true,srw_tempest_bot=true,srw_mlrs_bot=true,srw_mlrs_launcher=true}
for kind,cfg in pairs(SRW.Config.Robots) do
    cfg.Artillery=artillery[kind] or false
    cfg.BeamWeapon=kind=="srw_archangel_bot" or kind=="srw_lantern_bot" or kind=="srw_tank_bot" or kind=="srw_laser_bot" or kind=="srw_colossus_laser" or kind=="srw_hunter_interceptor" or kind=="srw_storm_interceptor" or kind=="srw_vault_laser" or kind=="srw_censer_laser"
    if cfg.Range then cfg.Range=cfg.Range*(cfg.Artillery and 4 or 2) end
    if cfg.Tier==3 and cfg.SpeedMinesPerSecond then cfg.SpeedMinesPerSecond=cfg.SpeedMinesPerSecond*3 end
end
SRW.Config.Robots.srw_dynamit_bot.RobotBlastDamage=4000
SRW.Config.Robots.srw_dynamit_bot.StructureBlastDamage=2400
SRW.Config.Robots.srw_dynamit_bot.BlastRadiusMines=6.25

SRW.Config.Robots.srw_hunter_bot.BulletSpeed=12000

-- Actual launch speeds for lead/terrain checks; native weapons use the same values.
local speeds={srw_hound=6000,srw_hound_machinegun=10000,srw_emp_bot=3500,
 srw_smith_bot=4500,srw_smith_flame=3000,srw_smith_rockets=3500,
 srw_tank_turret=10000,srw_psalm_turret=10000,srw_regent_turret=10000,
 srw_emp_turret=10000,srw_pike_turret=10000,srw_rocket_bot=2500,srw_hunter_rockets=3000}
for kind,speed in pairs(speeds) do SRW.Config.Robots[kind].BulletSpeed=speed end
for _,kind in ipairs({"srw_rocket_bot","srw_tank_rockets","srw_sentry_rockets"}) do
 SRW.Config.Robots[kind].Guided=true
end

-- Engineer is an additional user-requested concept; stationary guns are native, unscaled.
SRW.Config.Engineering={MineSpacing=2880,BunkerWidth=900,MineTrigger=240,MineHeight=500,
    MineLimitPerSide=128,BunkerLimitPerSide=16}
SRW.Config.Robots.srw_engineer_bot={Tier=2,ExitDelay=5,Health=1200,SpeedMinesPerSecond=2,
    MetalCost=700,EnergyCost=6000,ProductionSeconds=25,ActiveLimit=3}
SRW.Config.Robots.srw_field_bunker={Tier=2,Health=5000,SpeedMinesPerSecond=0,Stationary=true}
-- Flat-ground ballistic reach v^2/g from unchanged native launch speeds.
SRW.Config.Robots.srw_bunker_cannon={Tier=2,Range=6000*6000/981,BulletSpeed=6000,ReloadSeconds=26}
SRW.Config.Robots.srw_bunker_machinegun={Tier=2,Range=5000*5000/981,BulletSpeed=5000,ReloadSeconds=2.55,BeamHoldSeconds=1.05}
SRW.Config.Robots.srw_bunker_cannon_left=SRW.Config.Robots.srw_bunker_cannon
SRW.Config.Robots.srw_bunker_machinegun_left=SRW.Config.Robots.srw_bunker_machinegun
SRW.Config.Robots.srw_bunker_cannon.LimitedElevation=true
SRW.Config.Robots.srw_bunker_machinegun.LimitedElevation=true
SRW.Config.Robots.srw_bunker_cannon.MinElevation=-3
SRW.Config.Robots.srw_bunker_cannon.MaxElevation=7
SRW.Config.Robots.srw_bunker_machinegun.MinElevation=-7
SRW.Config.Robots.srw_bunker_machinegun.MaxElevation=20

-- Narrow traverse keeps the previous targeting range with faster rounds.
SRW.Config.Robots.srw_bunker_cannon.BulletSpeed=12500
SRW.Config.Robots.srw_bunker_machinegun.BulletSpeed=6500
SRW.Config.Robots.srw_bunker_cannon.Precise=true
SRW.Config.Robots.srw_bunker_machinegun.Precise=true

-- Approved Matryoshka: stationary gun, no lifetime timer. Native MG cadence.
SRW.Config.Matryoshka={Health=500,MetalFireCost=600,EnergyFireCost=6000,
    DeploySeconds=2.4,Range=5000*5000/981,BulletSpeed=5000,
    ReloadSeconds=1.5,BurstCount=7,BurstPeriod=.15,MuzzleAim=true}
