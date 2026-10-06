"""common.py -- shared plumbing for the [ARTREV] harness (paths, meta, ledger,
the SIMD/flag rejection, the ONE compile line, the gates).  Python 3.9-clean."""
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_STUDIES = os.path.dirname(HERE)


def repo_root():
    """The main checkout's root (the worktree's git common dir's parent)."""
    r = subprocess.run(["git", "-C", HERE, "rev-parse", "--git-common-dir"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        g = os.path.abspath(os.path.join(HERE, r.stdout.strip())) if not os.path.isabs(r.stdout.strip()) \
            else r.stdout.strip()
        return os.path.dirname(g)
    return os.path.dirname(REPO_STUDIES)


def tree_root():
    """The checkout this file lives in (worktree or main): scratch goes under it."""
    return os.path.dirname(REPO_STUDIES)


def art_root():
    return os.environ.get("ARTREV_ROOT") or os.path.join(tree_root(), "build-artrev")


def art_dir(name):
    return os.path.join(art_root(), name)


def die(msg, code=2):
    sys.stderr.write("artrev: %s\n" % msg)
    sys.exit(code)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def sha256_text(t):
    return hashlib.sha256(t.encode("utf-8", "surrogateescape")).hexdigest()


def run(cmd, **kw):
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    return subprocess.run(cmd, **kw)


# ------------------------------------------------------------------ meta
def load_meta(name):
    p = os.path.join(art_dir(name), "meta.json")
    if not os.path.exists(p):
        die("no artifact %r under %s (run `artrev.py gen` first)" % (name, art_root()))
    with open(p) as f:
        return json.load(f)


def save_meta(name, meta):
    with open(os.path.join(art_dir(name), "meta.json"), "w") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
        f.write("\n")


# ---------------------------------------------- the ONE compile line (fixed)
# The bench compiles `$CC -O2 -fPIC -shared shim.c` with the artifact #included
# (pcrec-bench/testees/pcrec/adapter.py "COMPILE COST", shim.c header).  Here
# the same: `$CC -O2 -fPIC` over shim.c (which #includes the artifact), one
# command line for EVERY arm; --san only ADDS sanitizer flags and is never used
# for timing.  Nothing a patch carries can add to it.
BASE_FLAGS = ["-O2", "-fPIC"]
SAN_FLAGS = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-g"]


def default_cc():
    env = os.environ.get("ARTREV_CC") or os.environ.get("CC")
    if env:
        return env
    if shutil.which("gcc-16"):
        return "gcc-16"
    return "gcc"


def cc_version(cc):
    r = run([cc, "--version"])
    return (r.stdout.splitlines() or ["?"])[0]


def check_cc_is_gcc(cc):
    v = cc_version(cc)
    if "clang" in v.lower() or "apple" in v.lower():
        die("compiler %r is %s -- not gcc.  ARTREV compiles with gcc only "
            "(set ARTREV_CC=gcc-16 on the Mac)" % (cc, v))
    return v


def arm_compile_cmd(meta, armdir, outobj_exe, san=False, extra_srcs=(), main_src=None, cc=None):
    """The full command compiling one arm's shim TU + a driver main into an exe.
    Returns argv.  The shim TU is compiled with the fixed flags."""
    cc = cc or os.environ.get("ARTREV_REMOTE_CC") or meta["cc"]
    flags = BASE_FLAGS + (SAN_FLAGS if san else [])
    cmd = [cc] + flags + ["-I" + armdir, "-DARTREV_PFX=%s" % meta["prefix"],
                          "-DARTREV_PFXU=%s" % meta["prefix"].upper(),
                          os.path.join(HERE, "shim.c")]
    if main_src:
        cmd.append(main_src)
    cmd += list(extra_srcs) + ["-o", outobj_exe]
    return cmd


def compile_arm(meta, armdir, kind, san=False):
    """Build `kind` in {id, bench} for the arm; returns exe path (cached by
    mtime of artifact.c, shim.c and the driver)."""
    drv = {"id": "driver_id.c", "bench": "bench_t.c"}[kind]
    bdir = os.path.join(armdir, "build")
    os.makedirs(bdir, exist_ok=True)
    exe = os.path.join(bdir, "%s%s" % (kind, "_san" if san else ""))
    srcs = [os.path.join(armdir, "artifact.c"), os.path.join(armdir, "artifact.h"),
            os.path.join(HERE, "shim.c"), os.path.join(HERE, drv)]
    if os.path.exists(exe) and os.path.getmtime(exe) >= max(os.path.getmtime(s) for s in srcs):
        return exe
    cmd = arm_compile_cmd(meta, armdir, exe, san=san, main_src=os.path.join(HERE, drv))
    r = run(cmd, env=dict(os.environ, TMPDIR=os.environ.get("TMPDIR", "/tmp")))
    if r.returncode != 0:
        die("compile failed for %s:\n  %s\n%s" % (armdir, " ".join(cmd), (r.stderr or "")[-1500:]))
    return exe


# ------------------------------------------ SIMD / flag rejection (charter 3.1)
_BANNED = [
    (r'#\s*include\s*[<"][^>"]*(?:intrin|immintrin|arm_neon|arm_sve|arm_acle|arm_fp16|arm_bf16|'
     r'wasm_simd|altivec|riscv_vector|vecintrin|simde)[^>"]*[>"]', "intrinsics header"),
    (r'__builtin_ia32_', "__builtin_ia32_*"),
    (r'__builtin_neon', "__builtin_neon*"),
    (r'__builtin_(?:shuffle|shufflevector|convertvector|vec_)', "vector builtin"),
    (r'__builtin_(?:aarch64|arm)_', "target builtin"),
    (r'\bvector_size\b', "vector_size"),
    (r'\bext_vector_type\b', "ext_vector_type"),
    (r'#\s*pragma\s+(?:GCC|clang)\s+(?:optimize|target|diagnostic\s+ignored\s+"-Wvector)', "#pragma GCC optimize/target"),
    (r'#\s*pragma\s+(?:GCC\s+ivdep|omp\b|simd\b|clang\s+loop\s+vectorize)', "vectorization pragma"),
    (r'__attribute__\s*\(\(.*?\b_{0,2}(?:optimize|target|target_clones|simd|vector_size|ext_vector_type)_{0,2}\b',
     "__attribute__((optimize/target/...))"),
    (r'\b__m(?:64|128|256|512)[a-z]*\b', "x86 vector type"),
    (r'\b_mm\d*_[a-z0-9_]+\s*\(', "_mm intrinsic call"),
    (r'\b(?:u?int|float|poly)\d+x\d+(?:x\d+)?_t\b', "NEON vector type"),
    (r'\bv(?:ld|st)[1-4]q?_[a-z0-9]+\s*\(', "NEON load/store intrinsic"),
]
_BANNED_RE = [(re.compile(p), why) for p, why in _BANNED]


def banned_in(lines):
    """[(lineno_in_list, why, text)] for every line a rule hits."""
    hits = []
    for i, ln in enumerate(lines):
        for rx, why in _BANNED_RE:
            if rx.search(ln):
                hits.append((i, why, ln.strip()))
                break
    return hits


def added_lines(orig_text, twin_text):
    out = []
    for ln in difflib.unified_diff(orig_text.splitlines(), twin_text.splitlines(), lineterm="", n=0):
        if ln.startswith("+") and not ln.startswith("+++"):
            out.append(ln[1:])
    return out


def reject_check(orig_text, twin_text):
    """Return list of (why, text) the twin adds that the charter forbids."""
    return [(why, t) for _, why, t in banned_in(added_lines(orig_text, twin_text))]


# ---------------------------------------------------------------- ledger
LEDGER_COLS = ["ts", "kind", "arm", "rev", "counted", "status", "sha", "detail"]
MAX_LEADS, MAX_REVS, MAX_TIMINGS = 6, 4, 3


def ledger_path(name):
    return os.path.join(art_dir(name), "iterations.tsv")


def ledger_rows(name):
    p = ledger_path(name)
    if not os.path.exists(p):
        return []
    rows = []
    with open(p) as f:
        for ln in f:
            if ln.startswith("#") or ln.startswith("ts\t") or not ln.strip():
                continue
            parts = ln.rstrip("\n").split("\t")
            parts += [""] * (len(LEDGER_COLS) - len(parts))
            rows.append(dict(zip(LEDGER_COLS, parts)))
    return rows


def ledger_append(name, kind, arm, rev, counted, status, sha="", detail=""):
    p = ledger_path(name)
    new = not os.path.exists(p)
    with open(p, "a") as f:
        if new:
            f.write("# [ARTREV] per-artifact iteration ledger (charter 3.1): one row per twin\n"
                    "# revision and per timing run, failures included.  counted=1 rows count toward\n"
                    "# the bounds (<=%d leads, <=%d revisions/lead, <=%d timing runs/revision).\n"
                    "# Never edit by hand: a hand-edited ledger voids the bound.\n" %
                    (MAX_LEADS, MAX_REVS, MAX_TIMINGS))
            f.write("\t".join(LEDGER_COLS) + "\n")
        f.write("\t".join([time.strftime("%Y-%m-%dT%H:%M:%S"), kind, arm, str(rev), str(int(counted)),
                           status, sha, detail.replace("\t", " ").replace("\n", " ")]) + "\n")


def counted_leads(rows):
    seen = []
    for r in rows:
        if r["kind"] == "twin" and r["counted"] == "1" and r["arm"] not in seen:
            seen.append(r["arm"])
    return seen


def revs_of(rows, arm):
    return len([r for r in rows if r["kind"] == "twin" and r["arm"] == arm])


def timings_of(rows, arm, rev):
    return len([r for r in rows if r["kind"] == "time" and r["arm"] == arm and r["rev"] == str(rev)])


def check_twin_bound(name, arm, counted):
    rows = ledger_rows(name)
    if not counted:
        return
    leads = counted_leads(rows)
    if arm not in leads and len(leads) >= MAX_LEADS:
        die("BOUND: %d leads already carried to a twin on %s (%s); the charter allows at most %d.  "
            "Refused." % (len(leads), name, ",".join(leads), MAX_LEADS), 3)
    if revs_of(rows, arm) >= MAX_REVS:
        die("BOUND: lead %s on %s already has %d twin revisions; the charter allows at most %d.  "
            "Refused." % (arm, name, revs_of(rows, arm), MAX_REVS), 3)


# ------------------------------------------------------------------ gates
def mac_suite_lock_path():
    if os.environ.get("ARTREV_SELFTEST") == "1" and os.environ.get("ARTREV_SUITE_LOCK_PATH"):
        return os.environ["ARTREV_SUITE_LOCK_PATH"]
    return os.path.join(repo_root(), "worktrees", ".mac-suite.lock")


def loadavg1():
    try:
        return os.getloadavg()[0]
    except OSError:
        return 0.0


def default_load_gate():
    return 2.0 if sys.platform == "darwin" else 0.5


def is_counted_arm(arm):
    return arm != "null" and not arm.startswith("ctl_") and arm not in ("orig", "orig2")


def lock_exists_path(p):
    """A lock may be a FILE or a DIRECTORY (the Mac suite lock has used both)."""
    return os.path.exists(p) or os.path.isdir(p)
