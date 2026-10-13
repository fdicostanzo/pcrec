#!/usr/bin/env bash
# S901 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-11) -- a compound's -futf-check prologue validates from Q's lookbehind reach (1) instead of P's, so an ill-formed byte inside P's reach before the start position is no longer refused.
# The twin's plant 2 fired on `\A\s+|\s+\z` because the twin gave Q no reach; as built, both parts stamp `_VALID_LB 1` there.
SAB_ID='S901-cmp11-prologue-q-reach'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='compound'
SAB_DESC='a compound'\''s -futf-check prologue validates from Q'\''s lookbehind reach (1) instead of P'\''s, so an ill-formed byte inside P'\''s reach before the start position is no longer refused'
SAB_DOC_FIGURE='HAND-CHECKED by lane cpb4 2026-10-12: not built: the REACH probe reads `^(?<=xy)a|b$` under -e utf8 -futf-check as RX_COMPOUND "none", so the row is UNREACHED as declared.'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='no admitted compound has a P lookbehind reach above Q'\''s: a floor arm that raises the reach past 1 routes the VM or declines (`^(?<=xy)a|b$`, `^(?<=é)a|b$`), and every admitted P and Q stamp the same `_VALID_LB`; UNREACHED until B6. The REACH probe reads NOW REACHED the day such a pattern ships a compound'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -futf-check -o - --pattern '\''^(?<=xy)a|b$'\'''
SAB_REACH_EXPECT='#define RX_COMPOUND "split"'
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(sb, "#define %s_VALID_LB %d\n", cx->opt->prefix,
                    cx->lb_max);'
SAB_AFTER='    pcrec_sb_printf(sb, "#define %s_VALID_LB %d\n", cx->opt->prefix,
                    cx->job->comp_shell ? 1 : cx->lb_max);   /* SABOTAGE S901 */'
