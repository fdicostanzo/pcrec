import sys, collections
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
V=sys.argv[2].split(',')
ans=collections.defaultdict(dict); ins=collections.defaultdict(dict); tot=collections.defaultdict(int)
for r in rows:
    if len(r)<9: print('BAD',r); continue
    n,v,g,f,ln,c,h,i,cy=r
    if f=='TOTAL': tot[(n,v,g)]=int(i); continue
    ans[(n,g,f)][v]=(c,h); ins[(n,g,f)][v]=(int(i),int(cy),int(ln))
bad=[(k,d) for k,d in ans.items() if len(set(d.values()))!=1]
print('answer mismatches',len(bad),'files',len(ans),'matches',sum(int(list(d.values())[0][0]) for d in ans.values()))
for k,d in bad: print(k,d)
pats=sorted({k[0] for k in ans})
for n in pats:
  for g in ['T','SH','X']:
    print(n,g,' '.join(f"{v}={tot[(n,v,g)]:,}" for v in V))
print('per-file: rows where a variant differs from auto by >5%+50 instr; columns', V, 'then paced/auto')
worst=collections.defaultdict(float)
for k,d in sorted(ins.items()):
    a=d['auto'][0]
    r=d[V[-1]][0]/max(1,a); worst[(k[0],k[1])]=max(worst[(k[0],k[1])],r)
    if any(abs(d[v][0]-a)>0.05*a+50 for v in d):
        print(k[0][:12],k[1],k[2],d['auto'][2],' '.join(f"{d[v][0]:>10,}" for v in V), f"x{r:.3f}")
print('worst paced/auto per pattern x group:', {k:round(v,3) for k,v in worst.items()})
