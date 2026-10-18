#!/usr/bin/env bash
# tests/knowledge/run_knowledge_tests.sh — [KNOW-SRC] K3: ROUND-TRIP IDENTITY
# for the ANALYSIS kind (docs/design/measure_sets.md rev 3 §9.6, §9.7 K3),
# over the three shipped bundles and the fixtures:
#
#   R1 load->list->load   the ITEM digest (`rows_digest`, the decoded view's
#                         `item` section) of the canonical view, re-loaded,
#                         equals the original's;
#   R2 list->load->list   the canonical view of the re-loaded canonical view
#                         is the first canonical view, byte for byte;
#   R3 structural         `pcrec-analyze --dump-doc` (analyze/, the
#                         zero-dependency TWIN: it shares no code with pcrec's
#                         reader or writer) reads the canonical file and the
#                         original file into the SAME document — the check
#                         that sees a section the digest does not cover
#                         dropped CONSISTENTLY (S961, S984);
#   R5 decoded = indep.   pcrec's `--view=decoded` of the original file equals
#                         `--dump-doc`'s decode of that FILE, field by field
#                         (a reader and writer wrong SYMMETRICALLY), and every
#                         `resolution` digest the named bundle answers itself
#                         equals `tests/findings/findings_ref.py
#                         bundle-digest` on the same file (the existing
#                         independent digest, named here as a gate).
#   (R4 committed = canonical is EXEMPT for this kind: the row's `r4` column,
#   until §9.9 decides the format.)
#
# Plus the loader's refusal of a DERIVED view fed back as an input (§9.6,
# S962): the shipped NAME listing and the decoded view, each written as an
# `-I` file, refuse naming the section and pointing at `--view=canonical`;
# and no canonical view carries a `#section` line at all.
#
# POPULATION (K35: each set has a floor, and a set that must load in full
# says so): src/findings/*.rxt (3, all); kfixtures.py's three (all);
# tests/findings/adversarial/ (all); tests/findings/witness/ (all); the
# resolution fixtures' A and B dirs (res_fixtures.py; a bundle that refuses
# by design — a cycle, a long chain, a two-bundle file — is out, and the
# count that loads has a floor). A round-tripped item is re-loaded with its
# canonical directory FIRST and its own directory after it, so an `include`
# still resolves.
#
# CONTROLS (each must FAIL its compare, or the compare could not fail): R3 on
# a canonical file with its `description` deleted; R3 on one whose two-
# encoding `serves` list lost an encoding (R1's digest unmoved by the same
# edit); R5 on a decode with two rows swapped.
#
# Verdict: `checks failed: 0`; under make, no `*** [test-knowledge] Error`.
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
ANALYZE="${ANALYZE:-${PCREC%/*}/pcrec-analyze}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
REF="python3 $ROOT_DIR/tests/findings/findings_ref.py"

if [ ! -x "$ANALYZE" ]; then
    bad "no pcrec-analyze at $ANALYZE (make builds it beside pcrec)"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# The `decoded` section of a pcrec decoded view (stdin): its `#section
# decoded` line up to the next section — the shape --dump-doc prints whole.
dec_section() { awk '/^#section /{s = ($2 == "decoded")} s'; }
# The ITEM digest a decoded view (file) carries.
item_digest() { awk -F'\t' '/^#section /{split($0, w, " "); s = (w[2] == "item")} s && $1 == "rows" {print $2}' "$1"; }

python3 "$SCRIPT_DIR/kfixtures.py" "$WORKDIR/kf"
python3 "$ROOT_DIR/tests/findings/res_fixtures.py" "$WORKDIR/res" >/dev/null

# set name | directory | must every file load (1) or a floor of loads
SETS=(
    "shipped|$ROOT_DIR/src/findings|all|3"
    "kfixtures|$WORKDIR/kf|all|3"
    "adversarial|$ROOT_DIR/tests/findings/adversarial|all|11"
    "witness|$ROOT_DIR/tests/findings/witness|all|5"
    "res-A|$WORKDIR/res/A|floor|15"
    "res-B|$WORKDIR/res/B|floor|3"
)

n_items=0
for row in "${SETS[@]}"; do
    IFS='|' read -r set dir policy floor <<< "$row"
    loaded=0; files=0
    for f in "$dir"/*.rxt; do
        [ -e "$f" ] || continue
        name="$(basename "$f" .rxt)"
        case "$name" in [a-z]*) ;; *) continue ;; esac
        printf '%s' "$name" | grep -qE '^[a-z][a-z0-9_-]*$' || continue
        files=$((files + 1))
        t="$WORKDIR/it/$set/$name"; y="$t/y"; mkdir -p "$y"
        if ! pcrec_run "$PCREC" -I "$dir" --list-analysis "$name" --view=decoded \
                > "$t/dec0" 2>"$t/err"; then
            [ "$policy" = all ] && bad "$set/$name: --view=decoded refused: $(head -c 200 "$t/err")"
            continue
        fi
        loaded=$((loaded + 1)); n_items=$((n_items + 1))
        id="$set/$name"
        pcrec_run "$PCREC" -I "$dir" --list-analysis "$name" --view=canonical \
            > "$y/$name.rxt" 2>"$t/err" || { bad "$id: --view=canonical refused: $(head -c 200 "$t/err")"; continue; }
        if grep -q '^#section' "$y/$name.rxt"; then
            bad "$id: the canonical view carries a '#section' line (a derived section written into an input)"
        fi
        if ! pcrec_run "$PCREC" -I "$y" -I "$dir" --list-analysis "$name" --view=decoded \
                > "$t/dec1" 2>"$t/err"; then
            bad "$id R1: the canonical view does not load: $(head -c 200 "$t/err")"
            continue
        fi
        # R1
        d0="$(item_digest "$t/dec0")"; d1="$(item_digest "$t/dec1")"
        if [ -n "$d0" ] && [ "$d0" = "$d1" ]; then
            ok "$id R1 load->list->load keeps the item digest ($d0)"
        else
            bad "$id R1 item digest '$d0' -> '$d1' across a round trip"
        fi
        # R2
        pcrec_run "$PCREC" -I "$y" -I "$dir" --list-analysis "$name" --view=canonical \
            > "$t/can1" 2>/dev/null
        if cmp -s "$t/can1" "$y/$name.rxt"; then
            ok "$id R2 list->load->list is a fixed point ($(wc -c < "$t/can1" | tr -d ' ') bytes)"
        else
            bad "$id R2 the canonical view is not a fixed point: $(diff "$y/$name.rxt" "$t/can1" | head -4 | tr '\n' ' ')"
        fi
        # R3 (the twin reads both files)
        if "$ANALYZE" --dump-doc "$f" > "$t/doc0" 2>"$t/aerr" &&
           "$ANALYZE" --dump-doc "$y/$name.rxt" > "$t/doc1" 2>>"$t/aerr" &&
           [ -s "$t/doc0" ] && cmp -s "$t/doc0" "$t/doc1"; then
            ok "$id R3 the independent reader reads the original and the canonical view as one document ($(($(wc -l < "$t/doc0") - 3)) fields)"
        else
            bad "$id R3 the independent reader's documents differ: $(cat "$t/aerr" | head -2 | tr '\n' ' ') $(diff "$t/doc0" "$t/doc1" 2>/dev/null | head -4 | tr '\n' ' ')"
        fi
        # R5 (pcrec's interpretation of the FILE vs the twin's)
        dec_section < "$t/dec0" > "$t/dsec0"
        if [ -s "$t/doc0" ] && cmp -s "$t/dsec0" "$t/doc0"; then
            ok "$id R5 decoded = the independent decode, field by field"
        else
            bad "$id R5 pcrec's decoded view differs from the independent decode: $(diff "$t/doc0" "$t/dsec0" | head -4 | tr '\n' ' ')"
        fi
        # R5's resolution digests: every row the bundle itself (link 0)
        # answers, against findings_ref.py on the same file.
        pcrec_run "$PCREC" -I "$dir" --list-analysis "$name" > "$t/list" 2>/dev/null
        awk -F'\t' '/^#section /{split($0, w, " "); s = (w[2] == "resolution")} s && !/^#/ && $3 == "0" && $7 != "none" {print $1, $2, $5, $6, $7}' \
            "$t/list" > "$t/res"
        nres=0; badres=0
        while read -r q e kind via dig; do
            nres=$((nres + 1))
            want="$($REF bundle-digest "$f" "$name" "$kind" "$via")"
            [ "$want" = "$dig" ] || { badres=$((badres + 1)); echo "  $id $q@$e $kind/$via: listing $dig, findings_ref $want" >&2; }
        done < "$t/res"
        if [ "$badres" -eq 0 ]; then
            ok "$id R5 $nres resolution digest(s) the bundle answers itself = findings_ref.py"
        else
            bad "$id R5 $badres of $nres resolution digests disagree with findings_ref.py"
        fi
    done
    if [ "$policy" = all ] && [ "$loaded" -ne "$files" ]; then
        bad "set $set: $loaded of $files files loaded (every one must)"
    fi
    if [ "$loaded" -ge "$floor" ]; then
        ok "set $set: $loaded item(s) round-tripped (floor $floor)"
    else
        bad "set $set: $loaded item(s) loaded, under its floor $floor — the population has shrunk (K35)"
    fi
done

# ---- the loader refuses a DERIVED view fed back (S962) -------------------
mkdir -p "$WORKDIR/der1" "$WORKDIR/der2"
pcrec_run "$PCREC" --list-analysis log > "$WORKDIR/der1/log.rxt" 2>/dev/null
pcrec_run "$PCREC" --list-analysis log --view=decoded > "$WORKDIR/der2/log.rxt" 2>/dev/null
for c in "der1|chain|--list-analysis log" "der2|decoded|--analysis log --pattern abc -o $WORKDIR/der2/x.c"; do
    IFS='|' read -r d sec args <<< "$c"
    # shellcheck disable=SC2086
    if pcrec_run "$PCREC" -I "$WORKDIR/$d" $args >/dev/null 2>"$WORKDIR/$d/err"; then
        bad "a '$sec' listing fed back through -I LOADED (the loader must refuse a derived view)"
    elif grep -qF "carries '#section $sec'" "$WORKDIR/$d/err" &&
         grep -qF -- "--view=canonical" "$WORKDIR/$d/err"; then
        ok "a '$sec' listing fed back through -I is refused naming the section and --view=canonical"
    else
        bad "a '$sec' listing fed back is refused, but not by the derived-section rule: $(head -c 200 "$WORKDIR/$d/err")"
    fi
done

# ---- controls: each compare must be able to fail ------------------------
c="$WORKDIR/it/shipped/default"
if [ -s "$c/y/default.rxt" ]; then
    grep -v '^    description ' "$c/y/default.rxt" > "$WORKDIR/ctl_desc.rxt"
    "$ANALYZE" --dump-doc "$WORKDIR/ctl_desc.rxt" > "$WORKDIR/ctl_desc.doc" 2>/dev/null
    if ! cmp -s "$WORKDIR/ctl_desc.doc" "$c/doc0"; then
        ok "control: R3 fails on a canonical default with its description dropped"
    else
        bad "control: R3 reads a canonical default WITHOUT its description as the same document — R3 cannot fail"
    fi
else
    bad "control: no canonical default to plant into"
fi
c="$WORKDIR/it/kfixtures/kline"
if [ -s "$c/y/kline.rxt" ]; then
    mkdir -p "$WORKDIR/ctl_enc"
    sed 's/when byte,utf8 via/when byte via/' "$c/y/kline.rxt" > "$WORKDIR/ctl_enc/kline.rxt"
    "$ANALYZE" --dump-doc "$WORKDIR/ctl_enc/kline.rxt" > "$WORKDIR/ctl_enc.doc" 2>/dev/null
    pcrec_run "$PCREC" -I "$WORKDIR/ctl_enc" --list-analysis kline --view=decoded \
        > "$WORKDIR/ctl_enc.dec" 2>/dev/null
    if ! cmp -s "$WORKDIR/ctl_enc.doc" "$c/doc0" &&
       [ "$(item_digest "$WORKDIR/ctl_enc.dec")" = "$(item_digest "$c/dec0")" ]; then
        ok "control: an encoding dropped from 'serves' leaves R1's digest unmoved and R3 catches it"
    else
        bad "control: dropping a serves encoding is not seen by R3, or moved R1's digest (rows_digest covers no serves)"
    fi
    { head -4 "$c/dsec0"; sed -n '6p' "$c/dsec0"; sed -n '5p' "$c/dsec0"; tail -n +7 "$c/dsec0"; } > "$WORKDIR/ctl_swap"
    if ! cmp -s "$WORKDIR/ctl_swap" "$c/doc0"; then
        ok "control: R5 fails on a decode with two rows swapped"
    else
        bad "control: R5 cannot see two swapped rows"
    fi
else
    bad "control: no canonical kline to plant into"
fi

if [ "$n_items" -ge 40 ]; then
    ok "population: $n_items items round-tripped (floor 40)"
else
    bad "population: $n_items items round-tripped, under the floor 40 (K35)"
fi
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
