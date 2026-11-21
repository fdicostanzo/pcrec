# union-of-tuples vs tuple-of-unions over the note's t population (h: 1-2 digits, m: 2 digits), padded per J8.
import re
subs=[f"{h}:{m:02d}" for h in [str(i) for i in range(10)]+[f"{i:02d}" for i in range(100)] for m in range(100)]
t=re.compile(r"(?<h>\d{1,2}):(?<m>\d\d)".replace("?<","?P<"))
def rx_union():   # padded([(9, 0), (10, 30)]) : rows (h:9,m:0)|(h:10,m:30), padded
    return re.compile(r"(?P<h>0*9):(?P<m>0*0)|(?P<h2>0*10):(?P<m2>0*30)")
def rx_prod():    # (padded(9 | 10), padded(0 | 30))
    return re.compile(r"(?P<h>0*(?:9|10)):(?P<m>0*(?:0|30))")
U,P=rx_union(),rx_prod()
a=b=d=0;ex=[]
for s in subs:
    assert t.fullmatch(s)
    h,m=s.split(":"); hi,mi=int(h),int(m)
    eu=(hi,mi) in {(9,0),(10,30)}; ep=hi in (9,10) and mi in (0,30)
    ru=bool(U.fullmatch(s)); rp=bool(P.fullmatch(s))
    assert ru==eu and rp==ep, s
    a+=eu; b+=ep
    if eu!=ep: d+=1; ex.append(s)
print("subjects",len(subs),"union",a,"product",b,"differ",d,ex)
