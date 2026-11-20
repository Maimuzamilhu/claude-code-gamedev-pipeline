---
name: blender-game-kit
description: Build game-ready models from Python in Blender for any game - modular level kits (walls, floors, doorways, stairs, platforms, ceilings), props and simple characters - bake procedural materials to textures, make cheap LOD copies and export FBX that drops straight into Unity or another engine. Use whenever the user wants 3D models or levels from Blender, says "Blender MCP", "make a modular kit", "model a room/dungeon/house/corridor/props", "export to Unity", "too many triangles", or wants art they can regenerate from code instead of modelling by hand.
---

# Blender game kit (models from code)

Build the game's world from Python scripts run in Blender. A dungeon, a house, a space
station, a city block: it is all modules on a grid plus props. A change is an edit and a
re-run, never hours of re-modelling.

> **Example (HOLD STILL):** the whole two-floor factory (walls, floors, doors, stairs, lab
> furniture, robots, debris) came from about 20 Blender scripts.

## How the agent runs Blender

- **Live Blender (Blender MCP add-on):** run Python in the user's open Blender, look at the
  viewport, search and import Poly Haven / Sketchfab assets. Best for exploring and checking looks.
- **Headless (for the real export):** `blender -b --factory-startup -P build_kit.py`. Same
  result every run, no UI state leaking in. Use this for anything the game ships.

Look shader nodes up by **type**, never by name (names are translated in other UI languages):
`next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")`.

## The grid is the design

Pick the module sizes first and never break them. Match them to your character: doors a bit
wider and taller than the player capsule, steps lower than its step height. A good start for a
human-sized character (these are HOLD STILL's numbers):

| Piece | Size |
|---|---|
| Wall module | 4.0 m wide, 0.12 m thick |
| Floor to ceiling | 3.2 m |
| Floor tile | 2.0 m |
| Door opening | 1.1 m by 2.2 m |
| Stair step | 0.18 m rise (keep under the character's step height) |

Pivot at the module's floor-centre so pieces snap on whole metres in Unity.

## Workflow

1. **Helpers first**: `box()`, `cyl()`, `assign(material)`, `finish()` (apply transforms, smooth
   by angle, UVs). See `scripts/modular_kit.py`, a small working kit to start from.
2. **One function per module** (`build_wall`, `build_floor`, `build_doorway`). Parameters for
   variants (with or without drain, hazard stripe, window).
3. **One mesh per module, many material slots.** Join the parts. Each module becomes one object
   and one texture set: fewer draw calls.
4. **Bake** procedural materials (noise, grime, bump) to `BaseColor`, `Normal`, `MetalSmooth`
   (R = metallic, A = smoothness) and `Emission`. Procedural nodes do not survive FBX export;
   without baking, Unity only sees flat colours.
5. **Export FBX** with Unity's axes:
   `axis_forward='-Z', axis_up='Y', apply_scale_options='FBX_SCALE_ALL', use_tspace=True,
   mesh_smooth_type='FACE', path_mode='STRIP'`.
6. **Write a validation file** after export: per module, triangle count, bounds, material
   count. Compare it with the previous run so regressions show up as numbers.

## Triangle budgets (what mattered)

- Count where the triangles go before optimising. Example: in HOLD STILL, three ceiling tiles were
  38.6% of all triangles in the scene because of 2 mm bevels nobody can see from 2 m below.
  A planar decimate (dissolve near-coplanar faces, 50 degrees, delimited by UV seams and
  material) cut them hard with no visible change. See `references/budgets.md`.
- Small bevels are for close-up hero props, not repeated modules.
- Make `_Lite` copies for far or repeated pieces instead of editing the source kit.

## Hand-off to Unity

- Import settings: generate colliders only on the pieces the player touches; use simple box
  colliders for the rest.
- Bind the baked textures to a URP Lit material per module by name (a small editor script that
  reads a `materials.json` written next to the FBX).
- Keep the `.blend` and the scripts in version control. The FBX is a build product.
