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
#   8. R4h'S FROZEN TARGET (lane advtarget, 2026-10-08): every file under
#      tests/memfn/pins/r4h_target/ is a 3-line header, the kit's text for
#      the same-named fixture byte for byte, then a `/* pcrec today:` block
#      to EOF. The middle must equal the fixture's freshly rendered .use
#      (and its .def be empty), so a kit move that the pins re-pinned still
#      reads red until the frozen target is re-frozen on purpose. K35: the
#      R4H_TARGETS shapes each have a file and the files number at least
#      R4H_TARGET_FLOOR. CONTROL: a copy of one target with one body byte
#      planted must compare unequal (a comparator that sees nothing is red).
# WHAT IT DOES NOT SEE: an arm no fixture reaches (each new arm adds its own
# fixtures and its id to ARMS_EXPECTED in the change that adds it), and a hook
# pcrec passes that differs from the driver's stand-in (I1 at a migration's
# IMPLEMENT and the identity gates are that check).
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="${LIB:-$ROOT_DIR/build/libpcrec.a}"
PINS="$ROOT_DIR/tests/memfn/pins/arms.tsv"
CC="${CC:-cc}"
ARMS_ROW_FLOOR=74
ARMS_EXPECTED="ofsskip precheck runcmp pf_memchr pf_walk"

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
GATE_CASE_FLOOR=39
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
adv-cls-trail RENDER generic'
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

echo "arm pins: $rows rows over $(wc -l < "$T/ids" | tr -d ' ') fixtures; gate cases: $ncase; r4h targets: $ntgt"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
