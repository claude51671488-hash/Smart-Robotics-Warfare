# Smart Robotics Warfare

Start with docs/DEVELOPMENT_STATUS.md and the relevant feature document in docs/.
This is a Forts Lua mod. Keep the runtime layout at repository root.

Preserve approved robot names, tiers, weapon roles and factory behavior. Do not
claim gameplay success from mocked tests or Lua syntax compilation. Native tests
require a fresh Forts process after resource changes. Workshop metadata is local
and ignored. Never overwrite subscribed Workshop snapshots during development.

The user accepted the bunker and Dynamit Bot's 48-pose rigid-joint gait.
Do not restore bunker loading/casing animation. Preserve the approved walker
method in docs/DYNAMIT_ANIMATION.md. The user deferred Hornet/aircraft work and
switched to the Kolokol mortar: approved Bastion V3 model, barrel +25%, selected
HE-B and incendiary-A ammunition art, and a simpler low-tech Matryoshka capsule.
See docs/KOLOKOL_ART.md and docs/MATRYOSHKA.md. The author approved capsule V4:
500 HP, shot cost 600 metal/6000 energy, weapons-first targeting and near-360
traverse. Damage is half the native 20mm round (45 direct/10 splash).
Latest author request (24 October), version 0.54.9: fixed Kolokol trunnion
position with native Head firing orientation (Root hardpoint fired forward).
Measured KS30 span, HE/incendiary radii 1350/1125, instant/fading mushroom and
short visual-only native ShockWave sequence remain. Opening is now a separate
non-weapon device, replaced atomically by the real turret after 2.4 active seconds
with HP/owner preserved; EMP pauses it. Ready art has fixed symmetric housing,
connected telescoping stand and a single native moving barrel. Do not restore
whole-turret aim snapshots or use weapon reload states for opening. 0.54.8 was
not accepted: author still saw opening flicker. 0.54.9 is installed, source checks
68/68 and native parse 180/180 pass; fresh gameplay opening/mortar checks remain.
See docs/KOLOKOL_0549.md and DEVELOPMENT_STATUS for actual native evidence.
Hornet native visual acceptance, Krita retouching and Spear II remain deferred.
Do not restart a prepared user flight scene or an active multiplayer match.
See DEVELOPMENT_STATUS for current checks, unfinished work and acceptance.

User-facing communication is Russian. Keep changes concrete and report what was
actually tested. Do not commit logs, backups, credentials or other downloaded mods.
