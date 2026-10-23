"""Independent per-device states, stopped/EMP/fuse poses and native asset bindings."""
from pathlib import Path
import sys,struct
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'.srw-tools'))
from lupa import LuaRuntime
l=LuaRuntime()
l.execute('''SRW={Config={Robots={srw_dynamit_bot={AnimationStride=140}}}};devices={};calls={};data={srw={Robots={}}}
function DeviceExists(id) return devices[id]~=nil end
function GetDevicePosition(id) return devices[id] end
function DeviceDisabled(id) return devices[id].disabled end
function SetDeviceSpriteState(id,state) calls[#calls+1]={id,state} end
''')
l.execute((r/'scripts/robots/dynamit_art.lua').read_text())
l.execute('''
devices[1]={x=0};devices[2]={x=500}
local a={Direction=1};local b={Direction=-1};data.srw.Robots={[1]=a,[2]=b}
SRW.RefreshDynamitAnimation(1,a);SRW.RefreshDynamitAnimation(2,b)
assert(#calls==0,'simulation mutates client sprites')
SRW.RefreshDynamitVisuals()
assert(a.AnimationState=='IdleRight' and b.AnimationState=='IdleLeft')
assert(#calls==2)
devices[1].x=20;SRW.RefreshDynamitAnimation(1,a)
assert(a.AnimationState=='RunRight7' and b.AnimationState=='IdleLeft')
SRW.RefreshDynamitVisuals();assert(#calls==3)
for i=1,100 do SRW.RefreshDynamitVisuals() end
assert(#calls==3,'same pose restarts every render frame')
devices[1].x=21;SRW.RefreshDynamitAnimation(1,a);SRW.RefreshDynamitVisuals()
assert(#calls==4,'additional travel did not advance the denser cycle')
devices[1].x=140;SRW.RefreshDynamitAnimation(1,a);SRW.RefreshDynamitVisuals()
assert(a.AnimationState=='RunRight1','phase does not follow travel')
SRW.RefreshDynamitAnimation(1,a);SRW.RefreshDynamitVisuals();assert(a.AnimationState=='IdleRight')
devices[2].x=480;SRW.RefreshDynamitAnimation(2,b);SRW.RefreshDynamitVisuals()
assert(b.AnimationState=='RunLeft7')
devices[2].disabled=true;devices[2].x=460;SRW.RefreshDynamitAnimation(2,b)
SRW.RefreshDynamitVisuals();assert(b.AnimationState=='IdleLeft')
b.FuseRemaining=.1;SRW.RefreshDynamitAnimation(2,b);SRW.RefreshDynamitVisuals()
assert(b.AnimationState=='ArmedLeft')
local count=#calls;devices[2]=nil;data.srw.Robots[2]=nil;SRW.RefreshDynamitVisuals();assert(#calls==count)
-- Reused IDs must not inherit a stale client cache entry.
devices[2]={x=0};data.srw.Robots[2]={Direction=-1}
SRW.RefreshDynamitAnimation(2,data.srw.Robots[2]);SRW.RefreshDynamitVisuals();assert(#calls==count+1)
-- Rendering exposes intermediate poses between two 25 Hz samples.
devices[3]={x=0};local c={Direction=1};data.srw.Robots[3]=c
SRW.RefreshDynamitAnimation(3,c);SRW.RefreshDynamitVisuals(.01)
devices[3].x=14;SRW.RefreshDynamitAnimation(3,c)
local first=#calls
SRW.RefreshDynamitVisuals(.01);assert(calls[#calls][2]=='RunRight2')
SRW.RefreshDynamitVisuals(.01);assert(calls[#calls][2]=='RunRight3')
SRW.RefreshDynamitVisuals(.01);assert(calls[#calls][2]=='RunRight4')
SRW.RefreshDynamitVisuals(.01);assert(calls[#calls][2]=='RunRight5')
assert(#calls==first+4,'rendering skips intermediate poses')
SRW.RefreshDynamitAnimation(3,c);SRW.RefreshDynamitVisuals(.01)
assert(calls[#calls][2]=='IdleRight','stationary feet kept extrapolating')
''')
game=Path('C:/Program Files (x86)/Steam/steamapps/common/Forts/data')
l=LuaRuntime();l.execute('path="mod"')
def inc(name):
    p=r/name[4:] if name.startswith('mod/') else game/name
    l.execute(p.read_text(encoding='utf-8-sig'))
l.globals().dofile=inc
inc('mod/devices/dynamit_bot.lua')
l.execute('''
assert(HitPoints==4000 and DeviceSplashDamage==4000 and StructureSplashDamage==2400)
assert(#Sprites==1 and Root.Sprite==Sprites[1].Name)
local s=Sprites[1].States
assert(#s.RunRight.Frames==48 and #s.RunLeft.Frames==48)
assert(s.RunRight.NextState=='RunRight' and s.RunLeft.NextState=='RunLeft')
assert(s.RunRight.Frames.duration==.44/2/48)
assert(#s.ArmedRight.Frames==1 and #s.ArmedLeft.Frames==1)
assert(s.RunLeft.Frames[1].texture~=s.RunRight.Frames[1].texture,'opposing direction needs reflected artwork')
assert(s.RunLeft1.Frames[1].texture==s.RunLeft.Frames[1].texture)
''')
for _,state in l.globals().Sprites[1].States.items():
    for key,frame in state.Frames.items():
        if isinstance(key,(int,float)):
            p=r/frame.texture[4:]
            b=p.read_bytes()
            assert b[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',b[16:24])==(444,444)
            assert b[25]==6,'PNG lost RGBA'
inc('mod/effects/dynamit_explode.lua')
l.execute('assert(#Sprites[1].States.Normal.Frames==6 and Effects[1].TimeToLive==.6)')
print('PASS: 48-pose cycle, rendering interpolation, independent devices, EMP/stop/fuse, RGBA assets and native explosion binding')
