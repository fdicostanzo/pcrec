#!/usr/bin/env python3
"""tests/findings/e1_object_check.py — the ANALYSIS OBJECT's checks
([WINDOW-E1], docs/design/memfn/window_contract.md §3.7.7: C-E1-1..C-E1-5),
read off a `-DPCREC_KS_TRACE` build's `KSRCTRACE object` records.

    e1_object_check.py TREE KSTPCREC FIXDIR RESDIR WORK

TREE is the repo (the store's `.rxt` files and findings_ref.py), KSTPCREC a
-DPCREC_KS_TRACE pcrec, FIXDIR e1_fixtures.py's tree, RESDIR res_fixtures.py's
(its `multi.rxt`), WORK scratch. Prints PASS:/FAIL: lines; exit 1 on a FAIL.

THE RECORD (src/gen/memfn_sites.c `analysis_trace`), one per query per
attempt, written where the object is built:

    KSRCTRACE object TAG ROW STATE SOURCE BUNDLE DIGEST BYTES FIDELITY SUM UNMEASURED

Each check's expectation comes from a source the object does not share:

  C-E1-1 CONTENT   a HAND-WRITTEN (row, state, source, bundle, bytes,
                   fidelity) table per fixture cell below, and every digest
                   recomputed by findings_ref.py from the fixture's own rows
                   (a regex reader, never pcrec's). Every T-KIND row that can
                   fire at E-1 must fire (a floor of one each).
                   THE ORDERING ASSERTION (S1031): each attempt's object
                   records come IMMEDIATELY after its `KSTRACE ... resolve`
                   record, one per query — the build point is eager, never
                   the first kit call.
  C-E1-2 QUERIES   every attempt lists the vocabulary once, in this order,
                   written here by hand: byte-rate, run-rarity.
  C-E1-3 PAYLOAD   a payload (SUM) travels iff the kind is PRESENT with a
                   PRIOR_AUTHORED or MEASURED source, and then sums to
                   exactly 1,000,000; PRIOR_NONE states bundle `-`, digest 0
                   and bytes 0 (S993's false-confidence table is a payload
                   under PRIOR_NONE).
  C-E1-4 AGREEMENT the artifact's `<PREFIX>_FINDINGS` against its final
                   attempt's object: `byte-rate=B:D` iff PRESENT with bundle B
                   and digest D; `byte-rate=none` iff PRIOR_NONE; `""` with
                   the object PRESENT is the OFFERED-NOT-ASKED cell (floor 1).
                   SHARED SOURCE: the stamp and the object both read the
                   findings memo, so this is an agreement check only; C-E1-1's
                   python digest is the independent line. Two targets under
                   two analyses in one invocation must each carry their own
                   object (S994), and a compound artifact's parts carry
                   objects equal to the shell's.
  C-E1-5 COLUMN    the `ARRIVES` rows are exactly the queries a pcrec reader
                   asks, derived HERE from a grep of src/ for the accessors'
                   callers outside src/core/findings.c (never read from the
                   table it checks).
"""
import os
import re
import subprocess
import sys

TREE, PC, FX, RES, WORK = sys.argv[1:6]
REF = [sys.executable, os.path.join(TREE, "tests/findings/findings_ref.py")]
STORE = os.path.join(TREE, "src/findings")
QUERIES = ["byte-rate", "run-rarity"]          # C-E1-2, by hand
fails = 0


def ok(m):
    print("PASS: " + m)


def bad(m):
    global fails
    fails += 1
    print("FAIL: " + m)


def ref_digest(rxt, name, kind="freq", via="unigram"):
    r = subprocess.run(REF + ["bundle-digest", rxt, name, kind, via],
                       capture_output=True, text=True)
    return r.stdout.strip()


def compile_(args, out):
    r = subprocess.run([PC, "-p", "rx"] + args + ["-o", out],
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stderr


def groups(stderr):
    """Per attempt: (the records right after its resolve record, every
    object record of the attempt). A record is the tuple of its 10 fields
    after `KSRCTRACE object`: tag row state source bundle digest bytes
    fidelity sum unmeasured."""
    out, cur = [], None
    lines = stderr.split("\n")
    for i, ln in enumerate(lines):
        if ln == "KSTRACE\tanalysis\t-\tresolve\t-":
            cur = {"lead": [], "all": []}
            out.append(cur)
            # the resolution's own notes may sit between; the first KS-family
            # records after them must be the object's
            j = i + 1
            while j < len(lines) and not lines[j].startswith(("KSTRACE\t", "KSRCTRACE\t")):
                j += 1
            while j < len(lines) and lines[j].startswith("KSRCTRACE\tobject\t"):
                cur["lead"].append(tuple(lines[j].split("\t")[2:]))
                j += 1
        elif ln.startswith("KSRCTRACE\tobject\t") and cur is not None:
            cur["all"].append(tuple(ln.split("\t")[2:]))
    return out


def stamp(path):
    try:
        m = re.search(r'^#define [A-Z0-9_]+_FINDINGS "(.*)"$', open(path).read(), re.M)
    except OSError:
        return None
    return m.group(1) if m else None


SD = ref_digest(os.path.join(STORE, "default.rxt"), "default")
I = lambda d, n: ["-I", os.path.join(FX, d), "--analysis", n]
U8 = ["-e", "utf8"]
QUIET = ["-fno-req-byte", "--pattern", "^abc"]   # asks nothing: compiles under l1none
PAT = ["--pattern", "abc"]
# C-E1-1's hand-written table: cell -> (args, row, state, source, bundle,
# bytes, fidelity, digest). `bundle` is the answering bundle, '-' where none;
# digest '0' where no table travels.
CELLS = {
    "none/byte":   ([] + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "default", "0", "-", SD),
    "none/utf8":   (U8 + PAT, "prior-none", "PRESENT", "PRIOR_NONE", "-", "0", "-", "0"),
    "weblog/byte": (["--analysis", "weblog"] + PAT, "measured", "PRESENT", "MEASURED", "weblog",
                    "1000000", "-", ref_digest(os.path.join(STORE, "weblog.rxt"), "weblog")),
    "weblog/utf8": (U8 + ["--analysis", "weblog"] + PAT, "measured", "PRESENT", "MEASURED", "weblog",
                    "1000000", "-", ref_digest(os.path.join(STORE, "weblog.rxt"), "weblog",
                                               "cpfreq", "encode-utf8")),
    # D162 add. 4: `fidelity synthesized` is not measured evidence
    "log/byte":    (["--analysis", "log"] + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "log",
                    "0", "synthesized", ref_digest(os.path.join(STORE, "log.rxt"), "log")),
    "log/utf8":    (U8 + ["--analysis", "log"] + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "log",
                    "0", "synthesized", ref_digest(os.path.join(STORE, "log.rxt"), "log",
                                                   "cpfreq", "encode-utf8")),
    # a byte-identical user copy of the store's default, found at -I: AUTHORED
    "copy/byte":   (I("COPY", "default") + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "default",
                    "0", "-", SD),
    "copy/utf8":   (U8 + I("COPY", "default") + PAT, "prior-none", "PRESENT", "PRIOR_NONE", "-",
                    "0", "-", "0"),
    # a bundle NAMED default declaring a measured source: MEASURED (S992)
    "mdef/byte":   (I("MDEF", "default") + PAT, "measured", "PRESENT", "MEASURED", "default",
                    "4242", "-", ref_digest(os.path.join(FX, "MDEF/default.rxt"), "default")),
    "mdef/utf8":   (U8 + I("MDEF", "default") + PAT, "prior-none", "PRESENT", "PRIOR_NONE", "-",
                    "0", "-", "0"),
    "auth/byte":   (I("AUTH", "mine") + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "mine",
                    "0", "-", ref_digest(os.path.join(FX, "AUTH/mine.rxt"), "mine")),
    "auth/utf8":   (U8 + I("AUTH", "mine") + PAT, "prior-none", "PRESENT", "PRIOR_NONE", "-",
                    "0", "-", "0"),
    # `include <default>` by name: byte falls to the store's default
    "inc/byte":    (I("INC", "incd") + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "default",
                    "0", "-", SD),
    "inc/utf8":    (U8 + I("INC", "incd") + PAT, "measured", "PRESENT", "MEASURED", "incd",
                    "333", "-", ref_digest(os.path.join(FX, "INC/incd.rxt"), "incd")),
    # a two-link user chain: each encoding's first answering link
    "chain/byte":  (I("CHAIN", "outer") + PAT, "measured", "PRESENT", "MEASURED", "inner",
                    "555", "verbatim", ref_digest(os.path.join(FX, "CHAIN/inner.rxt"), "inner")),
    "chain/utf8":  (U8 + I("CHAIN", "outer") + PAT, "measured", "PRESENT", "MEASURED", "outer",
                    "444", "-", ref_digest(os.path.join(FX, "CHAIN/outer.rxt"), "outer")),
    "l1none/byte": (I("L1", "l1none") + PAT, "authored", "PRESENT", "PRIOR_AUTHORED", "default",
                    "0", "-", SD),
    # underivable under utf8: the offer is PRIOR_NONE and refuses nothing
    "l1none/utf8": (U8 + I("L1", "l1none") + QUIET, "underivable-arrives", "PRESENT", "PRIOR_NONE",
                    "-", "0", "-", "0"),
}
RUNRARITY = ("no-shape", "ABSENT", "UNSTATED", "-", "0000000000000000", "0", "-", "-", "ABSENT")

fired, c1, order_bad, c2, c3, c3bad = set(), 0, 0, 0, 0, 0
c4 = {"agree": 0, "quiet": 0}
for cell, (args, row, st, src, bun, nb, fid, dg) in CELLS.items():
    out = os.path.join(WORK, cell.replace("/", "_") + ".c")
    rc, err = compile_(args, out)
    gs = groups(err)
    if rc != 0 or not gs:
        bad(f"C-E1-1 {cell}: the compile failed (rc {rc}) or wrote no resolve record: "
            f"{err.strip().splitlines()[-1:] }")
        continue
    for g in gs:
        if [r[0] for r in g["lead"]] != QUERIES or len(g["all"]) != len(QUERIES):
            order_bad += 1
            bad(f"C-E1-1/C-E1-2 {cell}: an attempt's object records are not the "
                f"{len(QUERIES)} queries right after its resolve record, in vocabulary "
                f"order (lead {[r[0] for r in g['lead']]}, {len(g['all'])} in the attempt)")
    if order_bad:
        continue
    c2 += 1
    br, rr = gs[-1]["lead"][0], gs[-1]["lead"][1]
    want_dg = dg if dg == "0" else dg
    got = (br[1], br[2], br[3], br[4], br[6], br[7])
    want = (row, st, src, bun, nb, fid)
    if got != want:
        bad(f"C-E1-1 {cell}: byte-rate is {got}, the table says {want}")
    elif (want_dg == "0" and br[5] != "0" * 16) or (want_dg != "0" and br[5] != want_dg):
        bad(f"C-E1-1 {cell}: byte-rate digest {br[5]}, findings_ref.py computes {want_dg}")
    else:
        c1 += 1
        fired.add(row)
    if rr[1:] != RUNRARITY:
        bad(f"C-E1-1 {cell}: run-rarity is {rr[1:]}, want {RUNRARITY} (no payload shape before B4)")
    else:
        fired.add("no-shape")
    # C-E1-3, over every record of every attempt
    for g in gs:
        for r in g["all"]:
            table = r[2] == "PRESENT" and r[3] in ("PRIOR_AUTHORED", "MEASURED")
            c3bad += 1
            if table and r[8] != "1000000":
                bad(f"C-E1-3 {cell}: {r[0]} carries a table but its payload sums to {r[8]}")
            elif not table and r[8] != "-":
                bad(f"C-E1-3 {cell}: {r[0]} ({r[2]}/{r[3]}) carries a payload ({r[8]})")
            elif r[3] == "PRIOR_NONE" and (r[4] != "-" or r[5] != "0" * 16 or r[6] != "0"):
                bad(f"C-E1-3 {cell}: {r[0]} PRIOR_NONE states bundle/digest/bytes {r[4:7]}")
            else:
                c3 += 1
                c3bad -= 1
    # C-E1-4 on the same artifact
    s = stamp(out)
    if s == "":
        c4["quiet"] += br[2] == "PRESENT"
    elif s == "byte-rate=none" and br[3] == "PRIOR_NONE":
        c4["agree"] += 1
    elif s and s == f"byte-rate={br[4]}:{br[5]}" and br[2] == "PRESENT":
        c4["agree"] += 1
    else:
        bad(f"C-E1-4 {cell}: stamp \"{s}\" disagrees with the object {br[2:6]}")

if c1 == len(CELLS) and not order_bad:
    ok(f"C-E1-1 the object's byte-rate kind matches the hand-written table and "
       f"findings_ref.py's digest on all {c1} fixture cells; run-rarity is no-shape on each")
    ok(f"C-E1-1 ordering: every attempt's object records follow its resolve record "
       f"at once (S1031's detector)")
need = {"no-shape", "underivable-arrives", "measured", "authored", "prior-none"}
if need <= fired:
    ok(f"C-E1-1 reach: every T-KIND row that can fire at E-1 fired ({', '.join(sorted(need))}); "
       "underivable, authored-absent and absent need a payload-carrying MEASURED-ONLY kind "
       "(UNREACHED until [FINDINGS] B4)")
else:
    bad(f"C-E1-1 reach: T-KIND row(s) {sorted(need - fired)} never fired")
if c2 == len(CELLS):
    ok(f"C-E1-2 every attempt lists {', '.join(QUERIES)} once, in vocabulary order ({c2} cells)")
if c3 and not c3bad:
    ok(f"C-E1-3 the payload invariant holds on all {c3} object records")

# C-E1-4: two targets, two analyses, one invocation (S994); multi.rxt (#22)
for name, src, tgts in (("multi2", os.path.join(FX, "multi2.rxt"), ["t_web", "t_def"]),
                        ("multi", os.path.join(RES, "multi.rxt"), ["t_asks", "t_quiet"])):
    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)
    r = subprocess.run([PC, "-o", d, src], capture_output=True, text=True, timeout=120)
    gs = groups(r.stderr)
    if r.returncode != 0 or len(gs) != len(tgts):
        bad(f"C-E1-4 {name}: rc {r.returncode}, {len(gs)} attempt(s) for {len(tgts)} targets "
            "(one attempt each expected)")
        continue
    bad_here = 0
    for t, g in zip(tgts, gs):
        s, br = stamp(os.path.join(d, t + ".c")), g["lead"][0] if g["lead"] else None
        if br is None:
            bad_here += 1
            bad(f"C-E1-4 {name}/{t}: the target's attempt built no object (S994)")
        elif s == "":
            c4["quiet"] += br[2] == "PRESENT"
        elif s != f"byte-rate={br[4]}:{br[5]}":
            bad_here += 1
            bad(f"C-E1-4 {name}/{t}: stamp \"{s}\", object {br[4]}:{br[5]}")
        else:
            c4["agree"] += 1
    if name == "multi2" and not bad_here:
        if gs[0]["lead"][0][4] == "weblog" and gs[1]["lead"][0][4] == "default":
            ok("C-E1-4 two targets under two analyses in one invocation each carry their own "
               "object (weblog, then default)")
        else:
            bad(f"C-E1-4 multi2: the targets' objects name {gs[0]['lead'][0][4]} and "
                f"{gs[1]['lead'][0][4]}, want weblog then default (one object per compile, S994)")
# a compound artifact: every part's object equals the shell's
r = subprocess.run([PC, "-p", "rx", "--features", "all", "--pattern", r"^\s+|\s+$",
                    "-o", os.path.join(WORK, "cmp.c")], capture_output=True, text=True, timeout=120)
gs = groups(r.stderr)
objs = {tuple(g["lead"]) for g in gs}
if r.returncode == 0 and len(gs) >= 3 and len(objs) == 1:
    ok(f"C-E1-4 a compound artifact's {len(gs)} compiles (the shell and its parts) carry equal objects")
else:
    bad(f"C-E1-4 the compound witness: rc {r.returncode}, {len(gs)} compile(s), "
        f"{len(objs)} distinct object(s) (want >= 3 compiles, 1 object)")
if c4["quiet"] >= 1 and c4["agree"] >= 1:
    ok(f"C-E1-4 the stamp agrees with the object on {c4['agree']} artifact(s); "
       f"{c4['quiet']} OFFERED-NOT-ASKED artifact(s) stamp \"\" with the kind PRESENT")
else:
    bad(f"C-E1-4 population: {c4['agree']} agreeing, {c4['quiet']} offered-not-asked (want >= 1 each)")

# C-E1-5: the ARRIVES column against the readers, derived from src/ by grep
ACCESSOR_QUERY = {"pcrec_find_byte_rate": "byte-rate", "pcrec_find_set_ppm": "byte-rate",
                  "pcrec_find_byte_rate_answers": "byte-rate"}
asked = set()
for d, _, fs in os.walk(os.path.join(TREE, "src")):
    for f in fs:
        p = os.path.join(d, f)
        if not f.endswith(".c") or os.path.relpath(p, TREE) == "src/core/findings.c":
            continue
        text = open(p, encoding="latin-1").read()
        for acc, q in ACCESSOR_QUERY.items():
            if re.search(r"\b%s\s*\(" % acc, text):
                asked.add(q)
gs = groups(compile_(PAT, os.path.join(WORK, "col.c"))[1])
arrives = {r[0] for r in gs[-1]["all"] if r[9] == "ARRIVES"} if gs else set()
if not asked:
    bad("C-E1-5 the grep found no accessor caller in src/ (the check lost its population)")
elif arrives == asked:
    ok(f"C-E1-5 the ARRIVES rows ({', '.join(sorted(arrives))}) are exactly the queries "
       "a pcrec reader asks (accessor callers outside findings.c)")
else:
    bad(f"C-E1-5 ARRIVES rows {sorted(arrives)} but pcrec readers ask {sorted(asked)} "
        "(D162 add. 3: a fact pcrec uses is sent ALWAYS; one it does not stays ABSENT unmeasured)")
sys.exit(1 if fails else 0)
