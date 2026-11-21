import json,re,collections,sys
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
def strip_rx(t): return re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','RX',t)
C=collections.defaultdict(list)
for ln,k,t in S:
    s=strip_rx(t)
    if k=='B': s=s.split('#')[0]
    s=s.replace('\\|','|')
    # colon
    for m in re.finditer(r':',s):
        i=m.start(); pre=s[:i]; post=s[i+1:]
        if post.startswith('='): cat=':= binding'
        elif pre.endswith('(?') or re.search(r'\(\?[\w-]*$',pre): cat='rx (?: outside slashes'
        elif re.search(r'\d$',pre) and re.match(r'\d',post): cat='text (time/number) in subject'
        elif pre.endswith(')') : cat='joint entry (tuple):'
        elif re.search(r'[\w\]\?]\s*$',pre):
            # find enclosing open
            d=0;enc=None
            for q in range(len(pre)-1,-1,-1):
                c=pre[q]
                if c in ')]': d+=1
                elif c in '([':
                    if d==0: enc=(c,q);break
                    d-=1
            if enc is None: cat='label: without bracket (fragment or top-level error)'
            elif enc[0]=='[': cat='[x: S] (error shape or index cond)'
            else:
                q=enc[1]
                if re.search(r'[\w]$',pre[:q]) : cat='label: inside call/head parens (error shape or typed head)'
                elif re.match(r'\s*\)',post): cat='(h:) section shape'
                else: cat='condition entry label:'
        else: cat='other'
        C[cat].append((ln,t))
for k in sorted(C): print('%-60s %d'%(k,len(C[k])))
if len(sys.argv)>1:
    for x in C[sys.argv[1]]: print(x)
