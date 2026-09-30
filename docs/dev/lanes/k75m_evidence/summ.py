import collections,csv
rows=list(csv.DictReader(open('raw.tsv'),delimiter='\t'))
def cls(r):
    v=r['result']; f=int(r['from'])
    if v.startswith('err'): return v
    if v in('nomatch','REFUSED'): return v
    s=int(v.split(',')[0]); return 'AT' if s==f else 'MOVED'
tab=collections.defaultdict(collections.Counter)
for r in rows:
    if r['poskind'] in('start','end'): continue
    tab[(r['pattern'],r['poskind'],r['arm'])][cls(r)]+=1
pats=[]
for r in rows:
    if r['pattern'] not in pats: pats.append(r['pattern'])
for p in pats:
    print('==',p)
    for kind in 'A','B','T':
        for arm in ['U','I','UA','IA','psearch','pmatch']:
            c=tab.get((p,kind,arm))
            if c: print(f'  {kind} {arm:8}',dict(c))
