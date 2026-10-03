import re, sys
src, dst = sys.argv[1], sys.argv[2]
form = sys.argv[3] if len(sys.argv) > 3 else 'f1'   # f1: init before the seed loop; f2: init on the entry pass only
s = open(src).read()
i0 = s.index('    {\n        ptrdiff_t window[1][2];\n        if (rx_prefilter(subject, subject_length, search_from, window) != 1) return 0;')
i1 = s.index('    if (capture_spans) rx_report_captures', i0)
body = s[i0:i1]
st0, bl0 = map(int, re.search(r'unsigned reseed_steps = (\d+), reseed_block = (\d+);', body).groups())
gap, blk, cap = map(int, re.search(r'>= (\d+)\) reseed_block = 0;\n.*?reseed_block = (\d+);\n.*?reseed_block < (\d+)\)', body, re.S).groups())
init = re.search(r'(    rx_run_state_init\(run\);\n.*?)    unsigned reseed_steps', body, re.S).group(1)
res = re.search(r'(        if \(result == RX_R_STEPS\).*?        if \(result == RX_R_INTERNAL\) return PCREC_ERR_INTERNAL;\n)', body, re.S).group(1)
adv = re.search(r'        if \(attempt_position >= subject_length\) return 0;\n(.*?)        if \(reseed_steps\)', body, re.S).group(1)
ind = lambda t: ''.join('    ' + l + '\n' if l else '\n' for l in t.rstrip('\n').split('\n'))
pre = init if form == 'f1' else ''
new = f'''{pre}    size_t seed_from = search_from, step_end;
    unsigned reseed_steps = {st0}, reseed_block = {bl0};
    for (;;) {{
        ptrdiff_t window[1][2];
        if (rx_prefilter(subject, subject_length, seed_from, window) != 1) return 0;
        attempt_position = (size_t)window[0][0];
        if (reseed_steps == ~0u) {{
            reseed_steps = 0;
            if (attempt_position - seed_from >= {gap}) reseed_block = 0;
            else if (!reseed_block) reseed_block = {blk};
            else {{ reseed_steps = reseed_block; if (reseed_block < {cap}) reseed_block *= 2; }}
        }}{' else {' + chr(10) + ind(init) + '        }' if form == 'f2' else ''}
        step_end = subject_length - attempt_position > reseed_steps ? attempt_position + reseed_steps : subject_length;
        for (;;) {{
            ctx.pos = attempt_position;
            result = rx_match_anchored(&ctx, run);
{ind(res)}            if (result >= 0) goto found;
            rx_reset_for_next_attempt(run);
            if (attempt_position >= step_end) break;
{ind(adv)}        }}
        if (attempt_position >= subject_length) return 0;
{adv}        seed_from = attempt_position;
        reseed_steps = ~0u;
    }}
found:
'''
s = s[:i0] + new + s[i1:]
open(dst, 'w').write(s)
