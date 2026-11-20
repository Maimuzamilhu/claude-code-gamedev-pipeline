---
name: free-game-audio
description: Give any game a full soundscape for free - footsteps per surface, doors, impacts, UI clicks, ambience loops, music stingers - by sourcing CC0 / CC-BY sound packs, cleaning them with ffmpeg (trim, mono, loudness-normalise, seamless loops, variants) and synthesising missing sounds in code (stingers, alarms, sci-fi chirps, drones, heartbeat). Use whenever the user needs sound effects, ambience, music stings, "the game is too quiet", "sounds are too loud/inconsistent", "make a seamless loop", OpenGameArt / Freesound, or audio credits.
---

# Free game audio

Sound sells a game more than graphics, and it can cost nothing. Three sources:

1. **CC0 packs** (no credit needed): OpenGameArt (filter CC0), Kenney audio packs, Sonniss GDC
   bundles (royalty-free), Freesound (filter CC0).
2. **CC-BY packs** (credit required): fine, but add the credit line to the credits screen the
   same day (see `cc0-asset-sourcing` for the ledger).
3. **Synthesised in code** (`scripts/synth_sfx.py`): stingers, alarms, chirps, drones,
   heartbeats, UI blips. No licence questions at all.

## The sound list (make it before searching)

| Category | Variants | Notes |
|---|---|---|
| Footsteps per surface (concrete, wood, metal, tile, grass, gravel) | 8-10 each | the most-heard sound in the game; pick a random one each step, never the same twice in a row |
| Doors: open, close, locked, heavy | 3-8 each | |
| Impacts (metal, wood, soft) | 5-10 each | for thrown or knocked objects |
| UI: press, back, tick | 2-3 each | short and quiet |
| Ambience per area | 1 seamless loop each | a different bed per room type tells players where they are |
| Player body: breathing, heartbeat | a few | great for tension in any game |
| Enemy: steps, idle, alert, lost | 3-5 each | the player must hear danger before seeing it |
| Music stingers: spotted, success, fail | 2-3 each | 1-3 s |

## Clean every file the same way (`scripts/prep_sfx.py`)

```bash
python scripts/prep_sfx.py sfx  raw/door_open.wav  Assets/Audio/Doors/door_open_00.wav
python scripts/prep_sfx.py loop raw/fan_hum.wav    Assets/Audio/Ambience/amb_fan.wav --seconds 20
python scripts/prep_sfx.py split raw/steps_take.wav Assets/Audio/Steps/step_metal  # one file per hit
```

- **sfx:** mono, trim leading and trailing silence, peak at -6 dBFS, tiny fades so nothing clicks.
- **loop:** mono, loudness-normalised to -24 LUFS (ambience sits under everything), the tail
  cross-faded into the head so it loops with no seam.
- **split:** cuts a recording of many hits (footsteps, clicks) into single files on the silences.

Consistent levels matter more than any single great sound. Mix in the engine with an audio
mixer: groups for SFX, ambience, voice, music, UI; duck ambience and music under voice lines.

## Synthesised sounds (`scripts/synth_sfx.py`)

```bash
python scripts/synth_sfx.py out/      # stinger x3, alarm, chirps x3, drone loop, heartbeat x2, ui blips
```

Edit the parameters at the top of each function to taste. These are pure numpy, so the
result has no third-party rights.

> **Example (HOLD STILL):** about 200 sound files: footsteps on 5 surfaces, robot steps cut from
> one recording into 25 singles, 20 door sounds, 9 ambience loops (one per area, -24 LUFS),
> scared breathing and a heartbeat that speeds up near danger, and three "spotted" stingers plus
> robot chirps synthesised with the same code as `synth_sfx.py`. Six CC-BY packs are credited
> on the credits screen.
