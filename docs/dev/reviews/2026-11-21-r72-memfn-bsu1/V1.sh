SAB_FILE="memfn/src/window.c"
SAB_COUNT=1
SAB_BEFORE='    return ih >= 0 && w->grp[ih] < 0 ? ih : -1;'
SAB_AFTER='    (void)ih; return -1;   /* SABOTAGE V1 */'
