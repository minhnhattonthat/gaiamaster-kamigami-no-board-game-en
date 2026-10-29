"""insert.py: script/*.json -> build edits (tools/build.py keys), with the engine patch on the EXE.

    edits(mode="en"|"marker", qa={id: text}) -> ({key: bytes}, write log, {id: marker})

- en: an entry's `en` replaces its jp; empty en keeps the Japanese.
- marker: every entry with Japanese becomes "[N]" (N = base-36 index over all entries in id order) + filler
  letters up to the Japanese line's pixel width, keeping its control codes and leading/trailing blanks; cut to the
  entry's byte budget. build/marker_ids.tsv maps N back to the id.
- qa: per-id overrides on top of either mode (stress lines for the width gate).
Code and field strings are written in place: the new bytes + NUL, then zeros over the rest of the old string only
(never past it: field tails can hold data). Longer text than `max` is an error in en mode (relocation: phase 7)
and cut in marker mode. Pools (PC_DATA voice lines) are rebuilt: strings re-laid 4-aligned, offsets remapped.
"""
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import engine  # noqa: E402
import font_en  # noqa: E402
import sjis  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
UNP = ROOT / "work/unpacked"
TREE = ROOT / "work/disc/tree"
EXE = "SLPS_020.75"
JP = re.compile(r"[぀-ヿ㐀-鿿！-ﾟ]")
TOKEN = re.compile(r"/P[0-9A-F]{2}|/V%[sd]|/V|/v|%[-+ 0-9]*[sd]|\n|\[[0-9A-F]{2}\]")
BLANK = " 　"
FILLER = "abcdefghijklmnopqrstuvwxyz"
# byte budgets tighter than the extractor's max: facility name byte 10 may be data (docs/re/text.md)
SAFE_MAX = {"facilities": 9, "exe_80011E": 9}


def read(key):
    return (TREE / key if key == EXE else UNP / key).read_bytes()


def blocks():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(SCRIPT.glob("*.json"))]


def b36(n):
    s = ""
    while True:
        n, r = divmod(n, 36)
        s = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[r] + s
        if not n:
            return s


def jp_px(s):
    s = TOKEN.sub("", s)
    return sum(8 if ord(c) < 0x80 else 12 for c in s)


def budget(block, e):
    m = e["max"]
    for k, v in SAFE_MAX.items():
        if m is not None and (block["block"].startswith(k) or e["id"].startswith(k)):
            m = min(m, v)
    return m


def fit(s, nbytes):
    """Cut s (from the end of its core text) to nbytes encoded."""
    while len(sjis.encode(s)) > nbytes:
        s = s[:-1]
    return s


def marker(e, tag, nbytes):
    jp = e["jp"]
    core = jp.strip(BLANK)
    lead, trail = jp[:len(jp) - len(jp.lstrip(BLANK))], jp[len(jp.rstrip(BLANK)):]
    toks = "".join(TOKEN.findall(core))
    head = "[%s]" % tag
    g = font_en.glyphs()
    target = jp_px(core)
    body = head
    while font_en.width(body, g) < target:
        body += FILLER[(len(body) - len(head)) % 26]
    fixed = len(sjis.encode(lead + toks + trail))
    if nbytes is not None and fixed + len(head) > nbytes:   # tiny slot: the bare tag, then whatever fits
        body = tag
    if nbytes is not None:
        body = fit(body, max(0, nbytes - fixed))
    if sjis.ESC.match(body):   # "[5E]" would encode as the byte 0x5E: escape the bracket
        body = "[5B]" + body[1:]
    return lead + body + toks + trail


def keep_jp():
    """script/keep_jp.txt: ids that stay Japanese (password keys and grid...), {id: reason}."""
    p = SCRIPT / "keep_jp.txt"
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    return dict(ln.split(" ", 1) for ln in lines if ln.strip() and not ln.startswith("#"))


def texts(mode, qa):
    """{id: new text} and {tag: id}."""
    out, tags, n, keep = {}, {}, 0, keep_jp()
    for b in blocks():
        for e in b["strings"]:
            tag = b36(n)
            n += 1
            if e["id"] in qa:
                out[e["id"]] = qa[e["id"]]
            elif mode == "en" and e["en"]:
                out[e["id"]] = e["en"]
            elif (mode == "marker" and JP.search(e["jp"]) and not e["notes"].startswith("tail of")
                  and e["id"] not in keep):
                out[e["id"]] = marker(e, tag, budget(b, e))
                tags[tag] = e["id"]
    return out, tags


def put(data, o, new, old, by, log, key):
    assert data[o:o + len(old)] == old, "%s %s @%X: original bytes differ" % (key, by, o)
    log.append("%s %X %s %s %s" % (key, o, bytes(data[o:o + len(new)]).hex(), bytes(new).hex(), by))
    data[o:o + len(new)] = new


def in_place(block, data, base, new, log, mode):
    key = block["file"]
    for e in block["strings"]:
        if e["id"] not in new:
            continue
        o = int(e["at"], 16) - base
        old = sjis.encode(e["jp"])
        b = sjis.encode(new[e["id"]])
        m = budget(block, e)
        if len(b) > m:
            if mode != "marker":
                sys.exit("%s: %d bytes, budget %d in place (relocation not implemented yet)" % (e["id"], len(b), m))
            b = sjis.encode(fit(new[e["id"]], m))
        put(data, o, b + bytes(max(1, len(old) + 1 - len(b))), old, e["id"], log, key)


def pool(block, data, new, log):
    """PC_DATA voice pool: header records (id, off, off, off) up to the 0xFFFF one, then strings (with unreferenced
    bytes between some). A new string goes in place when it fits before the next byte in use, else at the end of
    the file (4-aligned) with every record offset to it moved."""
    key = block["file"]
    recs, i = [], 0
    while True:
        recs.append(struct.unpack_from("<4I", data, 16 * i))
        i += 1
        if recs[-1][0] == 0xFFFF:
            break
    out = bytearray(data)
    moved = {}
    for e in block["strings"]:
        if e["id"] not in new:
            continue
        o, old, b = int(e["at"], 16), sjis.encode(e["jp"]), sjis.encode(new[e["id"]])
        room = len(old)
        while o + room + 1 < len(data) and data[o + room + 1] == 0:
            room += 1
        if len(b) <= room:
            put(out, o, b + bytes(max(1, len(old) + 1 - len(b))), old, e["id"], log, key)
        else:
            if out[-1]:
                out.append(0)
            while len(out) % 4:
                out.append(0)
            moved[o] = len(out)
            log.append("%s %X - %s %s (moved from %X)" % (key, len(out), b.hex(), e["id"], o))
            out += b + b"\0"
    for i, r in enumerate(recs):
        if any(x in moved for x in r[1:]):
            struct.pack_into("<4I", out, 16 * i, r[0], *(moved.get(x, x) for x in r[1:]))
    return bytes(out)


def edits(mode="en", qa=None):
    new, tags = texts(mode, qa or {})
    out, log = {}, []
    for b in blocks():
        key = b["file"]
        if key == EXE:
            data, elog = engine.patch(read(EXE))
            log += elog
        else:
            data, olog = engine.patch_overlay(key, read(key))
            log += olog
        if not any(e["id"] in new for e in b["strings"]):
            if key == EXE or key in engine.OVERLAYS:
                out[key] = data
            continue
        if b["kind"] == "pool":
            data = pool(b, data, new, log)
        else:
            data = bytearray(data)
            in_place(b, data, int(b["base"], 16) if b["kind"] == "code" else 0, new, log, mode)
            data = bytes(data)
        for k in [key] + b["copies"]:
            out[k] = data
    return out, log, tags


if __name__ == "__main__":
    o, lg, t = edits(sys.argv[1] if len(sys.argv) > 1 else "marker")
    print(len(o), "files,", len(lg), "writes,", len(t), "markers")
