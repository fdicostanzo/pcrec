#!/usr/bin/env bash
# tests/bench/tier_escalation.sh -- [OPT-1] STEP 3: the tier-escalation RATE
# over exemplar subject files. A MEASUREMENT lane, not a check: it prints
# numbers and exits 0 on a clean run (a compile/build/driver failure exits
# nonzero; a HIGH escalation rate is data, not a failure).
#
# =========================================================================
# WHAT THIS MEASURES AND WHY
# =========================================================================
# docs/design/two_tier_entry.md section 7, "THE FOLLOW-UP IS NAMED AND IS
# NOT THIS LANE'S" (lane srTier, [OPT-1] STEP 2): "How often real calls
# escalate is a MEASUREMENT nobody has ... The -D<PREFIX>_TEST_TIER_HOOK
# build already counts escalations, so a first cut needs a driver and no
# profiler." docs/spec/match_api.md section 3/section 10.9 states the bet
# and its cost when it loses (a 3.05x discontinuity at the boundary, 1.24-
# 1.53x slower above it, up to 2x the STEP/WORK budget on an escalating
# call) but has no number for how OFTEN a real workload crosses it. This
# script is that number, on the one realistic exemplar population this
# project has today: pcrec-bench's bench/email sub-bench (RFC 5322 email
# validation, hand-inlined `orig.rx` vs subroutine-factored `factored.rx`,
# 85 compliance subjects + 77 short search subjects + 3 x 1 MB throughput
# subjects, all real addresses/near-misses, not synthetic worst cases).
#
# THE HOOK: `rx_tier_escalated()`, an extern the artifact calls at its one
# escalation site under -DRX_TEST_TIER_HOOK and only then (match_api.md
# section 5.3, section 10.9) -- the same hook tests/codegen/tier_driver.c
# uses for an IDENTITY check against a synthetic depth ladder. This file
# reuses it for a RATE over a real population instead, so it does not
# duplicate run_tiered_entry.sh's job: that file proves the mechanism is
# correct; this one measures how often it fires. tests/bench/
# tier_escalation_driver.c is the counting driver (see its header).
#
# TWO FORMS, per bench/email's own regime split (its NOTES.md, "The match
# regime runs a SECOND pcrec artifact"): "search" calls `rx_search` on the
# plain artifact (the search_short and throughput sets); "whole" compiles
# `(?:PATTERN)\z` as a second artifact and calls `rx_match_caps` on it (the
# match/compliance set, all 85 subjects). Both artifacts are forced
# `--engine=vm`: pcrec's default engine selection (`auto`) puts BOTH
# `orig` and `factored` on the DFA at the pin this repo currently builds
# against (confirmed below, section 1) -- and a DFA artifact has no tier
# (two_tier_entry.md section 6: "No DFA byte moves"), so `auto` has
# nothing for this instrument to count. `--engine=vm` is pcrec-bench's own
# `pcrec-vm` config and, per its CLAUDE.md, "the one entry on bench/email
# where the depth path is reachable at all" -- i.e. the one config an
# escalation-rate measurement can say anything about.
#
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS (docs/dev/
# learnings.md section 3): `floor.rx` (the single-byte literal `@`) is run
# through the same pipeline as a NEGATIVE control -- its stamped default
# fits the fast tier's own budget outright (RX_FAST_FRAMES ==
# RX_RESUME_FRAMES, two_tier_entry.md section 3.1's "ONE TIER" case), so it
# must show zero escalations by construction; a nonzero count there would
# mean this driver or its hook is measuring something other than what it
# claims to.
#
# Usage: bash tests/bench/tier_escalation.sh
# Env: PCREC (default <root>/build/pcrec), CC (default gcc), KEEP=1,
#      BENCH_REPO_DIR (default /home/duxevents/pcrec-bench -- READ-ONLY,
#      per this repo's CLAUDE.md mandate; nothing here writes there)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"   # pcrec_run, TIMEOUT_BIN

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
BENCH_REPO_DIR="${BENCH_REPO_DIR:-/home/duxevents/pcrec-bench}"
EMAIL_DIR="$BENCH_REPO_DIR/bench/email"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "tier-escalation: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

fail=0
err() { echo "ERROR: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "ERROR: tier-escalation: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }
[ -d "$EMAIL_DIR" ] || { echo "ERROR: tier-escalation: no $EMAIL_DIR — pcrec-bench must be checked out beside pcrec (D52)" >&2; exit 1; }

stamp() { awk -v k="$2" '$1 == "#define" && $2 == k { print $3 }' "$1" | head -1; }
stamp_str() { awk -v k="$2" '$1 == "#define" && $2 == k { print $3 }' "$1" | tr -d '"' | head -1; }

# ===========================================================================
# section 1 -- build the four artifacts: {orig,factored} x {plain,whole}
# ===========================================================================
echo "-- section 1: building the four VM artifacts, and recording what auto selects --"

build_one() {   # build_one <name> <pattern-text> <workdir> [extra pcrec flags...]
    local name="$1" pat="$2" d="$3"; shift 3
    mkdir -p "$d"
    printf '%s' "$pat" > "$d/pattern.txt"
    pcrec_run "$PCREC" -p rx --features all "$@" -o "$d/gen.c" -- "$pat" \
        >"$d/pcrec.log" 2>&1
}

declare -A PATFILE=( [orig]="orig.rx" [factored]="factored.rx" [floor]="floor.rx" )
declare -A FAST_F FAST_T DEF_F DEF_T AUTO_ENGINE

for pat in orig factored floor; do
    ptext="$(cat "$EMAIL_DIR/patterns/${PATFILE[$pat]}")"
    wztext="(?:${ptext})\\z"

    # plain form, forced VM
    if ! build_one "$pat-plain" "$ptext" "$WORKDIR/$pat-plain" --engine=vm; then
        err "could not compile $pat plain (vm): $(head -3 "$WORKDIR/$pat-plain/pcrec.log")"
        continue
    fi
    FAST_F[$pat]="$(stamp "$WORKDIR/$pat-plain/gen.c" RX_FAST_FRAMES)"
    FAST_T[$pat]="$(stamp "$WORKDIR/$pat-plain/gen.c" RX_FAST_TRAIL)"
    DEF_F[$pat]="$(stamp "$WORKDIR/$pat-plain/gen.h" RX_RESUME_FRAMES)"
    DEF_T[$pat]="$(stamp "$WORKDIR/$pat-plain/gen.h" RX_TRAIL_FRAMES)"

    # whole-subject form, forced VM (built separately so a failure here does
    # not discard the plain-form stats just read)
    if ! build_one "$pat-whole" "$wztext" "$WORKDIR/$pat-whole" --engine=vm; then
        err "could not compile $pat whole-subject (vm): $(head -3 "$WORKDIR/$pat-whole/pcrec.log")"
    fi

    # what auto selects, plain form only (informational -- RX_ENGINE is
    # read here for REPORTING, never to decide which artifact's stamps to
    # check; run_tiered_entry.sh section 2's circularity note is about the
    # latter)
    if build_one "$pat-auto" "$ptext" "$WORKDIR/$pat-auto"; then
        AUTO_ENGINE[$pat]="$(stamp_str "$WORKDIR/$pat-auto/gen.c" RX_ENGINE)"
    else
        AUTO_ENGINE[$pat]="refused: $(head -1 "$WORKDIR/$pat-auto/pcrec.log")"
    fi

    tier="single-tier"
    [ "${FAST_F[$pat]}" -lt "${DEF_F[$pat]}" ] 2>/dev/null && tier="TIERED"
    echo "$pat: auto selects ${AUTO_ENGINE[$pat]}; forced-vm plain fast=${FAST_F[$pat]}/${FAST_T[$pat]} default=${DEF_F[$pat]}/${DEF_T[$pat]} ($tier)"
done

# ===========================================================================
# section 2 -- build the counting driver against each artifact
# ===========================================================================
echo
echo "-- section 2: building tier_escalation_driver against each artifact --"

for pat in orig factored floor; do
    for form in plain whole; do
        d="$WORKDIR/$pat-$form"
        [ -f "$d/gen.c" ] || continue
        if ! (cd "$d" && "$CC" -O2 -I"$d" -DRX_TEST_TIER_HOOK \
                -o "$d/driver" "$SCRIPT_DIR/tier_escalation_driver.c" "$d/gen.c") \
                >"$d/drv.log" 2>&1; then
            err "could not build the driver against $pat/$form: $(head -5 "$d/drv.log")"
        fi
    done
done

# ===========================================================================
# section 3 -- the subject lists (id\tpath), derived from pcrec-bench's own
# manifests, never hand-enumerated (docs/dev/learnings.md section 3: a
# reference list assembled by hand or by glob drifts silently)
# ===========================================================================
echo
echo "-- section 3: deriving subject lists from pcrec-bench's manifests --"

MATCH_LIST="$WORKDIR/list.match.tsv"      # all 85, whole-subject form
SEARCH_LIST="$WORKDIR/list.search.tsv"    # the 77 <=256B, search form
THRU_LIST="$WORKDIR/list.throughput.tsv"  # the three 1 MB, search form

awk -F'\t' 'NR>1{print $1}' "$EMAIL_DIR/manifest.tsv" | LC_ALL=C sort -u \
  | awk -v d="$EMAIL_DIR/subjects" '{print $1"\t"d"/"$1".bin"}' > "$MATCH_LIST"
NMATCH=$(wc -l < "$MATCH_LIST")

awk -F'\t' '$1=="orig" && $3=="search_short"{print $2}' "$EMAIL_DIR/expectations.tsv" \
  | LC_ALL=C sort -u \
  | awk -v d="$EMAIL_DIR/subjects" '{print $1"\t"d"/"$1".bin"}' > "$SEARCH_LIST"
NSEARCH=$(wc -l < "$SEARCH_LIST")

awk -F'\t' 'NR>1{print $1}' "$EMAIL_DIR/manifest_throughput.tsv" \
  | awk -v d="$EMAIL_DIR/throughput" '{print $1"\t"d"/"$1".bin"}' > "$THRU_LIST"
NTHRU=$(wc -l < "$THRU_LIST")

echo "match (whole-subject): $NMATCH subjects; search_short: $NSEARCH subjects; throughput: $NTHRU subjects"
if [ "$NMATCH" -ne 85 ] || [ "$NSEARCH" -ne 77 ] || [ "$NTHRU" -ne 3 ]; then
    err "subject list sizes disagree with bench/email/NOTES.md's stated population (want 85/77/3, got $NMATCH/$NSEARCH/$NTHRU) — the manifests moved and this script's populations are stale"
fi

# ===========================================================================
# section 4 -- run the driver, one call per subject, and summarise
# ===========================================================================
echo
echo "-- section 4: escalation counts --"

ROWS="$WORKDIR/rows.tsv"   # pattern form set id bytes escalated outcome
: > "$ROWS"

run_set() {   # run_set <pattern> <form> <setname> <driver-form> <list>
    local pat="$1" form="$2" setname="$3" driverform="$4" list="$5"
    local d="$WORKDIR/$pat-$form"
    [ -x "$d/driver" ] || { err "no driver for $pat/$form ($setname)"; return; }
    if ! "$TIMEOUT_BIN" 120 "$d/driver" "$driverform" "$list" > "$WORKDIR/out.$pat.$form.$setname" 2>"$WORKDIR/err.$pat.$form.$setname"; then
        err "driver failed on $pat/$form/$setname: $(head -3 "$WORKDIR/err.$pat.$form.$setname")"
        return
    fi
    awk -v p="$pat" -v f="$form" -v s="$setname" \
        '$1=="row"{print p"\t"f"\t"s"\t"$2"\t"$3"\t"$4"\t"$5}' \
        "$WORKDIR/out.$pat.$form.$setname" >> "$ROWS"
}

for pat in orig factored floor; do
    run_set "$pat" whole match   whole  "$MATCH_LIST"
    run_set "$pat" plain search  search "$SEARCH_LIST"
    run_set "$pat" plain thru    search "$THRU_LIST"
done

NROWS=$(wc -l < "$ROWS")
if [ "$NROWS" -lt 1 ]; then
    err "zero rows collected across every (pattern,form,set) cell — nothing was measured"
fi

# ROWS columns: 1=pattern 2=form 3=set 4=id 5=bytes 6=escalated 7=outcome
printf '%-10s %-6s %-6s %6s %6s %8s %10s %10s\n' \
    "pattern" "form" "set" "N" "E" "rate" "maxNoEsc" "minEsc"
awk -F'\t' '
{
    key = $1"\t"$2"\t"$3
    n[key]++
    bytes = $5; esc = $6
    if (esc == "1") {
        e[key]++
        if (minesc[key] == "" || bytes < minesc[key]) minesc[key] = bytes
    } else {
        if (bytes > maxnoesc[key]) maxnoesc[key] = bytes
    }
}
END {
    for (k in n) {
        split(k, a, "\t")
        ee = (e[k] == "" ? 0 : e[k])
        rate = ee / n[k]
        mn = (maxnoesc[k] == "" ? "-" : maxnoesc[k])
        me = (minesc[k] == "" ? "-" : minesc[k])
        printf "%-10s %-6s %-6s %6d %6d %8.4f %10s %10s\n", a[1], a[2], a[3], n[k], ee, rate, mn, me
    }
}' "$ROWS" | LC_ALL=C sort

echo
echo "-- outcome breakdown per cell --"
awk -F'\t' '
{
    key = $1"\t"$2"\t"$3
    outc = $7
    gsub(/:.*/, "", outc)
    ocount[key"\t"outc]++
}
END {
    for (k in ocount) print k"\t"ocount[k]
}' "$ROWS" | LC_ALL=C sort | awk -F'\t' '{printf "%-10s %-6s %-6s %-10s %d\n", $1,$2,$3,$4,$5}'

echo
echo "-- escalating subjects, by (pattern,form,set) --"
awk -F'\t' '$6=="1"{printf "%-10s %-6s %-6s id=%-10s bytes=%-8s outcome=%s\n", $1,$2,$3,$4,$5,$7}' "$ROWS"

echo
echo "-- give-up subjects (any escalation status), by (pattern,form,set) --"
awk -F'\t' '$7 ~ /^giveup:/{printf "%-10s %-6s %-6s id=%-10s bytes=%-8s escalated=%s %s\n", $1,$2,$3,$4,$5,$6,$7}' "$ROWS"

echo
echo "== Summary =="
echo "errors: $fail"
[ "$fail" -eq 0 ] && exit 0 || exit 1
