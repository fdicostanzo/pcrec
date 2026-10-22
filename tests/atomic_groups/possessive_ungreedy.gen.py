HEAD='''# tests/atomic_groups/possessive_ungreedy.rxt -- K122 (lane langfix2): a
# POSSESSIVE quantifier is GREEDY whatever `(?U)` says. `(?U)` inverts the
# default greed of a plain quantifier and a trailing `?` inverts it back
# (tests/modifiers/), but `X q+` is `(?>X q)` with q GREEDY: libpcre2 10.46
# answers `(?U)a*+` on "aaa" (0,3). pcrec answered (0,0) on both engines
# before the fix (the desugar kept the ungreedy default), so every block
# here is written twice, the default engine and `engine vm`.
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 (tests/lib/p2gen.py over
# p2probe, the adversary's own oracle driver), never by hand. python3 `re`
# has no `(?U)`, so every block is `# pcre2-only`.
'''
F='atomic-groups,classes,modifiers'
pats=[
 ('THE ADVERSARY\'S CELL: `*+` under `(?U)` takes every `a`.', '(?U)a*+', ['aaa','b','aab']),
 ('`++` under `(?U)`.', '(?U)a++', ['aaa','b']),
 ('`?+` under `(?U)`.', '(?U)a?+', ['a','b']),
 ('`{n,m}+` under `(?U)`: three, not the minimum two.', '(?U)a{2,3}+', ['aaa','aa','a']),
 ('`{n,}+` under `(?U)`.', '(?U)a{2,}+', ['aaaa','a']),
 ('`{,m}+` under `(?U)` (K117 spelling), after a set-then-scope.', 'a(?U)\\s{,2}+', ['a\nb','a\n\n\nb']),
 ('The cut is still a cut: `(?U)a*+a` never matches.', '(?U)a*+a', ['aaa']),
 ('A group body and its capture: the last iteration is the second byte.', '(?U)(a|b)*+', ['ab','abba']),
 ('Inside a scoped `(?U:...)` and its unscoped twin.', '(?U:\\s*+)b', ['a\nb']),
 ('CONTROL: the lazy `?` still inverts under `(?U)` (greedy), beside a possessive.', '(?U)a+?b??', ['aab','aa']),
 ('CONTROL: a plain quantifier under `(?U)` stays lazy.', '(?U)a+', ['aaa']),
]
BLOCKS=[]
for c,p,s in pats:
    BLOCKS.append(dict(c=c,p=p,f=F,s=s,po=1))
    BLOCKS.append(dict(c='the same block under engine vm',p=p,f=F,s=s,po=1,eng='vm'))
