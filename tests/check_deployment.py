"""Execute installer planning: development must have exactly one local target."""
from pathlib import Path
import json
import subprocess
r = Path(__file__).resolve().parents[1]
script = r/'tests/install-local.ps1'
source = script.read_text(encoding='utf-8')
targets = source.split('$targets = @(', 1)[1].split('\n$runtimeDirectories', 1)[0]
assert 'workshop' not in targets.lower(), 'development installer targets subscribed cache'
assert targets.count('C:') == 1 and 'data\\mods\\SmartRoboticsWarfare' in targets
result = subprocess.run([r'C:\Program Files\PowerShell\7\pwsh.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                         '-File', str(script)], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
plan = json.loads(result.stdout)
if isinstance(plan, dict):
    plan = [plan]
assert len(plan) == 1 and plan[0]['Copy'] == '0' and plan[0]['Files'] > 100
assert 'LOCAL DEV' in (r/'displayname.lua').read_text(encoding='utf-16')
print('PASS: real dry-run has one local development target, no Workshop cache destination, explicit DEV label')
