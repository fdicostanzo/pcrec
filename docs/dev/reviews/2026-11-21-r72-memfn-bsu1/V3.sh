SAB_FILE="memfn/src/window.c"
SAB_COUNT=1
SAB_BEFORE='static int s_deny_holds(const wf_sx *x)  { return kit_opt_state(x->d->s->opts, WF_LOOP_ID) < 0; }'
SAB_AFTER='static int s_deny_holds(const wf_sx *x)  { return kit_opt_state(x->d->s->opts, WF_LOOP_ID) < 0 && !(x->d->art && (x->d->art->levers & KIT_LEVER_SPAN_HEAD)); }   /* SABOTAGE V3 */'
