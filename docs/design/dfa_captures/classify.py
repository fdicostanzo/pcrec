#!/usr/bin/env python3
"""[dfacap] Cause split of census.py output (memo section 3.1). Usage: python3 classify.py census.tsv
The `why` text is the compiler's own RX_ENGINE_WHY; the lookaround-only split also reads
the TEXT heuristic column `textscan` (see census.py)."""
import sys,csv,collections,re
rows=list(csv.DictReader(open(sys.argv[1]),delimiter='\t'))
def cls(w):
    w=re.sub(r' at pattern offset \d+','',w)
    w=w.replace('\\?','?').replace('\\\\','\\')
    if re.match(r'^\(\?(=|!|<=|<!|\*|<\*)|^\(\*(n?a?p?l[ab]|pla|plb|nla|nlb|positive_|negative_|non_atomic_)',w): return 'lookaround'
    if re.match(r'^\\([0-9]|k|g\{)|^\(\?P=',w): return 'backref'
    if re.match(r'^\(\?(R|[0-9]|&|P>)|^\\g[<\']',w): return 'call/recursion'
    if w.startswith('(?>') or w.startswith('possessive'): return 'atomic/possessive'
    if w=='\\K': return '\\K'
    if w.startswith('(?C') or w.startswith('${'): return 'callout/var'
    if w.startswith('dfa overflowed'): return 'dfa size cap'
    if w.startswith('capture group'): return 'capture'
    return 'other:'+w
OTHER={'atomic','bref','call','kreset','verb','cond'}
def lookonly(r):
    t=set(x for x in r['textscan'].split(',') if x)
    return not (t & OTHER)
C=collections.Counter
for scope in ('all','corpus','bench'):
    R=[r for r in rows if scope=='all' or (scope=='corpus')==(r['src']=='corpus')]
    vm=[r for r in R if r['engine']=='vm']
    print('=====',scope,'n',len(R),'dfa',sum(r['engine']=='dfa' for r in R),'vm',len(vm),'refused',sum(r['engine']=='REFUSED' for r in R))
    cap=[r for r in vm if r['why'].startswith('capture group')]
    free=[r for r in vm if not r['why'].startswith('capture group')]
    print(' capture-forced',len(cap))
    k=C()
    for r in cap:
        if r['engine_nc']=='dfa': k['captures only -> dfa']+=1
        else:
            c=cls(r['why_nc'])
            if c=='lookaround':
                if lookonly(r):
                    k['captures + lookaround only'+(' (capture inside look)' if 'capinlook' in r['textscan'] else '')]+=1
                else: k['captures + lookaround + other']+=1
            else: k['captures + '+c]+=1
    for a,b in sorted(k.items(), key=lambda x:-x[1]): print('   %5d %s'%(b,a))
    print(' capture-free VM',len(free))
    k=C()
    for r in free:
        c=cls(r['why'])
        if c=='lookaround' and not lookonly(r): c='lookaround + other'
        k[c]+=1
    for a,b in sorted(k.items(), key=lambda x:-x[1]): print('   %5d %s'%(b,a))
    # hybrid prefilter among capture-only
    co=[r for r in cap if r['engine_nc']=='dfa']
    print(' captures-only prefilter:',C(r['prefilter'] for r in co), ' ncaps dist:',sorted(C(min(int(r['ncaps'] or 0),9) for r in co).items()))
print('REFUSED top:',C(re.sub(r'\(pattern offset \d+\)','',r['why'])[:70] for r in rows if r['engine']=='REFUSED').most_common(8))
