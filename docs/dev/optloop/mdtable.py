import json,os
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
rows=json.load(open(SP+"/rank.json")); st=json.load(open(SP+"/stamps.json"))
SCALAR=["pcre2-dfa","pcre2-interp","onig","re2","re2-longest","tre"]
VMAP={"auto-caps":"auto-caps","auto-nocaps":"auto-nocaps","vm-caps":"vm-caps","vm-in":"vm-caps"}
def sget(p,v,k):
    e=st.get(p,{}).get(VMAP.get(v,v))
    if not e or e["rc"]!=0: return "refused"
    return e["stamps"].get(k,"—").strip('"')
def engcell(p,v):
    eng=sget(p,v,"RX_ENGINE")
    if eng=="dfa": return "dfa/%s/%s"%(sget(p,v,"RX_DFA_SCAN"),sget(p,v,"RX_DFA_PREFILTER"))
    if eng=="vm":  return "vm/%s"%sget(p,v,"RX_VM_PREFILTER")
    return eng
rk=[r for r in rows if r["class"]=="ranked"]
rk.sort(key=lambda r:(-r["score"],-r["ratio"]))
L=["| # | score | family | pattern | regime | pcrec variant | pcrec ns | algorithmic target | target ns | ratio | pcrec artifact (engine/scan/prefilter) | best scalar | scalar × |",
   "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i,r in enumerate(rk,1):
    sc={k:v for k,v in r["ns"].items() if k in SCALAR}
    b=min(sc,key=sc.get) if sc else "—"
    sx=("%.2f"%(r["pcrec_ns"]/sc[b])) if sc else "—"
    reg="thr" if r["regime"].startswith("large") else "srch"
    L.append("| %d | %.4f | %s | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s |"%(
        i,r["score"],r["family"],r["pattern"],reg,r["pcrec_best"],
        ("%.1f"%r["pcrec_ns"]),r["algo"],("%.1f"%r["algo_ns"]),
        ("**%.2f**"%r["ratio"]) if r["ratio"]>1 else "%.2f"%r["ratio"],
        engcell(r["pattern"],r["pcrec_best"]),b,sx))
open(SP+"/table.md","w").write("\n".join(L)+"\n")
print(len(rk),"rows written")
