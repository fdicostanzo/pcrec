# Random-grammar differential fuzz over a small alphabet (not the doc's alphabet): groups, alternation, all quantifier
# flavours, backrefs, lookaround, atomic, anchors, \b, classes, \K, recursion, named groups, (?i)/(?s)/(?m)/(?U) scopes
import random
R = random.Random(int(__import__("os").environ.get("SEED", "4242")))
NG = [0]
def atom(d):
    c = R.random()
    if d > 3 or c < 0.30: return R.choice(["a", "b", "a", "b", ".", "[ab]", "[^a]", "\\n", "c", "\\w", "\\W", "\\s", "[a-b\\n]", "(?i:A)", "B"])
    if c < 0.45:
        NG[0] += 1; return "(" + alt(d + 1) + ")"
    if c < 0.55: return "(?:" + alt(d + 1) + ")"
    if c < 0.60: return "(?>" + alt(d + 1) + ")"
    if c < 0.66: return R.choice(["(?=", "(?!"]) + alt(d + 1) + ")"
    if c < 0.70: return R.choice(["(?<=", "(?<!"]) + R.choice(["a", "b", "ab", "a|b", "[ab]", "\\n", "ba|aa", "."]) + ")"
    if c < 0.76 and NG[0]: return "\\" + str(R.randint(1, NG[0]))
    if c < 0.80: return R.choice(["^", "$", "\\b", "\\B", "\\A", "\\z", "\\Z", "\\G"])
    if c < 0.83: return R.choice(["(?i)", "(?s)", "(?m)", "(?U)", "(?-i)", "(?n)"])
    if c < 0.85: return "\\K" if d == 0 else "a"
    if c < 0.88 and NG[0]: return "(?" + str(R.randint(1, NG[0])) + ")"
    if c < 0.92:
        NG[0] += 1; return "(?<n%d>" % NG[0] + alt(d + 1) + ")"
    return "(?:" + alt(d + 1) + ")"
def quant(s):
    if s in ("^", "$", "\\b", "\\B", "\\A", "\\z", "\\Z", "\\G", "\\K") or s.startswith("(?") and s.endswith(")") and len(s) <= 5 and s[2] in "ismUn-":
        return s
    c = R.random()
    if c < 0.55: return s
    q = R.choice(["*", "+", "?", "{2}", "{0,2}", "{1,3}", "{2,}", "{,2}", "{0}"])
    return s + q + R.choice(["", "", "?", "+"])
def seq(d):
    return "".join(quant(atom(d)) for _ in range(R.randint(1, 3)))
def alt(d):
    return "|".join(seq(d) for _ in range(R.choice([1, 1, 2, 3])))
SUBJ = ["", "a", "b", "ab", "ba", "aa", "bb", "aab", "abb", "abab", "aaba", "c", "\n", "a\nb", "Ab", "ab\n", "bA", "aabb", "baab", "abcab", "AAB", "aBa"]
P = []
for i in range(int(__import__("os").environ.get("NFUZZ", "500"))):
    NG[0] = 0
    pat = alt(0)
    subj = SUBJ + [("abab", 1), ("aab", 2), ("ab\nab", 3)]
    P.append(dict(pat=pat, subj=subj, feats="all", id="F%04d" % i))
PROBES = P
