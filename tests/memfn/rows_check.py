#!/usr/bin/env python3
"""tests/memfn/rows_check.py — [MEMFN-ROWCON] N4's checks on the kit's ROWS
(docs/design/memfn/row_contracts.md rev 4.1 §4). Run by run_rows.sh
(`make test-memfn-rows`); prints `checks passed:` / `checks failed:`.

    rows_check.py --root TREE --cc CC --tmp DIR

WHAT IT CONTROLS, AND AGAINST WHAT (each control shares no source with its
subject):

  A. THE ROW SET. tests/memfn/rows.tsv (hand-written) against the kit's
     actual rows, which this script derives by BUILDING the kit with
     -DMF_TRACE (every .c under memfn/src, found by `find`, short list
     fatal) and running C5's fixture driver: the trace prints every row of
     every selection table at exit (`MFTRACE REACH table=T row=R`, walked
     off compose.c's `arms[]`, runcmp.c's rows and, since R4e'.0,
     ofsskip.c's `fn_rows[]`). A row in either and not
     the other is red, as is a duplicate, a REACH_DROPPED count, or fewer
     than ROWS_FLOOR rows (a literal in run_rows.sh). The runcmp rows are
     also held to the two caller-visible statements of them, which share no
     source with the manifest: `pcrec --list-axes`'s `run-overlap` rows and
     docs/spec/tuning.md §2.38's row table.
  B. THE REASONS. Every row's reach is from the closed set (pcrec,
     total-fallback, pending-site:<trigger>, contract-reach:<G2 family>,
     the family read from memfn/tests/run_g2.sh's FAM_FLOORS); a `pcrec`
     row's witness is a pcrec compile and every other row's a fixture.
     Whether a `pcrec` row IS reached, and a closed-reason row is NOT, over
     the whole corpus is the census's (n2_report.py --floors): this check
     sees one witness, the census the population.
  C. THE SIGNATURES. For each row: its witness's artifact CONTAINS the
     signature and the trace CHOSE the row there; its control's artifact
     (a deny, another flag or another witness) does NOT contain it and the
     trace did NOT choose the row. The text (the artifact) and the selection
     (the kit's own trace) are two observations; the check requires they
     agree. Then every signature is held to EVERY artifact and fixture this
     run produced: wherever a signature appears, its row was chosen there
     (the sibling exclusion). Every pcrec compile is made twice, by the
     traced pcrec and by build/pcrec, and the artifacts must be identical
     byte for byte: the trace build moves nothing, and the text checked is
     the shipped compiler's.
  D. THE FLOOR FILE. tests/memfn/row_floors.tsv names exactly rows.tsv's
     rows; a pcrec floor is a positive integer or PLACEHOLDER, a non-pcrec
     row's is `-`; a g2 floor is a positive integer or PLACEHOLDER.
     PLACEHOLDER cells are counted and printed as UNREACHED (the manager's
     census pins them), never as a pass.

  E. THE ADVANCE HOOK CLASSES (R4h prep, G3). The kit's lexical class of
     each ADVANCE hook text (`more` CONJ, `peek` POSTFIX, `step` EXPR_STMT,
     else OTHER) against CLASS_EXPECT below, a table written HERE (not
     derived from fields.def or gate.c): each of arm_fixtures' `adv-cls-*`
     gate cases runs ALONE (`--gate --gate-only CASE`) under the traced kit,
     and its `MFTRACE REACH ... row=generic field=F class=C` lines are its
     hooks' classes as the gate read them. The two counter cases hold the
     caller-owned counter's CONDITIONAL use (MF_SITE_ABI 5): `count` is a
     used field of the caller-owned site and not of the kit-owned one. K35:
     at least CLASS_CASE_FLOOR cases (a literal in run_rows.sh), each narrow
     class expected at least twice and OTHER at least twice per field.

WHAT IT DOES NOT SEE: whether the floors hold (the full census does, in a
slot: n2_report.py --floors); G2's per-row reach (G2 prints form ids, not
rows); a row whose witness stops being chosen in the corpus but stays chosen
for its own witness pattern (the census's floor is that control).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

REASONS = ("pcrec", "total-fallback", "pending-site:", "contract-reach:")
passed = failed = 0
unreached = []


def ok(msg=None):
    global passed
    passed += 1
    if msg and os.environ.get("VERBOSE"):
        print("ok: " + msg)


def bad(msg):
    global failed
    failed += 1
    print("FAIL: " + msg)


def run(argv, **kw):
    return subprocess.run(argv, capture_output=True, timeout=120, **kw)


def read_tsv(path, ncol):
    rows = []
    with open(path) as f:
        for i, ln in enumerate(f, 1):
            ln = ln.rstrip("\n")
            if not ln or ln.startswith("#"):
                continue
            c = ln.split("\t")
            if len(c) != ncol:
                bad("%s:%d has %d columns, not %d" % (os.path.basename(path), i, len(c), ncol))
                continue
            rows.append(c)
    return rows


def unesc(s):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "\\": "\\"}.get(m.group(1), m.group(0)), s)


def trace_chosen(err):
    """(table, row) chosen at define/run phases, from END records."""
    out = set()
    for ln in err.decode("utf-8", "replace").splitlines():
        if not ln.startswith("MFTRACE END "):
            continue
        d = dict(t.partition("=")[::2] for t in ln.split()[2:])
        if d.get("chosen", "-") != "-" and d.get("phase") != "use":
            out.add((d.get("table"), d["chosen"]))
    return out


def reach_rows(err):
    rows, dropped = [], None
    for ln in err.decode("utf-8", "replace").splitlines():
        if ln.startswith("MFTRACE REACH ") and " field=" not in ln:
            d = dict(t.partition("=")[::2] for t in ln.split()[2:])
            rows.append((d.get("table"), d.get("row")))
        elif ln.startswith("MFTRACE REACH_DROPPED "):
            dropped = int(ln.split("n=")[1])
    return rows, dropped


def build(root, cc, tmp):
    """The traced kit objects, the traced fixture driver and a traced pcrec
    (build/libpcrec.a with its kit members swapped for traced ones). Returns
    (fx, tpcrec) or exits."""
    srcs = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(root, "memfn/src"))
                  for f in fs if f.endswith(".c"))
    if len(srcs) < int(os.environ["KIT_SRC_FLOOR"]):
        bad("memfn/src holds %d .c files, under KIT_SRC_FLOOR %s" % (len(srcs), os.environ["KIT_SRC_FLOOR"]))
        return None, None
    od = os.path.join(tmp, "kit")
    os.makedirs(od, exist_ok=True)
    objs = []
    for s in srcs:
        o = os.path.join(od, os.path.basename(s)[:-2] + ".o")
        r = run([cc, "-std=gnu11", "-O1", "-DMF_TRACE", "-c", "-o", o, s])
        if r.returncode:
            bad("%s does not compile with -DMF_TRACE: %s" % (s, r.stderr.decode()[:300]))
            return None, None
        objs.append(o)
    fx = os.path.join(tmp, "fx_trace")
    r = run([cc, "-std=gnu11", "-O1", "-I" + os.path.join(root, "memfn/include"),
             os.path.join(root, "tests/memfn/arm_fixtures.c")] + objs + ["-o", fx])
    if r.returncode:
        bad("the traced fixture driver does not build: " + r.stderr.decode()[:300])
        return None, None
    lib = os.path.join(root, "build/libpcrec.a")
    lc = os.path.join(tmp, "lib_nokit.a")
    shutil.copy(lib, lc)
    members = run(["ar", "t", lc]).stdout.decode().split()
    for o in objs:
        m = os.path.basename(o)
        if members.count(m) != 1:
            bad("build/libpcrec.a holds %d members named %s (need exactly 1)" % (members.count(m), m))
            return fx, None
    if run(["ar", "d", lc] + [os.path.basename(o) for o in objs]).returncode:
        bad("ar d failed on the library copy")
        return fx, None
    tp = os.path.join(tmp, "pcrec_trace")
    r = run([cc, "-std=gnu11", "-O1", "-I" + os.path.join(root, "lib"), "-I" + os.path.join(root, "src"),
             os.path.join(root, "cli/main.c")] + objs + [lc, "-o", tp])
    if r.returncode:
        bad("the traced pcrec does not link: " + r.stderr.decode()[:300])
        return fx, None
    return fx, tp


class Art:
    def __init__(self, label, text, chosen):
        self.label, self.text, self.chosen = label, text, chosen


def compile_pattern(root, tp, flags, pat, label):
    argv_tail = ["-p", "rx", "--features", "all"] + flags + ["-o", "-", "--pattern", pat]
    rt = run([tp] + argv_tail)
    rp = run([os.path.join(root, "build/pcrec")] + argv_tail)
    if rt.returncode or rp.returncode or not rp.stdout:
        bad("%s: does not compile (traced rc %d, plain rc %d): %s"
            % (label, rt.returncode, rp.returncode, rp.stderr.decode()[:200]))
        return None
    if rt.stdout != rp.stdout:
        bad("%s: the MF_TRACE pcrec's artifact differs from build/pcrec's" % label)
        return None
    return Art(label, rp.stdout.decode("utf-8", "replace"), trace_chosen(rt.stderr))


def render_fixture(fx, tmp, name, label):
    d = os.path.join(tmp, "fx_" + re.sub(r"\W", "_", name))
    os.makedirs(d, exist_ok=True)
    r = run([fx, d, "--only", name])
    if r.returncode:
        bad("%s: fixture %s does not render (rc %d)" % (label, name, r.returncode))
        return None
    text = ""
    for part in ("def", "use"):
        p = os.path.join(d, "%s.%s" % (name, part))
        if os.path.exists(p):
            text += open(p, encoding="utf-8", errors="replace").read()
    return Art(label, text, trace_chosen(r.stderr))


def spec_runcmp_rows(root):
    """docs/spec/tuning.md §2.38's row table: the first column of each
    `| \\`name\\` |` line between the §2.38 heading and the next heading."""
    names, on = [], False
    for ln in open(os.path.join(root, "docs/spec/tuning.md"), encoding="utf-8"):
        if ln.startswith("### "):
            on = ln.startswith("### 2.38 ")
            continue
        m = on and re.match(r"^\| `([a-z]+)` \|", ln)
        if m:
            names.append(m.group(1))
    return names


def axes_runcmp_rows(root):
    r = run([os.path.join(root, "build/pcrec"), "--list-axes"])
    names = []
    for ln in r.stdout.decode().splitlines():
        if ln.startswith("#section"):
            break
        c = ln.split("\t")
        if len(c) > 2 and c[0] == "run-overlap":
            names.append(c[2])
    return names


def axes_simd_rows(root):
    """The `simd`-layer rows of --list-axes' memfn section (name, layer)."""
    r = run([os.path.join(root, "build/pcrec"), "--list-axes"])
    rows, inside = [], False
    for ln in r.stdout.decode().splitlines():
        if ln.startswith("#section"):
            inside = ln.split()[1:2] == ["memfn"]
            continue
        c = ln.split("\t")
        if inside and not ln.startswith("#") and len(c) > 3 and c[3] == "simd":
            rows.append(c[0])
    return rows


# E's expectations: case -> {field: class}; a field absent from a case's dict
# must NOT be a used field there (None marks one explicitly). Written by hand
# from memfn.h's class definitions, sharing no code with gate.c.
CLASS_EXPECT = {
    "adv-cls-fwd":    {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"},
    "adv-cls-view":   {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"},
    "adv-cls-rev":    {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"},
    "adv-cls-vm":     {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"},
    "adv-cls-edge2":  {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"},
    "adv-cls-arrow":  {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"},
    "adv-cls-or":     {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-cls-assign": {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-cls-shift":  {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-cls-tern":   {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-cls-call":   {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-cls-comma":  {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-cls-trail":  {"more": "OTHER", "peek": "OTHER", "step": "OTHER"},
    "adv-caller-count": {"more": "CONJ", "count": "OTHER"},
    "adv-kit-count":    {"more": "CONJ", "count": None},
}
NARROW = {"more": "CONJ", "peek": "POSTFIX", "step": "EXPR_STMT"}


def reach_classes(err, row):
    """{field: set(classes)} of `row`'s REACH cells (table arms)."""
    out = {}
    for ln in err.decode("utf-8", "replace").splitlines():
        if not ln.startswith("MFTRACE REACH ") or " field=" not in ln:
            continue
        d = dict(t.partition("=")[::2] for t in ln.split()[2:])
        if d.get("table") == "arms" and d.get("row") == row:
            out.setdefault(d["field"], set()).add(d["class"])
    return out


def g2_families(root):
    txt = open(os.path.join(root, "memfn/tests/run_g2.sh"), encoding="utf-8").read()
    m = re.search(r'^FAM_FLOORS="([^"]*)"', txt, re.M)
    return [f.split(":")[0] for f in m.group(1).split()] if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--cc", default="cc")
    ap.add_argument("--tmp", required=True)
    a = ap.parse_args()
    root = a.root
    manifest = os.path.join(root, os.environ.get("ROWS_TSV", "tests/memfn/rows.tsv"))
    rows = read_tsv(manifest, 9)
    floors = read_tsv(os.path.join(root, os.environ.get("FLOORS_TSV", "tests/memfn/row_floors.tsv")), 4)

    fx, tp = build(root, a.cc, a.tmp)
    if not fx or not tp:
        return

    # ---- A. the row set -------------------------------------------------
    os.makedirs(os.path.join(a.tmp, "all"))
    r = run([fx, os.path.join(a.tmp, "all")])
    if r.returncode:
        bad("the traced fixture driver failed (rc %d)" % r.returncode)
    kit, dropped = reach_rows(r.stderr)
    floor = int(os.environ["ROWS_FLOOR"])
    if len(kit) < floor:
        bad("the kit's trace lists %d rows, under ROWS_FLOOR %d" % (len(kit), floor))
    else:
        ok()
    if dropped != 0:
        bad("the trace's REACH_DROPPED is %r (the reach registry is full or absent)" % dropped)
    else:
        ok()
    for k in sorted(set(kit)):
        if kit.count(k) > 1:
            bad("the kit has %d rows named %s/%s" % (kit.count(k), k[0], k[1]))
    man = [(c[0], c[1]) for c in rows]
    for k in sorted(set(man)):
        if man.count(k) > 1:
            bad("rows.tsv has %d lines for %s/%s" % (man.count(k), k[0], k[1]))
    for k in kit:
        if k in man:
            ok()
        else:
            bad("the kit has row %s/%s and rows.tsv does not" % k)
    for k in man:
        if k not in kit:
            bad("rows.tsv names %s/%s and the kit has no such row" % k)
    mrc = [k[1] for k in man if k[0] == "runcmp"]
    for src, names in (("pcrec --list-axes run-overlap", axes_runcmp_rows(root)),
                       ("docs/spec/tuning.md §2.38", spec_runcmp_rows(root))):
        if not names:
            bad("%s: no runcmp rows found (the reader is blind)" % src)
        elif sorted(names) != sorted(mrc):
            bad("%s lists the run compare's rows %s, rows.tsv %s" % (src, sorted(names), sorted(mrc)))
        else:
            ok()

    # ---- F. the SIMD acceptance record (R-13, §R4.9.6) ---------------------
    # Every `simd`-layer row of --list-axes' memfn section has a line per
    # level and official CPU class (zen1, zen4) in simd_accept.tsv; states
    # from the closed set; a line past CANDIDATE needs a bench tier and a
    # transcript that exists (C19's binding; its digest half is UNREACHED
    # until a timing run writes one).
    simd_rows = axes_simd_rows(root)
    acc = read_tsv(os.path.join(root, "tests/memfn/simd_accept.tsv"), 18)
    if not simd_rows:
        bad("pcrec --list-axes: no simd-layer row in the memfn section (the reader is blind)")
    states = ("CANDIDATE", "ACCEPTED", "STALE", "REJECTED")
    for r in simd_rows:
        lines = [c for c in acc if c[0] == r]
        lv = sorted({c[1] for c in lines})
        cls = {(c[1], c[2]) for c in lines}
        if not lv or any((l, k) not in cls for l in lv for k in ("zen1", "zen4")):
            bad("simd_accept.tsv: SIMD row %s lacks a line per level x {zen1, zen4} (has %s)"
                % (r, sorted(cls)))
        else:
            ok()
    nonc = 0
    for c in acc:
        if c[0] not in simd_rows:
            bad("simd_accept.tsv names %s, which is no simd-layer row" % c[0])
        if c[3] not in states:
            bad("simd_accept.tsv %s/%s/%s: state %r" % (c[0], c[1], c[2], c[3]))
        elif c[3] != "CANDIDATE":
            nonc += 1
            if c[4] != "bench" or c[17] == "-" or not os.path.exists(os.path.join(root, c[17])):
                bad("simd_accept.tsv %s/%s/%s: %s without a bench tier and an existing "
                    "transcript (C19)" % (c[0], c[1], c[2], c[3]))
    if not nonc:
        unreached.append("C19: simd_accept.tsv holds CANDIDATE lines only (%d); the digest "
                         "check is born with the first timing transcript" % len(acc))

    # ---- B. the reasons ---------------------------------------------------
    fams = g2_families(root)
    if not fams:
        bad("memfn/tests/run_g2.sh: no FAM_FLOORS line (the family list is unreadable)")
        fams = []
    for c in rows:
        t, rw, why, wk = c[0], c[1], c[2], c[3]
        if why == "pcrec" or why == "total-fallback":
            good = True
        elif why.startswith("pending-site:"):
            good = len(why) > len("pending-site:")
        elif why.startswith("contract-reach:"):
            good = why[len("contract-reach:"):] in fams
        else:
            good = False
        if not good:
            bad("%s/%s: reach %r is not in the closed set (pcrec, total-fallback, "
                "pending-site:<trigger>, contract-reach:<G2 family %s>)" % (t, rw, why, ",".join(fams)))
            continue
        want = "pattern" if why == "pcrec" else "fixture"
        if wk != want:
            bad("%s/%s: reach %s needs a %s witness, not %s" % (t, rw, why, want, wk))
        else:
            ok()
    n_total_fb = sum(1 for c in rows if c[2] == "total-fallback")
    if n_total_fb != len({c[0] for c in rows if c[2] == "total-fallback"}):
        bad("more than one total-fallback row in one table")

    # ---- C. the signatures ------------------------------------------------
    arts = []
    for c in rows:
        t, rw, why, wk, wf, wit, sig, cf, ctl = c
        sig = unesc(sig)
        key = (t, rw)
        if len(sig) < 4:
            bad("%s/%s: signature %r is too short to mean anything" % (t, rw, sig))
            continue
        flags = [] if wf == "-" else wf.split()
        cflags = [] if cf == "-" else cf.split()
        if wk == "pattern":
            w = compile_pattern(root, tp, flags, wit, "%s/%s witness" % key)
            cpat = wit if ctl == "=" else ctl
            k = compile_pattern(root, tp, cflags, cpat, "%s/%s control" % key)
        else:
            w = render_fixture(fx, a.tmp, wit, "%s/%s witness" % key)
            k = render_fixture(fx, a.tmp, ctl, "%s/%s control" % key) if ctl not in ("=", "-") else None
            if k is None and ctl in ("=", "-"):
                bad("%s/%s: a fixture witness needs another fixture as its control" % key)
        for art, want in ((w, True), (k, False)):
            if art is None:
                continue
            arts.append(art)
            has, chose = sig in art.text, key in art.chosen
            if has == want and chose == want:
                ok()
            else:
                bad("%s: signature %s, row %s chosen (want %s for both)"
                    % (art.label, "present" if has else "absent", "IS" if chose else "NOT",
                       "present/chosen" if want else "absent/not chosen"))
        if w and k and w.text == k.text:
            bad("%s/%s: the control's artifact is the witness's (the control changed nothing)" % key)
    # every fixture, rendered alone, joins the exclusion population
    os.makedirs(os.path.join(a.tmp, "ids"))
    ids = run([fx, os.path.join(a.tmp, "ids")])
    fixtures = [ln.split("\t")[0] for ln in ids.stdout.decode().splitlines() if ln]
    if len(fixtures) < int(os.environ["FIXTURE_FLOOR"]):
        bad("the fixture driver listed %d fixtures, under FIXTURE_FLOOR %s"
            % (len(fixtures), os.environ["FIXTURE_FLOOR"]))
    for f in fixtures:
        art = render_fixture(fx, a.tmp, f, "fixture " + f)
        if art:
            arts.append(art)
    excl = 0
    for c in rows:
        key, sig = (c[0], c[1]), unesc(c[6])
        for art in arts:
            if sig in art.text and key not in art.chosen:
                bad("signature of %s/%s appears in %s, where the trace did not choose it"
                    % (key[0], key[1], art.label))
            else:
                excl += 1
    if excl:
        ok()
    print("sibling exclusion: %d (signature, artifact) pairs over %d artifacts" % (excl, len(arts)))

    # ---- D. the floor file -------------------------------------------------
    why = {(c[0], c[1]): c[2] for c in rows}
    fk = [(c[0], c[1]) for c in floors]
    for k in sorted(set(why) - set(fk)):
        bad("rows.tsv names %s/%s and row_floors.tsv has no line for it" % k)
    for k in sorted(set(fk) - set(why)):
        bad("row_floors.tsv names %s/%s and rows.tsv does not" % k)
    for k in sorted(set(fk)):
        if fk.count(k) > 1:
            bad("row_floors.tsv has %d lines for %s/%s" % ((fk.count(k),) + k))
    ph = 0
    for c in floors:
        key, pf, gf = (c[0], c[1]), c[2], c[3]
        if key not in why:
            continue
        good_p = (pf == "-") if why[key] != "pcrec" else (pf == "PLACEHOLDER" or (pf.isdigit() and int(pf) > 0))
        good_g = gf == "PLACEHOLDER" or (gf.isdigit() and int(gf) > 0)
        if not (good_p and good_g):
            bad("row_floors.tsv %s/%s: pcrec %r, g2 %r (pcrec: a positive integer or PLACEHOLDER, "
                "`-` iff reach is not pcrec; g2: a positive integer or PLACEHOLDER)" % (key + (pf, gf)))
        else:
            ok()
        ph += (pf == "PLACEHOLDER") + (gf == "PLACEHOLDER")
    # ---- E. the ADVANCE hook classes ----------------------------------------
    ncase = 0
    for case, want in sorted(CLASS_EXPECT.items()):
        r = run([fx, "--gate", "--gate-only", case])
        line = r.stdout.decode("utf-8", "replace").strip()
        if r.returncode or not line.startswith(case + "\tRENDER\tgeneric"):
            bad("class case %s did not render through generic (rc %d): %r" % (case, r.returncode, line))
            continue
        ncase += 1
        got = reach_classes(r.stderr, "generic")
        for f, c in sorted(want.items()):
            if c is None:
                if f in got:
                    bad("class case %s: `%s` is a used field (classes %s); it must not be"
                        % (case, f, sorted(got[f])))
                else:
                    ok()
            elif got.get(f) == {c}:
                ok()
            else:
                bad("class case %s: `%s` classified %s, expected %s"
                    % (case, f, sorted(got.get(f, set())) or "nothing (not a used field?)", c))
    if ncase < int(os.environ["CLASS_CASE_FLOOR"]):
        bad("only %d ADVANCE class cases ran, under CLASS_CASE_FLOOR %s"
            % (ncase, os.environ["CLASS_CASE_FLOOR"]))
    else:
        ok()
    for f, c in sorted(NARROW.items()):
        npos = sum(1 for w in CLASS_EXPECT.values() if w.get(f) == c)
        nneg = sum(1 for w in CLASS_EXPECT.values() if w.get(f) == "OTHER")
        if npos < 2 or nneg < 2:
            bad("CLASS_EXPECT holds %d %s and %d OTHER cases for `%s` (2 of each at least)"
                % (npos, c, nneg, f))
        else:
            ok()
    print("ADVANCE class cases: %d" % ncase)

    if ph:
        unreached.append("%d floor cells in row_floors.tsv are PLACEHOLDER: the full census "
                         "(n2_report.py --floors) and a per-row G2 count pin them" % ph)


if __name__ == "__main__":
    try:
        main()
    finally:
        for u in unreached:
            print("UNREACHED: " + u)
        print("checks passed: %d" % passed)
        print("checks failed: %d" % failed)
    sys.exit(1 if failed else 0)
