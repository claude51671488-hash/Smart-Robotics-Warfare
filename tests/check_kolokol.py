"""Native configuration checks; gameplay still needs a Forts test."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent / '.srw-tools'))
from lupa import LuaRuntime
lua = LuaRuntime()
lua.execute('''
path="mods/srw"; Weapons={}; StandardMaxUpAngle=45
Projectiles={
 {SaveName="cannon",ProjectileDamage=999},
 {SaveName="mortar2",ProjectileDamage=60,DisableShields=true,Effects={Impact={default="he"}}},
 {SaveName="mortar",ProjectileIncendiary=true,IgnitesBackgroundMaterials=true,
  Effects={Impact={bracing="fire"}}}
}
''')
for file in ('weapons/weapon_list.lua', 'weapons/projectile_list.lua'):
    source = (root / file).read_text(encoding='utf-8')
    lua.execute(source)
    lua.execute(source)
lua.execute('''
assert(#Weapons==66 and #Projectiles==20)
assert(Weapons[2].SaveName=="srw_kolokol" and Weapons[2].Enabled)
assert(Weapons[2].Prerequisite=="workshop")
local he,fire=Projectiles[6],Projectiles[7]
assert(he.SaveName=="srw_kolokol_he" and he.ProjectileSplashDamage==810 and he.ProjectileDamage==405)
assert(fire.ProjectileDamage==90 and fire.ProjectileSplashDamage==315)
assert(not he.DisableShields and Projectiles[2].DisableShields)
assert(fire.ProjectileIncendiary and fire.IgnitesBackgroundMaterials)
assert(fire.Effects.Impact.bracing=="fire")
he.Effects.Impact.default="changed"
assert(Projectiles[2].Effects.Impact.default=="he")
function dofile(name)
 assert(name=="weapons/mortar.lua")
 Root={Sprite="mortar-base"}; Sprites={{Name="mortar-base"}}
 MinFireAngle=45; MaxFireAngle=85
end
''')
lua.execute((root / 'weapons/kolokol.lua').read_text(encoding='utf-8'))
lua.execute('''
assert(#Sprites==0 and Root.Sprite=="mortar-base")
assert(MaxFireSpeed==9000)
assert(#dlc2_Ammunition==2 and Projectile==dlc2_Ammunition[1].Projectile)
for _,ammo in ipairs(dlc2_Ammunition) do
 assert(ammo.Devices==nil and ammo.Sprite==path.."/ui/textures/HUD/kega.png")
 local found=false
 for _,p in ipairs(Projectiles) do if p.SaveName==ammo.Projectile then found=true end end
 assert(found, "Unregistered ammunition")
end
''')
for lang in ('English','Russian'):
    text=(root/f'mods/language-{lang}/weapons/strings.lua').read_text(encoding='utf-16')
    for name in ('srw_kolokol', 'srw_kolokol_he', 'srw_kolokol_incendiary'):
        assert f'Weapon.{name} = ' in text
assert (root/'ui/textures/HUD/kega.png').is_file()
print('PASS: Kolokol registration, ammunition references, inheritance, isolation and translations')
