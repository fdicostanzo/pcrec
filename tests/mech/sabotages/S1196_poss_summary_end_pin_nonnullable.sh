#!/usr/bin/env bash
# S1196 ([DD-11.5] P2e, lane ctxp2e) -- A1'S CHAIN SUMMARY CALLS `\z`
# NON-NULLABLE: `ps_node`'s non-gate A_CTX branch drops `first_of`'s
# nullability. Before P2e every A_CTX was non-nullable there; `\z` became the
# one that is not, and `ps_node` is the site the §4.6 census filed as a LABEL
# (it is a GENERIC read of `first_of`, not a class switch). Under the plant the
# summary disagrees with the plain fold it replaces.
SAB_ID="S1196-poss-summary-end-pin-nonnullable"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_DESC='the possessify chain summary drops first_of'\''s nullability for a non-gate A_CTX (\z)'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, harness over tests/assertions + tests/possessify 5 failed / 25985 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            r.nullable = f.nullable;
        }
        return r;'
SAB_AFTER='        }   /* SABOTAGE S1196 */
        return r;'
