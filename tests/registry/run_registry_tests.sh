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
# Env: CC (default gcc), KEEP=1 to keep the built binary

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

LIB="$ROOT_DIR/build/libpcrec.a"
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
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
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
regn="$(grep -c '^PASS: ' "$REGOUT" || true)"
if [ "$regn" -ne 167 ]; then
    if grep -q "^checks failed: 0" "$REGOUT"; then
        echo "registry: registry_check COVERAGE CHANGED — $regn passing checks, expected 167." >&2
        echo "registry:   if you added or removed checks on purpose, update this number" >&2
        echo "registry:   in the same commit; if not, coverage was removed" >&2
    else
        rnf="$(sed -n 's/^checks failed: //p' "$REGOUT" | tail -1)"
        echo "registry: registry_check shows $regn passing checks (167 expected; ${rnf:-?} failed," >&2
        echo "registry:   so a lower count is expected here). Fix the failures first; then this" >&2
        echo "registry:   number must return to 167 — if it does not, coverage was removed too" >&2
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
row ranks: all 18 tailed rows|MOD-0.2: a tailed row at the fallback tier loses every arbitration and its construct is unreachable; successor of check_tail_precedence's second half
arbitration liveness:|R11/M3 via MOD-0.2: an arbitration nothing contests is unobservable; these floors are check_tail_precedence's re-homed liveness clause
no-ambiguity sweep:|R15: after the D32 §9.5 scaffold was deleted, nothing probed the ambiguous flag over a swept space; a same-rank prefix pair would fire only in a user's compile
class ports: 5 scalar + 10 SET + 9 FN|MOD-0.3b/c/d: the unwired port data's only guard — values oracle-tied and populations pinned; deleting it makes a drifted or silently-populated port invisible until a producer ships it
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

# PC-3: the same table against libpcre2, which is the one authority none of the
# above is. It links the same library and includes the same header, then dlopens
# libpcre2 at runtime — and SKIPS LOUDLY if that library is absent, so a clone
# on a box without libpcre2-8-0 still gets a green suite. `-ldl` is the only
# extra link requirement.
PC3BIN="$WORKDIR/pcre2_check"
if ! "$CC" -O2 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
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
if [ -s "$PC3OUT" ] && ! grep -q "^SKIP:" "$PC3OUT"; then
    pc3n="$(grep -c '^PASS: ' "$PC3OUT" || true)"
    if [ "$pc3n" -ne 143 ]; then
        # WORDING SPLIT BY CASE (R9/C1-final2). This guard deliberately sits
        # outside the manifest gate — that is what keeps "one check fails while
        # another is silently deleted" caught — but its message was written for
        # the silent case and asserted "coverage was removed" on every red run,
        # where a lower PASS count is simply what a failure produces. Nobody
        # knows how many PASS lines a given failure suppresses, so the number
        # carries no information there and must not be read as one.
        if grep -q "^checks failed: 0" "$PC3OUT"; then
            echo "registry: PC-3 COVERAGE CHANGED — $pc3n passing checks, expected 143." >&2
            echo "registry:   if you added or removed checks on purpose, update this number" >&2
            echo "registry:   in the same commit; if not, coverage was removed" >&2
        else
            nf="$(sed -n 's/^checks failed: //p' "$PC3OUT" | tail -1)"
            echo "registry: PC-3 shows $pc3n passing checks (143 expected; ${nf:-?} failed, so a" >&2
            echo "registry:   lower count is expected here). Fix the failures first, then this" >&2
            echo "registry:   number must return to 143 — if it does not, coverage was removed too" >&2
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
MANIFEST
    fi
fi
exit $rc
