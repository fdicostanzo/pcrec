import json,re,collections,sys
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
def strip_rx(t): return re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','RX',t)
def match(s,i):
    d=0
    for q in range(i,len(s)):
        if s[q] in '([{': d+=1
        elif s[q] in ')]}':
            d-=1
            if d==0: return q
    return None
def top(inner,pat):
    d=0;i=0
    while i<len(inner):
        c=inner[i]
        if c in '([{': d+=1
        elif c in ')]}': d-=1
        elif d==0 and re.match(pat,inner[i:]): return True
        i+=1
    return False
def entries(inner):
    d=0;cur='';out=[]
    for c in inner:
        if c in '([{': d+=1
        elif c in ')]}': d-=1
        if c==',' and d==0: out.append(cur);cur=''
        else: cur+=c
    out.append(cur);return out
C=collections.defaultdict(list)
for ln,k,t in S:
    s=strip_rx(t)
    if k=='B': s=s.split('#')[0]
    s=s.replace('\\|','|')
    for i,c in enumerate(s):
        if c!='(': continue
        j=match(s,i)
        if j is None: C['unclosed'].append((ln,t));continue
        inner=s[i+1:j]; after=s[j+1:]; before=s[:i]
        if inner.startswith('?'): cat='rx group outside slashes'
        elif before.endswith('$'): cat='$( ) notation'
        elif re.search(r'[\w\]]$',before):
            cat='head' if re.match(r'\s*:=',after) else 'call args'
        elif inner.lstrip().startswith('&'): cat='section (& f)'
        elif re.match(r'\s*:(?!=)',after):
            cat='reference tuple left of :' if top(inner,',') else 'one-name paren left of :'
            if re.search(r'\?|(?<![:<>=!])=(?!=)',inner): cat+=' [with mark/default]'
        elif top(inner,r':(?!=)'):
            es=entries(inner)
            marks=any(re.match(r'\s*[\w.\[\]]+\?\s*:',e) for e in es)
            dflt=any(re.match(r'\s*[\w.\[\]]+\??\s*=[^=]',e) for e in es)
            joint=any(re.match(r'\s*\(',e) for e in es)
            cat='condition record'+(' [joint]' if joint else '')+(' [mark]' if marks else '')+(' [default]' if dflt else '')
        elif top(inner,','):
            if any(re.match(r'\s*\w+\s*=[^=]',e) for e in entries(inner)): cat='labelled record (error shape)'
            else: cat='tuple value'
        else:
            cat='grouping (one entry)'
        C[cat].append((ln,t))
for k in sorted(C): print('%-50s %d'%(k,len(C[k])))
if len(sys.argv)>1:
    for x in C[sys.argv[1]]: print(x)
