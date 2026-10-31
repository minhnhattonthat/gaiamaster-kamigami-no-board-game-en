"""engine.py: the EXE patches for English text (docs/re/text.md §English).

patch(exe) -> (new exe bytes, write log). Every write goes through put(), which checks the original bytes.

- ASCII 0x21-0x7E draws through the EXE's ASCII -> full-width table (0x8007E740) with the 12px font's glyph cells,
  whose pixels become the English glyphs of fonts/en12.txt (left-aligned); 15 ASCII codes with no full-width glyph
  get the cells of kanji the script never uses (SPARE).
- VWF: the drawer's sprite width / advance for those codes comes from a width table (hook VWF_ADV).
- Space advance SPACE_W instead of the half-width 8.
- Text objects hold 3x the glyphs their creator asks for (hook TRIPLE): English needs ~2x the glyphs per line.
- Escape /I advances the pen INDENT_W px: tools/insert.py writes it for the 4 leading U+3000 of story lines (8 bytes).
Hook code and the width table sit in index-table entries the font lookup never reads (codes below 0x8140).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font_en  # noqa: E402
from mipsasm import asm  # noqa: E402

BASE = 0x8000F800
GLYPHS, INDEX, ASCII_SJIS = 0x8006BCEC, 0x8007AECC, 0x8007E740
CODE, CODE_END = 0x8007AF50, 0x8007B14C            # INDEX + 2 * 0x40 .. INDEX + 2 * 0x140: never read
SPARE = "凱客芸源鋼錫収政専旋船続段潮報"               # glyph cells given to ASCII codes with none
ESCAPES = 0x800134D8                                 # '/' escape jump table, letters 'H'..'z' (unused -> 0x8003C8B4)
INDENT, INDENT_W = "/I", 48                          # new escape: the 4 leading full-width spaces of story lines

HOOKS = """
vwf_adv:                 ; drawer 0x8003CCAC: a0 = v0 = sprite width / advance of the glyph for code s0
    lh a0, 0x40(s1)
    addiu v0, s0, -0x21
    sltiu v1, v0, 0x5e
    beq v1, zero, adv_done
    addiu a0, a0, 1
    addiu v1, zero, 12
    bne a0, v1, adv_done ; 12px font only (size 15 = the BIOS 16px font keeps its width)
    lui v1, %hi(widths)
    addu v1, v1, v0
    lbu a0, %lo(widths)(v1)
adv_done:
    jr ra
    move v0, a0
triple:                  ; text create 0x8003D4D0: s4 (glyph cap) *= 3, then the original sll s1, s4, 4
    sll v0, s4, 1
    addu s4, s4, v0
    jr ra
    sll s1, s4, 4
indent:                  ; drawer escape /I (jump table ESCAPES): pen x += INDENT_W, no glyph
    lhu v1, 0x18(a0)
    nop
    addiu v1, v1, INDENT_W
    j 0x8003C8B4         ; the table's common exit: return the string pointer
    sh v1, 0x18(a0)
widths:
"""


def off(addr):
    return addr - BASE


class Patcher:
    def __init__(self, exe):
        self.orig, self.data, self.log = bytes(exe), bytearray(exe), []

    def put(self, addr, new, by, expect=None):
        o = off(addr)
        old = self.orig[o:o + len(new)]
        if expect is not None:
            assert old == expect, "%s at %08X: found %s, expected %s" % (by, addr, old.hex(), expect.hex())
        self.log.append("SLPS_020.75 %X %s %s %s" % (o, old.hex(), bytes(new).hex(), by))
        self.data[o:o + len(new)] = new

    def u16(self, addr):
        return struct.unpack_from("<H", self.orig, off(addr))[0]


def word(w):
    return struct.pack("<I", w)


def patch(exe):
    p = Patcher(exe)
    g = font_en.glyphs()
    spare = iter(SPARE)
    widths = bytearray()
    cells = {}
    for c in range(0x21, 0x7F):
        sj = p.u16(ASCII_SJIS + 2 * (c - 0x21))
        idx = p.u16(INDEX + 2 * (sj & 0x7FFF))
        if idx == 0 or idx in cells:
            sj = int.from_bytes(next(spare).encode("cp932"), "big")
            idx = p.u16(INDEX + 2 * (sj & 0x7FFF))
            assert idx and idx not in cells
            p.put(ASCII_SJIS + 2 * (c - 0x21), struct.pack("<H", sj), "ascii %r -> spare %04X" % (chr(c), sj))
        cells[idx] = chr(c)
        p.put(GLYPHS + 72 * idx, g[chr(c)][0], "glyph %r" % chr(c))
        widths.append(g[chr(c)][1])
    labels = {"INDENT_W": INDENT_W}
    code = asm(HOOKS, CODE, labels) + bytes(widths)
    assert CODE + len(code) <= CODE_END and labels["widths"] == CODE + len(code) - len(widths)
    p.put(CODE, code, "hooks + width table", expect=bytes(len(code)))
    # glyph lookup: ASCII takes the full-width table path (was: half-width digit font, letters blank)
    p.put(0x8003C308, asm("bne v0, zero, 0x8003C37C", 0x8003C308), "ascii -> full-width table",
          expect=asm("bne v0, zero, 0x8003C354", 0x8003C308))
    # drawer, new glyph: sprite width / advance = vwf_adv (was size + 1)
    p.put(0x8003CCAC, asm("jal %d\nnop\nnop\nnop" % labels["vwf_adv"], 0x8003CCAC), "vwf advance",
          expect=asm("lh v0, 0x40(s1)\nnop\naddiu v0, v0, 1\nmove a0, v0", 0x8003CCAC))
    # drawer, ASCII space: never the full-width 0x8140 path (flag 26 objects drew it 12 px wide)
    p.put(0x8003CA40, asm("beq zero, zero, 0x8003CA50", 0x8003CA40), "space always half",
          expect=asm("beq v0, zero, 0x8003CA50", 0x8003CA40))
    # drawer, space: advance SPACE_W (was 0x3E(s1) = 8)
    p.put(0x8003CA88, asm("addiu a0, zero, %d" % font_en.SPACE_W, 0x8003CA88), "space width",
          expect=asm("lh a0, 0x3e(s1)", 0x8003CA88))
    # drawer: escape /I = indent (the letter was unused: the table sent it to the common exit)
    p.put(ESCAPES + 4 * (ord(INDENT[1]) - 0x48), word(labels["indent"]), "escape /I -> indent",
          expect=word(0x8003C8B4))
    # text create: glyph cap x3
    p.put(0x8003D4D0, asm("jal %d" % labels["triple"], 0x8003D4D0), "glyph cap x3",
          expect=asm("sll s1, s4, 4", 0x8003D4D0))
    return bytes(p.data), p.log


# overlay patches: {file key: [(file offset, original, new, why)]}
OVERLAYS = {
    "PRGPACK.BDP/009/000.bin": [
        (0x3F74, asm("addiu a2, zero, -40", 0), asm("addiu a2, zero, -80", 0), "biography panel origin"),
        (0x41CC, asm("addiu a2, zero, 170", 0), asm("addiu a2, zero, 90", 0), "biography text origin"),
    ],
    # staff credits: ovl033 installs its own glyph/index tables (resource items 0xDD/0xDE) via 0x8003DD68; they
    # have no English glyphs, so keep the EXE font (English credits need ASCII only)
    "PRGPACK.BDP/033/000.bin": [(0x1F578, asm("jal 0x8003DD68", 0x800BEEB0), asm("nop", 0), "credits keep EXE font")],
}


def patch_overlay(key, data):
    """data with OVERLAYS[key] applied, and the log lines; original bytes asserted."""
    data, log = bytearray(data), []
    for o, old, new, why in OVERLAYS.get(key, []):
        assert data[o:o + len(old)] == old, "%s @%X: original bytes differ (%s)" % (key, o, why)
        log.append("%s %X %s %s %s" % (key, o, old.hex(), new.hex(), why))
        data[o:o + len(new)] = new
    return bytes(data), log


if __name__ == "__main__":
    exe = (Path(__file__).resolve().parents[1] / "work/disc/tree/SLPS_020.75").read_bytes()
    new, log = patch(exe)
    print("\n".join(ln[:120] for ln in log[-6:]), "\n%d writes" % len(log))
