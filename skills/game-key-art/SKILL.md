---
name: game-key-art
description: Create the images that sell a game - app/game icon, key art / cover / banner, and captioned screenshots from real gameplay - using genre research, image-model prompts built on the game's own frames, and a script that adds consistent caption banners. Use whenever the user wants an icon, logo, cover art, key art, banner, thumbnail, capsule image, store or itch.io screenshots, "make my screenshots look professional", or prompts for ChatGPT / an image model about their game.
---

# Game key art, icon and screenshots

## 1. Research the genre first (10 minutes, saves hours)

Open the store pages of 10 successful games in the same genre and write down, for each:
icon subject, background, accent colour, text or not; cover composition; screenshot caption
style. Patterns repeat inside a genre, and players read them instantly.

Patterns that hold across most genres:
- **Icon:** one subject, close-up (the hero, the villain's face, one object), very dark or very
  clean background, ONE bright accent colour, no small text, readable at 48 px.
- **Key art / cover:** the threat or hero large on one side, the player character smaller on
  the other, empty space for the logo, cinematic light. It should look like a film poster.
- **Screenshots:** real gameplay, strongest moment first, a short caption banner on each
  (2-5 words), the same frame style on all of them.

## 2. Image-model prompts built on real frames

Generated art must match the game, or players feel cheated. Start from the game's own frames:

1. Capture clean 1920x1080 frames of the hero, the enemy and the place (no HUD).
2. Give the image model one frame plus a prompt (templates in `references/prompts.md`):
   subject, composition, lighting, palette, "no text, no logo, no watermark".
3. Generate 4-8, pick the best, then fix details by editing that image, not by re-rolling.
4. Add the title yourself in the game's font (image models still mangle lettering).
5. Many stores now ask you to **declare AI-generated art** and label it. Say so honestly;
   screenshots must always be real gameplay.

## 3. Captioned screenshots (`scripts/caption_screenshots.py`)

```bash
python scripts/caption_screenshots.py shots/ out/ captions.txt --font Fonts/Title.ttf --accent "#D8261E"
```

`captions.txt` has one caption per screenshot, in file order. The script letterboxes each
frame into the target size, adds a dark banner with the caption centred, a thin accent line,
and saves PNG and JPG versions. One look across all of them.

## 4. Sizes worth exporting

| Asset | Size |
|---|---|
| Icon master | 1024x1024 PNG (export 512 / 256 / 128 from it) |
| Wide banner / feature | 1024x500 and 1920x1080 |
| Social preview (GitHub, link cards) | 1280x640 |
| Screenshots | 1920x1080 (16:9), 5-8 of them |
| Capsule / thumbnail | 1280x720 |

Keep important content away from the edges: stores crop and overlay buttons.

> **Example (HOLD STILL):** icon = a terrified scientist in the foreground, a robot's red
> optic behind her, a burning city of robots in the background (the story in one square);
> banner = the same scene wide with the title in the left third; 8 screenshots with captions
> like "HIDE. HOLD YOUR BREATH." and "EVERY ROBOT SENSES DIFFERENTLY". See this repo's README.
