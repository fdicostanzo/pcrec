#!/usr/bin/env bash
# tests/codegen/run_cpset_structure.sh — [M5.0] STAGE 1's STRUCTURAL CHECKS,
# i.e. THE HALF OF THE ACCEPTANCE A NO-OP FAILS.
#
# Design: docs/design/utf8_design.md §8.1.1 (r54 BLOCKING C1), which is the
# panel finding this file exists to answer, and it is worth stating in full
# because a structural check always looks like ceremony beside a gate:
#
#   > Stage 1 is a pure refactor whose acceptance was *one* instrument —
#   > byte-identity — and **byte-identity is exactly the bar a NO-OP passes.**
#   > A stage-1 branch that changed nothing at all, or that built the interval
#   > pipeline and then never used it, scores 100%.
#
# `run_encoding_identity.sh` is the gate. This is the control on the gate. They
# ship together and neither is stage 1's acceptance alone.
#
# EVERY CHECK HERE READS THE TREE, NOT AN ARTIFACT, and that is the division of
# labour rather than a shortcut: what stage 1 changed is a REPRESENTATION, and
# a representation that has been correctly refactored is by construction
# invisible in the emitted text. There is nothing for an artifact-reading check
# to see, which is precisely why the gate alone cannot tell a refactor from a
# no-op.
#
# Usage: bash tests/codegen/run_cpset_structure.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1,
#      CPSET_STRUCTURE_REF=<sha> to move the RED demonstration's base.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
. "$ROOT_DIR/tests/lib/cc_resolve.sh"     # [MACPORT] a real GNU gcc, for 2d
KEEP="${KEEP:-0}"
REFCOMMIT="${CPSET_STRUCTURE_REF:-cb546b3a}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "cpset-structure: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

SRC="$ROOT_DIR/src"

# ===========================================================================
# CHECK 1 — THE INTERVAL PIPELINE EXISTS AND EVERY PRODUCER GOES THROUGH IT
# ===========================================================================
#
# §8.1.1: *"A structural check that `struct Ast`'s `A_CLASS` payload is the
# interval form (no `bits[32]` member survives), and that the byte-tier
# producers (`\d`, `\w`, `\s`, POSIX classes, ranges, literals, `.`, the two
# negation sites) reach it."*
#
# ITS FAILING DIRECTION IS THE WHOLE POINT, and §9.2 makes it an obligation
# rather than a nicety: *"Check 1 must be demonstrated RED against
# `git archive HEAD` in the same wave, or it is a check nobody has seen fail."*
# That demonstration is section 1R below and it is not optional — a check whose
# red has never been observed is a check whose needles may match nothing.

echo "== CHECK 1: the interval payload exists and every producer reaches it =="

# 1a. THE PAYLOAD ITSELF. The positive needle names the declaration; the
# NEGATIVE needle is the one that matters, because a branch that ADDED an
# interval list beside the bitmap — two representations, which §2.2's second
# bullet forbids by name — would satisfy the positive half alone.
if grep -q 'const PcrecCpRange \*iv; int n; } cls;' "$SRC/core/internal.h"; then
    ok "[1a] Ast's A_CLASS payload is the interval form"
else
    bad "[1a] src/core/internal.h does not declare the interval A_CLASS payload"
fi
# THE NEEDLE READS CODE, NOT PROSE, and `decomment` is why. This tree's
# comments legitimately QUOTE the old spelling — `src/opt/revdet.c` and
# `src/core/internal.h` both have to name `u.cls.bits` to explain what the D70
# clobber survey was about, and `src/gen/emit_vm.c:1511` names it to say what
# it stopped doing. A needle that could not tell a quotation from a read would
# force those comments to be deleted or misspelled, which trades a real
# explanation for a check's convenience. The filter drops whole-line `//`
# comments and block-comment continuation lines (` * ...`), which is this
# codebase's only comment style below a declaration.
decomment() { grep -v '^[[:space:]]*\(\*\|/\*\|//\)' "$@"; }
# `--include` scopes the sweep to SOURCE, and the exclusion is not laziness:
# `src/core/CLAUDE.md` NARRATES the D70 clobber survey, whose whole subject is
# the 32-byte layout, and §2.2.3 requires that narration to be kept and
# re-derived rather than deleted. A needle that could not tell documentation
# from code would make the obligation and the check contradict each other.
BITS_READS="$(cd "$ROOT_DIR" && grep -rn --include='*.c' --include='*.h' 'u\.cls\.bits' src | grep -v '^[^:]*:[0-9]*:[[:space:]]*\(\*\|/\*\|//\)' || true)"
if [ -n "$BITS_READS" ]; then
    bad "[1a] a CODE reference to u.cls.bits survives in src/ — the 32-byte bitmap payload was supposed to be GONE, not renamed, and r54 E1's read is only inexpressible while it does not type-check:"
    printf '%s\n' "$BITS_READS" | head -10 >&2
else
    ok "[1a] no CODE reference to u.cls.bits survives anywhere in src/ — E1's read does not type-check (comments quoting the old spelling are permitted and expected)"
fi
if grep -n 'uint8_t bits\[32\]; } cls;' "$SRC/core/internal.h" >/dev/null 2>&1; then
    bad "[1a] the 32-byte bitmap member survives in the A_CLASS payload"
else
    ok "[1a] no bits[32] member survives in the A_CLASS payload"
fi

# 1b. THE BUILDER AND ITS FILE. `src/core/cpset.c` is the representation's one
# home; a branch that spread the merge logic across the producers would pass
# every other needle here.
for fn in pcrec_cpset_add pcrec_cpset_complement pcrec_cpset_publish \
          pcrec_cpset_add_bits pcrec_cls_bits pcrec_cls_bits_widen; do
    if grep -q "^[a-z].*$fn(" "$SRC/core/cpset.c"; then
        ok "[1b] src/core/cpset.c defines $fn"
    else
        bad "[1b] src/core/cpset.c does not define $fn"
    fi
done

# 1c. EVERY PRODUCER REACHES THE BUILDER. §8.1.1 names eight producers; they
# live at four constructors in `src/parse/parse.c`, and the check is that each
# constructor publishes an interval set rather than that each SPELLING appears
# — `\d`, `\w`, `\s` and the POSIX classes are all registry rows funnelling
# through `pcrec_ast_class_from_bits`, and needling their spellings would be
# needling `src/parse/registry.c`'s table rather than the pipeline.
#
#   char_node                  literals and character escapes
#   pcrec_ast_class_from_bits  \d \w \s, POSIX classes, every module port
#   p_class                    ranges, members, and its own negation
#   the `.` arm                every code point but \n
#
# The four are asserted by their publish sites, which is the ONE operation a
# producer cannot skip: a constructor that built a set and never published it
# emits the arena's zero, the EMPTY class.
NPUB="$(grep -c 'pcrec_cpset_publish(' "$SRC/parse/parse.c" || true)"
if [ "${NPUB:-0}" -ge 4 ]; then
    ok "[1c] all four class constructors in src/parse/parse.c publish an interval set ($NPUB publish sites, floor 4)"
else
    bad "[1c] only ${NPUB:-0} publish site(s) in src/parse/parse.c, want at least 4 (char_node, pcrec_ast_class_from_bits, p_class, the '.' arm) — a constructor that does not publish emits the arena's zero, i.e. the EMPTY class"
fi
# THE TWO NEGATION SITES, named separately because §2.7.1 is the BLOCKING
# finding they come from: both must complement within the ENCODING's universe,
# never within a constant.
NNEG="$(grep -c 'pcrec_cpset_complement(&\?[a-z]*, cls_universe(cx))' "$SRC/parse/parse.c" || true)"
if [ "${NNEG:-0}" -ge 2 ]; then
    ok "[1c] both negation sites complement within cls_universe(cx), the ENCODING's universe ($NNEG sites)"
else
    bad "[1c] found ${NNEG:-0} negation site(s) complementing within cls_universe(cx), want 2 — a complement taken within a hard-coded universe is r54 E2, and under a wider encoding it silently narrows every negated class"
fi
if grep -q 'e->max_cp' "$SRC/parse/parse.c" && grep -q 'unsigned    max_cp;' "$SRC/gen/enc/enc.h"; then
    ok "[1c] the universe is read from PcrecEnc.max_cp, the backend's own scalar"
else
    bad "[1c] the complement universe does not come from PcrecEnc.max_cp"
fi

# 1d. THE LOWERING EXISTS AND IS CALLED AT THE DERIVED POSITION. A branch that
# built the payload and never introduced the pass would pass 1a-1c.
if grep -q 'Ast \*pcrec_lower_enc(Ctx \*cx, Ast \*root)' "$SRC/opt/lower_enc.c"; then
    ok "[1d] src/opt/lower_enc.c defines the encoding lowering"
else
    bad "[1d] src/opt/lower_enc.c does not define pcrec_lower_enc"
fi
# THE POSITION IS CHECKED AS AN ORDER, not as a line number, because a line
# number is a fact about today's file and the ORDER is the design (§2.1.2,
# §13 obligation 4). Three assertions, one per constraint.
CC_LINE="$(grep -n 'pcrec_callgraph_build(&cx, root);'  "$SRC/core/compile.c" | head -1 | cut -d: -f1)"
PR_LINE="$(grep -n 'pcrec_postresolve(&cx, root);'      "$SRC/core/compile.c" | head -1 | cut -d: -f1)"
LO_LINE="$(grep -n 'root = pcrec_lower_enc(&cx, root);' "$SRC/core/compile.c" | head -1 | cut -d: -f1)"
NFA_LINE="$(grep -n 'pcrec_build_nfa(&cx, root,'        "$SRC/core/compile.c" | head -1 | cut -d: -f1)"
VM_LINE="$(grep -n 'pcrec_emit_vm(&cx, root);'          "$SRC/core/compile.c" | head -1 | cut -d: -f1)"
if [ -z "$LO_LINE" ]; then
    bad "[1d] src/core/compile.c never calls pcrec_lower_enc — the pipeline exists and nothing runs it, which is the 'built it and never used it' branch §8.1.1 names"
elif [ -z "$CC_LINE" ] || [ -z "$PR_LINE" ] || [ -z "$NFA_LINE" ] || [ -z "$VM_LINE" ]; then
    bad "[1d] could not locate one of the four pass-chain anchors in src/core/compile.c (callgraph=$CC_LINE postresolve=$PR_LINE nfa=$NFA_LINE emit_vm=$VM_LINE) — this check has stopped being able to express what it checks"
else
    if [ "$LO_LINE" -lt "$NFA_LINE" ] && [ "$LO_LINE" -lt "$VM_LINE" ]; then
        ok "[1d] constraint 1: the lowering ($LO_LINE) runs before pcrec_build_nfa ($NFA_LINE) and pcrec_emit_vm ($VM_LINE), the two byte-only consumers"
    else
        bad "[1d] constraint 1 VIOLATED: the lowering ($LO_LINE) does not precede both byte-only consumers (nfa=$NFA_LINE, emit_vm=$VM_LINE) — that is r54 E1, a silent miscompile rather than a refusal"
    fi
    if [ "$LO_LINE" -gt "$PR_LINE" ]; then
        ok "[1d] constraint 3: the lowering ($LO_LINE) runs after pcrec_postresolve ($PR_LINE), which asks lookbehind widths in CHARACTERS"
    else
        bad "[1d] constraint 3 VIOLATED: the lowering ($LO_LINE) runs before pcrec_postresolve ($PR_LINE), which would make a character-width walk count BYTES"
    fi
    # CONSTRAINT 2 IS DELIBERATELY NOT ASSERTED HERE, and the absence is a
    # finding rather than an omission. §2.1.2 states it as "the lowering
    # cannot run before :961"; this wave's own experiment
    # (docs/dev/lanes/utf8s1_report.md, wave-task (a)) MEASURED the opposite —
    # a REBUILDING lowering at the design's position moves 45 of
    # tests/recursion's 179 artifacts and moves none above the call graph. The
    # constraint is real and points the other way, it collides with constraint
    # 3, and which position survives is a ruling this lane escalated rather
    # than took. Asserting today's order here would pin a position the
    # measurement does not support; asserting the other would pin one the
    # design does not. So the check states the two constraints it can stand
    # behind and NAMES the third as open, which is the honest shape.
    echo "NOTE: constraint 2 is not asserted — see docs/dev/lanes/utf8s1_report.md wave-task (a); the measurement contradicts the design and the position is escalated, not settled"
fi

# ---------------------------------------------------------------------------
# 1R. THE RED DEMONSTRATION (§9.2's requirement, in the same wave)
# ---------------------------------------------------------------------------
# Every needle in CHECK 1 is re-run against `git archive <pin>` — the tree
# stage 1 started from — and EVERY ONE OF THEM MUST FAIL THERE. A check that
# has only ever been observed green is a check that may be matching nothing;
# this is the cheapest possible way to have seen it red, and it costs a
# `git archive` rather than a build because every needle reads source text.
echo
echo "== CHECK 1R: the same needles, RED against the pre-stage tree $REFCOMMIT =="
REFSRC="$WORKDIR/ref"
mkdir -p "$REFSRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$REFCOMMIT^{commit}" >/dev/null; then
    bad "[1R] the pin $REFCOMMIT does not resolve — the failing-direction demonstration cannot run, and it is an acceptance requirement rather than a nicety"
elif ! git -C "$ROOT_DIR" archive "$REFCOMMIT" src | tar -x -C "$REFSRC" 2>/dev/null; then
    bad "[1R] could not git-archive $REFCOMMIT"
else
    R="$REFSRC/src"
    red=0; green=0
    red_or_note() { # red_or_note <label> <0-if-check-would-pass>
        if [ "$2" -eq 0 ]; then
            green=$((green + 1)); echo "  UNEXPECTED GREEN on the pre-stage tree: $1" >&2
        else
            red=$((red + 1)); echo "  red (as required): $1"
        fi
    }
    grep -q 'const PcrecCpRange \*iv; int n; } cls;' "$R/core/internal.h" 2>/dev/null
    red_or_note "1a payload is the interval form" $?
    ! grep -rq --include='*.c' --include='*.h' 'u\.cls\.bits' "$R" 2>/dev/null
    red_or_note "1a no u.cls.bits survives" $?
    ! grep -q 'uint8_t bits\[32\]; } cls;' "$R/core/internal.h" 2>/dev/null
    red_or_note "1a no bits[32] member survives" $?
    [ -f "$R/core/cpset.c" ]
    red_or_note "1b the builder's file exists" $?
    [ "$( { grep -c 'pcrec_cpset_publish(' "$R/parse/parse.c" 2>/dev/null || echo 0; } | head -1)" -ge 4 ]
    red_or_note "1c four constructors publish an interval set" $?
    [ "$( { grep -c 'pcrec_cpset_complement(&\?[a-z]*, cls_universe(cx))' "$R/parse/parse.c" 2>/dev/null || echo 0; } | head -1)" -ge 2 ]
    red_or_note "1c both negation sites complement within the encoding's universe" $?
    grep -q 'unsigned    max_cp;' "$R/gen/enc/enc.h" 2>/dev/null
    red_or_note "1c PcrecEnc carries max_cp" $?
    [ -f "$R/opt/lower_enc.c" ]
    red_or_note "1d the lowering exists" $?
    grep -q 'root = pcrec_lower_enc(&cx, root);' "$R/core/compile.c" 2>/dev/null
    red_or_note "1d compile.c calls the lowering" $?

    if [ "$green" -eq 0 ] && [ "$red" -ge 9 ]; then
        ok "[1R] all $red CHECK 1 needles go RED against the pre-stage tree $REFCOMMIT — the check has been seen to fail, which is what makes its green mean something"
    else
        bad "[1R] $green of $((red + green)) CHECK 1 needles are already GREEN on the pre-stage tree — those needles do not distinguish stage 1 from the tree it started at, so their green here says nothing"
    fi
fi

# ===========================================================================
# CHECK 2 — THE RENDER HELPER IS THE ONLY READER, AND IT ASSERTS
# ===========================================================================
#
# §8.1.1: *"a grep with a floor and a negative needle: every site in §2.5.1's
# AFTER rows calls it (count >= 6), and no site outside it reads `u.cls.bits`
# directly — the negative half is the one that catches E1's recurrence, since
# a new emitter site added later would otherwise reintroduce exactly the read
# the panel found."*
#
# **THE NEGATIVE NEEDLE HAD TO CHANGE ITS SPELLING, AND SAYING SO IS PART OF
# THE CHECK.** `u.cls.bits` no longer exists, so a grep for it can never match
# and would be a needle that passes vacuously forever — the failure R15's own
# discipline is about. CHECK 1a keeps the zero-occurrence assertion (it is
# still worth stating that the member is GONE rather than renamed), and the
# live negative needle here is the one that can actually fire: **no file
# outside a named allowlist may touch `u.cls` at all.** A new emitter site
# reaching for the payload trips it whatever it then does with what it finds.
echo
echo "== CHECK 2: pcrec_cls_bits is the sole path from a class node to a bitmap =="

# 2a. THE FLOOR, AND IT COUNTS THE ACCESSOR FAMILY RATHER THAN ONE FUNCTION.
#
# §8.1.1 words the floor as "every site in §2.5.1's AFTER rows calls it (count
# >= 6)", counting `pcrec_cls_bits` alone. **FIVE of the six sites want a
# bitmap and the sixth does not**, which the census could not have known: row
# 9's `emit_vm.c:3287` is `vm_isl_single`, whose question is "is this class
# exactly one literal byte" — it scanned 256 values through `cls_has` to ask
# it, and the interval form answers it in one comparison through
# `pcrec_cls_single`. Rendering a bitmap there so the grep would find the word
# would be writing code for the check.
#
# So the floor counts the FAMILY — the four functions `src/core/cpset.c`
# exports for reading a published payload — and a second, tighter assertion
# keeps `pcrec_cls_bits` itself honest at the five sites that genuinely
# produce 32 bytes. Both are needed: the family floor is the "every AFTER site
# goes through an accessor" claim, and the bitmap floor is the one that would
# notice a render site quietly reaching past the helper.
FAM='pcrec_cls_bits(\|pcrec_cls_bits_widen(\|pcrec_cls_single(\|pcrec_cls_has('
NFA_FAM="$(grep -c "$FAM" "$SRC/ir/nfa.c" || true)"
VM_FAM="$(grep -c "$FAM" "$SRC/gen/emit_vm.c" || true)"
TOT=$(( ${NFA_FAM:-0} + ${VM_FAM:-0} ))
if [ "$TOT" -ge 6 ]; then
    ok "[2a] all six AFTER-row sites go through the cpset.c accessor family (nfa.c $NFA_FAM + emit_vm.c $VM_FAM = $TOT, floor 6)"
else
    bad "[2a] only $TOT accessor call(s) in nfa.c + emit_vm.c, want at least 6 (§2.5.1 rows 7, 8 and the four sites of row 9)"
fi
NFA_BITS="$(grep -c 'pcrec_cls_bits(' "$SRC/ir/nfa.c" || true)"
VM_BITS="$(grep -c 'pcrec_cls_bits(' "$SRC/gen/emit_vm.c" || true)"
TOTB=$(( ${NFA_BITS:-0} + ${VM_BITS:-0} ))
if [ "$TOTB" -ge 5 ]; then
    ok "[2a] the five sites that genuinely need 32 bytes render through pcrec_cls_bits itself (nfa.c $NFA_BITS + emit_vm.c $VM_BITS = $TOTB, floor 5)"
else
    bad "[2a] only $TOTB call(s) to pcrec_cls_bits proper, want at least 5 (nfa.c's trie leaf and A_CLASS arm; emit_vm.c's vm_det_seq and the forward and backward walks)"
fi

# 2b. THE NEGATIVE NEEDLE, and the allowlist is the reviewed artifact.
#
#   core/internal.h  declares the payload and the accessors
#   core/cpset.c     IS the representation
#   parse/parse.c    the producers, which read a produced node's list to OR it
#                    into the class under construction (§2.5.1's own note that
#                    a module port hands back an A_CLASS)
#   opt/altcls.c     §2.5.1's three WIDEN rows — a genuine interval union
#                    ABOVE the lowering, which never makes a bitmap
#   opt/lower_enc.c  the lowering itself, which must read what it lowers
#
# Everything else — every emitter, the NFA builder, the two DECLINE analyses —
# reaches a class ONLY through `pcrec_cls_bits`, `pcrec_cls_bits_widen`,
# `pcrec_cls_single` or `pcrec_cls_has`.
ALLOW='src/core/internal.h|src/core/cpset.c|src/parse/parse.c|src/opt/altcls.c|src/opt/lower_enc.c'
# Run from ROOT_DIR over the relative path `src`, so grep's output prefixes
# are the relative names the allowlist is written in — matching an absolute
# path against a relative pattern is how an allowlist silently allows nothing.
OFFENDERS="$(cd "$ROOT_DIR" && grep -rn --include='*.c' --include='*.h' 'u\.cls\.' src \
             | grep -vE "^($ALLOW):" \
             | grep -v '^[^:]*:[0-9]*:[[:space:]]*\(\*\|/\*\|//\)' || true)"
if [ -n "$OFFENDERS" ]; then
    bad "[2b] a file outside the allowlist reads the A_CLASS payload directly. Rendering a class node is pcrec_cls_bits's job and its assertion is the only thing standing between this tree and r54 E1's recurrence:"
    printf '%s\n' "$OFFENDERS" | head -10 >&2
else
    ok "[2b] no file outside the allowlist touches u.cls — every other consumer goes through the four accessors"
fi

# 2c. THE ASSERTION SHIPS ENABLED (§13 obligation 5: *"an assertion compiled
# out in the build everyone runs is a comment"*). It must be a `ctx_fail`, not
# an `assert`, and it must be in the render helper rather than in a caller.
if grep -A6 'void pcrec_cls_bits(Ctx \*cx, const Ast \*a, uint8_t out\[32\])' "$SRC/core/cpset.c" \
     | grep -q 'ctx_fail'; then
    ok "[2c] pcrec_cls_bits's out-of-range check is a ctx_fail — it ships enabled in every build"
else
    bad "[2c] pcrec_cls_bits does not ctx_fail on an out-of-range code point; an assert() would be compiled out under -DNDEBUG and, in a library, would kill the caller (K7)"
fi
if grep -q 'assert(' "$SRC/core/cpset.c"; then
    bad "[2c] src/core/cpset.c uses assert() — §13 obligation 5 requires the read-site check to ship enabled"
else
    ok "[2c] src/core/cpset.c uses no assert(): nothing here is compiled out by NDEBUG"
fi

# 2d. THE ASSERTION FIRES. A check on an assertion's PRESENCE is a check on a
# string; this one runs it. There is no pattern that can reach the helper
# out-of-range under `byte` (that is stage 1's whole point), so the witness is
# built the only honest way: a scratch compiler whose byte backend claims a
# wider universe, which makes `[^a]` produce intervals reaching 0x10FFFF and
# drives one straight into a render site.
echo
echo "== CHECK 2d: the render helper's assertion, RUN rather than grepped =="
SCRATCH="$WORKDIR/scratch"
mkdir -p "$SCRATCH"
cp -R "$ROOT_DIR/src" "$ROOT_DIR/lib" "$ROOT_DIR/cli" "$SCRATCH/" 2>/dev/null || true
if [ ! -f "$SCRATCH/src/gen/enc/enc_byte.c" ]; then
    bad "[2d] could not stage a scratch tree for the assertion witness"
else
    # THE ONE EDIT: the byte backend claims Unicode's universe. Nothing else
    # moves, so what the witness demonstrates is the render site's own refusal
    # and not some second thing the edit broke.
    sed -i.bak 's/PCREC_ENC_BYTE, "byte", 0xFFu, entries_byte/PCREC_ENC_BYTE, "byte", 0x10FFFFu, entries_byte/' \
        "$SCRATCH/src/gen/enc/enc_byte.c"
    if ! grep -q '0x10FFFFu, entries_byte' "$SCRATCH/src/gen/enc/enc_byte.c"; then
        bad "[2d] could not widen the scratch byte backend's max_cp — this witness has stopped being able to build itself"
    else
        # The LOWERING would refuse first, and correctly: its universe is the
        # same widened scalar, so it now accepts what it used to refuse and the
        # class reaches the render site. That is exactly the situation the
        # helper's assertion exists for — the lowering ran and did not confine.
        SCR_SRCS="$(find "$SCRATCH/src" -name '*.c' | LC_ALL=C sort)"
        # shellcheck disable=SC2086
        if ! $CC -O0 -std=gnu11 -w -I"$SCRATCH/lib" -I"$SCRATCH/src" \
                -o "$WORKDIR/pcrec_wide" "$SCRATCH"/cli/main.c $SCR_SRCS 2>"$WORKDIR/wide.log"; then
            bad "[2d] could not build the scratch witness compiler:"
            head -10 "$WORKDIR/wide.log" >&2
        else
            OUT="$("$WORKDIR/pcrec_wide" -p rx -o - -- '[^a]' 2>&1 >/dev/null)"
            RC=$?
            if printf '%s' "$OUT" | grep -q 'reached a byte-tier consumer'; then
                ok "[2d] the render helper's assertion FIRES on a class carrying a code point above 0xFF: \"$(printf '%s' "$OUT" | head -1)\""
            elif [ "$RC" -eq 0 ]; then
                bad "[2d] the scratch compiler COMPILED '[^a]' with a 0x10FFFF universe — a code-point interval list reached a byte-tier consumer and nothing said so. That is r54 E1 exactly: the artifact exists, it matches something, and no answer check can see it"
            else
                bad "[2d] the scratch compiler refused '[^a]' with an unexpected diagnostic (rc=$RC): $(printf '%s' "$OUT" | head -2)"
            fi
        fi
    fi
fi

# ===========================================================================
# CHECK 3 — THE STAMP CENSUS, as a MANIFEST
# ===========================================================================
#
# §8.1.1 places check 3 at STAGE 2 — *"Over the corpus compiled under BOTH
# encodings"* — and stage 2 is where its interesting half lives, because that
# half compares each `utf8` artifact against its `byte` twin and there is no
# twin to compare against yet. WHAT STAGE 1 CAN AND DOES DO IS ESTABLISH THE
# MANIFEST: the census over the one encoding that compiles, recorded so stage 2
# diffs against a file rather than against a memory, plus the [MECH-REACH]
# half — a demonstration that the instrument REACHES every stamp it claims to
# census. An instrument first exercised in the wave that depends on it is an
# instrument nobody has seen work.
#
# **IT IS A MANIFEST AND NOT A THRESHOLD**, r49's ruling: a check pinned to a
# count expires the moment the count is legitimately re-measured. Nothing below
# asserts a stamp's VALUE. What is asserted is that each named stamp was found
# on at least one artifact, i.e. that the census's needles are live.
echo
echo "== CHECK 3: the stamp census manifest (stage 1's half of §8.1.1 check 3) =="

CENSUS="$WORKDIR/stamps.tsv"
: > "$CENSUS"
# A SAMPLE, not the corpus. The manifest's stage-1 job is reach, and reach is
# demonstrated by the shapes that carry each stamp — the whole-corpus census is
# stage 2's, where it is a diff between two encodings and the population is the
# claim. These twelve span both engines, the hybrid, a prefilter, an island, a
# lookbehind and a call.
SAMPLE='a
abc
a(b|c)+d
(a)(b)(c)
[a-z]+@[a-z]+
^foo$
\bword\b
(?i)HeLLo
cat|dog|cow|calf|camel
(\w+)\s+\1
(?<=foo)bar
(a(?1)?b)'
NART=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    art="$(pcrec_run "$PCREC" --features all -p rx -o - -- "$pat" 2>/dev/null)"
    [ -n "$art" ] || continue
    NART=$((NART + 1))
    for m in RX_ENGINE RX_ENGINE_SEL RX_DFA_TABLE RX_VM_RUNGS RX_VM_STRATS \
             RX_VM_ALT_ISLANDS RX_VM_FRAMELESS RX_DFA_PREFILTER; do
        v="$(printf '%s\n' "$art" | sed -n "s/^#define $m \(.*\)$/\1/p" | head -1)"
        [ -n "$v" ] && printf '%s\t%s\t%s\n' "$pat" "$m" "$v" >> "$CENSUS"
    done
    sz="$(printf '%s' "$art" | wc -c | tr -d ' ')"
    printf '%s\t%s\t%s\n' "$pat" "EMITTED_BYTES" "$sz" >> "$CENSUS"
done <<EOF
$SAMPLE
EOF

if [ "$NART" -lt 10 ]; then
    bad "[3] the census compiled only $NART of the 12 sample patterns — the manifest's population has collapsed"
else
    ok "[3] the census compiled $NART sample artifacts and recorded $(wc -l < "$CENSUS" | tr -d ' ') stamp readings"
fi

# THE REACH ASSERTION, and it is the [MECH-REACH] half. A stamp name that
# appears on NO artifact in the sample is a needle that would census nothing at
# stage 2 while looking like coverage — the exact shape lane `macport`'s note
# and `learnings.md` §3 both record.
missing=""
for m in RX_ENGINE RX_ENGINE_SEL RX_DFA_TABLE RX_VM_RUNGS RX_VM_STRATS \
         RX_VM_ALT_ISLANDS RX_VM_FRAMELESS RX_DFA_PREFILTER EMITTED_BYTES; do
    grep -q "	$m	" "$CENSUS" || missing="$missing $m"
done
if [ -n "$missing" ]; then
    bad "[3] the census reached NO artifact carrying:$missing — those needles would report an empty census at stage 2 while looking like coverage ([MECH-REACH])"
else
    ok "[3] every stamp the census names was reached on at least one sample artifact — the instrument is live, not vacuous"
fi

# THE MANIFEST IS WRITTEN OUT, which is the deliverable stage 2 diffs against.
MANIFEST="$ROOT_DIR/tests/codegen/manifests/m5_stage1_stamps.tsv"
if [ -d "$(dirname "$MANIFEST")" ]; then
    if [ -f "$MANIFEST" ]; then
        if diff -q "$MANIFEST" "$CENSUS" >/dev/null 2>&1; then
            ok "[3] the recorded manifest ($MANIFEST) matches this run exactly"
        else
            bad "[3] the recorded manifest has drifted from this run. Under r49 that is a DIFF TO REVIEW, not a number to bump: read it, decide whether each moved stamp is a ruling or a regression, and re-record deliberately."
            diff "$MANIFEST" "$CENSUS" | head -20 >&2
        fi
    else
        cp "$CENSUS" "$MANIFEST"
        ok "[3] manifest recorded for the first time at $MANIFEST — stage 2 diffs its two-encoding census against this"
    fi
else
    bad "[3] tests/codegen/manifests/ does not exist; the manifest has nowhere to live"
fi

# ===========================================================================
# CHECK 4 — THE INTERVAL ALGEBRA, AGAINST AN ORACLE THAT SHARES NOTHING WITH IT
# ===========================================================================
#
# Checks 1-3 and the identity gate are all statements about a POPULATION: the
# payload exists, the accessors are the only readers, and the corpus's
# artifacts did not move. None of them exercises `src/core/cpset.c`'s SET
# ALGEBRA outside the narrow slice the corpus happens to reach —
# `pcrec_cpset_complement` is only ever called at `max_cp == 0xFF`,
# `pcrec_cpset_remove` has one caller, and no corpus pattern builds a list long
# enough to reach the absorb-many path in `add`.
#
# Stage 2's 0x10FFFF universe and stage 3's ~770-interval property classes
# will. `cpset_model_check.c` carries the full argument; what runs here is the
# check itself, so the algebra is defended by `make test` from the wave that
# introduced it rather than from the wave that first breaks it.
echo
echo "== CHECK 4: the interval algebra, model-checked against a bitset oracle =="
if ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror \
        -I "$ROOT_DIR/lib" -I "$ROOT_DIR/src" \
        -o "$WORKDIR/cpsetmodel" "$SCRIPT_DIR/cpset_model_check.c" \
        "$ROOT_DIR/build/libpcrec.a" 2>"$WORKDIR/cpsetmodel.log"; then
    bad "[4] cpset_model_check.c does not build:"
    head -10 "$WORKDIR/cpsetmodel.log" >&2
elif ! MODEL_OUT="$("$WORKDIR/cpsetmodel" 2>&1)"; then
    bad "[4] the interval algebra DISAGREES with the bitset oracle:"
    printf '%s\n' "$MODEL_OUT" | head -10 >&2
else
    ok "[4] $(printf '%s' "$MODEL_OUT" | head -1)"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
