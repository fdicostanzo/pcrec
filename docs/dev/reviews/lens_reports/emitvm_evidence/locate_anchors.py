import csv,sys
SRC="/Users/fdicostanzo/pcrec/src/gen/emit_vm.c"
CEN="/Users/fdicostanzo/pcrec/worktrees/revtools/tools/review/out/function_census.tsv"
txt=open(SRC,encoding='utf-8',errors='replace').read()
# line offsets
offs=[0]
for i,ch in enumerate(txt):
    if ch=='\n': offs.append(i+1)
def lineof(pos):
    lo,hi=0,len(offs)-1
    while lo<hi:
        mid=(lo+hi+1)//2
        if offs[mid]<=pos: lo=mid
        else: hi=mid-1
    return lo+1
funcs=[]
with open(CEN) as f:
    r=csv.reader(f,delimiter='\t'); next(r); hdr=next(r)
    for x in r:
        d=dict(zip(hdr,x))
        if 'emit_vm.c' in d['file']: funcs.append((int(d['start_line']),int(d['end_line']),d['name']))
funcs.sort()
def fnof(ln):
    best=None
    for s,e,n in funcs:
        if s<=ln<=e: best=n
    return best or "(file scope)"
raw=open("/private/tmp/claude-501/-Users-fdicostanzo-pcrec/15fa957d-51f7-4fd3-8c4c-d72a871d5530/scratchpad/ep2/anchors.tsv.raw",encoding='utf-8',errors='replace').read()
recs=[r for r in raw.split('\n') if '\x01' in r]
# records may be multi-line; re-split properly: join lines until next record start
lines=raw.split('\n')
recs=[]
cur=None
for l in lines:
    parts=l.split('\x01')
    if len(parts)>=3 and parts[0].startswith('S') and parts[0].endswith('.sh'):
        if cur: recs.append(cur)
        cur=[parts[0],parts[1],'\x01'.join(parts[2:])]
    elif cur is not None:
        cur[2]+='\n'+l
if cur: recs.append(cur)
print(f"records: {len(recs)}")
rows=[]
for name,slot,before in recs:
    before=before.rstrip('\n')
    n=txt.count(before)
    if n==0:
        rows.append((None,name,slot,0,"NOT FOUND",before.split('\n')[0][:60]))
        continue
    pos=txt.find(before)
    ln=lineof(pos)
    rows.append((ln,name,slot,n,fnof(ln),before.split('\n')[0][:70]))
rows.sort(key=lambda r:(r[0] is None, r[0]))
for ln,name,slot,n,fn,snip in rows:
    print(f"{str(ln):>6} {n:>2}x {fn:<26} {name[:-3]:<44} {snip}")
