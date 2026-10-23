from pathlib import Path
root=Path(__file__).resolve().parents[1]
for lang in ('Russian','English'):
    ru=lang=='Russian'
    entries={
        'srw_ui.lua':{
            'SRW_UI.SiegeOrder':'Заказать осадного' if ru else 'Order siege bot',
            'SRW_UI.SiegeRelease':'Выпустить осадного' if ru else 'Release siege bot'},
        'weapons/strings.lua':{
            'Weapon.srw_siege_bot':'Осадный робот [прототип]' if ru else 'Siege robot [prototype]'},
    }
    for file,values in entries.items():
        p=root/f'mods/language-{lang}'/file
        text=p.read_text(encoding='utf-16')
        for key,value in values.items():
            if key+' = ' not in text: text+=f'\n{key} = L"{value}"\n'
        p.write_text(text,encoding='utf-16')
print('Siege translations updated')
