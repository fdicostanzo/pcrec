# bounds written with leading zeros, under §2.4 l.906: a comparison literal WITH leading zeros keeps them
# (reading R: the set is the literal-WIDTH numerals; canonical width otherwise)
import re
def cmpset(op, lit):
    v=int(lit); w=len(lit) if (len(lit)>1 and lit[0]=='0') else None
    def inset(c):  # c: candidate string after padded's 0*
        if not re.fullmatch(r'\d+',c): return False
        if w is None:
            if len(c)>1 and c[0]=='0': return False
        elif len(c)!=w: return False
        n=int(c); return {'>':n>v,'>=':n>=v,'<':n<v,'<=':n<=v,'==':n==v}[op]
    return inset
def padded(op,lit):
    S=cmpset(op,lit)
    return lambda t: t is not None and any(t[:k]=='0'*k and S(t[k:]) for k in range(len(t)))
def between(gd,lo,hi):
    h,m=gd['h'],gd['m']
    ge = padded('>',lo[0])(h) or (padded('==',lo[0])(h) and padded('>=',lo[1])(m))
    le = padded('<',hi[0])(h) or (padded('==',hi[0])(h) and padded('<=',hi[1])(m))
    return ge and le
P=r'(?P<h>\d{1,2}):(?P<m>\d\d)'
for s in ['9:30','09:30','10:00','9:00','09:00','10:01']:
    gd=re.fullmatch(P,s).groupdict()
    print(s,'[9,0]..[10,0]:',between(gd,('9','0'),('10','0')),' [09,00]..[10,00]:',between(gd,('09','00'),('10','00')))
