#!/usr/bin/env bash
# tests/utf8/run_startbnd_diff.sh — [K50]'s CALLER-STARTPOS DIFFERENTIAL, the
# primary instrument for the `-fno-startpos-guard` axis (docs/spec/tuning.md
# §2.23, docs/spec/match_api.md §3.1, docs/dev/known_issues.md K50).
#
# THE SHAPE IS possessify/altcls's — one witness family, both arms in ONE
# translation unit, swept — AND THE CLAIM IS THE OPPOSITE ONE. Every other
# differential in this tree checks that two arms AGREE, because every other
# `-fno-` axis is answer-identity-preserving. This axis is not (it is the only
# one in tuning.md that is not), so agreement everywhere would mean the flag
# does nothing. What is checked instead is WHERE they differ:
#
#   §1  the arms are IDENTICAL at every character boundary — the guard is
#       transparent where it must be;
#   §2  the arms DIVERGE at exactly the mid-character positions, and the
#       divergence is exactly the typed refusal — never a different answer;
#   §3  the divergence population is NON-EMPTY (a dead guard is a red check,
#       not a quiet pass), with a FLOOR so a shrinking population is a
#       finding rather than a slow fade;
#   §4  a `byte` artifact is guard-free under EITHER flag, and the two builds
#       are byte-identical — the encoding with no defect pays nothing;
#   §5  the ENGINE's own positions are boundaries under BOTH arms. This is
#       K50's actual wrong-answer fix and it has no flag, so it is checked
#       against the reference answer rather than against the other arm.
#
# §1-§3 are the driver's job and its own header explains why the boundary
# predicate is recomputed there rather than read off an artifact. §4 and §5
# are this script's.
#
# Usage: bash tests/utf8/run_startbnd_diff.sh
# Env: PCREC (default <root>/build/pcrec), CC, GENCFLAGS, KEEP=1

set -u

# LC_ALL=C: this file compares emitted artifacts BYTE for byte in §4, and
# sorts nothing under a collation that could merge two spellings. R24 M-F1's
# cause, one directory over.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="startbnd"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/startbnd.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# THE WITNESS FAMILY, and why each member is in it.
#
# The charter's population is "negative assertions x \B x empty-alternation
# shapes". What they have in common is the ONLY property that turns a
# mid-character start from a wasted attempt into an ANSWER: they can match
# EMPTY at a position whose byte no lowered pattern can consume. A positive
# pattern cannot — under UTF-8 nothing begins by consuming a continuation
# byte — which is exactly the asymmetry utf8_design.md §5.5 missed and
# §2.6.1 had already written down.
#
# Each row is "<label><TAB><pattern><TAB><modules>", and the separator is a TAB
# on purpose: half this family's patterns contain `|`, which is what a first
# draft used and what silently turned `(?:x|)` into a pattern `(?:x` with a
# module named `)`. A separator that can occur in the data is a generator
# measuring itself.
# `%b` and not `%s`: the rows below spell their separator as `\t` and their
# patterns as `\\B`, so the format has to expand both. With `%s` the tab is a
# literal backslash-t and every row parses as one field.
PATTERNS=$(printf '%b\n' \
  'nwordb\t\\B\tassertions' \
  'nwordb-opt\t\\Bx?\tassertions' \
  'neg-look-any\t(?!.)\tlookaround' \
  'neg-behind-any\t(?<!.)\tlookaround' \
  'neg-look-lead\t(?!\\xce)\tlookaround' \
  'neg-behind-lit\t(?<!q)\tlookaround' \
  'empty-alt\t(?:x|)\t' \
  'empty-alt-first\t(?:|x)\t' \
  'star-nullable\tx*\t' \
  'alt-nullable-behind\t(?:(?<!q)|x)\tlookaround')

# THE SUBJECTS, and the same rule: each is here because it discriminates.
# Two-, three- and four-byte characters give one, two and three mid-character
# positions per character respectively, which is what makes the divergence
# population grow with the encoding's width rather than staying at one cell.
# The ill-formed rows are utf8_design.md §2.6(c)'s: an ill-formed byte is a
# position a search may START at (0xFF is not a continuation byte), and a
# continuation byte stranded after one is not — the fix must keep both, and
# a subject holding only well-formed text cannot tell.
SUBJECTS='
61CEB1
CEB1CEB2
61E4B8AD
61F09F9880
CEB161CEB2
61FF
FF61
61FFB1
E4B8AD61CEB1
'

# gen <out> <pattern> [args...] — compile one arm.
gen() {
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        > "$WORKDIR/$out.err" 2>&1
}

# ---------------------------------------------------------------------------
# §1-§3  THE TWO-ARM SWEEP
# ---------------------------------------------------------------------------
total_same=0; total_refused=0; total_other=0; swept=0; skipped=0

subjects_argv=$(echo "$SUBJECTS" | tr '\n' ' ')

printf '%s\n' "$PATTERNS" > "$WORKDIR/rows"

while IFS=$'\t' read -r label pat mods; do
    [ -z "$label" ] && continue
    featargs=""
    [ -n "$mods" ] && featargs="--features $mods"

    # A DIRECTORY PER CASE, with the two arms under FIXED names. The driver
    # `#include`s `"guarded.h"`/`"permissive.h"` so it reads the give-up code
    # out of the artifact rather than spelling it, and a fixed name is what
    # lets one driver source serve every case.
    d="$WORKDIR/$label"
    mkdir -p "$d"

    # The two arms. IDENTICAL invocations but for the flag and the prefix, so
    # nothing else can explain a difference.
    # shellcheck disable=SC2086
    if ! gen "$label/guarded" "$pat" -p g -e utf8 $featargs; then
        skipped=$((skipped + 1))
        echo "SKIP: [$label] guarded arm did not compile — $(head -1 "$d/guarded.err")"
        continue
    fi
    # shellcheck disable=SC2086
    if ! gen "$label/permissive" "$pat" -p p -e utf8 $featargs -fno-startpos-guard; then
        bad "[$label] the PERMISSIVE arm did not compile while the guarded one did — $(head -1 "$d/permissive.err")"
        continue
    fi

    # THE DENY ARM MUST CARRY NO GUARD, checked in the TEXT before anything is
    # run: the driver's LEAKED-INTO-THE-DENY-ARM bucket can only see a leak
    # that FIRES, and a guard emitted with an always-true condition would not.
    if grep -q "return PCREC_ERR_STARTPOS;" "$d/permissive.c"; then
        bad "[$label] -fno-startpos-guard emitted a startpos guard anyway (a 'return PCREC_ERR_STARTPOS;' is in the artifact)"
        continue
    fi
    if ! grep -q "return PCREC_ERR_STARTPOS;" "$d/guarded.c"; then
        bad "[$label] the DEFAULT arm emitted NO startpos guard under -e utf8 — the axis's default is not being taken, so every cell below would agree vacuously"
        continue
    fi

    if ! gen_cc "startbnd:$label" "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror \
            ${GENCFLAGS:-} -I"$d" \
            -o "$d/drv" "$d/guarded.c" "$d/permissive.c" \
            "$SCRIPT_DIR/startbnd_driver.c" > "$d/cc.log" 2>&1; then
        bad "[$label] the two arms did not compile into ONE translation unit — $(tail -3 "$d/cc.log" | tr '\n' ' ')"
        continue
    fi

    # shellcheck disable=SC2086
    if gen_run "startbnd:$label" "$d/drv" $subjects_argv > "$d/out" 2>&1; then
        :
    else
        bad "[$label] the sweep reported a classification defect:"
        grep -v '^buckets:' "$d/out" | head -8 >&2
    fi

    line=$(grep '^buckets:' "$d/out")
    s=$(echo "$line" | sed 's/.*same=\([0-9]*\).*/\1/')
    r=$(echo "$line" | sed 's/.*refused=\([0-9]*\).*/\1/')
    o=$(echo "$line" | sed 's/.*other=\([0-9]*\).*/\1/')
    total_same=$((total_same + s))
    total_refused=$((total_refused + r))
    total_other=$((total_other + o))
    swept=$((swept + 1))

    # §3's per-pattern half. A family member that produces NO divergence has
    # stopped reaching the site it was written for — [MECH-REACH]'s shape —
    # and saying so per pattern is what stops one live member carrying nine
    # dead ones.
    if [ "$r" -eq 0 ]; then
        bad "[$label] divergence population is EMPTY: this witness produced no refused cell at all, so it certifies nothing about the guard"
    fi
    echo "  [$label] same=$s refused=$r other=$o"
done < "$WORKDIR/rows"

# The loop above runs in this shell (a redirect, not a pipe), so the totals
# survive it — which is the whole reason `rows` is a file.
if [ "$swept" -eq 0 ]; then
    bad "§1-§3: NO pattern was swept at all (skipped=$skipped) — the sweep measured nothing"
else
    if [ "$total_other" -eq 0 ]; then
        ok "§1/§2 the two arms are IDENTICAL at every character boundary and differ ONLY by the typed refusal at mid-character positions: $total_same agreeing cells, $total_refused refused, 0 otherwise, over $swept witnesses x $(echo "$SUBJECTS" | grep -c .) subjects"
    else
        bad "§1/§2: $total_other cells were neither agreement-at-a-boundary nor refusal-at-a-non-boundary (see the per-pattern output above)"
    fi
fi

# §3's aggregate half, with the FLOOR the charter asks for. The number is
# DERIVED rather than observed, which is what makes it a check instead of a
# transcription of one run: each witness is swept over the same subjects, so
# the count is (patterns) x (continuation-byte positions across the subject
# list) = 10 x 14 = 140. The 14 is
#
#   61CEB1        1   (B1 at index 2)
#   CEB1CEB2      2   (indices 1, 3)
#   61E4B8AD      2   (indices 2, 3)
#   61F09F9880    3   (indices 2, 3, 4)
#   CEB161CEB2    2   (indices 1, 4)
#   61FF          0   -- 0xFF is NOT a continuation byte, so both its
#   FF61          0      positions are legal starts (utf8_design.md 2.6(c)),
#                        and these two subjects contribute to `same` instead.
#                        A run in which they started contributing REFUSALS
#                        would mean the fix had made an ill-formed byte
#                        unstartable, which is the failure 2.6(c) forbids.
#   61FFB1        1   (index 2: a continuation byte stranded after an
#                      illegal one is still not a character start)
#   E4B8AD61CEB1  3   (indices 1, 2, 5)
#
# It is a TRIPWIRE and not a target, so it is compared with `>=`: a run that
# finds MORE (a witness or a subject added) is fine and a run that finds FEWER
# means something stopped reaching the guard.
REFUSED_FLOOR="${STARTBND_REFUSED_FLOOR:-140}"
if [ "$total_refused" -ge "$REFUSED_FLOOR" ]; then
    ok "§3 non-vacuity: $total_refused mid-character cells actually diverged (floor $REFUSED_FLOOR) — the guard is live and the sweep reaches it"
else
    bad "§3 non-vacuity: only $total_refused mid-character cells diverged, below the floor of $REFUSED_FLOOR. Either the witness family stopped reaching the guard or the subject list shrank; re-derive the floor deliberately rather than lowering it"
fi

# ---------------------------------------------------------------------------
# §4  THE byte ENCODING PAYS NOTHING
# ---------------------------------------------------------------------------
# The claim is stronger than "no guard": the two BUILDS are byte-identical, so
# a byte-compiled caller cannot tell the flag exists. That is what makes a
# denied byte build a usable reference for any other check.
#
# THE TWO ARTIFACTS SHARE A BASENAME AND DIFFER ONLY IN THEIR DIRECTORY, and
# that is not tidiness: a self-contained artifact `#include`s its own header
# by name, so two builds written to `on.c` and `off.c` differ on that line for
# a reason that has nothing to do with the flag. A first draft did exactly
# that and reported all three patterns as MOVED — the check would have been
# permanently red on correct behaviour, which is the failure mode that gets a
# check deleted rather than believed.
byte_ok=1
for pat in '\B' 'a' '(?:x|)'; do
    tag=$(printf '%s' "$pat" | tr -c 'a-zA-Z0-9' '_')
    mkdir -p "$WORKDIR/byte_on_$tag" "$WORKDIR/byte_off_$tag"
    gen "byte_on_$tag/art"  "$pat" -p b --features assertions || byte_ok=0
    gen "byte_off_$tag/art" "$pat" -p b --features assertions -fno-startpos-guard || byte_ok=0
    if ! cmp -s "$WORKDIR/byte_on_$tag/art.c" "$WORKDIR/byte_off_$tag/art.c"; then
        bad "§4 [$pat] a byte artifact MOVED under -fno-startpos-guard; the byte backend restricts no position, so neither build may emit a guard and the two must be byte-identical"
        byte_ok=0
    fi
    if grep -q "return PCREC_ERR_STARTPOS;" "$WORKDIR/byte_on_$tag/art.c"; then
        bad "§4 [$pat] a byte artifact emitted a startpos guard: every position is a character boundary under that encoding, so the guard is a tautology that must not be emitted"
        byte_ok=0
    fi
    if ! grep -q '_STARTPOS_GUARD "permissive"' "$WORKDIR/byte_on_$tag/art.c"; then
        bad "§4 [$pat] a byte artifact does not stamp _STARTPOS_GUARD \"permissive\" — the stamp must report what the artifact IS, and a byte artifact answers at every position"
        byte_ok=0
    fi
done
[ "$byte_ok" -eq 1 ] && ok "§4 the byte encoding pays nothing: 3 patterns x 2 flag settings byte-identical, no guard emitted, stamp reads \"permissive\" honestly"

# ---------------------------------------------------------------------------
# §5  THE ENGINE'S OWN POSITIONS, WHICH ARE NOT PART OF THE AXIS
# ---------------------------------------------------------------------------
# K50's wrong-answer fix has no flag, so it cannot be checked by comparing the
# two arms — BOTH must be right. These cells are pinned against the REFERENCE
# ORACLE's answer (libpcre2 10.46 under PCRE2_UTF, transcript
# docs/design/utf8_measurements/out/startbnd.txt §1) rather than against
# anything this compiler produces.
#
# EACH ROW IS A DIFFERENT MECHANISM, which is the point of having three:
# row 1 is the DFA self-loop (K50's own witness, RX_ENGINE "dfa"), row 2 is
# ENG_ATTEMPT's start loop (a BOT-family branch routes it there and a nullable
# second branch keeps its interior start live), row 3 is the VM's retry (K49's
# site, checked here so a change that re-broke it fails in K50's own suite too).
eng_ok=1
check_engine_cell() {   # <label> <pattern> <modules> <hexsubject> <startpos> <expected> [extra pcrec args...]
    local label="$1" pat="$2" mods="$3" subj="$4" sp="$5" want="$6"; shift 6
    local feat=""
    [ -n "$mods" ] && feat="--features $mods"
    local d="$WORKDIR/eng_$label"
    mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! gen "eng_$label/engine" "$pat" -p e -e utf8 $feat "$@"; then
        bad "§5 [$label] did not compile — $(head -1 "$d/engine.err")"
        eng_ok=0; return
    fi
    if ! gen_cc "startbnd:eng:$label" "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror \
            ${GENCFLAGS:-} -I"$d" -o "$d/drv" \
            "$d/engine.c" "$SCRIPT_DIR/startbnd_engine_driver.c" \
            > "$d/cc.log" 2>&1; then
        bad "§5 [$label] did not build — $(tail -2 "$d/cc.log" | tr '\n' ' ')"
        eng_ok=0; return
    fi
    local got
    got=$(gen_run "startbnd:eng:$label" "$d/drv" "$subj" "$sp")
    if [ "$got" = "$want" ]; then
        echo "  §5 [$label] $got"
    else
        bad "§5 [$label] pattern '$pat' on $subj at startpos $sp answered $got, reference libpcre2 10.46 under PCRE2_UTF answers $want — a position the ENGINE generated is not a character boundary"
        eng_ok=0
    fi
}

check_engine_cell dfa-selfloop      '\B'         assertions           61CEB1     0 '(3,3)'
check_engine_cell dfa-selfloop-3b   '\B'         assertions           61E4B8AD   0 '(4,4)'
check_engine_cell dfa-selfloop-4b   '\B'         assertions           61F09F9880 0 '(5,5)'
check_engine_cell attempt-startloop '(?m)^a|\B'  assertions,modifiers 61CEB1     1 '(3,3)'
check_engine_cell vm-retry          '(?<!.)'     lookaround           CEB1CEB2   2 'no-match'
check_engine_cell dfa-forced        '\B'         assertions           61CEB1     0 '(3,3)' --engine=dfa
check_engine_cell vm-forced         '\B'         assertions           61CEB1     0 '(3,3)' --engine=vm

[ "$eng_ok" -eq 1 ] && ok "§5 CROSS-ENGINE: every candidate match start the engine generates is a character boundary, on the DFA self-loop, ENG_ATTEMPT's start loop and the VM's retry, and both engines agree with libpcre2 10.46 on the CORRECT answer (before this fix they agreed on the wrong one, which is why nothing caught K50)"

# The matrix scrapes these two lines by name (tests/mech/run_sabotage_matrix.sh's
# `startbnd` arm), so they are spelled the way every other suite in the tree
# spells them rather than in this script's own words.
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "startbnd-diff: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
