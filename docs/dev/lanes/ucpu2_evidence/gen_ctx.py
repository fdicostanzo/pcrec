import sys
exec(open('/tmp/ucpu2s/p2.py').read())
def esc(b):
    out=''
    for c in b:
        if c == 0x22: out += '\\"'
        elif c == 0x5c: out += '\\\\'
        elif 0x20 <= c < 0x7f: out += chr(c)
        else: out += '\\x%02x' % c
    return '"'+out+'"'
out=[]
def block(pat, enc, flags, subjects, note=None, feats='all', starts=()):
    opts = 0
    if enc == 'utf8': opts |= UTF
    if 'u' in flags: opts |= UCP
    if 'i' in flags: opts |= CASELESS
    pb = pat.encode('utf-8')
    if note:
        for ln in note.split('\n'): out.append('# ' + ln)
    out.append('# pcre2-only')
    out.append('pattern ' + pat)
    if enc: out.append('encoding ' + enc)
    if flags: out.append('flags ' + flags)
    if feats: out.append('features ' + feats)
    for s in subjects:
        sb = s.encode('latin-1') if enc != 'utf8' and isinstance(s, str) else (s.encode('utf-8') if isinstance(s, str) else s)
        r = oracle(opts, pb, sb)
        if r is None: out.append('n ' + esc(sb))
        elif isinstance(r, tuple): out.append('m %s %d %d' % (esc(sb), r[0], r[1]))
        else: raise SystemExit('oracle %s on %r %r' % (r, pat, sb))
    for (sp, s) in starts:
        sb = s.encode('latin-1') if enc != 'utf8' else s.encode('utf-8')
        r = oracle(opts, pb, sb, sp)
        if r is None: out.append('ns %d %s' % (sp, esc(sb)))
        elif isinstance(r, tuple): out.append('ms %d %s %d %d' % (sp, esc(sb), r[0], r[1]))
        else: raise SystemExit('oracle %s' % r)
    out.append('')

HDR = '''# [UCP] U2 -- THE CONTEXT NODE (A_CTX) and T3's recognizer (ucp_design.md
# §2.2, §2.4, §6 U2). A one-character lookaround and `\\b`/`\\B` are ONE node;
# the DFA carries it on a per-machine context-SET list whose ATOMS (membership
# vectors) replace the fixed word/newline/non-start partition. These cells
# are the U2 row's own:
#   - the OVERLAP WITNESSES: the census's k=2 pattern `(?<=\\$)\\d+(?:\\.\\d{2})?\\b`,
#     a nested V ⊂ W pair (`(?<=[aeiou])x\\b`), and a partially overlapping
#     pair (`(?<=[0-9a-f])x(?=[a-z_])`) — subjects separate every atom, so a
#     partition that collapses V∩W onto one set answers some cell wrong;
#   - T3's row 1 over the LANGUAGE (alternation, class, atomic, alpha and
#     non-atomic spellings, quantified lookarounds) and its declines
#     (two characters, a capture, a nullable body), each answer-checked;
#   - startpos cells: a lookbehind's context lies BEFORE the window (the
#     seeded start states) and a lookahead's after the match end (the reverse
#     machine's seeds);
#   - UCP `\\b`/`\\B` under `-e byte` (the Latin-1 word set).
#
# ORACLE: libpcre2 with the options each block states (`encoding utf8` =
# PCRE2_UTF, `flags u` = PCRE2_UCP). Generated from 10.48 and re-verified
# against the 10.46 reference (docs/dev/lanes/ucpu2_evidence/); `verify_ucp.py`
# re-checks every cell on every `make test`. `# pcre2-only`: python `re` has
# no PCRE2_UCP. Ill-formed-UTF-8 hazard cells (§2.3) live in
# tests/utf8/axis13_ctx_illformed.rxt, whose oracle is MATCH_INVALID_UTF.
'''
for enc in ('', 'utf8'):
    block(r'(?<=\$)\d+(?:\.\d{2})?\b', enc, '', ['a $12.34 b','$12.3x','x12','$1_','$$9','$9.99.','a$1 $2','$','9$'],
          note='the census k=2 witness: sets {$} and \\w (disjoint): three atoms' if not enc else None)
    block(r'(?<=[aeiou])x\b', enc, '', ['ax','bx','axe','axa','ex y','ux_','Ax','x','aax','ax.','ixi'],
          note='V ⊂ W: every vowel is a word character; `axa` needs the W bit of a V∩W byte' if not enc else None)
    block(r'(?<=[0-9a-f])x(?=[a-z_])', enc, '', ['axb','7xz','gxb','ax7','fx_','9x','x','Fxb','ax','bxa'],
          note='partial overlap: {0-9a-f} and {a-z_} share a-f; atoms hex-only, both, word-only, neither' if not enc else None)
    block(r'\b(?<![aeiou])\w+(?=[aeiou])', enc, '', ['strea','b','ba','ab','xyzzy','  tro'],
          note='three context sets on one machine (word, V twice by polarity)' if not enc else None)
# T3 rows
for p, subs in [
    (r'(?<=a|b)x', ['ax','bx','cx','x']),
    (r'(?<=[ab])x', ['ax','bx','cx','x']),
    (r'(?=[ab])\w+', ['a1','ca','cb','c']),
    (r'(?<![a-c])\d', ['a1','d1','1','c9']),
    (r'x(?!y)', ['xy','xz','x','yxy']),
    (r'(?<=\d)(?=\d)', ['12','1a2','a','123']),
    (r'(?*a)b', ['ab','b','ba']),
    (r'(?<*a)b', ['ab','b','cb']),
    (r'(*plb:a)b', ['ab','b']),
    (r'(*nla:a)\w', ['ab','ba','a']),
    (r'(?=a)*b', ['b','ab']),
    (r'(?<=a)+b', ['ab','b']),
    (r'(?=(?>a|b))\w', ['a','b','c']),
    (r'(?<=(?:a))b', ['ab','cb']),
    (r'(?i)(?<=a)b', ['ab','Ab','aB','cb']),
    (r'(?=[^a])', ['a','b','']),
    (r'(?<=[^a])b', ['ab','cb','b']),
    # declines: stay a lookaround, same answers
    (r'(?<=ab)x', ['abx','bx','ax']),
    (r'(?=a|bc)\w', ['a','bc','b']),
    (r'(?=a?)b', ['b','ab']),
    (r'(?<=\b)a', ['a','ba',' a']),
]:
    block(p, '', '', subs)
block(r'(?<=(a))x', '', '', ['ax','bx'], note='a capture-bearing body: T3 declines (the VM keeps the capture; g 1 read from the oracle ovector)')
out.insert(len(out)-2, 'g 1 0 1')
# startpos cells
block(r'(?<=a)b', '', '', ['ab'], starts=[(1,'ab'),(1,'cb'),(2,'aab'),(0,'b')],
      note='the lookbehind context is BEFORE the window: startpos seeds')
block(r'(?<!a)b', '', '', ['ab'], starts=[(1,'ab'),(1,'cb')])
block(r'b(?=a)', '', '', ['ba','bb'], starts=[(1,'bba'),(0,'bab')],
      note='the lookahead context is AFTER the match: the reverse machine seeds from s[end]')
block(r'b(?!a)', '', '', ['ba','b'], starts=[(1,'bba'),(1,'bbc')])
block(r'\b\w', '', '', ['a'], starts=[(1,'ab'),(1,' a')])
# UCP \b under byte: the Latin-1 word set
for p, subs in [
    (r'(*UCP)\b\w+\b', ['caf\xe9 x', '\xe9t\xe9', '\xb2x', ' \xaa ', 'a\xd7b', '\xb5']),
    (r'(*UCP)x\b', ['x\xe9', 'x ', 'x\xd7', 'x']),
    (r'(*UCP)x\B', ['x\xe9', 'x ', 'x\xdf']),
    (r'(*UCP)(?aW)x\b', ['x\xe9', 'x ']),
    (r'(*UCP)(?<=\w)x', ['\xe9x', ' x', '\xd7x']),
]:
    block(p, '', '', subs, note=None)
block(r'x\b', '', 'u', ['x\xe9','x '], note='`flags u` (--ucp) is the same axis as (*UCP)')
block(r'(?m)^ERROR(?:(?=\n)|\z)', '', '', ['ab\nERROR\nx','ERROR','xERROR\n','ERRORx\n'],
      note='a SHARED context set: `(?=\\n)` and `(?m)^` read the same newline set, one list entry that both\nthe context node and the multiline arms must find (the lookaround-expansion corpus found it)')
block(r'(?m)(?:\A|(?<=\n)(?!\z))ERROR$', '', '', ['ab\nERROR\nx','ERROR','xERROR','\nERROR'])
block(r'(?m)(?<=\n)a|b$', '', '', ['\na','b\n','ab','\nb'])
block(r'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)', '', '', ['xa','xq','xz','x','axr'],
      note='17 singleton context sets: 18 atoms, over PCREC_MAX_CTX_ATOMS (16) -- the DFA is DECLINED\n(limits.md §3.9) and the VM answers; the route manifest pins which engine')
block(r'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!i)(?!j)(?!k)(?!l)(?!m)(?!n)', '', '', ['xa','xn','xz','x'],
      note='14 singleton sets: 15 atoms, under the cap -- the DFA builds it')
sys.stdout.write(HDR + '\n' + '\n'.join(out))
