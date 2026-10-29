"""PCSX-Redux savestate -> 2 MB main RAM (for ramsearch.py / diffing), and RAM reads from a state.

    python -X utf8 tools/debug/stateram.py STATE.sstate [OUT.bin]      write the RAM dump (default STATE.ram.bin)
    python -X utf8 tools/debug/stateram.py STATE.sstate --peek 0x80085F28[:4] ...

The state is an uncompressed protobuf; RAM is one 2 MB field. It is located by the EXE's code bytes at
0x80015000, which never change at run time (nor in marker/en builds).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAM_SIZE = 0x200000


def ram(state):
    d = pathlib.Path(state).read_bytes()
    exe = (ROOT / "work/disc/tree/SLPS_020.75").read_bytes()
    # code at 0x80015000 (file offset = addr - 0x8000F800): past the EXE text that marker/en builds rewrite
    pat = exe[0x800 + 0x5000:0x800 + 0x5040]
    i = d.find(pat)
    if i < 0:
        sys.exit(f"{state}: EXE code not found; not a PCSX-Redux state of this game?")
    base = i - 0x15000
    return d[base:base + RAM_SIZE]


def peek(r, spec):
    a, _, n = spec.partition(":")
    a = int(a, 16) & 0x1FFFFF
    n = int(n or 4)
    return int.from_bytes(r[a:a + n], "little")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    r = ram(args[0])
    if "--peek" in args:
        for s in args[args.index("--peek") + 1:]:
            v = peek(r, s)
            print(f"{s} = {v} (0x{v:X})")
    else:
        out = args[1] if len(args) > 1 else str(pathlib.Path(args[0]).with_suffix(".ram.bin"))
        pathlib.Path(out).write_bytes(r)
        print(out)
