"""tests/captures/gen_empty_iteration.py -- writes empty_iteration.rxt beside it:
K128's cells, the empty-iteration rule at an unbounded repeat's LAST
MANDATORY iteration (docs/dev/known_issues.md K128). Re-run after editing
the case list:

    PCREC_PCRE2_PATH=libpcre2-8.so.0 \\
        python3 tests/captures/gen_empty_iteration.py [--check-pcrec BUILD/pcrec]

WHAT IT GUARDS. PCRE2 compiles `X{m,}` (m >= 1) as m-1 plain copies and ONE
repeating bracket, so its "an iteration that matched empty does not repeat"
rule already covers iteration m: after an empty iteration m the loop takes
its continuation, and a failure there backtracks INTO iteration m. pcrec
emitted m mandatory copies and then the guarded star, so after an empty
copy m the star still iterated, and a group set by the empty iteration
survived the later one: `(?:()|a)+?b` over "ab" gave group 1 = (0,0) where
libpcre2 leaves it unset (lane iterd27, F4). The rows are that witness and
its family: lazy and greedy, `+`, `{2,}` (copy 1 is NOT under the rule),
the counter rung's `{8,}`/`{16,}`/`{17,}` (no residue and a residue),
nesting, a capture-wrapped loop, a backreference and a lookahead reading
the group, and the controls whose answers never moved: `*` (no mandatory
copy), a bounded `{1,3}` (PCRE2 replicates it: no rule at all), possessive
and atomic.

EVERY EXPECTATION IS LIBPCRE2'S (10.46 on the dev box), span and every
group, at every start position. python3 `re` keeps the OLD model on this
family (upstream_issues.md U21), so a block on which python disagrees in
any cell is `# pcre2-only`; one on which it agrees is left for the python
tier too. Each block is written on the default route and under `engine
vm`, the forced VM with no prefilter.
"""
import importlib.util, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
os.environ.setdefault("PCREC_PCRE2_PATH", "libpcre2-8.so.0")
_spec = importlib.util.spec_from_file_location(
    "pcre2_ctypes", os.path.join(ROOT, "docs/design/eng_brep_measurements/probes/pcre2_ctypes.py"))
p2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p2)

# (pattern, subjects, why)
CASES = [
 ("(?:()|a)+?b", ["ab", "aab", "b", "bab"],
  "iterd27 F4: iteration 1 = () is empty, so no iteration 2; the retreat into "
  "iteration 1 takes `a` and group 1 is never set"),
 ("((?:()|a)+?)b", ["ab", "aab"],
  "the same loop inside a capture: group 1 is the loop, group 2 unset"),
 ("(?:(?:()|a)+?b)+", ["abab", "abb", "bab"],
  "nested: each outer iteration's inner loop restarts the rule"),
 ("(?:a|()|b)+?c", ["abc", "bc", "c", "bbc"],
  "the empty branch second: reached only when `a` fails"),
 ("(?:()|ab|a)+?b", ["ab", "abb", "aab"],
  "three branches, two of them consuming"),
 ("(?:()|a){2,}?b", ["ab", "aab", "b", "aaab"],
  "{2,}: copy 1 is a plain copy, NOT under the rule; copy 2 is the loop's first"),
 ("(?:a|()|b){2,}?c", ["abc", "aabc", "bc", "abbc"],
  "{2,} where copy 1 consumes and copy 2, iteration m, is the empty one"),
 ("(?:a|()|b){8,}?c", ["aaaaaaabc", "aaaaaaaabc", "aaaaaaac"],
  "the counter rung, no residue at K = 8: the last trip's last copy is iteration m"),
 ("(?:a|()|b){16,}?c", ["a" * 15 + "bc", "a" * 16 + "bc"],
  "the counter rung, two trips, no residue"),
 ("(?:a|()|b){17,}?c", ["a" * 16 + "bc", "a" * 17 + "bc"],
  "the counter rung with a residue: the residue's last copy is iteration m"),
 ("(?:a|()|b){9,}c", ["a" * 8 + "bc", "a" * 9 + "c"],
  "the counter rung, greedy (control)"),
 ("(?:()|a)+?$", ["aa", "a", ""],
  "a zero-width continuation"),
 ("(?:()|a)+?\\1b", ["ab", "aab", "b"],
  "a backreference reads the group: unset fails, set-empty matches empty"),
 ("(?:(?=(a))|a)+?b", ["ab", "aab", "b"],
  "the empty branch is a lookahead that captures"),
 ("(?:()|a)+b", ["ab", "aab", "b"],
  "greedy: the answer never depended on the rule (control)"),
 ("(a?)+", ["", "a", "b", "aa"],
  "greedy, a capture-bearing nullable body (control)"),
 ("(|a)+", ["a", ""],
  "the design note's own witness: the empty iteration's writes STAND (control)"),
 ("(a*)*", ["a", "b"],
  "`*`: no mandatory copy, the loop's own guard (control)"),
 ("(?:()|a)*?b", ["ab", "aab"],
  "`*?`: no mandatory copy (control)"),
 ("(?:()|a){1,3}?b", ["ab", "aab"],
  "bounded: PCRE2 replicates, no rule at all (control)"),
 ("(?:()|a)++b", ["ab", "b", "aab"],
  "possessive: the first empty iteration ends the loop for good (control)"),
 ("(?>(?:()|a)+?)b", ["ab", "b"],
  "atomic around the lazy loop (control)"),
]


def esc(s):
    return "".join(c if 0x20 <= ord(c) < 0x7f and c not in "\\\"" else
                   ("\\\\" if c == "\\" else "\\x%02x" % ord(c)) for c in s)


def ngroups(pat):
    return re.compile(pat).groups if python_ok(pat) else pat.count("(") - pat.count("(?")


def python_ok(pat):
    try:
        re.compile(pat)
        return True
    except re.error:
        return False


def pcre_cell(cx, s, p, ng):
    r = cx.search(s, p)
    if not r:
        return None
    span, groups = r
    groups = tuple(groups) + (None,) * (ng - len(groups))
    return span, groups


def py_cell(rx, s, p):
    m = rx.search(s, p)
    if not m:
        return None
    return m.span(), tuple(None if m.span(g) == (-1, -1) else m.span(g)
                           for g in range(1, rx.groups + 1))


def main():
    check = None
    if "--check-pcrec" in sys.argv:
        check = sys.argv[sys.argv.index("--check-pcrec") + 1]
    out = [
        "# tests/captures/empty_iteration.rxt -- K128: the empty-iteration rule at an",
        "# unbounded repeat's LAST MANDATORY iteration (docs/dev/known_issues.md K128).",
        "# Written by gen_empty_iteration.py, whose header says what each row guards;",
        "# every expectation is libpcre2's, span and groups, at every start position.",
        "# A block python3 `re` disagrees with anywhere is `# pcre2-only` (U21). Each",
        "# block is written on the default route and under `engine vm`.",
        ""]
    npo = 0
    for pat, subjects, why in CASES:
        cx = p2.compile(pat)
        ng = ngroups(pat)
        cells = [(s, p, pcre_cell(cx, s, p, ng)) for s in subjects for p in range(len(s) + 1)]
        agree = python_ok(pat)
        if agree:
            rx = re.compile(pat)
            agree = all(py_cell(rx, s, p) == v for s, p, v in cells)
        npo += 0 if agree else 1
        for route in ("auto", "vm"):
            if not agree:
                out.append("# pcre2-only")
            out.append("# " + why + ("" if route == "auto" else " [engine vm]"))
            out.append("pattern " + pat)
            out.append("features all")
            if route == "vm":
                out.append("engine vm")
            for s, p, v in cells:
                if v is None:
                    out.append('ns %d "%s"' % (p, esc(s)))
                    continue
                out.append('ms %d "%s" %d %d' % (p, esc(s), v[0][0], v[0][1]))
                for g, gs in enumerate(v[1], 1):
                    out.append("g %d %d %d" % ((g,) + (gs if gs else (-1, -1))))
            out.append("")
    text = "\n".join(out)
    open(os.path.join(HERE, "empty_iteration.rxt"), "w").write(text)
    mism = check_with(check, text) if check else "not run"
    print(f"empty_iteration.rxt: {len(CASES)} cases x 2 routes, {npo} pcre2-only;"
          f" libpcre2 {p2.version()}; pcrec check failures {mism}")


def check_with(pcrec, text):
    """Runs the written file through the harness with `pcrec` and returns the
    failure count (a pre-existing divergence is reported, not hidden)."""
    path = os.path.join(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")), "empty_iteration.rxt")
    open(path, "w").write(text)
    r = subprocess.run(["bash", os.path.join(ROOT, "tests/harness/run.sh"), path],
                       env=dict(os.environ, PCREC=pcrec, SKIP_ORACLE="1"),
                       capture_output=True, text=True)
    fails = [ln for ln in r.stdout.splitlines() + r.stderr.splitlines() if "FAIL" in ln]
    for ln in fails[:20]:
        print("  " + ln)
    return len(fails)


if __name__ == "__main__":
    main()
