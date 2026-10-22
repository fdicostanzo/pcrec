# S1337 ([DD-10], lane dd10; re-aimed by dd10fix onto PCREC_SPINE_EACH) -- ew_walk_marked hands a zero-width
# trailing factor's question to its left sibling by RECURSION again (the arm as it was before dd10): one C
# frame per zero-width factor. Same answers; only the compile-stack arm (20,000 trailing \b on limits.md
# §3.10's thread) sees it. Detector: tests/thread/run_compile_stack.sh.
SAB_ID="S1337-endwin-zero-width-run-recurses"
SAB_FILE="src/facts/endwin.c"
SAB_SUITES="compilestack"
SAB_DESC='ew_walk_marked recurses down the A_CAT spine past each zero-width trailing factor instead of iterating'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1337.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            int m = EW_NONE;
            PCREC_SPINE_EACH(f, a, A_CAT) {
                int r = ew_walk_marked(f, em);
                if (r > m) m = r;
                if (m == EW_Z || pcrec_cwmax(f) != 0) return m;
            }
            return m;'
SAB_AFTER='            int r = ew_walk_marked(a->r, em);   /* SABOTAGE S1337 */
            if (pcrec_cwmax(a->r) != 0) return r;
            if (r == EW_Z) return EW_Z;
            { int l = ew_walk_marked(a->l, em); return l > r ? l : r; }'
