"""Release failures must stop packaging, not silently bless stale artifacts."""
import json
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import release  # noqa: E402
import release_scan  # noqa: E402
import story_review  # noqa: E402


def test_unfinished_polish_blocks(tmp_path):
    path = tmp_path / 'polish.md'
    path.write_text('- [x] fixed\n- [ ] unresolved continuity\n')
    with pytest.raises(ValueError, match='unfinished'):
        release.require_polish(path)


def test_story_gate_cannot_be_omitted(tmp_path):
    (tmp_path / 'manifest.tsv').write_text('visual only')
    with pytest.raises(ValueError, match='both required'):
        release.qa_manifests(tmp_path)


def test_qa_seal_rejects_new_bin_and_changed_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(release, 'ROOT', tmp_path)
    image, manifest, seal = (tmp_path / n for n in ('game.bin', 'manifest.tsv', 'seal.json'))
    image.write_bytes(b'reviewed game')
    manifest.write_bytes(b'reviewed chapter')
    seal.write_text(json.dumps(dict(bin_sha1=release.digest(image, 'sha1'),
                                   manifests_sha256={'manifest.tsv': release.digest(manifest)})))
    release.check_seal(seal, image, [manifest])
    image.write_bytes(b'unreviewed game')
    with pytest.raises(ValueError, match='BIN'):
        release.check_seal(seal, image, [manifest])
    image.write_bytes(b'reviewed game')
    manifest.write_bytes(b'unreviewed chapter')
    with pytest.raises(ValueError, match='manifests differ'):
        release.check_seal(seal, image, [manifest])


def test_zip_contains_only_patch_and_readme(tmp_path):
    patch, readme, archive = (tmp_path / n for n in ('game.xdelta', 'README.txt', 'game.zip'))
    patch.write_bytes(b'patch')
    readme.write_text('instructions')
    release.make_zip(archive, patch, readme)
    with zipfile.ZipFile(archive) as result:
        assert result.namelist() == ['game.xdelta', 'README.txt']
        assert all(i.compress_type == zipfile.ZIP_STORED for i in result.infolist())


def test_scan_follows_relocated_pool_reference(tmp_path):
    data = bytearray(64)
    struct.pack_into('<I', data, 4, 32)
    data[16:21] = b'old!\0'
    data[32:38] = b'fresh\0'
    (tmp_path / 'pool').write_bytes(data)
    block = {'kind': 'pool'}
    row = {'at': '10', 'refs': ['off@4']}
    assert list(release_scan.strings(release_scan.Disc(tmp_path), block, row, 'pool')) == [b'fresh']
    struct.pack_into('<I', data, 4, 9999)
    (tmp_path / 'pool').write_bytes(data)
    with pytest.raises(ValueError, match='outside file'):
        list(release_scan.strings(release_scan.Disc(tmp_path), block, row, 'pool'))


def test_scan_mips_signed_low_address():
    data = struct.pack('<II', 0x3C028001, 0x2442F800)
    assert release_scan.target(data, ('lui', 0, 4)) == 0x8000F800


def test_story_inputs_cover_every_story_entry_and_variant():
    documents = dict(story_review.documents())
    assert len(documents) == 45
    assert all(f'chapter{n:02}' in documents for n in range(1, 21))
    assert {'chapter03_female', 'chapter07_female'} <= documents.keys()
    text = '\n'.join(documents.values())
    for name in ['scenarios', 'ovl033', *[f'ovl{n:03}' for n in range(38, 49)],
                 *[f'endings{n:02}' for n in range(11)]]:
        for row in story_review.block(name)['strings']:
            assert f">> {row['id']} |" in text


def test_release_help_has_no_build_side_effects():
    image = ROOT / 'build/gaiamaster_en.bin'
    before = image.stat().st_mtime_ns if image.exists() else None
    result = subprocess.run([sys.executable, str(ROOT / 'tools/release.py'), '--help'], capture_output=True)
    assert result.returncode == 0
    assert (image.stat().st_mtime_ns if image.exists() else None) == before


def test_existing_version_refused_before_build(tmp_path, monkeypatch):
    monkeypatch.setattr(release, 'ROOT', tmp_path)
    folder = tmp_path / 'release/v0.1'
    folder.mkdir(parents=True)
    patch = folder / 'GaiaMaster_EN_v0.1.xdelta'
    patch.write_bytes(b'previous release')
    monkeypatch.setattr(release, 'python', lambda *args: pytest.fail('build must not start'))
    with pytest.raises(SystemExit) as result:
        release.main([])
    assert result.value.code == 2
    assert patch.read_bytes() == b'previous release'
