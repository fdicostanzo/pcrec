#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (lane forms, R-45 plan A).
"""memfn/tests/span_forms/cards.py -- THE SPAN FORMS' CARDS C1-C5, their rule R0-R5 and the
identity check (docs/design/memfn/r45_reply.md rev 6 §3 "The cards", "The head `h` and the
default", "The head lever and its identity check"; cards kit-grid@7 in
memfn/data/cards/kit-grid.tsv).

The kit's measurement script for the forms I / L / H(h) (memfn/src/window.c, THE SPAN FORMS).
Every cell compiles a card pattern at PCREC level on ONE binary (the frozen combined-branch
build), h set through the TEST-ONLY lever (`build/pcrec-harness --harness=span-head=N`, never a
shipped compile), I as the deny `--memfn=no-span-loop`, the engine route (C5) as
`--memfn=no-window-search`; the artifact plus one find-all wrapper is one C file per cell, its
answers gated against python `re` before any timing.

  plan                     every cell (card, pattern, arm, regime, layer) and the counts
  dry RUNDIR [--quick]     builds EVERY cell (compile, gcc, the gate on every regime's
                           subject; C4's size record) and prints the cell list and count;
                           no clock
  run RUNDIR               the timing (a kit window main clears with the owner; never in a
                           lane): taskset-pinned, calibrated, LAUNCHES launches, median per
                           cell, results.tsv. NOT RUN by the lane that wrote it
  rule RESULTS [--g2 V]    R0-R5 over a results.tsv: h*, its label, the filings
  selftest                 the rule against every drill r45_reply rev 6 §3 lists
  identity H [PATTERNS]    the lever at H on the frozen pcrec-harness against the rebuilt
                           build/pcrec, byte for byte, over the card patterns, the census
                           covers and any PATTERNS file (the predicted movers, one a line)

Env: PCREC_TREE (default: this file's tree), FROZEN (the frozen tree's build dir, default the
tree's build/), WIDTH_FLAG (default `--window-search-width=4095`; `none` on a tree without
main's width option), CPU (taskset core, default 15), LAUNCHES (default 5).
"""
import hashlib, json, os, random, re, statistics, subprocess, sys, threading
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
# until the bench names them, the script carries the kit's own approximation, LABELLED: a cell
# timed by an approximation is not the bench's regime (the night order's regimes fallback).
REGIMES = ["hit-dense", "near-miss", "not-warm", "miss-heavy", "short-subject", "random"]
APPROX = {"not-warm": "kit approximation (each 4 KiB call after a 32 MiB eviction sweep, "
                      "untimed); the bench's D198 (f) method replaces it",
          "short-subject": "kit approximation (LF-separated 48-80 byte records, one find-all "
                           "each); the bench's short-subject-search subject replaces it"}

# ---- the cards (r45_reply rev 6 §3 "The cards"; kit-grid@7) ---------------------------------
FINITE = ["h%d" % h for h in GRID]
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


def cells(hstar=GRID_TOP):
    """Every cell: (card, pattern, arm, regime, layer); `hstar` resolves C3/C4's H(h*) arm
    (before R1 has run, the shipped head, the grid top)."""
    out = []
    for card, pats, arms, regs, layers, kind in CARDS:
        for p in pats:
            for a in arms:
                a = "h%d" % hstar if a == "hstar" else a
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
    /* calibrated: repeat whole calls until 50 ms of timed work, report ns per byte */
    unsigned long reps = 0;
    ns = 0;
    do { call(regime, s, (size_t)n, NULL, &ns); reps++; } while (ns < 5e7);
    printf("TIME %.6f ns/B reps %lu\n", ns / reps / (double)n, reps);
    return 0;
}
"""
REGIME_CODE = {"short-subject": 1, "not-warm": 2}


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


def run_cell(rundir, cell, n, timed):
    card, pat, arm, regime, layer = cell
    if card == "C4":
        cb, secs, rss, text = size_record(rundir, pat, arm, layer)
        return "size c_bytes=%d gcc_s=%.2f rss_kb=%d text=%d" % (cb, secs, rss, text)
    exe, _a = build_cell(rundir, pat, arm, layer)
    sp, k, s = subj_file(rundir, pat, regime, n)
    code = str(REGIME_CODE.get(regime, 0))
    r = subprocess.run([exe, sp, code, k, s], capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise RuntimeError("cell %s: %s" % ("|".join(cell), r.stdout.strip() or r.returncode))
    if not timed:
        return r.stdout.strip()
    vals = []
    for _ in range(LAUNCHES):
        t = subprocess.run(["taskset", "-c", CPU, exe, sp, code, k, s], capture_output=True, text=True,
                           timeout=900, env=dict(os.environ, CARD_TIME="1"))
        if t.returncode:
            raise RuntimeError("cell %s: %s" % ("|".join(cell), t.stdout.strip()))
        vals.append(float(t.stdout.split()[1]))
    return "%.6f %.6f" % (statistics.median(vals), max(vals) - min(vals))


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
        print("# regime %s: %s" % (r, why))


def cmd_dry(args):
    """Builds every cell and runs its gate once (no clock): the cell list, the count, the
    distinct compiles, and every failure (a failure is the run's red)."""
    rundir = args[0]
    quick = "--quick" in args
    n = 1 << 16 if quick else 1 << 20
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
    same = identical_to_I(rundir, cl)
    print("# dry: cells %d, built and gated %d, failures %d; distinct compiles %d; subject %d B" %
          (len(cl), len(cl) - len(bad), len(bad), len(builds), n))
    print("# dry: H(h) text identical to I: %s" % ", ".join("%s:%s" % (p, ",".join(map(str, hs)))
                                                            for p, hs in sorted(same.items())))
    for b in bad[:20]:
        print("FAIL", b)
    return 1 if bad else 0


def identical_to_I(rundir, cl):
    """Per C1-C2 pattern, the finite heads whose SIMD-off text equals I's (step (5)'s `text
    is I there`, read off the artifacts, not assumed from h >= k)."""
    out = {}
    for card, pats, _a, _r, _l, _k in CARDS:
        if card not in ("C1", "C2"):
            continue
        for p in pats:
            ia = open(artifact(rundir, p, "I", "off"), "rb").read()
            out[p] = [h for h in GRID if open(artifact(rundir, p, "h%d" % h, "off"), "rb").read() == ia]
    return out


def cmd_run(args):
    rundir = args[0]
    os.makedirs(rundir, exist_ok=True)
    res = os.path.join(rundir, "results.tsv")
    with open(res, "w") as f:
        f.write("#card\tpattern\tarm\tregime\tlayer\tmedian_ns_per_B\tspread\n")
        for c in cells():
            try:
                out = run_cell(rundir, c, 1 << 20, True)
            except Exception as e:
                out = "void %s" % e
            f.write("\t".join(c) + "\t" + "\t".join(out.split(" ", 1)) + "\n")
            f.flush()
    same = identical_to_I(rundir, cells())
    json.dump(same, open(os.path.join(rundir, "same_as_I.json"), "w"))
    print("cards: results in %s" % res)


# ---- THE RULE (r45_reply rev 6 §3, R0-R5, steps (1)-(5)) -------------------------------------
def r1(heads, cells_read, void_cells, t, tI, same_as_I, f, top=GRID_TOP):
    """R1 over the FINITE heads `heads` (R0 already applied). cells_read: the C1-C2 cells with a
    reading; void_cells: the cells void twice; t[h][c], tI[c] the raw medians; same_as_I[h][c]
    true where H(h)'s text is I's in cell c. Returns (h*, label, recorded pick or None,
    detail)."""
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
            why = "on a measured tie of every finite head"
        elif E == [top]:
            why = "every shorter finite head measured slower beyond f"
        else:
            why = "on a measured tie of {%s}" % ", ".join(map(str, E))
        label = "h = grid top (%d, CHOSEN), %s" % (top, why)
    else:
        label = "MEASURED"
    detail = {"W": W, "E": E, "dominated_by": nd, "kept": kept}
    # (5) VOID: a C1-C2 cell void twice never helps a head
    if void_cells:
        return top, ("h = grid top (%d, CHOSEN): cell(s) %s void twice; the cells read picked H(%d)"
                     % (top, ", ".join(sorted(void_cells)), pick)), pick, detail
    return pick, label, None, detail


def read_results(path):
    rows = []
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        rows.append(f)
    return rows


def cmd_rule(args):
    """R0-R5 over a results.tsv (and its same_as_I.json beside it). --g2 FILE: R0's input, one
    defective head per line (a head whose answers G2 or the cards' gates failed)."""
    path = args[0]
    defective = set()
    if "--g2" in args:
        defective = {int(x) for x in open(args[args.index("--g2") + 1]).read().split()}
    rows = read_results(path)
    same = json.load(open(os.path.join(os.path.dirname(path), "same_as_I.json")))
    med = {}
    void = set()
    for card, pat, arm, regime, layer, v, *rest in rows:
        if v == "void":
            void.add((pat, regime, layer))
            continue
        med[(card, pat, arm, regime, layer)] = (float(v), float(rest[0]) if rest else 0.0)
    # the floor f: the largest |median ratio - 1| among the A/A cells over every regime and layer
    aa = []
    for r in REGIMES:
        for ly in ("off", "on"):
            a, b = med.get(("AA", "lit16", "aa", r, ly)), med.get(("AA", "lit16", "aa-twin", r, ly))
            if not a or not b:
                print("rule: the floor is not computable (A/A cell %s/%s missing): the night is VOID "
                      "(cover_cap.md §11.4 row 1)" % (r, ly))
                return 2
            aa.append(abs(a[0] / b[0] - 1))
    f = max(aa)
    heads = [h for h in GRID if h not in defective]
    ccells, tI, t = [], {}, {h: {} for h in heads}
    sa = {h: {} for h in heads}
    for card in ("C1", "C2"):
        for pat in next(c[1] for c in CARDS if c[0] == card):
            for r in REGIMES:
                for ly in ("off", "on"):
                    cid = "%s/%s/%s" % (pat, r, ly)
                    keys = [(card, pat, "I", r, ly)] + [(card, pat, "h%d" % h, r, ly) for h in heads]
                    if any(k not in med for k in keys) or any(
                            med[k][1] > 2 * f * med[k][0] for k in keys):    # missing or bimodal
                        void.add(cid)
                    else:
                        ccells.append(cid)
                        tI[cid] = med[keys[0]][0]
                        for h in heads:
                            t[h][cid] = med[(card, pat, "h%d" % h, r, ly)][0]
                    for h in heads:
                        sa[h][cid] = h in same.get(pat, [])
    vc = sorted(c for c in void if isinstance(c, str))
    hs, label, rec, det = r1(heads, ccells, vc, t, tI, sa, f)
    print("rule: f = %.4f (A/A, %d cells); R0 defective heads: %s" % (f, len(aa), sorted(defective) or "none"))
    print("rule: W = %s" % {h: round(w, 4) for h, w in det["W"].items()})
    print("rule: E = %s; dominated-by counts %s; kept %s" % (det["E"], det["dominated_by"], det["kept"]))
    print("rule: h* = %d, %s%s" % (hs, label, "" if rec is None else " (recorded pick %d)" % rec))
    # R2: every C1-C3 cell where I beats H(h*) beyond f (dial evidence; never changes h*)
    for (card, pat, arm, r, ly), (v, _s) in sorted(med.items()):
        if card in ("C1", "C2", "C3") and arm == "I":
            hv = med.get((card, pat, "h%d" % hs, r, ly))
            if hv and hv[0] / v > 1 + f:
                print("R2 dial evidence: %s %s %s/%s: H(%d) %.4f vs I %.4f" % (card, pat, r, ly, hs, hv[0], v))
    # R4: C1's near-miss column, H(h*) against C5 (the engine route)
    for pat in next(c[1] for c in CARDS if c[0] == "C1"):
        for ly in ("off", "on"):
            hv, ev = med.get(("C1", pat, "h%d" % hs, "near-miss", ly)), med.get(("C5", pat, "engine", "near-miss", "off"))
            if hv and ev and hv[0] / ev[0] > 1 + f:
                print("R4 near-miss trigger (r45_reply §4): %s/%s H(%d) %.4f vs engine %.4f" % (pat, ly, hs, hv[0], ev[0]))
    # R5: C3's cells, H(h*) against L and I (a loss is filed: the trigger to extend the grid)
    for (card, pat, arm, r, ly), (v, _s) in sorted(med.items()):
        if card == "C3" and arm == "h%d" % hs:
            for other in ("I", "h0"):
                ov = med.get(("C3", pat, other, r, ly))
                if ov and v / ov[0] > 1 + f:
                    print("R5 long-span loss: %s %s/%s H(%d) %.4f vs %s %.4f" % (pat, r, ly, hs, v, other, ov[0]))
    # R3: per class, the head that would win on that class's cells alone, beside E[D] (the
    # expected death depth under the miss-heavy subject's byte rate)
    for pat in next(c[1] for c in CARDS if c[0] == "C1") + next(c[1] for c in CARDS if c[0] == "C2"):
        mine = [c for c in ccells if c.startswith(pat + "/")]
        if not mine:
            continue
        hcls, _l, _r, _d = r1(heads, mine, [], t, tI, sa, f)
        print("R3 class %s: h* on its own cells %d; E[D] %.2f" % (pat, hcls, death_depth(pat)))
    return 0


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


# ---- the drills (r45_reply rev 6 §3 "Drills"), each with the result the design states ------
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
     64, "every shorter finite head measured slower beyond f"),
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
    ("(xiii) drill N, a NOT-WARM-only loss", {"f": 0.02, "cells": [("hd32", 32), ("nw32", 32)],
                                              "ratios": {8: [0.90, 1.20], 16: [0.99, 1.0], 24: [0.99, 1.0]}},
     64, "on a measured tie of {0, 1, 2, 4, 16, 24, 32, 64}"),
    ("(xiv) a regime's method missing", {"f": 0.02, "cells": [("hd32", 32), ("nw32", 32), ("nw24", 24)],
                                         "void": ["nw32", "nw24"],
                                         "ratios": {8: [0.90, 1.20, 1.0], 16: [0.99, 1.0, 1.0],
                                                    24: [0.99, 1.0, 1.0]}},
     64, "cell(s) nw24, nw32 void twice; the cells read picked H(8)"),
]


def cmd_selftest(_args):
    bad = 0
    for name, spec, want_h, want_label in DRILLS:
        h, label, rec, det = drill(spec)
        ok = h == want_h and want_label in label
        bad += not ok
        print("%s %-48s h* = %-3d %s" % ("ok  " if ok else "FAIL", name, h, label))
        if not ok:
            print("     want h* = %d, a label holding %r; E %s kept %s W %s" % (want_h, want_label, det["E"],
                                                                                det["kept"], det["W"]))
    print("selftest: %d drills, %d failed" % (len(DRILLS), bad))
    return 1 if bad else 0


# ---- the identity check (r45_reply §3 "The head lever and its identity check") -------------
def cmd_identity(args):
    """The lever at H on the FROZEN binary (pcrec-harness --harness=span-head=H) against the
    REBUILT build/pcrec (REBUILT env, default this tree's build/), byte for byte, both layers,
    over the card patterns, the census covers and the PATTERNS file's lines."""
    h = int(args[0])
    pats = [p[0] for p in PATTERNS.values()]
    pats += ["[0-9a-f]{32}", r"\d{32}", r"\b[0-9a-f]{32}\b", r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}",
             r"\w{32}\B", r"(?i)[0-9a-f]{40}"]
    if len(args) > 1:
        pats += [ln.rstrip("\n") for ln in open(args[1], encoding="latin-1") if ln.strip()]
    rebuilt = os.path.join(os.environ.get("REBUILT") or os.path.join(TREE, "build"), "pcrec")
    wf = [] if WIDTH_FLAG == "none" else [WIDTH_FLAG]
    diff = 0
    for p in sorted(set(pats)):
        for ly in LAYERS.values():
            base = ["-p", PREFIX, "--features", "all"] + wf + ly + ["-o", "-", "--pattern", p]
            a = subprocess.run([HARNESS, "--harness=span-head=%d" % h] + base, capture_output=True, timeout=600)
            b = subprocess.run([rebuilt] + base, capture_output=True, timeout=600)
            if a.returncode != b.returncode or a.stdout != b.stdout:
                diff += 1
                print("IDENTITY DIFFERS: %r %s" % (p, " ".join(ly) or "simd-off"))
    print("identity: head %d, %d patterns x %d layers, %d differ" % (h, len(set(pats)), len(LAYERS), diff))
    return 1 if diff else 0


def main():
    cmds = {"plan": cmd_plan, "dry": cmd_dry, "run": cmd_run, "rule": cmd_rule,
            "selftest": cmd_selftest, "identity": cmd_identity}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[sys.argv[1]](sys.argv[2:]) or 0


if __name__ == "__main__":
    sys.exit(main())
