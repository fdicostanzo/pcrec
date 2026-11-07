#!/usr/bin/env python3
"""tests/memfn/finder_check.py -- R17-b' B1's checks on the kit's finder table
and its B1 entries (lane fdb1; docs/design/memfn/r17b_prime.md rev 3 §1, §2.5,
§4.5, §4.7; requests R-19, R-20 R-MS1..R-MS5). Run by run_finder.sh (`make
test-memfn-finder`); prints `checks passed:` / `checks failed:` and the
UNREACHED/OWED items it cannot check yet (never as a pass).

    finder_check.py --root TREE --fx PLAIN_FX --fxt TRACED_FX --tmp DIR

Two fixture drivers (tests/memfn/arm_fixtures.c): PLAIN_FX linked against
build/libpcrec.a, TRACED_FX against the kit rebuilt -DMF_TRACE (the routed
decision's `MFTRACE FDROUTE` and the PRES `MFTRACE FD` records, and the
define-time query's re-ask). B4' (lane b4p, LOCKDOWN) retired the trace-only
shadow, its `FD` FIND records and the `FDKEY` lookup records, and withdrew R0,
R5 and R7: D and E below no longer have a deciding row that reads a set key.

WHAT IT CONTROLS, AND AGAINST WHAT (each expectation is written HERE, from the
design's text, sharing no code with the kit):

  A. THE TABLE (C2's self-check, [rev3 C2]; the listing, R-MS4): the 10 rows
     the design locks at B4' (§1.3, §1.4; R0, R5 and R7 withdrawn; R3a, R3b,
     R4, R8, R1 and R2 deleted by span_pick 1a and 1f), by slot and
     in order; a basis on every row; a pick on every FIND row; no MEASURED row
     that reads no key (but R7w, MEASURED by the walk ruling); every row
     reading a DERIVED key (the converter's closed list, §5.2 C1: saving,
     xover, block, dom, lstar, g8) is DERIVED; the last row of each slot
     reads nothing; the listing carries no `routed`/`locked` column (the bit
     is deleted, LOCKDOWN); every key the
     kit's (no `pcrec.` key, R-MS1); every deny registered in options.def or
     one of B3b's three; no row lists an unpaid pick (the pay rule retired
     with R1 and R2, span_pick 1f). SN-4 (S1020) plants an UNSTATED basis.
  B. R-MS3: `walk` and `libc` hash, the forms later steps build are refused;
     the text hash ignores a rename, a comment and layout and moves on a
     one-operator edit; the walk form's hash IS its canonical text's.
     span_cards.md §3.2 (S2c): every id and class instance of formhash.c's
     ENTRY TABLE (FORM_IDS, written here from the design) resolves, reaches
     the design's kit row, is the design's class by its own site text's
     measure (settest's compares, rc-words' words); mf_form_hash(id) is the
     FOLD of its instances (every instance's site text in table order, a
     newline between two: review r9 G4; S2933); all instances hash pairwise
     distinct (sabotage (m), S2930); per INSTANCE (CHECKS-6) a rename of its
     site text renames something (CHECKS-4) and keeps the hash, and a
     one-instruction edit moves the instance's hash AND the id's fold.
  C. R-MS5 and the sets: memfn/data/sets/generate.py --check; THE CARD
     GUARD (span_cards.md §2.4, S2c; S2931): over every card table and every
     ver, a card whose deps name `kit:form.` has `form` as its FIRST dim, and
     every non-template `kit:form.<id>` dep resolves to a form hash (review
     r9 CHECKS-3), the count printed and pinned EXACTLY (CARD_FORMDEP_COUNT,
     bumped with each card that adds one); every row of
     every set on its method's card (quantity present, arity = dims), the
     set's `cards` section equal to its card table, `rows` and
     `values_digest` (measure_sets §1.6, recomputed here) as its header
     says; each card dep form resolves or is OWED with its step. THE
     measure_store PASS (span_cards.md §2.4, S2e): every committed
     measure_store set of a `kit-grid` method has its cards section equal
     to its card table's ver; every row on its card; each form-first row's
     form token resolves to a form hash (red, never "later", in a FORMAT-2
     set; a format-1 set's rows keep the "later" treatment and its `-` deps
     are NOTED) and, in a format-2 set, its recorded `kit:form.<id>=<hash>`
     names that same id with a 16-hex hash (sabotage (u) S2966, (u2) S2967);
     a recorded hash differing from today's is STALE, counted and printed,
     never red (measure_sets §2.4). Form-bearing rows counted and floored
     (STORE_FORMROW_FLOOR); non-form rows must carry `-` (explicit).
  D. R-MS1: every finder site under NO set and the FULL synthetic set decides
     the same rows; a `pcrec.` row and an out-of-bound value are refused (no
     clamp). (The key-removal loop, S917's detector, went with the rows that
     read a key: S917 is UNREACHED.)
  E. (retired with the shadow's FDKEY records: no deciding row reads a key.)
  F. R-MS2: `consulted` is 0 on every compile (no deciding row reads a key);
     the true arms are OWED to the first row that does.
  G. THE QUERY FAMILY (§4.5 rule 2): every fixture's class agrees with its
     define's and with this file's own reading of the site and the text
     (arm_fixtures --query); the query is pure (the same artifacts with and
     without it); the traced driver's define-time re-ask refuses nothing.
  H. (retired with the pay rule, span_pick 1f: R1 and R2, its only readers,
     were deleted with `mf_finder_pay` and `--pay-grid`; S1025 retired.)
  I. THE CALL MODE IS A STATED FACT (R-23, MF_SITE_ABI 14; S1089): a site with
     `body` UNSTATED is REFUSED at the define (the kit's refusal names `body`),
     never classed as any mode; PARAM (reserved) and a value outside mf_body
     are refused too; ONESHOT is accepted (no refusal, a FIND row decides;
     no row reads `body` since R1 went, span_pick 1f).
     (S919's gate plant reads a state no site reaches since the refusal: it
     is retired, declared UNREACHED.)
     Also (lane n2fix): no PRES shadow decision is declined on `need` (the
     OPTIONAL span on `pre-opt` is on the record, so the control is not blind).
  L. THE SEAM CARRIES A PAYLOAD AND ITS DIGEST, AND NO ROW READS THE DIGEST
     (span_pick.md unit 1g, MF_SITE_ABI 22): memfn.h's mf_akind members are
     exactly {tag, version, present, digest, payload} and mf_analysis's
     {list_v, nkinds, kinds} (an allowlist, comments stripped), its code names
     no mf_prov/MF_PROV_/MF_FID_, and no memfn/src file names `digest`. A
     rate-reading site (pre-lead, pre-lead-run, pre-opt) renders byte-
     identically (plain and traced) under analysis objects with the same rates
     that differ only in `mf_akind.digest`, each shown to REACH the object
     (its render under the reference object differs from the no-object one,
     floor 1 site); set10 and byte1t, which never consult the object, render
     identically with no object and with any digest. prov_check.c is the
     digest's offset as a build-only static assertion.
  J. The retired denies are REFUSED: `--memfn=no-fd-r0` and `no-fd-r5` name
     no row since B4' (withdrawn with R0 and R5), `no-fd-r8` and `no-fd-ndisp`
     none since span_pick 1f (deleted with R8, R1 and R2).
  K. B2's ROUTING (§1.6, R17-b' B2): each of D1, D1c, D1w DECIDES the
     one-byte site it is written for (the kit's report
     `mf_result.row` and the traced `MFTRACE FDROUTE` record, two
     observations) and the text is that row's pick, read here from the text
     by this file's own signature (LIBC: one memchr with the kit's guard;
     LIBC_BACK: the memchr from the floor and the `+ 1` store; WALK: the
     table walk and its post-test; the DFA hat's bounded block and moved
     test); a fixture whose consumer kind is UNSTATED is decided by NO row
     (R7w's contract serves the stated kinds only); `--memfn=no-fd-d1` moves
     the DFA_SCAN byte site to D1w's walk (`fd-d1`'s OFF arm, [rev3 A17]).
  M. B3b's ROUTING (§1.4, §1.6, R17-b' B3b): D2 and slot PRES's P0, P2, P3,
     P4, P9 decide; their three denies are registered (`fd-pres-g1`, `fd-pres-pick`,
     `pres-set-lead`). Each PRES fixture's span is decided by the row and
     carries the link written HERE from §1.4's table (P0 REQUIRED: verified
     whole; P3: the pick verified, a member of a set with a run not verified;
     P4: the leading member verified at the head; P2: every span proven, so
     the site is only ASKED; P9 under the pick's deny), each deny moves its
     fixture's decision, and the define REFUSES parts that are not the links'
     layout (a lead dropped), a presence statement with no proof (the
     start search's `pres_proof` UNSTATED) and a span beginning below the
     match start (`omin` < 0). D2 routes the RUN fixture through the
     composer's walk.
"""
import argparse
import glob
import os
import re
import struct
import subprocess
import sys

passed = failed = 0
unreached = []

# D172 S2 commit 6 (lane wsc5): D2 RETIRED (window_site.md §2.2), id reserved
# D172 S3 (lane s3): RPT, the REPORT row, RETIRED with its R-26.6 preview
# (window_site.md §4), id reserved; code review r1 C1 (lane s3): PAIR, ofsskip's
# fn-pair scope as a FIND-slot row (window_site.md §2.2), read by E-find's stop;
# span_pick.md rev 5.2 unit 1a (lane sp1a): the iterator rows R3a, R3b, R4
# DELETED (zero reach by code), ids reserved; unit 1f (lane sp1f): R8, R1, R2
# DELETED with their denies, the pay rule and mf_finder_pay, ids reserved;
# unit 1e (lane sp1e): D-hors, Table D's row, joined T-FIND FIRST (the one
# walk), its deny `window-skip` unchanged
FIND_ROWS = ["D-hors", "D1", "D1c", "D1w", "PAIR", "R7w"]
# the ids B4' withdrew and 1a/1f deleted (reserved, never reused), and the
# denies that went with them (retired: unknown options)
WITHDRAWN_ROWS = ["R0", "R5", "R7", "R3a", "R3b", "R4", "R8", "R1", "R2"]
RETIRED_DENIES = ["fd-r0", "fd-r5", "fd-r8", "fd-ndisp"]
# a MEASURED row that reads no key: R7w, MEASURED by the walk ruling's real-text
# verdict (walk_vs_v1_record.md §5), not by a set key
KEYLESS_MEASURED = {"R7w"}
PRES_ROWS = ["P0", "P2", "P3", "P4", "P9"]
DERIVED_Q = {"saving", "xover", "block", "dom", "lstar", "g8"}
B1_DENIES = ["fd-d1"]
B3B_DENIES = ["fd-pres-g1", "fd-pres-pick", "pres-set-lead"]
PENDING_DENIES = {}
LATER_FORMS = {"V1": "B4", "W64": "B6", "NONE": "B5", "dispatch-twin": "B4/B8"}
# span_cards.md §3.2 (unit S2c): the form-hash ENTRY TABLE's ids, their
# instances (class -> the class's measure) with the canonical one starred in
# the design (`*`), and the kit row each instance's facts must reach (the
# composer's arm, T-FIND's row on a window's stop, T-CMP's row; settest none).
# `walk-set` folded into `walk` (its site text is the walk's byte for byte).
# The class measure, read here from the SITE TEXT: settest's compare count
# (`==`, `<=`, `>=`), rc-words' word count (`&&` + 1).
FORM_IDS = {
    "walk":      ("pf_walk",   {"-": None}, "-"),
    "libc":      ("pf_memchr", {"-": None}, "-"),
    "pair":      ("PAIR",      {"-": None}, "-"),
    "settest":   ("-",         {"c1": 1, "c2": 2, "cn": 3}, "c2"),
    "rc-words":  ("words",     {"w1": 1, "w2": 2, "w3": 3}, "w2"),
    "rc-memcmp": ("memcmp",    {"l1": None}, "l1"),
}
FORM_INSTANCE_FLOOR = 10
# span_cards.md §2.4 [rev1.2 READY-2; rev1.3 r9-CHECKS-3]: the card guard's
# population, EXACT (kit-grid@1 9, kit-kernels@1 5, kit-synthetic 0, kit-grid@3
# 3): a card added with a kit:form. dep bumps it in the same change
CARD_FORMDEP_COUNT = 17
# span_cards.md §2.4 (S2e): the measure_store pass's population floor, pinned
# at landing as zen4-grid3@1's form-bearing row count (38 rows, 5 `enter`)
STORE_FORMROW_FLOOR = 33
FD_SITES = ["set10", "set2r", "byte1", "run3", "pre-req", "pre-opt",
            "byte1t", "byte1vm", "hat1", "mline"]
# M: fixture -> [(pred, the deciding row(s), the span's link)], from §1.4's
# table (link = v<verify>p<proven_by>m<member>o<order>; member 1 + the
# chosen index, order 0 the head, 1 the run, 2 the rest)
B3B_PRES = {
    "fd-P0":     [("0", "P0", "v1p0m0o0")],
    "fd-P3":     [("0", "P3", "v1p0m1o0")],
    "fd-P9":     [("0", "P9", "v1p0m0o0")],
    "fd-P4":     [("0", "P3+P4", "v1p0m1o0"), ("1", "P3", "v1p0m1o1")],
    "fd-P4-den": [("0", "P3", "v0p0m1o0"), ("1", "P3", "v1p0m1o1")],
    "fd-P2":     [("0", "P2", "v0p1m0o0")],
    "fd-P2-den": [("0", "P3", "v1p0m1o0")],
}
# K: site -> (the deciding row, a text signature regex the row's pick writes)
B2_ROUTES = {
    "byte1t":  ("D1",  r"^    if \(scan_position >= subject_length\) return 0;\|    const void \*q = memchr\(subject \+ scan_position, 120, subject_length - scan_position\);\|    if \(!q\) return 0;\|"),
    "byte1vm": ("D1w", r"^    while \(scan_position < subject_length && !\w+\[subject\[scan_position\]\]\) scan_position\+\+;\|    if \(scan_position >= subject_length\) return 0;\|$"),
    "hat1":    ("D1",  r"^    if \(scan_position \+ 1 < subject_length\) \{\|        size_t skip_from = scan_position;\|        const void \*q = memchr\(subject \+ scan_position, 120, subject_length - 1 - scan_position\);.*\|        if \(scan_position > skip_from\) state = 1;\|    \}\|$"),
    "mline":   ("D1c", r"^    const void \*q = memchr\(subject \+ scan_position, 10, subject_length - scan_position\);\|    if \(!q\) break;\|    scan_position = .*\+ 1;\|$"),
}
QUERY_FLOOR = 39


def ok():
    global passed
    passed += 1


def bad(msg):
    global failed
    failed += 1
    print("FAIL: " + msg)


def run(argv, **kw):
    return subprocess.run(argv, capture_output=True, timeout=120, **kw)


# ---- A ----------------------------------------------------------------------

def listing(fx):
    r = run([fx, "--finder-rows"])
    rows, opts = [], []
    for ln in r.stdout.decode().splitlines():
        if ln.startswith("#") or not ln:
            continue
        c = ln.split("\t")
        if c[0] == "OPTION":
            opts.append(c[1])
        else:
            rows.append(dict(zip(("id", "slot", "needs", "pick", "unpaid", "deny", "basis",
                                  "step", "keys"), c)))
    return rows, opts


def keys_of(row):
    return [] if row["keys"] == "-" else row["keys"].split(";")


def check_table(fx):
    rows, opts = listing(fx)
    find = [r["id"] for r in rows if r["slot"] == "FIND"]
    pres = [r["id"] for r in rows if r["slot"] == "PRES"]
    (ok if find == FIND_ROWS else bad)("FIND rows %s, the design's %s" % (find, FIND_ROWS)) \
        if find != FIND_ROWS else ok()
    if pres != PRES_ROWS:
        bad("PRES rows %s, the design's %s" % (pres, PRES_ROWS))
    else:
        ok()
    if len(rows) != len(FIND_ROWS) + len(PRES_ROWS):
        bad("the table holds %d rows, not the %d of B1" % (len(rows), len(FIND_ROWS) + len(PRES_ROWS)))
    for r in rows:
        ks = keys_of(r)
        if r["basis"] not in ("MEASURED", "DERIVED", "UNMEASURED-DEFAULT"):
            bad("%s: basis %r (C2: mandatory)" % (r["id"], r["basis"]))
            continue
        if r["slot"] == "FIND" and r["pick"] in ("-", ""):
            bad("%s: a FIND row with no pick" % r["id"])
        if r["unpaid"] != "-":
            bad("%s: an unpaid pick %s, but the pay rule retired (span_pick 1f)" % (r["id"], r["unpaid"]))
        if not ks and r["basis"] == "MEASURED" and r["id"] not in KEYLESS_MEASURED:
            bad("%s: MEASURED but reads no key" % r["id"])
        quant = {k.split(".")[1] for k in ks if k.count(".") >= 1}
        if quant & DERIVED_Q and r["basis"] != "DERIVED":
            bad("%s: reads the derived %s but its basis is %s" % (r["id"], sorted(quant & DERIVED_Q), r["basis"]))
        if any(not k.startswith("kit.") for k in ks):
            bad("%s: reads a key that is not the kit's: %s" % (r["id"], ks))
        d = r["deny"]
        if d != "-" and d not in opts and PENDING_DENIES.get(d) != r["step"]:
            bad("%s: deny %s is not in options.def" % (r["id"], d))
        ok()
    for slot, ids in (("FIND", FIND_ROWS), ("PRES", PRES_ROWS)):
        last = [r for r in rows if r["id"] == ids[-1]]
        if not last or keys_of(last[0]):
            bad("the last %s row %s reads a key (§1.5 rule 3: totality)" % (slot, ids[-1]))
        else:
            ok()
    for d in B1_DENIES:
        (ok() if d in opts else bad("options.def lacks B1's deny %s" % d))
    for d in RETIRED_DENIES:
        (ok() if d not in opts else bad("options.def still holds %s (retired with its rows)" % d))
    for rid in WITHDRAWN_ROWS:
        (ok() if rid not in [r["id"] for r in rows] else
         bad("the listing still holds the withdrawn or deleted row %s (its id is reserved)" % rid))
    for d in B3B_DENIES:
        (ok() if d in opts else bad("options.def lacks B3b's deny %s" % d))
    for d, step in PENDING_DENIES.items():
        if d in opts:
            bad("%s is registered before its step %s" % (d, step))
        else:
            unreached.append("deny %s: registered with its rows' routing at %s" % (d, step))
    return rows


# ---- B ----------------------------------------------------------------------

def class_measure(fid, txt):
    if fid == "settest":
        return len(re.findall(r"==|<=|>=", txt))
    if fid == "rc-words":
        return txt.count("&&") + 1
    return None


def check_hash(fx):
    r = run([fx, "--hash"]).stdout.decode().splitlines()
    form = {c[1]: (c[2], c[3]) for c in (ln.split("\t") for ln in r) if c[0] == "FORM"}
    text = {c[1]: c[2] for c in (ln.split("\t") for ln in r) if c[0] == "TEXT"}
    inst = [c[1:] for c in (ln.split("\t") for ln in r) if c[0] == "FORMCLS"]
    for f in FORM_IDS:
        if form.get(f, ("-1",))[0] != "0" or not re.fullmatch(r"[0-9a-f]{16}", form[f][1]):
            bad("mf_form_hash(%s) does not resolve: %s" % (f, form.get(f)))
        else:
            ok()
    # S2c: every instance of the entry table resolves, reaches its row, is
    # the design's class; mf_form_hash(id) is the fold of its instances (G4)
    seen = {}
    texts = {}
    for c in inst:
        if len(c) != 6:
            bad("FORMCLS line %r is not id cls rc hash row canon" % (c,))
            continue
        fid, cls, rc, h, row, canon = c
        want = FORM_IDS.get(fid)
        if not want or cls not in want[1]:
            bad("the entry table holds %s %s, which the design does not name" % (fid, cls))
            continue
        if rc != "0" or not re.fullmatch(r"[0-9a-f]{16}", h):
            bad("instance %s %s does not resolve (rc %s): its facts reach no row, or another" % (fid, cls, rc))
            continue
        seen[(fid, cls)] = h
        (ok() if row == want[0] else
         bad("instance %s %s reached row %s, the design's %s" % (fid, cls, row, want[0])))
        (ok() if (canon == "1") == (cls == want[2]) else
         bad("instance %s %s: canon %s, the design's canonical class is %s" % (fid, cls, canon, want[2])))
        t = run([fx, "--site-text", fid, cls]).stdout.decode()
        texts.setdefault(fid, []).append(t)
        m = want[1][cls]
        if m is not None:
            got = class_measure(fid, t)
            (ok() if (got == m if m < 3 else got >= m) else
             bad("instance %s %s: its text's class measure is %d, the class's %s%d"
                 % (fid, cls, got, "" if m < 3 else ">= ", m)))
    want_all = {(f, c) for f, v in FORM_IDS.items() for c in v[1]}
    for k in sorted(want_all - set(seen)):
        bad("the design's instance %s %s has no resolving FORMCLS line" % k)
    (ok() if len(seen) >= FORM_INSTANCE_FLOOR else
     bad("%d form instances resolve, under the floor %d" % (len(seen), FORM_INSTANCE_FLOOR)))
    # pairwise distinct: two ids (or two classes) hashing one text is one
    # form under two names (sabotage (m))
    byh = {}
    for k, h in seen.items():
        byh.setdefault(h, []).append(k)
    dup = [v for v in byh.values() if len(v) > 1]
    (ok() if not dup else
     bad("form instances hash one text: %s" % "; ".join(" = ".join("%s %s" % k for k in v) for v in dup)))
    # G4 FOLD: mf_form_hash(id) is ONE hash over every instance's site text,
    # in table order (FORMCLS order), a newline between two; folded here from
    # the texts, never by formhash.c's loop (sabotage S2933)
    for f in FORM_IDS:
        fold = run([fx, "--hash-text", "-"], input="\n".join(texts.get(f, [])).encode()).stdout.decode().strip()
        (ok() if texts.get(f) and form.get(f, ("", ""))[1] == fold else
         bad("mf_form_hash(%s) %s is not the fold of its %d instances' site texts %s"
             % (f, form.get(f), len(texts.get(f, [])), fold)))
    # R-MS3's fixtures per INSTANCE (CHECKS-4, CHECKS-6, G4)
    for (f, c), h in sorted(seen.items()):
        k = "%s/%s" % (f, c)
        rn, nr = text.get(k + ".rename"), text.get(k + ".renamed", "0")
        ed, fe = text.get(k + ".edit"), text.get(k + ".foldedit")
        (ok() if nr.isdigit() and int(nr) > 0 else
         bad("the rename of %s's site text renamed nothing (%s): 'rename keeps the hash' would hold vacuously" % (k, nr)))
        (ok() if rn and rn == h else
         bad("the rename of %s's site text moved its hash (%s vs %s)" % (k, rn, h)))
        (ok() if ed and ed != "-" and ed != h else
         bad("the one-instruction edit of %s's site text left its hash (or found no edit site): %s" % (k, ed)))
        (ok() if fe and fe != "-" and fe != form.get(f, ("", ""))[1] else
         bad("an edit of instance %s alone left mf_form_hash(%s) %s (the fold must cover it): %s"
             % (k, f, form.get(f), fe)))
    for f, step in LATER_FORMS.items():
        if form.get(f, ("0",))[0] != "-1":
            bad("mf_form_hash(%s) resolves before its step %s" % (f, step))
        else:
            ok()
            unreached.append("R-MS3: form %s hashes from %s" % (f, step))
    for v in ("rename", "comment", "layout"):
        (ok() if text.get(v) == text.get("base") else
         bad("the %s variant moved the text hash (%s vs %s)" % (v, text.get(v), text.get("base"))))
    for v in ("edit", "edit2"):
        (ok() if text.get(v) and text.get(v) != text.get("base") else
         bad("the one-operator edit %s left the text hash" % v))
    (ok() if form.get("walk", ("", ""))[1] == text.get("base") else
     bad("the walk form's hash is not its canonical text's (%s vs %s)"
         % (form.get("walk"), text.get("base"))))
    return form


# ---- C ----------------------------------------------------------------------

def read_sections(path):
    secs, cur, head = {}, None, None
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            cur = ln.split()[1]
            secs[cur] = {"head": None, "rows": []}
            continue
        if ln.startswith("#"):
            if cur:
                secs[cur]["head"] = ln[1:].split("\t")
            continue
        if cur and ln:
            secs[cur]["rows"].append(dict(zip(secs[cur]["head"], ln.split("\t"))))
    return secs


def read_cards(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("#") or not ln:
            continue
        out.append(ln)
    return out


# docs/spec/measures.md §3.1's code table and §3.3's digest, written here from
# the spec (not from memfn/data/sets/generate.py, whose digest was once a
# first-letter FNV with a mistyped offset basis and passed its own twin).
UNIT_CODE = {"ratio": 1, "walkbytes": 2, "bytes": 3, "count": 4}
STATUS_CODE = {"measured": 1, "fitted": 2, "derived": 3, "null": 4}


def digest(rows):
    h = 0xcbf29ce484222325
    def feed(b):
        nonlocal h
        for c in b:
            h ^= c
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    feed(b"pcrec-meas-1\0")
    for r in sorted(rows, key=lambda r: r["key"].encode()):
        feed(r["key"].encode() + b"\0")
        feed(bytes([UNIT_CODE[r["unit"]], STATUS_CODE[r["status"]]]))
        feed(struct.pack("<q", int(r["value_e6"])))
    return "%016x" % h


def check_sets(root, form):
    g = run([sys.executable, "-I", os.path.join(root, "memfn/data/sets/generate.py"), "--check"])
    (ok() if g.returncode == 0 else bad("generate.py --check: " + g.stdout.decode().strip()))
    cards = {}
    # every card table in the directory, by listing (a hand list drifts: a
    # table added later would be read by no check), floored (K35)
    cdir = os.path.join(root, "memfn/data/cards")
    names = sorted(f[:-4] for f in os.listdir(cdir) if f.endswith(".tsv"))
    (ok() if len(names) >= 3 else bad("memfn/data/cards holds %d card tables, under 3" % len(names)))
    formdep = 0
    resolves = {f for f, (rc, _h) in form.items() if rc == "0"}
    for name in names:
        cl = read_cards(os.path.join(cdir, name + ".tsv"))
        cards[name] = cl
        for c in cl:
            f = c.split("\t")
            (ok() if len(f) == 13 and f[0] == "kit" and f[4] in UNIT_CODE else
             bad("%s.tsv: card row is not 13 kit columns with a §3.1 unit: %r" % (name, c)))
            # span_cards.md §2.4 (S2c): a card whose deps name a form hash
            # keys its rows by the form, FIRST (the key's `form` token IS
            # the dep's id), over every table and every ver
            if len(f) == 13 and "kit:form." in f[12]:
                formdep += 1
                (ok() if f[3].split(";")[0] == "form" else
                 bad("%s.tsv: card %s@%s names a kit:form. dep but its first dim is %r, not form"
                     % (name, f[1], f[2], f[3].split(";")[0])))
                # every named (non-template) form id resolves to a hash
                for d in f[12].split(";"):
                    if d.startswith("kit:form.") and not d.startswith("kit:form.<"):
                        (ok() if d[len("kit:form."):] in resolves else
                         bad("%s.tsv: card %s@%s names dep %s, which resolves to no form hash"
                             % (name, f[1], f[2], d)))
    print("check C: %d cards with a kit:form. dep" % formdep)
    (ok() if formdep == CARD_FORMDEP_COUNT else
     bad("%d cards with a kit:form. dep, the pinned count is %d (a card added or removed: re-pin)"
         % (formdep, CARD_FORMDEP_COUNT)))
    sdir = os.path.join(root, "memfn/data/sets")
    later = set()
    nsets = 0
    for fn in sorted(os.listdir(sdir)):
        if not fn.endswith(".tsv"):
            continue
        nsets += 1
        s = read_sections(os.path.join(sdir, fn))
        hdr = {r["key"]: r.get("value", "") for r in s["header"]["rows"]}
        method = hdr.get("method", "")
        table = method.split("@")[0]
        if table not in cards:
            bad("%s: method %s names no card table" % (fn, method))
            continue
        crow = [dict(zip(("owner", "quantity", "ver", "dims"), c.split("\t")[:4])) for c in cards[table]]
        ver = method.split("@")[1]
        on = {c["quantity"]: c for c in crow if c["ver"] == ver}
        secc = ["\t".join(r[h] for h in s["cards"]["head"]) for r in s["cards"]["rows"]]
        mine = [c for c in cards[table] if c.split("\t")[2] == ver]
        (ok() if secc == mine else bad("%s: its cards section is not %s.tsv" % (fn, table)))
        rows = s["rows"]["rows"]
        bogus = sorted({r["unit"] for r in rows if r["unit"] not in UNIT_CODE} |
                       {r["status"] for r in rows if r["status"] not in STATUS_CODE})
        if bogus:
            bad("%s: unit/status outside measures.md §3.1's code table: %s" % (fn, ",".join(bogus)))
            continue
        (ok() if hdr.get("rows") == str(len(rows)) else
         bad("%s: header rows %s, section %d" % (fn, hdr.get("rows"), len(rows))))
        (ok() if hdr.get("values_digest") == digest(rows) else
         bad("%s: values_digest %s, recomputed %s" % (fn, hdr.get("values_digest"), digest(rows))))
        # two more routes: the knowledge suite's spec-only reader, and pcrec's own loader
        # (which refuses a digest, a unit row, a unit or a status the spec does not hold)
        kr = run([sys.executable, "-I", os.path.join(root, "tests/knowledge/ks_ref.py"), "digest",
                  os.path.join(sdir, fn)])
        (ok() if kr.returncode == 0 and kr.stdout.decode().strip() == hdr.get("values_digest") else
         bad("%s: ks_ref.py digest %r, header %s" % (fn, kr.stdout.decode().strip(),
                                                    hdr.get("values_digest"))))
        ld = run([os.path.join(root, "build", "pcrec"), "--list-measurements=" + os.path.join(sdir, fn)])
        (ok() if ld.returncode == 0 else
         bad("%s: pcrec --list-measurements refuses it: %s" % (fn, ld.stdout.decode().strip()[:200])))
        for r in rows:
            parts = r["key"].split(".")
            q = parts[1] if len(parts) > 1 else ""
            c = on.get(q)
            if parts[0] != "kit" or not c:
                bad("%s: row %s is off its card (no %s card at %s)" % (fn, r["key"], q, method))
                continue
            dims = 0 if c["dims"] == "-" else len(c["dims"].split(";"))
            if len(parts) - 2 != dims:
                bad("%s: row %s has %d tokens, its card's dims %s" % (fn, r["key"], len(parts) - 2, c["dims"]))
                continue
            if table == "kit-grid" and c["dims"].split(";")[0] == "form":
                f = parts[2]
                fid = "walk" if f == "WALK" else f
                if form.get(fid, ("-1",))[0] != "0":
                    later.add(fid)
            ok()
    (ok() if nsets >= 5 else bad("memfn/data/sets holds %d sets, under 5" % nsets))
    for f in sorted(later):
        unreached.append("R-MS5/R-MS3: the interim set's form %s resolves from %s (card dep "
                         "kit:form.%s)" % (f, {"V1": "B4", "S1": "B6", "A1": "B6", "W64": "B6"}.get(f, "?"), f))


def check_store(root, form):
    cdir = os.path.join(root, "memfn/data/cards")
    resolves = {f: h for f, (rc, h) in form.items() if rc == "0"}
    nform = nstale = nsets = 0
    later = set()
    for path in sorted(glob.glob(os.path.join(root, "measure_store", "*", "*", "set.tsv"))):
        name = "%s@%s" % tuple(path.split(os.sep)[-3:-1])
        s = read_sections(path)
        hdr = {r["key"]: r.get("value", "") for r in s["header"]["rows"]}
        method = hdr.get("method", "")
        table, _, ver = method.partition("@")
        if table != "kit-grid":
            continue
        nsets += 1
        f2 = hdr.get("format") == "2"
        mine = [c for c in read_cards(os.path.join(cdir, table + ".tsv")) if c.split("\t")[2] == ver]
        secc = ["\t".join(r[h] for h in s["cards"]["head"]) for r in s["cards"]["rows"]]
        # the canonical writer orders cards bytewise (measures.md §6¶2): compared as sets of rows
        (ok() if sorted(secc) == sorted(mine) else
         bad("store %s: its cards section is not %s.tsv's ver %s" % (name, table, ver)))
        on = {c.split("\t")[1]: c.split("\t") for c in mine}
        for r in s["rows"]["rows"]:
            parts = r["key"].split(".")
            c = on.get(parts[1] if len(parts) > 1 else "")
            if parts[0] != "kit" or not c:
                bad("store %s: row %s is off its card (no such card at %s)" % (name, r["key"], method))
                continue
            dims = c[3].split(";")
            if dims[0] != "form":
                (ok() if r.get("deps") in ("-", None) or not f2 else
                 bad("store %s: row %s has no form dim but records deps %r" % (name, r["key"], r.get("deps"))))
                continue
            fid = "walk" if parts[2] == "WALK" else parts[2]
            if not f2:
                if fid not in resolves:
                    later.add((name, fid))
                continue
            if fid not in resolves:
                bad("store %s: row %s's form %s resolves to no form hash (red, never later)" % (name, r["key"], fid))
                continue
            dep = [d for d in r.get("deps", "-").split(";") if d.startswith("kit:form.")]
            m = re.fullmatch(r"kit:form\.([A-Za-z0-9_-]+)=([0-9a-f]{16})", dep[0]) if len(dep) == 1 else None
            if not m or m.group(1) != fid:
                bad("store %s: row %s records deps %r, not one kit:form.%s=<16 hex>" % (name, r["key"], r.get("deps"), fid))
                continue
            ok()
            nform += 1
            if m.group(2) != resolves[fid]:
                nstale += 1
                print("check C: STALE %s %s recorded %s, today %s" % (name, r["key"], m.group(2), resolves[fid]))
    for name, fid in sorted(later):
        unreached.append("measure_store %s: form %s resolves later (a format-1 set; its `-` deps NOTED)" % (name, fid))
    print("check C: measure_store pass: %d kit-grid set(s), %d format-2 form-bearing rows checked, %d stale"
          % (nsets, nform, nstale))
    (ok() if nform >= STORE_FORMROW_FLOOR else
     bad("measure_store pass: %d form-bearing rows, under the floor %d (K35)" % (nform, STORE_FORMROW_FLOOR)))


# ---- D, E, F, I, J ----------------------------------------------------------

def fd_run(fx, site, setpath=None, opts=None):
    argv = [fx, "--fd-site", site]
    if setpath:
        argv += ["--fd-set", setpath]
    if opts:
        argv += ["--opts", opts]
    r = run(argv)
    out, err = r.stdout.decode(), r.stderr.decode()
    dec = []
    for ln in err.splitlines():
        if ln.startswith("MFTRACE FD "):                 # slot PRES (the define's and the ask's)
            dec.append(dict(t.split("=", 1) for t in ln.split()[2:] if "=" in t))
        elif ln.startswith("MFTRACE FDROUTE "):          # slot FIND (the routed decision)
            d = dict(t.split("=", 1) for t in ln.split()[2:] if "=" in t)
            d["slot"] = "FIND"
            dec.append(d)
    cons = re.search(r"^CONSULTED\t(\d+)", out, re.M)
    ref = re.search(r"^REFUSED\t(.*)$", out, re.M)
    return r.returncode, dec, [], (int(cons.group(1)) if cons else None), \
        (ref.group(1) if ref else None), err


def decisions(dec):
    return [(d.get("slot"), d.get("pred", "-"), d.get("layer"), d.get("row")) for d in dec]


def check_sites(root, fx, fxt, tmp, rows):
    full = os.path.join(root, "memfn/data/sets/synthetic-every-key.tsv")
    nsite = 0
    # sites a FIND/PRES decision exists for (consumer kind stated or a presence
    # span); a fixture whose kind is UNSTATED is decided by no FIND row
    for site in FD_SITES:
        rc0, dec0, _, cons0, ref0, err0 = fd_run(fxt, site)
        rc1, dec1, _, cons1, ref1, err1 = fd_run(fxt, site, full)
        if rc0 or rc1 or ref0 or ref1:
            bad("%s: the kit refused (no set rc %d %s; full set rc %d %s)" % (site, rc0, ref0, rc1, ref1))
            continue
        nsite += 1
        # D: a decision does not depend on the set (no deciding row reads a key)
        (ok() if decisions(dec0) == decisions(dec1) else
         bad("%s: the full set moved the decision (%s -> %s)" % (site, decisions(dec0), decisions(dec1))))
        # no gate decision is declined on `need` (a row's contract refusing the
        # span it was the first to hold on: P0 held an OPTIONAL span its
        # REQUIRED-only contract refused, 1439 would-declines in B1/B2's N2
        # census, lane n2fix). Not on every field: these fixtures leave
        # site_kind UNSTATED, so a FIND decision may decline on that, as its own
        # (stated-kind) compiles do not.
        wd = [ln for ln in err0.splitlines()
              if ln.startswith("MFTRACE END table=fd ") and
              (" phase=shadow " in ln or " phase=define " in ln)
              and " would_decline=1 " in ln and "need:" in ln]
        (ok() if not wd else bad("%s: the gate declined on need (%s)" % (site, wd[0])))
        if site == "pre-opt":                   # K35: the OPTIONAL presence span is on the record
            opt = [d for d in dec0 if d.get("slot") == "PRES" and d.get("need") == "OPTIONAL"]
            (ok() if opt else bad("pre-opt: no OPTIONAL PRES decision, the would-decline control is blind"))
        # F: no deciding row reads a set key
        for c, what in ((cons0, "no set"), (cons1, "the full set")):
            (ok() if c == 0 else bad("%s: consulted %s under %s (no deciding row reads a key)"
                                       % (site, c, what)))
    (ok() if nsite == len(FD_SITES) else bad("%d of %d finder sites ran" % (nsite, len(FD_SITES))))
    # refusals: a pcrec. row; a value past the bound
    for name, body in (("pcrec-row", "pcrec.beta.WALK.DFA_SCAN.r1e0c0\tratio\t1000000\t-\t-\t-\tmeasured"),
                       ("too-big", "kit.eps.streamed.slope\tratio\t2000000000000000000\t-\t-\t-\tmeasured")):
        path = os.path.join(tmp, name + ".tsv")
        with open(path, "w") as fh:
            fh.write("#section header\n#key\tvalue\nid\t%s\n#section rows\n"
                     "#key\tunit\tvalue_e6\tabs_ns_e6\tnoise_e6\tn\tstatus\n%s\n" % (name, body))
        rc, _, _, _, ref, _ = fd_run(fx, "set10", path)
        (ok() if ref and "refused" in ref else bad("a set with a %s row was not refused (rc %d)" % (name, rc)))
    # plain build: consulted 0 under the full set too
    rc, _, _, cons, ref, _ = fd_run(fx, "set10", full)
    (ok() if rc == 0 and cons == 0 else bad("plain build: consulted %s (rc %d %s)" % (cons, rc, ref)))
    unreached.append("R-MS2: consulted's true arms (an ABSENT and a present key read by a deciding "
                     "row) have no reader since B4' withdrew R0, R5 and R7 (S917 is UNREACHED); "
                     "the first row with a key comparator ([MEMFN-REGIME], B6) re-opens them")
    # I: the call mode is a stated fact (R-23): every body value is stated
    # once; the three that are not a mode are refused naming `body`
    for site, want in (("set10-nobody", "`body` UNSTATED"),
                       ("set10-param", "`body` PARAM is reserved"),
                       ("set10-bodyoor", "`body` outside mf_body")):
        rc, dec, _, _, ref, _ = fd_run(fxt, site, full)
        (ok() if ref and want in ref and not dec else
         bad("%s: the kit did not refuse a bad call mode naming %s (rc %d, refusal %s, %d "
             "decisions)" % (site, want, rc, ref, len(dec))))
    # ONESHOT is accepted: no refusal, the FIND rows are asked, and no gate
    # record names `body` (no row reads it since R1, R2 and R8 went: span_pick 1f)
    _, _, _, _, ref_b, err_b = fd_run(fxt, "set10", full)
    g_b = [ln for ln in err_b.splitlines() if "table=fd" in ln and "verdict=" in ln]
    (ok() if not ref_b and g_b and not any("body:" in ln for ln in g_b) else
     bad("body ONESHOT: refused (%s), no fd gate record (%d) or one names `body`: %s"
         % (ref_b, len(g_b), [ln for ln in g_b if "body:" in ln][:1])))
    # J: the retired denies name no row (withdrawn with R0 and R5 at B4',
    # deleted with R8, R1 and R2 at span_pick 1f)
    for d in RETIRED_DENIES + ["fd-r7"]:
        r = run([os.path.join(root, "build", "pcrec"), "-p", "rx", "--pattern", "a(b|c)+d",
                 "--memfn=no-" + d, "-o", os.path.join(tmp, "retired.c")])
        (ok() if r.returncode != 0 and b"unknown option" in r.stderr else
         bad("--memfn=no-%s was not refused as an unknown option (rc %d): the deny is retired"
             % (d, r.returncode)))


# ---- K ----------------------------------------------------------------------

def fd_routed(fx, site, opts=None):
    argv = [fx, "--fd-site", site] + (["--opts", opts] if opts else [])
    r = run(argv)
    out, err = r.stdout.decode(), r.stderr.decode()
    rt = re.search(r"^ROUTED\t(.*)$", out, re.M)
    tx = re.search(r"^TEXT\t(.*)$", out, re.M)
    fr = [dict(t.split("=", 1) for t in ln.split()[2:] if "=" in t)
          for ln in err.splitlines() if ln.startswith("MFTRACE FDROUTE ")]
    return r.returncode, (rt.group(1) if rt else None), (tx.group(1) if tx else ""), fr


def check_routing(fx, fxt):
    n = 0
    for site, (row, sig) in B2_ROUTES.items():
        rc, rt, text, _ = fd_routed(fx, site)
        _, rtt, _, fr = fd_routed(fxt, site)
        if rc or rt != row or rtt != row or [d.get("row") for d in fr] != [row]:
            bad("%s: decided by %s (traced %s, FDROUTE %s), the design's routed row is %s"
                % (site, rt, rtt, [d.get("row") for d in fr], row))
            continue
        (ok() if re.search(sig, text) else
         bad("%s: row %s's text is not its pick's: %s" % (site, row, text)))
        n += 1
    (ok() if n == len(B2_ROUTES) else bad("%d of %d routed sites checked" % (n, len(B2_ROUTES))))
    for site in ("set10", "set2r", "byte1"):
        _, rt, _, _ = fd_routed(fx, site)
        _, _, _, fr = fd_routed(fxt, site)
        (ok() if rt == "-" and not fr else
         bad("%s: decided by row %s (FDROUTE %s): a fixture with no stated consumer kind "
             "is decided by no row" % (site, rt, [d.get("row") for d in fr])))
    _, rt, text, _ = fd_routed(fx, "byte1t", "no-fd-d1")
    (ok() if rt == "D1w" and re.search(B2_ROUTES["byte1vm"][1], text) else
     bad("--memfn=no-fd-d1: byte1t decided by %s with %r, not D1w's walk ([rev3 A17])"
         % (rt, text)))


# ---- M ----------------------------------------------------------------------

def pres_records(err):
    return [dict(t.split("=", 1) for t in ln.split()[2:] if "=" in t)
            for ln in err.splitlines() if ln.startswith("MFTRACE FD ") and " slot=PRES " in ln]


def check_pres_routing(fx, fxt, tmp):
    n = 0
    for name, want in sorted(B3B_PRES.items()):
        d = os.path.join(tmp, "m_" + name)
        os.makedirs(d, exist_ok=True)
        r = run([fxt, d, "--only", name])
        recs = pres_records(r.stderr.decode())
        got = [(x.get("pred"), x.get("row"), x.get("link")) for x in recs]
        if r.returncode or got != want:
            bad("%s: PRES decided %s (rc %d), the design's %s" % (name, got, r.returncode, want))
            continue
        n += 1
        ok()
        # the plain kit agrees (an asked site prints its links)
        rp = run([fx, d, "--only", name])
        links = re.findall(r"^LINK\t(\d+)\t(\S+)$", rp.stdout.decode(), re.M)
        if links:
            (ok() if [(p, l) for p, l in links] == [(p, l) for p, _, l in want] else
             bad("%s: the plain kit's asked links %s, the traced %s" % (name, links, want)))
    (ok() if n == len(B3B_PRES) else bad("%d of %d PRES fixtures decided as designed" % (n, len(B3B_PRES))))
    # the define holds the parts to the links' layout: a lead dropped is refused
    _, _, _, _, ref, _ = fd_run(fx, "pre-lead-run")
    (ok() if ref and "layout" in ref else
     bad("pre-lead-run (P4 leads, its part dropped) was not refused naming the layout: %s" % ref))
    _, _, _, _, ref, _ = fd_run(fx, "pre-lead-run", None, "no-pres-set-lead")
    (ok() if not ref else bad("pre-lead-run under no-pres-set-lead was refused: %s" % ref))
    _, _, _, _, ref, _ = fd_run(fx, "pre-noproof")
    (ok() if ref and "pres_proof" in ref else
     bad("a presence statement with no proof was not refused naming `pres_proof`: %s" % ref))
    # a presence span may not begin below the match start (C-1: omin >= 0,
    # KW-10's re-asked ranges): refused, never read as a wider window
    _, _, _, _, ref, _ = fd_run(fx, "pre-omin")
    (ok() if ref and "omin" in ref else
     bad("a presence span with omin < 0 was not refused naming `omin`: %s" % ref))
    # D2 RETIRED (D172 S2 commit 6): the RUN fixture is decided by no routed
    # row and renders the composer's own walk, as D2's pick did
    rc, rt, _, fr = fd_routed(fx, "run3")
    _, rtt, _, frt = fd_routed(fxt, "run3")
    (ok() if not rc and rt == "-" and rtt == "-" and not frt else
     bad("run3: decided by %s (traced %s, FDROUTE %s), no row routes a RUN span 0 since D2 "
         "retired" % (rt, rtt, [x.get("row") for x in frt])))


# ---- G ----------------------------------------------------------------------

def check_query(fx, fxt, tmp):
    d1, d2, d3 = (os.path.join(tmp, x) for x in ("q_plain", "q_query", "q_trace"))
    for d in (d1, d2, d3):
        os.makedirs(d, exist_ok=True)
    r1 = run([fx, d1])
    r2 = run([fx, d2, "--query"])
    r3 = run([fxt, d3, "--query"])
    if r1.returncode or r2.returncode or r3.returncode:
        bad("the fixture driver failed (plain %d, --query %d, traced %d): %s"
            % (r1.returncode, r2.returncode, r3.returncode, r3.stderr.decode()[-300:]))
        return
    lines = [ln.split("\t") for ln in r2.stderr.decode().splitlines() if ln.startswith("QUERY\t")]
    (ok() if len(lines) >= QUERY_FLOOR else bad("--query asked %d fixtures, under %d" % (len(lines), QUERY_FLOOR)))
    for c in lines:
        (ok() if c[2] == "agree" else bad("query family: fixture %s: %s" % (c[1], c[2])))
    same = run(["diff", "-r", d1, d2]).returncode == 0
    (ok() if same else bad("the query is not pure: --query moved a fixture's text"))
    tl = [ln.split("\t") for ln in r3.stderr.decode().splitlines() if ln.startswith("QUERY\t")]
    (ok() if len(tl) == len(lines) and all(c[2] == "agree" for c in tl) else
     bad("the traced driver's query family disagrees (%d lines)" % len(tl)))
    asks = sum(1 for ln in r3.stderr.decode().splitlines() if ln.startswith("MFTRACE ASK "))
    (ok() if asks >= QUERY_FLOOR else bad("the traced driver wrote %d ASK records" % asks))


# ---- L ----------------------------------------------------------------------

# span_pick.md unit 1g (MF_SITE_ABI 22): the analysis object's members, an
# ALLOWLIST written HERE from the design (the header is held against it): a
# new member is a seam event that must edit this table.
SEAM_MEMBERS = {
    "mf_akind": {"tag", "version", "present", "digest", "payload"},
    "mf_analysis": {"list_v", "nkinds", "kinds"},
}
# spellings the seam retired (header code must not name them; comments may)
RETIRED_SEAM_RE = re.compile(r"\b(mf_prov\w*|MF_PROV_\w+|MF_FID_\w+)\b")
# the digests the render loop hands: the reference first, then one odd, one
# even, and the extremes (span_pick R22: rates fixed, only the digest varies)
AN_DIGESTS = ("0", "1", "2", "0x1234", "0xffffffffffffffff")
# the sites the object is read on: kit_byte_rate's callers (the PRES picks)
RATE_SITES = ("pre-lead", "pre-lead-run", "pre-opt")
# FIND sites that never consult the object: identical with or without one
PLAIN_SITES = ("set10", "byte1t")
RATE_SITES_FLOOR = 1


def strip_c_comments(text):
    return re.sub(r"/\*.*?\*/|//[^\n]*", " ", text, flags=re.S)


def seam_members(code, name):
    m = re.search(r"typedef\s+struct\s*\w*\s*\{([^{}]*)\}\s*%s\s*;" % name, code)
    return None if not m else set(re.findall(r"(\w+)\s*;", m.group(1)))


def check_seam(root, fx, fxt):
    """span_pick unit 1g (MF_SITE_ABI 22): the kit is handed a payload and its
    digest, and no kit row reads the digest. Statically: memfn.h's analysis
    structs hold exactly SEAM_MEMBERS (comments stripped), its code names no
    retired spelling, and no memfn/src file names `digest`. Dynamically
    (stdout, rc and the traced shadow's stderr): the rate-reading sites render
    byte-identically under analysis objects that differ only in
    `mf_akind.digest`, with the rates fixed; each such site's REACH is shown
    (its render under the reference object differs from its render under no
    object, floor RATE_SITES_FLOOR sites), and the sites that never consult
    the object render identically with no object and with any."""
    code = strip_c_comments(open(os.path.join(root, "memfn/include/memfn.h"),
                                 errors="replace").read())
    for name, want in SEAM_MEMBERS.items():
        got = seam_members(code, name)
        if got is None:
            bad("L: memfn.h declares no `typedef struct ... { ... } %s;` (the object moved)" % name)
        else:
            (ok() if got == want else
             bad("L: %s members %s, want exactly %s (a seam event must edit this check)"
                 % (name, sorted(got), sorted(want))))
    hits = sorted(set(RETIRED_SEAM_RE.findall(code)))
    (ok() if not hits else bad("L: memfn.h's code names retired provenance: %s" % hits[:5]))
    src = os.path.join(root, "memfn/src")
    named = sorted(f for f in os.listdir(src) if f.endswith((".c", ".h")) and
                   re.search(r"digest", strip_c_comments(
                       open(os.path.join(src, f), errors="replace").read())))
    (ok() if not named else bad("L: kit sources name `digest` (a kit row reads it): %s" % named))
    for prog, name in ((fx, "plain"), (fxt, "traced")):
        reached = 0
        for site in RATE_SITES:
            none = run([prog, "--fd-site", site])
            ref = run([prog, "--fd-site", site, "--fd-an", AN_DIGESTS[0]])
            if ref.returncode > 1 or none.returncode > 1:
                bad("L: %s kit: site %s failed to render (rc %d, %d)"
                    % (name, site, none.returncode, ref.returncode))
                continue
            if (none.returncode, none.stdout, none.stderr) != (ref.returncode, ref.stdout, ref.stderr):
                reached += 1
            for dg in AN_DIGESTS[1:]:
                got = run([prog, "--fd-site", site, "--fd-an", dg])
                if (got.returncode, got.stdout, got.stderr) != (ref.returncode, ref.stdout, ref.stderr):
                    bad("L: %s kit: site %s renders differently with mf_akind.digest %s "
                        "(a kit row reads the digest)" % (name, site, dg))
                else:
                    ok()
        (ok() if reached >= RATE_SITES_FLOOR else
         bad("L: %s kit: %d of %s render differently under an analysis object than under "
             "none (floor %d): the digest loop reaches no reader"
             % (name, reached, RATE_SITES, RATE_SITES_FLOOR)))
        for site in PLAIN_SITES:
            none = run([prog, "--fd-site", site])
            if none.returncode or b"TEXT" not in none.stdout:
                bad("L: %s kit: site %s rendered nothing under no analysis (rc %d)"
                    % (name, site, none.returncode))
                continue
            for dg in AN_DIGESTS:
                got = run([prog, "--fd-site", site, "--fd-an", dg])
                if (got.returncode, got.stdout, got.stderr) != (none.returncode, none.stdout, none.stderr):
                    bad("L: %s kit: site %s renders differently with an analysis object "
                        "(digest %s) than with none (a kit row reads the object's "
                        "provenance or digest)" % (name, site, dg))
                else:
                    ok()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--fx", required=True)
    ap.add_argument("--fxt", required=True)
    ap.add_argument("--tmp", required=True)
    a = ap.parse_args()
    rows = check_table(a.fx)
    form = check_hash(a.fx)
    check_sets(a.root, form)
    check_store(a.root, form)
    check_sites(a.root, a.fx, a.fxt, a.tmp, rows)
    check_query(a.fx, a.fxt, a.tmp)
    check_routing(a.fx, a.fxt)
    check_pres_routing(a.fx, a.fxt, a.tmp)
    check_seam(a.root, a.fx, a.fxt)
    for u in unreached:
        print("UNREACHED: " + u)
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
