# Lookbehind body shapes around the M226 internal error; octal under utf8; misc refusal shapes
P = []
def p(pat, subj=(), **k):
    k.update(pat=pat, subj=list(subj)); k.setdefault("feats", "all"); k.setdefault("id", "L%03d" % (len(P)+1)); P.append(k)
S = [(s, 0) for s in ["ax", "bcx", "bx", "cx", "abcx", "acx", "abx", "bdx", "x", "aax", "abcdx", "cdx", "adx", "bbx", "ccx", "dx", "ex", "efx", "abefx"]] + [("bcx", 2), ("ax", 1)]
for pat in ["(?<=(?:a|bc))x", "(?<=(?:a|b))x", "(?<=(?:ab|cd))x", "(?<=(?:a|b)c)x", "(?<=c(?:a|b))x", "(?<=(?:a|b)(?:c|d))x", "(?<=(?:a|bc)|d)x",
            "(?<=d|(?:a|bc))x", "(?<=(?:(?:a|b)|c))x", "(?<=(?:a|b){2})x", "(?<=(?:ab|c){1})x", "(?<=(?:a)|bc)x", "(?<=(?:a|bc)(?:d|ef))x",
            "(?<=(a|b))x", "(?<=(ab|cd))x", "(?<=(?>a|b))x", "(?<=(?>ab|c))x", "(?<=(?i:a|b))x", "(?<=(?i:a|bc))x", "(?<=(?:a|bc)?)x",
            "(?<=a(?:b|c)d)x", "(?<=(?:a|bc)d)x", "(?<!(?:a|bc))x", "(?<!(?:a|b))x", "(?<=(?:a|[bc]))x", "(?<=(?:\\d|\\w))x", "(?<=(?:a|b|c))x",
            "(?<=(?:a|b|cd))x", "(?<=(?:ab|b|c))x", "(?<=(?:a|(?:b|c)))x", "(?<=(?:a|(?:bc|d)))x", "(?<=(?=a)(?:a|bc))x", "(?<=(?:a|bc)\\b)x",
            "(?<=(?:a|b)|(?:cd|ef))x", "(?<=(?:a|bc)(?<=c))x", "(?<=(?:)|a)x", "(?<=(?:)a)x", "(?<=(?:a|))x", "(?<=a(?:)|bc)x", "(?<=(?:a{2}|bc))x",
            "(?<=(?:a{2}|b))x", "(?<=(?:aa|b{2}))x", "(?<=(?:a|b)\\K)x", "(?<=(?:a|\\x{62}))x", "(?<=(?:\\Qa\\E|b))x", "(?<=(?:a|b)(?1))(c)x",
            "(?<=(?1))(a|b)x", "(?<=(?1))(a|bc)x", "(?<=(?&n))(?<n>a)x", "(?<=(?R))x", "(?<=x(?:a|b))y", "(?<=(?:(a)|(b)))x", "(?<=\\b(?:a|bc))x",
            "(?<*(?:a|b))x", "(*plb:(?:a|bc))x", "(*nlb:(?:a|bc))x", "(?<=(?:a|bc))", "(?<=(?:a|bc))x|y", "(?:(?<=(?:a|b))x)+"]:
    p(pat, S)
    if pat in ("(?<=(?:a|b))x", "(?<=(?:ab|cd))x", "(?<=(?:a|b)(?:c|d))x", "(?<=(a|b))x", "(?<=(?:a|b){2})x"):
        p(pat, S, extra=["--engine=vm"])
        p(pat, S, extra=["--engine=dfa", "--no-captures"])
# octal / escapes above \377 under utf8
U = ["\u0100", "\u01ff", "\u00ff", "A", "\u0100\u0100", "\x08", "a\u0100"]
for pat in ["\\400", "\\777", "[\\400]", "[\\777]", "(a)\\400", "\\0400", "\\1000", "[\\400-\\777]", "[\\0-\\400]", "\\4000", "(?i)\\400", "\\400+", "\\o{400}",
            "\\N{U+100}", "\\N{U+41}", "[\\N{U+41}]", "\\c", "\\cA", "\\c\\", "\\c{", "\\c\u00e9"]:
    p(pat, U, enc="utf8")
# property loose matching
for pat in ["\\p{ ^Greek}", "\\p{ ^L}", "\\p{^ L}", "\\p{ Greek}", "\\p{Greek }", "\\p{ sc = Greek }", "\\p{sc= Greek}", "\\p{s c=Greek}", "\\p{^sc=Greek}",
            "\\P{^Greek}", "\\p{^^L}", "\\p{L-}", "\\p{-L}", "\\p{l}", "\\p{lu}", "\\p{Lu-}", "\\p{x_an}", "\\p{XAN}", "\\p{any}", "\\p{ANY}",
            "\\p{l&}", "\\p{L &}", "\\p{l_c}", "\\p{Script=Greek}", "\\p{SCRIPT=greek}", "\\p{scx:greek}", "\\p{sc=Zyyy}", "\\p{scx=Zinh}",
            "\\p{Old_Italic}", "\\p{olditalic}", "\\p{Old-Italic}", "\\p{OLD ITALIC}", "\\p{Ital}", "\\p{sc=Qaac}", "\\p{Coptic}", "\\p{Copt}",
            "\\p{Hira}", "\\p{Kana}", "\\p{Hiragana}", "\\pZ", "\\p^L", "\\p{\\x4c}", "\\pl", "\\p{L}{2}", "[\\p{ ^Greek}]"]:
    p(pat, ["\u03b1", "a", "\u0342", "\u0300", "A", "\U00010300", "\u2c80", "\u03e2", "\u3042", "\u30a2", " ", "\u3000", "\u0661", "L", "\u03b1\u03b2"], enc="utf8")
PROBES = P
