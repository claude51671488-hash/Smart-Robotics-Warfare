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
Kolokol art is now 30% larger; HE/incendiary blast radius is x1.5 with a native
reactor-sized smoky plume and no Kolokol radius circle. Native verification of
0.54.3 is still pending; do not claim it from automatic checks.
Hornet native visual acceptance, Krita retouching and Spear II remain deferred.
Do not restart a prepared user flight scene or an active multiplayer match.
See DEVELOPMENT_STATUS for current checks, unfinished work and acceptance.

User-facing communication is Russian. Keep changes concrete and report what was
actually tested. Do not commit logs, backups, credentials or other downloaded mods.
