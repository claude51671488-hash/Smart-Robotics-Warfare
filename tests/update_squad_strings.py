from pathlib import Path
root=Path(__file__).resolve().parents[1]
values={
'SquadProgressHeader':('Готово | % | Осталось, с | Вышло | Выход, с','Ready | % | Remaining, s | Released | Exit, s'),
'SquadDraftHeader':('Состав | Металл / энергия | Время, с','Draft | Metal / energy | Time, s'),
'SquadMode':('Создать отряд','Create squad'), 'SquadBack':('Назад к фабрике','Back to factory'),
'SquadSave':('Сохранить отряд','Save squad'), 'SquadLoad':('Загрузить состав','Load template'),
'SquadStart':('В производство','Start production'), 'SquadClear':('Очистить состав','Clear draft'),
'SquadRelease':('Выпустить отряд','Release squad'),
'SquadType1':('+ Dynamit','+ Dynamit'), 'SquadType2':('+ Гончая','+ Hound'),
'SquadType3':('+ Ремонтник','+ Repair bot'), 'SquadType4':('+ Осадный','+ Siege bot'),
'SquadType5':('+ ПВО','+ AA bot'),
'squad_full':('Для отряда недостаточно мест в резерве','Not enough reserve space for squad'),
'squad_saved':('Состав сохранён для этого матча','Squad template saved for this match'),
'squad_no_template':('Нет сохранённого состава','No saved template'),
'squad_busy':('Сначала завершите выпуск текущего отряда','Release the current squad first'),
'squad_empty':('Добавьте роботов в состав','Add robots to the squad'),
'squad_started':('Отряд поставлен в производство','Squad queued for production'),
'squad_not_ready':('Отряд ещё производится','Squad is not ready'),
'squad_released':('Отряд выпущен','Squad released'),
'exit_wait':('Выход занят: действует интервал выпуска','Exit cooldown active'),
}
for lang,column in (('Russian',0),('English',1)):
    p=root/f'mods/language-{lang}/srw_ui.lua'; text=p.read_text(encoding='utf-16')
    for key,pair in values.items():
        if 'SRW_UI.'+key+' = ' not in text: text+=f'\nSRW_UI.{key} = L"{pair[column]}"\n'
    p.write_text(text,encoding='utf-16')
print('Squad strings updated')
