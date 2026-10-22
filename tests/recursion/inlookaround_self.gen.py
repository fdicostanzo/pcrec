HEAD='''# tests/recursion/inlookaround_self.rxt -- K127 (lane langfix2): a call inside
# a lookbehind whose length computation RE-ENTERS A GROUP CONTAINING THAT
# LOOKBEHIND is refused, as libpcre2 10.46 refuses it (err 125, "length of
# lookbehind assertion is not limited"). pcrec accepted these before the fix
# (a lookbehind contributes 0 to its group's width, so the callee's width
# looked fixed) and the artifacts answered no-match or gave up with
# PCREC_ERR_FRAMES. The rule (`pcrec_callgraph_lookbehind_recurses`): follow
# the lookbehind body's calls, and each callee's calls, except calls inside a
# nested lookahead (a nested lookbehind's calls ARE followed); refuse if a
# reached group contains the lookbehind anywhere (a lookaround included). A
# call under `{0}` still counts.
#
# The ACCEPTED controls are the boundary: a call to a group that does not
# contain the lookbehind, and the re-entry reached only through a lookahead.
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 (tests/lib/p2gen.py over
# p2probe); every `perr` block is one libpcre2 also refuses (err 125).
'''
F='recursion,lookaround'
FN='recursion,lookaround,named-groups'
BLOCKS=[
 dict(c="THE ADVERSARY'S CELLS: the whole pattern, called from a lookbehind inside it.", p='(?<=(?R))x', f=F, s='perr'),
 dict(c='', p='x(?<=(?R))', f=F, s='perr'),
 dict(c='A numbered group calling itself from a lookbehind in its body.', p='((?<=(?1))a)', f=F, s='perr'),
 dict(c='Negative polarity.', p='((?<!(?1))x)', f=F, s='perr'),
 dict(c='Through a second group that calls back (`(?2)` -> `(?1)`, which contains it).', p='((?<=(?2))a)(b|(?1))', f=F, s='perr'),
 dict(c='The lookbehind nested in a lookahead inside the called group still counts.', p='(a(?=(?<=(?1))))', f=F, s='perr'),
 dict(c='Under `{0}` (lexical, as libpcre2 counts it).', p='((?<=(?1){0})x)', f=F, s='perr'),
 dict(c='Under an atomic group.', p='((?<=(?>(?1)))x)', f=F+',atomic-groups', s='perr'),
 dict(c='One of two top-level alternatives.', p='(?<=(?R)|b)x', f=F, s='perr'),
 dict(c='A DEFINE\'d named group.', p='(?(DEFINE)(?<g>a(?<=(?&g))))x(?&g)', f=FN, s='perr'),
 dict(c='A NESTED LOOKBEHIND IS FOLLOWED (lane langfix3): group 2 re-enters group 1\nthrough its own lookbehind. libpcre2 10.46: err 125 at offset 1.', p='((?<=(?2)))(a(?<=(?1)))', f=F, s='perr'),
 dict(c='The same through a negative lookbehind (libpcre2: err 125 at 1).', p='((?<=(?2)))(a(?<!(?1)))', f=F, s='perr'),
 dict(c='The nested lookbehind\'s call after a literal (libpcre2: err 125 at 1).', p='((?<=(?2)))(a(?<=b(?1)))', f=F, s='perr'),
 dict(c='A three-group cycle through two nested lookbehinds. libpcre2 reports err 125\nat offset 31 (the lookbehind in group 3); pcrec refuses at 19 (group 2\'s),\nwhich is also on the cycle.', p='(?<=(?1)|(?2))(a)(b(?<=(?3)))(c(?<=(?2)))', f=F, s='perr'),
 dict(c='ACCEPTED: the callee does not contain the lookbehind.', p='(?<=(?1))(a)', f=F, s=['aa','a']),
 dict(c='ACCEPTED: a lookbehind after the group it calls.', p='(a)(?<=(?1))', f=F, s=['aa','b']),
 dict(c='ACCEPTED: the call back to group 1 is reached only through a lookahead in group 2.', p='((?<=(?2))a)(b(?=(?1)))', f=F, s=['ba','b','xa']),
 dict(c='ACCEPTED: the same re-entry through a nested LOOKAHEAD is not followed. (On\n"aa" both libpcre2 (-52, recursion loop) and pcrec (-3) give up at match\ntime, so no such subject is here.)', p='((?<=(?2)))(a(?=(?1)))', f=F, s=['a','ba','x']),
 dict(c='ACCEPTED: the same through a negative lookahead.', p='((?<=(?2)))(a(?!(?1)))', f=F, s=['a','ba','x']),
 dict(c='ACCEPTED: the lookbehind sits in a group the lookbehind does not call.', p='((?<=(?2)))(?2)(a)', f=F, s=['a','aa']),
 dict(c='ACCEPTED: a forward named call (the deferred width re-check\'s own cell).', p='^(?:(?<g>ab)){0}ab(?<=(?&g))$', f=FN, s=['ab','abab']),
]
