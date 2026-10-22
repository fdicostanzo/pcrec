# Misc families: startpos, NUL bytes, nesting depth, -i flag, (?<=(?R)), recursion+lookbehind, multi-alternative captures, quoting oddities
P = []
def p(pat, subj=(), **k):
    k.update(pat=pat, subj=list(subj)); k.setdefault("feats", "all"); k.setdefault("id", "X%03d" % (len(P)+1)); P.append(k)
SP = [("abcabc", i) for i in range(7)] + [("a\nb\n", i) for i in range(5)] + [("", 0)]
for pat in ["^", "\\A", "\\G", "\\Gb", "\\Gc", "$", "\\Z", "\\z", "(?m)^", "(?m)$", "\\b", "\\B", "(?<=a)", "(?<=\\G)", "\\G(?<=a)", "c\\G", "(?=\\G)b",
            "a|\\Gb", "\\G?", "(?:\\G|a)b", "(?!\\G)b", "(?<!\\G)b", "\\K", "a\\K", "(?m)\\G^", "(\\G)", "\\Gx*", "\\G$"]:
    p(pat, SP)
# startpos inside a utf-8 character
for pat in [".", "\\x{e9}", "(?<=.)", "\\G.", "\\b", "a", "^"]:
    p(pat, [("éa", 1), ("€a", 1), ("€a", 2), ("\U0001f600a", 3), ("éa", 2), ("éa", 3)], enc="utf8")
# NUL in subject
for pat in ["\\x00", "\\0", ".", "[^a]", "\\W", "\\s", "[\\x00-\\x01]", "a\\x00?b", "\\x00+", "[[:cntrl:]]", "\\N", "\\H", "\\V", "(?i)\\x00", "\\x{0}", "\\000", "[\\0]"]:
    p(pat, ["\x00", "a\x00b", "ab", "\x00\x00", "a"])
    p(pat, ["\x00", "a\x00b", "ab", "\x00\x00", "a"], enc="utf8")
# nesting depth
for n in (249, 250, 251):
    p("(" * n + "a" + ")" * n, ["a"])
    p("(?:" * n + "a" + ")" * n, ["a"])
# -i on the command line combined with inline options
for pat in ["a", "(?-i)a", "(?-i:a)b", "(?^)a", "[a-z]", "(a)\\1", "\\x{e9}", "(?i)a"]:
    p(pat, ["a", "A", "aA", "Ab", "AB", "\xe9", "\xc9"], i=True)
    p(pat, ["a", "A", "aA", "Ab", "AB", "é", "É"], i=True, enc="utf8")
# recursion inside lookaround
for pat in ["(?<=(?R))x", "(?<=a(?R)?)x", "x(?<=(?R))", "(a)(?<=(?1))x", "(?<=(?1))(a)", "(?<=(?1)(?1))(ab)", "(?=(?R))", "(?!(?1))(a)",
            "(?<=(?&n))(?<n>ab)", "(a|bc)(?<=(?1))", "(?<=(?1))(a(?1)?)", "(?(DEFINE)(?<x>ab))(?<=(?&x))c", "(?(DEFINE)(?<x>a|bc))(?<=(?&x))c"]:
    p(pat, ["x", "ax", "abx", "abab", "a", "aa", "bc", "abc", "aab"])
# group count / no-captures / count-groups consistency
for pat in ["(a)(b)", "(?:a)(b)", "(?n)(a)(?<x>b)", "(?=(a))", "(?(DEFINE)(a))", "(a)|(b)|(c)"]:
    p(pat, ["ab", "c"], extra=["--no-captures"])
# misc oddities
for pat in ["a(?#x)b", "(?i)(?#x)a", "a{1}{", "a{1}}", "a{1,2}{", "(?:a{2}){0}", "a{0}{", "(?:){0}", "(?:)*", "(?:)+", "()*", "()+?", "(|)", "(a|)", "(?:|a)*?b",
            "[a]{0,0}b", "[\\x00-\\xff]", "[^\\x00-\\xff]", "[^\\x00-\\xff]?a", "(?s)[^\\n]", "\\x{0}*", "\\d{0,0}", "x*{", "x+{1", "(?i)[^\\x00-\\x40\\x5b-\\x60\\x7b-\\xff]"]:
    p(pat, ["ab", "a", "b", "", "x{", "aa{", "{", "\x00", "\xff", "\n", "A", "Z", "aab"])
PROBES = P
