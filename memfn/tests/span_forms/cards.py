#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (lane forms, R-45 plan A; lane formsfixa,
# review 2026-11-17 r35's F2-F11).
"""memfn/tests/span_forms/cards.py -- THE SPAN FORMS' CARDS C1-C5, their rule R0-R5 and the
identity check (docs/design/memfn/r45_reply.md rev 7 §3 "The cards", "The head `h` and the
default", "The head lever and its identity check"; cards kit-grid@7 in
memfn/data/cards/kit-grid.tsv).

The kit's measurement script for the forms I / L / H(h) (memfn/src/window.c, THE SPAN FORMS).
Every cell compiles a card pattern at PCREC level on ONE binary (the frozen combined-branch
build), h set through the TEST-ONLY lever (`build/pcrec-harness --harness=span-head=N`, never a
shipped compile), I as the deny `--memfn=no-span-loop`, the engine route (C5) as
`--memfn=no-window-search`; the artifact plus one find-all wrapper is one C file per cell, its
answers gated against python `re` before any timing.

THE NIGHT (r45_reply rev 7 §3 "the night order"; each step a command, RUNDIR one directory):
  plan                     every cell (card, pattern, arm, regime, layer), the counts and the
                           EXPECTED WALL TIME of each timing step (UNMEASURED constants, named)
  dry RUNDIR [--quick]     builds EVERY cell (compile, gcc, the gate on every regime's
                           subject; C4's size record at the grid top) and prints the cell list
                           and count; no clock
  run RUNDIR [--with-approx]
                           step 1: times C1, C2, C5 and the A/A cells (results.tsv). Regimes
                           the kit only APPROXIMATES are void by method (rev 7, F8) and are not
                           timed unless --with-approx (a record only; the rule never reads them)
  rerun RUNDIR             re-times every cell `rule` lists as VOID ONCE (all its arms), into
                           results_rerun.tsv / results_c3_h<H>_rerun.tsv (rev 7, F7)
  rule RUNDIR [--g2 FILE]  R0-R5: the floor, h*, its label, the filings; exit 0 complete,
                           2 the night is void or defective, 3 a step is owed (a re-run, or C3
                           at h*); the line `rule: NEXT ...` names it
  c3 RUNDIR H              step 2b: times C3 at I, L and H(H) (results_c3_h<H>.tsv) and records
                           C4's sizes at H (sizes_h<H>.tsv); run at the h* `rule` picked (F4)
  selftest                 the rule against every drill r45_reply rev 7 §3 lists, plus the noise
                           drill (F2), the unimodal drill (F3) and the void/R0/re-run drills
  identity H [PATTERNS]    step 3: the lever at H on the FROZEN pcrec-harness against the
                           REBUILT build/pcrec, byte for byte, both encodings, both layers,
                           over the card patterns, the census covers (read from the sweep's own
                           corpus) and the PATTERNS file (main's predicted movers, one a line;
                           REQUIRED when H < 64)

Env: PCREC_TREE (default: this file's tree), FROZEN (the frozen tree's build dir; REQUIRED by
`identity`, default the tree's build/ elsewhere), REBUILT (identity's rebuilt build dir, default
the tree's build/), WIDTH_FLAG (default `--window-search-width=4095`; `none` on a tree without
main's width option), CPU (taskset core, default 15), LAUNCHES (default 5), JOBS.
"""
import functools, hashlib, json, math, os, random, re, statistics, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.environ.get("PCREC_TREE") or os.path.normpath(os.path.join(HERE, "..", "..", ".."))
BUILD = os.environ.get("FROZEN") or os.path.join(TREE, "build")
HARNESS = os.path.join(BUILD, "pcrec-harness")
PCREC = os.path.join(BUILD, "pcrec")
WIDTH_FLAG = os.environ.get("WIDTH_FLAG", "--window-search-width=4095")
CPU = os.environ.get("CPU", "15")
LAUNCHES = int(os.environ.get("LAUNCHES", "5"))
PREFIX = "rxa"
CC = os.environ.get("CC", "gcc")

# ---- the grid and the arms (r45_reply §3 "The grid") ----------------------------------------
# The DEFAULT candidates are the FINITE heads; I (h >= k) is timed in every cell as the
# reference, never a candidate. UNMEASURED: the grid is CHOSEN (r45_reply §3).
GRID = [0, 1, 2, 4, 8, 16, 24, 32, 64]
GRID_TOP = 64
SIMD = "-fmemfn-simd=x86-64-v3"
LAYERS = {"off": [], "on": [SIMD]}

# ---- the rule's statistical constants (r45_reply rev 7 §3 "The floor `f`", "Void") ----------
# ALPHA: the rule's FAMILY-WISE false-pick budget, CHOSEN = the acceptance r35 F2 ruled (P(h* !=
# 64 on pure noise) <= 5 %). The floor is sized so that ALL the per-cell comparisons together
# show a false win beyond f with probability at most ALPHA (one-sided Bonferroni over N).
ALPHA = 0.05
# SIGMA_CONF: the one-sided confidence of the upper bound on the A/A sigma (12 cells estimate
# it; the bound pays for that estimate's own noise). CHOSEN.
SIGMA_CONF = 0.95
# GAP_K: a timed arm is BIMODAL when its launches split into two groups of >= 2 each with a gap
# of more than GAP_K launch sigmas between them (rev 7, F3). CHOSEN from a 2e7-sample simulation
# of 5 launches (lane formsfixa): P(gap > 4.5 sigma) is 1e-7 under normal noise and 7e-6 under
# t(5) noise per arm, i.e. <= 1 % of nights at ~1,100 arm cells; `selftest`'s unimodal drill
# re-checks it through this script, and its bimodal control shows the test can fire.
GAP_K = 4.5
# MED_SD5: the median of the sample SD of 5 normal draws, in sigma units: sqrt(median
# chi2(4) / 4) = sqrt(3.3567 / 4). DERIVED. The launch sigma of a (regime, layer) pool is the
# median of its arms' launch SDs over this constant (a median, so one bimodal arm cannot
# inflate the pool's own scale).
MED_SD5 = 0.9161
MIN_POOL = 10       # a pool with fewer timed arms borrows the night's pooled scale. CHOSEN.


def arm_flags(arm):
    """The compile flags of an arm: I (the deny, today's text), h<N> (the lever), engine."""
    if arm == "I":
        return HARNESS, ["--memfn=no-span-loop"]
    if arm == "engine":
        return HARNESS, ["--memfn=no-window-search"]
    if arm.startswith("h"):
        return HARNESS, ["--harness=span-head=%d" % int(arm[1:])]
    if arm in ("aa", "aa-twin"):
        return HARNESS, []
    raise SystemExit("cards: unknown arm %r" % arm)


# ---- the card patterns: each a fixed-width window, stated per position as its byte set ------
HEX, DIG = "0123456789abcdef", "0123456789"
LIT40 = "quick brown fox jumps over the lazy dogs"    # 40 bytes: lit-l40, the run-compare control
LIT16 = "jumps over a dog"                             # 16 bytes: the A/A control lit-l16
assert len(LIT40) == 40 and len(LIT16) == 16


def rep(s, k):
    return [s] * k


PATTERNS = {
    # id: (regex, per-position byte sets)
    "hex24": (r"[0-9a-f]{24}", rep(HEX, 24)),
    "hex32": (r"[0-9a-f]{32}", rep(HEX, 32)),
    "dig24": (r"\d{24}", rep(DIG, 24)),
    "dig32": (r"\d{32}", rep(DIG, 32)),
    "uuid36": (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
               rep(HEX, 8) + ["-"] + rep(HEX, 4) + ["-"] + rep(HEX, 4) + ["-"] + rep(HEX, 4) + ["-"]
               + rep(HEX, 12)),
    "lit40": (re.escape(LIT40), list(LIT40)),
    # the census rows' own patterns (cover_cap.md's corpus list): counterk.rxt (49), spanarms.rxt (60)
    "alt49": (r"(?:ab|ba|aa|bb){24}c", rep("ab", 48) + ["c"]),
    "abc60": (r"(?:abc){20}", list("abc" * 20)),
    "hex64": (r"[0-9a-f]{64}", rep(HEX, 64)),
    "hex500": (r"[0-9a-f]{500}", rep(HEX, 500)),
    "hex1000": (r"[0-9a-f]{1000}", rep(HEX, 1000)),
    "a500": (r"a{500}", rep("a", 500)),
    "a1000": (r"a{1000}", rep("a", 1000)),
    "hex4095": (r"[0-9a-f]{4095}", rep(HEX, 4095)),
    "a4095": (r"a{4095}", rep("a", 4095)),
    "a32": (r"a{32}", rep("a", 32)),
    "lit16": (re.escape(LIT16), list(LIT16)),
}

# The regimes (r45_reply §3 C1; cover_cap.md §11.4's five plus uniform random bytes). Two take
# their METHOD from the bench (D198 (f) NOT-WARM, the bench's `short-subject-search` subject);
# until the bench names them, the script carries the kit's own approximation, and a cell in such
# a regime is VOID BY METHOD (rev 7, r35 F8): the rule never reads it as that regime. A regime
# whose bench method is ported here leaves APPROX in the same change.
REGIMES = ["hit-dense", "near-miss", "not-warm", "miss-heavy", "short-subject", "random"]
APPROX = {"not-warm": "kit approximation (each 4 KiB call after a 32 MiB eviction sweep, "
                      "untimed); the bench's D198 (f) method replaces it",
          "short-subject": "kit approximation (LF-separated 48-80 byte records, one find-all "
                           "each); the bench's short-subject-search subject replaces it"}


def method_of(regime):
    return "kit-approx" if regime in APPROX else "kit"


# ---- the cards (r45_reply rev 7 §3 "The cards"; kit-grid@7) ---------------------------------
FINITE = ["h%d" % h for h in GRID]
CARD_ROWS = {"C1": "span_cross", "C2": "span_pop", "C3": "span_long", "C4": "span_size",
             "C5": "span_engine"}
CARDS = [
    # card, patterns, arms, regimes, layers, kind
    ("C1", ["hex24", "dig24", "hex32", "dig32"], ["I"] + FINITE, REGIMES, ["off", "on"], "time"),
    ("C2", ["uuid36", "lit40", "alt49", "abc60", "hex64"], ["I"] + FINITE, REGIMES, ["off", "on"], "time"),
    ("C3", ["hex500", "hex1000", "a500", "a1000"], ["I", "h0", "hstar"], REGIMES, ["off", "on"], "time"),
    ("C4", ["hex32", "hex500", "hex1000", "hex4095", "a32", "a500", "a1000", "a4095"],
     ["I", "h0", "hstar"], [], ["off", "on"], "size"),
    ("C5", ["hex24", "dig24", "hex32", "dig32", "uuid36", "lit40", "alt49", "abc60", "hex64",
            "hex500", "hex1000", "a500", "a1000"], ["engine"], REGIMES, ["off"], "time"),
    ("AA", ["lit16"], ["aa", "aa-twin"], REGIMES, ["off", "on"], "time"),
]
CARD_PATS = {c[0]: c[1] for c in CARDS}
STEP1 = ("C1", "C2", "C5", "AA")       # `run`: before h* exists
STEP2B = ("C3", "C4")                   # `c3 H`: after the rule froze h* (rev 7, F4)


def cells(hstar=GRID_TOP, cards=None):
    """Every cell: (card, pattern, arm, regime, layer); `hstar` resolves C3/C4's H(h*) arm.
    `cards`: only these cards (default all)."""
    out = []
    for card, pats, arms, regs, layers, kind in CARDS:
        if cards is not None and card not in cards:
            continue
        for p in pats:
            seen = []
            for a in arms:
                a = "h%d" % hstar if a == "hstar" else a
                if a in seen:          # h* = 0: H(h*) is L, one arm
                    continue
                seen.append(a)
                for ly in layers:
                    for r in (regs or ["-"]):
                        out.append((card, p, a, r, ly))
    return out


# ---- subjects ---------------------------------------------------------------------------------
WORDS = ("the of and to in is it that was for on are as with his they at be this from have or "
         "by one had not but what all were when we there can an your which their said if do "
         "will each about how up out them then she many some so these would other into has "
         "more her two like him see time could no make than first been its who now people my "
         "made over did down only way find use may water long little very after words called "
         "just where most know get through back much before go good new write our used me man "
         "too any day same right look think also around another came come work three word must "
         "because does part even place well such here take why things help put years different "
         "away again off went old number great tell men say small every found still between "
         "name should home big give air line set own under read last never us left end along "
         "while might next sound below saw something thought both few those always looked show "
         "large often together asked house don't world going want school important until 1 2 3 "
         "2026 404 200 0x1f ab12 deadbeef c0ffee").split()


def subject(pat, regime, n, seed):
    """The regime's subject for pattern `pat`, n bytes (records for short-subject)."""
    rnd = random.Random("%s|%s|%d|%d" % (pat, regime, n, seed))
    pos = PATTERNS[pat][1]
    k = len(pos)
    out = bytearray()
    if regime == "hit-dense":
        while len(out) < n:
            out += bytes(ord(rnd.choice(s)) for s in pos)
    elif regime == "near-miss":
        # EMITTED-2's shape: the window's first k - 1 positions, then a byte outside the last set
        last = set(pos[-1])
        miss = next(c for c in "zZ#@!" if c not in last)
        while len(out) < n:
            out += bytes(ord(rnd.choice(s)) for s in pos[:-1]) + miss.encode()
    elif regime == "random":
        out += bytes(rnd.getrandbits(8) for _ in range(n))
    elif regime == "short-subject":
        while len(out) < n:
            ln = rnd.randint(48, 80)
            rec = bytearray()
            while len(rec) < ln:
                rec += (rnd.choice(WORDS) + " ").encode()
            if rnd.randrange(8) == 0 and k <= 4096:
                m = bytes(ord(rnd.choice(s)) for s in pos)
                at = rnd.randrange(len(rec) + 1)
                rec = rec[:at] + m + rec[at:]
            out += rec.replace(b"\n", b" ") + b"\n"
    else:   # miss-heavy and not-warm: plain text, death at depth 0-1
        while len(out) < n:
            out += (rnd.choice(WORDS) + (" " if rnd.randrange(12) else "\n")).encode()
    return bytes(out[:n])


def expect(pat, regime, buf):
    """python `re`'s find-all over the subject (each LF-free record for short-subject):
    count and the sum of the match starts."""
    rx = re.compile(PATTERNS[pat][0].encode())
    parts = []
    if regime == "short-subject":
        off = 0
        for rec in buf.split(b"\n"):
            parts.append((off, rec))
            off += len(rec) + 1
    else:
        parts = [(0, buf)]
    k = s = 0
    for off, b in parts:
        for m in rx.finditer(b):
            k += 1
            s += off + m.start()
    return k, s


# ---- the cell's C text: the artifact and one driver -----------------------------------------
DRIVER = r"""
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
/* one find-all over s[0, n) (restart at the match end, one past an empty match);
   positions reported as base + start; a give-up returns a count no gate can equal */
static uint64_t fa(const unsigned char *s, size_t n, size_t base, uint64_t *sum)
{
    ptrdiff_t caps[RXA_NCAPS][2];
    uint64_t k = 0;
    size_t from = 0;
    while (from <= n) {
        int r = rxa_search(s, n, from, caps);
        if (r == 0) break;
        if (r < 0) return (uint64_t)1 << 62;
        size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
        k++;
        if (sum) *sum += base + st;
        from = en > st ? en : st + 1;
    }
    return k;
}
static unsigned char *evict;
enum { EVICT = 32 << 20, CHUNK = 4096 };
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }
/* one call of the regime over the subject: whole, per record, or per 4 KiB chunk after an
   untimed eviction sweep (not-warm); *ns gets the timed nanoseconds */
static uint64_t call(int regime, const unsigned char *s, size_t n, uint64_t *sum, double *ns)
{
    uint64_t k = 0;
    if (regime == 0) {
        double t0 = now(); k = fa(s, n, 0, sum); *ns += now() - t0;
    } else if (regime == 1) {
        double t0 = now();
        for (size_t p = 0; p < n;) {
            const unsigned char *e = memchr(s + p, '\n', n - p);
            size_t q = e ? (size_t)(e - s) : n;
            k += fa(s + p, q - p, p, sum);
            p = q + 1;
        }
        *ns += now() - t0;
    } else {
        for (size_t p = 0; p < n; p += CHUNK) {
            for (size_t i = 0; i < EVICT; i += 64) evict[i]++;
            size_t m = n - p < CHUNK ? n - p : CHUNK;
            double t0 = now(); k += fa(s + p, m, p, sum); *ns += now() - t0;
        }
    }
    return k;
}
int main(int argc, char **argv)
{
    if (argc != 5) return 2;
    int regime = atoi(argv[2]);
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 2;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)n + 1);
    if (!s || fread(s, 1, (size_t)n, f) != (size_t)n) return 2;
    fclose(f);
    if (regime == 2 && !(evict = calloc(EVICT, 1))) return 2;
    uint64_t sum = 0;
    double ns = 0;
    uint64_t k = call(regime, s, (size_t)n, &sum, &ns);
    if (k != strtoull(argv[3], 0, 10) || sum != strtoull(argv[4], 0, 10)) {
        printf("GATE FAIL count %llu sum %llu\n", (unsigned long long)k, (unsigned long long)sum);
        return 1;
    }
    if (!getenv("CARD_TIME")) { printf("GATE ok %llu\n", (unsigned long long)k); return 0; }
    /* calibrated: repeat whole calls until 50 ms of timed work, report ns per byte. NOT-WARM is
       calibrated on CALLS instead (r35 F11): one pass, i.e. n / CHUNK timed chunk calls, each
       after its untimed eviction sweep; a time-calibrated loop would pay ~50 untimed passes */
    unsigned long reps = 0;
    ns = 0;
    do { call(regime, s, (size_t)n, NULL, &ns); reps++; } while (regime != 2 && ns < 5e7);
    printf("TIME %.6f ns/B reps %lu\n", ns / reps / (double)n, reps);
    return 0;
}
"""
REGIME_CODE = {"short-subject": 1, "not-warm": 2}
SUBJECT_N = 1 << 20


class GateFail(RuntimeError):
    """A cell's answers differ from python `re`'s: R0's input, never a void (rev 7, F5)."""


def _h(*parts):
    h = hashlib.sha256()
    for x in parts:
        h.update(hashlib.sha256(x if isinstance(x, bytes) else x.encode("latin-1")).digest())
    return h.hexdigest()[:16]


# C4 records sizes AGAINST the size-cap ladder (250,000 / 1,000,000), so its compiles lift the cap
# past the largest form (I at 4095 is ~630 KB, R-45 FACT); no timed cell lifts it
SIZE_CAP = ["--max-emit-code-bytes=4000000"]


def artifact(rundir, pat, arm, layer, size=False):
    """The cell's artifact (pcrec-level compile on the frozen binary), cached by its inputs."""
    binp, fl = arm_flags(arm)
    wf = [] if WIDTH_FLAG == "none" else [WIDTH_FLAG]
    args = [binp, "-p", PREFIX, "--features", "all"] + wf + (SIZE_CAP if size else []) + LAYERS[layer] + fl + [
        "-o", "-", "--pattern", PATTERNS[pat][0]]
    d = os.path.join(rundir, "art")
    os.makedirs(d, exist_ok=True)
    c = os.path.join(d, "a_%s.c" % _h(" ".join(args), open(binp, "rb").read()))
    if not os.path.exists(c):
        r = subprocess.run(args, capture_output=True, timeout=600)
        if r.returncode:
            raise RuntimeError("pcrec refused %s %s %s: %s" % (pat, arm, layer,
                               r.stderr.decode(errors="replace")[-400:]))
        tmp = "%s.%d.%d" % (c, os.getpid(), threading.get_ident())
        open(tmp, "wb").write(r.stdout)
        os.replace(tmp, c)
    return c


# A span loop's text (window.c wf_loop: `size_t <J> = LO; for (; <J> < END; <J>++) if (!`; G2's
# parse_loops reads the same head). Arm I (`--memfn=no-span-loop`) must carry none.
LOOP_RE = re.compile(rb"_j = [0-9]+; for \(; [A-Za-z0-9_]*_j < [0-9]+; [A-Za-z0-9_]*_j\+\+\) if \(!")


def loop_audit(texts):
    """texts: [(label, arm, bytes)]. (arm-I cells whose text holds a span loop, non-I cells that do):
    a deny that is ignored is invisible to every other check (r35 F15), and a zero over I with a
    zero reach is vacuous (the caller fails that too)."""
    leaks = [l for l, a, t in texts if a == "I" and LOOP_RE.search(t)]
    reach = [l for l, a, t in texts if a != "I" and LOOP_RE.search(t)]
    return leaks, reach


def check_deny(rundir, cl):
    """Every arm-I artifact of `cl` carries no span loop, and a non-I artifact does (the reach
    control). Returns (failures, n_I, n_reach)."""
    keys = sorted({(c[1], c[2], c[4], c[0] == "C4") for c in cl})
    texts = [("%s %s %s" % (k[0], k[1], k[2]), k[1], open(artifact(rundir, k[0], k[1], k[2], size=k[3]), "rb").read())
             for k in keys]
    leaks, reach = loop_audit(texts)
    nI = sum(1 for _l, a, _t in texts if a == "I")
    bad = ["DENY IGNORED: arm I emits a span loop: %s" % l for l in leaks]
    if not nI:
        bad.append("DENY CHECK VACUOUS: no arm-I artifact in the cell list")
    if not reach:
        bad.append("DENY CHECK VACUOUS: no non-I artifact emits a span loop (the loop text moved?)")
    return bad, nI, len(reach)


def build_cell(rundir, pat, arm, layer):
    """The cell's binary (artifact + driver), gcc -O2; cached."""
    a = artifact(rundir, pat, arm, layer)
    src = open(a, encoding="latin-1").read()
    exe = os.path.join(rundir, "bin", "x_%s" % _h(src, DRIVER))
    if os.path.exists(exe):
        return exe, a
    os.makedirs(os.path.dirname(exe), exist_ok=True)
    tu = "%s.%d.%d.src" % (exe, os.getpid(), threading.get_ident())
    open(tu, "w", encoding="latin-1").write("#include <stddef.h>\n#include <stdint.h>\n"
                                             "#include <string.h>\n" + src + "\n" + DRIVER)
    # two arms can render the same text (H(h) is I where h >= k): each build its own temp names
    tmp = "%s.%d.%d" % (exe, os.getpid(), threading.get_ident())
    r = subprocess.run([CC, "-std=gnu11", "-O2", "-w", "-x", "c", "-o", tmp, tu], capture_output=True,
                       timeout=1800)
    if r.returncode:
        raise RuntimeError("gcc %s %s %s: %s" % (pat, arm, layer, r.stderr.decode()[-400:]))
    os.replace(tmp, exe)
    os.replace(tu, exe + ".c")
    return exe, a


def subj_file(rundir, pat, regime, n):
    p = os.path.join(rundir, "subj", "%s.%s.%d" % (pat, regime, n))
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        b = subject(pat, regime, n, 1)
        k, s = expect(pat, regime, b)
        tmp = "%s.%d.%d" % (p, os.getpid(), threading.get_ident())
        open(tmp + ".e", "w").write("%d %d\n" % (k, s))
        os.replace(tmp + ".e", p + ".expect")
        open(tmp, "wb").write(b)
        os.replace(tmp, p)
    k, s = open(p + ".expect").read().split()
    return p, k, s


def size_record(rundir, pat, arm, layer):
    """C4: emitted C bytes, gcc -O2 -c time and max RSS, .text bytes (no timing of the matcher)."""
    a = artifact(rundir, pat, arm, layer, size=True)
    obj = os.path.join(rundir, "obj", os.path.basename(a) + ".o")
    os.makedirs(os.path.dirname(obj), exist_ok=True)
    tu = obj + ".c"
    open(tu, "w", encoding="latin-1").write("#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n"
                                             + open(a, encoding="latin-1").read())
    r = subprocess.run(["/usr/bin/time", "-f", "%e %M", CC, "-std=gnu11", "-O2", "-w", "-c", "-o", obj, tu],
                       capture_output=True, text=True, timeout=1800)
    if r.returncode:
        raise RuntimeError("gcc -c %s %s: %s" % (pat, arm, r.stderr[-300:]))
    secs, rss = r.stderr.strip().splitlines()[-1].split()
    sz = subprocess.run(["size", "-A", obj], capture_output=True, text=True).stdout
    text = next((int(l.split()[1]) for l in sz.splitlines() if l.startswith(".text ")), 0)
    return os.path.getsize(a), float(secs), int(rss), text


def _exec(argv, cell, env=None):
    t = subprocess.run(argv, capture_output=True, text=True, timeout=900, env=env)
    if t.returncode == 1 and t.stdout.startswith("GATE FAIL"):
        raise GateFail("cell %s: %s" % ("|".join(cell), t.stdout.strip()))
    if t.returncode:
        raise RuntimeError("cell %s: rc %d %s" % ("|".join(cell), t.returncode, t.stdout.strip()))
    return t.stdout


def run_cell(rundir, cell, n, timed):
    """Not timed: the gate's line. Timed: the list of LAUNCHES launch times (ns/B)."""
    card, pat, arm, regime, layer = cell
    if card == "C4":
        cb, secs, rss, text = size_record(rundir, pat, arm, layer)
        return "size c_bytes=%d gcc_s=%.2f rss_kb=%d text=%d" % (cb, secs, rss, text)
    exe, _a = build_cell(rundir, pat, arm, layer)
    sp, k, s = subj_file(rundir, pat, regime, n)
    code = str(REGIME_CODE.get(regime, 0))
    out = _exec([exe, sp, code, k, s], cell)
    if not timed:
        return out.strip()
    env = dict(os.environ, CARD_TIME="1")
    return [float(_exec(["taskset", "-c", CPU, exe, sp, code, k, s], cell, env).split()[1])
            for _ in range(LAUNCHES)]


# ---- results files: one row per arm cell ------------------------------------------------------
# card pattern arm regime layer status median spread launches method; status ok | void |
# gatefail | method (void by method, not timed). The launches are kept so the rule can test
# bimodality (rev 7, F3); `spread` (max - min) is a record only.
HEADER = "#card\tpattern\tarm\tregime\tlayer\tstatus\tmedian_ns_per_B\tspread\tlaunches\tmethod\n"


def row_line(cell, status, launches=None, note=""):
    if launches:
        med, spr = statistics.median(launches), max(launches) - min(launches)
        return "\t".join(cell) + "\t%s\t%.6f\t%.6f\t%s\t%s\n" % (
            status, med, spr, ",".join("%.6f" % v for v in launches), method_of(cell[3]))
    return "\t".join(cell) + "\t%s\t-\t-\t%s\t%s\n" % (status, note.replace("\t", " ").replace("\n", " ")[:300] or "-",
                                                       method_of(cell[3]))


def read_rows(path):
    """{(card, pat, arm, regime, layer): row dict} from a results file (absent file: {})."""
    out = {}
    if not os.path.exists(path):
        return out
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        key = tuple(f[:5])
        st = f[5]
        launches = [float(x) for x in f[8].split(",")] if st == "ok" else []
        out[key] = {"status": st, "med": float(f[6]) if st == "ok" else None, "launches": launches,
                    "method": f[9], "note": f[8] if st != "ok" else ""}
    return out


def time_cells(rundir, cl, path, with_approx=True):
    with open(path, "a") as f:
        if os.path.getsize(path) == 0:
            f.write(HEADER)
        for c in cl:
            if c[3] in APPROX and not with_approx:
                f.write(row_line(c, "method", note="void by method: " + APPROX[c[3]]))
                continue
            try:
                f.write(row_line(c, "ok", run_cell(rundir, c, SUBJECT_N, True)))
            except GateFail as e:
                f.write(row_line(c, "gatefail", note=str(e)))
            except Exception as e:      # noqa: BLE001 -- a void, re-run once (F7)
                f.write(row_line(c, "void", note=str(e)))
            f.flush()


# ---- plan (with the expected wall time, r35 F11) ---------------------------------------------
# UNMEASURED: the per-launch costs below are assumptions for the window request, never inputs to
# the rule; F11 asks for one launch's wall time in the cards' own window to replace them.
EST_LAUNCH_S = float(os.environ.get("EST_LAUNCH_S", "0.08"))   # 50 ms timed + exec + one gate call
EST_SWEEP_S = float(os.environ.get("EST_SWEEP_S", "0.004"))    # one 32 MiB eviction sweep (~8 GB/s)


def est_cell_s(cell):
    """One arm cell's wall: its gate run plus LAUNCHES launches."""
    if cell[3] == "not-warm":   # every call sweeps once per 4 KiB chunk: the gate call + one timed pass
        per = 2 * (SUBJECT_N // 4096) * EST_SWEEP_S
        return (1 + LAUNCHES) * per
    return EST_LAUNCH_S * (1 + LAUNCHES)


def cmd_plan(_args):
    cl = cells()
    by = {}
    for c in cl:
        by[c[0]] = by.get(c[0], 0) + 1
    for c in cl:
        print("\t".join(c))
    builds = {(c[1], c[2], c[4]) for c in cl}
    print("# cells %d (%s); distinct compiles %d" % (len(cl), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                                     len(builds)))
    for r, why in APPROX.items():
        print("# regime %s: %s; VOID BY METHOD (rev 7, F8)" % (r, why))
    s1 = [c for c in cells(cards=STEP1)]
    s1_read = [c for c in s1 if c[3] not in APPROX]
    s2 = [c for c in cells(cards=("C3",))]
    s2_read = [c for c in s2 if c[3] not in APPROX]
    w = lambda cs: sum(est_cell_s(c) for c in cs) / 3600.0      # noqa: E731
    print("# expected wall (UNMEASURED: EST_LAUNCH_S %.3f s per launch, EST_SWEEP_S %.4f s per eviction "
          "sweep, LAUNCHES %d, the cells already built by `dry`):" % (EST_LAUNCH_S, EST_SWEEP_S, LAUNCHES))
    print("#   run:  %d cells timed, %.2f h (with --with-approx: %d cells, %.2f h)" % (
        len(s1_read), w(s1_read), len(s1), w(s1)))
    print("#   c3:   %d cells timed, %.2f h (C4's sizes: compile-only, not in the window)" % (len(s2_read), w(s2_read)))
    print("#   rerun: one cell per void, ~%.0f s per C1-C2 cell (10 arms)" % (10 * EST_LAUNCH_S * (1 + LAUNCHES)))


def cmd_dry(args):
    """Builds every cell and runs its gate once (no clock): the cell list, the count, the
    distinct compiles, and every failure (a failure is the run's red)."""
    rundir = args[0]
    quick = "--quick" in args
    n = 1 << 16 if quick else SUBJECT_N
    os.makedirs(rundir, exist_ok=True)
    cl = cells()
    jobs = int(os.environ.get("JOBS", "4"))
    bad, done = [], {}
    # the compiles first, one per (pattern, arm, layer), in parallel; the gates then reuse them
    builds = sorted({(c[1], c[2], c[4], c[0] == "C4") for c in cl})

    def one_build(b):
        pat, arm, layer, size = b
        try:
            if size:
                artifact(rundir, pat, arm, layer, size=True)
            else:
                build_cell(rundir, pat, arm, layer)
            return None
        except Exception as e:
            return "BUILD %s %s %s: %s" % (pat, arm, layer, e)
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for e in ex.map(one_build, builds):
            if e:
                bad.append(e)

    def one(c):
        try:
            return c, run_cell(rundir, c, n, False), None
        except Exception as e:
            return c, None, str(e)
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for c, out, err in ex.map(one, cl):
            print("%s\t%s" % ("\t".join(c), out if out else "FAIL " + err))
            if err:
                bad.append(err)
            done[c] = out
    dbad, nI, nreach = check_deny(rundir, cl)
    bad += dbad
    print("# dry: deny check: %d arm-I artifacts with no span loop, %d non-I artifacts with one (reach), "
          "failures %d" % (nI, nreach, len(dbad)))
    same = identical_to_I(rundir)
    print("# dry: cells %d, built and gated %d, failures %d; distinct compiles %d; subject %d B" %
          (len(cl), len(cl) - len(bad), len(bad), len(builds), n))
    print("# dry: H(h) text identical to I: %s" % ", ".join("%s:%s" % (p, ",".join(map(str, hs)))
                                                            for p, hs in sorted(same.items())))
    for b in bad[:20]:
        print("FAIL", b)
    return 1 if bad else 0


def identical_to_I(rundir):
    """Per C1-C2 pattern, the finite heads whose SIMD-off text equals I's (read off the
    artifacts, not assumed from h >= k). Where it is, the rule reads I's median for the head:
    one text, one binary, one reading (rev 7, F2)."""
    out = {}
    for card in ("C1", "C2"):
        for p in CARD_PATS[card]:
            ia = open(artifact(rundir, p, "I", "off"), "rb").read()
            out[p] = [h for h in GRID if open(artifact(rundir, p, "h%d" % h, "off"), "rb").read() == ia]
    return out


def cmd_run(args):
    rundir = args[0]
    os.makedirs(rundir, exist_ok=True)
    res = os.path.join(rundir, "results.tsv")
    if os.path.exists(res):
        raise SystemExit("cards: %s exists; a night's step 1 runs once (re-runs: `rerun`)" % res)
    open(res, "w").close()
    dbad, nI, nreach = check_deny(rundir, cells(cards=STEP1))
    print("cards: deny check: %d arm-I artifacts loop-free, reach %d" % (nI, nreach))
    if dbad:
        for b in dbad:
            print("FAIL", b)
        os.remove(res)
        raise SystemExit("cards: the deny check failed; no timing")
    json.dump(identical_to_I(rundir), open(os.path.join(rundir, "same_as_I.json"), "w"))
    time_cells(rundir, cells(cards=STEP1), res, with_approx="--with-approx" in args)
    print("cards: results in %s; next: cards.py rule %s" % (res, rundir))


def cmd_c3(args):
    rundir, h = args[0], int(args[1])
    if h not in GRID:
        raise SystemExit("cards: c3: %d is not a finite grid head" % h)
    res = os.path.join(rundir, "results_c3_h%d.tsv" % h)
    if os.path.exists(res):
        raise SystemExit("cards: %s exists (re-runs: `rerun`)" % res)
    open(res, "w").close()
    time_cells(rundir, cells(hstar=h, cards=("C3",)), res, with_approx=False)
    with open(os.path.join(rundir, "sizes_h%d.tsv" % h), "w") as f:
        for c in cells(hstar=h, cards=("C4",)):
            try:
                f.write("\t".join(c) + "\t" + run_cell(rundir, c, 0, False) + "\n")
            except Exception as e:      # noqa: BLE001
                f.write("\t".join(c) + "\tFAIL " + str(e).replace("\n", " ")[:300] + "\n")
    print("cards: C3 at H(%d) in %s; next: cards.py rule %s" % (h, res, rundir))


def cmd_rerun(args):
    """Re-times every cell the rule lists as void ONCE, all arms of the cell (F7)."""
    rundir = args[0]
    night = load_night(rundir)
    v = analyse(night, set())
    if v["code"] == 2:
        print("cards: rerun: the night is void or defective (`rule` says why); nothing to re-run")
        return 2
    todo = v["owed_rerun"]
    if not todo:
        print("cards: rerun: no cell is void once")
        return 0
    for src, cellkeys in todo.items():
        # every arm the card defines for the cell, whether or not step 1 wrote its row
        defined = (cells(cards=STEP1) if src == "results.tsv" else
                   cells(hstar=int(src[len("results_c3_h"):-len(".tsv")]), cards=("C3",)))
        cl = [k for k in defined if (k[0], k[1], k[3], k[4]) in cellkeys]
        time_cells(rundir, cl, os.path.join(rundir, src.replace(".tsv", "_rerun.tsv")))
        print("cards: re-timed %d cells (%d arm cells) of %s" % (len(cellkeys), len(cl), src))
    return 0


# ---- THE RULE (r45_reply rev 7 §3, R0-R5, steps (1)-(5)) -------------------------------------
def r1(heads, cells_read, void_cells, t, tI, same_as_I, f, top=GRID_TOP, measured="MEASURED"):
    """R1 over the FINITE heads `heads` (R0 already applied). cells_read: the C1-C2 cells with a
    reading; void_cells: the cells void twice (or void by method); t[h][c], tI[c] the raw
    medians; same_as_I[h][c] true where H(h)'s text is I's in cell c. Returns (h*, label,
    recorded pick or None, detail); h* None when no finite head survives R0."""
    if not heads:
        return None, "no form ships: every finite head failed R0 (plan A's fallback: forms land OFF)", None, {}
    # (1) W(h): the worst ratio to I over the cells READ; a twice-void cell adds the term 1
    #     for each head whose text is I there, no term for any other head
    W = {}
    for h in heads:
        terms = [t[h][c] / tI[c] for c in cells_read]
        terms += [1.0 for c in void_cells if same_as_I[h][c]]
        W[h] = max(terms) if terms else float("inf")
    # (2) E, computed once, never chained
    m = min(W.values())
    E = sorted(h for h in heads if W[h] <= (1 + f) * m)

    # (3) dominance over the cells READ only: g dominates h when g is faster beyond f in at
    #     least one cell and slower beyond f in none; keep the members dominated by the fewest
    def dom(g, h):
        faster = any(t[h][c] / t[g][c] > 1 + f for c in cells_read)
        slower = any(t[g][c] / t[h][c] > 1 + f for c in cells_read)
        return faster and not slower
    nd = {h: sum(1 for g in E if g != h and dom(g, h)) for h in E}
    least = min(nd.values())
    kept = [h for h in E if nd[h] == least]
    # (4) the LARGEST kept head
    pick = max(kept)
    if pick == top:
        if E == sorted(heads):
            label = "h = grid top (%d, CHOSEN), on a measured tie of every finite head" % top
        elif E == [top]:
            label = "h = grid top (%d, CHOSEN): every shorter finite head measured slower beyond f" % top
        else:
            label = "h = grid top (%d, CHOSEN), on a measured tie of {%s}" % (top, ", ".join(map(str, E)))
    else:
        label = measured
    detail = {"W": W, "E": E, "dominated_by": nd, "kept": kept}
    # (5) VOID: a C1-C2 cell void twice never helps a head; h* is the LARGEST R0-SURVIVING head
    #     (rev 7, F5), the grid top whenever it survives
    if void_cells:
        hs = max(heads)
        lead = ("h = grid top (%d, CHOSEN)" % hs if hs == top else
                "h = %d, the largest R0-surviving head (CHOSEN; the grid top failed R0)" % hs)
        vs = sorted(void_cells)
        named = ", ".join(vs) if len(vs) <= 6 else "%s, ... (%d in all)" % (", ".join(vs[:4]), len(vs))
        return hs, ("%s: cell(s) %s void twice; the cells read picked H(%d)"
                    % (lead, named, pick)), pick, detail
    return pick, label, None, detail


def z_upper(p):
    """The standard normal quantile at 1 - p."""
    return statistics.NormalDist().inv_cdf(1 - p)


def chi2_lower(q, n):
    """chi-square(n)'s q quantile, Wilson-Hilferty (within ~1 % at n >= 10)."""
    z = statistics.NormalDist().inv_cdf(q)
    return n * (1 - 2 / (9 * n) + z * math.sqrt(2 / (9 * n))) ** 3


def count_floor(aa_logs, n_comp, alpha=ALPHA):
    """THE FLOOR f (rev 7, r35 F2): sized to the rule's comparison count. aa_logs: ln(t(aa) /
    t(aa-twin)) over the A/A cells read; n_comp: the number of one-sided head-against-I
    comparisons the rule makes (heads x cells read where the head's text is not I's). sigma is the
    A/A cells' RMS log ratio (two independent medians, as a head against I), raised to its
    SIGMA_CONF upper bound; f = exp(z(alpha / N) sigma_up) - 1, never below the largest A/A ratio
    itself (the floor cover_cap.md §11.4 reads)."""
    n = len(aa_logs)
    sig = math.sqrt(sum(x * x for x in aa_logs) / n)
    sig_up = sig * math.sqrt(n / chi2_lower(1 - SIGMA_CONF, n))
    z = z_upper(alpha / max(1, n_comp))
    f_aa = max(math.exp(abs(x)) - 1 for x in aa_logs)
    return max(f_aa, math.exp(z * sig_up) - 1), {"sigma": sig, "sigma_up": sig_up, "z": z, "N": n_comp,
                                                  "f_aa": f_aa}


def launch_sigmas(rows):
    """Per (regime, layer), the launch sigma (log scale) of its timed arm cells: median SD /
    MED_SD5; a thin pool borrows the night's."""
    pools, allsd = {}, []
    for k, r in rows.items():
        if r["status"] == "ok" and len(r["launches"]) >= 2:
            lg = [math.log(v) for v in r["launches"]]
            sd = statistics.stdev(lg)
            pools.setdefault((k[3], k[4]), []).append(sd)
            allsd.append(sd)
    glob = statistics.median(allsd) / MED_SD5 if allsd else 0.0
    return {p: (statistics.median(v) / MED_SD5 if len(v) >= MIN_POOL else glob) for p, v in pools.items()}, glob


def bimodal(launches, sig):
    """Two groups of >= 2 launches with more than GAP_K launch sigmas between them (F3)."""
    if len(launches) < 4 or sig <= 0:
        return False
    x = sorted(math.log(v) for v in launches)
    return any(x[i] - x[i - 1] > GAP_K * sig for i in range(2, len(x) - 1))


def load_night(rundir):
    """Every results file of a night: {name: (rows, rerun rows)}, same_as_I, the C3 heads."""
    files = {}
    for name in sorted(os.listdir(rundir)):
        if name.startswith("results") and name.endswith(".tsv") and not name.endswith("_rerun.tsv"):
            files[name] = (read_rows(os.path.join(rundir, name)),
                           read_rows(os.path.join(rundir, name.replace(".tsv", "_rerun.tsv"))))
    sp = os.path.join(rundir, "same_as_I.json")
    same = json.load(open(sp)) if os.path.exists(sp) else {}
    return {"files": files, "same": same}


def merge(rows1, rows2):
    """A re-run replaces EVERY arm of each cell it re-timed; attempts per cell."""
    cell = lambda k: (k[0], k[1], k[3], k[4])      # noqa: E731
    redone = {cell(k) for k in rows2}
    out = {k: r for k, r in rows1.items() if cell(k) not in redone}
    out.update(rows2)
    att = {cell(k): (2 if cell(k) in redone else 1) for k in out}
    return out, att


def analyse(night, g2_defective, alpha=ALPHA):
    """The whole rule over a night's files. Returns a dict: code (0 complete, 2 void/defective,
    3 owed), lines (the record), hstar, label, rec, owed_rerun {file: {cellkeys}}."""
    lines, owed = [], {}
    res = {"code": 0, "lines": lines, "hstar": None, "label": None, "rec": None, "owed_rerun": owed}
    if "results.tsv" not in night["files"]:
        lines.append("rule: no results.tsv: step 1 (`run`) has not run")
        res["code"] = 3
        return res
    rows, att = merge(*night["files"]["results.tsv"])
    same = night["same"]
    sigs, glob = launch_sigmas(rows)
    cellk = lambda k: (k[0], k[1], k[3], k[4])      # noqa: E731

    # ---- R0: G2's list, plus every head whose cell gate failed (rev 7, F5) -------------------
    defective = set(g2_defective)
    for k, r in rows.items():
        if r["status"] == "gatefail":
            if k[2] == "I" or k[0] == "AA":
                lines.append("R0: %s failed its gate in %s: the reference is wrong; the night is DEFECTIVE "
                             "(filed)" % (k[2], "/".join(k)))
                res["code"] = 2
                return res
            if k[2].startswith("h"):
                defective.add(int(k[2][1:]))
                lines.append("R0: H(%s) failed its gate in %s: DEFECTIVE (filed)" % (k[2][1:], "/".join(k)))
            else:
                lines.append("R0: the engine route failed its gate in %s (filed; R4 not computed there)"
                             % "/".join(k))
    # C3's gate fails are R0 too, at any head they name (F5's worse case: H(64) loops ONLY there)
    c3files = {n: merge(*v) for n, v in night["files"].items() if n.startswith("results_c3_h")}
    for n, (r3, _a) in sorted(c3files.items()):
        for k, r in r3.items():
            if r["status"] == "gatefail":
                if k[2] == "I":
                    lines.append("R0: I failed its gate in %s: the night is DEFECTIVE (filed)" % "/".join(k))
                    res["code"] = 2
                    return res
                defective.add(int(k[2][1:]))
                lines.append("R0: H(%s) failed its gate in C3 %s: DEFECTIVE (filed)" % (k[2][1:], "/".join(k)))
    heads = [h for h in GRID if h not in defective]

    def is_void(k, r):
        if r["status"] != "ok":
            return r["status"]
        sig = sigs.get((k[3], k[4]), glob)
        return "bimodal" if bimodal(r["launches"], sig) else None

    # ---- the floor: A/A cells of the regimes READ (approximated regimes are void by method) ---
    aa_logs = []
    for rg in REGIMES:
        if rg in APPROX:
            continue
        for ly in ("off", "on"):
            a, b = rows.get(("AA", "lit16", "aa", rg, ly)), rows.get(("AA", "lit16", "aa-twin", rg, ly))
            bad = [x for x in (a, b) if x is None or is_void(("AA", "lit16", "aa", rg, ly), x)]
            if bad:
                if att.get(("AA", "lit16", rg, ly), 1) < 2:
                    owed.setdefault("results.tsv", set()).add(("AA", "lit16", rg, ly))
                    continue
                lines.append("rule: the floor is not computable (A/A cell %s/%s missing or void twice): the "
                             "night is VOID (cover_cap.md §11.4 row 1)" % (rg, ly))
                res["code"] = 2
                return res
            aa_logs.append(math.log(a["med"] / b["med"]))

    # ---- C1-C2 cells: read, void twice, void by method, or owed a re-run (F7, F8) -----------
    ccells, vc, tI, t = [], [], {}, {h: {} for h in heads}
    sa = {h: {} for h in heads}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            for rg in REGIMES:
                for ly in ("off", "on"):
                    cid = "%s/%s/%s" % (pat, rg, ly)
                    for h in heads:
                        sa[h][cid] = h in same.get(pat, [])
                    if rg in APPROX:
                        vc.append(cid + " (void by method)")
                        for h in heads:
                            sa[h][cid + " (void by method)"] = sa[h][cid]
                        continue
                    arms = ["I"] + ["h%d" % h for h in heads if not sa[h][cid]]
                    why = []
                    for a in arms:
                        r = rows.get((card, pat, a, rg, ly))
                        w = "missing" if r is None else is_void((card, pat, a, rg, ly), r)
                        if w:
                            why.append("%s %s" % (a, w))
                    if why:
                        if att.get((card, pat, rg, ly), 1) < 2:
                            owed.setdefault("results.tsv", set()).add((card, pat, rg, ly))
                        else:
                            vc.append(cid)
                        continue
                    ccells.append(cid)
                    tI[cid] = rows[(card, pat, "I", rg, ly)]["med"]
                    for h in heads:
                        t[h][cid] = tI[cid] if sa[h][cid] else rows[(card, pat, "h%d" % h, rg, ly)]["med"]
    # C3 voids are never dropped: once, owed a re-run; twice, carried on the record below
    for n, (r3, a3) in sorted(c3files.items()):
        for k, r in r3.items():
            w = is_void(k, r)
            if w and w != "gatefail" and a3.get(cellk(k), 1) < 2 and r["method"] != "kit-approx":
                owed.setdefault(n, set()).add(cellk(k))
    if owed:
        for n, ks in sorted(owed.items()):
            lines.append("rule: %d cell(s) of %s void ONCE (%s%s): R1 waits for the re-run"
                         % (len(ks), n, ", ".join("/".join(c) for c in sorted(ks)[:6]),
                            ", ..." if len(ks) > 6 else ""))
        lines.append("rule: NEXT cards.py rerun RUNDIR")
        res["code"] = 3
        return res
    n_comp = sum(1 for h in heads for c in ccells if not sa[h][c])
    if not aa_logs:
        lines.append("rule: no A/A cell is read: the night is VOID")
        res["code"] = 2
        return res
    f, fd = count_floor(aa_logs, n_comp, alpha)
    lines.append("rule: f = %.4f (count-sized: A/A sigma %.4f, upper %.4f over %d cells; N = %d comparisons, "
                 "z = %.2f; the A/A max ratio alone %.4f)" % (f, fd["sigma"], fd["sigma_up"], len(aa_logs),
                                                               fd["N"], fd["z"], fd["f_aa"]))
    lines.append("rule: R0 defective heads: %s; cells read %d, void %d" % (sorted(defective) or "none",
                                                                         len(ccells), len(vc)))
    measured = "MEASURED (kit-grid@7 cards C1 %s, C2 %s; %d cells read)" % (CARD_ROWS["C1"], CARD_ROWS["C2"],
                                                                           len(ccells))
    hs, label, rec, det = r1(heads, ccells, vc, t, tI, sa, f, measured=measured)
    res.update(hstar=hs, label=label, rec=rec, f=f, det=det)
    if hs is None:
        lines.append("rule: h* none: %s" % label)
        res["code"] = 2
        return res
    lines.append("rule: W = %s" % {h: round(w, 4) for h, w in det["W"].items()})
    lines.append("rule: E = %s; dominated-by counts %s; kept %s" % (det["E"], det["dominated_by"], det["kept"]))
    # R3: per class, the head its own cells pick, against the grid value nearest E[D]; DERIVED
    # when every class with a cell read tracks (rev 7, F10)
    track, any_cls = True, False
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            mine = [c for c in ccells if c.startswith(pat + "/")]
            if not mine:
                continue
            any_cls = True
            hcls = r1(heads, mine, [], t, tI, sa, f)[0]
            ed = death_depth(pat)
            near = min(heads, key=lambda h: (abs(h - ed), -h))
            track &= hcls == near
            lines.append("R3 class %s: its own cells pick %d; E[D] %.2f (nearest head %d)%s"
                         % (pat, hcls, ed, near, "" if hcls == near else ": does not track"))
    if label.startswith("MEASURED") and any_cls and track:
        label = "DERIVED (R3: h* tracks E[D] in every class)" + label[len("MEASURED"):]
        res["label"] = label
    lines.append("rule: h* = %d, %s" % (hs, label))
    # R2 (C1-C2 half): every cell where I beats H(h*) beyond f (dial evidence; never changes h*)
    for c in ccells:
        if t[hs][c] / tI[c] > 1 + f:
            lines.append("R2 dial evidence: %s: H(%d) %.4f vs I %.4f" % (c, hs, t[hs][c], tI[c]))
    # R4: C1's near-miss column, H(h*) against C5 (the engine route)
    for pat in CARD_PATS["C1"]:
        for ly in ("off", "on"):
            hv = rows.get(("C1", pat, "I" if hs in same.get(pat, []) else "h%d" % hs, "near-miss", ly))
            ev = rows.get(("C5", pat, "engine", "near-miss", "off"))
            if hv and ev and hv["status"] == ev["status"] == "ok" and hv["med"] / ev["med"] > 1 + f:
                lines.append("R4 near-miss trigger (r45_reply §4): %s/%s H(%d) %.4f vs engine %.4f"
                             % (pat, ly, hs, hv["med"], ev["med"]))
    # C3 at h* (step 2b, F4): R2's C3 half and R5; absent, NOT COMPUTED and owed
    name = "results_c3_h%d.tsv" % hs
    if name not in c3files:
        lines.append("rule: R2(C3)/R5 NOT COMPUTED at h* = %d" % hs)
        lines.append("rule: NEXT cards.py c3 RUNDIR %d" % hs)
        res["code"] = 3
        return res
    r3, a3 = c3files[name]
    harm = "h%d" % hs
    if any(rg in APPROX for rg in REGIMES):
        lines.append("R5 C3: regimes %s void by method (not checked)" % ", ".join(sorted(APPROX)))
    for pat in CARD_PATS["C3"]:
        for rg in REGIMES:
            for ly in ("off", "on"):
                cid = "%s/%s/%s" % (pat, rg, ly)
                got = {a: r3.get(("C3", pat, a, rg, ly)) for a in ("I", "h0", harm)}
                bad = [a for a, r in got.items() if r is None or is_void(("C3", pat, a, rg, ly), r)]
                if rg in APPROX:
                    continue
                if bad:
                    lines.append("R5 C3 %s: VOID twice (%s): R2/R5 not checked there (recorded)"
                                 % (cid, ", ".join(bad)))
                    continue
                v = got[harm]["med"]
                if got["I"]["med"] < v / (1 + f):
                    lines.append("R2 dial evidence: C3 %s: H(%d) %.4f vs I %.4f" % (cid, hs, v, got["I"]["med"]))
                for other in ("I", "h0"):
                    if other != harm and v / got[other]["med"] > 1 + f:
                        lines.append("R5 long-span loss: C3 %s H(%d) %.4f vs %s %.4f" % (cid, hs, v, other,
                                                                                        got[other]["med"]))
    lines.append("rule: NEXT the build compiles h* = %d in; then cards.py identity %d (FROZEN=<this night's "
                 "build>)" % (hs, hs))
    return res


def cmd_rule(args):
    """R0-R5 over a night's RUNDIR. --g2 FILE: R0's input, one defective head per line (a head
    whose answers G2 failed)."""
    rundir = args[0]
    g2 = set()
    if "--g2" in args:
        g2 = {int(x) for x in open(args[args.index("--g2") + 1]).read().split()}
    v = analyse(load_night(rundir), g2)
    for ln in v["lines"]:
        print(ln)
    return v["code"]


@functools.lru_cache(maxsize=None)
def death_depth(pat):
    """E[D] = sum_i prod_{j<i} mass(S_j), the masses from the miss-heavy subject's byte rate."""
    b = subject(pat, "miss-heavy", 1 << 16, 1)
    cnt = [0] * 256
    for x in b:
        cnt[x] += 1
    mass = [sum(cnt[ord(ch)] for ch in set(s)) / len(b) for s in PATTERNS[pat][1]]
    e, p = 0.0, 1.0
    for ms in mass:
        e += p
        p *= ms
    return e


# ---- the drills (r45_reply rev 7 §3 "Drills"), each with the result the design states ------
def drill(spec):
    """spec: f, heads, cells [(id, k)], ratios {h: [per cell]} (t(I) = 1 unless tI given),
    void [ids]; the default ratio is 1.0 (a head that ties I)."""
    f = spec.get("f", 0.025)
    heads = spec.get("heads", GRID)
    cl = spec["cells"]
    tI = {c: spec.get("tI", {}).get(c, 1.0) for c, _k in cl}
    t = {h: {} for h in heads}
    for h in heads:
        r = spec["ratios"].get(h, spec.get("default", {}).get(h))
        for i, (c, k) in enumerate(cl):
            v = r[i] if isinstance(r, list) else (r if r is not None else 1.0)
            t[h][c] = v if h < k else tI[c]     # H(h) renders exactly I where h >= k
            if h >= k and isinstance(r, list) and r[i] != tI[c]:
                raise SystemExit("drill data: H(%d) differs from I in cell %s (k %d)" % (h, c, k))
    void = spec.get("void", [])
    read = [c for c, _k in cl if c not in void]
    same = {h: {c: h >= k for c, k in cl} for h in heads}
    return r1(heads, read, void, t, tI, same, f)


LOSE = 1.20
DRILLS = [
    ("(i) I and H equal at k <= 32", {"cells": [("c24", 24), ("c32", 32)], "ratios": {}},
     64, "on a measured tie of every finite head"),
    ("(ii) I faster in one cell (k 24)", {"cells": [("c24", 24), ("c32", 32)],
                                          "ratios": {h: [1.10, 1.0] for h in (0, 1, 2, 4, 8, 16)}},
     64, "on a measured tie of {24, 32, 64}"),
    ("(iii) L faster everywhere", {"cells": [("c24", 24), ("c60", 60)],
                                   "ratios": {0: [0.80, 0.80]}}, 0, "MEASURED"),
    ("(iv) all within noise", {"cells": [("c%d" % i, 60) for i in range(6)],
                               "ratios": {h: [1 + ((h * 7 + i * 13) % 19 - 9) / 1000 for i in range(6)]
                                          for h in GRID if h < 60}},
     64, "on a measured tie of every finite head"),
    ("(v) I faster in both k 60 cells", {"cells": [("a60", 60), ("b60", 60)],
                                         "ratios": {h: [1.08, 1.06] for h in GRID if h < 60}},
     64, "(64, CHOSEN): every shorter finite head measured slower beyond f"),
    ("(vi) near-equal chain", {"cells": [("c60", 60)],
                               "ratios": {0: [0.94], 1: [0.92], 2: [0.90], 4: [1.12], 8: [1.12],
                                          16: [1.12], 24: [1.12], 32: [1.12]}}, 2, "MEASURED"),
    ("(vii) a losing value outside E", {"f": 0.01, "heads": [0, 4, 8],
                                        "cells": [("c1", 60), ("c2", 60)], "tI": {"c1": 1.20, "c2": 1.20},
                                        "ratios": {0: [1.00, 1.10], 8: [1.08, 1.00], 4: [0.80, 2.00]}},
     8, "MEASURED"),
    ("(vii') without the losing value", {"f": 0.01, "heads": [0, 8],
                                         "cells": [("c1", 60), ("c2", 60)], "tI": {"c1": 1.20, "c2": 1.20},
                                         "ratios": {0: [1.00, 1.10], 8: [1.08, 1.00]}}, 8, "MEASURED"),
    ("(viii) H(64) fails G2 (R0) on (ii)'s data", {"heads": [0, 1, 2, 4, 8, 16, 24, 32],
                                                    "cells": [("c24", 24), ("c32", 32)],
                                                    "ratios": {h: [1.10, 1.0] for h in (0, 1, 2, 4, 8, 16)}},
     32, "MEASURED"),
    ("(viii) every finite head fails R0", {"heads": [], "cells": [("c24", 24)], "ratios": {}},
     None, "no form ships"),
    ("(ix) a dominance cycle", {"cells": [("c1", 60), ("c2", 60), ("c3", 60)],
                                "ratios": {0: [LOSE] * 3, 1: [LOSE] * 3, 2: [LOSE] * 3, 4: [LOSE] * 3,
                                           24: [LOSE] * 3, 8: [0.95, 1.02, 0.99], 16: [0.97, 0.99, 1.00],
                                           32: [0.99, 1.00, 0.97]}}, 32, "MEASURED"),
    ("R3-1: H(8) best in one cell, H(32) in another",
     {"cells": [("c24", 24), ("c60", 60), ("c3", 60)],
      "ratios": {0: [LOSE] * 3, 1: [LOSE] * 3, 2: [LOSE] * 3, 4: [LOSE] * 3,
                 8: [0.80, 0.95, 1.00], 32: [1.00, 0.85, 1.00]}}, 32, "MEASURED"),
    ("(x) one cell, no new minimum", {"cells": [("c", 60)],
                                      "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [LOSE],
                                                 8: [0.97], 16: [0.99]}}, 16, "MEASURED"),
    ("(x) h = 4 at 0.95, the new minimum", {"cells": [("c", 60)],
                                            "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [0.95],
                                                       8: [0.97], 16: [0.99]}}, 8, "MEASURED"),
    ("(x) h = 4 at 0.985, not the minimum", {"cells": [("c", 60)],
                                             "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [0.985],
                                                        8: [0.97], 16: [0.99]}}, 16, "MEASURED"),
    ("(xi) two cells", {"heads": [0, 1, 2, 4, 8, 16, 24, 32, 64], "cells": [("c1", 60), ("c2", 60)],
                        "ratios": {0: [LOSE] * 2, 1: [LOSE] * 2, 2: [LOSE] * 2, 4: [LOSE] * 2,
                                   8: [0.97, 0.97], 16: [0.99, 0.99]}}, 16, "MEASURED"),
    ("(xi) h = 12 joins E and dominates 16", {"heads": [0, 1, 2, 4, 8, 12, 16, 24, 32, 64],
                                              "cells": [("c1", 60), ("c2", 60)],
                                              "ratios": {0: [LOSE] * 2, 1: [LOSE] * 2, 2: [LOSE] * 2,
                                                         4: [LOSE] * 2, 8: [0.97, 0.97],
                                                         12: [0.985, 0.95], 16: [0.99, 0.99]}},
     12, "MEASURED"),
    ("(xii) drill V read clean", {"f": 0.04, "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                  "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0], 2: [LOSE] * 3 + [1.0],
                                             4: [LOSE] * 3 + [1.0], 16: [LOSE] * 3 + [1.0],
                                             8: [0.90, 0.93, 0.95, 1.0], 24: [0.95, 0.90, 0.93, 1.0],
                                             32: [0.93, 0.95, 0.90, 1.0]}}, 32, "MEASURED"),
    ("(xii) drill V, k 24 void twice", {"f": 0.04, "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                        "void": ["k24"],
                                        "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0],
                                                   2: [LOSE] * 3 + [1.0], 4: [LOSE] * 3 + [1.0],
                                                   16: [LOSE] * 3 + [1.0], 8: [0.90, 0.93, 0.95, 1.0],
                                                   24: [0.95, 0.90, 0.93, 1.0], 32: [0.93, 0.95, 0.90, 1.0]}},
     64, "cell(s) k24 void twice; the cells read picked H(8)"),
    ("(xii) drill V, k 40 void twice", {"f": 0.04, "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                        "void": ["k40"],
                                        "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0],
                                                   2: [LOSE] * 3 + [1.0], 4: [LOSE] * 3 + [1.0],
                                                   16: [LOSE] * 3 + [1.0], 8: [0.90, 0.93, 0.95, 1.0],
                                                   24: [0.95, 0.90, 0.93, 1.0], 32: [0.93, 0.95, 0.90, 1.0]}},
     64, "cell(s) k40 void twice; the cells read picked H(32)"),
    ("(xii') k 24 void twice, H(64) failed R0", {"f": 0.04, "heads": [0, 1, 2, 4, 8, 16, 24, 32],
                                                 "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                                 "void": ["k24"],
                                                 "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0],
                                                            2: [LOSE] * 3 + [1.0], 4: [LOSE] * 3 + [1.0],
                                                            16: [LOSE] * 3 + [1.0], 8: [0.90, 0.93, 0.95, 1.0],
                                                            24: [0.95, 0.90, 0.93, 1.0],
                                                            32: [0.93, 0.95, 0.90, 1.0]}},
     32, "h = 32, the largest R0-surviving head"),
    ("(xiii) drill N, a NOT-WARM-only loss", {"f": 0.02, "cells": [("hd32", 32), ("nw32", 32)],
                                              "ratios": {8: [0.90, 1.20], 16: [0.99, 1.0], 24: [0.99, 1.0]}},
     64, "on a measured tie of {0, 1, 2, 4, 16, 24, 32, 64}"),
    ("(xiv) a regime's method missing", {"f": 0.02, "cells": [("hd32", 32), ("nw32", 32), ("nw24", 24)],
                                         "void": ["nw32", "nw24"],
                                         "ratios": {8: [0.90, 1.20, 1.0], 16: [0.99, 1.0, 1.0],
                                                    24: [0.99, 1.0, 1.0]}},
     64, "cell(s) nw24, nw32 void twice; the cells read picked H(8)"),
]


# ---- synthetic nights: the noise, unimodal and void/R0/re-run drills (rev 7, F2-F7) --------
def synth_rows(rng, sigma, wins=None, noise="normal", bimodal_cells=(), approx_read=True, regimes=None):
    """A synthetic step-1 results set: C1-C2 every arm, A/A every regime and layer; each arm cell's
    LAUNCHES launches are T x exp(noise) with T the cell's true time (one per pattern/regime/
    layer, every arm equal: pure noise) times the arm's `wins` factor where its text is not I's.
    Regimes are all READ (`approx_read`: the bench's methods present), so the rule's floor and
    dominance see the real cell count (108 C1-C2 cells x 9 heads)."""
    wins = wins or {}
    rows = {}

    def eps():
        if noise == "t5":
            return rng.gauss(0, 1) / math.sqrt(rng.gammavariate(2.5, 2.0) / 5) / math.sqrt(5 / 3)
        return rng.gauss(0, 1)

    def put(key, T):
        if key[:5] in bimodal_cells or (key[1], key[3], key[4]) in bimodal_cells:
            ls = [T * math.exp(sigma * eps()) * (1.08 if i < 2 else 1.0) for i in range(LAUNCHES)]
        else:
            ls = [T * math.exp(sigma * eps()) for _ in range(LAUNCHES)]
        rows[key] = {"status": "ok", "med": statistics.median(ls), "launches": ls,
                     "method": "kit" if approx_read else method_of(key[3]), "note": ""}
    same = {}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            k = len(PATTERNS[pat][1])
            lit = pat in ("lit40", "abc60")
            same[pat] = [h for h in GRID if lit or h >= k]
            for rg in (regimes or REGIMES):
                for ly in ("off", "on"):
                    T = rng.uniform(0.2, 2.0)
                    put((card, pat, "I", rg, ly), T)
                    for h in GRID:
                        put((card, pat, "h%d" % h, rg, ly), T * (1.0 if h in same[pat] else wins.get(h, 1.0)))
    for rg in (regimes or REGIMES):
        for ly in ("off", "on"):
            T = rng.uniform(0.2, 2.0)
            put(("AA", "lit16", "aa", rg, ly), T)
            put(("AA", "lit16", "aa-twin", rg, ly), T)
    return rows, same


def synth_night(rng, sigma, **kw):
    """One whole synthetic night through `analyse`: step 1, then the re-run of any cell void once
    (fresh launches), so the drill exercises the merge too."""
    global APPROX
    keep = APPROX
    APPROX = {}                   # every regime read: the bench's methods present
    try:
        rows, same = synth_rows(rng, sigma, **kw)
        night = {"files": {"results.tsv": (rows, {})}, "same": same}
        v = analyse(night, set())
        voided_first = sum(len(s) for s in v["owed_rerun"].values())
        if v["owed_rerun"].get("results.tsv"):
            kw2 = dict(kw, bimodal_cells=())
            fresh, _s = synth_rows(rng, sigma, **kw2)
            redo = {k: r for k, r in fresh.items() if (k[0], k[1], k[3], k[4]) in v["owed_rerun"]["results.tsv"]}
            night["files"]["results.tsv"] = (rows, redo)
            v = analyse(night, set())
        v["voided_first"] = voided_first
        return v
    finally:
        APPROX = keep


NOISE_TRIALS = 300


def noise_drill(trials=NOISE_TRIALS, sigma=0.01, noise="normal", seed=1):
    rng = random.Random(seed)
    off, voids, fs = 0, 0, []
    for _ in range(trials):
        v = synth_night(rng, sigma, noise=noise)
        off += v["hstar"] != GRID_TOP
        voids += v["voided_first"] > 0
        fs.append(v.get("f", 0))
    return off / trials, voids, statistics.median(fs)


def cmd_selftest(_args):
    bad = 0
    for name, spec, want_h, want_label in DRILLS:
        h, label, rec, det = drill(spec)
        ok = h == want_h and want_label in label
        bad += not ok
        print("%s %-48s h* = %-4s %s" % ("ok  " if ok else "FAIL", name, h, label))
        if not ok:
            print("     want h* = %s, a label holding %r; detail %s" % (want_h, want_label, det))

    def check(name, ok, line):
        nonlocal bad
        bad += not ok
        print("%s %-48s %s" % ("ok  " if ok else "FAIL", name, line))

    # F2: THE NOISE DRILL at the real cell count (108 C1-C2 cells x 9 heads), >= 300 trials
    p, nv, fmed = noise_drill()
    check("(F2) noise drill, normal launches sigma 1 %", p <= 0.05,
          "P(h* != 64) = %.3f over %d trials (accept <= 0.05); median f %.4f; nights with a first void %d"
          % (p, NOISE_TRIALS, fmed, nv))
    p5, nv5, fmed5 = noise_drill(noise="t5", seed=2)
    check("(F2) noise drill, t(5) launches sigma 1 %", p5 <= 0.05,
          "P(h* != 64) = %.3f over %d trials (accept <= 0.05); median f %.4f; nights with a first void %d"
          % (p5, NOISE_TRIALS, fmed5, nv5))
    # its power (the floor's cost, recorded): a true 10 % win of every head <= 8 where it loops
    rng = random.Random(3)
    picks = [synth_night(rng, 0.01, wins={h: 0.90 for h in (0, 1, 2, 4, 8)})["hstar"] for _ in range(60)]
    check("(F2) power: a true 10 % win at h <= 8", sum(x == 8 for x in picks) / 60 >= 0.9,
          "h* = 8 in %d of 60 nights (picks %s)" % (sum(x == 8 for x in picks), sorted(set(picks))))
    # F3: THE UNIMODAL DRILL: unimodal launches must not void (per night, and per cell)
    rng = random.Random(4)
    nights, cellsv, ncell = 0, 0, 0
    for _ in range(NOISE_TRIALS):
        v = synth_night(rng, 0.01, noise="t5")
        nights += v["voided_first"] > 0
        cellsv += v["voided_first"]
        ncell += 108 + 12
    check("(F3) unimodal drill, t(5) launches", nights / NOISE_TRIALS <= 0.05,
          "void rate %.3f of nights, %.5f of cells over %d nights (accept <= 0.05)"
          % (nights / NOISE_TRIALS, cellsv / ncell, NOISE_TRIALS))
    # its control: a truly bimodal arm (2 of 5 launches 8 % slow) must void
    rng = random.Random(5)
    hit = 0
    for _ in range(50):
        APP, globals()["APPROX"] = APPROX, {}
        try:
            rows, same = synth_rows(rng, 0.01, bimodal_cells=[("C1", "hex32", "h8", "hit-dense", "off")])
            v = analyse({"files": {"results.tsv": (rows, {})}, "same": same}, set())
        finally:
            globals()["APPROX"] = APP
        hit += ("C1", "hex32", "hit-dense", "off") in v["owed_rerun"].get("results.tsv", set())
    check("(F3) control: a bimodal arm voids", hit >= 45,
          "2 of 5 launches 8 %% slow (~8 launch sigmas): voided in %d of 50 (accept >= 45)" % hit)

    # F7: the re-run merge: void once -> owed; re-run clean -> read; re-run void -> void twice
    def night_with(first_bimodal, rerun_bimodal, g2=(), c3=None, seed=6):
        rng = random.Random(seed)
        APP, globals()["APPROX"] = APPROX, {}
        try:
            cell = ("C1", "hex32", "h8", "hit-dense", "off")
            rows, same = synth_rows(rng, 0.01, bimodal_cells=[cell] if first_bimodal else [])
            files = {"results.tsv": (rows, {})}
            if rerun_bimodal is not None:
                fresh, _s = synth_rows(rng, 0.01, bimodal_cells=[cell] if rerun_bimodal else [])
                files["results.tsv"] = (rows, {k: r for k, r in fresh.items()
                                               if (k[0], k[1], k[3], k[4]) == ("C1", "hex32", "hit-dense", "off")})
            if c3 is not None:
                files.update(c3)
            return analyse({"files": files, "same": same}, set(g2))
        finally:
            globals()["APPROX"] = APP
    v = night_with(True, None)
    check("(F7) a cell void once", v["code"] == 3 and v["hstar"] is None and any("rerun" in l for l in v["lines"]),
          "code %d; %s" % (v["code"], v["lines"][-1]))
    v = night_with(True, False)
    check("(F7) re-run clean: the cell is read", v["hstar"] == GRID_TOP and v["rec"] is None,
          "h* %s, %s" % (v["hstar"], v["label"]))
    v = night_with(True, True)
    check("(F7) re-run void again: void twice, step (5)", v["hstar"] == GRID_TOP and v["rec"] is not None
          and "void twice" in v["label"], "h* %s, %s" % (v["hstar"], v["label"]))
    # F5: step (5) with G2's 64 defective and a void cell: the largest R0-surviving head, not 64
    v = night_with(True, True, g2=[64])
    check("(F5) step (5) after R0 removed 64", v["hstar"] == 32 and "largest R0-surviving" in v["label"],
          "h* %s, %s" % (v["hstar"], v["label"]))

    # F5's worse case: H(64) fails its gate in C3 (the only card where it loops): never a clean tie
    def c3_rows(h, gatefail_arm=None):
        rng = random.Random(7)
        r3 = {}
        for pat in CARD_PATS["C3"]:
            for rg in REGIMES:
                for ly in ("off", "on"):
                    T = rng.uniform(0.2, 2.0)
                    for a in dict.fromkeys(("I", "h0", "h%d" % h)):
                        if a == gatefail_arm and pat == "hex1000" and rg == "hit-dense" and ly == "off":
                            r3[("C3", pat, a, rg, ly)] = {"status": "gatefail", "med": None, "launches": [],
                                                          "method": "kit", "note": "GATE FAIL"}
                            continue
                        ls = [T * math.exp(0.01 * rng.gauss(0, 1)) for _ in range(LAUNCHES)]
                        r3[("C3", pat, a, rg, ly)] = {"status": "ok", "med": statistics.median(ls),
                                                      "launches": ls, "method": "kit", "note": ""}
        return {"results_c3_h%d.tsv" % h: (r3, {})}
    v = night_with(False, None, c3=c3_rows(64, gatefail_arm="h64"))
    check("(F5) C3 gate fail of H(64): not a clean tie", v["hstar"] != GRID_TOP
          and any("H(64) failed its gate in C3" in l for l in v["lines"]) and v["code"] == 3,
          "h* %s, code %d; %s" % (v["hstar"], v["code"], v["label"]))
    v = night_with(False, None, c3=c3_rows(64))
    check("(F4) C3 timed at h* = 64: R2(C3)/R5 computed", v["code"] == 0 and v["hstar"] == GRID_TOP
          and not any("NOT COMPUTED" in l for l in v["lines"]), "code %d; %s" % (v["code"], v["lines"][-1]))
    v = night_with(False, None)
    check("(F4) C3 not yet timed at h*", v["code"] == 3 and any("NOT COMPUTED at h* = 64" in l for l in v["lines"]),
          v["lines"][-1])
    # F8: the approximated regimes are void by method: step (5) fires, the pick is recorded
    rng = random.Random(8)
    rows, same = synth_rows(rng, 0.01, approx_read=False)
    v = analyse({"files": {"results.tsv": (rows, {})}, "same": same}, set())
    check("(F8) approximated regimes void by method", v["hstar"] == GRID_TOP and "void by method" in v["label"],
          "h* %s; %s" % (v["hstar"], v["label"][:110]))
    # r35 F15: the deny check fires on an arm-I artifact that carries a span loop, and passes a clean one
    loop = b"x = ({ size_t rxa_mf1_j = 0; for (; rxa_mf1_j < 31; rxa_mf1_j++) if (!(a)) break; });"
    lk, rc_ = loop_audit([("p I off", "I", loop), ("p h0 off", "h0", loop)])
    check("(F15) deny check: a looping arm I fails", lk == ["p I off"] and rc_ == ["p h0 off"], "leaks %s reach %s" % (lk, rc_))
    lk, rc_ = loop_audit([("p I off", "I", b"for (;;) { }"), ("p h0 off", "h0", loop)])
    check("(F15) deny check: a clean arm I passes", lk == [] and rc_ == ["p h0 off"], "leaks %s reach %s" % (lk, rc_))
    print("selftest: %d checks, %d failed" % (len(DRILLS) + 16, bad))
    return 1 if bad else 0


# ---- the identity check (r45_reply rev 7 §3 "The head lever and its identity check") -------
ENCODINGS = {"byte": [], "utf8": ["-e", "utf8"]}


def census_covers(frozen_pcrec, limit=None):
    """Every corpus pattern the FROZEN pcrec covers in either encoding: the sweep's own population
    (scripts/emit_sweep.py enumerate_corpus) read through `--emit-facts`'s `cover` section, the
    census of record (cover_cap.md §6: "the sweep's count is the count of record"; r35 F9)."""
    sys.path.insert(0, os.path.join(TREE, "scripts"))
    import emit_sweep as es     # noqa: E402
    # the sweep decodes escapes to bytes; argv takes them back through the fs encoding
    pats = sorted({os.fsdecode(p) if isinstance(p, bytes) else p
                   for _f, _k, p in es.enumerate_corpus(frozen_pcrec, TREE, 60)})
    if limit:
        pats = pats[:limit]

    def covered(p):
        r = subprocess.run([frozen_pcrec, "--features", "all", "--emit-facts=byte,utf8", "--pattern", p],
                           capture_output=True, timeout=120)
        sect = ""
        for ln in r.stdout.decode("latin-1").splitlines():
            if ln.startswith("#section "):
                sect = ln.split(None, 1)[1]
            elif sect == "cover" and not ln.startswith("#"):
                f = ln.split("\t")
                if len(f) > 1 and f[1] == "cover":
                    return p
        return None
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
        return len(pats), [p for p in ex.map(covered, pats) if p]


def cmd_identity(args):
    """The lever at H on the FROZEN binary (pcrec-harness --harness=span-head=H) against the
    REBUILT build/pcrec, byte for byte, both encodings and both layers, over the card patterns,
    the census covers (read from the sweep's corpus) and the PATTERNS file (main's predicted
    movers; REQUIRED when H < 64). --census-limit N is a SMOKE (exit 4, never a verdict)."""
    if not os.environ.get("FROZEN"):
        raise SystemExit("identity: FROZEN is unset: name the build dir the cards timed (an unset FROZEN would "
                         "compare the rebuilt tree's own harness, losing the frozen-to-rebuilt tie; r35 F9)")
    h = int(args[0])
    rest = [a for a in args[1:] if not a.startswith("--census-limit")]
    limit = None
    if "--census-limit" in args:
        limit = int(args[args.index("--census-limit") + 1])
        rest = [a for a in rest if a != str(limit)]
    rebuilt_dir = os.environ.get("REBUILT") or os.path.join(TREE, "build")
    if os.path.realpath(rebuilt_dir) == os.path.realpath(BUILD):
        raise SystemExit("identity: FROZEN and REBUILT are one build dir (%s): nothing ties the frozen binary "
                         "to the rebuilt one" % BUILD)
    if h < GRID_TOP and not rest:
        raise SystemExit("identity: h = %d < %d and no PATTERNS file: the predicted movers are the population "
                         "at h* < 64 (r45_reply §3); refusing to pass on the cards alone" % (h, GRID_TOP))
    pats = sorted({p[0] for p in PATTERNS.values()})
    n_corpus, census = census_covers(PCREC, limit)
    print("identity: census: %d corpus patterns read, %d covered by the frozen pcrec" % (n_corpus, len(census)))
    if not census:
        print("identity: FAIL: the census is empty (K35)")
        return 1
    movers = []
    if rest:
        movers = [ln.rstrip("\n") for ln in open(rest[0], encoding="latin-1") if ln.strip()]
        print("identity: predicted movers: %d (%s)" % (len(movers), rest[0]))
    allp = sorted(set(pats) | set(census) | set(movers))
    rebuilt = os.path.join(rebuilt_dir, "pcrec")
    wf = [] if WIDTH_FLAG == "none" else [WIDTH_FLAG]

    def one(job):
        p, ename, ly = job
        base = ["-p", PREFIX, "--features", "all"] + ENCODINGS[ename] + wf + LAYERS[ly] + ["-o", "-", "--pattern", p]
        a = subprocess.run([HARNESS, "--harness=span-head=%d" % h] + base, capture_output=True, timeout=600)
        b = subprocess.run([rebuilt] + base, capture_output=True, timeout=600)
        return job, a.returncode != b.returncode or a.stdout != b.stdout
    jobs = [(p, e, ly) for p in allp for e in ENCODINGS for ly in LAYERS]
    diff = 0
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
        for (p, e, ly), d in ex.map(one, jobs):
            if d:
                diff += 1
                print("IDENTITY DIFFERS: %r %s %s" % (p, e, ly))
    print("identity: head %d, %d patterns (cards %d, census %d, movers %d) x %d encodings x %d layers, %d differ"
          % (h, len(allp), len(pats), len(census), len(movers), len(ENCODINGS), len(LAYERS), diff))
    if limit:
        print("identity: SMOKE (--census-limit %d): not a verdict" % limit)
        return 4
    return 1 if diff else 0


def main():
    cmds = {"plan": cmd_plan, "dry": cmd_dry, "run": cmd_run, "rerun": cmd_rerun, "rule": cmd_rule,
            "c3": cmd_c3, "selftest": cmd_selftest, "identity": cmd_identity}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[sys.argv[1]](sys.argv[2:]) or 0


if __name__ == "__main__":
    sys.exit(main())
