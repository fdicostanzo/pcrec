# S1337 ([DD-10], lane dd10) -- ew_walk_marked hands a zero-width trailing factor's question to its left
# sibling by RECURSION again: one C frame per zero-width factor. Same answers; only the compile-stack arm
# (20,000 trailing \b on limits.md §3.10's thread) sees it. Detector: tests/thread/run_compile_stack.sh.
SAB_ID="S1337-endwin-zero-width-run-recurses"
SAB_FILE="src/facts/endwin.c"
SAB_SUITES="compilestack"
SAB_DESC='ew_walk_marked recurses down the A_CAT spine past each zero-width trailing factor instead of iterating'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1337.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='                if (r > m) m = r;
            }
            { int l = ew_walk_marked(a, em); return l > m ? l : m; }'
SAB_AFTER='                if (r > m) m = r;
                { int l = ew_walk_marked(a->l, em); return l > m ? l : m; }   /* SABOTAGE S1337 */
            }
            { int l = ew_walk_marked(a, em); return l > m ? l : m; }'
