"""Cut a downloaded Poly Haven model to a game budget and repack its textures for Unity URP Lit.

  blender -b --factory-startup -P blender_prep_for_unity.py -- <asset_dir> <out_dir> <tri_budget>

For the asset in <asset_dir> (as written by polyhaven_fetch.py):
  - imports the FBX and decimates every mesh so the whole asset fits <tri_budget>
  - writes <mat>_Albedo (opacity merged into alpha if the asset has one),
    <mat>_Normal (OpenGL convention, which Unity expects),
    <mat>_MetalSmooth (R = metallic, A = 1 - roughness: URP's metallic/smoothness map)
  - exports <id>.fbx with Unity axes and materials.json (material name -> texture files)
    so a small editor script can bind each URP material by name
  - copies SOURCE.txt (licence record) next to the export
"""
import bpy
import glob
import json
import os
import shutil
import sys

import numpy as np


def tris(objs):
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)


def load(path):
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = 'Non-Color'     # raw values: the sRGB colour is written back unchanged
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px, w, h


def save(px, w, h, path):
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    img.colorspace_settings.name = 'Non-Color'
    img.pixels.foreach_set(np.clip(px, 0, 1).astype(np.float32).ravel())
    img.filepath_raw, img.file_format = path, 'PNG'
    img.save()
    bpy.data.images.remove(img)


def find(texdir, key, kind):
    for ext in ("png", "jpg", "exr"):
        hit = glob.glob(os.path.join(texdir, "*%s_%s_*.%s" % (key, kind, ext)))
        if hit:
            return hit[0]
    return None


def main(src, dst, budget):
    aid = os.path.basename(os.path.normpath(src))
    fbx = glob.glob(os.path.join(src, "*.fbx"))[0]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    before = tris(meshes)
    ratio = min(1.0, budget / max(1, before))
    if ratio < 0.999:
        for o in meshes:
            m = o.modifiers.new("dec", 'DECIMATE')
            m.ratio, m.use_collapse_triangulate = ratio, True
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier="dec")
    os.makedirs(dst, exist_ok=True)
    texdir = os.path.join(src, "textures")
    mapping = {}
    for mat in bpy.data.materials:
        if not mat.users:
            continue
        key = aid      # which texture prefix belongs to this material: its image nodes say
        if mat.node_tree:
            for n in mat.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image and "_diff_" in n.image.name:
                    key = n.image.name.split("_diff_")[0]
        e = {}
        d = find(texdir, key, "diff")
        if d:
            a = find(texdir, key, "alpha") or find(texdir, key, "opacity")
            if a:
                px, w, h = load(d)
                ap, aw, ah = load(a)
                if (aw, ah) == (w, h):
                    px[:, :, 3] = ap[:, :, 0]
                save(px, w, h, os.path.join(dst, key + "_Albedo.png"))
                e["albedo"] = key + "_Albedo.png"
            else:
                name = key + "_Albedo" + os.path.splitext(d)[1]
                shutil.copyfile(d, os.path.join(dst, name))
                e["albedo"] = name
        n = find(texdir, key, "nor_gl")
        if n:
            px, w, h = load(n)
            px[:, :, 3] = 1.0
            save(px, w, h, os.path.join(dst, key + "_Normal.png"))
            e["normal"] = key + "_Normal.png"
        mt, rg = find(texdir, key, "metal"), find(texdir, key, "rough")
        if mt or rg:
            _, w, h = load(rg or mt)
            ms = np.zeros((h, w, 4), dtype=np.float32)
            if mt:
                mp, mw, mh = load(mt)
                if (mw, mh) == (w, h):
                    ms[:, :, 0] = mp[:, :, 0]
            ms[:, :, 3] = (1.0 - load(rg)[0][:, :, 0]) if rg else 0.4
            save(ms, w, h, os.path.join(dst, key + "_MetalSmooth.png"))
            e["metalsmooth"] = key + "_MetalSmooth.png"
        mapping[mat.name] = e
    for o in bpy.data.objects:
        o.select_set(o.type == 'MESH')
    bpy.ops.export_scene.fbx(filepath=os.path.join(dst, aid + ".fbx"), use_selection=True,
                             object_types={'MESH'}, apply_scale_options='FBX_SCALE_ALL',
                             axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
                             use_tspace=True, path_mode='STRIP', embed_textures=False)
    with open(os.path.join(dst, "materials.json"), "w") as f:
        json.dump(mapping, f, indent=1)
    if os.path.exists(os.path.join(src, "SOURCE.txt")):
        shutil.copyfile(os.path.join(src, "SOURCE.txt"), os.path.join(dst, "SOURCE.txt"))
    print("[prep] %s: %d -> %d tris, %d materials" % (aid, before, tris(meshes), len(mapping)))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) < 3:
        print(__doc__)
    else:
        main(args[0], args[1], int(args[2]))
