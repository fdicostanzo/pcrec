# 2026-10-16 r5 — two-critic panel on docs/design/findall_iter.md revision 2 ([FINDALL-NEXT], lane iterrev)

Subject: `docs/design/findall_iter.md` revision 2 (the iterator as compound controllers,
internal batching in `_in` memory, binding at init with setters, F-1's residual twins, S
derived from declared words; Q-I1..Q-I4). Design text only. Reviewed read-only against the
main tree.

Critics: **itcrit2** (sonnet; checks, emitter reality, staleness) and **itcrit1** (opus;
semantics and caller contract), both with the unlock lens. Compiled by the main session from
the two reports, as written.

MANAGER VERDICT (2026-10-16): every finding (IC1-IC9, F12, F13, the sabotage-id and
NEW-DATASET notes, IT1-IT15) is ACCEPTED, except where a ruling overrides it:
- **IT4 is REJECTED by ruling.** D165 addendum 3 (Frank): no per-call owner check; misuse
  across artifacts is UNDEFINED. `owner`, its compare, the setter store IT4 proposed, S931
  and the foreign-owner arm are deleted. IT9 dissolves with the field.
- **IT3 + IC3 are accepted with the manager's fix:** the batch region is NOT added to
  `<prefix>_buffers`; it is taken through the iterator's own setter.
- **Q-I1 stays open with Frank;** IT6 is discharged by making §3.4a and §0.3 conditional.

Revision 3 (lane `iterrev3`) discharges them; the map is the section "Disposition and
revision 3 discharge" at the end.

## Critic itcrit2 (sonnet): checks, emitter reality, staleness

Read-only review of `docs/design/findall_iter.md` revision 2 (lane/iterrev, merged to main), `iterrev_report.md` and `compound_entries.md` rev 3, against `src/gen/` and a grep of `docs/`. Nothing was run.

- **IC1 · HIGH · The F-1 relocation check and its plant cover one of three twins.**
  - P-d plants only the compound controller calling `_next_pos`. `_valid_upto` and `_var_valid` have no plant (sibling-of-a-family gap).
  - The floor is "97 compound artifacts", which does not include `-futf-check` or var-bearing artifacts. Today `_valid_upto` is called at `src/gen/emit_dfa.c:822` and `_var_valid` at `src/gen/emit_vm.c:12540`, outside the compound emitter.
  - Whether the check can fail depends on the `-fPIC` build. Without PIC, gcc may inline the exported leaf and leave no relocation, so the check passes whether or not the twin exists.
  - Fix: add one plant and one per-leaf population floor for each twin. Name the `-fPIC` build and the `make` target that runs the check.

- **IC2 · HIGH · The S machinery has no detector that can fail at I1.**
  - S936, S937 and check 2 are declared UNREACHED (§1.3, §6.8).
  - Check 1 compares the literal 64 against a max computed from declarations. The declarations are `pair-hits` (I3), `kit-find` (I2, from `lane/memfn-r17` `c90d65e53`, unmerged) and `reseed-hint` (FILED). One lane writes both sides, so it only fails if someone forgets to edit one. That is the learnings §3 shared-source failure.
  - The only independent control is `sizeof(<p>__iter_state)`, which arrives at I2. Until then every artifact's `rx_iter` carries 64 B for rows with no emitter.
  - §8a's home for the declarations, the `entry_rows[]` STATE column, does not exist yet (`compound_entries.md` §4.1 says `entry_rows[]` "does not exist" [r3 LK-1]), so check 1 reads a table that may be the debt fallback.
  - Fix: state plainly that S=64 is unverified until I2. Either defer S to I2, or add a real I1 control, such as a synthetic row forced into one test artifact.

- **IC3 · HIGH · The batch region moves artifact bytes beyond what §6.1 lists.** All of this is conditional on batching shipping.
  - `<prefix>_buffers` is emitted by `emit_buffers_surface` (`src/gen/emit_dfa.c:2546-2602`). It is written into the header at `:3513` and into the `.c` at `:13757`, on every artifact including DFA. The new fields and the rewritten "two regions" comment text (`:2578-2593`) therefore move every header. §6.1 does list the header size as a mover.
  - `src/gen/emit_vm.c:13826` emits `static const <p>_buffers <p>_no_buffers = { (void*)0, 0, (void*)0, 0 };` positionally. After the change it triggers `-Wmissing-field-initializers` in every frameless VM artifact's generated code. F11 and §10 Q-I3 name only the spec example and in-tree callers, so this emitter site is missed.
  - `<PREFIX>_BATCH_ENTRY_SIZE` sits beside macros written with `pcrec_sb_stampf` (`:2556-2560`), i.e. stamps. §8a calls it "a header macro" and §6.3 lists only `ITER_RETRY`. The stamp inventory, registry and spec §10.4's "five macros" count would all move.
  - The I1 contents, and so its abi-reader list, depend on a noise-floor outcome that is not known at design time. If batching is filed as I4, the full abi ritual runs twice.
  - Fix: add the three sites to §6.1. Decide batching before I1 so the abi event is one event.

- **IC4 · MED · "One combinator emitter serves both" is not true in the source.**
  - `src/gen/emit_compound.c:115` is `emit_first_nonzero_search`, a split-only emitter. It has no `guard` or `meter` column, and `grep` finds no `iterate`, `CompComb` or `entry_rows` in `src/`.
  - §2.1 and §8.2 say the convergence is designed. That is a claim about E0, which has not landed.
  - Fix: mark the "one emitter" sentences as dependent on E0.

- **IC5 · MED · The meter column has a one-sided detector.**
  - P-b and P-c plant the retry side. Nothing plants the `shared` cell on split flipping to `per-operand`. That change would move an existing give-up (D163 add. 6 Q1).
  - The doc does not say which engine the constructed budget cells run on. A DFA retry (`dfa-root`) may meter differently from a VM retry.
  - Fix: add a mirror plant on split, and state the engine for P-b and P-c.

- **IC6 · MED · Several detectors are not in default `make test`.**
  - P-h and S938 need ASan, and `make asan` is opt-in (CLAUDE.md).
  - The relocation check needs `objdump -dr` on a PIC build.
  - The doc never says which target runs them. K35: a detector that is not in `make test` has no population on the default run.
  - Fix: name the target for each, or move them into `make test`.

- **IC7 · MED · The batching-identity oracle for give-up cells is K=1 `next` (§6.7), which shares STEP with the subject.**
  - §7.2 admits this, but P-a and P-b rest on it alone. A bug common to STEP at K=1 and in a fill is invisible.
  - Fix: add libpcre2 with matching limits, or accept explicitly that give-up identity is regression-only.

- **IC8 · MED · Part names and stage ids drift against `compound_entries.md`.**
  - `compound_entries.md:772-774` lists `__adv` as "I3's static twin" and names `__step` as the part. Revision 2 puts the twins in I1 (§2.4) and renames the parts to `__fill`, `__deliver`, `__enter` and a STEP body.
  - Both documents use "I3" for different things: pair-hits here (§6.9), the wrapper step there (`compound_entries.md` I3).
  - `__step` and `__find` were rated R2. Under the fill loop the caller of `__find` is `__fill`, but `compound_entries.md` lists no `__fill` row.

- **IC9 · LOW · F9 is partly a non-finding.** `docs/spec/match_api.md:3108` uses `rx_buffers` because `rx` is the example prefix. The shipped type is per-prefix, as F9 says, but D165's `rx_buffers` was probably that same example prefix and not a different type.

### F12: stale HELD notes (`compound_entries.md`, all unedited)

- `:54` F4 row ("batch-fill R3 witness HELD with Q2").
- `:192` (`_next_n` held).
- `:440` says the fill is "not designed in `findall_iter.md`", which is now false.
- `:664` ("Only the internal batch fill (R3, HELD) would separate them").
- `:776` and `:781`.
- `:757` ("two dial rows ... disjoint subjects") should be re-read against the new `-1` witness.

### F13: stale S = 48 / 56 cites

- Revision 2's F13 says `compound_entries.md` cites 48/56. Grep finds none in rev 3, so that part of F13 is wrong. Remove it.
- Stale in `docs/design/CLAUDE.md:3222` (the `findall_iter.md` index entry still describes revision 1: S = 56, `FRESH_AT`, "one store"). The branch added a line but did not fix this one.
- Stale in `docs/dev/lanes/CLAUDE.md:3943` and `iterdes_report.md:18,103` (historical, but unmarked).
- `docs/dev/decisions.md:9707` (Q-R17P-10, S = 48) is superseded by A10 at `:9718`. It is historical and fine if annotated.
- `r17b_prime.md` on `lane/memfn-r17` carries 48/56 at lines 97, 126, 1115-1120, 1162-1164, 1422 and 1453. The kit manager has to fix those.
- `plan.md`, `wake.md` and `testing.md` have no cites.

### Sabotage ids

S923-S942 are unallocated (highest file is S910; no other doc uses them), but `compound_entries.md` uses S999-S1008 and `wcrev3` uses S991-S998. The manager should allocate P-a..P-h and S923-S942 before the next lane lands, to avoid a renumber.

### NEW-DATASET

Declared UNREACHED rows (S936/S937, check 2) need a tracked trigger, "I2 first kit row". Make it a plan.md row so it cannot silently stay vacuous.

### UNLOCKS with triggers

- A generic "twin-forwarding" check (IC1) would also cover the §2.4 wrapper edges once `compound_entries.md` I3 lands.
- A per-region `batch` lifetime assertion (debug `-DPCREC_ITER_CHECK`, trigger: first user report of two iterators sharing a batch) would turn the copy rule into a detectable fault.

## Critic itcrit1 (opus): semantics and caller contract

- **IT1 MAJOR.** The bind step contradicts itself about the option bits. §1.2 has bind store `BOUND`, and the fast path needs `hdr == PCREC_ITER_BOUND` exactly. Storing that clears OPT_AT/VARS/IN. Yet §2.3's fill reads "it has OPT_IN", and `vars`/`bufs` are "read only if OPT_VARS/OPT_IN". Init never writes those fields, so after bind the fill reads whatever was in memory. Evidence: findall_iter.md (lane/iterrev) §1.1 field comments at lines 126/128, §1.2 "then stores BOUND", §2.3 fill line 421. Fix: bind writes `bufs = NULL` and `vars = NULL, nvars = 0` when their bit is clear, plus `nbatch`→K into a FIXED field (about 2-3 stores). The alternative is to keep the bits and mask them out of the fused compare.
- **IT2 MAJOR.** A drained batch with a pending code re-runs STEP. The emitted `_next` (§2.1) checks `bhead < bcount` and then calls `__fill`. Nothing checks `rc_next != 1`, so the call after the last buffered match runs the failed (or exhausted) search again with a fresh meter before ending. The answer is the same because the code is deterministic, but it costs a full budgeted search that K=1 never pays, and it breaks the deliver comment "the NEXT call ends". Fix: `__fill` begins with `if (it->rc_next != 1) end(rc_next)`. P-a does not catch this. Add a counted-work cell.
- **IT3 MAJOR (NEW-DATASET home, Q-I3).** Adding `batch`/`nbatch` to `<prefix>_buffers` is a silent hazard, not only a `-Wextra` warning. Existing callers fill the descriptor member by member and would leave the new fields indeterminate with no warning: pcrec-bench `testees/pcrec/shim.c:1728,1759` and `docs/dev/optloop/artrev/A09/tools/budget_main.c:17`. F11 covers only the positional sites (`match_api.md:3108`, `docs/dev/lanes/f3search_driver.c:117`). Fix: leave the descriptor alone. Take the region as binder arguments, `<p>_iter_buffers(&it, &bufs, batch, nbatch)` or a separate `rx_iter_batch(&it, void *, size_t)`. Then F11 goes away, `_in` callers are untouched, and the batch lifetime rule attaches to the iterator, which is the object it governs.
- **IT4 MAJOR.** The owner check does not cover buffers. If `<A>_iter_buffers(&it, &a_bufs)` is followed by `<B>_next(&it, …)`, the iterator is FRESH, B records owner = B and runs on A's frames with B's frame size. That is an overrun, not a refusal. Q-I2's "typed binder keeps the type check" holds only at the setter call. Evidence: §1.2 (the owner is written at the first call) and Q-I2. Fix: the typed setter also stores `owner = &<A>_info`, and bind refuses (`PCREC_ERR_ITER`) a pre-set owner that is not its own. Add a sabotage row with a foreign-buffers cell.
- **IT5 MAJOR.** D165 item 1 makes "subject immutable while iterating" part of the design, but no spec hunk in §6.2 states it, and §1.2 only says a mismatch is "impossible by construction". §3.4a's identity, the kit's cache (§4.1) and validate-once (§3.6) all depend on it. With batching, a caller that edits the subject between calls sees different matches; with today's loop that is legal. A strtok-style in-place tokenizer is one example. Fix: §3.8 states that `s[0,n)`, the `vars` contents, the bound descriptor and the batch region must not change while the iterator is BOUND, and that a violation is undefined.
- **IT6 MAJOR.** §3.4a's "identical by construction" rests on Q-I1's leaning (one meter per logical search). Under D163 add. 6 Q1 read literally (decisions.md:9591), the fill and the retry change where the iterator gives up, and §3.4a is false. P-b and P-c then test against an unruled expectation. Fix: make §3.4a and §0.3 explicitly conditional on Q-I1.
- **IT7 MINOR.** §1.3 check 1 asserts S **equal to** the computed max. The sizing policy and U14 keep 64 B after K5 retires, which makes the max 48, so the build fails at retirement. Fix: assert `S >= max` and have the census report the headroom, or keep a retired row declared with status `retired`, counted until the shrink event.
- **IT8 MINOR.** A setter called on an ENDED iterator sets `hdr = 0`. The next call then overwrites `rc` (0 or a give-up code) with `PCREC_ERR_ITER`, which loses the sticky reason that P-g protects. Fix: a setter poisons only a non-ENDED header.
- **IT9 MINOR.** The owner compare costs a third load under `-fPIC`. Measured with gcc 15.2 -O2 -fPIC: `movq p_info@GOTPCREL(%rip)`. §5.1 counts "two L1 loads", and the parity gate's R2 regime pays the third. Fix: compare against a hidden-visibility static owner tag.
- **IT10 MINOR.** At K=1 with NULL `caps`, §2.1 says STEP writes into "the step's own local", but the local's width is not stated. Batched entries always hold `NCAPS` pairs. If the local is one pair, or STEP skips capture extraction, then K=1-NULL and batched runs do different work, which can mean different metered work. Fix: state that STEP's destination is always `NCAPS` pairs, or that capture extraction is not metered.
- **IT11 MINOR.** Mid-batch, `it.lo` runs up to `nbatch−1` searches ahead. §3.4's FRAMES-recovery recipe ("a fresh iterator at the failing `lo`") uses `lo` as if it were contract. Fix: the spec says `lo` is defined only after the iterator ends (the failing search's position) and unspecified before that, or offers an accessor.
- **IT12 MINOR.** The bind checks have no stated order. §1.2 lists guard, UTF, vars, but does not tie them to `_search`'s prologue order (match_api.md §3.2¶2, "boundary guard first"). A subject that is both mid-character and ill-formed must refuse with the same code as the loop's first call. Fix: cite that rule, with one emitter for both entries.
- **IT13 MINOR (SIBLING).** `reports_empty` is defined as a list, "nullable OR `\K`". Fix: define it as minimum REPORTED width = 0, computed by one analysis, so a construct like `(*ACCEPT)` (mod_verbs.c:141, unbuilt) joins without a new term. Trigger: any module that changes the reported span.
- **IT14 MINOR (UNLOCK).** pcre2demo's failed-retry advance steps over a whole CRLF under CRLF/ANY/ANYCRLF newlines. pcrec refuses newline verbs today (mod_verbs.c:175-176; `DEF_NEWLINE_CONV` is reserved, registry.md:197), so nothing is wrong now. File a row with trigger "`DEF_NEWLINE_CONV` gains a producer": the retry-fail arm becomes newline-aware and the non-empty advance stays unchanged.
- **IT15 MINOR.** The DFA notempty root counts against the caps (§3.3). At I1 a `reports_empty` DFA pattern near a cap can become refused or switch engine, and a caller can see that. Fix: §6.7's mover census also counts refusal-set and engine-stamp changes, not just text.
- **S derivation (no finding).** 40+16+8=64 B follows A10's per-word rule, and keeping K5 is consistent with A10. The only defect is check 1's equality (IT7).
- **Global-iteration equivalence (no finding).** Empty match at n, the anchored retry, the `\K` reported start, the UTF continuation advance and validate-once's monotone range all match pcre2demo as written.
- **Init spelling and fused compare, probed clean (no finding).** `rx_iter_init` plus setters compile with no warnings at gcc 15.2 -O2 -Wall -Wextra and -fanalyzer. Valgrind reports nothing for the fused compare reading the never-written `owner` on a FRESH iterator. Hand C was compiled in the session scratchpad.
