#!/usr/bin/env python3
"""reach_probe.py -- how many corpus artifacts each [PRIOR-COST-UNIFY] U1
adapter would actually serve, read from STAMPS (compile-only, no timing).

Population: every `pattern`/`pattern-esc` line of every tests/**/*.rxt,
enumerated by `pcrec --list-source` (emit_sweep.py's own enumerator,
imported, so the population is that instrument's), compiled
`-p rx --features all -o -` at the default engine, `-e byte` (the encoding
the default prior serves). For every artifact stamped
RX_DFA_PREFILTER "handoff" a second compile with -fno-req-handoff gives the
row the K admission displaced (adapter A2's question).

Usage: reach_probe.py PCREC_BIN TREE_DIR > reach.tsv   (summary on stderr)
"""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(sys.argv[2], "scripts"))
import emit_sweep as es  # noqa: E402

BIN, TREE = sys.argv[1], sys.argv[2]
STAMP = re.compile(rb'^#define (RX_[A-Z_]+) "([^"]*)"', re.M)
KEYS = ("RX_ENGINE", "RX_VM_PREFILTER", "RX_VM_RESEED", "RX_DFA_SCAN",
        "RX_DFA_PREFILTER", "RX_DFA_PREFILTER_OFFSETS", "RX_REQ_RUN",
        "RX_REQ_HANDOFF", "RX_FINDINGS")


def stamps(pat, extra=()):
    argv = [BIN, "-p", "rx", "--features", "all", *extra, "-o", "-",
            "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    return {k.decode(): v.decode("utf-8", "replace")
            for k, v in STAMP.findall(r.stdout)}


def one(item):
    f, kind, pat = item
    s = stamps(pat)
    if s is None:
        return None
    twin = ""
    if s.get("RX_DFA_PREFILTER") == "handoff":
        t = stamps(pat, ("-fno-req-handoff",))
        twin = t.get("RX_DFA_PREFILTER", "?") if t else "refused"
    return [f, (pat if isinstance(pat, bytes) else pat.encode("utf-8", "surrogateescape")).decode("latin-1").encode("unicode_escape").decode()] + \
        [s.get(k, "") for k in KEYS] + [twin]


def main():
    corpus = es.enumerate_corpus(BIN, TREE, 60)
    with ThreadPoolExecutor(8) as ex:
        rows = [r for r in ex.map(one, corpus) if r]
    print("#file\tpattern\t" + "\t".join(KEYS) + "\tHANDOFF_TWIN_PREFILTER")
    for r in rows:
        print("\t".join(r))
    col = {k: i + 2 for i, k in enumerate(KEYS)}
    tw = len(KEYS) + 2
    n = len(rows)
    def cnt(pred):
        return sum(1 for r in rows if pred(r))
    ofs = lambda v: v.startswith(("offset-set", "run-pinned"))
    out = [
        ("compiled artifacts", n, "corpus pattern lines that compile"),
        ("#4 handoff re-entry (A1 UP, A2, A4)", cnt(lambda r: r[col["RX_DFA_PREFILTER"]] == "handoff"), "RX_DFA_PREFILTER handoff"),
        ("A1 on #4: run landmark", cnt(lambda r: r[col["RX_DFA_PREFILTER"]] == "handoff" and r[col["RX_REQ_RUN"]] not in ("", "none")), "handoff with RX_REQ_RUN != none"),
        ("A2: displaced row is offset-set/run-pinned", cnt(lambda r: ofs(r[tw])), "-fno-req-handoff twin stamps offset-set*/run-pinned*"),
        ("#7 prefix_k selected a k-set", cnt(lambda r: r[col["RX_DFA_PREFILTER_OFFSETS"]] not in ("", "none")), "RX_DFA_PREFILTER_OFFSETS != none"),
        ("#3 R4 asked: adaptive rows", cnt(lambda r: r[col["RX_VM_RESEED"]].startswith("adaptive")), "RX_VM_RESEED adaptive*"),
        ("#3 R4 answered dense", cnt(lambda r: r[col["RX_VM_RESEED"]] == "adaptive-dense"), "RX_VM_RESEED adaptive-dense"),
        ("A3: R4 on an offset/run-pinned prefilter", cnt(lambda r: r[col["RX_VM_RESEED"]].startswith("adaptive") and ofs(r[col["RX_DFA_PREFILTER"]])), "adaptive* with RX_DFA_PREFILTER offset-set*/run-pinned*"),
        ("prior NONE (byte-rate=none)", cnt(lambda r: "byte-rate=none" in r[col["RX_FINDINGS"]]), "RX_FINDINGS byte-rate=none"),
    ]
    for name, v, how in out:
        print(f"{name}\t{v}\t{how}", file=sys.stderr)


if __name__ == "__main__":
    main()
