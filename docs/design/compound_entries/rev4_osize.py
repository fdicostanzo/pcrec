#!/usr/bin/env python3
# rev 4 SCRATCH-GRADE probe (lane cmprev4): whole-.o bytes per layout. usage:
#   python3 -I rev4_osize.py PCREC THIS_DIR SCRATCH > results/rev4_osize.tsv
# scratch: .o size of real artifacts under three part layouts (gcc / shared / inline),
# at -O2 and -O2 -fPIC. Reuses probe_layout.py's variant(). Compile-only, no clock.
import os, re, subprocess, sys
sys.path.insert(0, sys.argv[2])
import probe_layout as pl
pcrec, scratch = sys.argv[1], sys.argv[3]
W = [w for w in pl.WITNESSES] + [
    ("vm-hybrid-alt5", [], r"(foo|bar|baz|qux|quux)\d+", None),
    ("vm-hybrid-cls", [], r"([a-z]+)@([a-z]+)\.com", None),
]
def secs(obj):
    r = pl.run(["size", "-A", obj]); d = {}
    for l in r.stdout.splitlines():
        p = l.split()
        if len(p) >= 2 and p[0].startswith("."):
            try: d[p[0]] = int(p[1])
            except ValueError: pass
    return d
print("witness\tregime\tlayout\trefused\ttext\teh_frame\talloc_total\to_file\to_stripped\tnfuncs")
for label, args, pat, _ in W:
    base = os.path.join(scratch, label)
    r = pl.run([pcrec, "-p", "rx", *args, "-o", base + ".c", "--pattern", pat])
    if r.returncode: print(label, "REFUSED", r.stderr[:80]); continue
    src = open(base + ".c", encoding="latin-1").read()
    for regime, extra in (("O2", []), ("O2-fPIC", ["-fPIC"])):
        for layout in ("gcc", "shared", "inline"):
            refused = set()
            while True:
                if layout == "gcc": txt, parts = pl.variant(src, lambda n: None)
                elif layout == "shared": txt, parts = pl.variant(src, lambda n: "__attribute__((noinline,noclone))")
                else: txt, parts = pl.variant(src, lambda n: None if n in refused else "__attribute__((always_inline)) inline")
                vc = f"{base}.{regime}.{layout}.c"; open(vc, "w", encoding="latin-1").write(txt)
                obj = vc[:-2] + ".o"
                r = pl.run(["gcc", "-O2", *extra, "-std=gnu11", "-c", "-o", obj, vc])
                if r.returncode == 0: break
                bad = set(re.findall(r"function [‘'](\w+)[’'] can never be (?:copied|inlined)", r.stderr)) & set(parts)
                if layout != "inline" or not bad or bad <= refused:
                    print(label, regime, layout, "FAIL", r.stderr[:200]); obj = None; break
                refused |= bad
            if not obj: continue
            s = secs(obj)
            alloc = sum(v for k, v in s.items() if k in (".text", ".rodata", ".data", ".bss") or k.startswith(".rodata") or k.startswith(".data.rel"))
            st = obj + ".s.o"; pl.run(["strip", "--strip-unneeded", "-o", st, obj])
            nf = len(pl.fn_sizes(obj))
            print(f"{label}\t{regime}\t{layout}\t{','.join(sorted(refused)) or '-'}\t{s.get('.text',0)}\t{s.get('.eh_frame',0)}\t{alloc}\t{os.path.getsize(obj)}\t{os.path.getsize(st)}\t{nf}", flush=True)
