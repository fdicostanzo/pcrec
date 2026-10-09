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
     compare, masked `(w(b + o) & w("K")) == w("T")` or unmasked, lies inside
     the run (first at 0, last at exactly L - W, no byte uncovered), and the
     words' T and K constants decode to the fact's bytes and mask position by
     position; every constant is a string literal (never a byte-order
     statement).
  2. THE DISPATCH: a block whose scan position is a pair carries exactly two
     `memchr` calls, on A = T[k*] and B = A | ~K[k*], each re-searched iff its
     hit is `< pos + k*`; a block whose scan position is exact carries one, on
     T[k*] (S453's shape is one memchr on an all-letter run).
  3. NO SEARCH OUTSIDE THE LOOP: every `memchr(` of a run block sits after the
     block's `while (pos + ` line (S454's detector).
  4. THE STAMPS: `<PREFIX>_REQ_RUN` equals the `req_run` fact; `REQ_BYTE` is a
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
     `--list-source`): every masked `req_run`/`req_whole_run` position has
     `T & ~K == 0` and `popcount(K)` 7 or 8; the count of masked rows read is
     printed and floored (half the 92 measured at landing, D110), so the
     check cannot pass on an empty population.
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


def emit(tag, pat, *flags):
    out = os.path.join(WORK, "rq_" + tag + ".c")
    r = subprocess.run([PCREC, "--features", "all", "-p", "rx", *flags, "-o", out,
                        "--pattern", pat], capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    return out, open(out, encoding="latin-1").read()


def facts(pat, *flags):
    r = subprocess.run([PCREC.encode(), b"--features", b"all", b"--emit-facts",
                        *[f.encode() for f in flags], b"--pattern", pat],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    d = {}
    for ln in r.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] not in d:
            d[f[1]] = f[6]
    return d


def parse_run(v):
    """`hex@idx[/mask]` or `hex[/mask]` -> (T bytes, K bytes, idx or None)."""
    if v in (None, "", "none", "-"):
        return None
    m = re.match(r"^([0-9a-f]+)(?:@(\d+))?(?:/([0-9a-f]+))?$", v)
    t = bytes.fromhex(m.group(1))
    k = bytes.fromhex(m.group(3)) if m.group(3) else b"\xff" * len(t)
    return t, k, int(m.group(2)) if m.group(2) is not None else None


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
        return
    if any(n < wl[0] for n in ml):
        bad(f"{label}: a memchr( sits ABOVE the block's `while (pos + ` guard -- a search outside the loop (S454)")
    else:
        ok(f"{label}: all {len(ml)} memchr( calls sit inside the guarded loop")
    consts = [int(x) for x in re.findall(r"memchr\(subject \+ pos(?: \+ \d+)?, (\d+),", blk)]
    a = t[scan_k]
    if k[scan_k] != 0xFF:
        b = a | (~k[scan_k] & 0xFF)
        kk = "pos + %d" % scan_k if scan_k else "pos"
        if sorted(consts) != sorted([a, b]):
            bad(f"{label}: the pair position {scan_k} is scanned on {consts}, expected both members {a} and {b} (S453 scans T alone)")
        elif ("fresh || ha < %s)" % kk) not in blk or ("fresh || hb < %s)" % kk) not in blk:
            bad(f"{label}: a stream's re-search condition is not `< {kk}` (S449's `< pos` hangs)")
        else:
            ok(f"{label}: the pair position {scan_k} is two streams ({a}, {b}), each re-searched iff `< {kk}`")
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
        return
    w = words[0][1]
    offs = [o for o, _, _, _ in words]
    if any(x[1] != w for x in words) or offs[0] != 0 or offs[-1] != L - w \
            or any(o + w > L for o in offs) or any(b2 > a2 + w for a2, b2 in zip(offs, offs[1:])):
        bad(f"{label}: word offsets {offs} (W={w}) for a {L}-position run -- first 0, last L - W = {L - w}, none outside")
        return
    st, sk = bytearray(L), bytearray(L)
    for o, ww, tb, kb in words:
        st[o:o + ww] = tb
        sk[o:o + ww] = kb
    if bytes(st) != t or bytes(sk) != k:
        bad(f"{label}: the words spell T={bytes(st).hex()} K={bytes(sk).hex()}, the fact is T={t.hex()} K={k.hex()}")
        return
    nm = sum(1 for x in words if x[3] != b"\xff" * w)
    ok(f"{label}: {len(words)} words of {w} at {offs} spell the fact's T and K exactly ({nm} masked, "
       f"{len(words) - nm} unmasked), the last at L - W")


# (tag, pattern, flags)
WIT = [
    ("select", "(?i)select", ()),
    ("selvm", "(?i)select", ("--engine=vm",)),
    ("union", "(?i)union.*?select.*?from", ()),
    ("k66", r"(x?)(?i:abcdefghijkl)\1", ()),
    ("s2b", r"(x?)([a-z]+)+S\d(?i:select)\1", ()),
    ("s2c", r"(x?)([a-z]+)+S\d(?i:s)qz\1", ()),
    ("s2a", r"(?i:select)\d+x", ()),
    ("mixed", "[0-9]+(?i:a)bcdefg", ()),
    ("abcde", "a[bc]de", ()),
    ("x1234", "(?i)x/1234", ()),
    ("frank", "frank|fred", ()),
    ("gcon", "(?i)group_concat", ()),
]

for tag, pat, flags in WIT:
    got = emit(tag, pat, *flags)
    fx = facts(pat.encode(), *flags)
    if got is None or fx is None:
        bad(f"'{pat}' {' '.join(flags)}: refused")
        continue
    path, text = got
    st = dict(re.findall(r'^#define RX_(REQ_\w+|DFA_PREFILTER) "(.*)"$', text, re.M))
    run, whole = parse_run(fx.get("req_run")), parse_run(fx.get("req_whole_run"))
    rset = set() if fx.get("req_set") in ("none", None) else {int(x) for x in fx["req_set"].split(",")}
    lbl = f"'{pat}'" + (" " + " ".join(flags) if flags else "")
    # 4. the stamps
    if st.get("REQ_RUN") != fx.get("req_run"):
        bad(f"{lbl}: RX_REQ_RUN '{st.get('REQ_RUN')}' differs from the req_run fact '{fx.get('req_run')}'")
    rb = st.get("REQ_BYTE", "none")
    if rb != "none" and int(rb) not in rset:
        bad(f"{lbl}: RX_REQ_BYTE {rb} is not a member of req_set {sorted(rset)} (S452's shape)")
    elif run and run[1][run[2]] == 0xFF and rb != str(run[0][run[2]]):
        bad(f"{lbl}: the run's scan member is exact, yet RX_REQ_BYTE {rb} is not bytes[idx] = {run[0][run[2]]}")
    else:
        ok(f"{lbl}: RX_REQ_BYTE {rb} is a req_set member (or none), bytes[idx] only at an exact scan member")
    why = st.get("REQ_WHY")
    if (why == "none") != (rb == "none" and st.get("REQ_RUN") == "none"):
        bad(f"{lbl}: RX_REQ_WHY '{why}' against REQ_BYTE '{rb}' / REQ_RUN '{st.get('REQ_RUN')}' -- 'none' must hold iff both are none")
    elif run and run[1] != b"\xff" * len(run[1]) and (why == "none" or fx.get("run_pin") not in ("none", "", None)
                                                      and ":" not in fx.get("run_pin", "")):
        bad(f"{lbl}: a masked run reads REQ_WHY '{why}' / run_pin '{fx.get('run_pin')}' (never none, never pinned whole)")
    else:
        ok(f"{lbl}: REQ_WHY '{why}' consistent with REQ_BYTE/REQ_RUN, run_pin '{fx.get('run_pin')}'")
    # 1-3. the blocks
    if run and why == "emitted":
        b0 = block(text, "rx_reqrun")
        if b0 is None:
            bad(f"{lbl}: REQ_WHY emitted with a run, but no rx_reqrun block")
        elif run[1] != b"\xff" * len(run[1]):
            check_block(f"{lbl} rx_reqrun", b0, run[0], run[1], run[2])
        b1 = block(text, "rx_reqrun_whole")
        if b1 is not None and whole:
            at = int(re.search(r"memchr\(subject \+ pos(?: \+ (\d+))?,", b1).group(1) or 0)
            check_block(f"{lbl} rx_reqrun_whole", b1, whole[0], whole[1], at)
        if tag == "k66" and (b1 is None or "&" not in b1):
            bad(f"{lbl}: the K66 site's whole-run block is missing or compares unmasked (S448)")
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
        exact = {whole[0][i] for i in range(len(whole[0])) if whole[1][i] == 0xFF} if whole else set()
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
for tag, pat in (("ctl1", "[0-9]+abcdef"), ("ctl2", "/user|/users"), ("ctl3", "(?i)ab")):
    a, d = emit(tag, pat), emit(tag + "_d", pat, "-fno-req-run-fold")
    if a is None or d is None:
        bad(f"control '{pat}': refused")
    elif a[1].replace("rq_" + tag + ".", "X.") != d[1].replace("rq_" + tag + "_d.", "X."):
        bad(f"control '{pat}': the artifact moves under -fno-req-run-fold though its run is exact")
    else:
        ok(f"control '{pat}': byte-identical with and without -fno-req-run-fold (an exact run)")


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
nmask = nbadc = 0
for (pat, args), fx in zip(sorted(rows), res):
    if fx is None:
        continue
    for key in ("req_run", "req_whole_run"):
        pr = parse_run(fx.get(key))
        if not pr or pr[1] == b"\xff" * len(pr[1]):
            continue
        nmask += 1
        for tt, kk in zip(pr[0], pr[1]):
            if tt & ~kk & 0xFF or bin(kk).count("1") not in (7, 8):
                nbadc += 1
                bad(f"canonical form: '{pat[:60]!r}' {key} {fx.get(key)} has a position "
                    f"T={tt:02x} K={kk:02x} (T & ~K must be 0, popcount(K) 7 or 8)")
                break
FLOOR = 46
if nbadc == 0 and nmask >= FLOOR:
    ok(f"canonical form: {nmask} masked req_run/req_whole_run rows over {len(rows)} corpus patterns, "
       f"every position T & ~K == 0 and popcount(K) 7 or 8 (floor {FLOOR})")
elif nmask < FLOOR:
    bad(f"canonical form: only {nmask} masked rows read over {len(rows)} corpus patterns, under the floor "
        f"{FLOOR} -- the population this check exists for has shrunk or the walk stopped producing cubes")

print(f"reqcube_check: {npass} passed, {nfail} failed")
sys.exit(1 if nfail else 0)
