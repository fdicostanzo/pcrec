import csv
SRC="/Users/fdicostanzo/pcrec/src/gen/emit_vm.c"
CEN="/Users/fdicostanzo/pcrec/worktrees/revtools/tools/review/out/function_census.tsv"
txt=open(SRC,encoding='utf-8',errors='replace').read()
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
raw=open("/private/tmp/claude-501/-Users-fdicostanzo-pcrec/15fa957d-51f7-4fd3-8c4c-d72a871d5530/scratchpad/ep2/anchors.tsv.raw",encoding='utf-8',errors='replace').read()
ls=raw.split('\n'); recs=[]; cur=None
for l in ls:
    p=l.split('\x01')
    if len(p)>=3 and p[0].startswith('S') and p[0].endswith('.sh'):
        if cur: recs.append(cur)
        cur=[p[0],p[1],'\x01'.join(p[2:])]
    elif cur is not None: cur[2]+='\n'+l
if cur: recs.append(cur)
anch=[]
for n,s,b in recs:
    b=b.rstrip('\n'); pos=txt.find(b)
    if pos>=0: anch.append((lineof(pos),n[:-3]))
funcs=[]
with open(CEN) as f:
    r=csv.reader(f,delimiter='\t'); next(r); h=next(r)
    for x in r:
        d=dict(zip(h,x))
        if 'emit_vm.c' in d['file']: funcs.append((int(d['start_line']),int(d['end_line']),int(d['code_lines']),d['name']))
funcs.sort()
BUFS=[758,946,2984,3066,3836,4078,4105,4176,4857,4862,5345,5460,5761,6379,6818,6819,6942,6943,7009,7010,7023,7024,7088,7401,7477,7516,7676,8003,8156,8167,8200,8215,10033,10377,10383,10594,10770,10870,11118,11127]
L=[("L0 file header / capacities / seam ids",1,233),
   ("L1 emitter state (Vm, VEvent, Cost, ladders) + Vm helpers",234,779),
   ("L2 slot layout + slot naming",780,1078),
   ("L3 AST predicates + class pool",1079,1536),
   ("L4 rung-fitness analysis",1537,1842),
   ("L5 cost + slot counting",1843,2915),
   ("L6 emission primitives + MRL",2916,3278),
   ("L7 island rung",3279,3963),
   ("L8 rung emitters",3964,6003),
   ("L9 lookaround",6004,6547),
   ("L10 subroutines: W, call, splice, region",6548,7128),
   ("L11 the dispatcher (vm_emit)",7129,7644),
   ("L12 the listing",7645,8278),
   ("L13 frame/trail layout + default entry",8279,8538),
   ("L14 pcrec_emit_vm",8539,11575)]
tot=0
print(f"{'layer':<46}{'span':>12}{'lines':>7}{'code':>6}{'fns':>5}{'anch':>6}{'bufs':>6}")
for nm,lo,hi in L:
    fs=[f for f in funcs if f[0]>=lo and f[1]<=hi]
    code=sum(f[2] for f in fs)
    a=len([1 for ln,_ in anch if lo<=ln<=hi])
    b=len([1 for x in BUFS if lo<=x<=hi])
    tot+=a
    print(f"{nm:<46}{str(lo)+'-'+str(hi):>12}{hi-lo+1:>7}{code:>6}{len(fs):>5}{a:>6}{b:>6}")
print("anchors accounted:",tot,"of",len(anch))
