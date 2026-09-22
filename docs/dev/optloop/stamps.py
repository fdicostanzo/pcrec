import json,subprocess,os,re,base64
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
P=b"/Users/fdicostanzo/pcrec/worktrees/optrev/build/pcrec"
pats=json.load(open(SP+"/patterns.json"))
outd=SP+"/art"; os.makedirs(outd,exist_ok=True)
VAR={"auto-caps":["--features","all"],
     "auto-nocaps":["--features","all","--no-captures"],
     "vm-caps":["--features","all","--engine=vm"]}
res={}
for name,d in pats.items():
    pb=base64.b64decode(d["pattern_b64"])
    res[name]={}
    for v,flags in VAR.items():
        out=os.path.join(outd,"%s__%s.c"%(re.sub(r'[^A-Za-z0-9_.-]','_',name),v))
        cmd=[P]+[f.encode() for f in flags]+[b"-o",out.encode(),b"--pattern",pb]
        try: r=subprocess.run(cmd,capture_output=True,timeout=300)
        except subprocess.TimeoutExpired:
            res[name][v]={"rc":"timeout"}; continue
        e={"rc":r.returncode}
        if r.returncode!=0:
            e["err"]=r.stderr.decode("utf-8","replace").strip()[:500]
        else:
            txt=open(out,encoding="utf-8",errors="replace").read()
            st={}
            for m in re.finditer(r'^#define\s+(RX_[A-Z0-9_]+)\s+(.*?)\s*$',txt,re.M):
                st[m.group(1)]=m.group(2).strip()
            e["stamps"]=st; e["bytes"]=os.path.getsize(out)
        res[name][v]=e
json.dump(res,open(SP+"/stamps.json","w"),indent=0)
ok=sum(1 for n in res for v in res[n] if res[n][v]["rc"]==0)
print("compiles ok",ok,"of",len(res)*3)
for n in res:
    for v in res[n]:
        if res[n][v]["rc"]!=0: print("FAIL",n,v,"|",res[n][v].get("err","")[:260])
