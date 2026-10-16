#!/usr/bin/env python3
# rev 4 SCRATCH-GRADE probe (lane cmprev4): per-CLASS .o bytes. usage:
#   python3 -I rev4_osize_cls.py PCREC THIS_DIR SCRATCH > results/rev4_osize_cls.tsv
# scratch: per-CLASS .o size: only the named class's parts get the attribute.
import os, re, subprocess, sys
sys.path.insert(0, sys.argv[2]); import probe_layout as pl
pcrec, scratch = sys.argv[1], sys.argv[3]
CLS = {"prefilter": re.compile(r"^rx_prefilter$"), "compound": re.compile(r"^rx__\w+_search$"),
       "vm-entry(A1,owned)": re.compile(r"^rx_(match_anchored|search_run|match_run|match_caps_run)$")}
W = [("compound-split", [], r"^\s+|\s+$"), ("vm-hybrid-frameless", [], r"(a)b"),
     ("vm-hybrid-framed", [], r"(a|ab)(c|bcd)(d*)"), ("vm-hybrid-alt5", [], r"(foo|bar|baz|qux|quux)\d+"),
     ("vm-hybrid-cls", [], r"([a-z]+)@([a-z]+)\.com"),
     ("vm-hybrid-cls-inline-rung", ["--vm-entry-shape=4"], r"([a-z]+)@([a-z]+)\.com"),
     ("vm-hybrid-cls-plain-rung", ["--vm-entry-shape=1"], r"([a-z]+)@([a-z]+)\.com")]
def text(obj):
    for l in pl.run(["size", "-A", obj]).stdout.splitlines():
        p = l.split()
        if p and p[0] == ".text": return int(p[1])
print("witness\tclass\tlayout\trefused\ttext\to_file\tfn_sizes_of_class_or_callers")
for label, args, pat in W:
    base = os.path.join(scratch, "c_" + label)
    if pl.run([pcrec, "-p", "rx", *args, "-o", base + ".c", "--pattern", pat]).returncode: continue
    src = open(base + ".c", encoding="latin-1").read()
    lines0, ds = pl.defs(src)
    for cname, cre in CLS.items():
        members = [n for _, n in ds if cre.match(n)]
        if not members: continue
        for layout in ("gcc", "shared", "inline"):
            refused = set()
            while True:
                def a(n):
                    if not cre.match(n) or layout == "gcc": return None
                    if layout == "shared": return "__attribute__((noinline,noclone))"
                    return None if n in refused else "__attribute__((always_inline)) inline"
                txt, _ = pl.variant(src, a)
                vc = f"{base}.{cname.split("(")[0]}.{layout}.c"; open(vc, "w", encoding="latin-1").write(txt)
                obj = vc[:-2] + ".o"
                r = pl.run(["gcc", "-O2", "-std=gnu11", "-c", "-o", obj, vc])
                if r.returncode == 0: break
                bad = set(re.findall(r"function [‘'](\w+)[’'] can never be (?:copied|inlined)", r.stderr))
                if layout != "inline" or not bad or bad <= refused: obj = None; print(label, cname, layout, "FAIL", r.stderr[:160]); break
                refused |= bad
            if not obj: continue
            fs = pl.fn_sizes(obj)
            print(f"{label}\t{cname}\t{layout}\t{','.join(sorted(refused)) or '-'}\t{text(obj)}\t{os.path.getsize(obj)}\t{','.join(f'{k}={v}' for k,v in sorted(fs.items()) if cre.match(k) or 'search' in k)}", flush=True)
