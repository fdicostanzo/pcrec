# generic engine from rev 22 TEXT for set-once labels: program = (regex, population, [items]); an item is
# ('c', {label: 'plain'|'mark'|('def',v)}, pred(tuple dict)) or ('not', program)
import re,itertools
def parse(rx,s):
    m=re.fullmatch(rx,s); return None if not m else m.groupdict()
class Prog:
    def __init__(s,rx,pop,items): s.rx,s.pop,s.items=rx,pop,items; s._dom={}
    def matches(s): return [(t,parse(s.rx,t)) for t in s.pop if parse(s.rx,t) is not None]
    def dom(s,lab):
        # mark-narrows: unmarked conditions narrow; a marked one only where its marked labels are present;
        # a complemented pattern narrows as a label-free filter (§2.2 (3)); no DOM read while a DOM is computed
        if lab in s._dom: return s._dom[lab]
        out=set()
        for t,g in s.matches():
            ok=True
            for it in s.items:
                if it[0]=='not':
                    if it[1].holds(t): ok=False
                else:
                    _,labs,pred=it
                    if any(g[l] is None for l,k in labs.items() if k=='mark'): continue
                    vals={}
                    for l,k in labs.items():
                        if g[l] is not None: vals[l]=g[l]
                        elif isinstance(k,tuple): vals[l]=k[1]
                        else: ok=False; break
                    if ok and not pred(vals): ok=False
                if not ok: break
            if ok and g[lab] is not None: out.add(g[lab])
        s._dom[lab]=out; return out
    def cond(s,it,g):
        _,labs,pred=it
        cands=[]
        for l,k in labs.items():
            if g[l] is not None: cands.append([g[l]])
            elif k=='mark': cands.append(sorted(s.dom(l)))
            elif isinstance(k,tuple): cands.append([k[1]])
            else: return False
        return any(pred(dict(zip(labs,c))) for c in itertools.product(*cands))
    def holds(s,t):
        g=parse(s.rx,t)
        if g is None: return False
        for it in s.items:
            if it[0]=='not':
                if it[1].holds(t): return False
            elif not s.cond(it,g): return False
        return True
