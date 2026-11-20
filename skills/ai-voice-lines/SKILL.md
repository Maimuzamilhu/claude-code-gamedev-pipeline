---
name: ai-voice-lines
description: Generate voice lines for any game character locally and for free with the open Kokoro-82M text-to-speech model from Hugging Face (Apache 2.0, no account, no API key, no per-line cost), then shape them with effects - radio, robot, PA speaker, monster, ghost, phone, cave echo - and export game-ready WAV files. Use whenever the user wants dialogue, narration, barks, NPC or enemy voices, placeholder voice acting, "AI voice", "text to speech", "TTS", "Hugging Face voice model", or wants characters to talk without hiring actors.
---

# AI voice lines (local, free)

**Kokoro-82M** (https://huggingface.co/hexgrad/Kokoro-82M, Apache 2.0) is a small, good-sounding
text-to-speech model that runs on a normal CPU in about a second per line. It is run through
**kokoro-onnx** (MIT). Nothing is uploaded anywhere and the generated audio is yours.

## Setup (explain it step by step)

```bash
python -m venv kokoro-venv
kokoro-venv/Scripts/pip install kokoro-onnx soundfile numpy      # Windows
# kokoro-venv/bin/pip install kokoro-onnx soundfile numpy        # macOS / Linux
```

Download the two model files (about 330 MB together) into a `model/` folder outside the game
project:

- https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
- https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

## Write the lines as data

`lines.json`: one entry per line, so a rewrite is a re-run:

```json
[
  {"id": "guard_alert",  "text": "Who's there?",            "voice": "am_adam", "speed": 1.0,  "fx": "radio"},
  {"id": "hero_intro",   "text": "I have to get out of here.", "voice": "bf_emma", "speed": 0.95, "fx": "none"},
  {"id": "robot_found",  "text": "I see you.",              "voice": "am_onyx", "speed": 0.8,  "fx": "robot"}
]
```

Generate: `python scripts/make_voices.py lines.json model/ out/`

`fx` presets in the script: `none`, `radio` (walkie-talkie), `phone`, `robot` (comb filter,
lowered, small speaker), `pa` (driven horn + slap-back echo + hiss), `monster` (pitched down,
saturated), `ghost` (pitched up, airy echo), `cave` (long echo).

## Choosing voices

Voice ids start with language/accent and gender: `a` = American, `b` = British, `f` = female,
`m` = male (`af_heart`, `af_sky`, `am_adam`, `am_onyx`, `bf_emma`, `bm_george`, ...). Generate
the same line with 3-4 voices and let the user pick by ear. `speed` 0.8-0.9 sounds heavier and
more menacing; 1.05-1.1 sounds urgent.

## Making lines sound good in a game

- **Short barks** (1-4 words) work best and read clearly over gameplay.
- Trim silence, normalise peaks to about -1 dBFS, add a few ms fade in and 60 ms fade out
  (the script does this) so lines do not click.
- Spell for pronunciation: "Arc seven" instead of "ARC-7".
- Name files `<character>_<situation>_<n>.wav` and pick a random variant at runtime so repeats
  are less obvious.
- Keep the generator script, the `lines.json` and the raw takes outside the game folder; ship
  only the final WAVs. Record the model and licence in your asset ledger.
- AI voices are a strong first version. Real actors can replace the WAVs later with the same
  file names.

> **Example (HOLD STILL):** the robots' lines ("Movement." "Where are you?" "I see you."
> "Directive seven. Harvest.") use `am_onyx` and `am_adam` at speed 0.8-1.08 through the
> `robot` and `pa` effects; the scientist Grace uses `bf_emma`; a boy uses `af_sky` pitched up.
> The voiced lines also carry the trailer.
