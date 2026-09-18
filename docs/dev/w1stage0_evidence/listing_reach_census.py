#!/usr/bin/env python3
"""
[REVW.1] wave 1 stage 0 -- the listing-reach census (EP2 addition).

WHY THIS EXISTS. emitvm_second_pass.md S7 (ADDENDUM 2), the "one thing I
would want measured before wave 1 starts": does run_ir_listing.sh's fixed
PATTERNS population (tests/codegen/run_ir_listing.sh) actually REACH L8's
rung emitters -- vm_alt, vm_cursor_rep, vm_rev_emit, vm_revdet_rep,
vm_counter_*, vm_star, vm_rep, vm_atomic, the chains -- whose vm_rolef ROLE
TEXT is the listing's own content? The `.c`-artifact byte-identity gates say
nothing about this population; the answer here is what stage 3 (a future
wave) needs to know its acceptance criterion's population against the irsb
stream specifically.

METHOD, in two halves.

  (1) STATIC: every `vm_rolef(v, "<fmt>"` call site in src/gen/emit_vm.c,
      attributed to its ENCLOSING FUNCTION by a backward scan for the
      nearest preceding `<ret> <name>(` line at column 0 (this file's own
      convention -- src/gen/emit_vm.c's functions are all file-scope,
      declared at column 0, per docs/dev/coding_guide.md S1.7's "single-
      letter locals ARE the house convention" neighbourhood). The call's
      format string is reduced to its LITERAL PREFIX (everything before the
      first `%` conversion, trimmed) -- a substring that, if it appears in a
      --emit-ir listing's ROLE COMMENT text, proves that call site fired.

  (2) DYNAMIC: compile every pattern in a given population (default:
      run_ir_listing.sh's own PATTERNS array, extracted from that file so
      there is only one place the set is typed) at --engine=vm --emit-ir,
      and for each static call site's literal prefix, record whether it
      appears ANYWHERE in the combined listing text.

CAVEAT, stated because every instrument in this tree states its blind spot:
a literal-prefix substring match can occasionally be satisfied by an
UNRELATED role string that happens to share a prefix (none observed in this
run, checked by hand against the printed per-site table) -- this is a
CENSUS, not a byte-identity gate; a false-positive "reached" is the risk
side that costs nothing here (it would only make stage 3's population
estimate optimistic, never certify wrong bytes), so it is accepted rather
than defended against with a second instrument.

Usage: python3 listing_reach_census.py <pcrec> <repo-root> [--corpus]
  --corpus additionally runs the census over the FULL tests/**/*.rxt corpus
  (every `pattern`/`pattern-esc` line, default engine selection -- i.e. only
  patterns that select VM at all can reach anything) as a second population,
  informational rather than the primary answer (the charter's own question
  is about run_ir_listing.sh's population specifically).
"""
import re
import subprocess
import sys
import os

PCREC = sys.argv[1]
REPO_ROOT = sys.argv[2]
DO_CORPUS = "--corpus" in sys.argv[3:]

EMIT_VM = os.path.join(REPO_ROOT, "src", "gen", "emit_vm.c")
RUN_IR_LISTING = os.path.join(REPO_ROOT, "tests", "codegen", "run_ir_listing.sh")

# The L8 rung-emitter family, lens10/EP2's own naming (emitvm_second_pass.md
# L8's row). Any enclosing function found by the backward scan that is NOT
# in this set is reported too (censuses everything vm_rolef reaches, not
# only this named family) but this set is what the charter's own question
# is about.
L8_RUNG_EMITTERS = {
    "vm_alt", "vm_cursor_rep", "vm_rev_emit", "vm_revdet_rep",
    "vm_star", "vm_rep", "vm_atomic",
    # "the chains" -- the call-site save/restore chain functions EP2 names
    # at emit_vm.c:6818/6942/7009/7023; attributed by whatever function
    # name the backward scan actually finds there, reported under its own
    # name rather than folded into this set sight unseen.
}
# vm_counter_* is a prefix family (vm_counter_body etc.) -- matched by
# startswith below rather than listed by exact name, since the exact set of
# vm_counter_* functions is a fact to DISCOVER, not to assume.


def enclosing_function(lines, call_line_idx):
    """Backward scan from call_line_idx (0-based) for the nearest preceding
    C function definition head at column 0: `<ret-type-ish> <name>(`.
    Returns the function name, or None if the file start is reached first
    (a call outside any function -- should not happen, reported as None
    rather than guessed)."""
    # A function head in this file is a line starting at column 0 with no
    # leading whitespace, ending in `(` before the parameter list, and not
    # a control keyword / macro / declaration-only line ending in `;`.
    head_re = re.compile(r'^(?:static\s+)?[A-Za-z_][A-Za-z0-9_ \*]*\b([A-Za-z_][A-Za-z0-9_]*)\s*\(')
    for i in range(call_line_idx, -1, -1):
        line = lines[i]
        if line.startswith((' ', '\t', '}', '#', '/', '*')):
            continue
        if line.rstrip().endswith(';'):
            continue
        m = head_re.match(line)
        if m:
            return m.group(1)
    return None


def literal_prefix(fmt: str) -> str:
    """The portion of a printf-style format literal before its first `%`
    conversion, trimmed. Empty if the format starts with a conversion."""
    idx = fmt.find('%')
    prefix = fmt if idx < 0 else fmt[:idx]
    return prefix.strip()


def find_rolef_sites():
    with open(EMIT_VM, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split('\n')

    # Match `vm_rolef(v, "..."`, allowing the format literal's opening quote
    # to be on a LATER line than the `vm_rolef(v,` token (DOTALL over the
    # whitespace/newlines between them -- four real call sites in this file
    # wrap the call open onto one line and the format string onto the next,
    # e.g. `vm_lbl(v, bl[i], vm_rolef(v,\n       "lookbehind branch..."`; an
    # earlier same-line-only version of this regex silently DROPPED all four
    # (found by cross-checking this script's own site count against a plain
    # `grep -c vm_rolef` sweep, minus the definition and one comment mention
    # -- 42 - 1 - 4 = 37, which is exactly what the same-line regex found).
    # Concatenated adjacent string literals (C's own mechanism, used
    # elsewhere in this file for long role strings) are joined.
    call_re = re.compile(r'vm_rolef\s*\(\s*v\s*,\s*"((?:[^"\\]|\\.)*)"', re.DOTALL)
    def_line_no = None
    for i, line in enumerate(lines):
        if re.match(r'^static const char \*vm_rolef\s*\(', line):
            def_line_no = i
            break

    sites = []
    seen_starts = set()
    for m in call_re.finditer(text):
        start = m.start()
        line_no = text.count('\n', 0, start)  # 0-based
        if def_line_no is not None and line_no in (def_line_no, def_line_no + 1):
            continue
        if start in seen_starts:
            continue
        seen_starts.add(start)
        fmt = m.group(1)
        # Follow C string-literal concatenation past the matched close-quote.
        rest_start = m.end()
        pos = rest_start
        while True:
            more = re.match(r'\s*"((?:[^"\\]|\\.)*)"', text[pos:], re.DOTALL)
            if not more:
                break
            fmt += more.group(1)
            pos += more.end()
        fn = enclosing_function(lines, line_no)
        sites.append({
            "line": line_no + 1,
            "function": fn,
            "format": fmt,
            "prefix": literal_prefix(fmt),
        })
    sites.sort(key=lambda s: s["line"])
    return sites


def rung_family(fn):
    if fn is None:
        return "UNATTRIBUTED"
    if fn in L8_RUNG_EMITTERS:
        return fn
    if fn.startswith("vm_counter_") or fn == "vm_counter":
        return fn
    return fn  # report under its own name regardless; family membership is informational


def extract_patterns_from_run_ir_listing():
    """The (pattern, features) rows run_ir_listing.sh actually runs.

    [REVW.2] wave 2 stage 3, 2026-09-18 (lane w2b): that script gained a
    PATTERN_FEATURES array positionally parallel to PATTERNS, because four of
    the families this census reports as UNREACHED are module-gated and refuse
    to compile at all without the matching --features flag -- which is what
    w2census_report.md's TASK 2 found to be the real cause of the reach gap
    w1stage0 recorded. Reading PATTERNS alone here would compile the widened
    rows with no features, they would refuse, and this instrument would keep
    reporting the OLD number while the arm it measures had already improved:
    the instrument going stale silently in the optimistic-looking direction.

    A row count mismatch between the two arrays is a hard error rather than a
    zip-truncation, for the same reason the script itself asserts it.
    """
    with open(RUN_IR_LISTING, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r'PATTERNS=\(\n(.*?)\n\)', text, re.S)
    if not m:
        raise SystemExit("could not find PATTERNS=( ... ) in run_ir_listing.sh")
    pats = re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1))

    mf = re.search(r'PATTERN_FEATURES=\(\n(.*?)\n\)', text, re.S)
    if not mf:
        # Pre-widening shape: no features array, every row is base grammar.
        return [(p, "") for p in pats]
    feats = re.findall(r"'((?:[^'\\]|\\.)*)'", mf.group(1))
    if len(feats) != len(pats):
        raise SystemExit(
            "run_ir_listing.sh: PATTERNS has %d rows and PATTERN_FEATURES has %d; "
            "this census cannot guess which pattern needs which module"
            % (len(pats), len(feats)))
    return list(zip(pats, feats))


def decode_rxt_escape(s: str) -> bytes:
    out = bytearray()
    i = 0
    b = s.encode("utf-8", errors="surrogateescape")
    n = len(b)
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:
            nxt = b[i + 1]
            if nxt == ord('t'):
                out.append(0x09); i += 2; continue
            elif nxt == ord('n'):
                out.append(0x0A); i += 2; continue
            elif nxt == ord('r'):
                out.append(0x0D); i += 2; continue
            elif nxt == 0x5C:
                out.append(0x5C); i += 2; continue
            elif nxt == ord('x') and i + 3 < n:
                hx = bytes([b[i+2], b[i+3]])
                try:
                    val = int(hx, 16); out.append(val); i += 4; continue
                except ValueError:
                    pass
            out.append(c); i += 1; continue
        else:
            out.append(c); i += 1
    return bytes(out)


def find_rxt_files(root):
    files = []
    for dirpath, _, filenames in os.walk(os.path.join(root, "tests")):
        for fn in filenames:
            if fn.endswith(".rxt"):
                files.append(os.path.join(dirpath, fn))
    return sorted(files)


def corpus_patterns():
    files = find_rxt_files(REPO_ROOT)
    pats = []
    for f in files:
        try:
            r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=30)
        except subprocess.TimeoutExpired:
            continue
        for line in r.stdout.decode("utf-8", errors="surrogateescape").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            fields = line.split("\t")
            if len(fields) < 5 or fields[0] not in ("pattern", "pattern-esc"):
                continue
            pats.append(decode_rxt_escape(fields[4]))
    return pats


def emit_ir_text(pattern_bytes_or_str, engine_vm_forced, features=""):
    argv = [PCREC, "-p", "rx"]
    if engine_vm_forced:
        argv += ["--engine=vm"]
    if features:
        argv += ["--features", features]
    argv += ["--emit-ir", "--", pattern_bytes_or_str]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="surrogateescape")


def run_census(sites, patterns, engine_vm_forced, label):
    combined = []
    n_compiled = 0
    n_vm = 0
    for row in patterns:
        # A row is either a bare pattern (the corpus arm) or a
        # (pattern, features) pair (the run_ir_listing.sh arm).
        if isinstance(row, tuple):
            pat, feats = row
        else:
            pat, feats = row, ""
        txt = emit_ir_text(pat, engine_vm_forced, feats)
        if txt is None:
            continue
        n_compiled += 1
        n_vm += 1  # --emit-ir only succeeds on a VM artifact by construction
        combined.append(txt)
    blob = "\n".join(combined)

    reached = {}
    for s in sites:
        prefix = s["prefix"]
        hit = bool(prefix) and (prefix in blob)
        key = (s["function"], s["line"])
        reached[key] = hit

    n_sites = len(sites)
    n_reached = sum(1 for v in reached.values() if v)
    by_fn = {}
    for s in sites:
        fn = s["function"] or "UNATTRIBUTED"
        by_fn.setdefault(fn, {"total": 0, "reached": 0})
        by_fn[fn]["total"] += 1
        if reached[(s["function"], s["line"])]:
            by_fn[fn]["reached"] += 1

    print(f"=== {label} ===")
    print(f"patterns supplied: {len(patterns)}, compiled to a VM --emit-ir listing: {n_compiled}")
    print(f"vm_rolef call sites: {n_sites}, reached (literal prefix seen in listing text): {n_reached}")
    print("")
    print(f"{'function':32} {'reached':>8} {'total':>6}")
    for fn in sorted(by_fn):
        d = by_fn[fn]
        mark = "L8" if fn in L8_RUNG_EMITTERS or fn.startswith("vm_counter") else "  "
        print(f"{mark} {fn:29} {d['reached']:8} {d['total']:6}")
    print("")
    unreached = [s for s in sites if not reached[(s["function"], s["line"])]]
    if unreached:
        print(f"UNREACHED sites ({len(unreached)}):")
        for s in unreached:
            print(f"  emit_vm.c:{s['line']:<6} {s['function']:<20} prefix={s['prefix']!r}")
    print("")
    return {"n_sites": n_sites, "n_reached": n_reached, "by_fn": by_fn, "unreached": unreached}


def main():
    sites = find_rolef_sites()
    print(f"# vm_rolef call sites found in {EMIT_VM}: {len(sites)}", file=sys.stderr)
    unattributed = [s for s in sites if s["function"] is None]
    if unattributed:
        print(f"# WARNING: {len(unattributed)} call site(s) could not be attributed to an enclosing function:", file=sys.stderr)
        for s in unattributed:
            print(f"#   emit_vm.c:{s['line']}", file=sys.stderr)

    ir_listing_pats = extract_patterns_from_run_ir_listing()
    print(f"# run_ir_listing.sh PATTERNS extracted: {len(ir_listing_pats)}", file=sys.stderr)

    run_census(sites, ir_listing_pats, engine_vm_forced=True,
               label="PRIMARY: run_ir_listing.sh's own PATTERNS population (--engine=vm forced, matching that script's own invocation)")

    if DO_CORPUS:
        pats = corpus_patterns()
        print(f"# corpus pattern/pattern-esc lines: {len(pats)}", file=sys.stderr)
        run_census(sites, pats, engine_vm_forced=False,
                   label="SECONDARY (informational): the full corpus at DEFAULT engine selection (a pattern that selects the DFA contributes nothing)")


if __name__ == "__main__":
    main()
