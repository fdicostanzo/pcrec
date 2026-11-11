#!/usr/bin/env bash
# tests/families/run_named_diff.sh — [FEAT-FAMILIES] pre-move differential for
# module `named-groups` against libpcre2 10.46; body in module_diff.sh. The
# module's rows are the three DECLARING spellings; the references (\k, \g,
# (?P=n)) belong to `backrefs` and are enabled here only so declared names are
# exercised the way users write them. tests/named_groups/*.rxt pins chosen
# cells (python `re` for (?P<>) plus translation for the others); this sweeps
# against the real oracle, with every group span compared.
LABEL=named-groups
FEATS="named-groups,backrefs,modifiers,classes,lookaround"
ALPHA='abx'; MAXLEN=4
EXTRA_SUBJECTS=$'aa\nabab\nAB\nAb\nba\nabba\nxax'
PATTERNS='n01	1	(?<n>a)
n02	1	(?'"'"'n'"'"'a)
n03	1	(?P<n>a)
n04	2	(?<n>a)(?<m>b)
n05	2	(?<n>a)|(?<m>b)
n06	2	(?<n>a)(b)
n07	3	(b)(?<n>a)(x)
n08	1	(?<n>a)\k<n>
n09	1	(?<n>a)\k'"'"'n'"'"'
n10	1	(?<n>a)\k{n}
n11	1	(?<n>a)\g{n}
n12	1	(?<n>a)(?P=n)
n13	1	(?<n>a)\1
n14	1	(?<n>a|b)+
n15	1	(?<n>a)*
n16	1	(?<n>a)?
n17	2	(?<n>(?<m>a)b)
n18	1	(?:(?<n>a)|b)+
n19	1	(?n)(a)(?<n>b)
n20	1	(?<_x1>a)
n21	2	(?<A>a)(?<a>b)
n22	1	(?<n>a)(?i)\k<n>
n23	1	\k<n>(?<n>a)
n24	1	(?<=a)(?<n>b)
n25	1	(?<n>a)(?<!a)b
n26	1	(?<n>a(?=b))b
n27	2	(?<n>a)|(?<n2>b)\k<n2>
n28	1	^(?<n>a*)\k<n>$
n29	2	(?<n>a)(?:(?<m>b)|x)
n30	1	(?<n>)a
n31	1	(?<n>a|)b
n32	1	(?<n>^a)
n33	2	(?<N1>a)(?<n1>b)
n34	1	(?P<n>a)(?P=n)
n35	1	(?<n>.)\k<n>
n36	1	(?<n>[ab])+x
n37	2	(?J)(?<n>a)(?<n>b)\k<n>
n39	2	(?i)(?<n>A)(?-i)(?<m>b)
n40	1	(?<abcdefghijklmnopqrstuvwxyzabcdefgh>a)'
REFUSALS='r01	(?<n>a)(?<n>b)
r02	(?<1n>a)
r03	(?<n a)
r04	(?<>a)
r05	(?<n>a
r06	(?'"'"'n>a)
r07	(?P<n'"'"'a)
r08	(?Pn>a)
r09	(?<n>a)\k<m>
r10	(?<n-1>a)
r11	(?<n>a)\k<n
r12	(?<n>a)\g{m}
r13	(?P=n)(?<n>a)
r14	(?<n>a)(?P=m)
r15	(?<ab\ncd>a)
r16	(?<123>a)
r17	(?P<>a)
r18	(?<nn>a)(?<nn>b)(?J)
r19	(?<a-b>c)
r20	(?<n>a)(?<N>b)(?<n>c)'
EXPECT_CELLS=21567; EXPECT_MATCH=5719; EXPECT_REFUSE=20
. "$(dirname "${BASH_SOURCE[0]}")/module_diff.sh"
