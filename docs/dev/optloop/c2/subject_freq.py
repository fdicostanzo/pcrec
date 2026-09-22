#!/usr/bin/env python3
"""[OPTLOOP.2 c2prep] The bench throughput subjects' byte and RUN census.

Shared input to two cycle-2 deliverables:

  * `firstset_design.md`'s COST MODEL — the candidate-start set's summed
    byte frequency is the model's only subject-side term, and this script
    is where the numbers in that note's worked examples come from.
  * `reqpos_census.md`'s tier-2b half — "how rare is the PAIR against the
    single byte", which is a property of the subject text and not of the
    pattern.

The subjects are REGENERATED from pcrec-bench's own `captext.py` into a
scratch directory and verified against the hashes `cycle1_analysis.md`
(setup 0.3) pins.  Nothing is written inside pcrec-bench.  No timing is
taken anywhere in this file: every number is a count.

Usage:  SUBJ=<dir of t-*.bin> python3 subject_freq.py
"""
import os, sys, json, collections

PINNED = {
    "t-64k":   "d2e4f134473cc40a9a4e7df7a30e0efa11f566d96ee990c62cd663a2439c8524",
    "t-256k":  "3cf7b248873da164518b74e039cc2380f39e233b2899716c82c8eb4b7b49b5a7",
    "t-1m":    "ccbdf7eb97f15776a68b8bbb9d6387870cd01d4796207fb20032958caf9754ee",
}

# The candidate-start SETS the design note's worked examples turn on.  Each
# is written as the set pcrec derives today and the set the AST-level
# analysis would derive, so the model can be evaluated on both.
WORD = set(bytes(range(0x30,0x3a)) + bytes(range(0x41,0x5b))
           + bytes(range(0x61,0x7b)) + b"_")
SETS = {
    "word-63 (today's set behind a leading \\b)": WORD,
    "aws {A}":                    set(b"A"),
    "json-constant {t,f,n}":      set(b"tfn"),
    "nested-comment-rec {/}":     set(b"/"),
    "digits":                     set(bytes(range(0x30,0x3a))),
    "upper":                      set(bytes(range(0x41,0x5b))),
}

# Literal RUNS (tier 2b / the pair filter).  A run is scored by how often
# it occurs, against the rarest single byte in it -- the ratio IS the pair
# filter's selectivity gain.
RUNS = [b"tr", b"fa", b"nu", b"true", b"false", b"null",
        b"AKIA", b"://", b"https://", b"</", b"/*", b"*/"]

def census(path):
    b = open(path, "rb").read()
    n = len(b)
    freq = collections.Counter(b)
    return b, n, freq

def main():
    subj = os.environ.get("SUBJ")
    if not subj:
        sys.exit("SUBJ=<dir> required")
    import hashlib
    out = {}
    for sid in ("t-64k", "t-256k", "t-1m"):
        p = os.path.join(subj, sid + ".bin")
        b, n, freq = census(p)
        h = hashlib.sha256(b).hexdigest()
        if h != PINNED[sid]:
            sys.exit("%s: hash %s != pinned %s -- STOP" % (sid, h, PINNED[sid]))
        rec = {"n": n, "sha256": h}
        rec["bytes"] = {("%02x" % k): v for k, v in sorted(freq.items())}
        rec["sets"] = {}
        for name, s in SETS.items():
            c = sum(freq[x] for x in s)
            rec["sets"][name] = {"count": c, "density": c / n, "size": len(s)}
        rec["runs"] = {}
        for r in RUNS:
            # count occurrences (overlapping), and the rarest member byte
            c, i = 0, b.find(r)
            while i >= 0:
                c += 1
                i = b.find(r, i + 1)
            member = {chr(x): freq[x] for x in set(r)}
            rarest = min(member.values())
            rec["runs"][r.decode("latin-1")] = {
                "count": c, "density": c / n,
                "rarest_member": rarest,
                "rarest_density": rarest / n,
                "gain_vs_rarest_member": (rarest / c) if c else None,
            }
        out[sid] = rec
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
