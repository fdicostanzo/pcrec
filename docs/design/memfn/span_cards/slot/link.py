# span_cards/slot/link.py — PER-LAUNCH LINKING AND PLACEMENT (span_cards.md §3.2, rev 1.3 READY-8), the cell
# renderer's wrappers and the cell-text check.
#   link.py JOB RUNDIR RUN_ID     renders every arm's translation unit, compiles it, links the job's seven
#                                 launch executables J<j>.L<l> with a seeded PAD before every arm and twin,
#                                 asserts the placement constraints on the LINKED executables (nm), the
#                                 text equality of arm and twin (sources by cmp, linked .text by objdump,
#                                 relocation targets masked), every cell TU's site-text hash against the
#                                 instance its KEY names, and records each timed function's address, its hot
#                                 loop (placement.tsv) and each cell's text facts (cell_text.tsv: the instance
#                                 and fold hashes est.py writes as the row's dep, r9 G5)
#   link.py ctl RUNDIR            the control executable `ctl` (the canonical walk at the three find_byte
#                                 lengths, one placement), built once per window, and its sha-256
# Cell texts come from tests/memfn/arm_fixtures.c's `--site-parts` (formhash's entry table: the ONE renderer,
# the texts mf_form_hash folds); the wrapper is ONE text per site shape (below). THE KEY NAMES THE TEXT (r9 G2):
# a row key's (form, cls) is read off its tokens (plan.key_form), the render uses it, and an Arm whose own form
# or class disagrees REFUSES (KEY-ARM MISMATCH). gcc 15.2 -O2 -march=x86-64 -mtune=generic, the declared target
# (§2.7). A PAD is a .text of P bytes, P = 16 x (1 + draw mod 255), so P is a multiple of 16 in [16, 4096); its
# draw is seeded by (run id, job, l, arm, d) (MEAS-1, READY-8).
import hashlib, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan  # noqa: E402
import vcls  # noqa: E402

TREE = plan.TREE
CC = ["gcc", "-std=gnu11", "-O2", "-march=x86-64", "-mtune=generic"]
# THE PHASES. §3.2 assumed 16-aligned functions (4 values mod 64, "at least 3 of 4"). gcc 15.2's generic
# tuning aligns tight loops to 32 (`.p2align 5`, -malign-tight-loops), so an arm object's .text is 32-aligned
# and its timed function can take only 64 / A values mod 64 (A = the object's .text alignment, read from the
# object, 32 today). The cells time the declared target's DEFAULT code (no alignment flag), so the
# constraint is read on the alignment the code has: in every launch arm and twin differ mod 64, and over the
# 7 launches each arm takes at least min(3, 64 / A) values (both of the two at A = 32).
MAXDRAW = 64                       # the bounded re-draw per (launch, arm) (READY-5): UNMEASURED DEFAULT (D149)
PAD_UNITS, PAD_STEP = 255, 16      # P = PAD_STEP x (1 + draw mod PAD_UNITS): UNMEASURED DEFAULT (D149)

def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise SystemExit("link: %s: rc %d\n%s" % (" ".join(cmd[:4]), r.returncode, (r.stderr or r.stdout)[-1500:]))
    return r.stdout

FX_INPUTS = [os.path.join(TREE, *p) for p in (("tests", "memfn", "arm_fixtures.c"), ("build", "libpcrec.a"),
                                               ("memfn", "include", "memfn.h"), ("memfn", "src", "kit.h"))]

def sha_files(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(hashlib.sha256(open(p, "rb").read()).digest())
    return h.hexdigest()

def fx_path(rundir):
    """the fixture binary, CACHED BY ITS INPUTS (r9 G1/HOUSE-9): RUNDIR/fx.<sha of arm_fixtures.c, libpcrec.a
    and the two headers>, so a rebuilt libpcrec.a is a new fx, never a reused one"""
    fx = os.path.join(rundir, "fx." + sha_files(FX_INPUTS)[:16])
    if not os.path.exists(fx):
        sh(["gcc", "-std=gnu11", "-O1", "-I" + os.path.join(TREE, "memfn", "include"),
            FX_INPUTS[0], FX_INPUTS[1], "-o", fx + ".tmp"])
        os.replace(fx + ".tmp", fx)
    return fx

def facts(fx, form, cls):
    out = sh([fx, "--facts", form] + ([cls] if cls else []))
    return dict(ln.split("\t", 1) for ln in out.splitlines() if "\t" in ln)

def parts(fx, form, cls):
    out = sh([fx, "--site-parts", form] + ([cls] if cls else []))
    f, _, b = out.partition("\f\n")
    return f, b

def form_hash(fx, form, cls):
    """(the instance's hash, the form's FOLD hash mf_form_hash(form)): cls None names the canonical instance"""
    inst = fold = None
    for ln in sh([fx, "--hash"]).splitlines():
        p = ln.split("\t")
        if p[0] == "FORM" and p[1] == form and p[2] == "0":
            fold = p[3]
        if p[0] == "FORMCLS" and p[1] == form and p[3] == "0" and (p[2] == cls or (cls is None and p[-1] == "1")):
            inst = p[4]
    if not inst or not fold:
        raise SystemExit("link: no form hash for %s %s" % (form, cls))
    return inst, fold

def cbytes(bs):
    return ", ".join(str(b) for b in bs)

def hexbytes(s):
    return [int(x, 16) for x in s.split()] if s and s != "-" else []

# ---- the wrappers: ONE text per site shape ----------------------------------------------------------------
# SYM is the arm's symbol stem (-DSYM=a<k>), so an arm's and its twin's sources are byte-identical.
WRAP_FIND = """#include <stddef.h>
#include <stdint.h>
#include <string.h>
#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)
%(table)s
/* SITE FILE BEGIN */
%(file)s
/* SITE FILE END */
static inline __attribute__((always_inline)) int step(const unsigned char *subject, size_t n, size_t *io)
{
    size_t pos = *io;
/* SITE BODY BEGIN */
%(body)s
/* SITE BODY END */
    *io = pos;
    return pos < n;
}
__attribute__((noinline)) uint64_t CAT(SYM, _time)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc)
{
    (void)c; (void)nc;
    uint64_t k = 0;
    for (size_t p = 0; p < n && step(s, n, &p); p++) k++;
    return k;
}
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)c; (void)nc;
    uint64_t k = 0;
    for (size_t p = 0; p < n && step(s, n, &p); p++) {
        k++;
        *sum += p;
        for (int i = 0; i < 8; i++) { *h ^= (p >> (8 * i)) & 0xff; *h *= 1099511628211ull; }
    }
    return k;
}
"""

WRAP_CMP = """#include <stddef.h>
#include <stdint.h>
#include <string.h>
#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)
/* SITE FILE BEGIN */
%(file)s
/* SITE FILE END */
static inline __attribute__((always_inline)) int test(const unsigned char *subject, size_t pos)
{
    return
/* SITE BODY BEGIN */
%(body)s
/* SITE BODY END */
    ;
}
__attribute__((noinline)) uint64_t CAT(SYM, _time)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc)
{
    (void)n;
    uint64_t k = 0;
    for (size_t i = 0; i < nc; i++) k += test(s, c[i]) != 0;
    return k;
}
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)n;
    uint64_t k = 0;
    for (size_t i = 0; i < nc; i++)
        if (test(s, c[i])) {
            k++;
            *sum += i;
            for (int j = 0; j < 8; j++) { *h ^= (i >> (8 * j)) & 0xff; *h *= 1099511628211ull; }
        }
    return k;
}
"""

# the null verify base (the driver's: the candidate loop with the compare replaced by a constant; the
# candidate's first byte is still loaded, so the loop reads what the compare's loop reads first)
WRAP_NULL = """#include <stddef.h>
#include <stdint.h>
#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)
__attribute__((noinline)) uint64_t CAT(SYM, _time)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc)
{
    (void)n;
    uint64_t k = 0;
    for (size_t i = 0; i < nc; i++) { unsigned char b = s[c[i]]; __asm__ volatile("" : : "r"(b)); k++; }
    return k;
}
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)sum; (void)h;
    return CAT(SYM, _time)(s, n, c, nc);
}
"""

def render(fx, a):
    """(source text, (form, cls) or None, facts): (form, cls) the KEY's (r9 G2), the Arm's own must agree"""
    if a.kind == "verify" and a.form == "null":
        q = a.name.split(".")
        if len(q) != 3 or q[:2] != ["base", "null"] or not a.of or a.of[1] != q[2]:
            raise SystemExit("link: KEY-ARM MISMATCH %s: a null base names its class, the Arm's is %s" % (a.name, a.of))
        return WRAP_NULL, None, facts(fx, a.of[0], a.of[1])
    if a.kind in ("enter", "j1"):              # whole artifacts (art.py): rundir is fx's directory
        import art
        return art.render(a, os.path.dirname(fx)), None, {}
    kf = plan.key_form(a.name)
    if kf is None or kf != ("walk" if a.kind == "ctl" else a.form, a.cls if a.kind == "verify" else None):
        raise SystemExit("link: KEY-ARM MISMATCH %s: the key names %s, the Arm %s %s" % (a.name, kf, a.form, a.cls))
    form, cls = kf
    f = facts(fx, form, cls)
    fi, bo = parts(fx, form, cls)
    if f["shape"] == "cmp-expr":
        return WRAP_CMP % {"file": fi, "body": bo}, (form, cls), f
    table = ""
    if f.get("table", "-") != "-":
        m = set(hexbytes(f["table_members"]))
        table = "static const unsigned char %s[256] = { %s };" % (f["table"], cbytes(1 if i in m else 0 for i in range(256)))
    return WRAP_FIND % {"table": table, "file": fi, "body": bo}, (form, cls), f

def span(src, what):
    m = re.search(r"/\* SITE %s BEGIN \*/\n(.*?)/\* SITE %s END \*/" % (what, what), src, re.S)
    return m.group(1) if m else ""

LANDING = {None: "LD_MISS", "periodic": "LD_PERIODIC", "random": "LD_RANDOM"}

def bitmap(bs):
    m = [0] * 32
    for b in bs:
        m[b >> 3] |= 1 << (b & 7)
    return m

def arm_entry(a, sym, f, rundir):
    """the arm's slot.h table entry; a verify arm's (and its null base's) run, mask or members are the facts of
    the instance it names (the base: its class's, r9 G7), never copied bytes"""
    kind = {"find": "K_FIND", "ctl": "K_FIND", "verify": "K_CMP", "enter": "K_ART", "j1": "K_ART"}[a.kind]
    if a.kind == "verify" and a.form == "null":
        kind = "K_NULL"
    if a.landing not in LANDING:
        raise SystemExit("link: %s: unknown landing %r (one of %s)" % (a.name, a.landing, sorted(k for k in LANDING if k)))
    if a.kind in ("find", "ctl") and (a.landing is None) != (a.gap is None):
        raise SystemExit("link: %s: a landing without a gap, or a gap without a landing" % a.name)
    lens = ", ".join(str(x) for x in a.lengths)
    hit = hexbytes(f.get("members", "-")) if a.kind in ("find", "ctl") else []
    member = [0] * 32
    run, mask, L = [0] * 32, [0] * 32, 0
    if a.kind == "verify":
        if f.get("L", "-") != "-":
            L = int(f["L"])
            run[:L] = hexbytes(f["run"])
            mask[:L] = hexbytes(f["mask"])
        else:
            member = bitmap(hexbytes(f["members"]))
    subj = expect = "NULL"
    if a.kind in ("enter", "j1"):
        import art
        subj, expect = art.subject(a, rundir)
    return ("    { \"%s\", %s, %s_time, %s_gate, %d, { %s }, %s, %d, %d, { %s }, { %s }, %d, { %s }, { %s }, %d, %s, %s },"
            % (a.name, kind, sym, sym, len(a.lengths), lens, LANDING[a.landing], 1 if a.split == "alt" else 0,
               a.gap or 0, cbytes(hit) or "0", cbytes(member), L, cbytes(run), cbytes(mask),
               50 if a.pas == "p50" else 0, subj, expect))

def seed_pad(run_id, job, l, arm, d):
    h = hashlib.sha256(("%s|%s|%d|%s|%d" % (run_id, job, l, arm, d)).encode()).digest()
    return PAD_STEP * (1 + int.from_bytes(h[:8], "little") % PAD_UNITS)

def compile_tu(src, path, sym):
    open(path, "w").write(src)
    obj = path[:-2] + ".o"
    sh(CC + ["-c", "-DSYM=" + sym, "-DCAND_STRIDE=%du" % plan.CAND_STRIDE, "-DPOOL_BYTES=%du" % plan.POOL_BYTES,
             "-I" + HERE, path, "-o", obj])
    return obj

def find_members(fx):
    """the union of every find form's members, read from the forms' facts (gen.c's miss text avoids them)"""
    ms = set()
    for form in sorted({a.form for js in plan.build()[0].values() for a in js if a.kind in ("find", "ctl")} | {"walk"}):
        ms |= set(hexbytes(facts(fx, form, None)["members"]))
    return bitmap(ms)

def shape_tag(a, f):
    """r9 EMIT-3: a verify class split by lowering shape (vcls.out) is priced by its MAJORITY shape: the
    instance's shape must be it (else REFUSE), and with no majority shape the row is a lower bound"""
    if a.kind != "verify" or a.form == "null" or f.get("members", "-") == "-":
        return "-"
    maj = plan.shape_majority(a.form, a.cls)
    if maj == "":
        return "-"
    if maj is None:
        return "lower-bound"
    got = vcls.shape(hexbytes(f["members"]))
    if got != maj:
        raise SystemExit("link: EMIT-3: %s's instance %s.%s has lowering shape %s, its class's majority is %s"
                         % (a.name, a.form, a.cls, got, maj))
    return "-"

def pad_obj(d, P, k):
    s = os.path.join(d, "pad%d.s" % k)
    open(s, "w").write("\t.text\n\t.globl pad%d\npad%d:\n\t.skip %d, 0xcc\n" % (k, k, P))
    o = s[:-2] + ".o"
    sh(["gcc", "-c", s, "-o", o])
    return o

def nm_addrs(exe):
    a = {}
    for ln in sh(["nm", exe]).splitlines():
        p = ln.split()
        if len(p) == 3 and p[2].endswith("_time"):
            a[p[2][:-5]] = int(p[0], 16)
    return a

def fn_text(exe, sym):
    out = sh(["objdump", "-d", "--no-show-raw-insn", "--disassemble=" + sym + "_time", exe])
    ins, start = [], None
    for ln in out.splitlines():
        m = re.match(r"\s+([0-9a-f]+):\s+(.*)$", ln)
        if not m:
            continue
        addr = int(m.group(1), 16)
        start = addr if start is None else start
        t = re.sub(r"\s*#.*$", "", m.group(2))
        t = re.sub(r"<[^>]*>", "<>", t)
        t = re.sub(r"-?0x[0-9a-f]+(?=\(%rip\))", "D", t)  # rip-relative displacements (relocations)
        t = re.sub(r"\b[0-9a-f]{4,}\b", "T", t)          # absolute branch and call targets
        ins.append((addr, t, m.group(2)))
    return start, ins

def hot_loop(ins):
    best = None
    for addr, _t, raw in ins:
        m = re.match(r"j\w+\s+([0-9a-f]+)", raw)
        if m and int(m.group(1), 16) < addr:
            tgt = int(m.group(1), 16)
            best = tgt if best is None else min(best, tgt)
    return best

def build_objs(job, rundir, arms):
    fx = fx_path(rundir)
    d = os.path.join(rundir, job, "obj")
    os.makedirs(d, exist_ok=True)
    common = []
    for c in ("drv", "gen"):
        common.append(compile_tu(open(os.path.join(HERE, c + ".c")).read(), os.path.join(d, c + ".c"), "x"))
    objs, checks, hashes, ctext = [], [], {}, []
    for k, a in enumerate(arms):
        src, fc, f = render(fx, a)
        sym = "a%d" % k
        o = compile_tu(src, os.path.join(d, "arm%d.c" % k), sym)
        if a.kind in ("enter", "j1"):             # whole artifacts share one prefix: keep only SYM's two globals
            import art
            art.localize(o, sym)
        objs.append((a, sym, o, f, src))
        if fc:
            got = sh([fx, "--hash-text", "-"], input=span(src, "FILE") + span(src, "BODY")).strip()
            want, fold = hashes.setdefault(fc, form_hash(fx, fc[0], fc[1]))
            checks.append((a.name, fc, got, want))
            ctext.append([a.name, fc[0], fc[1] or "-", got, fold, shape_tag(a, f)])
    bad = [c for c in checks if c[2] != c[3]]
    for c in bad:
        print("CELL-TEXT MISMATCH %s: site text %s, the hash of the instance its key names (%s %s) %s"
              % (c[0], c[2], c[1][0], c[1][1] or "-", c[3]))
    if bad:
        raise SystemExit(3)
    print("cell-text: %d cell TUs, every site-text hash equals the hash of the instance its KEY names" % len(checks))
    open(os.path.join(rundir, job, "cell_text.tsv"), "w").write(
        "#arm\tform\tcls\tinstance_hash\tfold_hash\ttags\n" + "".join("\t".join(r) + "\n" for r in ctext))
    # arm vs twin: the sources byte-identical (cmp)
    by = {a.name: src for a, _s, _o, _f, src in objs}
    for n, src in by.items():
        if n.endswith("#b") and by.get(n[:-2]) != src:
            raise SystemExit("link: %s's source differs from its arm's" % n)
    tab = os.path.join(d, "tab.c")
    open(tab, "w").write('#include "slot.h"\n' + "".join(
        "uint64_t %s_time(const unsigned char *, size_t, const uint32_t *, size_t);\n"
        "uint64_t %s_gate(const unsigned char *, size_t, const uint32_t *, size_t, uint64_t *, uint64_t *);\n"
        % (s, s) for _a, s, _o, _f, _src in objs)
        + "const arm slot_arms[] = {\n" + "\n".join(arm_entry(a, s, f, rundir) for a, s, _o, f, _src in objs)
        + "\n};\nconst int slot_narms = %d;\n" % len(objs)
        + "const unsigned char slot_find_members[32] = { %s };\n" % cbytes(find_members(fx)))
    common.append(compile_tu(open(tab).read(), tab, "x"))
    return common, objs

def link_launch(job, rundir, run_id, l, common, objs, d):
    """d: the draw index per arm name (0 if absent)"""
    ld = os.path.join(rundir, job, "L%d" % l)
    os.makedirs(ld, exist_ok=True)
    cmd = []
    for k, (a, _s, o, _f, _src) in enumerate(objs):
        cmd += [pad_obj(ld, seed_pad(run_id, job, l, a.name, d.get(a.name, 0)), k), o]
    exe = os.path.join(ld, "%s.L%d" % (job, l))
    sh(["gcc", "-o", exe] + common + cmd)
    return exe

def text_align(obj):
    for ln in sh(["readelf", "-SW", obj]).splitlines():
        p = ln.replace("[ ", "[").split()
        if len(p) > 2 and p[1] == ".text" and p[2] == "PROGBITS":
            return int(p[-1])
    return 16

def link_job(job, rundir, run_id):
    """THE DRAW (rev 1.3 READY-8 as built): each arm's and twin's pad is drawn from (run id, job, l, arm, d), d
    its OWN draw index. An object's address depends only on the objects linked before it, so the per-launch
    constraint is repaired in link order, twin by twin (re-drawing the failing twin's pad), and a fixed pair
    stays fixed. The cross-launch constraint re-draws the failing arm's own pad in the latest launch first
    (7, 6, ..., 1), then repairs that launch's later pairs again. Every (launch, arm) is bounded at MAXDRAW
    draws; exhausting a bound REFUSES naming the launch, the arm and the constraint."""
    jobs, _rows, _floor, _un = plan.build()
    arms = [a for a in jobs[job] if a.kind != "ctl"]   # the control is its own executable (link_ctl)
    common, objs = build_objs(job, rundir, arms)
    names = {a.name: s for a, s, _o, _f, _src in objs}
    order = [a.name for a, _s, _o, _f, _src in objs]
    draws = {l: {} for l in range(1, 8)}
    exes, addrs = {}, {}
    # phases a function can take mod 64: 64 / A; an object aligned to 64 (gcc aligns some loops so) has ONE,
    # its phase is the code's own, and neither constraint can apply to it (recorded, never re-drawn)
    need = {s: min(3, 64 // max(16, text_align(o))) for _a, s, o, _f, _src in objs}
    def bump(l, name, why):
        draws[l][name] = draws[l].get(name, 0) + 1
        if draws[l][name] >= MAXDRAW:
            raise SystemExit("link: REFUSED: %s launch %d arm %s: %d draws, %s still fails"
                             % (job, l, name, MAXDRAW, why))
    def fix_launch(l):
        while True:
            exes[l] = link_launch(job, rundir, run_id, l, common, objs, draws[l])
            addrs[l] = nm_addrs(exes[l])
            bad = next((n for n in order if n.endswith("#b") and need[names[n]] > 1
                        and addrs[l][names[n]] % 64 == addrs[l][names[n[:-2]]] % 64), None)
            if not bad:
                return
            bump(l, bad, "the per-launch constraint (arm and twin differ mod 64)")
    for l in range(1, 8):
        fix_launch(l)
    while True:
        bad = next((n for n in order if len({addrs[l][names[n]] % 64 for l in range(1, 8)}) < need[names[n]]), None)
        if not bad:
            break
        l = max(range(1, 8), key=lambda x: (draws[x].get(bad, 0) < MAXDRAW - 1, x))
        bump(l, bad, "the cross-launch constraint (min(3, 64 / A) values mod 64 over the 7 launches)")
        fix_launch(l)
    # text equality of arm and twin on the linked .text, and the hot loop, recorded
    rec = []
    for l in range(1, 8):
        for n, s in names.items():
            st, ins = fn_text(exes[l], s)
            if n.endswith("#b"):
                _st, ins0 = fn_text(exes[l], names[n[:-2]])
                if [t for _a, t, _r in ins] != [t for _a, t, _r in ins0]:
                    raise SystemExit("link: %s launch %d: the linked .text of %s differs from its arm's" % (job, l, n))
            hl = hot_loop(ins)
            rec.append("%s\tL%d\t%s\t%x\t%d\t%s\t%d" % (job, l, n, st, st % 64, "%x" % hl if hl else "-",
                                                         draws[l].get(n, 0)))
    open(os.path.join(rundir, job, "placement.tsv"), "w").write(
        "#job\tlaunch\tarm\taddr\tmod64\thot_loop\tdraws\n" + "\n".join(rec) + "\n")
    print("placement: %s: 7 launches linked (draws %s), arm/twin differ mod 64 in every launch where A < 64, every arm takes "
          "min(3, 64/A) values mod 64 (phases %s); linked .text equal arm vs twin"
          % (job, ",".join(str(sum(draws[l].values())) for l in range(1, 8)),
             ",".join(sorted({str(v) for v in need.values()}))))
    return exes

def ctl_inputs(rundir):
    """the control's inputs: the fixture binary's key (the walk's text) and the driver's and linker's sources"""
    return sha_files(FX_INPUTS + [os.path.join(HERE, x) for x in ("drv.c", "gen.c", "slot.h", "link.py", "plan.py")])

def link_ctl(rundir):
    """the window's FIXED control executable, built once per RUNDIR; its inputs' sha is kept beside it and a
    later call whose inputs differ REFUSES (a window times one control; new inputs need a new RUNDIR)"""
    d = os.path.join(rundir, "ctl")
    exe = os.path.join(d, "ctl")
    key = ctl_inputs(rundir)
    kp = os.path.join(d, "inputs.sha256")
    if not os.path.exists(exe):
        os.makedirs(d, exist_ok=True)
        common, objs = build_objs("ctl", rundir, [plan.Arm("ctl", "ctl", "ctl", "walk", lengths=plan.LENGTHS)])
        shutil.move(link_launch("ctl", rundir, "ctl", 1, common, objs, {}), exe)
        open(os.path.join(rundir, "ctl.sha256"), "w").write(hashlib.sha256(open(exe, "rb").read()).hexdigest() + "\n")
        open(kp, "w").write(key + "\n")
    elif not os.path.exists(kp) or open(kp).read().strip() != key:
        raise SystemExit("link: REFUSED: %s was built from other inputs than today's (the fixture binary, the "
                         "driver or the linker moved): a window times ONE control; use a new RUNDIR" % exe)
    return exe

if __name__ == "__main__":
    if sys.argv[1] == "ctl":
        print(link_ctl(sys.argv[2]))
    else:
        link_job(sys.argv[1], sys.argv[2], sys.argv[3])
