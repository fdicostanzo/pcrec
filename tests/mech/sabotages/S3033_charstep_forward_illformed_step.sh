#!/usr/bin/env bash
# S3033 ([UCP] U3, review 2026-11-10 r4 ucpu3 checks-6/9, lane ucpu3fix) -- THE
# FORWARD WALK STEPS TWO BYTES OVER AN ILL-FORMED BYTE. A byte that does not
# decode is one character; the plant skips the byte after it too. Measured at
# landing: 49 charstep cells red (the subject tip's corpus: 8). The REVERSE
# twin (pos -= 2) is answer-equivalent: no consuming set holds an ill-formed
# byte and a reverse machine has no all-bytes loop, so the walk is dead after
# it (lane report).
SAB_ID="S3033-charstep-forward-illformed-step"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="charstep"
SAB_DESC="the character-stepped forward walk steps two bytes over an ill-formed byte"
SAB_DOC_FIGURE='charstep arm: 49 cells red (measured at landing, lane ucpu3fix); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3033.'
SAB_REACH='"$PCREC" -e utf8 --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)\\b\\w+\\b" >/dev/null 2>&1 && grep -c "define RX_DFA_SCAN \"char-step\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        "        pos += l ? l : 1;\n"'
SAB_AFTER='        "        pos += l ? l : 2;\n"   /* SABOTAGE S3033 */'
