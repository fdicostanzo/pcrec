#!/usr/bin/env python3
"""K128 differential: repeat-of-alternation-with-an-empty-branch patterns,
pcrec (default + vm engines) against libpcre2, captures compared.

usage: emptyiter_diff.py PCREC OUTDIR [--n N] [--seed S] [--jobs J]
Prints one line per divergent (pattern, engine) and a summary line
"== emptyiter_diff COMPLETE: P patterns, C checks, D divergent, R refused".
"""
import itertools, os, random, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = ["()", "(a?)", "(b|)", "", "a", "ab", "(a)", "b", "a*", "(a)?"]
QUANTS = ["+", "+?", "{2,}", "{2,}?", "*", "*?", "++", "*+", "{8,}?", "{9,}", "{1,2}?", "{1,3}"]
CONTS = ["b", "c", "$", "b$", "\\1", "(b)?c"]
SUBJECTS = ["", "a", "b", "ab", "aab", "abab", "abc", "ba", "aabbc", "bc"]

def nullable_branch(b):
    return b in ("", "()", "(a?)", "(b|)", "a*", "(a)?")

def family():
    """The whole family, in a fixed order: every ordered pair (and some triples)
    of POOL branches with at least one empty-matching branch, under every
    quantifier and continuation, in four wrappings."""
    bodies = [b for b in ("|".join(t) for t in itertools.permutations(POOL, 2)
                          if any(nullable_branch(x) for x in t))]
    bodies += ["()|a|()", "a|()|b", "(a)|()|ab", "()|ab|a", "|(a)|b"]
    pats = []
    for body, q, c in itertools.product(bodies, QUANTS, CONTS):
        pats.append("(?:%s)%s%s" % (body, q, c))
        pats.append("(%s)%s%s" % (body, q, c))
        pats.append("((?:%s)%s)%s" % (body, q, c))
        pats.append("(?:(?:%s)%s%s)+?" % (body, q, c if c not in ("$", "b$") else "b"))
    return [p for p in pats if "\\1" not in p or "(" in p.replace("(?:", "")]

def gen(n, seed):
    pats = family()
    return random.Random(seed).sample(pats, min(n, len(pats)))

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120, **kw)

def one(pcrec, out, i, p):
    ref = run([os.path.join(out, "p2ref"), p] + SUBJECTS).stdout
    if ref.startswith("COMPILE-ERROR"):
        return [("skip", p, "", "pcre2 refuses")]
    res = []
    for eng in ("default", "vm"):
        d = tempfile.mkdtemp(dir=out, prefix="c%d%s" % (i, eng))
        args = [pcrec, "-p", "rx", "--features", "all", "--pattern", p, "-o", os.path.join(d, "art.c")]
        if eng == "vm": args.insert(5, "--engine=vm")
        r = run(args)
        if r.returncode != 0:
            res.append(("refused", p, eng, r.stderr.strip().splitlines()[0] if r.stderr else ""))
            continue
        exe = os.path.join(d, "s")
        r = run(["gcc", "-O0", "-w", "-I" + d, "-o", exe, os.path.join(HERE, "pcdrv.c"),
                 os.path.join(d, "art.c")])
        if r.returncode != 0:
            res.append(("ccfail", p, eng, r.stderr[:200])); continue
        got = run([exe] + SUBJECTS).stdout
        res.append(("ok" if got == ref else "DIVERGE", p, eng, "" if got == ref else
                    "\n   ref: " + ref.replace("\n", "\n        ") + "\n   got: " + got.replace("\n", "\n        ")))
        subprocess.run(["rm", "-rf", d])
    return res

def main():
    pcrec, out = sys.argv[1], sys.argv[2]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 300
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 128
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 4
    os.makedirs(out, exist_ok=True)
    subprocess.run(["gcc", "-O1", "-o", os.path.join(out, "p2ref"), os.path.join(HERE, "p2ref.c"),
                    "-lpcre2-8"], check=True)
    pats = gen(n, seed)
    with ThreadPoolExecutor(jobs) as ex:
        allres = list(ex.map(lambda ip: one(pcrec, out, ip[0], ip[1]), enumerate(pats)))
    cnt = {"ok": 0, "DIVERGE": 0, "refused": 0, "ccfail": 0, "skip": 0}
    for rs in allres:
        for kind, p, eng, why in rs:
            cnt[kind] += 1
            if kind != "ok":
                print("%s %s [%s] %s" % (kind, p, eng, why))
    print("== emptyiter_diff COMPLETE: %d patterns, %d checks, %d divergent, %d refused, %d ccfail, %d pcre2-refused"
          % (len(pats), cnt["ok"] + cnt["DIVERGE"], cnt["DIVERGE"], cnt["refused"], cnt["ccfail"], cnt["skip"]))

if __name__ == "__main__":
    main()
