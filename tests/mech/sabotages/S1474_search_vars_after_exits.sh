# S1474 (K129, lane corefix) -- THE SEARCH ENTRY RESOLVES ITS VARIABLES
# AFTER THE PROOF-BASED EXITS AGAIN.
#
# The pre-fix shape, restored: `_search_run` resolved `${name}` after the
# end window, the necessary-byte memchr, the root width, the prefilter and
# the start-set seek, each of which can `return 0`. So `a${v}` with v unset
# answered "no match" on "bbb" while `_match` refused with
# PCREC_ERR_UNSET_VAR (iterd27 F3). Two sites: the hoisted resolve goes, and
# the old one (after run_state_init, through the printf's reseed slot) comes
# back. The corpus's `gu` rows stay GREEN -- their subjects reach no early
# exit -- which is why the entries arm exists.
SAB_ID="S1474-search-vars-after-exits"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vars"
SAB_DESC="the VM search body resolves the caller's variables after its proof-based no-match exits (necessary byte, start set, root width, end window) instead of right after the caller-position guard, so an UNSET bare \${v} answers 0 instead of PCREC_ERR_UNSET_VAR on any subject one of those exits rules out"
SAB_DOC_FIGURE="PREDICTED: the 'vars' arm RED on its K129 entries rows for a\${v}, [ab]\${v}, \${v}abc, \${v}x\$, \${v}x and é\${v} (_search and _search_in return 0), the ^\${v} control and the offset-0 row GREEN, the corpus and splice-oracle arms GREEN -- the pre-fix tree measured exactly this by hand (lane corefix). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1474."
SAB_COUNT=1
SAB_BEFORE='    if (v->cx->n_var_exps)
        pcrec_sb_puts(c, "    ctx.vars = vars; ctx.nvars = nvars;\n");
    pcrec_sb_puts(c, vm_vars_resolve_insert(v, "&ctx"));'
SAB_AFTER='    /* SABOTAGE S1474: resolved after the exits, below */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='        v->p,
        reseed_decl,'
SAB_AFTER2='        v->p,
        pcrec_sb_fragf(&v->cx->arena, "%s%s%s",
                       v->cx->n_var_exps ? "    ctx.vars = vars; ctx.nvars = nvars;\n" : "",
                       vm_vars_resolve_insert(v, "&ctx"), reseed_decl),   /* SABOTAGE S1474 */'
