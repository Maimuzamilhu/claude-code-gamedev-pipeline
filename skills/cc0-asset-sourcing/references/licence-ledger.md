# Licence ledger template

Keep this as `Docs/ASSET_LICENSES.md` in the game project. One row per shipped file (or folder of
files from one source). Add the row the moment the file enters the project.

```markdown
# Third-party assets

| Shipped file | Derived from | Author | Licence | Added |
|---|---|---|---|---|
| `Assets/Art/Props/metal_toolbox/` (decimated to 500 tris, textures repacked for URP) | Metal Toolbox - https://polyhaven.com/a/metal_toolbox | Mateusz Sadek | CC0 1.0 | 2026-11-14 |
| `Assets/Fonts/Rajdhani-Bold.ttf` | https://github.com/google/fonts/tree/main/ofl/rajdhani (licence file beside it) | Indian Type Foundry | SIL OFL 1.1 | 2026-11-13 |
| `Assets/Audio/Steps/step_wood_*.wav` | "Footsteps on different surfaces", https://opengameart.org/... | congusbongus | **CC-BY 3.0: credit required** | 2026-11-14 |

**Credits screen must include:** (one line per CC-BY source, exactly as the author asks)
```

## Licence cheat sheet

| Licence | Commercial game | Credit | Notes |
|---|---|---|---|
| CC0 / public domain | yes | not required (nice to do) | safest |
| MIT, Apache 2.0 | yes | keep the licence text with the files | code and some art |
| CC-BY 3.0 / 4.0 | yes | **required**, in credits | write the line the day you add the file |
| SIL OFL (fonts) | yes | ship the licence file | do not sell the font on its own |
| CC-BY-SA | yes, but your derived asset must be shared alike | required | think before using |
| CC-BY-NC, CC-ND | **no** for a paid or ad-supported game | - | avoid |
| GPL (art packs) | risky in a closed game | - | avoid |
| "Free for personal use" | **no** | - | avoid |
