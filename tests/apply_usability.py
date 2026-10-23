from pathlib import Path
import re
r=Path(__file__).resolve().parents[1]
def edit(name,a,b):
 p=r/name; s=p.read_text(encoding='utf-8'); assert a in s,(name,a); p.write_text(s.replace(a,b),encoding='utf-8')
edit('script.lua','0.20.0-tank-rockets','0.21.0-formation-ui')
edit('script.lua','dofile(path .. "/scripts/robots/movement.lua")','dofile(path .. "/scripts/robots/movement.lua")\ndofile(path .. "/scripts/robots/spacing.lua")')
edit('script.lua','    SRW.UpdateRobots(0.04)','    SRW.SeparateRobots(0.04)\n    SRW.UpdateRobots(0.04)')
edit('scripts/robots/movement.lua','        elseif bot.Kind=="srw_hound"','        elseif bot.SpacingThisTick and bot.FuseRemaining==nil then\n            -- Formation correction already moved this robot this tick.\n        elseif bot.Kind=="srw_hound"')
for name in ['movement','hound','repair','shield','aa']:
 p=r/f'scripts/robots/{name}.lua'; s=p.read_text(); s=s.replace('CastRayFromDevice(', '(SRW.MovementRay or CastRayFromDevice)('); p.write_text(s)
edit('scripts/config.lua','srw_aa_bot = { ExitDelay','srw_aa_bot = { Tier=2, ExitDelay')
for kind in ['hound','repair_bot','siege_bot']:
 edit('scripts/config.lua',f'srw_{kind} = {{ ExitDelay',f'srw_{kind} = {{ Tier=1, ExitDelay')
edit('scripts/factories/production.lua','function SRW_OrderAA(team,id)\n    local f=SRW.ValidFactory(tonumber(team),tonumber(id)); if not f then return end','function SRW_OrderAA(team,id)\n    local f=SRW.ValidFactory(tonumber(team),tonumber(id)); if not f then return end\n    if (f.Tier or 1)<2 then f.Status="tier_required"; return end')
# Compact existing controls without introducing an unregistered font style.
for file in ['factory','squads','shield']:
 p=r/f'scripts/ui/{file}.lua'; s=p.read_text()
 s=s.replace('Vec3(64,36,0)','Vec3(36,22,0)')
 s=re.sub(r'false,\s*"Normal"', 'false,"Readout"',s)
 if file=='factory':
  for a,b in [('20,180','12,166'),('20,210','12,186'),('20,240','12,206'),('600,240','370,206'),('270+((i-1)%3)*46','234+((i-1)%3)*30'),('Vec3(20,y','Vec3(12,y'),('Vec3(94,y+9','Vec3(54,y+5'),('Vec3(360,y','Vec3(240,y'),('Vec3(434,y+9','Vec3(282,y+5'),('700,325','480,269'),('700,371','480,299'),('700,279','480,239'),('20,408','12,332'),('94,417','54,337')]: s=s.replace(a,b)
  s=s.replace('"$SRW_UI." .. f.Status','"$SRW_UI." .. (f.Status or "ready")')
  s=s.replace('"#%d (T%d) | %d/%d | %d | %d/10 | %.1f"','"#%d | T%d | %d/%d | %d | %d/10 | %.1f"')
 elif file=='squads':
  for a,b in [('x+74,y+9','x+42,y+5'),('650,170','430,160'),('230+((i-1)%5)*38','216+((i-1)%5)*28'),(',20,y)',',12,y)'),(',360,y)',',250,y)'),('485,y+9','310,y+5'),('650,230+(i-1)*38','430,216+(i-1)*28'),('650,420','430,364'),('20,475','12,406'),('650,475','12,424')]: s=s.replace(a,b)
  s=s.replace('local onPage=not row or math.floor((row-1)/5)+1==SRW.SquadPage','local onPage=not row or math.floor((row-1)/5)+1==SRW.SquadPage\n        local unlocked=not row or not f or (SRW.Config.Robots[SRW.RobotKinds[row]].Tier or 1)<=(f.Tier or 1)')
  s=s.replace('and onPage)','and onPage and unlocked)')
 elif file=='shield':
  for a,b in [('20,180','12,166'),('20,220','12,190'),('265+(i-1)*46','220+(i-1)*30'),('Vec3(20,y','Vec3(12,y'),('Vec3(94,y+9','Vec3(54,y+5')]: s=s.replace(a,b)
  s=s.replace('if sid==selected then','if sid==selected or shield.Mobile then')
  s=s.replace('if shield.Active and shield.Arc then drawArc(shield.Arc,p,{r=60,g=180,b=255,a=math.floor(35+220*ratio)}) end','''if shield.Active and shield.Arc then
                drawArc(shield.Arc,p,{r=60,g=220,b=255,a=math.floor(100+155*ratio)})
                if shield.Mobile then drawArc(shield.Arc,{x=p.x+2,y=p.y},{r=150,g=245,b=255,a=220}) end
            end''')
 p.write_text(s,encoding='utf-8')
for lang,ru in [('Russian',True),('English',False)]:
 p=r/f'mods/language-{lang}/srw_ui.lua'; s=p.read_text(encoding='utf-16')
 values={'Title': 'Фабрика роботов' if ru else 'Robot factory',
 'SquadMode':'Все роботы / отряд' if ru else 'All robots / squad',
 'SquadBack':'Быстрый заказ' if ru else 'Quick orders',
 'tier_required':'Улучшите фабрику: выберите её и нажмите улучшение' if ru else 'Select the factory and upgrade its tier'}
 for k,v in values.items(): s=re.sub(r'(SRW_UI\.'+k+r'\s*=\s*L)"[^"\r\n]*"',lambda m:m[1]+'"'+v+'"',s)
 p.write_text(s,encoding='utf-16')
# Tests that exercise old AA quick order must now use the required factory tier.
p=r/'tests/check_aa.py'; s=p.read_text().replace('srw_factory_ground_1','srw_factory_ground_2').replace('{Team=101,Queue=0','{Team=101,Tier=2,Queue=0'); p.write_text(s)
p=r/'tests/check_shields.py'; s=p.read_text().replace('pos.y==265','pos.y==220').replace('pos.y==311','pos.y==250'); p.write_text(s)
