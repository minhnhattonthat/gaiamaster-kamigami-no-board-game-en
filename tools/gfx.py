"""gfx.py: English lettering for the Japanese drawn as graphics (docs/re/graphics.md rows G1-G17).

    python -X utf8 tools/gfx.py [--only G2] [--out work/gfx]   -> preview PNGs (original above, English below)

Each LABELS row clears a rect of a 4/8bpp TIM (indices, not colours) and draws English in the same palette
indices with an OFL font from fonts/ (docs/fonts.md). insert.edits() merges edits(): every copy of a TIM
(docs/re/gfx_survey/index.tsv lists them) gets the same new pixels. Pixels outside the declared rects never change
(checked in edits()).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import tim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UNPACKED = ROOT / "work/unpacked"
FONTS = ROOT / "fonts"
LILITA = FONTS / "lilitaone/LilitaOne-Regular.ttf"
SILK = FONTS / "silkscreen/Silkscreen-Regular.ttf"
SILKB = FONTS / "silkscreen/Silkscreen-Bold.ttf"
PIXEL = {SILK: 8, SILKB: 8}   # pixel fonts: native size (cap height 5 px), drawn without scaling


# ---------------------------------------------------------------- pixels
def indices(t):
    b = np.frombuffer(t["pix"], np.uint8)
    if t["bpp"] == 4:
        a = np.empty(b.size * 2, np.uint8)
        a[0::2], a[1::2] = b & 15, b >> 4
    else:
        a = b.copy()
    return a[:t["w"] * t["h"]].reshape(t["h"], t["w"])


def encode(data, t, a):
    """data (the TIM bytes) with its pixel block replaced by index array a."""
    flat = a.reshape(-1).astype(np.uint8)
    pix = (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes() if t["bpp"] == 4 else flat.tobytes()
    start = t["end"] - len(t["pix"])
    assert len(pix) <= len(t["pix"])
    return data[:start] + pix + data[start + len(pix):]


def pixel_mask(text, size, w, font, track=1):
    """(bool mask, cap-top row) for a pixel font at its native size, no antialiasing; fails if wider than w."""
    f = ImageFont.truetype(str(font), size)
    hb = f.getbbox("H")
    img = Image.new("1", (w * 3, size * 3), 0)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    x = size
    for c in text:
        d.text((x, size), c, fill=1, font=f)
        x += f.getlength(c) + track
    box = img.getbbox()
    m = np.array(img.crop(box), bool)
    assert m.shape[1] <= w, f"{text!r}: {m.shape[1]} px > {w}"
    return m, size + hb[1] - box[1]


def text_mask(text, h, w, font=LILITA, shear=0.0, track=0):
    """(bool mask, cap-top row): text with cap height h px, sheared right by `shear` (italic), squeezed to fit w.
    Rendered 8x and scaled down: small thresholded renders lose stems."""
    if font in PIXEL:
        return pixel_mask(text, PIXEL[font], w, font, track)
    f = ImageFont.truetype(str(font), 160)
    hb = f.getbbox("H")
    cap = hb[3] - hb[1]
    big_w = int(sum(f.getlength(c) for c in text) + track * len(text) * cap / h) + 400
    img = Image.new("L", (big_w, 400), 0)
    d = ImageDraw.Draw(img)
    x = 100
    for c in text:
        d.text((x, 100), c, fill=255, font=f)
        x += f.getlength(c) + track * cap / h
    box = img.getbbox()
    top = 100 + hb[1] - box[1]          # cap top inside the cropped render
    img = img.crop(box)
    sh = int(round(shear * img.height))
    if sh:
        img = img.transform((img.width + sh, img.height), Image.AFFINE, (1, shear, -sh, 0, 1, 0),
                            resample=Image.BICUBIC)
    s = h / cap
    nh = max(1, round(img.height * s))
    img = img.resize((min(max(1, round(img.width * s)), w), nh), Image.LANCZOS)
    return np.array(img) >= 110, round(top * s)


def shift(m, dx, dy):
    o = np.zeros_like(m)
    h, w = m.shape
    o[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = m[max(-dy, 0):h - max(dy, 0), max(-dx, 0):w - max(dx, 0)]
    return o


def grow(m):
    return m | shift(m, 1, 0) | shift(m, -1, 0) | shift(m, 0, 1) | shift(m, 0, -1)


# ---------------------------------------------------------------- styles: (canvas, mask) -> paint in place
def shadowed(fill, edge, shadow, dx=2, dy=2):
    """Main-menu buttons: fill index, a light left edge, a drop shadow down-right."""
    def paint(c, m):
        c[shift(m, dx, dy) & ~m] = shadow
        c[m] = fill
        c[m & ~shift(m, 1, 0)] = edge
    return paint


def outlined(outline, ramp):
    """Outline index around a fill that runs through `ramp` indices from the top row of the text to the bottom."""
    def paint(c, m):
        c[grow(m) & ~m] = outline
        rows = np.nonzero(m.any(1))[0]
        if not rows.size:
            return
        y0, y1 = rows[0], rows[-1]
        for y in range(y0, y1 + 1):
            c[y][m[y]] = ramp[min(len(ramp) - 1, (y - y0) * len(ramp) // (y1 - y0 + 1))]
    return paint


# ---------------------------------------------------------------- labels
# rect = (x, y, w, h) cleared to the background index bg (per row: the rect's left column when bg is None);
# text drawn with cap height th, left-aligned at x + pad (or centred when centre=True), vertically centred.
def L(rect, text, style, th, bg=None, centre=True, shear=0.25, pad=2, font=LILITA, track=0):
    return dict(rect=rect, text=text, style=style, th=th, bg=bg, centre=centre, shear=shear, pad=pad,
                font=font, track=track)


MENU = shadowed(fill=4, edge=3, shadow=8)
BUTTON = outlined(8, [1, 1, 2, 3, 4, 4])
PLATE = outlined(0xB, [5, 4, 3, 2, 2, 3, 4, 5, 6])
HUD_PLATE = outlined(0xB, [1])
HUD_NAMES = ["Jiggar", "Goliath", "Tiara", "Galahad", "Yasutsuna", "Agathe", "Meg-meg", "Hayate",
             "Son Gokuh", "Sinbad", "Dante"]


def banner_labels(rows):
    """Keep each original banner frame; use at most two native pixel-font lines."""
    result = []
    for x, y, width, text in rows:
        room = width - 28
        words = text.split()
        def size(s):
            return pixel_mask(s, 8, 512, SILK, 0)[0].shape[1]
        lines = [text]
        if size(text) > room:
            choices = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
            lines = min(choices, key=lambda pair: max(map(size, pair)))
        assert max(map(size, lines)) <= room, text
        height = 16 // len(lines)
        for i, line in enumerate(lines):
            result.append(L((x + 12, y + 4 + i * height, width - 24, height), line,
                            outlined(0xB, [1]), 5, shear=0, font=SILK, track=0, pad=2))
    return result


def compact_labels(rows, style=None, bg=0):
    """One or two native pixel-font lines inside an original 16 px atlas tile."""
    result = []
    for rect, text in rows:
        x, y, width, height = rect
        def size(s):
            return pixel_mask(s, 8, 512, SILK, 0)[0].shape[1]
        words = text.split()
        lines = [text]
        if size(text) > width - 2:
            choices = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
            lines = min(choices, key=lambda pair: max(map(size, pair)))
        assert max(map(size, lines)) <= width - 2, text
        line_height = height // len(lines)
        for i, line in enumerate(lines):
            result.append(L((x, y + i * line_height, width, line_height), line,
                            style or outlined(8, [1]), 5, bg=bg, shear=0, font=SILK, track=0, pad=1))
    return result


BOARD_LABELS = [
    ((0, 0, 80, 16), "City of the West Wind"), ((80, 0, 80, 16), "Green Sanctuary"),
    ((0, 16, 88, 16), "Heat-Haze Ruins"), ((88, 16, 128, 16), "Land of the Ring Ruins"),
    ((0, 32, 112, 16), "Bushido Castle"), ((112, 32, 128, 16), "Pandemonium the Demon City"),
    ((0, 48, 88, 16), "Tokyo 199X"),
]


SCENARIO_BANNERS_A = [
    (0, 0, 136, "The Adventure Begins"), (0, 24, 120, "Companions on the Road"),
    (0, 48, 136, "Escape the Bandits"), (0, 72, 168, "The Princess's Proposal"),
    (0, 96, 120, "Defeat the Impostor"), (0, 120, 152, "Collect the Debt"),
    (0, 144, 168, "Chanbara Wars"), (0, 168, 120, "Tournament Qualifiers"),
    (0, 192, 120, "Martial Arts Tournament"), (0, 216, 184, "Princess Crisis"),
]
SCENARIO_BANNERS_B = [
    (0, 0, 136, "Operation East vs. West"), (0, 24, 120, "Great Sage Equal to Havoc"),
    (0, 48, 120, "Battle of the Gods"), (0, 72, 184, "Economic Animal"),
    (0, 96, 136, "Showdown in the Sky City"), (0, 120, 120, "The Impostor's Revenge"),
    (0, 144, 120, "The Underground Tournament"), (0, 168, 120, "The Demon Lord Returns"),
    (0, 192, 120, "The Ninja Code"), (0, 216, 120, "The Witch's Forest"),
    (136, 0, 120, "A Battle of Women"), (136, 24, 120, "The Foreign Warrior"),
]
EVENT_BANNERS = {
    0: "Send to GO", 1: "Warp", 6: "Awful Luck", 7: "Bad Luck", 8: "Good Luck",
    9: "Great Luck", 10: "Plunder", 14: "Wreck a Shop", 18: "Change Route", 20: "Battle Card",
    21: "Dodge Payment", 24: "Evil Statue", 25: "Devil's Tower", 26: "Graveyard", 27: "Hot Spring",
    28: "Goddess Statue", 29: "Garden", 30: "Cathedral", 31: "Circus", 32: "Tremor",
    37: "Land Purchase", 38: "Move 1", 39: "Move 2", 40: "Move 3", 41: "Move 4", 42: "Move 5",
    43: "Move 6", 44: "3 Dice", 45: "4 Dice", 46: "Cursed Swamp", 47: "Reaper Statue", 48: "Card Swap",
}


def event_banner(number, text):
    key = f"EVCARD.BDP/{number:03}/003.bin"
    texture = tim.parse((UNPACKED / key).read_bytes())
    palette = texture["clut"][0]
    def colour(rgb):
        return min(range(256), key=lambda i: sum((a - b) ** 2 for a, b in zip(palette[i][:3], rgb)))
    bg = int(np.bincount(indices(texture)[98:113, 16:81].reshape(-1), minlength=256).argmax())
    ink, shade = [colour(tuple(round(c * scale) for c in palette[bg][:3])) for scale in (0.3, 0.7)]
    return dict(key=key, clut=0, labels=[L((16, 98, 65, 15), text,
        shadowed(ink, ink, shade, 1, 1), 10, bg=bg, shear=0, pad=1)])


# Hand-drawn outlines in a 60-unit em. Broad stems, cut corners, pointed feet
# and flared terminals follow the Japanese wordmark rather than the menu font.
# Each glyph is (advance, outer polygons, counter polygons); case is deliberate.
TITLE_GLYPHS = {
    "G": (30, [[(28, 2), (23, 11), (15, 8), (9, 15), (8, 43), (12, 51),
                (19, 48), (20, 34), (14, 34), (16, 26), (29, 26), (26, 53),
                (15, 60), (2, 57), (0, 48), (2, 15), (10, 3), (20, 0)]], []),
    "a": (25, [[(2, 16), (17, 13), (24, 19), (21, 51), (24, 56), (14, 59),
                (14, 54), (7, 59), (0, 54), (0, 39), (6, 31), (16, 29),
                (16, 22), (5, 23), (0, 27)]],
              [[(8, 39), (15, 36), (14, 47), (8, 50), (6, 47)]]),
    "i": (13, [[(3, 18), (12, 15), (9, 51), (12, 55), (0, 60), (2, 49)],
               [(4, 1), (12, 0), (11, 10), (3, 12)]], []),
    "M": (35, [[(0, 60), (5, 9), (2, 1), (14, 4), (19, 28), (29, 3),
                (35, 0), (30, 53), (34, 57), (21, 60), (26, 22),
                (17, 45), (12, 23), (8, 52)]], []),
    "s": (23, [[(23, 15), (18, 24), (9, 22), (6, 27), (20, 37), (21, 49),
                (13, 58), (0, 59), (1, 49), (11, 51), (14, 46), (1, 35),
                (1, 24), (8, 15)]], []),
    "t": (20, [[(6, 8), (16, 3), (14, 18), (22, 17), (19, 25), (13, 26),
                (10, 48), (19, 45), (15, 55), (6, 59), (1, 54), (4, 27),
                (0, 28), (1, 20), (5, 19)]], []),
    "e": (24, [[(22, 17), (24, 29), (20, 40), (7, 41), (8, 50), (20, 46),
                (17, 55), (6, 59), (0, 53), (0, 31), (6, 18), (15, 13)]],
              [[(8, 27), (15, 23), (16, 32), (7, 34)]]),
    "r": (20, [[(2, 18), (11, 14), (11, 21), (18, 14), (23, 15), (19, 26),
                (13, 27), (9, 34), (7, 52), (11, 55), (0, 60)]], []),
}


def title_mask(scale=1):
    """One shared vector wordmark for both TIMs; rasterize at native resolution."""
    img = Image.new("1", (256 * scale, 160 * scale))
    draw = ImageDraw.Draw(img)
    cursor = 5
    for letter in "GaiaMaster":
        advance, outlines, counters = TITLE_GLYPHS[letter]
        for polygons, ink in ((outlines, 1), (counters, 0)):
            for polygon in polygons:
                draw.polygon([(round((cursor + x * 0.87 + (60 - y) * 0.13) * scale),
                               round((29 + y) * scale)) for x, y in polygon], fill=ink)
        cursor += (advance + 2) * 0.87
    return np.array(img, bool)


def title_style(small=False):
    """Original CLUT ramps and ornaments, with a shared English silhouette.

    The small TIM contains an 80x48 framed thumbnail and an empty second panel.
    Its 16-entry CLUT is never replaced with the large logo's palette.
    """
    def paint(canvas):
        original = tim.parse((UNPACKED / "SCR_DATA.BDP/127/032.dec").read_bytes())
        palette = np.array(original["clut"][0], dtype=int)
        scale = 3
        art = np.zeros((160 * scale, 256 * scale), np.uint8)
        source = indices(original).repeat(scale, 0).repeat(scale, 1)

        def offset(mask, x, y):
            return shift(mask, round(x * scale), round(y * scale))

        def expand(mask, radius=1):
            for _ in range(round(radius * scale)):
                mask = grow(mask)
            return mask
        # The original Roman masthead, TM, and outer gold wings contain no JP.
        for x, y, w, h in [(79, 15, 159, 12), (234, 85, 14, 7),
                           (29, 96, 59, 27), (174, 96, 60, 27)]:
            box = np.s_[y * scale:(y + h) * scale, x * scale:(x + w) * scale]
            art[box] = source[box]

        def polygon(points):
            img = Image.new("1", (256 * scale, 160 * scale))
            ImageDraw.Draw(img).polygon([(x * scale, y * scale) for x, y in points], fill=1)
            return np.array(img, bool)

        def ramp(mask, stops):
            rows = np.flatnonzero(mask.any(1))
            for y in rows:
                ink = stops[min(len(stops) - 1,
                                (y - rows[0]) * len(stops) // len(rows))]
                art[y, mask[y]] = ink

        # Rebuild only the central crest hidden by the Japanese subtitle. Gold
        # faces and the vermilion lower facet echo the original diamond/flame.
        crest = polygon([(128, 45), (157, 89), (171, 109), (146, 132),
                         (128, 153), (108, 132), (84, 109), (101, 89)])
        art[offset(expand(crest), 2, 3)] = 236
        art[expand(crest)] = 187
        ramp(crest, [3, 10, 15, 23, 33, 45, 55, 153])
        left = polygon([(128, 52), (92, 108), (128, 145), (114, 108)])
        ramp(left, [3, 10, 15, 23, 45, 153])
        right = polygon([(129, 55), (163, 108), (130, 144), (141, 107)])
        ramp(right, [15, 23, 33, 55, 153])
        gold = (palette[source, 0] >= 180) & (palette[source, 1] >= 80) & (palette[source, 2] < 32)
        gold[99 * scale:] = False
        art[gold & crest] = source[gold & crest]
        # Continue the wings behind the subtitle, preserving their outer tips.
        wing = polygon([(78, 98), (107, 101), (128, 109), (148, 101),
                        (177, 98), (181, 111), (155, 118), (128, 114),
                        (101, 118), (75, 111)])
        ramp(wing, [3, 10, 15, 23, 33, 45])

        mask = title_mask(scale)
        edges = [mask]
        for _ in range(4):
            edges.append(expand(edges[-1], 0.8))
        # Black offset, dark bronze outside, orange bevel, yellow top rim,
        # turquoise inner lip, then the saturated royal-blue face.
        art[offset(edges[4], 2, 3)] = 236
        art[edges[4]] = 206
        art[edges[3]] = 33
        art[edges[3] & ~offset(edges[3], 1, 1)] = 3
        art[edges[2]] = 3
        art[edges[2] & ~offset(edges[2], -1, -1)] = 62
        art[edges[1]] = 127
        ramp(mask, [2, 59, 64, 78, 84, 97, 103, 108, 115])
        art[mask & ~offset(mask, 1, 0.6)] = 2
        art[mask & ~offset(mask, -0.7, -0.7)] = 212

        # The original subtitle is stacked over the crest: gold-edged dark
        # lettering and a red lower shadow, not a detached white caption.
        for text, y, width in [("Board Game", 103, 156), ("of the Gods", 124, 150)]:
            letters, _ = text_mask(text, 16 * scale, width * scale, shear=0.13, track=0.3 * scale)
            h, w = letters.shape
            mask = np.zeros_like(art, bool)
            mask[y * scale:y * scale + h, (256 * scale - w) // 2:(256 * scale + w) // 2] = letters
            edge = expand(mask, 1.7)
            art[offset(expand(edge), 1, 2)] = 153
            art[expand(edge)] = 187
            art[edge] = 23
            art[edge & ~offset(edge, 1, 1)] = 3
            art[expand(mask, 0.7)] = 3
            art[mask] = 236

        # Coverage antialiasing is quantized back to CLUT 0, including the edge
        # shades already used by the Japanese artwork. No palette bytes change.
        rgba = Image.fromarray(palette[art].astype(np.uint8))
        rgba = np.array(rgba.resize((256, 160), Image.Resampling.BOX))
        colours, inverse = np.unique(rgba[:, :, :3].reshape(-1, 3), axis=0, return_inverse=True)
        distance = ((colours[:, None].astype(int) - palette[None, 1:, :3]) ** 2).sum(2)
        art = (distance.argmin(1)[inverse] + 1).reshape(160, 256).astype(np.uint8)
        art[rgba[:, :, 3] < 96] = 0
        if not small:
            canvas[:] = art
            return
        # Keep the thumbnail frame, the second panel and TIM padding verbatim.
        # The actual logo lives inside (3,3,75,42), not across the 176px atlas.
        thumbnail = tim.parse((UNPACKED / "SCR_DATA.BDP/213/000.bin").read_bytes())
        canvas[:] = indices(thumbnail)
        target = canvas[3:45, 3:78]
        rgb = palette[art, :3]
        luminance = (rgb * np.array([0.299, 0.587, 0.114])).sum(2)
        levels = Image.fromarray(np.uint8(luminance))
        levels = np.array(levels.resize((75, 42), Image.Resampling.BOX))
        alpha = Image.fromarray(np.uint8(art != 0) * 255)
        alpha = np.array(alpha.resize((75, 42), Image.Resampling.BOX))
        # Palette indices 1..14 are the original increasing purple brightness.
        target[:] = np.clip(np.rint(levels / 248 * 13) + 1, 1, 14).astype(np.uint8)
        target[alpha < 80] = 1
    return paint


LABELS = {
    "G1": dict(key="SCR_DATA.BDP/127/032.dec", clut=0, labels=[
        L((0, 0, 256, 160), "", None, 1, bg=0) | {"art": title_style()},
    ]),
    "G1-small": dict(key="SCR_DATA.BDP/213/000.bin", clut=0, labels=[
        L((0, 0, 176, 50), "", None, 1, bg=0) | {"art": title_style(small=True)},
    ]),
    "G15": dict(key="SCR_DATA.BDP/141/004.dec", clut=0, labels=[
        L(rect, "Purge", outlined(12, ramp), 24, bg=0, shear=0.25, pad=2)
        for rect, ramp in [((96, 16, 56, 80), [8, 7, 8]), ((168, 16, 56, 80), [1, 3, 6]),
                           ((8, 128, 64, 80), [1, 2, 5]), ((80, 128, 64, 80), [1, 2, 5]),
                           ((160, 128, 56, 80), [1, 3, 6])]
    ]),
    "G16": dict(key="DUELEF.BDP/007/001.dec", clut=0, labels=[
        L((20, 40, 44, 36), "Seal", outlined(127, [6]), 12, shear=0, pad=3) | {"erase": "red-ink"},
    ]),
    "G17": dict(key="SCR_DATA.BDP/116/003.dec", clut=0, labels=[
        L((24, 72, 272, 92), "", outlined(0, [0]), 1, bg=0),
        *[L((24, 78 + 24 * i, 272, 20), text, outlined(0, [255]), 11, bg=0, shear=0)
          for i, text in enumerate(["This software is still in development.",
                                    "No replacements will be provided",
                                    "if problems occur."])],
    ]),
    **{f"G14-{n:03}": event_banner(n, text) for n, text in EVENT_BANNERS.items()},
    "G10": dict(key="SCR_DATA.BDP/009/000.dec", clut=0, labels=[
        L(rect, text, outlined(8, [1, 2, 3, 4]), 9, bg=0, pad=7 if text == "Rumble" else 1)
        for rect, text in [
            ((4, 4, 104, 16), "Options"), ((116, 4, 64, 16), "Rules"), ((184, 8, 64, 16), "Level"),
            ((0, 24, 96, 16), "Audio"), ((96, 24, 48, 16), "Easy"),
            ((144, 24, 56, 16), "Normal"), ((200, 24, 56, 16), "Hard"),
            ((0, 40, 56, 16), "Rule"), ((56, 40, 48, 16), "Settings"),
            ((104, 40, 80, 16), "Stereo"), ((184, 40, 56, 16), "Turn"),
            ((0, 56, 64, 16), "Dialogue"), ((64, 56, 48, 16), "Display"),
            ((120, 56, 24, 16), ""), ((144, 56, 40, 16), "On"), ((184, 56, 40, 16), "Off"),
            ((232, 56, 24, 16), "?"), ((0, 72, 56, 16), "Speed"),
            ((56, 72, 80, 16), "Salary"), ((144, 72, 80, 16), "Mono"), ((224, 72, 32, 16), "by"),
            ((176, 104, 56, 16), "Back"), ((232, 104, 24, 16), ""),
            ((0, 120, 48, 16), "Interest"), ((48, 120, 40, 16), "Debt"),
            ((88, 120, 64, 16), "Funds"), ((152, 120, 64, 16), "Land Count"),
            ((0, 152, 40, 16), "Yes"), ((40, 152, 40, 16), "No"), ((80, 152, 128, 16), "COM Level"),
            ((208, 152, 40, 16), "Strong"), ((0, 168, 120, 16), "Animation"),
            ((120, 168, 80, 16), "Owned Land"), ((216, 168, 40, 16), "Weak"),
            ((144, 184, 48, 16), "Fast"), ((192, 184, 64, 16), "Voice"),
            ((120, 200, 48, 16), "Rumble"), ((168, 200, 64, 16), "until end?"),
            ((80, 216, 80, 16), "Lucky"), ((160, 216, 88, 16), "Starting Amount?"),
            ((64, 232, 80, 16), "Turns"), ((144, 232, 56, 16), "per raise?"),
            ((200, 232, 56, 16), "Increase"),
        ]
    ]),
    "G8": dict(key="SCR_DATA.BDP/000/004.dec", clut=0, labels=compact_labels([
        ((0, 0, 72, 16), "Roll Dice"), ((80, 0, 48, 16), "Buy Shop"),
        ((160, 0, 64, 16), "Map Info"), ((0, 16, 48, 16), "Use Card"),
        ((80, 16, 48, 16), "Sell Assets"), ((144, 16, 84, 16), "None Owned!"),
        ((24, 32, 48, 16), "Menu"), ((104, 32, 36, 16), "Graph"),
        ((152, 32, 24, 16), "Shop"), ((184, 32, 24, 16), "Save"),
        ((0, 48, 24, 16), "Info"), ((30, 48, 36, 16), "Save"),
        ((80, 48, 24, 16), "Add"), ((104, 48, 48, 16), "Assets Info"),
        ((208, 32, 48, 16), "Personal Info"), ((192, 48, 48, 16), "Redeem Mortgage"),
    ], outlined(0, [4])) + [
        # Info Menu replaces only the first 24 px of Trade Menu; personal
        # graphs likewise reuse the last 36 px of the original graph label.
        L((0, 32, 24, 16), "Trade", outlined(0, [4]), 5, bg=0,
          shear=0, font=SILK, track=-1, pad=1),
        L((80, 32, 24, 16), "", outlined(0, [4]), 1, bg=0),
        L((128, 16, 12, 16), "", outlined(0, [4]), 1, bg=0),
        # The empty-hand tooltip reads only the first 48 px of Use Card.
        L((48, 16, 24, 16), "", outlined(0, [4]), 1, bg=0),
    ]),
    "G4-save": dict(key="SCR_DATA.BDP/007/001.dec", clut=0, labels=compact_labels(BOARD_LABELS)),
    "G4-world": dict(key="SCR_DATA.BDP/061/000.dec", clut=0, labels=compact_labels(BOARD_LABELS)),
    "G4-rankings": dict(key="SCR_DATA.BDP/012/004.dec", clut=0, labels=compact_labels(BOARD_LABELS)),
    "G3": dict(key="SCR_DATA.BDP/007/000.dec", clut=0, labels=[
        L(rect, text, outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1)
        for rect, text in [((0, 0, 64, 16), "Save"), ((64, 0, 64, 16), "Load"),
                           ((128, 0, 64, 16), "Story"), ((0, 16, 128, 16), "No Data"),
                           ((136, 16, 56, 16), "Versus"), ((216, 32, 40, 16), "Turn"),
                           ((176, 80, 64, 16), "Normal")]
    ] + [L((216, 48, 24, 8), "Turn", outlined(8, [1]), 5, bg=0, font=SILK, track=0, shear=0, pad=0)] + [
        L((48 * (i % 5), 168 + 16 * (i // 5) + 8 * line, 48, 8), text,
          outlined(0xB, [1]), 5, bg=0, font=SILK, track=0, shear=0, pad=1)
        for i in range(20) for line, text in enumerate(["Chapter", str(i + 1)])
    ]),
    "G13-a": dict(key="SCR_DATA.BDP/061/006.dec", clut=0, labels=banner_labels(SCENARIO_BANNERS_A)),
    "G13-b": dict(key="SCR_DATA.BDP/061/007.dec", clut=0, labels=banner_labels(SCENARIO_BANNERS_B)),
    "G7": dict(key="SCR_DATA.BDP/214/000.dec", clut=0, labels=[
        L((2, y + 2, 148, 12), "Weapon Skill Level: " + kind, outlined(8, [1, 2, 3, 4]),
          5, bg=0, shear=0, pad=1, font=SILK, track=0)
        for y, kind in [(0, "Magic"), (16, "Ranged"), (32, "Sword"), (200, "Other")]
    ]),
    "G11": dict(key="SCR_DATA.BDP/060/000.dec", clut=0, labels=[
        L((0, 24, 72, 16), "Continue", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((72, 24, 56, 16), "Quit", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
    ]),
    "G12": dict(key="PRGPACK.BDP/000/001/000.dec", clut=0, labels=[
        L((48, 0, 72, 16), "Continue", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((80, 16, 56, 16), "Quit", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
    ]),
    "G9": dict(key="SCR_DATA.BDP/012/000.dec", clut=0, labels=[
        L((192, 32, 64, 16), "Assets", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((192, 48, 40, 16), "Cash", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((192, 64, 40, 16), "Land", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((152, 200, 104, 16), "Rankings", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((56, 216, 40, 16), "Turn", outlined(8, [1, 2, 3, 4]), 11, bg=0, pad=1),
        L((96, 216, 24, 8), "Turn", outlined(8, [1]), 5, bg=0, font=SILK, shear=0, pad=0),
    ]),
    "G5-board": dict(key="SCR_DATA.BDP/000/001.dec", clut=1, labels=[
        L((194, i * 16 + 1, 59, 13), name, HUD_PLATE, 5, bg=0, shear=0, font=SILK, track=0, pad=1)
        for i, name in enumerate(HUD_NAMES)
    ]),
    "G5-save": dict(key="SCR_DATA.BDP/059/008.bin", clut=1, labels=[
        L((194, i * 16 + 1, 59, 13), name, HUD_PLATE, 5, bg=0, shear=0, font=SILK, track=0, pad=1)
        for i, name in enumerate(HUD_NAMES)
    ]),
    "G5-weapon": dict(key="SCR_DATA.BDP/214/000.dec", clut=1, labels=[
        L((163, i * 16 + 1, 58, 13), name, HUD_PLATE, 5, bg=0, shear=0, font=SILK, track=0, pad=1)
        for i, name in enumerate(HUD_NAMES)
    ]),
    "G2": dict(key="SCR_DATA.BDP/127/033.dec", clut=0, labels=[
        L((4, 4, 214, 24), "Versus Mode", MENU, 15, bg=0xE),
        L((4, 36, 214, 24), "Story Mode", MENU, 15, bg=0xE),
        L((4, 68, 214, 24), "Weapon Skill List", MENU, 15, bg=0xE),
        L((4, 100, 214, 24), "Options", MENU, 15, bg=0xE),
        L((4, 132, 214, 24), "Normal Mode", MENU, 15, bg=0xE),
        L((4, 164, 214, 24), "Quick Mode", MENU, 15, bg=0xE),
        L((3, 195, 99, 24), "Single", MENU, 15, bg=0xE),
        L((108, 195, 96, 24), "Tag", MENU, 15, bg=0xE),
        L((5, 231, 117, 17), "New Game", BUTTON, 11, bg=9),
        L((133, 231, 117, 17), "Continue", BUTTON, 11, bg=9),
    ]),
    # character select: title (G6) and the 11 name plates (G5); plates 64x16 on a grid from (0,112), inner 3..60
    "G6": dict(key="SCR_DATA.BDP/117/000.dec", clut=1, labels=[
        L((12, 40, 188, 16), "Character Select", outlined(9, [5, 4, 3, 2, 1, 1, 1, 2, 3, 4, 5]), 11, bg=0),
    ] + [
        L((64 * (i % 4) + 3, 112 + 16 * (i // 4) + 3, 58, 10), n, PLATE, 5, bg=0, shear=0, font=SILK, track=0, pad=1)
        for i, n in enumerate(["Jiggar", "Galahad", "Meg-meg", "Sinbad", "Goliath", "Yasutsuna", "Hayate", "Dante",
                               "Tiara", "Agathe", "Son Gokuh"])
    ]),
}


def copies(key):
    """Every unpacked path holding the same image as key (index.tsv), key first."""
    rel = key.replace("/", "\\")
    for ln in (ROOT / "docs/re/gfx_survey/index.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        paths = ln.split("\t")[5].split(";")
        if rel in paths:
            return [key] + [p.replace("\\", "/") for p in paths if p != rel]
    return [key]


def render(g):
    data = (UNPACKED / g["key"]).read_bytes()
    t = tim.parse(data)
    a = indices(t)
    new = a.copy()
    allowed = np.zeros(a.shape, bool)
    for lb in g["labels"]:
        x, y, w, h = lb["rect"]
        allowed[y:y + h, x:x + w] = True
        c = new[y:y + h, x:x + w]
        if lb.get("erase") == "red-ink":
            colours = np.array(t["clut"][g["clut"]], dtype=int)[c]
            ink = (colours[:, :, 0] > colours[:, :, 1] * 2) & (colours[:, :, 1] < 60)
            paper = np.argwhere(~ink)
            assert len(paper), "no paper pixels for restoring the seal background"
            old = c.copy()
            for point in np.argwhere(ink):
                nearest = paper[((paper - point) ** 2).sum(1).argmin()]
                c[tuple(point)] = old[tuple(nearest)]
        else:
            c[:] = (lb["bg"] if lb["bg"] is not None else c[:, :1])
        if "art" in lb:
            lb["art"](c)
        if not lb["text"]:
            continue
        m, top = text_mask(lb["text"], lb["th"], w - 2 * lb["pad"], lb["font"], lb["shear"], lb["track"])
        mh, mw = m.shape
        ox = (w - mw) // 2 if lb["centre"] else lb["pad"]
        oy = (h - lb["th"]) // 2 - top + lb.get("dy", 0)   # caps centred; descenders hang below
        full = np.zeros((h + 2 * mh, w), bool)
        full[mh + oy:mh + oy + mh, ox:ox + mw] = m
        assert not full[:mh].any() and not full[mh + h:].any(), f"{lb['text']!r} does not fit its rect"
        full = full[mh:mh + h]
        lb["style"](c, full)
    assert not (new != a)[~allowed].any(), "pixels changed outside the label rects"
    return data, t, a, new


def edits(only=None):
    """({key: new bytes}, write log lines "key OFF old new gfx:Gn" in the build's format, one per changed run)."""
    out, log = {}, []
    for name, g in LABELS.items():
        if only and name not in only:
            continue
        data, t, _, new = render(g)
        # Multiple label groups can share one texture (weapon headers + plates).
        # Compose their nonoverlapping changes rather than overwriting a group.
        if g["key"] in out:
            previous = indices(tim.parse(out[g["key"]]))
            changed = new != indices(t)
            assert not ((previous != indices(t)) & changed).any(), "overlapping graphics groups"
            previous[changed] = new[changed]
            composed = encode(data, t, previous)
        else:
            composed = encode(data, t, new)
        b = encode(data, t, new)
        diff = np.flatnonzero(np.frombuffer(data, np.uint8) != np.frombuffer(b, np.uint8))
        runs = np.split(diff, np.flatnonzero(np.diff(diff) > 1) + 1) if diff.size else []
        for k in copies(g["key"]):
            assert (UNPACKED / k).read_bytes() == data, k
            out[k] = composed
            log += ["%s %X %s %s gfx:%s" % (k, r[0], data[r[0]:r[-1] + 1].hex(), b[r[0]:r[-1] + 1].hex(), name)
                    for r in runs]
    return out, log


def preview(name, g, out):
    data, t, a, new = render(g)
    imgs = []
    for arr in (a, new):
        tt = dict(t, pix=encode(data, t, arr)[t["end"] - len(t["pix"]):t["end"]])
        imgs.append(tim.image(tt, g["clut"]))
    w, h = imgs[0].size
    sheet = Image.new("RGBA", (w, h * 2 + 4), (255, 0, 255, 255))
    sheet.paste(imgs[0], (0, 0))
    sheet.paste(imgs[1], (0, h + 4))
    sheet = sheet.resize((w * 3, (h * 2 + 4) * 3), Image.NEAREST)
    p = out / f"{name}.png"
    sheet.save(p)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "work/gfx"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, g in LABELS.items():
        if not a.only or name in a.only:
            print(preview(name, g, out))
    print(len(edits(a.only)[0]), "files")


if __name__ == "__main__":
    main()
