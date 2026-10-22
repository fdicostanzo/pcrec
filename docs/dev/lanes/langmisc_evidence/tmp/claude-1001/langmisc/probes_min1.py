P = []
def p(pat, subj, **k):
    k.update(pat=pat, subj=subj); k.setdefault("feats", "all"); k.setdefault("id", "N%03d" % (len(P)+1)); P.append(k)
S = ["a\nb", "a\n\nb", "a  ", "a", "a\n", "aaa", "a\t\t\t"]
for pat in ["[ab](?:(?n)(?U)(\\s){,2}+)|\\W{2}+", "a(?U)\\s{,2}+", "a(?U)\\s{0,2}+", "a(?U)\\s*+", "a(?U)\\s++", "a(?U)\\s?+", "a(?U)\\s{1,2}+",
            "a(?U)(\\s){,2}+", "(?U)a\\s{,2}+$", "(?U)a\\s*+$", "(?U)a{0,3}+", "(?U)a*+", "(?U)a++", "(?U)a?+", "(?U)a{1,}+", "(?U)a{2,3}+", "(?U)(a|b)*+",
            "(?U)(?:a)*+", "(?U)a*+b", "(?U)\\s*+b", "(?U)a{,2}+", "(?U)a{0,2}+", "(?U)[a\\n]{,2}+", "a(?U)[\\s]{,2}+", "(?U)a*?+", "a\\s{,2}+", "a(?U)\\s{,2}"]:
    p(pat, S)
    p(pat, S, extra=["--engine=vm"])
PROBES = P
