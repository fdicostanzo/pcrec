# Hand twins for SIZE estimation only (r17bp design note): WALK+V1, WALK+A1,
# WALK+V1+A1 built from spike1's V0 (walk), V1 (R17-b) and A1 (AVX2 W=64) files.
import re, sys
S, out = sys.argv[1], sys.argv[2]
v0 = open(f"{S}/V0/art.c").read(); v1 = open(f"{S}/V1/art.c").read(); a1 = open(f"{S}/A1/art.c").read()
walkm = re.search(r"^ *while \(((scan|attempt)_position)[^\n]*\n", v0, re.M)
walk, pos = walkm.group(0).strip(), walkm.group(1)
tname = re.search(r"!(\w+)\[", walk).group(1)
tbl = re.search(r"    static const unsigned char " + tname + r"\[256\] = \{\n(?:.*\n)*?    \};\n", v0).group(0)
stem = re.search(r"struct (\w+)__c \1__c = \{", v1).group(1)
init_old = f"    struct {stem}__c {stem}__c = {{ subject, subject_length, 0, 0, 0 }};\n"
assert init_old in v1
start = "search_from"
FORM = {2: "    if (span < {t1}) return 0;\n    return 1;\n",
        3: "    if (span < {t1}) return 0;\n    if (span < 64) return 1;\n    return 2;\n"}
def form_fn(k, t1):
    return (f"static inline unsigned char {stem}__form(size_t n, size_t lo)\n{{\n"
            f"    size_t span = n - lo;\n" + FORM[k].format(t1=t1) + "}\n")
def finish(t, ffn, call):
    t = t.replace("    unsigned long long m;\n};", "    unsigned long long m;\n    unsigned char f;\n};", 1)
    t = t.replace(f"static inline size_t {stem}__next_candidate(", ffn + f"static inline size_t {stem}__next_candidate(", 1)
    t = t.replace(init_old, tbl + f"    struct {stem}__c {stem}__c = {{ subject, subject_length, 0, 0, 0, {stem}__form(subject_length, {start}) }};\n", 1)
    def rep(m):
        ind, body = m.group(1), m.group(2)
        body = body.replace(f"{stem}__next_candidate(&{stem}__c, {pos})", call)
        return f"{ind}if ({stem}__c.f == 0) {{ {walk} }}\n{ind}else {body}"
    t, nsub = re.subn(r"^( *)(if \(" + pos + r" < " + stem + r"__c\.n[^\n]*\n)", rep, t, flags=re.M)
    assert nsub >= 1
    return t
one = f"{stem}__next_candidate(&{stem}__c, {pos})"
open(f"{out}/walk_v1.c", "w").write(finish(v1, form_fn(2, 36), one))
a1n = re.search(r"static inline size_t " + stem + r"__next_candidate\(.*?\n\}\n", a1, re.S).group(0)
v1n = re.search(r"static inline size_t " + stem + r"__next_candidate\(.*?\n\}\n", v1, re.S).group(0)
open(f"{out}/walk_a1.c", "w").write(finish(a1, form_fn(2, 64), one))
t3 = a1.replace(a1n, v1n + a1n.replace(f"{stem}__next_candidate(", f"{stem}__next_candidate__w32(", 1), 1)
call3 = f"({stem}__c.f == 1 ? {one} : {stem}__next_candidate__w32(&{stem}__c, {pos}))"
open(f"{out}/walk_v1_a1.c", "w").write(finish(t3, form_fn(3, 36), call3))
