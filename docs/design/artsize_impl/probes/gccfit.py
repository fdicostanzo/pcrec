#!/usr/bin/env python3
"""What actually drives gcc's cost: emitted NODES or emitted TABLE ENTRIES?

The cap's whole justification is D45's compile budget, so the cap must be on
the quantity that predicts gcc CPU. Measured directly: a spread of artifacts
chosen to DECORRELATE nodes from entries (table-heavy patterns have ~0 nodes;
node-heavy patterns have ~0 entries).
"""
import sys, os, subprocess, time
sys.path.insert(0, "/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3")
from measure import emit, scan

W = "/home/duxevents/pcrec/worktrees/artsize3"
S = "/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/gccfit"
os.makedirs(S, exist_ok=True)

NESTED = "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,%d}(){2,3}){1,2}){2,3}"
SUBJECTS = []
# node-heavy, table-light: the nested family across N and K
for N in (2, 4, 6, 8):
    for K in (1, 2, 4, 8):
        SUBJECTS.append(("nested-N%d-K%d" % (N, K), NESTED % N, ["--unroll=%d" % K]))
# table-heavy, node-light: pure DFA bounded repeats
for n in (2000, 8000, 15000, 20000, 25000, 31000):
    SUBJECTS.append(("a1_%d" % n, "a{1,%d}" % n, []))
# mixed
for n in (500, 2047, 4000):
    SUBJECTS.append(("alt%d" % n, "((a)|ab){0,%d}c" % n, []))


def gcc_cpu(path):
    """gcc -O2 -c CPU seconds via wait4 rusage, watchdog-bounded."""
    t = subprocess.run([W + "/scripts/watchdog", "-s", "300", "-c", "280", "-m", "4000m",
                        "-S", "gccfit", "--", "/usr/bin/time", "-f", "%U %S %M",
                        "-o", path + ".time",
                        "gcc", "-O2", "-std=gnu11", "-c", "-o", path + ".o", path],
                       capture_output=True)
    if t.returncode != 0:
        return None, None, t.returncode
    with open(path + ".time") as f:
        u, s, m = f.read().split()
    osz = os.path.getsize(path + ".o") if os.path.exists(path + ".o") else 0
    os.path.exists(path + ".o") and os.remove(path + ".o")
    return float(u) + float(s), osz, 0


def main():
    out = open(sys.argv[1], "w")
    out.write("label\tbytes\tnodes\tentries\tgcc_cpu_s\tdot_o\trc\n")
    for lab, pat, extra in SUBJECTS:
        text, err, _ = emit(pat, extra=extra, timeout=300)
        if err:
            out.write("%s\t\t\t\t\t\t%s\n" % (lab, err[:60])); out.flush(); continue
        r = scan(text)
        p = os.path.join(S, lab + ".c")
        open(p, "w").write(text)
        cpu, osz, rc = gcc_cpu(p)
        out.write("%s\t%d\t%d\t%d\t%s\t%s\t%d\n" % (
            lab, r["bytes"], r["labels"], r["table_entries"],
            ("%.3f" % cpu) if cpu is not None else "", osz if osz else "", rc))
        out.flush()
        os.remove(p)
        print("%-16s bytes=%-8d nodes=%-5d entries=%-7d gcc=%s" % (
            lab, r["bytes"], r["labels"], r["table_entries"],
            ("%.3f s" % cpu) if cpu is not None else "KILLED rc=%d" % rc), flush=True)
    out.close()


if __name__ == "__main__":
    main()
