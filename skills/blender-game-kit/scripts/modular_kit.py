"""A small, working modular kit: wall, wall with doorway, floor tile, ceiling tile, step.

Run headless:   blender -b --factory-startup -P modular_kit.py -- out/Kit.fbx
or paste into Blender's Text Editor and press Run.

Every module is ONE object (parts joined) with its pivot at the floor centre, sized on the grid,
so pieces snap together in the engine on whole metres. Edit the numbers at the top to retune
the whole kit, then re-run.
"""
import bpy
import bmesh
import os
import sys

GRID_W = 4.0    # wall module width (m)
ROOM_H = 3.2    # floor to ceiling
WALL_T = 0.12   # wall thickness
TILE = 2.0      # floor / ceiling tile
DOOR_W, DOOR_H = 1.1, 2.2
STEP_RISE, STEP_RUN = 0.18, 0.30

COLORS = {"wall": (0.62, 0.64, 0.66, 1), "floor": (0.22, 0.23, 0.25, 1),
          "trim": (0.08, 0.08, 0.09, 1), "ceiling": (0.80, 0.80, 0.78, 1),
          "hazard": (0.85, 0.62, 0.05, 1)}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def material(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = COLORS.get(name, (0.5, 0.5, 0.5, 1))
    bsdf.inputs["Roughness"].default_value = 0.7
    return m


def box(name, size, loc, mat):
    """Axis-aligned box: size (x, y, z) in metres, loc = centre."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(material(mat))
    return ob


def join(name, parts):
    """Join parts into one object (one draw call per module), pivot stays at the origin."""
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = ob.data.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=1.0)           # world-scale UVs: textures tile per metre
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob


def build_wall(x):
    h = ROOM_H
    parts = [box("w", (GRID_W, WALL_T, h - 0.15), (0, 0, 0.15 + (h - 0.15) / 2), "wall"),
             box("skirt", (GRID_W, WALL_T + 0.02, 0.15), (0, 0, 0.075), "trim")]
    ob = join("MOD_Wall", parts)
    ob.location.x = x
    return ob


def build_doorway(x):
    side = (GRID_W - DOOR_W) / 2
    h = ROOM_H
    parts = []
    for s in (-1, 1):
        parts.append(box("w", (side, WALL_T, h), (s * (DOOR_W / 2 + side / 2), 0, h / 2), "wall"))
        parts.append(box("jamb", (0.06, WALL_T + 0.04, DOOR_H), (s * (DOOR_W / 2 + 0.03), 0, DOOR_H / 2), "trim"))
    parts.append(box("lintel", (DOOR_W, WALL_T, h - DOOR_H), (0, 0, DOOR_H + (h - DOOR_H) / 2), "wall"))
    parts.append(box("head", (DOOR_W + 0.12, WALL_T + 0.04, 0.06), (0, 0, DOOR_H + 0.03), "trim"))
    ob = join("MOD_Wall_Door", parts)
    ob.location.x = x
    return ob


def build_floor(x, hazard=False):
    parts = [box("slab", (TILE, TILE, 0.1), (0, 0, -0.05), "floor")]
    if hazard:
        parts.append(box("stripe", (TILE, 0.1, 0.004), (0, -TILE / 2 + 0.15, 0.002), "hazard"))
    ob = join("MOD_Floor_Hazard" if hazard else "MOD_Floor", parts)
    ob.location.x = x
    return ob


def build_ceiling(x):
    ob = join("MOD_Ceiling", [box("tile", (TILE, TILE, 0.04), (0, 0, ROOM_H + 0.02), "ceiling")])
    ob.location.x = x
    return ob


def build_steps(x, count=6):
    parts = [box("step", (1.2, STEP_RUN, STEP_RISE * (i + 1)),
                 (0, i * STEP_RUN + STEP_RUN / 2, STEP_RISE * (i + 1) / 2), "floor") for i in range(count)]
    ob = join("MOD_Steps", parts)
    ob.location.x = x
    return ob


def report(objs):
    for ob in objs:
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        d = ob.dimensions
        print("[kit] %-18s %5d tris  %.2f x %.2f x %.2f m  %d mats" % (ob.name, tris, d.x, d.y, d.z, len(ob.data.materials)))


def export(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    for ob in bpy.data.objects:
        ob.location.x = 0          # every module at the origin: pivots line up in the engine
        ob.select_set(ob.type == 'MESH')
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                             apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             mesh_smooth_type='FACE', use_tspace=True, path_mode='STRIP')
    print("[kit] exported", path)


if __name__ == "__main__":
    out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.join(os.getcwd(), "Kit.fbx")
    reset()
    built = [build_wall(0), build_doorway(5), build_floor(10), build_floor(13, hazard=True),
             build_ceiling(16), build_steps(19)]
    report(built)
    export(out)
