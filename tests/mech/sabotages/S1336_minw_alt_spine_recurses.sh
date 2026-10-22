# S1336 ([DD-10], lane dd10; re-aimed by dd10fix onto PCREC_SPINE_EACH) -- pcrec_minw recurses down the A_ALT
# spine again: one C frame per alternative. K114's crash shape: answers are unchanged, so only the
# compile-stack arm (the 10,000-capture and 20,000-literal alternations on limits.md §3.10's thread) can see
# it. Detector: tests/thread/run_compile_stack.sh (test-stackdepth).
SAB_ID="S1336-minw-alt-spine-recurses"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="compilestack"
SAB_DESC='pcrec_minw walks the A_ALT spine recursively (both children), costing one C frame per alternative'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1336.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            long long m = LLONG_MAX;
            PCREC_SPINE_EACH(b, a, A_ALT) {
                long long r = pcrec_minw(b);
                if (r < m) m = r;
            }
            return pcrec_sat_add(acc, m, MRL_MINW_MAX);'
SAB_AFTER='            long long l = pcrec_minw(a->l), m = pcrec_minw(a->r);   /* SABOTAGE S1336 */
            return pcrec_sat_add(acc, l < m ? l : m, MRL_MINW_MAX);'
