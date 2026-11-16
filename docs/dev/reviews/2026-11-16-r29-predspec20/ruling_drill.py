import itertools,re,sys,ctypes
src=open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/evidence/absent_check.py').read().split('\n')
exec('\n'.join(src[:96]))
def caps(p,t,names):
    m=re.fullmatch(py(p),t)
    return tuple(m.group(n) for n in names)
def pcaps(p,t,names):
    c=_code(p); md=L.pcre2_match_data_create_from_pattern_8(c,None)
    rc=L.pcre2_match_8(c,t.encode(),len(t.encode()),0,ANCH|ENDANCH,md,None)
    ov=L.pcre2_get_ovector_pointer_8(md); out=[]
    for n in names:
        k=L.pcre2_substring_number_from_name_8(c,n.encode())
        out.append(None if ov[2*k]==UNSET else t[ov[2*k]:ov[2*k+1]])
    L.pcre2_match_data_free_8(md); return tuple(out)
print("DRILL 1: a * loop that can run at most once by MEANING vs the `?` spelling")
P1=r'(?<k>\d)?-(?<h>\d)?'; P2=r'(?:(?<k>\d)(?=-))*-(?:(?<h>\d)(?!\d))*'
n=dm=dc=0
for L_ in range(0,5):
    for tup in itertools.product('059-a',repeat=L_):
        t=''.join(tup); n+=1
        a=whole(P1,t); b=whole(P2,t)
        if a!=b: dm+=1; continue
        if a:
            c1=pcaps(P1,t,['k','h']); c2=pcaps(P2,t,['k','h'])
            assert c1==caps(P1,t,['k','h']) and c2==caps(P2,t,['k','h'])
            if c1!=c2: dc+=1
print(" subjects",n,"match differ",dm,"capture differ",dc, "| engine disagreements",DISAGREE[0])
print("DRILL 2: same subjects, same PCRE-reported captures, different iteration sequences")
P3=r'(?<n>\d)+'; P4=r'\d*(?<n>\d)'
n=dm=dc=da=0
for L_ in range(1,4):
    for tup in itertools.product('0379',repeat=L_):
        t=''.join(tup); n+=1
        a=whole(P3,t); b=whole(P4,t)
        if a!=b: dm+=1; continue
        if pcaps(P3,t,['n'])!=pcaps(P4,t,['n']): dc+=1
        seq3=list(t); seq4=[t[-1]]   # iterations: P3 every digit, P4 the one capture
        if all(int(x)<5 for x in seq3)!=all(int(x)<5 for x in seq4): da+=1; ex=t
print(" subjects",n,"match differ",dm,"PCRE final-capture differ",dc,"(n: <5) by the sequence rule differ",da,"e.g.",repr(ex),"| engine disagreements",DISAGREE[0])
print("DRILL 3: a value-side bound under all() on zero passes")
P5=r'(?<k>\d+);(?:(?<n>\d),)*'
for t in ['50;','5;','50;7,']:
    print(" ",repr(t),"match",whole(P5,t),"n set",is_set(P5,t,'n'),"k =",pcaps(P5,t,['k'])[0])
DOM=[str(d) for d in range(10) if whole(P5,'0;%d,'%d)]
print("  DOM(n) =",DOM," values > 50:",[d for d in DOM if int(d)>50]," values > 5:",[d for d in DOM if int(d)>5])
print("DRILL 4: membership of a literal in a backreference group's value set is decidable by running the group")
G=r'(?<a>a+)b(?P=a)'
for s in ['aaba','aabaa','aaabaaa','ab']:
    print(" ",repr(s),"in DOM(h):",whole(G,s), "| whole pattern with h set:", whole(r'(?<h>(?<a>a+)b(?P=a))?x',s+'x'))
print("engine disagreements total",DISAGREE[0])
