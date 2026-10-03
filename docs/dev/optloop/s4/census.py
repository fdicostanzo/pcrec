import glob, os, re, subprocess, collections, sys
P=os.environ.get("PCREC","build/pcrec")
pats=sorted(glob.glob(os.environ.get("BENCH","../pcrec-bench")+"/bench/*/patterns/*.rx"))
OV={3,5,6,7,9,10,11,12,13,14,15}
art=collections.Counter(); lens=collections.Counter(); mov=collections.Counter(); folds=collections.Counter()
OUT=os.environ.get("OUT","cen"); os.makedirs(OUT,exist_ok=True)
for cfg,args in (("auto",[]),("vm",["--engine=vm"])):
    for f in pats:
        pat=open(f,"rb").read().decode("latin-1").rstrip("\n")
        name=f.split("/bench/")[1].replace("/patterns/","/").replace(".rx","")
        enc=["-e","utf8"] if "/utf8/" in f else []
        out=OUT+"/%s_%s.c"%(name.replace("/","_"),cfg)
        r=subprocess.run([P,"--features","all","-p","rx","-o",out,*enc,*args,"--pattern",pat],capture_output=True,timeout=120)
        if r.returncode: art[(cfg,"refused")]+=1; continue
        src=open(out,encoding="latin-1").read()
        art[(cfg,"ok")]+=1
        L=[int(m) for m in re.findall(r'memcmp\([^;]*?", (\d+)\)',src)]
        for l in L: lens[(cfg,l)]+=1
        if any(l in OV for l in L): mov[cfg]+=1
        # caseless per-byte fold tests in VM code: "(subject[...] | 0x20) =="
        nf=len(re.findall(r'\| 0x20\) ==',src))
        if nf: folds[cfg]+=1; 
        if nf>=3 and cfg=="vm" and len(sys.argv)>1: print(name, nf)
print(art); print("artifacts with an overlap-length memcmp:",dict(mov)); print("artifacts with fold-pair tests:",dict(folds))
print(sorted(lens.items()))
