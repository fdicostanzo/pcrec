HEAD='''# tests/lookaround/lookbehind_group_alt.rxt -- K123 (lane langfix2): a
# lookbehind ALTERNATIVE that is itself a non-capturing or scoped group with
# two or more alternatives. Such a group parses to a bare A_ALT, the same kind
# as the lookbehind's own top-level spine, and before the fix both the width
# rule and `vm_look_behind` read it AS spine and failed every such pattern
# with "internal error: a lookbehind body's alternation spine is longer than
# its reported branch count". The branch count the parse reported is now
# authoritative (`pcrec_lookbehind_branches`).
#
# Two halves. ACCEPTED: the group's alternatives share one length, so the
# top-level branch is fixed-width and compiles (first branch, later branch,
# scoped `(?i:...)`, the `(*plb:` spelling, negative, captures inside). And
# VARIABLE: the group's alternatives differ in length, so the top-level
# branch varies. pcrec refused these by capability until [VLOOKBEHIND] stage
# 1 built the candidate loop (pattern_language.md §7.4); they answer now, and
# a refusal was never the internal error.
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 (tests/lib/p2gen.py over
# p2probe).
'''
F='lookaround'
BLOCKS=[
 dict(c="THE ADVERSARY'S CELL: a non-capturing group of two same-length alternatives.", p='(?<=(?:ab|cd))x', f=F, s=['cdx','abx','adx','x']),
 dict(c='Three alternatives, one length.', p='(?<=(?:ab|cd|ef))x', f=F, s=['efx','abx','aex']),
 dict(c='The group is the FIRST of two top-level branches (it is what the spine walk\nleaves over), different length from the second.', p='(?<=(?:ab|cd)|e)x', f=F, s=['cdx','ex','dx']),
 dict(c='The group is the LAST top-level branch.', p='(?<=e|(?:ab|cd))x', f=F, s=['cdx','ex','bx']),
 dict(c='Captures inside the group: which alternative committed is observable.', p='(?<=(?:(a)|(b)))x', f=F, s=['bx','ax','cx']),
 dict(c='A scoped `(?i:...)` group (the adversary\'s second shape), same length.', p='(?<=(?i:ab|cd))x', f=F+',modifiers', s=['CDx','aBx','cbx']),
 dict(c='The `(*plb:` spelling.', p='(*plb:(?:ab|cd))x', f=F, s=['abx','acx']),
 dict(c='Negative polarity.', p='(?<!(?:ab|cd))x', f=F, s=['abx','acx','x']),
 dict(c='A counted repeat inside the group, same length.', p='(?<=(?:a{2}|bc))x', f=F, s=['aax','bcx','ax']),
 dict(c='Nested groups of alternatives.', p='(?<=(?:a(?:b|c)|d(?:e|f)))x', f=F, s=['acx','dfx','adx']),
 dict(c="VARIABLE: one top-level branch of width 1..2 (a varying branch since\n[VLOOKBEHIND] stage 1).", p='(?<=(?:a|bc))x', f=F, s=['ax','bcx','cx','x'], po=1),
 dict(c="VARIABLE, scoped.", p='(?<=(?i:a|bc))x', f=F+',modifiers', s=['Ax','bCx','cx'], po=1),
 dict(c="VARIABLE, the group first of two branches (a varying branch, then a fixed\none).", p='(?<=(?:a|bc)|d)x', f=F, s=['ax','bcx','dx','cx'], po=1),
 dict(c="VARIABLE, negative polarity.", p='(?<!(?:a|bc))x', f=F, s=['ax','bcx','cx','x'], po=1),
]
