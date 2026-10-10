# slbuild — [START-LANDING] SL1-SL3 built

Lane slbuild, 2026-10-10, opus (engine tier). Branch `lane/slbuild` off main
`06d19c67` (abi 73, [OPT-REVEND] L1 + L2 with stage 2 merged). Design:
`docs/design/start_landing.md` revision 2 (§R2, §2, §3, §7, §9); rulings D156
addenda 3 and 4 (Q1-Q4), Q5 resolved.

## 0. STEP 0 — the edit set re-derived, and the design reconciled with main

The design was written at `efc58146` (abi 71), before locate × finish L0
(`c85a1aac`) and [OPT-REVEND] L1 + L2 with stage 2 (abi 73). Its edit set is
re-derived at `06d19c67` as `studies/start_landing/edit_set_main.tsv` (the
design's `edit_set.tsv` is left as written, at its pin). Every `line` entry
occurs exactly once in its file at this pin (counted).

**The census** (`docs/design/start_table/call_graph.py .` at this pin, then
`sabotage_anchors.py . CG studies/start_landing/edit_set_main.tsv --final
after-SL3 --edit-names`): 639 row files, 660 sites, 137 in the family.
- **RE-AIM at SL2 (11):** S07, S221 (`unanch_scan`: pinned's success site and
  the dispatch move into the one success-site emitter), S223 (the
  `start_pinned_assert_routing` line becomes the per-action assertion), S693
  (the abi literal), and S758, S759, S760, S764, S765, S766, S780 (rows inside
  `emit_rev_end`, a `def` this lane edits: the census classes every anchor in a
  rewritten definition as a re-aim; the ones whose anchor TEXT does not move
  re-run unchanged, recorded per row at SL2).
- **RE-RUN at SL2 (28 sites):** the `cand_rows[]` rows (S283, S284, S462, S473,
  S594-S600, S610, S738, S741, S745, S768, S770-S772, S777), the four
  `pf_emit_first_*` rows (S481-S484, the NEXT closers), S566 and S572; 104 sites
  once after SL3.
- The 3 unresolved `src/` sites (S176, S571, S640) are pre-existing and outside
  the family, as at L0 (the tool's exit 2 is theirs).

**What no longer holds as written, and the site it moved to (no design
change):**
1. **SL3's hand is already built** (revbuild L2, `[r2-landing]`): RECOVER asks
   carry `CandSel.hand`; `CAND_HAND_EXISTS` (the composite) and
   `CAND_HAND_WINDOW` (the `rev-end` walk) exist as the design's masks; rows take
   per route (`pinned` EXISTS only, `reverse-pass` both); `dfa_search_start_of`
   reads the PATH's cell (the LOCATE row's `u.locate.recover`); the trace build
   aborts on a hand-less ask (`recover-no-hand`). What is left for SL3 is the
   per-HAND totality check on RECOVER (the self-check has it for FINISH only)
   and the two sabotage rows the design declared unreached until L2.2 (rows 8
   and 13), now reachable. The two new rows' `take` cells (EXISTS only) must
   land WITH the rows in SL2: a row without them would be selected by
   `rev-end`'s WINDOW ask.
2. **`recover_on_path` exists**: it is `cand_recover_asked` (L0 re-spelled
   `pinned`'s P4 as the path's read). The two new predicates call it; no new
   function.
3. **`dfa_search_is_pinned` has two callers, not five** (`emit_unanchored`,
   the orientation block), plus `emit_rev_end`'s two assertions on
   `u.recover.pinned`. R's membership is already L0's member fold
   (`cand_path_members`, `CAND_MR`), and the machine stamps already fold over
   `dfa_member_machines`, so a row whose `.needs` omit R drops it with no stamp
   edit, as designed.
4. **The empty engine stamps `attempt-start`, not `reverse-pass`** (L2.1's
   generated rule): an empty body's path asks no RECOVER, so SL-C1's W0/L0′ is
   structural on the path, and §7.3 §1's witness `a\bb` reads `attempt-start`.
5. **End-pinned fixed-width patterns now take `rev-end`** (WINDOW hand), so
   neither new row applies to them, as §3.3 designed; the design's mover counts
   (bench 155+155, corpus 1,750/1,751) are re-measured at SL2 against this pin.
   The `rev-end` relocate (a tie with no anchored machine) re-enters the
   composite's scan; it runs the PATH's RECOVER row (the WINDOW ask's,
   `reverse-pass`), whose reverse machine the walk already needs.
6. **The `search-start` listing has a fifth row** (`attempt-start`, L2.1's
   absence row). The new rows list 2 and 3, `reverse-pass` 4.
7. **The abi event is 73 -> 74.**

No assumption fails in a way that changes design; the build proceeds.

## 1. SL1 — the facts (no artifact mover)

**Built.** `src/facts/kset.c`: the frontier walk is ONE iterator
(`wstart`/`wclose`/`wadvance`); `wclose` is one closure in two phases (the
exact closure with assertions stopped at, then the passing one), so it also
reports `accept_free` and `asrt`. Two E3 core facts in `facts.def`, owner
`src/facts/kset.c`: `width` (`pcrec_width_walk`, `[bmin, bmax]` over the union
frontier, assertions passed) and `land_char` (`pcrec_land_char`, Λ: per byte,
exact, mid-character read off `PcrecEnc.start_cls`, a re-met mid-character
frontier a cycle via a memo instead of a depth constant, Λ.2 asserted as
K50-NULLGATE). `--emit-facts` lists them (`one-char` / `one-char+guard` /
`declined` with `decline:nullable|assert-at-start|dead-start|alive-not-accept|
assert-after`; `[bmin,bmax]` / `[bmin,inf)`). Spec: `facts_listing.md`
§4.1.2¶7a/¶7b and §4.1.3¶3.

**Checks.**
- (a) Census agreement (`studies/start_landing/agree_sl1.sh`, the design's
  probe functions re-anchored into a scratch copy of HEAD, the same compile):
  bench 734 compiles, 545 agree, 0 disagree, 6 `capped` (the probe's 4096-byte
  width cap: `cls-upto-8192/16384`, `cls-lazy-16384`, where the build reads
  `[0,8192]`/`[0,16384]`); corpus 9,420 compiles, 5,909 agree, 0 disagree, 6
  capped. Summaries in `studies/start_landing/results/slbuild/`.
- (b) The hand-witness table, `tests/codegen/run_facts_checks.sh` §9
  `[facts-sl1]`: 15 literal witnesses written from the definitions (the
  design's 12 plus `a*`, `a|bc`, utf8 `\w+`), REACH over the four reachable
  declines; 9/0. Failing direction: a plant reading an assertion after the
  first character as an accept turns it red on `\w+\b` and `a\bb`.
- Zero-mover gate: `scripts/emit_sweep.py --ref 06d19c67` — c-default,
  c-vm, emit-ir-vm, emit-ir-auto (four arms), stderr, composition, dumps: 0
  movers, 0 asymmetric. The facts stream moves on all 5,125 reached compiles,
  by the two new rows (the listing prints every fact). `make strict` clean.

**Deviation.** The design's hand table wrote `a\bb`'s Λ as "(empty engine)";
§2.4's definition gives `decline:assert-after` (an assertion before the
accept), and the table carries that. `dead-start` has no witness (a start
closure with no consumer, accept or assertion is not a machine this parser
builds); it is the safe answer for one.

**Scope note.** One backup copy of `src/facts/kset.c` was written to `/tmp`
for a failing-direction plant and removed at once; every other scratch file is
under this worktree's `build/scratch/`.

## 2. SL2 — the rows (bfe30c75, then 5b3dd37b and the FILEPIN self-pin; abi 73 -> 74)

**Built** (design rev 2 §7.1 SL2; `src/gen/CLAUDE.md`'s new section).
- RECOVER gets two rows between `pinned` and `reverse-pass`, in this order:
  `end-minus-width` (deny `-fno-start-width`, bit 53), then `landing` (deny
  `-fno-start-landing`, bit 54; `.needs` reads NEXT).
  - The payload is an ACTION, `u.recover.act`, read through
    `dfa_search_act`. It replaces `dfa_search_is_pinned`.
  - `recover_on_path` is L0's `cand_recover_asked`, read by all three new
    predicates.
  - Only `reverse-pass` needs the reverse machine (`CAND_MR`), so L0's
    member fold removes it from every other artifact.
- The new rows take only `EXISTS`. `rev-end`'s `WINDOW` ask selects neither
  of them.
- The landing record lives in `pf_close`, the one closer of the NEXT block,
  and all eight `pf_emit_*` closers call it.
- The tolerant-utf8 guard is a POST-LOOP skip (Q2), via
  `pcrec_dfa_landing_guard`:
  - It does one decode, predicted not taken, and steps forward only on
    failure.
  - Nothing of it is inside the scan loop.
  - It is omitted under `-futf-check`.
  - The DECODE mask bit is ORed before the prologue in both emitters.
- BOUNDARY vs DECODABLE START are named apart in the code. A landing is
  always a candidate the skip handed the machine at a character BOUNDARY
  (P0). The guard asks a different question: does the character there
  DECODE.
- There is ONE success-site emitter, `emit_search_success`, carrying
  `caps[0]`, the K78 fill and `return 1`. It serves pinned, end-minus-width,
  landing, the reverse pass and the `rev-end` report.
- The orientation block's step 3 is now per action.
- The ABI block's ESSENTIAL `search_form` comment names the two new values.
- `lib/pcrec.h` and `axes.def` carry the two bits, masked out of
  `rx_info.flags`. **The bit numbers 53/54 are this lane's pick and need
  confirming.**

**Movers.** `studies/start_landing/movers_sl2.py` compares the parent (the SL1
build, 0 emitted movers against main) with the child. Every compile is checked
against the census's predicted row.

| population | compiles | -> end-minus-width | -> landing | mispredict |
|---|---|---|---|---|
| bench | 734 | 210 | 88 | 0 |
| corpus (default + nocaps) | 9,420 | 2,592 | 833 | 1 |

The design predicted 310 bench movers. The difference is the 12 end-pinned
fixed-width rows that take `rev-end` since L2 (STEP 0 finding 5).

The one corpus mispredict is a **FIT mover**: `(\p{Xwd})` under utf8. With
landing it drops R, so its 359 KB hybrid fits WITH its prefilter, where the
size ladder used to drop the prefilter (design §7 attack (c)). Four more FIT
movers turned up in `tests/resource`:
- `\p{L}+` fits with its anchored machine (894,606 B);
- `(a|b){1,30000}` `-fno-scan-edge` fits at 672,758 B;
- `\p{L}` and `[^\p{C}\p{M}\p{P}]` no longer reach their anchored-drop and
  premul-drop rungs.

Every rung witness is re-aimed the same way: it now passes
`-fno-start-landing` (masked, answer-neutral) and still measures its rung.
In addition, the PF-DROP rung got a corpus witness that takes no landing,
`(\p{Xwd})x`, with libpcre2 10.46 answers. That witness is S420's reach probe
and harness target.

**Answers, checked.** `tests/codegen/run_start_landing.sh` (8/0, `make
test-start-landing`, in TEST_SECTIONS):
- §1: 20 witness rows by deny arm.
- §2: stamp == body == mirror over 4,648 corpus patterns.
- §4: deny identity over 5,684 declined artifacts. The product arm puts all
  1,618 new-row artifacts back on the reverse pass.
- §3 floors (measured landing 211, end-minus-width 1,407, product reach
  1,618).
- §5: 15 patterns at every startpos of 24 subjects with fixed ill-formed
  tokens. Verdict and `caps[0]` from search/match/match_caps are identical to
  the triple-deny build's reverse pass.
- §H: the hostile cell runs inside its 10 s bound.

`tests/utf8/landing_illformed.rxt` holds 140 cells generated from libpcre2
10.46 MATCH_INVALID_UTF. It is green by default and under both deny arms.
`tests/assertions/rev_end.rxt`, `tests/revend/stage2_captures.rxt` and
`run_rev_end.sh` stay green (test-codegen and the chain).

**Q2 (4), the no-guard timing arm**, from `studies/start_landing/guard_timing/`.
Each pattern ran a find-all over 1 MiB of well-formed UTF-8, comparing the
default artifact with a copy whose guard block was deleted. Arms were
interleaved, 5 rounds × 3 reps, medians shown. This is scratch tier, measured
on the dev box while other suites ran:

| pattern | matches | guard ns | no-guard ns | ratio | per match |
|---|---|---|---|---|---|
| `.` | 764,869 | 4,441,013 | 4,338,587 | 1.024 | +0.13 ns |
| `\p{L}+` | 147,883 | 2,327,746 | 2,150,815 | 1.082 | +1.2 ns |
| `[a-zé]+` | 135,797 | 2,123,748 | 2,069,011 | 1.026 | +0.4 ns |

So the guard on the happy path costs one well-predicted decode per reported
match. Answer counts agree between the arms.

**Re-pins, found by grep and by the suites that count.**
- abi readers: `ABI_EXPECT` and its ledger message, match_api.md (`#error`
  example, guard value, the `abi` row, §6¶17), S693 (AFTER 73),
  `abi_changelog.md`'s new entry, and the FILEPIN self-pin.
- registry: axes coverage 220 -> 226, and the D107 NON-LIMIT allowlist gains
  `CRA_SEARCH_FROM` (a tag ordinal).
- cpset `EMITTED_BYTES`: 12 rows +137 (the comment). Six fixed-width rows also
  lose R, giving net -2,546 to -5,160. Verified by diff.
- rxtsource census: +1/+5/+159, and the C3 pins move by the same cells.
- startset VM-hat manifests: the PF-DROP file's moved block and new witness,
  plus landing_illformed's three forced-VM movers.
- The scan-edge census rows deny the new rows, because they count REVERSE
  edges.
- cand-oracle witnesses: +4.
- nomatch-caps witnesses: relabelled, +3.
- `run_search_pinned.sh`: START_VALUES, witness flags, the §2 sweep and the
  §10 triple-deny reference.
- `run_dfa_stamps.sh` [start] now reads the two new mechanisms off the text.
- The form census tallies and floors all five `RX_DFA_START` values.
- The `run_axes.sh` product arm gets its reach floor
  (`tests/axes/start_landing_movers.tsv`).
- Spec hunks:
  - match_api.md: §3.1¶21 "one of four forms", §6.3.4¶11/¶12 and the
    value-set table, row 25;
  - tuning.md: §2.19¶6/¶8, §2.47, §2.48, the index, the flags table and the
    dial table.

**`--list-axes` moved by exactly** two added `search-start` rows
(`end-minus-width` 2, `landing` 3), plus `reverse-pass`'s order 2 -> 4.
`start_table/listing_diff.py` keys cells and cannot express an added row, so
the diff is recorded here rather than as a `listing_declared_SL2.tsv`. The
`--trace` RECOVER records move on exactly the mover compiles, which is the
census above. No separate `trace_declared_SL2.txt` was written (deviation).

## 3. SL3 — the hand's totality (b29b382d)

The hand itself landed with revbuild (STEP 0 finding 1). SL3 adds two checks
to `cand_path_selfcheck`. Both run in the trace build (`run_cand_oracle.sh`
88/0):
- **`table-recover-not-total`.** RECOVER's askers are read off the table: each
  LOCATE row's `u.locate.recover` (EXISTS for the composite, WINDOW for
  `rev-end`). On every route RECOVER is asked, the last row taking each such
  hand must be undeniable, `cand_always`, and built by construction.
- **`table-recover-start-unproved`.** A RECOVER row whose action is not the
  reverse walk may take only hands that carry `CT_START`.

## 4. Sabotage (S782-S791, appended to `.mgr/sabotage_ids.txt`)

| id | design §7.5 row | plant | detector (arms) |
|---|---|---|---|
| S782 | 1 | Λ reads byte alive-not-accept as accepting | facts [facts-sl1] (`ab`), startlanding |
| S783 | 2 | Λ continues past an assertion after the first character | facts (`\w+\b`, `a\bb`), startlanding |
| S784 | 4 | `pf_close` drops the landing record | startlanding §1/§5, harness |
| S785 | 5 | the guard is never emitted | harness on landing_illformed.rxt, startlanding §1 |
| S786 | 6-7 | the end-minus-width start subtracts W-1 (row 6 is this detector plus [facts-sl1]'s `é` [2,2]) | startlanding §5, harness |
| S787 | 9 | the dispatch takes the landing body for an end-minus-width selection | dfastamps [start], startlanding §2 |
| S788 | 11 | `emit_search_success` omits the K78 fill | nomatchcaps |
| S789 | 12 | the guard's skip re-walks the excursion per byte (O(K²)) | startlanding §H |
| S790 | 8 | `end-minus-width` takes WINDOW | revend, candoracle (selfcheck), harness on rev_end.rxt |
| S791 | 13 | the start stamp reads a fresh EXISTS ask | dfastamps [start] on `abc$` |

- Every plant compiles, and every anchor resolves (669 rows, 690 sites).
  The verdicts come from the chain's solo mech runs below.
- Row 3 was dropped by design.
- Row 10 (`recover_on_path` dropped) is an EQUIVALENT MUTANT at this pin.
  L2.1's generated stamp rule reads RECOVER only where the path asks it, and
  every RECOVER ask site is on the path. The predicate's conjunct is therefore
  read nowhere off-path.
- Re-aimed rows:
  - S221: the pinned start write is now `emit_search_success`'s argument.
  - S223: the per-action assertion line.
  - S420: reach is `(\p{Xwd})x`.
  - S693: AFTER 73.
  - S220/S227: their reach probes deny the new rows, because `(?!a)` and
    `foo\B` take end-minus-width.
- The rev-end-def rows (S758-S760, S764-S766, S780) resolve unchanged. Their
  anchors did not move.

## 5. SL4 — the bench relay draft (the manager writes the inbox)

> **[START-LANDING] landed: `RX_DFA_START` / `rx_info.search_form` gain two
> values, abi 74.** pcrec's RECOVER slot (how a DFA search recovers the
> match start) now has four rows, first match:
> 1. `pinned`;
> 2. `end-minus-width` (every match is W bytes, so the start is the verified
>    end minus W);
> 3. `landing` (the start is where the forward scan's candidate skip last
>    landed, stepped past an ill-formed character under utf8);
> 4. `reverse-pass`.
>
> `attempt-start` (L2.1) remains the absence value. The two new rows carry NO
> reverse machine, so their artifacts are smaller and skip the backwards scan.
> They are answer-identical: pcrec checks them against the reverse pass at
> every startpos and against libpcre2 10.46 on ill-formed utf8.
> - **Deny flags.** `-fno-start-width` (`PCREC_NO_START_WIDTH`, bit 53) and
>   `-fno-start-landing` (`PCREC_NO_START_LANDING`, bit 54) are masked out of
>   `rx_info.flags`. Where both rows apply, only the PRODUCT of the two flags
>   reaches the reverse pass; from a `pinned` artifact with W = 0, all three
>   denies are needed.
> - **Expected movers at pcrec's pin.** 298 of your 734 compiles (default +
>   nocaps): 210 to `end-minus-width` and 88 to `landing`. They are the
>   design's §5 predictions minus the 12 end-pinned fixed-width rows that take
>   `rev-end` since L2.
> - **FIT movers.** A mover that drops R can now fit a size rung it did not
>   fit before: `(\p{Xwd})` and `\p{L}+` under utf8 no longer take their size
>   rungs. A cell keyed on `ENGINE_SEL "size-cap-retry"` for those shapes
>   moves.
>
> **Your readers that break by design** (`readers.sh` at f3df603f):
> 1. `tools/selfcheck.py:5871`: the hard gate requires
>    `sorted(dfa_start values) == ["pinned", "reverse-pass"]`. It must accept
>    the closed set `{pinned, end-minus-width, landing, reverse-pass,
>    attempt-start}`. `attempt-start` already broke it at L2.1.
> 2. `testees/pcrec/list_axes.tsv:117-118`: the `search-start` axis gains rows
>    2 and 3, `reverse-pass` moves to order 4, and two deny bits appear.
> 3. `testees/pcrec/adapter.py:804`: the closed enum `["pinned",
>    "reverse-pass"]` (and the prose at :264/:826/:987).
> 4. `pcrecbench/report.py:763`/`:2542`/`:5648`: the `start=<pinned|
>    reverse-pass>` legend.
> 5. The fixture records keyed on `dfa_start` (selfcheck.py :3554/:3625/:3645).
> 6. The trend META key for `dfa_start`.

## 6. Deviations

- The design's twins-on-the-built-rows check (d) is the gate's §5, run against
  the triple-deny build rather than via `run_check.sh MODE=assert`.
- No `listing_declared_SL2.tsv` / `trace_declared_SL2.txt` files (§2).
- Row 10 has no sabotage row (§4). Row 6 is folded into S786.
- `run_axes.sh`'s product-arm floor is half the manifest's STATIC case-line
  count. The chain's first full run prints the measured number.
- The two deny bit numbers are this lane's pick.
- Scope: one `/tmp` backup at SL1 (logged in §1). All other scratch files are
  under `build/scratch/`.
