#!/usr/bin/env python3
"""lane lrvm: per-cell event counts from gcovrun.sh's line counts.
    python3 gcov_counts.py LR/gcov > gcov_counts.tsv
Each column sums the execution counts of the emitted lines whose TEXT
matches its regex (the emitter's own spellings at main f2fcffb4, abi 74)."""
import os, re, sys
EV = [
    ('rx_search_calls', r'^int rx_search\('),
    ('vm_attempts', r'if \(result >= 0\) break;'),
    ('vm_hat_seek_iter', r'!rx_start_set\[subject\['),
    ('dfa_hat_skip_iter', r'!rx_start_bytes\[subject\['),
    ('dfa_stay_iter', r'rx_forward_stay\d+\[subject'),
    ('dfa_fwd_steps', r'rx_forward_byte_class\[subject\[scan_position(\+\+)?\]\][;)]'),
    ('dfa_attempt_steps', r'goto \*rx_targets_\d+\[rx_byte_class'),
    ('memchr_calls', r'memchr\('),
    ('span_iter', r'while \(\(rx_span_cursor'),
    ('frames_popped', r'const size_t frame_index = --run->resume_depth;'),
    ('trail_reset_iter', r'while \(run->trail_depth\) \{'),
    ('trail_pop_iter', r'while \(run->trail_depth > run->resume_stack'),
    ('span_match_calls', r'^ptrdiff_t rx_span_match\('),
]
root = sys.argv[1]
print('\t'.join(['cell'] + [e for e, _ in EV]))
for d in sorted(os.listdir(root)):
    f = os.path.join(root, d, 'rx.c.gcov')
    if not os.path.exists(f):
        continue
    tot = {e: 0 for e, _ in EV}
    for l in open(f, errors='replace'):
        m = re.match(r'\s*([0-9]+)\*?:\s*[0-9]+:(.*)', l)
        if not m:
            continue
        c, t = int(m.group(1)), m.group(2)
        for e, rx in EV:
            if re.search(rx, t):
                tot[e] += c
    print('\t'.join([d] + [str(tot[e]) for e, _ in EV]))
