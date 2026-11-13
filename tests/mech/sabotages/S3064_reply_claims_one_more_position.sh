#!/usr/bin/env bash
# S3064 -- R-38 K38-2 (docs/design/memfn/span_runs_sheet.md rev 1.3 §2.4 C2's decision plant;
# §5 K38-2 PLAN (c) FAM-2; lane k382). THE REPLY CLAIMS ONE MORE POSITION: mf_class.run as
# mf_ask (compose.c ask_sel's presence ask) and mf_defined (define_sel) answer it says ver_len + 1
# where the extent ends before the run does, while the renderer (fd_pres_run's quiet ask) renders
# the old extent.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), C2's text classifier: EXTENT, a
# position the reply claims verified is not compared; it reads the extent OFF THE REPLY (FAM-2).
SAB_ID="S3064-reply-claims-one-more-position"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2pres"
SAB_DESC="the run reply says ver_len + 1 while the text compares the old extent: C2's classifier (EXTENT) must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3064 RED (EXTENT: part at 0 len 32: position 30 is NOT compared, the reply's stretch is [22, 31); oracle violations=120). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3064."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        return fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, &why) ? -1 : 0;'
SAB_AFTER='        if (fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, &why)) return -1;   /* SABOTAGE S3064 */
        { int r_ = kit_pres_run(s); if (r_ >= 0 && out->pres[r_].verify && out->run.ver_len && out->run.ver_lo + out->run.ver_len < kit_pres_run_span(s, r_)->len) out->run.ver_len++; }
        return 0;'
SAB_FILE2="memfn/src/compose.c"
SAB_COUNT2=1
SAB_BEFORE2='            return kit_fail(art, "mf_define: the presence decision refuses this site: %s", pw);'
SAB_AFTER2='            return kit_fail(art, "mf_define: the presence decision refuses this site: %s", pw);
        { int r_ = kit_pres_run(s); if (r_ >= 0 && r->cls.pres[r_].verify && r->cls.run.ver_len && r->cls.run.ver_lo + r->cls.run.ver_len < kit_pres_run_span(s, r_)->len) r->cls.run.ver_len++; }   /* SABOTAGE S3064 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-REPLY-ROOM"
