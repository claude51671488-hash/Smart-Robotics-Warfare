from pathlib import Path
root=Path(__file__).resolve().parents[1]
for lang in ('Russian','English'):
    ru=lang=='Russian'
    for file,entries in {
        'srw_ui.lua':{'SRW_UI.AAOrder':'Заказать ПВО' if ru else 'Order AA bot',
                     'SRW_UI.AARelease':'Выпустить ПВО' if ru else 'Release AA bot'},
        'weapons/strings.lua':{'Weapon.srw_aa_bot':'Робот ПВО [прототип]' if ru else 'AA robot [prototype]'},
    }.items():
        p=root/f'mods/language-{lang}'/file
        text=p.read_text(encoding='utf-16')
        for key,value in entries.items():
            if key+' = ' not in text: text+=f'\n{key} = L"{value}"\n'
        p.write_text(text,encoding='utf-16')
print('AA translations updated')
