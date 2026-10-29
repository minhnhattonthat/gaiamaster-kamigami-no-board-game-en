"""Shift-JIS text runs in every file under an unpacked tree, kana-weighted to drop graphics noise.

    python -X utf8 tools/jpscan_tree.py work/unpacked > work/jp_all.txt

Prints per-archive totals, then one line per file: run count, path, (first run, last run, total chars).
"""
import collections
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from skill import SKILL  # noqa: E402

sys.path.insert(0, str(Path(SKILL) / 'scripts'))
from jpscan import sjis_runs  # noqa: E402


def good(s):
    return sum(0x3041 <= ord(c) <= 0x30FA for c in s) >= max(2, len(s) * 0.3) and len(set(s)) > 3


def main(root):
    root = Path(root)
    per, samples = collections.Counter(), {}
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        runs = [r for r in sjis_runs(p.read_bytes(), 3) if good(r[1])]
        if runs:
            k = str(p.relative_to(root))
            per[k] = len(runs)
            samples[k] = (runs[0][1][:30], runs[-1][1][:30], sum(len(r[1]) for r in runs))
    top, topn = collections.Counter(), collections.Counter()
    for k, n in per.items():
        t = k.split(os.sep)[0]
        top[t] += n
        topn[t] += 1
    for t, n in top.most_common():
        print(t, 'files', topn[t], 'runs', n)
    print()
    for k, n in sorted(per.items()):
        print(n, k, samples[k])


if __name__ == '__main__':
    main(sys.argv[1])
