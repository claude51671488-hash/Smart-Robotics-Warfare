from pathlib import Path
import re
r=Path(__file__).resolve().parents[1]
for name in ['factory','squads']:
 p=r/f'scripts/ui/{name}.lua'; s=p.read_text()
 # Controls now use a dedicated parent; world-space and network calls are unchanged.
 s=re.sub(r'(SetControlText|ShowControl|AddTextControl|AddButtonControl|ControlExists)\(""',r'\1("srw_factory_window"',s)
 s=re.sub(r'Vec3\((\d+),(\d+),-101\)',lambda m:f'Vec3({m[1]},{int(m[2])-150},-101)',s)
 if name=='factory':
  s=s.replace('local y=234','local y=84').replace('239+((i-1)%3)*30','89+((i-1)%3)*30')
  s=s.replace('    texts = {}\n    AddTextControl','    texts = {}\n    if SRW.CreateFactoryWindow then SRW.CreateFactoryWindow() end\n    AddTextControl')
  s=s.replace('    local localTeam = GetLocalTeamId()','    if SRW.FactoryWindowVisible and not SRW.FactoryWindowVisible(selectedFactory) then f=nil end\n    local localTeam = GetLocalTeamId()')
  s=s.replace('    if SRW.ClickSquadUI and','    if name=="srw_window_close" and SRW.CloseFactoryWindow then SRW.CloseFactoryWindow(selectedFactory); SRW.RefreshUI(); return end\n    if SRW.ClickSquadUI and')
  s=s.replace('Vec3(370,56,-101)','Vec3(280,56,-101)')
  s=s.replace('string.format("#%d | T%d | %d/%d | %d | %d/10 | %.1f", selectedFactory, f.Tier or 1, SRW.FactoryReserve(f), SRW.FactoryCapacity(f), SRW.FactoryQueue(f), SRW.ActiveCount(f.Team,"srw_dynamit_bot"), f.Remaining)','string.format("%d/%d | %d | %.1f", SRW.FactoryReserve(f), SRW.FactoryCapacity(f), SRW.FactoryQueue(f), f.Remaining)')
 else:
  s=s.replace('430,160','430,10').replace('local y=216','local y=66').replace('430,216+','430,66+').replace('430,364','430,214').replace('12,406','12,256').replace('12,424','12,274')
 p.write_text(s)
p=r/'script.lua'; s=p.read_text().replace('0.23.0-individual-production','0.24.0-factory-window')
s=s.replace('dofile(path .. "/scripts/ui/factory.lua")','dofile(path .. "/scripts/ui/window.lua")\ndofile(path .. "/scripts/ui/factory.lua")')
s=s.replace('    SRW.RefreshUI()','    SRW.RefreshUI()\n    SRW.RefreshFactoryMap(delta)'); p.write_text(s)
for lang in ['Russian','English']:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16'); ru=lang=='Russian'
 values={'MapTitle':'Карта роботов' if ru else 'Robot map', 'MapRobots':'● Союзные роботы' if ru else '● Allied robots',
 'MapReactors':'● Реакторы врага' if ru else '● Enemy reactors','MapDot':'●'}
 for k,v in values.items(): s+=f'\nSRW_UI.{k} = L"{v}"\n'
 s=re.sub(r'(\bCounts\s*=\s*L)".*?"',lambda m:m[1]+'"'+('Резерв | Очередь | Осталось, с' if ru else 'Reserve | Queue | Remaining, s')+'"',s)
 p.write_text(s,encoding='utf-16')
