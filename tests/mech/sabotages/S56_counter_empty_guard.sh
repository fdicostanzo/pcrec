# S56 — [ENG-BREP counter-K] THE EMPTY-ITERATION GUARD *ADDED* TO THE BOUNDED
# PATH. Deliberately the sabotage that ADDS something.
#
# D44/R21 E-2 RULED the empty-iteration guard exists for `rmax == -1` ONLY, and
# measured the alternative: with the guard applied to bounded repeats too, 60 of
# 225,240 generated pairs diverge from libpcre2; restricted to unbounded, 0 of
# 225,240. PCRE2's actual behaviour is that a bounded repeat REPLICATES — a
# `{1,2}` body is `body body?`, each copy an independent opportunity to match
# empty, because there IS no "continuation" test at a bounded count.
#
# §5 of the design note says the one thing an implementation lane must not do is
# add the guard for safety, on the reasoning that it looks like a termination
# fix and is a semantics change. A sabotage row is how that instruction acquires
# a check instead of remaining a sentence — and it is the row most likely to be
# "fixed" back in by a future reader who sees a nullable body in a loop and
# reaches for the guard reflexively.
#
# The emitted consequence: a nullable body's loop stops after its first trip, so
# the quantifier matches fewer iterations than it promises. The witness must be
# NULLABLE and above K — `(a?){0,12}b` and `(a?){0,17}b` in patterns.txt — which
# is also why §8.1 spells the nullable cells at {0,12} rather than §5's {0,4}:
# below K no counter is emitted and the cell would be checking replication's
# termination, which E-2 already settled.
SAB_ID="S56-counter-empty-guard"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="an empty-iteration guard is ADDED to the bounded counter path, which D44/R21 E-2 measured wrong on 60 of 225,240 pairs"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §5 (the guard that must NOT be added)"
SAB_COUNT=1
SAB_BEFORE='        vm_ev(v, VE_NOTE, 0, 0,
              "trip guard: the residue is a compile-time constant");'
SAB_AFTER='        vm_ev(v, VE_NOTE, 0, 0,
              "trip guard: the residue is a compile-time constant");
        if (optional && vm_nullable(a->l))   /* SABOTAGE S56 */
            sb_printf(b, "    if (stv[%d] > 0) goto %s_L%d;\n", ctr, v->p, next);'
