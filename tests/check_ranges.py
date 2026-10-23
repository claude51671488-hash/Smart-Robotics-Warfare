"""Check inherited weapon limits and ballistic reach, not the engine renderer/solver."""
from pathlib import Path
import math
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent / '.srw-tools'))
from lupa import LuaRuntime

def environment():
    lua = LuaRuntime()
    lua.execute('SRW={}; path="mod"')
    def include(name):
        if name.startswith('mod/'):
            lua.execute((root / name[4:]).read_text(encoding='utf-8'))
        # Native artwork definitions are not needed for these explicit overrides.
    lua.globals().dofile = include
    lua.execute((root / 'scripts/config.lua').read_text(encoding='utf-8'))
    return lua

lua = environment()
kinds = [k for k,c in lua.globals().SRW.Config.Robots.items() if c.Range and not k.startswith("srw_bunker_")]
artillery = {'srw_siege_bot', 'srw_heavy_siege_bot', 'srw_bastion_bot', 'srw_colossus_bot'}
for kind in kinds:
    env = environment()
    env.execute((root / ('weapons/' + kind[4:] + '.lua')).read_text(encoding='utf-8'))
    g = env.globals()
    cfg = g.SRW.Config.Robots[kind]
    assert g.MaxFireRadius >= cfg.Range, kind
    if g.MinFireSpeed is not None and g.MaxFireSpeed is not None:
        assert g.MinFireSpeed <= g.MaxFireSpeed, kind
    if kind in artillery:
        assert g.MinFireAngle==45 and g.MaxFireAngle==135, kind
        # Check near and far shots, including higher and lower targets.
        for distance in [1000, cfg.Range, -1000, -cfg.Range]:
            for dy in [-300, 0, 300]:
                solutions = []
                for angle in list(range(45,86)) + list(range(95,136)):
                    theta = math.radians(angle)
                    denominator = 2 * math.cos(theta)**2 * (distance*math.tan(theta)+dy)
                    if denominator <= 0:
                        continue
                    speed = math.sqrt(981*distance**2/denominator)
                    if g.MinFireSpeed <= speed <= g.MaxFireSpeed and distance*math.cos(theta)>0:
                        time = distance/(speed*math.cos(theta))
                        solutions.append(time)
                assert solutions and min(solutions) < 60, (kind, distance, dy)
    elif kind == 'srw_hunter_bot':
        assert g.MinFireAngle < 0, 'Trapper inherited artillery angles'

lua.execute('Projectiles={{SaveName="cannon"},{SaveName="mortar2"}}')
lua.execute((root / 'weapons/projectile_list.lua').read_text())
shells = {p.SaveName:p for _,p in lua.globals().Projectiles.items()}
for name in ['srw_hammer_shell','srw_heavy_siege_he','srw_bastion_shell','srw_cathedral_shell']:
    assert shells[name].Gravity == 981 and shells[name].MaxAge == 60
assert shells['srw_hound_shell'].Gravity == 981
assert shells['srw_hunter_apfsds'].Gravity == 981
print('PASS: every armed robot range fits its weapon, valid speed intervals, artillery elevation/reach/lifetime, isolated direct-fire guns')
