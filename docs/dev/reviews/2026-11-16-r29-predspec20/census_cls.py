import json,re,collections,sys
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
def strip_rx(t):
    return re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','RX',t)
C=collections.defaultdict(list)
def add(cat,ln,t): C[cat].append((ln,t))
def parens(s):
    # return list of (open_idx, close_idx)
    st=[];out=[]
    for i,ch in enumerate(s):
        if ch in '([': st.append((ch,i))
        elif ch in ')]':
            if st:
                o,j=st.pop()
                if o=='(' and ch==')': out.append((j,i))
    return out
def top_split(inner):
    d=0;parts=[];cur=''
    for ch in inner:
        if ch in '([{': d+=1
        if ch in ')]}': d-=1
        if ch==',' and d==0: parts.append(cur);cur=''
        else: cur+=ch
    parts.append(cur);return parts
def has_top(inner,ch):
    d=0
    for i,c in enumerate(inner):
        if c in '([{': d+=1
        elif c in ')]}': d-=1
        elif d==0 and c==ch: return True
    return False
for ln,k,t in S:
    s=strip_rx(t)
    if k=='B': s=s.split('#')[0]
    s=s.replace('\\|','|')
    # QUESTION MARK
    for m in re.finditer(r'\?',s):
        pre=s[:m.start()]; post=s[m.end():]
        if re.search(r'[\w\]]$',pre):
            word=re.search(r'[\w.\[\]]+$',pre).group(0)
            if s.strip()==word+'?' and word in('x',): add('?:rx-quantifier-bare x?',ln,t)
            elif re.match(r'\s*(:|,|\)|=|$)',post): add('?:label-mark',ln,t)
            else: add('?:other',ln,t)
        elif s.strip()=='?': add('?:bare ? (quantifier, prose)',ln,t)
        else: add('?:other',ln,t)
    # EQUALS
    s2=re.sub(r':=|==|<=|>=|!=|=~','',s)
    for m in re.finditer(r'=',s2):
        pre=s2[:m.start()];post=s2[m.end():]
        # find enclosing bracket
        d=0;enc=None
        for i in range(len(pre)-1,-1,-1):
            c=pre[i]
            if c in ')]': d+=1
            elif c in '([':
                if d==0: enc=(c,i);break
                d-=1
        if s2.strip()=='=' : add('=:bare mark (prose)',ln,t);continue
        if enc is None:
            add('=:no enclosing bracket',ln,t);continue
        c,i=enc
        if c=='[': add('=:array label',ln,t);continue
        # find matching close
        dd=0;j=None
        for q in range(i,len(s2)):
            if s2[q] in '([': dd+=1
            elif s2[q] in ')]':
                dd-=1
                if dd==0: j=q;break
        inner=s2[i+1:j] if j else s2[i+1:]
        after=s2[j+1:] if j else ''
        # entry containing this '='
        if re.match(r'\s*:(?!=)',after): add('=:label default (in reference tuple)',ln,t);continue
        # entry-level: does entry have ':' after '='?
        seg=post.split(',')[0]
        if re.search(r'(?<!:):(?!=)',seg) and not re.match(r'[\w.]+\s*:',''): 
            add('=:label default (single-entry condition)',ln,t);continue
        if re.search(r'[\w.]$',pre[:i]):
            if re.match(r'\s*:=',s[ s.find(inner)+len(inner)+1:] if inner in s else ''): add('=:head default',ln,t)
            else: add('=:call parameter',ln,t)
            continue
        add('=:labelled record in value position (error shape)',ln,t)
for k in sorted(C):
    print('%-55s %d'%(k,len(C[k])))
if len(sys.argv)>1:
    for x in C[sys.argv[1]]: print(x)
