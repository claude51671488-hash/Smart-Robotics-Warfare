from pathlib import Path
import re
r=Path(__file__).resolve().parents[1]
# Keep SaveName and squad indices stable: existing queues refer to these IDs.
names=[('srw_dynamit_bot','Dynamit Bot','Dynamit Bot'),('srw_hound','Гончая','Hound'),
('srw_repair_bot','Латочник I','Patcher I'),('srw_siege_bot','Молот I','Hammer I'),
('srw_aa_bot','Решето II','Sieve II'),('srw_shield_bot','Покров II','Shroud II'),
('srw_emp_bot','Разряд II','Discharge II'),('srw_laser_bot','Лазерный прототип II','Laser prototype II'),
('srw_rocket_bot','Псалом II','Psalm II'),('srw_hunter_bot','Ловчий II','Trapper II'),
('srw_bastion_bot','Собор III','Cathedral III'),('srw_heavy_aa_bot','Неборез III','Skycleaver III'),
('srw_heavy_siege_bot','Кадило III','Censer III'),('srw_tank_bot','Бастион II','Bastion II'),
('srw_colossus_bot','Регент III','Regent III')]
def replace(s,key,value):
 pattern=r'('+re.escape(key)+r'\s*=\s*L)"[^"\r\n]*"'
 result,n=re.subn(pattern,lambda m:m[1]+'"'+value+'"',s)
 if n!=1: raise ValueError((key,n))
 return result
for lang,col in [('Russian',1),('English',2)]:
 base=r/f'mods/language-{lang}'; ru=lang=='Russian'
 p=base/'srw_ui.lua'; s=p.read_text(encoding='utf-16')
 for i,row in enumerate(names,1):
  s=replace(s,f'SRW_UI.SquadType{i}','+ '+row[col])
  if i>=6: s=replace(s,f'SRW_UI.SingleType{i}',row[col])
 for prefix,index in [('Repair',2),('Siege',3),('AA',4)]:
  for action in ['Order','Release']:
   s=replace(s,f'SRW_UI.{prefix}{action}',('Заказать: ' if action=='Order' else 'Выпустить: ') + names[index][col] if ru else action+': '+names[index][col])
 p.write_text(s,encoding='utf-16')
 for category,namespace in [('weapons','Weapon'),('devices','Device')]:
  p=base/category/'strings.lua'; s=p.read_text(encoding='utf-16')
  for internal,russian,english in names:
   key=namespace+'.'+internal
   if re.search(re.escape(key)+r'\s*=',s):
    value=russian if ru else english
    if internal!='srw_laser_bot': value+=' [прототип]' if ru else ' [prototype]'
    s=replace(s,key,value)
  if category=='weapons':
   for key,rus,eng in [('srw_tank_turret','Автопушка Бастиона','Bastion autocannon'),('srw_tank_rockets','Ракетное ПВО Бастиона','Bastion AA rockets'),('srw_colossus_laser','Лазер Регента','Regent laser')]:
    s=replace(s,'Weapon.'+key,rus if ru else eng)
  p.write_text(s,encoding='utf-16')
p=r/'script.lua'; p.write_text(p.read_text().replace('0.25.0-guided-rockets','0.26.0-concept-names'))
