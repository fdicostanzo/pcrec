# slotxf8 — slotx review r1 follow-ups F7 (§7.2 sentence) and F8 (one draft set per target)

STATE: stopped (F7 done; F8 stopped at the brief's STOP RULE, one question for main below)

## Summary

F7 is done: `docs/design/measure_sets.md` §7.2 now has main's agreed sentence at the rule's home (a card row
binds from its first merge to main or its first set/record under it, whichever comes first; before that it is a
draft of its lane chain and may be respelled). The card file comment (`memfn/data/cards/kit-grid.tsv`) and
`memfn/data/cards/CLAUDE.md` now point at §7.2 and no longer restate the carve-out.
`docs/dev/lanes/mfind_report.md` has the one-line "respelled by lane slotx" note under find_hit@6's old dims.
There is no ver-7 row.

F8 is STOPPED before any code change. `docs/design/memfn/span_cards.md` §2.7 cannot spell a per-target class for
the three targets the ver-6 run actually uses (generic, x86-64, x86-64-v3) without adding something §2.7 does not
define. The brief's STOP RULE covers exactly this case, so I report the question instead of making up a spelling.
F6 stays open, because it follows F8. The interim refusal (DRAFT-TARGET MIXED, S3172) is still in place and still
fires, so no wrong draft can be written in the meantime. No committed set or record exists for ver 6: there is no
`grid6` anywhere under `measure_store/` or `memfn/data/sets/`.

## F7

| site | change |
|---|---|
| `docs/design/measure_sets.md` §7.2, the `owner`, `quantity`, `ver` row | appended, tagged `[review 2026-11-15 r1 F7]`: "A row binds from its first merge to main or its first set/record under it, whichever comes first; before that it is a draft of its lane chain and may be respelled" |
| `memfn/data/cards/kit-grid.tsv` (comment only, no card row touched) | "before any merge or timing of the row, so no set or record reads its first spelling" is replaced by "while the row was still a draft of its lane chain (when a card row binds: docs/design/measure_sets.md §7.2)" |
| `memfn/data/cards/CLAUDE.md` | "(lane slotx, before any merge or timing)" is replaced by "(lane slotx, a respelling of a draft row: `measure_sets.md` §7.2 says when a row binds)" |
| `docs/dev/lanes/mfind_report.md`, under the `find_hit@6` dims line | "(Respelled by lane slotx (adds `reject`), before any merge or timing; measure_sets.md §7.2.)" |

Commit 92d911ef2. Who reads `kit-grid.tsv`, found by grep: `slot/plan.py`, `memfn/data/sets/generate.py` (only
for kit-grid@1's interim set), `span_cards/tree_drill.py`, `r17b_prime/b4prep/mk_lever_set.py`, mech sabotage
S2931. All of them parse card rows and none pins the file's bytes. Only `#` lines changed.

## F8

What the ruling needs: `write_draft` writes one set per (ver, target), and each set's `class` header carries its
target (§2.7: `class` IS the set's target identity, folded into the format-2 digest).

What §2.7 defines: `class` = "the ISA level the fixtures were compiled FOR / the box's tuning class". It spells
exactly one value, `x86_64/zen4`, for the generic (scalar) target compiled `-march=x86-64 -mtune=generic`. It
says grid1's `x86_64-avx2/zen4` must not be copied. It leaves the spelling of other targets' variants to J6's
design at [XARCH-DEV]. `docs/spec/measures.md` §2.1 says only "the ISA level and tuning class it was measured
for". The loader (`src/core/measures.c`) treats `class` as free text, so a new value would not be a loader event.

The ver-6 rows use three kit targets (`memfn/src/targets.def`): `generic` (every unframed arm), `x86-64` (mfind-w16)
and `x86-64-v3` (mfind-w32). §2.7 does not decide either of these:

1. **x86-64-v3 has no class spelling.** Several spellings are plausible (`x86_64-v3/zen4`, `x86-64-v3/zen4`), and
   §2.7 rules none of them.
2. **generic and x86-64 come out as the same class under §2.7's own definition.** Both are compiled for the
   `x86_64` baseline (x86-64's only need, sse2, is already in the floor), so both read `x86_64/zen4`. If the split
   is per KIT TARGET, the two sets need distinct class spellings. §2.7 defines none, and `targets.def` keeps the
   target tokens (`x86-64`) apart from the class's `x86_64` on purpose. Without distinct spellings the class does
   not carry the kit target and F6 does not close. If the split is per ISA LEVEL (the class's own meaning), then
   generic and x86-64 rows share one set, and that conflicts with the ruled guard "a set that would still mix
   targets after the split is refused".
3. Under either reading, each extra set needs its own `id`: no-shadowing refuses a reused id with another class,
   and `record.SETS` has one id per ver (`zen4-grid6@1`). This is naming, not format, but nobody has ruled it yet.

**The question for main** (please reply either way): for the one ver-6 run, what is (a) the class of the
x86-64-v3 set, (b) whether generic and x86-64 rows are one set (`x86_64/zen4`, split by ISA level) or two (and if
two, the x86-64 set's class), and (c) the per-target set ids? **My leaning:** split by the ISA level the code was
built for, because that is what `class` already means in §2.7. That gives generic + x86-64 -> `zen4-grid6@1`,
class `x86_64/zen4` (§2.7's ruled value), and x86-64-v3 -> `zen4-grid6-v3@1`, class `x86_64-v3/zen4`. The guard
would then refuse any set whose rows were built for more than one ISA level. F6 closes on that reading as long as
the guard holds every row's target to the class's ISA level (x86-64 and generic code is the same baseline code;
the ISA check, `link.py`'s `target_isa`, already shows that per cell). The rest of F8 (a RED self-test case and
sabotage rows S3183+, the split, GREEN) is ready to go once main answers. Its expected outputs depend on that
answer, so I have not written any of it.

## Validation

| what | command | result |
|---|---|---|
| premise | `python3 -I .../slot/est.py selftest $X/st0` on d26bc5751 | `== est SELFTEST ok: 56 cases, 0 wrong`; `[F8] write_draft refuses a ver-6 set mixing targets (generic, x86-64, x86-64-v3) and writes no set ok` |
| est self-test after F7 | `python3 -I .../slot/est.py selftest $X/st1` | `== est SELFTEST ok: 56 cases, 0 wrong` (no new cases: F8 not built) |
| make strict | `make -j8 strict` (`$X/strict.log`) | `strict rc=0`, no `*** [` line |
| dry runs | `run.py dry JMB/JMH $X/dryJ slotxf8-J` (`$X/dryJMB.log`, `$X/dryJMH.log`) | both rc=0: JMB `ROUND CHECK ok: 24 points, 2688 calls, 0 misses` (launch 7), groups 2; JMH `ROUND CHECK ok: 172 points, 2752 calls, 0 misses` (launch 7), groups 23 (about 9 min) |

`$X` = `/var/tmp/pcrec-pcrec/scratch/memfn/slotxf8`. No sabotage rows are new, so the combined gate's full table
has nothing new to show DETECTED from this lane. v1/e3/e4 are not affected: F7 touched comments and docs only.

## STATE AT HANDOFF

- STATE: stopped (F8 at the STOP RULE; F7 complete)
- tip: the commit carrying this report on lane/memfn-slotx (F7 at 92d911ef2)
- new sabotage rows: none (S3183-S3187 unused)
- rulings file: none applied (`slotxf8_rulings.md` empty at every checkpoint)
- OWED: none
- next: F8 by a fresh lane once main answers the question above; F6 closes with it
