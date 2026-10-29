#!/usr/bin/env bash
# tests/vm/run_trail_compact.sh -- [K134] the VM's trail compaction, held to
# what it promises (src/gen/emit_vm.c `vm_emit_trail_compact`;
# docs/spec/limits.md §3.2, §4).
#
#   1. CHECKPOINT STRUCTURE. tests/codegen/trail_checkpoints.py over every
#      witness artifact below: every cycle of the emitted program that writes
#      the trail passes a `<PREFIX>_TRAIL_CHECK`, and the heaviest
#      checkpoint-free path is within the artifact's margin. It reads the
#      EMITTED C, not the emitter's own idea of which jumps go back.
#      TRAIL_CORPUS=1 adds the whole corpus (every pattern line under tests/,
#      --engine=vm; minutes, not part of make test).
#   2. NO ANSWER CHANGES. tests/vm/trail_compact_driver.c runs each witness
#      subject through `rx_search_in` at every trail capacity of a ladder up
#      to the plain run's own high-water: each run gives up with
#      PCREC_ERR_FRAMES or returns exactly the large-buffer answer. Witnesses
#      marked `compacts` must also ANSWER below that high-water at least once
#      (only a compaction can do that), so a witness that stopped reaching
#      the compaction reads as a failure, not as a quiet pass.
#   3. THE FAST TIER ESCALATES. A long flat cscan subject on the un-suffixed
#      entry (built with -DRX_TEST_TIER_HOOK) escalates exactly once and
#      answers: the fast tier's kept trail does not leave a quarter free, so
#      it stops compacting and gives up instead of compacting at every pass.
#   4. THE DOCUMENTED BOUNDARY. `^(a(?1)?b)$` on a^n b^n needs exactly
#      4n + 17 trail entries (docs/spec/limits.md §4): n = 200 answers at 817
#      and gives up at 816. The compaction keeps 3n - 2 entries and continues
#      only while a quarter of the trail stays free below the floor, so this
#      pins the floor, the margin and the quarter rule together; without the
#      quarter rule 613 entries would do (3n + 13), which no answer shows.
#
# Usage: bash tests/vm/run_trail_compact.sh
# Env: PCREC, CC, GENCFLAGS, KEEP=1, TRAIL_CORPUS=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="trailcompact"
CHECKER="$ROOT_DIR/tests/codegen/trail_checkpoints.py"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "trailcompact: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# The cscan pattern, as tests/recursion/cscan.rxt spells it (its one
# `pattern` row in --list-source, escaped), so the witness follows the corpus file.
CSCAN="$("$PCREC" --list-source "$ROOT_DIR/tests/recursion/cscan.rxt" 2>/dev/null \
         | awk -F'\t' '$1=="pattern" {print $5; exit}')"
[ -n "$CSCAN" ] || bad "[K134] could not read the cscan pattern from tests/recursion/cscan.rxt"

# name | pattern-esc | subject (a python expression) | compacts? | probes
# `compacts` = the plain run's trail holds entries no unwind reads, so some
# capacity below its high-water must answer. `identity` = every pass pushes
# its own frame (nothing to drop): the answers must still never change.
WITNESSES="$WORKDIR/witnesses"
{
    printf 'cscan-idents\t%s\t%s\tcompacts\n' "$CSCAN" "'(?{ '+' '.join('x%d'%i for i in range(400))+' })'"
    printf 'cscan-splice\t%s\t%s\tcompacts\n' "$CSCAN" "'(?{ '+'a\\\\\\n'*800+' })'"
    printf 'cscan-parens\t%s\t%s\tcompacts\n' "$CSCAN" "'(?{ '+'('*200+')'*200+' })'"
    printf 'cscan-braces\t%s\t%s\tcompacts\n' "$CSCAN" "'(?{ '+'{'*40+' x; '+'}'*40+' })'"
    printf 'specimen\t%s\t%s\tcompacts\t816:-3 817:1\n' '^(a(?1)?b)$' "'a'*200+'b'*200"
    printf 'possessive-captures\t%s\t%s\tcompacts\n' '(?:(a)(b)?)*+x' "'ab'*500+'x'"
    printf 'atomic-captures\t%s\t%s\tcompacts\n' '(?>(a)|b)+c' "'ab'*500+'c'"
    printf 'nested-possessive\t%s\t%s\tcompacts\n' '(?:(?:(a)b)++c)*+d' "'abc'*300+'d'"
    printf 'backref-loop\t%s\t%s\tidentity\n' '(a)\\1+' "'a'*1000"
    printf 'greedy-frames\t%s\t%s\tidentity\n' '(a|ab)*c' "'ab'*300+'c'"
    printf 'empty-guard\t%s\t%s\tidentity\n' '(?:(a)|())+b' "'a'*500+'b'"
} > "$WITNESSES"

nw=0; ncompacts=0
nprobe=0
while IFS="$(printf '\t')" read -r name pat subj kind probes; do
    nw=$((nw + 1))
    d="$WORKDIR/$name"; mkdir -p "$d"
    # --list-source escapes backslashes and newlines but not quotes
    if ! pcrec_run "$PCREC" -p rx --features all --engine=vm -o "$d/gen.c" \
            --pattern-esc --pattern "\"${pat//\"/\\\"}\"" >/dev/null 2>"$d/err"; then
        bad "[K134] $name: pcrec refused the witness: $(head -2 "$d/err" | tr '\n' ' ')"
        continue
    fi
    # 1. checkpoint structure
    if out="$(python3 -I "$CHECKER" "$d/gen.c" 2>&1)"; then
        case "$out" in
            *" 0 checkpoints"*) bad "[K134] $name: no trail checkpoint in the artifact, so nothing here reaches the compaction ($out)" ;;
            *) ok "[K134] $name: every trail-writing cycle passes a checkpoint (${out#*: })" ;;
        esac
    else
        bad "[K134] $name: $(printf '%s\n' "$out" | grep -m3 FAIL | tr '\n' ' ')"
    fi
    # 2. no answer changes
    python3 -I -c "import sys; sys.stdout.buffer.write(($subj).encode('latin-1'))" > "$d/s.bin"
    # shellcheck disable=SC2086
    if ! gen_cc "$name" "$CC" $GENCFLAGS -DRX_TEST_TIER_HOOK -I "$d" -o "$d/t" \
            "$SCRIPT_DIR/trail_compact_driver.c" "$d/gen.c"; then
        bad "[K134] $name: the driver did not build: $(printf '%s\n' "$GEN_CC_LOG" | head -3 | tr '\n' ' ')"
        continue
    fi
    caps=""
    for pr in ${probes:-}; do caps="$caps ${pr%%:*}"; done
    # shellcheck disable=SC2086
    res="$(gen_run "trailcompact $name" "$d/t" "$d/s.bin" $caps 2>"$d/run.err")"; rc=$?
    set -- $res
    if [ "$rc" -ne 0 ] || [ "${1:-}" != "ref" ]; then
        bad "[K134] $name: the driver failed (rc $rc): $res $(head -3 "$d/run.err" | tr '\n' ' ')"
        continue
    fi
    below="$(printf '%s\n' "$res" | awk '{for (i = 1; i < NF; i++) if ($i == "below_hw") print $(i + 1)}')"
    mism="$(printf '%s\n' "$res" | awk '{for (i = 1; i < NF; i++) if ($i == "mismatch") print $(i + 1)}')"
    if [ "$mism" != "0" ]; then
        bad "[K134] $name: an answer changed under a smaller trail: $res"
    else
        ok "[K134] $name: no answer changed at any trail capacity ($res)"
    fi
    if [ "$kind" = "compacts" ]; then
        if [ "${below:-0}" -gt 0 ]; then
            ncompacts=$((ncompacts + 1))
            ok "[K134] $name: $below capacities below the plain run's high-water answered (only a compaction can)"
        else
            bad "[K134] $name: no capacity below the plain run's high-water answered, so the compaction never made room ($res)"
        fi
    fi
    # 4. the documented boundary
    for pr in ${probes:-}; do
        nprobe=$((nprobe + 1))
        case " $res " in
            *" at $pr "*) ok "[K134] $name: trail ${pr%%:*} returns ${pr#*:}, the boundary limits.md §4 states" ;;
            *) bad "[K134] $name: trail ${pr%%:*} should return ${pr#*:} (limits.md §4's 4n + 17 for n = 200): $res" ;;
        esac
    done
    # 3. the fast tier escalates (the cscan identifier witness)
    if [ "$name" = "cscan-idents" ]; then
        esc="$(printf '%s\n' "$res" | awk '{for (i = 1; i < NF; i++) if ($i == "escalations") print $(i + 1)}')"
        drc="$(printf '%s\n' "$res" | awk '{for (i = 1; i < NF; i++) if ($i == "default_rc") print $(i + 1)}')"
        if [ "$esc" = "1" ] && [ "$drc" = "1" ]; then
            ok "[K134] $name: the un-suffixed entry escalated once and answered"
        else
            bad "[K134] $name: the un-suffixed entry escalated ${esc:-?} times (want 1) and returned ${drc:-?} (want 1): the fast tier's hysteresis"
        fi
    fi
done < "$WITNESSES"

# K35: the populations, counted.
if [ "$nw" -eq 11 ] && [ "$ncompacts" -eq 8 ] && [ "$nprobe" -eq 2 ]; then
    ok "[K134] population: $nw witnesses, $ncompacts of them answered below the plain high-water, $nprobe boundary probes"
else
    bad "[K134] population: $nw witnesses (want 11), $ncompacts compacting (want 8), $nprobe boundary probes (want 2)"
fi

if [ "${TRAIL_CORPUS:-0}" = "1" ]; then
    if out="$(python3 -I "$CHECKER" --corpus "$PCREC" "$ROOT_DIR" 2>&1)"; then
        ok "[K134] corpus: $(printf '%s\n' "$out" | tail -1)"
    else
        bad "[K134] corpus: $(printf '%s\n' "$out" | grep -m5 -E 'FAIL|trail_checkpoints' | tr '\n' ' ')"
    fi
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
