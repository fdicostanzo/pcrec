#!/usr/bin/env python3
"""tests/compound/check_split_diff.py -- [COMPOUND] B4's G2: the split
compound against the lever and libpcre2, on the SHIPPED configuration
(docs/design/compound.md §E.2, §E.3 G2; the twin's twin2.py promoted).

  check_split_diff.py PCREC PCREC_HARNESS CASES WORKDIR [--jobs N]

CASES is `id<TAB>enc<TAB>pattern-hex<TAB>engine` per line
(tests/compound/split_cases.tsv: the twin's case list, the panel witnesses
and the owed CMP-13 row). Each case runs under its encoding's option arms --
`byte`; `utf8` with each startpos guard (refuse, none, align) x `-futf-check`
off and on, the six arms the twin measured -- compiled twice by ONE source
tree: the default build (`ca`, a compound wherever a row admits) and the
harness build under `--harness=no-compound` (`pl`, today's plain artifact,
the lever), both `--features all`. `split_diff.c` links the two with
libpcre2-8 and compares, at every startpos of every subject (the twin's
generator: the pattern's own literals, its non-ASCII bytes and witness
bytes, the panel's subjects verbatim):
  - search, match-here and match-here-with-captures, compound vs lever,
    exactly (codes, refusals and every caps slot);
  - the lever's whole-match span against libpcre2;
  - the find-all loop.
G4 rides along on every admitted case-arm: the compound and the plain
artifact at `-p rx` have the same `.h`, byte for byte, and the same exported
symbol set, no part symbol global. Both builds must agree on compiling at all. Per admitted case-arm the
generated subjects must produce at least one match (chk M3), and the
admitted population must reach its floor (K35): a compiler that stopped
admitting would otherwise pass on nothing. Exit 1 on any difference.
"""
import concurrent.futures as cf, itertools, os, random, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc")
ADMIT_FLOOR = 85          # case-arms the split row admits (measured 91 at B4)

# the panel's own witness subjects, verbatim (sem MF1-MF4/S1, arch M5)
SEEDS = {
    rb"\A\s+|\s+\z": [b"\xff\x20", b"\x20\xff\x20"],
    rb"a{0,4}\A": [b"\xc3\xa9\xff", b"aa"],
    rb"^x|a(?R)?b": [b"aabb", b"xaabb"],
    rb"(?>\Ga|ab)c": [b"\xc3\xa9\x61\x62\x63", b"abc"],
    rb"(?:^(a)|b)(?1)": [b"xba", b"aa"],
    rb"^(?<=\x{e9})a|b": [b"\xc3\xa9a", b"\xc3\xa9b", b"b"],
    rb"^\s*\{|\}\s*$": [b"{  }", b"{ }\n", b" { } "],
}
ARMS = {
    "byte": [("byte", [], 0)],
    "utf8": [("%s%s" % (g, "-uc" if uc else ""), ["-e", "utf8"] + gf +
              (["-futf-check"] if uc else []), 1)
             for g, gf in (("refuse", []), ("none", ["-fno-startpos-guard"]),
                           ("align", ["-fstartpos-guard=align"]))
             for uc in (0, 1)],
}


def witness_bytes(p, utf):
    req = [bytes([c]) for c in sorted(set(b for b in p if b >= 0x80))]
    for m in re.finditer(rb"\\x\{([0-9a-fA-F]+)\}", p):
        cp = int(m.group(1), 16)
        if cp >= 0x80:
            req.append(chr(cp).encode("utf-8") if utf and cp < 0x110000 else bytes([cp & 0xff]))
    if utf:
        req += [b"\xc3\xa9", b"\x80", b"\xc3", b"\xff"]
    out = []
    for r in req:
        if r not in out:
            out.append(r)
    return out[:5]


def subjects(p, utf):
    """The twin's generator (docs/design/compound/twin/twin2.py `subjects`)."""
    req = witness_bytes(p, utf)
    esc = re.findall(rb"\\([^A-Za-z0-9])", p)
    bare = re.sub(rb"\\x\{[^}]*\}|\\[pPgkN]\{[^}]*\}|\\.|\(\?(?:[a-zA-Z^-]*[:)]|[=!>|]|<[=!]|"
                  rb"P?<\w+>|'\w+')|\(\*[^)]*\)|\{\d*,?\d*\}", b"", p)
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,;:'\"/#-=@&%!~`<>_"
    lits = list(dict.fromkeys([e for e in esc if 32 < e[0] < 127] +
                              [bytes([c]) for c in bare if 32 < c < 127 and chr(c) in keep]))[:4]
    alpha = []
    for a in list(req) + lits + [b" ", b"\n"] + ([b"\t"] if b"\\s" in p else []):
        if a not in alpha:
            alpha.append(a)
    alpha = alpha[:10]
    out = [b""]
    for L in range(1, 4):
        out += [b"".join(t) for t in itertools.product(alpha, repeat=L)]
    rnd = random.Random(1)
    for _ in range(600):
        out.append(b"".join(rnd.choice(alpha) for _ in range(rnd.randint(4, 24))))
    out += SEEDS.get(p, [])
    words = list(dict.fromkeys(re.findall(rb"[A-Za-z_]{3,}", re.sub(rb"\\[a-zA-Z]", b" ", p))))[:24]
    seps = [b" ", b"(", b";", b"\n", b"x", b"", b"'", b"/"]
    for _ in range(300 if words else 0):
        k = rnd.randint(1, 4)
        out.append(b"".join(rnd.choice(seps) + rnd.choice(words) for _ in range(k)) + rnd.choice(seps))
    return b"".join(s.hex().encode() + b"\n" for s in out)


def stamp(path):
    m = re.search(rb'#define CA_COMPOUND "([^"]*)"', open(path, "rb").read())
    return m.group(1).decode() if m else "MISSING"


def export_identity(pcrec, harness, d, pat, common):
    """G4 (compound.md §E.3): the compound at `-p rx` against the lever's
    plain artifact at `-p rx`, each in its own directory: the `.h` byte for
    byte, and the object's exported symbol set (`nm -g`, taken from the PLAIN
    artifact, never from the closure the compiler computed), no part symbol
    global. None, or what differs."""
    sets = []
    for tag, cmd in (("c", [pcrec]), ("p", [harness, "--harness=no-compound"])):
        dd = os.path.join(d, "g4" + tag)
        os.makedirs(dd, exist_ok=True)
        r = subprocess.run(cmd + ["-p", "rx", "-o", os.path.join(dd, "rx.c")] + common +
                           ["--pattern", pat], capture_output=True, timeout=600)
        if r.returncode:
            return "the -p rx compile refused"
        o = os.path.join(dd, "rx.o")
        b = subprocess.run([CC, "-O1", "-std=gnu11", "-c", "-I", dd, "-o", o,
                            os.path.join(dd, "rx.c")], capture_output=True, timeout=600)
        if b.returncode:
            return "the -p rx object did not build"
        nm = subprocess.run(["nm", "-g", "--defined-only", o], capture_output=True, timeout=60)
        sets.append((open(os.path.join(dd, "rx.h"), "rb").read(),
                     sorted(l.split()[-1] for l in nm.stdout.decode().splitlines() if l.strip())))
    if sets[0][0] != sets[1][0]:
        return "the compound's .h differs from the plain artifact's"
    if sets[0][1] != sets[1][1]:
        return "exported symbols %s vs plain %s" % (sets[0][1], sets[1][1])
    if any("__" in x for x in sets[0][1]):
        return "a part symbol is global"
    return None


def run_case(job):
    pcrec, harness, wd, cid, pat, arm, args, utf = job
    d = os.path.join(wd, re.sub(r"[^A-Za-z0-9]", "_", cid)[-60:] + "_" + arm)
    os.makedirs(d, exist_ok=True)
    common = ["--features", "all"] + args
    ra = subprocess.run([pcrec, "-p", "ca", "-o", os.path.join(d, "ca.c")] + common +
                        ["--pattern", pat], capture_output=True, timeout=600)
    rb = subprocess.run([harness, "--harness=no-compound", "-p", "pl", "-o",
                         os.path.join(d, "pl.c")] + common + ["--pattern", pat],
                        capture_output=True, timeout=600)
    if ra.returncode and rb.returncode:
        shutil.rmtree(d)
        return cid, arm, "refused", None
    if bool(ra.returncode) != bool(rb.returncode):
        return cid, arm, "FAIL", "the default and lever builds disagree on compiling"
    st = stamp(os.path.join(d, "ca.c"))
    exe = os.path.join(d, "t")
    b = subprocess.run([CC, "-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-DUTF=%d" % utf,
                        "-I", d, "-o", exe, os.path.join(HERE, "split_diff.c"),
                        os.path.join(d, "ca.c"), os.path.join(d, "pl.c")] +
                       os.environ.get("PCRE2_CFLAGS", "").split() +
                       (os.environ.get("PCRE2_LIBS") or "-lpcre2-8").split(),
                       capture_output=True, timeout=600)
    if b.returncode:
        return cid, arm, "FAIL", "build: " + b.stderr.decode()[:400]
    o = subprocess.run([exe, pat.hex()], input=subjects(pat, utf), capture_output=True, timeout=900)
    g4 = export_identity(pcrec, harness, d, pat, common) if st != "none" else None
    shutil.rmtree(d)
    if g4:
        return cid, arm, "FAIL", "G4: " + g4
    line = o.stdout.decode().strip()
    kv = dict(x.split("=", 1) for x in line.split(" FIRST:")[0].split())
    bad = sum(int(kv[k]) for k in ("d_search", "d_match", "d_oracle", "d_findall"))
    if o.returncode or bad:
        return cid, arm, "FAIL", "%s: %s" % (st, line[:500])
    return cid, arm, st, (int(kv["cells"]), int(kv["matches"]))


def main():
    pcrec, harness, cases, wd = sys.argv[1:5]
    jobs_n = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    jobs = []
    for ln in open(cases, encoding="ascii"):
        f = ln.rstrip("\n").split("\t")
        if len(f) < 3 or ln.startswith("#"):
            continue
        cid, enc, pat = f[0], f[1], bytes.fromhex(f[2])
        for arm, args, utf in ARMS[enc]:
            jobs.append((pcrec, harness, wd, cid, pat, arm, args, utf))
    fails, cells, matches, admitted, nomatch_admitted, refused = [], 0, 0, 0, [], 0
    with cf.ThreadPoolExecutor(jobs_n) as ex:
        for cid, arm, st, res in ex.map(run_case, jobs):
            if st == "FAIL":
                fails.append("%s [%s]: %s" % (cid, arm, res))
                continue
            if st == "refused":
                refused += 1
                continue
            cells += res[0]
            matches += res[1]
            if st not in ("none",):
                admitted += 1
                if res[1] == 0:
                    nomatch_admitted.append("%s [%s]" % (cid, arm))
    for f in fails[:30]:
        print("FAIL: " + f)
    for f in nomatch_admitted:
        print("FAIL: admitted case-arm with no matching cell (chk M3): " + f)
    ok = not fails and not nomatch_admitted and admitted >= ADMIT_FLOOR
    if admitted < ADMIT_FLOOR:
        print("FAIL: %d admitted case-arms, below the floor %d (K35)" % (admitted, ADMIT_FLOOR))
    print("%s: G2 split differential: %d case-arms (%d refused by both, %d admitted); "
          "%d cells, %d matches; compound vs lever and lever vs libpcre2; %d failures"
          % ("PASS" if ok else "FAIL", len(jobs), refused, admitted, cells, matches,
             len(fails) + len(nomatch_admitted)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
