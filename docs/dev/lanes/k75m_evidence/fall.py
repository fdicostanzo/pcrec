import subprocess,collections
PCREC='/Users/fdicostanzo/pcrec/worktrees/k75m/build/pcrec'
PATS=['a','.','x*','a|','\\B','\\b','(?<=a)b','(?<!a)b','(?<=.)x*','^a','b$']
W='/tmp/claude-k75m'
out=open(W+'/findall_diff.txt','w')
print('%-10s %6s %10s %10s'%('pattern','n','cur!=pcre2','m1!=pcre2'))
for p in PATS:
    subprocess.check_call([PCREC,'-p','rx','-e','utf8','--features','all','-o','art.c','--pattern',p],cwd=W)
    subprocess.check_call(['gcc-16','-O1','-DART_H="art.h"','-I.','-o','fa','fa_drv.c','art.c'],cwd=W)
    A=[l.split('\t') for l in subprocess.check_output([W+'/fa'],cwd=W).decode().split('\n') if l]
    B=dict(l.split('\t') for l in subprocess.check_output([W+'/ff',p],cwd=W).decode().split('\n') if l for l in [l] if '\t' in l) if False else {}
    for l in subprocess.check_output([W+'/ff',p],cwd=W).decode().split('\n'):
        if l:
            k,_,v=l.partition('\t'); B[k]=v
    dc=dm=0; ex=collections.defaultdict(list)
    for h,cur,m1 in A:
        ref=B[h]
        if cur!=ref: dc+=1
        if m1!=ref:
            dm+=1; ex['m1'].append((h,ref,cur,m1))
        out.write(f'{p}\t{h}\tpcre2={ref}\tcur={cur}\tm1={m1}\n')
    print('%-10s %6d %10d %10d'%(p,len(A),dc,dm))
    for h,ref,cur,m1 in ex['m1'][:3]: print('     e.g. %s pcre2=%s cur=%s m1=%s'%(h,ref,cur,m1))
