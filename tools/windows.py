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
    "map_info": (87, 5, "measured"),     # board square panel (command menu / map info): square name + 4 lines
    "credits": (296, 1, "measured"),     # ovl033 staff roll, each line centred on x=157
    "scenario_title": (9999, 1, "measured"),  # never printed: no drawer reads it (tools/debug/scenread.lua); banner = G13
    "ending": (203, 3, "measured"),      # SCR_DATA 122 per-rank fates: the dialog box, 3 lines (ovl057, game end)
    "facility": (87, 1, "measured"),     # via %s in the map_info line "施設    %s": label + name share 87 px
    "area": (80, 1, "measured"),         # area selector: 120 minus "Area " (29), space (4), letter A-G (7)
    "area_row": (120, 1, "measured"),   # x24..143 incl., before the right frame; mode 10 has an A-G suffix
    "results_col": (36, 1, "measured"),  # ovl057 row labels (お店 土地数 資産...) of the board status table, x 141
    "unreachable": (9999, 1, "measured"),  # no code path prints it (UNREACHABLE): no width budget
}
# strings the game never prints. ovl052 leader tip (0x800C8FF0..): the tie count s5 is only ever set to 0
# (0x800C9038, 0x800C9044), so only the 1-leader line 800C874C shows; the 2/3/4-way lines are dead code.
UNREACHABLE = {"ovl052_800C8768", "ovl052_800C8780", "ovl052_800C8790", "ovl052_800C87A8"}
# EXE fixed tables (no per-entry refs): card names
LIST_TABLES = [(0x80011248, 0x80011248 + 57 * 26), (0x80011814, 0x80011814 + 50 * 20)]
CARD_TITLES = {"ovl029_800A019C", "ovl029_800A01B8"}   # centred by hand: 5 leading U+3000 (12 px each)
MAP_INFO = (0x800A13BC, 0x800A1620)    # ovl008 square panel lines (status / facility / owner / toll / value)
CREDITS = (0x800A3D00, 0x800A4540)     # ovl033 staff roll


def box(block, e):
    name = block["block"]
    if e["id"] in {"ovl008_800A0330", "ovl008_800A033C"}:
        return "area_row"
    if e["id"] in UNREACHABLE:
        return "unreachable"
    if name.startswith("pc"):
        return "dialog"
    if name == "profiles":
        return "char_desc"
    if name == "scenarios":
        o = int(e["at"], 16) % 0x920
        return ("scenario_title" if o < 0x1E else "dialog" if o < 0x8A else "card" if o < 0x194
                else "area")   # intro: the guide's portrait box on the world map (2T1, story_ch01 f008312)
    if name.startswith("square"):
        return "map_info"
    for k in ("ending", "facilit", "area"):
        if name.startswith(k):
            return {"facilit": "facility"}.get(k, k)
    if name == "ovl008" and MAP_INFO[0] <= int(e["at"], 16) < MAP_INFO[1]:
        return "map_info"
    if name == "ovl033" and CREDITS[0] <= int(e["at"], 16) < CREDITS[1]:
        return "credits"
    if name == "ovl057" and int(e["at"], 16) < 0x8009FA00:
        return "results_col"
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
