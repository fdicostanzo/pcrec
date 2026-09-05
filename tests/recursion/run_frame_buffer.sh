#!/usr/bin/env bash
# tests/recursion/run_frame_buffer.sh — [DD-14.FB] (D71 item 2), the two
# checks the .rxt corpus structurally cannot hold.
#
# ON DEMAND, not part of `make test`: section 2 reserves 128 MB of address
# space and drives it to its ceiling, touching ~105 MB of resident memory and
# building 940 KB subjects. That is a measurement about a RESERVATION, and
# `make test`'s job is the population. tests/recursion/framebuffer.rxt carries
# the behavioural cells and tests/codegen the structural ones; both ride
# `make test`.
#
# =========================================================================
# SECTION 1 — the NULL descriptor IS the un-suffixed call, across a SPREAD
# =========================================================================
# Spec §10.3: "`buf == NULL` is defined to be exactly a call to the
# un-suffixed entry with the same other arguments. Not 'similar to', not
# 'equivalent in observable behaviour' — the same call."
#
# AND SINCE [DD-14.FB]'s CRITIC PASS IT COVERS ALL THREE `_in` ENTRIES, not
# one. driver.c cross-checks `<prefix>_match_in` and `<prefix>_match_caps_in`
# against their un-suffixed siblings on every non-default route, so the `null`
# route below drives all three and demands exact agreement of all three
# (capture spans included) — on the `null` route no divergence is permitted at
# all, because §10.3 defines that call to BE the un-suffixed one. Before that
# cross-check existed, `<prefix>_search_in` was the ONLY `_in` entry any cell,
# driver or measurement in this tree ever ran: three entries shipped and one
# was exercised. MEASURED in the failing direction (scratch emitter, never
# committed): an emitter whose `<prefix>_match_in` ignores its descriptor takes
# tests/recursion/framebuffer.rxt from 16/0 to 12/4; before the cross-check it
# took it from 16/0 to 16/0.
#
# framebuffer.rxt pins that on ONE pattern at TWO subjects. That is a thin
# population for a claim of exact identity, and thin in a specific direction:
# a delegation that special-cased, say, the give-up path, or that dropped the
# capture copy-out, would be invisible on a pattern chosen to exercise the
# give-up boundary. So this section runs a SPREAD — patterns picked to reach
# different emitted shapes and different ANSWER KINDS (match, no-match,
# captures, give-up, zero-width, DFA-selected) — and compares the driver's
# printed line BYTE FOR BYTE between the two routes. Not "both matched": the
# same bytes, capture spans included.
#
# =========================================================================
# SECTION 2 — THE SEVEN CAPACITY SITES, EXACT IN BOTH DIRECTIONS
# =========================================================================
# Under AddressSanitizer, on buffers with NO SLACK. See fb_exact_driver.c's
# header for why the absence of slack is the whole point: a capacity guard
# that is off by one is invisible on a generously sized buffer in both
# directions at once — too loose writes into slack the caller happens to own,
# too tight never fires.
#
# =========================================================================
# SECTION 3 — the mmap'd, lazily-committed reservation, RUN
# =========================================================================
# Spec §10.6's worked example, re-measured. See fb_mmap_driver.c's header for
# what it prints and why it is a C driver rather than a corpus cell.
#
# Usage: bash tests/recursion/run_frame_buffer.sh
# Env:   PCREC (default <root>/build/pcrec), CC (default gcc), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

# [K37, srMech 2026-08-25] `pcrec` runs under D45's compile budget here too:
# this file already wrapped every GENERATED-code run in "$TIMEOUT_BIN" but ran
# the compiler itself bare, which is the gap K37 names (a sabotaged compiler
# that does not terminate hangs the matrix instead of failing its arm).

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O2 -std=gnu11 -Wall -Wextra -Werror}"

# REQUIRE_ASAN — [srMech 2026-08-25, Frank's ruling on S155] SECTION 2 IS AN
# INSTRUMENT, AND A MISSING INSTRUMENT IS NOT A MEASUREMENT.
#
# S2 is the only thing in this tree that can see an out-of-bounds WRITE by an
# emitted matcher, which is the whole of what sabotage row S155 does (the
# other two capacity guards still return the same typed answer one frame
# later, so no answer-checking cell moves). Its ASan build is a PREFLIGHT, and
# the fallback below runs the two `one-short` arms WITHOUT the sanitizer.
#
# MEASURED: on THIS box that fallback still catches it -- the one-frame overrun
# corrupts the heap and glibc aborts this driver ("double free or corruption
# (!prev)", exit 134), which the `exact_rc -ne 0` arm below scores as a
# failure. But a write one element past a heap region is UNDEFINED BEHAVIOUR,
# so whether anything notices belongs to the ALLOCATOR rather than to the test.
# On a box where the write lands in slack the allocator owns, the three
# verdicts read 1/-3/-3, this section PASSES, and the row would read "ran,
# caught nothing" -- a statement about the CODE, and a FALSE one.
#
# So the caller gets to say that the instrument is REQUIRED. With
# REQUIRE_ASAN=1 a failed preflight is recorded and this script exits 3 --
# distinct from 0 (green) and 1 (a check failed) -- and tests/mech's
# `framebuffer` arm reads that as UNMEASURED, which forces the row to ANOMALY
# rather than letting it read UNDETECTED.
#
# IT DOES NOT SUPPRESS A REAL FAILURE. The script still runs every section and
# still prints its `checks failed:` total, so a sabotage that section 1 or 3
# DOES catch is still caught: the matrix scrapes the totals first and only
# consults the exit status when nothing failed. Default 0 keeps the opt-in
# `make test-frame-buffer` behaviour exactly as it was -- a NOTE and a green
# run on a box with no sanitizer.
REQUIRE_ASAN="${REQUIRE_ASAN:-0}"
asan_unavailable=0

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_frame_buffer.sh: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0; note=0
ok()   { echo "PASS: $*"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $*"; fail=$((fail + 1)); }
info() { echo "NOTE: $*"; note=$((note + 1)); }

# =========================================================================
# SECTION 1
# =========================================================================
# THE ROWS ARE FUNCTION CALLS, NOT A DELIMITED TABLE, and that is not a style
# choice: three of the twelve patterns below contain a `|`, and the first
# version of this section used `|` as its field separator. It silently
# truncated `a(b|c)+d` to `a(b`, `catfish|cat|dog` to `catfish` and
# `^(a|(?1)a)$` to `^(a\`, and the compiles then failed LOUDLY — which is the
# only reason it was caught rather than quietly testing five patterns fewer
# than it claimed. Shell quoting handles what a separator cannot.
s1_ok=1
s1_run=0
s1_want=0

# spread_row <label> <pattern> <flags> <subject>
spread_row() {
    local label="$1" pat="$2" flags="$3" subj="$4"
    local d="$WORKDIR/s1_$label"
    s1_want=$((s1_want + 1))
    mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! "$TIMEOUT_BIN" "$(pcrec_timeout_secs)" "$PCREC" -p rx $flags -o "$d/gen.c" -- "$pat" >/dev/null 2>&1; then
        bad "[DD-14.FB §10.3] could not compile the '$label' fixture '$pat'"
        s1_ok=0; return
    fi
    # shellcheck disable=SC2086
    if ! $CC $GENCFLAGS -I"$d" -o "$d/t" "$ROOT_DIR/tests/harness/driver.c" "$d/gen.c" >"$d/cc.log" 2>&1; then
        bad "[DD-14.FB §10.3] could not build the '$label' driver: $(head -3 "$d/cc.log" | tr '\n' ' ')"
        s1_ok=0; return
    fi
    local a_out b_out a_rc b_rc
    a_out="$("$TIMEOUT_BIN" 30 "$d/t" "$subj" 0 default 2>&1)"; a_rc=$?
    b_out="$("$TIMEOUT_BIN" 30 "$d/t" "$subj" 0 null 2>&1)";    b_rc=$?
    s1_run=$((s1_run + 1))
    if [ "$a_out" != "$b_out" ] || [ "$a_rc" -ne "$b_rc" ]; then
        bad "[DD-14.FB §10.3] '$label' ($pat) DIVERGES between the two routes: <prefix>_search printed '$a_out' (exit $a_rc), <prefix>_search_in(...,NULL) printed '$b_out' (exit $b_rc). §10.3 defines the NULL descriptor to be the SAME CALL, so any difference at all is a defect"
        s1_ok=0
    fi
}

# The give-up subject: a^343 b^343, one past the stamped default's reach.
giveup_subject="$(python3 -c "print('a'*343 + 'b'*343)")"

#           label                pattern              flags                    subject
spread_row 'plain-match'      'a(b|c)+d'            ''                        'abcd'
spread_row 'plain-nomatch'    'a(b|c)+d'            ''                        'abce'
spread_row 'captures'         '(\d+)-(\d+)'         ''                        '12-345'
spread_row 'zero-width'       '(a*)*'               ''                        'bbb'
spread_row 'alt-trie'         'catfish|cat|dog'     ''                        'catfish'
spread_row 'anchored'         '^abc$'               ''                        'abc'
spread_row 'unbounded-vm'     '(a|aa)+b'            '--engine=vm'             'aaaaaaab'
spread_row 'recursion-match'  '^(a(?1)?b)$'         '--features recursion'    'aaabbb'
spread_row 'recursion-giveup' '^(a(?1)?b)$'         '--features recursion'    "$giveup_subject"
spread_row 'leftrec-runaway'  '^(a|(?1)a)$'         '--features recursion'    'aaaaaaaaaab'
spread_row 'kreset'           'a\Kb'                '--features assertions'   'ab'
spread_row 'backref'          '(a+)\1'              '--features backrefs'     'aaaa'

if [ "$s1_run" -lt "$s1_want" ] || [ "$s1_want" -lt 12 ]; then
    bad "[DD-14.FB §10.3] only $s1_run of $s1_want spread rows ran — a section that silently lost rows is not the spread it claims to be"
elif [ "$s1_ok" -eq 1 ]; then
    ok "[DD-14.FB §10.3]: all THREE _in entries agree exactly with their un-suffixed siblings on all $s1_run spread rows — <prefix>_search_in(..., NULL) printed BYTE-IDENTICAL output, and driver.c's cross-check found <prefix>_match_in and <prefix>_match_caps_in (capture spans included) identical to theirs on every row — matches, no-matches, capture spans, a zero-width loop, a \\K entry, a backreference, a give-up and a constant-time runaway refusal, across both engines"
fi

# =========================================================================
# SECTION 2 — exact-fit buffers under ASan
# =========================================================================
# ASan is a PREFLIGHT, not an assumption: if this $CC cannot build it the
# section SKIPS LOUDLY (a NOTE, never a pass), the same shape
# tests/thread/run_thread_tests.sh uses for TSan. Without the sanitizer the
# exact arm would still run and still be worth something — the two `one-short`
# arms are ordinary assertions — but the claim it is here to make, that
# NOTHING writes past either region, needs the instrument.
exact_d="$WORKDIR/exact"
mkdir -p "$exact_d"
printf 'int main(void){return 0;}\n' > "$exact_d/probe.c"
exact_san="-fsanitize=address,undefined"
# shellcheck disable=SC2086
if ! $CC -O0 $exact_san -o "$exact_d/probe" "$exact_d/probe.c" >/dev/null 2>&1; then
    info "[DD-14.FB §2] $CC cannot build with $exact_san — the exact-fit section runs WITHOUT the sanitizer, so its 'nothing writes past either region' claim is NOT made this run"
    exact_san=""
    asan_unavailable=1
fi
if ! "$TIMEOUT_BIN" "$(pcrec_timeout_secs)" "$PCREC" -p rx --features recursion --engine=vm -o "$exact_d/gen.c" -- '^(a(?1)?b)$' >/dev/null 2>&1; then
    bad "[DD-14.FB §2] could not compile the exact-fit fixture"
# shellcheck disable=SC2086
elif ! $CC $GENCFLAGS $exact_san -I"$exact_d" -o "$exact_d/fb" \
        "$SCRIPT_DIR/fb_exact_driver.c" "$exact_d/gen.c" >"$exact_d/cc.log" 2>&1; then
    bad "[DD-14.FB §2] could not build fb_exact_driver.c: $(head -5 "$exact_d/cc.log" | tr '\n' ' ')"
else
    exact_out="$("$TIMEOUT_BIN" 300 "$exact_d/fb" 2>&1)"; exact_rc=$?
    echo "$exact_out" | sed 's/^/      /'
    exact_rows="$(printf '%s\n' "$exact_out" | grep -c '^row ')"
    # FIELDS: row <n> <nframes> <ntrail> <exact> <frame_short> <trail_short>,
    # so the three verdicts are $5/$6/$7. Written as $4/$5/$6 first time round,
    # which made every row read as bad -- caught because the check went RED on
    # a correct build rather than green on a broken one, which is the direction
    # a mis-indexed check is allowed to fail in.
    exact_bad="$(printf '%s\n' "$exact_out" | awk '$1=="row" && !($5==1 && $6==-3 && $7==-3)' | wc -l)"
    if [ "$exact_rc" -ne 0 ]; then
        bad "[DD-14.FB §2] the exact-fit driver exited $exact_rc — under $exact_san a non-zero exit is very likely a sanitizer report, which is exactly the finding this section exists for: $(printf '%s' "$exact_out" | tail -5 | tr '\n' ' ')"
    elif [ "$exact_rows" -lt 5 ]; then
        bad "[DD-14.FB §2] only $exact_rows exact-fit rows ran (want 5)"
    elif [ "$exact_bad" -ne 0 ]; then
        bad "[DD-14.FB §2] $exact_bad exact-fit row(s) did not read 'match, give-up, give-up'. A capacity guard is off by one: an exact-fit buffer that does not match means a guard refuses a match the buffer could hold, and a one-short buffer that DOES match means a guard let a write past the end"
    elif [ -n "$exact_san" ]; then
        ok "[DD-14.FB §2] all $exact_rows exact-fit depths MATCH on buffers with no slack at all, and give up one frame or one trail entry short — under $exact_san, so nothing wrote past either region. The seven capacity sites are exact in BOTH directions, which is the off-by-one a generously sized buffer cannot see either way"
    else
        ok "[DD-14.FB §2] all $exact_rows exact-fit depths MATCH on buffers with no slack, and give up one frame or one trail entry short (NO sanitizer this run — the over-run half is unmeasured)"
    fi
fi

# =========================================================================
# SECTION 3
# =========================================================================
d="$WORKDIR/mmap"
mkdir -p "$d"
if ! "$TIMEOUT_BIN" "$(pcrec_timeout_secs)" "$PCREC" -p rx --features recursion --engine=vm -o "$d/gen.c" -- '^(a(?1)?b)$' >/dev/null 2>&1; then
    bad "[DD-14.FB §3/§10.6] could not compile '^(a(?1)?b)\$' for the reservation example"
# shellcheck disable=SC2086
elif ! $CC $GENCFLAGS -I"$d" -o "$d/fb" "$SCRIPT_DIR/fb_mmap_driver.c" "$d/gen.c" >"$d/cc.log" 2>&1; then
    bad "[DD-14.FB §3/§10.6] could not build fb_mmap_driver.c: $(head -5 "$d/cc.log" | tr '\n' ' ')"
else
    out="$("$TIMEOUT_BIN" 300 "$d/fb" 342 400000 466000 470000 2>&1)"; rc=$?
    if [ "$rc" -eq 2 ]; then
        info "[DD-14.FB §3/§10.6] SKIPPED LOUDLY: this machine would not give a 2 x 64 MB MAP_NORESERVE reservation ($out). Nothing about the worked example is claimed by this run"
    elif [ "$rc" -ne 0 ]; then
        bad "[DD-14.FB §3/§10.6] the reservation driver exited $rc: $out"
    else
        echo "$out" | sed 's/^/      /'
        res_line="$(printf '%s\n' "$out" | grep '^reserve ')"
        r_bytes="$(printf '%s' "$res_line" | awk '{print $2}')"
        r_frames="$(printf '%s' "$res_line" | awk '{print $3}')"
        r_trail="$(printf '%s' "$res_line" | awk '{print $4}')"
        r_rss="$(printf '%s' "$res_line" | awk '{print $5}')"
        fsz="$(sed -n 's/^#define RX_RESUME_FRAME_SIZE //p' "$d/gen.h")"
        tsz="$(sed -n 's/^#define RX_TRAIL_FRAME_SIZE //p' "$d/gen.h")"

        # (a) THE ARITHMETIC THE MACROS EXIST FOR. If the stamped sizes were
        #     wrong the capacity derived from them would be wrong too, and the
        #     reservation would be mis-sized in the caller's own code — which
        #     is sabotage row S-FB6 seen from the caller's side.
        if [ "$r_frames" = "$((r_bytes / fsz))" ] && [ "$r_trail" = "$((r_bytes / tsz))" ]; then
            ok "[DD-14.FB §10.4/§10.6] the caller's own byte->capacity arithmetic off the emitted macros gives $r_frames frames and $r_trail trail entries from $r_bytes bytes per region (frame $fsz B, trail $tsz B)"
        else
            bad "[DD-14.FB §3/§10.6] the reservation's derived capacities ($r_frames / $r_trail) disagree with $r_bytes / RX_*_FRAME_SIZE ($fsz / $tsz)"
        fi

        # (b) MAP_NORESERVE DOES WHAT THE RULING WANTS IT TO. 128 MB reserved,
        #     a couple of MB resident, until touched.
        if [ "${r_rss:-0}" -gt 0 ] && [ "$r_rss" -lt 8192 ]; then
            ok "[DD-14.FB §3/§10.6] 2 x 64 MB of MAP_NORESERVE address space costs ${r_rss} KB of resident memory before any match — the caller reserves for the worst case and pays for the actual one"
        elif [ "${r_rss:-0}" -eq 0 ]; then
            info "[DD-14.FB §3/§10.6] resident-set size unavailable on this machine (/proc/self/statm) — the lazy-commit half of the example is unmeasured here"
        else
            bad "[DD-14.FB §3/§10.6] the untouched reservation is already ${r_rss} KB resident — MAP_NORESERVE is not deferring the commit, and the 'nearly free ceiling' claim does not hold on this machine"
        fi

        # (c) THE 800 KB ROW: the ruling's own target, matched through the
        #     reservation and REFUSED through the un-suffixed entry.
        row800="$(printf '%s\n' "$out" | awk '$1=="row" && $2==400000')"
        r800="$(printf '%s' "$row800" | awk '{print $4}')"
        t800="$(printf '%s' "$row800" | awk '{print $5}')"
        rss800="$(printf '%s' "$row800" | awk '{print $6}')"
        null800="$(printf '%s' "$row800" | awk '{print $7}')"
        # THE RSS IS BOUNDED, NOT MERELY PRINTED. §10.6's claim is not only
        # "it matches" but "it touches about 88 MB of a 128 MB reservation" --
        # the lazy-commit property is the whole reason MAP_NORESERVE is the
        # worked example. A printed number nobody compares is not a check: an
        # artifact that touched the entire reservation, or one whose per-level
        # cost had doubled, would print a different number and still read
        # green. The window is deliberately wide (the arithmetic predicts
        # 400,000 x 2 x 40 + 400,000 x 8.982 x 16 = 89.5 MB, and the design
        # measured 88.6) because this bounds a MAGNITUDE, not a constant:
        # anything under 40 MB means the walk is not reaching the depth it
        # claims, anything over 128 MB means it is outside the reservation.
        fb_rss_lo=40000
        fb_rss_hi=131072
        if [ "$r800" = "1" ] && [ "$null800" = "-3" ] \
           && [ "${rss800:-0}" -ge "$fb_rss_lo" ] && [ "${rss800:-0}" -le "$fb_rss_hi" ]; then
            ok "[DD-14.FB §3/§10.6] an 800,000-byte subject MATCHES through <prefix>_search_in in ${t800}s having touched ${rss800} KB (within [$fb_rss_lo, $fb_rss_hi] KB, the lazily-committed share of a 128 MB reservation), and the SAME artifact returns PCREC_ERR_FRAMES on it through <prefix>_search — D71 item 2's 'PCRE2-depth recursion with pcrec still never allocating', met"
        elif [ "$r800" = "1" ] && [ "$null800" = "-3" ]; then
            bad "[DD-14.FB §3/§10.6] the 800 KB subject matches and is refused through the un-suffixed entry as it should, but it touched ${rss800:-?} KB, outside [$fb_rss_lo, $fb_rss_hi]. Below the floor the walk is not reaching the depth it claims; above the ceiling it is outside the reservation it was given"
        else
            bad "[DD-14.FB §3/§10.6] the 800 KB row reads _in=$r800 un-suffixed=$null800 (want 1 and -3): '$row800'"
        fi

        # (d) THE CEILING IS PREDICTABLE, which is the property that lets a
        #     caller SIZE a reservation instead of guessing at one.
        r466="$(printf '%s\n' "$out" | awk '$1=="row" && $2==466000 {print $4}')"
        r470="$(printf '%s\n' "$out" | awk '$1=="row" && $2==470000 {print $4}')"
        if [ "$r466" = "1" ] && [ "$r470" = "-3" ]; then
            ok "[DD-14.FB §3/§10.6] the ceiling sits between n=466,000 and n=470,000, which is where ntrail / 8.98 trail entries per level predicts it ($((r_trail / 9)) levels) — a caller CAN size a reservation from the emitted numbers"
        else
            bad "[DD-14.FB §3/§10.6] the ceiling moved: n=466,000 gives $r466 (want 1) and n=470,000 gives $r470 (want -3). The trail-per-level ratio the spec's sizing advice rests on has changed"
        fi

        # (e) THE ROW THE SPEC OVERSTATES. §10.6 says "with the same artifact
        #     returning PCREC_ERR_FRAMES on every one of those subjects
        #     through rx_search" — but its own first row is 684 B, and §10.1
        #     says the artifact MATCHES up to 684 B. The two sentences cannot
        #     both be true. Reported rather than encoded: a check that asserted
        #     the spec's blanket claim would be asserting a contradiction.
        null342="$(printf '%s\n' "$out" | awk '$1=="row" && $2==342 {print $7}')"
        if [ "$null342" = "1" ]; then
            info "[DD-14.FB] SPEC FINDING (§10.6 vs §10.1): the 684-byte row's un-suffixed control returns 1 (a MATCH), not PCREC_ERR_FRAMES. §10.6's closing sentence claims the un-suffixed entry refuses 'every one of those subjects', but 684 B is exactly the largest subject §10.1 says it MATCHES. The claim holds for the four LARGER rows and not for the first; the same overstatement is in docs/design/frame_buffer_design.md §8"
        elif [ "$null342" = "-3" ]; then
            bad "[DD-14.FB] the 684-byte subject no longer matches through <prefix>_search. §10.1's measured give-up boundary (matches at 684 B, refuses at 686 B) has moved, and D73's release-note numbers with it"
        else
            # NEITHER 1 NOR -3 means the row is MISSING or MALFORMED, and
            # without this arm that read as silence: the two arms above fired
            # nothing and the section still summed green. A check whose
            # evidence went missing must say so, not fall through.
            bad "[DD-14.FB] no usable n=342 row in the reservation driver's output (got '${null342:-<none>}' for the un-suffixed control). The spec-consistency check above measured NOTHING this run, and a missing row is not a pass"
        fi
    fi
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "notes: $note"
if [ $((pass + fail)) -eq 0 ]; then
    echo "run_frame_buffer.sh: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -ne 0 ] && exit 1
# A REAL FAILURE OUTRANKS A MISSING INSTRUMENT (see REQUIRE_ASAN above): the
# exit-1 above comes first, so a caller that required the sanitizer and got a
# genuine red still reads a genuine red.
if [ "$REQUIRE_ASAN" = "1" ] && [ "$asan_unavailable" = "1" ]; then
    echo "UNMEASURED: REQUIRE_ASAN=1 and $CC cannot build with -fsanitize=address,undefined." >&2
    echo "UNMEASURED: section 2 is the only instrument here that can see an out-of-bounds WRITE," >&2
    echo "UNMEASURED: so 'zero checks failed' this run is the ABSENCE of a measurement, not a result." >&2
    exit 3
fi
exit 0
