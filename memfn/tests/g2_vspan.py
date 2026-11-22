#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2-V, R-47 U4, lane bsu4g).
"""memfn/tests/g2_vspan.py — G2-V, the vector span's own checks (docs/design/memfn/block_span.md
rev 4.2 §10.2, the "G2-V unit" and "G2-V whole" rows). run_g2_win.sh's section V; runnable alone.

  g2_vspan.py unit  --root ROOT --lib LIB --work DIR [--seed N]
  g2_vspan.py whole --root ROOT --lib LIB --work DIR [--seed N]

UNIT. Every V rendering over a GENERATED space, at the x86-64-v3 target (the only target whose
text has the `w32` level block): sets of 1..8 byte ranges in both polarities, sets of bytes
>= 0x80, the empty set, 255-member sets, single-byte-removed sets; k at every rung edge (16, 17,
31, 32, 33, 63, 64, 65, 999, 1000) and random interior k; two byte-rate regimes per set (`dense`,
whose stop set is common, so the site routes D-hors: T-vwin; `rare`, R7w's walk: T-vscan).
The generator (g2/g2_vspan_gen.c, the one kit caller) renders each case twice: at x86-64-v3,
the text under test, and at the portable target under the lever span-head=0, THE k SOURCE
(§10.1: `J = LO; for (; J < END;`, k = END - LO). This runner reads LO, K and the row's kind
off those texts, holds the kit's own numbers in its `__w32` text (`p = S + C + LO`, the loop's K,
B) to them (printing both; a disagreement is a failure), and drives g2/g2_vspan_drv.c: every
window FLUSH AGAINST A PROT_NONE PAGE at its low end, and again at its high end. THE CONTROL:
python `all(re.fullmatch(cls, bytes([b])) for b in window)`, with `cls` the class this file
WRITES (a regex string), never the kit's set and never a table the kit computed. The bytes the
kit is handed are derived from the same written spec by plain set arithmetic, and held equal to
re's reading of `cls` before anything runs (a disagreement is the test's own fault, a failure).

WHOLE. Patterns `cls{k+1}` and mixed patterns (a literal run beside a stretch, two stretches, a
stretch beside a non-core position) compiled by build/pcrec at -fno-memfn-simd and
-fmemfn-simd=x86-64-v3, at --window-search-width 32 and 4095; each artifact's find-all (restart
at the match end) over subjects in the cards' six regimes and the forced near-miss staircases
(a failing index at each position of each stretch, at the first window and after a match),
every subject FLUSH AGAINST A PROT_NONE PAGE at its start, and again at its end. THE CONTROL:
python `re.finditer` over the same pattern string. Its V sites are counted by §10.1's k source
(the traced harness's `MFTRACE FDROUTE` row and frame, k off the head-0 lever compile's loop
text, the predicate D-hors 16..1000 / R7w 24..64 on E-find applied HERE), with the kit's own
answer (the walk's selector calls) printed beside it; a disagreement is a failure.

Floors are LITERALS below (K35), measured on the Linux dev box, seed 20261122, less ~10%.
Prints `checks passed: N` / `checks failed: M`; exit 0 iff M == 0.
"""
import argparse
import os
import random
import re
import subprocess
import sys

# ---- THE FLOORS (K35): hand-written literals, measured 2026-11-22 (lane bsu4g, seed 20261122,
# the dev box), each the measure less ~10%. Raise when the space grows; never lower one to pass.
UNIT_FLOORS = {            # V renderings per (row, rung): the cases whose x86-64-v3 text is tested
    ("vwin", 16): 172, ("vwin", 32): 518, ("vscan", 16): 124, ("vscan", 32): 279,   # (192 576 138 310)
}
UNIT_EDGE_KS = [16, 17, 31, 32, 33, 63, 64, 65, 999, 1000]   # each must be reached at vwin
UNIT_VSCAN_KS = [24, 31, 32, 33, 63, 64]                     # each must be reached at vscan
UNIT_FLOOR_WINDOWS = 1060000   # windows driven, each at both placements (1177900)
UNIT_FLOOR_FALSE = 549000      # windows whose answer is 0: a non-member somewhere (610819)
UNIT_FLOOR_KINDS = {"ranges": 273, "neg": 273, "high": 85, "named": 68, "full255": 102,
                    "removed": 290}   # V cases per set kind (304 304 95 76 114 323)
UNIT_EMPTY_CASES = 19      # empty-set cases generated (22): the kit refuses each (no window can match), counted
WHOLE_FLOORS = {            # V sites per (row, rung), one per (pattern, width), by the k source
    ("vwin", 16): 31, ("vwin", 32): 18, ("vscan", 16): 17, ("vscan", 32): 11,   # (35 20 19 13)
}
WHOLE_FLOOR_SUBJECTS = 10150   # (11280)
WHOLE_FLOOR_STAIR = 9400       # staircase subjects, a failing index per stretch position (10440)
WHOLE_FLOOR_MATCHES = 5990     # matches python found over the V-site patterns' subjects (6659)
WHOLE_FLOOR_MIXED = 7          # mixed patterns x widths with a V site (8)

TARGET = "x86-64-v3"
PASS = [0]
FAIL = [0]


def ok():
    PASS[0] += 1


def bad(msg):
    FAIL[0] += 1
    if FAIL[0] <= 60:
        print("FAIL: " + msg)


def floor(label, got, want):
    if got >= want:
        ok()
    else:
        bad("floor %s: %d < %d" % (label, got, want))


def run(argv, timeout=900, **kw):
    return subprocess.run(argv, capture_output=True, timeout=timeout, **kw)


def cc():
    return os.environ.get("CC", "gcc")


# ======================================================================================
# UNIT
# ======================================================================================

def esc(b):
    return "\\x%02x" % b


def ranges_spec(ranges, neg):
    """(cls, members): the class this test WRITES, and its members by set arithmetic."""
    body = "".join(esc(a) if a == b else "%s-%s" % (esc(a), esc(b)) for a, b in ranges)
    mem = set()
    for a, b in ranges:
        mem |= set(range(a, b + 1))
    if neg:
        mem = set(range(256)) - mem
    return ("[^%s]" if neg else "[%s]") % body, mem


def gen_sets(rnd):
    """The generated set space: (kind, cls, members)."""
    out = []

    def rand_ranges(r, lo, hi):
        pts = sorted(rnd.sample(range(lo, hi + 1), 2 * r))
        return [(pts[2 * i], pts[2 * i + 1]) for i in range(r)]
    for r in range(1, 9):
        for neg in (0, 1):
            for rep in range(2):
                cls, mem = ranges_spec(rand_ranges(r, 0, 255), neg)
                out.append(("neg" if neg else "ranges", cls, mem))
    for rep in range(4):                                    # bytes >= 0x80 only
        cls, mem = ranges_spec(rand_ranges(1 + rnd.randrange(4), 0x80, 0xff), 0)
        out.append(("high", cls, mem))
    out.append(("high", "[\\x80-\\xbf]", set(range(0x80, 0xc0))))
    out.append(("named", "[0-9a-f]", set(b"0123456789abcdef")))
    out.append(("named", "[0-9]", set(b"0123456789")))
    out.append(("named", "\\w", set(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")))
    out.append(("named", "[aeiou]", set(b"aeiou")))
    out.append(("empty", "[^\\x00-\\xff]", set()))
    out.append(("full255", "[^\\n]", set(range(256)) - {10}))
    for b in (0x00, 0x7f, 0x80, 0xff, rnd.randrange(256)):
        out.append(("full255", "[^%s]" % esc(b), set(range(256)) - {b}))
    # single-byte-removed: a base set less its highest, lowest, or a random member, written
    # as a negative lookahead ahead of the base class (708's nib_drop drops the highest)
    bases = [("[0-9a-f]", set(b"0123456789abcdef")), ("[^\\n]", set(range(256)) - {10}),
             ("[\\x80-\\xbf]", set(range(0x80, 0xc0)))]
    for rep in range(3):
        bases.append(ranges_spec(rand_ranges(2 + rnd.randrange(5), 0, 255), rnd.randrange(2)))
    for cls, mem in bases:
        ms = sorted(mem)
        for b in {ms[-1], ms[0], rnd.choice(ms)}:
            out.append(("removed", "(?!%s)%s" % (esc(b), cls), mem - {b}))
    return out


def setspec_ok(cls, mem):
    """re's reading of the written class equals the set handed to the kit."""
    rx = re.compile(cls.encode("latin-1"))
    rd = {b for b in range(256) if rx.fullmatch(bytes([b]))}
    return rd == mem, rx


def bitmap_hex(mem):
    bm = bytearray(32)
    for b in mem:
        bm[b >> 3] |= 1 << (b & 7)
    return bm.hex()


LOOP_RE = re.compile(r"g2vh(\d+)_mf1_j = (-?\d+); for \(; g2vh\d+_mf1_j < (-?\d+);")


def read_case(work, cid):
    """The facts this runner reads off the two texts: the k source and the kit's own numbers."""
    v = open(os.path.join(work, "v_%d.txt" % cid), encoding="latin-1").read()
    h = open(os.path.join(work, "h_%d.txt" % cid), encoding="latin-1").read()
    loops = [(int(a), int(b)) for _, a, b in LOOP_RE.findall(h)]
    p = "g2vu%d_mf1_" % cid
    f = {"loops": loops, "hors": "%ssh[256]" % p in v, "text": v}
    f["sel_calls"] = len(re.findall(r"\b%svs\d+\(%ss, %sc\)" % (p, p, p), v.split("/* ---- body ---- */")[-1]))
    f["w32_calls"] = len(re.findall(r"return %svs0__w32\(%ss, %sc\);" % (p, p, p), v))
    m = re.search(r"const unsigned char \*p = %ss \+ %sc(?: \+ (\d+)| - (\d+))?;" % (p, p), v)
    f["kit_lo"] = None if not m else (int(m.group(1)) if m.group(1) else -int(m.group(2)) if m.group(2) else 0)
    m = re.search(r"for \(; i \+ (\d+) < (\d+); i \+= (\d+)\) if \(!%svs0__w32_b\(p \+ i\)\) return 0;" % p, v)
    f["kit_b"], f["kit_k"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    m = re.search(r"return %svs0__w32_b\(p \+ \((\d+) - (\d+)\)\);" % p, v)
    f["kit_tail"] = (int(m.group(1)), int(m.group(2))) if m else None
    return f


def unit(a):
    rnd = random.Random("g2vu|%d" % a.seed)
    work = os.path.join(a.work, "vunit")
    os.makedirs(work, exist_ok=True)
    sets = gen_sets(rnd)
    cases = []                   # (id, kind, cls, mem, rx, regime, k)
    cid = 0
    for kind, cls, mem in sets:
        same, rx = setspec_ok(cls, mem)
        if not same:
            bad("the test's own class %s and its member set disagree (the test is wrong)" % cls)
            continue
        ks_d = UNIT_EDGE_KS + [rnd.randint(18, 998), rnd.randint(34, 62)]
        ks_r = [16, 17, 24, 31, 32, 33, 63, 64, 65, rnd.randint(25, 62)]
        for regime, ks in (("dense", ks_d), ("rare", ks_r)):
            for k in ks:
                cid += 1
                cases.append((cid, kind, cls, mem, rx, regime, k))
    spec = os.path.join(work, "spec.txt")
    with open(spec, "w") as f:
        for c in cases:
            f.write("%d %d %s %s\n" % (c[0], c[6] + 1, c[5], bitmap_hex(c[3])))
    g2 = os.path.join(a.root, "memfn", "tests", "g2")
    gen = os.path.join(work, "gen")
    r = run([cc(), "-std=gnu11", "-O1", "-Wall", "-Wextra", "-Werror", "-I" + os.path.join(a.root, "memfn", "include"),
             os.path.join(g2, "g2_vspan_gen.c"), a.lib, "-o", gen])
    if r.returncode:
        bad("unit: the generator does not build: " + r.stderr.decode()[:400])
        return
    r = run([gen, spec, work, TARGET], timeout=600)
    glog = r.stdout.decode()
    if r.returncode:
        bad("unit: the generator failed (rc %d): %s" % (r.returncode, (r.stderr.decode() + glog)[-400:]))
        return
    ok()
    refused = {int(m.group(1)) for m in re.finditer(r"^G2VU refused (\d+) ", glog, re.M)}
    # the cases, read off the texts
    vcases, pop, edge_seen, kinds_seen, empty = [], {}, {}, {}, 0
    for c in cases:
        cid, kind, cls, mem, rx, regime, k = c
        if kind == "empty":
            empty += 1
        if cid in refused:
            # the empty set has no E-find frame (no window can match): refused, counted
            if kind == "empty":
                ok()
            else:
                bad("unit case %d (%s, %s, k %d): refused by the kit: %s" % (
                    cid, cls, regime, k, re.search(r"^G2VU refused %d (.*)$" % cid, glog, re.M).group(1)))
            continue
        f = read_case(work, cid)
        has_v = "g2vu%d_mf1_vs0(" % cid in f["text"]
        if not has_v:
            continue
        if not f["loops"]:
            bad("unit case %d: a V text but no head-0 loop (the k source is unread)" % cid)
            continue
        lo, end = f["loops"][0]
        K = end - lo
        row = "vwin" if f["hors"] else "vscan"
        B = 32 if K >= 32 else 16
        # the kit's own numbers beside the k source's
        kit = (f["kit_lo"], f["kit_k"], f["kit_b"], f["kit_tail"])
        if (f["kit_lo"], f["kit_k"], f["kit_b"], f["kit_tail"]) != (lo, K, B, (K, B)):
            bad("unit case %d (%s, k %d): the k source reads LO %d K %d B %d, the kit's __w32 text %r"
                % (cid, cls, k, lo, K, B, kit))
            continue
        if f["sel_calls"] != 1 or f["w32_calls"] != 1:
            bad("unit case %d: %d selector calls in the walk, %d __w32 calls in the selector (1 and 1)"
                % (cid, f["sel_calls"], f["w32_calls"]))
            continue
        ok()
        pop[(row, B)] = pop.get((row, B), 0) + 1
        edge_seen.setdefault(row, set()).add(K)
        kinds_seen[kind] = kinds_seen.get(kind, 0) + 1
        vcases.append((cid, cls, mem, rx, lo, K, row, B))
    print("G2VU cases %d rendered-V %d refused %d (empty-set cases %d)" % (len(cases), len(vcases), len(refused), empty))
    print("G2VU population " + " ".join("%s/b%d=%d" % (r_, b_, pop.get((r_, b_), 0))
                                        for r_, b_ in sorted(UNIT_FLOORS)))
    print("G2VU kinds " + " ".join("%s=%d" % (k_, kinds_seen.get(k_, 0)) for k_ in sorted(UNIT_FLOOR_KINDS)))
    for key, want in sorted(UNIT_FLOORS.items()):
        floor("unit %s/b%d" % key, pop.get(key, 0), want)
    for k_ in UNIT_EDGE_KS:
        floor("unit vwin reaches k %d" % k_, int(k_ in edge_seen.get("vwin", set())), 1)
    for k_ in UNIT_VSCAN_KS:
        floor("unit vscan reaches k %d" % k_, int(k_ in edge_seen.get("vscan", set())), 1)
    for k_, want in sorted(UNIT_FLOOR_KINDS.items()):
        floor("unit kind %s" % k_, kinds_seen.get(k_, 0), want)
    floor("unit empty-set cases", empty, UNIT_EMPTY_CASES)
    # ---- the windows and their expected answers (the CONTROL: re over the written class) ----
    wfile = os.path.join(work, "windows.txt")
    expect = {}                  # cid -> list of expected '0'/'1' per window
    hashes = {}                  # (cid, idx) -> window bytes (sampled)
    nfalse = 0
    with open(wfile, "w") as wf:
        for cid, cls, mem, rx, lo, K, row, B in vcases:
            memb = [b for b in range(256) if rx.fullmatch(bytes([b]))]      # re's reading, per byte
            ismem = [bool(rx.fullmatch(bytes([b]))) for b in range(256)]
            non = [b for b in range(256) if not ismem[b]]
            fill = [rnd.choice(memb) for _ in range(min(8, len(memb)))] or [0]
            if rnd.randrange(3) == 0:
                fill = memb[:]                                               # every member, cycled
            nf = len(fill)
            wf.write("C %d %d %d %d %s\n" % (cid, lo, K, nf, " ".join(map(str, fill))))
            exp = []

            def window(fseed, ov):
                w = bytearray(fill[(i * 7 + fseed) % nf] for i in range(K))
                for p_, b_ in ov:
                    w[p_] = b_
                return w

            def emit_w(fseed, ov):
                idx = len(exp)
                # the control, literally: every byte of the window a member of `cls` per re
                win = window(fseed, ov)
                e = all(ismem[b] for b in set(win))
                exp.append("1" if e else "0")
                if idx % 97 == 0:
                    hashes[(cid, idx)] = bytes(win)
                wf.write("W %d %d %s\n" % (fseed, len(ov), " ".join("%d %d" % x for x in ov)))
            # all-member windows
            for _ in range(3):
                emit_w(rnd.randrange(64), [])
            # the staircase: a non-member at each position (every position up to 65, else the
            # block edges near both ends and random interior positions)
            if K <= 65:
                stair = list(range(K))
            else:
                stair = sorted({p_ for p_ in [0, 1, 15, 16, 17, 31, 32, 33, 63, 64, 65,
                                               K - 33, K - 32, K - 31, K - 17, K - 16, K - 15, K - 2, K - 1]
                                + [rnd.randrange(K) for _ in range(16)] if 0 <= p_ < K})
            if non:
                for p_ in stair:
                    emit_w(rnd.randrange(64), [(p_, rnd.choice(non))])
            # random windows: 1..3 bytes from the whole byte space
            for _ in range(24):
                emit_w(rnd.randrange(64), [(rnd.randrange(K), rnd.randrange(256)) for _ in range(1 + rnd.randrange(3))])
            # sweeps: every byte value at the first, the last and a block-edge position
            for p_ in sorted({0, K - 1, min(K - 1, B - 1), min(K - 1, B)}):
                fseed = rnd.randrange(64)
                wf.write("S %d %d\n" % (fseed, p_))
                base = window(fseed, [])
                for v in range(256):
                    idx = len(exp)
                    win = bytearray(base)
                    win[p_] = v
                    exp.append("1" if all(ismem[b] for b in set(win)) else "0")
                    if idx % 97 == 0:
                        hashes[(cid, idx)] = bytes(win)
            wf.write("E\n")
            expect[cid] = exp
            nfalse += exp.count("0")
    drv = os.path.join(work, "drv")
    r = run([cc(), "-std=gnu11", "-O1", "-w", os.path.join(g2, "g2_vspan_drv.c"), os.path.join(work, "vsites.c"),
             "-o", drv], timeout=900)
    if r.returncode:
        bad("unit: the driver with the kit's text does not compile: " + r.stderr.decode()[:600])
        return
    with open(wfile) as wf:
        r = run([drv], stdin=wf, timeout=900)
    out = r.stdout.decode()
    if r.returncode == 4:
        print("SKIPPED ARM w32: %s; G2-V unit's %d cases NOT run" % (out.strip(), len(vcases)))
        bad("unit: the host cannot run the x86-64-v3 text (a skip is not a pass)")
        return
    for m in re.finditer(r"^FAULT .*$", out, re.M):
        bad("unit: " + m.group(0) + "  (a read past the window's guarded end or below its start)")
    if r.returncode:
        bad("unit: the driver exited %d: %s" % (r.returncode, r.stderr.decode()[-300:]))
    got = {int(m.group(1)): m.group(2) for m in re.finditer(r"^R (\d+) ([01]*)$", out, re.M)}
    nwin = wrong = 0
    for cid, exp in expect.items():
        g = got.get(cid)
        if g is None:
            bad("unit case %d: no answers" % cid)
            continue
        if len(g) != 2 * len(exp):
            bad("unit case %d: %d answers for %d windows" % (cid, len(g), len(exp)))
            continue
        nwin += len(exp)
        cbad = 0
        for i, e in enumerate(exp):
            for place in (0, 1):
                if g[2 * i + place] != e:
                    cbad += 1
                    wrong += 1
                    if cbad <= 2:
                        c = next(x for x in vcases if x[0] == cid)
                        bad("unit case %d (%s, %s, LO %d K %d B %d) window %d flush %s: the kit says %s, re says %s"
                            % (cid, c[1], c[6], c[4], c[5], c[7], i, "high" if place else "low", g[2 * i + place], e))
        if cbad == 0:
            ok()
    # the windows this runner described are the windows the driver built
    hseen = 0
    for m in re.finditer(r"^H (\d+) (\d+) ([0-9a-f]{16})$", out, re.M):
        key = (int(m.group(1)), int(m.group(2)))
        if key not in hashes:
            continue
        h = 1469598103934665603
        for b in hashes[key]:
            h = ((h ^ b) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        if "%016x" % h != m.group(3):
            bad("unit case %d window %d: the driver built another window than the runner described" % key)
        hseen += 1
    floor("unit window hashes checked", hseen, len(hashes))
    print("G2VU windows %d (x2 placements) false %d wrong %d hashes %d" % (nwin, nfalse, wrong, hseen))
    floor("unit windows", nwin, UNIT_FLOOR_WINDOWS)
    floor("unit false windows", nfalse, UNIT_FLOOR_FALSE)


# ======================================================================================
# WHOLE
# ======================================================================================

# The patterns: a token list per pattern, so the staircase knows each stretch position's class.
# ('c', CLS, N): CLS repeated N times; ('l', BYTES): a literal run; ('r', REGEX, SAMPLE): a
# position the window states outside its core (context), matched by SAMPLE in a witness.
W_CLASSES = ["[0-9a-f]", "[0-9]", "[^\\n]", "[\\x80-\\xbf]", "[aeiou]", "\\w", "[A-Z]", "[+.0-9]"]
W_NS = [16, 17, 24, 25, 32, 33, 41, 65, 66]


def w_patterns():
    pats = []
    for cls in W_CLASSES:
        for n in W_NS:
            pats.append(("cls", [("c", cls, n)]))
    pats.append(("cls", [("c", "[0-9a-f]", 1001)]))
    pats.append(("cls", [("c", "[^\\n]", 1000)]))
    pats.append(("cls", [("c", "[0-9a-f]", 300)]))
    # mixed: two stretches; a stretch beside non-core positions (word boundaries); literal runs
    # beside a stretch (the literal is D1's stop, so the k source routes no V there: counted)
    pats.append(("two", [("c", "[0-9a-f]", 20), ("c", "[g-z]", 20)]))
    pats.append(("two", [("c", "[0-9]", 30), ("c", "[a-f]", 30)]))
    pats.append(("two", [("c", "[^\\n]", 40), ("c", "[0-9]", 20)]))
    pats.append(("ctx", [("r", "\\b", b""), ("c", "[0-9a-f]", 32), ("r", "\\b", b"")]))
    pats.append(("ctx", [("r", "\\b", b""), ("c", "\\w", 40), ("r", "\\b", b"")]))
    pats.append(("ctx", [("r", "\\b", b""), ("c", "[0-9]", 25)]))
    pats.append(("lit", [("l", b"abc"), ("c", "[0-9]", 30)]))
    pats.append(("lit", [("c", "[0-9a-f]", 30), ("l", b"xyz")]))
    pats.append(("lit", [("c", "[0-9a-f]", 25), ("l", b"."), ("c", "[0-9]", 25)]))
    out = []
    for kind, toks in pats:
        rx = ""
        for t in toks:
            if t[0] == "c":
                rx += "%s{%d}" % (t[1], t[2])
            elif t[0] == "l":
                rx += "".join(re.escape(chr(c)) if chr(c).isalnum() else "\\x%02x" % c for c in t[1])
            else:
                rx += t[1]
        out.append((kind, rx, toks))
    return out


WORDS = ("the of and to in is you that it he was for on are as with his they at be this have from or one "
         "had by word but not what all were we when your can said there use an each which she do how their "
         "if will up other about out many then them these so some her would make like him into time has look "
         "two more write go see number no way could people my than first water been call who oil its now find "
         "long down day did get come made may part 404 200 0x1f ab12 deadbeef c0ffee 2026 e5 x86").split()


def w_subjects(rnd, toks, rx):
    """(label, subject) per regime, plus the staircases and edges."""
    mem = {}
    for t in toks:
        if t[0] == "c" and t[1] not in mem:
            r1 = re.compile(t[1].encode("latin-1"))
            ms = [b for b in range(256) if r1.fullmatch(bytes([b]))]
            mem[t[1]] = (ms, [b for b in range(256) if b not in set(ms)])
    ctx = any(t[0] == "r" for t in toks)
    sep = b" " if ctx else b""

    def witness():
        w = bytearray()
        pos = []                                  # (index, class) of every stretch position
        for t in toks:
            if t[0] == "c":
                for _ in range(t[2]):
                    pos.append((len(w), t[1]))
                    w.append(rnd.choice(mem[t[1]][0]))
            elif t[0] == "l":
                w += t[1]
            else:
                w += t[2]
        return w, pos
    npos = sum(t[2] for t in toks if t[0] == "c")
    big = npos > 200
    n = 3000 if big else 700
    out = []
    # the cards' six regimes (memfn/tests/span_forms/cards.py's names; written here)
    s = bytearray()
    while len(s) < n:
        s += witness()[0] + sep
    out.append(("hit-dense", bytes(s[:n])))
    s = bytearray()
    while len(s) < n:
        w, pos = witness()
        i, c = pos[-1]
        if mem[c][1]:
            w[i] = rnd.choice(mem[c][1])
        s += w + sep
    out.append(("near-miss", bytes(s[:n])))
    out.append(("random", bytes(rnd.getrandbits(8) for _ in range(n))))
    s = bytearray()
    while len(s) < n:
        rec = bytearray()
        ln = rnd.randint(48, 80)
        while len(rec) < ln:
            rec += (rnd.choice(WORDS) + " ").encode()
        if rnd.randrange(3) == 0:
            at = rnd.randrange(len(rec) + 1)
            rec[at:at] = b" " + witness()[0] + b" "
        s += rec.replace(b"\n", b" ") + b"\n"
    out.append(("short-subject", bytes(s[:n])))
    for lab in ("miss-heavy", "not-warm"):
        s = bytearray()
        while len(s) < n:
            s += (rnd.choice(WORDS) + (" " if rnd.randrange(12) else "\n")).encode()
        out.append((lab, bytes(s[:n])))
    # the forced near-miss staircases: a failing index at each stretch position, as the whole
    # subject (the first window, flush against both guards in turn) and after a match
    nst = 0
    for i, c in witness()[1]:
        if not mem[c][1]:
            continue
        w, _ = witness()
        w[i] = rnd.choice(mem[c][1])
        out.append(("stair-first", bytes(w)))
        w2, _ = witness()
        out.append(("stair-after", bytes(w2 + sep + w)))
        nst += 2
    # edges: a match alone (flush at both ends), one byte short, empty, two matches then a near-miss
    w, pos = witness()
    out.append(("alone", bytes(w)))
    out.append(("short", bytes(w[:-1])))
    out.append(("empty", b""))
    w2, _ = witness()
    w3, p3 = witness()
    i, c = p3[len(p3) // 2]
    if mem[c][1]:
        w3[i] = rnd.choice(mem[c][1])
    out.append(("pair-miss", bytes(w + sep + w2 + sep + w3)))
    return out, nst


H0_LOOP = re.compile(r"\b\w+_mf(\d+)_j = (-?\d+); for \(; \w+_mf\d+_j < (-?\d+); \w+_mf\d+_j\+\+\) if \((.*?)\) break;")
FDROUTE = re.compile(r"^MFTRACE FDROUTE \S+ site=(\d+) row=(\S+) \S+ \S+ frame=(\S+)", re.M)


def k_source(htr, rx, width, work):
    """§10.1's k source for one (pattern, width): {site: (row, k)} of each site's FIRST eligible
    stretch, by the traced build's FDROUTE row and frame and the head-0 lever compile's loops."""
    out = os.path.join(work, "k.c")
    r = run([htr, "-p", "k", "--features", "all", "--harness=span-head=0", "--window-search-width=%d" % width,
             "-o", out, "--pattern", rx], timeout=120)
    if r.returncode:
        return None, "the traced harness refused: " + r.stderr.decode()[-200:]
    routes = {int(m.group(1)): (m.group(2), m.group(3)) for m in FDROUTE.finditer(r.stderr.decode())}
    txt = open(out, encoding="latin-1").read()
    loops = {}
    for m in H0_LOOP.finditer(txt):
        site, lo, end, cond = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        own = "[" not in re.sub(r"\w+_mf\d+_s\[[^\]]*\]", "", cond)     # C-own: no table read
        loops.setdefault(site, []).append((end - lo, own))
    v = {}
    for site, (row, frame) in routes.items():
        if frame != "E-find":
            continue
        for k, own in loops.get(site, []):
            if own and ((row == "D-hors" and 16 <= k <= 1000) or (row == "R7w" and 24 <= k <= 64)):
                v[site] = (row, k)
                break
    return v, None


def whole(a):
    rnd = random.Random("g2vw|%d" % a.seed)
    work = os.path.join(a.work, "vwhole")
    os.makedirs(work, exist_ok=True)
    g2 = os.path.join(a.root, "memfn", "tests", "g2")
    pcrec = os.path.join(a.root, "build", "pcrec")
    # the k source's traced harness: the tree's kit compiled -DMF_TRACE into a copy of LIB
    trlib = os.path.join(work, "libpcrec_mftrace.a")
    r = run(["bash", os.path.join(a.root, "tests", "memfn", "mk_mftrace_lib.sh"), trlib, a.lib], timeout=600,
            env=dict(os.environ, CC=cc()))
    if r.returncode:
        bad("whole: the traced library does not build: " + r.stderr.decode()[-300:])
        return
    htr = os.path.join(work, "htr")
    r = run([cc(), "-O1", "-std=gnu11", "-I" + os.path.join(a.root, "lib"), "-I" + os.path.join(a.root, "src"),
             "-DPCREC_HARNESS", "-o", htr, os.path.join(a.root, "cli", "main.c"), trlib], timeout=600)
    if r.returncode:
        bad("whole: the traced harness does not build: " + r.stderr.decode()[-300:])
        return
    pats = w_patterns()
    subjects = []           # (pat index, label, bytes)
    nstair = 0
    for pi, (kind, rx, toks) in enumerate(pats):
        subs, nst = w_subjects(rnd, toks, rx)
        nstair += nst
        for lab, sb in subs:
            subjects.append((pi, lab, sb))
    arts = []               # (pat index, width, layer, prefix)
    pop, kit_disagree, mixed_v, vsite_pats = {}, 0, 0, set()
    for pi, (kind, rx, toks) in enumerate(pats):
        for width in (32, 4095):
            v, err = k_source(htr, rx, width, work)
            if v is None:
                bad("whole %s at %d: %s" % (rx, width, err))
                continue
            for site, (row, k) in v.items():
                key = ("vwin" if row == "D-hors" else "vscan", 32 if k >= 32 else 16)
                pop[key] = pop.get(key, 0) + 1
            if v:
                vsite_pats.add(pi)
                if kind != "cls":
                    mixed_v += 1
            for layer in ("off", "on"):
                pfx = "w%d" % len(arts)
                c = os.path.join(work, pfx + ".c")
                flags = ["-fmemfn-simd=%s" % TARGET] if layer == "on" else ["-fno-memfn-simd"]
                r = run([pcrec, "-p", pfx, "--features", "all", "--window-search-width=%d" % width] + flags
                        + ["-o", c, "--pattern", rx], timeout=120)
                if r.returncode:
                    bad("whole %s at %d %s: pcrec refused: %s" % (rx, width, layer, r.stderr.decode()[-200:]))
                    continue
                txt = open(c, encoding="latin-1").read()
                # the kit's own answer beside the k source's: one walk call of a selector per V site,
                # and (SIMD-on only) one __w32 call in each selector
                calls = {int(m.group(1)) for m in re.finditer(r"\b%s_mf(\d+)_vs\d+\(%s_mf\1_s, %s_mf\1_c\)" % (pfx, pfx, pfx), txt)}
                w32 = len(re.findall(r"return %s_mf\d+_vs\d+__w32\(%s_mf\d+_s, %s_mf\d+_c\);" % (pfx, pfx, pfx), txt))
                want_w32 = len(v) if layer == "on" else 0
                if calls != set(v) or w32 != want_w32:
                    kit_disagree += 1
                    bad("whole %s at %d %s: the k source routes V at sites %s, the kit's text calls a selector at %s "
                        "(__w32 calls %d, %d expected)" % (rx, width, layer, sorted(v), sorted(calls), w32, want_w32))
                else:
                    ok()
                arts.append((pi, width, layer, pfx))
    print("G2VW patterns %d artifacts %d subjects %d (staircase %d)" % (len(pats), len(arts), len(subjects), nstair))
    print("G2VW population (k source, per pattern x width) " + " ".join(
        "%s/b%d=%d" % (r_, b_, pop.get((r_, b_), 0)) for r_, b_ in sorted(WHOLE_FLOORS)))
    print("G2VW mixed patterns x widths with a V site %d; kit/k-source disagreements %d" % (mixed_v, kit_disagree))
    for key, want in sorted(WHOLE_FLOORS.items()):
        floor("whole %s/b%d" % key, pop.get(key, 0), want)
    floor("whole mixed V", mixed_v, WHOLE_FLOOR_MIXED)
    floor("whole staircase subjects", nstair, WHOLE_FLOOR_STAIR)
    floor("whole subjects", len(subjects), WHOLE_FLOOR_SUBJECTS)
    # compile the artifacts and the driver
    import concurrent.futures as cf

    def comp(pfx):
        c = os.path.join(work, pfx + ".c")
        return pfx, run([cc(), "-std=gnu11", "-O2", "-w", "-I" + work, "-c", "-o", c[:-2] + ".o", c], timeout=600)
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G2V_JOBS", "6"))) as ex:
        for pfx, r in ex.map(comp, [x[3] for x in arts]):
            if r.returncode:
                bad("whole: artifact %s does not compile: %s" % (pfx, r.stderr.decode()[:300]))
                return
    tab = os.path.join(work, "vw_tab.c")
    with open(tab, "w") as f:
        f.write("#include <stddef.h>\ntypedef int (*vw_fn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);\n")
        for pi, w_, l_, pfx in arts:
            f.write("int %s_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);\n" % pfx)
        f.write("struct vw_art { int pat; vw_fn fn; };\nconst struct vw_art vw_arts[] = {\n")
        for pi, w_, l_, pfx in arts:
            f.write("    { %d, %s_search },\n" % (pi, pfx))
        f.write("};\nconst unsigned vw_narts = %d;\n" % len(arts))
    drv = os.path.join(work, "drv")
    r = run([cc(), "-std=gnu11", "-O1", "-w", os.path.join(g2, "g2_vwhole_drv.c"), tab]
            + [os.path.join(work, x[3] + ".o") for x in arts] + ["-o", drv], timeout=600)
    if r.returncode:
        bad("whole: the driver does not link: " + r.stderr.decode()[:400])
        return
    sfile = os.path.join(work, "subjects.bin")
    with open(sfile, "wb") as f:
        f.write(len(subjects).to_bytes(4, "little"))
        for pi, lab, sb in subjects:
            f.write(pi.to_bytes(4, "little") + len(sb).to_bytes(4, "little") + sb)
    r = run([drv, sfile], timeout=900)
    out = r.stdout.decode()
    if r.returncode == 4:
        print("SKIPPED ARM w32: %s; G2-V whole NOT run" % out.strip())
        bad("whole: the host cannot run the x86-64-v3 artifacts (a skip is not a pass)")
        return
    for m in re.finditer(r"^FAULT (\d+) (\d+) (\S+) (-?\d+) (\S+).*$", out, re.M):
        ai, si = int(m.group(1)), int(m.group(2))
        pi, w_, l_, pfx = arts[ai]
        bad("whole: %s at width %d, %s: subject %d (%s, %d bytes) flush %s FAULTS reading s[%s] (%s)"
            % (pats[pi][1], w_, l_, si, subjects[si][1], len(subjects[si][2]), m.group(3), m.group(4), m.group(5)))
    if r.returncode:
        bad("whole: the driver exited %d" % r.returncode)
    # the control: python re over the same pattern string
    exp = {}
    nmatch = 0
    for si, (pi, lab, sb) in enumerate(subjects):
        rxc = re.compile(pats[pi][1].encode("latin-1"))
        h = 1469598103934665603
        cnt = 0
        for mm in rxc.finditer(sb):
            cnt += 1
            for ch in ("%d,%d;" % (mm.start(), mm.end())).encode():
                h = ((h ^ ch) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        exp[si] = (cnt, "%016x" % h)
        if pi in vsite_pats:
            nmatch += cnt
    nrun = wrong = 0
    seen = set()
    for m in re.finditer(r"^M (\d+) (\d+) (\d) (-?\d+) (\d+) ([0-9a-f]{16})$", out, re.M):
        ai, si, place, rc, cnt, h = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), m.group(6)
        seen.add((ai, si, place))
        nrun += 1
        if rc or (cnt, h) != exp[si]:
            wrong += 1
            if wrong <= 12:
                pi, w_, l_, pfx = arts[ai]
                bad("whole: %s at width %d, %s: subject %d (%s) flush %s: %d matches (rc %d), re finds %d%s"
                    % (pats[pi][1], w_, l_, si, subjects[si][1], "high" if place else "low", cnt, rc, exp[si][0],
                       "" if cnt != exp[si][0] else " (other spans)"))
    want = sum(2 for ai, x in enumerate(arts) for si, s_ in enumerate(subjects) if s_[0] == x[0])
    if nrun != want:
        bad("whole: %d find-all runs answered, %d expected" % (nrun, want))
    elif not wrong:
        ok()
    print("G2VW find-all runs %d (both placements) wrong %d; matches over V-site patterns %d" % (nrun, wrong, nmatch))
    floor("whole matches", nmatch, WHOLE_FLOOR_MATCHES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["unit", "whole", "both"])
    ap.add_argument("--root", required=True)
    ap.add_argument("--lib", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--seed", type=int, default=20261122)
    a = ap.parse_args()
    if a.what in ("unit", "both"):
        unit(a)
    if a.what in ("whole", "both"):
        whole(a)
    print("checks passed: %d" % PASS[0])
    print("checks failed: %d" % FAIL[0])
    return 1 if FAIL[0] else 0


if __name__ == "__main__":
    sys.exit(main())
