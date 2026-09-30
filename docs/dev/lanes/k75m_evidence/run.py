import subprocess, sys, os, collections, json
PCREC='/Users/fdicostanzo/pcrec/worktrees/k75m/build/pcrec'
LIB='/Users/fdicostanzo/pcrec/worktrees/k75m/build/libpcrec.a'
SUBJ=[ # name, hex
 ('A-e9x','c3a978'),('A-euro-x','e282ac78'),('A-emoji-x','f09f988078'),('A-a-e9-a','61c3a961'),
 ('B-alone','80'),('B-after-ascii','6180'),('B-a-80-a','618061'),('B-after-complete','c3a98061'),
 ('B-run','6180808062'),('B-after-complete-run','e282ac80806a'.replace('6a','61')),
 ('T-trunc-e3-80','e38061'),('T-trunc-f0-9f-98','f09f9861'),('T-trunc-then-ascii-stray','e36180'),
 ('T-trunc-cont-then-stray','e3806180'),('I-ff-80','ff8061'),('I-c0-80','c08061'),
]
PATS=['a','.','x*','\\B','(?<=a)x*','(?<=a).','(?<!a)','(?<=\u00e9)x*','(?<=.)x*']
hexs=[h for _,h in SUBJ]
def kinds(h):
    b=bytes.fromhex(h); n=len(b); k=['S']*(n+1)  # S start/boundary
    def wf(i):
        for L in (1,2,3,4):
            if i+L<=n:
                try:
                    t=b[i:i+L].decode('utf-8')
                    if len(t)==1: return L
                except: pass
        return 0
    i=0; out=['?']*(n+1); out[n]='end'
    i=0
    while i<n:
        L=wf(i)
        if L>=1:
            out[i]='start'
            for j in range(i+1,i+L): out[j]='A'
            i+=L
        else:
            if b[i]&0xC0!=0x80:
                out[i]='start'  # invalid lead (ill-formed start)
                claim={0xC2:2}.get(b[i]) 
                c=b[i]
                cl=2 if 0xC2<=c<=0xDF else 3 if 0xE0<=c<=0xEF else 4 if 0xF0<=c<=0xF4 else 1
                j=i+1
                while j<n and j<i+cl and b[j]&0xC0==0x80: out[j]='T'; j+=1
                i=j
            else:
                out[i]='B'; i+=1
    return out
res={}
for p in PATS:
    d='/tmp/claude-k75m/art'; 
    subprocess.check_call([PCREC,'-p','rx','-e','utf8','--features','all','-o',d+'.c','--pattern',p])
    subprocess.check_call(['gcc-16','-O1','-DART_H="art.h"','-I/tmp/claude-k75m','-o',d+'_drv','pd.c',d+'.c'],cwd='/tmp/claude-k75m')
    po=subprocess.check_output([d+'_drv']+hexs).decode().splitlines()
    qo=subprocess.check_output(['./pr',p]+hexs,cwd='/tmp/claude-k75m').decode().splitlines()
    for l in po+qo:
        si,f,arm,r=l.split('\t'); res[(p,int(si),int(f),arm)]=r
json.dump({'|'.join(map(str,k)):v for k,v in res.items()},open('/tmp/claude-k75m/res.json','w'))
with open('/tmp/claude-k75m/raw.tsv','w') as o:
    o.write('pattern\tsubject\thex\tfrom\tposkind\tarm\tresult\n')
    for (p,si,f,arm),r in sorted(res.items(), key=lambda kv:(PATS.index(kv[0][0]),kv[0][1],kv[0][2],kv[0][3])):
        o.write(f'{p}\t{SUBJ[si][0]}\t{SUBJ[si][1]}\t{f}\t{kinds(SUBJ[si][1])[f]}\t{arm}\t{r}\n')
print(len(res))
