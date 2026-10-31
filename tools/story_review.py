"""Generate complete, deterministic story-review inputs; never generate verdicts.

Scenario records are in campaign order (20 chapters, then two female variants).
The shared cinematic overlay is ordered by each call site's instruction address,
including repeated lines. Branches remain alternatives, not a claimed linear route.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/qa/story/chapters'


def block(name):
    return json.loads((ROOT / 'script' / f'{name}.json').read_text(encoding='utf-8'))


def pair(row, context):
    return f">> {row['id']} | {context} | {row['jp']}\n{row['en'] or row['jp']}\n"


def documents():
    scenarios = block('scenarios')['strings']
    for chapter in range(22):
        name = f'chapter{chapter + 1:02}' if chapter < 20 else ('chapter03_female' if chapter == 20 else 'chapter07_female')
        rows = [r for r in scenarios if int(r['at'], 16) // 0x920 == chapter]
        title = rows[0]['en']
        intro = f'{name}: {title}\nBelial introduces the board; objectives and place names follow.\n'
        if chapter == 0:
            intro += 'Preceded by the chosen character opening in cinematics.txt.\n'
        if chapter == 19:
            intro += 'Followed by final_038..048 and character ending in cinematics.txt.\n'
            intro += 'epilogue_00..10 contain separate rank outcomes, not successive story scenes.\n'
        yield name, intro + ''.join(pair(r, 'Belial / board rules') for r in rows)
    rows = []
    for row in block('ovl033')['strings']:
        refs = [int(r.split('@')[1].split('/')[0], 16) for r in row['refs'] if r.startswith('lui@')]
        for offset in refs or [0xFFFFFFFF]:
            rows.append((offset, row))
    yield 'cinematics', ('All character openings, endings and credits; call-site order.\n'
                         'Branch alternatives and shared lines are retained; speaker is inferred from context.\n'
                         + ''.join(pair(r, f'callsite {o:08X}') for o, r in sorted(rows, key=lambda x: x[0])))
    for n in range(38, 49):
        b = block(f'ovl{n:03}')
        rows = []
        for row in b['strings']:
            for ref in row['refs'] or ['none@FFFFFFFF']:
                rows.append((int(ref.split('@')[1].split('/')[0], 16), row))
        yield f'final_{n:03}', f'Final confrontation overlay {n}; branch alternatives in call-site order.\n' + ''.join(
            pair(r, f'callsite {o:08X}') for o, r in sorted(rows, key=lambda x: x[0]))
    for n in range(11):
        yield f'epilogue_{n:02}', ('Four alternative rank outcomes, not one continuous story.\n'
                                  + ''.join(pair(r, f'character {n} rank {int(r["at"], 16) // 0x69 + 1}')
                                            for r in block(f'endings{n:02}')['strings']))


def generate(out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    for name, text in documents():
        (out / f'{name}.txt').write_text(text, encoding='utf-8', newline='\n')
    print(f'{len(list(documents()))} complete story documents generated in {out}')


if __name__ == '__main__':
    generate()
