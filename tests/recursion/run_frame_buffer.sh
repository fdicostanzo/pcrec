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
# SECTION 2 — the mmap'd, lazily-committed reservation, RUN
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

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O2 -std=gnu11 -Wall -Wextra -Werror}"

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
    if ! "$PCREC" -p rx $flags -o "$d/gen.c" -- "$pat" >/dev/null 2>&1; then
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
    ok "[DD-14.FB §10.3]: <prefix>_search_in(..., NULL) printed BYTE-IDENTICAL output to <prefix>_search on all $s1_run spread rows — matches, no-matches, capture spans, a zero-width loop, a \\K entry, a backreference, a give-up and a constant-time runaway refusal, across both engines"
fi

# =========================================================================
# SECTION 2
# =========================================================================
d="$WORKDIR/mmap"
mkdir -p "$d"
if ! "$PCREC" -p rx --features recursion --engine=vm -o "$d/gen.c" -- '^(a(?1)?b)$' >/dev/null 2>&1; then
    bad "[DD-14.FB §10.6] could not compile '^(a(?1)?b)\$' for the reservation example"
# shellcheck disable=SC2086
elif ! $CC $GENCFLAGS -I"$d" -o "$d/fb" "$SCRIPT_DIR/fb_mmap_driver.c" "$d/gen.c" >"$d/cc.log" 2>&1; then
    bad "[DD-14.FB §10.6] could not build fb_mmap_driver.c: $(head -5 "$d/cc.log" | tr '\n' ' ')"
else
    out="$("$TIMEOUT_BIN" 300 "$d/fb" 342 400000 466000 470000 2>&1)"; rc=$?
    if [ "$rc" -eq 2 ]; then
        info "[DD-14.FB §10.6] SKIPPED LOUDLY: this machine would not give a 2 x 64 MB MAP_NORESERVE reservation ($out). Nothing about the worked example is claimed by this run"
    elif [ "$rc" -ne 0 ]; then
        bad "[DD-14.FB §10.6] the reservation driver exited $rc: $out"
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
            bad "[DD-14.FB §10.6] the reservation's derived capacities ($r_frames / $r_trail) disagree with $r_bytes / RX_*_FRAME_SIZE ($fsz / $tsz)"
        fi

        # (b) MAP_NORESERVE DOES WHAT THE RULING WANTS IT TO. 128 MB reserved,
        #     a couple of MB resident, until touched.
        if [ "${r_rss:-0}" -gt 0 ] && [ "$r_rss" -lt 8192 ]; then
            ok "[DD-14.FB §10.6] 2 x 64 MB of MAP_NORESERVE address space costs ${r_rss} KB of resident memory before any match — the caller reserves for the worst case and pays for the actual one"
        elif [ "${r_rss:-0}" -eq 0 ]; then
            info "[DD-14.FB §10.6] resident-set size unavailable on this machine (/proc/self/statm) — the lazy-commit half of the example is unmeasured here"
        else
            bad "[DD-14.FB §10.6] the untouched reservation is already ${r_rss} KB resident — MAP_NORESERVE is not deferring the commit, and the 'nearly free ceiling' claim does not hold on this machine"
        fi

        # (c) THE 800 KB ROW: the ruling's own target, matched through the
        #     reservation and REFUSED through the un-suffixed entry.
        row800="$(printf '%s\n' "$out" | awk '$1=="row" && $2==400000')"
        r800="$(printf '%s' "$row800" | awk '{print $4}')"
        t800="$(printf '%s' "$row800" | awk '{print $5}')"
        rss800="$(printf '%s' "$row800" | awk '{print $6}')"
        null800="$(printf '%s' "$row800" | awk '{print $7}')"
        if [ "$r800" = "1" ] && [ "$null800" = "-3" ]; then
            ok "[DD-14.FB §10.6] an 800,000-byte subject MATCHES through <prefix>_search_in in ${t800}s having touched ${rss800} KB, and the SAME artifact returns PCREC_ERR_FRAMES on it through <prefix>_search — D71 item 2's 'PCRE2-depth recursion with pcrec still never allocating', met"
        else
            bad "[DD-14.FB §10.6] the 800 KB row reads _in=$r800 un-suffixed=$null800 (want 1 and -3): '$row800'"
        fi

        # (d) THE CEILING IS PREDICTABLE, which is the property that lets a
        #     caller SIZE a reservation instead of guessing at one.
        r466="$(printf '%s\n' "$out" | awk '$1=="row" && $2==466000 {print $4}')"
        r470="$(printf '%s\n' "$out" | awk '$1=="row" && $2==470000 {print $4}')"
        if [ "$r466" = "1" ] && [ "$r470" = "-3" ]; then
            ok "[DD-14.FB §10.6] the ceiling sits between n=466,000 and n=470,000, which is where ntrail / 8.98 trail entries per level predicts it ($((r_trail / 9)) levels) — a caller CAN size a reservation from the emitted numbers"
        else
            bad "[DD-14.FB §10.6] the ceiling moved: n=466,000 gives $r466 (want 1) and n=470,000 gives $r470 (want -3). The trail-per-level ratio the spec's sizing advice rests on has changed"
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
[ "$fail" -eq 0 ] && exit 0
exit 1
