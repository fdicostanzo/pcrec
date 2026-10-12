#!/usr/bin/env python3
"""lane lrvm hand twins: mechanical transforms of an emitted artifact (prefix
rx, main f2fcffb4, abi 74). Each transform is the general change a phase-2
candidate would make, applied by hand to one artifact.
    python3 twin.py IN.c OUT.c TRANSFORM[,TRANSFORM...]
TRANSFORMS
  static_seam    the VM's backreference compare calls a STATIC inline copy of
                 rx_span_match (the exported symbol stays, unchanged); under
                 the bench's -O2 -fPIC the exported one is a PLT call gcc may
                 not inline (semantic interposition).
  static_noinline  as static_seam but the private copy is `static
                 __attribute__((noinline))`: a direct (non-PLT) call that gcc
                 may not inline, so it buys the PLT removal and NOT the
                 specialization (twintime, 2026-10-11: splits the two on bak-2).
  static_noinline_noclone  as static_noinline plus `noclone`: gcc otherwise
                 emits `rx__span_match_in.constprop.0` (the constant reflen
                 folded into a private clone), which gives back part of the
                 specialization; this arm is the strict PLT-only one.
  trail_free     FRAMELESS artifacts only: RX_SET stores without trailing and
                 a failed attempt resets exactly the slots RX_SET can write to
                 PCREC_UNSET (what the trail undo restores them to, since every
                 attempt starts with all slots unset).
  seek_memchr    the VM hat's start-set table walk becomes memchr (|S| = 1) or
                 a two-stream memchr leapfrog with pending hits (|S| = 2).
  stay=STATE     add a self-loop stay loop for forward DFA state STATE (its
                 table derived from the artifact's own transition table); the
                 state must be non-accepting on every class.
  precheck=BYTE  the whole-call necessary-byte pre-check at rx_search_run's
                 entry (the shape the emitter writes when REQ_WHY is
                 `emitted`), for an artifact whose REQ_WHY is `one-attempt`.
  rewind         a cursor rung whose follow atom begins with a one-byte test
                 seeks DOWN to the next position passing that test before it
                 pushes its resume frame, instead of one frame push/pop per
                 position (the follow test text is copied from the artifact).
  stepset=BYTE   a hybrid's stepping retry skips to the next BYTE (the start
                 set of a one-member-start pattern) instead of the next byte.
"""
import re, sys

def die(m):
    sys.exit('twin.py: ' + m)

def static_seam(t, attr='static inline __attribute__((always_inline))'):
    m = re.search(r'\nptrdiff_t rx_span_match\((.*?)\n\}\n', t, re.S)
    if not m:
        die('no rx_span_match definition')
    body = m.group(0).strip('\n').replace('ptrdiff_t rx_span_match(', attr + ' ptrdiff_t rx__span_match_in(', 1)
    n0 = t.count('took = rx_span_match(')
    if n0 == 0:
        die('no VM call site of rx_span_match')
    t = t.replace('took = rx_span_match(', 'took = rx__span_match_in(')
    anchor = t.find('static inline __attribute__((always_inline)) ptrdiff_t rx_match_anchored(')
    if anchor < 0:
        anchor = t.find('static ptrdiff_t rx_match_anchored(')
    if anchor < 0:
        die('no rx_match_anchored')
    return t[:anchor] + body + '\n' + t[anchor:]

def trail_free(t):
    if '#define RX_RESUME_FRAMES 1\n' not in t and 'RX_VM_FRAMELESS 1' not in t:
        die('trail_free: not a frameless artifact')
    slots = sorted(set(re.findall(r'RX_SET\((RX_SLOT_\w+)', t)))
    if not slots:
        die('trail_free: no RX_SET')
    t = re.sub(r'#define RX_SET\(slot_, v_\) do \{\s*\\\n\s*RX_TRAIL\(slot_\); slot_values\[\(slot_\)\] = \(v_\);\s*\\\n\s*\} while \(0\)',
               '#define RX_SET(slot_, v_) do { slot_values[(slot_)] = (v_); } while (0)', t)
    if 'RX_TRAIL(slot_); slot_values' in t:
        die('trail_free: RX_SET not rewritten')
    old = re.search(r'(static inline __attribute__\(\(always_inline\)\) void rx_reset_for_next_attempt\(rx_run_state \*run\)\n\{\n)(.*?)(\n\})', t, re.S)
    if not old:
        die('trail_free: no rx_reset_for_next_attempt')
    new = ''.join('    run->slot_values[%s] = PCREC_UNSET;\n' % s for s in slots) + '    run->resume_depth = 0;'
    return t[:old.start(2)] + new + t[old.end(2):]

def start_set_bytes(t):
    m = re.search(r'static const unsigned char rx_start_set\[256\] = \{(.*?)\};', t, re.S)
    if not m:
        die('no rx_start_set table')
    v = [int(x) for x in re.findall(r'\d+', m.group(1))]
    return [b for b in range(256) if v[b]], m.end()

LOOP = 'while (attempt_position < subject_length && !rx_start_set[subject[attempt_position]]) attempt_position++;'

def seek_memchr(t):
    S, end = start_set_bytes(t)
    if len(S) == 1:
        rep = ('{ const void *q_ = attempt_position < subject_length ? memchr(subject + attempt_position, %d, subject_length - attempt_position) : NULL;'
               ' attempt_position = q_ ? (size_t)((const unsigned char *)q_ - subject) : subject_length; }' % S[0])
        decl = ''
    elif len(S) == 2:
        a, b = S
        decl = '\n    size_t rx_ha_ = 0, rx_hb_ = 0; int rx_fresh_ = 1;'
        rep = ('if (attempt_position < subject_length) {'
               ' if (rx_fresh_ || rx_ha_ < attempt_position) { const void *q_ = memchr(subject + attempt_position, %d, subject_length - attempt_position); rx_ha_ = q_ ? (size_t)((const unsigned char *)q_ - subject) : subject_length; }'
               ' if (rx_fresh_ || rx_hb_ < attempt_position) { const void *q_ = memchr(subject + attempt_position, %d, subject_length - attempt_position); rx_hb_ = q_ ? (size_t)((const unsigned char *)q_ - subject) : subject_length; }'
               ' rx_fresh_ = 0; attempt_position = rx_ha_ < rx_hb_ ? rx_ha_ : rx_hb_; }' % (a, b))
    else:
        die('seek_memchr: |S| = %d' % len(S))
    if t.count(LOOP) < 1:
        die('seek_memchr: no seek loop')
    t = t[:end] + decl + t[end:]
    return t.replace(LOOP, rep)

def arr(t, name):
    m = re.search(r'%s\[\d+\] = \{(.*?)\};' % re.escape(name), t, re.S)
    if not m:
        die('no table ' + name)
    return [int(x) for x in re.findall(r'-?\d+', m.group(1))]

def stay(t, st):
    bc = arr(t, 'rx_forward_byte_class'); ns = arr(t, 'rx_forward_next_state')
    acc = arr(t, 'rx_forward_is_accepting_by_class')
    ncls = max(bc) + 1
    if any(acc[st + c] for c in range(ncls)) or arr(t, 'rx_forward_is_accepting')[st]:
        die('stay: state %d accepts' % st)
    row = [ns[st + c] for c in range(ncls)]
    tab = [1 if row[bc[b]] == st else 0 for b in range(256)]
    name = 'rx_forward_stayT%d' % st
    decl = ('    static const unsigned char %s[256] = {' % name + ','.join(map(str, tab)) + '};\n')
    anchor = t.find('    size_t scan_position = search_from;\n    size_t last_accept_position = (size_t)-1;')
    if anchor < 0:
        die('stay: no forward loop anchor')
    t = t[:anchor] + decl + t[anchor:]
    m = re.search(r'(\n        else if \(forward_state == \d+\) \{\n.*?\n        \}\n)', t, re.S)
    br = ('\n        else if (forward_state == %d) {\n'
          '            while ((scan_position + 1 < subject_length) && (%s[subject[scan_position]])) {\n'
          '                scan_position++;\n            }\n        }\n' % (st, name))
    if m:
        return t[:m.end(1) - 1] + br + t[m.end(1):]
    m = re.search(r'\n        if \(forward_state == 0 && last_accept_position == \(size_t\)-1\) \{\n.*?\n        \}\n', t, re.S)
    if not m:
        die('stay: no skip block')
    return t[:m.end() - 1] + br + t[m.end():]

def precheck(t, byte):
    a = 'static int rx_search_run('
    i = t.find(a)
    j = t.find('    if (search_from > subject_length) return 0;\n', i)
    if i < 0 or j < 0:
        die('precheck: no rx_search_run entry')
    j += len('    if (search_from > subject_length) return 0;\n')
    ins = ('    if (subject_length <= search_from ||\n'
           '        !memchr(subject + search_from, %d, subject_length - search_from))\n'
           '        return 0;\n' % byte)
    return t[:j] + ins + t[j:]

def rewind(t):
    pat = re.compile(r'(\n(rx_L\d+): __attribute__\(\(unused\)\);\n)'
                     r'(    if \(\(ptrdiff_t\)rx_span_cursor < (slot_values\[\d+\] \+ 0)\) goto rx_fail;\n'
                     r'    RX_PUSH\(&&rx_L\d+, rx_span_cursor\);\n'
                     r'    scan_position = rx_span_cursor;\n'
                     r'    goto (rx_L\d+);\n)')
    n = 0
    out = t
    for m in list(pat.finditer(t)):
        low, follow = m.group(4), m.group(5)
        fm = re.search(r'\n' + follow + r': __attribute__\(\(unused\)\);\n    if \(scan_position < subject_length && (\(.*?\))\) \{ scan_position\+\+; goto rx_L\d+; \}\n    goto rx_fail;\n', t)
        if not fm:
            continue
        test = fm.group(1).replace('scan_position', 'rx_span_cursor')
        seek = ('    for (;;) {\n'
                '        if ((ptrdiff_t)rx_span_cursor < %s) goto rx_fail;\n'
                '        if (rx_span_cursor < subject_length && %s) break;\n'
                '        if ((ptrdiff_t)rx_span_cursor == %s) goto rx_fail;\n'
                '        rx_span_cursor -= 1;\n'
                '    }\n' % (low, test, low))
        out = out.replace(m.group(1) + m.group(3), m.group(1) + seek + m.group(3), 1)
        n += 1
    if not n:
        die('rewind: no cursor rung with a one-byte follow test')
    return out

def stepset(t, byte):
    old = '        if (attempt_position >= subject_length) return 0;\n        attempt_position++;\n'
    k = t.find(old + '        if (reseed_steps) reseed_steps--;\n')
    if k < 0:
        die('stepset: no stepping retry')
    k += len(old)
    ins = ('        { const void *q_ = attempt_position < subject_length ? memchr(subject + attempt_position, %d, subject_length - attempt_position) : NULL;'
           ' attempt_position = q_ ? (size_t)((const unsigned char *)q_ - subject) : subject_length; }\n' % byte)
    return t[:k] + ins + t[k:]

t = open(sys.argv[1]).read()
for tr in sys.argv[3].split(','):
    k, _, v = tr.partition('=')
    if k == 'static_seam': t = static_seam(t)
    elif k == 'static_noinline': t = static_seam(t, 'static __attribute__((noinline))')
    elif k == 'static_noinline_noclone': t = static_seam(t, 'static __attribute__((noinline, noclone))')
    elif k == 'trail_free': t = trail_free(t)
    elif k == 'seek_memchr': t = seek_memchr(t)
    elif k == 'stay': t = stay(t, int(v))
    elif k == 'precheck': t = precheck(t, int(v))
    elif k == 'stepset': t = stepset(t, int(v))
    elif k == 'rewind': t = rewind(t)
    elif k == 'none': pass
    else: die('unknown transform ' + k)
if '#include <string.h>' not in t:
    t = '#include <string.h>\n' + t
open(sys.argv[2], 'w').write(t)
