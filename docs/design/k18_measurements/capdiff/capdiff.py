#!/usr/bin/env python3
"""capdiff.py — the K18 capture-offset differential
(k18_memo_design.md Sec.4.6's open item).

For every pattern in a `LABEL\\tPATTERN` TSV (gen_capshapes.py's output, or
any other file in that shape), builds TWO artifacts:

  * AUTO   -- the default build. Every capture-bearing pattern is VM-forced
              (src/opt/select_engine.c's `forces_captures`) with the DFA
              prefilter ON (`fit.prefilter`, src/opt/select_engine.c:195),
              so this is the pipeline a real caller gets and the one that
              actually threads the K18-rewritten closure's output (the
              reverse-machine's computed START) into the VM's capture
              extraction (src/gen/emit_vm.c's `<prefix>_search`, "start =
              (size_t)win[0][0]").
  * VMONLY -- `--engine=vm`, prefilter OFF (D44/R21 E-6): an independent
              second derivation sharing no DFA-closure code with AUTO.

and compares, per (pattern, subject) cell, FOUR ways:

  1. AUTO caps      vs python3 `re`      (the base-tier oracle, D4)
  2. AUTO caps      vs libpcre2 caps     (D44's three-way rule)
  3. VMONLY caps    vs AUTO caps         (isolates a prefilter-fed defect:
                                          if these two independently-derived
                                          answers agree and AUTO is still
                                          wrong, the defect is not in the
                                          prefilter/DFA at all)
  4. python3 `re`   vs libpcre2          (sanity: the two oracles should
                                          never disagree with each other in
                                          this space -- if they do, the CELL
                                          is excluded from 1/2 rather than
                                          blamed on pcrec, per D26/upstream_
                                          issues.md's standing discipline)

Every comparison reads the DRIVER'S raw three-valued line
(`match S0 E0 ...` / `nomatch` / `err_steps` / `err_frames`) via
tests/vm/vm_driver.c, never a C-truthy interpretation of `<prefix>_search`'s
return code (K21's lesson) -- this script does not reimplement that
discrimination, it consumes the shared driver that already does it.

Usage:
    PCREC=/path/to/pcrec python3 capdiff.py patterns.tsv [--jobs N]
        [--maxlen-2 N] [--maxlen-3 N] [--maxlen-4 N] [--label LABEL]

Env: PCREC (default build/pcrec relative to repo root), PCREC_VM (default:
same binary, invoked with --engine=vm), CC (default gcc).
"""
import itertools
import os
import re
import subprocess
import sys
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../docs/design/k18_measurements/capdiff -- four levels up is repo root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
DRIVER = os.path.join(ROOT, "tests", "vm", "vm_driver.c")
PCRE2_ORACLE_SRC = os.path.join(HERE, "pcre2_batch_oracle.c")

PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
CC = os.environ.get("CC", "gcc")
GENCFLAGS = os.environ.get("GENCFLAGS", "-O0 -std=gnu11").split()


def gen_timeout():
    try:
        r = subprocess.run(["bash", os.path.join(ROOT, "tests", "lib", "gen_timeout.sh"), "secs"],
                            capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip())
    except Exception:
        return 5


GEN_TIMEOUT = gen_timeout()


# --------------------------------------------------------------- subjects

def alphabet_for(pat):
    letters = sorted(set(c for c in pat if c.isalpha() and c.islower()))
    if not letters:
        letters = ["a"]
    return letters[:4]


def sweep(alphabet, maxlen):
    out = [""]
    for n in range(1, maxlen + 1):
        out += ["".join(t) for t in itertools.product(alphabet, repeat=n)]
    return out


def subjects_for(pat, maxlen_by_size):
    alpha = alphabet_for(pat)
    maxlen = maxlen_by_size.get(len(alpha), 2)
    return sorted(set(sweep(alpha, maxlen)))


# ----------------------------------------------------------------- build

def pcrec_build(pat, d, tag, extra):
    # vm_driver.c #includes "gen.h" literally (it is the shared driver, not
    # reshaped per caller), so each build gets its OWN subdirectory named
    # "gen.c"/"gen.h" rather than a tag-suffixed filename -- two builds (auto,
    # vmonly) in one parent dir cannot otherwise both satisfy that #include.
    sub = os.path.join(d, tag)
    os.makedirs(sub, exist_ok=True)
    csrc = os.path.join(sub, "gen.c")
    try:
        r = subprocess.run([PCREC, "-p", "rx"] + extra + ["-o", csrc, "--", pat],
                           capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None, "PCREC-TIMEOUT"
    if r.returncode != 0:
        return None, "pcrec: " + r.stderr.strip()[:300]
    exe = os.path.join(sub, "t")
    try:
        r = subprocess.run([CC] + GENCFLAGS + ["-DVM_CHECK_ANCHORED", "-I", sub,
                                               "-o", exe, DRIVER, csrc],
                           capture_output=True, text=True, timeout=GEN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, "D45-GEN-TIMEOUT(%ds)" % GEN_TIMEOUT
    if r.returncode != 0:
        return None, "gcc: " + r.stderr.strip()[:600]
    return exe, None


def run_driver(exe, subj, startpos=0):
    argv = [exe, esc(subj)] + ([str(startpos)] if startpos else [])
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return "DRIVER_EXIT_%d" % r.returncode
    line = r.stdout.strip()
    if line == "nomatch":
        return "nomatch"
    if line.startswith("err_"):
        return line
    parts = line.split()
    if parts[0] != "match":
        return "BAD_OUTPUT:" + line
    nums = [int(x) for x in parts[1:]]
    return tuple(zip(nums[0::2], nums[1::2]))


def esc(s):
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            out.append("\\x%02x" % ord(ch))
    return "".join(out)


# ----------------------------------------------------------------- oracle

def py_oracle(pat, subj, startpos=0):
    try:
        rx = re.compile(pat.encode("latin-1"))
    except re.error:
        return None, 0
    b = subj.encode("latin-1")
    if startpos > len(b):
        return "nomatch", rx.groups
    m = rx.search(b, startpos)
    if not m:
        return "nomatch", rx.groups
    out = []
    for k in range(rx.groups + 1):
        out.append(m.span(k))
    return tuple(out), rx.groups


def trim(caps, k):
    """First k+1 pairs of a caps tuple/'nomatch'/err_* verdict, UNSET-padded
    if the artifact reported fewer slots than the pattern's own group count
    (never happens today, but a mismatch should show up as a real diff
    rather than an IndexError)."""
    if not isinstance(caps, tuple):
        return caps
    out = list(caps[: k + 1])
    while len(out) < k + 1:
        out.append((-1, -1))
    return tuple(out)


# --------------------------------------------------------------- pcre2

def build_pcre2_oracle(workdir):
    exe = os.path.join(workdir, "pcre2_batch_oracle")
    r = subprocess.run([CC, "-O2", "-std=gnu11", "-o", exe, PCRE2_ORACLE_SRC, "-ldl"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("capdiff: failed to build pcre2_batch_oracle: " + r.stderr)
    return exe


def pcre2_batch(exe, cells):
    """cells: list of (pattern, startpos, subject_str). Returns a parallel
    list of verdicts, each 'nomatch' / 'cerr N' / 'mlimit N' / a caps tuple."""
    inp = []
    for pat, sp, subj in cells:
        inp.append("%s\t%d\t%s\n" % (pat, sp, subj.encode("latin-1").hex()))
    r = subprocess.run([exe], input="".join(inp), capture_output=True, text=True,
                       timeout=max(60, len(cells) // 20))
    verfile = r.stderr
    lines = r.stdout.splitlines()
    if len(lines) != len(cells):
        sys.exit("capdiff: pcre2_batch_oracle line-count mismatch: %d cells, %d lines\n"
                 "stderr: %s" % (len(cells), len(lines), verfile))
    out = []
    for line in lines:
        parts = line.split()
        if parts[0] == "nomatch":
            out.append("nomatch")
        elif parts[0] in ("cerr", "mlimit"):
            out.append("%s %s" % (parts[0], parts[1]))
        else:
            nums = [int(x) for x in parts[1:]]
            out.append(tuple(zip(nums[0::2], nums[1::2])))
    return out, verfile


# ------------------------------------------------------------------ main

def check_pattern(workdir, label, pat, maxlen_by_size):
    d = tempfile.mkdtemp(dir=workdir)
    fails = []
    exe_auto, err = pcrec_build(pat, d, "auto", [])
    if err:
        return label, pat, ["BUILD auto: " + err], [], 0
    exe_vm, err = pcrec_build(pat, d, "vm", ["--engine=vm"])
    if err:
        return label, pat, ["BUILD vmonly: " + err], [], 0

    subs = subjects_for(pat, maxlen_by_size)
    rows = []  # (subj, auto_verdict, vm_verdict, py_verdict, ngroups)
    for subj in subs:
        py_v, ngroups = py_oracle(pat, subj)
        if py_v is None:
            shutil.rmtree(d, ignore_errors=True)
            return label, pat, [], [], 0
        auto_v = run_driver(exe_auto, subj)
        vm_v = run_driver(exe_vm, subj)
        rows.append((subj, auto_v, vm_v, py_v, ngroups))

    shutil.rmtree(d, ignore_errors=True)
    return label, pat, fails, rows, len(subs)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    patfile = args[0]

    def opt(name, default):
        flag = "--" + name
        if flag in sys.argv:
            return sys.argv[sys.argv.index(flag) + 1]
        return default

    jobs = int(opt("jobs", "8"))
    maxlen_by_size = {
        1: int(opt("maxlen-1", "5")),
        2: int(opt("maxlen-2", "4")),
        3: int(opt("maxlen-3", "3")),
        4: int(opt("maxlen-4", "2")),
    }

    if not os.path.exists(PCREC):
        sys.exit("capdiff: no pcrec binary at %s" % PCREC)

    patterns = []
    with open(patfile) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or "\t" not in line:
                continue
            lab, pat = line.split("\t", 1)
            patterns.append((lab, pat))

    workdir = tempfile.mkdtemp(prefix="capdiff.")
    pcre2exe = build_pcre2_oracle(workdir)

    print("capdiff: %d patterns, PCREC=%s, jobs=%d" % (len(patterns), PCREC, jobs),
          file=sys.stderr)

    results = []
    try:
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = [ex.submit(check_pattern, workdir, lab, pat, maxlen_by_size)
                    for lab, pat in patterns]
            for i, f in enumerate(futs):
                results.append(f.result())
                if (i + 1) % 50 == 0:
                    print("capdiff: %d/%d patterns done" % (i + 1, len(patterns)),
                          file=sys.stderr)

        # ---- collect every cell needing the libpcre2 oracle ---------------
        cells = []  # (pattern, startpos, subject)
        cellrefs = []  # (result_index, row_index)
        for ri, (label, pat, fails, rows, n) in enumerate(results):
            for rj, (subj, auto_v, vm_v, py_v, ngroups) in enumerate(rows):
                cells.append((pat, 0, subj))
                cellrefs.append((ri, rj))

        pcre2_verdicts, pcre2_stderr = pcre2_batch(pcre2exe, cells)
        by_cell = {}
        for (ri, rj), v in zip(cellrefs, pcre2_verdicts):
            by_cell[(ri, rj)] = v
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    # ---- score --------------------------------------------------------
    npat = 0
    ncell = 0
    n_auto_vs_py = 0
    n_auto_vs_pcre2 = 0
    n_auto_vs_vm = 0
    n_py_vs_pcre2 = 0   # oracle/oracle sanity disagreements
    build_fail_labels = []
    faillines = []

    for ri, (label, pat, fails, rows, n) in enumerate(results):
        npat += 1
        if fails:
            build_fail_labels.append("%s\t%s\t%s" % (label, pat, "; ".join(fails)))
            continue
        for rj, (subj, auto_v, vm_v, py_v, ngroups) in enumerate(rows):
            ncell += 1
            pcre2_v = by_cell[(ri, rj)]

            py_t = trim(py_v, ngroups)
            pcre2_t = trim(pcre2_v, ngroups) if isinstance(pcre2_v, tuple) else pcre2_v
            auto_t = trim(auto_v, ngroups) if isinstance(auto_v, tuple) else auto_v
            vm_t = trim(vm_v, ngroups) if isinstance(vm_v, tuple) else vm_v

            py_norm = "nomatch" if py_t == "nomatch" else py_t
            pcre2_norm = pcre2_t
            if isinstance(pcre2_norm, str) and pcre2_norm.startswith("mlimit"):
                continue  # PCRE2 safeguard tripped: not a verdict, excluded

            oracle_disagree = False
            if py_norm != pcre2_norm and not (
                isinstance(pcre2_norm, str) and pcre2_norm.startswith("cerr")):
                n_py_vs_pcre2 += 1
                oracle_disagree = True
                faillines.append('ORACLE-DISAGREE %s\t"%s" -> py=%s pcre2=%s'
                                 % (label, esc(subj), py_norm, pcre2_norm))

            if not oracle_disagree:
                if auto_t != py_norm:
                    n_auto_vs_py += 1
                    faillines.append('%s\t"%s" AUTO-vs-PY: got %s want %s'
                                     % (label, esc(subj), auto_t, py_norm))
                if isinstance(pcre2_norm, tuple) or pcre2_norm == "nomatch":
                    if auto_t != pcre2_norm:
                        n_auto_vs_pcre2 += 1
                        faillines.append('%s\t"%s" AUTO-vs-PCRE2: got %s want %s'
                                         % (label, esc(subj), auto_t, pcre2_norm))

            if auto_t != vm_t:
                n_auto_vs_vm += 1
                faillines.append('%s\t"%s" AUTO-vs-VMONLY (prefilter suspect): %s vs %s'
                                 % (label, esc(subj), auto_t, vm_t))

    print("=" * 78)
    print("capdiff summary")
    print("patterns:                    %d" % npat)
    print("patterns with a build failure: %d" % len(build_fail_labels))
    print("pattern/subject cells:       %d" % ncell)
    print("AUTO vs python re disagreements:   %d" % n_auto_vs_py)
    print("AUTO vs libpcre2 disagreements:    %d" % n_auto_vs_pcre2)
    print("AUTO vs VMONLY (prefilter) disagreements: %d" % n_auto_vs_vm)
    print("python vs libpcre2 (oracle/oracle sanity) disagreements: %d" % n_py_vs_pcre2)
    print("=" * 78)
    if build_fail_labels:
        print("\n-- build failures --")
        for l in build_fail_labels[:40]:
            print(l)
        if len(build_fail_labels) > 40:
            print("... and %d more" % (len(build_fail_labels) - 40))
    if faillines:
        print("\n-- cell failures (first 200) --")
        for l in faillines[:200]:
            print(l)
        if len(faillines) > 200:
            print("... and %d more" % (len(faillines) - 200))

    bad = n_auto_vs_py + n_auto_vs_pcre2 + n_auto_vs_vm
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
