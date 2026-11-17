import os, sys, io, re, contextlib
LANES = '/var/tmp/pcrec-pcrec/scratch/crit-predspec24/R/tree/docs/dev/lanes'
LPF = os.path.join(LANES, 'lastpass_evidence', 'lastpass_model.py')
src = open(LPF).read()
LP = {'__file__': LPF, '__name__': 'lastpass_defs'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:re.search(r'^# =+ PART A: libpcre2$', src, re.M).start()], LPF, 'exec'), LP)
LP['MODE']['v'] = 'R'; LP['OCCM']['v'] = 'H2'
Pat, AndP, Diff, Keep, Where = LP['Pat'], LP['AndP'], LP['Diff'], LP['Keep'], LP['Where']
search, whole, findall = LP['search'], LP['whole'], LP['findall']
def ZERO(A, B): return Keep(A, lambda row, s, i, e: whole(B, s[i:e]))
def show(nm, Pn, s):
    r = search(Pn, s); print(nm, repr(s), 'SEARCHED', None if r is None else (s[r[0]:r[1]], r[0]), 'FIND-ALL', [(s[a:b], a) for a, b, _ in findall(Pn, s)])
A = Pat(r'\d')
for B in (r'\d$', r'\d(?=\d)', r'\d\b'):
    show('engine A & /%s/      ' % B, AndP(A, Pat(B)), '12')
    show('engine A & (0: /%s/) ' % B, ZERO(A, Pat(B)), '12')
    show('engine A & !/%s/     ' % B, Diff(A, Pat(B)), '12')
sys.path.insert(0, '.')
from ev import *
def B1(t, p, st):  # \d$ on its own text
    if p < len(t) and t[p].isdigit() and p + 1 == len(t): yield p + 1, st
print('text A & /\\d$/ (stretch matched whole, alone):', searched(AND(DIG, B1), '12'), findall(AND(DIG, B1), '12'))
