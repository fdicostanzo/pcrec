#!/usr/bin/env bash
# S849 ([MEMFN] R17-a, lane r17a; setfind.md rev 2.3 §12.5, r4 K2-4) -- W0 0
# ACCEPTED ON A FIND SITE.
#
# WHAT IT BREAKS. A forward FIND STATES its window (W0, pred.window_stated
# 1; memfn.h): 0 is the zero-fill, "unstated", never "move-back 0", so a
# FIND builder that forgot is refused at R17-a rather than read as a default.
# Two lines hold it: site_check's vocabulary refusal (compose.c
# `window_check`) and the gate, which reads W0 0 as a stated NO no row
# serves. The plant removes BOTH (a one-line plant is masked by the other,
# measured): site_check accepts 0, and the classifier reads 0 as unstated, so
# every row serves the site.
#
# WHERE IT IS SEEN. No artifact moves (every pcrec FIND builder states W0).
# C5's gate case window-unstated (a PF walk site with W0 0) RENDERs instead
# of REFUSE (run_arm_pins.sh check 6). Arm memfnarms.
SAB_ID="S849-r17a-window-unstated-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC="a forward FIND stating window_stated 0 (W0 unstated) is accepted and rendered as if its window were the candidate"
SAB_DOC_FIGURE="HAND-MEASURED by lane r17a: see docs/dev/lanes/r17a_report.md (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='window-unstated	REFUSE	mf_define: outside the vocabulary: a forward FIND states its window (`window_stated` 1): 0 is unstated, never move-back 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    } else if (p->window_stated != 1) {'
SAB_AFTER='    } else if (p->window_stated > 1) {      /* SABOTAGE S849: W0 0 accepted */'
SAB_FILE2="memfn/src/gate.c"
SAB_COUNT2=1
SAB_BEFORE2='    return kit_window_site(in->s) ? flag01(in->s->pred.window_stated) : -1;'
SAB_AFTER2='    return kit_window_site(in->s) && in->s->pred.window_stated ? flag01(in->s->pred.window_stated) : -1; /* SABOTAGE S849 */'
