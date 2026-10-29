"""batches.py: translation batches (docs/translator-brief.md, skill references/translation.md).

    python -X utf8 tools/batches.py split             work/tl/bNNN.tsv + build/terms_bNNN.txt (refuses if any exist)
    python -X utf8 tools/batches.py check bNNN..      validate work/tl/bNNN.out.tsv; exit 1 on any error
    python -X utf8 tools/batches.py merge bNNN..      checked batches -> script/*.json "en" (refuses a failing batch)
    python -X utf8 tools/batches.py pairs bNNN OUT    reviewer pairs file
    python -X utf8 tools/batches.py width "text" [--box dialog]   px per line as the game draws it
    python -X utf8 tools/batches.py lint              every en in script/ against the same rules (check.py runs it)

A row is one line of one box (the game draws each string as its own line). Name-like boxes (squares, areas, card
names...) are deduplicated: one row per distinct Japanese, merged into every id with that text. The row's JP has its
leading/trailing blanks stripped; merge puts the JP's blanks back around the English.
"""
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font_en  # noqa: E402
import insert  # noqa: E402
import sjis  # noqa: E402
import windows  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
BUILD = ROOT / "build"
GLOSSARY = ROOT / "glossary.md"
DEDUPE = {"map_info", "area", "facility", "list_name", "scenario_title", "results_col", "card_title"}
FORM = {"dialog": "dlg", "story": "dlg", "char_desc": "narration", "ending": "narration", "card": "menu",
        "card_title": "menu", "credits": "name", "results_col": "menu", "scenario_title": "name"}
PC = {22: "Belial", 23: "Jiggar", 24: "Sinbad", 25: "Hayate", 26: "Agathe", 27: "Meg-meg", 28: "Goliath",
      29: "Tiara", 30: "Galahad", 31: "Son Gokuh", 32: "Yasutsuna", 33: "Dante"}
ICONS = "≠≦≧├┤┌┐└┘★○×←→↓∞"          # JP font cells that still draw (icons, buttons, arrows)
OK_CHARS = set(chr(c) for c in range(0x20, 0x7F)) | set(ICONS) | {"　"}
TOKEN = insert.TOKEN
BLANK = insert.BLANK
TOKEN_PX = {"%s": 48, "/V%s": 48, "/V%d": 6, "/V": 6, "/v": 6, "%d": 18}   # guessed widths of what a code prints
ROWS_SOFT, ROWS_HARD, CHARS_SOFT = 120, 160, 3000
SPLIT = re.compile(r"[。！？」…」）～＠!?.]$")


def core(jp):
    c = jp.strip(BLANK)
    lead = jp[:len(jp) - len(jp.lstrip(BLANK))]
    return lead, c, jp[len(lead) + len(c):]


def needs_tl(e, keep):
    return bool(insert.JP.search(e["jp"])) and not e["notes"].startswith("tail of") and e["id"] not in keep


def pc_order(b):
    """Voice pool strings in record order (id, line 1..3), then the unreferenced ones; {id: 'voice N line L'}."""
    data = insert.read(b["file"])
    by = {int(e["at"], 16): e for e in b["strings"]}
    order, where, i = [], {}, 0
    while True:
        r = struct.unpack_from("<4I", data, 16 * i)
        i += 1
        if r[0] == 0xFFFF:
            break
        for n, o in enumerate(r[1:]):
            e = by.get(o)
            if e and e["id"] not in where:
                order.append(e)
                where[e["id"]] = "voice %d line %d" % (r[0], n + 1)
    order += [e for e in b["strings"] if e["id"] not in where]
    return order, where


def rows():
    """Every row to translate, in batch order: dicts id, block, entry, box, speaker, form, limit, jp, group."""
    keep, out, seen = insert.keep_jp(), [], {}
    for b in insert.blocks():
        ents, where = (pc_order(b) if b["kind"] == "pool" else (b["strings"], {}))
        for e in ents:
            if not needs_tl(e, keep):
                continue
            bx = windows.box(b, e)
            lead, c, trail = core(e["jp"])
            key = (bx, c)
            if bx in DEDUPE and key in seen:
                seen[key]["group"].append(e["id"])
                continue
            px, lines, state = windows.BOXES[bx]
            m = insert.budget(b, e)
            nb = None if m is None else m - len(sjis.encode(lead + trail))
            spk = ""
            if b["kind"] == "pool":
                spk = "%s (%s)" % (PC[int(b["block"][2:])], where.get(e["id"], "unused"))
            elif b["block"] == "profiles":
                spk = "narrator (char select)"
            r = dict(id=e["id"], block=b, entry=e, box=bx, speaker=spk, form=FORM.get(bx, "name" if bx in DEDUPE else "dlg"),
                     limit="%dpx%s%s" % (px, "" if nb is None else " %dB" % nb, "?" if state == "guess" else ""),
                     jp=c, group=[e["id"]], px=px, state=state, nbytes=nb, hard=hard_bytes(b, e))
            seen[key] = r
            out.append(r)
    return out


def hard_bytes(b, e):
    """Byte budget that relocation can't lift: fixed fields, tables and strings no pointer reaches."""
    return b["kind"] == "fields" or (b["kind"] == "code" and not e["refs"])


def px(en):
    w = 0
    for t in TOKEN.findall(en):
        m = re.fullmatch(r"%[-+ 0]*(\d+)d", t)
        w += int(m.group(1)) * 6 if m else TOKEN_PX.get(t, 0)
    g = font_en.glyphs()
    return w + sum(12 if ch == "　" or ch in ICONS else font_en.SPACE_W if ch == " " else g[ch][1]
                   for ch in TOKEN.sub("", en) if ch in OK_CHARS)


# ---- glossary ----

def glossary():
    """[(jp, en, avoid, enforced)] from the tables in glossary.md; enforced = Characters / Places / Cards tables."""
    out, section = [], ""
    for ln in GLOSSARY.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            section = ln[3:].lower()
        cells = [c.strip() for c in ln.strip().strip("|").split("|")] if ln.startswith("|") else []
        if len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-"):
            enf = "always" if section in ("characters", "places") else "quoted" if section == "cards" else ""
            out.append((cells[0], cells[1], [a.strip() for a in (cells[4] if len(cells) > 4 else "").split(",") if a.strip()], enf))
    return out


KANA = r"[ァ-ヺー]"


def has_term(jp, term):
    """Whole-run match for katakana terms (ミン never matches inside タイミング); plain substring otherwise."""
    if re.fullmatch(KANA + "+", term):
        return re.search(r"(?<![ァ-ヺー])%s(?![ァ-ヺー])" % re.escape(term), jp) is not None
    return term in jp


def terms_for(jps, gl):
    return [g for g in gl if any(has_term(j, g[0]) for j in jps)]


# ---- checks ----

def check_line(r, en, gl):
    """(errors, warnings) for one row's English."""
    err, warn = [], []
    if en == "<blank>":
        return err, warn
    if not en.strip():
        return ["empty (write <blank> for a line left empty on purpose)"], warn
    bad = sorted(set(ch for ch in en if ch not in OK_CHARS))
    if bad:
        err.append("characters not allowed: %s" % " ".join(bad))
    if "\\u" in en or "\t" in en:
        err.append("escape or tab")
    if Counter(TOKEN.findall(en)) != Counter(TOKEN.findall(r["jp"])):
        err.append("codes differ: JP %s EN %s" % (TOKEN.findall(r["jp"]), TOKEN.findall(en)))
    rest = TOKEN.sub("", en)
    for ch, why in (("/", "'/' is the control escape"), ("%", "'%' only as a %s/%d code"),
                    ("[", "no square brackets"), ("]", "no square brackets")):
        if ch in rest:
            err.append(why)
    for ic in set(r["jp"]) & set("≠≦≧├┤┌┐└┘"):
        if en.count(ic) != r["jp"].count(ic):
            err.append("icon %s count differs" % ic)
    if re.search(r"(%[-+ 0-9]*[sd]|/V%[sd])(st|nd|rd|th)\b", en):
        err.append("ordinal suffix glued to a code")
    w = px(en)
    if w > r["px"]:
        (warn if r["state"] == "guess" else err).append("%dpx > %dpx (%s box)" % (w, r["px"], r["box"]))
    if r["nbytes"] is not None:
        n = len(sjis.encode(en))
        if n > r["nbytes"]:
            (err if r["hard"] else warn).append("%d bytes > %d%s" % (n, r["nbytes"], "" if r["hard"] else
                                                                        " (relocation can take it)"))
    low = en.lower()
    for jp, ten, avoid, enf in gl:
        if has_term(r["jp"], jp):
            if (enf == "always" or enf == "quoted" and (r["jp"] == jp or "「%s」" % jp in r["jp"])) and ten.lower() not in low:
                err.append("glossary: %s -> %s missing" % (jp, ten))
        for a in avoid:
            if re.search(r"\b%s\b" % re.escape(a.lower()), low):
                err.append("glossary: avoid %r (%s -> %s)" % (a, jp, ten))
    if re.search(r"[ァ-ヺ一-龥%]さん", r["jp"]) and "-san" not in en:
        warn.append("JP has -san, EN doesn't")
    return err, warn


def read_tsv(p):
    out = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            k, _, v = ln.partition("\t")
            out.setdefault(k.strip(), []).append(v)
    return out


def batch_rows(name):
    ids = [ln.split("\t", 1)[0] for ln in (TL / (name + ".tsv")).read_text(encoding="utf-8").splitlines()
           if ln.strip() and not ln.startswith("#")]
    by = {r["id"]: r for r in rows()}
    return [by[i] for i in ids if i in by]


def check(name, quiet=False):
    rs, gl = batch_rows(name), glossary()
    out = TL / (name + ".out.tsv")
    if not out.exists():
        print("%s: no %s" % (name, out.name))
        return False
    got = read_tsv(out)
    errs = []
    want = [r["id"] for r in rs]
    for k in got:
        if k not in want:
            errs.append("%s: not in the batch" % k)
        elif len(got[k]) > 1:
            errs.append("%s: given %d times" % (k, len(got[k])))
    nwarn = 0
    for r in rs:
        if r["id"] not in got:
            errs.append("%s: missing" % r["id"])
            continue
        e, w = check_line(r, got[r["id"]][0], gl)
        errs += ["%s: %s" % (r["id"], x) for x in e]
        nwarn += len(w)
        if not quiet:
            for x in w:
                print("WARN %s: %s" % (r["id"], x))
    for x in errs:
        print("ERROR", x)
    print("%s: %s (%d rows, %d errors, %d warnings)" % (name, "OK" if not errs else "FAIL", len(rs), len(errs), nwarn))
    return not errs


def split():
    TL.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    if list(TL.glob("b*.tsv")):
        sys.exit("work/tl already has batches: refusing to renumber (move them away first)")
    gl, batches, cur, chars = glossary(), [], [], 0
    for r in rows():
        if cur and (len(cur) >= ROWS_HARD or (len(cur) >= ROWS_SOFT or chars >= CHARS_SOFT)
                    and (SPLIT.search(cur[-1]["jp"]) or cur[-1]["block"] is not r["block"])):
            batches.append(cur)
            cur, chars = [], 0
        cur.append(r)
        chars += len(r["jp"])
    batches.append(cur)
    for n, bt in enumerate(batches, 1):
        name = "b%03d" % n
        lines = ["%s\t%s\t%s\t%s\t%s" % (r["id"], r["speaker"], r["form"], r["limit"], r["jp"]) for r in bt]
        (TL / (name + ".tsv")).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        t = terms_for([r["jp"] for r in bt], gl)
        (BUILD / ("terms_%s.txt" % name)).write_text(
            "".join("%s -> %s%s\n" % (j, e, "  (avoid: %s)" % ", ".join(a) if a else "") for j, e, a, _ in t),
            encoding="utf-8", newline="\n")
        print(name, len(bt), "rows", sum(len(r["jp"]) for r in bt), "chars", bt[0]["id"], "..", bt[-1]["id"])


def merge(names):
    by_block = {}
    for name in names:
        if not check(name, quiet=True):
            sys.exit("%s fails its check: not merged" % name)
        got = read_tsv(TL / (name + ".out.tsv"))
        for r in batch_rows(name):
            en = got[r["id"]][0]
            for i in r["group"]:
                by_block.setdefault(r["block"]["block"], {})[i] = en
    n = 0
    for p in sorted(insert.SCRIPT.glob("*.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        new = by_block.get(b["block"])
        if not new:
            continue
        for e in b["strings"]:
            if e["id"] in new:
                lead, _, trail = core(e["jp"])
                en = new[e["id"]]
                e["en"] = " " if en == "<blank>" else lead + en + trail
                n += 1
        p.write_text(json.dumps(b, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("merged", n, "strings from", len(names), "batches")


def pairs(name, path):
    got = read_tsv(TL / (name + ".out.tsv"))
    out = []
    for r in batch_rows(name):
        out.append(">> %s [%s %s%s] | %s" % (r["id"], r["box"], r["limit"], (" " + r["speaker"]) if r["speaker"] else "", r["jp"]))
        out.append("   %s" % (got.get(r["id"], ["(missing)"])[0]))
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(path, len(out) // 2, "pairs")


def lint():
    """Every translated string in script/ against the row rules; exit 1 on errors."""
    gl, errs, warns = glossary(), 0, 0
    keep = insert.keep_jp()
    for b in insert.blocks():
        for e in b["strings"]:
            if not e["en"] or not needs_tl(e, keep):
                continue
            bx = windows.box(b, e)
            lead, c, trail = core(e["jp"])
            m = insert.budget(b, e)
            px_, _, state = windows.BOXES[bx]
            r = dict(jp=c, box=bx, px=px_, state=state, hard=hard_bytes(b, e),
                     nbytes=None if m is None else m - len(sjis.encode(lead + trail)))
            en = e["en"]
            en = "<blank>" if en == " " else en[len(lead):len(en) - len(trail)] if en.startswith(lead) and en.endswith(trail) else en
            er, w = check_line(r, en, gl)
            for x in er:
                print("ERROR %s: %s" % (e["id"], x))
            errs += len(er)
            warns += len(w)
    print("lint: %d errors, %d warnings" % (errs, warns))
    return errs == 0


def selftest():
    r = dict(jp="「%s」を捨てて", box="dialog", px=203, state="measured", hard=False, nbytes=20)
    assert check_line(r, 'Throw away "%s"', [])[0] == []
    assert check_line(r, "Throw away it", [])[0]                       # code lost
    assert check_line(r, 'Toss "%s" 1/2', [])[0]                       # slash
    assert check_line(r, "Toss the %sth", [])[0] == ["ordinal suffix glued to a code"]
    assert check_line(r, "W" * 40 + '"%s"', [])[0]                     # px over
    assert check_line(dict(r, hard=True), 'Throw it all away now, "%s"', [])[0]   # bytes over a fixed field
    assert check_line(r, 'Throw it all away now, "%s"', [])[0] == []    # soft bytes: warning only
    assert has_term("ミンが", "ミン") and not has_term("タイミング", "ミン")
    gl = [("ジガー", "Jiggar", ["Jigger"], "always"), ("幸運", "Good Luck", [], "quoted")]
    assert check_line(dict(r, jp="ジガー%s"), "Jigger %s", gl)[0]
    assert check_line(dict(r, jp="幸運を%s"), "Luck to %s", gl)[0] == []
    assert check_line(dict(r, jp="「幸運」%s"), "Luck %s", gl)[0]
    assert ("ジガー", "Jiggar", ["Jigger", "Jigga"], "always") in glossary()
    assert px("%4d") == 24 and px("ab") == font_en.width("ab")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "help"
    if cmd == "split":
        split()
    elif cmd == "check":
        sys.exit(0 if all([check(n) for n in a[1:]]) else 1)
    elif cmd == "merge":
        merge(a[1:])
    elif cmd == "pairs":
        pairs(a[1], a[2])
    elif cmd == "width":
        for ln in a[1].split("\\n"):
            print(px(ln), "px", len(sjis.encode(ln)), "bytes |", ln)
        if "--box" in a:
            print("budget:", windows.BOXES[a[a.index("--box") + 1]])
    elif cmd == "lint":
        sys.exit(0 if lint() else 1)
    elif cmd == "selftest":
        selftest()
        print("ok")
    else:
        print(__doc__)
