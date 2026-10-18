#!/usr/bin/env bash
# S458 ([K82], lane k82fix) -- A TIE LEADS.
#
# The row's PICK lists the run's scan cube FIRST so a tie keeps the run alone:
# under NONE an exact scan member and the set pick are both one byte, and a
# second pass over an equally rare byte buys nothing (G1's own `<=` argument).
# This plant names the set pick the reader's `rightmost`, so ties go to it and
# every NONE artifact with an exact scan member and a non-empty set grows a
# lead. Detector: run_prechecks.sh §5.11's `é@` (-e utf8) row, lead "-".
# [MEMFN] R17-b' B3b (lane b3b, 2026-10-18) RE-AIMED: the pre-check's presence
# decisions are the memfn kit's routed PRES rows (memfn/src/finder.c `fd_pres`,
# the ports in memfn/src/presence.c) and pcrec lays its parts out from their
# links, so the plant moves to the kit's line that makes the same choice.
# Here: the set-leads port compares `<=`, so a tie leads (intent unchanged).
# The same edit as B3a's S1097 (whose detector is the trace build's five-pick
# comparator); this row's detector is the pre-check suite, which the port now
# reaches because P4 renders.
SAB_ID="S458-set-leads-tie-leads"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="prechecks"
SAB_DESC="the set-leads row's PICK sends a tie to the set pick, so an equally rare byte (every exact scan member under NONE) is memchr'd in front of the run for nothing"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S458."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "é@" && grep -q "^#define RX_REQ_RUN \"c3a940@2\"" "$REACH_TMP/o.c" && ! grep -q "!memchr(subject + search_from, 64," "$REACH_TMP/o.c" && echo REACH-TIE-NO-LEAD'
SAB_REACH_EXPECT="REACH-TIE-NO-LEAD"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            out->set_leads = cube_mass(rate, (unsigned)q, 0xFFu) <'
SAB_AFTER='            out->set_leads = cube_mass(rate, (unsigned)q, 0xFFu) <=   /* SABOTAGE S458 */'
