# A working set of numbers (HOLD STILL)

Human-sized player, a building of rooms and corridors, robots on a Unity NavMesh agent.
Start here and tune with your own logs.

## Movement (m/s)

| State | Speed |
|---|---|
| Patrol | 1.75 (dwell 2.2 s at each waypoint) |
| Investigate | 2.45 |
| Search | 2.10 for 9 s, sweeping about 5.5 m around the last cue |
| Pursue | 4.05 (player run is slightly faster, so escapes are possible) |

- Capture range: 1.35 m.
- Pursue grace after losing sight: 4.5 s.
- Spot "open" time before a sighting counts: about 1.1 s of continuous view.
- Difficulty ramps per cycle (not per minute): +0.16 m/s speed and +14% hearing per cycle, so
  the noose tightens across a run instead of inside one encounter.

## Partial paths and doors

- If a path is partial, wait up to 3 s at its end, re-plan every 1 s, then go straight to the
  next waypoint.
- Door swing rule: if the player is within 4 m, the door swings away from the player; otherwise
  away from the opener.

## Continue / respawn

- On continue, every robot retreats to at least 15 m from the player.
- 5 s of grace: no capture is possible.
- At most 2 continues per objective, so the player cannot brute-force a section.

## Soak test

- Robots run unattended for long sessions while a script logs stuck events.
- Result after fixes: 16 watchdog recoveries in a long soak, zero hard stucks.
