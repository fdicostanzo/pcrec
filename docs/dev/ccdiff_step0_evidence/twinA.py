#!/usr/bin/env python3
"""TWIN A -- UNIFORM-TABLE FOLDING.

The general emitter fact: pcrec BUILDS these tables, so it knows at emission
time whether every cell holds the same value.  When one does, the load is a
constant and the emitter can spell it as one.  Clang already performs this
fold on its own (LLVM's ConstantFoldLoadFromUniformValue); gcc 15 does not
fold a variable-index load even from an all-equal `static const` array.

The rewrite is confined to the emitted `_step` / `_accepts` helper BODIES, so
every call site keeps its arguments and therefore every side effect
(`subject[scan_position++]`).
"""
import re, sys

src = open(sys.argv[1]).read()
notes = []

def uniform(name):
    m = re.search(r'static const \w+(?: \w+)* ' + name + r'\[\d+\] = \{(.*?)\};',
                  src, re.S)
    if not m:
        return None
    vals = [v.strip() for v in m.group(1).replace('\n', ' ').split(',') if v.strip()]
    if not vals:
        return None
    return vals[0] if len(set(vals)) == 1 else None

for d in ('forward', 'reverse', 'anchored'):
    v = uniform('rx_%s_next_state' % d)
    if v is not None:
        src = src.replace(
            'static inline rx_%s_state rx_%s_step(const unsigned short *transitions, rx_%s_state s, unsigned cl)\n{ return transitions[s + cl]; }' % (d, d, d),
            'static inline rx_%s_state rx_%s_step(const unsigned short *transitions, rx_%s_state s, unsigned cl)\n{ (void)transitions; (void)s; (void)cl; return %s; }  /* [twinA] uniform table */' % (d, d, d, v))
        notes.append('%s_next_state uniform = %s' % (d, v))
    a = uniform('rx_%s_is_accepting' % d)
    if a is not None:
        src = src.replace(
            'static inline int rx_%s_accepts(const unsigned char *accepting, rx_%s_state s)\n{ return accepting[s]; }' % (d, d),
            'static inline int rx_%s_accepts(const unsigned char *accepting, rx_%s_state s)\n{ (void)accepting; (void)s; return %s; }  /* [twinA] uniform table */' % (d, d, a))
        notes.append('%s_is_accepting uniform = %s' % (d, a))

open(sys.argv[2], 'w').write(src)
print('; '.join(notes) if notes else 'NO UNIFORM TABLE')
