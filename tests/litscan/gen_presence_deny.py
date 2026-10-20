"""tests/litscan/gen_presence_deny.py -- writes presence_deny.rxt beside it:
[MEMFN] R17-b' B3b's presence links under the kit's three new denies
(b3brev finding 2, ruling (b); docs/dev/lanes/b3b_report.md §8). Re-run after
editing the case list:

    PCREC_PCRE2_PATH=libpcre2-8.so.0 \\
        python3 tests/litscan/gen_presence_deny.py [--check-pcrec BUILD/pcrec]

WHAT IT GUARDS. B3b removed `req_site_define`'s internal-error guard
against a handoff pre-check with a part AFTER its landmark (a whole run, or
a set member tested after the landmark's position is kept), because
`--memfn=no-fd-pres-pick` (the PRES row P9) now puts such parts on handoff
sites, and argued their soundness in the function's header instead: each
part is a fact every match holds in [lo, n), at the entry and at the
handoff's re-entry alike. These blocks are that argument's witnesses, the
review's scenario: a necessary byte that lies BELOW the scan position at
the re-entry (a set member before the byte landmark, `a.?b`, decoy
landmarks first so the scan re-enters), a necessary byte below the
REPORTED start (`\\K`), lookbehind-sourced bytes below the attempt (the
facts must not hold them), whole-run and rest members after a run window,
seeded and multibyte cases. `tests/memfn/run_presence.sh [deny-answers]`
runs this file, handoff.rxt and K65/K66's under each of the three denies;
the default route runs it as part of the corpus.

EVERY EXPECTATION COMES FROM AN ORACLE (gen_handoff.py's own helpers: a
`byte` block's from python3 `re` AND libpcre2, which must agree; a `utf8`
block's from libpcre2 under PCRE2_UTF | PCRE2_MATCH_INVALID_UTF alone, so
`# pcre2-only`; a byte block python cannot compile, \\K, likewise). Cells
sit at every character-boundary start position.
"""
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PCREC_PCRE2_PATH", "libpcre2-8.so.0")
_spec = importlib.util.spec_from_file_location("gen_handoff", os.path.join(HERE, "gen_handoff.py"))
gh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gh)

# (pattern, encoding, subjects, why)
CASES = [
 ("a.?b", "byte",
  ["bbbbab", "bbbbbbbbbbbbaxb", "bxbxbab", "zbzbzbazb", "ab", "aab", "ba", "bbbb",
   "abxab", "xyzab b", "ab ab ab", "bab", "b\nbab", "abbbbbbbb", "bbbbbbbba"],
  "byte landmark `b` (K = 2), the set member `a` BEFORE it: decoy landmarks first, so "
  "the forward scan RE-ENTERS the handoff, and P9 tests `a` from the re-entry's scan "
  "position: the review's necessary-byte-below-posvar scenario"),
 ("a{3}(?i:cat)", "byte",
  ["cat cat aaacat", "CAT aaxcat aaacat", "aacat", "aaaCAT", "aaacat", "aaaacat",
   "xcatxaaacat"],
  "run window `cat` (K = 3), the set member `a` before it, tested after the window "
  "under P9; decoy windows first"),
 ("é{2}cat", "utf8",
  ["cat éécat", "écat écat éécat", "éécat", "écat", "ééécat", "cat\xe9cat"],
  "the same under utf8: the set's two UTF-8 bytes of `é` before the window"),
 ("(?<=qz)x?a:", "byte",
  ["qza:", "qzxa:", "a: qza:", "zqa: qzxa:", "qz", "a:a:qza:", "qzqza:"],
  "LOOKBEHIND-sourced bytes `q`, `z` lie below the attempt start: the presence facts "
  "must not hold them (a start just past `qz` matches)"),
 ("(?<=q)a:", "byte",
  ["qa:", "a:qa:", "qxa:qa:", "a:", "qqa:"],
  "a lookbehind byte one below the attempt, K = 0"),
 ("a{2,4}\\Kb", "byte",
  ["ab aab", "aaaab", "b aab", "aaaaab", "aab", "ab"],
  "\\K: the necessary `a` lies below the REPORTED start (never below the attempt's)"),
 ("(?:a(?!q)|aq)x{0,3}q", "byte",
  ["aq", "axq", "aqxxxq", "q q aq", "axxxq", "qqqq axq"],
  "a lookahead in the prefix, the set member `a` before the landmark `q`"),
 ("foo(?:username|password|passphrase)bar", "byte",
  ["foousernamebar", "foo bar foopassphrasebar", "bar foo foopasswordbar", "foobar"],
  "run windows with set members in an alternation between them"),
 ("[a-c]{2,4}x[0-9]{2,4}y[A-C]{2,4}z[j-l]{2,4}w[x-z]{2,4}", "byte",
  ["abx12yABzjkwxy", "x1y w abx12yABzjkwxy", "abcx1234yABCzjklwxyz", "abx12yABzjkw"],
  "five byte landmarks, K = 14: every set member but the landmark is a part P9 adds"),
 ("x.y", "utf8",
  ["x€y", "€y x\U0001F600y", "y y xéy", "xy", "xééy"],
  "utf8, K = 5: the set member `x` before the landmark `y`, multibyte between"),
 ("ab?c", "byte",
  ["cccac", "c c abc", "acbc ac", "abbc", "c"],
  "the shortest: `a` before the byte landmark `c`, K = 2, decoys first"),
 ("a.{1,5}z", "byte",
  ["abz", "a1234z", "a123456z", "xaz", "azz", "abbbbbz az", "z a.z zz", "aaaaaz", "a\nz"],
  "the emit_sweep DIFFER_PINS manifest of the `--memfn=no-fd-pres-pick` arms: the pick "
  "deny moves this pattern's bytes, so the pin needs it in the corpus (pinfix_report.md)"),
]


def main():
    check = None
    if "--check-pcrec" in sys.argv:
        check = sys.argv[sys.argv.index("--check-pcrec") + 1]
    out = [
        "# tests/litscan/presence_deny.rxt -- [MEMFN] R17-b' B3b: the presence pre-check's",
        "# parts after the landmark, on handoff routes, as the kit's denies lay them out",
        "# (b3brev finding 2; docs/dev/lanes/b3b_report.md §8). Written by",
        "# gen_presence_deny.py; every expectation is an oracle's (python3 `re` AND libpcre2",
        "# for a `byte` block, libpcre2 alone for a `utf8` block or one python cannot",
        "# compile). Cells at every character-boundary start position. The default route",
        "# runs it in the corpus; tests/memfn/run_presence.sh [deny-answers] runs it under",
        "# --memfn=no-fd-pres-pick / no-fd-pres-g1 / no-pres-set-lead.",
        ""]
    for pat, enc, subjects, why in CASES:
        cells = []
        for s in subjects:
            b = gh.bsubj(s, enc)
            pc = gh.pcre_cells(pat, enc, b)
            if enc == "byte" and not gh.pcre2_only(pat):
                py = gh.py_cells(pat, b)
                for p, v in pc.items():
                    if py.get(p) != v:
                        sys.exit(f"ORACLES DISAGREE: {pat!r} {b!r} @{p}: pcre2 {v} python {py.get(p)}")
            cells.append((b, pc))
        if enc == "utf8" or gh.pcre2_only(pat):
            out.append("# pcre2-only")
        out.append("# " + why)
        out.append("pattern " + pat)
        out.append("features all")
        out.append("encoding " + enc)
        for b, pc in cells:
            for p, v in sorted(pc.items()):
                if v:
                    out.append('ms %d "%s" %d %d' % (p, gh.esc(b), v[0], v[1]))
                else:
                    out.append('ns %d "%s"' % (p, gh.esc(b)))
        out.append("")
    text = "\n".join(out)
    open(os.path.join(HERE, "presence_deny.rxt"), "w", encoding="utf-8",
         errors="surrogateescape").write(text)
    mism = "not run"
    if check:
        mism = check_with(check, text)
    print(f"presence_deny.rxt: {len(CASES)} cases; pcrec check failures {mism}")


def check_with(pcrec, text):
    """The written file through the harness with `pcrec`, default and each deny:
    the failure count summed (a divergence is reported, not hidden)."""
    path = os.path.join(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")), "presence_deny.rxt")
    open(path, "w", encoding="utf-8", errors="surrogateescape").write(text)
    import subprocess
    n = 0
    for fl in ("", "--memfn=no-fd-pres-pick", "--memfn=no-fd-pres-g1", "--memfn=no-pres-set-lead"):
        r = subprocess.run(["bash", os.path.join(gh.ROOT, "tests/harness/run.sh"), path],
                           env=dict(os.environ, PCREC=pcrec, SKIP_ORACLE="1", RXTFLAGS=fl),
                           capture_output=True, text=True)
        fails = [ln for ln in r.stdout.splitlines() + r.stderr.splitlines() if "FAIL" in ln]
        for ln in fails[:10]:
            print(f"  [{fl or 'default'}] " + ln)
        n += len(fails)
    return n


if __name__ == "__main__":
    main()
