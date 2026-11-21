import sys; sys.path.insert(0, '.')
sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec24/R/tree/docs/dev/lanes/rxmodel_evidence')
import pcre2h
from ev import *
import re as _re
def lt5(c):
    v = c.get('h'); return v is not None and _re.fullmatch(r'0|[1-9]\d*', v) is not None and int(v) < 5
seen = []
def lt5log(c):
    seen.append((c.stretch(), c.get('h'))); return lt5(c)
m = pcre2h.Pcre(r'(?:(?<h>\d)?;(?C"t"))+', {'t': lt5log})
print('PCRE2 W1c item-in-loop WHOLE 3;; :', m.whole('3;;'), 'callout saw', seen)
seen.clear(); print('PCRE2 search 3;; :', m.search('3;;'), seen)
# my text evaluator
item1c = ANDc(seq(opt(grp('h', DIG)), lit(';')), T('h', lt(5)))
W1c = rep(item1c, 1)
print('text-evaluator W1c WHOLE 3;; :', whole(W1c, '3;;'), 'SEARCHED', searched(W1c, '3;;'))
R1 = rep(seq(opt(grp('h', DIG)), lit(';'))); LOOPED_NAMES[R1.lid] = {'h'}
W1d = ANDc(R1, some(R1, T('h', lt(5))), none(R1, NOT(T('h', lt(5)))))
print('W1d WHOLE 3;; :', whole(W1d, '3;;'), 'SEARCHED', searched(W1d, '3;;'))
# count PCRE2 W1c vs W1d over RG3
def strings(alpha, n):
    out, cur = [""], [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
RG3 = strings("37;", 5)
dw = [t for t in RG3 if m.whole(t) != (whole(W1d, t) is not None)]
ds = [t for t in RG3 if (lambda r: None if r is None else (r[0], r[1]))(m.search(t)) != (lambda r: None if r is None else (r[1], r[1]+len(r[0])))(searched(W1d, t))]
print('PCRE2 W1c vs text W1d: WHOLE', len(dw), sorted(dw, key=lambda x: (len(x), x))[:5], 'SEARCHED', len(ds), sorted(ds, key=lambda x: (len(x), x))[:5])
