# S1475 (K129, lane corefix) -- `_match` RESOLVES ITS VARIABLES AFTER THE
# K73 OFFSET-0 RULE AGAIN.
#
# The anchored entry's own instance of iterd27 F3: under utf8 a nullable
# pattern carries the offset-0 rule's NOMATCH form (`pos == 0` on a
# continuation byte answers -1), and it ran before the variables, so `${v}`
# with v unset answered -1 on a subject beginning 0x80 instead of refusing.
# Planted on `_match` alone; `_match_caps` keeps the fixed order, so the
# entries arm reds on _match/_match_in and stays right on the caps pair.
SAB_ID="S1475-match-vars-after-offset0"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vars"
SAB_DESC="the VM _match body resolves the caller's variables after the K73 offset-0 NOMATCH rule, so under utf8 \${v} with v unset answers -1 on a subject that begins with a continuation byte instead of PCREC_ERR_UNSET_VAR"
SAB_DOC_FIGURE="PREDICTED: the 'vars' arm RED on its K129 offset-0 row (\${v} -e utf8 over 80: _match and _match_in return -1; _match_caps and _match_caps_in still refuse), every other K129 row and the corpus/oracle arms GREEN. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1475."
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, vm_vars_resolve_insert(v, "ctx"));
    /* [K73] The offset-0 start rule, NOMATCH form'
SAB_AFTER='    /* SABOTAGE S1475: resolved after the offset-0 rule, below */
    /* [K73] The offset-0 start rule, NOMATCH form'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='        "    %s_run_state_init(run);\n"
        "    result = %s_match_anchored(ctx, run%s%s);\n",
        v->p, v->p,'
SAB_AFTER2='        "    %s_run_state_init(run);\n"
        "%s"   /* SABOTAGE S1475 */
        "    result = %s_match_anchored(ctx, run%s%s);\n",
        v->p, vm_vars_resolve_insert(v, "ctx"), v->p,'
