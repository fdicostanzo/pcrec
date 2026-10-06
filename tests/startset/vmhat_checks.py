#!/usr/bin/env python3
"""tests/startset/vmhat_checks.py -- [START-SET] stage 2, THE VM HAT's checks
(D148; docs/design/startset.md §2 V, §4.2, §4.3, §6.2, §6.4.3).

Population: every corpus block with its own options (startset_lib.
corpus_blocks, the stage-1 checks' and the census's population), on two
ARMS: `auto` (the block's own options) and `vm` (its options with
`--engine=vm` replacing any engine). Each arm is compiled twice, the default
build and `-fno-start-set` (the DENY arm, today's emitter), to the SAME `-o`
basename in two directories so the `#include` line cannot differ.

[vm-iff] THE STAMP NAMES THE SEEK THAT WAS EMITTED: `RX_VM_START_SCAN
    "first-class"` iff the artifact declares the `rx_start_set` table once and
    seeks through it twice (the entry and the retry); `"none"` iff neither.
    Read off the emitted TEXT, not off the selection.
[vm-route] a mover is a VM artifact with no DFA prefilter (`RX_ENGINE "vm"`,
    `RX_VM_PREFILTER "none"`): every DFA artifact and every hybrid reads
    `"none"` (sabotage S493's detector; the hybrid's start test is its
    prefilter, startset.md §2 V).
[vm-anchor] a mover is unanchored (`RX_VM_START "unanchored"`): an anchored
    or `\\G`-start artifact runs one attempt (S492's detector).
[vm-handoff] no mover carries a K82 handoff (`RX_REQ_HANDOFF "none"`):
    §6.4.3 item 7's structural check -- the seek starts at `search_from`
    because no VM-route artifact without a prefilter can hand off.
[vm-deny] THE DENY ARM IS TODAY'S EMITTER: its stamp reads `"none"` and it
    has no table or seek; a non-mover's default artifact is byte-identical to
    its deny artifact (a stage-3 DFA-hat mover excepted: its identity is
    dfahat_checks.py's [dfa-deny]); and a mover's default artifact, with the table, the
    two seeks and the stamp value removed, IS its deny artifact (the hat adds
    exactly the seek and nothing else).
[vm-table] on every mover, the emitted table EQUALS the `start_set` fact of
    the same compile (the `--emit-facts` row): the seek scans exactly the
    fact (sabotage S478's structural detector; the answer cells and the
    differential are its answer-level ones).
[vm-movers] THE MOVER MANIFEST BY ID (checks-F5; the k82hbuild precedent):
    the blocks whose default artifact stamps a non-`"none"` value, per arm,
    against `manifests/manifest_s2_vm_{auto,forced}.tsv` -- 0 off-diagonal
    in both directions. TWO DERIVATIONS: the manifest is the census's (the
    facts and V's predicate, read off `--emit-facts`), this is the emitted
    text. The manifest's pcrec-bench rows are outside this tree and are
    counted, not checked here (the lane report carries their reading).
[vm-wit] hand-written witnesses: the expected stamp written HERE from the
    pattern and V's conjuncts, never read off the compiler.

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
# K35 floors: HALF the landing population (D110). Measured at landing (lane
# ssbuild2): docs/dev/lanes/ssbuild2_report.md §4.
FLOOR_BLOCKS = 1736          # blocks compiled on both arms (3,473 at landing)
FLOOR_MOVERS_AUTO = 88       # corpus movers at auto (176 at landing)
FLOOR_MOVERS_VM = 1280       # corpus movers under --engine=vm (2,560 at landing)

STAMP = re.compile(r'^#define RX_(\w+) (.*)$', re.M)
TABLE = "static const unsigned char rx_start_set[256] = {"
SEEK = "!rx_start_set[subject[attempt_position]]"
SEEK_LINE = re.compile(r'^ *while \(attempt_position < subject_length && '
                       r'!rx_start_set\[subject\[attempt_position\]\]\) attempt_position\+\+;\n'
                       r' *if \(attempt_position >= subject_length\) return 0;\n', re.M)
TABLE_BLOCK = re.compile(r'^    static const unsigned char rx_start_set\[256\] = \{\n(?:.*\n)*?    \};\n', re.M)

passed = failed = 0


def ok(m):
    global passed
    passed += 1
    print("PASS: " + m)


def bad(m):
    global failed
    failed += 1
    print("FAIL: " + m)


def vm_args(args):
    return [a for a in args if not a.startswith("--engine=")] + ["--engine=vm"]


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


def table_of(text):
    m = TABLE_BLOCK.search(text)
    if not m:
        return None
    v = [int(x) for x in re.findall(r"\d+", m.group(0).split("=", 1)[1])]
    return {b for b in range(256) if v[b]} if len(v) == 256 else None


def strip_hat(text):
    t = TABLE_BLOCK.sub("", text)
    t = SEEK_LINE.sub("", t)
    return t.replace('#define RX_VM_START_SCAN "first-class"', '#define RX_VM_START_SCAN "none"')


def one(job):
    b, arm, td = job
    args = b["args"] if arm == "auto" else vm_args(b["args"])
    base = os.path.join(td, "%x_%s" % (abs(hash((b["id"], tuple(b["args"])))) & 0xffffffffffff, arm))
    t1 = compile_c(b["pattern"], args, base + "_hat")
    if t1 is None:
        return {"status": "refused"}
    t0 = compile_c(b["pattern"], ["-fno-start-set", *args], base + "_deny")
    rec = {"status": "ok", "st": stamps(t1), "st0": stamps(t0 or ""), "deny_ok": t0 is not None,
           "ntable": t1.count(TABLE), "nseek": t1.count(SEEK),
           "ntable0": (t0 or "").count(TABLE), "nseek0": (t0 or "").count(SEEK)}
    mover = rec["st"].get("VM_START_SCAN") not in (None, "none")
    rec["mover"] = mover
    rec["deny_same"] = t0 is not None and ((strip_hat(t1) == t0) if mover else (t1 == t0))
    if mover:
        rec["table"] = table_of(t1)
        try:
            f = subprocess.run([PCREC, *args, "--emit-facts", "--pattern", b["pattern"]],
                               capture_output=True, timeout=TMO)
            fct, _ = L.facts(f.stdout.decode("utf-8", "replace"))
            rec["fact"] = L.set_of(fct["start_set"]["value"])[1]
        except Exception:
            rec["fact"] = None
    for d in (base + "_hat", base + "_deny"):
        for fn in ("rx.c", "rx.h"):
            try:
                os.remove(os.path.join(d, fn))
            except OSError:
                pass
    return rec


def manifest(name):
    rows = set()
    nbench = 0
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
    jobs = []
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        for b in blocks:
            for arm in ("auto", "vm"):
                jobs.append((b, arm, td))
        with cf.ThreadPoolExecutor(JOBS) as ex:
            res = list(ex.map(one, jobs))
    by = {}
    for (b, arm, _), r in zip(jobs, res):
        by[(b["id"], " ".join(b["args"]), arm)] = r
    compiled = sum(1 for b in blocks if by[(b["id"], " ".join(b["args"]), "auto")]["status"] == "ok"
                   and by[(b["id"], " ".join(b["args"]), "vm")]["status"] == "ok")
    print("REACH: %d blocks (%d .rxt files, %d rows), %d compile on both arms (floor %d)"
          % (len(blocks), cnt["files"], cnt["rows"], compiled, FLOOR_BLOCKS))
    if compiled < FLOOR_BLOCKS:
        bad("[vm-reach] %d blocks compile on both arms, below the floor %d" % (compiled, FLOOR_BLOCKS))
    viol = {"iff": [], "route": [], "anchor": [], "handoff": [], "deny": [], "table": []}
    movers = {"auto": set(), "vm": set()}
    nmov_tbl = 0
    for (bid, opts, arm), r in by.items():
        if r["status"] != "ok":
            continue
        st, key = r["st"], "%s [%s] %s" % (bid, opts, arm)
        scan = st.get("VM_START_SCAN")
        if scan is None:
            viol["iff"].append(key + ": no RX_VM_START_SCAN stamp")
            continue
        if r["mover"]:
            movers[arm].add((bid, opts))
            if not (scan == "first-class" and r["ntable"] == 1 and r["nseek"] == 2):
                viol["iff"].append("%s: stamp %s, %d table(s), %d seek(s)" % (key, scan, r["ntable"], r["nseek"]))
            if st.get("ENGINE") != "vm" or st.get("VM_PREFILTER") != "none":
                viol["route"].append("%s: ENGINE %s VM_PREFILTER %s" % (key, st.get("ENGINE"), st.get("VM_PREFILTER")))
            if st.get("VM_START") != "unanchored":
                viol["anchor"].append("%s: VM_START %s" % (key, st.get("VM_START")))
            if st.get("REQ_HANDOFF") != "none":
                viol["handoff"].append("%s: REQ_HANDOFF %s" % (key, st.get("REQ_HANDOFF")))
            nmov_tbl += 1
            if r.get("table") is None or r.get("fact") is None or r["table"] != r["fact"]:
                viol["table"].append("%s: table %s, fact %s" % (
                    key, None if r.get("table") is None else len(r["table"]),
                    None if r.get("fact") is None else len(r["fact"])))
        elif r["ntable"] or r["nseek"]:
            viol["iff"].append("%s: stamp none, %d table(s), %d seek(s)" % (key, r["ntable"], r["nseek"]))
        dfahat = st.get("DFA_PREFILTER") in ("first-memchr-bounded", "first-class-bounded")
        if not r["deny_ok"] or r["st0"].get("VM_START_SCAN") != "none" or r["ntable0"] or r["nseek0"] \
                or (not r["deny_same"] and not dfahat):
            viol["deny"].append("%s: deny compiled=%s stamp=%s table=%d seek=%d identical-after-strip=%s"
                                % (key, r["deny_ok"], r["st0"].get("VM_START_SCAN"), r["ntable0"],
                                   r["nseek0"], r["deny_same"]))
    names = {"iff": "[vm-iff] the stamp names the emitted seek",
             "route": "[vm-route] every mover is a prefilter-less VM artifact",
             "anchor": "[vm-anchor] every mover is unanchored",
             "handoff": "[vm-handoff] no mover carries a K82 handoff",
             "deny": "[vm-deny] the deny arm is today's emitter (non-movers identical; movers identical once the seek is removed)",
             "table": "[vm-table] every mover's table equals its start_set fact"}
    for k, label in names.items():
        if viol[k]:
            bad("%s: %d violation(s)" % (label, len(viol[k])))
            for v in viol[k][:8]:
                print("    " + v)
        else:
            ok("%s (%s)" % (label, "%d movers" % (len(movers["auto"]) + len(movers["vm"]))
                            if k != "deny" else "%d artifact pairs" % sum(1 for r in res if r["status"] == "ok")))
    print("REACH: movers auto %d (floor %d), --engine=vm %d (floor %d); tables read %d"
          % (len(movers["auto"]), FLOOR_MOVERS_AUTO, len(movers["vm"]), FLOOR_MOVERS_VM, nmov_tbl))
    for arm, mf, floor in (("auto", "manifest_s2_vm_auto.tsv", FLOOR_MOVERS_AUTO),
                           ("vm", "manifest_s2_vm_forced.tsv", FLOOR_MOVERS_VM)):
        want, nbench = manifest(mf)
        got = movers[arm]
        extra, missing = sorted(got - want), sorted(want - got)
        if len(got) < floor:
            bad("[vm-movers] %s: %d movers, below the floor %d" % (arm, len(got), floor))
        if extra or missing:
            bad("[vm-movers] %s: movers vs %s: %d not in the manifest, %d manifest rows not movers"
                % (arm, mf, len(extra), len(missing)))
            for e in extra[:6]:
                print("    MOVER-NOT-IN-MANIFEST %s [%s]" % e)
            for e in missing[:6]:
                print("    MANIFEST-NOT-MOVER %s [%s]" % e)
        else:
            ok("[vm-movers] %s: movers == %s by ID (%d rows, 0 off-diagonal; %d pcrec-bench rows outside the tree, not checked here)"
               % (arm, mf, len(got), nbench))


# (pattern, options, expected stamp, why) -- written from V's conjuncts.
WITNESSES = [
    (b"(ab)\\1", ["--features", "all"], "first-class", "a backreference routes to the VM with no prefilter; S = {a}"),
    (b"(?i)(ca)t\\1", ["--features", "all"], "first-class", "caseless: S = {c, C}"),
    (b"(k)\\1", ["--features", "all", "-i", "-e", "utf8"], "first-class", "utf8 caseless: S holds the KELVIN SIGN's lead byte E2"),
    (b"a*b?", ["--features", "all", "--engine=vm"], "none", "NULLABLE: the pattern matches empty (S491's conjunct)"),
    (b"^(ab)\\1", ["--features", "all"], "none", "ANCHORED: one attempt (S492's conjunct)"),
    (b"\\G(ab)\\1", ["--features", "all"], "none", "\\G-START: one attempt (S492's conjunct)"),
    (b"(?:\\Ga|b)c", ["--features", "all", "--engine=vm"], "first-class", "a \\G branch beside an unanchored one: start_anchor unanchored; \\G reads search_from, which the seek never moves"),
    (b"(a|b)c\\d+", ["--features", "all"], "none", "a VM HYBRID: its prefilter is its start test (S493's conjunct)"),
    (b"abc", ["--features", "all"], "none", "a DFA artifact"),
    (b"(?s).(a)\\1", ["--features", "all"], "none", "|S| = 256 under byte (dotall): a full set skips nothing"),
    (b"(ab)\\1", ["--features", "all", "-fno-start-set"], "none", "DENIED"),
]


def witness_checks():
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        for i, (pat, args, want, why) in enumerate(WITNESSES):
            t = compile_c(pat, args, os.path.join(td, "w%d" % i))
            got = None if t is None else stamps(t).get("VM_START_SCAN")
            if got == want:
                ok("[vm-wit] %r %s -> %s (%s)" % (pat.decode("latin-1"), " ".join(args), want, why))
            else:
                bad("[vm-wit] %r %s -> %s, expected %s (%s)" % (pat.decode("latin-1"), " ".join(args), got, want, why))
        # The utf8 witness's table holds the lead byte E2 and both cases of k.
        t = compile_c(b"(k)\\1", ["--features", "all", "-i", "-e", "utf8"], os.path.join(td, "u"))
        tb = None if t is None else table_of(t)
        if tb == {0x4B, 0x6B, 0xE2}:
            ok("[vm-wit] (k)\\1 -i -e utf8: the table is {K, k, E2}")
        else:
            bad("[vm-wit] (k)\\1 -i -e utf8: the table is %s, expected {K, k, E2}"
                % (None if tb is None else sorted(hex(x) for x in tb)))


corpus_checks()
witness_checks()
print("checks passed: %d" % passed)
print("checks failed: %d" % failed)
sys.exit(1 if failed else 0)
