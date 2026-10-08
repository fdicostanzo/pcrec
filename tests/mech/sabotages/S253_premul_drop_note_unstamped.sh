# S253 — [K59-PREMUL] THE RUNG FIRES AND SAYS NOTHING.
#
# Frank's addendum ruling (2026-09-17): EVERY drop-ladder rung firing prints
# a loud, non-fatal stderr note naming what was dropped, the cost direction,
# and the caller's recourse (`size_drop_note`, `src/core/compile.c`). This
# row defeats ONLY the bookkeeping that decides whether the premul rung's
# note gets printed (until B3 `dropped_premul`; since B3 the notes loop over
# the fired record), leaving the rung's actual EFFECT —
# the emitted artifact, the RX_DFA_TABLE stamp, the RX_ENGINE_SEL value —
# completely untouched. The rescue still happens; it happens silently.
#
# THIS IS S238's OWN SHAPE, ONE RUNG OVER ("the rung fires and says
# nothing"), and for the identical reason: nothing that reads the ARTIFACT
# can tell a silent rescue from a loud one, because the artifact is
# byte-for-byte the same either way. Only an instrument that reads STDERR
# can see it.
#
# WHAT SEES IT: `tests/codegen/run_tune_dial.sh` §6, whose per-position loop
# greps $WORKDIR/err.txt (stdout+stderr) for the premul note's own literal
# substring at every position where the artifact's own stamps say the rung
# fired. With the note suppressed, the check's `note_premul` bit reads 0
# where the stamp comparison demands 1, and the row fails there while every
# stamp/compile assertion in the same section stays green -- the row must
# NOT turn `--tune=balanced`/etc. into a refusal, since it deletes a
# bookkeeping write, not the flag OR the eligibility test.
SAB_ID="S253-premul-drop-note-unstamped"
SAB_FILE="src/core/compile.c"
SAB_SUITES="tunedial"
SAB_DESC="the premul drop rung still fires (the artifact still shrinks, RX_DFA_TABLE still moves off 'premultiplied', RX_ENGINE_SEL still reads 'size-cap-retry') but the notes loop skips the premul row, so the verbose stderr note Frank's ruling requires never prints -- a silent rescue where the ladder's own contract demands a loud one"
SAB_DOC_FIGURE="docs/dev/known_issues.md K59 (the closing rung); tests/codegen/run_tune_dial.sh section 6's note_premul assertion"
SAB_COUNT=1
# REACH: does the K59 witness still take this rung at all (balanced)? If it
# does not, the note has nothing to fire on and this row measures nothing.
SAB_REACH='"$PCREC" --features unicode-props -e utf8 -p rx -o - --pattern "[^\p{C}\p{M}\p{P}]" | grep -o "size-cap-retry" | head -1'
SAB_REACH_EXPECT='size-cap-retry'
# RE-AIMED 2026-10-08 (lane decfbB3, [DEC-FALLBACK] B3): `dropped_premul` is
# gone; the notes are a loop over the fired record (`fit_fired`), each fired
# row printing its own `note` cell. The plant keeps the row firing and its
# bit recorded, and makes the notes loop skip ONLY the premul row: the same
# "bookkeeping that decides whether the note prints", at its new home.
# Re-verified: under the plant the K59 witness still compiles, still stamps
# size-cap-retry and RX_DFA_TABLE off premultiplied, and prints the anchored
# note but not the premul one.
SAB_BEFORE='            if (fit_rungs[i].note.what && (fit_fired >> i & 1u))'
SAB_AFTER='            if (fit_rungs[i].note.what && (fit_fired >> i & 1u) &&
                fit_rungs[i].act != FIT_DROP_PREMUL)   /* SABOTAGE S253: the premul note never prints */'
