#!/usr/bin/env python3
"""[START-SET] edge lane: search a small pattern family for a DFA-hat MOVER on
which the UNCONDITIONAL re-seed (pf_emit_ofs_reseed's `pos ? seed[..] : s0`)
answers differently from the conditional one, i.e. a machine where state 0 is
re-entered mid-scan through a byte whose seed differs.  Also reports, for
every mover, the no-re-seed twin's diffs (the count-collapsed obligation's
shape).  Env: PCREC, FSP, W.   search_uncond.py OUT_TSV [N_PATTERNS] [extra pcrec flags]"""
import itertools, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import hat, mut
ATOMS = [r"\b", r"\B", r"(?<=a)", r"(?<!a)", r"(?<=[ab])", "x", "y", "a", "ab", "xy", "[xy]", r"\w", " ", r"(?=x)", "z"]
CTX = [r"\b", r"\B", r"(?<=a)", r"(?<!b)", "", "x"]
CORE = ["(ab|cd)", "(a|b)", "(ab|c)", "(x|ab)", "(a)", "([ab]c)"]
def gen_collapsed(rng):
    m = rng.randint(1, 2); n = m + rng.randint(1, 2)
    return rng.choice(CTX) + rng.choice(CORE) + "{%d,%d}" % (m, n) + rng.choice([r"\b", r"\B", "", "y", r"(?=a)"])
def gen(rng):
    if os.environ.get("FAMILY") == "collapsed": return gen_collapsed(rng)
    br = []
    for _ in range(rng.randint(2, 3)):
        br.append("".join(rng.choice(ATOMS) for _ in range(rng.randint(1, 3))))
    return "(?:" + "|".join(br) + ")" + rng.choice(["", "y", r"\b", "z", "a"])
def main():
    out, N = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 400
    xf = sys.argv[3:]
    rng = random.Random(148); seen = set(); rows = []
    alpha = [b"a", b"b", b"x", b"y", b"z", b" "]
    subs = [b"".join(t) for n in range(6) for t in itertools.product(alpha, repeat=n)]
    cases = [(p, s) for s in subs for p in range(len(s) + 1)]
    while len(seen) < N:
        pat = gen(rng)
        if pat in seen: continue
        seen.add(pat)
        b = {"pat": pat, "flags": "", "enc": "byte", "engine": None, "frames": None, "xflags": xf}
        d = os.path.join(os.environ["W"], "su"); c = hat.classify(b, d)
        if c.get("hat") != "dfa": continue
        if os.environ.get("FAMILY") == "collapsed" and c.get("lang") != "count-collapsed": continue
        S, m = c["S"], c["m"]; T = S & m["Estar"]
        arts = [("rx", open(c["path"]).read())]
        for p, mode in (("tc", "cond"), ("tu", "uncond"), ("tn", "none")):
            path, _ = hat.compile_block(b, d, p); arts.append((p, hat.dfa_twin(open(path).read(), p, T, mode)))
        exe = mut.build(d, arts); res = mut.run(exe, cases)
        dc = sum(r[1] != r[0] for r in res); du = [cs for cs, r in zip(cases, res) if r[2] != r[0]]; dn = sum(r[3] != r[0] for r in res)
        rows.append((pat, (c["vmpf"] or c["engine"]) + "/" + (c.get("lang") or "-"), len(S), len(m["E"]), len(m["seeds"]), dc, len(du), dn, repr(du[0]) if du else ""))
        if du or dc: print("FOUND", rows[-1], flush=True)
    with open(out, "w") as f:
        f.write("pattern\troute\tS\tE\tnseeds\tcond_diffs\tuncond_diffs\tnoreseed_diffs\tuncond_witness\n")
        for r in rows: f.write("\t".join(map(str, r)) + "\n")
    print("movers %d, cond-diffs>0 %d, uncond-diffs>0 %d, noreseed-diffs>0 %d" % (len(rows), sum(r[5] > 0 for r in rows), sum(r[6] > 0 for r in rows), sum(r[7] > 0 for r in rows)))
if __name__ == "__main__": main()
