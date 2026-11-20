"""Download free CC0 models and textures from Poly Haven, with a licence record for each.

  python polyhaven_fetch.py search chair                 # list matching models + textures
  python polyhaven_fetch.py model metal_toolbox 1k out/  # FBX + its textures + SOURCE.txt
  python polyhaven_fetch.py texture garage_floor 2k out/ # diffuse, GL normal, rough, metal, AO

Everything on Poly Haven is CC0 (public domain): free for commercial games, no credit required
(crediting the artists is good practice). A SOURCE.txt is written next to each download so your
licence ledger can be filled in. Standard library only.
"""
import json
import os
import sys
import urllib.request

API = "https://api.polyhaven.com"
UA = {"User-Agent": "gamedev-pipeline-skill/1.0"}   # Poly Haven asks API users to send a User-Agent
TEXTURE_MAPS = ["Diffuse", "nor_gl", "Rough", "Metal", "AO"]   # nor_gl = OpenGL normal (Unity convention)


def get_json(path):
    with urllib.request.urlopen(urllib.request.Request(API + path, headers=UA), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        return
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(dest, "wb") as f:
        f.write(r.read())
    print("  got", dest)


def write_source(asset_id, out):
    info = get_json("/info/" + asset_id)
    authors = ", ".join(info.get("authors", {}).keys())
    text = ("Asset: %s\nSource: https://polyhaven.com/a/%s\nAuthor(s): %s\nLicence: CC0 1.0 (public domain)\n"
            "Original polycount: %s\n" % (info.get("name", asset_id), asset_id, authors, info.get("polycount", "n/a")))
    with open(os.path.join(out, "SOURCE.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text.strip())


def search(term):
    term = term.lower()
    for kind in ("models", "textures", "hdris"):
        assets = get_json("/assets?t=" + kind)
        hits = [(k, v) for k, v in assets.items()
                if term in k.lower() or term in v.get("name", "").lower()
                or any(term in t.lower() for t in v.get("tags", []) + v.get("categories", []))]
        print("== %s (%d)" % (kind, len(hits)))
        for k, v in sorted(hits)[:40]:
            extra = (" %s tris" % v["polycount"]) if "polycount" in v else ""
            print("  %-36s %s%s" % (k, v.get("name", ""), extra))


def model(asset_id, res, out_root):
    files = get_json("/files/" + asset_id)
    fbx = files["fbx"][res]["fbx"]
    out = os.path.join(out_root, asset_id)
    download(fbx["url"], os.path.join(out, os.path.basename(fbx["url"])))
    for rel, f in fbx.get("include", {}).items():     # the textures the FBX references
        download(f["url"], os.path.join(out, rel))
    write_source(asset_id, out)


def texture(asset_id, res, out_root):
    files = get_json("/files/" + asset_id)
    out = os.path.join(out_root, asset_id)
    for m in TEXTURE_MAPS:
        if m in files and res in files[m]:
            fmts = files[m][res]
            f = fmts.get("png") or fmts.get("jpg") or next(iter(fmts.values()))
            download(f["url"], os.path.join(out, os.path.basename(f["url"])))
    write_source(asset_id, out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "search":
        search(a[1])
    elif len(a) >= 2 and a[0] in ("model", "texture"):
        res = a[2] if len(a) > 2 else ("1k" if a[0] == "model" else "2k")
        out = a[3] if len(a) > 3 else "polyhaven"
        (model if a[0] == "model" else texture)(a[1], res, out)
    else:
        print(__doc__)
