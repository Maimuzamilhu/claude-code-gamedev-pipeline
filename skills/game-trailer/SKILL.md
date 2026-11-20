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

- Bed: 1-2 ambience loops from the game under everything.
- Hits: a stinger or impact on the reveal and on the title.
- Voice: one or two lines from the game's characters (see `ai-voice-lines`).
- Body: heartbeat or breathing for tension games, crowd or music for others.
- Fade in 0.8 s, fade out 1.2 s, limiter at -1 dB so it is loud but not clipped.

## 5. Export variants

- 16:9 1920x1080 MP4 for YouTube and store pages.
- A 5-second GIF for a README (`ffmpeg ... fps=10,scale=640:-1` with a palette).
- A 9:16 crop for shorts and reels if needed.

> **Example (HOLD STILL):** 26.5 s, five shots (robot head reveal, a robot walking past the
> hiding player, walking among powered-down robots, a run that makes a robot turn, an extreme
> close-up "I see you"), captions "THE MACHINES WON" / "THEY HUNT FOR YOUR MIND" /
> "STAY SILENT. STAY HIDDEN." / "RUN... AND THEY HEAR YOU", then the title. The mix is
> 16 cues taken straight from the game's audio folder. Watch it in this repo's README.
