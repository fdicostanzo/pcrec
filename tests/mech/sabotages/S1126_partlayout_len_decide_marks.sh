#!/usr/bin/env bash
# S1126 ([ENTRY-TABLE] E1, lane e1fix; review r1 F9; compound_entries.md
# §3.0 I5) -- `pcrec_sb_len_decide` STOPS SUBTRACTING THE MARKS. Its readers
# are the size term's early abort (`abort_over`, armed at 3 x the code cap on
# ladder attempts only) and `<PREFIX>_VM_PROGRAM_BYTES` (the VM program's own
# buffer, `vmsb`, which never holds a mark: measured by hand, the stamp is
# unmoved under the plant). So the subtraction can decide an outcome only
# where a ladder attempt's decision length lies within the marks' bytes (4
# per head mark, 5 for the stamp mark) of 3 x cap AND that attempt would
# still fit the cap, i.e. its comment-excluded size is at most a third of
# its raw size: prose above two thirds of the artifact. The most comment-
# heavy artifact measured is about half prose (`limits.md` §8's size term:
# 47.8 % over the corpus; 52 % for the near-cap witness below under
# -fcomments), so every attempt the abort could stop is one the caps refuse
# anyway. UNREACHED: the probe asks for a witness whose prose exceeds two
# thirds of its raw bytes.
SAB_ID="S1126-partlayout-len-decide-marks"
SAB_FILE="src/core/sb.c"
SAB_SUITES="partlayout"
SAB_DESC='pcrec_sb_len_decide stops subtracting the part-layout marks, so the size term'"'"'s early abort reads a controlled attempt as up to nine bytes longer'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): reach MISSING, UNREACHED as expected (the probe found no witness above two-thirds prose: 87,311 bytes, 41,814 of code), against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1126."
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='the early abort fires at 3 x the code cap, and an attempt within the marks'"'"' 9 bytes of that bound fits the cap only if more than two thirds of its raw bytes are prose; the most comment-heavy artifact measured is about half prose, and the other reader (VM_PROGRAM_BYTES, vmsb) never holds a mark (lane e1fix, 2026-10-18)'
SAB_COUNT=1
SAB_REACH='out=$("$PCREC" -p rx -fcomments --warn-emit-bytes=1 --part-residual=shared -o "$REACH_TMP/x.c" --pattern "((a)|ab){0,500}c" 2>&1); t=$(echo "$out" | sed -n "s/.*large artifact: \([0-9]*\) bytes.*/\1/p"); k=$(echo "$out" | sed -n "s/.*(\([0-9]*\) of code).*/\1/p"); echo "total=$t code=$k"; [ -n "$t" ] && [ $((3 * k)) -lt "$t" ] && echo REACH-PROSE-OVER-TWO-THIRDS'
SAB_REACH_EXPECT='REACH-PROSE-OVER-TWO-THIRDS'
SAB_BEFORE='    size_t n = pcrec_sb_len_uncut(sb) - sb->simd_guarded - sb->layout_bytes;'
SAB_AFTER='    size_t n = pcrec_sb_len_uncut(sb) - sb->simd_guarded;   /* SABOTAGE S1126 */'
