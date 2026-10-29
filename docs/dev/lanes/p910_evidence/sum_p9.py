import sys, collections
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
V=['auto','vm','autoseed','autofind','vmfind','vmfind0','vmfindm1']
ans=collections.defaultdict(dict); tot=collections.defaultdict(int); per=collections.defaultdict(dict)
for r in rows:
    if len(r)<9: print('BAD',r); continue
    n,v,g,f,ln,c,h,i,cy=r
    if f=='TOTAL': tot[(n,v,g)]=int(i); continue
    ans[(n,g,f)][v]=(c,h); per[(n,g,f)][v]=(int(i),int(cy),int(ln))
bad=[(k,d) for k,d in ans.items() if len(set(d.values()))!=1]
print('answer mismatches:',len(bad), 'files:',len(ans), 'matches/variant:', sum(int(list(d.values())[0][0]) for d in ans.values()))
for k,d in bad[:10]: print(k,d)
print('instructions:u totals per group (auto/variant ratio)')
for n in ['ctx-lazy-64','ctx-lazy-256','ctx-lazy-1024','ctx-greedy-256','level-context']:
  for g in ['T','SH','X']:
    base=tot[(n,'auto',g)]
    print(n,g,' '.join(f"{v}={tot[(n,v,g)]:,}(x{base/max(1,tot[(n,v,g)]):.2f})" for v in V))
print('per-byte on the dominant subjects (instr/B, cyc/B; cycles = ratio only, shared box)')
for (n,g,f),d in sorted(per.items()):
    if (n=='ctx-lazy-64' and f in ('t-letters-064k.bin','t-letters-016k.bin')) or (n=='level-context' and f.startswith('t-1024k')):
        print(n,f,' '.join(f"{v}={d[v][0]/d[v][2]:.2f}/{d[v][1]/d[v][2]:.2f}" for v in V))
