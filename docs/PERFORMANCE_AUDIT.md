# Performance audit — 0.39.2

The available game log on 2026-10-12 contains 12,560 Landcruisers/Hex Cannons
incompatibility messages and 12,559 terrain.lua vertexCount errors. It contains
no SRW load banner or SRW health counters. This is evidence about that particular
session, not proof of the cause of the user's SRW slowdown.

SRW changes:
- Ground weapon and AA target enumeration/positions are shared within the combat
  phase of a simulation tick. Existence and ownership are still checked live.
  Newly created projectiles can enter AA acquisition on the following tick;
  shield interception continues to enumerate current projectiles independently.
- Snapshots are local, cleared after mounted weapons update, not saved in data.
- Shield segment intersection uses scalar arithmetic instead of three temporary
  vector tables per test.
- Squad arcs are reused when their radius is unchanged; positions and HP still
  update every tick. Old squad state is replaced, not accumulated.

Inspection: robot, mount, factory, shield and guidance records have removal paths;
shield projectile history is replaced each tick. Minimap controls are reused up to
the peak simultaneous marker count, not added per spawn. No forced garbage
collection was added to the game. Full target sorting and beam scans still cost
more as the number of live entities grows.

Validation: mocked Lua stress test checks 10,000 waves, snapshot invalidation,
guided missile cleanup and 100,000 segment intersections. This does not measure
Forts native memory, graphics effects or actual FPS. A fresh long SRW match and
its log are still needed to confirm the in-game result. Do not combine
Landcruisers with the Hex Cannons setup reported incompatible in the available log.
