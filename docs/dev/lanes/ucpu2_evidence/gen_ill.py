import sys
exec(open('/tmp/ucpu2s/p2.py').read())
exec(open('/tmp/ucpu2s/gen_ctx.py').read().split("out=[]")[0].split("exec(open")[0])
def esc(b):
    out=''
    for c in b:
        if c == 0x22: out += '\\"'
        elif c == 0x5c: out += '\\\\'
        elif 0x20 <= c < 0x7f: out += chr(c)
        else: out += '\\x%02x' % c
    return '"'+out+'"'
out=[]
def block(pat, subs, note=None):
    if note:
        for ln in note.split('\n'): out.append('# ' + ln)
    out.append('# pcre2-only'); out.append('pattern ' + pat); out.append('encoding utf8'); out.append('features all')
    for sb in subs:
        r = oracle(UTF|MIU, pat.encode('utf-8'), sb)
        if r is None: out.append('n ' + esc(sb))
        elif isinstance(r, tuple): out.append('m %s %d %d' % (esc(sb), r[0], r[1]))
        else: raise SystemExit('oracle %r %r %r' % (r, pat, sb))
    out.append('')
HDR='''# [UCP] U2 -- the context node over ILL-FORMED UTF-8 (ucp_design.md §2.3's
# hazard cells). A context set every member of which is ASCII reads EXACTLY on
# bytes in both directions, ill-formed input included: a stray continuation
# byte, a lead byte and 0xFF are all outside every ASCII set, which is ⊥'s
# rule (§3.5). A set with a non-ASCII member does NOT, which is why T3's row 1
# admits only byte-expressible sets (`pcrec_enc_set_bytes`) and `(?<=[^a])a`
# keeps its VM lookbehind: an all-byte context would read 0x80 as "in [^a]"
# and answer (1,2) on `80 61`, where libpcre2 answers nomatch. The first two
# blocks are the design's own cells; the rest pin the ASCII sets T3 DOES turn
# into context nodes against the same inputs.
#
# ORACLE: libpcre2 under PCRE2_UTF|PCRE2_MATCH_INVALID_UTF — pcrec's ruled
# `-e utf8` semantics (utf8_design.md §2.6; axis03's rule). Generated from
# 10.48, re-verified against 10.46 (docs/dev/lanes/ucpu2_evidence/). Plain
# PCRE2_UTF would refuse these subjects outright, so `verify_ucp.py`'s in-
# pattern-verb oracle cannot check this file; tests/harness/run.sh (pcrec's
# live behaviour) does, and the expectations are the MIU oracle's.
'''
block(r'(?<=[^a])a', [b'\x80a', b'\xc3\xa9a', b'ba', b'aa', b'\xffa', b'\xe6\x97a'],
      note='§2.3: a NON-ASCII context set stays a lookaround (T3 declines it)')
block(r'(?![^a])', [b'\xe6\x97a', b'a', b'\xc3\xa9', b''])
block(r'(?<=a)b', [b'a\x80b', b'ab', b'\x80ab', b'\xc3\xa9b'],
      note='ASCII context sets: the context node, exact over ill-formed bytes')
block(r'(?<![a])b', [b'\x80b', b'ab', b'\xffb', b'\xc3\xa9b'])
block(r'b(?!a)', [b'b\x80', b'ba', b'b\xc3\xa9', b'b'])
block(r'b(?=[^\x80-\x{10ffff}])', [b'bz', b'b\xc3\xa9', b'b\x80', b'b'],
      note='a negated class whose complement is ASCII-only is byte-expressible')
block(r'\b\w', [b'\x80a', b'\xc3\xa9a', b'a'])
block(r'(?<=[a-z])\x{e9}', [b'a\xc3\xa9', b'\x80\xc3\xa9', b'1\xc3\xa9'])
sys.stdout.write(HDR + '\n' + '\n'.join(out))
