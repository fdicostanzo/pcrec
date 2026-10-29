#!/usr/bin/env python3
"""Rev 2's per-statement token signature, AS WRITTEN (vmcons2_report.md,
"The per-statement signature"): strstr counts of each token row on the
statement's printed text, compared with the counts a kind row declares.

usage: sig_rev2.py PREFIX KIND 'statement text'
Prints the counted vector, the declared vector for KIND and MATCH/MISMATCH.
Only the kinds the premise test needs are declared (FAIL, BRANCH_FAIL)."""
import sys

def count(t, p):
    P = p.upper()
    n = lambda s: t.count(s)
    return {
        'goto_L': n('goto %s_L' % p),
        'goto_fail': n('goto %s_fail' % p),
        'goto_star': n('goto *'),
        'return': n('return'),
        'slot_values[': n('slot_values['),
        'cursor_write': n('scan_position =') + n('scan_position +=') + n('scan_position++'),
        'run_write': n('--run->') + sum(t.count('run->%s =' % f) for f in
                     ('resume_depth', 'trail_depth', 'call_top', 'steps_left',
                      'work_left', 'callee_gave_up')),
        'macros': sum(n('%s_%s(' % (P, m)) for m in
                      ('SET', 'PUSH', 'CUT', 'CALL', 'TRAIL_CHECK', 'CHARGE_WORK')),
        'brace': n('{') - n('}'),
    }

ZERO = dict.fromkeys(['goto_L', 'goto_fail', 'goto_star', 'return', 'slot_values[',
                      'cursor_write', 'run_write', 'macros', 'brace'], 0)
# The kind table's rows, read as written: FAIL has the unwind edge only
# ("goto <p>_fail | 1 if the record has an unwind edge"); BRANCH_FAIL has
# next + unwind and its recorded reads R (none here: the operands are the
# span cursor local and scan_position).
DECL = {
    'FAIL': dict(ZERO, goto_fail=1),
    'BRANCH_FAIL': dict(ZERO, goto_fail=1),
}

p, kind, text = sys.argv[1], sys.argv[2], sys.argv[3]
c = count(text, p)
d = DECL[kind]
print('text    :', text.strip())
print('counted :', c)
print('declared:', kind, d)
print('result  :', 'MATCH (no mismatch, no V0)' if c == d else 'MISMATCH (V0)')
