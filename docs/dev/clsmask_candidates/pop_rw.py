#!/usr/bin/env python3
"""clsmask_candidates: the REAL-WORLD population -- every rwquest question
(docs/dev/lanes/rwquest/questions.tsv) over a head sample of its FIRST corpus
file (worktrees/.corpus/, gitignored; [REGIME-CORPUS]).

    pop_rw.py QUESTIONS CORPUSDIR SUBJDIR [SAMPLE_BYTES] > pop_rw.tsv

Flags: i -> -i, utf -> -e utf8, ucp -> --ucp, m/s -> an inline (?m)/(?s)
prefix (pcrec has no CLI spelling for them). Every mode (find-all, count,
line, first) is driven as the bench's find-all loop: the per-byte rates this
study reads do not depend on the mode, and `line` mode's per-line search
differs from find-all only at line ends. The sample is the file's first
SAMPLE_BYTES (default 256 KiB) cut back to a line end: the corpus's
sorted-file head bias (rwcorpus_report.md) applies to it.

Rows: walk_survey's population shape (pid set enc icase pattern_hex regime
subjects) plus a trailing `extra` column (extra pcrec args, space-joined).
"""
import os, sys

QS, CORP, SUBJ = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
SAMPLE = int(sys.argv[4]) if len(sys.argv) > 4 else 256 * 1024
os.makedirs(SUBJ, exist_ok=True)
lines = open(QS, "rb").read().split(b"\n")
hdr = lines[0].decode().split("\t")
col = {h: i for i, h in enumerate(hdr)}
print("pid\tset\tenc\ticase\tpattern_hex\tregime\tsubjects\textra")
for ln in lines[1:]:
    if not ln:
        continue
    f = ln.split(b"\t")
    qid = f[col["id"]].decode()
    files = f[col["files"]].decode().split(";")
    flags = f[col["flags"]].decode()
    fl = [] if flags == "-" else flags.split(",")
    pat = f[col["pattern"]]
    path = os.path.join(CORP, files[0])
    if not os.path.exists(path):
        continue
    b = open(path, "rb").read(SAMPLE + 1)
    if len(b) > SAMPLE:
        b = b[:SAMPLE]
        k = b.rfind(b"\n")
        if k > 0:
            b = b[:k + 1]
    sp = os.path.join(SUBJ, qid)
    open(sp, "wb").write(b)
    pre = b"".join(b"(?%s)" % x.encode() for x in fl if x in ("m", "s"))
    extra = []
    if "utf" in fl:
        extra += ["-e", "utf8"]
    if "ucp" in fl:
        extra += ["--ucp"]
    enc = "utf8" if "utf" in fl else "byte"
    print("rw/%s\t%s\t%s\t%d\t%s\tfindall\t%s\t%s" % (
        qid, f[col["class"]].decode(), enc, int("i" in fl), (pre + pat).hex(), sp, " ".join(extra)))
