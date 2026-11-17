#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (lane forms, R-45 plan A; lane formsfixa,
# review 2026-11-17 r35's F2-F11; lane formsfixc, review r36's G2-G8 and rulings R1; lane formsfixe,
# review r37's H1-H4, H7: the twin term, the agreement gate, the pool record and reach refusals;
# lane formsfixg, review r38's J1, J2, J7, J8: the per-pattern twin term, the launch rounds, the
# class drill, the identity reach per source; lane formsfixi, review r39's K1-K6, K8, K12: the layout
# twins, R0 over the confirm, reading B, one owed list, the checked controls).
"""memfn/tests/span_forms/cards.py -- THE SPAN FORMS' CARDS C1-C5, their rule R0-R5 and the
identity check (docs/design/memfn/r45_reply.md rev 11 §3 "The cards", "The head `h` and the
default", "The head lever and its identity check"; cards kit-grid@7 in
memfn/data/cards/kit-grid.tsv).

The kit's measurement script for the forms I / L / H(h) (memfn/src/window.c, THE SPAN FORMS).
Every cell compiles a card pattern at PCREC level on ONE binary (the frozen combined-branch
build), h set through the TEST-ONLY lever (`build/pcrec-harness --harness=span-head=N`, never a
shipped compile), I as the deny `--memfn=no-span-loop`, the engine route (C5) as
`--memfn=no-window-search`; the artifact plus one find-all wrapper is one C file per cell, its
answers gated against python `re` before any timing.

THE NIGHT (r45_reply rev 11 §3 "the night order"; each step a command, RUNDIR one directory):
  plan                     every cell (card, pattern, arm, regime, layer), the counts and the
                           EXPECTED WALL TIME of each timing step (UNMEASURED constants, named)
  dry RUNDIR [--quick]     builds EVERY cell (compile, gcc, the gate on every regime's
                           subject; C4's size record at the grid top) and prints the cell list
                           and count; no clock
  run RUNDIR [--with-approx]
                           step 1: times C1, C2, C5 and the A/A cells (results.tsv), each
                           cell in ROUNDS of one launch per arm (rev 10, r38 J2); C1-C2
                           cells include I's LAYOUT TWIN `I.lt`, the A/A pair is aa and its
                           layout twin (rev 11, r39 K1). Regimes
                           the kit only APPROXIMATES are void by method (rev 7, F8) and are not
                           timed unless --with-approx (a record only; the rule never reads them)
  rerun RUNDIR [--g2 FILE] re-times what `rule` OWES, computed by the SAME function with the
                           same recorded G2 list (rev 11, r39 K6): every cell VOID ONCE (all
                           its arms) into results_rerun.tsv / results_c3_h<H>_rerun.tsv (rev 7,
                           F7); once none is void, the CONFIRM: each cell holding a head's win
                           beyond f, timed on FRESH layout twins (I.cf and each winning head's
                           h<N>.cf), into results_confirm.tsv (rev 10 R2; rev 11 K1)
  rule RUNDIR [--g2 FILE]  R0-R5: the floor, h*, its label, the filings; exit 0 complete,
                           2 the night is void or defective, 3 a step is owed (a re-run, a
                           confirm, or C3 at h*); the line `rule: NEXT ...` names it. --g2
                           FILE (one G2-defective head a line) is RECORDED in
                           RUNDIR/rule_g2.json; every later `rule`/`rerun` reads the record
  c3 RUNDIR H              step 2b: times C3 at I, L and H(H) (results_c3_h<H>.tsv) and records
                           C4's sizes at H (sizes_h<H>.tsv); run at the h* `rule` picked (F4)
  selftest [--rev11]       the rule against every drill r45_reply rev 11 §3 lists, plus the noise
                           drill (F2), the unimodal drill (F3), the void/R0/re-run drills, the
                           CLASS drill (r38: noise, a step and a drift at every level) and rev
                           11's rows (r39: per-exe offsets, reading B's power, R0 over the
                           confirm, one owed list); --rev11 runs rev 11's rows alone
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

# ---- the rule's statistical constants (r45_reply rev 11 §3 "The floor `f`", "Void") ----------
# ALPHA: the rule's FAMILY-WISE false-pick budget, CHOSEN = the acceptance r35 F2 ruled (P(h* !=
# 64 on pure noise) <= 5 %). The floor is sized so that ALL the per-cell comparisons together
# show a false win beyond f with probability at most ALPHA (one-sided Bonferroni over N).
ALPHA = 0.05
# SIGMA_CONF: the one-sided confidence of the upper bound on the A/A sigma (12 cells estimate
# it; the bound pays for that estimate's own noise). CHOSEN.
SIGMA_CONF = 0.95
# GAP_K: a timed arm is BIMODAL when its launches split into two groups of >= 2 each with a gap
# of more than GAP_K launch sigmas between them (rev 7, F3). CHOSEN from a 2e7-sample simulation
# of 5 launches (lane formsfixa): P(gap > 4.5 sigma) is 1e-7 per arm under normal noise; under
# t(5) noise about 3e-5 per arm (r36 SIMULATE-7: the pooled sigma reads 0.908 of the true one,
# so the effective gap is ~4.1 true sigmas), consistent with the unimodal drill's 2-3 % of
# nights; its bimodal control shows the test can fire. A split that MOVES a median (3 of 5) at
# sizes f..2f is below any 5-launch gate at that false rate (rev 8 §3 "Bimodal"); I's POOLED
# reading carries that case (rulings R1).
GAP_K = 4.5
# MED_SD5: the median of the sample SD of 5 normal draws, in sigma units: sqrt(median
# chi2(4) / 4) = sqrt(3.3567 / 4). DERIVED. The launch sigma of a (regime, layer) pool is the
# median of its arms' launch SDs over this constant (a median, so one bimodal arm cannot
# inflate the pool's own scale).
MED_SD5 = 0.9161
# MIN_POOL: a pool with fewer timed arms borrows the night's pooled scale (for the bimodal test;
# the floor takes the larger of the two). CHOSEN; unreachable on a real night (92-105 arms a pool).
MIN_POOL = 10
# THE PER-POOL FLOOR TERM (rev 8, r36 G2). SDMED5: the SD of the median of 5 standard normal
# draws, sqrt(0.2868) (order-statistic tables; 0.5355 by 4e6 draws). DERIVED. A ratio of two
# arms' medians then has log SD sqrt(2) x SDMED5 x the pool's launch sigma.
SDMED5 = 0.5355
# MEDSD_REL: the relative standard error of the pool's sigma (a median of n launch SDs over
# MED_SD5), 1 / (2 f(m) m) per sqrt(n), f the density of a 5-draw SD at its median m: f(m) =
# chi2(4)'s density at 4 m^2 times 8 m = 1.148, so 1 / (2 x 1.148 x 0.9161) = 0.4754. DERIVED
# (asymptotic in n; a pool holds ~100 arms).
MEDSD_REL = 0.4754


# ---- LAYOUT TWINS (rev 11, RULED r39 K1) ------------------------------------------------------
# Every noise estimator rev 10 had was a contrast INSIDE ONE EXE (I's pool, the twin terms, the
# gate, the A/A pair: hash-equal artifacts run as one cached exe), while a head against I is TWO
# exes; an offset an exe carries as a whole (code placement, alignment) was read by nothing and
# replicated on the confirm. A LAYOUT TWIN is the same artifact's object code linked a second time
# behind a padding object (`.skip LAYOUT_PAD[n]` bytes of .text linked FIRST), so every function of
# the artifact and its driver sits at another address: byte-different, the same object code, the
# same answers (every twin cell is answer-gated like any cell; `dry` prints the proof). Arm names:
#   I.lt     I's layout twin 1, one more arm of I's pool in every C1-C2 cell (step 1)
#   aa-twin  the A/A arm's layout twin 1 (rev 10: the same exe as `aa`)
#   I.cf, h<N>.cf   the CONFIRM's fresh layout twins 2 of I and of each winning head
# UNMEASURED: the pad sizes are CHOSEN, about 1 KiB and 2 KiB, so the two twins sit at different
# addresses from the base and from each other; the shift `dry` MEASURES (nm, `rxa_search`) is the
# pad rounded up to the TU's .text alignment: 1,056-1,088 B (layout 1), 2,080-2,112 B (layout 2)
# on the 11-17 dry run (gcc 15.2).
LAYOUT_PAD = {1: 1040, 2: 2080}


def arm_base(arm):
    """The arm whose TEXT this arm compiles: `I.lt`/`I.cf` -> I, `h8.cf` -> h8, `aa-twin` -> aa."""
    return "aa" if arm == "aa-twin" else arm.split(".")[0]


def arm_lay(arm):
    """The arm's layout: 0 the base exe, 1 step 1's layout twin, 2 the confirm's fresh twin."""
    if arm == "aa-twin" or arm.endswith(".lt"):
        return 1
    return 2 if arm.endswith(".cf") else 0


def arm_head(arm):
    """The finite head an arm times (h8, h8.cf -> 8), else None."""
    b = arm_base(arm)
    return int(b[1:]) if b.startswith("h") else None


def arm_flags(arm):
    """The compile flags of an arm: I (the deny, today's text), h<N> (the lever), engine; a layout
    twin compiles its base arm's flags (one text)."""
    arm = arm_base(arm)
    if arm == "I":
        return HARNESS, ["--memfn=no-span-loop"]
    if arm == "engine":
        return HARNESS, ["--memfn=no-window-search"]
    if arm.startswith("h"):
        return HARNESS, ["--harness=span-head=%d" % int(arm[1:])]
    if arm == "aa":
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


# ---- the cards (r45_reply rev 11 §3 "The cards"; kit-grid@7) ---------------------------------
FINITE = ["h%d" % h for h in GRID]
CARD_ROWS = {"C1": "span_cross", "C2": "span_pop", "C3": "span_long", "C4": "span_size",
             "C5": "span_engine"}
CARDS = [
    # card, patterns, arms, regimes, layers, kind
    ("C1", ["hex24", "dig24", "hex32", "dig32"], ["I", "I.lt"] + FINITE, REGIMES, ["off", "on"], "time"),
    ("C2", ["uuid36", "lit40", "alt49", "abc60", "hex64"], ["I", "I.lt"] + FINITE, REGIMES, ["off", "on"], "time"),
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


def loop_audit(texts, reach_arm=None):
    """texts: [(label, arm, bytes)]. (arm-I cells whose text holds a span loop, reach cells that do;
    the reach cells are the non-I arms, or only `reach_arm`): a deny that is ignored is invisible
    to every other check (r35 F15), and a zero over I with a zero reach is vacuous (the caller
    fails that too)."""
    leaks = [l for l, a, t in texts if a == "I" and LOOP_RE.search(t)]
    reach = [l for l, a, t in texts if a != "I" and (reach_arm is None or a == reach_arm) and LOOP_RE.search(t)]
    return leaks, reach


def check_deny(rundir, cl, reach_arm=None, vacuous_why="the loop text moved, or no arm loops at this width"):
    """Every arm-I artifact of `cl` carries no span loop, and a reach artifact does (the reach
    control; `reach_arm` names its arm, else any non-I arm). `vacuous_why`: the caller's reading of
    an empty reach (rev 10, r38 J8: c3's is a width where H(64) loops nowhere, not a moved loop
    text). Returns (failures, n_I, n_reach)."""
    keys = sorted({(c[1], arm_base(c[2]), c[4], c[0] == "C4") for c in cl})     # a layout twin is its base's text
    texts = [("%s %s %s" % (k[0], k[1], k[2]), k[1], open(artifact(rundir, k[0], k[1], k[2], size=k[3]), "rb").read())
             for k in keys]
    leaks, reach = loop_audit(texts, reach_arm)
    nI = sum(1 for _l, a, _t in texts if a == "I")
    bad = ["DENY IGNORED: arm I emits a span loop: %s" % l for l in leaks]
    if not nI:
        bad.append("DENY CHECK VACUOUS: no arm-I artifact in the cell list")
    if not reach:
        bad.append("DENY CHECK VACUOUS: no %s artifact emits a span loop (%s)" % (reach_arm or "non-I", vacuous_why))
    return bad, nI, len(reach)


def _tmp(p):
    return "%s.%d.%d" % (p, os.getpid(), threading.get_ident())


def pad_object(rundir, lay):
    """The layout twin's padding object: one function of LAYOUT_PAD[lay] bytes of .text, linked
    FIRST so the artifact's and the driver's functions sit LAYOUT_PAD[lay] (rounded) higher."""
    o = os.path.join(rundir, "bin", "pad_L%d.o" % lay)
    if not os.path.exists(o):
        os.makedirs(os.path.dirname(o), exist_ok=True)
        src = _tmp(o) + ".c"
        open(src, "w").write("void cards_layout_pad_L%d(void) { __asm__ volatile (\".skip %d\"); }\n"
                             % (lay, LAYOUT_PAD[lay]))
        r = subprocess.run([CC, "-O2", "-c", "-o", _tmp(o), src], capture_output=True, timeout=300)
        os.remove(src)
        if r.returncode:
            raise RuntimeError("gcc pad L%d: %s" % (lay, r.stderr.decode()[-300:]))
        os.replace(_tmp(o), o)
    return o


def build_cell(rundir, pat, arm, layer):
    """The cell's binary (artifact + driver), gcc -O2; cached. The TU is compiled ONCE to an object
    (keyed by its text); the exe links that object alone (layout 0) or behind the arm's padding
    object (a layout twin, rev 11 r39 K1): one object code, its functions at another address."""
    a = artifact(rundir, pat, arm, layer)
    src = open(a, encoding="latin-1").read()
    key = _h(src, DRIVER)
    lay = arm_lay(arm)
    exe = os.path.join(rundir, "bin", "x_%s" % key + ("_L%d" % lay if lay else ""))
    if os.path.exists(exe):
        return exe, a
    os.makedirs(os.path.dirname(exe), exist_ok=True)
    obj = os.path.join(rundir, "bin", "o_%s.o" % key)
    if not os.path.exists(obj):
        tu = _tmp(obj) + ".src"
        open(tu, "w", encoding="latin-1").write("#include <stddef.h>\n#include <stdint.h>\n"
                                                 "#include <string.h>\n" + src + "\n" + DRIVER)
        # two arms can render the same text (H(h) is I where h >= k): each build its own temp names
        r = subprocess.run([CC, "-std=gnu11", "-O2", "-w", "-x", "c", "-c", "-o", _tmp(obj), tu],
                           capture_output=True, timeout=1800)
        if r.returncode:
            raise RuntimeError("gcc %s %s %s: %s" % (pat, arm, layer, r.stderr.decode()[-400:]))
        os.replace(_tmp(obj), obj)
        os.replace(tu, obj[:-2] + ".c")
    r = subprocess.run([CC, "-o", _tmp(exe)] + ([pad_object(rundir, lay)] if lay else []) + [obj],
                       capture_output=True, timeout=600)
    if r.returncode:
        raise RuntimeError("link %s %s %s: %s" % (pat, arm, layer, r.stderr.decode()[-400:]))
    os.replace(_tmp(exe), exe)
    return exe, a


def search_addr(exe):
    """The address of `rxa_search` in an exe (nm), or None."""
    r = subprocess.run(["nm", exe], capture_output=True, text=True, timeout=60)
    for ln in r.stdout.splitlines():
        f = ln.split()
        if len(f) == 3 and f[2] == PREFIX + "_search":
            return int(f[0], 16)
    return None


def layout_proof(rundir, pat, arm, layer):
    """(byte-different, the shift of rxa_search in bytes) of a layout twin against its base exe:
    the proof that the twin is ANOTHER layout of the same object code (its answers are the gate's)."""
    tw, _a = build_cell(rundir, pat, arm, layer)
    base, _b = build_cell(rundir, pat, arm_base(arm), layer)
    differ = open(tw, "rb").read() != open(base, "rb").read()
    at, ab = search_addr(tw), search_addr(base)
    return differ, (at - ab) if at is not None and ab is not None else None


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


def run_cell(rundir, cell, n):
    """The gate's line (no clock), or C4's size record. Timing is `time_cells`' (rev 10: the rounds)."""
    card, pat, arm, regime, layer = cell
    if card == "C4":
        cb, secs, rss, text = size_record(rundir, pat, arm, layer)
        return "size c_bytes=%d gcc_s=%.2f rss_kb=%d text=%d" % (cb, secs, rss, text)
    exe, _a = build_cell(rundir, pat, arm, layer)
    sp, k, s = subj_file(rundir, pat, regime, n)
    return _exec([exe, sp, str(REGIME_CODE.get(regime, 0)), k, s], cell).strip()


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


# ---- THE LAUNCH ORDER (rev 10, RULED r38 J2): interleaved within a cell --------------------
# Rev 9 timed a card's arm cells ARM-MAJOR (all 5 launches of one arm, then the next arm), so a
# step in box speed between I and its twins (h24, h32, h64 at k 24: last in the block) read as a
# head win no estimator could see (r38 J2). Rev 10 times each CELL (card, pattern, regime,
# layer) as ROUNDS: one launch of every arm per round, LAUNCHES rounds, so every arm of the
# cell samples the same stretch of time and a step or a drift moves every arm alike. Within a
# round the arms run in a fixed pseudo-random order per (cell, round), derived from the cell's
# key (no RNG state; `cards.py` and the drills read the same order): a step INSIDE the middle
# round splits the cell's arms into "before" and "after" at random, never twins against heads
# by construction. The cells' own order (the ruled night order inside a card) is unchanged.
def cell_groups(cl):
    """The cell list `cl` grouped by cell (card, pattern, regime, layer), in first-appearance order:
    [(cellkey, [arm cells])]."""
    groups = {}
    for c in cl:
        groups.setdefault((c[0], c[1], c[3], c[4]), []).append(c)
    return list(groups.items())


def round_arms(cs, r):
    """Round r's launch order over a cell's arm cells `cs`: a fixed permutation from the cell key."""
    return sorted(cs, key=lambda c: hashlib.sha256(("%s/%d" % ("/".join(c), r)).encode()).hexdigest())


def launch_order(cl, interleave=True):
    """[(arm cell, launch index)] in the order the night times them; interleave=False is rev 9's
    arm-major order (the drills' control)."""
    out = []
    if not interleave:
        for c in cl:
            out += [(c, i) for i in range(LAUNCHES)]
        return out
    for _k, cs in cell_groups(cl):
        for r in range(LAUNCHES):
            out += [(c, r) for c in round_arms(cs, r)]
    return out


def prepare_cell(rundir, cell, n):
    """The gate run (untimed) of one arm cell; returns its timed argv. Raises GateFail on a wrong
    answer, anything else on a void."""
    _card, pat, _arm, regime, _layer = cell
    exe, _a = build_cell(rundir, pat, cell[2], cell[4])
    sp, k, s = subj_file(rundir, pat, regime, n)
    code = str(REGIME_CODE.get(regime, 0))
    _exec([exe, sp, code, k, s], cell)
    return ["taskset", "-c", CPU, exe, sp, code, k, s]


def time_cells(rundir, cl, path, with_approx=True):
    env = dict(os.environ, CARD_TIME="1")
    with open(path, "a") as f:
        if os.path.getsize(path) == 0:
            f.write(HEADER)
        for _key, cs in cell_groups(cl):
            argv, launches, out = {}, {}, {}
            for c in cs:
                if c[3] in APPROX and not with_approx:
                    out[c] = row_line(c, "method", note="void by method: " + APPROX[c[3]])
                    continue
                try:
                    argv[c] = prepare_cell(rundir, c, SUBJECT_N)
                    launches[c] = []
                except GateFail as e:
                    out[c] = row_line(c, "gatefail", note=str(e))
                except Exception as e:      # noqa: BLE001 -- a void, re-run once (F7)
                    out[c] = row_line(c, "void", note=str(e))
            for r in range(LAUNCHES):       # the rounds (rev 10, J2): one launch of every arm per round
                for c in round_arms(list(argv), r):
                    if c in out:
                        continue
                    try:
                        launches[c].append(float(_exec(argv[c], c, env).split()[1]))
                    except Exception as e:      # noqa: BLE001 -- the arm is void, re-run once (F7)
                        out[c] = row_line(c, "void", note=str(e))
            for c in cs:
                f.write(out[c] if c in out else row_line(c, "ok", launches[c]))
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
    builds = {(c[1], arm_base(c[2]), c[4], c[0] == "C4") for c in cl}
    twins = {(c[1], c[2], c[4]) for c in cl if arm_lay(c[2])}
    print("# cells %d (%s); distinct compiles %d; layout-twin links %d (rev 11, r39 K1: I.lt and aa-twin, the compiled "
          "object linked behind a %s-byte pad)" % (len(cl), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                                  len(builds), len(twins), LAYOUT_PAD[1]))
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
    no_lt = [c for c in s1_read if c[2] != "I.lt"]
    print("#   run's layout twin I.lt (rev 11, r39 K1): +%d cells, +%.3f h over rev 10's step 1 (%.3f h without it: +%.1f %%)"
          % (len(s1_read) - len(no_lt), w(s1_read) - w(no_lt), w(no_lt), 100 * (w(s1_read) / w(no_lt) - 1)))
    print("#   c3:   %d cells timed, %.2f h (C4's sizes: compile-only, not in the window)" % (len(s2_read), w(s2_read)))
    na = len(GRID) + 2
    print("#   rerun: one cell per void, ~%.0f s per C1-C2 cell (%d arms)" % (na * EST_LAUNCH_S * (1 + LAUNCHES), na))
    # THE CONFIRM'S COST (rev 11, r39 K5): one re-run per winning (cell, head), on fresh layout twins (I.cf and the
    # head's .cf, each a link of an object `dry` compiled); its BOUND is every mover cell read with every moving head
    # winning; the one-win case is one head in one regime (its moving patterns x 2 layers)
    lp = EST_LAUNCH_S * (1 + LAUNCHES)
    movers = [(card, p, rg) for card in ("C1", "C2") for p in CARD_PATS[card] for rg in REGIMES if rg not in APPROX
              if p not in ("lit40", "abc60") and any(h < len(PATTERNS[p][1]) for h in GRID)]
    bound_arms = sum(2 * (1 + sum(1 for h in GRID if h < len(PATTERNS[p][1]))) for _c, p, _r in movers)
    one = sum(2 for card in ("C1", "C2") for p in CARD_PATS[card] if p not in ("lit40", "abc60") and 8 < len(PATTERNS[p][1]))
    print("#   confirm (rev 10, r38 R2; rev 11, r39 K1/K5): one re-run per winning (cell, head) on FRESH layout twins, ~%.0f s "
          "per cell and winning head (I.cf + h<N>.cf); BOUND (every mover cell read, every moving head winning): %d "
          "cells, %d arm cells, %.3f h; one real win of one head in one regime (H(8): %d cells) %.3f h; RECORD (rev 11 "
          "selftest, not computed here): a pure-noise night 0.000 confirm cells a night (normal and t(5) launches), "
          "per-exe offsets tau 1/2/3 %% mean <= 0.01 (max 4)" % (2 * lp, 2 * len(movers), bound_arms,
                                                               bound_arms * lp / 3600.0, one, one * 2 * lp / 3600.0))
    print("# timing order (rev 10, r38 J2): the cells above grouped by (card, pattern, regime, layer), each timed in "
          "%d ROUNDS of one launch per arm (`launch_order`): run %d cells, %d timed launches" % (
              LAUNCHES, len(cell_groups(s1_read)), len(launch_order(s1_read))))


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
            return c, run_cell(rundir, c, n), None
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
    cbad, cI, creach = c3_deny_check(rundir)
    print("# dry: step 2b's deny check (`c3` refuses on it; r37 H4): %d arm-I C3/C4 artifacts loop-free, reach "
          "(h%d) %d%s" % (cI, GRID_TOP, creach, "; WOULD REFUSE: " + "; ".join(cbad) if cbad else ""))
    # THE LAYOUT TWINS' PROOF (rev 11, r39 K1): step 1's twins (I.lt, aa-twin; gated above as cells) and the
    # confirm's fresh twin of I (I.cf, layout 2), built and answer-gated here in every regime of every C1-C2
    # pattern and layer; each twin must be BYTE-DIFFERENT from its base exe with rxa_search at another address
    # (the same object code, another layout). The confirm's head twins (h<N>.cf) are links of objects built here.
    cf = [(card, p, "I.cf", rg, ly) for card in ("C1", "C2") for p in CARD_PATS[card] for rg in REGIMES for ly in LAYERS]
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        cfout = list(ex.map(one, cf))
    cfbad = [err for _c, _o, err in cfout if err]
    bad += cfbad
    tw = sorted({(c[1], c[2], c[4]) for c in cl + cf if arm_lay(c[2])})
    proofs = {}
    for p, a, ly in tw:
        try:
            proofs[(p, a, ly)] = layout_proof(rundir, p, a, ly)
        except Exception as e:      # noqa: BLE001
            proofs[(p, a, ly)] = (False, None)
            bad.append("LAYOUT %s %s %s: %s" % (p, a, ly, e))
    notdiff = [k for k, (d, _s) in proofs.items() if not d]
    notmoved = [k for k, (_d, s) in proofs.items() if not s]
    shifts = sorted({s for _d, s in proofs.values() if s})
    bad += ["LAYOUT TWIN NOT BYTE-DIFFERENT: %s" % " ".join(k) for k in notdiff]
    bad += ["LAYOUT TWIN: rxa_search did not move: %s" % " ".join(k) for k in notmoved]
    ntw = sum(1 for c in cl if arm_lay(c[2]))
    print("# dry: layout twins (rev 11, r39 K1): %d twin exes (%d step 1, %d confirm I.cf), byte-different %d, rxa_search "
          "moved %d (shifts %s B); answer-gated: %d step 1 twin cells + %d I.cf cells, failures %d"
          % (len(tw), sum(1 for k in tw if arm_lay(k[1]) == 1), sum(1 for k in tw if arm_lay(k[1]) == 2),
             len(tw) - len(notdiff), len(tw) - len(notmoved), ",".join(map(str, shifts)) or "-", ntw, len(cf),
             len(cfbad) + sum(1 for c in cl if arm_lay(c[2]) and not done.get(c))))
    same = identical_to_I(rundir)
    print("# dry: cells %d, built and gated %d, failures %d; distinct compiles %d; subject %d B" %
          (len(cl), len(cl) - len(bad), len(bad), len({(b[0], arm_base(b[1]), b[2], b[3]) for b in builds}), n))
    print("# dry: H(h) artifact hash-equal to I's (I's pool, measured per layer): %s" % ", ".join(
        "%s/%s:%s" % (p, ly, ",".join(map(str, hs))) for p, d in sorted(same.items()) for ly, hs in sorted(d.items())))
    for b in bad[:20]:
        print("FAIL", b)
    return 1 if bad else 0


def identical_to_I(rundir):
    """Per C1-C2 pattern and LAYER, the finite heads whose built artifact hash-equals I's (MEASURED
    when the cells are built, never inferred from h >= k; rulings R1, rev 8 r36 G3: rev 7 read
    the SIMD-off layer for both). Where it does, the rule reads I's POOLED median for the head:
    one text, one binary, one reading (rev 7, F2)."""
    out = {}
    for card in ("C1", "C2"):
        for p in CARD_PATS[card]:
            out[p] = {}
            for ly in LAYERS:
                ia = hashlib.sha256(open(artifact(rundir, p, "I", ly), "rb").read()).hexdigest()
                out[p][ly] = [h for h in GRID if hashlib.sha256(
                    open(artifact(rundir, p, "h%d" % h, ly), "rb").read()).hexdigest() == ia]
    return out


def same_heads(same, pat, ly):
    """The heads whose text is I's for (pattern, layer), from the measured record (validated by
    `pool_record_refusal` before the rule reads it: no silent default, r37 H3)."""
    return same[pat][ly]


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


def c3_deny_check(rundir):
    """The deny check on step 2b's population (rev 8, r36 G7; rev 9, r37 H4). C3 and C4 are where
    an ignored deny loops; step 1's patterns never reach that. The REACH arm is the DEFECT'S OWN
    arm: an ignored deny renders I as the build's default head H(64), so the reach is H(64)'s
    artifacts over C3 and C4, rendered whatever h* the step times (rev 8's L proved the regex
    works, not that the defect's arm loops: at width 32 only C4's hex32 at h0 loops, and an
    ignored deny read GREEN). Where H(64) loops nowhere (width 32) the check is VACUOUS and red."""
    return check_deny(rundir, cells(hstar=GRID_TOP, cards=STEP2B), reach_arm="h%d" % GRID_TOP,
                      vacuous_why="H(%d) loops nowhere in C3/C4 at this window width (a width below the cards' "
                                  "longest span, e.g. 32), or its loop text moved" % GRID_TOP)


def cmd_c3(args):
    rundir, h = args[0], int(args[1])
    if h not in GRID:
        raise SystemExit("cards: c3: %d is not a finite grid head" % h)
    res = os.path.join(rundir, "results_c3_h%d.tsv" % h)
    if os.path.exists(res):
        raise SystemExit("cards: %s exists (re-runs: `rerun`)" % res)
    dbad, nI, nreach = c3_deny_check(rundir)
    print("cards: c3: deny check on C3 and C4: %d arm-I artifacts loop-free, reach (h%d, the arm an ignored deny "
          "renders) %d" % (nI, GRID_TOP, nreach))
    if dbad:
        for b in dbad:
            print("FAIL", b)
        raise SystemExit("cards: c3: the deny check failed; no timing")
    open(res, "w").close()
    time_cells(rundir, cells(hstar=h, cards=("C3",)), res, with_approx=False)
    with open(os.path.join(rundir, "sizes_h%d.tsv" % h), "w") as f:
        for c in cells(hstar=h, cards=("C4",)):
            try:
                f.write("\t".join(c) + "\t" + run_cell(rundir, c, 0) + "\n")
            except Exception as e:      # noqa: BLE001
                f.write("\t".join(c) + "\tFAIL " + str(e).replace("\n", " ")[:300] + "\n")
    print("cards: C3 at H(%d) in %s; next: cards.py rule %s" % (h, res, rundir))


G2_RECORD = "rule_g2.json"


def night_g2(rundir, g2file=None):
    """R0's G2 list for the night, ONE source for every command (rev 11, RULED r39 K6): `--g2 FILE`
    (one defective head per line) is recorded in RUNDIR/rule_g2.json; a command without `--g2`
    reads that record (none recorded: no G2-defective head). Returns (set, where it came from)."""
    rec = os.path.join(rundir, G2_RECORD)
    if g2file:
        g2 = {int(x) for x in open(g2file).read().split()}
        json.dump({"g2": sorted(g2), "from": os.path.abspath(g2file)}, open(rec, "w"))
        return g2, "from %s, recorded in %s" % (g2file, G2_RECORD)
    if os.path.exists(rec):
        return set(json.load(open(rec))["g2"]), "recorded in %s" % G2_RECORD
    return set(), "none given, none recorded"


def owed_now(rundir, g2file=None):
    """The rule over the night with its recorded G2 list: THE one computation of what is owed
    (`owed_rerun`, `owed_confirm`), called by `rule` and by `rerun` alike (rev 11, r39 K6: rev 10's
    `rerun` read an empty G2 list, owed a subset of `rule --g2`'s confirms, and the night stalled)."""
    g2, src = night_g2(rundir, g2file)
    v = analyse(load_night(rundir), g2)
    v["g2"], v["g2_src"] = g2, src
    return v


def confirm_cells(owed):
    """The confirm's arm cells for owed {(card, pat, regime, layer): [heads]}: I's fresh layout twin
    `I.cf` and each owed head's `h<N>.cf` (rev 11, r39 K1/K3)."""
    out = []
    for (card, pat, rg, ly), hs in sorted(owed.items()):
        out += [(card, pat, a, rg, ly) for a in ["I.cf"] + ["h%d.cf" % h for h in sorted(hs)]]
    return out


def cmd_rerun(args):
    """Re-times every cell the rule lists as void ONCE, all arms of the cell (F7), into
    results_rerun.tsv / results_c3_h<H>_rerun.tsv; and every cell the rule lists as holding a win
    beyond f, ONCE, into results_confirm.tsv (rev 10, r38 R2: confirm by re-run)."""
    rundir = args[0]
    v = owed_now(rundir, args[args.index("--g2") + 1] if "--g2" in args else None)
    print("cards: rerun: R0's G2 list %s (%s)" % (sorted(v["g2"]) or "none", v["g2_src"]))
    if v["code"] == 2:
        print("cards: rerun: the night is void or defective (`rule` says why); nothing to re-run")
        return 2
    todo = v["owed_rerun"]
    if v["owed_confirm"]:
        cl = confirm_cells(v["owed_confirm"])
        time_cells(rundir, cl, os.path.join(rundir, "results_confirm.tsv"))
        print("cards: confirming re-run of %d cells (%d arm cells: I's and each winning head's fresh layout twin) that "
              "hold a win beyond f" % (len(v["owed_confirm"]), len(cl)))
        return 0
    if not todo:
        print("cards: rerun: no cell is void once and no win awaits its confirm")
        return 0
    for src, cellkeys in todo.items():
        # every arm the card defines for the cell, whether or not step 1 wrote its row
        defined = (cells(cards=STEP1) if src == "results.tsv" else
                   cells(hstar=int(src[len("results_c3_h"):-len(".tsv")]), cards=("C3",)))
        cl = [k for k in defined if (k[0], k[1], k[3], k[4]) in cellkeys]
        time_cells(rundir, cl, os.path.join(rundir, src.replace(".tsv", "_rerun.tsv")))
        print("cards: re-timed %d cells (%d arm cells) of %s" % (len(cellkeys), len(cl), src))
    return 0


# ---- THE RULE (r45_reply rev 11 §3, R0-R5, steps (1)-(5)) -------------------------------------
def r1(heads, cells_read, void_cells, t, tI, same_as_I, f, top=None, measured="MEASURED", wins_ok=None):
    """R1 over the FINITE heads `heads` (R0 already applied). cells_read: the C1-C2 cells with a
    reading; void_cells: the cells void twice (or void by method); t[h][c], tI[c] the raw
    medians; same_as_I[h][c] true where H(h)'s text is I's in cell c; f the floor, one number
    or {cell: floor} (rev 8, r36 G2: each cell's (regime, layer) floor). `top`: the largest
    R0-surviving head (rev 8, r36 G5), never the constant. Returns (h*, label, recorded pick or
    None, detail); h* None when no finite head survives R0. `wins_ok`: the (head, cell) wins the
    confirm reproduced (rev 11, r39 K4 READING B: they gate step (4)'s "beat I beyond f" ONLY;
    W, E and dominance read the first reading); None: every first-reading win counts."""
    if not heads:
        return None, "no form ships: every finite head failed R0 (plan A's fallback: forms land OFF)", None, {}
    fc = (lambda c: f[c]) if isinstance(f, dict) else (lambda c: f)      # noqa: E731
    # E reads worst ratios across cells: its tolerance is the largest floor of the cells read
    fE = max((fc(c) for c in cells_read), default=max(f.values(), default=0.0) if isinstance(f, dict) else f)
    if top is None:
        top = max(heads)
    lead = ("h = grid top (%d, CHOSEN)" % top if top == GRID_TOP else
            "h = %d, the largest R0-surviving head (CHOSEN; the grid top failed R0)" % top)
    # (1) W(h): the worst ratio to I over the cells READ; a twice-void cell adds the term 1
    #     for each head whose text is I there, no term for any other head
    W = {}
    for h in heads:
        terms = [t[h][c] / tI[c] for c in cells_read]
        terms += [1.0 for c in void_cells if same_as_I[h][c]]
        W[h] = max(terms) if terms else float("inf")
    # (2) E, computed once, never chained
    m = min(W.values())
    E = sorted(h for h in heads if W[h] <= (1 + fE) * m)

    # (3) dominance over the cells READ only: g dominates h when g is faster beyond f in at
    #     least one cell and slower beyond f in none; keep the members dominated by the fewest
    def dom(g, h):
        faster = any(t[h][c] / t[g][c] > 1 + fc(c) for c in cells_read)
        slower = any(t[g][c] / t[h][c] > 1 + fc(c) for c in cells_read)
        return faster and not slower
    nd = {h: sum(1 for g in E if g != h and dom(g, h)) for h in E}
    least = min(nd.values())
    kept = [h for h in E if nd[h] == least]
    # (4) the LARGEST kept head that is the top or itself beat I beyond f in some cell read
    #     (rev 8, r36 G4: the tolerance is not transitive, so a kept head within f of a
    #     winner and within f of I measured no win and never ships)
    won = [h for h in kept if any(tI[c] / t[h][c] > 1 + fc(c) and (wins_ok is None or (h, c) in wins_ok)
                                  for c in cells_read)]
    cand = [h for h in kept if h == top or h in won]
    pick = max(cand) if cand else top
    if pick not in won:             # the top on a tie: CHOSEN (a top that measured a win is MEASURED)
        tie = "every finite head" if top == GRID_TOP else "every R0-surviving head"
        if not cand:
            label = "%s: no kept head (%s) measured a win against I beyond f" % (lead, ", ".join(map(str, kept)))
        elif E == sorted(heads):
            label = "%s, on a measured tie of %s" % (lead, tie)
        elif E == [top]:
            label = "%s: every shorter finite head measured slower beyond f" % lead
        else:
            label = "%s, on a measured tie of {%s}" % (lead, ", ".join(map(str, E)))
    else:
        label = measured
    detail = {"W": W, "E": E, "dominated_by": nd, "kept": kept, "won": won, "fE": fE}
    # (5) VOID: a C1-C2 cell void twice never helps a head; h* is the LARGEST R0-SURVIVING head
    #     (rev 7, F5), the grid top whenever it survives
    if void_cells:
        hs = top
        vs = sorted(void_cells)
        named = ", ".join(vs) if len(vs) <= 6 else "%s, ... (%d in all)" % (", ".join(vs[:4]), len(vs))
        return hs, ("%s: cell(s) %s void twice; the cells read picked H(%d)"
                    % (lead, named, pick)), pick, detail
    return pick, label, None, detail


def z_upper(p):
    """The standard normal quantile at 1 - p."""
    return statistics.NormalDist().inv_cdf(1 - p)


def _gamma_p(a, x):
    """The regularized lower incomplete gamma P(a, x): series below a + 1, Lentz's continued
    fraction for Q above (Numerical Recipes' split)."""
    if x <= 0:
        return 0.0
    lead = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a + 1:
        s = term = 1.0 / a
        ap = a
        for _ in range(10000):
            ap += 1
            term *= x / ap
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return s * lead
    tiny = 1e-300
    b = x + 1 - a
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return 1 - lead * h


@functools.lru_cache(maxsize=None)
def chi2_lower(q, n):
    """chi-square(n)'s q quantile, EXACT by bisection on P(n/2, x/2) (rev 9: the twin term's
    degrees of freedom can be small, where rev 8's Wilson-Hilferty form is poor)."""
    lo, hi = 0.0, n + 20 * math.sqrt(2 * n) + 20
    for _ in range(100):
        mid = (lo + hi) / 2
        if _gamma_p(n / 2, mid / 2) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


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


def launch_sigmas(rows, raw=False):
    """Per (regime, layer), the launch sigma (log scale) of its timed arm cells: median SD /
    MED_SD5; a thin pool borrows the night's. raw: {pool: (own sigma, n arms)} as well."""
    pools, allsd = {}, []
    for k, r in rows.items():
        if r["status"] == "ok" and len(r["launches"]) >= 2:
            lg = [math.log(v) for v in r["launches"]]
            sd = statistics.stdev(lg)
            pools.setdefault((k[3], k[4]), []).append(sd)
            allsd.append(sd)
    glob = statistics.median(allsd) / MED_SD5 if allsd else 0.0
    sigs = {p: (statistics.median(v) / MED_SD5 if len(v) >= MIN_POOL else glob) for p, v in pools.items()}
    if raw:
        return sigs, glob, {p: (statistics.median(v) / MED_SD5, len(v)) for p, v in pools.items()}, len(allsd)
    return sigs, glob


def twin_sigmas(pool_logs):
    """THE TWIN CONTRASTS (rev 9, RULED r37 H1 + H2): per (regime, layer), the noise of one
    ratio of two arms' medians, read from the arms the night ALREADY times that are one binary:
    I's pool in each C1-C2 cell read (I and every head whose artifact hash-equals I's there).
    pool_logs: {(regime, layer): [[ln median of each pool arm], ...]}, one list per cell. Within
    a pool every arm has one true time, so its spread is launch noise PLUS between-run noise
    (an arm-level offset held over all 5 launches, which the launch sigma cannot see). sigma_c
    = sqrt(2 x SS / df), SS the pools' summed squared deviations from their own means and df the
    summed (arms - 1): the RMS of the pools' log-median contrasts, the log SD of a head against
    I. Returns {(regime, layer): (sigma_c, df)}; a (regime, layer) with no pool of two is absent."""
    out = {}
    for p, pools in pool_logs.items():
        ss, df = 0.0, 0
        for xs in pools:
            if len(xs) >= 2:
                m = sum(xs) / len(xs)
                ss += sum((x - m) ** 2 for x in xs)
                df += len(xs) - 1
        if df:
            out[p] = (math.sqrt(2 * ss / df), df)
    return out


def pool_floors(f_aa, raw, glob, n_all, n_comp, alpha=ALPHA, twins=None):
    """THE PER-(REGIME, LAYER) FLOOR (rev 8, r36 G2; rev 9, r37 H1): f(regime, layer) = max(
    the A/A floor `f_aa`, the LAUNCH term exp(z(alpha / N) x sqrt(2) x SDMED5 x sigma_up) - 1,
    the TWIN term exp(z(alpha / N) x sigma_c_up) - 1). sigma_up: the pool's launch sigma raised to
    its SIGMA_CONF upper bound (MEDSD_REL / sqrt(n)); a thin pool takes the LARGER of its own and
    the night's sigma (r37 H10 (1): the bimodal test borrows the night's; the floor never goes
    below its own). sigma_c_up: `twins`' sigma_c raised to its SIGMA_CONF upper bound
    sqrt(df / chi2(1 - SIGMA_CONF; df)). The launch term sees one arm's launch scatter only; the
    twin term sees an arm-level (between-run) offset in its own (regime, layer), which neither
    the launch term nor the night-wide A/A term can (r37 H1)."""
    z = z_upper(alpha / max(1, n_comp))
    zc = statistics.NormalDist().inv_cdf(SIGMA_CONF)
    twins = twins or {}
    out = {}
    for p, (s, n) in raw.items():
        up = s * (1 + zc * MEDSD_REL / math.sqrt(n))
        if n < MIN_POOL:
            up = max(up, glob * (1 + zc * MEDSD_REL / math.sqrt(max(1, n_all))))
        fl = max(f_aa, math.exp(z * math.sqrt(2) * SDMED5 * up) - 1) if POOL_TERM else f_aa
        if TWIN_TERM and p in twins:
            fl = max(fl, twin_term(twins[p], z))
        out[p] = fl
    return out


def twin_term(tw, z):
    """One twin term: exp(z x sigma_c,up) - 1, sigma_c raised to its SIGMA_CONF upper bound
    sqrt(df / chi2(1 - SIGMA_CONF; df)) (exact; df can be small)."""
    sc, df = tw
    return math.exp(z * sc * math.sqrt(df / chi2_lower(1 - SIGMA_CONF, df))) - 1


def layout_sigma(d):
    """THE LAYOUT TWIN CONTRAST (rev 11, RULED r39 K1): d {cell id 'pat/regime/layer': ln(t(I.lt) /
    t(I))}. Returns (sigma_x, df): sigma_x the RMS of the contrasts (two single-arm medians of two
    exes: the kind of a head against I), df the number of distinct EXE PAIRS (pattern, layer) among
    them (one exe serves every regime, so the regimes of one pair share its offset: df counts
    pairs, never cells). (0.0, 0) when there is none."""
    if not d:
        return 0.0, 0
    return math.sqrt(sum(x * x for x in d.values()) / len(d)), len({(c.split("/")[0], c.split("/")[2]) for c in d})


LAYOUT_TERM = True  # selftest's K1 control turns the layout twin term off (rev 10's floor)
LAYOUT_TWIN_ARM = True  # ... and I.lt out of I's pool (rev 10's arm set); every EARLIER control turns both off too:
                        # rev 11's twin also sees their defects (a control that left it on was blind, as rev 10's
                        # controls had to turn the confirm off)
LAYOUT_TWINS = True  # ... and the synthetic layout twins (rev 10: aa-twin was aa's exe, the confirm re-ran step 1's exes)
READING_B = True    # selftest's K4 control turns reading B off (rev 10: an unreproduced win read as a tie in W/E/dominance)
POOL_I = True       # selftest's control turns I's pool off (rev 7's reading) to show the G3 drill sees it
POOL_TERM = True    # selftest's control turns the pool term off (rev 7's floor) to show the drill sees it
TWIN_TERM = True    # selftest's controls turn the twin term off (rev 8's floor) to show the H1 drill sees it
AGREE_GATE = True   # ... and the agreement gate off (rev 8's rule) to show the H2 drill sees it
PAT_TWIN = True     # selftest's controls turn the PER-PATTERN twin term off (rev 9's floor) to show J1's drill sees it
CONFIRM = True      # ... and the confirming re-run off (rev 9's rule) to show the arm-level drill sees it (r38 R2)


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
    # absent: None, which the rule REFUSES (rev 9, r37 H3); never `{}`, which read as I-alone pools
    same = json.load(open(sp)) if os.path.exists(sp) else None
    return {"files": files, "same": same}


def pool_record_refusal(same):
    """I's pool record (`same_as_I.json`) must name EVERY C1-C2 pattern x layer, each list holding
    the grid top (H(64) renders exactly I at every C1-C2 length: rev 8's "at least I and H(64)").
    A missing file, pattern or layer silently shrank every pool to I alone (r37 H3). Returns the
    refusal text, or None."""
    if same is None:
        return "same_as_I.json is missing (I's pool record; `cards.py run` writes it)"
    if not isinstance(same, dict):
        return "same_as_I.json is not a pattern map"
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            v = same.get(pat)
            if isinstance(v, list):
                return ("same_as_I.json holds rev 7's format (SIMD-off only, one list a pattern): re-run "
                        "`cards.py dry`/`run` to record identity per layer (rev 8)")
            if not isinstance(v, dict):
                return "same_as_I.json lacks C1-C2 pattern %s" % pat
            for ly in LAYERS:
                if ly not in v:
                    return "same_as_I.json lacks pattern %s at layer %s" % (pat, ly)
                if GRID_TOP not in v[ly]:
                    return ("same_as_I.json: pattern %s layer %s lists %s, without the grid top %d (H(%d) renders "
                            "exactly I at every C1-C2 length)" % (pat, ly, v[ly], GRID_TOP, GRID_TOP))
    return None


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
    res = {"code": 0, "lines": lines, "hstar": None, "label": None, "rec": None, "owed_rerun": owed,
           "owed_confirm": {}, "wins": 0, "confirmed": 0}
    if "results.tsv" not in night["files"]:
        lines.append("rule: no results.tsv: step 1 (`run`) has not run")
        res["code"] = 3
        return res
    rows, att = merge(*night["files"]["results.tsv"])
    same = night["same"]
    why_pool = pool_record_refusal(same)
    if why_pool:
        lines.append("rule: REFUSED: %s; I's pools cannot be read: the night is DEFECTIVE (rev 9, r37 H3)" % why_pool)
        res["code"] = 2
        return res
    sigs, glob, sig_raw, n_all = launch_sigmas(rows, raw=True)
    cellk = lambda k: (k[0], k[1], k[3], k[4])      # noqa: E731

    # ---- R0: G2's list, plus every head whose cell gate failed in ANY reading (rev 7, F5; rev 11,
    #      r39 K2: the confirm's reading too, `results_confirm.tsv`, and C3's) -----------------
    # One scan, every results file the night holds, read alike: I or an A/A arm (or a layout twin
    # of either: the reference itself) failing makes the night DEFECTIVE; a head (or its twin)
    # failing is DEFECTIVE; the engine route's failure is filed (R4 not computed there).
    defective = set(g2_defective)
    c3files = {n: merge(*v) for n, v in night["files"].items() if n.startswith("results_c3_h")}
    allfiles = [("results.tsv", rows)] + [(n, merge(*v)[0]) for n, v in sorted(night["files"].items())
                                          if n != "results.tsv"]
    for n, rr in allfiles:
        where = "" if n == "results.tsv" else " (%s)" % n
        for k, r in sorted(rr.items()):
            if r["status"] != "gatefail":
                continue
            if arm_base(k[2]) in ("I", "aa"):
                lines.append("R0: %s failed its gate in %s%s: the reference is wrong; the night is DEFECTIVE "
                             "(filed)" % (k[2], "/".join(k), where))
                res["code"] = 2
                return res
            h = arm_head(k[2])
            if h is not None:
                defective.add(h)
                lines.append("R0: H(%d) failed its gate in %s%s: DEFECTIVE (filed)" % (h, "/".join(k), where))
            else:
                lines.append("R0: the engine route failed its gate in %s%s (filed; R4 not computed there)"
                             % ("/".join(k), where))
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
    pool_n, pool_meds, cell_key, pool_arms, lay_d, same_meds = {}, {}, {}, {}, {}, {}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            for rg in REGIMES:
                for ly in ("off", "on"):
                    cid = "%s/%s/%s" % (pat, rg, ly)
                    ident = same_heads(same, pat, ly)
                    for h in heads:
                        sa[h][cid] = h in ident
                    if rg in APPROX:
                        vc.append(cid + " (void by method)")
                        for h in heads:
                            sa[h][cid + " (void by method)"] = sa[h][cid]
                        continue
                    # I's POOL (rulings R1, rev 8 r36 G3): I and every arm whose built artifact
                    # hash-equals I's in this cell (measured, `same_as_I.json`), R0 or not: one
                    # binary, so one reading, the median over all their launches
                    # rev 11 (r39 K1): I's LAYOUT TWIN `I.lt` is one more arm of the pool (another exe of I)
                    pool = ["I"] + ((["I.lt"] if LAYOUT_TWIN_ARM else []) + ["h%d" % h for h in GRID if h in ident]
                                    if POOL_I else [])
                    if rows.get((card, pat, "I", rg, ly)) is None:
                        lines.append("rule: cell %s REFUSED: I's own arm is missing from its pool (no row); the "
                                     "night is DEFECTIVE (filed)" % cid)
                        res["code"] = 2
                        return res
                    arms = pool + ["h%d" % h for h in heads if not sa[h][cid]]
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
                    tI[cid] = statistics.median([v for a in pool for v in rows[(card, pat, a, rg, ly)]["launches"]])
                    pool_n[cid] = len(pool)
                    pool_arms[cid] = pool
                    pool_meds[cid] = [rows[(card, pat, a, rg, ly)]["med"] for a in pool]
                    if "I.lt" in pool:
                        lay_d[cid] = math.log(rows[(card, pat, "I.lt", rg, ly)]["med"] / rows[(card, pat, "I", rg, ly)]["med"])
                        same_meds[cid] = [m for a, m in zip(pool, pool_meds[cid]) if a != "I.lt"]
                    cell_key[cid] = (card, pat, rg, ly)
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
    if not aa_logs:
        lines.append("rule: no A/A cell is read: the night is VOID")
        res["code"] = 2
        return res

    def floors_over(cs):
        """The floors over the cells `cs` (N and the twin contrasts read from them): the (regime,
        layer) floors, and the PER-PATTERN twin terms (rev 10, RULED r38 J1)."""
        n_c = sum(1 for h in heads for c in cs if not sa[h][c])
        f_, fd_ = count_floor(aa_logs, n_c, alpha)
        logs, plogs = {}, {}
        for c in cs:
            lm = [math.log(m) for m in pool_meds[c]]
            logs.setdefault(tuple(c.split("/")[1:3]), []).append(lm)
            plogs.setdefault(c.split("/")[0], []).append(lm)
        tw = twin_sigmas(logs)
        ptw = twin_sigmas(plogs)
        z = z_upper(alpha / max(1, n_c))
        pterm = {p: twin_term(v, z) for p, v in ptw.items()}
        lx = layout_sigma({c: lay_d[c] for c in cs if c in lay_d})
        lay_term = twin_term(lx, z) if LAYOUT_TERM and lx[1] else 0.0
        return (f_, fd_, tw, pool_floors(f_, sig_raw, glob, n_all, n_c, alpha, twins=tw), ptw, pterm,
                (lx, lay_term))
    f, fd, tw, floors, ptw, pterm, lay = floors_over(ccells)

    def cell_floor(c):
        """THE CELL'S FLOOR (rev 10, RULED r38 J1): max(its (regime, layer) floor, its PATTERN's twin
        term). The twin term is computed at the finest level the night times twins: per pattern,
        over that pattern's own hash-equal pools in the cells read (its 12 (regime, layer) cells:
        df 12 at a 2-arm pool, 36 at hex24's 4), because between-run noise acts per binary and a
        (regime, layer) term pooled over 9 patterns dilutes one pattern's noise (r38 J1: 0.40-0.69).
        A pattern with no estimate (df 0) has no term: its cells are VOID (the gate), never pooled up."""
        p, rg, ly = c.split("/")
        fl = max(floors.get((rg, ly), f), lay[1])       # rev 11 (r39 K1): the layout twin term
        return max(fl, pterm[p]) if PAT_TWIN and p in pterm else fl
    # THE AGREEMENT GATE (rev 9, RULED r37 H2): I's pool is one binary, so its arms' medians differ
    # only by noise. Where they disagree beyond the cell's own floor, one of them moved (a whole-arm
    # slowdown moves a 2-arm pool's median by ~half its size and no gap test sees it): the cell is
    # VOID, re-run once, never a pick. A pool of two cannot say which arm moved; it voids too.
    # Rev 10 (r38 J1): the cell's own floor includes its pattern's twin term, and a cell whose
    # pattern has no twin estimate is void here too (never pooled up to a coarser level).
    gated = []
    if AGREE_GATE:
        for c in list(ccells):
            ms = pool_meds[c]
            fl = cell_floor(c)
            noest = PAT_TWIN and c.split("/")[0] not in pterm
            if noest or (len(ms) >= 2 and max(ms) / min(ms) > 1 + fl):
                gated.append("%s (no twin estimate for its pattern)" % c if noest else
                             "%s (pool of %d: %.4f > 1 + %.4f)" % (c, len(ms), max(ms) / min(ms), fl))
                ccells.remove(c)
                del tI[c], pool_n[c]
                for h in heads:
                    t[h].pop(c, None)
                if att.get(cell_key[c], 1) < 2:
                    owed.setdefault("results.tsv", set()).add(cell_key[c])
                else:
                    vc.append(c)
    if gated:
        lines.append("rule: agreement gate: %d cell(s) whose hash-equal arms disagree beyond f: %s"
                     % (len(gated), "; ".join(gated[:6]) + ("; ..." if len(gated) > 6 else "")))
    res["gated"] = len(gated)
    if owed:
        lines.append("rule: %d cell(s) of results.tsv VOID ONCE by the agreement gate: R1 waits for the re-run"
                     % len(owed["results.tsv"]))
        lines.append("rule: NEXT cards.py rerun RUNDIR")
        res["code"] = 3
        return res
    if gated:      # void twice: the floors are re-read over the cells still read
        f, fd, tw, floors, ptw, pterm, lay = floors_over(ccells)
    lines.append("rule: f(A/A) = %.4f (count-sized: A/A sigma %.4f, upper %.4f over %d cells; N = %d comparisons, "
                 "z = %.2f; the A/A max ratio alone %.4f)" % (f, fd["sigma"], fd["sigma_up"], len(aa_logs),
                                                               fd["N"], fd["z"], fd["f_aa"]))
    pf = lambda rg, ly: floors.get((rg, ly), f)      # noqa: E731
    lines.append("rule: twin contrasts per (regime, layer) (I's pools, rev 9, r37 H1): %s"
                 % ", ".join("%s/%s sigma %.4f df %d" % (rg, ly, tw[(rg, ly)][0], tw[(rg, ly)][1])
                             for rg in REGIMES if rg not in APPROX for ly in ("off", "on") if (rg, ly) in tw))
    lines.append("rule: f per (regime, layer) = max(f(A/A), the launch-sigma term, the twin term) (rev 9): %s"
                 % ", ".join("%s/%s %.4f" % (rg, ly, pf(rg, ly)) for rg in REGIMES if rg not in APPROX
                             for ly in ("off", "on")))
    lines.append("rule: twin term per pattern (its own hash-equal pools, rev 10, r38 J1)%s: %s"
                 % ("" if PAT_TWIN else " [OFF: control]",
                    ", ".join("%s sigma %.4f df %d term %.4f" % (p, ptw[p][0], ptw[p][1], pterm[p])
                              for p in sorted(ptw))))
    # THE LAYOUT TWIN TERM (rev 11, RULED r39 K1): the night's MEASURED between-exe noise. Every
    # other estimator is a contrast inside one exe; `I.lt` is I linked at another address, so
    # ln(t(I.lt) / t(I)) per cell read is a contrast of the SAME KIND as a head against I (two
    # exes). sigma_x = their RMS; its df = the number of distinct exe PAIRS read (one per (pattern,
    # layer): an exe serves every regime, so its offset is shared by that pair's regimes), raised
    # to its SIGMA_CONF bound like every twin term; the term floors every cell. Its SIZE (the
    # between-exe offset's own sigma, the twin contrast's excess over the same-exe pools' contrast)
    # is printed: the measurement the 11-19 night makes.
    (lsig, ldf), lterm = lay
    same_all = twin_sigmas({"night": [[math.log(m) for m in same_meds[c]] for c in ccells if c in same_meds]})
    ssig = same_all.get("night", (0.0, 0))[0]
    lines.append("rule: layout twin term (I against its layout twin I.lt, rev 11, r39 K1)%s: contrast sigma %.4f over %d "
                 "cells, df %d (exe pairs), term %.4f; the same-exe pools' contrast sigma %.4f; BETWEEN-EXE offset "
                 "sigma per exe (MEASURED) %.4f" % ("" if LAYOUT_TERM else " [OFF: control]", lsig,
                                                    sum(1 for c in ccells if c in lay_d), ldf, lterm, ssig,
                                                    math.sqrt(max(0.0, lsig * lsig - ssig * ssig) / 2)))
    res["layout"] = {"sigma": lsig, "df": ldf, "term": lterm, "same_sigma": ssig}
    fcell = {c: cell_floor(c) for c in ccells}
    # CONFIRM BY RE-RUN (rev 10, RULED r38 R2; rev 11, RULED r39 K1, K3, K4, K6). Replication: a
    # head's win beyond f in a cell COUNTS only if the cell's confirming re-run wins again beyond the
    # cell's floor. The confirm times FRESH LAYOUT TWINS (layout 2): `I.cf` (I) and `h<N>.cf` for
    # each head owed in that cell, never step 1's exes, so an offset an exe carries cannot replicate
    # (r39 K1). The confirm's reading of a head's win is I.cf's median against h<N>.cf's: a missing,
    # void or bimodal I.cf or h<N>.cf confirms nothing for that head; another head's arm says
    # nothing about this head's win (r39 K3: the per-arm reading, the text now says so). The confirm
    # feeds ONE predicate, step (4)'s "beat I beyond f" (READING B, r39 K4); W, E and dominance read
    # the first reading, never the confirm's. One confirm per (cell, head) win: a head whose
    # `.cf` row exists is never owed again, so the confirms end.
    wins = sorted((h, c) for h in heads for c in ccells if not sa[h][c] and tI[c] / t[h][c] > 1 + fcell[c])
    conf = merge(*night["files"]["results_confirm.tsv"])[0] if "results_confirm.tsv" in night["files"] else {}
    need = {}
    for h, c in wins if CONFIRM else []:
        card, pat, rg, ly = cell_key[c]
        if (card, pat, "h%d.cf" % h, rg, ly) not in conf:
            need.setdefault(cell_key[c], []).append(h)
    res["wins"] = len(wins)
    if need:
        res["owed_confirm"] = need
        ks = sorted(need)
        lines.append("rule: %d cell(s) hold a head's win beyond f (%d wins, %d owed): R1 waits for their confirming re-run "
                     "on fresh layout twins (%s%s)" % (len(need), len(wins), sum(len(v) for v in need.values()),
                                                       ", ".join("/".join(k) + " H(%s)" % ",".join(map(str, need[k]))
                                                                 for k in ks[:6]), ", ..." if len(ks) > 6 else ""))
        lines.append("rule: NEXT cards.py rerun RUNDIR")
        res["code"] = 3
        return res

    def confirmed(h, c):
        card, pat, rg, ly = cell_key[c]
        arms = ["I.cf", "h%d.cf" % h]
        rs = [conf.get((card, pat, a, rg, ly)) for a in arms]
        if any(r is None or is_void((card, pat, a, rg, ly), r) for a, r in zip(arms, rs)):
            return False
        return rs[0]["med"] / rs[1]["med"] > 1 + fcell[c]
    okwins = {(h, c) for h, c in wins if confirmed(h, c)} if CONFIRM else None
    res["confirmed"] = nok = len(okwins) if okwins is not None else 0
    if CONFIRM and not READING_B:       # the K4 control: rev 10's reading (an unreproduced win reads as a TIE)
        for h, c in wins:
            if (h, c) not in okwins:
                t[h][c] = tI[c]
        okwins = None
    if wins and CONFIRM:
        lines.append("rule: confirm by re-run on fresh layout twins (rev 11, r39 K1/K4): %d of %d wins beyond f reproduced; "
                     "only those count as step (4)'s win; W, E and dominance read the first reading"
                     % (nok, len(wins)))
    lines.append("rule: I's pool per cell read (arms whose artifact is I's, measured): %s"
                 % ", ".join("%s %d" % kv for kv in sorted(pool_n.items())))
    lines.append("rule: R0 defective heads: %s; cells read %d, void %d" % (sorted(defective) or "none",
                                                                         len(ccells), len(vc)))
    measured = "MEASURED (kit-grid@7 cards C1 %s, C2 %s; %d cells read)" % (CARD_ROWS["C1"], CARD_ROWS["C2"],
                                                                           len(ccells))
    hs, label, rec, det = r1(heads, ccells, vc, t, tI, sa, fcell, measured=measured, wins_ok=okwins)
    res.update(hstar=hs, label=label, rec=rec, f=f, floors=floors, det=det)
    if hs is None:
        lines.append("rule: h* none: %s" % label)
        res["code"] = 2
        return res
    lines.append("rule: W = %s" % {h: round(w, 4) for h, w in det["W"].items()})
    lines.append("rule: E = %s; dominated-by counts %s; kept %s" % (det["E"], det["dominated_by"], det["kept"]))
    # R3: per class, the head its own cells pick, against the grid value nearest E[D]; DERIVED
    # when every class with a cell read tracks (rev 7, F10). Only a class whose text MOVES for
    # some surviving head is read (rev 8, r36 G6): a literal class (lit40, abc60) renders I at
    # every head, so its own pick is the top on any data and could never track
    track, any_cls = True, False
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            mine = [c for c in ccells if c.startswith(pat + "/")]
            if not mine:
                continue
            if all(all(h in same_heads(same, pat, ly) for ly in LAYERS) for h in heads):
                lines.append("R3 class %s: its text is I's at every surviving head (never a mover): not read" % pat)
                continue
            any_cls = True
            hcls = r1(heads, mine, [], t, tI, sa, {c: fcell[c] for c in mine}, wins_ok=okwins)[0]
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
        if t[hs][c] / tI[c] > 1 + fcell[c]:
            lines.append("R2 dial evidence: %s: H(%d) %.4f vs I %.4f" % (c, hs, t[hs][c], tI[c]))
    # R4: C1's near-miss column, H(h*) against C5 (the engine route)
    for pat in CARD_PATS["C1"]:
        for ly in ("off", "on"):
            cid = "%s/near-miss/%s" % (pat, ly)
            hv = t[hs].get(cid)
            ev = rows.get(("C5", pat, "engine", "near-miss", "off"))
            if hv is not None and ev and ev["status"] == "ok" and hv / ev["med"] > 1 + max(
                    fcell[cid], pf("near-miss", "off")):
                lines.append("R4 near-miss trigger (r45_reply §4): %s/%s H(%d) %.4f vs engine %.4f"
                             % (pat, ly, hs, hv, ev["med"]))
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
                fr = pf(rg, ly)
                if got["I"]["med"] < v / (1 + fr):
                    lines.append("R2 dial evidence: C3 %s: H(%d) %.4f vs I %.4f" % (cid, hs, v, got["I"]["med"]))
                for other in ("I", "h0"):
                    if other != harm and v / got[other]["med"] > 1 + fr:
                        lines.append("R5 long-span loss: C3 %s H(%d) %.4f vs %s %.4f" % (cid, hs, v, other,
                                                                                        got[other]["med"]))
    lines.append("rule: NEXT the build compiles h* = %d in; then cards.py identity %d (FROZEN=<this night's "
                 "build>)" % (hs, hs))
    return res


def cmd_rule(args):
    """R0-R5 over a night's RUNDIR. --g2 FILE: R0's input, one defective head per line (a head
    whose answers G2 failed)."""
    rundir = args[0]
    v = owed_now(rundir, args[args.index("--g2") + 1] if "--g2" in args else None)
    print("rule: R0's G2 list %s (%s)" % (sorted(v["g2"]) or "none", v["g2_src"]))
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


# ---- the drills (r45_reply rev 11 §3 "Drills"), each with the result the design states ------
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
     32, "h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of {24, 32}"),
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
                                                 8: [0.97], 16: [0.975]}}, 16, "MEASURED"),
    ("(x) h = 4 at 0.95, the new minimum", {"cells": [("c", 60)],
                                            "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [0.95],
                                                       8: [0.97], 16: [0.975]}}, 8, "MEASURED"),
    ("(x) h = 4 at 0.985, not the minimum", {"cells": [("c", 60)],
                                             "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [0.985],
                                                        8: [0.97], 16: [0.975]}}, 16, "MEASURED"),
    ("(xi) two cells", {"heads": [0, 1, 2, 4, 8, 16, 24, 32, 64], "cells": [("c1", 60), ("c2", 60)],
                        "ratios": {0: [LOSE] * 2, 1: [LOSE] * 2, 2: [LOSE] * 2, 4: [LOSE] * 2,
                                   8: [0.97, 0.97], 16: [0.975, 0.975]}}, 16, "MEASURED"),
    ("(xi) h = 12 joins E and dominates 16", {"heads": [0, 1, 2, 4, 8, 12, 16, 24, 32, 64],
                                              "cells": [("c1", 60), ("c2", 60)],
                                              "ratios": {0: [LOSE] * 2, 1: [LOSE] * 2, 2: [LOSE] * 2,
                                                         4: [LOSE] * 2, 8: [0.97, 0.97],
                                                         12: [0.985, 0.95], 16: [0.975, 0.975]}},
     12, "MEASURED"),
    ("(G4) H(8) alone wins; 16, 24 within f of both", {"cells": [("c", 60)],
                                                        "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [LOSE],
                                                                   8: [0.97], 16: [0.99], 24: [0.99]}},
     8, "MEASURED"),
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
def synth_exe(key, same):
    """The EXE an arm cell runs (rev 11, r39 K1), the unit a between-exe offset attaches to: I's
    base exe serves I and every head whose text is I's (one text, one cached exe); each other head
    its own; A/A's pair; each layout twin (`I.lt`, `aa-twin`, the confirm's `.cf`) another exe of
    its base text. One exe serves every regime of its (pattern, layer). LAYOUT_TWINS off (the K1
    control, rev 10's arm set): no exe is ever twinned: `aa-twin` and `I.lt` run their base's exe
    (rev 10's A/A pair and a hash-equal pool member) and the confirm re-runs step 1's exes."""
    card, pat, arm, _rg, ly = key
    lay = arm_lay(arm) if LAYOUT_TWINS else 0
    if card == "AA":
        return ("aa", ly, lay)
    h = arm_head(arm)
    if arm_base(arm) == "I" or (h is not None and h in same[pat][ly]):
        return ("I", pat, ly, lay)
    return (arm_base(arm), pat, ly, lay)


def synth_rows(rng, sigma, wins=None, noise="normal", bimodal_cells=(), approx_read=True, regimes=None,
               rscale=None, aascale=1.0, splits=None, cellwins=None, armoff=None, timefx=None,
               order="interleaved", pos0=0, exeoff=None, only=None):
    """A synthetic step-1 results set: C1-C2 every arm (I's layout twin `I.lt` too, rev 11), A/A
    every regime and layer; each arm cell's
    LAUNCHES launches are T x exp(noise) with T the cell's true time (one per pattern/regime/
    layer, every arm equal: pure noise) times the arm's `wins` factor where its text is not I's.
    Regimes are all READ (`approx_read`: the bench's methods present), so the rule's floor and
    dominance see the real cell count (108 C1-C2 cells x 9 heads). HETEROGENEOUS noise (rev 8,
    r36 G2): `rscale` {regime: x} multiplies a regime's launch sigma, `aascale` the A/A arms'.
    `splits` {(card, pat, arm, regime, layer): (n, factor)}: n of the arm's launches x factor (a
    median-moving split when n >= 3, r36 G3). `cellwins` {(card, pat, arm, regime, layer): factor}:
    one arm's true time in one cell (r36 G4; a layout twin of the arm shares it: one text).
    `armoff` (tau, regimes, spare_aa): BETWEEN-RUN
    noise (rev 9, r37 H1): every arm of those regimes (None: every regime) carries its own offset
    exp(N(0, tau)), held over all its launches; the A/A arms are spared when spare_aa. A re-run
    draws fresh offsets (a new run). Its draws come after the arm's launches, so a night without
    `armoff` draws exactly rev 8's stream. `armoff` (tau, sel): the offset on every arm cell
    `sel(key)` names (rev 10's CLASS DRILL, r38: noise confined to one night, regime, layer,
    pattern or arm; a layout twin is selected as its base arm). TIME (rev 10, r38 J2): `timefx(pos)`
    multiplies every launch by a function
    of its position in the night's launch order (`launch_order` over step 1's cells, the order
    `time_cells` times; `order` "arm-major" is rev 9's, the control), `pos0` the first position
    (a re-run runs after the night). It draws nothing, so the streams are unchanged.
    BETWEEN-EXE noise (rev 11, r39 K1): `exeoff` (tau, store): every distinct exe (`synth_exe`)
    carries ONE offset exp(N(0, tau)) a night, drawn into `store` (the night's dict, its own RNG
    under "_rng") on first use and held over the first reading, every re-run and the confirm; a
    fresh layout twin is a new exe, a new offset. `only` {(card, pat, regime, layer): [arms]}:
    generate those arm cells only (the confirm's `I.cf` / `h<N>.cf`), else step 1's."""
    wins = wins or {}
    rscale = rscale or {}
    splits = splits or {}
    cellwins = cellwins or {}
    rows = {}
    slots = launch_slots(order) if timefx else None
    same = {}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            k = len(PATTERNS[pat][1])
            lit = pat in ("lit40", "abc60")
            same[pat] = {ly: [h for h in GRID if lit or h >= k] for ly in LAYERS}

    def eps():
        if noise == "t5":
            return rng.gauss(0, 1) / math.sqrt(rng.gammavariate(2.5, 2.0) / 5) / math.sqrt(5 / 3)
        return rng.gauss(0, 1)

    def put(key, T):
        base = (key[0], key[1], arm_base(key[2])) + key[3:5]
        sg = sigma * rscale.get(key[3], 1.0) * (aascale if key[0] == "AA" else 1.0)
        T *= cellwins.get(base, 1.0)
        if key[:5] in bimodal_cells or (key[1], key[3], key[4]) in bimodal_cells:
            ls = [T * math.exp(sg * eps()) * (1.08 if i < 2 else 1.0) for i in range(LAUNCHES)]
        elif key[:5] in splits:
            n, fac = splits[key[:5]]
            ls = [T * math.exp(sg * eps()) * (fac if i < n else 1.0) for i in range(LAUNCHES)]
        else:
            ls = [T * math.exp(sg * eps()) for _ in range(LAUNCHES)]
        if armoff and (armoff[1](base) if callable(armoff[1]) else
                       (armoff[1] is None or key[3] in armoff[1]) and not (armoff[2] and key[0] == "AA")):
            o = math.exp(rng.gauss(0, armoff[0]))
            ls = [v * o for v in ls]
        if exeoff:
            tau, store = exeoff
            ex = synth_exe(key, same)
            if ex not in store:
                store[ex] = math.exp(store["_rng"].gauss(0, tau))
            ls = [v * store[ex] for v in ls]
        if timefx:
            ls = [v * timefx(pos0 + q) for v, q in zip(ls, slots.get(key[:5]) or slots[base])]
        rows[key] = {"status": "ok", "med": statistics.median(ls), "launches": ls,
                     "method": "kit" if approx_read else method_of(key[3]), "note": ""}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            for rg in (regimes or REGIMES):
                for ly in ("off", "on"):
                    T = rng.uniform(0.2, 2.0)
                    arms = (["I", "I.lt"] + ["h%d" % h for h in GRID] if only is None else
                            only.get((card, pat, rg, ly), []))
                    for a in arms:
                        h = arm_head(a)
                        put((card, pat, a, rg, ly), T * (1.0 if h is None or h in same[pat]["off"] else wins.get(h, 1.0)))
    for rg in (regimes or REGIMES) if only is None else ():
        for ly in ("off", "on"):
            T = rng.uniform(0.2, 2.0)
            put(("AA", "lit16", "aa", rg, ly), T)
            put(("AA", "lit16", "aa-twin", rg, ly), T)
    return rows, same


@functools.lru_cache(maxsize=None)
def launch_slots(order="interleaved"):
    """{arm cell: [the night position of each of its launches]} over step 1's cells (C5's launches
    take their places in the order too), and the night's launch count under key None."""
    lo = launch_order(cells(cards=STEP1), interleave=order == "interleaved")
    out = {}
    for q, (c, _i) in enumerate(lo):
        out.setdefault(c, []).append(q)
    out[None] = len(lo)
    return out


def synth_night(rng, sigma, **kw):
    """One whole synthetic night through `analyse`: step 1, then the re-run of any cell void once
    (fresh launches), so the drill exercises the merge too."""
    global APPROX
    keep = APPROX
    APPROX = {}                   # every regime read: the bench's methods present
    if kw.get("exeoff") is not None and not isinstance(kw["exeoff"], tuple):    # tau: one store a night
        kw = dict(kw, exeoff=(kw["exeoff"], {"_rng": random.Random(rng.random())}))
    try:
        rows, same = synth_rows(rng, sigma, **kw)
        night = {"files": {"results.tsv": (rows, {})}, "same": same}
        v = analyse(night, set())
        voided_first = sum(len(s) for s in v["owed_rerun"].values())
        # the re-run rounds: a transient does not recur; the re-run runs AFTER the night (a time
        # effect holds its end value there). A cell the gate voids only once the cells first owed
        # are read owes a further round (r38 J4 (1)); every cell is re-run at most once
        kw2 = dict(kw, bimodal_cells=(), splits={},
                   pos0=launch_slots(kw.get("order", "interleaved"))[None] if kw.get("timefx") else 0)
        redo, rounds = {}, 0
        while v["owed_rerun"].get("results.tsv") and rounds < 3:
            rounds += 1
            fresh, _s = synth_rows(rng, sigma, **kw2)
            redo.update({k: r for k, r in fresh.items() if (k[0], k[1], k[3], k[4]) in v["owed_rerun"]["results.tsv"]})
            night["files"]["results.tsv"] = (rows, redo)
            v = analyse(night, set())
        v["voided_first"] = voided_first
        v["rerun_rounds"] = rounds
        # the confirming re-run (rev 10, r38 R2; rev 11, r39 K1): fresh launches after the night, on the
        # cells' FRESH LAYOUT TWINS (I.cf and each owed head's .cf: new exes, new offsets); a confirm
        # owed only after an earlier confirm (R0 from it moved N) is one more round, each (cell, head) once
        conf, ncells, crounds = {}, 0, 0
        while v["owed_confirm"] and crounds < 3:
            crounds += 1
            ncells += len(v["owed_confirm"])
            fresh, _s = synth_rows(rng, sigma, only={k: ["I.cf"] + ["h%d.cf" % h for h in hs]
                                                     for k, hs in v["owed_confirm"].items()}, **kw2)
            conf.update(fresh)
            night["files"]["results_confirm.tsv"] = (conf, {})
            v = analyse(night, set())
        v["voided_first"], v["rerun_rounds"], v["confirm_cells"] = voided_first, rounds, ncells
        return v
    finally:
        APPROX = keep


NOISE_TRIALS = 300


def noise_drill(trials=NOISE_TRIALS, sigma=0.01, noise="normal", seed=1, **kw):
    """P(h* != 64), the nights with a first void, the median f(A/A); NOISE_LAST keeps the median
    floor of (hit-dense, off), the cell floor the H2 drill sizes its shifts by."""
    rng = random.Random(seed)
    off, voids, fs, fc, cc, lx = 0, 0, [], [], [], []
    for _ in range(trials):
        v = synth_night(rng, sigma, noise=noise, **kw)
        off += v["hstar"] != GRID_TOP
        voids += v["voided_first"] > 0
        fs.append(v.get("f", 0))
        cc.append(v.get("confirm_cells", 0))
        if v.get("layout"):     # the night's MEASURED between-exe offset sigma (rev 11, r39 K1)
            lv = v["layout"]
            lx.append(math.sqrt(max(0.0, lv["sigma"] ** 2 - lv["same_sigma"] ** 2) / 2))
        if v.get("floors"):
            fc.append(v["floors"].get(("hit-dense", "off"), 0))
    NOISE_LAST["fcell"] = statistics.median(fc) if fc else 0.0
    NOISE_LAST["confirm"] = cc
    NOISE_LAST["layout"] = statistics.median(lx) if lx else None
    return off / trials, voids, statistics.median(fs)


NOISE_LAST = {}


# ---- THE CLASS DRILL (rev 10, RULED r38): noise at EVERY level of the night's structure -------
# Three rounds running (r36 G2, r37 H1, r38 J1/J2) the rule's defect was a noise shape one level
# below the drills: an estimator pooled coarser than the noise it must read, or a noise that
# followed the launch ORDER. So the drill family varies noise at each level the floor pools over
# (night, regime, layer, pattern, arm) and a STEP and a DRIFT in box speed inside a block of each
# level of the night's launch order (the night; one pattern's block; one layer of it; one cell =
# one regime there; the cell's middle round, where a step splits the arms). The blocks sit in
# hex24 (the largest twin pool, r38 J2's shape) and the middle round also in hex64 (a 2-arm pool).
CLASS_TAUS = (0.01, 0.02, 0.03)
CLASS_SIZES = (0.02, 0.05, 0.10)


def _c12(k):
    return k[0] in ("C1", "C2")


CLASS_NOISE = [
    # (level, what, armoff selector): the offset exp(N(0, tau)) per arm cell it names
    ("night", "every arm, A/A too", lambda k: True),
    ("regime", "one regime (random), A/A spared", lambda k: _c12(k) and k[3] == "random"),
    ("layer", "one layer (on), A/A spared", lambda k: _c12(k) and k[4] == "on"),
    ("pattern", "hex24 (pool 4)", lambda k: k[1] == "hex24"),
    ("pattern", "hex32 (pool 3)", lambda k: k[1] == "hex32"),
    ("pattern", "hex64 (pool 2)", lambda k: k[1] == "hex64"),
    ("arm", "I, every cell", lambda k: _c12(k) and k[2] == "I"),
] + [("arm", "H(%d), every cell" % h, (lambda k, a="h%d" % h: _c12(k) and k[2] == a)) for h in GRID]


@functools.lru_cache(maxsize=None)
def night_blocks():
    """The launch-order blocks the class drill places a step or a drift in: {name: (first, end)}
    positions in the interleaved night (`launch_order` over step 1's cells); each block is
    asserted CONTIGUOUS, so the drill's block is the night's."""
    lo = launch_order(cells(cards=STEP1))
    sel = {
        "night": lambda c, r: True,
        "pattern block (hex24)": lambda c, r: c[:2] == ("C1", "hex24"),
        "layer block (hex24/off)": lambda c, r: c[:2] == ("C1", "hex24") and c[4] == "off",
        "regime cell (hex24/near-miss/off)": lambda c, r: c[:2] == ("C1", "hex24") and c[3:] == ("near-miss", "off"),
        "middle round (hex24/near-miss/off)": lambda c, r: (c[:2] == ("C1", "hex24") and c[3:] == ("near-miss", "off")
                                                            and r == LAUNCHES // 2),
        "middle round (hex64/near-miss/off)": lambda c, r: (c[:2] == ("C2", "hex64") and c[3:] == ("near-miss", "off")
                                                            and r == LAUNCHES // 2),
    }
    out = {}
    for name, f in sel.items():
        qs = [q for q, (c, r) in enumerate(lo) if f(c, r)]
        assert qs and qs[-1] - qs[0] + 1 == len(qs), "block %s is not contiguous" % name
        out[name] = (qs[0], qs[-1] + 1)
    return out


def time_drill(kind, block, size, seed, trials=NOISE_TRIALS, sigma=0.01, **kw):
    """P(h* != 64) and the nights with a first void, on 1 % nights with a box-speed STEP (x(1 +
    size) from a cut drawn uniformly inside the block, every night its own cut, held to the end)
    or a linear DRIFT (0 at the block's start to `size` at its end, held after) in launch order."""
    a, b = night_blocks()[block] if block in night_blocks() else block
    rng, rc = random.Random(seed), random.Random(seed + 7919)
    off = voids = 0
    for _ in range(trials):
        if kind == "step":
            cut = rc.randrange(a + 1, b) if b - a > 1 else a
            fx = lambda q, cut=cut: 1 + size if q >= cut else 1.0       # noqa: E731
        else:
            fx = lambda q: 1 + size * min(1.0, max(0.0, (q - a) / (b - a)))      # noqa: E731
        v = synth_night(rng, sigma, timefx=fx, **kw)
        off += v["hstar"] != GRID_TOP
        voids += v["voided_first"] > 0
    return off / trials, voids


def power_cells(head, regime, win):
    """`cellwins` for a true win of H(head) in ONE regime: every C1-C2 cell of that regime where the
    head's text is not I's (both layers)."""
    out = {}
    for card in ("C1", "C2"):
        for p in CARD_PATS[card]:
            if p in ("lit40", "abc60") or head >= len(PATTERNS[p][1]):
                continue
            for ly in LAYERS:
                out[(card, p, "h%d" % head, regime, ly)] = win
    return out


def power_rate(head=8, regime="hit-dense", win=0.95, trials=NOISE_TRIALS, seed=700, with_confirms=False):
    rng = random.Random(seed)
    vs = [synth_night(rng, 0.01, cellwins=power_cells(head, regime, win)) for _ in range(trials)]
    picks = [v["hstar"] for v in vs]
    if with_confirms:
        return sum(x == head for x in picks), picks, [v.get("confirm_cells", 0) for v in vs]
    return sum(x == head for x in picks), picks


def _flags(**kw):
    """Set the rule's control switches; returns the previous values (restore with _flags(**old))."""
    old = {k: globals()[k] for k in kw}
    globals().update(kw)
    return old


def _confirm_rows(rng, owed, **kw):
    return synth_rows(rng, 0.01, only={k: ["I.cf"] + ["h%d.cf" % h for h in hs] for k, hs in owed.items()}, **kw)[0]


def selftest_rev11(check):
    """The rev 11 rows (RULED r39): K1's layout twins, K2's R0 over the confirm, K3's per-arm
    confirm, K4's reading B and its power rows, K6's one owed list."""
    # ---- K1: a per-EXE offset held across the first reading, the re-runs and the confirm --------
    for j, tau in enumerate(CLASS_TAUS):
        ph, nvh, _fm = noise_drill(seed=1600 + j, exeoff=tau)
        cc = NOISE_LAST["confirm"]
        check("(r39 K1) per-exe offsets tau %d %%" % round(100 * tau), ph <= 0.05,
              "P(h* != 64) = %.3f over %d nights (accept <= 0.05); confirm cells on these no-win nights: mean %.2f, "
              "max %d, nights with one %d; nights with a first void %d; the night's MEASURED between-exe sigma "
              "(median) %.4f" % (ph, NOISE_TRIALS, statistics.mean(cc), max(cc), sum(1 for x in cc if x), nvh,
                                 NOISE_LAST["layout"]))
        check("(r39 K1) the night measures the exe offset, tau %d %%" % round(100 * tau),
              abs(NOISE_LAST["layout"] - tau) <= 0.35 * tau,
              "median measured between-exe sigma %.4f against the true %.4f (accept within 35 %%)"
              % (NOISE_LAST["layout"], tau))
    _p, _n, _f = noise_drill(seed=1603)
    check("(r39 K1) the measurement on a night without exe offsets", NOISE_LAST["layout"] <= 0.004,
          "median measured between-exe sigma %.4f (accept <= 0.004: launch noise alone reads ~0)" % NOISE_LAST["layout"])
    # its control: rev 10's floor (no layout term) and confirm (step 1's exes again) on the 2 % night
    old = _flags(LAYOUT_TERM=False, LAYOUT_TWINS=False, LAYOUT_TWIN_ARM=False)
    try:
        pc, _nv, _fm = noise_drill(seed=1610, exeoff=0.02)
    finally:
        _flags(**old)
    check("(r39 K1) control: tau 2 %, rev 10's floor and confirm", pc > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15; r39 measured 0.62-0.63)"
          % (pc, NOISE_TRIALS))
    # ---- K4: READING B; the multi-winner power row and the one-winner 4 % row (RECORD) ------------
    multi = {}
    for h in (0, 1, 2, 4, 8, 16):
        multi.update(power_cells(h, "hit-dense", 0.95))
    rng = random.Random(1620)
    pm = [synth_night(rng, 0.01, cellwins=multi)["hstar"] for _ in range(NOISE_TRIALS)]
    old = _flags(READING_B=False)
    try:
        rng = random.Random(1620)
        pma = [synth_night(rng, 0.01, cellwins=multi)["hstar"] for _ in range(NOISE_TRIALS)]
    finally:
        _flags(**old)
    check("(r39 K4) power: every head <= 16 5 % faster (hit-dense)", sum(x == 16 for x in pm) >= 0.85 * NOISE_TRIALS,
          "h* = 16 (the largest equal head) in %d of %d nights (accept >= 85 %%); picks %s"
          % (sum(x == 16 for x in pm), NOISE_TRIALS, dict(sorted((x, pm.count(x)) for x in set(pm)))))
    check("(r39 K4) control: the same nights, rev 10's reading", sum(x == 16 for x in pma) < 0.85 * NOISE_TRIALS,
          "h* = 16 in %d of %d nights (the drill sees the defect: accept < 85 %%; r39 measured 122-131)"
          % (sum(x == 16 for x in pma), NOISE_TRIALS))
    n4, _p4 = power_rate(win=0.96, seed=1621)
    print("REC  %-48s h* = 8 in %d of %d nights (RECORD, not gated: a one-winner 4 %% win, H(8) in hit-dense; "
          "r39 measured 182 under rev 10)" % ("(r39 K4) power: a 4 % win of H(8), one regime", n4, NOISE_TRIALS))

    # ---- K2 and K3: the confirm's own reading, through R0 and per arm ----------------------------
    def win_night(seed, edit):
        """A night with a real 10 % win of H(8) in hit-dense, its confirm rows `edit`ed, analysed."""
        rng = random.Random(seed)
        old = _flags(APPROX={})
        try:
            cw = power_cells(8, "hit-dense", 0.90)
            rows, same = synth_rows(rng, 0.01, cellwins=cw)
            night = {"files": {"results.tsv": (rows, {})}, "same": same}
            v = analyse(night, set())
            owed = v["owed_confirm"]
            conf = _confirm_rows(rng, owed, cellwins=cw)
            edit(conf, owed)
            night["files"]["results_confirm.tsv"] = (conf, {})
            return v, analyse(night, set())
        finally:
            _flags(**old)

    def gatefail(arm):
        def ed(conf, owed):
            card, pat, rg, ly = sorted(owed)[0]
            conf[(card, pat, arm, rg, ly)] = {"status": "gatefail", "med": None, "launches": [], "method": "kit",
                                              "note": "GATE FAIL"}
        return ed
    v0, v = win_night(1630, lambda conf, owed: None)
    _v0, vh = win_night(1630, gatefail("h8.cf"))
    _v0, vi = win_night(1630, gatefail("I.cf"))
    check("(r39 K2) a gate failure in the CONFIRM reaches R0", v["hstar"] == 8
          and vh["hstar"] != 8 and any("H(8) failed its gate" in l and "results_confirm.tsv" in l for l in vh["lines"])
          and vi["code"] == 2 and vi["hstar"] is None and any("I.cf failed its gate" in l for l in vi["lines"]),
          "clean: h* %s (%d cells owed); H(8)'s confirm row gatefail: h* %s, R0 line %s; I's: code %d, h* %s"
          % (v["hstar"], len(v0["owed_confirm"]), vh["hstar"],
             any("H(8) failed its gate" in l for l in vh["lines"]), vi["code"], vi["hstar"]))

    def void_arm(arm):
        def ed(conf, owed):
            for card, pat, rg, ly in owed:
                conf[(card, pat, arm, rg, ly)] = {"status": "void", "med": None, "launches": [], "method": "kit",
                                                  "note": "void"}
        return ed
    _v0, vo = win_night(1631, void_arm("h0.cf"))
    _v0, vI = win_night(1631, void_arm("I.cf"))
    check("(r39 K3) the confirm reads I's twin and the head's own", vo["hstar"] == 8 and vI["hstar"] == GRID_TOP,
          "another head's confirm arm void in every owed cell: h* %s (accept 8); I.cf void there: h* %s (accept 64, "
          "nothing confirms)" % (vo["hstar"], vI["hstar"]))

    # ---- K6: `rule --g2` and `rerun` owe ONE list; a G2-defective head never stalls the night -----
    import pwd
    import tempfile
    troot = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % pwd.getpwuid(os.getuid()).pw_name
    os.makedirs(troot, exist_ok=True)

    def k6_night(seed, keep_record=True):
        """One night through the COMMANDS (files on disk): `rule --g2` (G2 = {16}) then `rerun` without
        --g2, as the night's jobs call them, until the rule stops owing a rerun. Returns (stalled,
        rerun timed exactly the rule's owed list every pass, passes)."""
        import contextlib
        import io
        rng = random.Random(seed)
        cw = power_cells(8, "hit-dense", 0.955)
        old = _flags(APPROX={})
        real_tc = time_cells
        same_lists = True
        try:
            with tempfile.TemporaryDirectory(dir=troot) as td:
                rows, same = synth_rows(rng, 0.01, cellwins=cw)
                json.dump(same, open(os.path.join(td, "same_as_I.json"), "w"))
                with open(os.path.join(td, "results.tsv"), "w") as f:
                    f.write(HEADER)
                    for k, r in rows.items():
                        f.write(row_line(k, "ok", r["launches"]))
                g2f = os.path.join(td, "g2.txt")
                open(g2f, "w").write("16\n")
                timed = []

                def fake_tc(rundir, cl, path, with_approx=True):
                    timed.append(sorted(cl))
                    only = {}
                    for c in cl:
                        only.setdefault((c[0], c[1], c[3], c[4]), []).append(c[2])
                    fresh = synth_rows(rng, 0.01, cellwins=cw, only=only)[0]
                    new = not os.path.exists(path)
                    with open(path, "a") as f:
                        if new:
                            f.write(HEADER)
                        for c in cl:
                            f.write(row_line(c, "ok", fresh[c]["launches"]))
                globals()["time_cells"] = fake_tc
                for i in range(6):
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        code = cmd_rule([td, "--g2", g2f])
                    if not (code == 3 and "rule: NEXT cards.py rerun RUNDIR" in out.getvalue()):
                        return False, same_lists, i
                    vr = owed_now(td, g2f)          # what `rule --g2` owes
                    want = sorted(confirm_cells(vr["owed_confirm"])) if vr["owed_confirm"] else None
                    if not keep_record:             # the control: rev 10's `rerun` read no G2 list
                        os.remove(os.path.join(td, G2_RECORD))
                    timed.clear()
                    with contextlib.redirect_stdout(io.StringIO()):
                        cmd_rerun([td])
                    if want is not None and timed != [want]:
                        same_lists = False
                return True, same_lists, 6
        finally:
            globals()["time_cells"] = real_tc
            _flags(**old)
    res = [k6_night(1640 + i) for i in range(12)]
    ctl = [k6_night(1640 + i, keep_record=False) for i in range(12)]
    check("(r39 K6) `rule --g2` and `rerun` owe one list (G2 = {16})", not any(s for s, _l, _n in res)
          and all(l for _s, l, _n in res) and sum(1 for s, _l, _n in ctl if s) >= 1,
          "12 nights through the commands: stalled %d, rerun timed the rule's owed list on every pass: %s, passes %s; "
          "control (no G2 record, rev 10's rerun): stalled %d of 12 (accept >= 1)"
          % (sum(1 for s, _l, _n in res if s), all(l for _s, l, _n in res), [n for _s, _l, n in res],
             sum(1 for s, _l, _n in ctl if s)))


def cmd_selftest(args):
    if "--rev11" in args:       # the rev 11 rows alone (a development aid; the night runs the whole selftest)
        bad, n = [0], [0]

        def check(name, ok, line):
            bad[0] += not ok
            n[0] += 1
            print("%s %-48s %s" % ("ok  " if ok else "FAIL", name, line))
        selftest_rev11(check)
        print("selftest --rev11: %d checks, %d failed" % (n[0], bad[0]))
        return 1 if bad[0] else 0
    bad = 0
    for name, spec, want_h, want_label in DRILLS:
        h, label, rec, det = drill(spec)
        ok = h == want_h and want_label in label
        bad += not ok
        print("%s %-48s h* = %-4s %s" % ("ok  " if ok else "FAIL", name, h, label))
        if not ok:
            print("     want h* = %s, a label holding %r; detail %s" % (want_h, want_label, det))

    nchk = len(DRILLS)

    def check(name, ok, line):
        nonlocal bad, nchk
        bad += not ok
        nchk += 1
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
    # G2 (rev 8, r36): the same acceptance under HETEROGENEOUS noise: one regime 2x or 3x the
    # others, the A/A cells 0.7x the arms, and every regime at its own scale
    for i, (nm, kw) in enumerate((
            ("one regime 2x (random)", {"rscale": {"random": 2.0}}),
            ("one regime 3x (not-warm)", {"rscale": {"not-warm": 3.0}}),
            ("A/A cells 0.7x the arms", {"aascale": 0.7}),
            ("regimes 0.5/1/3/0.7/2/1 x", {"rscale": dict(zip(REGIMES, (0.5, 1, 3, 0.7, 2, 1)))}))):
        ph, nvh, fmh = noise_drill(seed=40 + i, **kw)
        check("(G2) noise drill, %s" % nm, ph <= 0.05,
              "P(h* != 64) = %.3f over %d trials (accept <= 0.05); median f(A/A) %.4f; nights with a first void %d"
              % (ph, NOISE_TRIALS, fmh, nvh))
    # its control: rev 7's floor (the A/A term alone) on the 3x night must FAIL the acceptance;
    # rev 9's twin term and gate also see a noisier regime, so the control turns them off too
    # (rev 10: and the per-pattern twin term, which sees a noisier regime too)
    globals()["POOL_TERM"], globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = (False,) * 7
    try:
        pc, _nv, _fm = noise_drill(seed=41, rscale={"not-warm": 3.0})
    finally:
        globals()["POOL_TERM"], globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = (True,) * 7
    check("(G2) control: one regime 3x, A/A floor alone", pc > 0.15,
          "P(h* != 64) = %.3f over %d trials (the drill sees the defect: accept > 0.15)" % (pc, NOISE_TRIALS))
    # its power (the floor's cost, recorded): a true 10 % win of every head <= 8 where it loops
    rng = random.Random(3)
    picks = [synth_night(rng, 0.01, wins={h: 0.90 for h in (0, 1, 2, 4, 8)})["hstar"] for _ in range(60)]
    check("(F2) power: a true 10 % win at h <= 8", sum(x == 8 for x in picks) / 60 >= 0.9,
          "h* = 8 in %d of 60 nights (picks %s)" % (sum(x == 8 for x in picks), sorted(set(picks))))
    # G4 (rev 8, r36): a real one-cell win of H(8) alone (5 % in C1/hex32/hit-dense/off) never
    # ships a head that measured no win (r36 measured H(16)/H(24) MEASURED in ~12 % of nights)
    rng = random.Random(9)
    g4 = {}
    for _ in range(200):
        x = synth_night(rng, 0.01, cellwins={("C1", "hex32", "h8", "hit-dense", "off"): 0.95})["hstar"]
        g4[x] = g4.get(x, 0) + 1
    nowin = sum(n for x, n in g4.items() if x not in (8, GRID_TOP))
    check("(G4) a one-cell win of H(8) alone", nowin <= 10,
          "picks %s over 200 nights; a head other than 8 or 64: %d (accept <= 10, the noise budget)"
          % (dict(sorted(g4.items())), nowin))
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

    # G3 (rulings R1, rev 8 r36): a MEDIAN-MOVING split (3 of 5 launches slow) of I's arm in ONE
    # cell, at sizes f..2f (f this script's median floor on a 1 % night): I's pooled reading
    # keeps it from shipping a head (r36 measured h* = 24 in 54 of 100 nights at 5 %)
    cellI = ("C1", "hex32", "I", "hit-dense", "off")
    for mult in (1.0, 1.5, 2.0):
        s = fmed * mult
        rng = random.Random(int(50 + 10 * mult))
        offn = sum(synth_night(rng, 0.01, splits={cellI: (3, 1 + s)})["hstar"] != GRID_TOP
                   for _ in range(NOISE_TRIALS))
        check("(G3) 3-of-5 split of I, %.1f f (%.1f %%)" % (mult, 100 * s), offn / NOISE_TRIALS <= 0.05,
              "P(h* != 64) = %.3f over %d nights (accept <= 0.05)" % (offn / NOISE_TRIALS, NOISE_TRIALS))
    # its control: rev 7's reading (I's own arm alone) under the same split must FAIL the acceptance
    # (rev 10: rev 7 had no per-pattern twin term either; with I alone no pool has a twin, so the
    # term would void every cell and blind the control)
    globals()["POOL_I"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = False, False, False, False, False
    try:
        rng = random.Random(65)
        offc = sum(synth_night(rng, 0.01, splits={cellI: (3, 1 + 1.5 * fmed)})["hstar"] != GRID_TOP
                   for _ in range(NOISE_TRIALS))
    finally:
        globals()["POOL_I"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = True, True, True, True, True
    check("(G3) control: the 1.5 f split, I's arm alone", offc / NOISE_TRIALS > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)"
          % (offc / NOISE_TRIALS, NOISE_TRIALS))
    # its converse: the same split in a HEAD arm (not pooled) never ships that head
    cellH = ("C1", "hex32", "h8", "hit-dense", "off")
    for mult in (1.0, 2.0):
        s = fmed * mult
        rng = random.Random(int(70 + 10 * mult))
        picks = [synth_night(rng, 0.01, splits={cellH: (3, 1 + s)})["hstar"] for _ in range(100)]
        check("(G3) converse: the split in H(8), %.1f f" % mult, sum(x == 8 for x in picks) == 0,
              "h* = 8 in %d of 100 nights (accept 0); picks %s" % (sum(x == 8 for x in picks), sorted(set(picks))))
    # The FAST 3-of-5 split in a head arm: outside the pool's reach and the gate's (r36's null-rate
    # numbers, rev 8 §3 "Bimodal"), rev 9's NAMED LIMIT (27 of 100). Rev 10's confirming re-run
    # (r38 R2) retires it: a transient does not recur on the confirm. Now a check (accept <= 5 of
    # 100), with rev 9's rate printed beside it
    rng = random.Random(90)
    picks = [synth_night(rng, 0.01, splits={cellH: (3, 1 / (1 + 1.5 * fmed))})["hstar"] for _ in range(100)]
    globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = False, False, False, False
    try:
        rng = random.Random(90)
        picks9 = [synth_night(rng, 0.01, splits={cellH: (3, 1 / (1 + 1.5 * fmed))})["hstar"] for _ in range(100)]
    finally:
        globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = True, True, True, True
    check("(G3, r38 R2) a FAST 3-of-5 split in H(8), 1.5 f", sum(x == 8 for x in picks) <= 5,
          "h* = 8 in %d of 100 nights (accept <= 5: rev 9's NAMED LIMIT retired by the confirm)" % sum(x == 8 for x in picks))
    # its control, CHECKED (rev 11, r39 K8: rev 10 only printed it): rev 9's rule must ship the split
    check("(G3, r38 R2) control: the FAST split, rev 9's rule", sum(x == 8 for x in picks9) > 15,
          "h* = 8 in %d of 100 nights, no per-pattern term and no confirm (the drill sees the limit: accept > 15)"
          % sum(x == 8 for x in picks9))

    # H1 (rev 9, RULED r37): BETWEEN-RUN noise, an offset per ARM held over its 5 launches. In one
    # regime with the A/A cells spared (the shape the launch term and the night-wide A/A term
    # cannot see), and in every regime (A/A arms included, and spared)
    for i, tau in enumerate((0.01, 0.02, 0.03)):
        for nm, ao, sd in (("one regime (not-warm), A/A spared", (tau, ("not-warm",), True), 300 + i),
                           ("every regime", (tau, None, False), 310 + i),
                           ("every regime, A/A spared", (tau, None, True), 320 + i)):
            ph, nvh, fmh = noise_drill(seed=sd, armoff=ao)
            check("(H1) arm offsets tau %d %%, %s" % (round(100 * tau), nm), ph <= 0.05,
                  "P(h* != 64) = %.3f over %d nights (accept <= 0.05); median f(A/A) %.4f, f(hit-dense/off) %.4f; "
                  "nights with a first void %d" % (ph, NOISE_TRIALS, fmh, NOISE_LAST["fcell"], nvh))
    # its control: rev 8's rule (no twin term, no agreement gate) on the 2 % one-regime night
    globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = (False,) * 6
    try:
        pc, _nv, _fm = noise_drill(seed=301, armoff=(0.02, ("not-warm",), True))
    finally:
        globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = (True,) * 6
    check("(H1) control: tau 2 %, one regime, rev 8's rule", pc > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)" % (pc, NOISE_TRIALS))

    # H2 (rev 9, RULED r37): a WHOLE-ARM (5-of-5) shift of I and of H(64) in the SMALLEST pools (I,
    # H(64): hex64, uuid36, alt49), sized by the cell's own floor f (hit-dense, off) on a 1 % night
    _p, _n, _f = noise_drill(seed=1)
    fcell = NOISE_LAST["fcell"]
    for pat in ("hex64", "uuid36", "alt49"):
        for arm in ("I", "h%d" % GRID_TOP):
            for j, mult in enumerate((1.0, 1.5, 2.0)):
                key = ("C2", pat, arm, "hit-dense", "off")
                ph, nvh, _fm = noise_drill(seed=400 + 10 * j + (arm == "I") + 100 * ("hex64", "uuid36", "alt49").index(pat),
                                           splits={key: (5, 1 + mult * fcell)})
                check("(H2) 5-of-5 shift of %s at %s, %.1f f (%.1f %%)" % (arm if arm == "I" else "H(64)", pat, mult,
                                                                          100 * mult * fcell), ph <= 0.05,
                      "P(h* != 64) = %.3f over %d nights (accept <= 0.05); nights with a first void %d"
                      % (ph, NOISE_TRIALS, nvh))
    globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = (False,) * 6
    try:
        pc, _nv, _fm = noise_drill(seed=499, splits={("C2", "hex64", "I", "hit-dense", "off"): (5, 1 + 1.5 * fcell)})
    finally:
        globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = (True,) * 6
    check("(H2) control: I at hex64, 1.5 f, rev 8's rule", pc > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)" % (pc, NOISE_TRIALS))
    # the agreement gate's own cost: the void rate it ADDS on pure noise (F3's acceptance: <= 5 %
    # of nights void a cell once, whatever voids it)
    for nm, nz, sd in (("normal", "normal", 500), ("t(5)", "t5", 501)):
        globals()["AGREE_GATE"] = False
        try:
            _p0, nv0, _f0 = noise_drill(seed=sd, noise=nz)
        finally:
            globals()["AGREE_GATE"] = True
        _p1, nv1, _f1 = noise_drill(seed=sd, noise=nz)
        check("(H2) the gate's void rate, %s launches" % nm, nv1 / NOISE_TRIALS <= 0.05,
              "nights with a first void %.3f with the gate, %.3f without: added %.3f (accept: with <= 0.05)"
              % (nv1 / NOISE_TRIALS, nv0 / NOISE_TRIALS, (nv1 - nv0) / NOISE_TRIALS))
    # H3 (rev 9, r37): I's pool record must name every C1-C2 pattern x layer, each with the top
    full = {p: {ly: [h for h in GRID if h >= len(PATTERNS[p][1]) or p in ("lit40", "abc60")] for ly in LAYERS}
            for c in ("C1", "C2") for p in CARD_PATS[c]}
    part = {p: v for p, v in full.items() if p != "hex64"}
    nolayer = dict(full, uuid36={"off": full["uuid36"]["off"]})
    no64 = dict(full, alt49={ly: [] for ly in LAYERS})
    refs = [pool_record_refusal(x) for x in (full, None, part, nolayer, no64)]
    APP, globals()["APPROX"] = APPROX, {}
    try:
        rows, _same = synth_rows(random.Random(11), 0.01)
        vmiss = analyse({"files": {"results.tsv": (rows, {})}, "same": None}, set())
    finally:
        globals()["APPROX"] = APP
    check("(H3) a missing or partial pool record is refused", refs[0] is None and all(refs[1:]) and vmiss["code"] == 2
          and vmiss["hstar"] is None and any("REFUSED" in l for l in vmiss["lines"]),
          "full: %s; missing/partial/layer/no-64 refused: %s; the rule on a missing record: code %d"
          % (refs[0], [bool(x) for x in refs[1:]], vmiss["code"]))
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
    check("(F5, G5) C3 gate fail of H(64): a CHOSEN tie at 32", v["hstar"] == 32
          and any("H(64) failed its gate in C3" in l for l in v["lines"]) and v["code"] == 3
          and "largest R0-surviving head (CHOSEN" in v["label"] and "MEASURED" not in v["label"],
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
    # G6 (rev 8, r36): R3's DERIVED is reachable: H(1) 30 % faster wherever it loops; every
    # moving class picks 1, its E[D] head; the literal classes are not read
    APP, globals()["APPROX"] = APPROX, {}
    try:
        rng = random.Random(10)
        rows, same = synth_rows(rng, 0.01, wins={1: 0.70})
        night = {"files": {"results.tsv": (rows, {})}, "same": same}
        v = analyse(night, set())
        if v["owed_confirm"]:       # rev 10 (r38 R2): its wins are confirmed by the cells' re-run (rev 11: fresh twins)
            fresh, _s = synth_rows(rng, 0.01, wins={1: 0.70}, only={k: ["I.cf"] + ["h%d.cf" % h for h in hs]
                                                                    for k, hs in v["owed_confirm"].items()})
            night["files"]["results_confirm.tsv"] = (fresh, {})
            v = analyse(night, set())
    finally:
        globals()["APPROX"] = APP
    notread = sorted(l.split()[2].rstrip(":") for l in v["lines"] if "never a mover" in l)
    check("(G6) R3 DERIVED reachable", v["hstar"] == 1 and v["label"].startswith("DERIVED")
          and notread == ["abc60", "lit40"], "h* %s, %s; classes not read %s" % (v["hstar"], v["label"][:60], notread))
    # G7 (rev 8, r36; rev 9, r37 H4): the deny check reds on C3's population (an ignored deny
    # renders I as H(64), which loops past offset 64 at k = 500), with H(64), the DEFECT'S arm, as
    # the reach arm
    c3loop = b"x = ({ size_t rxa_mf1_j = 64; for (; rxa_mf1_j < 500; rxa_mf1_j++) if (!(a)) break; });"
    l0 = b"x = ({ size_t rxa_mf1_j = 0; for (; rxa_mf1_j < 500; rxa_mf1_j++) if (!(a)) break; });"
    lk, rc_ = loop_audit([("hex500 I off", "I", c3loop), ("hex500 h0 off", "h0", l0),
                          ("hex500 h64 off", "h64", c3loop)], reach_arm="h64")
    check("(G7) C3 deny check: an ignored deny fails", lk == ["hex500 I off"] and rc_ == ["hex500 h64 off"],
          "leaks %s reach %s" % (lk, rc_))
    # H4: at a width where H(64) loops nowhere (32), an ignored deny renders I = H(64) loop-free:
    # with L as the reach (rev 8) it read GREEN; with H(64) the reach is empty, VACUOUS and red
    w32 = [("hex500 I off", "I", b"if (!(a)) return 0;"), ("hex32 h0 off", "h0", l0),
           ("hex500 h64 off", "h64", b"if (!(a)) return 0;")]
    lk0, rc0 = loop_audit(w32, reach_arm="h0")
    lk, rc_ = loop_audit(w32, reach_arm="h64")
    seen = {}
    real = check_deny
    globals()["check_deny"] = lambda _rd, cl, reach_arm=None, vacuous_why=None: seen.update(
        arms=sorted({c[2] for c in cl}), cards=sorted({c[0] for c in cl}), reach=reach_arm, why=vacuous_why) or ([], 0, 0)
    try:
        c3_deny_check("-")
    finally:
        globals()["check_deny"] = real
    check("(H4) c3's reach arm is H(64), the defect's", lk0 == [] and rc0 == ["hex32 h0 off"] and lk == [] and rc_ == []
          and seen.get("reach") == "h64" and "h64" in seen.get("arms", []) and seen.get("cards") == ["C3", "C4"]
          and "loops nowhere" in (seen.get("why") or ""),
          "width 32, ignored deny: reach h0 %s (rev 8: green), reach h64 %s (vacuous: red); c3 checks %s over "
          "arms %s, reach %s" % (rc0, rc_, seen.get("cards"), seen.get("arms"), seen.get("reach")))
    # G8 (rev 8, r36): an empty movers file at h < 64 is refused; a smoke exits 4 first (the
    # example a real mover, r37 H7: `\w{32}\B` loops at h <= 29)
    r_none, r_empty, r_one, r_64 = (movers_refusal(32, None), movers_refusal(32, []),
                                    movers_refusal(24, [r"\w{32}\B"]), movers_refusal(64, []))
    check("(G8) identity: empty movers at h < 64 refused", bool(r_none) and bool(r_empty) and r_one is None
          and r_64 is None, "none: %s; empty: %s; one: %s; h 64 empty: %s" % (
              bool(r_none), (r_empty or "")[:40], r_one, r_64))
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        codes = (census_verdict([], 5), census_verdict(["x"], 5), census_verdict([], None), census_verdict(["x"], None))
    check("(G8) identity: smoke exit 4 before the empty FAIL", codes == (4, None, 1, None),
          "limit+empty %s, limit %s, empty %s, full %s" % codes)
    # H7 (rev 9, r37): the identity check floors the population that MOVES, not the file
    rr = (reach_refusal(32, 0, 40), reach_refusal(24, 3, 40), reach_refusal(64, 0, 40))
    check("(H7) identity: zero movers at h < 64 refused", bool(rr[0]) and rr[1] is None and rr[2] is None,
          "h 32 none move: %s; h 24 three move: %s; h 64: %s" % (bool(rr[0]), rr[1], rr[2]))
    # ---- rev 10 (RULED r38): THE CLASS DRILL, its controls, the power line, the void rate ----
    for i, (lvl, what, sel) in enumerate(CLASS_NOISE):
        for j, tau in enumerate(CLASS_TAUS):
            ph, nvh, _fm = noise_drill(seed=1000 + 10 * i + j, armoff=(tau, sel))
            check("(r38) noise at %s: %s, tau %d %%" % (lvl, what, round(100 * tau)), ph <= 0.05,
                  "P(h* != 64) = %.3f over %d nights (accept <= 0.05); nights with a first void %d"
                  % (ph, NOISE_TRIALS, nvh))
    for i, block in enumerate(night_blocks()):
        for kind in ("step", "drift"):
            for j, size in enumerate(CLASS_SIZES):
                ph, nvh = time_drill(kind, block, size, seed=1200 + 20 * i + 10 * (kind == "drift") + j)
                check("(r38) %s %+d %% in the %s" % (kind, round(100 * size), block), ph <= 0.05,
                      "P(h* != 64) = %.3f over %d nights (accept <= 0.05); nights with a first void %d"
                      % (ph, NOISE_TRIALS, nvh))
    # the controls: each defect's own shape under rev 9's rule must FAIL the acceptance
    globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = False, False, False, False
    try:
        pj1, _n = noise_drill(seed=1400, armoff=(0.02, lambda k: k[1] == "hex64"))[:2]
        cut = min(launch_slots("arm-major")[("C1", "hex24", "h8", rg, ly)][0] for rg in REGIMES for ly in LAYERS)
        pj2, _n = time_drill("step", (cut, cut + 1), 0.05, seed=1401, order="arm-major")
        pj2i, _n = time_drill("step", (cut, cut + 1), 0.05, seed=1401)
        parm, _n, _f = noise_drill(seed=1402, armoff=(0.02, lambda k: _c12(k) and k[2] == "h8"))
    finally:
        globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = True, True, True, True
    check("(r38) control J1: hex64 tau 2 %, rev 9's floor", pj1 > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)" % (pj1, NOISE_TRIALS))
    check("(r38) control J2: +5 % after hex24's H(4), arm-major", pj2 > 0.15,
          "P(h* != 64) = %.3f over %d nights, rev 9's floor and order (accept > 0.15); the same cut in the "
          "interleaved order, rev 9's floor: %.3f" % (pj2, NOISE_TRIALS, pj2i))
    # rev 11 (r39 K8): the interleaved order is r38 J2's fix, so the same cut in ROUNDS under rev 9's floor
    # must hold (a check, not a printed number: an order that regressed to arm-major reds here)
    check("(r38 J2) the same cut in rounds, rev 9's floor", pj2i <= 0.05,
          "P(h* != 64) = %.3f over %d nights (the rounds alone hold the step: accept <= 0.05)" % (pj2i, NOISE_TRIALS))
    check("(r38 R2) control: H(8)'s arm tau 2 %, rev 9's rule", parm > 0.15,
          "P(h* != 64) = %.3f over %d nights, no per-pattern term and no confirm (accept > 0.15)" % (parm, NOISE_TRIALS))
    # the POWER line: a real 5 % win of ONE head in ONE regime, before (rev 9's rule) and after;
    # with the confirm cells it costs (the plan's re-run term on a night with one real win)
    globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = False, False, False, False
    try:
        pw0 = {rg: power_rate(regime=rg)[0] for rg in ("hit-dense", "random")}
    finally:
        globals()["PAT_TWIN"], globals()["CONFIRM"], globals()["LAYOUT_TERM"], globals()["LAYOUT_TWIN_ARM"] = True, True, True, True
    pw1, pcc = {}, {}
    for rg in ("hit-dense", "random"):
        pw1[rg], _p, pcc[rg] = power_rate(regime=rg, with_confirms=True)
    check("(r38) power: a 5 % win of H(8) in one regime", all(pw1[rg] >= max(0.9 * NOISE_TRIALS, pw0[rg] / 2)
                                                             for rg in pw1),
          "h* = 8 in %s of %d nights (rev 9's rule: %s; accept >= 90 %% and >= half rev 9's); confirm cells a night "
          "mean %s" % ("/".join("%s %d" % kv for kv in pw1.items()), NOISE_TRIALS,
                       "/".join("%s %d" % kv for kv in pw0.items()),
                       "/".join("%s %.1f" % (rg, statistics.mean(v)) for rg, v in pcc.items())))
    # the void rate on pure noise under rev 10 (F3: <= 5 % of nights void a cell once)
    for nm, nz, sd in (("normal", "normal", 1500), ("t(5)", "t5", 1501)):
        _p, nv, _f = noise_drill(seed=sd, noise=nz)
        check("(r38) void rate on pure noise, %s launches" % nm, nv / NOISE_TRIALS <= 0.05,
              "nights with a first void %.3f (accept <= 0.05); confirm cells a night mean %.3f, nights with one %d"
              % (nv / NOISE_TRIALS, statistics.mean(NOISE_LAST["confirm"]), sum(1 for x in NOISE_LAST["confirm"] if x)))
    selftest_rev11(check)
    # J2: `time_cells` times in ROUNDS (stubbed execution, no clock): each run of n launches holds
    # every arm of the cell once, and the order is the one the drills place their steps in
    import tempfile
    calls = []
    real_p, real_e = prepare_cell, _exec
    globals()["prepare_cell"] = lambda _rd, c, _n: list(c)
    globals()["_exec"] = lambda argv, c, env=None: calls.append(tuple(c)) or "t %d\n" % (len(calls) + 1)
    try:
        cl = [c for c in cells(cards=("C1",)) if c[1] == "hex24" and c[3] in ("hit-dense", "near-miss")]
        import pwd
        troot = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % pwd.getpwuid(os.getuid()).pw_name
        os.makedirs(troot, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=troot) as td:      # the temp root, never /tmp
            out = os.path.join(td, "r.tsv")
            open(out, "w").close()
            time_cells(td, cl, out)
            nrows = sum(1 for ln in open(out) if not ln.startswith("#"))
    finally:
        globals()["prepare_cell"], globals()["_exec"] = real_p, real_e
    n_arm = len(GRID) + 2       # I, its layout twin I.lt (rev 11), the finite heads
    rounds = [calls[i:i + n_arm] for i in range(0, len(calls), n_arm)]
    rr = all(len(set(r)) == n_arm and len({(c[0], c[1], c[3], c[4]) for c in r}) == 1 for r in rounds)
    same_order = [c for c, _i in launch_order(cl)] == calls
    check("(r38 J2) time_cells interleaves the arms in rounds", rr and same_order and nrows == len(cl)
          and len(calls) == LAUNCHES * len(cl),
          "%d launches over %d arm cells (%d rows): every round of %d holds each arm once: %s; the drills' order: %s"
          % (len(calls), len(cl), nrows, n_arm, rr, same_order))
    # J7: the identity reach per SOURCE: a movers file that moves nothing fails though a card moves
    rs = (source_reach_refusal(24, {"cards": 1, "census": 0, "movers": 0}, has_movers=True),
          source_reach_refusal(24, {"cards": 1, "census": 0, "movers": 2}, has_movers=True),
          source_reach_refusal(64, {"cards": 0, "census": 0, "movers": 0}, has_movers=True))
    check("(r38 J7) identity: the movers file's own reach", bool(rs[0]) and rs[1] is None and rs[2] is None,
          "h 24, a card moves, movers 0: %s; movers 2: %s; h 64: %s" % (bool(rs[0]), rs[1], rs[2]))
    print("selftest: %d checks, %d failed" % (nchk, bad))
    return 1 if bad else 0


# ---- the identity check (r45_reply rev 11 §3 "The head lever and its identity check") -------
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


def movers_refusal(h, movers):
    """At h < 64 the predicted movers are the population (r45_reply §3): a missing OR EMPTY
    movers file is refused (rev 8, r36 G8: at h = 32 and width 32 neither the cards nor the census
    can move, so an empty file would pass on populations blind to the head). None: proceed."""
    if h >= GRID_TOP:
        return None
    if movers is None:
        return ("h = %d < %d and no PATTERNS file: the predicted movers are the population at h* < 64 "
                "(r45_reply §3); refusing to pass on the cards alone" % (h, GRID_TOP))
    if not movers:
        return ("h = %d < %d and the PATTERNS file is EMPTY: an empty prediction at h* < 64 is a population "
                "of zero (K35); refusing" % (h, GRID_TOP))
    return None


def reach_refusal(h, n_moving, n_pats):
    """The identity check's population is the patterns whose bytes MOVE at h, not the file that
    names them (rev 9, r37 H7: `a{40}` is byte-identical at heads 0-64, so a movers file holding
    it passed the file-level refusal with zero head-sensitive patterns). At h < 64 a zero is
    refused (K35). None: proceed."""
    if h >= GRID_TOP or n_moving:
        return None
    return ("h = %d < %d and none of the %d patterns (cards, census, movers) renders differently at lever %d "
            "than at lever %d on the frozen binary: the identity check would compare a population blind to "
            "the head (K35); refusing" % (h, GRID_TOP, n_pats, h, GRID_TOP))


def source_reach_refusal(h, counts, has_movers):
    """The reach PER SOURCE (rev 10, RULED r38 J7): `counts` {cards, census, movers: the number of
    that source's patterns whose bytes move at h}. Rev 9 pooled the three (r37 H7), so a movers
    file that moves nothing passed whenever a card moved (r38 J7: `a{40}` beside card hex32 at h
    24). At h < 64 the movers file's OWN count must be nonzero, and so must the total (K35).
    None: proceed."""
    if h >= GRID_TOP:
        return None
    if has_movers and not counts.get("movers"):
        return ("h = %d < %d and none of the PATTERNS file's patterns renders differently at lever %d than at "
                "lever %d on the frozen binary (cards %d, census %d move): the predicted movers are the "
                "population at h* < 64 and this one is blind to the head (K35); refusing"
                % (h, GRID_TOP, h, GRID_TOP, counts.get("cards", 0), counts.get("census", 0)))
    if not sum(counts.values()):
        return reach_refusal(h, 0, 0)
    return None


def lever_reach(h, pats, wf):
    """The patterns whose FROZEN lever-h text differs from the frozen lever-64 text in some
    encoding x layer (the defect a head-blind identity check would degenerate to is lever-64's
    bytes: the reach renders that arm and counts where it differs)."""
    def one(job):
        p, ename, ly = job
        base = ["-p", PREFIX, "--features", "all"] + ENCODINGS[ename] + wf + LAYERS[ly] + ["-o", "-", "--pattern", p]
        a = subprocess.run([HARNESS, "--harness=span-head=%d" % h] + base, capture_output=True, timeout=600)
        b = subprocess.run([HARNESS, "--harness=span-head=%d" % GRID_TOP] + base, capture_output=True, timeout=600)
        return p, a.returncode != b.returncode or a.stdout != b.stdout
    jobs = [(p, e, ly) for p in pats for e in ENCODINGS for ly in LAYERS]
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
        return sorted({p for p, d in ex.map(one, jobs) if d})


def census_verdict(census, limit):
    """None to proceed; else the exit code: a SMOKE (--census-limit) exits 4 before any verdict,
    an empty census or none (rev 8, r36 G8); a full run with an empty census FAILS (K35)."""
    if limit:
        if not census:
            print("identity: SMOKE (--census-limit %d): the census of the first %d patterns is empty; not a "
                  "verdict" % (limit, limit))
            return 4
        return None
    if not census:
        print("identity: FAIL: the census is empty (K35)")
        return 1
    return None


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
    movers = None
    if rest:
        movers = [ln.rstrip("\n") for ln in open(rest[0], encoding="latin-1") if ln.strip()]
    why = movers_refusal(h, movers)
    if why:
        raise SystemExit("identity: " + why)
    movers = movers or []
    if rest:
        print("identity: predicted movers: %d (%s)" % (len(movers), rest[0]))
    pats = sorted({p[0] for p in PATTERNS.values()})
    n_corpus, census = census_covers(PCREC, limit)
    print("identity: census: %d corpus patterns read, %d covered by the frozen pcrec" % (n_corpus, len(census)))
    code = census_verdict(census, limit)
    if code is not None:
        return code
    allp = sorted(set(pats) | set(census) | set(movers))
    rebuilt = os.path.join(rebuilt_dir, "pcrec")
    wf = [] if WIDTH_FLAG == "none" else [WIDTH_FLAG]
    if h < GRID_TOP:
        moving = lever_reach(h, allp, wf)
        print("identity: reach: %d of %d patterns render differently at lever %d than at lever %d on the frozen "
              "binary (r37 H7)%s" % (len(moving), len(allp), h, GRID_TOP,
                                     (": " + ", ".join(repr(p) for p in moving[:8]) + (", ..." if len(moving) > 8 else ""))
                                     if moving else ""))
        mv = set(moving)
        counts = {"cards": len(mv & set(pats)), "census": len(mv & set(census)), "movers": len(mv & set(movers))}
        print("identity: reach per source (r38 J7): cards %d of %d, census %d of %d, movers %d of %d"
              % (counts["cards"], len(set(pats)), counts["census"], len(set(census)), counts["movers"], len(set(movers))))
        why = source_reach_refusal(h, counts, has_movers=bool(rest))
        if why:
            print("identity: FAIL: " + why)
            return 4 if limit else 1

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
