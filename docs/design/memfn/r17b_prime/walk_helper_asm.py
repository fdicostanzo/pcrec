# r17b_prime: does moving pcrec's table walk out of the use and into a kit
# helper reached through the per-call struct (the scaffold an R0 site would
# carry at SIMD-off, note §4.1) compile to the SAME machine code as today's
# inline walk? Reads spike1's V0 (main's walk text) read-only, writes one
# twin per cell into OUT, compiles both at gcc -O2 and compares the holding
# function's disassembly with addresses stripped. No timing.
#   usage: python3 -I walk_helper_asm.py SPIKE_BIN_DIR OUT_DIR
import re, subprocess, sys, os
S, OUT = sys.argv[1], sys.argv[2]
os.environ["TMPDIR"] = OUT
def dis(obj, fn):
    t = subprocess.run(["objdump", "-d", "--no-show-raw-insn", obj], capture_output=True, text=True).stdout
    m = re.search(r"<" + fn + r">:\n(.*?)\n\n", t, re.S)
    return [re.sub(r"[0-9a-f]{2,}", "", l.split(":", 1)[1]).strip() for l in m.group(1).splitlines()]
for c in ["dig", "bounded", "dfa-hat", "vm-hat", "hex-run", "vm-hat-1"]:
    os.makedirs(f"{OUT}/{c}", exist_ok=True)
    v0 = open(f"{S}/{c}/V0/art.c").read()
    m = re.search(r"^( *)while \(((scan|attempt)_position)( \+ 1)? < subject_length && !(\w+)\[subject\[\2\]\]\) \2\+\+;\n", v0, re.M)
    ind, pos, eb, t = m.group(1), m.group(2), m.group(4) or "", m.group(5)
    helper = ("struct rx__c { const unsigned char *s; size_t n; size_t base, top; unsigned long long m; unsigned char f; };\n"
              "static inline size_t rx__walk(const struct rx__c *c, size_t lo, const unsigned char *t)\n{\n"
              f"    while (lo{eb} < c->n && !t[c->s[lo]]) lo++;\n    return lo;\n}}\n"
              "static inline unsigned char rx__form(size_t n, size_t lo) { (void)n; (void)lo; return 0; }\n"
              "static inline size_t rx__next(struct rx__c *c, size_t lo, const unsigned char *t) { return rx__walk(c, lo, t); }\n")
    last_inc = [mm.end() for mm in re.finditer(r"^#include [^\n]*\n", v0, re.M)][-1]
    v = v0[:last_inc] + helper + v0[last_inc:]
    guard = f"{pos} < rx__c.n" + (f" && rx__c.n - {pos} > 1" if eb else "")
    v = v.replace(m.group(0).strip(), f"if ({guard}) {pos} = rx__next(&rx__c, {pos}, {t});")   # every use, each at its own indent
    k = v.find("    size_t scan_position = search_from;") if pos == "scan_position" else v.find("    attempt_position = search_from;")
    v = v[:k] + "    struct rx__c rx__c = { subject, subject_length, 0, 0, 0, rx__form(subject_length, search_from) };\n" + v[k:]
    open(f"{OUT}/{c}/walkhelper.c", "w").write(v); open(f"{OUT}/{c}/V0.c", "w").write(v0)
    open(f"{OUT}/{c}/art.h", "w").write(open(f"{S}/{c}/V0/art.h").read())
    fn = "rx_search" if pos == "scan_position" else "rx_search_in"   # the VM run is inlined there
    for f in ("V0", "walkhelper"):
        subprocess.run(["gcc", "-O2", "-c", "-o", f"{OUT}/{c}/{f}.o", f"{OUT}/{c}/{f}.c"], check=True)
    a, b = dis(f"{OUT}/{c}/V0.o", fn), dis(f"{OUT}/{c}/walkhelper.o", fn)
    print(f"{c:9s} {fn:14s} inline-walk {len(a):4d} insns  helper-walk {len(b):4d} insns  identical={a == b}")
