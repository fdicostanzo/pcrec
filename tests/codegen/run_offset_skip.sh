#!/usr/bin/env bash
# tests/codegen/run_offset_skip.sh — [OPT-K]: the OFFSET-k CANDIDATE-START
# SKIP, held to the ARTIFACT rather than to its stamp.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `docs/design/offset_k_skip.md`. A DFA scan's candidate-start filter used to
# look only at offset 0. It may now derive, from the pattern's own prefix, a
# SET of `(offset k, byte-set)` tests every match must satisfy, scan for the
# rarest member with one `memchr` AT ITS OFFSET, verify the others on each
# candidate, and resume from a failed candidate one position later:
#
#     static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos, ...)
#     {
#         while (pos + 13 < n) {
#             size_t cand;
#             const void *q = memchr(subject + pos + 8, 45, n - pos - 8);
#             if (!q) return n;
#             cand = (size_t)((const unsigned char *)q - subject) - 8;
#             if (cand + 13 >= n) return n;
#             if (rx_ofs_k0[subject[cand]] && subject[cand + 13] == 45) return cand;
#             pos = cand + 1;
#         }
#         return n;
#     }
#
# MEASURED on 1 MB of the comparative bench's own log text, 9 interleaved
# trials per arm: `uuid` 4.5-5.1x, `iso-ts` 4.8-6.9x, `stack-frame` 7.2-11.6x,
# `needleXYZW` 17.1x. `-fno-offset-skip` (docs/spec/tuning.md §2.14) denies it.
#
# =========================================================================
# WHY EACH CHECK EXISTS, AND WHAT NO OTHER CHECK IN THE TREE SEES
# =========================================================================
# THE MECHANISM IS ANSWER-IDENTITY-PRESERVING BY CONSTRUCTION, which is
# exactly why it needs structural checks: the whole `.rxt` corpus, both
# oracles, `make test-axes` and every differential agree whether or not the
# emitter selected the form at all. Five failure modes, none of which an
# answer comparison can reach:
#
#   (i)   THE FORM SILENTLY STOPS BEING SELECTED. Every answer stays right and
#         the row's whole 4x-17x evaporates. Nothing else in the tree counts
#         the population; §2 names the patterns and requires the form.
#   (ii)  THE FORM IS SELECTED WHERE IT WAS MEASURED NOT TO PAY. The
#         selection requires the scan offset to MOVE off 0, because a verify
#         removes loop ENTRIES while a scan removes BYTES — measured 0.96x-1.02x
#         on `bignum` against a model prediction of 13x. §3 names the declines,
#         including the three bench CONTROLS and the two email patterns
#         (the derivation-domain control).
#   (iii) THE SCAN OFFSET AND THE STAMP DRIFT APART. The stamp is a string the
#         emitter prints; the offsets are arithmetic inside a helper. §2 reads
#         BOTH against a THIRD source (the literal table below) so neither can
#         be checked against the other alone.
#   (iv)  THE PRIOR STOPS SUMMING TO ONE. The cost model reads
#         `pcrec_byte_freq_ppm` as a probability; a table that summed to 1.13
#         (which the first draft's did) makes "the whole alphabet" cost
#         something other than one candidate per byte and silently re-ranks
#         every offset. No artifact shows it. §1 links the shipped library and
#         asks the shipped array.
#   (v)   THE DENIAL LEAVES A TRACE. `-fno-offset-skip` must put the artifact
#         back to the four older forms; §4 asserts the helper is gone and the
#         stamp says so.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3. The obvious wrong version of this check reads
# `RX_DFA_PREFILTER_OFFSETS` and re-parses it into the offsets it asserts:
# that asserts the emitter can print. So the expected k-set for every witness
# is a LITERAL in the table below, taken from the design note's §4.7, and BOTH
# the stamp AND the emitted helper text are compared against it. The three
# come out of three write sites — `dfa_prefilter_offsets` writes the macro,
# `pf_block_ofs` writes the helper, and this file's table is a human reading
# of the note — so any two of them drifting is RED.
#
# THE PATTERNS ARE THE SAME ONES `tests/offsetskip/offset_skip.rxt` USES, on
# purpose and stated in both files: that corpus checks the emitted skip's
# ARITHMETIC and would pass just as well on a pattern that got no skip at all,
# so it needs this file to say the mechanism was reached. A corpus that
# silently stopped exercising its mechanism is [MECH-REACH]'s failure and this
# project's most-recorded check defect.
#
# =========================================================================
# VALIDATION (the check was made to fail on purpose before it shipped)
# =========================================================================
# Recorded 2026-08-28, lane optk. Each plant made in the named source, rebuilt,
# this script run, and reverted. The clean baseline is in the file's own run.
# See the VALIDATION RECORD at the bottom of this file for the measured
# pass/fail counts.
#
# Usage: bash tests/codegen/run_offset_skip.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc / gen_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "offset-skip: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: offset-skip: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# THE DOCUMENTED VALUE SET, spelled here so this file states the contract it
# checks rather than accepting whatever the emitter says
# (docs/spec/match_api.md §6.3). A new value needs a spec hunk and a line
# here, in the same change.
OFS_VALUES="offset-set offset-set-bounded"

# THE CAP, spelled here as a SECOND source. `PCREC_OFSK_MAX_SET` in
# src/core/internal.h is the first; a check that read the compiler's own
# constant could not see it move.
OFSK_MAX_SET=4

emit() { # emit <name> <pattern> [extra pcrec args...]
    local name="$1" pat="$2"
    shift 2
    pcrec_run "$PCREC" -p rx --no-captures --features all "$@" \
        -o "$WORKDIR/$name.c" -- "$pat" >/dev/null 2>&1
}

stamp() { grep -m1 "^#define RX_DFA_PREFILTER \"" "$1" | awk '{print $3}' | tr -d '"'; }
offs()  { grep -m1 "^#define RX_DFA_PREFILTER_OFFSETS \"" "$1" | awk '{print $3}' | tr -d '"'; }

# =========================================================================
# §1 THE PRIOR SUMS TO EXACTLY 1,000,000
# =========================================================================
# Asked of the SHIPPED ARRAY through the SHIPPED LIBRARY, not of the source
# text: a python re-implementation summing the literals in prefix_k.c would be
# a second transcription of the table and would agree with any typo it shared.
# `pcrec_byte_freq_total_ppm` walks the same array the selection reads.
cat > "$WORKDIR/prior.c" <<'EOF'
#include <stdio.h>
#include "core/internal.h"
int main(void)
{
    unsigned t = pcrec_byte_freq_total_ppm();
    unsigned zero = 0, b;
    for (b = 0; b < 256; b++) if (pcrec_byte_freq_ppm((int)b) == 0) zero++;
    printf("%u %u\n", t, zero);
    return 0;
}
EOF
if gen_cc "offset-skip prior probe" "$CC" -O0 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$WORKDIR/prior" "$WORKDIR/prior.c" "$ROOT_DIR/build/libpcrec.a" 2>"$WORKDIR/prior.log"; then
    read -r ptotal pzero < <("$WORKDIR/prior")
    if [ "$ptotal" = "1000000" ]; then
        ok "§1 the byte-frequency prior sums to exactly 1,000,000 ppm"
    else
        bad "§1 the byte-frequency prior sums to $ptotal ppm, not 1,000,000 — the cost model reads it as a probability, so every offset's rank is computed against the wrong denominator (src/opt/prefix_k.c, docs/design/offset_k_skip.md §4.1)"
    fi
    # THE FLOOR IS PART OF THE CONTRACT, not tidiness: a zero would let the
    # model believe a byte is IMPOSSIBLE and choose a skip on a certainty it
    # does not have.
    if [ "$pzero" = "0" ]; then
        ok "§1 no byte in the prior has zero mass (the floor holds on all 256)"
    else
        bad "§1 $pzero bytes have ZERO mass in the prior — the model would treat them as impossible, which is a certainty the static table does not have (docs/design/offset_k_skip.md §4.1)"
    fi
else
    bad "§1 could not build the prior probe against build/libpcrec.a: $(head -3 "$WORKDIR/prior.log")"
fi

# =========================================================================
# §2 THE WITNESSES: the form is SELECTED, and its arithmetic is what it says
# =========================================================================
# Columns: label | pattern | expected stamp | expected _OFFSETS | scan offset |
#          scan byte (decimal) | maxk
# Every value is a LITERAL from docs/design/offset_k_skip.md §4.7, never read
# back out of the artifact.
witness() { # witness <label> <pattern> <stamp> <offsets> <k*> <byte> <maxk>
    local lbl="$1" pat="$2" xs="$3" xo="$4" ks="$5" by="$6" mk="$7"
    local f="$WORKDIR/w.c"
    emit w "$pat" || { bad "§2 [$lbl] '$pat' did not compile"; return; }

    local gs go
    gs="$(stamp "$f")"; go="$(offs "$f")"
    case " $OFS_VALUES " in *" $gs "*) ;; *)
        bad "§2 [$lbl] '$pat' stamps RX_DFA_PREFILTER \"$gs\", which is not one of the offset-set values ($OFS_VALUES) — the offset-k form was NOT selected, so the row's measured 4x-17x is gone and nothing else in the tree would notice"
        return ;;
    esac
    [ "$gs" = "$xs" ] || bad "§2 [$lbl] stamps \"$gs\", expected \"$xs\" (the -bounded half is the D11 clamp and is a different emitted body, not a label)"
    [ "$go" = "$xo" ] || bad "§2 [$lbl] stamps offsets \"$go\", expected \"$xo\""

    # --- and now the same facts read out of the EMITTED HELPER --------------
    local blk
    blk="$(sed -n '/^static inline size_t rx_ofsskip(/,/^}$/p' "$f")"
    if [ -z "$blk" ]; then
        bad "§2 [$lbl] stamps an offset-set value but emits NO rx_ofsskip block — the stamp and the mechanism have come apart, which is the drift this file exists to catch"
        return
    fi
    # the SCAN: one memchr, at the declared offset, for the declared byte
    if [ "$ks" = "0" ]; then
        printf '%s\n' "$blk" | grep -qE "memchr\(subject \+ pos, $by, n - pos\)" \
            || bad "§2 [$lbl] the helper does not memchr for byte $by at offset 0"
    else
        printf '%s\n' "$blk" | grep -qE "memchr\(subject \+ pos \+ $ks, $by, n - pos - $ks\)" \
            || bad "§2 [$lbl] the helper does not memchr for byte $by at offset $ks — the scan offset the stamp declares and the one the code searches at disagree"
    fi
    # the hit -> start MAPPING: cand = hit - k*
    if [ "$ks" = "0" ]; then
        printf '%s\n' "$blk" | grep -qE "cand = \(size_t\)\(\(const unsigned char \*\)q - subject\);" \
            || bad "§2 [$lbl] the helper does not map the hit to a candidate start at offset 0"
    else
        printf '%s\n' "$blk" | grep -qE "cand = \(size_t\)\(\(const unsigned char \*\)q - subject\) - $ks;" \
            || bad "§2 [$lbl] the helper does not compute cand = hit - $ks"
    fi
    # the END guard, on maxk
    printf '%s\n' "$blk" | grep -qE "if \(cand \+ $mk >= n\) return n;" \
        || bad "§2 [$lbl] the helper has no 'cand + $mk >= n' guard — a candidate without maxk+1 bytes left would be read past the subject"
    printf '%s\n' "$blk" | grep -qE "while \(pos \+ $mk < n\)" \
        || bad "§2 [$lbl] the helper's loop is not bounded at 'pos + $mk < n', which is also what keeps memchr off a NULL subject (K27's class)"
    # the RESUME, and it is the off-by-one a sabotage row plants
    printf '%s\n' "$blk" | grep -qE "^ +pos = cand \+ 1;$" \
        || bad "§2 [$lbl] the helper does not resume at 'cand + 1' — resuming further along skips any real match closer than k* to a failed candidate"
    # the VERIFY CHAIN has exactly (members - 1) terms
    local want_terms got_terms
    want_terms=$(( $(printf '%s' "$xo" | awk -F, '{print NF}') - 1 ))
    got_terms=$(printf '%s\n' "$blk" | grep -cE 'subject\[cand( \+ [0-9]+)?\]')
    # the scan's own line does not read subject[cand], so every match is a verify
    if [ "$got_terms" = "$want_terms" ]; then
        ok "§2 [$lbl] '$pat': $gs $go — memchr $by at offset $ks, cand = hit - $ks, $want_terms verify term(s), maxk $mk, resume at cand+1"
    else
        bad "§2 [$lbl] the helper reads subject[cand...] $got_terms time(s), expected $want_terms (one per selected offset except the scan)"
    fi
    # the cap
    local nmem
    nmem=$(printf '%s' "$xo" | awk -F, '{print NF}')
    [ "$nmem" -le "$OFSK_MAX_SET" ] \
        || bad "§2 [$lbl] the k-set has $nmem members, above the cap $OFSK_MAX_SET"
}

#        label          pattern                                   stamp                offsets    k*  byte maxk
witness "iso-ts"       '\d{4}-\d{2}-\d{2}'                        offset-set           '0,4*'      4   45   4
witness "uuid"         '\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b'  offset-set-bounded '0,8*,13' 8 45 13
witness "stack-frame"  '\bat [a-z]'                               offset-set-bounded   '0,1*'      1  116   1
witness "needleXYZW"   'needleXYZW'                               offset-set           '0,6*'      6   88   6

# =========================================================================
# §2b THE RESEED — the one place a wrong answer is reachable
# =========================================================================
# `\b`'s truth reads the byte to the LEFT and pcrec carries that in the DFA
# state's IDENTITY, so the start state escapes on EVERY word character (the
# note's §2.1). This skip jumps over exactly those bytes, so it must put the
# state back from `s[cand-1]` on landing; without it the machine evaluates
# `\b` as true after a word character and MATCHES. `tests/offsetskip/`'s §6
# has the answer cells; this is the emitted line they depend on.
if emit reseed '\b[0-9]{2}-[0-9]{2}'; then
    if grep -qE 'forward_state = scan_position \? rx_forward_seed_state\[rx_forward_byte_class\[subject\[scan_position - 1\]\]\] : [0-9]+;' "$WORKDIR/reseed.c"; then
        ok "§2b a seeded machine re-seeds forward_state from s[cand-1] after the skip lands"
    else
        bad "§2b '\\b[0-9]{2}-[0-9]{2}' takes the offset-k skip but does NOT re-seed the state on landing — the skip jumps over the word characters that were carrying \\b's left-hand context, so the machine would evaluate \\b in the no-context start state and match after a word character (docs/design/offset_k_skip.md §5.4)"
    fi
    # ...and the SEED TABLE it reads has to be there
    grep -qE 'rx_forward_seed_state\[' "$WORKDIR/reseed.c" \
        && ok "§2b the seed table the reseed reads is emitted" \
        || bad "§2b the reseed reads rx_forward_seed_state[] but no such table is emitted"
fi

# =========================================================================
# §2c MISCOMPILE-1's OWN CHECK: the offset-0 verify is NOT `can_begin_match`
# =========================================================================
# `can_begin_match` is the DFA start state's ESCAPE set — "does this byte move
# the machine off `fs`" — which is the right question for the SCAN that walks
# it and the WRONG one for a VERIFY that refuses a candidate START. The skip
# lands past bytes it jumped over, so the parked state there may be a seeded
# `s1u[UPC_WORD]`, and a byte that cannot begin a match from `fs` can begin one
# from there.
#
# MEASURED before the fix: `\b\.[0-9]{4}Z` has `can_begin_match` = exactly the
# 63 word bytes with `.` EXCLUDED, and `.` is the only byte a match can start
# with — "ab.1234Z" answered NOMATCH against a baseline and python3 `re` of
# (2,8). The corpus rows are in tests/offsetskip §8; this is the emitted line
# they depend on, and the two are named in each other.
if emit mc1 '\b\.[0-9]{4}Z'; then
    blk="$(sed -n '/^static inline size_t rx_ofsskip(/,/^}$/p' "$WORKDIR/mc1.c")"
    if printf '%s\n' "$blk" | grep -q 'rx_can_begin_match'; then
        bad "§2c the offset-k skip helper reads rx_can_begin_match — that is the ESCAPE set (does this byte leave the start state), not the CAN-BEGIN-A-MATCH set, and using it as a verify LOSES MATCHES on every pattern with a leading assertion (MISCOMPILE-1: '\b\.[0-9]{4}Z' on \"ab.1234Z\" answered nomatch against a baseline of (2,8))"
    else
        ok "§2c the offset-k skip helper does not read can_begin_match (MISCOMPILE-1)"
    fi
    # THE SHARPEST FORM THE WITNESS CAN TAKE: the byte the old set EXCLUDED is
    # the only byte the corrected verify ACCEPTS. `.` is not a word character,
    # so it is absent from the escape set; it is the pattern's whole offset-0
    # class, so the corrected verify is `subject[cand] == 46`.
    if printf '%s\n' "$blk" | grep -qE 'subject\[cand\] == 46'; then
        ok "§2c ...and requires '.' (46) at offset 0 — the byte the escape set EXCLUDES"
    else
        bad "§2c the helper does not test subject[cand] == 46 on '\b\.[0-9]{4}Z'. '.' is the only byte a match can begin with here AND is absent from can_begin_match, so this is the one line that separates the two sets"
    fi
fi

# THE VACUITY GUARD, and it needs a SECOND BUILD rather than a second read.
# The corrected form no longer emits `can_begin_match` at all, so there is
# nothing in the artifact to compare against — and "the table is not the other
# table" is worth nothing if the two would have been equal anyway. The
# `-fno-offset-skip` build of the SAME pattern emits the byte-class form and
# therefore the escape set, so the two tables come from two builds and two
# emitter paths. On `uuid` they must DIFFER: 16 hex bytes against 63 word ones.
if emit v1 '\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b' \
   && emit v2 '\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b' -fno-offset-skip; then
    a="$(sed -n '/rx_ofs_k0\[256\]/,/};/p' "$WORKDIR/v1.c" | tr -cd '0-9,')"
    b="$(sed -n '/rx_can_begin_match\[256\]/,/};/p' "$WORKDIR/v2.c" | tr -cd '0-9,')"
    na=$(printf '%s' "$a" | tr ',' '\n' | grep -c '^1$')
    nb=$(printf '%s' "$b" | tr ',' '\n' | grep -c '^1$')
    if [ -z "$a" ] || [ -z "$b" ]; then
        bad "§2c could not read both offset-0 tables on the uuid witness (ofs_k0 from the default build, can_begin_match from the -fno-offset-skip one) — the guard cannot say whether the two sets differ"
    elif [ "$a" = "$b" ]; then
        bad "§2c the corrected offset-0 verify table is IDENTICAL to the escape set on the uuid witness ($na bytes each) — either the fix has been undone or the witness has stopped distinguishing the two sets, and every row above asserts nothing"
    else
        ok "§2c the offset-0 verify ($na bytes) and the escape set ($nb bytes) genuinely differ on the uuid witness — the MISCOMPILE-1 rows are not vacuous"
    fi
fi

# =========================================================================
# §3 THE DECLINES — the population the form must NOT reach
# =========================================================================
# Three of these are the comparative bench's own CONTROLS (patterns pcrec is
# already ahead of PCRE2-JIT on) and two are its derivation-domain control
# (the email specimen, whose `+`-smeared prefix puts `@` at no fixed offset).
# The other two are the measured (ii) above: the scan does not move off 0, and
# the form was measured a wash.
decline() { # decline <label> <pattern> <why>
    local lbl="$1" pat="$2" why="$3"
    emit d "$pat" || { bad "§3 [$lbl] '$pat' did not compile"; return; }
    local gs go
    gs="$(stamp "$WORKDIR/d.c")"; go="$(offs "$WORKDIR/d.c")"
    if [ "$go" = "none" ] && ! grep -q 'rx_ofsskip' "$WORKDIR/d.c"; then
        ok "§3 [$lbl] declines the offset-k form ($gs) — $why"
    else
        bad "§3 [$lbl] '$pat' now SELECTS the offset-k form ($gs $go) — $why. If that is intended, it needs a measurement on this row before the line moves, not after"
    fi
}
decline "hex32-id"    '\b[0-9a-f]{32}\b' \
    "every offset is the same 16-byte hex class; pcrec is 1.14x AHEAD of the JIT here and two coin-flip verify branches on 80% of positions is how that is lost"
decline "ipv4"        '(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])' \
    "unequal-width alternation puts the '.' at a variable offset; 3.56x ahead"
decline "http-5xx"    '"(?:GET|POST|PUT|PATCH|DELETE|HEAD) [^ "]+ HTTP/1\.[01]" 5[0-9]{2}\b' \
    "its offset-0 byte is already '\"' at 0.3%; 15.0x ahead"
decline "bignum"      '\b[0-9]{10,19}\b' \
    "the scan would stay at offset 0 (a bitmap walk), which MEASURED 0.96x-1.02x against a model prediction of 13x"
decline "dense"       '[01]*1[01]{8}' \
    "the scan would stay at offset 0; MEASURED 0.97x, and run_codegen_tests.sh's M2.12 ordering pin is about this pattern"
decline "email-orig"  "(?:[a-z0-9!#\$%&'*+/=?^_\`{|}~-]+(?:\\.[a-z0-9!#\$%&'*+/=?^_\`{|}~-]+)*)@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?" \
    "the '+'-smeared prefix leaves no fixed offset at all — the DERIVATION-DOMAIN control"
decline "one byte"    ':' \
    "a one-byte pattern has no offset 1 to select"

# =========================================================================
# §4 THE DENIAL LEAVES NO TRACE
# =========================================================================
# `-fno-offset-skip` filters the two candidates out of the list, so the
# artifact must be what the four older forms produce. The one thing it does
# NOT put back is the `_DFA_PREFILTER_OFFSETS` line, which every `abi` 9
# artifact carries unconditionally (D81: a selection fact is stamped whether
# or not it fired) — so the denied build differs from the pre-[OPT-K]
# compiler's output by exactly that line, and §5 of the design note says so.
for pat in '\d{4}-\d{2}-\d{2}' '\b[0-9a-f]{8}-[0-9a-f]{4}' 'needleXYZW'; do
    if emit off "$pat" -fno-offset-skip; then
        gs="$(stamp "$WORKDIR/off.c")"; go="$(offs "$WORKDIR/off.c")"
        if [ "$go" = "none" ] && ! grep -q 'rx_ofsskip' "$WORKDIR/off.c"; then
            ok "§4 -fno-offset-skip on '$pat' emits no skip helper and stamps \"$gs\" / \"none\""
        else
            bad "§4 -fno-offset-skip on '$pat' STILL emits the offset-k form ($gs $go) — the deny flag is not filtering the candidate list, so the axis has no control and its identity gate is comparing a build against itself"
        fi
    else
        bad "§4 '$pat' did not compile under -fno-offset-skip"
    fi
done

# ...and it must not be a blanket off-switch for the whole prefilter axis:
# a pattern that never had an offset-k form must be UNCHANGED by the flag.
#
# THE COMPARISON SKIPS THE ARTIFACT'S OWN `#include "<name>.h"` LINE, and it
# does so BY CONTENT rather than by line NUMBER. The two builds go to `p1.c`
# and `p2.c`, so each includes its own header and that one line differs for a
# reason that has nothing to do with the flag. This read `tail -n +8` — the
# preamble's length on the day it was written — and [K50] broke it by adding a
# `<PREFIX>_STARTPOS_GUARD` selection stamp to the SHARED prologue: the
# `#include` moved to line 8, stopped being skipped, and this check went red on
# a pair of artifacts that are byte-identical everywhere the flag could reach.
# A line count is a pin on every stamp anyone adds later; dropping the include
# by its own shape is the same claim without that coupling.
drop_own_header() { grep -v '^#include "' "$1"; }
if emit p1 '\b[0-9a-f]{32}\b' && emit p2 '\b[0-9a-f]{32}\b' -fno-offset-skip; then
    if cmp -s <(drop_own_header "$WORKDIR/p1.c") <(drop_own_header "$WORKDIR/p2.c"); then
        ok "§4 a DECLINED pattern is byte-identical across the flag (the flag denies this axis and nothing else)"
    else
        bad "§4 '\\b[0-9a-f]{32}\\b' is not byte-identical across -fno-offset-skip, and it selects no offset-k form either way — the flag is reaching something that is not its axis"
    fi
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1

# =========================================================================
# VALIDATION RECORD — MEASURED, 2026-08-28, lane optk
# =========================================================================
# Each plant made in the named source, rebuilt, this script AND
# `tests/harness/run.sh tests/offsetskip/offset_skip.rxt` run, then reverted.
# **CLEAN BASELINE: this file 19 passed / 0 failed; the corpus 80 / 0.**
# Logs: scratchpad/optk/plants{,2,3}.log.
#
#   PLANT 1 -- THE RESUME OFF BY ONE. `pf_block_ofs` emits
#     `pos = cand + 1 + <k*>;` instead of `pos = cand + 1;`.
#     **MEASURED: this file 19 passed / 4 FAILED (§2's resume arm on all four
#     witnesses); the corpus 79 / 1.**
#
#     AND THE CORPUS ARM IS ONLY 1 BECAUSE A ROW WAS ADDED AFTER THIS PLANT
#     MEASURED ZERO, which is the most transferable thing in this record. The
#     first run of this plant left the corpus 75/75 GREEN: its four
#     overlapping-candidate blocks EXERCISE the resume line and cannot DETECT
#     a change to it. The plant loses a match only when a real start `p` lies
#     in `(cand, cand + k*]`, which puts the failed candidate's own scan byte
#     at match offset `h - p < k*` — so the pattern must ALLOW its scan byte
#     BEFORE the offset it is scanned at, and none of `uuid`, `iso-ts`,
#     `stack-frame` or `needleXYZW` can (hex, digits, `a`, `needle`). The
#     corpus gained `[-a]{3}-b`, which scans `-` at offset 3 and permits `-`
#     at 0-2, and the row that fires is `m "zaa--b" 1 6`.
#
#   PLANT 2 -- THE RESEED DELETED. `pf_emit_ofs_reseed` returns immediately.
#     **MEASURED: this file 18 / 1 (§2b alone); the corpus 79 / 1** — and the
#     corpus row is a FALSE MATCH, the worst direction: a subject whose only
#     difference from a matching one is a leading word character starts
#     matching. Nothing in §2, §3 or §4 moves, which is the check localising
#     rather than going uniformly red.
#
#   PLANT 3 -- THE SELECTION NEVER FIRES (`pcrec_prefix_ksets` returns before
#     publishing). **MEASURED: this file 14 / 5 — §2's four witnesses and
#     §4's byte-identity-across-the-flag row — and THE CORPUS 80 / 0, GREEN.**
#     That green is the whole reason this file exists: every answer in the
#     tree stays right, `make test-axes` stays green (its claim is that the
#     denied and default builds AGREE, and with the selection gone they are
#     the same build), and the row's measured 4.5x-17.1x is simply gone.
#     §4's row going red is worth reading too — with nothing to deny, the
#     axis's own control is comparing a build against itself.
#
#   PLANT 4 -- THE PRIOR NO LONGER SUMS TO ONE (one entry moved
#     124561 -> 134561). **MEASURED: this file 18 / 1 (§1 alone); the corpus
#     80 / 0.** No artifact and no answer moves; the cost model silently
#     re-ranks every offset against the wrong denominator.
