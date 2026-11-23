SAB_FILE="memfn/src/window.c"
SAB_COUNT=1
SAB_BEFORE='    return w->stop_alone ? w->stop_ix : -1;'
SAB_AFTER='    (void)w; return -1;   /* SABOTAGE V2 */'
