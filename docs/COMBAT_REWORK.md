# 0.40.0 — combat rework and Executioner III

Confirmed multipliers relative to 0.39.2: artillery damage ×3, targeting range ×4; other robot damage ×2 and range ×2; explosion radii ×2.5; tier-III movement speed ×3. Multipliers are not compounded. Artillery launch speed doubles and shell lifetime is 60 seconds so the new ranges are physically reachable. Missile guidance/seeker ranges and lifetime were extended. Dynamit damage/radius are scaled; its fuse/proximity rule stays unchanged. Vanilla weapons are not rebalanced.

The user's Krita mergedimage.png is extracted unchanged to ui/textures/projectiles/user_shell.png. SRW travelling ammunition uses it, including mesh projectile roots. Continuous laser beams and invisible shield fields keep their functional rendering. No texture was generated or repainted.

Artillery samples a horizontal impact interval which shrinks over up to eight successful firing commands at the same target. It tracks target velocity and leads the aim point; turns/acceleration/teleports lose ranging accuracy. The flight-time estimate is approximate, not a full acceleration predictor. Direct guns retain target height, use angular dispersion increasing with range and long-reload guns approach small distant targets. Terrain-obstructed direct shots are withheld; artillery still uses native high-angle aiming. Wheels/tracks have lower target priority than chassis beams. Native mount animation/orientation needs confirmation in Forts; mocks only validate aim coordinates/decisions.

Regent's direct mounts were moved forward/down, keeping rockets high/rear. Other existing staggered mounts remain. Temporary vanilla artwork still needs an in-game clearance check on both sides.

Stationary generators: two total per allied side (teamId modulo 100), counting every tier. Separate mobile robot shields do not consume this limit. Native upgrade I→II costs 3000 metal/15000 energy, 23 s; II→III costs 5000/20000, 60 s. Upgrades preserve remaining shield HP and turn the field off while building. No free refill.

| Tier | Placement radius, batteries | HP | Energy/s | Broken regeneration/s | Idle regeneration/s |
|---|---:|---:|---:|---:|---:|
| I | 8 | 4000 | 500 | 20 | 40 |
| II | 12 | 8000 | 800 | 40 | 80 |
| III | 16 | 15000 | 1600 | 100 | 200 |

Idle regeneration starts after 10 seconds without damage on all tiers (assumption for tiers I/II). Existing activation fee 10000 energy and maximum manual arc length eight batteries are unchanged. Third-tier arcs additionally spawn invisible native beam-blocking fields. Their list is replaced/cleaned on movement, expiry, disablement or generator loss. They do not block friendly shots/robots/vehicles. Beam shield damage uses native projectile DPS, with a 1000 HP/s fallback for function-driven beams; exact per-mod beam tables are not evaluated yet. Blocking behaviour must be checked against vanilla and modded lasers in game.

Shield contour redraw increased to about 30 Hz with 35 ms line lifetime and a single mobile contour. No long-lived visual history is accumulated.

Executioner III, approved concept 15, factory slot 19: two independent AP guns and guided heavy AT launcher; priority for higher-tier robots, structures as fallback, no personal shield, normal squad sharing. Factory III required; individual and squad production supported. Total factory types: 19, including 18 approved concepts and one separate laser prototype. Next: Storm III.

Validation: full mocked Lua regression suite plus dedicated ranging/elevation, tier/limit/regen/beam cleanup and Executioner atomic production tests. This is not an in-game FPS or graphics validation. Restart Forts and begin a new match; old squads retain their stored speeds and offsets.
