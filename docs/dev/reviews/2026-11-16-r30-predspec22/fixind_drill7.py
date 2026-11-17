import re, itertools
# list /(?:(?<h>\d)(?::(?<m>\d))?,)*/ ; R=(<5,<5); default m=0; pairing loop = the list loop; plain cond needs a pass
def passes(s): return [(int(a), int(b) if b else 0) for a,b in re.findall(r'(\d)(?::(\d))?,', s)]
R=lambda t: t[0]<5 and t[1]<5
items=['1:1','7:7','3','8','2:9']
pop=['']+[','.join(c)+',' for n in (1,2) for c in itertools.product(items,repeat=n)]
d=[]
for s in pop:
    p=passes(s)
    q = bool(p) and all(R(t) for t in p)          # q := P & ((h, m = 0): R)
    a = not q                                       # P & !q
    b = bool(p) and all(not R(t) for t in p)       # ((h, m = 0): !R)
    if a!=b: d.append(s)
print(len(d),"of",len(pop),"differ; e.g.",d[:4])
