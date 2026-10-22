#!/usr/bin/env bash
# tests/memfn/run_wreply.sh — D172 S2's LEVER CHECK (docs/design/memfn/
# window_site.md rev 3.2 §2.4, §3.5, §5.1; lane wsc4, INVERTED at commit 5 by
# lane wsc5): the window family is the DEFAULT (build/pcrec's art previews
# the memfn kit's window family, and the DFA prefilter's NEXT rows read the
# family's PHASE-1 reply, emit_dfa.c `next_keys[]`); the INVERSE lever
# `--harness=window-legacy` (build/pcrec-harness) restores the old path, the
# planner's pick, so a mover can be localized by flipping back.
#
# THE BAR:
#   1. IDENTITY: build/pcrec (the reply) is byte-identical to the inverse
#      lever (the pick): the artifact, stderr and rc, over WITNESSES that
#      reach every NEXT key (each row below states the row the default must
#      stamp), at every flag set of FLAGSETS. The corpus-wide form is
#      emit_sweep against pre-S2 main for build/pcrec and, through `--sweep
#      REF`, for the inverse-lever binary (box lock, heavy).
#   2. REACH: identity alone cannot tell "NEXT reads the reply" from "NEXT
#      still reads the pick" (the two agree on every artifact, the shadow's
#      zero). So a COPY of the tree is built with the statement PERTURBED,
#      which moves the reply and never the pick (the old path does not read
#      the statement):
#        P-a  the RESEED alternative is not stated: by default no witness
#             may stamp an offset-set row (the reply cannot choose RESEED);
#             the inverse lever stamps them as the clean tree does;
#        P-b  R is stated under PCREC_NO_RUN_PREFILTER (V2 broken): under
#             `-fno-run-prefilter`, a PARKED + C-pin witness's reply sets
#             RE-SEED, its run-pinned rows are denied, NEXT reaches `memchr`,
#             and the default compile must be REFUSED loudly (§3.5); the
#             inverse lever compiles it.
#   --plant ID / --plants: the same run with one more planted defect in the
#   copy (the table below); the run must go red. Writes only its work dir.
#
# Controls: every witness row's stamp is checked (a witness that stopped
# reaching its key fails, [MECH-REACH]); K35 floors on cases and keys.
# Takes the box lock (scripts/boxlock) unless its caller holds it.
# Env: TMPDIR (the work dir's parent), JOBS (the copy's make -j, default 16).
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/timeout_bin.sh"
P="$ROOT/build/pcrec"
H="$ROOT/build/pcrec-harness"
LEVER="--harness=window-legacy"
JOBS="${JOBS:-16}"
# THE BOX LOCK (scripts/boxlock): ~160 compiles and a tree build per copy is
# over the sweep cap, so the run takes the lock unless its caller holds it
if ! bash "$ROOT/scripts/boxlock" held; then
    exec bash "$ROOT/scripts/boxlock" run --label wreply -- bash "${BASH_SOURCE[0]}" "$@"
fi
WORK="$(mktemp -d "${TMPDIR:-/tmp}/wreply.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
pass=0 fail=0
ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }
verdict() { echo "checks passed: $pass"; echo "checks failed: $fail"; [ "$fail" -eq 0 ]; exit $?; }

# THE WITNESSES: PATTERN|ROW, the row `<P>_DFA_PREFILTER` stamps at the
# default flags, on either path; the comment names the reply.
WITNESSES=(
    '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|offset-set'  # RESEED
    '\d{4}-\d{2}-\d{2}|offset-set'                                             # RESEED
    'in|instanceof|offset-set'                                                 # RESEED, R stated, no C-pin (class A)
    '\Bfoo\B|offset-set-bounded'                                               # RESEED, bounded
    '\b\.[0-9]{4}Z|offset-set-bounded'                                         # RESEED, k0 outside F0 (MISCOMPILE-1)
    'abc|run-pinned'                                                           # RESEED + C-pin
    '(?i)x/1234|run-pinned'                                                    # RESEED + C-pin, a cube in R
    'xy.*xy(?i:z)|run-pinned'                                                  # PARKED + C-pin
    '\babcd\b|run-pinned-bounded'                                              # RESEED + C-pin, bounded
    'foo\b|run-pinned-bounded'                                                 # PARKED + C-pin, bounded
    'a(b|c)+d|memchr'                                                          # PARKED
    '\bx|first-memchr-bounded'                                                 # PARKED (the DFA hat)
    'x[ab]cdefg|handoff'                                                       # PARKED (handoff re-entry)
)
FLAGSETS=("" "--engine=vm" "-fno-offset-skip" "-fno-run-prefilter" "-fmemfn-simd")
KEY_FLOORS="offset-set:3 offset-set-bounded:2 run-pinned:3 run-pinned-bounded:2"
CASE_FLOOR=65                   # 13 witnesses x 5 flag sets
# P-b's witness: a PARKED + C-pin artifact whose fall-back row does not re-seed
PB_PAT='xy.*xy(?i:z)'
PB_FLAGS="-fno-run-prefilter"
PB_MSG="sets RE-SEED"

# THE PERTURBATIONS (both in one copy; FILE@@FROM@@TO, FROM replaced once):
PERTS=(
    'src/gen/emit_dfa.c@@    bool reseed = wk && wk->nwalk >= 1 && us->cand.count >= 1@@    bool reseed = 0 && wk && wk->nwalk >= 1 && us->cand.count >= 1'
    'src/gen/emit_dfa.c@@!pcrec_opt_has(cx->opt, PCREC_NO_OFFSET_SKIP) &&\n        !pcrec_opt_has(cx->opt, PCREC_NO_RUN_PREFILTER)) {@@!pcrec_opt_has(cx->opt, PCREC_NO_OFFSET_SKIP)) {'
)
# THE PLANTS (pcrec-side ids from S1412, the kit manager's wsc4 brief):
plant_spec() {
    case "$1" in
        # a NEXT row reading the planner's pick where the family answered
        S1412) echo 'src/gen/emit_dfa.c@@    if (!u->wr_stated) return next_keys[k].pick(s);@@    return next_keys[k].pick(s);' ;;
        # the RE-SEED bit ignored where it reaches a row that does not re-seed
        S1413) echo 'src/gen/emit_dfa.c@@        if (us->wr_stated && us->wr.reseed && !f->pf->u.pf.reseeds)@@        if (us->wr_stated && 0 && !f->pf->u.pf.reseeds)' ;;
        # the run-pinned key not reading C-pin (a RESEED reply without it takes the run rows)
        S1414) echo 'src/gen/emit_dfa.c@@nk_pick_run_pinned, WR_ANY, 1, 1,@@nk_pick_run_pinned, WR_ANY, 1, WR_ANY,' ;;
        *) return 1 ;;
    esac
}
PLANTS="S1412 S1413 S1414"

# Applies FILE@@FROM@@TO specs ("\n" a newline) to tree copy $1.
apply() {
    local dir=$1; shift
    local spec
    for spec in "$@"; do
        python3 -I - "$dir" "$spec" <<'EOF' || return 1
import sys
d, spec = sys.argv[1], sys.argv[2]
f, a, b = spec.split("@@")
a, b = a.replace("\\n", "\n"), b.replace("\\n", "\n")
p = d + "/" + f
s = open(p).read()
if s.count(a) != 1:
    sys.exit("%s: the text is found %d times" % (f, s.count(a)))
open(p, "w").write(s.replace(a, b))
EOF
    done
}

# A copy of the tree's tracked files as they stand, with specs applied, built:
# $1 the copy's name, the rest its specs. Echoes the copy's build dir.
build_copy() {
    local name=$1; shift
    local dir="$WORK/$name"
    mkdir -p "$dir"
    (cd "$ROOT" && git ls-files -z | tar --null --ignore-failed-read -T - -cf -) |
        tar -xf - -C "$dir" || return 1
    apply "$dir" "$@" || return 1
    "$TIMEOUT_BIN" 900 make -C "$dir" -j"$JOBS" build/pcrec build/pcrec-harness \
        >"$WORK/$name.build.log" 2>&1 || { tail -5 "$WORK/$name.build.log"; return 1; }
    echo "$dir/build"
}

# One compile: binary $1, extra args $2, flags $3, pattern $4, into dir $5
# (o.c, err, rc). The output name is the same on every side (the -o trap).
comp() {
    mkdir -p "$5"
    # shellcheck disable=SC2086
    "$TIMEOUT_BIN" 60 "$1" $2 -p rx --features all $3 -o "$5/o.c" --pattern "$4" >"$5/out" 2>"$5/err"
    echo $? >"$5/rc"
}
stamp() { sed -n 's/^#define RX_DFA_PREFILTER "\(.*\)"$/\1/p' "$1/o.c" 2>/dev/null; }

# --- 1. identity over the witnesses, and each witness's key ----------------
identity() {   # $1 the default binary (the reply), $2 the harness binary (the lever: the pick), $3 label
    local n=0 w pat row f k
    declare -A seen=()
    for w in "${WITNESSES[@]}"; do
        pat="${w%|*}" row="${w##*|}"
        for f in "${FLAGSETS[@]}"; do
            n=$((n + 1))
            comp "$1" "" "$f" "$pat" "$WORK/$3/a"
            comp "$2" "$LEVER" "$f" "$pat" "$WORK/$3/b"
            if cmp -s "$WORK/$3/a/o.c" "$WORK/$3/b/o.c" && cmp -s "$WORK/$3/a/err" "$WORK/$3/b/err" &&
               cmp -s "$WORK/$3/a/rc" "$WORK/$3/b/rc"; then ok
            else bad "$3 identity: '$pat' [$f] differs across the lever (rc $(cat "$WORK/$3/a/rc")/$(cat "$WORK/$3/b/rc"))"; fi
            [ -z "$f" ] || continue
            if [ "$(stamp "$WORK/$3/a")" = "$row" ]; then ok; seen[$row]=$(( ${seen[$row]:-0} + 1 ))
            else bad "$3 reach: '$pat' stamps '$(stamp "$WORK/$3/a")' by default, its row is '$row'"; fi
        done
    done
    [ "$n" -ge "$CASE_FLOOR" ] && ok || bad "$3: $n cases ran, floor $CASE_FLOOR"
    for kf in $KEY_FLOORS; do
        k="${kf%:*}"
        [ "${seen[$k]:-0}" -ge "${kf##*:}" ] && ok || bad "$3: key row $k reached by ${seen[$k]:-0} witnesses, floor ${kf##*:}"
    done
    echo "$3: $n identity cases over ${#WITNESSES[@]} witnesses"
}

# --- 2. reach: the perturbed statement moves the reply, never the pick -------
reach() {   # $1 the perturbed copy's build dir, $2 label
    local w pat row off on moved=0
    for w in "${WITNESSES[@]}"; do
        pat="${w%|*}" row="${w##*|}"
        comp "$1/pcrec-harness" "$LEVER" "" "$pat" "$WORK/$2/off"
        comp "$1/pcrec" "" "" "$pat" "$WORK/$2/on"
        off="$(stamp "$WORK/$2/off")" on="$(stamp "$WORK/$2/on")"
        [ "$off" = "$row" ] && ok || bad "$2 P-a control: '$pat' stamps '$off' under the inverse lever, its row is '$row'"
        [ "$(cat "$WORK/$2/on/rc")" = 0 ] && ok || bad "$2 P-a: '$pat' refused by default: $(head -1 "$WORK/$2/on/err")"
        case "$on" in
            offset-set*) bad "$2 P-a: '$pat' stamps '$on' by default with no RESEED alternative stated (NEXT read the pick)" ;;
            *) ok ;;
        esac
        case "$row" in offset-set*) [ "$on" != "$row" ] && moved=$((moved + 1)) ;; esac
    done
    [ "$moved" -ge 5 ] && ok || bad "$2 P-a: $moved offset-set witnesses moved, floor 5"
    comp "$1/pcrec-harness" "$LEVER" "$PB_FLAGS" "$PB_PAT" "$WORK/$2/pboff"
    comp "$1/pcrec" "" "$PB_FLAGS" "$PB_PAT" "$WORK/$2/pbon"
    [ "$(cat "$WORK/$2/pboff/rc")" = 0 ] && ok || bad "$2 P-b control: '$PB_PAT' [$PB_FLAGS] refused under the inverse lever"
    if [ "$(cat "$WORK/$2/pbon/rc")" != 0 ] && grep -q "$PB_MSG" "$WORK/$2/pbon/err"; then ok
    else bad "$2 P-b: '$PB_PAT' [$PB_FLAGS] by default was not refused for RE-SEED (rc $(cat "$WORK/$2/pbon/rc"), stamp '$(stamp "$WORK/$2/pbon")')"; fi
    echo "$2: P-a moved $moved offset-set witnesses off the offset rows; P-b refused"
}

for b in "$P" "$H"; do
    [ -x "$b" ] || { echo "FAIL: $b not built (make first)"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
done

if [ "${1:-}" = "--sweep" ]; then
    # the corpus-wide identity of the OLD path: emit_sweep with the inverse
    # lever's binary as the working side (a wrapper: emit_sweep's --extra
    # reaches both sides); build/pcrec's own sweep is plain emit_sweep;
    # the rest of the arguments are emit_sweep's (--ref REV or --ref-bin B, ...)
    shift
    wrap="$WORK/pcrec-wreply"
    printf '#!/bin/sh\nexec "%s" %s "$@"\n' "$H" "$LEVER" >"$wrap"
    chmod +x "$wrap"
    python3 -I "$ROOT/scripts/emit_sweep.py" --bin "$wrap" --tree "$ROOT" "$@"
    exit $?
fi

if [ "${1:-}" = "--plant" ] || [ "${1:-}" = "--plants" ]; then
    ids="${2:-}"
    [ "$1" = "--plants" ] && ids="$PLANTS"
    [ -n "$ids" ] || { echo "FAIL: --plant needs an id ($PLANTS)"; exit 2; }
    red=0
    for id in $ids; do
        spec="$(plant_spec "$id")" || { echo "FAIL: no plant $id"; exit 2; }
        before=$fail
        if [ "$id" = S1414 ]; then      # caught by identity alone
            bd="$(build_copy "plant_$id" "$spec")" || { echo "FAIL: $id: the planted copy does not build"; exit 2; }
            identity "$bd/pcrec" "$bd/pcrec-harness" "plant_$id" >"$WORK/plant_$id.log" 2>&1
        else
            bd="$(build_copy "plant_$id" "${PERTS[@]}" "$spec")" || { echo "FAIL: $id: the planted copy does not build"; exit 2; }
            fail=0; pass=0
            reach "$bd" "plant_$id" >"$WORK/plant_$id.log" 2>&1
        fi
        first="$(grep -m1 '^FAIL' "$WORK/plant_$id.log")"
        if [ -n "$first" ]; then red=$((red + 1)); echo "PLANT $id: RED ($first)"
        else echo "PLANT $id: GREEN (not caught)"; fi
        fail=$before
    done
    n=$(echo $ids | wc -w)
    echo "plants: $red of $n red"
    [ "$red" -eq "$n" ]
    exit $?
fi

identity "$P" "$H" clean
bd="$(build_copy perturbed "${PERTS[@]}")" || { bad "the perturbed copy does not build"; verdict; }
reach "$bd" perturbed
verdict
