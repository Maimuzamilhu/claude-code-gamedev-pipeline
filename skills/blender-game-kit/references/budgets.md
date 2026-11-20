# Triangle and texture budgets that worked

Starting budgets for a 3D game that must run smoothly on modest hardware. They come from HOLD
STILL (a two-floor building, 4 robots, about 1,000 placed modules); stylised or top-down games
can usually go lower. Treat them as a starting point and measure your own scene.

| Thing | Budget |
|---|---|
| Repeated wall / floor / ceiling module | 50 - 600 tris |
| Small prop (stool, clipboard, container) | <= 800 tris |
| Medium prop (shelf, power box, aircon) | 1,500 - 3,000 tris |
| Hero prop (forklift, machine, sofa) | <= 8,000 tris |
| Enemy robot | 8,000 - 15,000 tris |
| Whole visible frame | aim for under ~300k tris |
| Texture size | 1K for props, 2K for big wall/floor materials |

## Find the waste first

```python
# in Blender: triangles per object, biggest first
rows = []
for o in bpy.data.objects:
    if o.type == 'MESH':
        rows.append((sum(len(p.vertices) - 2 for p in o.data.polygons), o.name))
for t, n in sorted(rows, reverse=True)[:20]:
    print(t, n)
```

In the engine, multiply each module's triangles by how many times it is placed. A 7,000-triangle
ceiling tile placed 222 times was 38.6% of the scene.

## Cheap fixes, in order

1. **Planar decimate** (dissolve near-coplanar faces, angle about 50 degrees, delimit by UV seam
   and material): removes invisible chamfers, keeps the silhouette and the baked UVs.
2. **Collapse decimate to a target** for scanned props (Poly Haven models are 4k-45k tris, made
   for film). `ratio = budget / current_tris`.
3. **Merge small parts** into one mesh per module.
4. **LOD / `_Lite` copies** for far-away or many-times-placed pieces.
5. Only then consider removing detail by hand.
