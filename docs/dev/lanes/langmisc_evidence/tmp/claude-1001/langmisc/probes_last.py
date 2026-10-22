# \K, (?n)+numbered refs, duplicate names + calls, (?U)/(?^) interplay, option-only groups
P = []
def p(pat, subj=(), **k):
    k.update(pat=pat, subj=list(subj)); k.setdefault("feats", "all"); k.setdefault("id", "Z%03d" % (len(P)+1)); P.append(k)
S = ["ab", "abc", "aab", "ac", "abab", "b", "a", "aaa", "ba", "abb", "bab"]
for pat in ["a\\Kb", "(a\\Kb)", "(?:a\\K|b)c", "a\\K|b", "(a\\K)+", "a\\Kx|ab", "(a\\K)(?1)", "a\\K\\Kb", "(?>a\\K)b", "a+\\Kb", "\\Ka", "a(?:\\K)?b", "(?:a\\K)*b",
            "a\\Kb|abc", "(a)\\K\\1", "(?=ab)a\\Kb", "a\\K$", "\\K$", "a(?R)?\\Kb", "(a\\K|b)+c",
            "(?n)(a)(?<x>b)\\1", "(?n)(a)(?<x>b)\\k<x>", "(?n)(?<x>a)(b)(?<y>c)?\\2", "(?n)(a)\\1", "(?n)((?<x>a))\\1",
            "(?J)(?<n>a)|(?<n>b)(?&n)", "(?J)(?<n>a)(?<n>b)(?&n)", "(?J)(?:(?<n>a)|(?<n>b))\\g{n}", "(?J)(?<n>a)?(?<n>b)\\k<n>", "(?J)(?<n>a)(?<n>b)?\\k<n>",
            "(?J)(?<n>a)(?<n>b)(?P=n)", "(?J)(?<n>.)(?<n>.)\\k<n>{2}",
            "(?U)(?^)a+", "(?U)a+(?^)a+", "(?U:a+)a", "(?U)(?-U)a+", "(?U)a{2}", "(?U)a{2}?", "(?U)a{1,2}?b", "(?U)(a+?)", "(?U)a??", "(?U)a?",
            "(?n)(?^)(a)", "(?x)(?^)a b", "(?xx)(?^x)[ a]", "(?s)(?^).", "(?m)(?^)^b", "(?i)(?^i)A",
            "(?:(?i))*a", "(?:(?i))+a", "((?s)).", "(?:(?m)|x)*a", "(?:(?i)){0}a", "(?:a|(?i))*b"]:
    p(pat, S + ["AB", "Ab", "aB", "a\nb", "b\na", "\nb", "a b"])
PROBES = P
