# Emulation of rev 17 §8 tuple-compare family from the draft TEXT alone (python re).
import re, itertools, sys
UNSET = object()
def num(t):
    # padded(S) = /0*${S}/, S an integer comparison set of CANONICAL numerals
    if t is None or not re.fullmatch(r'\d+', t): return None
    c = t.lstrip('0') or '0'
    return int(c)
def padded(op, b):
    def f(t):
        n = num(t)
        if n is None: return False
        return {'>':n>b,'>=':n>=b,'<':n<b,'<=':n<=b,'==':n==b}[op]
    return f
# a projection entry: label name -> macro of one param S: condition (label: S)
def sec(lbl):
    return lambda S: (lambda gd: S(gd.get(lbl)))   # unset (None) -> comparison false
AND=lambda *ms: (lambda gd: all(m(gd) for m in ms))
ANY=lambda ms: (lambda gd: any(m(gd) for m in ms))   # array of macros = any one entry
NOT=lambda m: (lambda gd: not m(gd))
def lex_ge2(s,lo): return ANY([s[0](padded('>',lo[0])), AND(s[0](padded('==',lo[0])), s[1](padded('>=',lo[1])))])
def lex_le2(s,hi): return ANY([s[0](padded('<',hi[0])), AND(s[0](padded('==',hi[0])), s[1](padded('<=',hi[1])))])
def lex_between2(s,lo,hi): return AND(lex_ge2(s,lo), lex_le2(s,hi))
def lex_ge3(s,lo): return ANY([s[0](padded('>',lo[0])),
    AND(s[0](padded('==',lo[0])), s[1](padded('>',lo[1]))),
    AND(s[0](padded('==',lo[0])), s[1](padded('==',lo[1])), s[2](padded('>=',lo[2])))])
def lex_le3(s,hi): return ANY([s[0](padded('<',hi[0])),
    AND(s[0](padded('==',hi[0])), s[1](padded('<',hi[1]))),
    AND(s[0](padded('==',hi[0])), s[1](padded('==',hi[1])), s[2](padded('<=',hi[2])))])
def lex_between3(s,lo,hi): return AND(lex_ge3(s,lo), lex_le3(s,hi))
def whole(P, C, subj):
    m = re.fullmatch(P, subj)
    if not m: return False
    return C(m.groupdict())
