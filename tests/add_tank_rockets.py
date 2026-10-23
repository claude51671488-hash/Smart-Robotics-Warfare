from pathlib import Path
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.19.0-tank-bot','0.20.0-tank-rockets')
edit('scripts/config.lua','        srw_tank_turret =','''        srw_tank_rockets = { Tier=2, Range=3300, BulletSpeed=5000, FireInterval=3,
            PrioritizeDamage=true },
        srw_tank_turret =''')
edit('weapons/weapon_list.lua','{"srw_tank_bot","srw_tank_turret"}','{"srw_tank_bot","srw_tank_turret","srw_tank_rockets"}')
edit('weapons/weapon_list.lua','(kind=="srw_tank_bot" and "tank_bot" or "tank_turret")','string.sub(kind,5)')
p=r/'weapons/projectile_list.lua'; s=p.read_text(); s+='''
clone("srw_salvo_rocket", "srw_tank_aa_rocket", {
    ProjectileDamage=30, AntiAirDamage=130,
    ProjectileSplashDamage=0, ProjectileSplashDamageMaxRadius=0,
})
'''; p.write_text(s)
for name in ['check_hound.py','check_kolokol.py']:
 edit('tests/'+name,'#Weapons==13','#Weapons==14')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/weapons/strings.lua'; s=p.read_text(encoding='utf-16')
 s+='\nWeapon.srw_tank_rockets = L"'+('Ракетное ПВО танка' if ru else 'Tank AA rockets')+'"\n'; p.write_text(s,encoding='utf-16')
