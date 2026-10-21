#!/usr/bin/env bash
# S891 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-1) -- the controller relocates Q to `from` itself (D163's literal text) instead of next_pos(from), so Q re-asks the position F already refused.
# Evidence: the twin's plant 1 (docs/design/compound/twin/).
# RE-ANCHORED 2026-10-21 (lane i1build, [FINDALL-NEXT] I1): the controller calls the residual's static twin; same plant, same detector.
SAB_ID='S891-cmp1-q-from-from'
SAB_FILE='src/gen/emit_compound.c'
SAB_SUITES='compound'
SAB_DESC='the controller relocates Q to `from` itself (D163'\''s literal text) instead of next_pos(from), so Q re-asks the position F already refused'
SAB_DOC_FIGURE='HAND-CHECKED by lane cpb4 2026-10-12: not built: the REACH probe reads `(?>^a|ab)c` as RX_COMPOUND "none" (it routes the VM), so the row is UNREACHED as declared.'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='every admitted compound is DFA, and a non-atomic DFA Q matches at `from` only where P does (its killed anchors are true there), so the plant moves no answer in the first build; the witness `(?>^a|ab)c` routes the VM (A4/A1) until B6. The REACH probe reads NOW REACHED the day that witness ships a compound'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern '\''(?>^a|ab)c'\'''
SAB_REACH_EXPECT='#define RX_COMPOUND "split"'
SAB_COUNT=1
SAB_BEFORE='"lower = %s__next_pos(subject, subject_length, search_from);", p)'
SAB_AFTER='"lower = search_from; (void)%s__next_pos;   /* SABOTAGE S891 */", p)'
