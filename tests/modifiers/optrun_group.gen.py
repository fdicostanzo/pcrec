HEAD='''# tests/modifiers/optrun_group.rxt -- K124 (lane langfix2): a GROUP whose
# whole body is a bare option setting is an ordinary repeatable group.
# libpcre2 10.46 refuses a quantifier on the bare run itself (`a(?i)*`, err
# 109, pinned in tests/reject/) but accepts it on any group around one:
# `(?:(?i))*a`, `((?s))?a`, `(?=(?m))+a`, `(?>(?i))*a`, `(?i:(?s))*a`. The
# group's body matches the empty string and its option change ends at its
# `)`, so `(?:(?i))*a` is `a` (case-sensitive). pcrec refused all of these
# as err 109 before the fix, because the group handed the run's own
# `not_repeatable` flag up to the quantifier; `pcrec_wrap_bare_anchor` now
# seals every group's body so the group is repeatable.
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 (tests/lib/p2gen.py over
# p2probe). The two `perr` controls at the end are libpcre2's own err 109.
'''
F='modifiers'
BLOCKS=[
 dict(c="THE ADVERSARY'S CELL: `*` on a non-capturing group of `(?i)`; the `(?i)` ends at\nthe group's `)`, so the `a` stays case-sensitive.", p='(?:(?i))*a', f=F, s=['A','a']),
 dict(c='`?` on a capturing group of `(?s)`: group 1 is the empty match.', p='((?s))?a', f=F, s=['a','b']),
 dict(c='`+` on a lookahead of `(?m)`.', p='(?=(?m))+a', f=F+',lookaround,assertions', s=['a']),
 dict(c='`{2}` on a group of an unsetting run.', p='(?:(?-i)){2}a', f=F, s=['a','A']),
 dict(c='`{0}`.', p='(?:(?i)){0}a', f=F, s=['A','a']),
 dict(c='`+` (at least one empty iteration).', p='(?:(?i))+a', f=F, s=['A','a']),
 dict(c='An atomic group.', p='(?>(?i))*a', f=F+',atomic-groups', s=['a','A']),
 dict(c='A scoped group whose body is a bare run.', p='(?i:(?s))*a', f=F, s=['a','A']),
 dict(c='A named group.', p='(?<n>(?i))+a', f=F+',named-groups', s=['a']),
 dict(c='Mid-pattern, under `?`, after a literal.', p='x(?:(?i))?a', f=F, s=['xA','xa']),
 dict(c='A `(?U)` run in a group does not leak out: the `a+` after it stays greedy.', p='(?:(?U))*a+', f=F, s=['aa']),
 dict(c='CONTROL (accepted before the fix too): two runs in one group.', p='(?:(?i)(?s))*a', f=F, s=['a','A']),
 dict(c='CONTROL: the bare run quantified is still err 109 at pattern start ...', p='(?i)*a', f=F, s='perr'),
 dict(c='... and mid-pattern.', p='a(?i)*', f=F, s='perr'),
]
