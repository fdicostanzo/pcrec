#!/usr/bin/env bash
# tests/atomic_groups/run_atomic_diff.sh — [M6.4.2]'s behavioural instrument
# for module `atomic-groups`: five things tests/atomic_groups/*.rxt
# structurally CANNOT assert, each against libpcre2 or against pcrec itself.
#
#   §1  THE SUBJECT SWEEP, against libpcre2, over a generated space with
#       startpos taking EVERY value in [0, n]. The `.rxt` corpus pins chosen
#       cells; this sweeps. The startpos axis is exhaustive because the cut
#       makes "the leftmost candidate is not the leftmost match" an ORDINARY
#       occurrence — `(?>a|ab)c` on "abc" is NO MATCH while its uncut twin
#       matches — so WHICH start the search reaches is the axis this construct
#       moves, and a sweep that fixed the argument could not see it.
#
#   §2  THE ENGINE DIFFERENTIAL, and it is the single most important section
#       in this file. Every pattern is compiled BOTH ways: the DEFAULT
#       (hybrid: capture-erased DFA prefilter + VM) and `--engine=vm` (the
#       prefilter OFF, R21 E-6). §4's whole hazard lives in the difference
#       between those two artifacts — the prefilter necessarily answers for
#       the UNCUT language, so its span END is not a bound on the cut match's
#       end — and a suite that ran only one of them would not see it. 114
#       cells of silent match loss were MEASURED on the emitted prefilter
#       before RULE H3 existed; this is the arm they would show up in.
#
#   §2b THE `-fno-possessify` ARM. Without it sabotage row S92 (the flag
#       CLEARS a user-written possessive) cannot be scored at all: its whole
#       failing direction is "RED only under the flag", and a corpus with no
#       flag arm has nowhere for it to be red. The flag denies possessify's
#       REWRITE and must NOT change a WRITTEN possessive's answer — that is
#       §3.2 RULE 2 as behaviour, and it is what makes storing the module's
#       semantics in `Ast.possessive` a miscompile rather than a style
#       question.
#
#   §3  THE DISCHARGE DIFFERENTIAL, pcrec against pcrec. Every pattern is
#       compiled with and without `-fno-atomic-discharge`, asserting IDENTICAL
#       ANSWERS. The discharge deletes a cut possessify's §2.2 verdict proves
#       dead; "changes no answer" is its entire claim and this is the only
#       thing in the tree that checks it. It also asserts §5.4's
#       EMISSION-NEUTRALITY where that property holds: for a DISCHARGED
#       possessive the VM artifact is byte-identical either way, because
#       possessify re-derives the identical verdict on the same quantifier and
#       re-marks it. The discharge changes ENGINE SELECTION and nothing else.
#
#   §4  THE THREE ENTRIES side by side (atomic_entries.c), which is H4's
#       obligation. `<prefix>_match`/`_match_caps` answer about exactly
#       `ctx->pos` and pass `ctx->len` as the MRL ceiling rather than a
#       prefilter window, so §4's hazard cannot reach them — a claim nothing
#       in the corpus can see either way. The match-here ORACLE is `\G(?:PAT)`
#       (wave D's trick): libpcre2 has no anchored mode, but `\G` is true iff
#       `pos == startpos`, so its answer for the wrapped pattern IS the
#       match-here answer for the bare one.
#
# EVERY POPULATION IS ASSERTED, NEVER PRINTED. A sweep that quietly generated
# nothing prints the same silence as one that agreed everywhere, and this
# project's own record is full of that shape (the design's §6.4a non-vacuity
# counter measured the wrong axis; the WRAP assertion passed on an empty
# population). Each section below ends in a floor its own run has to clear.
#
# Usage: bash tests/atomic_groups/run_atomic_diff.sh
# Env: PCREC, CC, KEEP=1
#
# SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern), never silently.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "atomic-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the oracle ----------------------------------------------------------
ORACLE="$WORKDIR/pcre2_oracle"
if ! $CC -O1 -std=gnu11 -Wall -Wextra -Werror -o "$ORACLE" \
        "$ROOT_DIR/tests/fuzz/pcre2_oracle.c" -ldl 2>"$WORKDIR/ob.log"; then
    echo "FAIL: could not build tests/fuzz/pcre2_oracle:" >&2
    cat "$WORKDIR/ob.log" >&2
    exit 1
fi
printf 'a' > "$WORKDIR/probe"
if ! "$ORACLE" 'a' "$WORKDIR/probe" >/dev/null 2>&1; then
    echo "SKIP: libpcre2 is not available at run time — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
    echo "checks passed: 0"
    echo "checks failed: 0"
    exit 0
fi

# ---- the subject space ---------------------------------------------------
# CUT-SHAPED BY CONSTRUCTION. The cells that can break a cut are the ones
# where the body's FIRST success is not the one the whole match needs, so the
# subject set has to contain the near-misses that force the search to move on:
# a prefix shared between an alternation's branches followed by something only
# the LONGER branch could have reached, and runs of a loop body followed by a
# byte the follow cannot take.
python3 - "$WORKDIR/subjects" <<'PY'
import itertools, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
subs = []
# EXHAUSTIVE up to length 4 over {a, b, c} — 121 subjects. Exhaustive rather
# than curated so every "shared prefix, then the wrong byte" shape the cut
# cells need is present by ENUMERATION rather than by someone remembering it.
for n in range(0, 5):
    for t in itertools.product("abc", repeat=n):
        subs.append("".join(t))
# The quote/space shapes the canonical idiom family is written in, and a few
# longer runs where a greedy loop would retreat many times before the follow
# succeeds — or never does.
subs += ['"', 'ab"cd"', '"x"y"', 'a"b', ' ab ', 'x ab', 'abcd', 'xabcd',
         'abcabc', 'aabbcc', 'ababab', 'abcbca',
         "a" * 12 + "b", "a" * 12 + "ab", "a" * 16, "ab" * 8,
         ("ab" * 6) + "c", "a" * 8 + "x" + "a" * 8, "b" * 12 + "c",
         "ababababababababc"]
for i, s in enumerate(subs):
    with open(os.path.join(out, "s%04d" % i), "wb") as f:
        f.write(s.encode("latin-1"))
print(len(subs))
PY
NSUBJ=$(ls "$WORKDIR/subjects" | wc -l)
if [ "$NSUBJ" -lt 120 ]; then
    bad "subject generation produced only $NSUBJ subjects — the sweep has no space"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the patterns --------------------------------------------------------
# FOUR CLASSES, and the classification is DATA here rather than a rule applied
# later, because the sections below assert different things about each.
#
#   cut       the cut BITES — the atomic answer differs from the uncut twin's
#             somewhere. §3's discharge must DECLINE these.
#   cut2      [M6.4.4] the same claim over the shape this file DID NOT HAVE
#             and the blinded D27 corpus did: a TWO-EXIT body under an
#             OVERLAPPING follow. Every `cut` row above has a follow whose
#             first byte cannot also start a body iteration (`(?:a|ab)*+c`),
#             and that disjointness is precisely what made the tier-1 defect
#             invisible here — the emitter's early loop exit landed at a
#             position where the follow could not match anyway, so no answer
#             moved. `(?:aa|a)++ab` on "aaab" moves: the exit lands where the
#             follow CAN match, which is the whole bug. Carried under EVERY
#             possessive rung and both preferences, with its own non-vacuity
#             floor and its own asserted rung coverage.
#   dead      the cut is provably a no-op — §2.2's verdict is positive, so the
#             free discharge SHOULD delete it. §3's population.
#   carve     a body the LIFT must decline: nullable or lazy. If the lift ever
#             accepted one, the nullable members HANG (a timeout, loud under
#             D45) and the lazy ones answer the wrong language.
#   control   no atomic construct at all — the arm that says the plumbing
#             works, and the only class python `re` can also answer.
PATSPEC=(
    "cut:(?>a|ab)c"
    "cut:(?>ab|a)b"
    "cut:(?>a|ab)b"
    "cut:(?>a|ab)bc"
    "cut:(?>a|ab)c|abcd"
    "cut:(?>ab|a)b|abcd"
    "cut:x*(?>a|ab)c|abcd"
    "cut:(?>(?>a|ab)c|abd)"
    "cut:(?>a(?>b|bc))c"
    "cut:(?>a|ab)*c"
    "cut:(?>a|b)*c"
    "cut:(?>ab)+c"
    "cut:(?>a*)a"
    "cut:(?>a*+)a"
    "cut:a*+a"
    "cut:a++a"
    "cut:(?:a|ab)*+c"
    "cut:(?:a|ab)++c"
    "cut:(?:a|ab){1,3}+c"
    "cut:(?:a|ab){2}+"
    "cut:(?:ab|b){8,}+c"
    "cut:(?>(a)|ab)"
    "cut:(?>(a)x|ab)"
    "cut:((?>(a)|ab))c|(abc)"
    "cut:(?>a|ab)(?>b|bc)c"
    "cut:(?>)a"
    "dead:a*+b"
    "dead:a++c"
    "dead:a?+b"
    "dead:[^\"]*+\""
    "dead:(?>a*)b"
    "dead:(?>a+)c"
    "dead:a{2}+b"
    "dead:a{2,}+b"
    "dead:a{1,2}+b"
    "dead:(?>a{1,2})b"
    "carve:(?>a*?)b"
    "carve:(?>a+?)b"
    "carve:(?>a{1,3}?)b"
    "carve:(?>[ab]*?)b"
    "carve:(?>(?:a|bc)*?)d"
    "carve:(?>a*?b)c"
    "carve:(?>(?:a*)*)b"
    "carve:(?:a*)*+b"
    "carve:(?>(?:a?)*)b"
    "carve:(?:a?)*+b"
    "carve:(?>(?:|a)*)b"
    "carve:(?:|a)*+b"
    "carve:(?>(?:a*?b)*)d"
    "control:a?b"
    "control:[ab]+c"
    "control:(?:a|ab)c"
    "control:(?:ab)+c"
    # ---- [M6.4.4] the two-exit / overlapping-follow family ---------------
    # BODY x QUANTIFIER FORM x PREFERENCE. The bodies are two-exit (a shared
    # prefix, so the loop's stopping position is a CHOICE rather than a
    # byte-determined fact) and the follow OVERLAPS the body's first set and
    # is two bytes wide — which is what makes "one more iteration plus the
    # follow does not fit" reachable at a position where the follow itself
    # still does. The rung each form lands on is ASSERTED below, not
    # commented: `nrung2` ORs the artifacts' own RX_VM_RUNGS and the floor is
    # all five bits.
    "cut2:(?:aa|a)++ab"
    "cut2:(?:aa|a)*+ab"
    "cut2:(?:aa|a){1,3}+ab"
    "cut2:(?:aa|a){8,12}+ab"
    "cut2:(?:aa|a){8,}+ab"
    "cut2:(?>(?:aa|a)+)ab"
    "cut2:(?>(?:aa|a)*)ab"
    "cut2:(?>(?:aa|a){1,3})ab"
    "cut2:(?>(?:aa|a)+?)ab"
    "cut2:(?>(?:aa|a)*?)ab"
    "cut2:(?>(?:aa|a){1,3}?)ab"
    "cut2:(?:a|aa)++ab"
    "cut2:(?:a|aa){1,3}+ab"
    "cut2:(?>(?:a|aa)+?)ab"
    "cut2:(?:ab|a)++ab"
    "cut2:(?:ab|a)*+ab"
    "cut2:(?:ab|a){1,3}+ab"
    "cut2:(?:a|ab)++ab"
    "cut2:(?:a|ab)*+ab"
    "cut2:(?:a|ab){1,3}+ab"
    "cut2:(?:(?:a|ab)(?:c|cd))*+ac"
    "cut2:(?:(?:a|ab)(?:c|cd))++ac"
    "cut2:(?:(?:a|ab)(?:c|cd)){1,3}+ac"
    # the REVDET rung (0x8) needs a reverse-deterministic body; `a|bc` is one
    # and its first set still overlaps the follow.
    "cut2:(?:a|bc)*+ab"
    "cut2:(?:a|bc)++ab"
    "cut2:(?>(?:a|bc)*)ab"
    # the CURSOR rung (0x1). These two were ALREADY RIGHT before the fix —
    # that rung takes no follow-derived early exit — so they are the family's
    # internal control: a fix that "worked" by disabling the cut everywhere
    # would not show up in the rows above, and would here.
    "cut2:a++ab"
    "cut2:a*+ab"
    # the loop one level INSIDE the group rather than as its direct child,
    # where `under_atomic` is FALSE and the general shape carries the cut. The
    # per-rung fix would have missed these; the boundary scoping covers them.
    "cut2:(?>a(?:aa|a)+)ab"
    "cut2:(?>(?:aa|a)+a)ab"
)

gen() { # gen <outdir> <pattern> [extra pcrec args]
    local d="$1" pat="$2"; shift 2
    mkdir -p "$d"
    pcrec_run "$PCREC" --features all -p rx "$@" -o "$d/gen.c" -- "$pat" 2>"$d/err" || return 1
    $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/atomic_batch.c" "$d/gen.c" \
        2>>"$d/err" || return 1
}

# =========================================================================
# §1 + §2 + §2b   THE SUBJECT SWEEP, three arms
# =========================================================================
#
# BATCHED, and the batching is a MEASUREMENT rather than tidiness. The first
# version of this sweep spawned one `pcre2_oracle` and three `fuzz_driver`
# processes PER CELL, over ~120,000 cells: measured at 44 cells per minute,
# i.e. about eleven hours for one run, which is not a test anyone runs and
# certainly not a sabotage-matrix arm. The oracle side is now ONE python
# process (atomic_oracle.py, driving the same libpcre2 through the project's
# committed ctypes binding) and the pcrec side is one process per (pattern,
# arm) reading cells on stdin (atomic_batch.c). Same cells, same comparison,
# ~200 processes instead of ~480,000.
#
# THE COMPARISON IS POSITIONAL, so a batch driver that dropped a line would
# shift every subsequent answer. Both batch programs treat an unreadable line
# as a HARD failure for exactly that reason, and the line COUNTS are asserted
# here as well — belt and braces, because this is the one failure mode the
# shape introduces.

: > "$WORKDIR/patlist"
ncut=0; ncut2=0; ndead=0; ncarve=0; nctl=0
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    printf '%s\t%s\n' "$cls" "$pat" >> "$WORKDIR/patlist"
    case "$cls" in
        cut) ncut=$((ncut + 1)) ;; cut2) ncut2=$((ncut2 + 1)) ;;
        dead) ndead=$((ndead + 1)) ;;
        carve) ncarve=$((ncarve + 1)) ;; *) nctl=$((nctl + 1)) ;;
    esac
done

# THE UNCUT TWINS, for the non-vacuity measurement only. A two-byte edit —
# `(?>` to `(?:`, a possessive `+` dropped — so a divergence is attributable to
# the ATOMICITY and to nothing else; a hand-written twin can differ in
# something else and make the measurement unreadable. Never compared against
# pcrec.
: > "$WORKDIR/twinlist"
while IFS=$'\t' read -r cls pat; do
    # BOTH cut classes. [M6.4.4] added `cut2` and this filter said `cut`
    # alone, so the family's twins were never handed to the oracle, every
    # lookup came back with zero rows, and the new floor read 0/30 — which is
    # what a floor is FOR, and is the second time in this file's short life
    # that a population assertion caught the script rather than the compiler.
    case "$cls" in cut|cut2) ;; *) continue ;; esac
    printf 'twin\t%s\n' "$(printf '%s' "$pat" | sed 's/(?>/(?:/g; s/\([*+?}]\)+/\1/g')" \
        >> "$WORKDIR/twinlist"
done < "$WORKDIR/patlist"

# DEDUPED ON THE PATTERN, and the duplicate is not hypothetical: the UNCUT
# twin of `(?>a|ab)c` IS `(?:a|ab)c`, which is also a `control` row, so the
# oracle emitted its cells TWICE and every consumer reading the column back
# with `awk '$1 == p'` got a 2x-length column. The length assertions below
# caught it — which is what they are for — but the fix belongs here.
cat "$WORKDIR/patlist" "$WORKDIR/twinlist" \
    | awk -F'\t' '!seen[$2]++' > "$WORKDIR/alllist"
if ! python3 "$SCRIPT_DIR/atomic_oracle.py" "$WORKDIR/alllist" \
        "$WORKDIR/subjects" "$WORKDIR/oracle.tsv" 2>"$WORKDIR/oracle.log"; then
    if grep -q 'libpcre2 unavailable' "$WORKDIR/oracle.log"; then
        echo "SKIP: libpcre2 is not available — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
        echo "checks passed: 0"; echo "checks failed: 0"; exit 0
    fi
    bad "the libpcre2 oracle pass failed: $(head -3 "$WORKDIR/oracle.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# THE CELL LIST, in one fixed order every arm is driven with.
: > "$WORKDIR/cells"
for f in "$WORKDIR"/subjects/*; do
    len=$(wc -c < "$f")
    for sp in $(seq 0 "$len"); do
        printf '%s\t%s\n' "$f" "$sp" >> "$WORKDIR/cells"
    done
done
NCELL=$(wc -l < "$WORKDIR/cells")

npat=0; ncells=0; nvm=0; nnp=0; ndiff=0; nbite=0; nbite2=0; nrung2=0
: > "$WORKDIR/diffs.txt"


while IFS=$'\t' read -r cls pat; do
    d="$WORKDIR/p$npat"; npat=$((npat + 1))
    if ! gen "$d" "$pat"; then
        bad "could not build a default-engine artifact for '$pat': $(head -2 "$d/err")"; continue
    fi
    if ! gen "$d/vm" "$pat" --engine=vm; then
        bad "could not build a --engine=vm artifact for '$pat': $(head -2 "$d/vm/err")"; continue
    fi
    if ! gen "$d/np" "$pat" -fno-possessify; then
        bad "could not build a -fno-possessify artifact for '$pat': $(head -2 "$d/np/err")"; continue
    fi

    # The oracle's answers for THIS pattern, in the cell list's order. `awk`
    # with an exact field compare, never a regex: a pattern is a regex and
    # matching one against a table of regexes is how a sweep silently compares
    # the wrong rows.
    # `AGPAT=... awk ... ENVIRON["AGPAT"]`, NOT `awk -v p="$pat"`. awk's `-v`
    # processes BACKSLASH ESCAPES in the value, so a pattern containing `\G`
    # arrives as `G` and matches nothing — measured: §4's whole oracle column
    # came back with 0 rows for every one of its 26 patterns. `ENVIRON` is the
    # only assignment form that passes the bytes through unchanged.
    AGPAT="$pat" awk -F'\t' '$1 == ENVIRON["AGPAT"] { print $4 }' \
        "$WORKDIR/oracle.tsv" > "$d/want"
    if [ "$(wc -l < "$d/want")" -ne "$NCELL" ]; then
        bad "'$pat': the oracle produced $(wc -l < "$d/want") answers for $NCELL cells — the sweep compares POSITIONALLY, so a short column would silently compare every later cell against the wrong answer"
        continue
    fi

    "$d/t"    < "$WORKDIR/cells" > "$d/got"   2>/dev/null
    "$d/vm/t" < "$WORKDIR/cells" > "$d/gotv"  2>/dev/null
    "$d/np/t" < "$WORKDIR/cells" > "$d/gotn"  2>/dev/null
    for arm in got:DEFAULT gotv:VM gotn:NOPOSS; do
        af="${arm%%:*}"; an="${arm#*:}"
        if [ "$(wc -l < "$d/$af")" -ne "$NCELL" ]; then
            bad "'$pat' [$an]: the batch driver produced $(wc -l < "$d/$af") answers for $NCELL cells — a dropped line shifts every later comparison"
            continue
        fi
        n_bad=$(paste "$d/$af" "$d/want" | awk -F'\t' '$1 != $2' | wc -l)
        case "$an" in
            DEFAULT) ncells=$((ncells + NCELL)) ;;
            VM)      nvm=$((nvm + NCELL)) ;;
            *)       nnp=$((nnp + NCELL)) ;;
        esac
        if [ "$n_bad" -ne 0 ]; then
            ndiff=$((ndiff + n_bad))
            printf '%s %s: %s cells differ, first:\n' "$an" "$pat" "$n_bad" >> "$WORKDIR/diffs.txt"
            paste "$WORKDIR/cells" "$d/$af" "$d/want" \
                | awk -F'\t' '$3 != $4 { print "   [" $1 "] @" $2 ": pcrec " $3 " / libpcre2 " $4 }' \
                | head -3 >> "$WORKDIR/diffs.txt"
        fi
    done

    # DOES THE CUT BITE on this subject set? Measured against the UNCUT twin's
    # own oracle column, not inferred from the pattern's shape.
    if [ "$cls" = "cut" ] || [ "$cls" = "cut2" ]; then
        tw="$(printf '%s' "$pat" | sed 's/(?>/(?:/g; s/\([*+?}]\)+/\1/g')"
        AGPAT="$tw" awk -F'\t' '$1 == ENVIRON["AGPAT"] { print $4 }' \
            "$WORKDIR/oracle.tsv" > "$d/twin"
        if [ "$(wc -l < "$d/twin")" -eq "$NCELL" ] \
           && ! cmp -s "$d/want" "$d/twin"; then
            if [ "$cls" = "cut" ]; then nbite=$((nbite + 1))
            else                        nbite2=$((nbite2 + 1)); fi
        fi
    fi

    # [M6.4.4] WHICH RUNG did this family member actually land on? READ OFF
    # THE ARTIFACT, never inferred from the quantifier's spelling — the whole
    # point of the family is to reach every possessive rung, and a
    # rung-selection change that quietly collapsed three forms onto one would
    # otherwise leave the claim "under EVERY possessive rung" true only in the
    # comment. The `--engine=vm` arm is the one that always has a VM artifact
    # to read.
    if [ "$cls" = "cut2" ]; then
        r2="$(sed -n 's/^#define RX_VM_RUNGS \(0x[0-9a-f]*\)u\{0,1\}.*/\1/p' \
              "$d/vm/gen.c" | head -1)"
        if [ -n "$r2" ]; then nrung2=$(( nrung2 | r2 )); fi
    fi
done < "$WORKDIR/patlist"

if [ "$ndiff" -eq 0 ]; then
    ok "§1/§2/§2b differential: $ncells DEFAULT (hybrid, prefilter LIVE), $nvm --engine=vm (prefilter OFF) and $nnp -fno-possessify cells over $npat patterns x $NSUBJ subjects x every startpos in [0, n] agree with libpcre2 exactly"
else
    bad "§1/§2/§2b differential: $ndiff cells disagree with libpcre2:"
    head -40 "$WORKDIR/diffs.txt" >&2
fi

# THE NON-VACUITY FLOORS. A sweep of patterns whose cut never bites would agree
# with libpcre2 on a compiler that ignored the atomicity entirely, which is the
# exact defect src/parse/registry.c's row comment has warned about since before
# there was a producer. `nbite` is MEASURED against each pattern's two-byte
# uncut twin rather than assumed from its shape.
if [ "$ncut" -ge 20 ] && [ "$ndead" -ge 8 ] && [ "$ncarve" -ge 10 ] \
   && [ "$nctl" -ge 3 ]; then
    ok "population: $ncut cut / $ndead dead-cut / $ncarve carve-out / $nctl control patterns (floors 20/8/10/3)"
else
    bad "population: $ncut cut / $ndead dead / $ncarve carve / $nctl control — below the floors 20/8/10/3, so the sweep is not measuring what it claims"
fi
if [ "$nbite" -ge 15 ]; then
    ok "non-vacuity: the cut MEASURABLY changes the answer on $nbite of the $ncut cut patterns (floor 15), measured against each one's two-byte UNCUT twin — so a compiler that lowered the group by ignoring the atomicity would be RED above, not green"
else
    bad "non-vacuity: only $nbite of $ncut cut patterns have a subject where the cut changes the answer (floor 15). The sweep above would pass on a compiler that ignored the atomicity"
fi
# [M6.4.4] THE FAMILY'S OWN NON-VACUITY, kept SEPARATE from the one above and
# not folded into it. The `cut` rows already clear 15 on their own, so a
# combined counter would have stayed green with this entire family answering
# its uncut twin — which is exactly the state the tree was in before the fix,
# and exactly what a merged floor cannot see.
if [ "$ncut2" -ge 25 ] && [ "$nbite2" -ge 18 ]; then
    ok "non-vacuity [two-exit / overlapping follow]: $ncut2 patterns in the family (floor 25) and the cut MEASURABLY changes the answer on $nbite2 of them (floor 18), each measured against its own two-byte uncut twin. This is the family the tier-1 miscompile lived in: before the fix these rows answered the UNCUT language on the frames rungs"
else
    bad "non-vacuity [two-exit / overlapping follow]: $ncut2 patterns (floor 25), only $nbite2 with a cut that changes the answer (floor 18) — the family that carries [M6.4.4]'s regression is not measuring what it claims"
fi
# EVERY POSSESSIVE RUNG, ASSERTED FROM THE ARTIFACTS. 0x1 cursor, 0x2
# frames-bounded, 0x4 frames-unbounded, 0x8 revdet, 0x10 counter.
if [ "$nrung2" -eq 31 ]; then
    ok "rung coverage [two-exit / overlapping follow]: the family's artifacts report RX_VM_RUNGS covering all five bits (0x1f = cursor | frames-bounded | frames-unbounded | revdet | counter), read off the emitted artifacts rather than inferred from the quantifier spellings"
else
    bad "rung coverage [two-exit / overlapping follow]: the family's artifacts cover RX_VM_RUNGS $(printf '0x%x' "$nrung2"), not 0x1f — a possessive rung has no member of this family on it, so the fix is unverified there"
fi
if [ "$ncells" -ge 20000 ]; then
    ok "cell floor: $ncells default-engine cells (floor 20000)"
else
    bad "cell floor: only $ncells default-engine cells (floor 20000)"
fi

# =========================================================================
# §3  THE DISCHARGE DIFFERENTIAL — pcrec against pcrec
# =========================================================================
# TWO ASSERTIONS, and they are different claims about the same rewrite.
#
#   ANSWERS. The discharge deletes a cut §2.2 proves dead; "changes no answer"
#   is its entire claim, and denying it with `-fno-atomic-discharge` is the
#   only way to check it. Asserted over EVERY class, not just `dead`: a
#   discharge that fired on a `cut` pattern (sabotage S91) shows up here as a
#   wrong answer rather than as a missing optimisation.
#
#   BYTES, for the DISCHARGED possessive spellings only. §5.4's
#   emission-neutrality: if the discharge fires, possessify's fixpoint
#   re-derives the identical verdict on the same quantifier and re-marks it, so
#   the VM artifact is byte-identical either way and the rewrite changes ENGINE
#   SELECTION and nothing else. Compared under `--engine=vm` because that is
#   where both builds produce a VM artifact to compare.
nd_ans=0; nd_bytes=0; nd_same=0; nd_engine=0; nd_barrier=0; ndd=0
while IFS=$'\t' read -r cls pat; do
    d="$WORKDIR/d$ndd"; ndd=$((ndd + 1))
    gen "$d/on"  "$pat"                        || continue
    gen "$d/off" "$pat" -fno-atomic-discharge   || continue
    "$d/on/t"  < "$WORKDIR/cells" > "$d/a" 2>/dev/null
    "$d/off/t" < "$WORKDIR/cells" > "$d/b" 2>/dev/null
    if [ "$(wc -l < "$d/a")" -ne "$NCELL" ] || [ "$(wc -l < "$d/b")" -ne "$NCELL" ]; then
        bad "§3 discharge: '$pat' produced a short answer column ($(wc -l < "$d/a") / $(wc -l < "$d/b") for $NCELL cells)"
    else
        nd_ans=$((nd_ans + NCELL))
        nd_bad=$(paste "$d/a" "$d/b" | awk -F'\t' '$1 != $2' | wc -l)
        if [ "$nd_bad" -ne 0 ]; then
            ndiff=$((ndiff + nd_bad))
            printf 'DISCHARGE %s: %s cells differ with and without -fno-atomic-discharge\n' \
                "$pat" "$nd_bad" >> "$WORKDIR/diffs.txt"
            paste "$WORKDIR/cells" "$d/a" "$d/b" \
                | awk -F'\t' '$3 != $4 { print "   [" $1 "] @" $2 ": on=" $3 " off=" $4 }' \
                | head -3 >> "$WORKDIR/diffs.txt"
        fi
    fi
    # THE ENGINE MOVED, which is what the discharge is FOR. Read off the
    # artifact rather than assumed: a `dead` pattern with no captures must
    # compile to a pure DFA with the discharge on, and to a VM artifact with it
    # off. THE DISCRIMINATOR IS THE VALUE, NOT THE PRESENCE ([DD-13]/D81,
    # 2026-08-25, found by the battery on d8608ca — r37's hazard, fourth
    # site): `RX_ENGINE` is now stamped on EVERY artifact, "dfa" or "vm";
    # this check read its ABSENCE as "a DFA" and went red on all ten
    # spellings the moment the DFA started stamping.
    if [ "$cls" = "dead" ]; then
        pcrec_run "$PCREC" --features all -p rx --no-captures -o "$d/e_on.c"  -- "$pat" 2>/dev/null
        pcrec_run "$PCREC" --features all -p rx --no-captures -fno-atomic-discharge \
                 -o "$d/e_off.c" -- "$pat" 2>/dev/null
        if grep -q '^#define RX_ENGINE "dfa"$' "$d/e_on.c" \
           && grep -q '^#define RX_ENGINE "vm"$' "$d/e_off.c"; then
            nd_engine=$((nd_engine + 1))
        else
            bad "§3 discharge: '$pat' has a §2.2-dead cut, so --no-captures must give a PURE DFA with the discharge ON and a VM artifact with it OFF; got on=$(grep -c '#define RX_ENGINE' "$d/e_on.c") off=$(grep -c '#define RX_ENGINE' "$d/e_off.c") RX_ENGINE defines"
        fi
        # EMISSION NEUTRALITY, on the VM path, for the discharged spellings.
        #
        # EMITTED TO STDOUT (`-o -`), never to two files. Every artifact
        # embeds its own `#include "<name>.h"`, so writing the two builds to
        # different paths makes them differ for a reason that has nothing to
        # do with the discharge — measured, on this rule's first run, as ten
        # spurious failures.
        # TWO PAIRS, because [M6.4.4] split what used to be one question.
        #   b_*  PRUNE ENABLED — what a user gets. The follow BARRIER is
        #        visible here and is asserted below, in its direction.
        #   p_*  PRUNE DISABLED on BOTH arms (`-fno-length-prune`) — the
        #        comparison §5.4's byte claim is actually about. The barrier
        #        acts on the length prune and on nothing else, so removing the
        #        prune AT THE SOURCE isolates the axis instead of sed-erasing
        #        two stamps and hoping that was all of it. MEASURED: with the
        #        prune off, the two arms are byte-identical again on every
        #        dead-cut pattern, which is what makes the split honest rather
        #        than a relaxation.
        pcrec_run "$PCREC" --features all -p rx --engine=vm --no-captures \
                 -o - -- "$pat" > "$d/b_on.c" 2>/dev/null
        pcrec_run "$PCREC" --features all -p rx --engine=vm --no-captures \
                 -fno-atomic-discharge -o - -- "$pat" > "$d/b_off.c" 2>/dev/null
        pcrec_run "$PCREC" --features all -p rx --engine=vm --no-captures \
                 -fno-length-prune -o - -- "$pat" > "$d/p_on.c" 2>/dev/null
        pcrec_run "$PCREC" --features all -p rx --engine=vm --no-captures \
                 -fno-length-prune -fno-atomic-discharge \
                 -o - -- "$pat" > "$d/p_off.c" 2>/dev/null
        nd_bytes=$((nd_bytes + 1))
        # TWO AXES ARE NORMALISED AND EXACTLY TWO, and both are things that
        # MUST differ — they are the flag doing its job, not the emitter
        # wobbling:
        #
        #   RX_ENGINE_WHY / .engine_why / the Engine: comment. With the
        #     discharge ON nothing forces the VM (the artifact is a VM one only
        #     because `--engine=vm` asked), so the why reads "--engine=vm";
        #     with it OFF the surviving A_ATOMIC forces it and the why names
        #     the construct. That IS the per-pattern split being observable.
        #   .flags. The artifact stamps which pcrec_options flags built it, and
        #     `-fno-atomic-discharge` is one of them (bit 12): 4 vs 4100.
        #
        # Everything else — every label, every slot, every cut, every capacity
        # — is compared byte for byte. MEASURED before the normalisation
        # existed: those four lines were the ONLY difference on all ten
        # dead-cut patterns, which is §5.4's claim confirmed rather than
        # weakened.
        # [M6.4.4] STILL TWO NORMALISED AXES — the comparison moved instead.
        #
        # §5.4 said the discharge "changes ENGINE SELECTION and nothing else",
        # and that was stated about an emitter which treated `A_ATOMIC` as
        # TRANSPARENT TO THE FOLLOW. The tier-1 miscompile the blinded D27
        # corpus found is the proof it is not: a live `A_ATOMIC` is a BARRIER,
        # because `(?>X)` matches X's own first success and the follow's
        # minimum width must not influence which success that is. So a
        # surviving cut now changes engine selection AND the length prune, and
        # on the PRUNE-ENABLED build the two arms genuinely differ — the whole
        # MRL apparatus (the macros, the window parameter, the call sites) is
        # present with the cut deleted and absent with it alive.
        #
        # SO THE PRUNE IS REMOVED AT THE SOURCE RATHER THAN SED-ERASED. `p_on`
        # and `p_off` are both built `-fno-length-prune`, which takes the one
        # axis the barrier acts on out of the question entirely and leaves
        # §5.4's claim standing EXACTLY where it is still true — MEASURED:
        # byte-identical on every dead-cut pattern once the prune is off.
        # Normalising the two prune STAMPS instead would have hidden a
        # thirteen-line machinery difference behind a two-line sed and called
        # the remainder a byte comparison.
        #
        # The barrier itself is not lost from the suite: it is asserted right
        # after, in its DIRECTION, on the prune-ENABLED pair.
        ag_norm() {
            sed -e 's/^\/\* Engine: .*/ENGINE-NORMALISED/' \
                -e 's/^#define RX_ENGINE_WHY .*/ENGINE-NORMALISED/' \
                -e 's/^ *\.engine_why = .*/ENGINE-NORMALISED/' \
                -e 's/^ *\.flags = .*/FLAGS-NORMALISED/' "$1"
        }
        ag_norm "$d/p_on.c"  > "$d/b_on.norm"
        ag_norm "$d/p_off.c" > "$d/b_off.norm"
        if cmp -s "$d/b_on.norm" "$d/b_off.norm"; then
            nd_same=$((nd_same + 1))
        else
            bad "§3 emission-neutrality: '$pat' emits DIFFERENT VM MACHINERY with and without the discharge, compared with the LENGTH PRUNE OFF on both arms so the follow barrier is out of the question (only the engine-why and flags stamps are normalised; this is everything else). §5.4 says possessify's fixpoint re-derives the identical verdict on the same quantifier, so with the prune removed the rewrite must change ENGINE SELECTION and nothing else: $(diff "$d/b_on.norm" "$d/b_off.norm" | head -4 | tr '\n' ' ')"
        fi
        # THE BARRIER, ASSERTED IN ITS DIRECTION. With the cut DELETED the
        # loop prunes against the follow and the artifact carries a real MRL
        # ceiling; with the cut ALIVE the follow does not cross it, so there is
        # no follow-derived ceiling left to stamp and the value is "none". A
        # fix that silently stopped scoping the follow would show up here as
        # "none" disappearing from the OFF arm — which is the miscompile
        # coming back, caught on the BYTES rather than only on an answer.
        on_ceil="$(sed -n 's/^#define RX_VM_PRUNE_CEILING //p' "$d/b_on.c" | head -1)"
        off_ceil="$(sed -n 's/^#define RX_VM_PRUNE_CEILING //p' "$d/b_off.c" | head -1)"
        if [ "$off_ceil" = '"none"' ] && [ "$on_ceil" != '"none"' ]; then
            nd_barrier=$((nd_barrier + 1))
        else
            bad "§3 follow barrier: '$pat' — with the cut ALIVE (-fno-atomic-discharge) the follow must not cross it, so the VM artifact must carry NO follow-derived MRL ceiling; got on=$on_ceil off=$off_ceil (want on!=\"none\", off=\"none\")"
        fi
    fi
done < "$WORKDIR/patlist"

if [ "$nd_ans" -ge 5000 ] && [ "$nd_engine" -ge 8 ] && [ "$nd_bytes" -ge 8 ] \
   && [ "$nd_same" -eq "$nd_bytes" ] && [ "$nd_barrier" -eq "$nd_bytes" ]; then
    ok "§3 discharge: $nd_ans answer cells identical with and without -fno-atomic-discharge (floor 5000); $nd_engine dead-cut patterns move DFA<->VM as the flag says (floor 8); all $nd_bytes of them emit byte-identical VM code either way with the length prune off on both arms (§5.4 emission-neutrality, isolated at the source by [M6.4.4]); and all $nd_barrier of them show the FOLLOW BARRIER in its direction on the prune-ENABLED build — a follow-derived MRL ceiling with the cut deleted, none with it alive"
elif [ "$fail" -eq 0 ]; then
    bad "§3 discharge: populations too small — $nd_ans answer cells (floor 5000), $nd_engine engine moves (floor 8), $nd_same/$nd_bytes byte-identical, $nd_barrier/$nd_bytes barrier-directional"
fi

# =========================================================================
# §4  THE THREE ENTRIES
# =========================================================================
# Driven over the CUT class only: the entries' claim is that §4's ceiling
# hazard cannot reach them, and the R3a shapes are where it would.
ne_cells=0; ne_bad=0; ne_pat=0
# The `\G(?:PAT)` wraps, in ONE more oracle pass. `\G` binds only its first
# branch without the `(?:...)`, which would silently turn the oracle into a
# different question for exactly the alternation patterns §4 cares most about.
: > "$WORKDIR/entpats"
while IFS=$'\t' read -r cls pat; do
    [ "$cls" = "cut" ] || continue
    printf 'ent\t\\G(?:%s)\n' "$pat" >> "$WORKDIR/entpats"
done < "$WORKDIR/patlist"
python3 "$SCRIPT_DIR/atomic_oracle.py" "$WORKDIR/entpats" "$WORKDIR/subjects" \
    "$WORKDIR/entoracle.tsv" 2>/dev/null || {
    bad "§4: could not compute the \\G match-here oracle column"; }
while IFS=$'\t' read -r cls pat; do
    [ "$cls" = "cut" ] || continue
    d="$WORKDIR/e$ne_pat"; ne_pat=$((ne_pat + 1))
    mkdir -p "$d"
    pcrec_run "$PCREC" --features all -p rx -o "$d/gen.c" -- "$pat" 2>/dev/null || continue
    $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/atomic_entries.c" "$d/gen.c" \
        2>"$d/err" || { bad "§4: could not build the entries driver for '$pat': $(head -2 "$d/err")"; continue; }
    # THE MATCH-HERE ORACLE column for this pattern, computed in the same
    # single oracle pass as everything else: libpcre2's answer for `\G(?:PAT)`
    # at `sp` IS the match-here answer for `PAT` at `sp`.
    AGPAT="\\G(?:$pat)" awk -F'\t' '$1 == ENVIRON["AGPAT"] { print $4 }' \
        "$WORKDIR/entoracle.tsv" > "$d/hw"
    if [ "$(wc -l < "$d/hw")" -ne "$NCELL" ]; then
        bad "§4: the \\G oracle column for '$pat' has $(wc -l < "$d/hw") rows for $NCELL cells"
        continue
    fi
    sed 's/\t/ /' "$WORKDIR/cells" | "$d/t" > "$d/ent" 2>/dev/null
    if [ "$(wc -l < "$d/ent")" -ne "$NCELL" ]; then
        bad "§4: the entries driver for '$pat' produced $(wc -l < "$d/ent") lines for $NCELL cells"
        continue
    fi
    ne_cells=$((ne_cells + NCELL))
    ne_this=$(paste "$WORKDIR/cells" "$d/ent" "$d/hw" | awk -F'\t' '
        {
            sp = $2; line = $3; hw = $4
            mh = line; sub(/.*\| match /, "", mh); sub(/ .*/, "", mh)
            cp = line; sub(/.*\| caps /, "", cp);  sub(/ .*/, "", cp)
            if (hw == "nomatch") { if (mh + 0 >= 0) { print; bad++ } }
            else {
                split(hw, a, " "); want = a[3] - sp
                if (mh + 0 != want || cp + 0 != want) { print; bad++ }
            }
        }' | wc -l)
    if [ "$ne_this" -ne 0 ]; then
        ne_bad=$((ne_bad + ne_this))
        printf 'ENTRY %s: %s cells disagree with libpcre2 (via \\G(?:PAT))\n' \
            "$pat" "$ne_this" >> "$WORKDIR/diffs.txt"
    fi
done < "$WORKDIR/patlist"
if [ "$ne_bad" -eq 0 ] && [ "$ne_cells" -ge 5000 ]; then
    ok "§4 entries: $ne_cells cells over $ne_pat cut patterns — <prefix>_match and <prefix>_match_caps agree with libpcre2's own anchored answer (\\G(?:PAT)) on the CONSUMED LENGTH, which is the number a D38 callout advances by and is NOT the reported span's width"
elif [ "$ne_bad" -ne 0 ]; then
    bad "§4 entries: $ne_bad of $ne_cells cells disagree:"
    grep '^ENTRY' "$WORKDIR/diffs.txt" | head -20 >&2
else
    bad "§4 entries: only $ne_cells cells (floor 5000) — the entries sweep is not populated"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
