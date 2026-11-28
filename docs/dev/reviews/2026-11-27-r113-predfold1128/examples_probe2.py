import os
M = os.path.abspath('docs/dev/lanes/predfold1128_evidence/predfold1128_model.py')
src = open(M, encoding='utf-8').read(); g = {'__file__': M, '__name__': 'probe128'}
exec(compile(src[:src.index('# ==== CHECKS128')], M, 'exec'), g)
AH = "A := /(?<h>\\d)/"; BP = "B(rx) := /${[p = rx]}xx/"
for nm, e, b, t in [
 ('own text, group w/ labelled call', '[k = ([c = B([a = A])] SEQ "!")] & (k.a.h: <5)', [AH, BP], ['3xx!', '7xx!']),
 ('own text, group w/o call label', '[k = (B([a = A]) SEQ "!")] & (k.a.h: <5)', [AH, BP], ['3xx!', '7xx!']),
 ('outside, Y5 group w/o call label', 'Y5 & (Y5.a.h: <5)', [AH, BP, 'Y5 := B([a = A]) SEQ "!"'], ['3xx!', '7xx!']),
 ('outside, Y6 stacked: Y6.k.c.a.h', 'Y6 & (Y6.k.c.a.h: <5)', [AH, BP, 'Y6 := [k = [c = B([a = A])]] SEQ "!"'], ['3xx!', '7xx!']),
 ('own text bare a.h', '[k = [c = B([a = A])]] & (a.h: <5)', [AH, BP], ['3xx', '7xx']),
]:
    Pg, err = g['run11'](e, b)
    print('%-40s %s' % (nm, ('REFUSED ' + (err or '')[:160]) if Pg is None else ('LEGAL %s' % g['ans11'](Pg, t))))
