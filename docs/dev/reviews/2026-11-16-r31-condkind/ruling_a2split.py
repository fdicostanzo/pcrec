import re,itertools,sys
P1=re.compile(r'(?<g>a)?b'.replace('(?<','(?P<'))
P2=re.compile(r'(?:(?<g>a)(?=b))*b'.replace('(?<','(?P<'))
# same subjects, same labelling (whole value)
subs=[''.join(t) for n in range(0,6) for t in itertools.product('ab',repeat=n)]
same=0; m1=[];m2=[]
for s in subs:
    a=P1.fullmatch(s); b=P2.fullmatch(s)
    assert bool(a)==bool(b),s
    if a: assert a.group('g')==b.group('g'),s; same+=1; m1.append(s)
print('subjects',len(subs),'matched by both, same labelling:',same,m1)
# A2 all((g:"a")): P1 g is a set-once column (upper bound 1): one row; P2 g in a * loop: passes = iterations
def passes2(s):
    # count iterations: P2 can iterate at most once; iteration happened iff g set
    m=P2.fullmatch(s); return [m.group('g')] if m.group('g') is not None else []
for s in m1:
    a=P1.fullmatch(s); r1 = (a.group('g')=='a')   # one row, NULL -> UNKNOWN -> not TRUE
    ps=passes2(s); r2 = all(p=='a' for p in ps)    # every pass passes, none needed
    print(repr(s),'A2 on P1 (one row):',r1,' A2 on P2 (passes):',r2)
