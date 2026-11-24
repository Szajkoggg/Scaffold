"""Renders review pictures of a model from fixed views, headless.

    "$BLENDER" -b --factory-startup --python-exit-code 1 -P docs/process/tools/blender/render_preview.py --
        --input <model.blend|.fbx|.glb|.gltf|.obj> --out <folder> [--views front,three-quarter,top,side]
        [--size 1024] [--engine workbench|eevee]

Template from the scaffold's blender module (docs/process/modules/blender.md, "Review"); a project may copy and adapt
it. Writes <out>/<input name>@<view>.png: the view key is the file name (visual-review). The camera frames the
model's bounding box from the same angles every time, so a before and an after of the same view are comparable.
Workbench (default) shows shape and colour quickly and the same on every machine; EEVEE shows materials and needs
the GPU.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

VIEWS = {  # name: (azimuth degrees around Z, elevation degrees above the ground)
    "front": (0, 5),
    "three-quarter": (35, 25),
    "side": (90, 5),
    "top": (0, 89),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(prog="render_preview.py")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--views", default="front,three-quarter,top")
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--engine", choices=["workbench", "eevee"], default="workbench")
    return parser.parse_args(argv)


def empty_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def load(path: str) -> None:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.objects = list(src.objects)
        for obj in dst.objects:
            if obj is not None:
                bpy.context.scene.collection.objects.link(obj)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    else:
        raise SystemExit(f"unsupported input: {path}")
    if not any(o.type == "MESH" for o in bpy.context.scene.objects):
        raise SystemExit(f"no mesh in {path}")


def bounds() -> tuple:
    # Objects just loaded have stale world matrices until the view layer updates: without this, every object
    # counts as if it stood at its first object's place and the framing misses the rest.
    bpy.context.view_layer.update()
    points = [o.matrix_world @ Vector(c) for o in bpy.context.scene.objects if o.type == "MESH" for c in o.bound_box]
    low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return (low + high) / 2, max((high - low).length / 2, 1e-3)


def set_engine(name: str) -> None:
    # Engine identifiers change between Blender versions: try the candidates instead of hard-coding one.
    candidates = ["BLENDER_WORKBENCH"] if name == "workbench" else ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"]
    for identifier in candidates:
        try:
            bpy.context.scene.render.engine = identifier
            return
        except TypeError:
            continue
    raise SystemExit(f"no render engine for {name} in Blender {bpy.app.version_string}")


def setup(size: int, engine: str) -> bpy.types.Object:
    scene = bpy.context.scene
    set_engine(engine)
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.image_settings.file_format = "PNG"
    if engine == "workbench":
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
    sun = bpy.data.objects.new("PreviewSun", bpy.data.lights.new("PreviewSun", "SUN"))
    sun.rotation_euler = (math.radians(50), 0, math.radians(-40))
    scene.collection.objects.link(sun)
    camera = bpy.data.objects.new("PreviewCamera", bpy.data.cameras.new("PreviewCamera"))
    camera.data.lens = 50
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera


def aim(camera: bpy.types.Object, centre: Vector, radius: float, azimuth: float, elevation: float) -> None:
    fov = camera.data.angle
    distance = radius / math.sin(fov / 2) * 1.1
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    camera.location = centre + direction * distance
    camera.rotation_euler = (centre - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.clip_end = distance + radius * 4


def main() -> None:
    args = parse_args()
    views = [v.strip() for v in args.views.split(",") if v.strip()]
    unknown = [v for v in views if v not in VIEWS]
    if unknown:
        raise SystemExit(f"unknown views {unknown}; known: {', '.join(VIEWS)}")
    empty_scene()
    load(os.path.abspath(args.input))
    camera = setup(args.size, args.engine)
    centre, radius = bounds()
    os.makedirs(args.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.input))[0]
    for view in views:
        aim(camera, centre, radius, *VIEWS[view])
        path = os.path.join(os.path.abspath(args.out), f"{stem}@{view}.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print(f"[render_preview] {path}")


main()
