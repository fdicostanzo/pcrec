#!/usr/bin/env bash
# run_entry_shape_identity.sh -- [CC-DIFF] STEP 2 (2026-09-04, lane ccd2):
# THE VM ENTRY-SHAPE LADDER'S ANSWER-IDENTITY GATE.
#
# `--vm-entry-shape=1..4` (docs/spec/tuning.md S2.21) chooses among four
# emission shapes for the VM entry chain. All four are supposed to be the SAME
# MATCHER: the rung moves frames, canaries and body copies, never an answer.
# This file holds them to that, witness by witness, span by span, group by
# group -- against the artifact AUTO emits, which is the shape a caller who
# passes no flag actually gets.
#
# WHY IT IS A FILE AND NOT A SCRATCH SWEEP. The write phase ran this
# comparison ad hoc (14 patterns x 409 subjects, 0 mismatches) and the run died
# with its scratchpad, so the branch carried a CLAIM and not a CHECK. What is
# committed can be re-run after the next change to the emitter; what was run
# once cannot.
#
# ============================================================================
# THE TWO ARMS THAT MAKE A GREEN RUN WORTH READING
# ============================================================================
#
# (1) NON-VACUITY, ASSERTED POSITIVELY AND PER WITNESS. The ad-hoc sweep's own
#     report admitted that THREE of its fourteen witnesses -- `[0-9a-f]{32}`,
#     `(?<=foo)bar` and `(?>a*)ab` -- matched NOTHING on its subject set. All
#     three hashed to the all-nomatch digest, so all three "agreed" across all
#     five shapes while testing the emitter and not a single answer. That is
#     `docs/dev/learnings.md` S3's [MECH-REACH] shape exactly: a witness that
#     stopped reaching its site still reads green.
#
#     THE FIX IS IN THE SUBJECTS FOR TWO OF THE THREE, AND IN THE PATTERN FOR
#     THE THIRD -- and which is which was decided by the gate, not by taste.
#     All three name POPULATIONS the rung ladder must cover (a long fixed-width
#     class run; a lookbehind, which is FRAMED, so the forward rungs are
#     illegal and the artifact must fall back; an atomic group), so dropping one
#     would have bought a green run by deleting coverage. `[0-9a-f]{32}` and
#     `(?<=foo)bar` match perfectly well once given subjects that contain a
#     32-digit hex run and the string `foobar`, so their vacuity really was in
#     the subject set.
#
#     `(?>a*)ab` IS DIFFERENT, AND THE GATE IS WHAT ESTABLISHED IT. Its first
#     run reported the witness VACUOUS on the new subject set too, which sent
#     the pattern back for a reading: `(?>a*)` consumes every available `a`
#     ATOMICALLY and never gives one back, so the following `a` can never be
#     supplied and the pattern's LANGUAGE IS EMPTY. No subject set could have
#     rescued it. The write phase's report called it "matched nothing on this
#     subject set"; it matches nothing on any subject set, which is a stronger
#     statement and the reason the pattern itself is replaced (by `(?>a*)b`)
#     rather than re-subjected. The gate REFUSES to pass a witness whose AUTO
#     arm produced no match at all, which is exactly how this surfaced.
#
# (2) THE RUNG REACHED THE EMITTER. Five builds that all ignored the flag agree
#     with each other perfectly. So each build's own `<PREFIX>_VM_ENTRY_SHAPE`
#     stamp is read back from the emitted .c and the run is RED unless all four
#     tokens (`plain`/`shared`/`forward`/`inline`) are realised somewhere in
#     the sweep. This is a census over the whole table rather than a per-cell
#     pin, because a single artifact legally falls to the nearest legal rung --
#     a framed witness CANNOT take `forward` and pinning it to one would be
#     wrong, not strict.
#
#     The stamps are grepped from the .c and not `#ifdef`-ed in the driver
#     because the emitter writes them to the .c and not the paired .h; the
#     driver says so at its head.
#
# EVERY WITNESS IS EMITTED `--features all --engine=vm`, and BOTH halves are
# load-bearing. `--engine=vm` because the rung ladder only reaches VM
# artifacts: under AUTO several of these patterns select the DFA engine and
# stamp no rung at all, which would make this gate vacuous a second way.
# `--features all` because three of the witnesses -- the lookbehind, the atomic
# group and the backreference -- belong to modules that are off by default, and
# without it they are refused rather than compared. That refusal is what the
# gate's first run reported, and it is the reason the flag is here rather than
# the three witnesses being dropped: they are the table's only members of three
# populations the rung ladder must cover.
#
# The rung ladder only reaches VM artifacts, so every witness is emitted
# `--engine=vm`. Under AUTO several of these patterns select the DFA engine and
# stamp nothing at all -- which is correct behaviour and would make this gate
# vacuous a second way if the flag were left off.
set -u
cd "$(dirname "$0")/../.." || exit 2
PCREC=${PCREC:-build/pcrec}
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run bounds every compiler call
CC=${CC:-gcc}
GENCFLAGS=${GENCFLAGS:-}
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0
bad() { echo "run_entry_shape_identity.sh: FAIL: $*" >&2; fail=1; }

# ============================================================================
# THE WITNESS TABLE: label | pattern | population | subjects
# ============================================================================
# `population` is what the witness is HERE FOR, so a later reader can see what
# a deletion would cost. Subjects are SPACE-SEPARATED WORDS, so two tokens the
# driver expands carry what that list cannot: `@EMPTY` is the whole empty
# subject, and `@SP` is one space. The backreference witness needs the second
# one -- `(\w+)\s+\1` cannot match a single word, and the gate's non-vacuity
# arm is what reported that rather than passing on six all-nomatch outputs.
witnesses=(
  # --- the three the ad-hoc sweep ran VACUOUS, with subjects that hit ---
  'hex32|[0-9a-f]{32}|long fixed-width class run|0123456789abcdef0123456789abcdef xx0123456789abcdef0123456789abcdefyy deadbeefdeadbeefdeadbeefdeadbeef0123456789abcdef0123456789abcdef nothinghere'
  'lookbehind|(?<=foo)bar|FRAMED: the rung is illegal and the artifact must fall to plain|foobar xxfoobar barfoo foobarfoobar nobar'
  'atomic|(?>a*)b|atomic group|aab xaabx b aaab ccc'
  # --- the eleven that were already real, kept ---
  'alt3|a(b|c)+d|framed, capture in a quantified alternation|abcd abd acd abcbcd xx'
  'backref|(\w+)\s+\1|framed, backreference|hello@SPhello xx@SPworld@SPworld@SPyy abc@SPabd nope'
  'twocap|(abc)(def)|frameless, trail-touching|abcdef xxabcdefyy abc def'
  'email|([a-z]+)@([a-z]+)\.([a-z]{2,4})|three captures, trail-touching|frank@example.com a@b.io nope@ x'
  'digits|\d{1,16}|bounded digit run|1 1234567890 x99y 2026 abc'
  'lower8|[a-z]{0,8}|ZERO-WIDTH capable: matches the empty subject|@EMPTY abcdefgh xyz 123'
  'year4|[12][0-9]{3}|narrow first-byte class|2026 1999 in 1066 and 2026 3000'
  'lit16|abcdefghijklmnop|plain literal, no VM branching|abcdefghijklmnop xxabcdefghijklmnopyy abcdefghijklmno'
  'ipv4|(?:[0-9]{1,3}\.){3}[0-9]{1,3}|repeated group with a quantifier|192.168.0.1 a 10.0.0.255 b 1.2.3 999.999.999.999'
  'w8|(?:yoslwssiyybw|dybf|oodo|omykisp|idox|oemrbp|xzxj|qnhl)|WIDE ALTERNATION: a real island program|dybf xxoodoyy qnhl idox oemrbp zzz'
  'nested|((a)|b){1,4}c|nested captures under a bounded repeat|abc bbc aac c aaaac'
)

shapes_seen=""
nwit=0
for w in "${witnesses[@]}"; do
    # The pattern itself may contain '|' (w8 is an alternation), so the
    # split above is deliberately re-assembled: everything between the first
    # and the last two fields is the pattern.
    label=${w%%|*}
    rest=${w#*|}
    subj=${rest##*|}
    rest=${rest%|*}
    pop=${rest##*|}
    pat=${rest%|*}
    nwit=$((nwit+1))

    d="$TMP/$label"; mkdir -p "$d"
    ok=1
    for s in 0 1 2 3 4; do
        if ! pcrec_run "$PCREC" -p rx --features all --engine=vm --vm-entry-shape=$s -o "$d/a$s.c" -- "$pat" >"$d/emit$s.err" 2>&1; then
            bad "$label: emit at --vm-entry-shape=$s failed: $(head -2 "$d/emit$s.err")"
            ok=0; break
        fi
        cp "$d/a$s.h" "$d/art.h"
        if ! $CC -O2 -std=gnu11 $GENCFLAGS -I"$d" -o "$d/run$s" \
                tests/codegen/entry_shape_driver.c "$d/a$s.c" 2>"$d/cc$s.err"; then
            bad "$label: compile at rung $s failed: $(head -3 "$d/cc$s.err")"
            ok=0; break
        fi
        rm -f "$d/art.h"
        # ARM 2: what the emitter says it DID.
        st=$(grep -o 'RX_VM_ENTRY_SHAPE "[a-z]*"' "$d/a$s.c" | head -1 | sed 's/.*"\(.*\)"/\1/')
        if [ -z "$st" ]; then
            bad "$label rung $s: no RX_VM_ENTRY_SHAPE stamp in the emitted .c — either the artifact is not a VM artifact (so this witness reaches nothing) or the stamp moved"
            ok=0; break
        fi
        [ "$s" = 0 ] || case " $shapes_seen " in *" $st "*) ;; *) shapes_seen="$shapes_seen $st";; esac
        # shellcheck disable=SC2086
        "$d/run$s" $subj > "$d/out$s" 2>"$d/run$s.err" || {
            bad "$label rung $s: driver exited non-zero: $(head -2 "$d/run$s.err")"; ok=0; break; }
    done
    [ "$ok" -eq 1 ] || continue

    # ARM 1: NON-VACUITY. AUTO must have matched something, or this witness
    # compared five all-nomatch outputs and proved nothing.
    if ! grep -q '	m0	' "$d/out0"; then
        bad "$label: VACUOUS — the AUTO arm matched NOTHING on its subjects, so the four rungs agreed about nothing (population: $pop)"
        continue
    fi

    for s in 1 2 3 4; do
        if ! cmp -s "$d/out0" "$d/out$s"; then
            bad "$label: rung $s PARTS FROM AUTO — $(diff "$d/out0" "$d/out$s" | head -3 | tr '\n' ' ')"
        fi
    done
done

# ARM 2's verdict, over the whole table.
for want in plain shared forward inline; do
    case " $shapes_seen " in
        *" $want "*) ;;
        *) bad "no witness in this table realised rung '$want' — the flag may have stopped reaching the emitter, in which case every comparison above compared a build to itself";;
    esac
done

echo "run_entry_shape_identity.sh: $nwit witnesses x 5 shapes; rungs realised:$shapes_seen"
if [ "$fail" -ne 0 ]; then
    echo "run_entry_shape_identity.sh: FAILED" >&2
    exit 1
fi
echo "run_entry_shape_identity.sh: all rungs answer-identical to AUTO; every witness matched at least once"
exit 0
