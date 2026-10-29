"""extract.py: every Japanese string on the disc -> script/<block>.json (one file per block).

    python -X utf8 tools/extract.py            write missing block files only
    python -X utf8 tools/extract.py --force    rewrite jp/max/refs, keep en/status/notes by id (lists changed jp)
    python -X utf8 tools/extract.py --scan     re-index Japanese-looking runs on the disc (docs/re/jp_runs.json)

Needs work/disc/tree (build.py) and work/unpacked (unpack_all.py). Block kinds (docs/re/text.md):
- code: the EXE and PRGPACK overlays. Strings = NUL-terminated text that a pointer word or lui pair reaches
  (tools/mips.py), plus text runs in the gaps (no ref: edit in place only), plus fixed tables (`TABLES`).
- pool: PC_DATA 022-033 voice lines, reached by file-relative u32 offsets in (id, off, off, off) records.
- fields: fixed-width fields in SCR_DATA records (`LAYOUTS`); max = field size - 1.
Entry: id (block_at), at (RAM address for code, else file offset), jp, en, max (bytes before the NUL in place),
refs, notes. A block's `copies` are other files with the same bytes: the inserter writes them all.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sjis  # noqa: E402
from mips import refs as find_refs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UNP = ROOT / "work/unpacked"
TREE = ROOT / "work/disc/tree"
OUT = ROOT / "script"
EXE, EXE_BASE, EXE_END = "SLPS_020.75", 0x8000F800, 0x80086800
OVL_BASES = (0x8009F938, 0x800C8450, 0x80099224, 0x800990D0, 0x80099230, 0x80130F7C)
# fixed tables in code images: (address, records, stride, name field bytes incl. NUL, note on the first entry)
TABLES = {EXE: [(0x80011248, 57, 26, 16, "weapon/skill card names (16-byte name + 10 bytes of stats)"),
                (0x80011814, 50, 20, 15, "event/symbol card names (15-byte name + 5 bytes of data)"),
                (0x80011E3C, 6, 14, 11, "facility names (11-byte name + 3 bytes of data; byte 10 unproven)")]}
# where code images keep text; elsewhere ref'd 'strings' are code or tables that happen to decode
TEXT_RANGES = {EXE: [(0x80010120, 0x80013200), (0x80085F98, 0x80086120)]}


def read(key):
    return (TREE / key if key == EXE else UNP / key).read_bytes()


def cstr(d, o):
    e = d.find(b"\0", o)
    return d[o:e if e >= 0 else len(d)]


def text_run(s):
    """Gap-scan filter: clean text, mostly double-byte, no half-width kana; 2+ chars with a kana, else 3+."""
    if not sjis.is_text(s):
        return False
    t = sjis.decode(s)
    wide = sum(ord(c) >= 0x3000 and not 0xFF61 <= ord(c) <= 0xFF9F for c in t)
    kana = sum(0x3041 <= ord(c) <= 0x30FA for c in t)
    return (not any(0xFF61 <= ord(c) <= 0xFF9F for c in t) and wide >= 0.6 * len(t)
            and wide >= (2 if kana else 3))


def room(d, o, n, stop):
    """Bytes free for a string at o (n bytes long), minus the NUL: its NUL and the zero padding up to the next
    4-byte boundary, never past a nonzero byte or `stop`. Longer zero runs may be live variables."""
    e = o + n
    while e < min(len(d), stop, (o + n + 4) & ~3) and d[e] == 0:
        e += 1
    return e - o - 1


def fmt_ref(r, img=""):
    p = img + ":" if img else ""
    return "%sptr@%X" % (p, r[1]) if r[0] == "ptr" else "%slui@%X/%X" % (p, r[1], r[2])


# ---- code images

def overlays():
    """{key: data} for every PRGPACK overlay (entry NNN/000.bin, or its LZ-decoded .dec)."""
    out = {}
    for d in sorted((UNP / "PRGPACK.BDP").iterdir()):
        dec, raw = d / "000.dec", d / "000.bin"
        p = dec if dec.exists() else raw
        if p.exists():
            out[p.relative_to(UNP).as_posix()] = p.read_bytes()
    return out


def best_base(data):
    """The overlay load address that lands the most refs on text."""
    best = (0, None, {})
    for b in OVL_BASES:
        r = find_refs(data, b, b, b + len(data))
        hits = {t: v for t, v in r.items() if sjis.is_text(cstr(data, t - b))}
        if len(hits) > best[0]:
            best = (len(hits), b, r)
    return best[1], best[2]


def code_block(name, key, data, base, refs, extra_refs=None):
    end = base + len(data)
    ents, covered = {}, bytearray(len(data))
    if key in TEXT_RANGES:
        covered = bytearray(b"\1" * len(data))
        for lo, hi in TEXT_RANGES[key]:
            covered[lo - base:hi - base] = bytes(hi - lo)
    for tb, count, stride, field, note in TABLES.get(key, []):
        for i in range(count):
            o = tb - base + stride * i
            s = cstr(data, o)[:field]
            assert len(s) < field and (not s or sjis.is_text(s)), "%s: table %X record %d" % (name, tb, i)
            if s:
                ents[o] = dict(jp=s, max=field - 1, refs=refs.get(base + o, []), notes=note if i == 0 else "")
            covered[o:o + field] = b"\1" * field
    starts = sorted(t - base for t in refs if base <= t < end and not covered[t - base]
                    and sjis.is_text(cstr(data, t - base)))
    for o in starts:
        ents[o] = dict(jp=cstr(data, o), refs=refs[base + o])
        covered[o:o + len(ents[o]["jp"])] = b"\1" * len(ents[o]["jp"])
    o = 0
    while o < len(data):  # gap scan: NUL-delimited runs nobody points at
        s = cstr(data, o)
        if s and not any(covered[o:o + len(s)]) and text_run(s):
            ents[o] = dict(jp=s, refs=[], notes="no direct ref: in place only")
        o += len(s) + 1
    keys = sorted(ents)
    out = []
    for i, o in enumerate(keys):
        e = ents[o]
        nxt = keys[i + 1] if i + 1 < len(keys) else len(data)
        inside = [p for p in keys[:i] if p + len(ents[p]["jp"]) > o]
        if "max" not in e:
            e["max"] = room(data, o, len(e["jp"]), nxt) if not inside else len(e["jp"])
        r = [fmt_ref(x) for x in e["refs"]] + [fmt_ref(x, img) for img, xs in (extra_refs or {}).get(base + o, [])
                                               for x in xs]
        notes = e.get("notes", "")
        if inside:
            notes = ("tail of %s_%X; " % (name, base + inside[-1]) + notes).strip("; ")
        out.append(dict(id="%s_%X" % (name, base + o), at="%X" % (base + o), jp=sjis.decode(e["jp"]), en="",
                        max=e["max"], refs=r, notes=notes))
    return out


# ---- data files

def pool_block(name, data):
    slots, i = {}, 0
    while True:
        rec = struct.unpack_from("<4I", data, 16 * i)
        if rec[0] == 0xFFFF:
            break
        for k in range(1, 4):
            assert 16 * i < rec[k] < len(data), (name, i)
            slots.setdefault(rec[k], []).append("off@%X" % (16 * i + 4 * k))
        i += 1
    out = []
    for o in sorted(slots):
        s = cstr(data, o)
        assert sjis.encode(sjis.decode(s)) == s
        out.append(dict(id="%s_%04X" % (name, o), at="%04X" % o, jp=sjis.decode(s), en="", max=None,
                        refs=slots[o], notes=""))
    return out


def profiles(d):  # SCR_DATA 118/000: 11 x 0x42A: u32, 3 lines, then 6 x (u16 voice id, 3 lines); lines 0x32
    for r in range(0, len(d), 0x42A):
        yield from ((r + 4 + 0x32 * k, 0x32) for k in range(3))
        yield from ((r + 0x9C + 0x98 * j + 0x32 * k, 0x32) for j in range(6) for k in range(3))


def endings(d):  # SCR_DATA 122/NNN: 12 lines of 0x23
    return ((o, 0x23) for o in range(0, len(d), 0x23))


def squares(d):  # SCR_DATA 210/NNN/001: 90 board squares x 0x28, name first (14 bytes, flags follow)
    return ((o, 14) for o in range(0, len(d), 0x28))


def scenarios(d):  # SCR_DATA 210/012: 22 x 0x920: title 0x1E, 3 x 0x24 intro, 6 x 0x1E win/lose, area names 0x10
    for r in range(0, len(d), 0x920):
        yield r, 0x1E
        yield from ((r + 0x1E + 0x24 * k, 0x24) for k in range(3))
        yield from ((r + 0x8A + 0x1E * k, 0x1E) for k in range(6))
        yield from ((r + o, 0x10) for o in range(0x194, 0x914, 0x10))  # 4 x 30 names; data at +0x914


def facilities(d):  # SCR_DATA 210/NNN/003: 6 x 14, name 11 bytes (as the EXE facility table)
    return ((o, 11) for o in range(0, len(d), 14))


def areas(d):  # SCR_DATA 210/NNN/004: 16 area-name fields of 14 bytes
    return ((o, 14) for o in range(0, len(d), 14))


BOARDS = range(12)
# (block name, files, layout); identical files become one block with copies
LAYOUTS = [("profiles", ["SCR_DATA.BDP/118/000.bin"], profiles),
           ("endings", ["SCR_DATA.BDP/122/%03d.bin" % i for i in range(11)], endings),
           ("squares", ["SCR_DATA.BDP/210/%03d/001.bin" % i for i in BOARDS], squares),
           ("facilities", ["SCR_DATA.BDP/210/%03d/003.bin" % i for i in BOARDS], facilities),
           ("areas", ["SCR_DATA.BDP/210/%03d/004.bin" % i for i in BOARDS], areas),
           ("scenarios", ["SCR_DATA.BDP/210/012.bin", "SCR_DATA.BDP/215/000.bin"], scenarios)]


def field_block(name, data, layout):
    out = []
    for o, n in layout(data):
        f = data[o:o + n]
        s = f.split(b"\0")[0]
        if not s:
            assert not any(f), "%s: data in an empty field at %X" % (name, o)
            continue
        assert len(s) < n and not any(f[len(s):]) and sjis.is_text(s), "%s: field at %X is not text" % (name, o)
        out.append(dict(id="%s_%04X" % (name, o), at="%04X" % o, jp=sjis.decode(s), en="", max=n - 1, refs=[],
                        notes=""))
    return out


# ---- driver

def blocks():
    """Yields (block name, header dict, strings)."""
    exe = read(EXE)
    ovl = overlays()
    seen, bases = {}, {}
    for key, data in ovl.items():
        h = hashlib.sha1(data).digest()
        if h in seen:
            seen[h][1].append(key)
            continue
        base, r = best_base(data)
        if base:
            seen[h] = (key, [])
            bases[key] = (base, r)
    exe_refs = find_refs(exe, EXE_BASE, EXE_BASE + 0x800, EXE_END)
    cross = {}
    for key, data in ovl.items():
        if key in bases:
            img = "o" + key.split("/")[1]
            for t, xs in find_refs(data, bases[key][0], EXE_BASE + 0x800, EXE_END).items():
                cross.setdefault(t, []).append((img, xs))
    yield "exe", dict(file=EXE, copies=[], kind="code", base="%X" % EXE_BASE), \
        code_block("exe", EXE, exe, EXE_BASE, exe_refs, cross)
    for key, copies in seen.values():
        name = "ovl" + key.split("/")[1]
        base, r = bases[key]
        yield name, dict(file=key, copies=copies, kind="code", base="%X" % base), \
            code_block(name, key, ovl[key], base, r)
    for i in range(22, 34):
        key = "PC_DATA.BDP/%03d/000.bin" % i
        yield "pc%03d" % i, dict(file=key, copies=[], kind="pool"), pool_block("pc%03d" % i, read(key))
    for name, keys, layout in LAYOUTS:
        groups = {}
        for key in keys:
            groups.setdefault(hashlib.sha1(read(key)).digest(), []).append(key)
        for key, *copies in groups.values():
            n = name if len(groups) == 1 else "%s%02d" % (name, keys.index(key))
            yield n, dict(file=key, copies=copies, kind="fields"), field_block(n, read(key), layout)


RUN = re.compile(rb"(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x20-\x7e])+")
SCAN = ROOT / "docs/re/jp_runs.json"


def kana_run(s):
    """Loose filter for the scan index (keeps graphics noise like 'ャャズY')."""
    kana = sum(0x3041 <= ord(c) <= 0x30FA for c in s)
    return kana >= max(2, 0.3 * len(s)) and len(set(s)) > 3


def looks_japanese(s):
    """Coverage-test filter: 2+ hiragana, at most 20% ASCII once control codes are dropped. Katakana-only noise
    is common in graphics; katakana-only names sit in the layouts and tables, which the test checks anyway."""
    t = re.sub(r"%\d*[sd]|/P[0-9A-F]{2}|/V%d|/v", "", s)
    hira = sum(0x3041 <= ord(c) <= 0x3093 for c in t)
    return hira >= 2 and sum(ord(c) < 0x80 for c in t) <= 0.2 * len(t) and len(set(t)) > 3


def scan():
    """Every Japanese-looking run on the disc -> docs/re/jp_runs.json {file: [[offset, text]]}, for the coverage
    test (tests/test_text.py). Walks all of work/unpacked (slow: ~170k files)."""
    files = [TREE / EXE] + sorted(p for p in UNP.rglob("*") if p.is_file())
    out = {}
    for p in files:
        if p.suffix == ".bin" and p.with_suffix(".dec").exists():
            continue  # LZ-compressed bytes; the .dec holds the text
        runs = []
        for m in RUN.finditer(p.read_bytes()):
            try:
                s = m.group().decode("cp932")
            except UnicodeDecodeError:
                continue
            if kana_run(s):
                runs.append([m.start(), m.end(), s])
        if runs:
            out[EXE if p.name == EXE else p.relative_to(UNP).as_posix()] = runs
    SCAN.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8", newline="\n")
    print("%d runs in %d files -> %s" % (sum(map(len, out.values())), len(out), SCAN))


def write(name, head, strings, force):
    path = OUT / (name + ".json")
    if path.exists():
        if not force:
            return 0
        old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))["strings"]}
        for e in strings:
            o = old.get(e["id"])
            if o:
                e.update(en=o["en"], notes=o["notes"] or e["notes"], **({"status": o["status"]} if "status" in o else {}))
                if o["jp"] != e["jp"] and o["en"]:
                    e["status"] = "jp-changed"
                    print("jp changed:", e["id"])
    path.write_text(json.dumps(dict(block=name, **head, strings=strings), ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8", newline="\n")
    return 1


def main():
    if "--scan" in sys.argv:
        return scan()
    force = "--force" in sys.argv
    OUT.mkdir(exist_ok=True)
    n = w = 0
    for name, head, strings in blocks():
        n += len(strings)
        w += write(name, head, strings, force)
    print("%d strings, %d block files written" % (n, w))


if __name__ == "__main__":
    main()
