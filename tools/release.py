"""Build and verify a local patch+README zip. Never publishes anything.

Default runs the entire cold-boot tour; --skip-tour reuses reviewed captures,
but still requires their manifest hashes and this exact BIN in the QA seal.
After reviewing a changed build, update docs/re/release-qa.json explicitly.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

import check_rom
import release_scan
import story_review
from skill import SKILL

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'work/qa'
BIN = ROOT / 'build/gaiamaster_en.bin'
CUE = BIN.with_suffix('.cue')


def digest(path, algorithm='sha256'):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def hashes(path):
    result = {name: digest(path, name) for name in ('md5', 'sha1', 'sha256')}
    crc = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            crc = zlib.crc32(chunk, crc)
    return dict(result, crc32=f'{crc:08X}', size=path.stat().st_size)


def run(*args):
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)


def python(*args):
    run(sys.executable, '-X', 'utf8', *args)


def require_polish(path):
    if re.search(r'^\s*- \[ \]', path.read_text(encoding='utf-8'), re.M):
        raise ValueError('docs/polish.md has unfinished items')


def qa_manifests(root=QA):
    manifests = sorted(root.rglob('manifest.tsv'))
    required = {root / 'manifest.tsv', root / 'story/manifest.tsv'}
    if not required.issubset(manifests):
        raise ValueError('visual and story manifests are both required')
    return manifests


def check_seal(seal_path, image, manifests):
    seal = json.loads(seal_path.read_text(encoding='utf-8'))
    if seal['bin_sha1'] != digest(image, 'sha1'):
        raise ValueError('built BIN has no matching reviewed-build QA seal')
    current = {p.relative_to(ROOT).as_posix(): digest(p) for p in manifests}
    if seal['manifests_sha256'] != current:
        raise ValueError('QA manifests differ from the reviewed-build seal')


def make_zip(path, patch, readme):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as archive:
        archive.write(patch, patch.name)
        archive.write(readme, 'README.txt')
    with zipfile.ZipFile(path) as archive:
        if set(archive.namelist()) != {patch.name, 'README.txt'} or archive.testzip():
            raise ValueError('release zip contents/CRC verification failed')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version', default='0.1', help='local release version (default: 0.1)')
    ap.add_argument('--force', action='store_true', help='replace this version after all gates pass')
    ap.add_argument('--skip-tour', action='store_true', help='reuse exact reviewed captures; all QA gates still run')
    args = ap.parse_args(argv)
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', args.version):
        ap.error('version must be numeric X.Y or X.Y.Z')
    name = f'GaiaMaster_EN_v{args.version}'
    folder = ROOT / 'release' / f'v{args.version}'
    outputs = [folder / f'{name}.xdelta', folder / 'README.txt', folder / f'{name}.zip', folder / 'verification.json']
    if not args.force and any(p.exists() for p in outputs):
        ap.error('version files already exist; use --force to replace after verification')
    patcher = shutil.which('xdelta3')
    if not patcher:
        ap.error('xdelta3 is required on PATH')
    check_rom.check()
    original = next(ROOT / line.split(None, 1)[1].strip().lstrip('*')
                    for line in (ROOT / 'rom.sha1').read_text().splitlines() if line.endswith('.bin'))
    python('tools/build.py')
    python('tools/check.py')
    python(Path(SKILL) / 'scripts/emu.py', CUE, '--out', QA / 'smoke-release',
           '--route', 'tools/routes/boot.txt', '--smoke')
    scan_dir = ROOT / 'work/release-scan'
    scan_dir.mkdir(parents=True, exist_ok=True)
    # A new extraction prevents a stale or missing file from satisfying the audit.
    with tempfile.TemporaryDirectory(prefix='disc-', dir=scan_dir) as temporary:
        tree = Path(temporary) / 'tree'
        run(ROOT / 'tools/mkpsxiso/dumpsxiso.exe', '-x', tree, '-s', Path(temporary) / 'layout.xml', CUE)
        targets = release_scan.scan(tree, scan_dir / 'audit')
    if not args.skip_tour:
        python('tools/tour.py')
    story_review.generate()
    gate = Path(SKILL) / 'scripts/qa_gate.py'
    if not args.skip_tour:
        python(gate, 'init', QA / 'manifest.tsv', QA / 'tour')
    # Regenerate story hashes after reading the current source. Review cannot
    # survive a changed chapter just because an old pairs file was left behind.
    python(gate, 'init', QA / 'story/manifest.tsv', story_review.OUT, '--glob', '*.txt')
    manifests = qa_manifests()
    for manifest in manifests:
        python(gate, 'check', manifest, manifest.parent / 'verdicts')
    require_polish(ROOT / 'docs/polish.md')
    check_seal(ROOT / 'docs/re/release-qa.json', BIN, manifests)
    base_hashes, patched_hashes = hashes(original), hashes(BIN)
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='package-', dir=scan_dir) as temporary:
        stage = Path(temporary)
        patch = stage / f'{name}.xdelta'
        run(patcher, '-e', '-9', '-S', 'djw', '-s', original, BIN, patch)
        applied = stage / 'reapplied.bin'
        run(patcher, '-d', '-s', original, patch, applied)
        if hashes(applied) != patched_hashes:
            raise ValueError('xdelta re-application does not match the built BIN')
        readme = stage / 'README.txt'
        template = (ROOT / 'docs/release-readme.txt').read_text(encoding='utf-8')
        for token, value in dict(version=args.version, patch=patch.name, base_name=original.name,
                                 base_size=base_hashes['size'], base_crc32=base_hashes['crc32'],
                                 base_md5=base_hashes['md5'], base_sha1=base_hashes['sha1'],
                                 patched_crc32=patched_hashes['crc32'], patched_sha1=patched_hashes['sha1']).items():
            template = template.replace('{{' + token + '}}', str(value))
        if '{{' in template:
            raise ValueError('unresolved README template token')
        readme.write_text(template, encoding='utf-8', newline='\n')
        archive = stage / f'{name}.zip'
        make_zip(archive, patch, readme)
        verification = dict(version=args.version, original=base_hashes, patched=patched_hashes,
                            patch_sha256=digest(patch), zip_sha256=digest(archive), text_targets=targets,
                            reapplied=True, debug_off=True, tour_reused=args.skip_tour,
                            manifests={p.relative_to(ROOT).as_posix(): digest(p) for p in manifests})
        report = stage / 'verification.json'
        report.write_text(json.dumps(verification, indent=2) + '\n', encoding='utf-8')
        for source, destination in zip((patch, readme, archive, report), outputs):
            os.replace(source, destination)
    print(f'Verified local release: {outputs[2]}\nBIN SHA-1: {patched_hashes["sha1"]}')


if __name__ == '__main__':
    main()
