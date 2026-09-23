import os,subprocess,json
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/ae23a9c2-51e4-4c4d-8f53-5b260a960163/scratchpad"
AFT="/Users/fdicostanzo/pcrec/worktrees/b1ledger/build/pcrec"
PD="/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"
FA=SP+"/fa"
SUBS=[(s,open(FA+"/"+s+".bin","rb").read()) for s in ("t-64k","t-256k","t-1m")]
RATE=23113.3/1376256.0
CASES=[("nested-comment-rec",[],47,None),("wild-codegrammar-json-array-begin",[],91,None),
 ("float-literal-bound",["--engine=vm"],46,None),("file-ext-order",["--engine=vm"],114,None),
 ("wild-secrets-github-pat",["--engine=vm"],95,None),("router-prefix-order",[],114,None),
 ("winpath-near-miss",[],92,None),("email-nested-plus",[],64,None),("floor-byte",[],126,None),
 ("uuid-near-miss",[],45,37),("ipv4-near-miss",[],46,16),("keyword-prefix-order",[],110,None),
 ("wild-validator-uuid-grok",["--no-captures"],45,None),("logparse-atomic-removed",["--no-captures"],32,None)]
out={}
for name,extra,rb,endw in CASES:
    pat=open(PD+"/"+name+".rx","rb").read().decode("latin-1")
    r=subprocess.run([AFT,"--features","all"]+extra+["--pattern",pat,"-o",FA+"/art.c"],capture_output=True)
    if r.returncode: print(name,"REFUSED"); continue
    c=subprocess.run(["gcc-16","-O2","-I",FA,"-o",FA+"/m",FA+"/main.c",FA+"/art.c"],capture_output=True)
    if c.returncode: print(name,"BUILD FAIL",c.stderr.decode()[:200]); continue
    tot_calls=0; tot_scan=0; tot_m=0
    for sid,b in SUBS:
        p=subprocess.run([FA+"/m",FA+"/"+sid+".bin"],capture_output=True,timeout=600)
        spans=[tuple(map(int,l.split())) for l in p.stdout.decode().split("\n") if l.strip()]
        tot_m+=len(spans)
        pos=0; calls=0; scan=0
        for (s,e) in spans+[(None,None)]:
            calls+=1
            lo=pos
            if endw is not None and len(b)>endw and lo<len(b)-endw: lo=len(b)-endw
            i=b.find(bytes([rb]),lo)
            scan += (len(b)-lo) if i<0 else (i-lo+1)
            if s is None: break
            pos = e if e>s else s+1
            if pos>len(b): break
        tot_calls+=calls; tot_scan+=scan
    out[name]={"calls":tot_calls,"scan":tot_scan,"matches":tot_m,
               "pred_ns":tot_scan*RATE+tot_calls*2.5}
    print("%-36s matches=%-8d calls=%-8d scanbytes=%-9d pred_added_ns=%.1f"%(name,tot_m,tot_calls,tot_scan,out[name]["pred_ns"]))
json.dump(out,open(SP+"/findall.json","w"),indent=0)
