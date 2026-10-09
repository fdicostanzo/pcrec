#!/usr/bin/env bash
# tests/memfn/run_deleg_sites.sh — C10, the delegation table and the stack
# ([MEMFN] R4c; docs/design/memfn/integration.md §10.5, §8.5, §14.5).
#
# STATIC HALF (this file; the per-instance half is pcrec's own, at compile
# time: `pcrec_memfn_check_use` and `deleg_check` in src/gen/memfn_sites.c):
#   1. every DELEG_SITES row (src/gen/memfn_sites.def) names a site D91
#      classifies, at D91's budget. The classification is THIS FILE's literal
#      (D91_SCAN / D91_LOOP below), sharing no source with the table;
#   2. every (op, handoff, kinds) a row allows is in the kit's vocabulary
#      (mf_vocab_has, asked by a probe linked against build/libpcrec.a);
#   3. MF_P_INLOOP is spelled in CODE under src/ only in src/gen/memfn_sites.c, the
#      file that derives it from a row's budget column;
#   4. no `mf_site`, `mf_pred` or `mf_result` is declared by VALUE under src/
#      (r2 K3: a site can carry 255 predicates, about 170 KB; they live in
#      the arena).
# CONTROLS: checks 1 and 4 run again over a planted copy (a row moved to the
# other budget; one by-value `mf_pred`) and must flag exactly those.
# WHAT IT DOES NOT SEE: a by-value declaration through a typedef of its own
# or a macro, and a row whose op is right but whose site emits through a
# different op (pcrec's `deleg_check` refuses that at compile time).
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="${LIB:-$ROOT_DIR/build/libpcrec.a}"
CC="${CC:-cc}"
DEF="$ROOT_DIR/src/gen/memfn_sites.def"
D91_SCAN="PF PRE OFS SETREST VERIFY MLINE"
# N7 ([MEMFN] M7, RULED Q-R8-10): the encoding seam's span compare runs at
# every VM backreference / variable step, so it is D91's budget 2.
D91_LOOP="STAY EDGE VMSPAN VMRUN N7"

pass=0; fail=0
ok()  { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }

T="$(mktemp -d "${TMPDIR:-/var/tmp}/deleg.XXXXXX")"
trap 'rm -rf "$T"' EXIT

# Prints one problem per line for checks 1 and 4 over (def file, src dir).
static_checks() {
    python3 - "$1" "$2" "$D91_SCAN" "$D91_LOOP" <<'EOF'
import os, re, sys
deff, srcdir, scan, loop = sys.argv[1], sys.argv[2], sys.argv[3].split(), sys.argv[4].split()
text = re.sub(r'/\*.*?\*/', '', open(deff).read(), flags=re.S)
rows = re.findall(r'DELEG_SITE\(\s*(\w+)\s*,(.*?)\)\s*$', text, flags=re.M | re.S)
rows = [(i, [a.strip() for a in re.split(r',(?![^(]*\))', body)]) for i, body in rows]
print('ROWS %d' % len(rows), file=sys.stderr)
for rid, args in rows:
    budget = args[3] if len(args) > 3 else '?'
    want = 'DELEG_SCAN' if rid in scan else 'DELEG_LOOP' if rid in loop else None
    if want is None:
        print('row %s names no site D91 classifies' % rid)
    elif budget != want:
        print('row %s has budget %s, D91 says %s' % (rid, budget, want))
decl = re.compile(r'\b(mf_site|mf_pred|mf_result)\s+(?!\*)[A-Za-z_]\w*\s*(\[|=|;|,)')
for dp, _, fs in os.walk(srcdir):
    for f in fs:
        if not f.endswith(('.c', '.h')): continue
        p = os.path.join(dp, f)
        body = re.sub(r'/\*.*?\*/', '', open(p, errors='replace').read(), flags=re.S)
        for n, line in enumerate(body.split('\n'), 1):
            if decl.search(line):
                print('%s:%d declares %s by value' % (os.path.relpath(p, srcdir), n, decl.search(line).group(1)))
EOF
}

# 1 + 4 on the tree
static_checks "$DEF" "$ROOT_DIR/src" > "$T/real" 2> "$T/real.rows"
nrows="$(awk '{ print $2 }' "$T/real.rows")"
if [ -s "$T/real" ]; then while read -r l; do bad "$l"; done < "$T/real"; else ok; fi
if [ "${nrows:-0}" -ge 1 ]; then ok; else bad "DELEG_SITES has no row (K35)"; fi

# 2: the vocabulary, per allowed handoff
cat > "$T/probe.c" <<EOF
#include <stdio.h>
#include "memfn.h"
#define DELEG_H(h) (1u << (h))
#define DELEG_SCAN 0
#define DELEG_LOOP 1
int main(void) {
    int bad = 0;
#define DELEG_SITE(id, op, handoffs, kinds, budget, ceil) \\
    for (unsigned h = 0; h < 32; h++) \\
        if (((handoffs) >> h) & 1u) { \\
            int has = mf_vocab_has(op, (mf_handoff)h, kinds); \\
            printf("%s %u %d\n", #id, h, has); bad |= !has; }
#include "$DEF"
    return bad;
}
EOF
if "$CC" -std=gnu11 -I"$ROOT_DIR/memfn/include" "$T/probe.c" "$LIB" -o "$T/probe" 2>"$T/cc.err"; then
    "$T/probe" > "$T/vocab"
    n="$(wc -l < "$T/vocab" | tr -d ' ')"
    if awk '$3 != 1 { exit 1 }' "$T/vocab" && [ "$n" -ge 1 ]; then ok
    else bad "a DELEG_SITES (op, handoff, kinds) the vocabulary lacks: $(awk '$3 != 1' "$T/vocab" | tr '\n' ';')"; fi
else
    cat "$T/cc.err"; bad "the vocabulary probe does not build"
fi

# 3: MF_P_INLOOP's one home (code, not comments)
others="$(python3 - "$ROOT_DIR/src" <<'EOF'
import os, re, sys
for dp, _, fs in os.walk(sys.argv[1]):
    for f in fs:
        p = os.path.join(dp, f)
        if not f.endswith(('.c', '.h', '.def')) or p.endswith('src/gen/memfn_sites.c'): continue
        if 'MF_P_INLOOP' in re.sub(r'/\*.*?\*/', '', open(p, errors='replace').read(), flags=re.S):
            print(os.path.relpath(p, sys.argv[1]))
EOF
)"
if [ -z "$others" ]; then ok; else bad "MF_P_INLOOP spelled outside memfn_sites.c: $others"; fi

# controls: one planted defect each, flagged exactly
mkdir -p "$T/src/gen"
sed 's/MF_TK_SET | MF_TK_RUN, DELEG_SCAN, MF_USE_DISCARD)/MF_TK_SET | MF_TK_RUN, DELEG_LOOP, MF_USE_DISCARD)/' "$DEF" > "$T/plant.def"
printf 'static void f(void)\n{\n    mf_pred p;\n    (void)p;\n}\n' > "$T/src/gen/plant.c"
static_checks "$T/plant.def" "$T/src" > "$T/plant" 2>/dev/null
if grep -q '^row PRE has budget DELEG_LOOP' "$T/plant" && grep -q '^gen/plant.c:3 declares mf_pred by value' "$T/plant" \
   && [ "$(wc -l < "$T/plant" | tr -d ' ')" -eq 2 ]; then ok
else bad "the planted controls were not flagged exactly: $(tr '\n' ';' < "$T/plant")"; fi

echo "DELEG_SITES: ${nrows:-0} rows; vocabulary pairs probed: $(wc -l < "$T/vocab" 2>/dev/null | tr -d ' ')"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
