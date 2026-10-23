from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
for lang in ('Russian','English'):
    ru=lang=='Russian'
    p=root/f'mods/language-{lang}/devices/strings.lua'
    text=p.read_text(encoding='utf-16')
    for tier,roman,capacity in ((1,'I',20),(2,'II',50),(3,'III',100)):
        name=f'srw_factory_ground_{tier}'
        values={name: f'Наземная фабрика роботов {roman}' if ru else f'Ground robot factory {roman}',
                name+'Tip2':f'Резерв: {capacity}; улучшение через меню устройства' if ru else f'Reserve: {capacity}; upgrade through the device menu',
                name+'Tip3':'Выберите фабрику для заказа и выпуска роботов' if ru else 'Select the factory to order and release robots'}
        for key,value in values.items():
            text,count=re.subn(rf'(Device\.{key}\s*=\s*)L"[^"\n]*"',lambda m:m[1]+'L"'+value+'"',text)
            if not count:text+=f'\nDevice.{key} = L"{value}"\n'
    p.write_text(text,encoding='utf-16')
print('Factory tier translations updated')
