import json,math,collections,sys
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
R="/Users/fdicostanzo/pcrec-bench/reports"
pats=json.load(open(SP+"/patterns.json"))
def load(path):
    rows=[];hdr=None
    for l in open(path,encoding="utf-8",errors="surrogateescape"):
        l=l.rstrip("\n")
        if l.startswith("#"): continue
        f=l.split("\t")
        if hdr is None: hdr=f; continue
        rows.append(dict(zip(hdr,f)))
    return rows
FR=load(R+"/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.matrix.tsv")
PCREC=["pcrec_25b1984f_auto-caps-simdna","pcrec_25b1984f_auto-nocaps-simdna",
       "pcrec_25b1984f_vm-caps-simdna","pcrec_25b1984f_vm-in-caps-simdna"]
JIT="libpcre2_10.46_jit-caps-simdna"
VSCAN="vectorscan_5.4.11_block-nosom-nocaps-simd"
ALGO=["libpcre2_10.46_dfa-nocaps-simdna","libpcre2_10.46_interp-caps-simdna",
      "oniguruma_6.9.10_default-caps-simdna","re2_11.0.0_default-caps-simdna",
      "re2_11.0.0_longest-caps-simdna","rust_1.13.1_default-caps-simdna",
      "tre_0.9.0_default-caps-simdna"]
SHORT={"libpcre2_10.46_dfa-nocaps-simdna":"pcre2-dfa","libpcre2_10.46_interp-caps-simdna":"pcre2-interp",
 "libpcre2_10.46_jit-caps-simdna":"pcre2-jit","oniguruma_6.9.10_default-caps-simdna":"onig",
 "re2_11.0.0_default-caps-simdna":"re2","re2_11.0.0_longest-caps-simdna":"re2-longest",
 "rust_1.13.1_default-caps-simdna":"rust","tre_0.9.0_default-caps-simdna":"tre",
 VSCAN:"vectorscan",
 "pcrec_25b1984f_auto-caps-simdna":"auto-caps","pcrec_25b1984f_auto-nocaps-simdna":"auto-nocaps",
 "pcrec_25b1984f_vm-caps-simdna":"vm-caps","pcrec_25b1984f_vm-in-caps-simdna":"vm-in"}
def num(v):
    try: return float(v)
    except: return None
out=[]
nonnum=[]
for r in FR:
    best=num(r["best_ns"])
    ns={}
    st={}
    for k,v in r.items():
        if k in ("subbench","pattern","regime_or_na","form","best_testee","best_ns"): continue
        x=num(v)
        if x is None: st[k]=v
        else: ns[k]=x*best
    pc={k:ns[k] for k in PCREC if k in ns}
    algo={k:ns[k] for k in ALGO if k in ns}
    rec=dict(pattern=r["pattern"],regime=r["regime_or_na"],form=r["form"],
             best_testee=SHORT.get(r["best_testee"],r["best_testee"]),best_ns=best,
             ns={SHORT[k]:v for k,v in ns.items()},st={SHORT.get(k,k):v for k,v in st.items()},
             family=pats.get(r["pattern"],{}).get("family","?"),
             requires=pats.get(r["pattern"],{}).get("requires",""))
    if not pc:
        rec["class"]="pcrec-nonnumeric"; nonnum.append(rec); out.append(rec); continue
    pbk=min(pc,key=pc.get); rec["pcrec_best"]=SHORT[pbk]; rec["pcrec_ns"]=pc[pbk]
    if not algo:
        rec["class"]="no-algo-target"; out.append(rec); continue
    abk=min(algo,key=algo.get); rec["algo"]=SHORT[abk]; rec["algo_ns"]=algo[abk]
    rec["ratio"]=pc[pbk]/algo[abk]
    jns=ns.get(JIT); rec["jit_ns"]=jns
    rec["jit_ratio"]=(pc[pbk]/jns) if jns else None
    vns=ns.get(VSCAN); rec["vscan_ratio"]=(pc[pbk]/vns) if vns else None
    rec["class"]="ranked"
    out.append(rec)
json.dump(out,open(SP+"/rank.json","w"),indent=0)
# family weights over ranked rows
famrows=collections.Counter(r["family"] for r in out)
for r in out:
    r["w"]=1.0/famrows[r["family"]]
    if r.get("ratio") and r["ratio"]>1: r["score"]=r["w"]*math.log2(r["ratio"])
    else: r["score"]=0.0
json.dump(out,open(SP+"/rank.json","w"),indent=0)
rk=[r for r in out if r["class"]=="ranked"]
print("ranked",len(rk),"nonnum",len(nonnum),"noalgo",len([r for r in out if r["class"]=="no-algo-target"]))
print("pcrec ahead or tied (ratio<=1):",len([r for r in rk if r["ratio"]<=1.0]))
rk.sort(key=lambda r:-r["score"])
for r in rk[:40]:
    print(f'{r["score"]:7.3f} {r["ratio"]:12.2f}x  {r["pattern"]:32s} {r["regime"][:5]:5s} {r["family"]:20s} pcrec={r["pcrec_best"]:11s}{r["pcrec_ns"]:12.1f}  algo={r["algo"]:12s}{r["algo_ns"]:12.1f}  jitr={r["jit_ratio"]}')
