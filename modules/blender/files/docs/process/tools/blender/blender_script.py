"""<What this script makes, in one line.>

    "$BLENDER" -b --factory-startup --python-exit-code 1 -P <path>/<this script>.py -- --out <folder> [--seed N]

Template from the scaffold's blender module (docs/process/modules/blender.md, "Rules"). Copy it for a new script and
fill in build(); the copy is the project's own. What the template keeps:

- headless only: it refuses to run inside an open Blender, so it never touches the user's scene;
- the Blender version the project's scripts are written for, checked before anything runs;
- the add-ons it needs, enabled by itself (--factory-startup loads only Blender's defaults);
- seeded randomness, so the same arguments give the same result;
- on failure: the scene saved to <out>/_failed.blend for inspection, and a non-zero exit code.
"""
import argparse
import os
import random
import sys

# Blender's bundled Python does not see the repository: the scripts' folder is added so shared modules import.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import addon_utils
import bpy

EXPECTED_BLENDER = (5, 2)  # major, minor the project's scripts are written for (docs/WORKING.md)
REQUIRED_ADDONS = []  # module names, e.g. ["io_scene_fbx"]; check with addon_utils.modules()


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
    parser.add_argument("--out", required=True, help="folder the outputs are written to")
    parser.add_argument("--seed", type=int, default=1, help="seed of every random choice")
    return parser.parse_args(argv)


def check_environment() -> None:
    if not bpy.app.background:
        raise SystemExit("run headless (blender -b ...): this script must not touch an open scene")
    if tuple(bpy.app.version[:2]) != EXPECTED_BLENDER:
        raise SystemExit(f"Blender {EXPECTED_BLENDER[0]}.{EXPECTED_BLENDER[1]} expected, "
                         f"this is {bpy.app.version_string}")
    for module in REQUIRED_ADDONS:
        loaded, _enabled = addon_utils.check(module)
        if not loaded and addon_utils.enable(module, default_set=False) is None:
            raise SystemExit(f"add-on {module} could not be enabled")


def empty_scene() -> None:
    """Removes the factory scene's objects and the data they leave behind."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def build(rng: random.Random, args: argparse.Namespace) -> None:
    """Makes the output. Prefer bmesh and the data API to bpy.ops: operators depend on selection and context."""
    raise NotImplementedError("fill in build()")


def main() -> None:
    args = parse_args()
    check_environment()
    os.makedirs(args.out, exist_ok=True)
    empty_scene()
    try:
        build(random.Random(args.seed), args)
    except Exception:
        debug = os.path.join(os.path.abspath(args.out), "_failed.blend")
        bpy.ops.wm.save_as_mainfile(filepath=debug, copy=True)
        print(f"[{os.path.basename(__file__)}] failed; the scene is saved to {debug}", file=sys.stderr)
        raise


main()
