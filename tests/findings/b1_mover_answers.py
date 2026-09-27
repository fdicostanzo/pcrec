#!/usr/bin/env python3
"""tests/findings/b1_mover_answers.py — [FINDINGS] B1's §13 (2) acceptance:
every artifact the B1 change MOVED (a per-artifact mover manifest, as the A/B
instrument docs/dev/optloop/s1/s1_identity.py writes it) must ANSWER and GIVE
UP identically to its pre-change twin.

For each moved (pattern, config) it compiles the pattern with the BASE and the
NEW compiler under the same flags (prefixes `pa`/`pb`), links both into one TU
with tests/possessify/possdiff_driver.c — the tree's pcrec-vs-pcrec
differential, which compares the match span, every capture slot and the
FAILURE SURFACE (a give-up must be the same give-up) at EVERY start position —
and feeds it subjects from three sources: the pattern's own corpus `m`/`n`
lines where it has any, a sweep over the pattern's own bytes (runs and
repetitions), and seeded random strings over those bytes plus UTF-8 lead and
continuation bytes. The population and the cell count are printed, and an
empty population is a failure (K35).

[OPT-LITSCAN] S2a (lane s2a) REUSES it for its movers and adds two knobs:
`CFLAGS` replaces the driver build's flags (default `-O1 -std=gnu11 -w`), so
the same sweep runs under `-fsanitize=address,undefined` with
`-DDIFF_EXACT_SUBJECT` (the driver then hands each subject over in a block of
exactly its length); and `PREFIXES=1` adds every prefix of every own subject
and of every literal word in the pattern, the subjects that end INSIDE a
literal run, which is where a subject-end guard is exercised.

Not part of `make test`: it needs the pre-change compiler. Usage:
  BASE=<pcrec> NEW=<pcrec> EXTRA="-e utf8" python3 b1_mover_answers.py \\
      s1_identity.json [s1_identity.json ...]
"""
import glob, json, os, random, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BASE, NEW = os.environ["BASE"], os.environ["NEW"]
EXTRA = os.environ.get("EXTRA", "").split()
CC = os.environ.get("CC", "gcc-16")
CFLAGS = os.environ.get("CFLAGS", "-O1 -std=gnu11 -w").split()
PREFIXES = os.environ.get("PREFIXES") == "1"
DRIVER = os.path.join(ROOT, "tests/possessify/possdiff_driver.c")
CFG = {"auto": ["--features", "all"], "vm": ["--features", "all", "--engine=vm"],
       "auto-caps": ["--features", "all"],
       "auto-nocaps": ["--features", "all", "--no-captures"],
       "vm-caps": ["--features", "all", "--engine=vm"],
       "vm-nocaps": ["--features", "all", "--engine=vm", "--no-captures"]}
BENCH = "/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"


def esc(b):
    return "".join(chr(c) if 0x21 <= c < 0x7f and c not in (0x5c, 0x22) else "\\x%02x" % c
                   for c in b)


def unesc(t):
    """An `.rxt`/driver-escaped subject back to its bytes (`\\ \\t \\n \\r \\xNN`)."""
    out, i, raw = bytearray(), 0, t.encode("latin-1", "surrogateescape")
    while i < len(raw):
        c = raw[i]
        if c == 0x5c and i + 1 < len(raw):
            n = raw[i + 1]
            if n == ord("x") and i + 3 < len(raw):
                out.append(int(raw[i + 2:i + 4], 16)); i += 4; continue
            out.append({ord("t"): 9, ord("n"): 10, ord("r"): 13}.get(n, n)); i += 2; continue
        out.append(c); i += 1
    return bytes(out)


def corpus_subjects():
    """pattern text -> the escaped subjects its .rxt blocks test."""
    out = {}
    for path in glob.glob(f"{ROOT}/tests/**/*.rxt", recursive=True):
        cur = None
        for ln in open(path, "rb").read().decode("utf-8", "surrogateescape").splitlines():
            if ln.startswith("pattern "):
                cur = ln[len("pattern "):]
                continue
            m = re.match(r'^(?:m|n|ms|ns|mc)\s+(?:\d+\s+)?"((?:[^"\\]|\\.)*)"', ln)
            if cur is not None and m:
                out.setdefault(cur, set()).add(m.group(1))
    return out


def subjects(pat, own):
    b = pat.encode("utf-8", "surrogateescape")
    alpha = sorted(set(c for c in b if c not in b"\\^$.|?*+(){}[],-"))[:24] or list(b"ab")
    s = set(own) | {"", "q"}
    if PREFIXES:
        for o in sorted(own)[:64]:
            raw = unesc(o)
            for k in range(len(raw)):
                s.add(esc(raw[:k]))
        for w in re.findall(rb"[A-Za-z0-9_]{2,}", b):
            for k in range(1, len(w) + 1):
                s.add(esc(w[:k]))
    for c in alpha:
        for n in (1, 2, 3, 8):
            s.add(esc(bytes([c]) * n))
    s.add(esc(bytes(alpha) * 3))
    rnd = random.Random(0xB1)
    pool = alpha + [0xC3, 0xA9, 0xE2, 0x82, 0xAC, 0x80, 0x0A, 0x20]
    for _ in range(40):
        s.add(esc(bytes(rnd.choice(pool) for _ in range(rnd.randint(1, 40)))))
    return sorted(s)


def main():
    movers = []
    for j in sys.argv[1:]:
        for r in json.load(open(j)):
            if r["identity"] == "changed":
                pat = r["key"] if r["pop"] == "corpus" else \
                    open(os.path.join(BENCH, r["key"] + ".rx"), "rb").read() \
                    .rstrip(b"\n").decode("utf-8", "surrogateescape")
                movers.append((r["pop"], r["key"], pat, r["cfg"]))
    movers = sorted(set(movers))
    own = corpus_subjects()
    ok = bad = skipped = cells = 0
    with tempfile.TemporaryDirectory() as d:
        for pop, key, pat, cfg in movers:
            flags = CFG[cfg] + EXTRA
            ra = subprocess.run([BASE, "-p", "pa", "-o", f"{d}/pa.c", "--pattern", pat] + flags,
                                capture_output=True, timeout=300)
            rb = subprocess.run([NEW, "-p", "pb", "-o", f"{d}/pb.c", "--pattern", pat] + flags,
                                capture_output=True, timeout=300)
            if ra.returncode or rb.returncode:
                skipped += 1
                print(f"SKIP {pop} {cfg} {key[:60]!r}: a side did not compile")
                continue
            cc = subprocess.run([CC] + CFLAGS + ["-I", d,
                                 '-DDIFF_A_LABEL="base"', '-DDIFF_B_LABEL="b1"',
                                 "-o", f"{d}/t", DRIVER, f"{d}/pa.c", f"{d}/pb.c"],
                                capture_output=True, timeout=600)
            if cc.returncode:
                bad += 1
                print(f"FAIL {pop} {cfg} {key[:60]!r}: driver did not build: {cc.stderr[:200]!r}")
                continue
            subj = "\n".join(subjects(pat, own.get(pat, ()))) + "\n"
            run = subprocess.run([f"{d}/t"], input=subj.encode("latin-1", "surrogateescape"),
                                 capture_output=True, timeout=600)
            m = re.search(rb"cells (\d+)", run.stdout)
            cells += int(m.group(1)) if m else 0
            if run.returncode == 0:
                ok += 1
            else:
                bad += 1
                print(f"FAIL {pop} {cfg} {key[:60]!r}: {run.stderr[:300]!r}")
    print(f"movers {len(movers)}: identical {ok}, diverged {bad}, skipped {skipped}; "
          f"cells compared {cells}")
    if not movers or ok == 0:
        print("FAIL: empty population")
        sys.exit(1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
