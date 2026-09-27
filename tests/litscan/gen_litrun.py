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
 ("xy(a|ab)c", ["xyac","xyabc","xyab","xyc","qxyabcq"],
  "a run immediately followed by a choice point: the element after the run carries a resume frame"),
 ("ab", ["ab","a","b","ba","xxab"], "the shortest run, two bytes"),
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
"# single-child chains. The harness runs every file on both engines, so the",
"# VM side is what reads the converted compare.",
""]
for pat, subs, why in cases:
    out.append("# " + why)
    out.append("pattern " + pat)
    if "(?=" in pat: out.append("features lookaround")
    rx = re.compile(pat.encode('latin-1'))
    for s in subs:
        b = s.encode('latin-1')
        m = rx.search(b)
        esc = "".join(chr(c) if 0x20 <= c < 0x7f and c not in (0x5c, 0x22) else ("\\\\" if c == 0x5c else "\\x%02x" % c) for c in b)
        out.append('m "%s" %d %d' % (esc, m.start(), m.end()) if m else 'n "%s"' % esc)
    out.append("")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "litrun.rxt"), "w").write("\n".join(out))
