#!/usr/bin/env python3
"""[r40 F1] The JUMP-TABLE term J: bytes per entry and gcc CPU per entry.

The corpus cannot fit this coefficient -- its J tops out at 210 entries while
K41's second witness carries 34,188 (163x beyond). So J is measured DIRECTLY,
the way §4.2 measured nodes and data-table entries.

DECORRELATION. In an anchored family `^(<literal of length n over an alphabet
of k letters>)x` the emitted prefilter takes the computed-goto form
(RX_DFA_SCAN "attempt", RX_DFA_TABLE "none") with S ~ n states, N ~ n VM nodes
and J = S * ncls where ncls ~ k+1. So varying n moves N and J together, and
varying k at FIXED n moves J alone. The grid gives both.
"""
import sys, os, subprocess, string
sys.path.insert(0, "/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3")
from measure import emit, scan

W = "/home/duxevents/pcrec/worktrees/artsize3"
S = "/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/jfit"
os.makedirs(S, exist_ok=True)

SUBJECTS = []
for n in (100, 200, 400, 800):
    for k in (2, 6, 14, 26):
        al = string.ascii_lowercase[:k]
        SUBJECTS.append(("n%d_k%d" % (n, k),
                         "^(%s)x" % "".join(al[i % k] for i in range(n))))


def gcc_cpu(path, trials=2):
    best = None
    for _ in range(trials):
        r = subprocess.run([W + "/scripts/watchdog", "-s", "300", "-c", "280",
                            "-m", "4000m", "-S", "jfit", "--",
                            "/usr/bin/time", "-f", "%U %S", "-o", path + ".time",
                            "gcc", "-O2", "-std=gnu11", "-c", "-o", path + ".o", path],
                           capture_output=True)
        if r.returncode != 0:
            return None, None, r.returncode
        u, s = open(path + ".time").read().split()
        c = float(u) + float(s)
        best = c if best is None else min(best, c)
    osz = os.path.getsize(path + ".o") if os.path.exists(path + ".o") else 0
    if os.path.exists(path + ".o"):
        os.remove(path + ".o")
    return best, osz, 0


def main():
    out = open(sys.argv[1], "w")
    out.write("label\tn\tk\tbytes\tN\tS\tE\tJ\tgcc_cpu_s\tdot_o\terr\n")
    for lab, pat in SUBJECTS:
        n, k = (int(x[1:]) for x in lab.split("_"))
        text, err, _ = emit(pat, timeout=300)
        if err:
            out.write("%s\t%d\t%d\t\t\t\t\t\t\t\t%s\n" % (lab, n, k, err[:60]))
            out.flush(); continue
        r = scan(text)
        p = os.path.join(S, lab + ".c")
        open(p, "w").write(text)
        cpu, osz, rc = gcc_cpu(p)
        out.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n" % (
            lab, n, k, r["bytes"], r["labels"], r["slabels"], r["table_entries"],
            r["jump_entries"], ("%.3f" % cpu) if cpu else "", osz or "",
            "" if cpu else "rc=%s" % rc))
        out.flush(); os.remove(p)
        print("%-9s bytes=%-8d N=%-5d S=%-5d E=%-6d J=%-7d gcc=%s" % (
            lab, r["bytes"], r["labels"], r["slabels"], r["table_entries"],
            r["jump_entries"], ("%.3f s" % cpu) if cpu else "KILLED"), flush=True)
    out.close()


if __name__ == "__main__":
    main()
