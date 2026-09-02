#!/usr/bin/env bash
# tests/codegen/run_vm_frameless.sh — [OPT-VMFL]: `<PREFIX>_VM_FRAMELESS`,
# held to the artifact's own text rather than to the predicate that wrote it.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# A VM program that emits no `RX_PUSH` site and no linked call has no resume
# frame to pop, so [CC-CLANG] omits the fail label's pop-and-resume `goto *`
# dispatch entirely — clang refuses an indirect goto in a function with no
# address-of-label expression, and the dispatch was unreachable there anyway.
# `<PREFIX>_VM_FRAMELESS` is that fact stamped (`docs/spec/match_api.md`
# §6.3, family (b); `docs/dev/optvmfl_step0.md` §4.2 is the proposal).
#
#     #define RX_VM_FRAMELESS 1   /* no push, no linked call, no `goto *` */
#     #define RX_VM_FRAMELESS 0   /* the program has a resume mechanism */
#
# THE CONTRACT, in the spec's own words: **1 iff the artifact's VM program
# emits no `RX_PUSH` site and no linked call, i.e. the fail label has no
# pop-and-resume dispatch.** Unconditional on every VM artifact including a
# HYBRID; never defined on a pure-DFA artifact.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3, and it is the whole design of this file. The
# stamp's value is `!has_push`, a BOOL the emitter computes. This check never
# reads that bool: it counts `goto *` occurrences in the EMITTED TEXT, which
# `emit_vm.c` writes at the fail label and at each shared callee body, and
# asserts the biconditional against it. A stamp that drifted from the
# dispatch it names is a RED here, in both directions.
#
# THE ENGINE DISCRIMINATOR IS `goto rx_L0;` — the VM's program entry, matcher
# text — and NOT `RX_ENGINE`. Reading a macro to decide which artifacts to
# check the macros on is the circularity `run_dfa_stamps.sh` refuses in a
# comment, and this file inherits the refusal.
#
# =========================================================================
# THE `goto *` COUNT IS SCOPED TO THE VM PROGRAM'S OWN FUNCTION, and this
# file's first run is what said it must be
# =========================================================================
# `run_codegen_tests.sh`'s `[DD-14-RECURSION rule 1]` counts `goto *` with a
# WHOLE-FILE grep, and it is right to: it compiles under `--engine=vm`, which
# turns the hybrid prefilter OFF (D44/R21 E-6), so the artifact contains no
# DFA scan and every indirect jump in it is the VM's.
#
# THAT DOES NOT TRANSFER TO THE AXES THIS FILE SWEEPS. On the default and
# `-fprefilter` axes a hybrid inlines a DFA scan, and an `ENG_ATTEMPT` scan's
# STEP IS A COMPUTED GOTO (`goto *<p>_targets_K[class]`) — its states are code
# labels. MEASURED on the first run: `(?m)^(a|b)$` carries SIX `goto *`, every
# one inside `static int rx_prefilter(...)`, and ZERO inside the VM program.
# Its `RX_VM_FRAMELESS 1` was correct and this check was wrong — 199 artifacts
# of the sweep, all of them `(?m)^`-shaped, i.e. exactly the population that
# routes a DFA scan to `ENG_ATTEMPT`.
#
# So the count runs from the program entry `    goto rx_L0;` to the enclosing
# function's closing brace at column 0, which contains the fail label and
# every shared callee region and excludes the inlined prefilter above it.
#
# =========================================================================
# WHY THE FORCE AXIS IS SWEPT AND NOT ONLY THE DEFAULT
# =========================================================================
# `-fprefilter` builds a HYBRID out of a pattern that would otherwise be a
# pure DFA artifact, which is the population where "unconditional on every VM
# artifact, hybrids INCLUDED" is actually at risk: the hybrid's VM program is
# the same emitter's output, but nothing else in the tree compiles that
# population, so a stamp emitted under a condition that happened to hold on
# the default axis would pass a default-only sweep. It is the same K35 shape
# `[OPT-5]` STEP 2's own `N_hybrid_pinned` had to be re-measured for.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "vm-frameless: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: vm-frameless: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

emit() { # emit <outfile> <pattern> [extra args...]
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --features all "$@" -o "$out" -- "$pat" >/dev/null 2>&1
}

# `goto *` INSIDE THE VM PROGRAM'S OWN FUNCTION — see the header. The region
# opens at the program entry and closes at the first column-0 `}`.
vm_goto_star() {
    awk '/^    goto rx_L0;/ { inb = 1 }
         inb && /goto \*/   { n++ }
         inb && /^}/        { inb = 0 }
         END { print n + 0 }' "$1"
}

# =========================================================================
# §1 NAMED WITNESSES — both values, spelled here, with the mechanism asserted
# =========================================================================
# Expectations are LITERALS from the spec's own IFF, never harvested. Each row
# also asserts the `goto *` count, so a witness cannot pass by stamping a
# value whose machinery is absent or present.
witness() { # witness <label> <pattern> <expected 0|1> [args...]
    local lbl="$1" pat="$2" want="$3"; shift 3
    local f="$WORKDIR/w.c"
    emit "$f" "$pat" "$@" || { bad "§1 [$lbl] '$pat' did not compile"; return; }
    grep -q "^    goto rx_L0;" "$f" \
        || { bad "§1 [$lbl] '$pat' produced no VM program — this witness cannot test a VM-only macro"; return; }
    local got; got="$(grep -m1 '^#define RX_VM_FRAMELESS ' "$f" | awk '{print $3}')"
    [ -n "$got" ] || { bad "§1 [$lbl] '$pat' is a VM artifact and defines NO RX_VM_FRAMELESS — the macro is unconditional (spec §6.3)"; return; }
    [ "$got" = "$want" ] || bad "§1 [$lbl] '$pat' stamps RX_VM_FRAMELESS $got, expected $want"
    local n; n="$(vm_goto_star "$f")"
    if [ "$want" = 1 ]; then
        [ "$n" -eq 0 ] || bad "§1 [$lbl] '$pat' stamps FRAMELESS 1 but its VM program contains $n \`goto *\` — the stamp and the dispatch have come apart"
    else
        [ "$n" -ge 1 ] || bad "§1 [$lbl] '$pat' stamps FRAMELESS 0 but its VM program contains NO \`goto *\` — the stamp claims a resume mechanism the program does not have"
    fi
}

# TWO WITNESSES WERE WRONG ON THE FIRST RUN AND THE REPLACEMENTS ARE THE
# LESSON, so they are recorded rather than quietly swapped.
#   `(a|b)(?1)(?1)` was chosen as a LINKED-call row and is nothing of the
#   kind: `src/opt/altcls.c` merges `(a|b)` to a class before any engine
#   exists, so the body has no choice point, and wave G then SPLICES both
#   call sites (`RX_VM_CALL_SPLICED 2`, `_LINKED 0`) — a spliced target emits
#   no region and no `RX_RETURN`. The artifact is genuinely frameless and
#   stamps 1. A row that needs a LINKED call needs a target that cannot be
#   spliced, i.e. one in a CYCLE.
#   `foo[0-9]+bar -fprefilter` is REFUSED, not compiled: the pattern is
#   capture-free, so it compiles to the pure DFA engine, and `-fprefilter` is
#   DO-OR-DIE (there is no VM artifact to attach a prefilter to). A forced
#   hybrid needs a capture-bearing pattern.
witness "straight-line capture"  '(a)b'          1
witness "backref, no choice"     '(a)\1'         1
witness "two cursor loops"       '(a*)(b*)c'     1
witness "recursive call"         '^(a(?1)?b)$'   0
witness "DEFINE'd recursion"     '(?(DEFINE)(?<w>a(?&w)?b))(?&w)' 0
witness "hybrid (forced)"        '(foo)[0-9]+bar'  1 -fprefilter
[ "$fail" -eq 0 ] && ok "§1 six named witnesses stamp the documented value and their \`goto *\` count agrees with it, on both values and on a FORCED HYBRID"

# THE NEGATIVE CONTROL FOR THE VALUE SET. Without it every row above would
# pass on a compiler that stamped one constant: four rows expect 1 and two
# expect 0, so a constant fails — but only if BOTH values are genuinely
# reachable, which this asserts rather than infers from the rows.
w1=0; w0=0
for p in '(a)b' '(a)\1' '(a*)(b*)c' '^(a(?1)?b)$' 'a(?R)?b'; do
    emit "$WORKDIR/n.c" "$p" || continue
    v="$(grep -m1 '^#define RX_VM_FRAMELESS ' "$WORKDIR/n.c" | awk '{print $3}')"
    [ "$v" = 1 ] && w1=$((w1 + 1)); [ "$v" = 0 ] && w0=$((w0 + 1))
done
if [ "$w1" -ge 1 ] && [ "$w0" -ge 1 ]; then
    ok "§1 both values are live in the witness set ($w1 frameless, $w0 pushing) — a compiler stamping a constant fails this file"
else
    bad "§1 only ONE value is reachable in the witness set ($w1 frameless, $w0 pushing): every row above is comparing a build against one constant"
fi

# =========================================================================
# §2 A PURE-DFA ARTIFACT DOES NOT DEFINE IT
# =========================================================================
# The other half of the IFF, and it is a real claim rather than a formality:
# the macro is emitted by `emit_vm.c`, and `pcrec_emit_dfa_engine` is SHARED
# with that file, so a stamp written one level too high would land on every
# DFA artifact in the tree.
emit "$WORKDIR/d.c" 'abc' --no-captures || bad "§2 'abc --no-captures' did not compile"
if grep -q "^    goto rx_L0;" "$WORKDIR/d.c"; then
    bad "§2 the pure-DFA witness produced a VM program — this section cannot test the DFA side"
elif grep -q 'RX_VM_FRAMELESS' "$WORKDIR/d.c"; then
    bad "§2 a pure-DFA artifact defines RX_VM_FRAMELESS — it has no resume stack and no VM program, so the macro is meaningless there (spec §6.3: the (b) family is VM-only)"
else
    ok "§2 a pure-DFA artifact defines NO RX_VM_FRAMELESS, which is the other half of the macro's IFF"
fi

# =========================================================================
# §3 THE CORPUS SWEEP, ON THE DEFAULT AND FORCE AXES
# =========================================================================
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
if [ "$npat" -lt 2620 ]; then
    bad "vm-frameless: corpus extraction found only $npat patterns, below the 2620 floor (K35)"
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

NSHARD="${PROCS:-$(nproc)}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh"
split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
    || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }

# Sharded by LINE CHUNKS of the pattern file, never an `xargs` over pattern
# TEXT: a pattern is arbitrary bytes and every quoting scheme for passing one
# as an argument is a bug waiting to be found by the corpus.
cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD: worker could not load pcrec_run"; exit 1; }
art="$WORKDIR/a.$$.c"
trap 'rm -f "$art"' EXIT
one() { # one <axis-label> <extra pcrec args...>
    local ax="$1"; shift
    if ! pcrec_run "$PCREC" --features all -p rx "$@" -o - -- "$pat" > "$art" 2>/dev/null; then
        echo "REFUSED-$ax"; return
    fi
    # ONE `awk` per artifact, and its `goto *` count is SCOPED to the VM
    # program's own function — a hybrid's inlined ENG_ATTEMPT scan steps by
    # computed goto, so a whole-file count is not this macro's subject (the
    # header carries the measurement that said so).
    set -- $(awk '
        /^    goto rx_L0;/            { vm=1; inb=1 }
        /^#define RX_VM_FRAMELESS /   { n++; val=$3 }
        inb && /goto \*/              { g++ }
        inb && /^}/                   { inb=0 }
        END { printf "%d %d %s %d\n", vm+0, n+0, (n?val:"-"), g+0 }
    ' < "$art")
    local vm="$1" n="$2" val="$3" g="$4"
    if [ "$vm" -eq 0 ]; then
        echo "DFA-$ax"
        [ "$n" -eq 0 ] || { echo "BAD: RX_VM_FRAMELESS on an artifact with no VM program ($ax): $pat"; }
        return
    fi
    echo "VM-$ax"
    [ "$n" -eq 1 ] || { echo "BAD: RX_VM_FRAMELESS appears $n times on a VM artifact, expected exactly 1 ($ax): $pat"; return; }
    case "$val" in 0|1) ;; *) echo "BAD: RX_VM_FRAMELESS '$val' is not 0 or 1 ($ax): $pat"; return ;; esac
    # THE BICONDITIONAL, against the emitted TEXT and never against the bool.
    if [ "$val" = 1 ]; then
        echo "FRAMELESS-$ax"
        [ "$g" -eq 0 ] || echo "BAD: stamps FRAMELESS 1 but the VM program contains $g 'goto *' ($ax): $pat"
    else
        echo "PUSHING-$ax"
        [ "$g" -ge 1 ] || echo "BAD: stamps FRAMELESS 0 but the VM program contains NO 'goto *' ($ax): $pat"
    fi
}
while IFS= read -r pat; do
    one default
    one force -fprefilter
done
WORKER

export ROOT_DIR PCREC WORKDIR
for i in $(seq 0 $((NSHARD - 1))); do
    f="$(printf '%s/sh/p%02d' "$WORKDIR" "$i")"
    [ -f "$f" ] || continue
    bash "$WORKDIR/worker.sh" < "$f" > "$WORKDIR/out.$i" 2>&1 &
done
wait
cat "$WORKDIR"/out.* > "$WORKDIR/all.out" 2>/dev/null

tok() { grep -c "^$1\$" "$WORKDIR/all.out" 2>/dev/null || true; }
n_bad=$(grep -c '^BAD: ' "$WORKDIR/all.out" 2>/dev/null || true)
for ax in default force; do
    printf '    %-8s VM %s (frameless %s / pushing %s), DFA %s, refused %s\n' \
        "$ax:" "$(tok "VM-$ax")" "$(tok "FRAMELESS-$ax")" "$(tok "PUSHING-$ax")" \
        "$(tok "DFA-$ax")" "$(tok "REFUSED-$ax")"
done

if [ "$n_bad" -eq 0 ]; then
    ok "§3 on all $npat corpus patterns, on BOTH the default and the -fprefilter FORCE axis: every VM artifact defines RX_VM_FRAMELESS exactly once with a documented value, no non-VM artifact defines it, and the value agrees with the VM PROGRAM's own \`goto *\` count in both directions"
else
    bad "§3 the corpus sweep reported $n_bad failures; first eight:"
    grep -m8 '^BAD: ' "$WORKDIR/all.out" >&2
fi

# BOTH VALUES MUST HAVE A LIVE CORPUS POPULATION, on each axis. A
# biconditional only ever checked on one of its sides is a vacuous pass, and
# the population that vanishes is the check that cannot fail — [OPT-1]'s own
# recorded lesson about `tiered`. FLOORS rather than equalities so ordinary
# corpus churn does not trip them.
for ax in default force; do
    nf="$(tok "FRAMELESS-$ax")"; np="$(tok "PUSHING-$ax")"
    if [ "$nf" -ge 100 ] && [ "$np" -ge 100 ]; then
        ok "§3 [$ax] both sides of the biconditional have a live population (frameless $nf, pushing $np, floors 100/100)"
    else
        bad "§3 [$ax] one side of the biconditional has collapsed (frameless $nf, pushing $np, floors 100/100) — the sweep above is passing on whichever side survives"
    fi
done

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0

# =========================================================================
# SABOTAGE TRANSCRIPTS
# =========================================================================
# Recorded at landing, 2026-09-02. This file's failing directions were
# exercised by hand rather than by a permanent mech row, and that is stated
# rather than implied: [OPT-VMFL] STEP 0's own charter is a stamp, and the
# BEHAVIOUR its bool gates (the fail label's dispatch omission) already has
# its own coverage in `run_codegen_tests.sh`'s `[DD-14-RECURSION rule 1]`,
# whose `goto *` relation moved to `(has_push ? 1 : 0) + shared-callee-bodies`
# at [CC-CLANG] for exactly this fact.
#
#   PLANT 1 -- THE STAMP INVERTED (`has_push ? 1 : 0`). This file: RED in §1
#     on all six witnesses and in §3 on every VM artifact of both axes. No
#     answer moves anywhere in the tree, which is why the stamp needs a
#     structural check at all.
#
#   PLANT 2 -- THE STAMP RECOMPUTED FROM `v.npush` rather than reading the
#     shared bool (the derivation the memo's §4.2 rejects by name). This file:
#     RED in §3 on the artifacts where the resume-point cap's ESTIMATE
#     disagrees with what was emitted — the counter rung's unbounded arm once
#     drove `npush` negative, which is the measured reason the dispatch gate
#     itself does not read it.
#
#   PLANT 3 -- THE STAMP EMITTED CONDITIONALLY (only when frameless). This
#     file: RED in §1 (every `want=0` witness reports the macro absent) and in
#     §3 (`appears 0 times`). That is [OPT-1]'s `_FAST_FRAMES` lesson: a fact
#     readable by a macro's ABSENCE is not a fact a consumer can `#if` on.
