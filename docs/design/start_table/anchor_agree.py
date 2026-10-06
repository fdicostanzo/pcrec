#!/usr/bin/env python3
"""docs/design/start_table/anchor_agree.py -- does the DFA route's anchoring
decision (ENG_ATTEMPT's `start_max`, read off the MACHINE: dfa_interior_dead
over s1u/s1g) agree with the `start_anchor` FACT (the AST walk the VM's
attempt_max, G2's VM arm and the reseed `anchored` row read)?

Two derivations of one question are the disagreement start_table.md §2.4
must name. emit_dfa.c asserts one direction (fact anchored => machine
anchored); this counts the other (machine anchored, fact unanchored), which
the code calls "welcome". Read off the emitted text and --emit-facts only.

Usage: anchor_agree.py PCREC_BIN TREE [extra pcrec args...]
"""
import collections, os, re, subprocess, sys
sys.path.insert(0, os.path.join(sys.argv[2], "scripts"))
import emit_sweep as es  # noqa: E402

binp, tree, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
pats = sorted(set(p[2].encode("utf-8", "surrogateescape") if isinstance(p[2], str) else p[2]
                  for p in es.enumerate_corpus(binp, tree, 30)))
cnt = collections.Counter()
ex = collections.defaultdict(list)
for pat in pats:
    base = [binp.encode(), b"--features", b"all"] + [e.encode() for e in extra]
    r = subprocess.run(base + [b"-p", b"rx", b"-o", b"-", b"--pattern", pat], capture_output=True)
    if r.returncode or b'#define RX_DFA_SCAN "attempt"' not in r.stdout:
        continue
    m = re.search(rb"const size_t start_max = ([^;]*);", r.stdout)
    mach = "none" if not m else ("bot" if m.group(1).startswith(b"0") else
                                 "gstart" if m.group(1).startswith(b"search_from") else "none")
    f = subprocess.run(base + [b"--emit-facts", b"--pattern", pat], capture_output=True)
    fm = re.search(rb"\tstart_anchor\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([^\t]*)\t", f.stdout)
    fact = fm.group(1).decode() if fm else "?"
    key = f"machine={mach} fact={fact}"
    cnt[key] += 1
    if len(ex[key]) < 4:
        ex[key].append(pat.decode("utf-8", "replace"))
for k, n in sorted(cnt.items()):
    print(f"{n:5d}  {k}   e.g. {ex[k]}")
