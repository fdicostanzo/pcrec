#!/usr/bin/env python3
"""tests/codegen/reqcube_check.py -- [OPT-LITSCAN] S4 C3's structural checks on
THE CASELESS NECESSARY RUN (docs/design/litscan_s4.md §5.4; docs/spec/
tuning.md §2.28-§2.30, §2.39), run by run_codegen_tests.sh's
[OPT-LITSCAN S4 C3] block. Prints one `PASS: ...` / `FAIL: ...` line per check.

    python3 reqcube_check.py PCREC WORKDIR CC

The mechanism is ANSWER-IDENTITY-preserving, so the corpus cannot see a word
that reads a mask the fact does not carry behind a subject that never differs
there, a pair block that scans one member on an all-uppercase subject, a
search hoisted above the loop guard on a subject long enough to hold the run,
a REQ_BYTE that names T, or a non-canonical position whose stream happens to
coincide. Every expectation below is read from the `--emit-facts` listing
(the facts' ONE renderer, which the stamps share) and from the PATTERN TEXT,
never from the emitted C it checks:

  1. THE MASKED VERIFY SPELLS THE FACT: every word of the run pre-check's
     compare, masked `(w(b + o) & w("K")) == w("T")` or unmasked, covers ONE
     contiguous stretch [lo, hi) of the whole run (R-38 K38-2: the kit's
     verified extent; offsets are run positions, the candidate the
     occurrence's position 0; no byte of the stretch uncovered, none outside
     the run), the stretch holds the scan position, and the words' T and K
     constants decode to the whole run's bytes and mask there position by
     position; every constant is a string literal (never a byte-order
     statement).
  2. THE DISPATCH: a block whose scan position is a pair carries exactly two
     `memchr` calls, on A = T[k*] and B = A | ~K[k*], each stream's frontier
     raised to `pos + k*` (a hit below it is stale); a block whose scan
     position is exact carries one, on
     T[k*] (S453's shape is one memchr on an all-letter run).
  2b. ONE RUN PART (R-38 K38-2; R-30's implied window and [K66]'s second
     part retired): an emitted pre-check with a run carries ONE rx_reqrun
     block and no rx_reqrun_whole; where the facts put the run on a VM route
     with no prefilter (the route no DFA scan fronts, the need REQUIRED) its
     compare covers the WHOLE run ([K66]'s promise, now the kit's WHOLE
     mode), counted (>= 1, S448's witness among them).
  2c. C4 (span_runs_sheet.md §2.4): `<PREFIX>_REQ_RUN`'s `@` names the
     OFFSET the emitted run-part find scans (its `memchr(subject + pos + k`
     or pair frontier), on every emitted witness with a run block, counted.
  3. NO SEARCH OUTSIDE THE LOOP: every `memchr(` of a run block sits after the
     block's `while (pos + ` line (S454's detector).
  4. THE STAMPS: `<PREFIX>_REQ_RUN`'s hex and mask equal the `req_whole_run`
     fact's (the `@` is the searching site's, 2c); `REQ_BYTE` is a
     member of `req_set` or `"none"`, and equals `bytes[idx]` where
     `mask[idx]` is `ff` (S452); `REQ_WHY "none"` iff REQ_BYTE and REQ_RUN are
     both `"none"`; a masked run is never `REQ_WHY "none"` and is never pinned
     whole.
  5. K65 on the no-DFA-scan route lists every set member the whole run's
     EXACT positions do not prove (S451's detector, structurally).
  6. THE KEPT PINS: `a[bc]de` and `(?i)x/1234` keep `run-pinned` with the
     exact-stretch pins `2:2+2` and `1:1+5`, REQ_WHY `emitted` / `dominated`,
     and a prefilter block byte-identical to the one `-fno-req-run-fold`
     emits (the abi-58 program: the pin's term did not move).
  7. THE DENY: under `-fno-req-run-fold` no masked compare, no pair stream and
     no `/` suffix remain, and an exact-only artifact is byte-identical with
     and without the flag.
  8. THE CANONICAL FORM over every corpus pattern (as written, through
     `--list-source`): every masked `req_whole_run` position has
     `T & ~K == 0` and at most 128 members (popcount(K) >= 1; 7 or 8 before
     [RUN-POS-SET] stage 3's S2 landing); a set-form run (stage 3) holds a
     position that is not one cube and no bracketed position over 128
     members; the count of masked rows read is printed and floored (half the
     92 measured at landing, D110), so the check cannot pass on an empty
     population.
  9. Every witness compiles under the harness's own -Wall -Wextra -Werror.

Failing direction, recorded at the landing (docs/dev/lanes/c3build_report.md):
the sabotage rows planting S453 (dispatch), S454 (hoisted search), S452
(REQ_BYTE = T) and S455 (an upper-member hull) each turn their check red.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

PCREC, WORK, CC = sys.argv[1], sys.argv[2], sys.argv[3] or "cc"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
npass = nfail = 0


def ok(msg):
    global npass
    npass += 1
    print("PASS: [OPT-LITSCAN S4 C3] " + msg)


def bad(msg):
    global nfail
    nfail += 1
    print("FAIL: [OPT-LITSCAN S4 C3] " + msg)


# D172 S3: every witness here is compiled under the `cover` row's deny,
# `--memfn=no-window-search` (registry.md §6¶8a): a fixed-width witness is a `cover`
# artifact by default, whose search is the memfn kit's window site, not the
# offset-skip block this check reads; the deny renders the default build
# before S3, the artifact this check was written against.
COVER_DENY = "--memfn=no-window-search"


def emit(tag, pat, *flags):
    out = os.path.join(WORK, "rq_" + tag + ".c")
    r = subprocess.run([PCREC, "--features", "all", "-p", "rx", COVER_DENY, *flags, "-o", out,
                        "--pattern", pat], capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    return out, open(out, encoding="latin-1").read()


def facts(pat, *flags):
    """The record's facts (7-column rows) and the listing's `decisions` stamps
    (3-column `RX_*` rows, the route the record does not hold), first encoding
    only; compiled under the same deny as emit() so the route is the same."""
    r = subprocess.run([PCREC.encode(), b"--features", b"all", COVER_DENY.encode(), b"--emit-facts",
                        *[f.encode() for f in flags], b"--pattern", pat],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    d = {}
    for ln in r.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] not in d:
            d[f[1]] = f[6]
        elif len(f) == 3 and f[1].startswith("RX_") and f[1] not in d:
            d[f[1]] = f[2].strip('"')
    return d


def cube_of(members):
    """The covering cube (T, K) of a member set, and whether it IS that cube."""
    t, o = 0xFF, 0
    for b in members:
        t &= b; o |= b
    k = ~(t ^ o) & 0xFF
    return t, k, len(members) == 1 << (8 - bin(k).count("1"))


def parse_run(v):
    """A run's spelling (tuning.md §2.28¶7, facts_listing.md §4.1.2¶1) ->
    (T bytes, K bytes, idx or None, per-position member sets, set_form).
    `hex@idx[/mask]` or `hex[/mask]` where every position is one cube; else
    ([RUN-POS-SET] stage 3) each position of two or more members a bracketed
    hex class (`[61-7a]`, `[cecf]`, `[80-89b1-bf]`) and no `/`. T and K are each
    position's covering cube (exact where the position IS a cube); None for an
    unreadable spelling."""
    if v in (None, "", "none", "-"):
        return None
    m = re.match(r"^((?:[0-9a-f]{2}|\[(?:[0-9a-f]{2}(?:-[0-9a-f]{2})?)+\])+)(?:@(\d+))?(?:/([0-9a-f]+))?$", v)
    if not m:
        return None
    sets, setform = [], "[" in m.group(1)
    for tok in re.findall(r"\[[^\]]*\]|[0-9a-f]{2}", m.group(1)):
        if tok[0] == "[":
            mem = set()
            for lo, hi in re.findall(r"([0-9a-f]{2})(?:-([0-9a-f]{2}))?", tok):
                mem |= set(range(int(lo, 16), int(hi or lo, 16) + 1))
            sets.append(frozenset(mem))
        else:
            sets.append(frozenset([int(tok, 16)]))
    if m.group(3):
        if setform:
            return None
        t, k = bytes.fromhex(m.group(1)), bytes.fromhex(m.group(3))
        if len(k) != len(t):
            return None
        sets = [frozenset(b for b in range(256) if b & kk == tt) for tt, kk in zip(t, k)]
    else:
        t = bytes(cube_of(x)[0] for x in sets)
        k = bytes(cube_of(x)[1] for x in sets)
    return t, k, int(m.group(2)) if m.group(2) is not None else None, sets, setform


def cdecode(lit):
    b, i = bytearray(), 0
    while i < len(lit):
        ch = lit[i]
        if ch == "\\":
            nx = lit[i + 1]
            if nx in "01234567":
                b.append(int(lit[i + 1:i + 4], 8))
                i += 4
                continue
            b.append({"n": 10, "t": 9, "r": 13}.get(nx, ord(nx)))
            i += 2
            continue
        b.append(ord(ch))
        i += 1
    return bytes(b)


LIT = r'"((?:[^"\\]|\\.)*)"'
MWORD = re.compile(r'\(rx_w([248])\(subject \+ cand(?: \+ (\d+))?\) & rx_w\1\(' + LIT +
                   r'\)\) == rx_w\1\(' + LIT + r'\)')
UWORD = re.compile(r'rx_w([248])\(subject \+ cand(?: \+ (\d+))?\) == rx_w\1\(' + LIT + r'\)')
INTLIT = re.compile(r'rx_w[248]\([^()]*\)\)? (?:==|&) (?:0x|[0-9])')


def block(text, name):
    """The text of function <name>'s LOOP up to its closing brace: since
    R4e'.0b (D155 item 6) the loop is the helper `<name>__body` and <name>
    itself is a one-call selector."""
    i = text.find("static inline size_t %s__body(" % name)
    if i < 0:
        return None
    j = text.find("\n}\n", i)
    return text[i:j + 3]


def check_block(label, blk, t, k, scan_k):
    L = len(t)
    lines = blk.split("\n")
    wl = [n for n, ln in enumerate(lines) if ln.lstrip().startswith("while (pos + ")]
    ml = [n for n, ln in enumerate(lines) if "memchr(" in ln]
    if not wl:
        bad(f"{label}: no `while (pos + ` guard line in the block")
        return None
    if any(n < wl[0] for n in ml):
        bad(f"{label}: a memchr( sits ABOVE the block's `while (pos + ` guard -- a search outside the loop (S454)")
    else:
        ok(f"{label}: all {len(ml)} memchr( calls sit inside the guarded loop")
    # one memchr per stream: from `pos [+ k]` (one stream), or from the stream's frontier
    # `ha`/`hb` in its bounded look-ahead (the pair arm, kit ofsskip.c ofs_pair_text)
    consts = [int(x) for x in re.findall(r"memchr\(subject \+ (?:pos(?: \+ \d+)?|h[ab]), (\d+),", blk)]
    a = t[scan_k]
    if k[scan_k] != 0xFF:
        b = a | (~k[scan_k] & 0xFF)
        kk = "pos + %d" % scan_k if scan_k else "pos"
        if sorted(consts) != sorted([a, b]):
            bad(f"{label}: the pair position {scan_k} is scanned on {consts}, expected both members {a} and {b} (S453 scans T alone)")
        elif ("if (ha < %s) ha = %s;" % (kk, kk)) not in blk or ("if (hb < %s) hb = %s;" % (kk, kk)) not in blk:
            bad(f"{label}: a stream's frontier is not raised to `{kk}` (S449/S450's `pos` hangs)")
        else:
            ok(f"{label}: the pair position {scan_k} is two streams ({a}, {b}), each frontier raised to `{kk}`")
    else:
        if consts != [a]:
            bad(f"{label}: the exact scan position {scan_k} is scanned on {consts}, expected one memchr of {a}")
        else:
            ok(f"{label}: the exact scan position {scan_k} is one memchr of {a}")
    words = []
    for m in MWORD.finditer(blk):
        words.append((int(m.group(2) or 0), int(m.group(1)), cdecode(m.group(4)), cdecode(m.group(3))))
    for m in UWORD.finditer(blk):
        w = int(m.group(1))
        words.append((int(m.group(2) or 0), w, cdecode(m.group(3)), b"\xff" * w))
    words.sort()
    if INTLIT.search(blk):
        bad(f"{label}: a word is compared or masked against an INTEGER literal -- a byte-order assumption")
    if not words:
        bad(f"{label}: no word compare in the verify (the masked run took no `words` row)")
        return None
    w = words[0][1]
    offs = [o for o, _, _, _ in words]
    lo, hi = offs[0], offs[-1] + w
    if any(x[1] != w for x in words) or lo < 0 or hi > L or not lo <= scan_k < hi \
            or any(b2 > a2 + w for a2, b2 in zip(offs, offs[1:])):
        bad(f"{label}: word offsets {offs} (W={w}) for a {L}-position run -- one contiguous stretch "
            f"inside the run, holding the scan position {scan_k}")
        return None
    st, sk = bytearray(hi - lo), bytearray(hi - lo)
    for o, ww, tb, kb in words:
        st[o - lo:o - lo + ww] = tb
        sk[o - lo:o - lo + ww] = kb
    if bytes(st) != t[lo:hi] or bytes(sk) != k[lo:hi]:
        bad(f"{label}: the words spell T={bytes(st).hex()} K={bytes(sk).hex()}, the fact is "
            f"T={t[lo:hi].hex()} K={k[lo:hi].hex()} over [{lo},{hi})")
        return None
    nm = sum(1 for x in words if x[3] != b"\xff" * w)
    ok(f"{label}: {len(words)} words of {w} at {offs} spell the whole run's T and K over [{lo},{hi}) "
       f"({nm} masked, {len(words) - nm} unmasked)")
    return lo, hi


# (tag, pattern, flags)
WIT = [
    ("select", "(?i)select", ()),
    ("selvm", "(?i)select", ("--engine=vm",)),
    ("union", "(?i)union.*?select.*?from", ()),
    ("k66", r"(x?)(?i:abcdefghijkl)\1", ()),
    # s2b/s2c: `S` must sit OUTSIDE the run, so the byte between carries no
    # information (`.`); they read `S\d` until [RUN-POS-SET] stage 3's S2
    # landing made `\d` a run position (`S` joined the run as an exact byte)
    ("s2b", r"(x?)([a-z]+)+S.(?i:select)\1", ()),
    ("s2c", r"(x?)([a-z]+)+S.(?i:s)qz\1", ()),
    ("s2a", r"(?i:select)\d+x", ()),
    ("mixed", "[0-9]+(?i:a)bcdefg", ()),
    ("abcde", "a[bc]de", ()),
    ("x1234", "(?i)x/1234", ()),
    ("frank", "frank|fred", ()),
    ("gcon", "(?i)group_concat", ()),
]

n_whole_route = 0
n_c4 = 0
n_setform = 0
for tag, pat, flags in WIT:
    got = emit(tag, pat, *flags)
    fx = facts(pat.encode(), *flags)
    if got is None or fx is None:
        bad(f"'{pat}' {' '.join(flags)}: refused")
        continue
    path, text = got
    st = dict(re.findall(r'^#define RX_(REQ_\w+|DFA_PREFILTER) "(.*)"$', text, re.M))
    whole = parse_run(fx.get("req_whole_run"))   # the `req_run` row retired (F5)
    rset = set() if fx.get("req_set") in ("none", None) else {int(x) for x in fx["req_set"].split(",")}
    lbl = f"'{pat}'" + (" " + " ".join(flags) if flags else "")
    # 4. the stamps (the hex and mask are the whole run's; `@` is 2c's)
    srun = parse_run(st.get("REQ_RUN"))
    if (srun is None) != (whole is None) or (srun and srun[3] != whole[3]):
        bad(f"{lbl}: RX_REQ_RUN '{st.get('REQ_RUN')}' does not spell the req_whole_run fact '{fx.get('req_whole_run')}'")
    rb = st.get("REQ_BYTE", "none")
    if rb != "none" and int(rb) not in rset:
        bad(f"{lbl}: RX_REQ_BYTE {rb} is not a member of req_set {sorted(rset)} (S452's shape)")
    elif rb != fx.get("req_byte", "none"):
        bad(f"{lbl}: RX_REQ_BYTE {rb} is not the req_byte fact {fx.get('req_byte')} (one home, F10)")
    else:
        ok(f"{lbl}: RX_REQ_BYTE {rb} is a req_set member (or none), and the req_byte fact")
    why = st.get("REQ_WHY")
    if (why == "none") != (rb == "none" and st.get("REQ_RUN") == "none"):
        bad(f"{lbl}: RX_REQ_WHY '{why}' against REQ_BYTE '{rb}' / REQ_RUN '{st.get('REQ_RUN')}' -- 'none' must hold iff both are none")
    elif whole and any(len(x) > 1 for x in whole[3]) and (why == "none" or fx.get("run_pin") not in ("none", "", None)
                                                      and ":" not in fx.get("run_pin", "")):
        bad(f"{lbl}: a masked run reads REQ_WHY '{why}' / run_pin '{fx.get('run_pin')}' (never none, never pinned whole)")
    else:
        ok(f"{lbl}: REQ_WHY '{why}' consistent with REQ_BYTE/REQ_RUN, run_pin '{fx.get('run_pin')}'")
    # 1-3, 2b, 2c. the one run block. The WHOLE-run route is read from the
    # FACTS listing (the engine and VM_PREFILTER decisions), never from the
    # text checked.
    whole_route = bool(whole and fx.get("RX_ENGINE") == "vm" and fx.get("RX_VM_PREFILTER") == "none")
    if whole and why == "emitted":
        b0 = block(text, "rx_reqrun")
        if block(text, "rx_reqrun_whole") is not None:
            bad(f"{lbl}: a second run part (rx_reqrun_whole) is still emitted (K38-2: one run part)")
        if b0 is None:
            bad(f"{lbl}: REQ_WHY emitted with a run, but no rx_reqrun block")
        else:
            # the scan offset: one stream's `memchr(subject + pos [+ k]`, or the pair arm's
            # frontier raise `if (ha < pos [+ k])`
            m = re.search(r"memchr\(subject \+ pos(?: \+ (\d+))?,", b0) or \
                re.search(r"if \(ha < pos(?: \+ (\d+))?\)", b0)
            at = int(m.group(1) or 0) if m else -1
            # 2c, C4: the stamp's `@` is that offset
            if srun is None or srun[2] != at:
                bad(f"{lbl}: RX_REQ_RUN's @ {srun[2] if srun else None} is not the run block's scan offset {at} (C4)")
            else:
                n_c4 += 1
                ok(f"{lbl}: RX_REQ_RUN's @{at} is the run block's scan offset (C4)")
            if whole[4]:
                # [RUN-POS-SET] stage 3: a run with a position that is not one
                # cube is verified by the memfn kit's set test (Part D), not by
                # the masked words checks 1-2 read; counted, never checked here.
                n_setform += 1
            elif whole[1] != b"\xff" * len(whole[1]):
                ext = check_block(f"{lbl} rx_reqrun", b0, whole[0], whole[1], at)
                if whole_route:
                    if ext != (0, len(whole[0])):
                        bad(f"{lbl}: on the route no DFA scan fronts, the run part verifies {ext}, "
                            f"not the whole run [0,{len(whole[0])}) (S448)")
                    else:
                        n_whole_route += 1
                        ok(f"{lbl}: the route no DFA scan fronts verifies the whole run")
        if tag == "k66" and (b0 is None or "&" not in b0 or not whole_route):
            bad(f"{lbl}: the K66 site's run block is missing, compares unmasked, or is not on the whole-run route (S448)")
    # 5. K65's rest on the no-DFA-scan route
    # [K82] a member tested by the set-leads row's one-byte check (the first
    # `!memchr(..., B, ...)` above the run call) is tested too, and K65's
    # rest skips it. s2b's 'S' (4203 ppm) is rarer than its run's scan pair,
    # so it LEADS; s2c's 'S' is commoner than its exact scan byte 'z' (498),
    # so it stays in rq_set -- the witness where a pair position's T marked
    # done (S452) still drops it.
    if tag in ("s2b", "s2c"):
        m = re.search(r"rq_set\[\] = \{([^}]*)\}", text)
        got_set = {int(x) for x in m.group(1).split(",")} if m else set()
        call = text.find("rx_reqrun(subject")
        lm = re.search(r"!memchr\([a-z_]+ \+ [a-z_]+, (\d+),", text[:call]) if call >= 0 else None
        lead = {int(lm.group(1))} if lm else set()
        exact = {next(iter(x)) for x in whole[3] if len(x) == 1} if whole else set()
        want = rset - exact
        where = {"s2b": lead, "s2c": got_set}[tag]
        if want <= got_set | lead and 83 in where:
            ok(f"{lbl}: every set member no exact whole-run position proves is tested (lead {sorted(lead)}, "
               f"K65's rq_set {sorted(got_set)}; 83, 'S', in the {'lead' if tag == 's2b' else 'rq_set'})")
        else:
            bad(f"{lbl}: lead {sorted(lead)} / K65's rq_set {sorted(got_set)} lack {sorted(want - got_set - lead)} "
                f"or 'S' (83) is not where it belongs -- a masked position marked done (S451/S452) or the lead lost")
    if tag == "s2a" and rb != "120":
        bad(f"{lbl}: RX_REQ_BYTE reads {rb}, want 120 ('x', the set's pick; the run's scan member is a pair)")
    if tag == "union" and not (rb == "none" and why == "emitted" and fx.get("run_pin") == "none"):
        bad(f"{lbl}: want REQ_BYTE none, REQ_WHY emitted, run_pin none; got {rb}, {why}, {fx.get('run_pin')}")
    # 6. the kept pins
    if tag in ("abcde", "x1234"):
        want = {"abcde": ("2:2+2", "emitted"), "x1234": ("1:1+5", "dominated")}[tag]
        if st.get("DFA_PREFILTER") != "run-pinned" or fx.get("run_pin") != want[0] or why != want[1]:
            bad(f"{lbl}: want run-pinned / run_pin {want[0]} / REQ_WHY {want[1]}; got "
                f"{st.get('DFA_PREFILTER')} / {fx.get('run_pin')} / {why}")
        else:
            ok(f"{lbl}: run-pinned on the exact stretch {want[0]}, REQ_WHY {want[1]}")
        den = emit(tag + "_deny", pat, *flags, "-fno-req-run-fold")
        if den is None or block(den[1], "rx_ofsskip") != block(text, "rx_ofsskip") or block(text, "rx_ofsskip") is None:
            bad(f"{lbl}: the rx_ofsskip block differs from -fno-req-run-fold's (the pin's term moved)")
        else:
            ok(f"{lbl}: the rx_ofsskip block is byte-identical to -fno-req-run-fold's (the abi-58 prefilter)")
    # 7. the deny
    den = emit(tag + "_d", pat, *flags, "-fno-req-run-fold")
    if den is None:
        bad(f"{lbl} -fno-req-run-fold: refused")
    else:
        dt = den[1]
        drun = re.search(r'^#define RX_REQ_RUN "(.*)"$', dt, re.M)
        if (drun and "/" in drun.group(1)) or "ha < " in dt or MWORD.search(dt):
            bad(f"{lbl} -fno-req-run-fold: a masked run, a pair stream or a masked word survives the deny")
        else:
            ok(f"{lbl} -fno-req-run-fold: no masked run, pair stream or masked word")
    # 9. compiles
    r = subprocess.run([CC, "-O1", "-Wall", "-Wextra", "-Werror", "-c", "-o", path + ".o", path],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        bad(f"{lbl}: does not compile under -Wall -Wextra -Werror: {r.stderr.strip()[:300]}")
    else:
        ok(f"{lbl}: compiles under -Wall -Wextra -Werror")

# 7b. an exact-only artifact is byte-identical with and without the flag
# ctl1 read `[0-9]+abcdef` until stage 3 made `[0-9]` a run position (a set
# position moves under -fno-req-run-fold); `.` keeps the run exact
for tag, pat in (("ctl1", ".+abcdef"), ("ctl2", "/user|/users"), ("ctl3", "(?i)ab")):
    a, d = emit(tag, pat), emit(tag + "_d", pat, "-fno-req-run-fold")
    if a is None or d is None:
        bad(f"control '{pat}': refused")
    elif a[1].replace("rq_" + tag + ".", "X.") != d[1].replace("rq_" + tag + "_d.", "X."):
        bad(f"control '{pat}': the artifact moves under -fno-req-run-fold though its run is exact")
    else:
        ok(f"control '{pat}': byte-identical with and without -fno-req-run-fold (an exact run)")


# 2c's REACHING regime (span_runs_sheet.md §2.4 C4 (b) under (a)): the probe
# lever `run-tie-left` (the harness build only) breaks the kit's run-decision
# ties LEFTMOST while pcrec's own index (its pick over the run, the
# `req_byte` fact's input: the DEFAULT build's `@`, both tying rightmost
# there; the listing's `req_run` row and its `@idx` retired, F5) stays
# rightmost, so a stamp fed pcrec's index names the wrong offset there. Each
# witness ties on the SAME byte at two positions, so the offset (not only
# the set) is what is checked; the reach is counted: the lever's `@` must
# differ from the default build's on at least one.
HARNESS = os.path.join(os.path.dirname(PCREC), "pcrec-harness")
n_reach = 0
for tag, pat in (("c4t1", "a.*zqxzqx"), ("c4t2", "a.*(?i:selectselect)")):
    out = os.path.join(WORK, "rq_" + tag + ".c")
    r = subprocess.run([HARNESS, "--harness=run-tie-left", "--features", "all", "-p", "rx", COVER_DENY,
                        "-o", out, "--pattern", pat], capture_output=True, timeout=120)
    dflt = emit("d" + tag, pat)
    if r.returncode != 0 or dflt is None:
        bad(f"C4 lever '{pat}': refused")
        continue
    text = open(out, encoding="latin-1").read()
    st = dict(re.findall(r'^#define RX_(REQ_\w+) "(.*)"$', text, re.M))
    dst = dict(re.findall(r'^#define RX_(REQ_\w+) "(.*)"$', dflt[1], re.M))
    srun, frun = parse_run(st.get("REQ_RUN")), parse_run(dst.get("REQ_RUN"))
    b0 = block(text, "rx_reqrun")
    m = b0 and (re.search(r"memchr\(subject \+ pos(?: \+ (\d+))?,", b0) or
                re.search(r"if \(ha < pos(?: \+ (\d+))?\)", b0))
    at = int(m.group(1) or 0) if m else -1
    if st.get("REQ_WHY") != "emitted" or srun is None or srun[2] != at:
        bad(f"C4 lever '{pat}': REQ_WHY {st.get('REQ_WHY')}, @ {srun[2] if srun else None}, "
            f"the run block scans offset {at}")
    else:
        n_reach += frun is None or srun[2] != frun[2]
        ok(f"C4 lever '{pat}': @{at} is the run block's scan offset (the default build's {frun[2] if frun else None})")
(ok if n_reach >= 1 else bad)(f"C4 lever reach: {n_reach} witness(es) where the kit's offset is not "
                              f"pcrec's index (floor 1)")


# 2b/2c's populations: a masked whole-run witness on the route no DFA scan
# fronts (k66), and the C4 witnesses. Either at zero means its branch went
# unread, so the check could not fail in that direction.
if n_whole_route < 1 or n_c4 < 3:
    bad(f"populations: {n_whole_route} whole-route witness(es) (floor 1), {n_c4} C4 witness(es) (floor 3)")
else:
    ok(f"populations: {n_whole_route} whole-route witness(es), {n_c4} C4 witness(es)")


# 8. the canonical form over the whole corpus, as written
def dec_field(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9); i += 2; continue
            if n == 0x6e: out.append(10); i += 2; continue
            if n == 0x72: out.append(13); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)


rows = set()
for r_, _d, fs in os.walk(os.path.join(ROOT, "tests")):
    for f in fs:
        if not f.endswith(".rxt"):
            continue
        r = subprocess.run([PCREC, "--list-source", os.path.join(r_, f)], capture_output=True, timeout=120)
        if r.returncode:
            continue
        for ln in r.stdout.split(b"\n"):
            fl = ln.split(b"\t")
            if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"):
                continue
            pat = dec_field(fl[4])
            if not pat or b"\0" in pat:
                continue
            args = []
            if b"i" in fl[5]: args.append("-i")
            if b"u" in fl[5]: args.append("--ucp")
            if fl[8]: args += ["-e", fl[8].decode()]
            rows.add((pat, tuple(args)))

with ThreadPoolExecutor(int(os.environ.get("PROCS", "4"))) as ex:
    res = list(ex.map(lambda pa: facts(pa[0], *pa[1]), sorted(rows)))
nmask = nset = nbadc = 0
for (pat, args), fx in zip(sorted(rows), res):
    if fx is None:
        continue
    for key in ("req_whole_run",):     # the `req_run` row retired (F5)
        v = fx.get(key)
        pr = parse_run(v)
        if v not in (None, "", "none", "-") and pr is None:
            nbadc += 1
            bad(f"canonical form: '{pat[:60]!r}' {key} {v} is not a run spelling (tuning.md §2.28¶7)")
            continue
        if not pr or all(len(x) == 1 for x in pr[3]):
            continue
        if pr[4]:
            # [RUN-POS-SET] stage 3: the set form is used only where some
            # position is NOT one cube, and every bracketed position holds 2-128
            # members (a position carrying information, PCREC_MAX_REQ_RUN_POS_SET)
            nset += 1
            wide = [x for x in pr[3] if len(x) > 1]
            if all(cube_of(x)[2] for x in wide) or any(len(x) > 128 for x in wide):
                nbadc += 1
                bad(f"canonical form: '{pat[:60]!r}' {key} {v} is set-spelled but every position is one cube, "
                    f"or a position holds more than 128 members")
            continue
        nmask += 1
        for tt, kk in zip(pr[0], pr[1]):
            # a cube carrying information: canonical T, at most 128 members
            if tt & ~kk & 0xFF or bin(kk).count("1") < 1:
                nbadc += 1
                bad(f"canonical form: '{pat[:60]!r}' {key} {v} has a position "
                    f"T={tt:02x} K={kk:02x} (T & ~K must be 0, popcount(K) at least 1)")
                break
FLOOR = 46
if nbadc == 0 and nmask >= FLOOR:
    ok(f"canonical form: {nmask} masked and {nset} set-form req_whole_run rows over {len(rows)} corpus "
       f"patterns, every cube position T & ~K == 0 with at most 128 members, every set form holding a "
       f"position that is not one cube (floor {FLOOR} masked)")
elif nmask < FLOOR:
    bad(f"canonical form: only {nmask} masked rows read over {len(rows)} corpus patterns, under the floor "
        f"{FLOOR} -- the population this check exists for has shrunk or the walk stopped producing cubes")
print(f"REACH: reqcube_check: {n_setform} emitted witness run(s) in the set form (verified by the kit's set test, outside checks 1-2)")

print(f"reqcube_check: {npass} passed, {nfail} failed")
sys.exit(1 if nfail else 0)
