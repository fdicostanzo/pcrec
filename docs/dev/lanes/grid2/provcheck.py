#!/usr/bin/env python3
"""grid2 provenance and arm-signature gate (rev 3: r17b_prime.md §5.4, D166 add. 2, R-MS3).

  provcheck.py OUT record    print the COMPILER'S provenance as `compiler_*` lines (build.sh
                             appends them to OUT/provenance.txt, the set header's source);
                             exit 1 if the compiler is stale, dirty or unidentifiable
  provcheck.py OUT check     record + re-emit every cell with the compiler and compare + assert
                             every timed arm's SIGNATURE + the route stamps + the cover shapes;
                             writes OUT/prov.status, prints `PROV-FAIL ...` per failure, exit 1
  provcheck.py OUT census    the MANIFEST census: what the arm tables (what time.sh will time)
                             hold for the rev-3 items against LITERAL expectations written here
                             from the §5.4 table (not derived from design2.py); prints
                             `CENSUS-FAIL ...` per failure, exit 1

WHY. The slot times arms; a wrong arm times fine and answers right (a `walk` built from the V1
text, a VM_ATTEMPT cell silently built as a DFA_HAT, a dropped N point). The legs R/L/C/O cannot
see those, so this gate reads what is being timed:
  - the COMPILER: the exact commit, abi, binary sha256, whether the build inputs are clean and
    older than the binary (a stale or dirty compiler is FAILED, ALLOW_DIRTY_COMPILER=1 records
    and proceeds); EXPECT_ABI / EXPECT_COMMIT fail on a mismatch when set;
  - the ARTIFACTS: every own cell is RE-EMITTED here, from this file's own pattern table and
    flag set (never from build.sh's), at the same `-o` basename, and compared byte for byte to
    art/<cell>/{new,deny}/art.c. That is how ALPHA-copied artifacts (grid1 copies five cells
    from slot25c) are proven to be THIS compiler's text;
  - the ARMS: each bin/<cell>/<arm>/art.c carries its arm's signature (walk: the table walk and
    no V1 text; V1: the V1 text and the cell's cover shape; libc/v1/loop/none/...: see SIG),
    and each ext cell the route stamps of its kind (RX_ENGINE, RX_DFA_SCAN, ...);
  - the MANIFEST: the N = 33..46 staircase, the three cover-shape cells, the VM_ATTEMPT
    groups, NONE's 30 arms.
Design changes are table edits (PATTERNS, SHAPES, ROUTES, SIG, the EXPECT_* literals).
"""
import glob, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
G1 = os.path.normpath(os.path.join(HERE, "..", "grid1"))
OUT = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "check"
PCREC = os.environ.get("PCREC", "/home/pcrec/projects/pcrec/worktrees/memfn-r17/build/pcrec")

# ---- the cells: pattern as the oracle sees it (rev 3 §5.4 / grid1 CELLS), emitted at default flags
# `-p rx`; deny = --memfn=no-pf-terms-mask. SHAPES = (range, eq, cube) calls in the V1 mask
# (r17b_prime/census_shapes.py's key; M3's shapes plus rev 3's item 3a).
# FEATURES: the two cells with \b were emitted with --features all (slot25c ALPHA's), the rest at the default set.
FEATURES = {"bounded": ["--features", "all"], "dfa-hat": ["--features", "all"]}
PATTERNS = {"dig": r"[0-9]+x", "bounded": r"[a-z]+\b", "dfa-hat": r"\b(?:true|false|null)\b",
            "hex-run": r"[a-f0-9]+", "word-eq": r"[A-Za-z_]+=", "quad": r"[0-9A-Fa-f_]+=", "wcls": r"\w+=",
            "c020": r"[ad]+=", "c001": r"[xy]+=", "c110": r"[0-9_]+="}
SHAPES = {"dig": (1, 0, 0), "bounded": (1, 0, 0), "dfa-hat": (0, 1, 1), "hex-run": (2, 0, 0), "word-eq": (2, 0, 1),
          "quad": (3, 1, 0), "wcls": (3, 0, 1), "c020": (0, 2, 0), "c001": (0, 0, 1), "c110": (1, 1, 0)}
# ext cells: pattern, extra flags (all are emitted with --features all -fno-req-byte -fno-req-run), the
# member byte of the FIND, and the ROUTE stamps the artifact must carry. A cell built on the wrong
# route (o-vm without --engine=vm is a DFA hat) answers identically and is caught only here.
EXT_FLAGS = ["--features", "all", "-fno-req-byte", "-fno-req-run"]
ROUTES = {
    "o-fwd":  (r"xy+z",       [],                            120, {"RX_ENGINE": "dfa", "RX_DFA_SCAN": "unanchored", "RX_DFA_PREFILTER": "memchr"}),
    "o-bnd":  (r"xy+(?=z)",   [],                            120, {"RX_ENGINE": "dfa", "RX_DFA_SCAN": "unanchored", "RX_DFA_PREFILTER": "memchr-bounded"}),
    "o-hat":  (r"\bx[a-z]+\b", [],                           120, {"RX_ENGINE": "dfa", "RX_DFA_SCAN": "unanchored", "RX_DFA_PREFILTER": "first-memchr-bounded"}),
    "o-hyb":  (r"xy+z",       ["--engine=vm", "-fprefilter"], 120, {"RX_ENGINE": "vm", "RX_VM_PREFILTER": "hybrid", "RX_DFA_PREFILTER": "memchr"}),
    "o-back": (r"(?m)^xy+z",  [],                             10, {"RX_ENGINE": "dfa", "RX_DFA_SCAN": "attempt", "RX_DFA_PREFILTER": "memchr"}),
    "o-vm":   (r"xy+z",       ["--engine=vm"],               120, {"RX_ENGINE": "vm", "RX_VM_START_SCAN": "first-class", "RX_VM_PREFILTER": "none"}),
}
EXT_ARMS = {"o-back": ["walk", "libc", "none"], "o-vm": ["walk", "libc", "v1"]}
EXT_ARMS_DEFAULT = ["walk", "libc", "loop", "v1", "none"]
# arm signatures: arm -> (substrings that MUST be in art.c, substrings that must NOT be). {b} = the member byte.
SIG_OB = {"libc": ([r"memchr(", ", {b}, "], []),
          "walk": ([r"g2_tab[256]", r"= { [{b}] = 1 }"], [r"memchr(subject"]),
          "loop": ([r"for (size_t i = 0; i < len; i++) if (p[i] == (unsigned char)b)"], []),
          "v1":   ([r"pcrec_mfk_w8_eq(pcrec_mfk_w8_load_vector"], []),
          "none": ([], [r"memchr(subject + scan_position, {b},", r"memchr(subject + start, {b},"])}
SIG_VM = {"walk": ([r"rx_start_set[256]", r"G2_TICK("], [r"PCREC_MFK_W8_H", r"memchr("]),
          "libc": ([r"rx_start_set[256]", r"memchr(subject + attempt_position, {b},"], [r"PCREC_MFK_W8_H"]),
          "v1":   ([r"PCREC_MFK_W8_H", r"__next_candidate("], [r"rx_start_set["])}
TRIG = {"trig-dig": r"[0-9]+x", "trig-word": r"[A-Za-z_]+="}

# ---- the manifest: literal expectations from the §5.4 table
N_EXPECT = {"full": [33, 34, 36, 38, 40, 42, 44, 46], "dry": [36, 46]}
COVER_EXPECT = {"full": [(c, n) for c in ("c020", "c001", "c110") for n in ("64k", "1m")],
                "dry": [(c, "64k") for c in ("c020", "c001", "c110")]}
VM_GAPS = {"full": ["2", "8", "32", "256", "4k", "inf"], "dry": ["8"]}
VM_LENS = {"full": ["8", "32", "64", "1m"], "dry": ["64"]}
NONE_CELLS = {"full": [("o-fwd", "o-bnd", "o-hat", "o-hyb", "o-back"), ["2", "8", "32", "256", "4k", "inf"]],
              "dry": [("o-fwd", "o-hat", "o-back"), ["8"]]}
ITEM3_GROUPS = {"full": 50, "dry": 5}                  # five DFA kinds x (6 gaps + 4 lengths)

fails = []
oks = 0


def fail(*a):
    fails.append(" ".join(str(x) for x in a))


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def toplevel(path):
    r = run(["git", "-C", os.path.dirname(path), "rev-parse", "--show-toplevel"])
    return r.stdout.strip() if r.returncode == 0 else None


def emit(args, outc):
    os.makedirs(os.path.dirname(outc), exist_ok=True)
    r = run([PCREC, "-p", "rx"] + args + ["-o", outc])
    return r.returncode == 0, r.stderr.strip()[:200]


# ================================================================ the compiler record
def record():
    real = os.path.realpath(PCREC)
    lines, bad = [], []
    sha = run(["sha256sum", real]).stdout.split()[0]
    mt = os.stat(real).st_mtime
    lines.append(f"compiler_path={PCREC}")
    lines.append(f"compiler_realpath={real}")
    lines.append(f"compiler_sha256={sha}")
    lines.append(f"compiler_mtime={time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(mt))}")
    ver = run([PCREC, "--version"]).stdout.strip().splitlines()
    lines.append(f"compiler_version={ver[0] if ver else '?'}")
    probe = os.path.join(OUT, "tmp", "prov", "probe", "art.c")
    ok, why = emit(["--pattern", "a"], probe)
    abi = "?"
    if ok:
        m = re.search(r"\(abi (\d+)\)", open(probe).readline())
        abi = m.group(1) if m else "?"
    else:
        bad.append(f"the compiler cannot emit a probe pattern: {why}")
    lines.append(f"compiler_abi={abi}")
    exp = os.environ.get("EXPECT_ABI")
    if exp and exp != abi:
        bad.append(f"abi {abi} != EXPECT_ABI {exp}")
    top = toplevel(real)
    if not top:
        if os.environ.get("ALLOW_UNKNOWN_COMPILER") != "1":
            bad.append("the compiler is not inside a git worktree: its commit is unidentifiable (ALLOW_UNKNOWN_COMPILER=1 to record that and go on)")
        lines.append("compiler_commit=UNKNOWN")
    else:
        head = run(["git", "-C", top, "rev-parse", "HEAD"]).stdout.strip()
        br = run(["git", "-C", top, "branch", "--show-current"]).stdout.strip()
        inputs = ["src", "cli", "lib", "memfn/src", "memfn/include", "Makefile"]
        dirty = [l for l in run(["git", "-C", top, "status", "--porcelain", "--"] + inputs).stdout.splitlines() if l.strip()]
        last = run(["git", "-C", top, "log", "-1", "--format=%H %ct %cI", "--"] + inputs).stdout.split()
        lines.append(f"compiler_worktree={top}")
        lines.append(f"compiler_commit={head}")
        lines.append(f"compiler_branch={br}")
        lines.append(f"compiler_inputs_last_commit={last[0] if last else '?'} {last[2] if len(last) > 2 else '?'}")
        lines.append(f"compiler_inputs_dirty_files={len(dirty)}")
        if dirty:
            if os.environ.get("ALLOW_DIRTY_COMPILER") == "1": lines.append("compiler_dirty_allowed=1")
            else: bad.append(f"the compiler's build inputs are DIRTY ({len(dirty)} files, e.g. {dirty[0].strip()}): its commit does not identify the binary")
        if last and mt < float(last[1]):
            bad.append(f"STALE-COMPILER: the binary ({lines[3]}) is older than the last commit touching its build inputs ({last[2]}); rebuild it")
        exp = os.environ.get("EXPECT_COMMIT")
        if exp and not head.startswith(exp):
            bad.append(f"commit {head} != EXPECT_COMMIT {exp}")
    # capabilities: the deny and every flag the ext cells use must be KNOWN to this compiler
    # (an unknown --memfn= value would be refused; an unknown -f flag too) and the deny must MOVE the text
    ax = run([PCREC, "--list-axes"]).stdout
    if "pf-terms-mask" not in ax:
        bad.append("the compiler does not list the pf-terms-mask deny (--memfn=no-pf-terms-mask): main's compiler cannot build the walk arms")
    a, b = os.path.join(OUT, "tmp", "prov", "cap", "new", "art.c"), os.path.join(OUT, "tmp", "prov", "cap", "deny", "art.c")
    ok1, w1 = emit(["--pattern", PATTERNS["dig"]], a)
    ok2, w2 = emit(["--memfn=no-pf-terms-mask", "--pattern", PATTERNS["dig"]], b)
    if not (ok1 and ok2): bad.append(f"capability probe failed to emit: {w1 or w2}")
    elif open(a).read() == open(b).read(): bad.append("the deny does not move the text: the walk arm would be built as the V1 form")
    lines.append(f"compiler_pf_terms_mask_deny={'moves-text' if ok1 and ok2 and open(a).read() != open(b).read() else 'NO'}")
    for l in bad: print(f"PROV-FAIL compiler: {l}", file=sys.stderr)
    print("\n".join(lines))
    return bad


# ================================================================ the arm signatures
def shape_of(text):
    ms = list(re.finditer(r"static inline unsigned long long (\w+)__mask\(const unsigned char \*p\)\n\{\n    pcrec_mfk_w8_vector v = pcrec_mfk_w8_load_vector\(p\);\n    return (.*);\n\}", text))
    return [(m.group(2).count("_range("), m.group(2).count("_eq("), m.group(2).count("_cube(")) for m in ms]


def read(p):
    try: return open(p).read()
    except OSError: return None


def need(cell, arm, text, musts, nots, byte=None):
    global oks
    sub = lambda s: s.replace("{b}", str(byte)) if byte is not None else s
    for m in musts:
        if sub(m) not in text: fail(f"PROV-FAIL {cell} {arm}: signature text {sub(m)!r} is missing (a wrong arm?)")
    for m in nots:
        if sub(m) in text: fail(f"PROV-FAIL {cell} {arm}: forbidden text {sub(m)!r} is present (a wrong arm?)")
    oks += 1


def stamps_of(text):
    return dict(re.findall(r'^#define (RX_[A-Z_]+) "([^"]*)"', text, re.M))


def check_own():
    bindir = os.path.join(OUT, "bin")
    for cell, pat in PATTERNS.items():
        # re-emission identity: the art/ copies are THIS compiler's text
        for side, extra in (("new", []), ("deny", ["--memfn=no-pf-terms-mask"])):
            fresh = os.path.join(OUT, "tmp", "prov", cell, side, "art.c")
            ok, why = emit(FEATURES.get(cell, []) + extra + ["--pattern", pat], fresh)
            have = read(os.path.join(OUT, "art", cell, side, "art.c"))
            if not ok: fail(f"PROV-FAIL {cell} {side}: the compiler cannot emit {pat!r}: {why}")
            elif have is None: fail(f"PROV-FAIL {cell} {side}: art/{cell}/{side}/art.c is missing")
            elif have != read(fresh): fail(f"PROV-FAIL {cell} {side}: art/{cell}/{side}/art.c is not this compiler's emission of {pat!r} (copied from another build?)")
        walk, v1 = read(f"{bindir}/{cell}/walk/art.c"), read(f"{bindir}/{cell}/V1/art.c")
        if walk is None or v1 is None:
            fail(f"PROV-FAIL {cell}: bin/{cell}/walk or V1 art.c missing"); continue
        newtxt, denytxt = read(f"{OUT}/art/{cell}/new/art.c") or "", read(f"{OUT}/art/{cell}/deny/art.c") or ""
        # walk = the deny text, V1 = the new text, both byte for byte (grid1/build.sh copies them verbatim)
        if walk != denytxt: fail(f"PROV-FAIL {cell} walk: bin/{cell}/walk/art.c is not the deny artifact (the walk arm is built as something else)")
        if v1 != newtxt: fail(f"PROV-FAIL {cell} V1: bin/{cell}/V1/art.c is not the new artifact")
        need(cell, "walk", walk, ["[256]"], ["PCREC_MFK_W8_H", "__next_candidate("])
        need(cell, "V1", v1, ["PCREC_MFK_W8_H", "__next_candidate("], [])
        sh = shape_of(v1)
        if sh != [SHAPES[cell]]: fail(f"PROV-FAIL {cell} V1: cover shape (range,eq,cube) per site {sh}, want [{SHAPES[cell]}]")
        # the instrument arms
        for a in ("tw0", "tw1", "tw2"):
            t = read(f"{bindir}/{cell}/{a}/art.c")
            if t is not None: need(cell, a, t, ["__form(", "__next("], [])
        t = read(f"{bindir}/{cell}/sc0/art.c")
        if t is not None: need(cell, "sc0", t, ["__walk("], ["PCREC_MFK_W8_H"])


def check_ext():
    bindir = os.path.join(OUT, "bin")
    for cell, (pat, extra, byte, route) in ROUTES.items():
        arms = EXT_ARMS.get(cell, EXT_ARMS_DEFAULT)
        if not os.path.isdir(f"{bindir}/{cell}"):
            fail(f"PROV-FAIL {cell}: no bin/{cell}"); continue
        # the cell's route, from a fresh emission with THIS file's flags
        fresh = os.path.join(OUT, "tmp", "prov", cell, "new", "art.c")
        ok, why = emit(EXT_FLAGS + extra + ["--pattern", pat], fresh)
        if not ok: fail(f"PROV-FAIL {cell}: the compiler cannot emit {pat!r} {extra}: {why}"); continue
        st = stamps_of(read(fresh))
        for k, v in route.items():
            if st.get(k) != v: fail(f"PROV-FAIL {cell}: the compiler's own emission has {k}={st.get(k)!r}, the cell's kind wants {v!r}")
        for a in arms:
            t = read(f"{bindir}/{cell}/{a}/art.c")
            if t is None: fail(f"PROV-FAIL {cell} {a}: bin/{cell}/{a}/art.c missing"); continue
            ast = stamps_of(t)
            for k, v in list(route.items()) + [("RX_REQ_BYTE", "none"), ("RX_REQ_RUN", "none")]:
                if ast.get(k) != v: fail(f"PROV-FAIL {cell} {a}: ROUTE {k}={ast.get(k)!r}, want {v!r} (the arm is not on the {cell} route)")
            if cell == "o-vm": musts, nots = SIG_VM[a]
            else:
                musts, nots = SIG_OB[a]
                if a == "libc" and cell == "o-back": musts = [r"memchr(", ", 10, "]
            need(cell, a, t, musts, nots, byte)
        if cell == "o-vm":
            v, w = read(f"{bindir}/o-vm/v1/art.c"), read(f"{bindir}/o-vm/walk/art.c")
            if v == read(f"{OUT}/art/o-vm/art.c") and shape_of(v) != [(0, 1, 0)]:
                fail(f"PROV-FAIL o-vm v1: one-term shape {shape_of(v)}, want [(0, 1, 0)]")
    for cell, pat in TRIG.items():
        for arm, flags in (("keep", []), ("drop", ["-fno-req-byte", "-fno-req-run"])):
            t = read(f"{bindir}/{cell}/{arm}/art.c")
            if t is None: fail(f"PROV-FAIL {cell} {arm}: missing"); continue
            st = stamps_of(t)
            if arm == "keep" and st.get("RX_REQ_BYTE") in (None, "none"): fail(f"PROV-FAIL {cell} keep: RX_REQ_BYTE={st.get('RX_REQ_BYTE')!r} (the pre-check is not there to keep)")
            if arm == "drop" and (st.get("RX_REQ_BYTE") != "none" or st.get("RX_REQ_RUN") != "none"): fail(f"PROV-FAIL {cell} drop: the pre-check is still emitted")


# ================================================================ the manifest census
def groups():
    r = run([sys.executable, "-I", os.path.join(G1, "arms.py"), OUT, "groups", "timed"])
    out = {}
    for l in r.stdout.splitlines():
        f = l.split("\t")
        if len(f) == 4: out[(f[0], f[1], f[2])] = f[3].split(",")
    return out


def census():
    mode = (read(os.path.join(OUT, "design.mode")) or "full").strip()
    g = groups()
    if not g: fail("CENSUS-FAIL: the arm tables yield no groups"); return
    # 2a
    got = sorted(int(m.group(1)) for (c, s, md) in g if c == "dig" and md == "first" and (m := re.fullmatch(r"g2-dig-n(3[3-9]|4[0-6])-ginf-Lnone-S", s)))
    if got != N_EXPECT[mode]: fail(f"CENSUS-FAIL item 2a: N staircase points {got}, want {N_EXPECT[mode]}")
    for n in N_EXPECT[mode]:
        arms = g.get(("dig", f"g2-dig-n{n}-ginf-Lnone-S", "first"), [])
        if not arms or arms[0] != "walk" or "V1" not in arms: fail(f"CENSUS-FAIL item 2a N={n}: arms {arms}, want walk (base) + V1")
    # 3a
    got = sorted((c[3:], re.fullmatch(r"g2-f3-c\d+-n(\w+)-ginf-Lnone-S", s).group(1)) for (c, s, md) in g if re.fullmatch(r"f3-c(020|001|110)", c) and md == "first" and re.fullmatch(r"g2-f3-c\d+-n\w+-ginf-Lnone-S", s))
    if got != sorted(COVER_EXPECT[mode]): fail(f"CENSUS-FAIL item 3a: cover groups {got}, want {sorted(COVER_EXPECT[mode])}")
    for (c, s, md), arms in g.items():
        if re.fullmatch(r"f3-c(020|001|110)", c) and (not arms or arms[0] != "walk" or "V1" not in arms):
            fail(f"CENSUS-FAIL item 3a {c} {s}: arms {arms}, want walk (base) + V1")
    # 3v
    vm = {(s, md): arms for (c, s, md), arms in g.items() if c == "o-vm"}
    want = {(f"ob_o-vm-n64k-g{gp}-L64k-S", "all") for gp in VM_GAPS[mode]} | {(f"ob_o-vm-n{ln}-ginf-Lnone-S", "first") for ln in VM_LENS[mode]}
    if set(vm) != want: fail(f"CENSUS-FAIL item 3v (VM_ATTEMPT): groups {sorted(vm)}, want {sorted(want)}")
    for k, arms in vm.items():
        if sorted(arms) != ["libc", "v1", "walk"] or arms[0] != "walk": fail(f"CENSUS-FAIL item 3v {k}: arms {arms}, want walk (base), libc, v1")
    # NONE (item 3, rev 3 C8): an extra arm of 5 kinds x 6 gap groups
    cells, gaps = NONE_CELLS[mode]
    want_none = {(c, f"ob_{c}-n64k-g{gp}-L64k-S", "all") for c in cells for gp in gaps}
    got_none = {k for k, arms in g.items() if "none" in arms}
    if got_none != want_none: fail(f"CENSUS-FAIL NONE arms: {len(got_none)} groups, want {len(want_none)}; missing {sorted(want_none - got_none)[:3]} extra {sorted(got_none - want_none)[:3]}")
    n3 = sum(1 for (c, s, md) in g if c in ("o-fwd", "o-bnd", "o-hat", "o-hyb", "o-back"))
    if n3 != ITEM3_GROUPS[mode]: fail(f"CENSUS-FAIL item 3: {n3} groups over the five DFA kinds, want {ITEM3_GROUPS[mode]}")
    print(f"census ({mode}): item 2a {len(N_EXPECT[mode])} N points, item 3a {len(COVER_EXPECT[mode])} groups, item 3v {len(want)} groups, NONE {len(want_none)} groups, item 3 {n3} groups")


def main():
    global fails
    if MODE == "record":
        bad = record(); sys.exit(1 if bad else 0)
    if MODE == "census":
        census()
    elif MODE == "check":
        os.makedirs(os.path.join(OUT, "tmp", "prov"), exist_ok=True)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            bad = record()
        for l in bad: fail(f"PROV-FAIL compiler: {l}")
        open(os.path.join(OUT, "prov.record"), "w").write(buf.getvalue())
        check_own(); check_ext()
        print(f"provcheck: {oks} arm signatures checked, compiler {dict(l.split('=', 1) for l in buf.getvalue().splitlines() if '=' in l).get('compiler_commit', '?')[:12]} abi {dict(l.split('=', 1) for l in buf.getvalue().splitlines() if '=' in l).get('compiler_abi', '?')}")
    else:
        raise SystemExit(__doc__)
    with open(os.path.join(OUT, "prov.status" if MODE == "check" else "census.status"), "w") as f:
        f.write("\n".join(fails) + ("\n" if fails else "") + ("PROV_OK\n" if MODE == "check" and not fails else "CENSUS_OK\n" if not fails else ""))
    for l in fails: print(l)
    sys.exit(1 if fails else 0)


main()
