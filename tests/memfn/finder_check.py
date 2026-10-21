#!/usr/bin/env python3
"""tests/memfn/finder_check.py -- R17-b' B1's checks on the kit's finder table
and its B1 entries (lane fdb1; docs/design/memfn/r17b_prime.md rev 3 §1, §2.5,
§4.5, §4.7; requests R-19, R-20 R-MS1..R-MS5). Run by run_finder.sh (`make
test-memfn-finder`); prints `checks passed:` / `checks failed:` and the
UNREACHED/OWED items it cannot check yet (never as a pass).

    finder_check.py --root TREE --fx PLAIN_FX --fxt TRACED_FX --tmp DIR

Two fixture drivers (tests/memfn/arm_fixtures.c): PLAIN_FX linked against
build/libpcrec.a, TRACED_FX against the kit rebuilt -DMF_TRACE (the finder
shadow's `MFTRACE FD`/`FDKEY` records and the define-time query's re-ask).

WHAT IT CONTROLS, AND AGAINST WHAT (each expectation is written HERE, from the
design's text, sharing no code with the kit):

  A. THE TABLE (C2's self-check, [rev3 C2]; the listing, R-MS4): the 19 rows
     the design locks at B4 less B5's (§1.3, §1.4), by slot and in order; a
     basis on every row; a pick on every FIND row; no MEASURED row that reads
     no key; every row reading a DERIVED key (the converter's closed list,
     §5.2 C1: saving, xover, block, dom, lstar, g8) is DERIVED; the last row
     of each slot reads nothing; no routed row at B1 (§1.6); every key the
     kit's (no `pcrec.` key, R-MS1); every deny registered in options.def or
     one of B3b's three. SN-4 (S1020) plants an UNSTATED basis.
  B. R-MS3: `walk` and `libc` hash, the forms later steps build are refused;
     the text hash ignores a rename, a comment and layout and moves on a
     one-operator edit; the walk form's hash IS its canonical text's.
  C. R-MS5 and the sets: memfn/data/sets/generate.py --check; every row of
     every set on its method's card (quantity present, arity = dims), the
     set's `cards` section equal to its card table, `rows` and
     `values_digest` (measure_sets §1.6, recomputed here) as its header
     says; each card dep form resolves or is OWED with its step.
  D. R-MS1: every finder site under NO set, the FULL synthetic set, and the
     full set less each key it reads in turn (a decision that read a removed
     key must move: S917's detector); a `pcrec.` row and an out-of-bound
     value are refused (no clamp).
  E. R-MS4 keys: every key the shadow looked up under the full set matches a
     template its row declares.
  F. R-MS2: `consulted` is 0 on every compile at B1, the traced shadow's
     reads included (no routed row reads a key before B4); the true arms are
     OWED to B4.
  G. THE QUERY FAMILY (§4.5 rule 2): every fixture's class agrees with its
     define's and with this file's own reading of the site and the text
     (arm_fixtures --query); the query is pure (the same artifacts with and
     without it); the traced driver's define-time re-ask refuses nothing.
  H. THE PAY RULE'S ARITHMETIC GRID (§2.5 [D9]; SN-9, S1025): T1/T2/T3 over a
     grid of operands at, below and above every boundary, the expected bits
     computed here; at least PAY_TIE_FLOOR ties.
  I. THE CALL MODE IS A STATED FACT (R-23, MF_SITE_ABI 14; S1089): a site with
     `body` UNSTATED is REFUSED at the define (the kit's refusal names `body`),
     never classed as any mode; PARAM (reserved) and a value outside mf_body
     are refused too; ONESHOT is accepted and R1's gate does not name `body`.
     (S919's gate plant reads a state no site reaches since the refusal: it
     is retired, declared UNREACHED.)
     Also (lane n2fix): no PRES shadow decision is declined on `need` (the
     OPTIONAL span on `pre-opt` is on the record, so the control is not blind).
  L. PROVENANCE `bytes` AND `fidelity` (R-24, MF_SITE_ABI 15; S1092): pcrec's
     stanza mapping states each token of the findings vocabulary (read off
     `pcrec --list-schema`) as its own enumerator (verbatim 1, adapted 2,
     synthesized 3, from window_contract.md §3.1), a block declaring none as
     the UNSTATED zero, refuses a word outside the set without a write, and
     passes `bytes` through exactly; no kit source names mf_prov or
     fidelity, and a site renders byte-identically (plain and traced) with
     no analysis object and with one stating each fidelity value (UNSTATED
     and an out-of-enum 9 included). The layout is prov_check.c's static
     assertions (appended, never reordered).
  J. A DENY reaches its row: `--memfn=no-fd-r0` skips R0 on its witness.
  K. B2's ROUTING (§1.6, R17-b' B2): the rows the design routes at B2 (D1,
     D1c, D1w) are routed and LOCKED, every other row is neither; each routed
     row DECIDES the one-byte site it is written for (the kit's report
     `mf_result.row` and the traced `MFTRACE FDROUTE` record, two
     observations) and the text is that row's pick, read here from the text
     by this file's own signature (LIBC: one memchr with the kit's guard;
     LIBC_BACK: the memchr from the floor and the `+ 1` store; WALK: the
     table walk and its post-test; the DFA hat's bounded block and moved
     test); a set site is decided by NO routed row (S922's reverse: routing
     early); `--memfn=no-fd-d1` moves the DFA_SCAN byte site to D1w's walk
     (`fd-d1`'s OFF arm, [rev3 A17]).
  M. B3b's ROUTING (§1.4, §1.6, R17-b' B3b): the rows the design routes at B3b
     (D2 and slot PRES's P0, P2, P3, P4, P9) are routed and LOCKED with B2's;
     their three denies are registered (`fd-pres-g1`, `fd-pres-pick`,
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
import os
import re
import struct
import subprocess
import sys

passed = failed = 0
unreached = []

# R-26.6 (lane r26zk): RPT, the REPORT row, the last FIND row (listed after
# slot PRES in the table), UNROUTED: no row routes before its step
FIND_ROWS = ["R0", "R5", "R8", "R3a", "R3b", "R4", "R1", "R2", "D1", "D1c", "D1w", "D2",
             "R7", "R7w", "RPT"]
PRES_ROWS = ["P0", "P2", "P3", "P4", "P9"]
DERIVED_Q = {"saving", "xover", "block", "dom", "lstar", "g8"}
B1_DENIES = ["fd-r0", "fd-r5", "fd-r8", "fd-ndisp", "fd-d1"]
B3B_DENIES = ["fd-pres-g1", "fd-pres-pick", "pres-set-lead"]
PENDING_DENIES = {}
LATER_FORMS = {"V1": "B4", "W64": "B6", "NONE": "B5", "dispatch-twin": "B4/B8"}
FD_SITES = ["set10", "set2r", "byte1", "run3", "pre-req", "pre-opt",
            "byte1t", "byte1vm", "hat1", "mline"]
# the rows the design routes at B2 and B3b (r17b_prime.md §1.6, §3.1 rows
# B2 and B3b); every other row routes at B4 or later
ROUTED_B2 = {"D1", "D1c", "D1w"}
ROUTED_B3B = {"D2", "P0", "P2", "P3", "P4", "P9"}
ROUTED = ROUTED_B2 | ROUTED_B3B
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
PAY_TIE_FLOOR = 6
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
                                  "routed", "locked", "step", "keys"), c)))
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
        if not ks and r["basis"] == "MEASURED":
            bad("%s: MEASURED but reads no key" % r["id"])
        quant = {k.split(".")[1] for k in ks if k.count(".") >= 1}
        if quant & DERIVED_Q and r["basis"] != "DERIVED":
            bad("%s: reads the derived %s but its basis is %s" % (r["id"], sorted(quant & DERIVED_Q), r["basis"]))
        if any(not k.startswith("kit.") for k in ks):
            bad("%s: reads a key that is not the kit's: %s" % (r["id"], ks))
        want = "1" if r["id"] in ROUTED else "0"
        if r["routed"] != want or r["locked"] != want:
            bad("%s: routed %s / locked %s at B3b (the routed rows are %s; no row routes "
                "before its step)" % (r["id"], r["routed"], r["locked"], sorted(ROUTED)))
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
    for d in B3B_DENIES:
        (ok() if d in opts else bad("options.def lacks B3b's deny %s" % d))
    for d, step in PENDING_DENIES.items():
        if d in opts:
            bad("%s is registered before its step %s" % (d, step))
        else:
            unreached.append("deny %s: registered with its rows' routing at %s" % (d, step))
    return rows


# ---- B ----------------------------------------------------------------------

def check_hash(fx):
    r = run([fx, "--hash"]).stdout.decode().splitlines()
    form = {c[1]: (c[2], c[3]) for c in (ln.split("\t") for ln in r) if c[0] == "FORM"}
    text = {c[1]: c[2] for c in (ln.split("\t") for ln in r) if c[0] == "TEXT"}
    for f in ("walk", "libc"):
        if form.get(f, ("-1",))[0] != "0" or not re.fullmatch(r"[0-9a-f]{16}", form[f][1]):
            bad("mf_form_hash(%s) does not resolve: %s" % (f, form.get(f)))
        else:
            ok()
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
    for name in ("kit-grid", "kit-synthetic"):
        cl = read_cards(os.path.join(root, "memfn/data/cards", name + ".tsv"))
        cards[name] = cl
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


# ---- D, E, F, I, J ----------------------------------------------------------

def fd_run(fx, site, setpath=None, opts=None):
    argv = [fx, "--fd-site", site]
    if setpath:
        argv += ["--fd-set", setpath]
    if opts:
        argv += ["--opts", opts]
    r = run(argv)
    out, err = r.stdout.decode(), r.stderr.decode()
    dec, keys = [], []
    for ln in err.splitlines():
        if ln.startswith("MFTRACE FD "):
            d = dict(t.split("=", 1) for t in ln.split()[2:] if "=" in t)
            dec.append(d)
        elif ln.startswith("MFTRACE FDKEY "):
            d = dict(t.split("=", 1) for t in ln.split()[2:] if "=" in t)
            keys.append(d)
    cons = re.search(r"^CONSULTED\t(\d+)", out, re.M)
    ref = re.search(r"^REFUSED\t(.*)$", out, re.M)
    return r.returncode, dec, keys, (int(cons.group(1)) if cons else None), \
        (ref.group(1) if ref else None), err


def decisions(dec):
    return [(d.get("slot"), d.get("pred", "-"), d.get("layer"), d.get("row")) for d in dec]


def tpl_match(tpl, key):
    rx = "".join("[A-Za-z0-9_+-]+" if p.startswith("<") else re.escape(p)
                 for p in re.split(r"(<[^>]+>)", tpl))
    return re.fullmatch(rx, key) is not None


def write_set_without(full, drop, path):
    secs = open(full, encoding="utf-8").read().split("\n")
    with open(path, "w") as fh:
        for ln in secs:
            if ln.split("\t")[0] == drop:
                continue
            fh.write(ln + "\n")


def check_sites(root, fx, fxt, tmp, rows):
    full = os.path.join(root, "memfn/data/sets/synthetic-every-key.tsv")
    tpls = {r["id"]: keys_of(r) for r in rows}
    nsite = nkey = 0
    for site in FD_SITES:
        rc0, dec0, _, cons0, ref0, err0 = fd_run(fxt, site)
        rc1, dec1, keys1, cons1, ref1, err1 = fd_run(fxt, site, full)
        if rc0 or rc1 or ref0 or ref1:
            bad("%s: the kit refused (no set rc %d %s; full set rc %d %s)" % (site, rc0, ref0, rc1, ref1))
            continue
        if not dec0 or not dec1:
            bad("%s: the shadow wrote no decision (NULL %d, full %d records)" % (site, len(dec0), len(dec1)))
            continue
        nsite += 1
        # no shadow decision is declined on `need` (a row's contract refusing the
        # span it was the first to hold on: P0 held an OPTIONAL span its
        # REQUIRED-only contract refused, 1439 would-declines in B1/B2's N2
        # census, lane n2fix). Not on every field: these fixtures leave
        # site_kind UNSTATED, so a FIND decision may decline on that, as its own
        # (stated-kind) compiles do not.
        wd = [ln for ln in err0.splitlines()
              if ln.startswith("MFTRACE END table=fd ") and
              (" phase=shadow " in ln or " phase=define " in ln)
              and " would_decline=1 " in ln and "need:" in ln]
        (ok() if not wd else bad("%s: the shadow's gate declined on need (%s)" % (site, wd[0])))
        if site == "pre-opt":                   # K35: the OPTIONAL presence span is on the record
            opt = [d for d in dec0 if d.get("slot") == "PRES" and d.get("need") == "OPTIONAL"]
            (ok() if opt else bad("pre-opt: no OPTIONAL PRES decision, the would-decline control is blind"))
        for c, what in ((cons0, "no set"), (cons1, "the full set")):
            (ok() if c == 0 else bad("%s: consulted %s under %s (no routed row reads a key at B1)"
                                       % (site, c, what)))
        # E: every looked-up key is declared by its row
        for k in keys1:
            row, key = k.get("row"), k.get("key")
            if not any(tpl_match(t, key) for t in tpls.get(row, [])):
                bad("%s: row %s looked up %s, which it does not declare (R-MS4)" % (site, row, key))
            else:
                ok()
        # D: each key the decision read, removed in turn, moves the reading row off
        chosen = {(d.get("slot"), d.get("pred", "-"), d.get("layer")): d.get("row") for d in dec1}
        found = sorted({(k["row"], k["key"]) for k in keys1 if k.get("found") == "1"})
        for row, key in found:
            if row not in chosen.values():
                continue                        # read by a row the walk passed over
            nkey += 1
            path = os.path.join(tmp, "less.tsv")
            write_set_without(full, key, path)
            rc2, dec2, _, _, ref2, _ = fd_run(fxt, site, path)
            if rc2 or ref2:
                bad("%s: the set less %s is refused: %s" % (site, key, ref2))
                continue
            ch2 = {(d.get("slot"), d.get("pred", "-"), d.get("layer")): d.get("row") for d in dec2}
            moved = [kk for kk, v in chosen.items() if v == row and ch2.get(kk) == row]
            (ok() if not moved else
             bad("%s: with %s ABSENT row %s still decides %s (an absent key read as a value: "
                 "S917)" % (site, key, row, moved)))
    (ok() if nsite == len(FD_SITES) else bad("%d of %d finder sites ran" % (nsite, len(FD_SITES))))
    (ok() if nkey >= 3 else bad("only %d read keys were removed in turn (K35 floor 3)" % nkey))
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
    unreached.append("R-MS2: consulted's true arms (an ABSENT and a present key read by a ROUTED "
                     "row) have no routed reader before B4")
    # I: the call mode is a stated fact (R-23): every body value is stated
    # once; the three that are not a mode are refused naming `body`
    for site, want in (("set10-nobody", "`body` UNSTATED"),
                       ("set10-param", "`body` PARAM is reserved"),
                       ("set10-bodyoor", "`body` outside mf_body")):
        rc, dec, _, _, ref, _ = fd_run(fxt, site, full)
        (ok() if ref and want in ref and not dec else
         bad("%s: the kit did not refuse a bad call mode naming %s (rc %d, refusal %s, %d "
             "decisions)" % (site, want, rc, ref, len(dec))))
    _, _, _, _, ref_b, err_b = fd_run(fxt, "set10", full)
    r1_b = [ln for ln in err_b.splitlines() if "table=fd" in ln and " row=R1 " in ln and "verdict=" in ln]
    (ok() if not ref_b and r1_b and not any("body:R1" in ln for ln in r1_b) else
     bad("body ONESHOT: refused (%s) or R1's gate names `body`: %s" % (ref_b, r1_b[:1])))
    # J: a deny reaches its row (R0's witness under the R0 set, its key set)
    r0set = os.path.join(tmp, "r0.tsv")
    with open(r0set, "w") as fh:
        fh.write("#section header\n#key\tvalue\nid\tr0\n#section rows\n#key\tunit\tvalue_e6\n"
                 "kit.saving.V1.WALK.r2\tratio\t0\nkit.saving.V1.WALK.r2e0c0\tratio\t0\n"
                 "kit.eps.streamed.slope\tratio\t10000\n")
    _, d_on, _, _, _, _ = fd_run(fxt, "set2r", r0set)
    _, d_off, _, _, _, _ = fd_run(fxt, "set2r", r0set, "no-fd-r0")
    on = [d.get("row") for d in d_on if d.get("slot") == "FIND"]
    off = [d.get("row") for d in d_off if d.get("slot") == "FIND"]
    (ok() if on == ["R0"] and off and "R0" not in off else
     bad("--memfn=no-fd-r0 does not skip R0 on its witness (%s -> %s)" % (on, off)))
    for d in ("fd-r5", "fd-r8", "fd-ndisp"):
        unreached.append("deny %s: its row cannot hold on a B2 fixture (E, H, or W64 "
                         "unbuilt); its reach is its routing step's" % d)


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
         bad("%s: decided by a routed row %s (FDROUTE %s): no row routes it before B4"
             % (site, rt, [d.get("row") for d in fr])))
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
    # D2 routes the RUN fixture through the composer's walk
    _, rt, _, fr = fd_routed(fx, "run3")
    _, rtt, _, frt = fd_routed(fxt, "run3")
    (ok() if rt == "D2" and rtt == "D2" and [x.get("row") for x in frt] == ["D2"] else
     bad("run3: decided by %s (traced %s, FDROUTE %s), the design's routed row is D2"
         % (rt, rtt, [x.get("row") for x in frt])))


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


# ---- H ----------------------------------------------------------------------

def pay_expect(c):
    npt, pts, rest = c[0], c[1:1 + 2 * c[0]], c[1 + 2 * c[0]:]
    hc, call, cf, hn, nf, hu, use, uf, hw, wf = rest
    t1 = hc and npt >= 1 and all(pts[2 * i] - pts[2 * i + 1] > call + cf for i in range(npt))
    t2 = hc and hn and call + cf <= nf
    t3 = hu and hw and use + uf <= wf
    return (1 if t1 else 0) | (2 if t2 else 0) | (4 if t3 else 0)


def check_pay(fx):
    cases, ties = [], 0
    for m in (0, 7, 1000, -50, 999999999):      # magnitudes, a negative one included
        for d in (-1, 0, 1):
            # T1 at its boundary (saving - floor vs call + cfloor), one point and two
            cases.append([1, m + 100 + d, 10, 1, m + 80, 10, 1, 10 ** 12, 1, 0, 0, 1, 10])
            cases.append([2, m + 500, 10, m + 100 + d, 10, 1, m + 80, 10, 1, 10 ** 12, 1, 0, 0, 1, 10])
            # T2 at its boundary: call + cfloor vs next floor
            cases.append([1, 10 ** 12, 1, 1, m + 40, 10, 1, m + 50 + d, 1, 0, 0, 1, 10])
            # T3 at its boundary: use + ufloor vs wmin floor
            cases.append([1, 10 ** 12, 1, 1, 1, 1, 1, 10 ** 12, 1, m + 7, 3, 1, m + 10 + d])
            ties += 4 if d == 0 else 0
    for absent in range(4):
        c = [1, 1000, 1, 1, 1, 1, 1, 1000, 1, 1, 1, 1, 1000]
        idx = {0: 3, 1: 6, 2: 8, 3: 11}[absent]
        c[idx] = 0
        cases.append(c)
    cases.append([0, 1, 1, 1, 1, 1000, 1, 1, 1, 1, 1000])   # no measured point: T1 fails
    r = run([fx, "--pay-grid"], input=("\n".join(" ".join(map(str, c)) for c in cases) + "\n").encode())
    got = r.stdout.decode().split()
    if len(got) != len(cases):
        bad("--pay-grid answered %d of %d cases" % (len(got), len(cases)))
        return
    for c, g in zip(cases, got):
        e = pay_expect(c)
        (ok() if int(g) == e else bad("pay rule on %s: kit %s, expected %d" % (c, g, e)))
    (ok() if ties >= PAY_TIE_FLOOR else bad("the grid holds %d ties, under %d" % (ties, PAY_TIE_FLOOR)))


# ---- L ----------------------------------------------------------------------

# window_contract.md rev 3.1 §3.1's enumerators, written HERE (the kit's header
# and pcrec's mapping are what they are held against).
FID_EXPECT = {"verbatim": 1, "adapted": 2, "synthesized": 3}
FID_OUTSIDE = ["Verbatim", "VERBATIM", "", "synth", "verbatim ", "none", "measured"]
KIT_READERS_RE = re.compile(r"mf_prov|mf_akind|MF_FID_|fidelity|->prov\b|\.prov\b")


def schema_fidelity_tokens(root):
    """The closed set of `fidelity` tokens, read off the schema dump the
    parser's own constraint check reads (`pcrec --list-schema`), never off the
    mapping under test."""
    r = run([os.path.join(root, "build", "pcrec"), "--list-schema"])
    for ln in r.stdout.decode().splitlines():
        c = ln.split("\t")
        if c[0] == "provenance" and c[1] == "fidelity":
            m = re.search(r"closed fidelity ((?:[a-z]+ ?)+)", "\t".join(c))
            if m:
                return m.group(1).split()
    return None


def prov_run(provchk, bytes_, tok):
    r = run([provchk, str(bytes_), tok])
    f = r.stdout.decode().rstrip("\n").split("\t")
    return (int(f[1]), int(f[2]), int(f[3]), int(f[4]), int(f[5])) if f[0] == "RC" else None


def check_prov(root, fx, fxt, provchk):
    """R-24 (MF_SITE_ABI 15): mf_prov carries the answering block's `bytes`
    and `fidelity`. (1) pcrec's mapping states every token of the findings
    vocabulary as its own nonzero enumerator, NULL as the UNSTATED zero, and
    refuses a word outside the set without writing (the layout half is
    prov_check.c's static assertions, a build failure). (2) the closed set is
    read off --list-schema and equals the mapping's, both directions. (3) `bytes` passes through exactly. (4) no
    kit row READS either field: the kit's sources name neither, and a site
    renders byte-identically (stdout and the traced shadow's stderr) with no
    analysis object and with one stating each fidelity value, UNSTATED and an
    out-of-enum value included."""
    toks = schema_fidelity_tokens(root)
    if toks is None:
        bad("L: --list-schema carries no `closed fidelity ...` constraint (the vocabulary's source moved)")
        return
    (ok() if sorted(toks) == sorted(FID_EXPECT) else
     bad("L: the schema's fidelity set %s is not the contract's %s" % (toks, sorted(FID_EXPECT))))
    seen = set()
    for t in toks:
        g = prov_run(provchk, 1234, t)
        e = FID_EXPECT.get(t)
        if g is None or e is None or g[0] != 0 or g[1] != e or g[2] != 1234:
            bad("L: token %r maps to %s, expected rc 0 fidelity %s bytes 1234" % (t, g, e))
        else:
            ok()
            seen.add(g[1])
    (ok() if seen == {1, 2, 3} else bad("L: the vocabulary reaches enumerators %s, not exactly 1,2,3" % sorted(seen)))
    g = prov_run(provchk, 0, "@none")
    (ok() if g and g[0] == 0 and g[1] == 0 and g[2] == 0 else
     bad("L: a block declaring no fidelity (NULL, bytes 0) maps to %s, expected rc 0 fidelity 0 (UNSTATED) bytes 0" % (g,)))
    for t in FID_OUTSIDE:
        g = prov_run(provchk, 55, t)
        # refused (-1) and the sentinels (fidelity 0xEE = 238, bytes 0xDEADBEEF) untouched
        (ok() if g and g[0] == -1 and g[1] == 238 and g[2] == 0xDEADBEEF else
         bad("L: the word %r is outside the vocabulary and must be refused without a write, got %s" % (t, g)))
    for n in (0, 1, 999960, 1000000, (1 << 40) + 7, (1 << 63) + 5):
        g = prov_run(provchk, n, "verbatim")
        (ok() if g and g[2] == n else bad("L: bytes %d did not pass through exactly (got %s)" % (n, g)))
    # (4) no kit reader
    hits = []
    for d in ("memfn/src",):
        for f in sorted(os.listdir(os.path.join(root, d))):
            if f.endswith((".c", ".h", ".def")):
                for i, ln in enumerate(open(os.path.join(root, d, f), errors="replace"), 1):
                    if KIT_READERS_RE.search(ln):
                        hits.append("%s/%s:%d" % (d, f, i))
    (ok() if not hits else bad("L: the kit's sources name mf_prov/fidelity (a reader before B3a): %s" % hits[:5]))
    base = None
    for prog, name in ((fx, "plain"), (fxt, "traced")):
        for site in ("set10", "byte1t"):
            ref = run([prog, "--fd-site", site])
            for fid in (0, 1, 2, 3, 9):
                got = run([prog, "--fd-site", site, "--fd-an", str(fid)])
                if (got.returncode, got.stdout, got.stderr) != (ref.returncode, ref.stdout, ref.stderr) or \
                        b"TEXT" not in ref.stdout:
                    bad("L: %s kit: site %s renders differently with an analysis stating fidelity %d "
                        "(or the control rendered nothing)" % (name, site, fid))
                else:
                    ok()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--fx", required=True)
    ap.add_argument("--fxt", required=True)
    ap.add_argument("--tmp", required=True)
    ap.add_argument("--provchk", required=True)
    a = ap.parse_args()
    rows = check_table(a.fx)
    form = check_hash(a.fx)
    check_sets(a.root, form)
    check_sites(a.root, a.fx, a.fxt, a.tmp, rows)
    check_query(a.fx, a.fxt, a.tmp)
    check_pay(a.fx)
    check_routing(a.fx, a.fxt)
    check_pres_routing(a.fx, a.fxt, a.tmp)
    check_prov(a.root, a.fx, a.fxt, a.provchk)
    for u in unreached:
        print("UNREACHED: " + u)
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
