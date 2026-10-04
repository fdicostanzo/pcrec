import re, math, subprocess, glob, os, collections
t=open(os.environ.get('PCREC','.')+'/src/core/findings_table.inc').read()
blk=t.split('pcrec_find_tbl_counts_0[256] = {')[1].split('};')[0]
c=[int(x) for x in re.findall(r'(\d+)ull',blk)]; S=sum(c); r=[x/S for x in c]
def cube(tb,k):
    f=~k&0xff; m=0; b=f
    while True:
        m+=r[tb|b]
        if b==0: break
        b=(b-1)&f
    return m
P=os.environ.get('PCREC','.')+'/build/pcrec'
out=collections.Counter(); rows=[]
for f in sorted(glob.glob(os.environ.get('BENCH','../pcrec-bench')+'/bench/*/patterns/*.rx')):
    setn=f.split('/bench/')[1].split('/')[0]
    enc=['-e','utf8'] if setn=='utf8' else []
    pat=open(f,'rb').read().rstrip(b'\n')
    try: o=subprocess.run([x.encode() for x in [P,'--features','all','-p','rx',*enc,'--emit-facts','--pattern']]+[pat],capture_output=True,text=True,timeout=60).stdout
    except subprocess.TimeoutExpired: out['timeout']+=1; continue
    m=re.search(r'\treq_whole_run\t.*?\t(yes|no)\t([0-9a-f/]*)\t',o)
    rr=re.search(r'\treq_run\t.*?\t(yes|no)\t(\S*)\t(\S*)',o)
    rb=re.search(r'\treq_byte\t.*?\t(yes|no)\t(\S*)',o)
    if not m or not m.group(2): out['norun']+=1; continue
    h=m.group(2); hb,_,mk=h.partition('/')
    tb=bytes.fromhex(hb); k=bytes.fromhex(mk) if mk else b'\xff'*len(tb)
    pop=sum(bin(x).count('1') for x in k)
    rated = 'none' not in (rr.group(3) if rr else 'none')
    pb=-sum(math.log2(max(cube(a,b),1e-9)) for a,b in zip(tb,k))
    masked=bool(mk)
    cls=('masked' if masked else 'exact')+('-rated' if rated else '-NONE')
    dec = rated and pb<16
    out[cls]+=1; out[cls+(' DECLINED' if dec else ' kept')]+=1
    rows.append((os.path.basename(f),setn,cls,pop,round(pb,1),h,rb.group(2) if rb else '',dec))
for k,v in sorted(out.items()): print(k,v)
for x in rows:
    if x[2].startswith('masked') or x[7]: print(*x)
print("---- row-5 census: set pick rarer than the run's scan member")
for f in sorted(glob.glob(os.environ.get('BENCH','../pcrec-bench')+'/bench/*/patterns/*.rx')):
    setn=f.split('/bench/')[1].split('/')[0]
    enc=['-e','utf8'] if setn=='utf8' else []
    pat=open(f,'rb').read().rstrip(b'\n')
    o=subprocess.run([x.encode() for x in [P,'--features','all','-p','rx',*enc,'--emit-facts','--pattern']]+[pat],capture_output=True,text=True,timeout=60).stdout
    rr=re.search(r'\treq_run\t.*?\t(yes|no)\t(\S*)\t(\S*)',o); rs=re.search(r'\treq_set\t.*?\t(yes|no)\t(\S*)',o)
    why=re.search(r'RX_REQ_WHY\t"(\S*)"',o)
    if not rr or rr.group(2) in ('','none'): continue
    h,_,mk=rr.group(2).partition('/'); hb,_,idx=h.partition('@'); idx=int(idx)
    tb=bytes.fromhex(hb); k=bytes.fromhex(mk) if mk else b'\xff'*len(tb)
    rated='none' not in rr.group(3)
    scan = cube(tb[idx],k[idx]) if rated else (256-sum(1 for _ in range(1)))  # placeholder
    if rated: scan_m=cube(tb[idx],k[idx])
    else: scan_m=2**(8-bin(k[idx]).count('1'))/256
    members=[int(x) for x in rs.group(2).split(',')] if rs and rs.group(2) not in ('none','') else []
    if not members: continue
    sp=min(members,key=lambda b:(r[b] if rated else 1/256)); sp_m=r[sp] if rated else 1/256
    if sp_m < scan_m: print(os.path.basename(f),setn,'masked' if mk else 'exact','rated' if rated else 'NONE',why.group(1) if why else '?','scan=%.4f'%scan_m,'setpick=%d %.5f'%(sp,sp_m))
