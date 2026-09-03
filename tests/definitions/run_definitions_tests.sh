#!/usr/bin/env bash
# tests/definitions/run_definitions_tests.sh — [DD-13b.W1.3] THE COMPOSITION
# IDENTITY PROOF: a composed artifact answers exactly what the flat one does.
#
# THE QUESTION. `pcrec --source` binds a definition into a target pattern by
# SUB-PARSING it, re-numbering its groups through an assignment map and
# splicing it in as `A_REP{0,0}(A_CAP{base}(body))`. Everything about that is
# invisible from outside except one thing: what the resulting matcher ANSWERS.
# So the check is answer-identity against a control, and the whole design of
# this file is about where the control comes from.
#
# THREE SOURCES, NO TWO OF WHICH SHARE ONE (memory
# `pcrec-check-design-lessons`; docs/dev/learnings.md §3):
#
#   1. python `re` on the FLAT pattern           — an outside oracle
#   2. the FLAT pattern compiled by pcrec        — pcrec with no composer
#   3. the COMPOSED source compiled by pcrec     — the thing under test
#
# The flat patterns are HAND-WRITTEN in `flat.rxtin` and are never generated.
# That is the point on which this check either is or is not a control: a flat
# pattern produced by pcrec — by `--emit-composed`, say — would be the
# composer describing itself, and every sabotage of the composer would move
# both sides together. Leg 1 exists for the same reason one layer out: legs 2
# and 3 are the same compiler, so a defect in a stage BELOW the composer
# (the emitter, an optimization pass) would move both of them and only an
# outside oracle can see it.
#
# WHAT A GREEN RUN DOES NOT PROVE, stated because the numbers here are small.
# It does not prove the composer right on any pattern this corpus does not
# contain; the population is seven targets and twenty-three cases. Its job is to
# be the FIRST place a composed artifact's answers are checked at all, and
# to be a place a sabotage row can be aimed at. The sabotage rows are named
# in w1_impl.md §8.4 (S-W13a..g); the ones this file is the named detector
# for are S-W13c (the erased tier stops erasing — `RX_NCAPS` moves),
# S-W13e (the pending-record pass is skipped — `rep` inverts, which is
# w1_impl §2.5's own MEASURED cell) and S-W13g (a forgotten scope field —
# a definition parsed at the caller's count MEANS something else).
#
# WHY THE FIXTURES ARE `.rxtin` AND NOT `.rxt`. `tests/harness/run.sh` finds
# `*.rxt` under `tests/`, and a composed block CANNOT be compiled from its
# own text — the definitions are a FILE-level fact. Until run.sh grows a
# composed-block path, a `.rxt` here would be a corpus file the corpus runner
# cannot build, and it would additionally move four pinned census numbers
# (`tests/rxtsource/run_rxtsource_tests.sh`'s CENSUS_* and the RUNSH_* it
# reconciles against). So the fixtures carry `tests/rxtsource/fixtures/`'s
# own `.rxtin` extension and this script copies them into a scratch
# directory as `.rxt` when it needs them — which is also what makes the
# `lib "defs_common.rxt"` reference in `composed.rxtin` resolve.

set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
DRIVER="$ROOT_DIR/tests/harness/driver.c"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:-}"

# EVERY BLOCK IS COMPILED UNDER THE SAME FEATURE SET, on both sides. It is
# passed on the command line rather than written into the fixtures because
# `composed.rxtin` is deliberately a file that declares no `features` line —
# the bench's own condition for an exported set (O-13 §4(b)), and the shape
# a library file should have. `(?&name)` needs `recursion` and
# `named-groups`; `all` is the simplest set that is the same on both legs,
# and being the SAME is the only property this check needs from it.
FEATURES="${DEFS_FEATURES:-all}"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-definitions.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT

checks_passed=0
checks_failed=0
pass() { checks_passed=$((checks_passed + 1)); echo "PASS: $*"; }
fail() { checks_failed=$((checks_failed + 1)); echo "FAIL: $*" >&2; }

cp "$SCRIPT_DIR/defs_common.rxtin" "$WORKDIR/defs_common.rxt"
cp "$SCRIPT_DIR/composed.rxtin"    "$WORKDIR/composed.rxt"
cp "$SCRIPT_DIR/flat.rxtin"        "$WORKDIR/flat.rxt"

# ---------------------------------------------------------------------
# THE PINNED POPULATION.
#
# Without it the comparison is vacuously true: two artifacts agree perfectly
# about zero cases, and a fixture that silently lost its blocks would make
# this whole section green. Both numbers are compared below against a
# derivation that does not go through pcrec.
PIN_TARGETS=7
PIN_CASES=23

# ---------------------------------------------------------------------
# (0) The population, derived by awk over the raw bytes — never by asking
# pcrec, which is half of what is under test.
n_targets=$(LC_ALL=C grep -c '^target ' "$WORKDIR/composed.rxt")
n_cases=$(LC_ALL=C grep -cE '^(m|n) ' "$WORKDIR/composed.rxt")
n_flat_cases=$(LC_ALL=C grep -cE '^(m|n) ' "$WORKDIR/flat.rxt")

if [ "$n_targets" = "$PIN_TARGETS" ] && [ "$n_cases" = "$PIN_CASES" ]; then
    pass "population: composed.rxtin has $n_targets targets and $n_cases cases (pinned)"
else
    fail "population MOVED: composed.rxtin has $n_targets targets / $n_cases cases,
  pinned $PIN_TARGETS / $PIN_CASES. If a fixture legitimately changed, update
  PIN_TARGETS/PIN_CASES here in the same commit."
fi
if [ "$n_cases" = "$n_flat_cases" ]; then
    pass "the flat control carries the same $n_flat_cases cases as the composed source"
else
    fail "the flat control has $n_flat_cases cases where the composed source has $n_cases —
  the two files must pair case for case or the comparison below is partial"
fi

# ---------------------------------------------------------------------
# (1) A LIBRARY SHIPS NOTHING BY ITSELF. `defs_common.rxt` declares no
# target, so `--source` on it builds nothing AT EXIT 0 — a different
# observable from a refusal, and the one format_design §6.1 requires.
lib_out="$("$TIMEOUT_BIN" 60 "$PCREC" --features "$FEATURES" \
             --source "$WORKDIR/defs_common.rxt" -o "$WORKDIR" 2>&1)"
lib_rc=$?
if [ "$lib_rc" = "0" ] && [ ! -e "$WORKDIR/w.c" ]; then
    pass "the definitions file builds NOTHING at exit 0 (a library ships nothing by itself)"
else
    fail "the definitions file should build nothing at exit 0; got exit $lib_rc: $lib_out"
fi

# ---------------------------------------------------------------------
# Build one artifact and its driver. $1 = directory, $2 = prefix,
# $3.. = the pcrec arguments that produce $1/gen.c.
build_one() {
    local dir="$1" px="$2"; shift 2
    local upx; upx="$(printf '%s' "$px" | LC_ALL=C tr '[:lower:]' '[:upper:]')"
    mkdir -p "$dir"
    local err rc
    err="$("$TIMEOUT_BIN" 120 "$PCREC" "$@" -o "$dir/gen.c" 2>&1 >/dev/null)"; rc=$?
    if [ $rc -ne 0 ] || [ ! -f "$dir/gen.h" ]; then
        echo "pcrec failed (exit $rc): $err"
        return 1
    fi
    # shellcheck disable=SC2086
    if ! "$TIMEOUT_BIN" 300 "$CC" -O1 $GENCFLAGS -I"$dir" \
            -DRXT_PREFIX="$px" -DRXT_UPREFIX="$upx" \
            -o "$dir/t" "$DRIVER" "$dir/gen.c" 2>"$dir/cc.log"; then
        echo "$CC failed: $(head -3 "$dir/cc.log")"
        return 1
    fi
    return 0
}

# The `m`/`n` cases of one block of one file, as `<kind>\t<subject>` rows.
# Reads the raw bytes; the subject keeps its .rxt escaping, which is exactly
# what driver.c decodes.
block_cases() {
    local file="$1" name="$2"
    LC_ALL=C awk -v want="$name" '
        /^pattern /            { inblock = 0; nm = "" ; next }
        /^name /               { nm = $2; inblock = (nm == want); next }
        inblock && /^m "/      { sub(/^m "/, ""); sub(/" [0-9]+ [0-9]+[[:space:]]*$/, ""); print "m\t" $0; next }
        inblock && /^n "/      { sub(/^n "/, ""); sub(/"[[:space:]]*$/, ""); print "n\t" $0; next }
    ' "$file"
}

# ---------------------------------------------------------------------
# (2) THE IDENTITY PROOF, per target.
total_cells=0
delivered_cells=0
for px in $(LC_ALL=C awk '/^target /{ n=$3; gsub(/[-.]/, "_", n); print n }' "$WORKDIR/composed.rxt"); do
    def="$(LC_ALL=C awk -v p="$px" '/^target /{ n=$3; m=n; gsub(/[-.]/,"_",m); if (m==p) { print n; exit } }' "$WORKDIR/composed.rxt")"

    cdir="$WORKDIR/c_$px"
    fdir="$WORKDIR/f_$px"

    if ! msg="$(build_one "$cdir" "$px" --features "$FEATURES" \
                   --source "$WORKDIR/composed.rxt" --target "$px")"; then
        fail "composed target '$px' ($def) did not build: $msg"
        continue
    fi
    flat_pat="$(LC_ALL=C awk -v want="$def" '
        /^pattern /  { p = substr($0, 9); next }
        /^name /     { if ($2 == want) { print p; exit } }
    ' "$WORKDIR/flat.rxt")"
    if [ -z "$flat_pat" ]; then
        fail "flat.rxtin declares no block named '$def' — the control is MISSING for this target,
  which would otherwise show up as this target simply not being compared"
        continue
    fi
    if ! msg="$(build_one "$fdir" "$px" --features "$FEATURES" -p "$px" -- "$flat_pat")"; then
        fail "flat control '$def' did not build: $msg"
        continue
    fi

    # THE COMPOSED ARTIFACT'S OWN STRUCTURE. `ngroups` is the TARGET
    # pattern's own count and the definitions' slots sit above it, so
    # `RX_NCAPS - 1 >= ngroups` always and `>` exactly when something was
    # bound. Asserting the DIRECTION rather than a number keeps this check
    # from having to know the assignment order, which is the artifact's
    # business (docs/spec/match_api.md §6).
    cngroups="$(LC_ALL=C grep -m1 '^    \.ngroups = ' "$cdir/gen.c" | tr -dc '0-9')"
    cncaps="$(LC_ALL=C grep -m1 -oE '^#define [A-Z0-9_]*_NCAPS [0-9]+' "$cdir/gen.h" | awk '{print $3}')"
    cnnames="$(LC_ALL=C grep -m1 '^    \.nnames = ' "$cdir/gen.c" | tr -dc '0-9')"
    cnentries="$(LC_ALL=C grep -m1 '^    \.nentries = ' "$cdir/gen.c" | tr -dc '0-9')"
    if [ -n "$cngroups" ] && [ -n "$cncaps" ] && [ "$((cncaps - 1))" -gt "$cngroups" ]; then
        pass "'$def': composed artifact has slots above ngroups (ngroups=$cngroups, RX_NCAPS=$cncaps) — a definition was bound"
    else
        fail "'$def': composed artifact has RX_NCAPS=$cncaps against ngroups=$cngroups —
  nothing was bound, so this target is not testing composition at all
  ([MECH-REACH]: a witness that stopped reaching its site)"
    fi
    if [ -n "$cnnames" ] && [ -n "$cnentries" ] && [ "$cnentries" -ge "$cnnames" ]; then
        pass "'$def': nnames=$cnnames <= nentries=$cnentries (the primary's rows are a prefix)"
    else
        fail "'$def': nnames=$cnnames, nentries=$cnentries — nnames must never exceed nentries"
    fi

    # THE `groups[]` ROW TABLES, read off both artifacts as TEXT — never off
    # the composer's own report of what it delivered. `name:slot` per row.
    crows="$(LC_ALL=C sed -n 's/^    { "\([^"]*\)", [0-9]*, \([0-9-]*\), .*$/\1:\2/p' "$cdir/gen.c")"
    frows="$(LC_ALL=C sed -n 's/^    { "\([^"]*\)", [0-9]*, \([0-9-]*\), .*$/\1:\2/p' "$fdir/gen.c")"

    # THE ANSWERS.
    while IFS=$'\t' read -r kind subj; do
        [ -n "$kind" ] || continue
        total_cells=$((total_cells + 1))
        cout="$("$TIMEOUT_BIN" 30 "$cdir/t" "$subj" 2>&1)"; crc=$?
        fout="$("$TIMEOUT_BIN" 30 "$fdir/t" "$subj" 2>&1)"; frc=$?
        pyout="$("$TIMEOUT_BIN" 30 python3 -c '
import re, sys
pat, subj = sys.argv[1], sys.argv[2]
subj = subj.encode("utf-8").decode("unicode_escape")
m = re.compile(pat).search(subj)
print("match %d %d" % m.span() if m else "nomatch")
' "$flat_pat" "$subj" 2>&1)"

        # The composed and flat artifacts must agree on the WHOLE-MATCH span,
        # which is the first three fields of driver.c's line. They may differ
        # in later fields: the flat control's groups are its own and the
        # composed artifact's are the definitions', and that difference is
        # the thing being built, not a disagreement.
        cspan="$(printf '%s' "$cout" | cut -d' ' -f1-3)"
        fspan="$(printf '%s' "$fout" | cut -d' ' -f1-3)"
        if [ "$crc" = "$frc" ] && [ "$cspan" = "$fspan" ]; then
            :
        else
            fail "'$def' subject \"$subj\": composed answered '$cspan' (exit $crc), flat answered '$fspan' (exit $frc)"
            continue
        fi
        # ---- [DD-13b.W1.3] THE DELIVERED SPANS, COMPARED BY NAME --------
        #
        # The whole-match span above says a composed matcher finds the same
        # text. It says NOTHING about whether a delivering site kept what its
        # callee matched, which is the half D89 addendum 4(2) added — and a
        # delivered row that always read (-1,-1) would pass every check above
        # it.
        #
        # THE BRIDGE IS THE ORACLE'S OWN RENAME RULE. Addendum 4(2) defines
        # the oracle for a delivering site as the definition's body inlined at
        # the site with its groups renamed `site_x`; `flat.rxtin` is written
        # that way by hand. So a composed row named `site.group` and the flat
        # control's row named `site_group` are THE SAME GROUP under that rule,
        # and comparing their spans is comparing a delivery against a pattern
        # nobody generated. A flat import's row is already the bare name on
        # both sides, so one substitution covers both shapes.
        #
        # THE SLOTS DIFFER ON PURPOSE and are never compared: the composed
        # artifact's delivered slot sits above `ngroups` and the control's is
        # an ordinary group number. Matching by NAME is what makes that
        # difference invisible, which is also the contract `match_api.md` §6
        # states for a caller.
        for crow in $crows; do
            cname="${crow%%:*}"; cslot="${crow##*:}"
            fname="$(printf '%s' "$cname" | tr '.' '_')"
            fslot=""
            for frow in $frows; do
                [ "${frow%%:*}" = "$fname" ] && fslot="${frow##*:}"
            done
            if [ -z "$fslot" ]; then
                fail "'$def': the composed artifact delivers '$cname' but the flat control has no group '$fname' —
  the control cannot check a delivery it does not carry (addendum 4(2)'s rename rule is site.group -> site_group)"
                continue
            fi
            cds="$(printf '%s' "$cout" | awk -v k="$cslot" '{print $(2*k+2), $(2*k+3)}')"
            fds="$(printf '%s' "$fout" | awk -v k="$fslot" '{print $(2*k+2), $(2*k+3)}')"
            if [ "$cds" = "$fds" ]; then
                delivered_cells=$((delivered_cells + 1))
                # A DELIVERED ROW THAT IS UNSET ON A MATCHING CASE IS THE
                # HALF-FEATURE THESE RULINGS REMOVED, so it is a failure even
                # when both sides agree about it — agreement on (-1,-1) is
                # exactly what a build with no retention would produce.
                if [ "$kind" = "m" ] && [ "$cds" = "-1 -1" ]; then
                    fail "'$def' subject \"$subj\": delivered group '$cname' reads (-1,-1) on a MATCHING case.
  Both artifacts agree, which is what a build with no retention at all looks like."
                fi
            else
                fail "'$def' subject \"$subj\": delivered '$cname' is [$cds] but the flat control's '$fname' is [$fds]"
            fi
        done

        if [ "$cspan" != "$pyout" ]; then
            fail "'$def' subject \"$subj\": both artifacts answered '$cspan' but python re on the flat pattern answered '$pyout' —
  the two pcrec legs agreeing against the oracle is a defect BELOW the composer"
            continue
        fi
        case "$kind" in
            m) case "$cspan" in match*) ;; *) fail "'$def' subject \"$subj\": expected a match, got '$cspan'";; esac ;;
            n) case "$cspan" in nomatch) ;; *) fail "'$def' subject \"$subj\": expected no match, got '$cspan'";; esac ;;
        esac
    done < <(block_cases "$WORKDIR/composed.rxt" "$def")
done

if [ "$delivered_cells" -gt 0 ]; then
    pass "retention: $delivered_cells delivered-span comparisons against the hand-written flat control"
else
    fail "retention: ZERO delivered spans were compared. Either no fixture uses a
  delivering call, or every composed artifact emitted no groups[] row — both of
  which make every check above vacuous for the feature D89 addendum 4(2) added."
fi

if [ "$total_cells" = "$PIN_CASES" ]; then
    pass "identity: $total_cells cells compared three ways (composed artifact, flat artifact, python re)"
else
    fail "identity ran $total_cells cells, pinned $PIN_CASES —
  a case that stopped being compared is invisible in a pass count"
fi

# ---------------------------------------------------------------------
# (3) DELIVERY BY NAME. A definition that NAMES a group puts a row in the
# composed artifact's `groups[]` whose `ref` is the definition's name, and
# that row sits BELOW every row the target pattern itself declared. Read off
# the emitted artifact as text — never off the composer's own report, which
# would be the composer checking itself.
pair_rows="$(LC_ALL=C grep -E '^    \{ "' "$WORKDIR/c_pair/gen.c" 2>/dev/null || true)"
if printf '%s\n' "$pair_rows" | LC_ALL=C grep -q '{ "word", [0-9]*, [0-9]*, "w" }'; then
    pass "delivery: 'pair' emits a groups[] row for 'word' with ref \"w\" (the definition's name)"
else
    fail "delivery: 'pair' has no groups[] row { \"word\", .., .., \"w\" }. Rows found:
$pair_rows"
fi
# THE ORDER IS THE ABI CONTRACT: `(ref-is-NULL, name, number)`, so every row
# with a NULL ref precedes every row without one. A caller running
# match_api.md §6's bsearch over groups[0..nnames) depends on it.
order_bad="$(printf '%s\n' "$pair_rows" | LC_ALL=C awk '
    /, NULL \}/ { if (seen_ref) bad++ ; next }
    /\}/        { seen_ref = 1 }
    END         { print bad + 0 }')"
if [ "$order_bad" = "0" ]; then
    pass "order: every ref-NULL row precedes every ref-bearing row (the primary's rows are a genuine PREFIX)"
else
    fail "order: $order_bad ref-NULL row(s) sort AFTER a ref-bearing row — nnames no longer names a prefix"
fi

echo
echo "definitions: $checks_passed passed, $checks_failed failed"
[ "$checks_failed" -eq 0 ]
