import csv,sys,collections
rows=list(csv.DictReader(open('raw.tsv'),delimiter='\t'))
pat=sys.argv[1]
d=collections.OrderedDict()
for r in rows:
    if r['pattern']!=pat: continue
    d.setdefault((r['subject'],r['hex'],int(r['from']),r['poskind']),{})[r['arm']]=r['result']
print('pattern',pat)
print('%-24s %-4s %-6s %-7s'%('subject','from','kind','')+' '.join('%-9s'%a for a in['U','I','UA','IA','psearch','pmatch']))
for (s,h,f,k),v in d.items():
    if k in('start','end') and len(sys.argv)<3: continue
    print('%-24s %-4d %-6s '%(s,f,k)+' '.join('%-9s'%v.get(a,'') for a in['U','I','UA','IA','psearch','pmatch']))
