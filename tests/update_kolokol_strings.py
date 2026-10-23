"""One-time, idempotent addition retaining Forts UTF-16 wide strings."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for lang, title, he, fire in (
    ('English', 'Kolokol heavy mortar [prototype]', 'HE mine', 'Incendiary mine'),
    ('Russian', 'Колокол — тяжёлая мортира [прототип]', 'Фугасная мина', 'Зажигательная мина'),
):
    path=root/f'mods/language-{lang}/weapons/strings.lua'
    raw=path.read_bytes()
    text=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8-sig')
    for name,value in (('srw_kolokol',title),('srw_kolokol_he',he),('srw_kolokol_incendiary',fire)):
        if f'Weapon.{name} = ' not in text:
            text+=f'\nWeapon.{name} = L"{value}"\n'
    path.write_text(text,encoding='utf-16')
print('Kolokol translations updated')
