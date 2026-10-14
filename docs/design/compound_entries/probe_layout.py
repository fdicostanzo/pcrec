#!/usr/bin/env python3
"""LAYOUT probe (compound_entries.md §2): the same emitted artifact under three
layouts of its static PARTS, measured compile-only (.text bytes) plus a
clockless dynamic INSTRUCTION count under callgrind (Ir per driver iteration).

  gcc     -- as emitted: gcc -O2 decides which static parts to inline
  shared  -- every part `__attribute__((noinline))`: one copy, called (size end)
  inline  -- every part `always_inline` where gcc can copy it; a part gcc
             REFUSES to copy (a static label table: the DFA attempt route) is
             recorded and kept shared (speed end, the hard constraint)

Parts are the static functions an exported entry calls: a compound's
`rx__<role>_search`, the VM's `rx_prefilter`, `rx_match_anchored`,
`rx_search_run`, `rx_match_run`, `rx_match_caps_run`.

usage: python3 -I probe_layout.py PCREC_BIN SCRATCH_DIR DRV_C > layout.tsv
"""
import os, re, subprocess, sys

PART_RE = re.compile(r"^(rx__\w+_search|rx_prefilter|rx_match_anchored|rx_search_run|"
                     r"rx_match_run|rx_match_caps_run)$")
WITNESSES = [
    ("compound-split", [], r"^\s+|\s+$", ["  ab cd  ", "x" * 8 + " "]),
    ("compound-split-fn", [], r"\}\s*$|^x", ["}  ", "abc}"]),
    ("dfa-attempt", [], r"^ab|cd", ["xxcdxxcd", "abab"]),
    ("vm-hybrid-frameless", [], r"(a)b", ["abab" * 4, "xxxx"]),
    ("vm-hybrid-framed", [], r"(a|ab)(c|bcd)(d*)", ["abcdabcd", "xxxx"]),
    ("vm-forced", ["--engine=vm"], r"(a)b", ["abab" * 4, "xxxx"]),
]
N1, N2 = 2000, 4000

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def defs(src):
    """(line index, name) of every static FUNCTION DEFINITION whose name is a part."""
    lines = src.split("\n")
    out = []
    for i, l in enumerate(lines):
        m = re.match(r"^static (?:inline )?[\w ]+?\b(\w+)\(", l)
        if not m or not PART_RE.match(m.group(1)):
            continue
        j, tail = i, ""
        while j < len(lines) and "{" not in tail and ";" not in tail:
            tail += lines[j]; j += 1
        if "{" in tail and (tail.find(";") < 0 or tail.find("{") < tail.find(";")):
            out.append((i, m.group(1)))
    return lines, out

def variant(src, attr_for):
    lines, ds = defs(src)
    for i, name in reversed(ds):
        a = attr_for(name)
        if a:
            lines[i] = a + " " + lines[i]
    return "\n".join(lines), [n for _, n in ds]

def text_bytes(obj):
    r = run(["size", "-A", obj])
    for l in r.stdout.splitlines():
        p = l.split()
        if p and p[0] == ".text":
            return int(p[1])
    return -1

def fn_sizes(obj):
    r = run(["nm", "-S", "--defined-only", obj])
    d = {}
    for l in r.stdout.splitlines():
        p = l.split()
        if len(p) == 4 and p[2] in "Tt":
            d[p[3]] = int(p[1], 16)
    return d

def ir(exe, n, subj, scratch):
    out = os.path.join(scratch, "cg.out")
    r = run(["valgrind", "--tool=callgrind", f"--callgrind-out-file={out}",
             exe, str(n), subj])
    for l in r.stderr.splitlines():
        m = re.search(r"Collected : (\d+)", l)
        if m:
            return int(m.group(1))
    raise RuntimeError(r.stderr[-400:])

def main():
    pcrec, scratch, drv = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
    os.makedirs(scratch, exist_ok=True)
    print("witness\tlayout\tparts\trefused_inline\ttext_bytes\tfn_sizes\tsubject\tIr_per_iter")
    for label, args, pat, subjects in WITNESSES:
        base = os.path.join(scratch, label)
        r = run([pcrec, "-p", "rx", *args, "-o", base + ".c", "--pattern", pat])
        if r.returncode:
            print(f"{label}\tREFUSED\t{r.stderr.strip()[:80]}"); continue
        src = open(base + ".c", encoding="latin-1").read()
        for layout in ("gcc", "shared", "inline"):
            refused = set()
            while True:
                if layout == "gcc":
                    txt, parts = variant(src, lambda n: None)
                elif layout == "shared":
                    txt, parts = variant(src, lambda n: "__attribute__((noinline))")
                else:
                    txt, parts = variant(src, lambda n: None if n in refused
                                         else "__attribute__((always_inline)) inline")
                vc = f"{base}.{layout}.c"
                open(vc, "w", encoding="latin-1").write(
                    txt.replace(f'#include "{label}.h"', f'#include "{label}.h"'))
                obj = f"{base}.{layout}.o"
                r = run(["gcc", "-O2", "-std=gnu11", "-c", "-o", obj, vc])
                if r.returncode == 0:
                    break
                # gcc's two refusals, quoted with ‘’ or '': a static label
                # table ("can never be copied") and a computed goto ("can never
                # be inlined"): both are HARD constraints on the speed end.
                bad = set(re.findall(r"function [‘'](\w+)[’'] can never be (?:copied|inlined)",
                                     r.stderr))
                bad &= set(parts)
                if layout != "inline" or not bad or bad <= refused:
                    print(f"{label}\t{layout}\tGCC-FAILED\t{r.stderr[:300]!r}"); break
                refused |= bad
            else:
                continue
            if r.returncode:
                continue
            exe = f"{base}.{layout}.exe"
            r2 = run(["gcc", "-O2", "-std=gnu11", f'-DARTIFACT_H="{label}.h"', f"-I{scratch}",
                      "-o", exe, drv, obj])
            if r2.returncode:
                print(f"{label}\t{layout}\tLINK-FAILED\t{r2.stderr[:200]!r}"); continue
            fs = fn_sizes(obj)
            fsz = ",".join(f"{k}={v}" for k, v in sorted(fs.items()))
            for subj in subjects:
                a, b = ir(exe, N1, subj, scratch), ir(exe, N2, subj, scratch)
                per = (b - a) / (N2 - N1)
                print(f"{label}\t{layout}\t{','.join(parts) or '-'}\t"
                      f"{','.join(sorted(refused)) or '-'}\t{text_bytes(obj)}\t{fsz}\t"
                      f"{subj!r}\t{per:.1f}", flush=True)

if __name__ == "__main__":
    main()
