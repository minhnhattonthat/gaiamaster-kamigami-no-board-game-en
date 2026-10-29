"""The debug warp's scene list must only name scenes warp.lua defines (regen.py runs them in the emulator)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scene_list_matches_warp():
    lua = (ROOT / "tools/debug/warp.lua").read_text(encoding="utf-8")
    table = lua[lua.index("local SCENES = {"):]
    table = table[:table.index("\n}\n")]
    defined = set(re.findall(r"^  (\w+) = ", table, re.M))
    names = []
    for ln in (ROOT / "tools/debug/scenes.txt").read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            name, vars_, _ = (c.strip() for c in ln.split("|", 2))
            names.append(name)
            scene = re.search(r"SCENE='(\w+)'", vars_)
            assert scene, f"{name}: no SCENE var"
            assert scene.group(1) in defined, f"{name}: warp.lua has no scene {scene.group(1)}"
    assert len(names) == len(set(names)), "duplicate state names in scenes.txt"
