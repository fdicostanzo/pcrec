import json,collections
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
R="/Users/fdicostanzo/pcrec-bench/reports"
F=R+"/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.subject-grain.tsv"
hdr=None; per=collections.defaultdict(dict)
for l in open(F,encoding="utf-8",errors="surrogateescape"):
    l=l.rstrip("\n")
    if l.startswith("#"): continue
    f=l.split("\t")
    if hdr is None: hdr=f; continue
    r=dict(zip(hdr,f))
    if r["regime_or_na"]!="large-subject-throughput" or r["metric"]!="median_ns": continue
    try: v=float(r["value"])
    except: continue
    per[(r["pattern"],r["testee"])][r["subject_or_na"]]=v
json.dump({ "%s|%s"%k:v for k,v in per.items()},open(SP+"/perbyte.json","w"))
SHORT={"libpcre2_10.46_dfa-nocaps-simdna":"pcre2-dfa","libpcre2_10.46_interp-caps-simdna":"pcre2-interp",
 "libpcre2_10.46_jit-caps-simdna":"pcre2-jit","oniguruma_6.9.10_default-caps-simdna":"onig",
 "re2_11.0.0_default-caps-simdna":"re2","re2_11.0.0_longest-caps-simdna":"re2-longest",
 "rust_1.13.1_default-caps-simdna":"rust","tre_0.9.0_default-caps-simdna":"tre",
 "vectorscan_5.4.11_block-nosom-nocaps-simd":"vectorscan",
 "pcrec_25b1984f_auto-caps-simdna":"auto-caps","pcrec_25b1984f_auto-nocaps-simdna":"auto-nocaps",
 "pcrec_25b1984f_vm-caps-simdna":"vm-caps","pcrec_25b1984f_vm-in-caps-simdna":"vm-in"}
rows=json.load(open(SP+"/rank.json"))
lose=[r for r in rows if r["class"]=="ranked" and r["ratio"]>1.0 and r["regime"]=="large-subject-throughput"]
lose.sort(key=lambda r:-r["score"])
print(f'{"pattern":36s} {"who":12s} {"64k":>10s} {"1m":>12s} {"ns/B@1m":>9s} {"x16":>6s} shape')
for r in lose:
    for who in (r["pcrec_best"],r["algo"]):
        k=None
        for full,s in SHORT.items():
            if s==who: k=full
        d=per.get((r["pattern"],k),{})
        a=d.get("t-64k"); b=d.get("t-1m")
        if not a or not b: continue
        g=b/a
        shape="O(1)" if g<2.0 else ("linear" if 10<g<25 else ("sub-lin" if g<=10 else "super"))
        print(f'{r["pattern"]:36.36s} {who:12s} {a:10.1f} {b:12.1f} {b/1048576:9.3f} {g:6.2f} {shape}')
    print()
