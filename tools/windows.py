"""windows.py: which text box each script id is drawn in, and that box's budget (docs/re/windows.md).

    python -X utf8 tools/windows.py            per box: entries, budget, measured or guess
    box(block, entry) -> name;  BOXES[name] = (px per line, lines, state)

State "measured" = read off a marker-build shot (windows.md names it); "guess" = not seen in game yet: the lint
warns, and a line that runs long against a guess means measure it, not abbreviate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import insert  # noqa: E402

BOXES = {
    "dialog": (203, 3, "measured"),      # portrait + message box: board, save/load, weapon list, game over
    "story": (196, 3, "measured"),       # ovl033 story scenes (prologue/epilogue, typewriter)
    "char_desc": (211, 3, "measured"),   # char select description bubble
    "card": (168, 6, "measured"),        # scenario card: win/lose conditions
    "card_title": (176, 1, "measured"),  # centred headings on the card (勝利条件 / 敗北条件)
    "list_name": (116, 1, "measured"),   # card names in the shop/hand list (number column at x=141)
    "scenario_intro": (168, 3, "guess"),
    "scenario_title": (176, 1, "guess"),
    "ending": (203, 12, "guess"),
    "square": (116, 1, "guess"),
    "facility": (116, 1, "guess"),
    "area": (116, 1, "guess"),
    "menu": (116, 1, "guess"),
}
# EXE fixed tables (no per-entry refs): card names
LIST_TABLES = [(0x80011248, 0x80011248 + 57 * 26), (0x80011814, 0x80011814 + 50 * 20)]
CARD_TITLES = {"ovl029_800A019C", "ovl029_800A01B8"}   # centred by hand: 5 leading U+3000 (12 px each)


def box(block, e):
    name = block["block"]
    if name.startswith("pc"):
        return "dialog"
    if name == "profiles":
        return "char_desc"
    if name == "scenarios":
        o = int(e["at"], 16) % 0x920
        return ("scenario_title" if o < 0x1E else "scenario_intro" if o < 0x8A else "card" if o < 0x194
                else "area")
    for k in ("ending", "square", "facilit", "area"):
        if name.startswith(k):
            return {"facilit": "facility"}.get(k, k)
    if name == "ovl033" or name.startswith("ovl03") and name >= "ovl038" or name.startswith("ovl04"):
        return "story"
    if e["id"] in CARD_TITLES:
        return "card_title"
    if name == "exe" and any(lo <= int(e["at"], 16) < hi for lo, hi in LIST_TABLES):
        return "list_name"
    return "dialog"


def budget(block, e):
    return BOXES[box(block, e)]


if __name__ == "__main__":
    from collections import Counter
    c = Counter(box(b, e) for b in insert.blocks() for e in b["strings"])
    for k, (px, lines, state) in BOXES.items():
        print("%-15s %5d entries  %3d px x %2d  %s" % (k, c[k], px, lines, state))
