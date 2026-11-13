# span_cards/slot/art.py — THE WHOLE-ARTIFACT ARMS (span_cards.md §2.3 `enter`, §3.2, §3.6 J1): their
# translation units, subjects and independent expectations. link.py calls render(a, rundir) for an arm of kind
# `enter` or `j1` and subject(a, rundir) for its table entry; localize(obj, sym) after compiling it.
#   python3 -I art.py check RUNDIR     every fixture's self-check and every subject's expectation, no compile
#
# AN ARM's TU is `<the artifact> <one wrapper>`: the artifact is build/pcrec's own output (`--features all`,
# census0's corpus flags, `-p rxa`, `-o -`: self-contained C), the wrapper ONE text per regime (WRAP_ALL: one
# find-all over the subject; WRAP_REC: the find-all over each LF-free record, J1's `short`). A find-all is the
# loop over `rxa_search(s, n, from, caps)`, restarting at the match end (one past an empty match). EVERY arm uses
# the prefix `rxa`, so an arm's and its twin's sources are byte-identical (link.py's cmp); after compiling,
# localize() makes every defined global but `<sym>_time`/`<sym>_gate` local (objcopy), so the launch links many
# artifacts with one prefix.
#
# J1 (§3.6): the arm's artifact is its pattern's with the PAIR declaration `<h>wa = 128, <h>wb = 128`
# (ofsskip.c ofs_pair_decl, `<h>` the site's handle prefix) substituted to the arm's width; the declaration must
# occur EXACTLY ONCE in the artifact, else the render REFUSES (the dry run fails naming the pattern).
#
# J5 (`enter`): THE FIXTURE RULE (enter/fixtures.tsv). For (kind, entry), a unit of census0's corpus
# (/var/tmp/.../s2b/j0/sweep.jsonl, census0.py's `units`: a window site or a window-stating FUNC part, arm RTE,
# rc 0) of that site_kind whose CHOSEN alternative (wr.alt: the entry the consumer is entered with) has that
# entry and >= 2 non-FULL verify-YES positions, so a FAIL candidate exists (the LAST verify position = the
# highest window offset that is not the stop); row-1-class units first (census0's card population); the window
# starts at the match start and the pattern needs >= 1 byte past it (so `die1` is a death in the consumer; kind 6
# REPORT is the exception: its window IS the match, a pass candidate is a match); python `re` gives the same
# answers; the shortest such pattern. A pair no unit reaches is reported by plan.py, never forced.
# THE SUBJECTS (1 MiB, 4,096 blocks of 256 bytes, seeded per (kind, entry)): filler from the fixture's alphabet;
# block i holds ONE candidate at 256 i + j_i (j_i seeded in [8, 96)): pre + window + die (pass; each position a
# seeded choice of the fixture's) or pre + window with its last verify position replaced by `fail` (+ die)
# (fail). Blocks 255, 511, ..., 4095 also hold a PLANT at offset 160: pre + the canonical window + live, a real
# match, the same in both subjects, the last after the last candidate (a required-byte pre-check that scans to
# the next plant sees every candidate). events = 4,096 candidates per call (pass), 0 (the fail base).
# THE EXPECTATION, INDEPENDENT of the artifact: python `re.finditer` over the subject's bytes (each record for
# `short`): count, the sum of the match starts and FNV-1a-64 over their 8 LE bytes (gen.c's fnv_pos), written to
# the arm's `expect` file as `count sum fnvhex`. The fixture's own self-check (refuses before any compile): the
# plant matches at its start, a die1 candidate does not, and the subjects' counts are the planted ones (+4,096 on
# kind 6's pass).
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "j1"))
import plan  # noqa: E402
import subjects as j1s  # noqa: E402

TREE = plan.TREE
PCREC = os.path.join(TREE, "build", "pcrec")
PREFIX = "rxa"
FLAGS = ["--features", "all"]          # census0's corpus compile flags (r33_sim/collect.py)
BLOCK, NBLK = 256, plan.LEN // 256
PLANT_EVERY, PLANT_AT = 256, 160
DECL = re.compile(r"\b(\w*)wa = 128, \1wb = 128\b")

FNV0, FNVP, M64 = 1469598103934665603, 1099511628211, (1 << 64) - 1

def fnv_pos(h, pos):
    for i in range(8):
        h = ((h ^ ((pos >> (8 * i)) & 0xff)) * FNVP) & M64
    return h

def unesc(s):
    out, i = bytearray(), 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            d = s[i + 1]
            if d == "x":
                out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
            out += {"n": b"\n", "t": b"\t", "\\": b"\\", "|": b"|"}[d]; i += 2; continue
        out += c.encode("latin-1"); i += 1
    return bytes(out)

# ---- fixtures and cells ---------------------------------------------------------------------------------------
class Fixture:
    def __init__(self, f):
        self.kind, self.entry, self.pattern, self.source = int(f[0]), f[1], f[2], f[3]
        self.window = [unesc(x) for x in f[4].split("|")]
        self.stop = int(f[5])
        self.pre, self.die, self.fail, self.live = unesc(f[6]), unesc(f[7]), unesc(f[8]), unesc(f[9])
        self.filler = unesc(f[10])
        offs = [o for o in range(len(self.window)) if o != self.stop]
        if not offs:
            raise SystemExit("art: fixture %d.%s: no verify position other than the stop" % (self.kind, self.entry))
        self.lastv = max(offs)
        self.rx = re.compile(self.pattern.encode("latin-1"))

def j1_patterns():
    """{id: (bench relpath, sha256)} from j1/patterns.tsv"""
    out = {}
    for ln in open(os.path.join(HERE, "j1", "patterns.tsv")):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        out[f[0]] = (f[1], f[2])
    return out

def bench_root():
    common = subprocess.run(["git", "-C", TREE, "rev-parse", "--git-common-dir"], capture_output=True, text=True,
                            check=True).stdout.strip()
    main = os.path.dirname(os.path.abspath(os.path.join(TREE, common)))
    return os.environ.get("PCREC_BENCH") or os.path.join(os.path.dirname(main), "pcrec-bench")

def j1_pattern_text(pid):
    rel, sha = j1_patterns()[pid]
    path = os.path.join(bench_root(), rel)
    b = open(path, "rb").read()
    got = hashlib.sha256(b).hexdigest()
    if got != sha:
        raise SystemExit("art: REFUSED: %s's sha-256 %s is not j1/patterns.tsv's %s (the bench's pattern moved)"
                         % (path, got, sha))
    return b.rstrip(b"\n").decode("latin-1")

def no_back(a):
    """kit-grid@4's step-back arms (Arm.back = t) are PLANNED, not yet rendered: span_runs_sheet.md §5.2 states the
    dimension t and its estimator, not how t enters the artifact (what is stepped back from, and the subject that
    makes the consumer enter t bytes early). Rendering the plain `enter` artifact for them would time the WRONG thing
    under the step-back key, so the dry run stops here until that is specified (K38-3 finding)"""
    if getattr(a, "back", None) is not None:
        raise SystemExit("art: REFUSED: %s: the step-back arm (t = %d) has no artifact specification yet "
                         "(span_runs_sheet.md §5.2 names t, not how it enters the artifact)" % (a.name, a.back))


def pattern_of(a):
    no_back(a)
    if a.kind == "enter":
        return Fixture(a.fixture).pattern
    return j1_pattern_text(a.fixture[0])

# ---- the TU -----------------------------------------------------------------------------------------------------
FA = """#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)
/* one find-all over s[0, n); positions reported as base + start; a give-up returns a count no gate can equal */
static inline __attribute__((always_inline)) uint64_t fa(const unsigned char *s, size_t n, size_t base,
                                                         uint64_t *sum, uint64_t *h, int g)
{
    ptrdiff_t caps[RXA_NCAPS][2];
    uint64_t k = 0;
    size_t from = 0;
    while (from <= n) {
        int r = rxa_search(s, n, from, caps);
        if (r == 0)
            break;
        if (r < 0)
            return (uint64_t)1 << 62;
        size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
        k++;
        if (g) {
            uint64_t p = base + st;
            *sum += p;
            for (int i = 0; i < 8; i++) { *h ^= (p >> (8 * i)) & 0xff; *h *= 1099511628211ull; }
        }
        from = en > st ? en : st + 1;
    }
    return k;
}
"""

WRAP_ALL = FA + """__attribute__((noinline)) uint64_t CAT(SYM, _time)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc)
{
    (void)c; (void)nc;
    return fa(s, n, 0, 0, 0, 0);
}
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)c; (void)nc;
    return fa(s, n, 0, sum, h, 1);
}
"""

# J1 short: the records are the subject's first NREC LF-free runs (exactly its records; the LF padding after them
# is never read), split ONCE per buffer (the first call on a buffer, ~NREC memchr calls, tens of us inside a
# >= 50 ms loop; every later call reuses it), so a call is the find-all over each record and nothing else
WRAP_REC = FA + """#define NREC %d
static const unsigned char *rec_s;
static size_t rec_n, rec_k;
static uint32_t rec_off[NREC][2];
static void rec_split(const unsigned char *s, size_t n)
{
    if (s == rec_s && n == rec_n)
        return;
    rec_k = 0;
    for (size_t p = 0; p < n && rec_k < NREC; ) {
        const unsigned char *e = memchr(s + p, '\\n', n - p);
        size_t q = e ? (size_t)(e - s) : n;
        if (q > p) { rec_off[rec_k][0] = (uint32_t)p; rec_off[rec_k][1] = (uint32_t)(q - p); rec_k++; }
        p = q + 1;
    }
    rec_s = s;
    rec_n = n;
}
__attribute__((noinline)) uint64_t CAT(SYM, _time)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc)
{
    (void)c; (void)nc;
    rec_split(s, n);
    uint64_t k = 0;
    for (size_t i = 0; i < rec_k; i++)
        k += fa(s + rec_off[i][0], rec_off[i][1], 0, 0, 0, 0);
    return k;
}
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)c; (void)nc;
    rec_split(s, n);
    uint64_t k = 0;
    for (size_t i = 0; i < rec_k; i++)
        k += fa(s + rec_off[i][0], rec_off[i][1], rec_off[i][0], sum, h, 1);
    return k;
}
""" % j1s.NREC

def _key(*parts):
    h = hashlib.sha256()
    for x in parts:
        h.update(hashlib.sha256(x if isinstance(x, bytes) else x.encode("latin-1")).digest())
    return h.hexdigest()[:16]

def artifact(pattern, rundir):
    """build/pcrec's artifact for the pattern, CACHED BY ITS INPUTS under RUNDIR/art/ (the pattern, the flags and
    build/pcrec's own bytes, r9 G1/HOUSE-9: a rebuilt compiler is a new artifact, never a reused one)"""
    d = os.path.join(rundir, "art")
    os.makedirs(d, exist_ok=True)
    c = os.path.join(d, "a_%s.c" % _key(pattern, " ".join(FLAGS + ["-p", PREFIX]), open(PCREC, "rb").read()))
    if not os.path.exists(c):
        r = subprocess.run([PCREC] + FLAGS + ["-p", PREFIX, "-o", "-", "--pattern", pattern], capture_output=True)
        if r.returncode:
            raise SystemExit("art: pcrec refused %r: %s" % (pattern, r.stderr.decode(errors="replace")[-600:]))
        open(c + ".tmp", "wb").write(r.stdout)
        os.replace(c + ".tmp", c)
    return open(c, encoding="latin-1").read()

def render(a, rundir):
    src = artifact(pattern_of(a), rundir)
    regime = "throughput"
    if a.kind == "j1":
        pid, _subj, regime, w = a.fixture
        n = len(DECL.findall(src))
        if n != 1:
            raise SystemExit("art: REFUSED: %s's artifact holds %d PAIR declarations `<h>wa = 128, <h>wb = 128`, "
                             "not exactly one (§3.6)" % (pid, n))
        src = DECL.sub(lambda m: "%swa = %d, %swb = %d" % (m.group(1), w, m.group(1), w), src)
    wrap = WRAP_REC if regime == "short" else WRAP_ALL
    return ("#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n/* ARTIFACT BEGIN */\n" + src
            + "\n/* ARTIFACT END */\n" + wrap)

def localize(obj, sym):
    r = subprocess.run(["objcopy", "--keep-global-symbol=%s_time" % sym, "--keep-global-symbol=%s_gate" % sym, obj],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("art: objcopy %s: %s" % (obj, r.stderr))

# ---- subjects and expectations -------------------------------------------------------------------------------
def expect_of(rx, buf, records=False):
    parts = j1s.records(buf) if records else [(0, buf)]
    k, s, h = 0, 0, FNV0
    for off, b in parts:
        for m in rx.finditer(b):
            p = off + m.start()
            k += 1
            s += p
            h = fnv_pos(h, p)
    return k, s, h

def enter_subjects(fx):
    """(pass bytes, fail bytes, plants)"""
    seed = 0xE7E40000 ^ (fx.kind << 8) ^ {"NONE": 1, "PARKED": 2, "RESEED": 3}[fx.entry]
    r = j1s.Rng(seed)
    fill = bytearray(fx.filler[r.below(len(fx.filler))] for _ in range(plan.LEN))
    ps, fs = bytearray(fill), bytearray(fill)
    W = len(fx.window)
    nplant = 0
    for i in range(NBLK):
        j = 8 + r.below(96 - 8)
        win = bytes(ch[r.below(len(ch))] for ch in fx.window)
        cand = fx.pre + win + fx.die
        bad = bytearray(cand)
        bad[len(fx.pre) + fx.lastv] = fx.fail[0]
        p = i * BLOCK + j
        ps[p:p + len(cand)] = cand
        fs[p:p + len(bad)] = bad
        if i % PLANT_EVERY == PLANT_EVERY - 1:
            pl = fx.pre + bytes(ch[0] for ch in fx.window) + fx.live
            q = i * BLOCK + PLANT_AT
            assert PLANT_AT + len(pl) <= BLOCK and j + len(cand) < PLANT_AT
            ps[q:q + len(pl)] = pl
            fs[q:q + len(pl)] = pl
            nplant += 1
    assert len(ps) == plan.LEN == len(fs) and W
    return bytes(ps), bytes(fs), nplant

def fixture_check(fx):
    """the fixture's own self-check: the plant is a match at its start, a die1 candidate is not, and the
    subjects' counts are the planted ones (+ every candidate on kind 6's pass)"""
    pl = fx.pre + bytes(ch[0] for ch in fx.window) + fx.live
    m = fx.rx.match(pl + fx.filler[:1], len(fx.pre))
    if not m:
        raise SystemExit("art: fixture %d.%s: the plant %r is not a match" % (fx.kind, fx.entry, pl))
    ps, fs, nplant = enter_subjects(fx)
    kp, kf = expect_of(fx.rx, ps)[0], expect_of(fx.rx, fs)[0]
    want_p = nplant + (NBLK if fx.kind == 6 else 0)
    if kp != want_p or kf != nplant:
        raise SystemExit("art: fixture %d.%s: python finds %d (pass) and %d (fail), the design plants %d and %d: "
                         "the candidates do not die where the fixture says" % (fx.kind, fx.entry, kp, kf, want_p, nplant))
    return kp, kf, nplant

def _write(path, data):
    if not os.path.exists(path) or open(path, "rb").read() != data:
        open(path + ".tmp", "wb").write(data)
        os.replace(path + ".tmp", path)

def _cstr(p):
    return '"%s"' % p.replace("\\", "\\\\").replace('"', '\\"')

def gen_key():
    """the subject generators' own key: this file, j1/subjects.py and the plan's LEN"""
    return _key(open(os.path.abspath(__file__), "rb").read(), open(j1s.__file__, "rb").read(), str(plan.LEN))

def subject(a, rundir):
    """the arm's (subj, expect) C string literals; files under RUNDIR/art/ (an arm and its twin share them),
    named by their INPUTS (the generators, the fixture row or the pattern's sha), so a changed input is a new
    file, never a reused one"""
    no_back(a)
    d = os.path.join(rundir, "art")
    os.makedirs(d, exist_ok=True)
    g = gen_key()
    if a.kind == "enter":
        fx = Fixture(a.fixture)
        which = "fail" if a.name.startswith("base.fail.") else "pass"
        stem = os.path.join(d, "enter.%d.%s.%s.%s" % (fx.kind, fx.entry, which, _key(g, "\t".join(a.fixture))))
        if not os.path.exists(stem + ".exp"):
            fixture_check(fx)
            ps, fs, _n = enter_subjects(fx)
            buf = ps if which == "pass" else fs
            _write(stem + ".bin", buf)
            _write(stem + ".exp", ("%d %d %016x\n" % expect_of(fx.rx, buf)).encode())
        return _cstr(stem + ".bin"), _cstr(stem + ".exp")
    pid, subj, regime, _w = a.fixture
    sb = os.path.join(d, "j1.%s.%s.%s.bin" % (subj, regime, g))
    if not os.path.exists(sb):
        buf = j1s.generate(subj, regime)
        if regime == "short" and len(j1s.records(buf)) != j1s.NREC:
            raise SystemExit("art: %s short subject holds %d records, not %d" % (subj, len(j1s.records(buf)), j1s.NREC))
        _write(sb, buf)
    ex = os.path.join(d, "j1.%s.%s.%s.%s.exp" % (pid, subj, regime, _key(g, j1_pattern_text(pid))))
    if not os.path.exists(ex):
        rx = re.compile(j1_pattern_text(pid).encode("latin-1"))
        _write(ex, ("%d %d %016x\n" % expect_of(rx, open(sb, "rb").read(), regime == "short")).encode())
    return _cstr(sb), _cstr(ex)

def main():
    rundir = sys.argv[2]
    if sys.argv[1] != "check":
        raise SystemExit("art.py: check RUNDIR")
    for k, e in sorted(plan.enter_fixtures()):
        f = plan.enter_fixtures()[(k, e)]
        if f[2] == "-":
            print("enter\t%d.%s\tunreached\t%s" % (k, e, f[-1]))
            continue
        fx = Fixture(f)
        kp, kf, n = fixture_check(fx)
        print("enter\t%d.%s\t%s\tpass %d fail %d (plants %d)\tlast verify offset %d" % (k, e, fx.pattern, kp, kf, n, fx.lastv))
    jobs, _r, _f, _u = plan.build()
    seen = set()
    for a in jobs.get("J1", []):
        if a.kind != "j1" or a.fixture[:3] in seen:
            continue
        seen.add(a.fixture[:3])
        _s, ex = subject(a, rundir)
        print("j1\t%s/%s/%s\texpect %s" % (a.fixture[0], a.fixture[1], a.fixture[2], open(ex.strip('"')).read().strip()))

if __name__ == "__main__":
    main()
