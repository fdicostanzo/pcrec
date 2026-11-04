# recida report: recursion-identity (A) re-based ([RECID-A], 2026-10-29)

## STATE AT HANDOFF

Update (Re-base 3): owed job main-recida3 (queue 331-main-recida3) re-runs the answers/newgate/plant validation; see the final STATE AT HANDOFF.

SUPERSEDED by re-base 2 (below, same heading at the end of the file): OWED: main-recida2 (330-main-recida2, after main-recida2-movers); job 698-recida-gate is withdrawn. Do not merge before both are green.

the re-based gate and every doc are COMMITTED on lane/recida; its VALIDATION IS OWED (the box was
never available: 4 ready queue jobs ahead, `boxlock` YIELDING). Nothing was stopped by an answer difference: the answer
checks that could be run (47 distinct patterns, 55 builds, 38,771 cells) are clean. Do NOT merge before job `698-recida-gate` reads green
(its `answers` step is the full answer check; its `newgate` and `plant` steps are the gate itself). Rulings file
`recida_rulings.md`: empty, nothing to apply. Evidence (lists, scripts) is in `docs/dev/lanes/recida_evidence/`.

OWED: queue job `recida-gate` (`698-recida-gate`, queued; ready before 17:30 on 2026-10-29, else not before 2026-10-30T13:30).

## Summary

- (A) now compares each call-free pattern's program region against `ABASEPIN = 7234c2e86` (the [EMIT-BIDI] merge,
  abi 86), not against `ac4917d`. All pin-relative exception machinery is deleted (list below); the stamp-truth
  converses, the four manifests, the positive control, the elision control and the linkage axis stay.
  `tests/codegen/run_recursion_identity.sh` went from 3108 to about 2430 lines.
- Measured at the re-base (emission only, `-fcomments`, the gate's own region extraction): main's program region equals
  `7234c2e86`'s for ALL 4480 call-free corpus patterns on all four axes (default, `--engine=vm`, `-fno-prefilter`,
  `--no-captures`): 0 differ on each. So abi 87-92 moved no call-free region and the re-based (A) starts at 0 differing.
- The default-axis 167 are fully accounted for (next section): 17 pre-existing (7 `(?U)`-possessive + 10 lookaround/context; the 9 `(?U)`-possessive movers are these 7 plus `(?U)a*+a` and `(?U)(a|b)*+`, which also moved at FLAG-SPELL),
  66 K128 (corefix, every one carries the K128 marker text), 84 [FLAG-SPELL] (flagfix). The vm axis (382 in job 695)
  adds patterns of the same two causes plus 2 EMIT-BIDI movers; 88 more vm patterns that differ from an older base are
  not movers at all (the older base REFUSES their new `\p{Age=}`/`\p{Emoji}`/`bc=`/`blk=` syntax). The bref-rename bucket dropped
  401 -> 366 -> 330 because 74 of its 404 patterns ALSO moved for K128/FLAG-SPELL and fell into the unattributed list.
- Answer check (run here, 55 gcc compiles): all 9 `(?U)`-possessive movers, 22 of the 66 K128 movers and 16 of the 84
  FLAG-SPELL movers (47 distinct patterns, 38,771 cells) compile at main and agree with libpcre2 on every cell, span and
  every group. 0 differences. The full populations are the owed job's `answers` step.
- Validation OWED: queue job `698-recida-gate` (6 steps, below). The gate was only `bash -n` checked here; a reduced
  run on a scratch copy was refused by the auto-mode classifier as interfering with box workloads, and I did not retry.

## Movers since ac4917d

Population: the 4480 call-free corpus patterns (`free`, from the old gate's own temp dir of the 14:21 trailgc run;
the old gate's 4481 in job 695). Method: for each pattern, region at main vs region at a compiler built from each
candidate commit (`recida_evidence/regionsweep.py`; builds of bf33d2dab^1, bf33d2dab, c4164f15b, b8c66a739,
187608482, 731228fb2, 9ae59f5d4, 7234c2e86, 7d3be7ec7). The old gate's per-axis counts (job 695,
`worktrees/.boxqueue/failed/20261029T141922.103463634-695-lands3-check/job.log`): 167/382/167/111.

**1. The bref-rename bucket (listed first, as asked).** The ruled [VAR] M6 seam rename (`bref_match(subject,len,off,off)`
-> `span_match(subject,len,ptr,len)`, d93aa931) touches every pattern whose pre-module region calls `_bref_match`:
404 call-free patterns, the same on all four axes (`bref_rename_population.default.txt`; text census 413 includes
patterns on the DFA that emit no call). Bucket as the gate counts it on the default axis = 330 = 404 - 74: the 74 are
the rename patterns that ALSO moved for K128 or [FLAG-SPELL], so the gate's rename rewrite no longer made them equal and
they sit in the unattributed 167 (`bref_rename_in_unattributed167.default.txt`; e.g. `((?:a|b|))+a\1`). Of the 330: 265
are the rename alone, 65 compose with another ruled bucket (ctx-node 42+1, possessify arms 14, fold 7+, lit-run 2...).
That is the whole reason the +/-30 band went red (401 at corefix^1, 366 on 10-23, 328/330 since).

**2. Movers by the landing that moved them** (counts are patterns, per axis default/vm/noprefilter/nocaptures; lists
in `recida_evidence/movers_*`):

| landing | ruled change | default | vm | noprefilter | nocaptures |
|---|---|---|---|---|---|
| before bf33d2dab^1 (unattributed at corefix^1, `movers_older17.default.txt`) | 7 of the 9 `(?U)`-possessive patterns (`(?U)a*+`, `a++`, `a?+`, `a{2,3}+`, `a{2,}+`, `(?U:\s*+)b`, `a(?U)\s{,2}+`; the other two moved again at flagfix) + 10 lookaround/context patterns (`(?<=a)+b`, `(?=a)+`, `(?=a)+a`, `(?i)(?<=a)b`, `(?m)(?<=\n)a\|b$`, `(?m)^ERROR(?:(?=\n)\|\z)` and four `(?<!(?i)..)`/`(?<=(?i)..)` lookbehinds) | 17 | (inside the vm list) | (inside) | (inside) |
| bf33d2dab (corefix merge, K128 guard write + label renumbering, abi 83) | ruled bugfix | 69 | 123 | 69 | 43 |
| 187608482 (flagfix merge, [FLAG-SPELL]: an empty concatenation node no longer survives, dead labels gone) | ruled fix | 93 | 359 | 93 | 59 |
| 731228fb2 (upropb, [UPROP-MORE]) | new syntax: the older base REFUSES these, so they were never movers | 0 | 88 | 0 | 0 |
| 7234c2e86 (EMIT-BIDI, abi 86; one C-text escaper respells a run-compare string) | ruled | 0 | 2 (`a{\n1}`, `a{\r1}`) | 0 | 0 |
| 9ae59f5d4 (subst), c4164f15b (kit R-29), b8c66a739 (iterators, abi 84), 7d3be7ec7 .. main (abi 87-92) | | 0 | 0 | 0 | 0 |

The 69 and 93 count every pattern whose region changed at that landing; the old gate had attributed 3 and 9 of them to a
ruled bucket (their other cause was ruled), so the default-axis unattributed 167 = 17 + 66 + 84. All 66 K128 members
carry its marker text ("the last mandatory iteration: record where it began"). `unattributed167.default.txt` is the old gate's
exact default list as recovered from the trailgc run's temp dir (a different tree, same 167 count and
`pick_patterns.py` mapping). The vm/noprefilter/nocaptures old-gate lists (382/167/111) need the gate itself: step
`oldgate` of the queued job regenerates all four and checks them against the committed answer populations.

## Answer checks

Method (`recida_evidence/anscheck.py`): for each pattern, build main's matcher (`--features all`, byte mode, the gate's
own flags), run EVERY (subject, startpos) cell over all strings of length <= 4 on an alphabet drawn from the pattern
(up to 3 letters, plus space/digit/newline when its escapes or anchors need them, plus one absent letter) through
`tests/backrefs/bref_batch.c`, and compare span AND every group span with libpcre2 through the project's ctypes oracle
(`tests/backrefs/bref_oracle.py`, libpcre2 10.46). On a difference it also builds the `ac4917d` matcher and says whether
the pre-module build agrees with libpcre2 (regression) or also differs (pre-existing).

Run here (default axis, main at 9db59722c = this lane's base, 55 gcc compiles in total):
- the 9 `(?U)`-possessive movers: 9/9 OK, 6,389 cells, 0 differences;
- a 46-pattern sample = 8 of the `(?U)` set + 22 of the 66 K128 movers (every third) + 16 of the 93 other unattributed
  (every sixth): 46/46 OK, 32,382 cells, 0 differences.
Not run here (the sweep cap: > 50 gcc compiles needs the box lock): the full populations. They are committed as
`pop_default.txt` (489), `pop_vm.txt` (489), `pop_noprefilter.txt` (179), `pop_nocaptures.txt` (119) = every pattern
whose region differs between bf33d2dab^1 and main on that axis (minus the 88 new-syntax patterns) plus the 17 older
movers; job step `answers` runs each on its own axis flags and `oldgate` adds any old-gate unattributed pattern outside
them (`pop_extra`). STOP RULE: one `DIFF` line there means the re-pin must not land.

## Re-pin

**Base: `7234c2e86`.** Why it is ruled: it is a main commit the manager merged (lane emitbidiland) and re-pinned (B) to
at that time; the 10-26 and 10-27 full-suite reads counted (A) at exactly 167/381/167/111 there and SCANEDGE-SET and
INLINE-C added no mover after it. Why it and not a later one: it is the EARLIEST commit whose call-free regions equal
main's (0 of 4480 on every axis; the commit before it, 9ae59f5d4, still differs on the two vm patterns above), so (A)
defends the longest range of landings (abi 87-92); `FILEPIN` itself would make (A) a subset of (B).

**Exceptions dropped** (all pin-relative, each unnecessary against this base; verified by the 0-of-4480 sweeps above):
1. [ART-SIZE] size-term region movers (`SIZE_TERM_REGION_MOVERS`, `SIZETERM_TOTAL`);
2. wave-G elision expectation inside (A) (`relided`, `nelide_region`); `ELIDED_PATTERNS` stays for (B)'s zero check and
   the elision control;
3. the deny-restore buckets: alternation island, ascii-fold, literal run, atom table, possessify arms (their
   stamp-truth converses and manifests stay);
4. the possessify arm-A engine-flip bucket (`POSS_FLIP_PATTERNS`, `rpossflip`);
5. the [VAR] M6 seam-rename rewrite (`bref_rename_rewrite`), its text census and +/-30 band;
6. D139's range-from-0 rewrite (`cls_range0_rewrite`);
7. the `${...}` var-construct admission and census;
8. the [UCP] U2 context-node bucket and census (`CTX_RE`);
9. the R4h layout canonicalizer (`adv_layout_canon`, `adv_new_count`, `adv_old_count`) and its floor;
10. the R-12 VMLAZY lazy-prefix rewrite (`lazy_prefix_rewrite`, `lazy_old_count`), its census and floor.
Added: `ABASEPIN` / `RECURSION_IDENTITY_ABASE`, the (A) base build (asserts `mod_recursion.c` is present and that it
compiles `(a)(?1)`), `gen_d`, a `BASE REFUSED` failure (a pattern the subject accepts and the base refuses is no longer
silently skipped), and the header block "[RECID-A]". `REFCOMMIT` (`ac4917d`) stays for the positive control and the
elision control only. Doc sentences updated: `docs/testing.md` (new section "[RECID-A]" and the two sentences that called
(A)'s pin never-moving), `docs/dev/decisions.md` (D136 addendum), `Makefile` comment, `tests/codegen/CLAUDE.md`, the
S273 and S711 mech rows' comments. `ac4917d` also appears in dated design/history/plan files, left as records.

**Keeping the gate able to fail.** The mech `recidentity` arm reads SKIPPED-no-git-history inside the matrix (scratch
trees have no `.git`), so the existing rows S273/S711 could never score this gate; the demonstration is the gate run
itself, step `plant` of the job. Shown here at the comparison level: a compiler carrying S273's plant (`vm_bref` length
`+ 1`, built at `$PCREC_TMPDIR/scratch/recida/pcrec_plant`) emits for `(a)\1` a region that differs from the base's by
exactly that token, and main's region is byte-identical to the base's (md5 of the extracted region: plant fc57f0332f10,
main = base 9e6f037579e4; likewise `^(?i:(a))\1$`: afff73030c20 vs 6be1c2198d40). With no exception list left to absorb
it, that difference is a `REGION DIFFERS` failure.

## Owed

- OWED: `698-recida-gate` (job script `docs/dev/lanes/recida_job_698-recida-gate`, queued as my last act: ready before
  17:30 on 2026-10-29, else not before 2026-10-30T13:30; cap 10800 s). Steps: build; refs (ac4917d matcher); oldgate
  (regenerates the four old REGION DIFFERS lists, KEEP=1); answers (the full answer check, STOP RULE); newgate
  (`bash tests/codegen/run_recursion_identity.sh`, must be rc 0 with 8 gate PASS lines per axis group and
  `(A) ... differing=0`); plant (S273 plant must turn it red through `(A)`). Green = six `== recida STEP ... rc=0`
  lines. Log dir `$PCREC_TMPDIR/scratch/recida/job698/`.
- Risk to read first in that job: the stamp-truth converses now run on every pattern the base accepts (before: only
  those `ac4917d` accepted), so a latent converse failure on a newer-syntax pattern would show in `newgate`. It would be
  a real finding about a deny axis, not about the re-base.
- Not done by this lane: plan.md [RECID-A] row (the manager's: it leaves plan.md for plan_completed.md when the job is
  green); the history index entry is added below in `docs/dev/history/claude_md/docs__dev__lanes.md`.

## Re-base 2 (2026-11-04, lane recida2, sonnet)

Why: the first re-base's gate job (698-recida-gate, 10-29) failed with 419 call-free movers versus 7234c2e86 on every axis, because
later ruled landings (abi 93-95: K134 trail checkpoints, R-30, the landmark walk, [VMREC] vm_stmt.c) changed emission before the branch
merged. It was never merged.

Done here:
- `git merge main` into lane/recida (merge commit f2238659d). Conflicts: `tests/codegen/run_recursion_identity.sh` (resolved: the
  branch's side everywhere, i.e. the exception machinery stays deleted, plus main's newer `FILEPIN` line f5de088bf and its
  self-pin comments), `tests/mech/sabotages/S273_span_match_length_off_by_one.sh` (both comments kept; main's
  `SAB_FILE=src/gen/vm_stmt.c` kept), and the history index (both sides kept). `bash -n` clean; no conflict markers left.
- New (A) base: **`4bd002e20`**, the commit the 2026-11-04 full suite froze. The merge showed no reason against it: `git diff
  4bd002e20 HEAD -- src cli lib memfn/src` is empty, so this tree's compiler IS 4bd002e20's. `ABASEPIN` default and the
  docs/testing.md "[RECID-A]" section updated; 7234c2e86 is kept as history (the first pin).
- Plant step updated for the [VMREC] move: the S273 plant site is now `src/gen/vm_stmt.c` (`vm_r_bref`), not emit_vm.c.

NOT yet known (the box was held by the kit's gates; both runs are queued, nothing inline): the mover list between 7234c2e86 and
4bd002e20, its per-axis counts (STOP RULE > 600), and the answer check. Jobs (scripts `docs/dev/lanes/recida2_job_329/330`):
- `329-main-recida2-movers`: the gate with `RECURSION_IDENTITY_ABASE=7234c2e86`, KEEP=1; writes `docs/dev/lanes/recida2_evidence/
  movers.{default,vm,noprefilter,nocaptures}.txt` (+ `other_diff_lines.*`); red if any axis > 600 or the lists are missing.
- `330-main-recida2` (waits on 329 via `boxqueue after`): answer check of a spread sample (every ~15th mover per axis, ALL (?U)-possessive
  movers, >= 50 distinct asserted) over libpcre2 with `anscheck.py` (any `DIFF` = STOP, do not land); the re-based gate at the new pin
  (rc 0); the S273 plant must turn it red through (A).
The pin edit is committed BEFORE the answers are in: if 330's `answers` step shows a DIFF or 329 reports > 600 movers on an axis, the
pin commit must be reverted, not merged. The evidence lists land uncommitted in the worktree and must be committed with the verdict.

## STATE AT HANDOFF

Lane/recida = main merged + the pin moved to 4bd002e20 + two queued jobs. NOT validated, DO NOT MERGE until
`329-main-recida2-movers` and `330-main-recida2` are both green (330 green = three `== recida2 STEP <n> rc=0` lines) and the
evidence lists under `recida2_evidence/` are committed. Rulings file `recida_rulings.md`: empty, nothing to apply. Old job
698-recida-gate is superseded (it ran the old base). Also owed to the manager: the plan.md row's status, once green, and moving it
to plan_completed.md.

OWED: queue jobs main-recida2-movers (329-main-recida2-movers) and main-recida2 (330-main-recida2).

## Re-base 3 (job fix)

Job 330 failed in 28 s on two faults, both fixed (harness only, no src/).

- **Base build**: the gate's (A) base archive took `src lib cli memfn` but not `shared/`;
  4bd002e20's `src/parse/rxt_source.c` includes `../shared/sha256.h`, so the build died with
  `fatal error: ../shared/sha256.h`. The (B) file-pin path already added `shared`; the (A) path now does
  too (`tests/codegen/run_recursion_identity.sh`). The failure line also carries the first error lines of the
  build log now (it was empty because the log tail went to stderr, which the job greps away). Reproduced
  alone under `gnutimeout 600` in scratch: without `shared` it fails as above; with it the base builds clean.
  Not a product fault.
- **Sampler** (`recida2_job_330`): per-axis stride sampling overlapped (46 distinct, needs 50). It now doubles
  the divisor until >= 50 distinct across the axes (every mover if need be): 89 distinct at divisor 30
  (default 31, vm 32, noprefilter 31, nocaptures 31). (?U)-possessive movers: 0 on default, noprefilter and
  nocaptures, 1 on vm (taken).
- Job `--dry-run` and `--ready` pass; requeued as `331-main-recida3`.

## STATE AT HANDOFF

Owed: main-recida3 (queue name 331-main-recida3), queued; (script docs/dev/lanes/recida2_job_330). Expect three `== recida2 STEP <n> rc=0`
lines. Any DIFF in answers = stop, merge nothing. Evidence dir recida2_evidence still uncommitted.
