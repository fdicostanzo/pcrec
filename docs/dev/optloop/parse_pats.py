import json,collections,re
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
raw=open(SP+"/src.tsv","rb").read()
lines=raw.split(b"\n")
cols="kind line name value pattern flags features features_only encoding engine budget_steps budget_frames with from pcrec export tags oracle esc tune".split()
def dec(b):
    out=bytearray(); i=0
    while i<len(b):
        c=b[i]
        if c==0x5c and i+1<len(b):
            n=b[i+1]
            if n==0x5c: out.append(0x5c); i+=2; continue
            if n==0x74: out.append(9); i+=2; continue
            if n==0x6e: out.append(10); i+=2; continue
            if n==0x72: out.append(13); i+=2; continue
            if n==0x78 and i+3<len(b):
                try: out.append(int(b[i+2:i+4],16)); i+=4; continue
                except ValueError: pass
        out.append(c); i+=1
    return bytes(out)
out={}
for l in lines:
    if l.startswith(b"#") or not l.strip(): continue
    f=l.split(b"\t")
    if len(f)<len(cols): continue
    r=dict(zip(cols,f))
    if r["kind"] not in (b"pattern",b"pattern-esc"): continue
    tags=r["tags"].decode()
    t=dict(kv.split("=",1) for kv in tags.split(", ") if "=" in kv)
    out[r["name"].decode()]={"pattern_b64":__import__("base64").b64encode(dec(r["pattern"])).decode(),
        "family":t.get("family",""),"hazard":t.get("hazard",""),"requires":t.get("requires",""),
        "kind":r["kind"].decode(),"line":int(r["line"])}
json.dump(out,open(SP+"/patterns.json","w"),indent=0)
print(len(out))
import base64
for n in ["wild-codegrammar-json-array-begin","bracket-array-define","ipv4-near-miss"]:
    print(n, base64.b64decode(out[n]["pattern_b64"])[:120])
