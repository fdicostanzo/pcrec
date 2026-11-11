#!/usr/bin/env bash
# tests/families/run_quoting_diff.sh — [FEAT-FAMILIES] pre-move differential for
# module `quoting` (\Q...\E) against libpcre2 10.46; body in module_diff.sh.
# The module's only other corpus is the D27 .rxt set (95 cells); this sweeps.
LABEL=quoting
FEATS="quoting,modifiers,classes"
ALPHA='ab.*+'; MAXLEN=3
EXTRA_SUBJECTS=$'a\\b\nQE\n\\Qab\\E\na|b\nab ab\nAB\n(a)\n^a$\na-z\n]a'
PATTERNS='q01	0	\Qa.b\E
q02	0	\Qa.b\Ec
q03	0	a\Q*\E
q04	0	a\Q*\E+
q05	0	\Qab\E+
q06	0	\Qab\E*c
q07	0	\Q\E
q08	0	a\Q\Eb
q09	0	a\Q\E+
q10	0	\Qa\Q\E
q11	0	\Qa|b\E
q12	1	(\Qa|b\E)
q13	0	x\Q(\E
q14	0	\Q.\E{2}
q15	0	a\Eb
q16	0	\Qa
q17	0	(?x)a \Qb c\E d
q18	0	(?i)\Qab\E
q19	0	\Qa\Eb|c
q20	0	^\Qa\E$
q21	0	\Q^\E
q22	0	\Q$\E
q23	0	[\Qa-z\E]
q24	0	[a\Q]\E]
q25	0	[\Q^\E]
q27	0	[a\Q\Eb]
q28	0	[\Q-\E]
q29	0	[a-\Qc\E]
q30	0	\Qa\bc\E
q31	0	\Q\\E
q32	0	\Q\\\E
q33	0	a\Q\E*
q34	0	a(?:\Qb\E)+
q35	0	\Qa\E\Qb\E
q36	0	\Q\Ea
q37	0	a\E\E
q38	0	\Q\E\Q\E
q39	0	(?x)\Qa b\E #c
q41	0	a\Q\E{2}
q42	0	\Q*\E?
q43	0	.\Q.\E
q44	0	\Q\E|a
q45	0	(?:\Q\E)*a'
REFUSALS='r01	\Q\E*
r02	\Q\E+
r03	\Q\E?
r04	*\Qa\E
r05	a**\Q\E
r06	[\Qz-a\E]
r07	[\Q\Ea-\Qa\E]
r08	[z-\Qa\E]
r09	(\Qa\E
r10	\Qa)\E
r11	(?x)\Q#\E
r12	a{\Q2\E}
r13	[\Q\E]
r14	[\E]a'
EXPECT_CELLS=27004; EXPECT_MATCH=5149; EXPECT_REFUSE=14
. "$(dirname "${BASH_SOURCE[0]}")/module_diff.sh"
