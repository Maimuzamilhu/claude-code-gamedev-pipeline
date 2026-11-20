---
name: cc0-asset-sourcing
description: Find, download and prepare free assets that are safe to use in a commercial game - CC0 models, PBR textures and HDRIs from Poly Haven and ambientCG, characters and animations, fonts - cut them to a game triangle budget, repack textures for Unity URP, and keep a licence ledger. Use whenever the user needs props, textures, materials, characters, fonts or "free assets", asks "can I use this in my game", says "Poly Haven", "CC0", "licence", or the game looks flat and needs realistic surfaces.
---

# Free CC0 assets, game-ready

Realistic look on a zero budget comes from **scanned CC0 assets** (public domain: free for
commercial use, no credit required), cut down to game budgets. This works for any setting:
medieval, sci-fi, modern, fantasy.

## Where to get what

| Need | Source | Licence |
|---|---|---|
| Props, furniture, tools (scanned) | Poly Haven (polyhaven.com) | CC0 |
| PBR textures (walls, floors, metal, ground) | Poly Haven, ambientCG (ambientcg.com) | CC0 |
| HDRI skies for lighting | Poly Haven | CC0 |
| Low-poly / stylised packs, characters, animations | Quaternius, Kenney | CC0 |
| Realistic human characters | Microsoft Rocketbox (GitHub) | MIT |
| Fonts | Google Fonts | SIL OFL (ship the licence file) |
| Anything else | Sketchfab (filter: Downloadable + CC0 / CC-BY) | per model |

Avoid "NonCommercial", "NoDerivatives" and GPL assets in a game you may sell. Open the licence
page and save a copy before using any file.

## Workflow

1. **Search** the catalogue by keyword (`scripts/polyhaven_fetch.py search <word>`), or with the
   Blender MCP add-on's asset search.
2. **Download** at 1K for props, 2K for big surfaces
   (`polyhaven_fetch.py model <id> 1k out/`, `texture <id> 2k out/`). The script writes a
   `SOURCE.txt` with name, URL, authors and licence for every asset.
3. **Cut to budget** in Blender and **repack textures** for URP Lit
   (`scripts/blender_prep_for_unity.py`): decimate to a triangle target, write
   `_Albedo`, `_Normal` (OpenGL, as Unity expects) and `_MetalSmooth`
   (R = metallic, A = 1 - roughness), export FBX with Unity axes plus a `materials.json`.
4. **Bind materials** in Unity with a small editor script that reads `materials.json`.
5. **Ledger**: add one row per file to `Docs/ASSET_LICENSES.md`
   (template in `references/licence-ledger.md`). For CC-BY, add the credit line to the in-game
   credits screen the same day, not at the end.

## Budgets

Scanned models are made for film (4,000 to 45,000 triangles). Typical game targets:
small prop <= 800, medium 1,500-3,000, hero prop <= 8,000. Textures: use the normal map and
roughness; they carry most of the realism.

## Common mistakes

- **DirectX vs OpenGL normals.** Unity wants OpenGL (`nor_gl`). The wrong one makes bumps look
  inverted under light.
- **Colour space.** Albedo is sRGB; normal, roughness, metallic and masks are linear
  ("Non-Color" in Blender, sRGB unticked in Unity).
- **Everything 4K.** It looks the same at game distance and costs memory. 1K-2K is enough.
- **No ledger.** Months later nobody remembers where a file came from.

> **Example (HOLD STILL):** 25 Poly Haven props (power boxes, pipes, shelves, extinguishers,
> microscope, sofa, kettle) decimated to 300-6,000 tris each; 8 Poly Haven wall and floor
> materials at 2K; a Rocketbox character (MIT) as the hero; Quaternius animation libraries
> (CC0); Rajdhani and Barlow fonts (OFL). Every file has a row in the ledger.
