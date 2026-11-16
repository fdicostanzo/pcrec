import json,re,collections
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
def strip_rx(t): return re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','RX',t)
C=collections.Counter(); EX=collections.defaultdict(list)
for ln,k,t in S:
    s=strip_rx(t)
    if k=='B': s=s.split('#')[0]
    for m in re.finditer(r'\$',s):
        post=s[m.end():]
        if post.startswith('{'): c='$ hole ${'
        elif re.match(r'[A-Za-z_]',post): c='$ label path read'
        elif post.startswith('('): c='$( ) notation'
        else: c='$ other (rx anchor / prose)'
        C[c]+=1; EX[c].append((ln,t))
    for m in re.finditer(r'!',s):
        post=s[m.end():]
        if post.startswith('~'): c='! in withdrawn !~'
        elif post.startswith('='): c='!= '
        elif post.strip()=='' : c='! bare (prose)'
        else: c='! prefix complement'
        C[c]+=1; EX[c].append((ln,t))
for k,v in sorted(C.items()): print('%-35s %d'%(k,v))
for x in EX['$ other (rx anchor / prose)'][:40]: print(x)
