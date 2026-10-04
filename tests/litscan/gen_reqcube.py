"""tests/litscan/gen_reqcube.py -- writes reqcube.rxt beside it, every `m`/`n`/
`ms`/`ns` expectation from python3 `re` (the base-tier oracle); the `gu` cells
are the budget CONTROLS and the one `# pcre2-only` block is stated in the
file's header with its 10.46 probe. Re-run after editing the case list:
    python3 tests/litscan/gen_reqcube.py

[OPT-LITSCAN] S4 C3, the caseless necessary run (docs/design/litscan_s4.md
§2.3, §5.1's planned cells). Every block is written TWICE, on the default
route and under `engine vm`, because the pre-check is emitted into both
engines' search entries and the routes differ in what else proves absence.
"""
import os, re

# (pattern, cells, why[, directives]) -- a cell is a subject (searched from 0)
# or (startpos, subject); directives are extra head lines for the block.
cases = [
 # ---- the alternation hull (S1), both branch orders, head and tail (S450) ----
 ("(?:S(?i:ab)|(?i:sab))", ["sab", "SAB", "Sab", "xsAbx", "ab", "zab"],
  "S1 head, branch order A: the common head is the CUBE HULL [Ss][Aa][Bb], never the left branch's exact S (S450 keeps the left mask and deletes 'sab')"),
 ("(?:(?i:sab)|S(?i:ab))", ["sab", "SAB", "Sab", "xsAbx", "ab", "zab"],
  "S1 head, branch order B: the hull is symmetric, so the order cannot change the answer"),
 ("(?:(?i:ab)S|(?i:abs))", ["abs", "ABS", "abS", "xaBsx", "ab", "abz"],
  "S1 tail, branch order A"),
 ("(?:(?i:abs)|(?i:ab)S)", ["abs", "ABS", "abS", "xaBsx", "ab", "abz"],
  "S1 tail, branch order B"),
 ("frank|fred", ["fred", "frank", "frx", "fre", "xxfrankxx", "FRED"],
  "the exact-branch hull: frank|fred reports the masked run fr[ae] (class C of the census)"),
 # ---- the kept pins (R2-C3): the run-pinned prefilter row reads an exact stretch ----
 ("a[bc]de", ["abde", "acde", "ade", "adde", "abd", "zzacdezz", "aXde"],
  "a[bc]de: the run is a[bc]de, the pin the exact stretch 'de' (run_pin 2:2+2); S447 compares the whole window exactly at the pin and deletes 'acde'"),
 ("(?i)x/1234", ["x/1234", "X/1234", "y/1234", "x/123", "--X/1234--", "x/1234x/1234"],
  "(?i)x/1234: the run X/1234 masked at x, the pin the exact stretch '/1234' (run_pin 1:1+5), G1 dominated"),
 # ---- REQ_BYTE from an exact member only (S2a) ----
 ("(?i:select)\\d+x", ["SELECT12x", "select12", "sElEcT1x", "select1y", "xx SeLeCt999x"],
  "S2a: the masked run's scan member is a pair, so REQ_BYTE is the set's pick (x, 120), never T"),
 # ---- the pair arm: re-search bound (S449), dispatch (S453), guard (S454) ----
 ("(?i)select", ["selecX select", "SELECXSELECT", "xSelEcT", "C c xc seleCt", "sel ect SELECT"],
  "S4 re-search: each first scan hit fails its verify, so the next candidate must come from a stream re-searched past it (S449's `< pos` bound hangs; the watchdog is the detector)"),
 ("(?i)select", ["select", "xselectx", "seLecT", "selectselect", (3, "selectselect"), (1, "select"), (6, "SELECTselect")],
  "the dispatch, LOWERCASE subjects: a masked scan position is scanned on BOTH its members (S453 scans T alone and deletes every lowercase match)"),
 ("(?i)select", ["", "s", "abc", "selec", "ELECT", "select", "selectx", "XSELECT"],
  "empty and short subjects (n = 0..7; n = 6 = MAXK + 1 is the first length that enters the loop): every search sits inside the guarded loop (S454 hoists one above it)"),
 # ---- the whole run at the K66 site (S448), with its short subjects ----
 ("(x?)(?i:abcdefghijkl)\\1", ["abcdefghijkl", "ABCDEFGHIJKL", "zaBcDeFgHiJkLz", "", "abcdefghijk", "abcdefghijkL", "xabcdefghijklx"],
  "the K66 site: a VM route with no DFA scan and a 12-position run, so the whole run is its own block; S448 compares it unmasked and deletes the lowercase and mixed matches",
  ["features backrefs,modifiers"]),
 # ---- the general mechanism: lengths, mixed words, one stream vs two ----
 ("(?i)abc", ["abc", "ABC", "aBc", "ab", "xxAbCxx", "ab c"],
  "three caseless letters (21 bits) clear the 16-bit floor: the shortest masked run"),
 ("(?i)sel(?:ab)*ect", ["select", "SELECT", "selabect", "SELABABECT", "selaect", "xxSeLeCtxx"],
  "a min-0 repeat between two caseless runs: nothing joins across it (S446 joins the body and deletes 'select', the zero-iteration match)"),
 ("(?i)ab", ["ab", "AB", "a", "xaBx"],
  "two caseless letters (14 bits) do not: no run, the per-byte path"),
 ("(?i)foo-bar", ["foo-bar", "FOO-BAR", "fOo-BaR", "foo_bar", "x-y FOO-BAR", "foo-ba"],
  "an exact member in the run: under the default rate the scan is the exact '-', one stream, with a masked verify"),
 ("(?i)foobar", ["foobar", "FOOBAR", "FoObAr", "fooba", "xx fOOBAr", "foo bar"],
  "all letters: the scan is a pair, two streams"),
 ("(?i)group_concat", ["group_concat", "GROUP_CONCAT", "Group_Concat", "group-concat", "groupconcat", "xxGROUP_concatxx", "group_conca"],
  "a 12-position run with an exact '_' inside a masked word (its mask byte is 0xFF)"),
 ("(?i)information_schema", ["information_schema", "INFORMATION_SCHEMA", "Information_Schema", "information-schema", "information_schem", "x.INFORMATION_schema.y"],
  "a 20-position run, windowed to 8 positions; the window is compared masked"),
 ("(?i)union.*?select.*?from", ["union select a from b", "UNION SELECT A FROM B", "uNiOn x SeLeCt y FrOm", "union select", "select from union", "xx union/**/select/**/from"],
  "union-select, the one measured customer: the run SELECT (42 bits) outranks UNION (35) and FROM (28); REQ_BYTE none, REQ_WHY emitted"),
 ("(?<=ab)(?i:cdef)", [(2, "abcdef"), (2, "abCDEF"), (2, "xxcdef"), "abcdef", "zzabCdEfzz"],
  "a caseless run starting at startpos, its context inside a lookbehind's span",
  ["features lookaround,modifiers"]),
]

# ---- S2b: done[] marks only EXACT positions (S451); NOMATCH -> give-up is the DEFECT ----
S2B = "(x?)([a-z]+)+S\\d(?i:select)\\1"
S2B_WHY = ("S2b: K65's second half must still memchr every set member the run does not prove; "
           "select's first position's T is 'S', the set's one member, so marking T done (S451) "
           "turns these n cells into step give-ups")
S2B_CELLS = ["a" * 16 + "1select", "a" * 17 + "1select", "a" * 18 + "1select", "abcS1SeLeCt"]
S2B_GU = "a" * 18 + "Sx1select"
# [K82] S2b's 'S' now LEADS the run (it is rarer than the scan pair), so the
# set-leads row tests it whatever K65's rest does. S2c keeps the defect
# reachable: its run [sS]qz scans the exact 'z' (498 ppm) and 'S' (4203) is
# commoner, so 'S' leads nothing and only K65's rest memchrs it -- the pair
# position's T that S451/S452 would mark done.
S2C = "(x?)([a-z]+)+S\\d(?i:s)qz\\1"
S2C_WHY = ("S2c ([K82]): S2b's shape with 'S' commoner than the run's exact scan byte 'z', "
           "so no set-leads row fires and K65's rest alone memchrs 'S', the T of the run's "
           "pair position; marking T done (S452) turns these n cells into step give-ups")
S2C_CELLS = ["a" * 16 + "1sqz", "a" * 17 + "1sqz", "a" * 18 + "1sqz", "abcS1Sqz", "abcS1sqz"]
S2C_GU = "a" * 18 + "Sx1sqz"


def esc(b):
    return "".join(chr(c) if 0x20 <= c < 0x7f and c not in (0x5c, 0x22)
                   else ("\\\\" if c == 0x5c else "\\x%02x" % c) for c in b)


def cell(rx, c):
    pos, s = c if isinstance(c, tuple) else (0, c)
    b = s.encode("latin-1")
    m = rx.search(b, pos)
    if pos:
        return 'ms %d "%s" %d %d' % (pos, esc(b), m.start(), m.end()) if m else 'ns %d "%s"' % (pos, esc(b))
    return 'm "%s" %d %d' % (esc(b), m.start(), m.end()) if m else 'n "%s"' % esc(b)


out = [
"# tests/litscan/reqcube.rxt -- [OPT-LITSCAN] S4 C3: THE CASELESS NECESSARY RUN",
"# (docs/design/litscan_s4.md §2.3; src/facts/req.c, src/gen/emit_dfa.c's pair arm,",
"# src/gen/runcmp.c's masked rows; docs/spec/tuning.md §2.28, §2.39).",
"#",
"# Written by gen_reqcube.py; every m/n/ms/ns expectation was produced by python3",
"# `re` from the pattern text, never by hand. Every block appears twice, on the",
"# default route and under `engine vm`, because the run pre-check is emitted into",
"# both engines' search entries. The cells are the design's planned witnesses",
"# (§5.1's table): the alternation cube hull in both branch orders, head and tail;",
"# the kept exact-stretch pins; REQ_BYTE from an exact member only; the pair arm's",
"# re-search bound, its dispatch (LOWERCASE subjects: an uppercase subject cannot",
"# see a scan of T alone) and its guard (subjects of length 0..7); the whole run",
"# at the K66 site; and the S2b give-up witness, where NOMATCH -> give-up is the",
"# defect direction. The `gu` cells are budget CONTROLS: with every necessary",
"# byte and the run present no pre-check can help, so they prove the `n` cells",
"# pass because of the pre-check rather than because 10000 steps sufficed.",
"#",
"# THE ONE `# pcre2-only` BLOCK is the review's exact S2b witness at L = 30",
"# (`\"a\" x 30 + \"1select\"`): python `re` backtracks exponentially there, a",
"# TIME exclusion, not a semantic divergence (its L = 16..18 twins above are",
"# python-verified). Its `n` follows from absence alone (`S` is necessary and",
"# absent). libpcre2 10.46, probed once on the reference box over the tailnet",
"# (lane c3build, 2026-10-03): L = 16 and 18 answer NOMATCH (-1), L = 30 answers",
"# PCRE2_ERROR_MATCHLIMIT (-47) -- its own required code unit is the caseless",
"# `t`, which is present, so it backtracks too; `abcS1SeLeCt` matches (0, 11).",
"# pcrec answers NOMATCH at every length, by K65's memchr('S').",
""]

for case in cases:
    pat, cells, why = case[:3]
    extra = case[3] if len(case) > 3 else []
    rx = re.compile(pat.encode("latin-1"))
    for route in ("auto", "vm"):
        out.append("# " + why + ("" if route == "auto" else " [engine vm]"))
        out.append("pattern " + pat)
        out.extend(extra)
        if route == "vm":
            out.append("engine vm")
        out.extend(cell(rx, c) for c in cells)
        out.append("")

rx = re.compile(S2B.encode("latin-1"))
for enc in ("byte", "utf8"):
    for route in ("auto", "vm"):
        out.append("# " + S2B_WHY + " [encoding %s%s]" % (enc, "" if route == "auto" else ", engine vm"))
        out.append("pattern " + S2B)
        out.append("features backrefs,classes,modifiers")
        out.append("encoding " + enc)
        if route == "vm":
            out.append("engine vm")
        out.append("budget steps=10000")
        out.extend(cell(rx, c) for c in S2B_CELLS)
        out.append('gu steps "%s"' % esc(S2B_GU.encode("latin-1")))
        out.append("")

rx = re.compile(S2C.encode("latin-1"))
for route in ("auto", "vm"):
    out.append("# " + S2C_WHY + " [encoding byte%s]" % ("" if route == "auto" else ", engine vm"))
    out.append("pattern " + S2C)
    out.append("features backrefs,classes,modifiers")
    out.append("encoding byte")
    if route == "vm":
        out.append("engine vm")
    out.append("budget steps=10000")
    out.extend(cell(rx, c) for c in S2C_CELLS)
    out.append('gu steps "%s"' % esc(S2C_GU.encode("latin-1")))
    out.append("")

out.append("# S2b, the review's exact witness at L = 30 (see the header: a python TIME")
out.append("# exclusion; libpcre2 10.46 answers MATCHLIMIT, pcrec NOMATCH by K65's memchr).")
out.append("# pcre2-only")
out.append("pattern " + S2B)
out.append("features backrefs,classes,modifiers")
out.append('n "%s"' % ("a" * 30 + "1select"))
out.append("")

open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqcube.rxt"), "w").write("\n".join(out))
