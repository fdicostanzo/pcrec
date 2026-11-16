import re
def cond(v,lab,op,b):
    t=v.get(lab)
    if t is None or not t.isdigit(): return False
    x=int(t); return {'>':x>b,'>=':x>=b,'==':x==b,'<':x<b,'<=':x<=b}[op]
def lex(v,s,b,strict,last):
    n=len(b)
    for k in range(n):
        ok=True
        for i in range(k+1):
            op='==' if i<k else (last if k==n-1 else strict)
            if i>=len(s) or not cond(v,s[i],op,b[i]): ok=False;break
        if ok: return True
    return False
ge=lambda v,s,lo:lex(v,s,lo,'>','>=')
le=lambda v,s,hi:lex(v,s,hi,'<','<=')
def run(name,P,s,lo,hi,acc,rej,mode='between'):
    bad=[]
    for t,exp in [(a,1) for a in acc]+[(r,0) for r in rej]:
        m=re.fullmatch(P,t)
        if not m: got=False
        else:
            v=m.groupdict()
            got={'between':lambda:ge(v,s,lo) and le(v,s,hi),'ge':lambda:ge(v,s,lo),
             'strict':lambda:ge(v,s,lo) and not le(v,s,lo)}[mode]()
        if bool(got)!=bool(exp): bad.append((t,exp,got))
    print(name,'BAD' if bad else 'ok',bad)
HM=r'(?P<h>\d{1,2}):(?P<m>\d\d)'
run('time',HM,['h','m'],[9,0],[10,0],['9:00','09:30','9:59','10:00'],['10:01','8:59','11:00','9:5'])
run('past',r'(?P<m>\d\d) past (?P<h>\d{1,2})',['h','m'],[9,0],[10,0],['30 past 9','00 past 10'],['01 past 10','59 past 8'])
run('hms',r'(?P<h>\d{1,2}):(?P<m>\d\d):(?P<sec>\d\d)',['h','m','sec'],[9,30,5],[10,0,0],['9:30:05','09:30:05','9:59:59','10:00:00'],['9:30:04','10:00:01','8:59:59','9:30'])
run('ver',r'(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)',['major','minor'],[1,4],[1,10],['1.4','1.9','1.10'],['1.3','1.11','2.0','0.9','1.04','1x4'])
run('semver',r'(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)',['major','minor','patch'],[1,4,0],None,['1.4.0','1.10.2','2.0.0'],['1.3.99','0.9.9','1.04.0'],'ge')
run('d+',r'(?P<major>\d+)\.(?P<minor>\d+)',['major','minor'],[1,4],[1,10],['1.04','01.10','1.010'],['1.011'])
run('opt',r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?',['h','m'],[9,30],[11,0],['10','9:45','11:00'],['9','11'])
run('strict',r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?',['h','m'],[9,30],None,['9:31','10'],['9:30','9','8'],'strict')
run('lz',HM,['h','m'],[9,0],[10,0],['9:30','09:30','9:00'],['10:01'])
