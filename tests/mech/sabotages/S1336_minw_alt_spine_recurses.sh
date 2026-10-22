# S1336 ([DD-10], lane dd10) -- pcrec_minw recurses down the A_ALT spine again: one C frame per alternative.
# K114's crash shape: answers are unchanged, so only the compile-stack arm (a 20,000-capture alternation on
# limits.md §3.10's 432 KB thread) can see it. Detector: tests/thread/run_compile_stack.sh (test-stackdepth).
SAB_ID="S1336-minw-alt-spine-recurses"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="compilestack"
SAB_DESC='pcrec_minw walks the A_ALT spine recursively (both children), costing one C frame per alternative'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1336.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            long long m = pcrec_minw(a->r);
            for (a = a->l; a->k == A_ALT; a = a->l) {
                long long r = pcrec_minw(a->r);
                if (r < m) m = r;
            }
            long long l = pcrec_minw(a);
            return pcrec_sat_add(acc, l < m ? l : m, MRL_MINW_MAX);'
SAB_AFTER='            long long l = pcrec_minw(a->l), m = pcrec_minw(a->r);   /* SABOTAGE S1336 */
            return pcrec_sat_add(acc, l < m ? l : m, MRL_MINW_MAX);'
