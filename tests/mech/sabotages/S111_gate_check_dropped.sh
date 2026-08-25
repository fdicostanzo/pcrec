# S111 (design row S-BR7) — THE MODULE GATE IS DROPPED FROM THE NEW ATOM PORT.
#
# THE MANDATE'S OWN LINE, as a row: "unsupported constructs must fail with a
# clean 'requires module X' error, NEVER MISCOMPILE" — and its less obvious
# half, that a construct must not START COMPILING when its module is off.
#
# The gate is `pcrec_ext_gate`, which demotes a RESULT ask to VERDICT for a row
# whose module is not enabled, so a port only ever runs at RESULT with the gate
# OPEN. Forcing the demotion away makes every `\1` compile at
# `--features none`, which is a compatibility change to the BASE tier made as
# a side effect of a module landing — the thing §14's `\0` ruling explicitly
# refuses to do even for a construct that needs no VM.
#
# tests/reject/ is the arm that sees it: 550 checks whose whole subject is
# WHICH module a refusal promises and WHETHER it refuses at all.
SAB_ID="S111-gate-check-dropped"
SAB_FILE="src/parse/ext.c"
SAB_SUITES="reject harness registry cli"
SAB_HARNESS_TARGET="tests/backrefs/gated.rxt"
SAB_DESC="pcrec_ext_gate stops demoting a RESULT ask for a disabled module, so every registry row with a wired producer compiles with its module OFF -- backrefs' thirteen included. A construct that compiles with --features none is the mandate's own forbidden shape, and no MATCH-semantics test can see it because the answers are right"
SAB_DOC_FIGURE="PREDICTED: reject RED broadly; the corpus RED on gated.rxt's refusal cells. Canonical figure owed from run_sabotage_matrix.sh S111."
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS A WIRED PRODUCER WITH ITS MODULE OFF, which is the
# only population `pcrec_ext_gate`'s demotion governs. `(a)\1` under
# `--features none` must be REFUSED naming `backrefs`; under the sabotage
# it COMPILES, which is the mandate's own forbidden shape. A construct with
# no producer would be refused either way and is not a witness.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "(a)\\1"'
SAB_REACH_EXPECT="\\1 (backreference/octal) requires module 'backrefs' (pattern offset 3)"
SAB_COUNT=1
SAB_BEFORE='    want = pcrec_ext_gate(r, want);

    if (!r) {'
SAB_AFTER='    /* SABOTAGE S111: the gate no longer demotes */

    if (!r) {'
