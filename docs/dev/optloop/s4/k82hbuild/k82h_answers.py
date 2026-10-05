#!/usr/bin/env python3
"""[K82] (B) THE HANDOFF -- the EVERY-STARTPOS ANSWER DIFFERENTIAL over every
program mover (docs/design/litscan_k82h.md §4.2 item 1, §4.3), per route.

  BASE=<pcrec at abi 60> NEW=<pcrec with the handoff> [ABI_FROM=60 ABI_TO=61] \\
      [CFLAGS=...] [PREFIXES=1] [ONLY_K_POS=1] python3 k82h_answers.py k82h_movers.json

For every MOVED (pattern, args) of k82h_movers.py's manifest: BASE and NEW
compiled under the same flags, linked into one TU with
tests/possessify/possdiff_driver.c (span, every capture slot and the failure
surface, at EVERY start position), fed tests/findings/b1_mover_answers.py's
subject sweep plus this row's own families:

  - members of the pattern's language biased to its WIDEST spellings
    (k82h_gen.py, python's own parser -- not pcrec's walk), so a match whose
    window sits exactly K bytes in exists to be found;
  - the pattern's own subjects and those members SHIFTED: each behind 1..K+3 filler bytes, so a
    match sits at, inside and beyond `c - K` from the call's start;
  - each own subject TWICE (the r1 S-F1 two-occurrence shape) and behind a
    decoy of its own last bytes;
  - under `-e utf8` ([r1 S-F5], [r1 C-C7]) ill-formed text: 1..6 stray
    continuation bytes before, inside and after each own subject, a
    truncated lead at the end, an overlong lead. K73/K75 decide; BASE is the
    reference, so no oracle is needed.

THERE IS NO ALLOWANCE. Frank's Q10 ruling declines the handoff on a
count-collapsed prefilter, the one language whose answers can sit below
`c - K`, so the VM attempts exactly the same positions with or without the
handoff and EVERY change of answer or give-up is a DEFECT (§4.2 item 1).

Movers are counted PER ROUTE (DFA unanchored / DFA attempt / VM hybrid); a
route with zero swept movers is a failure ([r1 S-F9], K35). With
ONLY_K_POS=1 only the K > 0 movers are run, and the run reports how many
of them the NEW binary DETECTS (any divergence) -- the K-1 plant's coverage
report (§4.2a (c)), where NEW is a compiler built with sabotage S463.
SHARD=i/n runs every n-th mover from the i-th (the per-route floor is then
checked by the caller over the shards' union). CFLAGS replaces the driver build's flags (the ASan/UBSan arm:
`-O1 -g -fsanitize=address,undefined -fno-builtin-memcmp
-DDIFF_EXACT_SUBJECT`).
"""
import collections, importlib.util, json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
spec = importlib.util.spec_from_file_location(
    "b1", os.path.join(ROOT, "tests/findings/b1_mover_answers.py"))
b1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b1)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k82h_gen   # noqa: E402

BASE, NEW = os.environ["BASE"], os.environ["NEW"]
ABI_FROM, ABI_TO = os.environ.get("ABI_FROM", "60"), os.environ.get("ABI_TO", "61")
CC = os.environ.get("CC", "gcc-16")
CFLAGS = os.environ.get("CFLAGS", "-O1 -std=gnu11 -w").split()
ONLY_K_POS = os.environ.get("ONLY_K_POS") == "1"
DRIVER = os.path.join(ROOT, "tests/possessify/possdiff_driver.c")


def short_subjects(pat):
    letters = sorted(set(re.findall(r"[A-Za-z]", pat)))[:12] or ["a"]
    out = {""}
    word = "".join(letters)
    for k in range(1, 8):
        out.add(word[:k]); out.add(word[:k].upper()); out.add(word[:k].lower())
    return {b1.esc(s.encode("latin-1")) for s in out}


def handoff_subjects(own, gen, k, utf8):
    """The shifted, doubled, decoyed and (utf8) ill-formed families, over the
    pattern's own subjects and its generated widest members (k82h_gen)."""
    out = {b1.esc(g) for g in gen}
    raws = [b1.unesc(o) for o in sorted(own)[:24]] + list(gen)
    for raw in raws:
        if not raw:
            continue
        for j in range(1, k + 4):
            out.add(b1.esc(b"z" * j + raw))
            out.add(b1.esc(b" " * j + raw + b" " + raw))
        out.add(b1.esc(raw + raw))
        out.add(b1.esc(raw + b" " + raw))
        out.add(b1.esc(raw[-3:] + raw))
        if utf8:
            for n in range(1, 7):
                st = b"\x80" * n
                out.add(b1.esc(st + raw))
                out.add(b1.esc(raw[:len(raw) // 2] + st + raw[len(raw) // 2:]))
                out.add(b1.esc(raw + st))
                out.add(b1.esc(b"x" + st + raw + st))
            out.add(b1.esc(raw + b"\xe2\x82"))
            out.add(b1.esc(raw + b"\xc3"))
            out.add(b1.esc(b"\xc0\xaf" + raw))
            out.add(b1.esc(b"\xf0\x9f\x98\x80" + raw))
    return out


def norm_abi(t):
    t = re.sub(rb"(PCREC_RX_ABI_H(?: \+ 0\))? (?:!= )?)%s\b" % ABI_FROM.encode(),
               rb"\g<1>" + ABI_TO.encode(), t)
    return re.sub(rb"\(abi %s\)" % ABI_FROM.encode(), b"(abi " + ABI_TO.encode() + b")", t)


def main():
    rows = json.load(open(sys.argv[1]))
    movers = sorted({(r["pop"], r["pat"], tuple(r["args"]), r["cfg"], r["route"], r["k"])
                     for r in rows if r.get("id") == "moved"})
    if ONLY_K_POS:
        movers = [m for m in movers if m[5]]
    if os.environ.get("SHARD"):   # "i/n": this process runs every n-th mover from i
        i, n = map(int, os.environ["SHARD"].split("/"))
        movers = movers[i::n]
    own = b1.corpus_subjects()
    tally = collections.Counter()
    per_route = collections.Counter()
    detected = collections.Counter()
    undetected = []
    cells = 0
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        for pop, pat, args, cfg, route, k in movers:
            flags = ["--features", "all"] + list(args)
            ra = subprocess.run([BASE.encode(), b"-p", b"pa", b"-o", f"{d}/pa.c".encode(),
                                 *[x.encode() for x in flags], b"--pattern",
                                 pat.encode("latin-1")], capture_output=True, timeout=300)
            rb = subprocess.run([NEW.encode(), b"-p", b"pb", b"-o", f"{d}/pb.c".encode(),
                                 *[x.encode() for x in flags], b"--pattern",
                                 pat.encode("latin-1")], capture_output=True, timeout=300)
            if ra.returncode or rb.returncode:
                tally["skipped"] += 1
                print(f"SKIP {pop} {cfg} {pat[:60]!r}: a side did not compile")
                continue
            # D143's mixed-abi guard: BASE's digit rewritten to NEW's.
            if ABI_FROM != ABI_TO:
                for f in ("pa.c", "pa.h"):
                    p = f"{d}/{f}"
                    open(p, "wb").write(norm_abi(open(p, "rb").read()))
            cc = subprocess.run([CC] + CFLAGS + ["-I", d, '-DDIFF_A_LABEL="base"',
                                 '-DDIFF_B_LABEL="new"', "-o", f"{d}/t", DRIVER,
                                 f"{d}/pa.c", f"{d}/pb.c"], capture_output=True, timeout=600)
            if cc.returncode:
                tally["defect"] += 1
                print(f"FAIL {pop} {cfg} {pat[:60]!r}: driver did not build: {cc.stderr[:300]!r}")
                continue
            key = pat.encode("latin-1").decode("utf-8", "surrogateescape")
            mine = own.get(key, set())
            gen = k82h_gen.members(pat.encode("latin-1"), "utf8" in args)
            subj = set(b1.subjects(key, mine)) | short_subjects(pat) | \
                handoff_subjects(mine, gen, k or 0, "utf8" in args)
            run = subprocess.run([f"{d}/t"], input=("\n".join(sorted(subj)) + "\n").encode(
                                 "latin-1", "surrogateescape"), capture_output=True, timeout=900)
            m = re.search(rb"cells (\d+)", run.stdout)
            cells += int(m.group(1)) if m else 0
            per_route[route] += 1
            err = run.stderr.decode("latin-1")
            if run.returncode == 0:
                tally["identical"] += 1
                if ONLY_K_POS:
                    undetected.append((pop, cfg, pat, k))
                continue
            sani = "Sanitizer" in err or "runtime error" in err
            tally["defect"] += 1
            detected[route] += 1
            divs = re.findall(r"DIVERGENCE subject=(.*) startpos=(\d+)\n  base: (.*)\n  new: (.*)\n", err)
            if not ONLY_K_POS or sani:
                print(f"DEFECT {pop} {cfg} {route} K={k} {pat[:60]!r}: rc={run.returncode} "
                      f"{'SANITIZER ' if sani else ''}{err[:300]!r}")
                for s, p, a, b in divs[:3]:
                    print(f"   subject={s[:60]} startpos={p}: {a} -> {b}")
    n = len(movers)
    print(f"movers {n} (per route {dict(per_route)}): identical {tally['identical']}, "
          f"DEFECT {tally['defect']}, skipped {tally['skipped']}; cells compared {cells}")
    if ONLY_K_POS:
        print(f"K>0 plant coverage: {sum(detected.values())} of {n - tally['skipped']} "
              f"detected (per route {dict(detected)}); undetected:")
        for pop, cfg, pat, k in undetected:
            print(f"   UNDETECTED {pop} {cfg} K={k} {pat[:70]!r}")
        sys.exit(0 if n else 1)
    for r in ("unanchored", "attempt", "hybrid"):
        if per_route[r] == 0:
            print(f"FAIL: route {r} has no swept mover (K35)")
            tally["defect"] += 1
    print(f"k82h_answers: {'PASS' if tally['defect'] == 0 else 'FAIL'}")
    sys.exit(1 if tally["defect"] else 0)


if __name__ == "__main__":
    main()
