#!/usr/bin/env python3
"""tests/findings/e1_fixtures.py TREE DIR — writes the ANALYSIS-OBJECT fixture
tree ([WINDOW-E1] C-E1-1, docs/design/memfn/window_contract.md §3.7.7) into
DIR, for run_findings_tests.sh §14 to compile against.

Written fresh every run (res_fixtures.py's reason: a fixture cannot drift
from the script that reads it). One `-I` directory per cell, so a cell's
bundle is found at the stop it names and nowhere else; every count table is
distinct, so an answer is identifiable by findings_ref.py's digest alone.

    DIR/COPY/default.rxt   a byte-identical copy of the store's default.rxt
    DIR/MDEF/default.rxt   a bundle NAMED `default` declaring a measured source
    DIR/AUTH/mine.rxt      a user bundle declaring `source authored`
    DIR/INC/incd.rxt       `include <default>` by name; serves utf8 itself
    DIR/CHAIN/outer.rxt    a two-link user chain: outer serves utf8 and
    DIR/CHAIN/inner.rxt      includes inner, which serves byte and utf8
    DIR/L1/l1none.rxt      tests/findings' `l1none` (underivable under utf8)
    DIR/multi2.rxt         two targets, two analyses, one invocation (S994)
"""
import os
import shutil
import sys


def block(name, rows, encs, source, bytes_=None, fidelity=None):
    """One `freq` block serving byte-rate under `encs`, with its stanza."""
    out = ["    freq",
           f"        question fixture '{name}'",
           "        reader byte-rate",
           "        analyzer tests/findings/e1_fixtures.py",
           "        encoding bytes",
           f"        serves byte-rate when {encs} via unigram"]
    for b in sorted(rows):
        out.append(f"        row {b:02x} {rows[b]}")
    out += ["        provenance", f"            source {source}",
            "            retrieved 2026-10-17"]
    if bytes_ is not None:
        out += [f"            bytes {bytes_}", "            sha256 " + "0" * 64]
    if fidelity:
        out.append(f"            fidelity {fidelity}")
    return "\n".join(out) + "\n"


def rows(seed):
    return {0x61 + seed: 4000 + seed, 0x20: 700 + seed, 0x2e: 11 + seed,
            0x51: 2 + seed}


def main(tree, d):
    w = lambda p, t: open(p, "w").write(t)
    for sub in ("COPY", "MDEF", "AUTH", "INC", "CHAIN", "L1"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    shutil.copyfile(os.path.join(tree, "src/findings/default.rxt"),
                    os.path.join(d, "COPY/default.rxt"))
    w(os.path.join(d, "MDEF/default.rxt"), "analysis default\n" +
      block("mdef", rows(1), "byte", "exemplar-mdef", bytes_=4242))
    w(os.path.join(d, "AUTH/mine.rxt"), "analysis mine\n" +
      block("mine", rows(2), "byte", "authored"))
    w(os.path.join(d, "INC/incd.rxt"), "analysis incd\n    include <default>\n" +
      block("incd", rows(3), "utf8", "exemplar-incd", bytes_=333))
    w(os.path.join(d, "CHAIN/outer.rxt"), "analysis outer\n    include <inner>\n" +
      block("outer", rows(4), "utf8", "exemplar-outer", bytes_=444))
    w(os.path.join(d, "CHAIN/inner.rxt"), "analysis inner\n" +
      block("inner", rows(5), "byte,utf8", "exemplar-inner", bytes_=555,
            fidelity="verbatim"))
    w(os.path.join(d, "L1/l1none.rxt"), """analysis l1none
    cpfreq
        question q
        reader r
        analyzer authored
        encoding utf8
        serves byte-rate when utf8 via encode-latin1
        row U+20AC 7
        provenance
            source authored
            retrieved 2026-09-28
""")
    # S994: two targets under two analyses in ONE invocation — each compile
    # builds its own object (a once-per-process object would hand the second
    # target the first's).
    w(os.path.join(d, "multi2.rxt"),
      "config w\n    analysis weblog\n"
      "target t_web = p with w\n"
      "target t_def = p\n\n"
      "pattern a.c\nname p\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
