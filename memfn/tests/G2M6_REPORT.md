# G2M6 — G2 brought to MF_SITE_ABI 8: the strided ADVANCE (lane g2m6, D27-blinded)

Lane g2m6, 2026-10-09, Linux dev box, in the cell `worktrees/g2u-cell/`. Serves the kit's request R-10 (M6,
VMSTRIDE: the strided ADVANCE, `MF_SITE_ABI` 8, `MF_MAX_TERM` 32). Written from `memfn/include/memfn.h`,
`docs/design/memfn/integration.md` (section 15.9's contract sentences; the greps for VMSTRIDE / Q-R10 / strided
gave the section numbers) and the cell's own G2 files; the kit's source was not read. Nothing was committed (the
cell is not a git work tree).

## Headline

`memfn/tests/run_g2.sh --quick --rows`, final tree, seed 20261005, gcc 15.2 (no clang on this box, so the clang
ASan+UBSan leg did not run, as in the baseline; the strided family was run under gcc ASan+UBSan by hand, below):

| | passed | failed | wall |
|---|---|---|---|
| before (this brief, the tree as handed over) | 48,566,738 | 0 | 202 s |
| after, final tree | **51,169,258** | **0** | **267 s** (313 s on the run before the last floor edit) |

Exit 0. Log of the final run: `.scratch/m6/r5.log` (work files `.scratch/tmp/g2.*`, kept). The wall times are on a
box that was never idle (load average 18-60 from other lanes, my runs pinned to `taskset -c 12-15`), so the
202 s -> 267 s difference is partly the box; the strided family itself costs about 35 s of driver time in the
foreground leg (`bs/g2_run --quick` on the strided batches alone: 30 s) plus five more W2 builds that run beside it.

Rows: `FLOOR_ROWS` stays 15 (no new row); (a) (b) (c) (d) (f) green, and the new check (g) (below).

```
row-chosen arms generic 261326        (224,416 in the baseline: +36,910, the strided sites' selections)
(all other rows unchanged from the baseline and the g2m7 report)
PASS (g) STRIDED sites chose arms/generic 4633 times >= floor 4100   (the STRIDE-only generator process)
```

The older families are untouched: `G2 family mismatch` reads 207 sites / 966,276 checks / 0 failed in the baseline and in
the final run, and the other families' counts are identical.

## Commands

```
cd /home/pcrec/projects/pcrec/worktrees/g2u-cell
TMPDIR=$PWD/.scratch/tmp taskset -c 12-15 gnutimeout 2400 memfn/tests/run_g2.sh --quick --rows --keep
```
Run in the background, the log polled. No full tier, no `make`. Sabotage: the same command with `--no-rows` in scratch
copies (`.scratch/sab/m6{a,b,c}`, `build` symlinked), by `.scratch/m6/sab.sh`. By hand, outside the runner: the strided
family alone with other seeds and under gcc ASan+UBSan (`.scratch/m6/stonly.sh SEED OUTDIR [cc flags]`).

## What is covered, per charter item

### 1. The strided ADVANCE oracle

`g2_ref.c` `g2_ref_stride`, a plain scalar byte loop over the generated sets; it calls no kit function (not even
`mf_ref_*`). From the cursor `lo`: advance by W while the cap (the counter, starting at `count_start`, is below
`span_hi`), `cursor + W <= n` (G2's own `more`) and every `s[cursor + i]` is in set_i. W = 1 is today's ADVANCE. It
returns why it stopped (cap / `more` / a failing term and its position), which the driver counts. The counter
advances exactly j times from its start, owned by the kit (named, or its own when only a cap needs one) or by the
caller (`count_by_caller`; the wrapper declares it before the kit's text). The final cursor and, when a counter is
named, its value are both checked.

Defects of the reference that must be caught (W1, `--ref-defect`): 8 the cap counted in bytes (`span_hi / W`
iterations), 9 `more` strict (`cursor + W < n`: the last exactly-fitting block dropped), 10 the terms in reverse order.
Failed checks on the sampled batches: 96,822 / 30,762 / 188,580.

### 2. The generated space

Family `stride` (`gen_fam_stride`, own RNG stream and id range 1,000,000; `--seed` moves it): 792 hard sites run
(the generator's FAMILY line: 792 rendered, 0 refused, all through the one row the kit reports, `generic`), plus 356
more of the enforced class `hook-nonident` (non-identifier `s` / cursor text; below).

* **W** in {1, 2, 3, 7, 8, 9, 16, 31, 32}: 160 / 78 / 77 / 80 / 80 / 78 / 81 / 79 / 79 sites run (W = 1 has the
  extra sites of item 4).
* **B - c0** ("rem"): every value 0..130 up to 40, and above 40 the residues W-1, 0 and 1 modulo W and every fifth,
  at `lo` 0 and at a random `lo` in 1..20. Instances by residue: W-1: 182,109, 0: 429,273, 1: 201,707; ends by an exact
  fit 88,570, by a partial last block 102,620, with no whole block at all 27,096.
* **Caps**: 0 (143,881 cap-ended instances), 1, a middle value, one under / at / one over the longest run a 130-byte
  window holds for that W, a bounded value no run reaches (100,000), unbounded. Cap-ended runs 296,989, 86,492 of them
  having advanced; caps that bind with room for another block 283,477; capped runs that ended before the cap 698,833.
  Counters: none 39,235 instances, kit-owned 571,003, caller-owned 284,554, **a cap with no counter named** 245,160
  (the kit's own counter; `count_start` is 0 there).
* **Per-position sets**: singletons, ranges (2..60 bytes), sparse (3..9 bytes), all full, mixed per position, one EMPTY
  position (first, last, middle: 272 sites), singletons with one FULL position. Neighbouring non-full sets always
  differ, so a term tested against another position's set fails.
* **Subjects failing at every position i < W**: for every window with a whole block, one subject per position whose set
  is not full, with the block that fails (rotating over the first, the last, the middle, the one at the cap) failing at
  exactly i; in three scenarios of four every other position holds (a kit that ignores that one term runs on), and
  blocks after it hold. First failing position, instances (all 32 positions): 166,653 at 0 down to 3,404 at 25 (every
  position well above its floor).
* The bytes of a partial last block HOLD, and bytes below `lo` are junk.

### 3. Reads

The driver's three layouts (guard page at `s + n` = B; guard page under `s + floor`, floor = lo; exact-size heap copy at
alignment 0..15) and a fourth, **tight**: when the oracle's run ends because `more` is false (the block at the cursor
is not wholly inside [0, n)), the guard page starts AT THE CURSOR, so a read of a byte of a partial last block, which
lies inside n, faults (`call_on` layout 0, `st_tight`). 114,021 instances ran tight, 0 faulted. Where the run ended by
the cap or a failing term the kit may read the block (and, `more` holding, the next), so there the guard stays at n.
`s` is NULL on alternate n == 0 calls (1,722 instances). A kit loop that does not end is stopped by a 10 s alarm and is a
failure (it also made one of my own W2 mutants a finding, below).

### 4. Hooks

* **Member hook**: absent (the kit's own test, `s[cursor + i]`: 385,980 instances), pcrec's own read that ignores the
  byte expression it is offered (`s[cursor + i]`, once per term with that term's id: 380,788), and the form that USES the
  byte expression the kit offers (so the kit must offer the byte at offset i: 373,184). All answer as the oracle.
* **`s` and `cursor`**: `cursor` spelled `cur`, `(cur)`, `g2c.pos`, `g2cv[0]`, `*g2cp` (888,640 / 62,414 / 61,491 /
  65,236 / 62,171 instances); `s` plain, `G2_EV(s)` (counted), `0 ? s : s` (ternary, unparenthesized-unsafe): 1,021,238 /
  59,762 / 58,952. Every non-identifier spelling is in the enforced class `hook-nonident`, and for the strided family a
  REFUSAL there is itself a failure (`STNONID rendered=356 refused=0`): the brief says the generic row parenthesizes.
* **`more`, `step`, `peek`**: five texts each, three of them outside the lexical classes (a top-level call, a top-level
  `||` that changes the meaning if pasted raw, a top-level comma, `*(s + c)`, `s[c] | 0`, a braced step).
* **W = 1**: neither `s` nor `cursor` required (both, either, neither unstated: 40 + 40 sites run), and the byte is `peek`
  (five `peek` texts x three member states).
* Also varied: four indents (`""`, 4 spaces, two tabs, 8 spaces), `plan_hint` stated on a third of the sites, `span_lo` = W
  on half the EXCLUDED sites (a true fact: the driver runs those only where a whole block fits), `floor` NULL / "0" /
  stated, both entry paths (`mf_emit` and `mf_define` + `mf_use`), the comment gate, `MF_D_RUN_OVERLAP` in a second pass.

### 5. Refusals

`st_refusals` (generator): 114 cases, 104 assert the field named in the refusal text, 8 cases are probes the header leaves
open (below), 22 controls prove the neighbouring shapes render. Each is asserted from the header's text.

| refused | field the text names |
|---|---|
| `reverse` 1 at W = 2, 3, 9, 32 | `reverse` |
| offsets not 0..W-1 or out of order (10 shapes x member absent / present, plus 3 at W = 32) | `pred` |
| an OPTIONAL term (W = 2, 3, 9, 32) | `pred` |
| a RUN term, a REF term (W = 2, 3, 32) | `pred` |
| nterm 33, 34, 255 (read before `term[32]`, in a buffer with room) | `pred` (the text: "nterm > MF_MAX_TERM") |
| a non-ADVANCE SKIP with nterm 2, 3, 32: SKIP/STMT/ASSIGN, SKIP/EXPR/RETURN, SKIP/FUNC/RETURN, with `result_decl` | `pred` (Q-G2-9 holds) |
| `s` unstated, `cursor` unstated, both, at W = 2, 3, 9, 32, member ABSENT and PRESENT | `s`, `cursor` |
| `peek` unstated at W = 1 and at W = 3, 9, 32 | `peek` |
| `more`, `step` unstated | `more`, `step` |
| `count_by_caller` 1 with `count` unstated | `count` |
| `MF_SITE_ABI` - 1 (7 at an 8 kit; never hard-coded) and + 1 | (refused; the text says "site abi 7, kit abi 8") |
| empty MISS on a strided ADVANCE, `count_by_caller` 2 | (refused) |

Controls that render: W = 32 with a member and without, W = 1 with `s` and `cursor` unstated (every combination, member
absent and present), a zero cap, a kit-owned counter from 2, a caller-owned counter, W = 1 reverse, the one-term
SKIP/ASSIGN, SKIP/EXPR/RETURN, SKIP/FUNC/RETURN.

### 6. Rows, K1, `G2_MAXT`

* `G2_MAXT` is 32 in `g2.h` (it was 8; the generator's `p * MF_MAX_TERM + t` table and term naming already followed
  the header). The cost is memory only (`g2_pred` is about 2 KB).
* **Rows / (b)**: no new row; `FLOOR_ROWS` unchanged. Check (g): a generator process of its own makes the strided sites
  alone (`--stride-only 1`, linked against `libpcrec_mftrace.a`, its REACH lines counted apart): **`arms/generic` chosen
  4,633 times, and nothing else**; floor 4,100. Check (b) therefore sees the generic row render strided sites in the
  tier sum too (261,326, up 36,910).
* **K1**: `g2_k1.c` checks `mf_ref_skip_blocks` against G2's own loop: every W, a cap as the caller's `min(n, K * w)`
  (K = none, 0, 1, 2, the run's length, one more), W = 1 against `mf_ref_skip_in_set`, subjects built from the sets,
  exact-size heap copies at every alignment: 34,620 checks, 0 failed (K1 total 411,620; floor `FLOOR_K1_SB` 31,000).

## Per-population floors (K35), measured less ~10%

The driver prints a `G2 stride census:` line of key=value pairs and `run_g2.sh` holds each to a literal floor
(`FLOOR_ST_*`): hard sites 710 (792), answer checks 1,560,000 (1,755,045), positive 700,000 (789,255), negative 860,000
(965,790), instances 1,010,000 (1,139,952), ends by cap / more / term 265,000 / 170,000 / 580,000, exact-fit /
partial-block / zero-block ends 79,000 / 91,000 / 24,000, windows at W-1 / 0 / 1 modulo W 162,000 / 380,000 / 179,000,
cap-ended / advanced / zero / binding-with-room / passed-by-the-run 265,000 / 77,000 / 128,000 / 252,000 / 620,000,
counters none / kit / caller / cap-without-counter 35,000 / 507,000 / 253,000 / 218,000, member absent / own /
byte_expr 343,000 / 338,000 / 331,000, least cursor spelling 55,000, counted / ternary `s` 53,000 / 52,000, tight
instances 101,000, n == 0 instances 1,530, EXCLUDED sites 350, W = 1 with `s` / cursor unstated 35 / 35, least-hit
failing position 3,000, least-covered width 69 sites / 93,000 instances; family floor `stride:700`; generator:
`STNONID rendered` 320 (356), refusal cases 100 (114), field-naming refusals 90 (104); the driver also prints
`G2 coverage MISSING` (and the runner's count-vs-lines check sees it) for any zero cell, including a first failing
position with no instance. Quick-tier numbers; the full tier has the same sites and more checks.

## Witnesses and sabotage

Beside W1 8-10 (above) and the older ones (unchanged):

* **W2 12-16** (generator `--mutate K`, strided sites only: `--stride-only 1`, non-strided and enforced-class sites are
  not generated): 12 / 13 / 14 force the last / first / middle term to ALWAYS hold (the member hook text and, for the
  kit's own test, the set and `table_ref`), 15 hands the kit a `more` that admits a block one byte short, 16 a cap one
  iteration too many. A site is mutated only where that is not an equivalent mutant (see Findings, "equivalent mutants"),
  and EVERY mutated site must be killed: **320 / 320, 391 / 391, 295 / 295, 416 / 416 (36,679 faults), 340 / 340**.
* **W3 (planted functions of one W = 3 site)**: `st-partial` reads a byte of the partial last block, inside n: 412
  faults, every one on a partial-block instance, and only the tight layout can see it; `st-over` reads `s[n]`: 2,370;
  `st-under` reads `s[lo - 1]`: 822; `st-clean`: 0 failed.

### Sabotage (scratch copies, never left in place)

All three ran `run_g2.sh --quick --no-rows --keep` in `.scratch/sab/m6{a,b,c}`, on the final tree plus one plant.

**(a) The reference's cap off by one** (`g2_ref_stride`: the loop stops when the counter EXCEEDS `span_hi`, one
iteration too many): exit 1, **348,821 failed checks**, `G2 family stride: ... failed-sites 390` of 792 (the capped ones
that the cap binds on); the floors trip too ("cap-ended runs 154,968 < 265,000", "cap 0 runs 69,360 < 128,000"). W2 16 reads
"caught on 0 of 340 sites", as it must: a kit given a cap one too many now agrees with the planted reference, so the two
defects cancel (the same cancellation g2m7 found for its W1 7 / sabotage c).

**(b) A driver without the tight layout** (`run_stride`: `int tight = -1;`, so the guard page never starts at the cursor):
exit 1, and not one ANSWER check fails (51,169,249 pass): the kit as delivered never reads a partial block, so nothing in an
answer can tell. Four reds, all from the harness's own bookkeeping: "W3 st-partial did not fault" (faults 0, was 412),
"W3 st-partial: no fault on an instance whose last block is partial" (partial-faults 0), "STRIDE tight-layout instances 0 <
floor 101,000" and the `G2 coverage MISSING: STRIDE cells` line. So a kit that read the partial block would be caught only
because the tight layout exists, and removing it is not silent. (The other two witnesses, `st-over` and `st-under`, are
unchanged, as they must be: they use the guard at n and the one under the floor.)

**(c) The caller-owned counter declared with the wrong start in the wrapper** (`wrap`: `g2_cnt = count_start + 1` under
`count_by_caller`): exit 1, **640,243 failed checks**, `G2 family stride: ... failed-sites 185` of 792 and 97 of the 1,143
`hook-nonident` sites, and nothing else: the failures are the sites that name a caller-owned counter (`site 1000003 ... cursor 1 count 2, want
1 / 1`: the count is wrong; where a cap binds the cursor is wrong too, 2 of the 150 failures the run reports), and the
answer checks of every other site are untouched. The floors trip on the lost positive and negative checks; W2 12-16 stay at
100% (they do not depend on the counter).

### ASan (outside the runner)

The runner's ASan+UBSan leg needs clang (absent here). The strided family alone was built with gcc
`-fsanitize=address,undefined -fno-sanitize-recover=undefined` (the generator's `--stride-only 1` batches, the driver, the
reference) and run `--quick`: **2,564,721 passed, 0 failed, no sanitizer report** (stderr empty); the exact-size heap layout
A is what lets ASan see an over-read of a partial last block that the guard layouts also catch. The same family at two other
seeds (7, 123456789; plain gcc): 0 failed.

## Findings (readings, not resolved by reading the kit)

* **No kit defect found**: every check is green on the kit as delivered, at the default seed and at two others
  (7 and 123456789, the strided family alone).
* **Q-G2M6-1. What byte expression does the kit offer a strided term's `member`?** The header says the kit's own test
  reads `s[cursor + i]` and that `member` is called once per term with that term's id, but not what `byte_expr` is for a
  strided term. G2 reads it as the byte at offset i (the natural W = 1 extension) in the `byte_expr` member style
  (373,184 instances, all pass), and ALSO keeps the style where pcrec's text ignores it. If pcrec's real text never uses
  it, the first style is stronger than the contract needs; if it ever does, the second is the contract.
* **Q-G2M6-2. `s` and `cursor` with the member hook present.** The header (`cursor`: "with `s`, REQUIRED on a strided
  ADVANCE (W > 1, Q-R10-4)") is unconditional; the brief names it under "member absent". G2 asserts the refusal in both
  states (the kit refuses both, naming the field).
* **Q-G2M6-3. `peek` at W > 1.** Q-G2-14 makes `peek` required; the strided paragraph says the byte "stays `peek`" only at
  W = 1. The kit refuses an unstated `peek` at W = 3, 9, 32 too, naming it ("`peek` (R1: used, not stated)"). G2 asserts
  that (it follows Q-G2-14), but if `peek` is truly unused at W > 1 the requirement forces pcrec to state a dead hook.
* **Q-G2M6-4. EXCLUDED on ADVANCE.** The header: "EXCLUDED renders the same, since nothing is tested". G2 reads EXCLUDED as
  a proven non-empty range, and so runs those sites only where a whole block fits at `lo` (`rem >= W`; 34,164 instances
  skipped, counted); `span_lo` = W is stated on half of them. The other reading (EXCLUDED only promises `lo < hi`) would
  allow `rem` below W and is not exercised.
* **Q-G2M6-5. A cap with no counter named.** The header says the kit "declares its own counter when only span_hi needs
  one"; where it starts is not said (`count_start` "either owner" suggests `count_start`). G2 states `count_start` 0 on
  those sites and never poisons it; with a named kit-owned counter the cap compares the COUNTER (start included) with
  `span_hi`, so a start of 1 or 3 leaves `span_hi - start` iterations. Q-R10-5 says `span_hi` "counts ITERATIONS"; the two
  agree only at start 0. G2 generates `span_hi >= count_start` and reads the cap as "counter >= span_hi stops"; kit-owned
  counters starting at 1 or 3 and caller-owned ones at 0 or 2 are generated (counter kinds 2 and 3), and the kit agrees.
* **Q-G2M6-6. Cases the header leaves open (reported, `INFO probe stride`, never judged)**: the whole predicate OPTIONAL and
  `end_back` 1 on a strided site both RENDER at W = 2, 3, 9, 32. Nothing says whether they should.
* **Q-G2M6-7. Reads after a failing term or the cap.** The contract reads [cursor, cursor + W) "only while `more` holds",
  which permits reading the failing block whole and, `more` holding, the next block; G2's guard stays at B there, so a kit
  that reads one block ahead passes. Only a `more`-stopped run is held to "no read at or after the cursor".
* **Q-G2M6-8. nterm > MF_MAX_TERM names `pred`** (the text: "nterm > MF_MAX_TERM"); the brief lists `pred` only for the
  offsets, OPTIONAL and non-SET cases. G2 accepts `pred` or `nterm`.
* **Q-G2M6-9. `MF_SITE_ABI` mismatch names no field**: "site abi 7, kit abi 8"; G2 asserts the refusal only.
* **Equivalent mutants (why W2 12-16 count only some sites).** A mutant that nothing can tell from the original must not be
  counted as a survivor. Found by running them: (1) an EMPTY set anywhere makes every block fail, so no cursor ever moves and
  no term can be told from another (the first W2 13 run showed 86 survivors, almost all this); (2) a term whose set is full
  cannot be made "more true"; (3) a cap that stops the loop at 0 iterations hides every term; (4) the read of an EMPTY
  set's member is `((void)(s[c]), 0)`, dead code the compiler removes, so W2 15 (`more` one byte short) is invisible there;
  (5) for an EXCLUDED site G2 never runs a window without a whole block, so W2 15 on a W = 1 site with a cap of 1 (one
  iteration, then the cap) is unobservable; (6) `n - cursor >= W-1`, with the cursor past n, wraps to true forever: the
  mutant never ends. That last one hung my first W2 15 run for minutes and is why the driver now has the 10 s alarm; the
  mutants of that spelling are excluded. A second finding of the same run: the first scenario plan failed the block at
  position i with the positions after it random, which a kit that ignores one middle term passes with probability
  2^-(W-1-i); three scenarios in four now fail EXACTLY one term.

## Files changed in the cell

* `memfn/tests/g2/g2.h`: `G2_MAXT` 32; `G2_FAM_STRIDE` ("stride"); the trailing `st_*` fields of `g2_site`.
* `memfn/tests/g2/g2_ref.h` / `g2_ref.c`: `g2_ref_stride`, the strided branch of `consistent`, W1 defects 8-10.
* `memfn/tests/g2/g2_gen.c`: the strided hooks and wrapper, `st_*` (sets, caps, `gen_fam_stride`, `st_refusals`), the member
  hook's own-read style, W2 12-16 (`st_mut_term` / `st_mut15` / `st_mut16` / `st_is_mutated`), `--stride-only`, the poison
  differential's two exceptions (`cursor` and `count_start`), the HOOK class for non-identifier cursors, the registry tail,
  the `STSITES` / `STREFUSE` / `STNONID` lines.
* `memfn/tests/g2/g2_driver.c`: `run_stride` and its subjects, the tight layout and the NULL-`s` option in `call_on`, the
  alarm, the W3 `st-*` functions, the census lines and the `G2 stride census:` machine line.
* `memfn/tests/g2/g2_k1.c`: `mf_ref_skip_blocks`.
* `memfn/tests/run_g2.sh`: the floors, the generator-population and per-compiler checks, W1 1-10, W2 1-16 (with the judge for
  12-16), the W3 judge for `st-*`, the STRIDE-only generator process and check (g), the K1 line.
* `memfn/tests/CLAUDE.md` (a new section, the file list), this report.

## Disclosure

Seen at spawn, not as inputs: the session-root `CLAUDE.md` (the pcrec working agreement: scope mandate, build and test
section, the situation index) together with the per-directory `CLAUDE.md` text for `docs/`, `docs/dev/` and `docs/dev/lanes/`
(whose long lane-report index, including this kit's earlier lane reports' summaries, arrived in context), the manager's memory
index (`MEMORY.md`), the git status snapshot (branch `main`, clean, five recent commit subjects), the environment note, the
skill and agent lists and one MCP server's instructions. None was a licence to read further. Read by the brief's leave:
`docs/dev/lanes/BOILERPLATE.md`. Read in the cell: `memfn/include/memfn.h` (whole), `memfn/tests/CLAUDE.md`,
`memfn/tests/G2M7_REPORT.md` (the house style), the cell's G2 files and `run_g2.sh`, and `docs/design/memfn/integration.md`
by `grep` for VMSTRIDE / Q-R10 / strided / MF_MAX_TERM (match lines only) and section 15.9 whole (the kit's as-built
description of the site; it says the render is R4h's frozen target with one `(member)` per term). Not read: `memfn/src/`,
`src/`, `tests/`, git history (the cell's `.git` is empty), `memfn/docs/`, the pins under `tests/memfn/pins/`, the earlier lanes'
files in `.scratch/`. Output of the opaque kit reached me as it came: its refusal texts (printed in `gen_results.txt`), the
MFTRACE REACH lines, and the rendered text of a few strided sites in the generated batches (to see that the wrapper compiled).

Process notes, for the manager: (1) my first manual `gcc` invocations (before I exported `TMPDIR`) let gcc put its transient
temp files in the default `/tmp`, which the scope mandate forbids; they were deleted by gcc itself. Every runner run, every
later compile and every sabotage run used `TMPDIR` under the cell. (2) `scripts/safekill` is not in the cell, so I stopped
my own stray processes (a hung W2 15 mutant, then a superseded sabotage chain) with plain `kill` on PIDs I had started; I
used `pgrep -a` once without `-f` and never `pkill`. (3) I edited `run_g2.sh` once while a run of it was in progress and
restarted that run at once, discarding it (bash reads a script incrementally).

## Charter checklist

| # | item | artifact |
|---|---|---|
| 1 | the strided ADVANCE oracle: STMT / SKIP / ADVANCE over W in 1..MF_MAX_TERM REQUIRED SET terms, term i at offset i; final cursor; the counter j times, kit- or caller-owned; W = 1 | `g2_ref.c` `g2_ref_stride`, `consistent`; wrapper `wrap` (the caller's counter); W1 8-10; K1 `mf_ref_skip_blocks` |
| 2 | the generated space: the nine W; B - c0 at every multiple of W +- 1; caps 0, 1, around the run, unbounded; set kinds incl. EMPTY at one position; subjects failing at every position | `gen_fam_stride`, `st_sets`, `st_cap`; `run_stride` / `st_window`; the `G2 stride` census lines and floors |
| 3 | reads: only [cursor, cursor + W) per iteration, only while `more`; guard pages at B; `s` NULL at B = 0 | the three layouts plus the TIGHT layout (`st_tight`), `st_nullok`; W3 `st-partial` / `st-over` / `st-under`; sabotage (b) |
| 4 | hooks: member present (once per term) and absent (the kit's own `s[cursor + i]`), `s` / `cursor` required at W > 1, W = 1 `peek`, non-identifier `s` / `cursor` | `st_mem` styles, `ST_CUR`, `hook_style`, the HOOK class with refusal = failure; refusal rows |
| 5 | refusals, each naming its field | `st_refusals` (114 cases, 104 field-asserted) |
| 6 | rows / (b) generic row sees strided sites; FLOOR_ROWS unchanged; `G2_MAXT`; K1 | check (g), `--stride-only 1`; `FLOOR_ROWS` 15; `G2_MAXT` 32; `g2_k1.c` |
| 7 | sabotage rows a / b / c, W1 / W2 coverage | above; W1 8-10, W2 12-16, W3 `st-*` |

Open questions: Q-G2M6-1 .. Q-G2M6-9 above.
