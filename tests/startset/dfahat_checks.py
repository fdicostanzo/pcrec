#!/usr/bin/env python3
"""tests/startset/dfahat_checks.py -- [START-SET] stage 3, THE DFA HAT's checks
(D148 + addenda 1-2; docs/design/startset.md §2 F, §4.1, §4.3, §6.2, §6.4).

Population: every corpus block with its own options (startset_lib.
corpus_blocks, the stage-1/2 checks' and the census's population), compiled
twice -- the default build and `-fno-start-set` (the DENY arm, today's
emitter) -- to the SAME `-o` basename in two directories so the `#include`
line cannot differ. A MOVER is an artifact whose `RX_DFA_PREFILTER` names a
DFA-hat row (`first-memchr-bounded`, `first-class-bounded`).

[dfa-iff] THE STAMP NAMES THE SKIP THAT WAS EMITTED, read off the TEXT:
    `first-class-bounded` iff one `rx_start_bytes` table and one skip over it;
    `first-memchr-bounded` iff no such table and one `memchr` skip; either iff
    exactly one CONDITIONAL re-seed `if (scan_position > skip_from)
    forward_state = ...seed_state[...]` and one `skip_from` declaration; a
    non-mover carries none of the three.
[dfa-route] every mover is the UNANCHORED forward scan (`RX_DFA_SCAN
    "unanchored"`) of a SEEDED machine (a `rx_forward_seed_state` table):
    sabotage S490's structural detector (no attempt-scan artifact carries a
    DFA-hat value) and S487's guard.
[dfa-reseed] THE RE-SEED IS CONDITIONAL (startset.md §6.4.3 item 1, S485's
    structural detector): the hat's skip block writes `forward_state` only
    under `if (scan_position > skip_from)`, never through the unconditional
    `scan_position ? ...seed... : s0` form the offset rows use.
[dfa-table] T AS EMITTED: the scanned set (the `rx_start_bytes` table, or
    the `memchr` byte) EQUALS the `start_set` fact of the same compile
    (`--emit-facts`; T = S) AND is a PROPER subset of the deny arm's
    `rx_can_begin_match` (E, the plain skip's own table). `S` IS the
    predicate's input, so the first half checks EMISSION (the table written is
    the set chosen; sabotage S486), not an independent derivation of `T`; the
    second half reads the deny arm's own table. Per-member reach of `T` is the
    start-byte oracle's (vmhat_diff.py) and the answer cells' (ss3 D6 panel
    checks-m3).
[dfa-refuse] NO BLOCK REFUSES OR TIMES OUT AT DEFAULT WHILE THE DENY ARM
    COMPILES IT (the ss3 D6 panel's checks-m1: both of this stage's build
    assertions are refusals, and the BLOCKER sound-F1 was exactly this shape;
    compile_fuzz.py is the generated population's twin).
[dfa-deny] THE DENY ARM IS TODAY'S EMITTER: a non-mover's default artifact is
    byte-identical to its deny artifact (a VM-hat mover excepted, counted: its
    identity is vmhat_checks.py's [vm-deny]). A mover's two artifacts are equal
    once the stamp/`rx_info.prefilter` value, the two tables and the skip
    block are normalized. Three cross-row MOVER CLASSES startset.md §4.3
    names may move too, each recognized by its own stamp and COUNTED: G1
    (`RX_REQ_WHY` "emitted" -> "dominated", the pre-check's text gone), the
    hybrid re-seed row (`RX_VM_RESEED`) and the scan edge
    (`RX_DFA_SCAN_EDGE`). A mover in a class is re-compiled on BOTH arms with
    that class's mechanisms denied (`-fno-req-byte -fno-req-run
    -fno-hyb-reseed -fno-scan-edge`), and the pair must then be equal outside
    the hat -- so a class is a named, re-checked exception and never a hole --
    and the re-compiled default must STILL carry the hat (checks-m2: a
    `CLASS_DENY` that turned the selection away from it would compare two
    non-hat builds and pass vacuously).
[dfa-movers] THE MOVER MANIFEST BY ID (checks-F5): the corpus blocks whose
    default artifact stamps a DFA-hat value, against
    `manifests/manifest_s3_dfa.tsv` -- 0 off-diagonal both ways. TWO
    DERIVATIONS: the manifest is the census's (the `--emit-facts` fact and
    `E` read off the deny build's emitted tables, T = S), this is the emitted text.
    The manifest's pcrec-bench rows are outside this tree and counted only.
[dfa-wit] hand-written witnesses: the expected stamp written HERE from the
    pattern and F's conjuncts, never read off the compiler.
[dfa-bot] SENTINEL (ss3 D6 panel sound-F2): a pattern that reads the
    start-of-subject or `\G` bits takes the ATTEMPT scan, so the unanchored
    scan the DFA hat rides never needs `s0` apart from `s1u[UPC_PLAIN]`.

Floors (K35, D110): half the population measured at landing, printed beside
the REACH lines.  Env: PCREC, JOBS.  Prints PASS:/FAIL: and the trailers.
"""
import os, re, subprocess, sys, tempfile, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import startset_lib as L

PCREC = os.environ.get("PCREC", os.path.join(TREE, "build", "pcrec"))
JOBS = int(os.environ.get("JOBS", "6"))
TMO = 120
# K35 floors: HALF the landing population (D110), measured at landing (lane
# ssbuild3; docs/dev/lanes/ssbuild3_report.md).
FLOOR_BLOCKS = 1700          # blocks compiled on both arms
FLOOR_MOVERS = 35            # corpus movers (71 at landing)

HAT = ("first-memchr-bounded", "first-class-bounded")
# The three cross-row mechanisms a DFA-hat mover may move (startset.md §4.3):
# G1's pre-check admission, the hybrid re-seed row, the scan edge.
CLASS_DENY = ["-fno-req-byte", "-fno-req-run", "-fno-hyb-reseed", "-fno-scan-edge"]
STAMP = re.compile(r'^#define RX_(\w+) +(.*)$', re.M)
TABLE = "static const unsigned char rx_start_bytes[256] = {"
FIND_SET = "!rx_start_bytes[subject[scan_position]]"
FIND_MEMCHR = re.compile(r'^ *size_t skip_from = scan_position;\n *const void \*q = memchr\(subject \+ scan_position, (\d+), ', re.M)
DECL = "size_t skip_from = scan_position;"
RESEED = re.compile(r'^ *if \(scan_position > skip_from\) forward_state = rx_forward_seed_state\[rx_forward_byte_class\[subject\[scan_position - 1\]\]\];$', re.M)
# The prefilter block: `if (forward_state == N && last_accept_position == (size_t)-1) {`
# through the closing brace at its own indent.
PF_BLOCK = re.compile(r'^( *)if \(forward_state == \d+ && last_accept_position == \(size_t\)-1\) \{\n(?:.*\n)*?\1\}\n', re.M)
U8TABLE = lambda name: re.compile(r'^    static const unsigned char rx_%s\[256\] = \{\n(?:.*\n)*?    \};\n' % name, re.M)

passed = failed = 0


def ok(m):
    global passed
    passed += 1
    print("PASS: " + m)


def bad(m):
    global failed
    failed += 1
    print("FAIL: " + m)


def stamps(text):
    return {m.group(1): m.group(2).strip().strip('"') for m in STAMP.finditer(text)}


def compile_c(pat, args, d):
    os.makedirs(d, exist_ok=True)
    o = os.path.join(d, "rx.c")
    try:
        r = subprocess.run([PCREC, *args, "-p", "rx", "-o", o, "--pattern", pat],
                           capture_output=True, timeout=TMO)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode:
        return None
    return open(o, encoding="latin-1").read()


def table(text, name):
    m = U8TABLE(name).search(text)
    if not m:
        return None
    v = [int(x) for x in re.findall(r"\d+", m.group(0).split("=", 1)[1])]
    return {b for b in range(256) if v[b]} if len(v) == 256 else None


def scanned(text):
    """The DFA hat's scanned set off the emitted text, or None."""
    t = table(text, "start_bytes")
    if t is not None:
        return t
    m = FIND_MEMCHR.search(text)
    return {int(m.group(1))} if m else None


def normalize(text):
    t = re.sub(r'(#define RX_DFA_PREFILTER +)"[^"]*"', r'\1"*"', text)
    t = re.sub(r'(\.prefilter = )"[^"]*"', r'\1"*"', t)
    t = U8TABLE("start_bytes").sub("", t)
    t = U8TABLE("can_begin_match").sub("", t)
    return PF_BLOCK.sub("", t)


def classify(t1, t0, s1, s0):
    """The cross-row mover classes a hat artifact differs from its deny by."""
    cls = []
    if s1.get("REQ_WHY") != s0.get("REQ_WHY"):
        cls.append("G1:%s->%s" % (s0.get("REQ_WHY"), s1.get("REQ_WHY")))
    if s1.get("VM_RESEED") != s0.get("VM_RESEED"):
        cls.append("reseed-row:%s->%s" % (s0.get("VM_RESEED"), s1.get("VM_RESEED")))
    if s1.get("DFA_SCAN_EDGE") != s0.get("DFA_SCAN_EDGE"):
        cls.append("scan-edge:%s->%s" % (s0.get("DFA_SCAN_EDGE"), s1.get("DFA_SCAN_EDGE")))
    return cls


def one(job):
    b, td = job
    base = os.path.join(td, "%x" % (abs(hash((b["id"], tuple(b["args"])))) & 0xffffffffffff))
    t1 = compile_c(b["pattern"], b["args"], base + "_hat")
    t0 = compile_c(b["pattern"], ["-fno-start-set", *b["args"]], base + "_deny")
    if t1 is None:
        return {"status": "hat-refused" if t0 is not None else "refused"}
    s1, s0 = stamps(t1), stamps(t0 or "")
    pf = s1.get("DFA_PREFILTER")
    rec = {"status": "ok", "st": s1, "st0": s0, "deny_ok": t0 is not None, "mover": pf in HAT,
           "ntable": t1.count(TABLE), "nfind_set": t1.count(FIND_SET),
           "nfind_memchr": len(FIND_MEMCHR.findall(t1)), "ndecl": t1.count(DECL),
           "nreseed": len(RESEED.findall(t1)), "seeded": "rx_forward_seed_state" in t1,
           "deny_hat_text": t0 is not None and (TABLE in t0 or DECL in t0)}
    if t0 is not None:
        if not rec["mover"]:
            rec["deny_same"], rec["classes"] = t1 == t0, []
        else:
            rec["classes"] = classify(t1, t0, s1, s0)
            rec["deny_same"] = normalize(t1) == normalize(t0)
            if rec["classes"]:
                # The cross-row classes DENIED ON BOTH ARMS: what is left must
                # be the hat alone, so the class is a named exception and not
                # a hole in the comparison.
                x1 = compile_c(b["pattern"], [*CLASS_DENY, *b["args"]], base + "_hatx")
                x0 = compile_c(b["pattern"], ["-fno-start-set", *CLASS_DENY, *b["args"]], base + "_denyx")
                rec["classx_hat"] = x1 is not None and stamps(x1).get("DFA_PREFILTER") in HAT
                rec["deny_same"] = (rec["classx_hat"] and x0 is not None
                                    and normalize(x1) == normalize(x0))
            rec["T"] = scanned(t1)
            rec["E"] = table(t0, "can_begin_match")
            blk = PF_BLOCK.search(t1)
            rec["uncond"] = bool(blk) and ("scan_position ? rx_forward_seed_state" in blk.group(0))
            try:
                f = subprocess.run([PCREC, *b["args"], "--emit-facts", "--pattern", b["pattern"]],
                                   capture_output=True, timeout=TMO)
                fct, _ = L.facts(f.stdout.decode("utf-8", "replace"))
                rec["S"] = L.set_of(fct["start_set"]["value"])[1]
            except Exception:
                rec["S"] = None
    for d in (base + "_hat", base + "_deny", base + "_hatx", base + "_denyx"):
        for fn in ("rx.c", "rx.h"):
            try:
                os.remove(os.path.join(d, fn))
            except OSError:
                pass
    return rec


def manifest(name):
    rows, nbench = set(), 0
    for ln in open(os.path.join(HERE, "manifests", name), encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        i, o, _h = ln.rstrip("\n").split("\t")
        if i.startswith("bench/"):
            nbench += 1
            continue
        rows.add((i, o))
    return rows, nbench


def corpus_checks():
    blocks, cnt = L.corpus_blocks(PCREC, TREE)
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        with cf.ThreadPoolExecutor(JOBS) as ex:
            res = list(ex.map(one, [(b, td) for b in blocks]))
    compiled = sum(1 for r in res if r["status"] == "ok" and r["deny_ok"])
    print("REACH: %d blocks (%d .rxt files, %d rows), %d compile on both arms (floor %d)"
          % (len(blocks), cnt["files"], cnt["rows"], compiled, FLOOR_BLOCKS))
    if compiled < FLOOR_BLOCKS:
        bad("[dfa-reach] %d blocks compile on both arms, below the floor %d" % (compiled, FLOOR_BLOCKS))
    viol = {k: [] for k in ("iff", "route", "reseed", "table", "deny", "refuse")}
    movers, classes, vmhat = set(), {}, 0
    for b, r in zip(blocks, res):
        if r["status"] == "hat-refused":
            viol["refuse"].append("%s [%s]: the default build refuses or times out, -fno-start-set compiles"
                                  % (b["id"], " ".join(b["args"])))
        if r["status"] != "ok":
            continue
        st, key = r["st"], "%s [%s]" % (b["id"], " ".join(b["args"]))
        pf = st.get("DFA_PREFILTER")
        if r["mover"]:
            movers.add((b["id"], " ".join(b["args"])))
            want_tbl = 1 if pf == "first-class-bounded" else 0
            if not (r["ntable"] == want_tbl and r["nfind_set"] == want_tbl
                    and r["nfind_memchr"] == 1 - want_tbl and r["ndecl"] == 1 and r["nreseed"] == 1):
                viol["iff"].append("%s: %s, %d table(s), %d set skip(s), %d memchr skip(s), %d decl(s), %d re-seed(s)"
                                   % (key, pf, r["ntable"], r["nfind_set"], r["nfind_memchr"], r["ndecl"], r["nreseed"]))
            if st.get("DFA_SCAN") != "unanchored" or not r["seeded"]:
                viol["route"].append("%s: DFA_SCAN %s, seeded %s" % (key, st.get("DFA_SCAN"), r["seeded"]))
            if r.get("uncond") or r["nreseed"] != 1:
                viol["reseed"].append("%s: unconditional=%s conditional=%d" % (key, r.get("uncond"), r["nreseed"]))
            T, S, E = r.get("T"), r.get("S"), r.get("E")
            if T is None or S is None or E is None or T != S or not (T < E):
                viol["table"].append("%s: |T| %s |S| %s |E| %s T==S %s T<E %s" % (
                    key, None if T is None else len(T), None if S is None else len(S),
                    None if E is None else len(E), T == S, T is not None and E is not None and T < E))
            for c in r.get("classes", []):
                classes[c.split(":")[0]] = classes.get(c.split(":")[0], 0) + 1
        elif r["ntable"] or r["nfind_set"] or r["ndecl"] or r["nreseed"]:
            viol["iff"].append("%s: %s, but %d table(s) %d decl(s) %d re-seed(s)"
                               % (key, pf, r["ntable"], r["ndecl"], r["nreseed"]))
        if not r["deny_ok"] or r["st0"].get("DFA_PREFILTER") in HAT or r["deny_hat_text"]:
            viol["deny"].append("%s: deny compiled=%s stamp=%s hat-text=%s"
                                % (key, r["deny_ok"], r["st0"].get("DFA_PREFILTER"), r["deny_hat_text"]))
        elif not r["mover"] and st.get("VM_START_SCAN", "none") != "none":
            vmhat += 1        # a VM-hat mover: its deny identity is vmhat_checks.py's [vm-deny]
        elif not r["deny_same"]:
            viol["deny"].append("%s: %s, differs from the deny arm outside the hat%s"
                                % (key, "mover" if r["mover"] else "non-mover",
                                   " (classes %s, re-compared with %s on both arms; hat still selected: %s)"
                                   % (r["classes"], " ".join(CLASS_DENY), r.get("classx_hat"))
                                   if r.get("classes") else ""))
    names = {"iff": "[dfa-iff] the stamp names the emitted skip and re-seed",
             "route": "[dfa-route] every mover is the unanchored scan of a seeded machine",
             "reseed": "[dfa-reseed] every mover's re-seed is conditional on the skip having moved",
             "table": "[dfa-table] every mover scans T == its start_set fact, a proper subset of the deny arm's E",
             "deny": "[dfa-deny] the deny arm is today's emitter (non-movers identical; movers identical outside the hat, a mover in a named class re-compared with the class denied on both arms, the hat still selected)",
             "refuse": "[dfa-refuse] no block refuses or times out at default while -fno-start-set compiles it"}
    for k, label in names.items():
        if viol[k]:
            bad("%s: %d violation(s)" % (label, len(viol[k])))
            for v in viol[k][:8]:
                print("    " + v)
        else:
            ok("%s (%s)" % (label, "%d movers" % len(movers) if k not in ("deny", "refuse")
                            else "%d artifact pairs" % sum(1 for r in res if r["status"] == "ok")))
    print("REACH: movers %d (floor %d); cross-row mover classes (startset.md §4.3): %s; VM-hat movers left to vmhat_checks.py: %d"
          % (len(movers), FLOOR_MOVERS, ", ".join("%s %d" % kv for kv in sorted(classes.items())) or "none", vmhat))
    want, nbench = manifest("manifest_s3_dfa.tsv")
    extra, missing = sorted(movers - want), sorted(want - movers)
    if len(movers) < FLOOR_MOVERS:
        bad("[dfa-movers] %d movers, below the floor %d" % (len(movers), FLOOR_MOVERS))
    if extra or missing:
        bad("[dfa-movers] movers vs manifest_s3_dfa.tsv: %d not in the manifest, %d manifest rows not movers"
            % (len(extra), len(missing)))
        for e in extra[:6]:
            print("    MOVER-NOT-IN-MANIFEST %s [%s]" % e)
        for e in missing[:6]:
            print("    MANIFEST-NOT-MOVER %s [%s]" % e)
    else:
        ok("[dfa-movers] movers == manifest_s3_dfa.tsv by ID (%d rows, 0 off-diagonal; %d pcrec-bench rows outside the tree, not checked here)"
           % (len(movers), nbench))


# (pattern, options, expected RX_DFA_PREFILTER, why) -- written from F's conjuncts.
FA = ["--features", "all"]
WITNESSES = [
    (b"\\b(?:true|false|null)\\b", FA, "first-class-bounded", "E = the 63 word bytes, S = {t, f, n}"),
    (b"\\B(?<!a)d", FA, "first-memchr-bounded", "S = {d}: the one-byte twin"),
    (b"(?:\\b|xy)a", FA, "first-class-bounded", "S = {a, x}; the conditional re-seed's witness (§6.4.3 item 1)"),
    (b"\\b((?:A3T[A-Z0-9]|AKIA|AGPA)[A-Z0-9]{16})\\b", FA, "first-memchr-bounded", "a VM hybrid's inlined scan takes the DFA hat (aws, S = {A})"),
    (b"\\B(a|b){1,3}", FA + ["-fprefilter-collapse"], "first-class-bounded", "a COUNT-COLLAPSED hybrid prefilter (sound-F5(d)'s witness)"),
    (b"(?:(?<=a)z|w)", FA, "byte-class-bounded", "S = {z, w} is not a subset of E = {a, w}: T would not narrow E (sound-F1's witness)"),
    (b"(?<=\\w) *a", FA, "byte-class-bounded", "S = {' ', a}: the space keeps every seed, so it is outside E and T = S does not narrow E (the ss3 panel's BLOCKER: the old T == S assertion refused this)"),
    (b"(?<=[ab])\\W*?b", FA, "byte-class-bounded", "S holds every non-word byte, none of them in E (the BLOCKER's 193-byte witness)"),
    (b"(?<=\\w) *(a)", FA, "byte-class-bounded", "the BLOCKER's VM-hybrid witness: the prefilter declines the same way"),
    (b"\\bab\\b", FA, "offset-set-bounded", "the offset rows sit above the DFA hat"),
    (b"a+|b+", FA, "byte-class", "UNSEEDED: E is already S"),
    (b"(?m)^(?:ab|\\bcd)", FA, "memchr", "the ATTEMPT scan keeps attempt_cand's own skip (S490's conjunct)"),
    (b"\\b(?:x*|ab)", FA, "none", "NULLABLE: the start state accepts, no skip at all"),
    (b"\\b(?:true|false|null)\\b", FA + ["-fno-start-set"], "byte-class-bounded", "DENIED"),
]


def witness_checks():
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        for i, (pat, args, want, why) in enumerate(WITNESSES):
            t = compile_c(pat, args, os.path.join(td, "w%d" % i))
            got = None if t is None else stamps(t).get("DFA_PREFILTER")
            if got == want:
                ok("[dfa-wit] %r %s -> %s (%s)" % (pat.decode("latin-1"), " ".join(args), want, why))
            else:
                bad("[dfa-wit] %r %s -> %s, expected %s (%s)" % (pat.decode("latin-1"), " ".join(args), got, want, why))
        # The hybrid re-seed row reads the DENSITY of the set the scan tests
        # (`pcrec_dfa_cand_ppm`, startset.md §4.3's [OPT-HYB-RESEED] mover
        # class): over T = {z, w}, two letters, it is below the dense row; over
        # the deny arm's E (the word bytes) it is the dense row. A reader that
        # priced the hat by its row NAME (S495, K84) reads 1,000,000 ppm.
        r = [compile_c(b"(?<=ab)z|\\bw", FA + x, os.path.join(td, "rs%d" % i))
             for i, x in enumerate(([], ["-fno-start-set"]))]
        got = tuple(None if t is None else stamps(t).get("VM_RESEED") for t in r)
        if got == ("adaptive", "adaptive-dense"):
            ok("[dfa-wit] (?<=ab)z|\\bw: RX_VM_RESEED adaptive over T, adaptive-dense under the deny arm's E")
        else:
            bad("[dfa-wit] (?<=ab)z|\\bw: RX_VM_RESEED (hat, deny) = %s, expected (adaptive, adaptive-dense)" % (got,))
        # SENTINEL (the ss3 D6 panel's sound-F2): `s0` and `s1u[UPC_PLAIN]`
        # differ only by the start-of-subject and `\G` bits, and the hat's
        # argument (and the build's `dfa_reseed_exact`, which reads both)
        # treats them as one plain context. That holds because a pattern
        # that reads those bits takes the ATTEMPT scan, never the unanchored
        # one the DFA hat rides; no assertion says so, this does.
        for i, pat in enumerate((b"^a|\\bb", b"\\Ab|\\bc", b"\\Ga|\\bb", b"(?m)^a|\\bb",
                                 b"(?:^|-)\\b(?:a|b)", b"(?:\\A|\\bq)(?:a|b)")):
            t = compile_c(pat, FA, os.path.join(td, "bot%d" % i))
            got = None if t is None else stamps(t).get("DFA_SCAN")
            if got == "attempt":
                ok("[dfa-bot] %r -> RX_DFA_SCAN attempt (a start-of-subject or \\G read keeps the unanchored scan, and the DFA hat, away)" % pat.decode())
            else:
                bad("[dfa-bot] %r -> RX_DFA_SCAN %s, expected attempt: the unanchored scan now admits a start-of-subject read, so s0 is no longer s1u[UPC_PLAIN] there (sound-F2)" % (pat.decode(), got))
        t = compile_c(b"\\b(?:true|false|null)\\b", FA, os.path.join(td, "t"))
        tb = None if t is None else table(t, "start_bytes")
        if tb == {ord("t"), ord("f"), ord("n")}:
            ok("[dfa-wit] \\b(?:true|false|null)\\b: the table is {t, f, n}")
        else:
            bad("[dfa-wit] \\b(?:true|false|null)\\b: the table is %s, expected {t, f, n}"
                % (None if tb is None else sorted(chr(x) for x in tb)))


corpus_checks()
witness_checks()
print("checks passed: %d" % passed)
print("checks failed: %d" % failed)
sys.exit(1 if failed else 0)
