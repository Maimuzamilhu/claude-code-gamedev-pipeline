# Prompt templates

Replace the brackets. Attach one real frame of the game when the model accepts an image, and
say "keep the character / enemy design from the attached image".

## Icon (generate 1024x1024)

```
Mobile/PC game icon, square, no text, no letters, no border. [ONE SUBJECT: e.g. extreme close-up
of the villain's face / the hero holding the key item], [EMOTION: terrified / determined],
[BACKGROUND: dark, blurred, hinting the world: e.g. a burning city, a haunted forest],
one bright [ACCENT COLOUR] accent, high contrast, cinematic rim light, highly detailed,
readable at small size, professional top-selling [GENRE] game icon style.
```

## Key art / banner (generate wide, crop to 1024x500 or 1920x1080)

```
Wide cinematic key art for a [GENRE] game, 2:1 landscape. [PLACE + TIME + LIGHT].
On the right, [THE THREAT / HERO] large and menacing, [DETAIL]. On the left, small in the frame,
[THE PLAYER CHARACTER] [ACTION]. Large empty dark area in the upper-left third for a title
(do not write any text). Photorealistic / [STYLE], moody, volumetric haze, film grain,
high contrast, AAA game poster, no text, no logo, no watermark.
```

## Screenshot polish (only colour and frame, never fake content)

```
Keep this exact game screenshot content and composition. Improve only colour grading:
slightly higher contrast, deeper blacks, [COLD BLUE / WARM] tint, subtle vignette.
Do not add, remove or change any object, character or text.
```

## Fixing a near-miss

Edit the chosen image instead of re-rolling: "Same image. Make the [eye] glow brighter,
remove the extra finger, keep everything else identical."
