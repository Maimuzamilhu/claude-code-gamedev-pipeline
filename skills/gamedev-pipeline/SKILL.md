---
name: gamedev-pipeline
description: Start here to make any 3D game with an AI coding agent - horror, adventure, puzzle, shooter, platformer, simulation. Turns an idea into a one-page plan, then walks the whole pipeline (engine connection, level kit in Blender, free CC0 assets, enemy or NPC AI, AI voice lines, sound, work orders, trailer, key art) and routes to the right skill in this pack. Use whenever someone says "help me make a game", "where do I start", "I have a game idea", "game dev with Claude", or is a beginner who does not know which tool or step comes next.
---

# Game dev pipeline (start here)

A complete, beginner-friendly path from idea to a finished, presentable 3D game, using free
tools: **Unity** (the engine), **Blender** (models), **free CC0 assets** (textures, props,
sounds), and **open AI models that run on your own computer** (voices).

Every skill in this pack is written for any game. Each one ends with a **real example from
HOLD STILL**, a third-person survival horror game built entirely with this pipeline, so you
can see actual numbers that worked.

## Talk to the user like this

Many users have never made a game. Explain each step in plain words, say what file or result
it produces, and do one step at a time. The first time a term appears (FBX, URP, NavMesh,
LUFS), explain it in one short clause. Show results (a screenshot, a number, a sound) after
each step so progress is visible.

## The pipeline

| Step | What you make | Skill |
|---|---|---|
| 0 | One-page plan: genre, core verb, place, loop, scope | this skill (below) |
| 1 | Agent connected to the engine: run code in the editor, read errors, test in play mode | `unity-editor-bridge` |
| 2 | Level kit: walls, floors, doors, stairs, props built from Python in Blender | `blender-game-kit` |
| 3 | Realistic props and textures for free, cut down to a game budget | `cc0-asset-sourcing` |
| 4 | Enemies or NPCs that see, hear and react believably | `game-enemy-ai` |
| 5 | Voice lines generated locally with an open model | `ai-voice-lines` |
| 6 | Footsteps, doors, ambience, music stingers: free packs + sounds made in code | `free-game-audio` |
| 7 | Audit, measure, fix in batches with numbered work orders | `game-dev-work-orders` |
| 8 | A trailer with a locked frame rate, captions, voice and a sound mix | `game-trailer` |
| 9 | Icon, key art, captioned screenshots | `game-key-art` |

New game: go in order. Existing game: ask what hurts most and start there.

## Step 0: the one-page plan

Write `Docs/PLAN.md` with the user before any code. Ask only what you cannot decide:

1. **The core verb.** What does the player do most? (jump, hide, build, shoot, solve, drive)
2. **The pressure.** What makes it hard? (an enemy, a timer, a puzzle, other players)
3. **The place.** One location is plenty for a first game.
4. **The loop.** Goal, then challenge, then reward, then next goal. Write the first 5 goals.
5. **Scope cut.** List what is NOT in version 1. A small finished game beats a big unfinished one.
6. **Look and sound in one line each.** ("Dark industrial, cold blue light, red warning lamps.")

Then start with a **grey box**: a floor, simple walls, a capsule as the player, the core verb
working. Make that fun before any art.

> **Example (HOLD STILL):** core verb *stay still and hide*; pressure *robots that hunt by
> sight, sound and body heat*; place *one two-floor factory*; loop *objective, then a robot
> patrol, then hide, then progress*; 4 acts, 17 objectives, 3 endings.

## Rules that keep a project sane

- **Measure, do not guess.** Before fixing "it feels laggy" or "the enemy is dumb", log numbers
  (frame times, distances, how often something happens). Check fixes against the same numbers.
- **Fix in batches, build once.** Builds are slow. Fix and test in the editor, then build once.
- **Licence ledger from day one.** Every third-party file gets a row in `Docs/ASSET_LICENSES.md`
  (file, source URL, author, licence, date). CC0 needs no credit; CC-BY needs a credits line.
- **Generated content is code.** Levels, props and sounds come from scripts you can re-run, so a
  change is an edit and a re-run, not hours of hand work.
- **Small commits** with plain messages that say what changed and why.

## Tools to install (all free)

1. **Unity Hub** + a **Unity 6** editor (3D URP template). Any engine works with the ideas here;
   the scripts target Unity.
2. **Blender 4.x** and the **Blender MCP** add-on so the agent can drive Blender.
3. **Python 3.10+** and **ffmpeg** (audio and video processing).
