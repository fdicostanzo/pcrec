#!/usr/bin/env bash
# tests/registry/run_registry_tests.sh — build and run the registry conformance
# check (SR-1 / D24).
#
# It links against build/libpcrec.a and includes src/core/internal.h, because
# the registry is INTERNAL: the point is to compare the table with the parser
# inside one process, not to re-derive it from CLI output. `pcrec --list-syntax`
# (SR-3) is the external view, and tests/reject/ consumes that one (SR-4).
#
# Usage: bash tests/registry/run_registry_tests.sh
# Env: CC (default gcc), KEEP=1 to keep the built binary, LIBPCREC (default
#   <repo-root>/build/libpcrec.a — SAN-1 override so this can link a
#   sanitizer-built library), SANFLAGS (default empty — SAN-1: extra flags
#   appended to this file's own test-driver builds), PCREC/JOBS forwarded to
#   run_pc4.sh below (inherited process env, no export needed)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
SANFLAGS="${SANFLAGS:-}"

LIB="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
if [ ! -f "$LIB" ]; then
    echo "registry: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "registry: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

BIN="$WORKDIR/registry_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" $SANFLAGS \
        -o "$BIN" "$SCRIPT_DIR/registry_check.c" "$LIB"; then
    echo "registry: FAILED TO BUILD registry_check.c" >&2
    exit 1
fi

REGOUT="$WORKDIR/registry_check.out"
"$BIN" 2>&1 | tee "$REGOUT"
rc=${PIPESTATUS[0]}

# ---- COVERAGE GUARD for registry_check itself (R15, checks critic) ------
#
# PC-3 below has carried a count + manifest since R9; registry_check — the
# suite in the SAME directory, holding the MOD-0.2 arbitration checks — had
# neither, so deleting check_row_ranks or the no-ambiguity sweep would have
# been invisible: `checks passed` shifts in output nothing compared. Same
# two layers, same rules: count evaluated always (with the R9/C1-final2
# wording split), manifest only on a green run (needles come from ok()
# lines, and a failing check never prints one).
# [M6.5.2] 178 -> 182, and the +4 is worth naming because it is NOT the twelve
# rows module `backrefs` wired. MEASURED off a run's PASS lines:
# `check_engine_capability` prints its per-row detail only on a FAILURE and one
# green line otherwise, so wiring twelve producers moves this count by ZERO.
# What moves it is `check_table_to_parser`, which prints TWO lines per RK_ESC
# row — an atom-diagnostic line and a class-position line — and the two new
# `\g<` / `\g'` rows are RK_ESC. 2 rows x 2 lines = 4.
# [M6.6.2 wave F] 182 -> 196, and the +14 splits as 12 + 2, MEASURED off a
# run's PASS lines rather than predicted. The 12 are `check_table_to_parser`'s
# one line per new RK_VERB row (the twelve `(*` alpha spellings); the 2 are the
# new `check_families` and `check_index_rows`, D71 item 3's index layer. The
# twelve SR-8 witnesses added in the same change move this by ZERO, for the
# reason the [M6.5.2] note above already gives: `check_engine_capability`
# prints its per-row detail only on a FAILURE.
regn="$(grep -c '^PASS: ' "$REGOUT" || true)"
if [ "$regn" -ne 196 ]; then
    if grep -q "^checks failed: 0" "$REGOUT"; then
        echo "registry: registry_check COVERAGE CHANGED — $regn passing checks, expected 196." >&2
        echo "registry:   if you added or removed checks on purpose, update this number" >&2
        echo "registry:   in the same commit; if not, coverage was removed" >&2
    else
        rnf="$(sed -n 's/^checks failed: //p' "$REGOUT" | tail -1)"
        echo "registry: registry_check shows $regn passing checks (196 expected; ${rnf:-?} failed," >&2
        echo "registry:   so a lower count is expected here). Fix the failures first; then this" >&2
        echo "registry:   number must return to 196 — if it does not, coverage was removed too" >&2
    fi
    rc=1
fi
if grep -q "^checks failed: 0" "$REGOUT"; then
    while IFS='|' read -r needle why; do
        [ -z "$needle" ] && continue
        if ! grep -qF "$needle" "$REGOUT"; then
            echo "registry: MANIFEST — registry_check no longer runs a check matching '$needle'." >&2
            echo "registry:   why it must exist: $why" >&2
            echo "registry:   do NOT satisfy this by editing a count; restore the check" >&2
            rc=1
        fi
    done <<'REGMANIFEST'
row ranks: all 20 tailed rows|MOD-0.2: a tailed row at the fallback tier loses every arbitration and its construct is unreachable; successor of check_tail_precedence's second half
arbitration liveness:|R11/M3 via MOD-0.2: an arbitration nothing contests is unobservable; these floors are check_tail_precedence's re-homed liveness clause
no-ambiguity sweep:|R15: after the D32 §9.5 scaffold was deleted, nothing probed the ambiguous flag over a swept space; a same-rank prefix pair would fire only in a user's compile
class ports: 7 scalar + 10 SET + 9 FN|MOD-0.3b/c/d: the unwired port data's only guard — values oracle-tied and populations pinned; deleting it makes a drifted or silently-populated port invisible until a producer ships it
class-position reach: 5 tailed/body-carrying rows|MOD-0.6/D33 §9.2, K10's fourth net: the one-byte in-class sweep above cannot express [\N{U+41}]-shaped bodies at all; this is the only check that arbitrates a tailed/body-carrying row's FULL syntax at class position and confirms it reaches itself and promises its own module
engine capability: all 62 wired-AND-BUILT VM_ONLY producers refuse|[M6.4.2]/D67, REPLACING the [M4.7a] tripwire whose premise SR-8 discharged: the tripwire asserted that no VM_ONLY row had a producer (the fact that made deferring SR-8 safe); this asserts the thing it demanded instead — every VM_ONLY row that HAS a producer refuses --engine=dfa BY NAME, on a HAND-WRITTEN witness whose cut genuinely bites (the row's own syntax cannot serve: 'a*+' correctly COMPILES, because the free discharge deletes a cut it proves dead), and every witness also COMPILES on the default engine so the check cannot go green on a compiler that stopped accepting the construct. The ITERATION is what makes it generic: a module wiring the NEXT VM_ONLY producer with no witness here is a named failure, which is how backrefs' twelve rows ([M6.5.2]) WERE caught -- they landed 2026-08-22, each with a hand-written witness, taking `wired` from 6 to 18. [M6.6.2] wave B+C took `wired` to 24 and split the number in two: module `lookaround` wires ONE port for six rows and BUILDS only three of them at that wave, so the witness requirement is gated on D65's derived `built` column and the label names the 21 wired-AND-BUILT rows. That is a REFINEMENT of the check and not a relaxation of it — a declining producer has no artifact to refuse and no default-engine compile to assert, so a witness for such a row cannot be written; the check additionally asserts that its checked count EQUALS the built-and-wired count, so a gate that excused a row it should have checked is a MISSING WITNESS rather than a smaller pass. [M6.6.2] wave D took it to 24: the port stopped declining the `<` tails when the back-step seam entry landed, the three lookbehind rows became `built`, and they started demanding witnesses WITH NO EDIT TO THE GATE -- which is the property the wave B+C refinement was built to have. `built_wired` now equals `wired`, so there is nothing left in this module for the gate to excuse. [M6.6.2] wave F took it to 36: the twelve `(*` alpha spellings carry the SAME shared port in their own `aport` and produce on their first call, so all three numbers (qualifying, wired, built) moved together for the first time. Their witnesses are PER MEMBER (D71 item 3's rule) and each one asserts the ALIAS's own syntax appears in the --engine=dfa refusal -- which is what pins that `pcrec_laport_group` stamps the row it was DISPATCHED on rather than the primary it resolved its flags from; point the stamp at the primary and exactly these twelve fail while the rest of the tree stays green. [DD-14] wave B+C took it to 60, and the SHAPE of that move is new: TWENTY-FOUR rows flip `unbuilt -> built` with NO row added and NO row reclassified -- `qualifying` holds at 66 while `wired` and `built_wired` both move by 24 -- because module `recursion`'s `(?` rows were ALREADY VM_ONLY (P4 measured all 26 that way before the module existed) and this wave gave them a PRODUCER rather than a classification. TWO of the twenty-four witnesses are CAPTURE-FREE and the rest cannot be: `(?R)` and `(?0)` call the whole pattern, so `a(?R)?b` has no group at all and is VM-forced by NOTHING BUT THE STAMP -- the sharp form the other witnesses' own capture-freedom rule asks for -- while every other spelling names a group by construction. The twenty-two still fire, because the captures arm of the `--engine=dfa` refusal names no construct and the witness matches on the NAME; the capture-free pair is what makes that argument checkable rather than merely stated. At wave B+C the two `\g<` / `\g'` rows were module `recursion`'s too and were deliberately NOT wired -- design 8.1 kept them `unbuilt` until wave D, since D65 flips `built` from the PORT and flipping them while the emitter could not compile the spelling would have shipped a compliance index that lies. [DD-14] wave D took `wired` and `built_wired` to 62: `pcrec_brport_g` (src/parse/mod_backrefs.c) gained the `<`/`'` arms, both rows' `aport` now points at it, and neither has a tail left to decline -- the same "no code at all" shape that kept them unbuilt now flips them the other way with no code at all either, via D65's live derivation rather than a declared flag
free discharge: all 4 provably-dead cuts compile to a PURE DFA|[M6.4.2]: the OTHER direction of the per-pattern split, and the only thing in the tree that would notice the free discharge silently ceasing to fire — every ANSWER would still be correct and only the ENGINE would change. VM_ONLY is too STRONG for 'a*+b' (whose cut §2.2 proves dead) and ANY_ENGINE too WEAK for '(?>a|ab)c'; this asserts the first half and the engine-capability check above asserts the second, which together are the first evidence the `engines` column has ever had in BOTH directions
built-status: 118 rows classified with 0 defects|D65 (docs/design/registry_built_status_memo.md, ratified wholesale 2026-08-21): the ONLY guard that pcrec_construct_built_status classifies every RS_MODULE row's own syntax cleanly (built or unbuilt), never landing in the PCREC_BUILT_DEFECT bucket the generated compliance index must never silently render — deleting it removes the one thing that would fail loudly the day a row's own well-formed syntax stops classifying, e.g. a reworded refusal or a doorway change the classifier's res.what/res.answered_at reading no longer matches
REGMANIFEST
fi
# The one NEGATIVE needle, outside the manifest loop because its polarity is
# reversed: the retired check's PASS line must NOT reappear. Someone
# resurrecting check_tail_precedence instead of maintaining its successors
# reintroduces an assertion about an engine that no longer exists.
if grep -qF "tail precedence: longest tail wins" "$REGOUT"; then
    echo "registry: the RETIRED check_tail_precedence is back — its engine was" >&2
    echo "registry:   deleted at MOD-0.2; maintain check_row_ranks and the" >&2
    echo "registry:   arbitration-liveness floors instead" >&2
    rc=1
fi

# SR-4: the dump is load-bearing for docs/pcre2_compliance.md. The construct
# INDEX in that file is generated from `pcrec --list-syntax`, so it cannot drift
# from the compiler; the surrounding analysis is hand-written and left alone.
# The names check is the one that catches the realistic failure — a module
# renamed in registry.c leaving the prose describing something that no longer
# exists.
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
if [ ! -x "$PCREC" ]; then
    echo "FAIL: registry: pcrec binary not found at $PCREC (SR-4 checks skipped)" >&2
    exit 1
fi
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --check; then rc=1; fi
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --names; then rc=1; fi

# [DOC-DRV]: component 3, the keyed annotation store. Same drift-detector
# shape as --check above (a stale key or a page-vs-store render mismatch
# fails loudly, naming the fix), extended to
# docs/pcre2_compliance_annotations.txt. --tension is informational by
# design (see compliance_section.py's own docstring) and is run for
# visibility, never for its exit code.
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --check-annotations; then rc=1; fi
PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --tension

# PC-3: the same table against libpcre2, which is the one authority none of the
# above is. It links the same library and includes the same header, then dlopens
# libpcre2 at runtime — and SKIPS LOUDLY if that library is absent, so a clone
# on a box without libpcre2-8-0 still gets a green suite. `-ldl` is the only
# extra link requirement.
PC3BIN="$WORKDIR/pcre2_check"
if ! "$CC" -O2 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" $SANFLAGS \
        -o "$PC3BIN" "$SCRIPT_DIR/pcre2_check.c" "$LIB" -ldl; then
    echo "registry: FAILED TO BUILD pcre2_check.c (PC-3)" >&2
    exit 1
fi
echo
PC3OUT="$WORKDIR/pc3.out"
if ! "$PC3BIN" | tee "$PC3OUT"; then rc=1; fi
[ "${PIPESTATUS[0]}" -eq 0 ] || rc=1

# ---- COVERAGE GUARD (R9/C1-7) -------------------------------------------
#
# Until R9 this directory had neither of the two protections tests/reject/ has
# carried since R7, and it is the directory holding the expensive checks. A
# critic deleted FIX-2's three new instruments outright — both differentials
# from main() and the 4a sweep — and everything stayed GREEN: `checks passed`
# went 129 -> 128 and 81 -> 76, in output that nothing compared. The commit
# message's whole claim is that these instruments will catch a K3/K4
# regression; they could not catch their own removal, and removal by a future
# refactor of this doorway is the likelier event.
#
# Two layers, for the reason tests/reject/ states: a count makes a deletion
# VISIBLE in the diff, and a manifest makes it FAIL. Neither replaces the other
# — the count cannot say which check went, and the manifest only covers checks
# someone thought to name.
# [M6.5.2] 167 -> 169: the two new `RK_ESC` rows with tails `<` and `'`
# (module `recursion`, splitting the `\g` doorway's SUBROUTINE half from its
# BACKREFERENCE half) each add one PC-3 check, and each needed a WRAPPER —
# their own `syntax` puts the construct LEFTMOST for pcrec, so the group
# declaration libpcre2 demands (`(a)\g<1>`) lives in pcre2_check.c's WRAPPERS
# table, the same shape the `(?P=` / `(?P>` pair already uses.
# [M6.6.2 wave F] 169 -> 181: the twelve `(*` alpha lookaround spellings, one
# PC-3 check each. NONE of them needed a wrapper -- each row's own `syntax` is
# already a pattern libpcre2 compiles standalone, which is the half of these
# rows that could not be taken on trust and was MEASURED against libpcre2 10.46
# before they were written (84 alias-vs-primary templates x 19 subjects, every
# startpos, span and every group span, 0 divergences). So this +12 is not
# bookkeeping: it is twelve new rows each now differentially checked against
# the oracle that decides whether they are real.
if [ -s "$PC3OUT" ] && ! grep -q "^SKIP:" "$PC3OUT"; then
    pc3n="$(grep -c '^PASS: ' "$PC3OUT" || true)"
    if [ "$pc3n" -ne 181 ]; then
        # WORDING SPLIT BY CASE (R9/C1-final2). This guard deliberately sits
        # outside the manifest gate — that is what keeps "one check fails while
        # another is silently deleted" caught — but its message was written for
        # the silent case and asserted "coverage was removed" on every red run,
        # where a lower PASS count is simply what a failure produces. Nobody
        # knows how many PASS lines a given failure suppresses, so the number
        # carries no information there and must not be read as one.
        if grep -q "^checks failed: 0" "$PC3OUT"; then
            echo "registry: PC-3 COVERAGE CHANGED — $pc3n passing checks, expected 181." >&2
            echo "registry:   if you added or removed checks on purpose, update this number" >&2
            echo "registry:   in the same commit; if not, coverage was removed" >&2
        else
            nf="$(sed -n 's/^checks failed: //p' "$PC3OUT" | tail -1)"
            echo "registry: PC-3 shows $pc3n passing checks (181 expected; ${nf:-?} failed, so a" >&2
            echo "registry:   lower count is expected here). Fix the failures first, then this" >&2
            echo "registry:   number must return to 181 — if it does not, coverage was removed too" >&2
        fi
        rc=1
    fi
    # The manifest: checks whose ABSENCE would silently un-guard a specific past
    # finding, matched by substring of the check's name.
    #
    # ONLY EVALUATED ON A GREEN PC-3 RUN (R9/C1F-6). The needles come from each
    # check's `ok()` text, and a check that runs and legitimately FAILS never
    # calls `ok()` — so its needle vanished and the manifest announced "no
    # longer runs a check matching ..." with the remedy "restore the check",
    # when the check had run, done its job, and what the reader must actually do
    # is fix the compiler. Reproduced from two different failing checks, so it
    # was every manifested entry, and it fired exactly when the operator is
    # under the most pressure to read correctly. Worse in the other direction
    # too: a real deletion then produces a message the reader has been trained
    # to treat as noise.
    #
    # A failing run already fails. The manifest exists for the SILENT case.
    if ! grep -q "^checks failed: 0" "$PC3OUT"; then
        # Say WHICH of the two it is. The gate is also true when PC-3 produced no
        # summary at all — a truncated run — and the first version of this notice
        # announced "reported failures" for a run that reported none (R9/C1-final2).
        # The truncated case is still caught, by the count guard, at rc=1.
        if grep -q "^checks failed:" "$PC3OUT"; then
            echo "registry: PC-3 reported failures; skipping the manifest (its needles" >&2
            echo "registry:   come from PASS lines, so a failing check would look deleted)" >&2
        else
            echo "registry: PC-3 produced NO summary line — it did not finish. Skipping the" >&2
            echo "registry:   manifest; the count guard above is what catches this" >&2
        fi
    else
    while IFS='|' read -r needle why; do
        [ -z "$needle" ] && continue
        if ! grep -qF "$needle" "$PC3OUT"; then
            echo "registry: MANIFEST — PC-3 no longer runs a check matching '$needle'." >&2
            echo "registry:   why it must exist: $why" >&2
            echo "registry:   do NOT satisfy this by editing a count; restore the check" >&2
            rc=1
        fi
    done <<'MANIFEST'
probe count intact|R9/C1F-4: 89%% of this doorway's probes were deletable with every PASS line and every other needle intact
pattern set unchanged|R9/C1-final2: a blanked or duplicated shape loses coverage without moving any probe count
class-bracket doorway: no over-acceptance|the K3/K4 verdict differential itself; PC-3's stated reason for existing
no module promised for a pattern PCRE2 will never accept|R9/C1-8: the both-refuse half never read pcrec's message, so doorway 4a's own over-promise had no external check
nested opener for every delimiter|R9/C1-1: the shape that names the construct generated none for . and =
live in both directions|R9/C1-6: the over-acceptance half was comparing against nothing
class delimiter byte sweep|R9/C1-3: a construct at this doorway with no registry row was invisible
POSIX class names: every name deferred|the doorway's over-promise check (R8/C4-7)
POSIX class name pcrec claims was produced INDEPENDENTLY|R9/C1-2: the pool could contribute zero real names and stay green
pcrec varies its own answer by position|R9/C3-verify: the libpcre2-side counter stays green under a full revert; this is the half that reads pcrec
POSIX name x position|R9/C3-4: <  and > are only legal as a class's entire content
every verb name pcrec claims was produced INDEPENDENTLY|R8/C1-4: the external pool could be empty with nothing failing
(? byte differential: 7650 probes|Q2: the doorway promised module 'modifiers' for 217 of 255 bytes; this is the only external check that 217 bytes are NOT constructs
(? byte differential: libpcre2's own populations|Q2: "all 255 agree" is also what a doorway promising a module for everything prints; the 38/217 split is what makes agreement mean something
option runs: 19448 probes|Q2: splitting the catch-all into 11 letter rows fixed the BYTE and left (?iZ) still promising a module; only a run-level sweep sees that
option runs: both verdict buckets|Q2: a sweep where every run is invalid agrees with a doorway that refuses everything
tail sweep (?P|SR-9: (?P= vs (?P< was invisible to every one-byte sweep in this repo (named in tests/registry/CLAUDE.md since R5)
tail sweeps: 2 of 4 prefixes|SR-9: (?< answers alike for every tail, so its split is pinned in tests/reject/ and this counter is what stops the whole sweep becoming that
K15 exclusion: fired|K15 (2026-08-12): the exclusion is a dead branch reading as coverage unless it actually fires on the hostile-alphabet pool; a regressed pool or a closed K15 must be investigated, not silently pass
uprops differential: pcrec matched libpcre2|MOD-0.6 slice 4: the \p/\P shape-space differential, obligation-mapped against a LIVE oracle per cell; its 52-letter axis is the independent drift guard on mod_uprops.c's hand-written 14-of-52 short-name table (manager ruling 2) — measured to fail 20/20 when the table drops a letter
gated[modifiers] recognition (OPTRUN-B3)|R20/OPTRUN-B3 (MOD-0.8c slice 2): every other differential in this file runs at the DEFAULT (empty) enabled set, so all 48.7M probes of the (? doorway measure recognition and never acceptance. SPEC-1 was a gate-open-only miscompile — a(?i)* accepted, libpcre2 err 109, matcher really matching — and no closed-gate sweep could see it. Reverting the fix in a scratch build fires this check 672 times while registry_check and cli stay green (2026-08-12). The set is FOCUSED per docs/testing.md's differential gate principle -- one module per pass; a second producing module at this doorway gets its own call and its own needle here
gated[modifiers] liveness: pcrec ACCEPTED|the gated pass's own vacuity guard: if pcrec accepts nothing with the gate open, the producers never ran and T1 cannot fail, so the pass reads as coverage while measuring the closed-gate space twice — OPTRUN-B3's defect reproduced by the check written to close it
gated[modifiers] quantifier cross: both spelling lists full|SPEC-1's own family, and the reason it is generated rather than listed: check11 owns this module and missed the defect because its structural table is 21 hand-written spellings with not one quantified form. The floor is what stops the family going quiet — check14 measured a refuse-everything pcrec collapsing it to zero cells with no disagreement reported
MANIFEST
    fi
fi

# ---- PC-4 (MOD-0.3e): the SEMANTIC differential ---------------------------
#
# PC-3 proves every row names a real construct; PC-4 compares what the
# PRODUCED constructs MATCH, cell by cell, against the live oracle — the
# check R8/C4-2 asked for, buildable only once a module gave pcrec
# semantics that can differ. Skips loudly without libpcre2 (probed inside
# run_pc4.sh before the gcc sweep is paid for). The needle below is this
# suite's guard that PC-4 stays wired: a deleted call would leave every
# other line green.
PC4OUT="$WORKDIR/pc4.out"
bash "$SCRIPT_DIR/run_pc4.sh" 2>&1 | tee "$PC4OUT"
pc4rc=${PIPESTATUS[0]}
if [ "$pc4rc" -ne 0 ]; then
    rc=1
elif ! grep -q "^SKIP: pc4" "$PC4OUT" && \
     ! grep -q "^pc4: 273 patterns" "$PC4OUT"; then
    echo "registry: PC-4 ran but its population line is missing or moved —" >&2
    echo "registry:   the 273-pattern space and pc4_check.c's predictions move" >&2
    echo "registry:   in the same change or not at all" >&2
    rc=1
fi
exit $rc
