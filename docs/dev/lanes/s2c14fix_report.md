# s2c14fix — review r10's rulings on span_cards rev 1.4 (lane report)

Branch `lane/memfn-s2c14fix`, cut from lane/memfn-s2c @ b4e0a8bab plus the review commit 4a1b3ee5a. Rulings:
`docs/dev/reviews/2026-11-06-r10-memfn-s2rev14.md`. Scope: this worktree and
`/var/tmp/pcrec-pcrec/scratch/memfn/s2c14fix/` only. The s2c worktree, the main tree and pcrec-bench were
not touched.

## Summary

- Every FIX-NOW is applied: REV14-1, -2, -3, -4, -6 and -7. REV14-5 and REV14-8 are ACCEPTED, each with its
  sentence or doc text.
- **No timed binary changes** (see "Timed-code impact"). Window 2's tree (b4e0a8bab) can be judged by this est.
- REV14-2's cap is **`r_max_e6 = 53751` (0.054 wb)** in `memfn/data/policy.tsv`. It is the largest A/A
  resolution over the first window's eight near-zero verify rows, derived by the new
  `docs/design/memfn/span_cards/rmax_drill.py`. It is labelled UNMEASURED DEFAULT (D149), because the population
  and the max are choices over one window. Trigger: re-derive it on the first window timed with rev 1.4's base.
- **Replay** with the fixed est over a fresh copy of s2d-20261106:
  - l1.p0/p50 are NULL (all six trimmed launches negative).
  - c1.p0/p50 are NULL (|med| 0.098/0.093 wb is above r = 0.054 wb).
  - w1 and c2 are sub-resolution at r 0.054 wb.
  - The outcome is REFUSED on byte.libc, l1 and c1.
- Slot sabotage: control green, **21 DETECTED, 0 MISSED**. S2941 and S2942 are re-aimed. S2946-S2949 are new.
- **OPEN for the manager:** the records of windows 1 and 2 pin no `r_max_e6`, because they were planned before
  the row existed. est then uses the live row and says so: a `policy` line in `rows` and a `# note r_max_e6` in
  the draft. S2e's recompute, which reads only the set and the record, cannot get r_max from a window-2 record.
  Options:
  - (a) the window-2 set's PROVENANCE names the value;
  - (b) the window-2 record is re-pinned before the draft;
  - (c) a window after this lands is the one that counts.
  Leaning: (c) for the official set, and (a) if window 2's set is kept as scratch.

## Fixes by finding id

- **REV14-1** (FIX-NOW). `slot/est.py`: a delta row that fails the NULL rule and whose six trimmed D_l are all
  negative is `null` ("a fixture defect, whatever r"). This is checked before the ¶3a branch.
  - Self-test cases: "negative on all six trimmed launches within r: null" (new) and "signs mixed, a negative
    median within r: measured, its value clamped to 0" (new; it replaces rev 1.4's clamp-on-all-negative case).
  - S2942 is re-aimed at the second case. S2947 is new.
  - The §R1.4 replay text is corrected: rev 1.4's "PASS" for l1/c1 demonstrated the defect.
  - `measures.md` §3.5¶3 and ¶3a are amended.
- **REV14-2** (FIX-NOW). `slot/est.py`: `r = min(resolution(x), R_MAX)`. R_MAX comes from the record's pinned
  policy (`r_max(rec)`), or from the live row, named, when the record predates it. The ¶3a branch also needs
  `aa <= r`: the row's paired A/A (§3.4 step 5's `med(|xb_l - x_l|)`) must be within r.
  - `memfn/data/policy.tsv`: the row `r_max_e6 53751`, with its derivation and the D149 label.
  - `span_cards/rmax_drill.py` derives it. It prints its inputs; with RUNDIR it re-takes them and checks
    equality, which passes on the copy.
  - Self-test cases, one per bound:
    - |med| within its own r but above r_max: null;
    - within r_max but below its own r: sub, r capped;
    - A/A above r: null;
    - A/A at r: sub;
    - the live r_max moved after the run: the pinned value rules;
    - a record pinning no r_max: the live row, named.
  - Sabotage: S2948 (cap dropped) and S2949 (A/A dropped).
- **REV14-3** (FIX-NOW). `slot/link.py` `null_check` has two halves.
  - The independent half (it never calls null_body): the base body is `slot_null(L)`, where L is ONE WHOLE load
    spelling the arm's body makes (fullmatch, not a substring), or its memcmp's `slot_ld`.
  - The equality half: the body EQUALS `null_body(arm body)`.
  - A synthetic probe refused the critic's four bodies: `pos`, `subject`, a constant and
    `mf_w4(subject + pos) == K`. It also refused the whole compare, a later load and a wrong-width load. It
    accepted only the first load.
  - S2941 is re-aimed so that null_body keeps the compare (the independent half refuses). S2946 is new: the
    render keeps the last load, and only the equality half refuses it.
- **REV14-4** (FIX-NOW). span_cards.md §3.5's table:
  - The "delta, signs mixed" row is now sub-resolution (med 1000 ≤ r 2331, aa 400: value 1000, noise 2331).
  - The rows are corrected under the r10 rule and new rows are added for the cap and the A/A.
  - `drill.py` gains ¶3a (`subres`), with R_MAX from policy, and computes every ¶3a row the table states.
- **REV14-5** (ACCEPTED). One sentence each in span_cards §R1.4 and `measures.md` §3.5¶3a: the clamp lifts a
  truly-zero row by at most r, which its noise covers.
- **REV14-6** (FIX-NOW). `slot/run.py`: `cpu_ticks()` reads utime+stime from `/proc/<pid>/stat`.
  `corunners()` ranks by the CPU used over `CORUNNER_SPAN` = 0.5 s, between two reads (UNMEASURED DEFAULT,
  D149). The `pid:comm:%cpu` format is unchanged, so record.py and QUIET_TOP need no change. §3.3 text updated.
- **REV14-7** (FIX-NOW, doc). span_cards §R1.4 and `measures.md` §3.5¶3a: `abs_ns_e6` stays the unclamped
  `med(abs_l)` and is provenance only.
- **REV14-8** (ACCEPTED, doc). The text says "the compare replaced by a register compare": §2.3's verify_cmp row
  and §3.2's null base, citing the critic's objdump (mov $1/cmp/sbb vs sete/movzbl/add).

Design text is marked `[rev1.4 r10-<id>]`, with §R1.4's r10 table. Spec hunks are in `measures.md` §3.5¶3 and
§3.5¶3a.

### The replay: every row's status (fixed est over a COPY of s2d-20261106)

How it was run:
- `cp -r` of the run dir to `scratch/memfn/s2c14fix/replay`.
- `record.py finalize` with the run's states and commit 508178bd2. This adds the quiet section and the notes; the
  rest is byte-equal.
- `est.py rows`, exit 3. Committed as `docs/design/memfn/span_cards/s2d1/r10_replay_rows.txt`.
- Its first line: `policy r_max_e6 53751 NOT pinned by the run record (planned before the row)`.

| row | value_e6 | noise_e6 | status |
|---|---|---|---|
| `kit.enter.1.NONE` | 1098768187 | 8545693 | ungated |
| `kit.enter.3.NONE` | 41765488 | 1687112 | ungated |
| `kit.enter.4.NONE` | 43434065 | 1711816 | ungated |
| `kit.enter.5.NONE` | 5101122 | 129232 | ungated |
| `kit.enter.6.NONE` | 38628124 | 1210175 | ungated |
| `kit.find_byte.libc` | 39024 | 1295 | gate FAIL |
| `kit.find_byte.pair` | 73639 | 1375 | gate pass |
| `kit.find_byte.walk` | 1000000 | 1985 | gate pass |
| `kit.find_hit.libc.periodic.one.1024` | 16266755 | 837117 | ungated |
| `kit.find_hit.libc.periodic.one.256` | 19116062 | 315968 | ungated |
| `kit.find_hit.libc.random.one.1024` | 56112819 | 915989 | ungated |
| `kit.find_hit.libc.random.one.256` | 54889371 | 430914 | ungated |
| `kit.find_hit.pair.periodic.alt.1024` | 87018336 | 1042643 | ungated |
| `kit.find_hit.pair.periodic.alt.256` | 39604378 | 715625 | ungated |
| `kit.find_hit.pair.periodic.one.1024` | 84768923 | 5129675 | ungated |
| `kit.find_hit.pair.periodic.one.256` | 38073332 | 458051 | ungated |
| `kit.find_hit.pair.random.alt.1024` | 142070682 | 3120639 | ungated |
| `kit.find_hit.pair.random.alt.256` | 95633348 | 1533056 | ungated |
| `kit.find_hit.pair.random.one.1024` | 130792281 | 2461235 | ungated |
| `kit.find_hit.pair.random.one.256` | 88469624 | 1456608 | ungated |
| `kit.find_hit.walk.periodic.one.1024` | 30476485 | 6008137 | ungated |
| `kit.find_hit.walk.periodic.one.256` | 28881170 | 1676936 | ungated |
| `kit.find_hit.walk.random.one.1024` | 51959001 | 23027371 | ungated |
| `kit.find_hit.walk.random.one.256` | 45968888 | 17186103 | ungated |
| `kit.verify_cmp.rc-memcmp.l1.p0` | - | - | null: negative per-event cost on all six trimmed launches (a fixture defect, whatever r) |
| `kit.verify_cmp.rc-memcmp.l1.p50` | - | - | null: negative per-event cost on all six trimmed launches (a fixture defect, whatever r) |
| `kit.verify_cmp.rc-words.w1.p0` | 23935 | 94773 | sub-resolution: consistent with zero within r 53751 |
| `kit.verify_cmp.rc-words.w1.p50` | 26065 | 99433 | sub-resolution: consistent with zero within r 53751 |
| `kit.verify_cmp.rc-words.w2.p0` | 7905906 | 86013 | ungated |
| `kit.verify_cmp.rc-words.w2.p50` | 8304745 | 108576 | ungated |
| `kit.verify_cmp.rc-words.w3.p0` | 13724385 | 189184 | ungated |
| `kit.verify_cmp.rc-words.w3.p50` | 11958329 | 767280 | ungated |
| `kit.verify_cmp.settest.c1.p0` | - | - | null: below its paired A/A or signs mixed, at a size above its resolution r 53751 |
| `kit.verify_cmp.settest.c1.p50` | - | - | null: below its paired A/A or signs mixed, at a size above its resolution r 53751 |
| `kit.verify_cmp.settest.c2.p0` | 34998 | 88372 | sub-resolution: consistent with zero within r 53751 |
| `kit.verify_cmp.settest.c2.p50` | 19088 | 96709 | sub-resolution: consistent with zero within r 53751 |
| `kit.verify_cmp.settest.cn.p0` | 6999281 | 687251 | ungated |
| `kit.verify_cmp.settest.cn.p50` | 15876576 | 127868 | ungated |

- Moved since rev 1.4's replay: l1.p0/p50 and c1.p0/p50 went from sub-resolution at 0 to null. w1 and c2 stay
  sub-resolution, but r is now 53751 (capped) and the noise is the measured 88372-99433. Every other row is
  unchanged.
- Drift is kept in all five jobs. The notes are unchanged.
- `== s2 OUTCOME REFUSED exit 3 floor:byte.libc (text); floor:verify.rc-memcmp.l1 (text);
  floor:verify.settest.c1 (text)`.
- c2.p50 is the row that sets R_MAX (its r_AA is the max), and its aa of 49610 is just inside r.

## Timed-code impact

The intent was NO, and it holds for every file. No fix needed a stop.

| file | changes a timed binary? | why |
|---|---|---|
| `docs/design/memfn/span_cards/slot/est.py` | NO | post-run estimator; reads cells and the record only |
| `docs/design/memfn/span_cards/slot/link.py` | NO | only `null_check` (runs after render) and one print line. `render`, `null_body`, `WRAP_CMP`, `SLOT_HELPERS`, the pads and the link commands are byte-unchanged, so every arm, twin and base TU is identical. link.py is hashed into a RUNDIR's ctl-inputs key, so a NEW rundir rebuilds ctl from identical text; window 2 is frozen at b4e0a8bab anyway |
| `docs/design/memfn/span_cards/slot/run.py` | NO | `corunners`/`cpu_ticks` run in the quiet check between launches, outside the rounds; they add a 0.5 s sleep per quiet check. The drv invocations (taskset, `round R NFILE`) are unchanged |
| `docs/design/memfn/span_cards/slot/sabotage.sh` | NO | plants run in scratch copies |
| `memfn/data/policy.tsv` | NO | read by plan.py into the frozen plan's `policy` section and the record; no reader in link/gen/drv/art (grep). A future window's `plan.tsv` bytes, and so its manifest's `plan` sha, will differ; the executables will not |
| `docs/design/memfn/span_cards/drill.py`, `rmax_drill.py` | NO | design drills, never run by a window |
| `docs/design/memfn/span_cards.md`, `docs/spec/measures.md`, CLAUDE.md files (span_cards, s2d1, slot, memfn/data), `s2d1/r10_replay_rows.txt`, this report | NO | text |

gen.c, drv.c, slot.h, art.py and plan.py are untouched (`git diff b4e0a8bab --stat`).

## Sabotage

`slot/sabotage.sh SCRATCH` (all rows) ran with `nice -n 19`. Log: `/var/tmp/pcrec-pcrec/scratch/memfn/s2c14fix/sab.log`.
- Control: J2 dry run green, est self-test green.
- **21 DETECTED, 0 MISSED**.
- After a one-line change to link.py's print message, n1, n2 and n3 were re-run (`sab2.log`, see Validation).
- "Green when reverted" is the control: the unplanted copy, same files.

| row | id | plant | detector (red) |
|---|---|---|---|
| n2 | S2941 (re-aimed, r10-REV14-3) | null_body returns `slot_null(<whole arm body>)`: keeps the compare | J4 dry run: `NULL-BASE MISMATCH base.null.c1: its body 'slot_null((subject[pos] == 47))' is not slot_null(one load ...)` |
| s1 | S2942 (re-aimed, r10-REV14-1) | sub-resolution value not clamped | self-test "signs mixed, a negative median within r: ... clamped to 0" WRONG |
| s2 | S2943 (re-anchored) | the `|med| <= r` condition dropped | self-test "signs mixed at a size above r: null" WRONG |
| n3 | S2946 (r10-REV14-3) | the render keeps the arm's LAST load (null_body over the last ` && ` conjunct) | J4 dry run: `NULL-BASE MISMATCH base.null.w2: its body 'slot_null(mf_w2(subject + pos + 1))' is not null_body(...)` |
| s3 | S2947 (r10-REV14-1) | the all-negative rule dropped | self-test "negative on all six trimmed launches within r: null" WRONG |
| s4 | S2948 (r10-REV14-2) | the cap on r dropped | self-test "\|med\| within its own r but above r_max: null" WRONG |
| s5 | S2949 (r10-REV14-2) | the A/A requirement dropped | self-test "within r, its paired A/A above r: null" WRONG |
| q1 | S2944 (re-anchored) | corunners returns `-` | J2 dry run `QUIET-LOG` |

The other 13 rows (j, j2, k, l1-l3, g2, g3, f1, f2, f6, n1, b1) are unchanged and all DETECTED.

Not covered by a sabotage row:
- REV14-6: telling an interval rank from a lifetime rank needs a controlled busy process, which means load on a
  box with a window. The four ids went to the est bounds.
- The pinned-vs-live r_max read: a self-test case covers it ("the live r_max moved after the run"), but it has no
  id.

## Validation

All of it was light: `nice -n 19`, -j2 at most, one step at a time. Nothing was queued and no timing ran.
`boxqueue status` showed only `171-altfix-...test` running, with no `kit-s2d-*` job. Log: `scratch/memfn/s2c14fix/val.log`.

- \`make\` (nice, -j2): rc 0.
- \`make strict\`: rc 0 ("whole tree compiles clean with -Werror -Wshadow").
- \`make test-memfn-finder\`: checks 3272 passed, 0 failed; proof checks 882 passed, 0 failed.
- \`tests/registry/limits_check.sh\`: 39 passed, 0 failed.
- \`tests/memfn/run_arch_blind.sh\`: 17 passed, 0 failed.
- \`make test-plan-lint\`: 2 passed, 0 failed (selftest 32 plants, 17 of 17 rules).
- \`make test-spec-history\`: 11 passed, 0 failed.
- \`slot/est.py selftest\`: **22 cases, 0 wrong**. 8 cases are new for r10 and 1 is re-aimed; each new bound has
  its own case.
- \`slot/sabotage.sh\`, all rows: control green, 21 DETECTED, 0 MISSED (\`sab.log\`). After the final link.py
  print change, n1, n2 and n3 were re-run: 3 DETECTED, control green (\`sab2.log\`).
- **Null-base green control:** the sabotage control dry-runs J2 only, so it never reaches a null base. An
  UNPLANTED \`run.py dry J4\` at the tip ran separately: rc 0, \`null-base: 7 bases, each its class arm's text
  outside the compare, its body null_body(the arm's), one load the arm makes\`, round check 0 misses
  (\`j4dry.log\`). Its quiet sample names co-runners by interval CPU
  (e.g. \`1367663:bash:10.0,...,8169:claude:4.0\`).
- **Rendered-TU identity:** link.py's \`render\` at b4e0a8bab (an exported copy) and at the tip, over the same
  fixture, gave 81 TUs (every non-artifact arm, twin, base and ctl of J2-J5) with IDENTICAL sha-256
  (\`rend_old.txt\` = \`rend_new.txt\`).
- \`rmax_drill.py RUNDIR\` over the replay copy: its inputs equal the run's; r_max_e6 = 53751.
- \`drill.py\` runs and prints every ¶3a row the §3.5 table states.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| FIX-NOW REV14-1 | est.py sign rule; replay text corrected; spec ¶3/¶3a; S2942 re-aimed, S2947 |
| FIX-NOW REV14-2 (R_MAX in policy.tsv with derivation, D149 label; A/A in branch; a self-test case per bound) | policy.tsv row; rmax_drill.py; est.py `r_max`, cap, `aa <= r`; six self-test cases; S2948, S2949 |
| FIX-NOW REV14-3 (equality; S2941 re-aimed) | link.py null_check; S2941 re-aimed; S2946 |
| FIX-NOW REV14-4 (text + drill.py ¶3a) | span_cards §3.5 table; drill.py `subres` |
| FIX-NOW REV14-6 (interval CPU) | run.py `cpu_ticks`/`corunners`; §3.3 |
| FIX-NOW REV14-7 (doc) | §R1.4; measures.md §3.5¶3a |
| ACCEPTED REV14-5 (one sentence) | §R1.4; measures.md §3.5¶3a |
| ACCEPTED REV14-8 (doc) | §2.3 verify_cmp row; §3.2 null base |
| new sabotage S2946-S2949, red planted / green reverted | four rows, DETECTED; control green |
| design text marked `[rev1.4 r10-<id>]`, §R1.4 rows; spec hunks by section cite | done; measures.md §3.5¶3, ¶3a |
| replay over a COPY; l1/c1 NULL; every row's status | done (table above; `s2d1/r10_replay_rows.txt`) |
| Timed-code impact section | done: NO for every file |
| validation list | see Validation |
| report + lanecheck DONE | this file; lanecheck below |

## STATE AT HANDOFF

Complete, OWED none. Tip: see the handback message. Open for the manager: the r_max pin of the window 1/2
records (Summary). The A/A derivation of r_max is to be redone on the first window timed with rev 1.4's base.
