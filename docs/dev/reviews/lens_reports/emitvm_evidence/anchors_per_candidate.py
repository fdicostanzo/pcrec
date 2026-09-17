SRC="/Users/fdicostanzo/pcrec/src/gen/emit_vm.c"
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
lines=raw.split('\n'); recs=[]; cur=None
for l in lines:
    p=l.split('\x01')
    if len(p)>=3 and p[0].startswith('S') and p[0].endswith('.sh'):
        if cur: recs.append(cur)
        cur=[p[0],p[1],'\x01'.join(p[2:])]
    elif cur is not None: cur[2]+='\n'+l
if cur: recs.append(cur)
spans=[]
for n,s,b in recs:
    b=b.rstrip('\n')
    pos=txt.find(b)
    if pos<0: continue
    spans.append((lineof(pos),lineof(pos+len(b)-1),n[:-3],s))
CANDS=[
 ("E1a vm_call save block",6818,6826),
 ("E1b vm_splice save block",6942,6950),
 ("E1c vm_splice deliver block",7009,7021),
 ("E1d vm_splice restore block",7023,7032),
 ("E2a span-scan possessive",4151,4159),
 ("E2b span-scan greedy",4291,4304),
 ("E3a bounds cursor",4105,4107),
 ("E3b bounds revdet",4862,4864),
 ("E3c bounds frames",5761,5764),
 ("F7 vm_wordb arm",7312,7348),
 ("F7 vm_cap arm",7349,7415),
 ("F7 vm_bref arm",7416,7555),
 ("F7 vm_cat arm",7557,7592),
 ("F7 vm_count_slots A_LOOK",2609,2709),
 ("F7 vm_count_slots A_REP",2777,2912),
 ("F1a vm_resolve_nonnull",8790,8812),
 ("F1a2 region/grpset pre-pass",8824,8866),
 ("F1b vm_build_region_saves",9000,9188),
 ("F1c vm_plan_capacities",9189,9405),
 ("F14 vm_look_behind branch loop",6315,6444),
 ("listing vm_render_listing",7777,8277),
 ("prologue+stamps",9405,10075),
 ("run_state+macros",10075,10400),
 ("run fn preamble/reset/dispatch",10400,10770),
 ("trailers",10770,10970),
 ("search entry+retry",10970,11310),
 ("public entries/info/main",11310,11575),
]
for nm,lo,hi in CANDS:
    inside=[(a,b,n) for a,b,n,s in spans if a>=lo and b<=hi]
    strad=[(a,b,n) for a,b,n,s in spans if not(b<lo or a>hi) and not(a>=lo and b<=hi)]
    print(f"{nm:<34} [{lo}-{hi}]  inside={len(inside):<3} straddling={len(strad)}")
    for a,b,n in inside: print(f"      in  {a}-{b}  {n}")
    for a,b,n in strad: print(f"      STR {a}-{b}  {n}")
