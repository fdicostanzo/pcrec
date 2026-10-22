#!/usr/bin/env python3 -I
"""e8min/mk_j1_patterns.py QUESTIONS_TSV OUT -- J1's pattern list for
shadow_census.py manifest --patterns: one line per rwquest question,
`id<TAB>extra argv or -<TAB>pattern`. Flags i/m/s are spelled inline ((?i) ...), utf is
`-e utf8`, ucp is `--ucp`; the rest of the question (class, files, mode) stays in
questions.tsv and is joined back by id."""
import sys

rows = [ln.rstrip("\n").split("\t") for ln in open(sys.argv[1])][1:]
with open(sys.argv[2], "w") as fh:
    fh.write("# J1 pattern list: id, extra argv, pattern (e8min/mk_j1_patterns.py)\n")
    for r in rows:
        qid, pat, flags = r[0], r[4], set(r[5].split(","))
        pre = "".join("(?%s)" % f for f in "ims" if f in flags)
        extra = " ".join((["-e", "utf8"] if "utf" in flags else []) + (["--ucp"] if "ucp" in flags else [])) or "-"
        fh.write("%s\t%s\t%s%s\n" % (qid, extra, pre, pat))
print("%d patterns -> %s" % (len(rows), sys.argv[2]))
