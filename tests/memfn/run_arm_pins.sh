#!/usr/bin/env bash
# tests/memfn/run_arm_pins.sh — C5's per-arm pins ([MEMFN] R4c;
# docs/design/memfn/integration.md §17.4, §10.5): every scalar arm the kit
# carries renders a FIXED set of site descriptions (tests/memfn/arm_fixtures.c)
# to text whose sha256 is pinned in tests/memfn/pins/arms.tsv.
#
# WHAT IT IS: a CHANGE DETECTOR (§17.4 [rev4.2]), not a freeze. A kit change
# that moves an arm's text re-pins the arm's rows in its own commit, in the
# same change as its abi event (D94's grep finds this file). The fixtures'
# hooks are the driver's own stand-ins, so a pcrec scaffolding change moves no
# digest (F12).
#
# PROVENANCE OF THE PINS: recorded at R4c's IMPLEMENT commit, whose I1 shadow
# comparator (src/gen/memfn_sites.c) proved every kit rendering equal to
# pcrec's pre-migration text over every compile the corpus sweep made; the
# run-bearing rows re-pinned and the runcmp rows added at M1b's REPLACE (the
# kit's own run compare and helpers, I1-proved at M1b's IMPLEMENT).
#
# CHECKS (5, the libc record, is below the witness)
#   1. every fixture renders, through the arm its row names (the kit's form
#      id): a fixture that fell to another row would pin the wrong arm;
#   2. every part's sha256 equals its pin;
#   3. K35: the rows number at least ARMS_ROW_FLOOR, a literal that shares no
#      source with the TSV, and every arm in ARMS_EXPECTED has a row;
#   4. the WITNESS: the driver's --perturb (one byte of one fixture's
#      description) must move exactly that fixture's use part and nothing else,
#      so a pin that stopped seeing its text is red.
#   6. THE GATE ([MEMFN-ROWCON] N3): the driver's --gate cases, each against
#      the outcome GATE_EXPECT below names (written here, not in the driver):
#      DECLINED at define, so the named row renders it, or REFUSED with a text
#      that names the field in backquotes. They show the general gate covers
#      the ad hoc K96 tests N3 deleted from memfn/src/ofsskip.c (a floor or a
#      non-`n` miss, at define and at the call) and the rulings it makes real
#      (F1 non-identifier hooks, an unstated miss, K-1's fn_ref 0), plus (R4h
#      prep) the caller-owned counter's rules (its name REQUIRED, the fact
#      0/1 and ADVANCE-only) and the ADVANCE shape-class cases, which all
#      render through generic here (their classes are rows_check.py's check
#      E, read off an MF_TRACE build). K35: every expected case must appear,
#      and at least GATE_CASE_FLOOR of them.
#   7. THE COUNTER'S OWNER (R4h prep, MF_SITE_ABI 5): adv-kit-count's text
#      declares its counter, adv-caller-count's never does, and both advance
#      and cap it.
#   9. THE READS-BELOW FIND (M4 prep, R-7, MF_SITE_ABI 6): pf-memchr-back
#      (MLINE's row) and find-back-reaches-n (the generic row) are compiled
#      into one program and run on fixed subjects against a byte loop that
#      states the contract (first c in [lo, n] whose predecessor, at or above
#      lo, is the byte): Q-R7-1's candidate n (`"a\n"` from 0 is 2) and
#      Q-R7-2's lo == n (a miss, through a zero-length memchr). K35: the case
#      count is a literal and every case must run.
#   8. R4h'S FROZEN TARGET (lane advtarget, 2026-10-08): every file under
#      tests/memfn/pins/r4h_target/ is a 3-line header, the kit's text for
#      the same-named fixture byte for byte, then a `/* pcrec today:` block
#      to EOF. The middle must equal the fixture's freshly rendered .use
#      (and its .def be empty), so a kit move that the pins re-pinned still
#      reads red until the frozen target is re-frozen on purpose. K35: the
#      R4H_TARGETS shapes each have a file and the files number at least
#      R4H_TARGET_FLOOR. CONTROL: a copy of one target with one body byte
#      planted must compare unequal (a comparator that sees nothing is red).
#  10. M7'S FROZEN TARGET (M7 prep, R-8, RULED Q-R8-9): every file under
#      tests/memfn/pins/n7_target/ is the encoding seam's span-compare loop
#      cut from a pre-M7 build/pcrec artifact (exact, the UCP expression
#      fold, the ASCII in-place fold), checked as check 8 checks its own:
#      the body must equal the fixture's fresh .use, N7_TARGETS each have a
#      file, at least N7_TARGET_FLOOR files, and a planted byte reads red.
#  11. THE MISMATCH RUNS (M7 prep): the five mm-* fixtures' bodies, each in
#      a function with the residual entry's signature and return protocol
#      (-(k)-1 on a difference at k, reflen on equal), run over every
#      subject of length 0..4 on a 7-byte alphabet, every `at` in [0, n+1],
#      every separate reference of length 0..3 and every reference inside
#      the subject (aliasing), with NULL `s`/`ref` where their length is 0,
#      against `ref`, a byte loop written from memfn.h's MF_OP_MISMATCH. K35:
#      the call count must reach MM_CALL_FLOOR.
#  12. M6'S FROZEN TARGET (M6 prep, R-10, MF_SITE_ABI 8): every file under
#      tests/memfn/pins/m6_target/ is the VM cursor rung's STRIDED span loop
#      cut from a pre-M6 build/pcrec artifact (W = 2 possessive with and
#      without the caller's `it_`, the greedy arm's `lim_`, utf8's W = 3,
#      W = 32, range members), checked as check 8 checks its own: the body
#      must equal the fixture's fresh .use, M6_TARGETS each have a file, at
#      least M6_TARGET_FLOOR files, and a planted byte reads red.
#  13. THE STRIDED RUNS (M6 prep): three strided fixtures' bodies (W = 2
#      capped by the caller's `it_`, W = 2 bounded by `lim_`, and W = 3 with
#      the kit's OWN byte tests, s[cursor + i], Q-R10-4), each in a function
#      run over every subject of length 0..STRIDE_MAXLEN on a small alphabet,
#      every start, every `lim_` in [start, n], and a NULL subject at n = 0,
#      against `ref`, a loop written from memfn.h's strided ADVANCE: the
#      final cursor c0 + j*W and the counter j, where j is the least with
#      c0 + (j+1)*W > B, or j = the cap, or some position i failing its set.
#      K35: the call count must reach STRIDE_CALL_FLOOR.
# WHAT IT DOES NOT SEE: an arm no fixture reaches (each new arm adds its own
# fixtures and its id to ARMS_EXPECTED in the change that adds it), and a hook
# pcrec passes that differs from the driver's stand-in (I1 at a migration's
# IMPLEMENT and the identity gates are that check).
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="${LIB:-$ROOT_DIR/build/libpcrec.a}"
PINS="$ROOT_DIR/tests/memfn/pins/arms.tsv"
CC="${CC:-cc}"
ARMS_ROW_FLOOR=102
ARMS_EXPECTED="ofsskip precheck runcmp pf_memchr pf_walk mismatch_inplace"

pass=0; fail=0
ok()  { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }

T="$(mktemp -d "${TMPDIR:-/var/tmp}/armpins.XXXXXX")"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/out" "$T/perturbed"

if ! "$CC" -std=gnu11 -Wall -Wextra -Werror -I"$ROOT_DIR/memfn/include" \
        "$ROOT_DIR/tests/memfn/arm_fixtures.c" "$LIB" -o "$T/fx" 2>"$T/cc.err"; then
    cat "$T/cc.err"
    bad "the fixture driver does not build against $LIB"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
"$T/fx" "$T/out" > "$T/ids" || bad "the kit refused a fixture (see above)"
"$T/fx" "$T/perturbed" --perturb > /dev/null || bad "the kit refused the perturbed fixture"

# digest every part: <fixture>\t<part>\t<bytes>\t<sha256>
digest() {
    python3 - "$1" <<'EOF'
import hashlib, os, sys
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    b = open(os.path.join(d, f), 'rb').read()
    fx, part = f.rsplit('.', 1)
    print('%s\t%s\t%d\t%s' % (fx, part, len(b), hashlib.sha256(b).hexdigest()))
EOF
}
digest "$T/out" > "$T/now"
digest "$T/perturbed" > "$T/pert"

# 1 + 2: each pinned row against what rendered
rows=0
while IFS=$'\t' read -r arm fx part bytes sha; do
    case "$arm" in ''|'#'*) continue ;; esac
    rows=$((rows + 1))
    got_id="$(awk -F'\t' -v f="$fx" '$1 == f { print $2 }' "$T/ids")"
    if [ "$got_id" != "$arm" ]; then
        bad "$fx renders through '${got_id:-nothing}', its pin says '$arm'"
    else ok; fi
    now="$(awk -F'\t' -v f="$fx" -v p="$part" '$1 == f && $2 == p { print $3 "\t" $4 }' "$T/now")"
    if [ "$now" != "$bytes"$'\t'"$sha" ]; then
        bad "$arm/$fx.$part moved: pinned $bytes bytes $sha, now ${now:-absent}"
    else ok; fi
done < "$PINS"

# every rendered part has a pin
while IFS=$'\t' read -r fx part _ _; do
    grep -q "^[^#][^	]*	$fx	$part	" "$PINS" || bad "$fx.$part rendered with no pin"
done < "$T/now"

# 3: K35
if [ "$rows" -lt "$ARMS_ROW_FLOOR" ]; then
    bad "only $rows pinned rows, floor $ARMS_ROW_FLOOR"
else ok; fi
for a in $ARMS_EXPECTED; do
    if grep -q "^$a	" "$PINS"; then ok; else bad "arm $a has no pinned fixture"; fi
done

# 4: the witness
moved="$(diff "$T/now" "$T/pert" | awk '/^>/ { print $2 "." $3 }')"
if [ "$moved" = "pre-onebyte-rest.use" ]; then ok
else bad "the --perturb witness moved '${moved:-nothing}', expected exactly pre-onebyte-rest.use"; fi

# 5: the libc record (libcnote, kit F2). Each fixture's art must report in
# MEMFN_LIBC exactly the libc functions its rendered text calls, with no pcrec
# scan involved. The oracle is this scan of the .def + .use text (comments and
# literals out, `memcpy` of a literal 1-8 out: the record's one exclusion),
# which shares no code with the kit. Floors (K35, literals): at least one
# fixture must expect memchr and one memcmp, so an oracle that reads
# nothing is red.
LIBC_FLOOR_MEMCHR=1; LIBC_FLOOR_MEMCMP=1
python3 - "$T/out" "$T/ids" "$LIBC_FLOOR_MEMCHR" "$LIBC_FLOOR_MEMCMP" > "$T/libc.res" <<'EOF2'
import os, re, sys
d, ids, fmc, fcm = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
NAMES = r'(?:mem[a-z]+|str[a-z]+|bcmp|bzero|bcopy)'
def scan(text):
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
    text = re.sub(r'//[^\n]*', ' ', text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", "''", text)
    found = set()
    for m in re.finditer(r'(?<![\w.>])(' + NAMES + r')\s*\(([^;]*)', text):
        name, rest = m.group(1), m.group(2)
        if name == 'memcpy':
            args = re.match(r'[^,]*,[^,]*,\s*([0-9]+)[uUlL]*\s*\)', rest)
            if args and 1 <= int(args.group(1)) <= 8:
                continue
        found.add(name)
    return found
nchr = ncmp = bad = 0
for line in open(ids):
    fx, _, got = line.rstrip('\n').split('\t')
    text = ''
    for part in ('def', 'use'):
        text += open(os.path.join(d, fx + '.' + part)).read() + '\n'
    want = ','.join(sorted(scan(text))) or 'none'
    nchr += 'memchr' in want.split(',')
    ncmp += 'memcmp' in want.split(',')
    if want != got:
        bad += 1
        print('BAD %s: MEMFN_LIBC is "%s", the text calls "%s"' % (fx, got, want))
if nchr < fmc: bad += 1; print('BAD only %d fixtures expect memchr, floor %d' % (nchr, fmc))
if ncmp < fcm: bad += 1; print('BAD only %d fixtures expect memcmp, floor %d' % (ncmp, fcm))
print('OK' if not bad else 'RED')
EOF2
if grep -q '^BAD' "$T/libc.res"; then
    grep '^BAD' "$T/libc.res" | sed 's/^BAD/FAIL:/'; bad "the libc record disagrees with the rendered text"
else ok; fi

# 6: the gate (N3). <case> <RENDER form-id | REFUSE field>
GATE_CASE_FLOOR=74
GATE_EXPECT='ofs-call-floor REFUSE floor
ofs-call-miss-other REFUSE miss
ofs-call-miss-unstated REFUSE miss
ofs-define-miss-unstated RENDER generic
ofs-define-floor RENDER generic
ofs-define-miss-other RENDER generic
ofs-define-nonident RENDER generic
ofs-call-nonident REFUSE s
ofs-fn_ref-0 REFUSE fn_ref
allp-func-fn_ref-0 REFUSE fn_ref
allp-func-fn_ref-7 RENDER generic
pre-assign-miss-unstated REFUSE miss
pre-assign-miss-token RENDER precheck
pre-assign-miss-other RENDER generic
pre-onmiss-miss-other RENDER precheck
pre-use-floor REFUSE floor
pre-define-floor RENDER generic
pre-define-nonident RENDER generic
pre-use-nonident REFUSE s
run-nonident RENDER generic
adv-caller-count RENDER generic
adv-caller-count-unstated REFUSE count
adv-kit-count-unstated RENDER generic
adv-kit-count RENDER generic
adv-caller-count-2 REFUSE count_by_caller
adv-caller-count-not-advance REFUSE count_by_caller
adv-cls-fwd RENDER generic
adv-cls-view RENDER generic
adv-cls-rev RENDER generic
adv-cls-vm RENDER generic
adv-cls-edge2 RENDER generic
adv-cls-arrow RENDER generic
adv-cls-or RENDER generic
adv-cls-assign RENDER generic
adv-cls-shift RENDER generic
adv-cls-tern RENDER generic
adv-cls-call RENDER generic
adv-cls-comma RENDER generic
adv-cls-trail RENDER generic
back-at-n-break RENDER pf_memchr
back-at-n-break-spaced RENDER pf_memchr
back-at-n-return RENDER pf_memchr
back-excluded-generic RENDER generic
back-floor-not-lo-generic RENDER generic
back-table-generic RENDER generic
back-excluded-break-refused REFUSE on_miss
pf-memchr-break-refused REFUSE on_miss
adv-at-n-refused REFUSE empty
mm-exact RENDER generic
mm-expr RENDER generic
mm-inplace RENDER mismatch_inplace
mm-inplace-braced RENDER mismatch_inplace
mm-ucp-inplace RENDER mismatch_inplace
mm-expr-nonident RENDER generic
mm-loop-exit REFUSE on_miss
mm-none-fold REFUSE fold
mm-ascii-nofold REFUSE fold
mm-fold-noat REFUSE fold
mm-leaves-0 REFUSE on_miss_leaves
mm-reverse REFUSE reverse
mm-empty-miss REFUSE empty
mm-two-terms REFUSE pred
mm-ref-off1 REFUSE pred
mm-ref-unstated REFUSE ref
mm-fold-kind-find REFUSE fold_kind
stride-render RENDER generic
stride-w32 RENDER generic
stride-reverse REFUSE reverse
stride-gap REFUSE pred
stride-optional REFUSE pred
stride-run-term REFUSE pred
stride-not-advance REFUSE pred
stride-s-unstated REFUSE s
stride-cursor-unstated REFUSE cursor'
"$T/fx" --gate > "$T/gate" 2>"$T/gate.err" || bad "the driver's --gate mode failed (see $T/gate.err)"
ncase=0
while read -r name want arg; do
    [ -n "$name" ] || continue
    ncase=$((ncase + 1))
    line="$(awk -F'\t' -v c="$name" '$1 == c' "$T/gate")"
    got="$(printf '%s' "$line" | cut -f2)"
    txt="$(printf '%s' "$line" | cut -f3-)"
    if [ -z "$line" ]; then
        bad "gate case $name did not run"
    elif [ "$got" != "$want" ]; then
        bad "gate case $name: expected $want $arg, got $got: $txt"
    elif [ "$want" = RENDER ] && [ "$txt" != "$arg" ]; then
        bad "gate case $name: rendered through '$txt', expected '$arg'"
    elif [ "$want" = REFUSE ] && ! printf '%s' "$txt" | grep -qF "\`$arg\`"; then
        bad "gate case $name: the refusal does not name \`$arg\`: $txt"
    else ok; fi
done <<< "$GATE_EXPECT"
if [ "$ncase" -lt "$GATE_CASE_FLOOR" ]; then
    bad "only $ncase gate cases expected, floor $GATE_CASE_FLOOR"
else ok; fi
if [ "$(wc -l < "$T/gate" | tr -d ' ')" -ne "$ncase" ]; then
    bad "the driver ran $(wc -l < "$T/gate" | tr -d ' ') gate cases, $ncase are expected"
else ok; fi

# 7: the counter's owner (R4h prep, Q-R4h-1 (a), MF_SITE_ABI 5). The same
# counted ADVANCE site twice: owned by the kit, its text DECLARES the counter
# (`unsigned long scan_run_length = 1;`); owned by the caller, it never does,
# yet still advances and caps it. Read off the rendered text (not the pin):
# a kit that ignored count_by_caller reads red here whatever was pinned.
adv_use() { cat "$T/out/$1.use" 2>/dev/null; }
if adv_use adv-kit-count | grep -qF 'unsigned long scan_run_length = 1;'; then ok
else bad "adv-kit-count: the kit-owned counter is not declared"; fi
if adv_use adv-caller-count | grep -q 'unsigned long'; then
    bad "adv-caller-count: the caller-owned counter is declared by the kit"
else ok; fi
for want in 'scan_run_length++;' 'scan_run_length < 16ULL'; do
    for fx in adv-kit-count adv-caller-count; do
        if adv_use "$fx" | grep -qF "$want"; then ok
        else bad "$fx: no \`$want\` (the counter is not advanced or capped)"; fi
    done
done

# 8: R4h's frozen target (advtarget). tgt_cmp FILE USE: 0 iff FILE's body
# (after 3 header lines, before the `/* pcrec today:` line) equals USE's bytes.
R4H_DIR="$ROOT_DIR/tests/memfn/pins/r4h_target"
R4H_TARGET_FLOOR=8
R4H_TARGETS="adv-stay-fwd adv-stay-rev adv-stay-view adv-edge-unbounded adv-edge-counted-fwd adv-edge-counted-rev adv-vmspan-it adv-vmspan"
tgt_cmp() {
    python3 - "$1" "$2" <<'EOF3'
import sys
t = open(sys.argv[1], 'rb').read().split(b'\n')
u = open(sys.argv[2], 'rb').read()
cut = [i for i, l in enumerate(t) if l.startswith(b'/* pcrec today:')]
if len(t) < 4 or not cut or cut[0] < 4:
    sys.exit(2)
body = b'\n'.join(t[3:cut[0]]) + b'\n'
sys.exit(0 if body == u else 1)
EOF3
}
ntgt=0
for f in "$R4H_DIR"/*.c; do
    [ -e "$f" ] || continue
    ntgt=$((ntgt + 1))
    fx="$(basename "$f" .c)"
    if [ ! -f "$T/out/$fx.use" ]; then
        bad "r4h_target/$fx.c names no rendered fixture"
    elif [ -s "$T/out/$fx.def" ]; then
        bad "r4h_target/$fx: the fixture renders a def part (the target is the use only)"
    elif tgt_cmp "$f" "$T/out/$fx.use"; then ok
    else bad "r4h_target/$fx.c differs from the kit's render of $fx (re-freeze on purpose, or the kit moved)"; fi
done
for fx in $R4H_TARGETS; do
    if [ -f "$R4H_DIR/$fx.c" ]; then ok; else bad "R4h target shape $fx has no frozen file"; fi
done
if [ "$ntgt" -lt "$R4H_TARGET_FLOOR" ]; then
    bad "only $ntgt R4h target files, floor $R4H_TARGET_FLOOR"
else ok; fi
# the control: one planted body byte (line 4's first space becomes a tab)
if [ -f "$R4H_DIR/adv-edge-counted-fwd.c" ]; then
    awk 'NR == 4 { sub(/ /, "\t") } { print }' "$R4H_DIR/adv-edge-counted-fwd.c" > "$T/planted.c"
    if cmp -s "$T/planted.c" "$R4H_DIR/adv-edge-counted-fwd.c"; then
        bad "the r4h_target plant changed nothing"
    elif tgt_cmp "$T/planted.c" "$T/out/adv-edge-counted-fwd.use"; then
        bad "the r4h_target comparator accepted a planted byte"
    else ok; fi
fi

# 9: the reads-below FIND (M4 prep, R-7). The two fixtures' bodies inside
# two functions, each run on BACK_CASES subjects against `ref`, a plain loop
# written from memfn.h's MF_OP_FIND (Q-R7-1): the first c in [lo, n] with
# c - 1 >= lo and s[c - 1] == '\n'. The MLINE row's text ends in `break;`
# (LOOP_EXIT), so its body sits in pcrec's loop shape: a `for (;;)` that the
# break leaves. Every subject is non-NULL, which AT_N promises.
BACK_CASES=10
cat > "$T/back.c" <<'EOF4'
#include <stdio.h>
#include <string.h>
#define MISS ((size_t)-1)
static size_t ref(const unsigned char *s, size_t n, size_t lo)
{
    for (size_t c = lo + 1; c <= n; c++) if (s[c - 1] == '\n') return c;
    return MISS;
}
static size_t row(const unsigned char *subject, size_t subject_length, size_t start)
{
    for (;;) {
#include "out/pf-memchr-back.use"
        return start;
    }
    return MISS;
}
static size_t gen(const unsigned char *subject, size_t subject_length, size_t start)
{
    size_t hit;
#include "out/find-back-reaches-n.use"
    return hit;
}
int main(void)
{
    static const struct { const char *s; size_t lo, want; } k[] = {
        { "a\n", 0, 2 }, { "a\n", 1, 2 }, { "a\n", 2, MISS }, { "ab", 0, MISS },
        { "\n", 0, 1 }, { "a\nb\n", 2, 4 }, { "\n\n", 0, 1 }, { "\n\n", 1, 2 },
        { "", 0, MISS }, { "xyz\n", 3, 4 },
    };
    int bad = 0, ran = 0;
    for (size_t i = 0; i < sizeof k / sizeof k[0]; i++) {
        const unsigned char *s = (const unsigned char *)k[i].s;
        size_t n = strlen(k[i].s), r = ref(s, n, k[i].lo);
        size_t a = row(s, n, k[i].lo), b = gen(s, n, k[i].lo);
        ran++;
        if (r != k[i].want || a != r || b != r) {
            printf("BAD case %zu: want %zd ref %zd row %zd generic %zd\n", i,
                   (ssize_t)k[i].want, (ssize_t)r, (ssize_t)a, (ssize_t)b);
            bad++;
        }
    }
    printf("RAN %d\n", ran);
    return bad != 0;
}
EOF4
if "$CC" -std=gnu11 -Wall -Wextra -Werror -I"$T" "$T/back.c" -o "$T/back" 2>"$T/back.err"; then
    "$T/back" > "$T/back.out"; brc=$?
    grep '^BAD' "$T/back.out" | sed 's/^BAD/FAIL: reads-below FIND:/'
    if [ "$brc" -eq 0 ] && grep -qx "RAN $BACK_CASES" "$T/back.out"; then ok
    else bad "the reads-below FIND answered wrong or ran short ($(tail -1 "$T/back.out"))"; fi
else
    cat "$T/back.err"; bad "the reads-below FIND program does not build"
fi

# 10: M7's frozen target (M7 prep, R-8): tgt_cmp, as check 8.
N7_DIR="$ROOT_DIR/tests/memfn/pins/n7_target"
N7_TARGET_FLOOR=3
N7_TARGETS="mm-exact mm-ucp-expr mm-ascii-inplace"
n7tgt=0
for f in "$N7_DIR"/*.c; do
    [ -e "$f" ] || continue
    n7tgt=$((n7tgt + 1))
    fx="$(basename "$f" .c)"
    if [ ! -f "$T/out/$fx.use" ]; then
        bad "n7_target/$fx.c names no rendered fixture"
    elif [ -s "$T/out/$fx.def" ]; then
        bad "n7_target/$fx: the fixture renders a def part (the target is the use only)"
    elif tgt_cmp "$f" "$T/out/$fx.use"; then ok
    else bad "n7_target/$fx.c differs from the kit's render of $fx (re-freeze on purpose, or the kit moved)"; fi
done
for fx in $N7_TARGETS; do
    if [ -f "$N7_DIR/$fx.c" ]; then ok; else bad "M7 target shape $fx has no frozen file"; fi
done
if [ "$n7tgt" -lt "$N7_TARGET_FLOOR" ]; then
    bad "only $n7tgt M7 target files, floor $N7_TARGET_FLOOR"
else ok; fi
if [ -f "$N7_DIR/mm-ascii-inplace.c" ]; then
    awk 'NR == 4 { sub(/ /, "\t") } { print }' "$N7_DIR/mm-ascii-inplace.c" > "$T/planted7.c"
    if cmp -s "$T/planted7.c" "$N7_DIR/mm-ascii-inplace.c"; then
        bad "the n7_target plant changed nothing"
    elif tgt_cmp "$T/planted7.c" "$T/out/mm-ascii-inplace.use"; then
        bad "the n7_target comparator accepted a planted byte"
    else ok; fi
fi

# 11: the MISMATCH runs (M7 prep). Each fixture's loop in the residual
# entry's shape; `ref` below is the contract (memfn.h MF_OP_MISMATCH): k is
# the least j < reflen with at + j >= n or F(s[at + j]) != F(ref[j]). The
# folds are the fixtures' own hook texts' relations: none, `ucp_fold` (the
# UCP fixture's `rx_span_ci_fold`, a stand-in Latin-1-like map), ASCII, and
# `| 0x20`. The ASCII one is written here a second way (a table), so the
# oracle shares no text with the hook it checks.
MM_CALL_FLOOR=1000000
cat > "$T/mm.c" <<'EOF5'
#include <stddef.h>
#include <stdio.h>
static unsigned char rx_span_ci_fold(unsigned char c)
{
    return (c >= 0xC0 && c <= 0xDE && c != 0xD7) ? (unsigned char)(c + 32) : c;
}
static unsigned char f_none(unsigned char c) { return c; }
static unsigned char f_ucp(unsigned char c) { return rx_span_ci_fold(c); }
static unsigned char lower[256];
static unsigned char f_ascii(unsigned char c) { return lower[c]; }
static unsigned char f_or20(unsigned char c) { return (unsigned char)(c | 0x20); }
static ptrdiff_t m_exact(const unsigned char *s, size_t n, const unsigned char *ref,
                         size_t reflen, size_t at)
{
#include "out/mm-exact.use"
    return (ptrdiff_t)reflen;
}
static ptrdiff_t m_ucp(const unsigned char *s, size_t n, const unsigned char *ref,
                       size_t reflen, size_t at)
{
#include "out/mm-ucp-expr.use"
    return (ptrdiff_t)reflen;
}
static ptrdiff_t m_ascii(const unsigned char *s, size_t n, const unsigned char *ref,
                         size_t reflen, size_t at)
{
#include "out/mm-ascii-inplace.use"
    return (ptrdiff_t)reflen;
}
static ptrdiff_t m_nonid(const unsigned char *sp, size_t n, const unsigned char *ref,
                         size_t reflen, size_t at)
{
#include "out/mm-nonident.use"
    return (ptrdiff_t)reflen;
}
static ptrdiff_t m_clash(const unsigned char *s, size_t n, const unsigned char *y,
                         size_t reflen, size_t at)
{
#include "out/mm-inplace-clash.use"
    return (ptrdiff_t)reflen;
}
static ptrdiff_t ref(const unsigned char *s, size_t n, const unsigned char *r,
                     size_t reflen, size_t at, unsigned char (*f)(unsigned char))
{
    for (size_t j = 0; j < reflen; j++)
        if (at + j >= n || f(s[at + j]) != f(r[j])) return -(ptrdiff_t)j - 1;
    return (ptrdiff_t)reflen;
}
typedef ptrdiff_t (*mfn)(const unsigned char *, size_t, const unsigned char *, size_t, size_t);
static const struct { const char *name; mfn m; unsigned char (*f)(unsigned char); } fx[] = {
    { "mm-exact", m_exact, f_none }, { "mm-ucp-expr", m_ucp, f_ucp },
    { "mm-ascii-inplace", m_ascii, f_ascii }, { "mm-nonident", m_nonid, f_or20 },
    { "mm-inplace-clash", m_clash, f_ascii },
};
static const unsigned char A[7] = { 'a', 'A', 'b', 'B', 0xE9, 0xC9, 'z' };
static long calls, bad;
static void one(const unsigned char *s, size_t n, const unsigned char *r, size_t rl, size_t at)
{
    for (size_t k = 0; k < sizeof fx / sizeof fx[0]; k++) {
        ptrdiff_t got = fx[k].m(s, n, r, rl, at), want = ref(s, n, r, rl, at, fx[k].f);
        calls++;
        if (got != want && bad++ < 20)
            printf("BAD %s n=%zu rl=%zu at=%zu: got %td want %td\n", fx[k].name, n, rl, at, got, want);
    }
}
/* the ns-digit base-7 number `code` as bytes of A */
static void fill(unsigned char *b, size_t ns, long code)
{
    for (size_t i = 0; i < ns; i++) { b[i] = A[code % 7]; code /= 7; }
}
int main(void)
{
    for (int c = 0; c < 256; c++) lower[c] = (unsigned char)(c >= 'A' && c <= 'Z' ? c + 32 : c);
    unsigned char s[4], r[3];
    for (size_t n = 0; n <= 4; n++) {
        long ns = 1;
        for (size_t i = 0; i < n; i++) ns *= 7;
        for (long sc = 0; sc < ns; sc++) {
            fill(s, n, sc);
            const unsigned char *sp = n ? s : NULL;
            for (size_t at = 0; at <= n + 1; at++) {
                for (size_t rl = 0; rl <= 3; rl++) {
                    long nr = 1;
                    for (size_t i = 0; i < rl; i++) nr *= 7;
                    for (long rc = 0; rc < nr; rc++) {
                        fill(r, rl, rc);
                        one(sp, n, rl ? r : NULL, rl, at);
                    }
                }
                for (size_t j = 0; j <= n; j++)          /* the reference inside s */
                    for (size_t rl = 0; j + rl <= n; rl++)
                        one(sp, n, rl ? s + j : NULL, rl, at);
            }
        }
    }
    printf("CALLS %ld BAD %ld\n", calls, bad);
    return bad != 0;
}
EOF5
if "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$T" "$T/mm.c" -o "$T/mm" 2>"$T/mm.err"; then
    "$T/mm" > "$T/mm.out"; mrc=$?
    grep '^BAD ' "$T/mm.out" | sed 's/^BAD/FAIL: mismatch:/'
    mcalls="$(awk '/^CALLS/ { print $2 }' "$T/mm.out")"
    if [ "$mrc" -eq 0 ] && [ "${mcalls:-0}" -ge "$MM_CALL_FLOOR" ]; then ok
    else bad "the MISMATCH fixtures answered wrong or ran short ($(tail -1 "$T/mm.out"))"; fi
else
    cat "$T/mm.err"; bad "the MISMATCH program does not build"
fi

# 12: M6's frozen target (M6 prep, R-10): tgt_cmp, as check 8.
M6_DIR="$ROOT_DIR/tests/memfn/pins/m6_target"
M6_TARGET_FLOOR=6
M6_TARGETS="adv-vmstride-it adv-vmstride adv-vmstride-lim adv-vmstride-u8w3 adv-vmstride-w32 adv-vmstride-range"
m6tgt=0
for f in "$M6_DIR"/*.c; do
    [ -e "$f" ] || continue
    m6tgt=$((m6tgt + 1))
    fx="$(basename "$f" .c)"
    if [ ! -f "$T/out/$fx.use" ]; then
        bad "m6_target/$fx.c names no rendered fixture"
    elif [ -s "$T/out/$fx.def" ]; then
        bad "m6_target/$fx: the fixture renders a def part (the target is the use only)"
    elif tgt_cmp "$f" "$T/out/$fx.use"; then ok
    else bad "m6_target/$fx.c differs from the kit's render of $fx (re-freeze on purpose, or the kit moved)"; fi
done
for fx in $M6_TARGETS; do
    if [ -f "$M6_DIR/$fx.c" ]; then ok; else bad "M6 target shape $fx has no frozen file"; fi
done
if [ "$m6tgt" -lt "$M6_TARGET_FLOOR" ]; then
    bad "only $m6tgt M6 target files, floor $M6_TARGET_FLOOR"
else ok; fi
if [ -f "$M6_DIR/adv-vmstride-w32.c" ]; then
    awk 'NR == 4 { sub(/ /, "\t") } { print }' "$M6_DIR/adv-vmstride-w32.c" > "$T/planted6.c"
    if cmp -s "$T/planted6.c" "$M6_DIR/adv-vmstride-w32.c"; then
        bad "the m6_target plant changed nothing"
    elif tgt_cmp "$T/planted6.c" "$T/out/adv-vmstride-w32.use"; then
        bad "the m6_target comparator accepted a planted byte"
    else ok; fi
fi

# 13: the strided runs (M6 prep). Each body in the cursor rung's shape: the
# cursor starts at `start`, the caller's `it_` at 0. `ref` is the contract
# (memfn.h's strided ADVANCE), written from it and sharing no text with the
# fixtures: positions are compared against the pattern bytes directly.
STRIDE_MAXLEN=9
STRIDE_CALL_FLOOR=500000
cat > "$T/st.c" <<'EOF6'
#include <stddef.h>
#include <stdio.h>
static size_t f_it(const unsigned char *subject, size_t subject_length, size_t start,
                   unsigned long *cnt)
{
    size_t rx_span_cursor = start;
    unsigned long it_ = 0;
#include "out/adv-vmstride-it.use"
    *cnt = it_;
    return rx_span_cursor;
}
static size_t f_lim(const unsigned char *subject, size_t lim_, size_t start)
{
    size_t rx_span_cursor = start;
#include "out/adv-vmstride-lim.use"
    return rx_span_cursor;
}
static size_t f_own(const unsigned char *subject, size_t subject_length, size_t start,
                    unsigned long *cnt)
{
    size_t rx_span_cursor = start;
    unsigned long it_ = 0;
#include "out/adv-vmstride-own.use"
    *cnt = it_;
    return rx_span_cursor;
}
/* the contract: j iterations, each a W-byte block wholly below B whose every
   position holds, at most `cap` of them (cap < 0: none) */
static size_t ref(const unsigned char *s, size_t B, size_t c, size_t W,
                  const unsigned char *pat, long cap, unsigned long *cnt)
{
    unsigned long j = 0;
    for (;;) {
        if (c + W > B || (cap >= 0 && (long)j >= cap)) break;
        size_t i = 0;
        while (i < W && s[c + i] == pat[i]) i++;
        if (i < W) break;
        c += W;
        j++;
    }
    *cnt = j;
    return c;
}
static long calls, bad;
static void check(const char *who, size_t got, unsigned long gc, size_t want,
                  unsigned long wc, size_t n, size_t start)
{
    calls++;
    if ((got != want || gc != wc) && bad++ < 20)
        printf("BAD %s n=%zu start=%zu: cursor %zu count %lu, want %zu %lu\n",
               who, n, start, got, gc, want, wc);
}
static void sweep(const unsigned char *alpha, size_t na, int which)
{
    static const unsigned char AB[] = "ab", OWN[] = "x\xc3y";
    unsigned char s[16];
    for (size_t n = 0; n <= STRIDE_MAXLEN; n++) {
        long ns = 1;
        for (size_t i = 0; i < n; i++) ns *= (long)na;
        for (long code = 0; code < ns; code++) {
            long c = code;
            for (size_t i = 0; i < n; i++) { s[i] = alpha[c % (long)na]; c /= (long)na; }
            for (size_t st = 0; st <= n; st++) {
                unsigned long gc = 0, wc = 0;
                if (which == 0) {
                    size_t g = f_it(s, n, st, &gc), w = ref(s, n, st, 2, AB, 5, &wc);
                    check("adv-vmstride-it", g, gc, w, wc, n, st);
                    for (size_t B = st; B <= n; B++) {
                        g = f_lim(s, B, st); w = ref(s, B, st, 2, AB, -1, &wc);
                        check("adv-vmstride-lim", g, 0, w, 0, n, st);
                    }
                } else {
                    size_t g = f_own(s, n, st, &gc), w = ref(s, n, st, 3, OWN, 7, &wc);
                    check("adv-vmstride-own", g, gc, w, wc, n, st);
                }
            }
        }
    }
}
int main(void)
{
    static const unsigned char A0[] = { 'a', 'b', 'c' }, A1[] = { 'x', 0xc3, 'y', 'z' };
    unsigned long gc = 0;
    /* a NULL subject at n = 0: `more` is false at entry, nothing is read */
    check("adv-vmstride-it", f_it(NULL, 0, 0, &gc), gc, 0, 0, 0, 0);
    check("adv-vmstride-lim", f_lim(NULL, 0, 0), 0, 0, 0, 0, 0);
    check("adv-vmstride-own", f_own(NULL, 0, 0, &gc), gc, 0, 0, 0, 0);
    sweep(A0, sizeof A0, 0);
    sweep(A1, sizeof A1, 1);
    printf("CALLS %ld BAD %ld\n", calls, bad);
    return bad != 0;
}
EOF6
if "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -DSTRIDE_MAXLEN="$STRIDE_MAXLEN" -I"$T" \
        "$T/st.c" -o "$T/st" 2>"$T/st.err"; then
    "$T/st" > "$T/st.out"; src=$?
    grep '^BAD ' "$T/st.out" | sed 's/^BAD/FAIL: strided:/'
    scalls="$(awk '/^CALLS/ { print $2 }' "$T/st.out")"
    if [ "$src" -eq 0 ] && [ "${scalls:-0}" -ge "$STRIDE_CALL_FLOOR" ]; then ok
    else bad "the strided ADVANCE fixtures answered wrong or ran short ($(tail -1 "$T/st.out"))"; fi
else
    cat "$T/st.err"; bad "the strided ADVANCE program does not build"
fi

echo "arm pins: $rows rows over $(wc -l < "$T/ids" | tr -d ' ') fixtures; gate cases: $ncase; r4h targets: $ntgt; n7 targets: $n7tgt; m6 targets: $m6tgt; mismatch calls: ${mcalls:-0}; strided calls: ${scalls:-0}"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
