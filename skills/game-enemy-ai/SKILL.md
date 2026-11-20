---
name: game-enemy-ai
description: Design and build enemies and NPCs that feel smart and fair in any game - guards, monsters, zombies, robots, creatures - with senses (sight, hearing, and custom ones), a rising suspicion meter instead of instant detection, patrol / investigate / search / chase states, hiding spots, door handling, anti-camping pressure and debug readouts. Use whenever the user wants an enemy, guard, stealth, hide-and-seek, "the AI is dumb", "it sees me through walls", "it gets stuck", "unfair deaths", NavMesh agents, or a monster that hunts the player.
---

# Enemy and NPC AI that feels fair

Players forgive a deadly enemy. They do not forgive one they cannot read. The goal is
**legibility**: after every capture the player can say "I know what I did wrong".

## 1. Senses as channels, not one boolean

Give each sense its own rule and its own counter, so cover and hiding spots become choices:

| Channel | How it works | What beats it |
|---|---|---|
| Sight | view cone + range + raycast to several body points, scaled by light and movement | walls, darkness, standing still |
| Hearing | the enemy polls a world **noise list** (position, loudness, time); falloff by distance, muffled by walls | walking slowly, soft floors |
| Custom (smell, heat, magic, radar) | your game's twist | something the player can reason about |

A hiding spot then has a value **per channel** (a closet blocks sight but not sound; a cold room
blocks heat). With one "is hidden" flag every hiding place is the same place, and the only
decision left is distance.

## 2. Suspicion rises, it does not flip

Each frame a sense adds to a 0..1 **suspicion** meter; out of contact it drains. Thresholds:
`> 0.3` curious (turn, look), `> 0.6` investigate (walk to the last cue), `1.0` spotted.
Show it (an icon over the enemy, a sound, a light colour). The "it almost saw me" moment is the
tension of the whole genre; instant detection throws it away.

## 3. States

`Patrol -> Investigate -> Search -> Pursue -> (Capture | lose track -> Search -> Patrol)`

- **Patrol:** waypoints with short dwells; vary the route between runs.
- **Investigate:** go to the noise/sight position at a brisk walk, look around.
- **Search:** sweep nearby rooms for a fixed time, then give up audibly ("lost them").
- **Pursue:** fast, but with a short **grace** time after line of sight breaks so it does not
  know where you are by magic.
- Make every transition **audible or visible** (voice line, light, sound sting).

## 4. Navigation that does not break

- Use the engine's NavMesh agent. After every destination, check the path status: if the path is
  **partial** (a closed door, a gap), wait a moment, re-plan, then move to the next waypoint
  instead of pushing into a wall forever.
- Doors: the enemy opens doors through the same door component the player uses; doors swing
  **away from whoever is closest** so they never shove the player.
- Add a **watchdog**: if an agent has not moved more than 0.3 m in N seconds while it should
  be moving, log it and recover (re-plan, or warp to the nearest NavMesh point). Count
  recoveries in a soak test; aim for zero hard stucks.
- After a respawn or "continue", make enemies **retreat** from the player and give a few seconds of
  grace so the player is not caught again instantly.

## 5. Anti-camping: pressure, not a timer

A player standing in one safe corner forever is the dominant boring strategy. Instead of
"30 seconds in one place = death", run a hidden **pressure meter** that fills while the player
loiters and drains while they move. At about two thirds, give a visible warning; at full,
**report** the player's rough area to the enemy (it comes to investigate). The same director
can back the enemy **off** after a long chase, so pressure rises and falls like a horror film.

## 6. Tune with numbers

Log per encounter: distance at first notice, time from notice to spotted, how the player was
found (which channel), escapes vs captures. Tune speeds and thresholds from that table, not
from feel alone. Add a debug overlay that shows each enemy's state and suspicion.

See `references/numbers-holdstill.md` for a full working set of values and
`references/perception-sketch.cs` for a compact engine-agnostic structure in C#.

> **Example (HOLD STILL):** four channels (sight, hearing, body heat, and a scanner), 20 hiding
> spot types each with per-channel concealment, robots that speak their state ("Movement."
> "Where are you?" "I see you."), a stillness director against camping, and a soak test that
> runs the robots for hours and counts watchdog recoveries.
