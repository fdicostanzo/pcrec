# verify: memfn-sp1a (SUBJECT c0c73bc20, BASE 564db08c5)
Harness: $V/fake.sh (fake binaries printing `MFTRACE REACH table=fd row=X chosen=N asked=M` + REACH_DROPPED, format confirmed against gate.c reach_print :883-912, which prints one line per registered row, zeros included) with a stub tree/scripts/emit_sweep.py (1200 patterns), arm "". Census plants under $V/c0 (copy of memfn + the two census files).

## CHECK-1
HOLDS. reach_equal.py:128 `if b.get(k, 0) != h.get(k, 0)` treats absent as 0. Repro: base prints fd/Z chosen=0 asked=0, head omits it, Z not in --gone, `--gone fd:G`: observed `differ=0 ... DONE rc=0`. (gate.c prints zero rows, so a real surviving zero-reach row dropped at HEAD would pass.)

## CHECK-2
HOLDS. reach_equal.py:98 `gone` is whatever --gone says; nothing derives or requires it. Repro: identical sides, no --gone: `DONE rc=0 keys=6 differ=0`.

## CHECK-3
HOLDS (by reading). reach_equal.py:117 `sums[s][arm].update(c)` accumulates all patterns into one Counter per arm; :128 compares those sums. Compensating per-pattern moves (A:X->Y, B:Y->X) leave sums equal. Not run.

## CHECK-4
HOLDS. :100 `if len(pats) < POP_FLOOR and not a.limit`. Repro: `--limit 3 --gone fd:G`: population 3, `DONE rc=0`, same trailer as full run.

## CHECK-5
HOLDS (by reading). reach_of :55-74 never reads r.returncode; a crash yields an empty Counter, only timeouts (:57) are counted, and those compared as counts (:137). Not run.

## CHECK-6
HOLDS on all four sub-claims (plants in $V/c0, rc via decider_census.py --root):
- unlisted `static int zz_unlisted(...) { for ... if (best > a[i]) best = a[i]; }` appended to window.c: `checks failed: 0`, rc=0.
- prototype-only: added row `window.c ghost_fn fn - T-VERIFY -` and only `static int ghost_fn(int);` in window.c: `checks passed: 56, failed: 0`, rc=0.
- dropped the single `run_group_ok` row from the map: `passed 54, failed 0`, rc=0 (MEMBER_FLOOR 45).
- respelled anchor `ms < bm ||` -> `ms<bm ||` in window.c: Python traceback at decider_census.py:200 `at = next(...)` StopIteration, rc=1, no FAIL/verdict line.

## SLOT-1
HOLDS. finder_check.py:20 `the 16 rows`; SUBJECT FIND_ROWS (:112) has 8 ids, PRES_ROWS (:118) 5: 13.

## SLOT-3
HOLDS. memfn/CLAUDE.md:25 reads "The deepest measured kit chain (`mf_form_hash` ... and the since-deleted `mf_set_terms` at K=4 on a painted stack) reached 13.7 KB; before R-28, 47.1 KB." The chain no longer exists; history in an orientation file.

## SLOT-4
HOLDS. BASE finder.c:539 `if (r->needs & KN_H) return 0;  /* no iterator before B9 */` and :537 `(KN_N | KN_H)`. SUBJECT: KN_H still declared (:71) and 'H' in needs_names (:1095); the diff removes both guard lines (:520 now only KN_N). Answer-neutral at SUBJECT: grep of finder.c finds KN_H only at :71 (and :1095's 'H' string), so no row carries KN_H (only R3a/R3b/R4 did at BASE, now deleted). Latent only.

## SLOT-6
HOLDS. reach_equal.py:140 `at_base = any(... sums["base"][arm])` is true for any registered row because gate.c prints every row, zeros included; :126 `continue` skips gone rows, so their BASE chosen/asked are never printed or checked as zero. Only a mistyped id fails. Also :135 `chosen == 0` is checked at HEAD only.

## SLOT-7
HOLDS, count refined. strip_c: site_census.py:84 and arch_blind_check.py:198 are byte-identical regex versions (viewed); decider_census.py:61 is a third (hand-rolled loop); form_checks.py:129 strip_comments is a fourth in tests/memfn. Definition finders in tests/memfn: c17_lex.py (:30,:47,:53), site_census.callers_in_text :91, decider_census.definitions :90 / item_name :118 = three. REACH parsers: rows_check.py:153 reach_rows, memfn/tests/run_g2.sh:998 reach_lines (+sed), reach_equal.py:43-74 = three. Did not verify the non-memfn comment strippers (wclass_census etc.).

VERIFY COMPLETE
