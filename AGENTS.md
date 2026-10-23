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
See docs/KOLOKOL_ART.md. The replacement capsule remains a proposal, not approved.
Do not invent turret ammunition balance or treat its concept GIF as a runtime.
Hornet native visual acceptance, Krita retouching and Spear II remain deferred.
Do not restart a prepared user flight scene or an active multiplayer match.
See DEVELOPMENT_STATUS for current checks, unfinished work and acceptance.

User-facing communication is Russian. Keep changes concrete and report what was
actually tested. Do not commit logs, backups, credentials or other downloaded mods.
