"""Extract the reverse-pass machine of a pcrec DFA artifact compiled from P.L and wrap it
as rw_walk(subject, seed, search_from): the reverse DFA seeded at `seed` (the landmark's
end), floored at search_from, returning the smallest accepting start or (size_t)-1.
The machine text is pcrec's own emitted text, renamed rx_reverse_ -> rw_reverse_."""
import re, sys
src = open(sys.argv[1]).read().split('\n')
out = []
# helper typedef / inline functions (top level, before rx_search)
i = 0
while i < len(src):
    l = src[i]
    if l.startswith('typedef unsigned rx_reverse_state') or re.match(r'static inline .*rx_reverse_', l):
        out.append(l)
        if not l.rstrip().endswith('}') and not l.startswith('typedef'):
            out.append(src[i+1]); i += 1
    i += 1
body = []
start = next(k for k, l in enumerate(src) if l.startswith('int rx_search('))
k = start
tables = []
while not src[k].startswith('}'):
    l = src[k]
    if re.match(r'\s+static const .* rx_reverse_\w+\[', l):
        t = [l]; k += 1
        while not src[k].strip().startswith('};'):
            t.append(src[k]); k += 1
        t.append(src[k]); tables += t
    if 'size_t rewind_position = match_end_position;' in l:
        b = []
        while 'if (match_start_position == (size_t)-1) return 0;' not in src[k]:
            b.append(src[k]); k += 1
        body = b
    k += 1
fn = ['static size_t rw_walk(const unsigned char *subject, size_t seed, size_t search_from)', '{']
fn += tables
fn += ['    size_t match_end_position = seed;', '    size_t match_start_position = (size_t)-1;', '    {']
fn += body
fn += ['    }', '    return match_start_position;', '}']
text = '\n'.join(out + [''] + fn) + '\n'
print(text.replace('rx_reverse_', 'rw_reverse_'))
