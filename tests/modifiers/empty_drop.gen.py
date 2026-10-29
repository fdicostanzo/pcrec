HEAD='''# tests/modifiers/empty_drop.rxt -- [FLAG-SPELL] (lane flagfix): a
# concatenation drops an empty node that carries nothing (src/parse/parse.c
# p_cat), so a bare option run `(?i)abc` and the scoped `(?i:abc)` build one
# tree. The drop runs after a quantifier has bound to its operand, so it can
# never change what a quantifier applies to. These cells are the ruling's
# (flagfix_rulings.md R1) pins of that boundary:
#   - `(?i)abc+` repeats the `c`, `(?i:abc)+` repeats the group: different
#     matchers, never paired by the spelling identity check;
#   - a QUANTIFIED empty group (`a(?:)+b`, `a(?:)*b`, `a(?:){3}b`) is a
#     quantifier node, not an empty one, and is left alone;
#   - a quantifier right after a bare run is still libpcre2's err 109;
#   - a branch that is empty after the drop stays an empty branch.
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 (tests/lib/p2gen.py over
# p2probe).
'''
F='modifiers'
BLOCKS=[
 dict(c='The bare run: the `+` binds to `c` alone.', p='(?i)abc+', f=F, s=['abcc','abcabc','ABCC','ab']),
 dict(c='The scoped run: the `+` binds to the group.', p='(?i:abc)+', f=F, s=['abcc','abcabc','ABCaBc','ab']),
 dict(c='A quantified empty group stays a quantifier node: `+`.', p='a(?:)+b', f=F, s=['ab','b','aab','a']),
 dict(c='... `*`.', p='a(?:)*b', f=F, s=['ab','b','xaby']),
 dict(c='... `{3}`.', p='a(?:){3}b', f=F, s=['ab','aXb']),
 dict(c='An unquantified empty group between two atoms.', p='a(?:)b', f=F, s=['ab','a b','xab']),
 dict(c='The bare run mid-pattern.', p='a(?i)bc', f=F, s=['aBC','ABC','abc']),
 dict(c='The run at the END of the pattern.', p='abc(?i)', f=F, s=['abc','ABC','xabcx']),
 dict(c='The run as the whole pattern: one empty match.', p='(?i)', f=F, s=['','x']),
 dict(c='Two runs and nothing else.', p='(?i)(?s)', f=F, s=['','x']),
 dict(c='The run inside a capturing group ends at its `)`: `b` stays case-sensitive.', p='(a(?i))b', f=F, s=['ab','aB','Ab']),
 dict(c='An alternation branch that is only a run stays an EMPTY branch (it matches first, at 0).', p='(?i)|x', f=F, s=['x','','yx']),
 dict(c='... and as the second branch, where it leaks into nothing after it.', p='x|(?i)', f=F, s=['x','X','y']),
 dict(c='... and inside a capturing group.', p='(x|(?i))y', f=F, s=['xy','y','XY','Y']),
 dict(c='A quantifier on the bare run mid-pattern is err 109 (`+`) ...', p='a(?i)+b', f=F, s='perr'),
 dict(c='... (`*`) ...', p='a(?i)*b', f=F, s='perr'),
 dict(c='... and at pattern start.', p='(?i)+', f=F, s='perr'),
]
