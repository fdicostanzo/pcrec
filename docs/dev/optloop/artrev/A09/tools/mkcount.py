import sys
s=open(sys.argv[1]).read()
def rep(a,b,need=True):
    global s
    if s.count(a)!=1:
        assert not need,(a,s.count(a)); return
    s=s.replace(a,b)
pre='static unsigned long C_calls,C_skip0,C_skip406,C_fstep,C_rskip,C_rstep,C_pf,C_vm,C_vmfail,C_vmpos,C_memchr,C_cand;\n'
rep('#include <string.h>\n','#include <string.h>\n'+pre)
rep('!rx_can_begin_match[subject[scan_position]]) scan_position++;','!rx_can_begin_match[subject[scan_position]]) {scan_position++;C_skip0++;}',False)
rep('rx_forward_stay14[subject[scan_position]]) scan_position++;','rx_forward_stay14[subject[scan_position]]) {scan_position++;C_skip406++;}',False)
rep('            forward_state = rx_forward_step(rx_forward_next_state, forward_state, forward_class);','            forward_state = rx_forward_step(rx_forward_next_state, forward_state, forward_class);C_fstep++;',False)
rep('rx_reverse_stay26[subject[rewind_position - 1]]) rewind_position--;','rx_reverse_stay26[subject[rewind_position - 1]]) {rewind_position--;C_rskip++;}',False)
rep('                reverse_state = rx_reverse_step(rx_reverse_next_state, reverse_state, reverse_class);','                reverse_state = rx_reverse_step(rx_reverse_next_state, reverse_state, reverse_class);C_rstep++;',False)
rep('        result = rx_match_anchored(&ctx, run, window_end);','        result = rx_match_anchored(&ctx, run, window_end);C_vm++; if(result<0)C_vmfail++;',False)
rep('    RX_PUSH(&&rx_L16, rx_span_cursor);','    RX_PUSH(&&rx_L16, rx_span_cursor);C_vmpos++;',False)
rep('    const unsigned char *hit = (const unsigned char *)memchr(','    C_memchr++;const unsigned char *hit = (const unsigned char *)memchr(',False)
rep('{ scan_position = p; forward_state = 0; break; }','{ scan_position = p; forward_state = 0; C_cand++; break; }',False)
open(sys.argv[2],'w').write(s)
