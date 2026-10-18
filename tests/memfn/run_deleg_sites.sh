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
#      the arena);
#   5. the one-byte fixtures (tests/memfn/c10_onebyte.tsv, R17-b' B2 [rev3
#      A8]): one per consumer KIND. A -DPCREC_CAND_TRACE build compiles each
#      with PCREC_MF_ROUTE_TRACE=1; its MFROUTED records must hold the
#      fixture's site with the fixture's kind and a finder row (routed; WHICH
#      row is the kit's choice, not matched: D157), and no other STATED
#      kind. UNSTATED records (EDGE, VMSPAN, N7 state no kind) are skipped by
#      name. The file's DISTINCT kind values must cover the five named in
#      C10_KINDS below. PRE's four kinds have no witness while PRE is
#      unrouted (its records carry no finder row); the PF/MLINE fixtures
#      witness the same kind values at the FIND sites. The expectations are
#      the fixture file, written from the design (r17b_prime.md §1.6/§4.3),
#      not from a recorded run.
#   6. [MEMFN] R17-b' B3a the `entry` column (r17b_prime.md rev 3 §3.4's
#      merge, Q-R17P-18), from a probe over the table: every row STATES its
#      DelegEntry (UNSTATED refused), DELEG_ENTRY_PRE only on a FIND row and
#      on at least one (K35), DELEG_ENTRY_SELF exactly on the ALL_PRESENT
#      row;
#   7. the PRESENCE fixtures (tests/memfn/c10_presence.tsv, Q-R17P-18):
#      through check 5's trace build, each fixture's MFPRES record holds
#      exactly the presence spans the file states (members, run length,
#      need, head_max) for its kind, and the file covers the four PRE kinds
#      (C10_PRES_KINDS below).
# CONTROLS: checks 1 and 4 run again over a planted copy (a row moved to the
# other budget; one by-value `mf_pred`) and must flag exactly those; check 5
# runs over two planted fixture files (a kind swapped; a kind dropped);
# check 6 over a planted table (a FIND row's entry SELF) and check 7 over a
# planted fixture file (a need swapped).
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
# VMSTRIDE ([MEMFN] M6): the VM cursor rung's strided span loop runs at every
# VM step that enters a cursor-rung repeat, as VMSPAN does: budget 2.
D91_LOOP="STAY EDGE VMSPAN VMSTRIDE VMRUN N7"
# C10's floor: the one-byte consumer kinds (R17-b' B2 [rev3 A8]) the fixture
# file must name, as distinct values. This file's literal, not a count of it.
C10_KINDS="DFA_SCAN DFA_HAT HYB_PF VM_ATTEMPT DFA_ATTEMPT"
# Check 7's floor: the PRE composite's four kinds (R17-b' B3a), a literal.
C10_PRES_KINDS="DFA_SCAN HYB_PF VM_ATTEMPT DFA_ATTEMPT"

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
#define DELEG_SITE(id, op, handoffs, kinds, budget, ceil, entry) \\
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

# 5: the one-byte fixtures, through a trace build of this tree
FIX="$ROOT_DIR/tests/memfn/c10_onebyte.tsv"
TRB="$T/trace"
c10_fix() {   # $1 = fixture file; prints one problem per line
    while IFS=$'\t' read -r fl pat site kind; do
        case "$fl" in '#'*|'') continue ;; esac
        set --
        [ "$fl" = - ] || set -- --features "$fl"
        PCREC_MF_ROUTE_TRACE=1 "$TRB/pcrec" "$@" -p rx -o "$T/f.c" --pattern "$pat" \
            > /dev/null 2> "$T/f.err" || { echo "$pat: does not compile"; continue; }
        grep '^MFROUTED' "$T/f.err" | awk -F'\t' -v pat="$pat" -v site="$site" -v kind="$kind" '
            $3 == "UNSTATED" { next }            # states no kind: neither witness nor spoiler
            $3 != kind { printf "%s: a record of another kind: %s/%s\n", pat, $2, $3; next }
            $2 == site && $4 != "-" { hit = 1 }
            END { if (!hit) printf "%s: no routed %s record of kind %s\n", pat, site, kind }'
    done < "$1"
}
c10_floor() { # $1 = fixture file; prints the named kinds it does not cover
    for k in $C10_KINDS; do
        awk -F'\t' -v k="$k" '$0 !~ /^#/ && $4 == k { n++ } END { exit !n }' "$1" || echo "$k"
    done
}
if "${TIMEOUT_BIN:-gnutimeout}" 900 make -s -C "$ROOT_DIR" -j4 BUILD_DIR="$TRB" \
        CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all > "$T/trace.log" 2>&1; then
    c10_fix "$FIX" > "$T/c10"
    if [ -s "$T/c10" ]; then while read -r l; do bad "C10 one-byte: $l"; done < "$T/c10"; else ok; fi
    miss="$(c10_floor "$FIX" | tr '\n' ' ')"
    if [ -z "$miss" ]; then ok; else bad "c10_onebyte.tsv names no fixture for kind(s): $miss"; fi
    # controls: a kind swapped (the fixture claims a kind the compile does not state) and a
    # kind dropped (the floor must name it); awk, not GNU sed, so the plant works on the Mac
    awk -F'\t' -v OFS='\t' '!d && $4 == "DFA_HAT" { $4 = "HYB_PF"; d = 1 } { print }' "$FIX" > "$T/swap.tsv"
    awk -F'\t' '$4 != "VM_ATTEMPT"' "$FIX" > "$T/drop.tsv"
    c10_fix "$T/swap.tsv" > "$T/c10swap"
    if ! cmp -s "$FIX" "$T/swap.tsv" && [ "$(wc -l < "$T/c10swap" | tr -d ' ')" -ge 1 ]; then ok
    else bad "C10 one-byte: the planted kind swap was not flagged"; fi
    if [ "$(c10_floor "$T/drop.tsv" | tr -d ' \n')" = VM_ATTEMPT ]; then ok
    else bad "C10 one-byte: the planted dropped kind was not flagged by the floor"; fi
    # 7: the presence fixtures (R17-b' B3a, Q-R17P-18)
    PFIX="$ROOT_DIR/tests/memfn/c10_presence.tsv"
    c10_pres() {   # $1 = fixture file; prints one problem per line
        while IFS=$'\t' read -r fl pat kind mem run need hm; do
            case "$fl" in '#'*|'') continue ;; esac
            set --
            [ "$fl" = - ] || set -- $fl
            PCREC_MF_ROUTE_TRACE=1 "$TRB/pcrec" --features all "$@" -p rx -o "$T/p.c" \
                --pattern "$pat" > /dev/null 2> "$T/p.err" || { echo "$pat: does not compile"; continue; }
            got="$(awk -F'\t' '$1 == "MFPRES" && $2 == "PRE" { print $3, $4, $5, $6, $7 }' "$T/p.err")"
            [ "$got" = "$kind $mem $run $need $hm" ] ||
                echo "$pat: stated presence [${got:-none}], the fixture states [$kind $mem $run $need $hm]"
        done < "$1"
    }
    c10_pres "$PFIX" > "$T/c10p"
    if [ -s "$T/c10p" ]; then while read -r l; do bad "C10 presence: $l"; done < "$T/c10p"; else ok; fi
    miss=""
    for k in $C10_PRES_KINDS; do
        awk -F'\t' -v k="$k" '$0 !~ /^#/ && $3 == k { n++ } END { exit !n }' "$PFIX" || miss="$miss $k"
    done
    if [ -z "$miss" ]; then ok; else bad "c10_presence.tsv names no fixture for kind(s):$miss"; fi
    awk -F'\t' -v OFS='\t' '!d && $6 == "REQUIRED" { $6 = "OPTIONAL"; d = 1 } { print }' "$PFIX" > "$T/pswap.tsv"
    c10_pres "$T/pswap.tsv" > "$T/c10pswap"
    if ! cmp -s "$PFIX" "$T/pswap.tsv" && [ "$(wc -l < "$T/c10pswap" | tr -d ' ')" -ge 1 ]; then ok
    else bad "C10 presence: the planted need swap was not flagged"; fi
else
    tail -5 "$T/trace.log"; bad "C10 one-byte: the trace build failed"
fi

# controls: one planted defect each, flagged exactly
mkdir -p "$T/src/gen"
sed 's/MF_TK_SET | MF_TK_RUN, DELEG_SCAN, MF_USE_DISCARD, DELEG_ENTRY_SELF)/MF_TK_SET | MF_TK_RUN, DELEG_LOOP, MF_USE_DISCARD, DELEG_ENTRY_SELF)/' "$DEF" > "$T/plant.def"
printf 'static void f(void)\n{\n    mf_pred p;\n    (void)p;\n}\n' > "$T/src/gen/plant.c"
static_checks "$T/plant.def" "$T/src" > "$T/plant" 2>/dev/null
if grep -q '^row PRE has budget DELEG_LOOP' "$T/plant" && grep -q '^gen/plant.c:3 declares mf_pred by value' "$T/plant" \
   && [ "$(wc -l < "$T/plant" | tr -d ' ')" -eq 2 ]; then ok
else bad "the planted controls were not flagged exactly: $(tr '\n' ';' < "$T/plant")"; fi

# 6: the entry column (R17-b' B3a), over the table and a planted copy
cat > "$T/entry.c" <<'EOF'
#include <stdio.h>
#include "memfn.h"
#define DELEG_H(h) (1u << (h))
#define DELEG_SCAN 0
#define DELEG_LOOP 1
enum { DELEG_ENTRY_UNSTATED = 0, DELEG_ENTRY_NONE, DELEG_ENTRY_SELF, DELEG_ENTRY_PRE };
int main(void) {
    int npre = 0;
#define DELEG_SITE(id, op, handoffs, kinds, budget, ceil, entry) \
    { int e = (entry); \
      if (e == DELEG_ENTRY_UNSTATED) printf("row %s states no entry\n", #id); \
      if (e == DELEG_ENTRY_PRE && (op) != MF_OP_FIND) printf("row %s: entry PRE on a non-FIND row\n", #id); \
      if (e == DELEG_ENTRY_PRE) npre++; \
      if ((e == DELEG_ENTRY_SELF) != ((op) == MF_OP_ALL_PRESENT)) \
          printf("row %s: entry SELF iff the ALL_PRESENT row\n", #id); }
#include DEFFILE
    if (!npre) printf("no FIND row takes the PRE verdict as its entry (K35)\n");
    return 0;
}
EOF
entry_check() {   # $1 = def file
    "$CC" -std=gnu11 -I"$ROOT_DIR/memfn/include" -DDEFFILE="\"$1\"" "$T/entry.c" -o "$T/entry" 2>"$T/entry.err" \
        || { echo "the entry probe does not build: $(head -2 "$T/entry.err" | tr '\n' ' ')"; return; }
    "$T/entry"
}
entry_check "$DEF" > "$T/e"
if [ -s "$T/e" ]; then while read -r l; do bad "C10 entry: $l"; done < "$T/e"; else ok; fi
sed '/^DELEG_SITE(PF,/,/)$/s/DELEG_ENTRY_PRE)/DELEG_ENTRY_SELF)/' "$DEF" > "$T/eplant.def"
entry_check "$T/eplant.def" > "$T/ep"
if grep -q '^row PF: entry SELF iff the ALL_PRESENT row' "$T/ep"; then ok
else bad "C10 entry: the planted entry was not flagged: $(tr '\n' ';' < "$T/ep")"; fi

echo "DELEG_SITES: ${nrows:-0} rows; vocabulary pairs probed: $(wc -l < "$T/vocab" 2>/dev/null | tr -d ' ')"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
