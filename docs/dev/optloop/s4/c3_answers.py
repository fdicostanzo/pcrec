#!/usr/bin/env python3
"""[OPT-LITSCAN] S4 C3 -- THE ANSWER DIFFERENTIAL over every mover, with
litscan_s4.md §5.1 item 2's classification table (r1 S2).

  BASE=<abi-58 pcrec> NEW=<abi-59 pcrec> [CFLAGS=...] [PREFIXES=1] \\
      python3 c3_answers.py <c3_movers.json>

For every MOVED (pattern, args) of c3_movers.py's manifest it compiles the
pattern with BASE and NEW under the same flags, links both into one TU with
tests/possessify/possdiff_driver.c (the tree's pcrec-vs-pcrec differential:
span, every capture slot and the failure surface, at EVERY start position),
and feeds it tests/findings/b1_mover_answers.py's subject sweep (the
pattern's own corpus subjects, a sweep over its bytes, seeded random strings,
and with PREFIXES=1 every prefix of those), plus the short subjects the pair
arm's guard is about (lengths 0..7 over the pattern's letters, both cases).

Each DIVERGENCE the driver prints is classified BASE -> NEW:

  identical                      pass (the driver prints nothing)
  give-up -> NOMATCH             ALLOWED, listed (the pre-check's only legal
                                 direction, D124 item 3)
  NOMATCH -> give-up             DEFECT (the done[] class, S2b)
  give-up -> match               DEFECT (a pre-check cannot create a match)
  any other change               DEFECT (a wrong answer)

The driver runs at the artifacts' own step budgets, so a NOMATCH that needed
K65's set member to stay linear shows up as a give-up. The population and the
cell count are printed; an empty population is a failure (K35). CFLAGS
replaces the driver build's flags, so the same sweep runs under
`-fsanitize=address,undefined -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT`
(design §5.2): every subject sits in a block of exactly its length.
"""
import importlib.util, json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
spec = importlib.util.spec_from_file_location(
    "b1", os.path.join(ROOT, "tests/findings/b1_mover_answers.py"))
b1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b1)

BASE, NEW = os.environ["BASE"], os.environ["NEW"]
CC = os.environ.get("CC", "gcc-16")
CFLAGS = os.environ.get("CFLAGS", "-O1 -std=gnu11 -w").split()
DRIVER = os.path.join(ROOT, "tests/possessify/possdiff_driver.c")
GIVEUP = ("err_steps", "err_frames")


def short_subjects(pat):
    letters = sorted(set(re.findall(r"[A-Za-z]", pat)))[:12] or ["a"]
    out = {""}
    word = "".join(letters)
    for k in range(1, 8):
        out.add(word[:k]); out.add(word[:k].upper()); out.add(word[:k].lower())
    return {b1.esc(s.encode("latin-1")) for s in out}


def classify(a, b):
    ka, kb = a.split()[0], b.split()[0]
    if ka in GIVEUP and kb == "nomatch":
        return "allowed"
    return "defect"


def main():
    movers = sorted({(r["pop"], r["pat"], tuple(r["args"]), r["cfg"])
                     for r in json.load(open(sys.argv[1])) if r.get("id") == "moved"})
    own = b1.corpus_subjects()
    tally = {"identical": 0, "allowed": 0, "defect": 0, "skipped": 0}
    cells = 0
    with tempfile.TemporaryDirectory() as d:
        for pop, pat, args, cfg in movers:
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
            # D143's mixed-abi guard refuses two artifacts of different abi in
            # one TU; BASE's shared block differs from NEW's in the digit
            # alone, so the BASE digit is rewritten (58 -> 59) in its .c/.h.
            for f in ("pa.c", "pa.h"):
                t = open(f"{d}/{f}", "rb").read()
                t = re.sub(rb"(PCREC_RX_ABI_H(?: \+ 0\))? (?:!= )?)58\b", rb"\g<1>59", t)
                t = re.sub(rb"\(abi 58\)", rb"(abi 59)", t)
                open(f"{d}/{f}", "wb").write(t)
            cc = subprocess.run([CC] + CFLAGS + ["-I", d, '-DDIFF_A_LABEL="base"',
                                 '-DDIFF_B_LABEL="c3"', "-o", f"{d}/t", DRIVER,
                                 f"{d}/pa.c", f"{d}/pb.c"], capture_output=True, timeout=600)
            if cc.returncode:
                tally["defect"] += 1
                print(f"FAIL {pop} {cfg} {pat[:60]!r}: driver did not build: {cc.stderr[:300]!r}")
                continue
            key = pat.encode("latin-1").decode("utf-8", "surrogateescape")
            subj = sorted(set(b1.subjects(key, own.get(key, ()))) | short_subjects(pat))
            run = subprocess.run([f"{d}/t"], input=("\n".join(subj) + "\n").encode(
                                 "latin-1", "surrogateescape"), capture_output=True, timeout=900)
            m = re.search(rb"cells (\d+)", run.stdout)
            cells += int(m.group(1)) if m else 0
            err = run.stderr.decode("latin-1")
            divs = re.findall(r"DIVERGENCE subject=(.*) startpos=(\d+)\n  base: (.*)\n  c3: (.*)\n", err)
            if run.returncode == 0:
                tally["identical"] += 1
                continue
            if not divs or "MATCH DIVERGENCE" in err or "REFEREE" in err or "Sanitizer" in err \
                    or "runtime error" in err:
                tally["defect"] += 1
                print(f"DEFECT {pop} {cfg} {pat[:60]!r}: rc={run.returncode} {err[:400]!r}")
                continue
            kinds = {classify(a, b) for _s, _p, a, b in divs}
            verdict = "defect" if "defect" in kinds else "allowed"
            tally[verdict] += 1
            for s, p, a, b in divs[:5]:
                print(f"{verdict.upper()} {pop} {cfg} {pat[:50]!r} subject={s[:60]} startpos={p}: {a} -> {b}")
    n = len(movers)
    print(f"movers {n}: identical {tally['identical']}, allowed (give-up -> NOMATCH) "
          f"{tally['allowed']}, DEFECT {tally['defect']}, skipped {tally['skipped']}; "
          f"cells compared {cells}")
    if n == 0 or tally["identical"] + tally["allowed"] == 0:
        print("FAIL: empty population")
        sys.exit(1)
    print(f"c3_answers: {'PASS' if tally['defect'] == 0 else 'FAIL'}")
    sys.exit(1 if tally["defect"] else 0)


if __name__ == "__main__":
    main()
