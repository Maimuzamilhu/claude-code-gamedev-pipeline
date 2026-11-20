---
name: game-trailer
description: Make a 20-60 second game trailer from real gameplay - script the shots, capture them from the Unity editor at a locked frame rate (no blinking or stutter), then assemble with ffmpeg - colour grade, captions in the game's font, a title card, and a sound mix built from the game's own voices, ambience and stingers. Use whenever the user wants a trailer, teaser, gameplay video, promo clip, "record my game", "the video flickers / blinks", or a video for a store page, YouTube, social media or a README.
---

# Game trailer from real gameplay

A trailer that works: the threat or hook in the first 3 seconds, 4-6 short shots, one caption
per shot, a title card, sound that hits on the cuts. 20-30 seconds is enough.

## 1. Script it (`references/shot-list.md`)

Write a table before recording: shot number, length (2.5-5 s), what the camera does, what
moves, the caption (2-5 words, all caps), and the sound cue. Order: hook, the core verb, the
pressure, one escalation, then the title.

## 2. Capture with a locked clock

Recording the screen in real time makes lights, particles and animation **blink and stutter**
because the editor's frame rate wobbles. Lock the game clock instead:
`scripts/TrailerRecorder.cs` sets `Time.captureFramerate = 30`, so every frame advances the game
exactly 1/30 s however long it takes to render, and writes each frame as a 1920x1080 JPG.

```csharp
// From the editor (play mode), per shot:
TrailerRecorder.Record("Recordings/shot01", 4.2f, t => {
    // t goes 0..1 across the shot: move the camera, the player, the enemies here
    cam.position = Vector3.Lerp(start, end, Mathf.SmoothStep(0, 1, t));
    cam.LookAt(target);
});
```

Tips that mattered:
- Turn the gameplay camera script **off** for close-ups and drive `Camera.main` yourself;
  an orbit camera fights you.
- Freeze AI you do not want moving; script the ones you do (`SetDestination`, set rotation).
- Use the highest quality level for capture; you are not limited by real time.
- 6 warm-up frames before frame 0 so poses settle (the recorder does this).

## 3. Assemble (`scripts/make_trailer.py` + `trailer.json`)

```bash
python scripts/make_trailer.py trailer.json
```

`trailer.json` lists the shot folders and captions, the title, the fonts, and the audio cues
(file, start time in seconds, volume, loop). The script grades each shot (contrast, saturation,
vignette), fades between shots, draws captions, builds the title card, mixes the sound and
writes one MP4 (H.264 + AAC, plays everywhere). See `references/trailer.example.json`.

## 4. Sound is half the trailer

**Voices must be heard.** The most common trailer mistake: voice lines sit under the ambience
and vanish on phone and laptop speakers (filtered voices like radio or robot lose their bass and
disappear first). Mark every spoken cue `"voice": true` in `trailer.json`: the script
loudness-matches each line, adds presence around 2.8 kHz, and **ducks** everything else about
10 dB while someone speaks (sidechain compression), then masters the mix to about -14 to -16
LUFS. To fix the sound of a finished video without re-rendering it, set `"video"` and
`"shot_seconds"` and run `make_trailer.py trailer.json --audio-only`. Check the result with a
spectrogram (`ffmpeg -i trailer.mp4 -lavfi showspectrumpic=s=1600x500 spec.png`): speech shows
as bright stacked stripes between 300 Hz and 3 kHz.

- Bed: 1-2 ambience loops from the game under everything.
- Hits: a stinger or impact on the reveal and on the title.
- Voice: 3-5 short lines from the game's characters, at least one human (see `ai-voice-lines`).
- Body: heartbeat or breathing for tension games, crowd or music for others.
- Fade in 0.8 s, fade out 1.2 s, limiter at -1 dB so it is loud but not clipped.

## 5. Export variants

- 16:9 1920x1080 MP4 for YouTube and store pages.
- A 5-second GIF for a README (`ffmpeg ... fps=10,scale=640:-1` with a palette).
- A 9:16 crop for shorts and reels if needed.

> **Example (HOLD STILL):** 26.5 s, five shots (robot head reveal, a robot walking past the
> hiding player, walking among powered-down robots, a run that makes a robot turn, an extreme
> close-up "I see you"), captions "THE MACHINES WON" / "THEY HUNT FOR YOUR MIND" /
> "STAY SILENT. STAY HIDDEN." / "RUN... AND THEY HEAR YOU", then the title. Five voice lines
> carry it: the scientist's tape ("Don't run when they come. Hold still."), the factory PA, a
> child counting to one hundred, and the robot's "I see you" and "Hold still". The first mix had
> the voices buried 25-30 dB under the ambience; voice cues + ducking fixed it. Watch it in this
> repo's README.
