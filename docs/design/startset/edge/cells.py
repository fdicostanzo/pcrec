#!/usr/bin/env python3
"""[START-SET] edge lane (ssedge): THE AUTHORED EDGE CELLS.

This is the hand-written half: a pattern, its compile options, the subjects,
and WHY (which edge of the DFA-hat / VM-hat argument the block sits on).
Every answer is the ORACLE's, written by `gen_rxt.py` (libpcre2; every
startpos that is a character boundary of the subject), never typed here.

Fields: file (the draft .rxt it lands in), pat, flags (i/u), enc, engine,
frames (--backtrack-frames), xflags (extra pcrec flags; `-futf-check` blocks
go to utfcheck_cells.tsv, `-fprefilter-collapse` blocks to a config/target
head), subj (list of bytes), edge (category key, startset.md §6.4), why.
`name` gives a block a definition name (only where a target needs one).
"""

def B(file, pat, subj, edge, why, **kw):
    d = {"file": file, "pat": pat, "subj": [s if isinstance(s, bytes) else s.encode("latin-1") for s in subj],
         "edge": edge, "why": why, "flags": "", "enc": "byte", "engine": None, "frames": None, "xflags": []}
    d.update(kw)
    return d

U = lambda s: s.encode("utf-8")          # a utf8 subject written as text

CELLS = [
# ---------------------------------------------------------------- W: the six sound-F1 corpus witnesses
# Each is DECLINED by the ruled rule (S ⊄ E, so T = S is not ⊊ E) and ADMITTED by r3's
# S ∩ E: these blocks are where "T = S ∩ E" and "E* without its non-s0 seed" are seen.
B("witnesses", r"(?:(?<=a)z|w)", ["aza", "az", "xaz", "azw", "aaz", "za", "waz", "zaz", "aaaz", "awz", ""],
  "W", "matrix.rxt:1064; S\\E = {z}: z begins a match only in the a-context the skip reaches by leaving s0"),
B("witnesses", r"(?:(?<*a)z|w)", ["aza", "az", "xaz", "awz", "za"], "W", "matrix.rxt:2597, the non-atomic spelling"),
B("witnesses", r"(?:(?<=[ab])z|w)", ["aza", "bz", "bzb", "xbz", "abz", "zb"], "W", "matrix.rxt:1122; a two-byte context class"),
B("witnesses", r"(?:(?<*[ab])z|w)", ["aza", "bz", "xbz", "zb"], "W", "matrix.rxt:2662"),
B("witnesses", r"(?<=a)b|(?<=bc)d", ["aba", "ab", "bcd", "xbcd", "abcd", "bcdx", "cbcd", "bd", "acd"], "W",
  "lookbehind.rxt:212; a HYBRID: the prefilter's skip loses the start, the VM never runs"),
B("witnesses", "(?m)(?<=\\n)a|b$", ["\naa", "\na", "x\na", "b", "ab", "b\n", "\nab", "a\nb", "aa"], "W",
  "ucp/ctxnode.rxt:400; the newline context"),
B("witnesses", r"(?:(?<=a)z|(?<=b)y|w)", ["az", "by", "xaz", "xby", "abyaz", "bz", "ay", "w"], "W3",
  "THREE seed states (s0, a-ctx, b-ctx), S\\E = {y,z}: E* without any ONE seed is still 256 here, so the "
  "omit-one-seed mutant is the identical table; r3's S ∩ E = {w} loses both"),
B("witnesses", r"(?:\b|x)y", ["xy", " xy", "zxy", "y", " y", "zy"], "W",
  "S\\E = {x} but Tdfa = {y}: x is a CONTEXT here (its own class), never a thread start; r3's set is "
  "UNSOUND only where an S\\E byte is in Tdfa, and this block is the control that it is not always"),
B("witnesses", r"(?:\bab|x)", [" ab", "ab", "zab", "xab", " x", "abab", " ax ab", "babx"], "S0",
  "a 2-seed MOVER where E* WITHOUT s0 drops a: a begins a match only from the nonword context, so a set "
  "built from the word-context seed alone skips the start at 1 of ' ab'"),
B("witnesses", r"(?:\Bab|x)", ["zab", "ab", " ab", "zzab", "x", "zx", "xz"], "S0", "the \\B polarity of the s0 omission"),

# ---------------------------------------------------------------- LB: lookbehind context across the skip
B("lookbehind", r"\b(?:(?<=bc)d|w)", ["bcd", " bcd", "bc d", "abcd", "w", " w", "xw", "bcw", "d", " d"], "LB2",
  "a hybrid MOVER (T = {d,w}): the two-byte context bc spans the skipped bytes; the prefilter erases the "
  "lookbehind and the VM verifies"),
B("lookbehind", r"(?<=ab)z|\bw", ["abz", "xabz", "ab z", "az", "bz", "w", " w", "abw", "zabz", "abza"], "LB2",
  "a hybrid mover; the two context bytes are both skipped (neither is in T = {z,w})"),
B("lookbehind", r"\b(?<=bc)d", ["bcd", "bc d", "abcd", " bcd", "d", "xbcd", " d", "cd", "abcdd"], "LB2",
  "|T| = 1 hybrid mover: the first-memchr-BOUNDED form, both landing paths (a hit, or clamped to n-1)"),
B("lookbehind", r"(?<=abc)d|\bx", ["abcd", "xabcd", "abd", "bcd", "x", "abcx", " x", "abcda"], "LB3", "three context bytes"),
B("lookbehind", r"(?:(?<=b(?<=ab)c)d|\bw)", ["abcd", "xbcd", "bcd", "aabcd", "w", "abcw", "abcda"], "LBN",
  "NESTED lookbehind: (?<=ab) inside (?<=b..c), context three bytes back"),
B("lookbehind", r"(?:(?<=b(?<=ab)c)d|(?<=a)z)", ["abcd", "az", "xbcd", "aza", "abcdaz"], "LBN",
  "nested lookbehind beside a one-byte context: a seeded hybrid, S\\E = {z} (declined; r3 admits it)"),
B("lookbehind", r"(?:(?<!a)z|w)", ["az", "z", "xz", "aw", "aaz", "zaz", "bz", "azz", "wa"], "LBNEG",
  "a NEGATIVE one-byte lookbehind: a DFA mover; the skipped a must suppress z"),
B("lookbehind", r"(?:(?<![ab])z|w)", ["az", "bz", "cz", "z", "abz", "cbz", "azz", "za"], "LBNEG", "negative, class context"),
B("lookbehind", r"(?:(?<=a)z|(?<=b)y|w)", ["xxaz", "bbby", "abaz", "bay", "aaaaz", "azx"], "LBK",
  "k context-changing bytes before the S\\E byte: only the LAST skipped byte's class reaches the re-seed"),
B("lookbehind", r"(?:(?<=a)z|w)", ["bbbaz", "abbbz", "babaz", "aaaz", "baz", "azb"], "LBK",
  "k skipped bytes: the context is set, reset, set again before z"),
B("lookbehind", r"\b(?:ab|cd)\b|(?<=x)z", ["xz", "abxz", "ab xz", " xz", "cd", "xcd", "zxz", "xzx"], "LBK",
  "a 3-seed MOVER (nonword, word, x): the x context is a word byte too"),

# ---------------------------------------------------------------- WB: \b / \B, both polarities, ASCII and --ucp
B("wordb", r"\b(?:ab|cd)\b", ["bab ab", "ab", " ab ", "xab ab", "abab", "cd!", "atrue ab", "a ab", "_ab ab", "9ab ab"], "WB",
  "the twin table's pattern: re-seed removed loses (4,6) of 'bab ab'"),
B("wordb", r"\B(?:ab|cd)\B", ["xabx", "ab", " abx", "xab", "xxabxx", "a abx", "_ab_"], "WB", "\\B both sides"),
B("wordb", r"\b(?:ab|cd)\B", ["abx", "xabx", " abx", "ab", "ab abx"], "WB", "\\b then \\B"),
B("wordb", r"\B(?:ab|cd)\b", ["xab", "ab", "xab ", " ab", "xxab"], "WB", "\\B then \\b"),
B("wordb", r"\b(?:ab|cd)\b", ["\xe9ab ab", "ab\xe9", "\xe9ab", " ab\xe9 ab", "\xaaab ab"], "WBU",
  "--ucp under byte: 0xE9 (é) and 0xAA (ª) are WORD bytes, so the skipped byte's class differs from ASCII",
  flags="u"),
B("wordb", r"\B(?:ab|cd)\B", ["\xe9ab\xe9", "ab", " ab\xe9", "\xe9ab "], "WBU", "\\B under --ucp", flags="u"),
B("wordb", r"\b(?:ab|cd)\b", ["bAB AB", "Ab", "xab AB", "CD", "aB ab"], "CI",
  "caseless: T has the case twins; the skipped context byte's case is irrelevant to \\b", flags="i"),
B("wordb", r"(?i)\bcat\b", ["ccat cat", "xcat", "cat", "acat CAT", "c cat", "Cat"], "HO",
  "a K82 HANDOFF mover (REQ_HANDOFF 0): the scan starts at max(startpos, c - K); its s[startpos] is in T"),
B("wordb", r"\b[a-z_][a-z0-9_]{0,31}=\"(?:[^\"\\]|\\.)*\"", ["x=\"a\"", " ab=\"\"", "9a=\"b\"", "a b=\"\"", "=\"\" a=\"\""], "HO",
  "kv-quoted (bench), REQ_HANDOFF 32"),

# ---------------------------------------------------------------- RS: the re-seed's FORM (sound-F7 measured, not argued)
# search_uncond.py found these DFA-hat MOVERS (84 random-family movers, 6 hits): state 0 is RE-ENTERED mid-scan
# through a byte whose seed is NOT state 0 (here: after "xy", the machine is back in s0's class), so
# pf_emit_ofs_reseed's UNCONDITIONAL `pos ? seed[..] : s0` overwrites a correct state 0 when the skip did not move.
# The conditional form (re-seed only if the scan moved) is REQUIRED on ordinary seeded machines, not only on \G ones.
B("reseed", r"(?:\b|xy)a", ["xya", "zxya", " xya", "a", "xa", "xyxya", "ax", "ya a"], "RS", "uncond re-seed loses (0,3) of 'xya'"),
B("reseed", r"(?:\b|z[xy])y", ["zxy", "azxy", "zyy", " zxy", "yz", "xy y"], "RS", "uncond re-seed loses 'zxy'"),
B("reseed", r"(?:  |\b| xy)y", [" xyy", "  y", "a xyy", "y", "y ", "xy y"], "RS", "uncond re-seed loses ' xyy'"),
B("reseed", r"(?:\b(?<!a)|xxy)a", ["xxya", "axxya", "ba", "xxyxxya", "yaxxya"], "RS", "uncond re-seed loses 'xxya'"),
B("reseed", r"(?:abz|x(?<=[ab])|\bz)y", ["abzy", "zabzy", "zy", " zy"], "RS",
  "the UNCONDITIONAL re-seed loses where NO re-seed at all does not (sweep: uncond 19, none 0)"),
B("reseed", r"(?:\b(?<!a)a|a[xy]a|\ba)z", ["axaz", "aaz", " az", "ayaz", "za z", "az", "xaz", "a z"], "RS",
  "uncond 38, none 0; also |T| = 1 (the memchr-bounded landing paths)"),

B("reseed", r"\B(?<!a)d", ["xd", "xdz", "ad", "zad", " d", "d", "xxd", "adxd"], "M1",
  "|T| = 1 DFA mover under \\B: the stale s0 is RESTRICTIVE here, so a missing re-seed on EITHER landing path of "
  "the first-memchr-bounded form loses: 'xd' (the d is the last byte: memchr over [0, n-1) misses, clamp path) and "
  "'xdz' (hit path)"),
B("reseed", r"\B(?<=bc)d", ["bcd", "xbcd", "bcdz", " bcd", "abcdbcd"], "M1", "|T| = 1 HYBRID mover under \\B: both landing paths"),
B("reseed", r"\Bd\B", ["xdx", "xd", "dx", "zzdzz", "d"], "M1", "|T| = 1, \\B both sides"),

# ---------------------------------------------------------------- ML: (?m) under the LF convention (the only one pcrec builds)
B("multiline", "(?m)(?:^|x)(?:ab|cd)", ["ab", "\nab", "xab", "zab", "z\nab", "\rab", "\r\nab", "zxab"], "ML",
  "the line start as a skip context: \\r is NOT a newline (LF is pcrec's only convention, D64)"),
B("multiline", "(?m)(?:ab|cd)$", ["ab", "ab\n", "abx", "ab\r\n", "ab\r", "xab\nab"], "ML", "(?m)$ before LF only"),
B("multiline", "(?m)(?<=\\n)a|b$", ["\r\na", "\ra", "\n\na", "b\r", "\na\r"], "ML", "the witness at CR and CRLF bytes"),
B("multiline", "(?:(?<=\\r)a|w)", ["\ra", "\r\na", "a", "\na", "x\ra", "\ra\r"], "ML", "a CR context: an ordinary byte"),
B("multiline", "(?m)\\b(?:ab|cd)$", ["ab", "x ab\n", "xab\nab", "ab\nab\n"], "ML", "\\b and (?m)$ together"),

# ---------------------------------------------------------------- U8: utf8 contexts
B("utf8", "(?:(?<=é)a|\\bw)", [U("éa"), U("xéa"), U("ea"), U("w"), U("éw"), b"\xa9a", U("ééa"), b"\xc3\xa9a\xc3"], "U8",
  "the context character é is TWO bytes C3 A9: the byte before the start is a CONTINUATION byte", enc="utf8"),
B("utf8", r"(?:(?<=a)z|w)", [U("az"), U("éaz"), U("aéz"), b"a\xffz", b"\xffaz", U("aza")], "U8",
  "the witness under utf8, with ill-formed bytes around the context", enc="utf8"),
B("utf8", r"\b(?:ab|cd)\b", [U("éab ab"), U("xéab"), b"\xc3ab", b"\xffab ab", U("一ab"), b"ab\x80"], "U8",
  "utf8, ASCII \\b: a multi-byte character is a NONWORD context; a lone continuation or 0xFF too", enc="utf8"),
B("utf8", r"\b(?:ab|cd)\b", [U("Kab ab"), U("Kab"), U("kAB ab")], "U8CI",
  "utf8 caseless: KELVIN SIGN (E2 84 AA) folds to k but is not an ASCII word byte", enc="utf8", flags="i"),
B("utf8", r"\bk\w", [U("Kx"), U("xKx"), U("kx"), U(" Kx"), U("x kx")], "U8CI",
  "a caseless start set holding a UTF-8 LEAD byte (E2 for U+212A)", enc="utf8", flags="i"),

# ---------------------------------------------------------------- BD: subject start/end/empty, search_from > 0, \G
B("bounds", r"\b(?:ab|cd)\b", ["", "a", "ab", "b", "xab", "abx", "x ab", "ab ", "bab ab"], "BD",
  "match at subject start and end, the empty subject; the bounded skip's n-1 stop"),
B("bounds", r"(?:(?<=a)z|w)", ["", "z", "w", "a", "az", "azz"], "BD", "the witness at the subject edges"),
B("bounds", r"\G(?:ab|cd)\b", ["ab", "xab", "abab", "ab ab", ""], "BG",
  "\\G: an ATTEMPT-scan machine (no DFA-hat skip site); the unconditional re-seed's only hazard is a \\G "
  "start state, and \\G never reaches the unanchored scan"),
B("bounds", r"(?:\Gx|\b)(?:ab|cd)\b", ["xab", "ab", "zxab", "x ab", " ab"], "BG",
  "\\G beside \\b: a HYBRID with a \\G start family (attempt scan)"),
B("bounds", r"\b(?:ab|cd)\b", ["zab ab", "z ab", "zzab ab"], "SF",
  "search_from > 0 with a word byte BEFORE search_from: the entry initializer reads s[startpos-1]"),

# ---------------------------------------------------------------- HY: hybrids, count-collapsed
B("hybrid", r"\b(ab|cd)\b", ["bab ab", "ab", "xab cd", "atrue ab", "_ab ab"], "HY", "the hybrid twin's pattern (captures on)"),
B("hybrid", r"\B(ab|cd)\B", ["xabx", " abx xabx", "ab"], "HY", "\\B on the hybrid"),
B("hybrid", r"\b(ab|cd)\b.{0,2}\b(ab|c)\b", ["ab c", "xab c ab c", "ab  ab", "bab ab c"], "HYC",
  "count-collapsed (-fprefilter-collapse): the critic's pattern", xflags=["-fprefilter-collapse"], name="coll-1"),
B("hybrid", r"\B(ab|cd){2,3}\B", ["xababx", "xabx xababx", "ababab", "xabcdx"], "HYC",
  "count-collapsed \\B: the collapse widens {2,3} to {1,}", xflags=["-fprefilter-collapse"], name="coll-2"),

B("hybrid", r"\B(a|b){1,3}", ["xa", "xab", "za b", "xaaab", "a", "ab", "xbx"], "HYC",
  "a count-collapsed hybrid whose NO-RE-SEED twin LOSES (search_uncond.py FAMILY=collapsed: 36 of 97 collapsed "
  "movers lose without the re-seed, 0 with it): sound-F5(d)'s failing witness", xflags=["-fprefilter-collapse"], name="coll-3"),
B("hybrid", r"\B(x|ab){1,2}\b", ["zab", "zx", "zab x", "zxab", "ab", "zx "], "HYC", "collapsed, \\B then \\b",
  xflags=["-fprefilter-collapse"], name="coll-4"),

# ---------------------------------------------------------------- VM: the VM hat
B("vmhat", r"\((?:[^()]|(?R))*\)", ["(a)", "x(a)", "((a)", "(()", "a(b(c)d)", ")(", "(a"], "VMR", "recursion"),
B("vmhat", r"(ab)\1", ["abab", "aabab", "ababab", "abaab", "xabab"], "VMB",
  "a backreference: the retry seek after a failed attempt at 0 must stop at 1"),
B("vmhat", r"()\1x", ["x", "ax", "", "xx"], "VMB", "a backreference to an EMPTY group (nullable prefix, S = {x})"),
B("vmhat", r"(a|)\1b", ["b", "aab", "ab", "xb", "aaab"], "VMB", "a backreference to a possibly-empty group"),
B("vmhat", r"(?=ab)a(b)", ["ab", "aab", "xab", "aba"], "VML", "lookahead-first", engine="vm"),
B("vmhat", r"(?=.*z)(a)", ["az", "ba z", "a", "za", "aaz"], "VML", "a lookahead-first pattern whose lookahead reads past the start"),
B("vmhat", r"(a*)\1", ["", "b", "aa", "baa", "aaa"], "VMN", "NULLABLE: V declines; seeking would lose the empty match at 0"),
B("vmhat", r"(?:x|(a)\1)?b", ["b", "xb", "aab", "ab"], "VMN", "nullable start set (b reached through an optional prefix) — non-nullable pattern"),
B("vmhat", r"(?i)(ca)t\1", ["catca", "CatCA", "xcatca", "ccatca", "cATca"], "VMI", "caseless: S = {c, C}"),
B("vmhat", r"(k)\1", [U("kk"), U("Kk"), U("kK"), U("xKK"), U("Kk"), b"\xe2kk"], "VMU",
  "utf8 caseless: S holds the LEAD byte E2 of U+212A", enc="utf8", flags="i"),
B("vmhat", r"(\w)\1x", ["aax", "abbx", "aaax", "xx", "ab"], "VMB", "a class-led backreference (|S| = 63)"),
B("vmhat", r"\b(\w+)\s+\1\b", ["ab ab", "xab ab", "a a", "ab abx ab ab"], "VMB", "the bench's dup-word shape"),
B("vmhat", r"(?1)x(y)", ["yxy", "ayxy", "yxyx"], "VMC", "a subroutine call ahead of its group", engine="vm"),
B("vmhat", r"\Bcat\B", ["xcatx", "cat", "acatb", "cats", "ccatx"], "VMW", "context assertions under the forced VM", engine="vm"),
B("vmhat", r"(?:\Ga|b)c", ["ac", "bc", "xac", "abc"], "VMG", "\\G under the forced VM: the seek must not move the \\G attempt", engine="vm"),
B("vmhat", r"a\Kb", ["ab", "aab", "xab"], "VMK", "\\K under the forced VM", engine="vm"),
B("vmhat", r"a*b?", ["", "zz", "a", "b"], "VMN", "NULLABLE under the forced VM (S491's witness)", engine="vm"),

# ---------------------------------------------------------------- GU: the capacity give-ups of Q-R3
B("giveup", r"(?=(?:a|b|x)*c)x", ["ababababababababababababxc", "xc", "abxc", "aaaaax"], "GU",
  "frames=8: the attempt at 0 exhausts frames inside the lookahead; the hat skips it (a in not S = {x})",
  engine="vm", frames=8),
]

# ---------------------------------------------------------------- -futf-check (tests/utfcheck's shape, not .rxt)
UTFCHECK = [
B("utfcheck", r"\b(?:ab|cd)\b", [b"\xff", b"ab\xff", b"\xffab", b"x\xff", b"", b"ab", b"\xc3", b"zz\xffzz"], "UC",
  "a DFA-hat mover under -futf-check: a subject with an ill-formed byte and NO T byte must refuse (-9), not "
  "return 0 from an early no-candidate exit", enc="utf8", xflags=["-futf-check"]),
B("utfcheck", r"(\w)\1x", [b"\xff", b"aax\xff", b"\xffaax", b"zz", b"\xc3", b"", b"aaax"], "UC",
  "a VM-hat artifact under -futf-check: the seek's no-candidate return must sit AFTER rx_valid_upto",
  enc="utf8", xflags=["-futf-check"]),
]
