import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
i0 = s.index('    unsigned reseed_steps = ')
i1 = s.index('    if (capture_spans) rx_report_captures', i0)
body = s[i0:i1]
st0, bl0 = map(int, re.search(r'unsigned reseed_steps = (\d+), reseed_block = (\d+);', body).groups())
gap, blk, cap = map(int, re.search(r'>= (\d+)\) reseed_block = 0;\n.*?reseed_block = (\d+);\n.*?reseed_block < (\d+)\)', body, re.S).groups())
res = re.search(r'(        if \(result == RX_R_STEPS\).*?        if \(result >= 0\) break;\n)', body, re.S).group(1)
adv = re.search(r'        if \(attempt_position >= subject_length\) return 0;\n(.*?)        if \(reseed_steps\)', body, re.S).group(1)
ind = lambda t: ''.join('    ' + l + '\n' if l else '\n' for l in t.rstrip('\n').split('\n'))
new = f'''    unsigned reseed_block = {bl0};
    size_t step_end = subject_length - attempt_position > {st0} ? attempt_position + {st0} : subject_length;
    for (;;) {{
        ctx.pos = attempt_position;
        result = rx_match_anchored(&ctx, run);
{res}        rx_reset_for_next_attempt(run);
        if (__builtin_expect(attempt_position >= step_end, 0)) {{
            if (attempt_position >= subject_length) return 0;
{ind(adv)}            ptrdiff_t window[1][2];
            unsigned reseed_steps = 0;
            if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0;
            if ((size_t)window[0][0] - attempt_position >= {gap}) reseed_block = 0;
            else if (!reseed_block) reseed_block = {blk};
            else {{ reseed_steps = reseed_block; if (reseed_block < {cap}) reseed_block *= 2; }}
            attempt_position = (size_t)window[0][0];
            step_end = subject_length - attempt_position > reseed_steps ? attempt_position + reseed_steps : subject_length;
            continue;
        }}
{adv}    }}
'''
s = s[:i0] + new + s[i1:]
open(dst, 'w').write(s)
