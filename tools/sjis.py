"""Shift-JIS text codec for the script, byte-exact: decode(b) -> str, encode(str) -> b, encode(decode(b)) == b.

Double-byte codes whose cp932 round trip is not exact (NEC/IBM duplicates), control bytes and '[' decode as `[XX]`
hex escapes; 0x0A is a real newline; ASCII 0x20-0x7E stays ASCII (the game's control codes: %s %d /P90 /V%d /v).
"""
import re

ESC = re.compile(r"\[([0-9A-F]{2})\]")


def lead(c):
    return 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC


def decode(b):
    out, i = [], 0
    while i < len(b):
        c = b[i]
        if lead(c) and i + 1 < len(b):
            try:
                ch = b[i:i + 2].decode("cp932")
            except UnicodeDecodeError:
                ch = None
            if ch and ch.encode("cp932") == b[i:i + 2]:
                out.append(ch)
                i += 2
                continue
        if c == 0x0A or (0x20 <= c < 0x7F and c != 0x5B):
            out.append(chr(c))
        elif 0xA1 <= c <= 0xDF:
            out.append(bytes([c]).decode("cp932"))
        else:
            out.append("[%02X]" % c)
        i += 1
    return "".join(out)


def encode(s):
    out, i = bytearray(), 0
    while i < len(s):
        m = ESC.match(s, i)
        if m:
            out.append(int(m[1], 16))
            i = m.end()
        else:
            out += s[i].encode("cp932")
            i += 1
    return bytes(out)


def is_text(b):
    """Clean text: decodes with no escapes and holds at least one double-byte character."""
    s = decode(b)
    return bool(b) and "[" not in s and any(ord(c) > 0xFF and not 0xFF61 <= ord(c) <= 0xFF9F for c in s)


if __name__ == "__main__":
    for raw in [b"%s\x82\xc9\x8e\x7e\x82\xdc\x82\xc1\x82\xbd\x82\xe6", b"[\x01\x87\x9a\xff\x81", b"/P90\xb1\n"]:
        assert encode(decode(raw)) == raw, (raw, decode(raw))
    assert decode(b"[") == "[5B]" and is_text("体力".encode("cp932")) and not is_text(b"%d")
