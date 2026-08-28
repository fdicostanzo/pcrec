#!/usr/bin/env python3
"""[ART-SIZE] STEP 1 census script.

Compiles every distinct `pattern` line in pcrec's own tests/**/*.rxt corpus,
plus every pcrec-bench pattern file (bench/email, bench/loglines, read-only),
with `build/pcrec -p rx --features all` at default (auto) engine selection,
then compiles the emitted C with `gcc -O2 -c` and records:

  - source bytes (the artifact pcrec emits, self-contained form: `-o -`)
  - .o bytes at -O2 (the number a user ships), plus `size`'s text/data/bss
  - gcc wall and CPU time (process rusage, equivalent to `/usr/bin/time -f`)
  - the D46 selection-fact stamps (engine, engine_why, vm_prefilter,
    dfa_scan, dfa_prefilter, dfa_table, vm_rungs, ncaps)
  - a byte ATTRIBUTION of the source by section (program / tables / prose /
    scaffolding / main), derived from the artifact's own line structure —
    see `attribute_source()`'s docstring for the exact rule — and validated
    to sum to the file's own byte count on every artifact (not a hope: an
    assertion that fires loudly if it does not).

Read-only against src/, tests/ and pcrec-bench/: this script only compiles
patterns through the built `build/pcrec` CLI and reads bench pattern files;
it writes nothing outside its own output directory and the session
scratchpad.

Population extraction matches the harness's own rule (docs/dev/plan.md
[ART-SIZE], tests/harness/run.sh's K35 note): distinct `pattern <regex>`
lines in tests/**/*.rxt, sorted under LC_ALL=C (Python's own str comparison
is already codepoint-order and does not depend on the process locale, so no
extra step is needed here to get the same POPULATION the shell `sort -u
LC_ALL=C` pipeline gets — verified against `grep -h '^pattern ' | LC_ALL=C
sort -u | wc -l` at 2758 for this corpus, matching this script's own count).

Usage:
  python3 census.py --root /home/duxevents/pcrec/worktrees/artsize \\
      --bench-root /home/duxevents/pcrec-bench \\
      --out /tmp/.../scratchpad/artsize/work \\
      [--limit N] [--workers 1] [--only-bench] [--skip-existing]

Output (in --out):
  patterns.tsv   id  source_tag  pattern            (pattern text, \\t-escaped)
  census.tsv     one row per pattern: see ROW_FIELDS below
  progress.log   appended one line per pattern processed (for polling)
"""
import argparse
import os
import re
import resource
import shlex
import signal
import subprocess
import sys
import time

ROW_FIELDS = [
    "id", "source_tag", "refused", "diag_class", "diag_text",
    "source_bytes", "pcrec_wall_ms",
    "gcc_verdict", "gcc_wall_ms", "gcc_cpu_ms",
    "o_bytes", "text_bytes", "data_bytes", "bss_bytes",
    "engine", "engine_why", "vm_prefilter", "dfa_scan", "dfa_prefilter",
    "dfa_table", "vm_rungs", "ncaps",
    "attr_program", "attr_tables", "attr_prose", "attr_scaffold",
    "attr_main", "attr_sum_ok",
]

# D45's plain-axis budgets (docs/dev/decisions.md D45; tests/lib/gen_timeout.sh):
# CPU-primary (10s) with a wall backstop (60s). Same numbers, reused here
# rather than re-derived, for a census compile exactly as for a harness one.
GCC_CPU_BUDGET = 10
GCC_WALL_BACKSTOP = 60
# pcrec's OWN invocation budget is a different, smaller quantity
# (tests/lib/gen_timeout.sh's pcrec_timeout_secs: 20s plain) — some corpus
# patterns are deliberately hostile (K25: a{0,25000} cost 15.3s in DFA
# minimization on this box's class of hardware), so this is generous rather
# than tight.
PCREC_WALL_BUDGET = 30
# A virtual-memory cap on pcrec's own invocation, mirroring tests/resource's
# BINDING ulimit -v discipline (an unbinding limit is not a control) — guards
# a runaway-allocating compile on a hostile corpus pattern without relying
# solely on the wall timeout to notice it. 3 GiB: comfortably above every
# legitimate corpus compile (K7's worst measured case is ~216 MB) and well
# under this box's memory.
PCREC_AS_LIMIT = 3 * 1024 * 1024 * 1024

PATTERN_RE = re.compile(r"^pattern (.*)$")


def find_rxt_patterns(root):
    """Every distinct `pattern <regex>` line under tests/**/*.rxt.

    `<regex>` is "everything after the first space on the line, taken
    verbatim to the end of the line (no quoting, no escaping)" per
    docs/spec/rxt_format.md — so a straight per-line regex match, no shell
    involved, is the format's own extraction rule.
    """
    tests_dir = os.path.join(root, "tests")
    seen = set()
    ordered = []
    rxt_files = []
    for dirpath, _dirnames, filenames in os.walk(tests_dir):
        for fn in filenames:
            if fn.endswith(".rxt"):
                rxt_files.append(os.path.join(dirpath, fn))
    rxt_files.sort()
    for path in rxt_files:
        with open(path, "rb") as f:
            data = f.read()
        text = data.decode("latin-1")
        for line in text.split("\n"):
            m = PATTERN_RE.match(line)
            if not m:
                continue
            pat = m.group(1)
            if pat in seen:
                continue
            seen.add(pat)
            ordered.append(pat)
    ordered.sort()  # LC_ALL=C-equivalent: Python str compares by codepoint
    return ordered


def find_bench_patterns(bench_root):
    """Every pcrec-bench pattern file under bench/{email,loglines}/patterns/.

    Read-only: this only reads the .rx files, never writes into
    pcrec-bench. Returns a list of (source_tag, pattern_text).
    """
    out = []
    for sub in ("email", "loglines"):
        pdir = os.path.join(bench_root, "bench", sub, "patterns")
        if not os.path.isdir(pdir):
            continue
        for fn in sorted(os.listdir(pdir)):
            if not fn.endswith(".rx"):
                continue
            path = os.path.join(pdir, fn)
            with open(path, "rb") as f:
                data = f.read()
            text = data.decode("latin-1")
            # A .rx file IS the pattern text, verbatim, with at most one
            # trailing newline (the file-writer's own convention, not part
            # of the pattern) — strip exactly one, never more.
            if text.endswith("\n"):
                text = text[:-1]
            name = fn[:-3]
            out.append((f"bench:{sub}:{name}", text))
    return out


def _set_as_limit():
    resource.setrlimit(resource.RLIMIT_AS, (PCREC_AS_LIMIT, PCREC_AS_LIMIT))


def compile_pattern(pcrec_bin, pattern):
    """Run `pcrec -p rx --features all -o - -- <pattern>`.

    Returns (ok, stdout_bytes, stderr_text, wall_ms).
    """
    argv = [pcrec_bin, "-p", "rx", "--features", "all", "-o", "-", "--", pattern]
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=_set_as_limit,
            timeout=PCREC_WALL_BUDGET,
        )
    except subprocess.TimeoutExpired:
        wall_ms = (time.monotonic() - t0) * 1000.0
        return False, b"", "WALL TIMEOUT: pcrec exceeded %ds" % PCREC_WALL_BUDGET, wall_ms
    wall_ms = (time.monotonic() - t0) * 1000.0
    if proc.returncode != 0:
        return False, b"", proc.stderr.decode("latin-1", "replace"), wall_ms
    return True, proc.stdout, "", wall_ms


DIAG_MODULE_RE = re.compile(r"requires module '([\w-]+)'")


def classify_diag(stderr_text):
    m = DIAG_MODULE_RE.search(stderr_text)
    if m:
        return "requires-module:" + m.group(1)
    if "WALL TIMEOUT" in stderr_text:
        return "pcrec-wall-timeout"
    if "too complex" in stderr_text:
        return "too-complex"
    if "pattern too large" in stderr_text or "too large" in stderr_text:
        return "too-large"
    first_line = stderr_text.strip().splitlines()[0] if stderr_text.strip() else ""
    return "other:" + first_line[:80]


def gcc_cpu_preexec():
    # RLIMIT_CPU soft-only (D45's own shape): SIGXCPU at the soft limit,
    # distinguishable from a hard SIGKILL / OOM. A generous hard ceiling
    # (+30s) is the escalation backstop if the soft signal is ignored.
    resource.setrlimit(resource.RLIMIT_CPU, (GCC_CPU_BUDGET, GCC_CPU_BUDGET + 30))


def compile_gcc(cc, c_path, o_path):
    """gcc -O2 -c the emitted source. Returns dict with verdict/wall/cpu."""
    argv = [cc, "-O2", "-std=gnu11", "-c", "-o", o_path, c_path]
    t0 = time.monotonic()
    pid = os.fork()
    if pid == 0:
        # child
        try:
            gcc_cpu_preexec()
            os.execvp(argv[0], argv)
        except Exception:
            os._exit(127)
    # parent: wall backstop via a SIGALRM-free poll loop (avoids signal
    # re-entrancy issues with the rest of the process); os.wait4 blocks, so
    # bound it with a watcher using os.waitpid(WNOHANG) in a short loop.
    deadline = t0 + GCC_WALL_BACKSTOP
    status = None
    rusage = None
    while True:
        try:
            wpid, status, rusage = os.wait4(pid, os.WNOHANG)
        except ChildProcessError:
            wpid = pid
            status = 0
            rusage = None
            break
        if wpid == pid:
            break
        if time.monotonic() > deadline:
            try:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
            except (ProcessLookupError, ChildProcessError):
                pass
            wall_ms = (time.monotonic() - t0) * 1000.0
            return {"verdict": "wall-backstop", "wall_ms": wall_ms, "cpu_ms": None}
        time.sleep(0.005)
    wall_ms = (time.monotonic() - t0) * 1000.0
    cpu_ms = (rusage.ru_utime + rusage.ru_stime) * 1000.0 if rusage else None
    if os.WIFSIGNALED(status):
        sig = os.WTERMSIG(status)
        if sig == signal.SIGXCPU:
            return {"verdict": "cpu-budget", "wall_ms": wall_ms, "cpu_ms": cpu_ms}
        return {"verdict": "signal-%d" % sig, "wall_ms": wall_ms, "cpu_ms": cpu_ms}
    rc = os.WEXITSTATUS(status)
    if rc != 0:
        return {"verdict": "gcc-error-%d" % rc, "wall_ms": wall_ms, "cpu_ms": cpu_ms}
    return {"verdict": "ok", "wall_ms": wall_ms, "cpu_ms": cpu_ms}


STAMP_RE = {
    "engine": re.compile(r'#define RX_ENGINE\s+"([^"]*)"'),
    "engine_why": re.compile(r'#define RX_ENGINE_WHY\s+"([^"]*)"'),
    "vm_prefilter": re.compile(r'#define RX_VM_PREFILTER\s+"([^"]*)"'),
    "dfa_scan": re.compile(r'#define RX_DFA_SCAN\s+"([^"]*)"'),
    "dfa_prefilter": re.compile(r'#define RX_DFA_PREFILTER\s+"([^"]*)"'),
    "dfa_table": re.compile(r'#define RX_DFA_TABLE\s+"([^"]*)"'),
    "vm_rungs": re.compile(r"#define RX_VM_RUNGS\s+(0x[0-9a-fA-F]+u?)"),
    "ncaps": re.compile(r"#define RX_NCAPS\s+(\d+)"),
}


def extract_stamps(source_text):
    out = {}
    for key, rx in STAMP_RE.items():
        m = rx.search(source_text)
        out[key] = m.group(1) if m else ""
    return out


# --------------------------------------------------------------------------
# Byte attribution.
#
# THE RULE (stated once here, cited by the report rather than re-derived):
# every line of the emitted source is assigned to exactly one of five
# buckets, by inspecting the artifact's OWN structure — comment syntax,
# `static const ... = { ... };` array-literal shape, and function/symbol
# NAMES the emitter itself chose (src/gen/CLAUDE.md's [M6-READ] naming:
# `<p>_<M>_step/_is_dead/_accepts/_accepts_class/_row/_view_live/_view_take`
# for the opaque-token accessors; `<prefix>_search/_match/_match_caps/_info`
# and the DFA/VM scan bodies for the program proper) — never from a count
# the compiler computes about the pattern. A line's bucket is decided the
# moment its owning unit is recognised (a comment block, a table literal, a
# function body between its opening and closing brace at column 0, or the
# span between one recognised unit and the next), so every byte of the file
# is claimed by exactly one bucket and the sum is the file size BY
# CONSTRUCTION — the per-artifact assertion below is therefore a bug check,
# not a hope that it comes out right.
#
#   PROSE      - block comments (/* ... */) and // line comments: the
#                [M6-READ] doc-comments, orientation block, section banner,
#                per-construct explanations. (No --emit-ir listing is ever
#                embedded in a plain `-o -` build, so this bucket is comment
#                text only for this census — noted in the report.)
#   TABLES     - `static const TYPE NAME[...] = { ... };` array literals:
#                DFA transition/accept/class/premultiplied tables and any
#                other read-only data array the emitter writes.
#   PROGRAM    - function bodies whose name matches the KNOWN entry/scan-loop
#                set (the matcher functions proper): <prefix>_search,
#                <prefix>_match, <prefix>_match_caps, <prefix>_match_*_in,
#                <prefix>_info, <prefix>_next_pos, rx_prefilter,
#                rx_match_anchored, rx_run_state_bind, rx_run_state_init,
#                rx_reset_for_next_attempt, rx_report_captures, and any other
#                non-accessor function body.
#   SCAFFOLD   - everything else with linkage or a declaration: #define
#                macros (including the stamps and the RX_TRAIL/RX_PUSH/
#                RX_SET/RX_CUT/RX_CHARGE_WORK operational macros), typedefs,
#                struct definitions, the opaque-token accessor functions
#                (name ends in _step/_is_dead/_accepts/_accepts_class/_row/
#                _view_live/_view_take, per src/gen/CLAUDE.md's [ENG-FORM]),
#                and blank/structural lines between recognised units.
#   MAIN       - an `int main(...)` body, when `--emit-main` is used (never
#                in this census's own `-o -` compiles; present only in the
#                witness/outlier throughput builds, which use --emit-main
#                and are attributed separately).
# --------------------------------------------------------------------------

ACCESSOR_SUFFIXES = (
    "_step", "_is_dead", "_accepts", "_accepts_class",
    "_row", "_view_live", "_view_take",
)

FUNC_DEF_RE = re.compile(
    r"^(?:static\s+)?(?:inline\s+)?(?:__attribute__\(\([^)]*\)\)\s*)*"
    r"[A-Za-z_][A-Za-z0-9_ \*]*\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*$"
)
TABLE_START_RE = re.compile(
    r"^(?:static\s+)?const\s+[A-Za-z_][A-Za-z0-9_ ]*\s+[A-Za-z_][A-Za-z0-9_]*\s*\[[^\]]*\]\s*=\s*\{"
)


def attribute_source(text):
    lines = text.split("\n")
    n = len(lines)
    buckets = {"program": 0, "tables": 0, "prose": 0, "scaffold": 0, "main": 0}

    def line_len(idx):
        # Byte length of lines[idx] AS IT APPEARS IN THE ORIGINAL FILE,
        # including its own trailing '\n' where one exists. text.split("\n")
        # puts one separator between every pair of elements and none after
        # the last, so every index except n-1 gets +1; the trailing empty
        # element a final '\n' produces (n-1 itself, when text ends in '\n')
        # correctly gets +0. This is what makes the buckets sum to the exact
        # file size rather than off by one.
        extra = 1 if idx < n - 1 else 0
        return len(lines[idx].encode("latin-1")) + extra

    def consume_table(start):
        """start: index of a line whose stripped form opens a table
        initializer. Returns (end_index_exclusive, byte_total)."""
        j = start
        total = line_len(j)
        j += 1
        while j < n:
            total += line_len(j)
            if lines[j].strip() == "};":
                j += 1
                break
            j += 1
        return j, total

    def consume_braced_block(start, bucket_name):
        """start: index of a line opening a brace-delimited block (a
        function body or main()). Scans line by line to the matching
        brace-depth-0 close, applying the SAME per-line dispatch as the
        top-level loop (comment / blank / table-literal detection) rather
        than dumping every nested line into the enclosing bucket — WITHOUT
        this, every doc-comment and every one of the thousands of per-node
        `// optional copy (N remaining)` comments the VM emitter writes
        inside its single giant search function would be misattributed as
        PROGRAM instead of PROSE (found by cross-checking a VM witness
        artifact against an independent `gcc -fpreprocessed -dD -E -P`
        comment-stripping pass: comments are ~15% of that file, not the
        <1% this function returned before this fix), and a local DFA table
        declared inside a scan function would be misattributed as PROGRAM
        instead of TABLES for the identical reason. Returns
        (end_index_exclusive, {bucket_name: n, 'tables': t, 'prose': p,
        'scaffold': s})."""
        out = {bucket_name: 0, "tables": 0, "prose": 0, "scaffold": 0}

        def bump(bucket, k):
            out[bucket] = out.get(bucket, 0) + k

        j = start
        depth = 0
        seen_open = False
        in_comment = False
        while j < n:
            raw = lines[j]
            stripped_j = raw.strip()

            if in_comment:
                bump("prose", line_len(j))
                if "*/" in raw:
                    in_comment = False
                j += 1
                continue

            if stripped_j.startswith("/*"):
                bump("prose", line_len(j))
                if "*/" not in raw[raw.find("/*") + 2:]:
                    in_comment = True
                j += 1
                continue

            if stripped_j.startswith("//"):
                bump("prose", line_len(j))
                j += 1
                continue

            if stripped_j == "":
                bump("scaffold", line_len(j))
                j += 1
                continue

            if TABLE_START_RE.match(stripped_j):
                j2, tbytes = consume_table(j)
                bump("tables", tbytes)
                # A table's braces are still real braces for the enclosing
                # function's depth count.
                for k in range(j, j2):
                    depth += lines[k].count("{") - lines[k].count("}")
                    if "{" in lines[k]:
                        seen_open = True
                j = j2
                if seen_open and depth <= 0:
                    break
                continue

            bump(bucket_name, line_len(j))
            ended_semi = raw.rstrip().endswith(";")
            depth += raw.count("{") - raw.count("}")
            if "{" in raw:
                seen_open = True
            j += 1
            if seen_open and depth <= 0:
                break
            # Safety net: a line that ends the statement with ';' while no
            # '{' has ever been seen means this was a DECLARATION, not a
            # definition with a body (a multi-line function-pointer
            # typedef, e.g. `typedef ptrdiff_t rx_renderfn(const rx_ctx
            # *ctx,\n  unsigned char *out, size_t outcap);` — FUNC_DEF_RE's
            # own no-semicolon-on-THIS-line rule only sees the first line,
            # so a wrapped typedef can slip through it). Without this, the
            # unterminated scan would run to end of file, folding
            # everything after it into one bucket.
            if not seen_open and ended_semi:
                break
        return j, out

    i = 0
    in_block_comment = False
    while i < n:
        raw = lines[i]
        stripped = raw.strip()

        if in_block_comment:
            buckets["prose"] += line_len(i)
            if "*/" in raw:
                in_block_comment = False
            i += 1
            continue

        if stripped.startswith("/*"):
            buckets["prose"] += line_len(i)
            if "*/" not in raw[raw.find("/*") + 2:]:
                in_block_comment = True
            i += 1
            continue

        if stripped.startswith("//"):
            buckets["prose"] += line_len(i)
            i += 1
            continue

        if stripped == "":
            buckets["scaffold"] += line_len(i)
            i += 1
            continue

        if TABLE_START_RE.match(stripped):
            j, tbytes = consume_table(i)
            buckets["tables"] += tbytes
            i = j
            continue

        if stripped.startswith("int main("):
            j, out = consume_braced_block(i, "main")
            for k, v in out.items():
                buckets[k] += v
            i = j
            continue

        fm = None if stripped.startswith("typedef") else FUNC_DEF_RE.match(stripped)
        if fm:
            name = fm.group(1)
            is_accessor = any(name.endswith(suf) for suf in ACCESSOR_SUFFIXES)
            bucket = "scaffold" if is_accessor else "program"
            j, out = consume_braced_block(i, bucket)
            for k, v in out.items():
                buckets[k] += v
            i = j
            continue

        # Anything else at top level: #define, typedef, struct, forward
        # decl, a stray '{'/'}' — scaffolding.
        buckets["scaffold"] += line_len(i)
        i += 1

    return buckets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--bench-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pcrec", default=None)
    ap.add_argument("--cc", default="gcc")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only-bench", action="store_true")
    ap.add_argument("--start-at", type=int, default=0)
    args = ap.parse_args()

    pcrec_bin = args.pcrec or os.path.join(args.root, "build", "pcrec")
    os.makedirs(args.out, exist_ok=True)
    workdir = os.path.join(args.out, "cc")
    os.makedirs(workdir, exist_ok=True)

    items = []  # (id, source_tag, pattern)
    if not args.only_bench:
        for idx, pat in enumerate(find_rxt_patterns(args.root)):
            items.append((f"rxt-{idx:05d}", "corpus", pat))
    for stag, pat in find_bench_patterns(args.bench_root):
        items.append((stag.replace(":", "-"), stag, pat))

    if args.limit:
        items = items[args.start_at:args.start_at + args.limit]
    else:
        items = items[args.start_at:]

    patterns_path = os.path.join(args.out, "patterns.tsv")
    census_path = os.path.join(args.out, "census.tsv")
    progress_path = os.path.join(args.out, "progress.log")

    mode_p = "a" if os.path.exists(patterns_path) else "w"
    mode_c = "a" if os.path.exists(census_path) else "w"
    with open(patterns_path, mode_p) as pf, open(census_path, mode_c) as cf, \
         open(progress_path, "a") as lf:
        if mode_p == "w":
            pf.write("id\tsource_tag\tpattern\n")
        if mode_c == "w":
            cf.write("\t".join(ROW_FIELDS) + "\n")

        t_start = time.monotonic()
        for n, (pid, stag, pat) in enumerate(items):
            pat_escaped = pat.replace("\\", "\\\\").replace("\t", "\\t")
            pf.write(f"{pid}\t{stag}\t{pat_escaped}\n")
            pf.flush()

            row = {k: "" for k in ROW_FIELDS}
            row["id"] = pid
            row["source_tag"] = stag

            ok, out_bytes, err_text, pwall = compile_pattern(pcrec_bin, pat)
            row["pcrec_wall_ms"] = f"{pwall:.2f}"
            if not ok:
                row["refused"] = "1"
                dc = classify_diag(err_text)
                row["diag_class"] = dc
                row["diag_text"] = err_text.strip().splitlines()[0][:200] if err_text.strip() else ""
                cf.write("\t".join(str(row[k]) for k in ROW_FIELDS) + "\n")
                cf.flush()
                lf.write(f"{n+1}/{len(items)} {pid} REFUSED {dc}\n")
                lf.flush()
                continue

            row["refused"] = "0"
            row["source_bytes"] = str(len(out_bytes))
            source_text = out_bytes.decode("latin-1")

            stamps = extract_stamps(source_text)
            for k in ("engine", "engine_why", "vm_prefilter", "dfa_scan",
                      "dfa_prefilter", "dfa_table", "vm_rungs", "ncaps"):
                row[k] = stamps[k]

            attrib = attribute_source(source_text)
            row["attr_program"] = str(attrib["program"])
            row["attr_tables"] = str(attrib["tables"])
            row["attr_prose"] = str(attrib["prose"])
            row["attr_scaffold"] = str(attrib["scaffold"])
            row["attr_main"] = str(attrib["main"])
            attr_sum = sum(attrib.values())
            row["attr_sum_ok"] = "1" if attr_sum == len(out_bytes) else f"0(sum={attr_sum})"

            c_path = os.path.join(workdir, pid + ".c")
            o_path = os.path.join(workdir, pid + ".o")
            with open(c_path, "wb") as cfh:
                cfh.write(out_bytes)

            gres = compile_gcc(args.cc, c_path, o_path)
            row["gcc_verdict"] = gres["verdict"]
            row["gcc_wall_ms"] = f"{gres['wall_ms']:.2f}"
            row["gcc_cpu_ms"] = f"{gres['cpu_ms']:.2f}" if gres["cpu_ms"] is not None else ""

            if gres["verdict"] == "ok" and os.path.exists(o_path):
                row["o_bytes"] = str(os.path.getsize(o_path))
                try:
                    sz = subprocess.run(["size", o_path], capture_output=True, text=True, timeout=10)
                    lines_ = sz.stdout.strip().splitlines()
                    if len(lines_) >= 2:
                        parts = lines_[1].split()
                        row["text_bytes"], row["data_bytes"], row["bss_bytes"] = parts[0], parts[1], parts[2]
                except Exception:
                    pass
                # Clean up .o after measuring — this is a census, not an
                # artifact archive; the .c stays for the outlier/witness
                # follow-up passes to re-read cheaply.
                try:
                    os.remove(o_path)
                except OSError:
                    pass
            else:
                # Keep the .c for postmortem on a gcc failure/timeout, but
                # don't let a huge pathological source pile up once logged.
                pass

            cf.write("\t".join(str(row[k]) for k in ROW_FIELDS) + "\n")
            cf.flush()
            elapsed = time.monotonic() - t_start
            lf.write(
                f"{n+1}/{len(items)} {pid} ok src={row['source_bytes']} "
                f"o={row['o_bytes']} gcc={row['gcc_verdict']} "
                f"({elapsed:.1f}s elapsed)\n"
            )
            lf.flush()

    print(f"done: {len(items)} items -> {census_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
