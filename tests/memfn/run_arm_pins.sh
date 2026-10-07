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
# CHECKS
#   1. every fixture renders, through the arm its row names (the kit's form
#      id): a fixture that fell to another row would pin the wrong arm;
#   2. every part's sha256 equals its pin;
#   3. K35: the rows number at least ARMS_ROW_FLOOR, a literal that shares no
#      source with the TSV, and every arm in ARMS_EXPECTED has a row;
#   4. the WITNESS: the driver's --perturb (one byte of one fixture's
#      description) must move exactly that fixture's use part and nothing else,
#      so a pin that stopped seeing its text is red.
# WHAT IT DOES NOT SEE: an arm no fixture reaches (each new arm adds its own
# fixtures and its id to ARMS_EXPECTED in the change that adds it), and a hook
# pcrec passes that differs from the driver's stand-in (I1 at a migration's
# IMPLEMENT and the identity gates are that check).
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="${LIB:-$ROOT_DIR/build/libpcrec.a}"
PINS="$ROOT_DIR/tests/memfn/pins/arms.tsv"
CC="${CC:-cc}"
ARMS_ROW_FLOOR=28
ARMS_EXPECTED="ofsskip precheck runcmp"

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

echo "arm pins: $rows rows over $(wc -l < "$T/ids" | tr -d ' ') fixtures"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
