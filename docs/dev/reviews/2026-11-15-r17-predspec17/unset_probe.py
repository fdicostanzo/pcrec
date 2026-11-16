# Emulates rev 17 §8 bodies on an author pattern with an OPTIONAL label, under §4.2 (a condition naming an
# unset label FAILS; `!` of a failed filter is true), and on a REPEATED label (a plain condition holds for
# EVERY iteration, over zero iterations vacuously). python3 re only; read-only probe.
import re
P = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?"
def cond(g, lab, pred):            # (lab: padded(pred)); unset -> False (§4.2)
    v = g.get(lab)
    return False if v is None else pred(int(v))
def ge2(g, lo): return cond(g,'h',lambda x:x>lo[0]) or (cond(g,'h',lambda x:x==lo[0]) and cond(g,'m',lambda x:x>=lo[1]))
def le2(g, hi): return cond(g,'h',lambda x:x<hi[0]) or (cond(g,'h',lambda x:x==hi[0]) and cond(g,'m',lambda x:x<=hi[1]))
print("(U) optional label m: author pattern /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/, bound [9, 0]")
for s in ["9", "10", "8", "9:00", "9:30", "8:59"]:
    g = re.fullmatch(P, s).groupdict()
    print("  %-5s ge2=%-5s le2=%-5s above=P&!le2=%-5s below=P&!ge2=%-5s equal=between(t,t)=%s" % (
        s, ge2(g,(9,0)), le2(g,(9,0)), not le2(g,(9,0)), not ge2(g,(9,0)), ge2(g,(9,0)) and le2(g,(9,0))))

# repeated labels: every iteration of h and m collected; a plain condition = all iterations (§4.2/§4.3)
R = r"(?:(\d{1,2}):(\d\d),)*"
def iters(s):
    return [(int(a), int(b)) for a, b in re.findall(r"(\d{1,2}):(\d\d),", s)] if re.fullmatch(R, s) else None
def allc(xs, pred): return all(pred(x) for x in xs)
def rge2(it, lo):
    hs = [h for h, _ in it]; ms = [m for _, m in it]
    return allc(hs, lambda x: x > lo[0]) or (allc(hs, lambda x: x == lo[0]) and allc(ms, lambda x: x >= lo[1]))
print("(L) repeated labels h, m in a loop /(?:(?<h>\\d{1,2}):(?<m>\\d\\d),)*/, lex_ge2 bound [9, 0]")
for s in ["", "10:00,9:30,", "9:30,10:00,", "8:00,", "9:15,", "10:00,11:00,"]:
    it = iters(s)
    want = all(t >= (9, 0) for t in it)
    print("  %-14r lex_ge2=%-5s every tuple >= 9:00: %s" % (s, rge2(it, (9, 0)), want))
