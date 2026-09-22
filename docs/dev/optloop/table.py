import json,math,collections,os,re
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
OUT=os.environ.get("OUT",SP+"/cycle1_rows.tsv")
rows=json.load(open(SP+"/rank.json")); st=json.load(open(SP+"/stamps.json"))
pats=json.load(open(SP+"/patterns.json")); p2=json.load(open(SP+"/p2info.json"))
subj=set(open(SP+"/subj/t-1m.bin","rb").read())
VMAP={"auto-caps":"auto-caps","auto-nocaps":"auto-nocaps","vm-caps":"vm-caps","vm-in":"vm-caps"}
def sget(p,v,k):
    e=st.get(p,{}).get(VMAP.get(v,v))
    if not e or e["rc"]!=0: return "refused"
    return e["stamps"].get(k,"-").strip('"')
def g(line,k):
    for f in (line or "").split("\t"):
        if f.startswith(k+"="): return f.split("=",1)[1]
cols=["rank","score","weight","family","pattern","regime","pcrec_variant","pcrec_ns",
      "algo_target","algo_ns","ratio","jit_ns","jit_ratio","vectorscan_ns",
      "engine","engine_sel","dfa_scan","dfa_prefilter","vm_prefilter","vm_prefilter_lang",
      "pcre2_anchored","pcre2_first","pcre2_req","pcre2_req_absent","pcre2_minlen","bucket"]
anch=set(l.split()[0] for l in open(SP+"/anch.txt") if l.strip())
rk=[r for r in rows if r["class"]=="ranked"]
rk.sort(key=lambda r:(-r["score"],-r.get("ratio",0)))
lines=["\t".join(cols)]
for i,r in enumerate(rk,1):
    p,v=r["pattern"],r["pcrec_best"]
    l=p2.get(p,"")
    fct=g(l,"firstcodetype"); first="-"
    if fct=="1": first=repr(chr(int(g(l,"firstcodeunit"))))
    elif fct=="0" and g(l,"bitmapbits") not in (None,"-1"): first="bitmap[%s]"%g(l,"bitmapbits")
    lct=g(l,"lastcodetype"); req="-"; reqab="-"
    if lct=="1":
        cu=int(g(l,"lastcodeunit")); req=repr(chr(cu)); reqab="ABSENT" if cu not in subj else "present"
    vals=[i,"%.4f"%r["score"],"%.4f"%r["w"],r["family"],p,r["regime"],v,"%.1f"%r["pcrec_ns"],
          r["algo"],"%.1f"%r["algo_ns"],"%.4f"%r["ratio"],
          ("%.1f"%r["jit_ns"]) if r.get("jit_ns") else "-",
          ("%.4f"%r["jit_ratio"]) if r.get("jit_ratio") else "-",
          ("%.1f"%r["ns"]["vectorscan"]) if "vectorscan" in r["ns"] else "-",
          sget(p,v,"RX_ENGINE"),sget(p,v,"RX_ENGINE_SEL"),sget(p,v,"RX_DFA_SCAN"),
          sget(p,v,"RX_DFA_PREFILTER"),sget(p,v,"RX_VM_PREFILTER"),sget(p,v,"RX_VM_PREFILTER_LANG"),
          "yes" if p in anch else "no", first, req, reqab, g(l,"minlength") or "-", ""]
    lines.append("\t".join(str(x) for x in vals))
open(OUT,"w").write("\n".join(lines)+"\n")
print("wrote",OUT,len(lines)-1,"rows")
