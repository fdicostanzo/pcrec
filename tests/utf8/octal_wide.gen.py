HEAD='''# tests/utf8/octal_wide.rxt -- K125 (lane langfix2): an octal escape above
# `\\377` (`\\400`..`\\777`, U+0100..U+01FF) is ACCEPTED under utf8, in a
# class and outside one, and as the octal reading of the backreference-vs-
# octal rule; it is refused (err 151 "octal value is greater than \\377 in
# 8-bit non-UTF-8 mode") under byte only. The ceiling is the encoding's
# universe, the same range check braced `\\x{...}` takes (pattern_language.md
# §5.2). pcrec refused the utf8 cells with the byte-mode diagnostic before
# the fix.
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 at PCRE2_UTF (tests/lib/
# p2gen.py over p2probe). Outside a class a `\\4`.. escape is module
# `backrefs`' digit row (pattern_language.md §7.3), so those blocks enable it.
'''
B='backrefs'
BLOCKS=[
 dict(c="THE ADVERSARY'S CELL: `\\400` is U+0100.", p='\\400', f=B, e='utf8', s=['Ā','ā','a']),
 dict(c='The top of the three-digit range, U+01FF.', p='\\777', f=B, e='utf8', s=['ǿ','Ǿ']),
 dict(c='In a class.', p='[\\400]', e='utf8', s=['Ā','a']),
 dict(c='A class range across the whole three-digit band above `\\377`.', p='[\\400-\\777]', e='utf8', s=['ſ','Ā','ǿ','Ȁ','ÿ']),
 dict(c='Negated: matches any OTHER character, one whole character wide.', p='[^\\400]', e='utf8', s=['Ā','é']),
 dict(c='After a group: `\\400` with one group is the OCTAL reading (rule 3: 4 > 1 group).', p='(a)\\400', f=B, e='utf8', s=['aĀ','a']),
 dict(c='Quantified.', p='\\400+', f=B, e='utf8', s=['ĀĀ','ā']),
 dict(c='Caseless: U+0100 and U+0101 are a fold pair.', p='\\400', f=B+',modifiers', e='utf8', fl='i', s=['ā','Ā']),
 dict(c='CONTROL: the scan takes at most three digits -- `\\1000` is `\\100` then `0`.', p='\\1000', f=B, e='utf8', s=['@0','@']),
 dict(c='CONTROL: under byte the same escape is still err 151 ...', p='\\400', f=B, s='perr'),
 dict(c='... and in a class.', p='[\\400]', s='perr'),
]
