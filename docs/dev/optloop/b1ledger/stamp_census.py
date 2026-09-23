import os,subprocess,sys,re,json
sys.path.insert(0,"/Users/fdicostanzo/pcrec-bench/bench/capability")
sys.path.insert(0,"/Users/fdicostanzo/pcrec-bench")
import captext as ct
SP=os.environ["SP"]
AFT="/Users/fdicostanzo/pcrec/worktrees/b1ledger/build/pcrec"
PD="/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"
subs=[("t-64k",ct.text(64*1024,0xC0FFEE1)),("t-256k",ct.text(256*1024,0xC0FFEE2)),("t-1m",ct.text(1024*1024,0xC0FFEE3))]
TOT=sum(len(b) for _,b in subs)
out={}
wd=SP+"/cen"; os.makedirs(wd,exist_ok=True)
for fn in sorted(os.listdir(PD)):
    if not fn.endswith(".rx"): continue
    name=fn[:-3]; pat=open(os.path.join(PD,fn),"rb").read()
    row={"pattern":name}
    for tag,extra in (("auto",[]),("nocaps",["--no-captures"]),("vm",["--engine=vm"])):
        cf=os.path.join(wd,"a.c")
        r=subprocess.run([AFT,"--features","all"]+extra+["--pattern",pat.decode("latin-1"),"-o",cf],
                         capture_output=True)
        if r.returncode!=0:
            row[tag]="refused"; continue
        src=open(cf,encoding="utf-8",errors="replace").read()
        d={}
        for k in ("RX_ENGINE","RX_REQ_BYTE","RX_END_WINDOW","RX_VM_START","RX_DFA_PREFILTER","RX_DFA_START","RX_VM_PREFILTER"):
            m=re.search(r'^#define %s "?([^"\n]*)"?$'%k,src,re.M)
            d[k]=m.group(1).strip() if m else "-"
        m=re.search(r'const size_t start_max = ([^;]*);',src)
        d["start_max"]=m.group(1).strip() if m else "-"
        d["one_start"] = ("fully ^-anchored" in src and "start_max = 0" in src) or ("attempt_max = search_from" in src)
        d["has_memchr_precheck"] = bool(re.search(r'!memchr\(subject \+ search_from',src))
        row[tag]=d
    # byte census
    rb=None
    for tag in ("auto","nocaps","vm"):
        v=row.get(tag)
        if isinstance(v,dict) and v["RX_REQ_BYTE"] not in ("-","none",""):
            rb=int(v["RX_REQ_BYTE"]); break
    if rb is not None:
        firsts=[]; cnt=0
        for sid,b in subs:
            i=b.find(bytes([rb])); firsts.append(i); cnt+=b.count(bytes([rb]))
        row["req_byte"]=rb
        row["req_count_thr"]=cnt
        row["scan_bytes_thr"]=sum((len(b) if f<0 else f+1) for (sid,b),f in zip(subs,firsts))
        row["absent_thr"]=all(f<0 for f in firsts)
        row["firsts"]=firsts
    out[name]=row
json.dump(out,open(SP+"/census.json","w"),indent=0)
print("patterns:",len(out),"total subject bytes:",TOT)
