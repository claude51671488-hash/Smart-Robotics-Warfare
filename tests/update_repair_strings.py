from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
for lang in ('Russian','English'):
    ru=lang=='Russian'
    p=root/f'mods/language-{lang}/srw_ui.lua'
    text=p.read_text(encoding='utf-16')
    values={
        'Title':'SRW — Фабрика роботов' if ru else 'SRW - Robot factory',
        'Order':'Заказать Dynamit' if ru else 'Order Dynamit',
        'Release':'Выпустить Dynamit' if ru else 'Release Dynamit',
        'HoundOrder':'Заказать Гончую' if ru else 'Order Hound',
        'HoundRelease':'Выпустить Гончую' if ru else 'Release Hound',
        'RepairOrder':'Заказать ремонтника' if ru else 'Order repair bot',
        'RepairRelease':'Выпустить ремонтника' if ru else 'Release repair bot',
    }
    for key,value in values.items():
        pattern=rf'((?:SRW_UI\.)?\b{key}\s*=\s*)L"[^"\n]*"'
        text,count=re.subn(pattern,lambda m:m[1]+'L"'+value+'"',text)
        if not count: text+=f'\nSRW_UI.{key} = L"{value}"\n'
    p.write_text(text,encoding='utf-16')
    p=root/f'mods/language-{lang}/devices/strings.lua'
    text=p.read_text(encoding='utf-16')
    values={
        'srw_repair_bot':'Ремонтник I [прототип]' if ru else 'Repair bot I [prototype]',
        'srw_repair_botTip2':'Без оружия; сопровождает и ремонтирует роботов' if ru else 'Unarmed; escorts and repairs robots',
        'srw_factory_ground_1Tip2':'Dynamit, Гончая и ремонтник; общий резерв 20' if ru else 'Dynamit, Hound and repair bot; shared reserve 20',
    }
    for key,value in values.items():
        pattern=rf'(Device\.{key}\s*=\s*)L"[^"\n]*"'
        text,count=re.subn(pattern,lambda m:m[1]+'L"'+value+'"',text)
        if not count: text+=f'\nDevice.{key} = L"{value}"\n'
    p.write_text(text,encoding='utf-16')
print('Repair bot translations updated')
