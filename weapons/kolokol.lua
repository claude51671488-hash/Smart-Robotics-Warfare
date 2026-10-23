-- Reuse the native mortar body until dedicated artwork is ready.
dofile("weapons/mortar.lua")
Sprites={}
HitPoints=250
WeaponMass=100
Projectile="srw_kolokol_he"
ReloadTime=10
EnergyFireCost=500
MetalFireCost=30
-- About 33% more maximum ballistic reach than 0.5.1 at equal elevation/angle.
MaxFireSpeed=9000.0
-- Retain native angles, clearance and ballistic controls for the first test.
dlc2_Ammunition={
    {
        StringId="Weapon.srw_kolokol_he",
        Sprite=path.."/ui/textures/HUD/kega.png",
        Projectile="srw_kolokol_he",
        MetalFireCost=30, EnergyFireCost=500,
    },
    {
        StringId="Weapon.srw_kolokol_incendiary",
        Sprite=path.."/ui/textures/HUD/kega.png",
        Projectile="srw_kolokol_incendiary",
        MetalFireCost=25, EnergyFireCost=400,
    },
}
