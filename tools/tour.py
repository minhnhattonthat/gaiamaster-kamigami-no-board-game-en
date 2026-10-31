"""Cold-boot QA tours, with full-resolution contact sheets and reproducible cases.

python tools/tour.py --only 'card_*'
python tools/tour.py --only 'story_ch0[1-9]'
python tools/tour.py --rom 'rom/GaiaMaster - Kamigami no Board Game (Japan).cue' --out work/qa/tour_jp
Run short batches: each case is foreground and sequential, with a separate emulator output directory.
Review the sheets, then run the skill's qa_gate.py; a successful route is not a visual verdict.
"""
import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from skill import SKILL
from debug.regen import scenes

ROOT = Path(__file__).resolve().parents[1]
EMU = Path(SKILL) / 'scripts/emu.py'
SHEET = Path(SKILL) / 'scripts/sheet.py'
CARDS = [0, 1, 6, 7, 8, 9, 10, 14, 18, 20, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32,
         37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]
BOARD_COMMAND_ROUTE = ('60 -;8 right;90 -;8 right;90 -;8 circle;120 -;8 right;90 -;'
                       '8 right;90 -;8 cross;120 -;8 right;90 -;8 circle;120 -;'
                       '8 right;90 -;8 right;90 -;8 right;90 -')


def cases():
    yield dict(name='intro', variables=["SCENE='intro'"])
    for name, variables, _ in scenes():
        yield dict(name=name, variables=variables)
    for char in range(9):
        yield dict(name=f'prologue_c{char}', variables=["SCENE='story'", 'CH=1', f'CHAR={char}'])
        yield dict(name=f'credits_c{char}', variables=["SCENE='ending_save'", f'CHAR={char}'])
    # Chapters 3 and 7 select alternate banners/scenarios for female characters.
    for chapter in (3, 7):
        yield dict(name=f'story_ch{chapter:02}_tiara', variables=["SCENE='story'", f'CH={chapter}', 'CHAR=1'])
    for card in CARDS:
        yield dict(name=f'card_{card:03}', variables=["SCENE='board_square'", 'SQUARE_KIND=2',
                   'PLAY=450', f'CARD_ART={card}'], extra_script='tools/debug/cardqa.lua', final_only=True)
    for demo in (3, 5, 9, 11, 15, 17, 21, 23):
        yield dict(name=f'bios_{demo:02}', variables=["SCENE='bios'", f'DEMO={demo}'])
    yield dict(name='weapon_display', variables=["SCENE='weapon_display'"],
               save='work/saves/story-ch02.mcd',
               route='60 -;8 r1;100 -;8 r1;100 -;8 r1;100 -;8 r1;100 -')
    yield dict(name='options_pages', variables=["SCENE='options'"],
               route='60 -;8 circle;180 -;8 circle;180 -;8 cross;180 -;8 cross;180 -;'
                     + ';'.join(['8 down;80 -'] * 9))
    yield dict(name='board_commands', variables=["SCENE='board_owned'"],
               route=BOARD_COMMAND_ROUTE)
    yield dict(name='board_story_commands', variables=["SCENE='board_owned'", 'BOARD_STORY=true'],
               route=BOARD_COMMAND_ROUTE)
    yield dict(name='board_redeem', variables=["SCENE='board_owned'"],
               extra_script='tools/debug/menuframeqa.lua', debugger=True, final_only=True,
               route_script='tools/debug/menuframeqa.lua', route_debugger=True,
               route='60 -;8 right;90 -;8 right;90 -;8 circle;120 -;8 right;180 -')
    yield dict(name='board_graph', variables=["SCENE='board_info'"],
               route='60 -;8 right;120 -;8 circle;300 -;8 right;180 -;8 circle;300 -')
    yield dict(name='double_up', variables=["SCENE='board_square'", 'SQUARE_KIND=4', 'PLAY=1500'])
    yield dict(name='purge', variables=["SCENE='board_square'", 'SQUARE_KIND=2',
               'PLAY=2400', 'EVENT_ID=0'], extra_script='tools/debug/cardqa.lua')
    yield dict(name='duel_seal', variables=["SCENE='duel_effect'", 'QUICK_BATTLE=false'],
               extra_scripts=['tools/debug/duelqa.lua', 'tools/debug/sealqa.lua'])
    yield dict(name='duel_return', variables=["SCENE='duel_return'"])
    yield dict(name='bonus_message', variables=["SCENE='board_play'", 'PLAY=18000'],
               extra_script='tools/debug/bonusqa.lua', debugger=True)
    yield dict(name='trial_disclaimer', variables=["SCENE='bios'", 'DEMO=5'],
               extra_script='tools/debug/trialqa.lua')
    for side in (0, 1):
        yield dict(name=f'duel_help{side}', variables=["SCENE='duel_effect'", 'QUICK_BATTLE=false',
                   f'HELP_SIDE={side}'], extra_script='tools/debug/duelhelp.lua')
    # Native chapter results on each distinct board: the Rankings atlas is a
    # separate copy from the world map and save-screen board labels.
    for stage, chapter in enumerate((4, 12, 6, 20, 5, 15, 16)):
        yield dict(name=f'rankings_s{stage}', variables=["SCENE='gameover'", f'CH={chapter}'])


def invoke(command, log):
    result = subprocess.run([sys.executable, '-X', 'utf8', *map(str, command)],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'exit {result.returncode}: {log}')


def start_frame(case, log):
    name = case['name']
    if name == 'intro':
        return 0
    if name == 'bonus_message':
        matches = [int(m[1]) for line in log.splitlines() if 'bonus message selected' in line
                   for m in [re.match(r'f(\d+)', line)] if m]
        if matches:
            return matches[-1] - 20
    if name.startswith('rankings_'):
        matches = [int(m[1]) for line in log.splitlines() if 'mash save screen done' in line
                   for m in [re.match(r'f(\d+)', line)] if m]
        if matches:
            return matches[-1] - 2400
    if name.startswith('duel'):
        matches = [int(m[1]) for line in log.splitlines() if 'mash duel done' in line
                   for m in [re.match(r'f(\d+)', line)] if m]
        if matches:
            return matches[-1] - 120
    if name.startswith('story_ch') and name != 'story_ch01':
        marker = 'save cancelled'
    elif name.startswith('credits_') or name == 'ending_save':
        marker = 'chapter 20 board'
    else:
        marker = 'step 12 fn' if name.startswith('prologue') else None
    if marker:
        matches = [int(m[1]) for line in log.splitlines() if marker in line
                   for m in [re.match(r'f(\d+)', line)] if m]
        if matches:
            return matches[-1]
    # Keep the actual menu arrival, omitting shared boot logos and title transitions.
    return 3600


def run(case, args):
    folder = args.out / case['name']
    folder.mkdir(parents=True, exist_ok=True)
    capture = folder / 'capture'
    state = folder / 'arrival.sstate'
    command = [EMU, args.rom, '--out', capture, '--script', 'tools/debug/warp.lua',
               '--frames', '60000', '--timeout', '300', '--state-out', state]
    if case.get('extra_script'):
        command += ['--script', case['extra_script']]
    if case.get('debugger'):
        command += ['--debugger']
    for script in case.get('extra_scripts', []):
        command += ['--script', script]
    if case.get('save'):
        command += ['--sav', case['save']]
    if not case.get('final_only'):
        command += ['--shot-every', '20']
    for value in case['variables']:
        command += ['--var', value]
    if not args.sheets_only:
        invoke(command, folder / 'emulator.txt')
    log = (capture / 'log.txt').read_text(encoding='utf-8')
    if 'REACHED ' not in log:
        raise RuntimeError(f'warp did not assert arrival: {folder}')
    pictures = [capture / 'final.png'] if case.get('final_only') else [
        p for p in sorted(capture.glob('f*.png')) if p.stem[1:].isdigit()
        and int(p.stem[1:]) >= start_frame(case, log)]
    if case.get('route'):
        after = folder / 'cursor'
        command = [EMU, args.rom, '--out', after, '--state-in', state,
                   '--route-str', case['route'], '--shot-every', '20', '--timeout', '180']
        if case.get('route_script'):
            command += ['--script', case['route_script']]
        if case.get('route_debugger'):
            command += ['--debugger']
        if case.get('save'):
            command += ['--sav', case['save']]
        if not args.sheets_only:
            invoke(command, folder / 'cursor.txt')
        pictures += sorted(p for p in after.glob('f*.png') if p.stem[1:].isdigit())
    if not pictures:
        raise RuntimeError(f'no selected screenshots: {folder}')
    # Only remove this case's previous generated sheet pages, never captures or verdicts.
    for old in folder.glob('sheet*.png'):
        old.unlink()
    # Long credits/gameplay captures exceed Windows' command-line limit if each
    # PNG is an argument. A directory of hard links preserves order without
    # copying image data; frames.tsv retains the original capture filenames.
    links = folder / 'frames'
    links.mkdir(exist_ok=True)
    assert links.resolve().is_relative_to(args.out.resolve())
    for old in links.glob('f[0-9]*.png'):
        old.unlink()
    index = []
    for number, picture in enumerate(pictures):
        target = links / f'f{number:08}.png'
        os.link(picture, target)
        index.append(f'{target.name}\t{picture.as_posix()}')
    (folder / 'frames.tsv').write_text('\n'.join(index) + '\n', encoding='utf-8')
    invoke([SHEET, links, '--div', '1', '--cols', '4', '--max', '16', '--changed', '0.02',
            '--out', folder / 'sheet.png'], folder / 'sheets.txt')
    (folder / 'case.json').write_text(json.dumps(case, indent=2) + '\n', encoding='utf-8')
    print(f"ok {case['name']}: {len(list(folder.glob('sheet*.png')))} sheets", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only', action='append', help='repeatable glob; default is all cases')
    ap.add_argument('--exclude', action='append', default=[], help='repeatable glob to omit redundant cases')
    ap.add_argument('--rom', default='build/gaiamaster_en.cue')
    ap.add_argument('--out', type=Path, default=Path('work/qa/tour'))
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--sheets-only', action='store_true', help='regenerate sheets from an existing successful capture')
    args = ap.parse_args()
    todo = [case for case in cases() if any(fnmatch.fnmatch(case['name'], pattern)
                                          for pattern in (args.only or ['*']))
            and not any(fnmatch.fnmatch(case['name'], pattern) for pattern in args.exclude)]
    if args.list:
        print('\n'.join(case['name'] for case in todo))
        return
    if not todo:
        ap.error('no cases matched')
    failed = []
    for case in todo:
        try:
            run(case, args)
        except RuntimeError as error:
            failed.append(case['name'])
            print(f"FAIL {case['name']}: {error}", flush=True)
    print(f'{len(todo) - len(failed)}/{len(todo)} routes passed; visual review still required')
    sys.exit(bool(failed))


if __name__ == '__main__':
    main()
