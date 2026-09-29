#!/usr/bin/env python3
"""scripts/cls_identity.py -- [CLS-TREE] S3's byte-identity instrument
(cls_s3_reader_inventory.md S7, ruling D-8).

WHAT IT IS. utf8k53_report.md S3.2's "3,348 of 3,348" sweep, committed: every
distinct (pattern, encoding, features, flags, engine) TRIPLE compiled by two
pcrec binaries -- a BASELINE and a CANDIDATE -- and the emitted C compared
BYTE FOR BYTE. scripts/emit_sweep.py has no encoding axis (its streams are
`-p rx --features all` at the default `byte`), and under `byte` an A_WCLASS is
never produced, so that sweep is vacuous for S3; this is its encoding-axis
sibling and imports its build/decode helpers rather than copying them.

POPULATIONS (all derived from the tree, none hand-listed except WITNESSES):
  corpus-asw  every `pattern` block of every tests/**/*.rxt at the (encoding,
              features, flags, engine) it is WRITTEN with (--list-source) --
              the K53 triples.
  corpus-x    every distinct (pattern, flags) x {byte, utf8} x {the features
              it is written with, `all`} -- the "every encoding x features"
              widening; most corpus blocks are written under `byte` and would
              otherwise never meet the wide-class lowering.
  bench       every pcrec-bench/bench/*/patterns/*.rx (read-only) x {byte,
              utf8} x `all` x {default, vm}.  Skipped LOUDLY if the sibling
              repo is absent.
  classes     every `\\p{X}` name found in the corpus, in five shapes (atom,
              negated atom, class member, negated class with a counted
              repeat, capturing run) x utf8 x `all` x {default, vm}.
  witnesses   the inventory's named artifact-moving cases (WITNESSES below).

REACH (K35 / MECH-REACH: a pass count is not evidence). A triple "reaches the
wide-class lowering" iff lower_class_utf8 returned non-NULL for it. The
compiler has no stamp for that (S7 asks for one and none exists; this lane
did NOT add a hook), so REACH is read from the compiler's OWN OUTPUT by a
counterfactual: the `--engine=vm --emit-ir` program listing of the pattern
under `-e utf8` differs from the listing of the same pattern under `-e byte`.
Lowering is the only thing in the pipeline that makes the two encodings'
PROGRAMS differ (an ASCII pattern's listing is identical across encodings --
measured, ir_listing.md), so a difference is the lowering firing. It is a
LOWER BOUND: a lowering that yields the same program as byte's spelling (a
lone non-ASCII literal, `\\x{e9}x`) reads as not reached, and a triple whose
forced-VM listing is refused (size) is counted `unmeasured`, not reached.
REACH is measured on BOTH binaries and the floor applies to the smaller.

POSITIVE CONTROL. A check whose control shares a source with the thing it
controls proves nothing (learnings.md S3). Two controls, neither derived from
the compiler's own claims:
  1. INSTRUMENT: one candidate output is corrupted in memory (one byte
     flipped) and pushed through the SAME comparison function; it must come
     back a mover.  Always run.
  2. COMPILER (--control): a scratch copy of the candidate revision has one
     boundary in lower_class_utf8's band table moved by one
     (`{ 0x80, 0x7FF, 2 }` -> `0x7FE`) -- an anchored plant, refused loudly if
     the anchor is missing -- is built, and the same sweep runs unperturbed-
     vs-perturbed over the reached utf8 triples plus a sample of byte
     triples.  It must report movers, every mover must be an encoding-utf8
     triple, and no byte triple may move.

USAGE
  # today's baseline: two INDEPENDENT builds of main, all populations
  python3 scripts/cls_identity.py --ref HEAD --cand-ref HEAD --control
  # a lane's own tree against its branch point
  python3 scripts/cls_identity.py --ref <branch-point> [--bin build/pcrec]
  # smoke (instrument only; floors read as violations)
  python3 scripts/cls_identity.py --ref HEAD --bin build/pcrec --sample 300

EXIT: 0 iff no mover, no asymmetric refusal, no timeout, REACH >= floor and
population >= floor (full runs only), and the controls pass.
"""
import argparse
import collections
import concurrent.futures
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import emit_sweep as es  # noqa: E402  (build_from_rev, decode_escape, run, ...)

DEFAULT_TREE = os.path.dirname(SCRIPT_DIR)
BENCH_ROOT = "/Users/fdicostanzo/pcrec-bench/bench"

# FLOORS, not equality pins (D110). Measured on main 2026-09-29 (report S3);
# set at ~90% so a corpus edit does not redden the instrument, while a
# population that COLLAPSES (an extractor break, K35) still does.
PINS = {
    "triples": 0,        # filled from the baseline record below
    "reach": 0,
}

# The inventory's S7 witnesses, plus the shapes its D-3/row-10 discussion names.
WITNESSES = [
    "\u00e9abc", "\u00e9|x", "[\u00e9]x", "[\u00e0-\u00ff]{2,5}", "[^a]x", ".",
    "(?i)[\u00e0-\u00ff]+", "[\u03b1\u03b2]+z", "(\\p{L})+x", "(\\p{Lu}\\p{Ll}*)y",
    "[^\\x{80}-\\x{10ffff}]+", "\\x{1F600}|\\x{e9}", "[\\x{e000}-\\x{f8ff}]x",
    "\\P{L}{2,4}", "(?:[a\u00e9]|b)+c", "(?<=[\u00e9])x", "x(?=[\u00e9\u00e8])",
]
CLASS_SHAPES = ["\\p{%s}", "\\P{%s}", "[\\p{%s}]x", "[^\\p{%s}]{2,3}", "(\\p{%s}+)y"]


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------
# Population
class Triple(collections.namedtuple("Triple", "pop pat enc feat flags engine")):
    __slots__ = ()

    def key(self):
        return "%s|%s|f=%s|%s|%s|%r" % (self.pop, self.enc, self.feat or "-",
                                         ",".join(self.flags) or "-",
                                         self.engine or "auto",
                                         self.pat[:70])


def corpus_blocks(list_source_bin, tree, timeout):
    """[(relpath, pattern bytes, flags, feat, enc, engine)] as WRITTEN."""
    out = []
    for f in es.find_files(tree, (".rxt",)):
        rc, txt, _ = es.run([list_source_bin, "--list-source", f], timeout)
        if rc != 0:
            continue
        for line in txt.decode("utf-8", "surrogateescape").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            c = line.split("\t")
            if len(c) < 10 or c[0] not in ("pattern", "pattern-esc"):
                continue
            out.append((os.path.relpath(f, tree), es.decode_escape(c[4]),
                        c[5], c[6], c[8], c[9]))
    return out


def flag_tuple(flagstr):
    return tuple(sorted(flagstr))


def build_population(list_source_bin, tree, timeout):
    pops = collections.OrderedDict()
    blocks = corpus_blocks(list_source_bin, tree, timeout)

    asw, x = set(), set()
    feats_of = collections.defaultdict(set)
    for _, pat, fl, ft, enc, eng in blocks:
        ft = ft or ""
        asw.add(Triple("corpus-asw", pat, enc or "byte", ft, flag_tuple(fl),
                       eng or ""))
        feats_of[(pat, flag_tuple(fl))].add(ft)
    for (pat, fl), fs in feats_of.items():
        for ft in sorted(fs | {"all"}):
            for enc in ("byte", "utf8"):
                x.add(Triple("corpus-x", pat, enc, ft, fl, ""))
    pops["corpus-asw"] = asw
    pops["corpus-x"] = x

    bench = set()
    if os.path.isdir(BENCH_ROOT):
        for d in sorted(os.listdir(BENCH_ROOT)):
            pd = os.path.join(BENCH_ROOT, d, "patterns")
            if not os.path.isdir(pd):
                continue
            for fn in sorted(os.listdir(pd)):
                if not fn.endswith(".rx"):
                    continue
                pat = open(os.path.join(pd, fn), "rb").read()
                if pat.endswith(b"\n"):
                    pat = pat[:-1]
                for enc in ("byte", "utf8"):
                    for eng in ("", "vm"):
                        bench.add(Triple("bench", pat, enc, "all", (), eng))
    else:
        log("[cls_identity] WARNING: %s absent -- bench population SKIPPED "
            "(the sibling repo is a read-only reference)" % BENCH_ROOT)
    pops["bench"] = bench

    names = set()
    for _, pat, *_ in blocks:
        for m in re.finditer(rb"\\[pP]\{\^?([A-Za-z_&=0-9]+)\}", pat):
            names.add(m.group(1))
    cls = set()
    for nm in sorted(names):
        for shape in CLASS_SHAPES:
            p = (shape % nm.decode()).encode()
            for eng in ("", "vm"):
                cls.add(Triple("classes", p, "utf8", "all", (), eng))
    pops["classes"] = cls

    wit = set()
    for w in WITNESSES:
        for enc in ("byte", "utf8"):
            for eng in ("", "vm"):
                wit.add(Triple("witnesses", w.encode(), enc, "all", (), eng))
    pops["witnesses"] = wit

    # A triple present in two populations is compiled once but counted where
    # it first appears; dedup on everything but `pop`.
    seen, ordered = set(), []
    for name, s in pops.items():
        for t in sorted(s, key=lambda t: t.key()):
            k = t[1:]
            if k in seen:
                continue
            seen.add(k)
            ordered.append(t)
    return ordered, {n: len(s) for n, s in pops.items()}


# --------------------------------------------------------------------------
# Compile
def argv_for(binp, t, timeout_unused=None, listing=False, enc=None):
    a = [binp, "-p", "rx", "-e", enc or t.enc]
    if t.feat:
        a += ["--features", t.feat]
    if "i" in t.flags:
        a.append("-i")
    if "u" in t.flags:
        a.append("--ucp")
    if listing:
        a += ["--engine=vm", "--emit-ir"]
    else:
        if t.engine:
            a.append("--engine=" + t.engine)
        # `-o -` on BOTH sides: the emitted .c names its own header after -o
        # (the -o basename trap, five recorded instances).
        a += ["-o", "-"]
    a += ["--pattern", t.pat] if es.pcrec_speaks_pattern_flag(binp) else ["--", t.pat]
    return a


def compile_t(binp, t, timeout):
    rc, out, err = es.run(argv_for(binp, t), timeout)
    if rc is None:
        return "timeout", None
    return ("ok", out) if rc == 0 else ("refuse", None)


def listing(binp, t, enc, timeout):
    rc, out, _ = es.run(argv_for(binp, t, listing=True, enc=enc), timeout)
    return out if rc == 0 else None


def reach_of(binp, t, timeout, cache):
    """True / False / None(unmeasured) for the utf8-vs-byte listing counterfactual."""
    if t.enc != "utf8":
        return None
    k = (binp, t.pat, t.feat, t.flags)
    if k not in cache:
        u = listing(binp, t, "utf8", timeout)
        b = listing(binp, t, "byte", timeout)
        cache[k] = None if (u is None or b is None) else (u != b)
    return cache[k]


class Result:
    def __init__(self):
        self.rows = []          # (Triple, status, reach_a, reach_b)
        self.stat = collections.Counter()
        self.movers, self.asym, self.timeouts = [], [], []


def sweep(triples, bin_a, bin_b, timeout, jobs, want_reach=True, tamper=None):
    """Compare bin_a's and bin_b's output for every triple. `tamper` (control 1)
    is a Triple whose bin_b output is corrupted in memory before comparing."""
    res = Result()
    ra, rb = {}, {}

    def one(t):
        sa, ca = compile_t(bin_a, t, timeout)
        sb, cb = compile_t(bin_b, t, timeout)
        if tamper is not None and t == tamper and cb:
            cb = bytes([cb[0] ^ 1]) + cb[1:]
        a = b = None
        if want_reach:
            a, b = reach_of(bin_a, t, timeout, ra), reach_of(bin_b, t, timeout, rb)
        return t, sa, ca, sb, cb, a, b

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for i, (t, sa, ca, sb, cb, a, b) in enumerate(ex.map(one, triples)):
            if "timeout" in (sa, sb):
                st = "timeout"
                res.timeouts.append(t)
            elif sa == sb == "ok":
                st = "identical" if ca == cb else "mover"
                if st == "mover":
                    res.movers.append(t)
            elif sa == sb == "refuse":
                st = "both-refuse"
            else:
                st = "asymmetric"
                res.asym.append((t, sa, sb))
            res.stat[st] += 1
            res.rows.append((t, st, a, b))
            if (i + 1) % 2000 == 0:
                log("[cls_identity] %d/%d" % (i + 1, len(triples)))
    return res


def reach_count(res, side):
    n = u = 0
    for t, st, a, b in res.rows:
        r = a if side == "a" else b
        if t.enc != "utf8":
            continue
        if r is None:
            u += 1
        elif r:
            n += 1
    return n, u


# --------------------------------------------------------------------------
PLANT_FILE = "src/opt/lower_enc.c"
PLANT_OLD = "{ 0x80,    0x7FF,    2 },"
PLANT_NEW = "{ 0x80,    0x7FE,    2 },"


def build_perturbed(cand_src, out_dir, cc):
    dst = os.path.join(out_dir, "src_perturbed")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(cand_src, dst, ignore=shutil.ignore_patterns("build", "build-*", ".git", "worktrees"))
    p = os.path.join(dst, PLANT_FILE)
    txt = open(p).read()
    if txt.count(PLANT_OLD) != 1:
        raise RuntimeError("control plant anchor missing/ambiguous in %s "
                           "(%d matches) -- re-anchor cls_identity.py PLANT_*"
                           % (PLANT_FILE, txt.count(PLANT_OLD)))
    open(p, "w").write(txt.replace(PLANT_OLD, PLANT_NEW))
    r = subprocess.run(["make", "-j4", "CC=" + cc], cwd=dst, capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode(errors="replace"))
        raise RuntimeError("perturbed build failed")
    return os.path.join(dst, "build", "pcrec")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", help="git rev to build as the BASELINE")
    ap.add_argument("--ref-bin")
    ap.add_argument("--bin", help="candidate binary (default <tree>/build/pcrec)")
    ap.add_argument("--cand-ref", help="build the CANDIDATE from this rev instead")
    ap.add_argument("--tree", default=DEFAULT_TREE)
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--sample", type=int, default=0,
                    help="every Nth-th triple only (smoke; floors do not apply)")
    ap.add_argument("--control", action="store_true",
                    help="also run the compiler-perturbation positive control")
    ap.add_argument("--no-reach", action="store_true")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    if not (a.ref or a.ref_bin):
        ap.error("--ref or --ref-bin required")

    tree = os.path.abspath(a.tree)
    out = a.out or os.path.join(tree, "build-clsid")
    os.makedirs(out, exist_ok=True)
    cc = es.resolve_cc(tree)
    t0 = time.time()

    src_dirs = {}
    if a.ref_bin:
        base = a.ref_bin
    else:
        base, src_dirs["base"] = es.build_from_rev(tree, a.ref, out, cc, "clsid_base")
    if a.cand_ref:
        cand, src_dirs["cand"] = es.build_from_rev(tree, a.cand_ref, out, cc, "clsid_cand")
    else:
        cand = a.bin or os.path.join(tree, "build", "pcrec")
    if not os.path.exists(cand):
        sys.exit("candidate binary missing: " + cand)

    triples, popsz = build_population(cand, tree, a.timeout)
    if a.sample:
        triples = triples[::a.sample]
    log("[cls_identity] population %s = %d distinct triples" % (popsz, len(triples)))

    res = sweep(triples, base, cand, a.timeout, a.jobs, want_reach=not a.no_reach)
    bad = []

    print("== cls_identity: baseline %s vs candidate %s" % (base, cand))
    print("triples: %d  %s" % (len(triples), dict(res.stat)))
    by_enc = collections.Counter(t.enc for t in triples)
    print("by encoding:", dict(by_enc))
    for pop in popsz:
        pr = [r for r in res.rows if r[0].pop == pop]
        print("  %-11s %6d (dedup'd across populations)  mover=%d" % (
            pop, len(pr), sum(1 for r in pr if r[1] == "mover")))
    if res.movers or res.asym or res.timeouts:
        bad.append("movers/asymmetric/timeouts")
        for t in res.movers[:30]:
            print("MOVER", t.key())
        for t, sa, sb in res.asym[:30]:
            print("ASYMMETRIC (base=%s cand=%s)" % (sa, sb), t.key())
        for t in res.timeouts[:30]:
            print("TIMEOUT", t.key())

    reach = None
    if not a.no_reach:
        ra, ua = reach_count(res, "a")
        rb, ub = reach_count(res, "b")
        reach = min(ra, rb)
        nu = sum(1 for t in triples if t.enc == "utf8")
        print("REACH (wide-class lowering exercised, via the utf8-vs-byte VM "
              "listing counterfactual): baseline %d, candidate %d of %d utf8 "
              "triples (unmeasured: %d / %d)" % (ra, rb, nu, ua, ub))
        if reach == 0:
            bad.append("REACH == 0: the instrument is vacuous")
        if not a.sample and reach < PINS["reach"]:
            bad.append("REACH %d below floor %d" % (reach, PINS["reach"]))
    if not a.sample and len(triples) < PINS["triples"]:
        bad.append("population %d below floor %d" % (len(triples), PINS["triples"]))

    # ---- control 1: instrument (in-memory corruption through the same path)
    ct = next((t for t in triples if compile_t(cand, t, a.timeout)[0] == "ok"), None)
    c1 = sweep([ct], base, cand, a.timeout, 1, want_reach=False, tamper=ct)
    ok1 = len(c1.movers) == 1
    print("CONTROL 1 (instrument, one byte of one output flipped): %s" %
          ("PASS -- reported as a mover" if ok1 else "FAIL -- corruption NOT reported"))
    if not ok1:
        bad.append("control 1")

    # ---- control 2: compiler perturbation
    if a.control:
        cand_src = src_dirs.get("cand") or tree
        pert = build_perturbed(cand_src, out, cc)
        reached = {(t.pat, t.feat, t.flags) for t, st, ra_, rb_ in res.rows
                   if t.enc == "utf8" and (rb_ or ra_)}
        sub = [t for t in triples if t.enc == "utf8" and (t.pat, t.feat, t.flags) in reached]
        sub += [t for t in triples if t.enc == "byte"][::max(1, len(triples) // 400)]
        c2 = sweep(sub, cand, pert, a.timeout, a.jobs, want_reach=False)
        enc_of = collections.Counter(t.enc for t in c2.movers)
        ok2 = bool(c2.movers) and enc_of.get("byte", 0) == 0
        print("CONTROL 2 (compiler plant %s, %d triples): movers=%d by-enc=%s: %s" % (
            PLANT_NEW.strip(), len(sub), len(c2.movers), dict(enc_of),
            "PASS" if ok2 else "FAIL"))
        if not ok2:
            bad.append("control 2")
    else:
        print("CONTROL 2 (compiler plant): not run (--control)")

    tsv = os.path.join(out, "clsid_triples.tsv")
    with open(tsv, "w") as f:
        f.write("pop\tenc\tfeat\tflags\tengine\tstatus\treach_base\treach_cand\tsha256(pat)\n")
        for t, st, ra_, rb_ in res.rows:
            f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                t.pop, t.enc, t.feat or "-", ",".join(t.flags) or "-",
                t.engine or "auto", st, ra_, rb_,
                hashlib.sha256(t.pat).hexdigest()[:12]))
    print("per-triple table: %s" % tsv)
    print("elapsed: %.0f s (jobs=%d)" % (time.time() - t0, a.jobs))
    if bad:
        print("RESULT: FAIL -- " + "; ".join(bad))
        sys.exit(1)
    print("RESULT: PASS -- %d/%d identical or both-refused, REACH>0" % (
        res.stat["identical"] + res.stat["both-refuse"], len(triples)))


if __name__ == "__main__":
    main()
