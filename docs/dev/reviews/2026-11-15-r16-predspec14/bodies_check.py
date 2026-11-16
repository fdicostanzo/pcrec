# FIXIND: bodies in the document's own language for two transforms §2.7 calls NOT EXPRESSIBLE.
#   months := join([mname = [/Jan(?:uary)?/, ..., /Dec(?:ember)?/]]);  mnum := $mname.index   (E-RFC's own construct)
#   month_numbered(S) := months & (mnum: S)
#   chars := /(?:(?<ch>(?s:.)))*/;  nchars := count((ch: /(?s:.)/))     (§4.3 count, a canonical numeral)
#   length(S) := chars & (nchars: S)
# Emulation: libpcre2-8 (whole match) gives which entry matched (.index = the set group's number, 1-based) and the
# iteration count of ch (one per character; checked by re-running the loop body over the span with python re).
# The stated meanings (§2.7 examples, §4.4): month_numbered(between(1, 6)) accepts "Jan" .. "Jun" (and full names);
# month_numbered(<3) = /Jan(uary)?|Feb(ruary)?/; length(<=20) accepts strings of length <= 20.
import sys, re
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec14/evidence")
import predspec14_anchor as E

M = ["Jan(?:uary)?", "Feb(?:ruary)?", "Mar(?:ch)?", "Apr(?:il)?", "May", "Jun(?:e)?", "Jul(?:y)?", "Aug(?:ust)?",
     "Sep(?:tember)?", "Oct(?:ober)?", "Nov(?:ember)?", "Dec(?:ember)?"]
MONTHS = "(?:" + "|".join("(%s)" % m for m in M) + ")"
FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]

def mnum(s):
    r = E.pcre(MONTHS, s, 0, E.ANCH | E.ENDANCH)
    if r is None:
        return None
    for g in range(1, len(r)):
        if r[g][0] != 2**64 - 1:
            return g
    return None

def month_numbered(pred, s):
    n = mnum(s)
    return n is not None and pred(n)

def stated_month(lo, hi, s):   # the transform's meaning: a month name read as its number, the number in S
    for i, (a, f) in enumerate(zip([x[:3] for x in FULL], FULL), 1):
        if s in (a, f) or (s == "Sept" and False):
            return lo <= i <= hi
    return False

subs = [x[:3] for x in FULL] + FULL + ["jan", "Ja", "Janu", "Junee", "", "Mayy", "Sept", "JanFeb", "13", "Dece"]
bad = n = 0
for lo, hi in ((1, 6), (1, 2), (7, 12), (12, 12), (5, 3)):
    for s in subs:
        n += 1
        a, b = month_numbered(lambda v: lo <= v <= hi, s), stated_month(lo, hi, s)
        if a != b:
            bad += 1; print("MONTH DIFF", lo, hi, repr(s), a, b)
print("month_numbered(between(lo, hi)) as months & (mnum: S): %d cases, %d differ from the stated meaning" % (n, bad))

CHARS = r"(?:(?<ch>(?s:.)))*"
def nchars(s):
    if E.pcre(CHARS, s, 0, E.ANCH | E.ENDANCH) is None:
        return None
    return len(re.findall(r"(?s:.)", s))   # each loop iteration takes exactly one character: unique parse
bad = n = 0
for s in ["", "a", "ab", "a\nb", "x" * 20, "x" * 21, "été", "1:2", "  "]:
    for pred, name in ((lambda v: v <= 20, "<=20"), (lambda v: v == 3, "==3"), (lambda v: v % 2 == 0, "even")):
        n += 1
        c = nchars(s)
        canon = str(c)            # a count is a canonical numeral string
        got = pred(int(canon))
        if got != pred(len(s)):
            bad += 1; print("LENGTH DIFF", repr(s), name)
print("length(S) as chars & (nchars: S): %d cases, %d differ from 'S on the length'" % (n, bad))
