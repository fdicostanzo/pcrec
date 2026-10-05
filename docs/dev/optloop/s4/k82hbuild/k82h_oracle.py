#!/usr/bin/env python3
"""[K82] (B) THE INVARIANT-F ORACLE (docs/design/litscan_k82h.md §4.2a (b)).

  NEW=<pcrec with the handoff> PCREC_PCRE2_PATH=<libpcre2-8> \\
      python3 k82h_oracle.py k82h_movers.json

INVARIANT F: for a pattern whose `req_run_maxoff` is a finite K, every
successful attempt at any `p` contains a masked occurrence of the run's window
at some `q` with `p <= q <= p + K`. It is a claim about the PATTERN'S
LANGUAGE, so it is checked with no pcrec code in the loop: for every program
mover of k82h_movers.py's manifest (one row per distinct pattern and
semantic flags -- the engine and capture configs share a language), every
subject of k82h_answers.py's sweep and every start position `p`, libpcre2 is
asked for an ANCHORED match at `p` (compile-time PCRE2_ANCHORED, startoffset
`p`; under `-e utf8` with PCRE2_UTF | PCRE2_MATCH_INVALID_UTF, at character
starts only), and where one exists the window -- `<PREFIX>_REQ_RUN`'s bytes
and mask, the ONE input shared with pcrec, read off the stamp -- must occur
in `[p, p + K]`. An anchored match at `p` makes `\\G` true at `p`, so it tests
a SUPERSET of the real successes; F must hold there too, because the walk
counts `\\G` as zero-width. Where python `re` compiles a byte pattern it is
asked the same question (`match(s, p)`) as a cross-check.

KDELTA=-1 is its failing-direction control (every K > 0 checked as K - 1).

Reports cells checked, matches found and VIOLATIONS per population (K35:
an empty population fails); 0 violations is the bar, and a violation is a K
that deletes matches.
"""
import collections, importlib.util, json, os, re, subprocess, sys, warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../../.."))
os.environ.setdefault("PCREC_PCRE2_PATH", "/opt/homebrew/lib/libpcre2-8.dylib")
_spec = importlib.util.spec_from_file_location(
    "pcre2_ctypes", os.path.join(ROOT, "docs/design/eng_brep_measurements/probes/pcre2_ctypes.py"))
p2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p2)
sys.path.insert(0, HERE)
os.environ.setdefault("BASE", os.environ.get("NEW", ""))   # k82h_answers reads both
import k82h_gen          # noqa: E402
import k82h_answers as A  # noqa: E402  (its subject families, b1's sweep)

NEW = os.environ["NEW"]
# THE FAILING-DIRECTION CONTROL: KDELTA=-1 checks every pattern against K - 1,
# which must produce violations wherever a match uses its full offset (the
# oracle's own sabotage; a run that reports 0 there could not see a short K).
KDELTA = int(os.environ.get("KDELTA", "0"))
ANCHORED, UTF, INVALID_UTF, CASELESS, UCP = 0x80000000, 0x00080000, 0x04000000, 0x8, 0x00020000
SEMANTIC = ("-e", "-i", "--ucp")


def run_stamp(pat, args):
    r = subprocess.run([NEW.encode(), b"--features", b"all", b"--emit-facts",
                        *[a.encode() for a in args], b"--pattern", pat],
                       capture_output=True, timeout=300)
    for ln in r.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] == "req_run":
            return f[6]
    return None


def parse_run(v):
    h, mk = v.split("@")[0], (v.split("/")[1] if "/" in v else "")
    t = bytes.fromhex(h)
    k = bytes.fromhex(mk) if mk else b"\xff" * len(t)
    return t, k


def occurs(b, t, k, lo, hi):
    n = len(t)
    for q in range(lo, min(hi, len(b) - n) + 1):
        if all((b[q + i] & k[i]) == t[i] for i in range(n)):
            return True
    return False


def semantic_args(args):
    out, i = [], 0
    while i < len(args):
        if args[i] == "-e":
            out += args[i:i + 2]; i += 2; continue
        if args[i] in ("-i", "--ucp"):
            out.append(args[i])
        i += 1
    return tuple(out)


def main():
    rows = json.load(open(sys.argv[1]))
    pats = {}
    for r in rows:
        if r.get("id") != "moved" or r.get("k") is None:
            continue
        key = (r["pop"], r["pat"], semantic_args(r["args"]))
        pats.setdefault(key, r["k"] + KDELTA if r["k"] else r["k"])
    items = sorted(pats.items())
    if os.environ.get("SHARD"):   # "i/n": every n-th pattern from the i-th
        i, n = map(int, os.environ["SHARD"].split("/"))
        items = items[i::n]
    own = A.b1.corpus_subjects()
    tally = collections.Counter()
    viol = []
    for (pop, pat, args), k in items:
        pb = pat.encode("latin-1")
        utf8 = "utf8" in args
        st = run_stamp(pb, list(args))
        if not st or st == "none":
            tally["no-run"] += 1; continue
        t, km = parse_run(st)
        opts = ANCHORED | (UTF | INVALID_UTF if utf8 else 0) | \
            (CASELESS if "-i" in args else 0) | (UCP if "--ucp" in args else 0)
        try:
            cx = p2.compile(pb, opts)
        except Exception:
            tally["pcre2-refused"] += 1; continue
        py = None
        if not utf8 and "--ucp" not in args:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    py = re.compile(pb.decode("latin-1"), re.IGNORECASE if "-i" in args else 0)
            except re.error:
                py = None
        key = pb.decode("utf-8", "surrogateescape")
        mine = own.get(key, set())
        gen = k82h_gen.members(pb, utf8)
        subj = set(A.b1.subjects(key, mine)) | A.short_subjects(pat) | \
            A.handoff_subjects(mine, gen, k, utf8)
        tally["patterns"] += 1
        tally["K>0 patterns"] += bool(k)
        for e in sorted(subj):
            b = A.b1.unesc(e)
            for p in range(len(b) + 1):
                if utf8 and p < len(b) and (b[p] & 0xC0) == 0x80:
                    continue
                tally["cells"] += 1
                try:
                    m = cx.search(b, p)
                except Exception:
                    tally["pcre2-error"] += 1; continue
                # PCRE2_MATCH_INVALID_UTF moves an anchored attempt PAST an
                # ill-formed sequence it starts in; that is not an attempt at
                # `p`, so it is counted apart (a `\\K` match reports a later
                # start of its own and stays an attempt at `p`).
                if m and m[0][0] != p and "\\K" not in pat:
                    tally["pcre2 moved past an ill-formed start"] += 1
                    m = None
                if m:
                    tally["pcre2 matches"] += 1
                    if not occurs(b, t, km, p, p + k):
                        tally["VIOLATIONS"] += 1
                        if len(viol) < 20:
                            viol.append(f"pcre2 {pop} {pat[:50]!r} {args} K={k} p={p} span={m[0]} subj={e[:60]}")
                if py is not None:
                    pm = py.match(b.decode("latin-1"), p)
                    if pm:
                        tally["python matches"] += 1
                        if not occurs(b, t, km, p, p + k):
                            tally["python VIOLATIONS"] += 1
                            if len(viol) < 20:
                                viol.append(f"python {pop} {pat[:50]!r} K={k} p={p} span={pm.span()} subj={e[:60]}")
    for v in viol:
        print("VIOLATION " + v)
    print("k82h_oracle: " + ", ".join(f"{a} {b}" for a, b in sorted(tally.items())))
    bad = tally["VIOLATIONS"] + tally["python VIOLATIONS"]
    if tally["patterns"] == 0 or tally["pcre2 matches"] == 0:
        print("FAIL: empty population (K35)"); bad += 1
    print(f"k82h_oracle: {'PASS' if bad == 0 else 'FAIL'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
