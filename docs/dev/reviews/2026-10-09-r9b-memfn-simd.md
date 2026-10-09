# 2026-10-09 r9b — light re-check of the memfn SIMD design after D155 (integration.md rev 4.9 §R4.9)

Subject: `lane/memfn-r9` @ 021b3b32 (main merged in), lane r9d. Two
read-only sonnet critics; nothing built or run.

| critic | lens | verdict |
|---|---|---|
| r9b-contract | contract and consistency of §R4.9 against D155 and D155 addendum 1 | deliverable after RC-1 and RC-2 |
| r9b-docs | documentation staleness (superseded measurements, stale process text, index) | not mergeable until DS-10 (BLOCKER) and DS-5..7, DS-9 |

All findings were applied by lane r9d (docs only, marks `[r9b]`).

## Checks with no finding

- Shape (b) (file-scope level macro) survives only as a superseded note.
- §R4.9.2.5 and §R4.9.2.6 agree with each other.
- §R4.9.2.4's bracket accounting matches C18 leg (c).
- §R4.9.3.1 matches Q-R9-11 and `[MEMFN-RTDISPATCH]`.
- C18 leg (d) allows the selector shape only.
- The 43 panel ids (13 C, 16 M, 14 F) are all in §R4.9.12.
- Cross-references resolve: D26, D77, D78, D80, D84, D91, D94, D119, D144
  add. 1/3/4, D146, D147 add. 8-13, D149, D151 add. 3, D155 + add. 1,
  and the plan rows.
- `levels.def` and `fn_rows[]` are correctly described as "born later".
- Check 2: `[EMIT-VERB]` resolves via decisions.md only; plan.md has no
  row for it. Whether one is expected is main's call (main owns plan.md);
  no plan row was filed here.

## By-id completeness table

File abbreviations: I = `docs/design/memfn/integration.md`, MC =
`memfn/CLAUDE.md`, DC = `docs/design/memfn/CLAUDE.md`, RP =
`docs/dev/lanes/r9d_report.md`.

| id | sev | applied where |
|---|---|---|
| RC-1 | should-fix | I §17.3 (C18 sentence): preprocessed-equal off-target; on-target insertion plus one replaced call per SIMD FUNC, `[D155]` |
| RC-2 | should-fix | I §R4.9 summary ("PREPROCESSED-EQUAL off-target ..."): rewritten, raw text insertion-only |
| RC-3 | nit | I the original C18 table row: leg (b) struck with ~~ ~~, row title marks it SUPERSEDED by the next row |
| RC-4 | nit | I §R4.9.0 D155 row, Q-R9-6 (§R4.9.10), §R4.9.12 item 6: "restated by add. 1 / Q-R9-10" appended |
| RC-5 | nit | I Q-R9-10 (+139 B) and §R4.9.2.6 ("twelve witnesses"): measured on the pre-(c) rendering, re-measured by G1 |
| RC-6 | nit | I Q49 row (§23 table) and R4e′ ("Q49 applies as written"): "except R4e′.0b, §R4.9.2.6"; the third hit (R4e′ batch-1 text) already carried `[D155]` R4e′.0b, left as is |
| RC-7 | nit | MC "Every search site migrates here": "(R4e′.0b, D155, is the one ordered byte move)" |
| DS-1 | - | already resolved by the manager's merge (lanes index conflict); no edit |
| DS-2 | - | already resolved (clean merge); no edit |
| DS-3 | should-fix | I header and §R4.9 intro: "reconciles the two at merge" replaced by "[M7] marks merged, text at 4.9"; the r9b pass noted in the header. MC's merged paragraph reads in order (rev 4.9, §R4.8, R4h/M4/M7 preps, §R4.7): no change |
| DS-4 | nit | MC checked, order already correct, no edit |
| DS-5 | should-fix | I C18 property (a): "taken on the superseded ... rendering" |
| DS-6 | should-fix | I C18 property (c): likewise |
| DS-7 | should-fix | I "C18 on the new shape" block: added the all-figures-superseded banner (144 compiles, -O2 inlining, counts, 15,884,000 calls) |
| DS-8 | nit | I `-O2` inlining at "inlined at -O2, measured" and the §R4.9 entry-point note; the `-Os` register line (safe, SIMD-off text identical in (b) and (c)); the runtime-dispatch probe header (superseded rendering per RP "Probes", not re-run on (c)) and "Measured: ... pcmpeqb 4/8/8" |
| DS-9 | should-fix | RP "Probes": banner that the Results block predates shape (c); `build/d155/` is gitignored scratch, the transcript is the record |
| DS-10 | BLOCKER | I header (line 19), §R4.9 summary, the test-list "C18's two legs" (now four legs (a)-(d)), and the original row title (marked SUPERSEDED). Remaining "two legs" hits are the struck/labelled old row |
| DS-11 | should-fix | MC layers: "OFF BY DEFAULT; the default flip is R4f, its own ruled event (§R4.9, D147 addendum 11)" |
| DS-12 | nit | MC: bracket ops `simd_open`/`simd_close` and `plan_pos2` added to "one bit" |
| DS-13 | nit | I old "SIMD last" text (R4e′/R4f, five hits: step intro, §13 R4f, two R4e′ Trigger lines, the older R4f list): `[rev4.9]` superseded tag |
| DS-14 | nit | DC rev 4.9 entry: Q-R9-1 was RESOLVED by D144 add. 4 (I §R4.9.10 says so), Q-R9-2..8 RULED |
