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
OK_CHARS = set(chr(c) for c in range(0x20, 0x7F)) | set(ICONS) | {"　", "\n"}   # \n only where the JP has it (codes check)
# insert.TOKEN with /V on its own: /V ... /v wraps a span ("/V%dゼニーひろったよ！/v", "/Vみんなから%dゼニー/v"),
# so English may put words between /V and the number ("/VIn place %d")
TOKEN = re.compile(r"/P[0-9A-F]{2}|/V|/v|%[-+ 0-9]*[sd]|\n|\[[0-9A-F]{2}\]")
BLANK = insert.BLANK
TOKEN_PX = {"%s": 48, "%d": 18}   # guessed widths of what a code prints
# %s whose source is known: a character name ("%s-san", or these ids), a card name ('"%s"'); widest of each
# domain from script/ (name_px / card_px). An overflow with every known %s at its widest is an error.
NAME_IDS = {"ovl008_800A13D4", "exe_800102BC", "exe_800102D0", "exe_80012048", "ovl008_800A1208",
            "ovl008_800A1220", "ovl010_800A1018"}
# rows left empty on purpose: the box's last line, and the JP row has no codes (the English ends a line early)
BLANK_OK = {"ovl008_800A14D4": "'ます' ending a 3-line square description; the English fits in 2"}
# Exact layout exceptions, reviewed in docs/re/windows.md. Changes require a new review.
PADDING_EXCEPTIONS = {
    "ovl010_800A0DE4": ("カードを", " chooses a card..."),
    "ovl010_800A0E60": ("回復した！！", " HP!!"),
    "ovl010_800A0E7C": ("のダメージを受けた！", " damage taken!"),
    "ovl010_800A0EB4": ("を使った！", " used!"),
    "ovl057_8009F9E0": (" 資産", "Assets"),
}
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


_DOM = {}


def domain_px():
    """Widest text a known %s prints: {'name': character names, 'card': card names (the list tables' English)}."""
    if not _DOM:
        _DOM["name"] = max(px(n) for n in PC.values())
        _DOM["card"] = max(px(e["en"].strip(BLANK)) for b in insert.blocks() for e in b["strings"]
                           if e["en"].strip(BLANK) and windows.box(b, e) == "list_name")
        _DOM["area"] = max(px(e["en"].strip(BLANK)) for b in insert.blocks() for e in b["strings"]
                           if e["en"].strip(BLANK) and windows.box(b, e) == "area")
    return _DOM


def hard_bytes(b, e):
    """Byte budget that relocation can't lift: fixed fields, tables and strings no pointer reaches."""
    return b["kind"] == "fields" or (b["kind"] == "code" and not e["refs"])


def px(en):
    if "\n" in en:
        return max(px(ln) for ln in en.split("\n"))
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
            enf = ("always" if section in ("characters", "places") or "(full)" in ln
                   else "quoted" if section == "cards" else "")
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

def check_line(r, en, gl, near=("", "")):
    """(errors, warnings) for one row's English; near = the English of the rows before and after it."""
    err, warn = [], []
    rid = r.get("id")
    if en == "<blank>":
        if rid not in BLANK_OK:
            err.append("<blank> only for a row in BLANK_OK (an unneeded last line of its box)")
        if TOKEN.findall(r["jp"]) or set(r["jp"]) & set(ICONS):
            err.append("<blank> would drop the JP's codes / icons")
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
    d = domain_px()
    names = en.count("%s") if rid in NAME_IDS else en.count("%s-san")
    cards = en.count('"%s"')
    unknown = en.count("%s") - names - cards
    w = px(en) + (d["name"] - TOKEN_PX["%s"]) * names + (d["card"] - TOKEN_PX["%s"]) * cards
    if rid in {"ovl008_800A0330", "ovl008_800A033C"}:
        # These selectors format an area name, then (mode 10) a literal A-G.
        w = px(en) - en.count("%s") * TOKEN_PX["%s"] + d["area"]
        if rid == "ovl008_800A033C":
            w += max(px(letter) for letter in "ABCDEFG")
        unknown = 0
    if w > r["px"]:   # known %s at their widest, unknown at 48 px; error when over with unknown %s at 24 px
        hard = r["state"] != "guess" and w - 24 * unknown > r["px"]
        (err if hard else warn).append("%dpx > %dpx (%s box, %d names at %d px, %d cards at %d px%s)" % (
            w, r["px"], r["box"], names, d["name"], cards, d["card"], "" if hard else ", estimate"))
    if r["nbytes"] is not None and r["hard"]:   # soft budgets: tools/reloc.py moves the string (build fails if not)
        n = len(sjis.encode(en))
        if n > r["nbytes"]:
            err.append("%d bytes > %d" % (n, r["nbytes"]))
    low = en.lower()
    spans = ("%s %s" % (near[0], en)).lower(), ("%s %s" % (en, near[1])).lower()   # a term split over two lines
    for jp, ten, avoid, enf in gl:
        if has_term(r["jp"], jp):
            t = ten.lower()
            if ((enf == "always" or enf == "quoted" and (r["jp"] == jp or "「%s」" % jp in r["jp"]))
                    and t not in low and not (enf == "always" and any(t in s for s in spans))):
                err.append("glossary: %s -> %s missing" % (jp, ten))
        for a in avoid:
            if re.search(r"\b%s\b" % re.escape(a), en):   # case-sensitive: avoid "Meg-Meg" must pass "Meg-meg"
                err.append("glossary: avoid %r (%s -> %s)" % (a, jp, ten))
    n_san = r["jp"].count("%sさん")   # every name keeps its -san (D1)
    if en.count("%s-san") < n_san:
        err.append("honorific: %d x %%sさん in JP, %d x %%s-san in EN" % (n_san, en.count("%s-san")))
    if re.search(r"(?<![母父許])(?<=[ァ-ヺ一-龥s])さん", r["jp"]) and "-san" not in en:   # not お母さん / 許さん
        warn.append("JP has -san, EN doesn't")
    return err, warn


def read_tsv(p):
    out = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            k, _, v = ln.partition("\t")
            out.setdefault(k.strip(), []).append(v.replace("\\n", "\n"))   # \n = a real line break (debug renderer)
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
    en_of = lambda i: got[rs[i]["id"]][0] if 0 <= i < len(rs) and rs[i]["id"] in got else ""  # noqa: E731
    for i, r in enumerate(rs):
        if r["id"] not in got:
            errs.append("%s: missing" % r["id"])
            continue
        e, w = check_line(r, got[r["id"]][0], gl, (en_of(i - 1), en_of(i + 1)))
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
        lines = ["%s\t%s\t%s\t%s\t%s" % (r["id"], r["speaker"], r["form"], r["limit"], r["jp"].replace("\n", "\\n"))
                 for r in bt]
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
            for i in r["group"]:   # deduped ids can live in other blocks: id = <block>_<address>
                by_block.setdefault(i.rsplit("_", 1)[0], {})[i] = en
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
        out.append("   %s" % (got.get(r["id"], ["(missing)"])[0].replace("\n", "\\n")))
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(path, len(out) // 2, "pairs")


def lint():
    """Every translated string in script/ against the row rules; exit 1 on errors."""
    gl, errs, warns, todo = glossary(), 0, 0, 0
    keep = insert.keep_jp()
    for b in insert.blocks():
        ss = b["strings"]
        for i, e in enumerate(ss):
            if not needs_tl(e, keep):
                continue
            if not e["en"]:
                todo += 1
                errs += 1
                print("ERROR %s: required English translation is empty" % e["id"])
                continue
            near = tuple(ss[j]["en"].strip(BLANK) if 0 <= j < len(ss) else "" for j in (i - 1, i + 1))
            bx = windows.box(b, e)
            lead, c, trail = core(e["jp"])
            m = insert.budget(b, e)
            px_, _, state = windows.BOXES[bx]
            r = dict(id=e["id"], jp=c, box=bx, px=px_, state=state, hard=hard_bytes(b, e),
                     nbytes=None if m is None else m - len(sjis.encode(lead + trail)))
            en = e["en"]
            if (en != " " and core(en)[::2] != (lead, trail)
                    and PADDING_EXCEPTIONS.get(e["id"]) != (e["jp"], en)):
                errs += 1
                print("ERROR %s: leading/trailing blanks differ from Japanese" % e["id"])
            en = "<blank>" if en == " " else en[len(lead):len(en) - len(trail)] if en.startswith(lead) and en.endswith(trail) else en
            er, w = check_line(r, en, gl, near)
            for x in er:
                print("ERROR %s: %s" % (e["id"], x))
            errs += len(er)
            warns += len(w)
    print("lint: %d errors, %d warnings, %d strings untranslated" % (errs, warns, todo))
    return errs == 0 and todo == 0


def selftest():
    r = dict(jp="「%s」を捨てて", box="dialog", px=203, state="measured", hard=False, nbytes=20)
    assert check_line(r, 'Throw away "%s"', [])[0] == []
    assert check_line(r, "Throw away it", [])[0]                       # code lost
    assert check_line(r, 'Toss "%s" 1/2', [])[0]                       # slash
    assert check_line(r, "Toss the %sth", [])[0] == ["ordinal suffix glued to a code"]
    assert check_line(r, "W" * 40 + '"%s"', [])[0]                     # px over
    assert check_line(dict(r, hard=True), 'Throw it all away now, "%s"', [])[0]   # bytes over a fixed field
    assert check_line(dict(r, px=400), 'Throw it all away now, "%s"', [])[0] == []    # soft bytes: warning only
    assert has_term("ミンが", "ミン") and not has_term("タイミング", "ミン")
    gl = [("ジガー", "Jiggar", ["Jigger"], "always"), ("幸運", "Good Luck", [], "quoted")]
    assert check_line(dict(r, jp="ジガー%s"), "Jigger %s", gl)[0]
    assert check_line(dict(r, jp="メグメグ%s"), "Meg-meg %s", [("メグメグ", "Meg-meg", ["Meg-Meg"], "always")])[0] == []
    assert check_line(dict(r, jp="幸運を%s"), "Luck to %s", gl)[0] == []
    assert check_line(dict(r, jp="「幸運」%s"), "Luck %s", gl)[0]
    full = [("天宮", "Heavenly Palace", [], "always")]
    assert check_line(dict(r, jp="早くそいつを天宮から"), "Throw him out of the...", full)[0]
    assert check_line(dict(r, jp="天宮にも"), "sick of the Heavenly", full, ("", "Palace anyway."))[0] == []
    assert ("ジガー", "Jiggar", ["Jigger", "Jigga"], "always") in glossary()
    assert px("%4d") == 24 and px("ab") == font_en.width("ab") and px("ab\nabc") == font_en.width("abc")
    # blanks: only BLANK_OK rows, never over codes
    four = dict(r, jp="%sさん %sさん %sさん %sさん", id="x")
    assert check_line(four, "<blank>", [])[0]
    assert check_line(dict(four, id="ovl008_800A14D4"), "<blank>", [])[0]           # BLANK_OK id, but codes
    assert check_line(dict(r, jp="ます", id="ovl008_800A14D4"), "<blank>", [])[0] == []
    assert check_line(dict(r, jp="ます", id="y"), "<blank>", [])[0]
    # every %sさん keeps -san; names / cards at their widest
    assert any("honorific" in x for x in check_line(four, "%s, %s, %s, %s", [])[0])
    assert any("honorific" in x for x in check_line(four, "%s-san, %s, %s, %s", [])[0])
    n = domain_px()["name"]
    tight = dict(r, jp="所有者  %s", px=px("Owner ") + n, id="ovl008_800A13D4")
    assert check_line(tight, "Owner %s", [])[0] == [] and check_line(dict(tight, px=tight["px"] - 1), "Owner %s", [])[0]
    assert check_line(dict(r, jp="%sさん", px=px("-san") + n - 1), "%s-san", [])[0]    # a name runs over
    assert check_line(dict(r, jp="「%s」", px=px('""') + domain_px()["card"] - 1), '"%s"', [])[0]
    assert check_line(dict(four, px=400), "%s-san, %s-san, %s-san and %s-san", [])[0] == []


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
