# u2house report: r5 xarch HOUSE-6 / HOUSE-7 / HOUSE-8 (2026-11-08, lane u2house, sonnet)

## Summary
Three XS house-rule items from review 2026-11-08 r5 xarch, kit only, no behaviour change. Branch lane/memfn-u2.

## The three edits
- HOUSE-6: every `gate_in` initializer in memfn/src is now designated, field by field, same values (the unnamed members stay zero as before): compose.c x4 (298, 1120, 1250), finder.c x2, ofsskip.c x3, runcmp.c x1, window.c x3. The review named compose.c and ofsskip.c; the grep found the rest and they were converted too. No positional `gate_in` initializer remains.
- HOUSE-7: the entry-table comment in formhash.c (~l.262-268) rewrapped; the 127-column line is split, wording unchanged.
- HOUSE-8: comment at fields.def's MF_CLASS(SIZE) row: the NO_<level> classes are positional after SIZE (next class number in levels.def's row order).

## Zero bytes
- No emitted-text path touched; the change is initializer syntax and comments. Rebuilt compose.o, ofsskip.o, formhash.o, finder.o, runcmp.o, window.o before and after.
- `.text` byte-identical for formhash.o only. The other five differ in instruction selection and scheduling: gcc zeroes a designated-initialized struct with a vector clear, then stores the named members (e.g. ofsskip.o fn_select: `pxor %xmm0` plus `movaps` where it stored each member). Same stored values, different instruction order; not byte-identical `.text`, not a behaviour change. Baselines: HEAD e9faa283c.

## Checks run
- -Werror -Wshadow with the kit's flags (`-O2 -g -Wall -Wextra -std=gnu11`, as `make strict` builds kit code): the six objects build clean.
- tests/memfn/run_arch_blind.sh: 16 passed, 7 FAILED. All seven are "NEW architecture vocabulary" hits in tests/mech/sabotages/S3001-S3004 (comments naming x86-64 / x86-64-v3), files this change does not touch (u2rev's, not allowlisted in c4_allowlist.tsv). The check was red on the branch tip before this lane; owed to whoever owns S3001-S3004.
- Not run (evening hold, branch does not build pcrec): make test, G2, mech.

## Charter-vs-committed checklist
- HOUSE-6 designated initializers: done (all 13 sites).
- HOUSE-7 comment rewrap: done.
- HOUSE-8 comment: done.
- -Werror object builds: done. .text identity: shown NOT identical for five of six (explained above).
- run_arch_blind.sh: run, 7 pre-existing failures reported above.
- Report and history index line: done.
