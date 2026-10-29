"""mipsasm.py: a tiny R3000 assembler for the engine hooks (only the instructions tools/engine.py uses).

asm(src, base) -> bytes. One instruction per line, `label:` lines, `;` comments, `%hi(X)` / `%lo(X)` of a label or
number (hi rounded up when lo >= 0x8000, as MIPS immediates sign-extend). Self-test: decode with capstone.
"""
import re
import struct

REGS = {n: i for i, n in enumerate("zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 "
                                   "t8 t9 k0 k1 gp sp fp ra".split())}
I_OPS = {"addiu": 9, "sltiu": 0x0B, "andi": 0x0C, "ori": 0x0D, "lb": 0x20, "lh": 0x21, "lw": 0x23, "lbu": 0x24,
         "lhu": 0x25, "sb": 0x28, "sh": 0x29, "sw": 0x2B}
R_OPS = {"addu": 0x21, "subu": 0x23, "and": 0x24, "or": 0x25, "slt": 0x2A, "sltu": 0x2B}


def hi(v):
    return (v + 0x8000) >> 16 & 0xFFFF


def lo(v):
    return v & 0xFFFF


def asm(src, base, labels=None):
    """labels: optional dict, filled with label -> address."""
    lines = [ln.split(";")[0].strip() for ln in src.splitlines()]
    labels, pc = {} if labels is None else labels, base
    for ln in lines:
        if ln.endswith(":"):
            labels[ln[:-1]] = pc
        elif ln:
            pc += 4
    out, pc = [], base

    def val(x):
        m = re.fullmatch(r"%(hi|lo)\((\w+)\)", x)
        if m:
            v = labels[m[2]] if m[2] in labels else int(m[2], 0)
            return hi(v) if m[1] == "hi" else lo(v)
        return labels[x] if x in labels else int(x, 0)

    for ln in lines:
        if not ln or ln.endswith(":"):
            continue
        op, _, rest = ln.partition(" ")
        a = [x.strip() for x in rest.split(",")] if rest else []
        r = lambda x: REGS[x]  # noqa: E731
        if op == "nop":
            w = 0
        elif op in I_OPS and "(" in a[-1]:          # load/store: lw rt, off(rs)
            off, rs = re.fullmatch(r"(.*)\((\w+)\)", a[1]).groups()
            w = I_OPS[op] << 26 | r(rs) << 21 | r(a[0]) << 16 | val(off) & 0xFFFF
        elif op in I_OPS:
            w = I_OPS[op] << 26 | r(a[1]) << 21 | r(a[0]) << 16 | val(a[2]) & 0xFFFF
        elif op == "lui":
            w = 0x0F << 26 | r(a[0]) << 16 | val(a[1]) & 0xFFFF
        elif op in R_OPS:
            w = r(a[1]) << 21 | r(a[2]) << 16 | r(a[0]) << 11 | R_OPS[op]
        elif op == "move":
            w = r(a[1]) << 21 | r(a[0]) << 11 | 0x21
        elif op == "sll":
            w = r(a[1]) << 16 | r(a[0]) << 11 | val(a[2]) << 6
        elif op == "jr":
            w = r(a[0]) << 21 | 8
        elif op in ("j", "jal"):
            w = (2 if op == "j" else 3) << 26 | val(a[0]) >> 2 & 0x3FFFFFF
        elif op in ("beq", "bne"):
            w = (4 if op == "beq" else 5) << 26 | r(a[0]) << 21 | r(a[1]) << 16 | (val(a[2]) - pc - 4) >> 2 & 0xFFFF
        else:
            raise ValueError("mipsasm: unknown instruction %r" % ln)
        out.append(w)
        pc += 4
    return struct.pack("<%dI" % len(out), *out)


def selftest():
    import capstone
    src = """start:
    lh a0, 0x40(s1)
    addiu v0, s0, -0x21
    sltiu v1, v0, 0x5e
    beq v1, zero, done
    lui v1, %hi(0x8007AF80)
    lbu a0, %lo(0x8007AF80)(v1)
    addu v1, v1, v0
    sll s1, s4, 4
    jal 0x8003C210
    move v0, a0
    done:
    jr ra
    nop"""
    code = asm(src, 0x8007AF50)
    md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 | capstone.CS_MODE_LITTLE_ENDIAN)
    got = [("%s %s" % (i.mnemonic, i.op_str)).strip() for i in md.disasm(code, 0x8007AF50)]
    want = ["lh $a0, 0x40($s1)", "addiu $v0, $s0, -0x21", "sltiu $v1, $v0, 0x5e", "beqz $v1, 0x8007af78",
            "lui $v1, 0x8008", "lbu $a0, -0x5080($v1)", "addu $v1, $v1, $v0", "sll $s1, $s4, 4",
            "jal 0x8003c210", "move $v0, $a0", "jr $ra", "nop"]
    assert got == want, got


if __name__ == "__main__":
    selftest()
    print("ok")
