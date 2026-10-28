"""tests/litscan/gen_handoff_vm.py -- writes handoff_vm.rxt beside it: [REQRUN-VM],
THE HANDOFF ON THE VM ROUTES' witnesses (docs/dev/lanes/reqvm0_report.md, the
VM soundness rule and its probes; docs/spec/tuning.md §2.41). Re-run after
editing the case list:

    PCREC_PCRE2_PATH=/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 \\
        python3 tests/litscan/gen_handoff_vm.py [--check-pcrec BUILD/pcrec]

The oracles, the cell grid (every character-boundary start position) and the
writer are gen_handoff.py's, imported, so the two files cannot disagree on
what an expectation is. A block names its ROUTE: `vm` is `engine vm` (the VM
with no DFA scan in front, where the attempt loop itself hands off and
re-enters, `handoff-attempts[-entry]`); `auto` is the default route of a
pattern with a capture group, the VM HYBRID, whose prefilter's forward scan
re-enters (`handoff`). A block's optional directives (a `budget`) are
written after `features all`.

THE GIVE-UP WITNESS. `(a|aa){0,10}cxyz` under `budget steps=3000` is
reqvm0's P1 in a shape whose MATCH is cheap: from startpos 0..7 the attempts
on the decoy `a` run exhaust the step budget under `-fno-req-handoff` (it
gives up, `PCREC_ERR_STEPS`), and with the handoff the whole run's first
hit, less K = 20, starts the loop past them, so it answers libpcre2's
(unbounded) answer. (reqvm0's own `(a?){12}a{12}xyz` also gives up inside
the matching attempt under `-fno-length-prune`, so it would move that axis
too; this one moves only `-fno-req-handoff` and the two denies that remove
the pre-check, `-fno-req-byte` and `-fno-req-run`, measured.) The corpus cells are that
answer; the deny arm's give-ups are run_axes.sh's GIVEUP1 manifest entries
for those three flags (one direction only, tuning.md §2.41¶9a).
"""
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("gen_handoff", os.path.join(HERE, "gen_handoff.py"))
gh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gh)

X = "\U0001F600"
URL7 = ("(https://www\\.(?:acme|globex|initech|umbrella|hooli)\\.(com|de|fr|nl|org)/[^\"?\\s]*)"
        "(?:(\\?(?:[^\"\\s]*&)?tld=)(?!\\2\\b)[a-z]+|(?!\\?(?:[^\"\\s]*&)?tld=)(\\?[^\"\\s]*)?(?=\"))")
RARE2 = "/(phpmyadmin|wp-admin)/[a-z]+\\.php"

# (pattern, encoding, route, subjects, why[, extra directives])
CASES = [
 # ---- the give-up witness (the ruling's one-way movement) ----
 ("(a|aa){0,10}cxyz", "byte", "vm",
  ["a" * 20 + "b" + "q" * 30 + "cxyz", "aacxyz", "cxyz"],
  "GIVE-UP WITNESS: under -fno-req-handoff startpos 0..7 of the first subject give up (steps); "
  "the handoff starts the loop at the whole run's hit less K = 20 and answers (one direction only)",
  ["budget steps=3000"]),
 # ---- the maximum offset and two occurrences, VM-only re-entered ----
 ("(?:xx|y)abc", "byte", "vm",
  ["zxxabc", "yabc", "xabcyabc", "zabczabcxxabc", "xyabc", "abcabcxxab"],
  "VM-only, K = 1 from the wider branch; dense dead `abc` hits re-enter after each failed attempt"),
 ("x{2,5}(?i:cat)", "byte", "vm",
  ["xxxxxCaT", "zxxxxxcat", "xxcat xxcat", "xxcatxxxxxcat", "xcat"],
  "VM-only ENTRY ONLY (`x` is a set-rest byte the run does not hold): K = 5"),
 # ---- \G keeps search_from (V2); the attempt position alone moves ----
 ("(?:\\Gab|x)(cat)dog", "byte", "vm",
  ["zzabcatdog", "abcatdog", "zxcatdog", "zzabcatdogxcatdog"],
  "\\G before the run (reqvm0 P4): NOMATCH from 0 on zzabcatdog; a \\G reading the moved start reports (2,10)"),
 ("(?:\\Gab|x)abc", "byte", "vm",
  ["xxabcab", "ababc", "abcxabc"],
  "\\G matching at the startpos (reqvm0 P3)"),
 # ---- lookbehind before the run (Claim 2: the body reads below lo) ----
 ("(?<=q.)ab", "byte", "vm",
  ["qzab", "zqzab", "qzabqab", "ab"],
  "a lookbehind before the run (reqvm0 P2): the attempt reads below the moved start"),
 # ---- utf8: the moved start rounds up to a character start (V3) ----
 (".cd", "utf8", "vm",
  ["\u20ac\u20accd", "x\u20accd", X + "cd", "cd", "\u00e9cd\u20accd"],
  "utf8, K = 4 (reqvm0 P5): c - K lands inside a character and rounds up"),
 (".{3}cat", "utf8", "vm",
  [X * 3 + "cat", "\u20ac\u20ac\u20accat", "a" + X * 3 + "cat", X + "cat"],
  "utf8, K = 12: three characters of up to four bytes"),
 (".{1,3}cd", "utf8", "vm",
  [b"\x80\x80\x80\x80\x80cd", b"ab\x80\x80\x80\x80cd", b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80xcd"],
  "utf8, ill-formed text before the run: c - K among continuation bytes"),
 # ---- caseless under utf8: K in BYTES on the lowered tree ----
 ("(?i)stra", "utf8", "vm",
  ["x\u017ftra", "\u017f\u017ftra", "stra", "xSTRA", "\u00e9\u017fTRA"],
  "caseless utf8 (reqvm0 P6): (?i)s matches U+017F, two bytes, so K = 2, not 0"),
 ("(?i)stra", "byte", "vm",
  ["x\u00ff\u00fftra", "stra", "xSTRA"],
  "the same pattern under -e byte: K = 0"),
 # ---- \K: K from the attempt start ----
 ("ab\\Kcd", "byte", "vm",
  ["abcd", "zabcd", "abxabcd"],
  "\\K: the reported start may exceed the moved start"),
 # ---- declines: an unbounded K, one attempt ----
 ("(a)\\1xyz", "byte", "vm",
  ["aaxyz", "zaaxyz", "axyz"],
  "decline: a backreference before the run (K unbounded)"),
 ("a+xyz", "byte", "vm",
  ["aaaaxyz", "zaxyz", "xyz"],
  "decline: an unbounded prefix (a+) before the run"),
 ("^abcd", "byte", "vm",
  ["abcd", "zabcd"],
  "decline: one attempt (^)"),
 # ---- bench subst case 7's shape, small (VM-only, run at offset 0) ----
 (URL7, "byte", "vm",
  ['"https://www.acme.com/a?tld=de" x', '"https://www.hooli.org/" "https://www.acme.de/b?x=1&tld=de"',
   'GET https://www.initech.fr/?tld=nl" https://www.globex.nl/p"'],
  "bench subst case 7's pattern (url-tld-fix), VM-only: the whole run https://www. at offset 0 drives every attempt"),
 # ---- the VM HYBRID: the prefilter's forward scan re-enters ----
 (RARE2, "byte", "auto",
  ["/a/b/c/wp-admin/setup.php", "/x/admin/ /phpmyadmin/index.php", "/admin//wp-admin/a.ph /wp-admin/b.php",
   "GET /wp-admin/ x /phpmyadmin/s.php"],
  "bench subst case 2's pattern (rare), the VM hybrid: dense '/' and dead admin/ hits re-enter inside the prefilter"),
 ("(ab)c?userpass", "byte", "auto",
  ["userpass userpass abuserpass", "abcuserpas abcuserpass", "xabuserpassabcuserpass"],
  "the hybrid's prefilter re-entry over dead landmark hits"),
]


def main():
    check = None
    if "--check-pcrec" in sys.argv:
        check = sys.argv[sys.argv.index("--check-pcrec") + 1]
    out = [
        "# tests/litscan/handoff_vm.rxt -- [REQRUN-VM], THE HANDOFF ON THE VM ROUTES:",
        "# the VM attempt loop with no DFA scan (`engine vm`) starts at the whole",
        "# run's first hit less K and re-enters it after each failed attempt; the VM",
        "# hybrid's prefilter re-enters it inside its forward scan (tuning.md §2.41).",
        "#",
        "# Written by gen_handoff_vm.py with gen_handoff.py's oracles: a `byte`",
        "# block's cells from python3 `re` AND libpcre2 (which must agree), a",
        "# `utf8` block's (and \\G, \\K) from libpcre2 alone (`# pcre2-only`), at",
        "# EVERY character-boundary start position. The rows are reqvm0's probes:",
        "# the give-up witness (its deny arm's give-ups are run_axes.sh's GIVEUP1",
        "# entries), \\G before the run, a lookbehind, utf8 round-up, caseless K in",
        "# bytes, \\K, the declines, and bench subst cases 7 and 2 on small subjects.",
        ""]
    for case in CASES:
        pat, enc, route, subjects, why = case[:5]
        extra = case[5] if len(case) > 5 else []
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
        out.extend(extra)
        out.append("encoding " + enc)
        if route == "vm":
            out.append("engine vm")
        for b, pc in cells:
            for p, v in sorted(pc.items()):
                if v:
                    out.append('ms %d "%s" %d %d' % (p, gh.esc(b), v[0], v[1]))
                else:
                    out.append('ns %d "%s"' % (p, gh.esc(b)))
        out.append("")
    text = "\n".join(out)
    mismatches = gh.check_with(check, text) if check else None
    open(os.path.join(HERE, "handoff_vm.rxt"), "w", encoding="utf-8",
         errors="surrogateescape").write(text)
    print(f"handoff_vm.rxt: {len(CASES)} blocks;"
          f" pcrec check mismatches {mismatches if check else 'not run'}")


if __name__ == "__main__":
    main()
