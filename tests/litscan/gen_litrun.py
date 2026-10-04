"""tests/litscan/gen_litrun.py -- writes litrun.rxt beside it, every expectation
from python3 `re` (the base-tier oracle). Re-run after editing the case list:
    python3 tests/litscan/gen_litrun.py
"""
import os, re
cases = [
 ("abcdef", ["abcdef","abcde","xxabcdef","abcdeX","","abcabcdef","xabcdefx","bcdef"],
  "a run that is the whole pattern: the bounds check at the subject's END (P8) -- one byte short never matches"),
 ("x(abc)defg", ["xabcdefg","xabcdef","xabdefg","zzxabcdefgzz","xabcdefgh"],
  "runs on either side of a capture: the A_CAP ends the first run and starts the second"),
 ("xyz(a|ab)c", ["xyzac","xyzabc","xyzab","xyzc","qxyzabcq"],
  "a run immediately followed by a choice point: the element after the run carries a resume frame"),
 ("ab", ["ab","a","b","ba","xxab"],
  "[OPT-LITSCAN F5, D127] a two-byte run: BELOW pcrec_lit_run's own floor, so the VM side reads the pre-S2a per-byte byte chain, not a compare"),
 ("abc", ["abc","ab","c","xabcx"],
  "[OPT-LITSCAN F5, D127] the shortest run that still takes the one-compare form, three bytes"),
 ("a\\x22b\\\\c\\?d", ["a\"b\\c?d","a\"b\\cd","xa\"b\\c?dx"],
  "bytes the C string literal must escape: a quote, a backslash and a question mark"),
 ("a\\?\\?=b", ["a??=b","a??b","a?=b"], "'??=' would be a trigraph if written raw"),
 ("\\x01\\x7f\\x80\\xfe", ["\x01\x7f\x80\xfe","\x01\x7f\x80","z\x01\x7f\x80\xfez"], "control and high bytes, written as octal escapes"),
 ("a\\x00b", ["a\x00b","ab","a\x00","xa\x00bx"], "a NUL inside the run: the compare length is a literal, never a string length"),
 ("\\x001", ["\x001","\x00","1"], "an octal escape followed by a digit byte"),
 ("a*bcd", ["aaabcd","aaabc","bcd","bc","xbcdx"], "a run after a star: every backtrack re-enters the compare"),
 ("^abc$", ["abc","abcd","xabc","abc\n"], "an anchored run between two assertions"),
 ("(?:abc)+d", ["abcd","abcabcd","abcab","abd","xabcabcdx"], "a run inside a repeated body"),
 ("(abc){2}x", ["abcabcx","abcx","abcabcabcx","abcabx"], "a run inside a counted, replicated group"),
 ("foo(?:username|password|passphrase)bar", ["foousernamebar","foopasswordbar","foopassphrasebar","foopassbar","foousernambar","xfoopassphrasebarx","foopasswor"],
  "an alternation island whose single-child trie chains are runs compared at their node's depth"),
 ("(?:alpha|alps|alp)x", ["alphax","alpsx","alpx","alphx","alx","zalpx"], "an island with a shared-prefix run and alternatives that end inside it"),
 ("AKIA|AGPA|AIDA|AROA", ["AKIA","AGPA","xAROAx","AKI","AROB","AIDAAKIA"], "four-byte alternatives that share a first byte: runs of three below the fan-out"),
 ("(?i)abc", ["abc","ABC","aBc","ab"], "caseless: every letter is a two-member class, so there is no exact run (S4 owns it)"),
 ("a[bc]de", ["abde","acde","ade","abdx"], "a class ends a run, so 'de' alone is one"),
 ("abc(?=def)", ["abcdef","abcde","abcxdef"], "a run before a lookahead"),
]
# [OPT-LITSCAN] S4 C1 (litscan_s4.md §1.3, §6.2): THE L-SWEEP. The run
# compare's `overlap` row writes two overlapping words at L in {3, 5-7, 9-15}
# and `memcmp` everywhere else, so every length 3..20, 31 and 32 is a cell,
# and every byte position is flipped once: a flip inside the overlap region
# must fail BOTH words, a flip at the last byte only the second. A subject one
# byte short at the end is P8's bound. Two shapes per length: the run alone
# (the VM's literal run; on the DFA the prefilter's run term or pre-check) and
# the run behind `[0-9]+` (a floating necessary run: the run pre-check).
POOL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
for L in list(range(3, 21)) + [31, 32]:
    run = POOL[:L]
    subs = [run, run[:-1], "zz" + run + "zz", run[1:]]
    subs += [run[:i] + "#" + run[i + 1:] for i in range(L)]
    cases.append((run, subs, "S4 L-sweep, L = %d: the run alone" % L))
    cases.append(("[0-9]+" + run, ["7" + s for s in subs] + ["x" + run],
                  "S4 L-sweep, L = %d: a floating necessary run" % L))
    # ...and the run alone ON THE VM: on the default route these patterns are
    # DFA artifacts, where the run compare is a prefilter term the DFA then
    # re-verifies, so a compare that ACCEPTS too much is invisible there. On
    # the VM the run compare is the only test of those bytes.
    cases.append((run, subs, "S4 L-sweep, L = %d: the run alone, forced VM" % L, "vm"))
out = ["# tests/litscan/litrun.rxt -- [OPT-LITSCAN] S2a: the VM's EXACT literal run",
"# (docs/design/patfacts/design.md §8.2; pcrec_lit_run in src/core/cpset.c).",
"#",
"# Every expectation below was produced by python3 `re` (the base-tier oracle)",
"# from the pattern text by this lane's generator, never hand-written. The",
"# shapes are the ones the mechanism has to get right: a run ending exactly at",
"# the subject's end and one byte short of it (P8's bounds check), bytes the",
"# emitted C string literal must escape (quote, backslash, '?', NUL, control",
"# and high bytes, an octal escape before a digit), a run beside a capture, a",
"# choice point, a star, a repeat and a lookahead, and the island's",
"# single-child chains. The harness runs each block on the route it is",
"# written for (the default route unless a block says `engine vm`), so the",
"# S4 L-sweep carries a forced-VM copy of each run: on the default route",
"# those patterns are DFA artifacts that re-verify any candidate.",
""]
for case in cases:
    pat, subs, why = case[:3]
    out.append("# " + why)
    out.append("pattern " + pat)
    if "(?=" in pat: out.append("features lookaround")
    if len(case) > 3 and case[3] == "vm": out.append("engine vm")
    rx = re.compile(pat.encode('latin-1'))
    for s in subs:
        b = s.encode('latin-1')
        m = rx.search(b)
        esc = "".join(chr(c) if 0x20 <= c < 0x7f and c not in (0x5c, 0x22) else ("\\\\" if c == 0x5c else "\\x%02x" % c) for c in b)
        out.append('m "%s" %d %d' % (esc, m.start(), m.end()) if m else 'n "%s"' % esc)
    out.append("")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "litrun.rxt"), "w").write("\n".join(out))
