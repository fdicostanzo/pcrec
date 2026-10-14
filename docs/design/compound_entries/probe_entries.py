#!/usr/bin/env python3
"""ENTRY MAP probe (compound_entries.md §1): for each route witness, compile the
emitted artifact with gcc and list every function symbol the object keeps,
its binding (T exported / t static) and size, plus which entries CALL or
TAIL-JUMP another emitted function, in two link regimes (-O2, -O2 -fPIC).
Compile-only: no clock is read.

usage: python3 -I probe_entries.py PCREC_BIN SCRATCH_DIR > entries.tsv
"""
import os, re, subprocess, sys

WITNESSES = [
    # (label, argv after the pattern flag, pattern)
    ("dfa-unanch-ewidth", [], "abc"),
    ("dfa-landing",       [], r"\w+"),
    ("dfa-attempt",       [], r"^ab|cd"),
    ("dfa-rev-end",       [], r"\d+$"),
    ("compound-split",    [], r"^\s+|\s+$"),
    ("compound-split-utf",["-e", "utf8", "-futf-check"], r"^\s+|\s+$"),
    ("vm-hybrid-frameless", [], r"(a)b"),
    ("vm-hybrid-framed",  [], r"(a|ab)(c|bcd)(d*)"),
    ("vm-forced",         ["--engine=vm"], r"(a)b"),
    ("vm-vars",           ["--features", "vars"], r"a${v}b"),
]

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def stamps(c, h):
    want = ("ENGINE", "DFA_SCAN", "COMPOUND", "VM_PREFILTER", "VM_FRAMELESS",
            "VM_ENTRY_SHAPE", "DFA_MATCH", "DFA_START")
    out = {}
    for path in (c, h):
        for line in open(path, encoding="latin-1"):
            m = re.match(r"#define RX_(\w+)\s+(.*)$", line)
            if m and m.group(1) in want:
                out[m.group(1)] = m.group(2).strip().strip('"')
    return ",".join(f"{k}={out[k]}" for k in want if k in out)

def funcs(obj):
    r = run(["nm", "-S", "--defined-only", obj])
    res = []
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) == 4 and p[2] in ("T", "t"):
            res.append((p[3], p[2], int(p[1], 16)))
    return res

def calls(obj):
    """Per function: instructions, and the functions it calls (call) or
    tail-jumps (jmp) to.  A call to a GLOBAL symbol shows in a .o as a
    relocation on the line after the instruction (R_X86_64_PLT32 / PC32), and
    objdump then prints a MEANINGLESS target (the placeholder's address, which
    can fall in the next function): the relocation's symbol wins, marked `@g`
    (resolved by the linker, through the PLT in a shared object with default
    visibility).  A call with no relocation was resolved in the object (a
    static function, or a global gcc bound locally): marked `@s`."""
    r = run(["objdump", "-dr", "--no-show-raw-insn", obj])
    cur, out, pending = None, {}, None

    def commit():
        nonlocal pending
        if pending and cur is not None:
            kind, tgt = pending
            if tgt.startswith("rx") and tgt != cur:
                out[cur]["edges"].add(f"{kind}:{tgt}@s")
        pending = None

    for line in r.stdout.splitlines():
        m = re.match(r"^[0-9a-f]+ <(.+)>:$", line)
        if m:
            commit()
            cur = m.group(1); out[cur] = {"insns": 0, "edges": set()}
            continue
        if cur is None or not line.strip():
            continue
        rm = re.search(r"R_X86_64_(?:PLT32|PC32)\s+([\w.]+)", line)
        if rm:
            if pending:
                kind, _ = pending
                tgt = rm.group(1)
                if tgt.startswith("rx") and tgt != cur:
                    out[cur]["edges"].add(f"{kind}:{tgt}@g")
                pending = None
            continue
        if re.match(r"^\s+[0-9a-f]+:\s", line):
            commit()
            out[cur]["insns"] += 1
            m2 = re.search(r"\b(call|jmp)\s+[0-9a-f]+ <([\w.]+?)(?:\+0x[0-9a-f]+)?>", line)
            if m2:
                pending = (m2.group(1), m2.group(2))
    commit()
    return out

def main():
    pcrec, scratch = sys.argv[1], sys.argv[2]
    os.makedirs(scratch, exist_ok=True)
    print("witness\tregime\tstamps\tsymbol\tbind\tbytes\tinsns\tcalls")
    for label, args, pat in WITNESSES:
        base = os.path.join(scratch, label)
        r = run([pcrec, "-p", "rx", *args, "-o", base + ".c", "--pattern", pat])
        if r.returncode:
            print(f"{label}\t-\tREFUSED\t{r.stderr.strip()[:80]}", flush=True); continue
        st = stamps(base + ".c", base + ".h")
        for regime, fl in (("O2", ["-O2"]), ("O2-fPIC", ["-O2", "-fPIC"])):
            obj = f"{base}.{regime}.o"
            r = run(["gcc", *fl, "-std=gnu11", "-c", "-o", obj, base + ".c"])
            if r.returncode:
                print(f"{label}\t{regime}\t{st}\tGCC-FAILED\t{r.stderr[:80]}"); continue
            cg = calls(obj)
            for name, bind, size in sorted(funcs(obj), key=lambda t: (t[1] != "T", t[0])):
                c = cg.get(name, {"insns": 0, "edges": set()})
                print(f"{label}\t{regime}\t{st}\t{name}\t{bind}\t{size}\t{c['insns']}\t"
                      + (",".join(sorted(c["edges"])) or "-"))

if __name__ == "__main__":
    main()
