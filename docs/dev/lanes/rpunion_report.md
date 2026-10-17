# rpunion — RP (the one render point) and the union over compile attempts

Lane rpunion (opus), 2026-10-17. Plan row [WINDOW-E1]'s two remaining steps
after E-1 (main `a997a97ce`): `docs/design/memfn/window_contract.md` rev 3.1
§3.7.3a (RP) and D167 addendum 3 / finding F-5 (the union). Branch
`lane/rpunion` off main `184fc9110`. Not merged, not pushed.

| commit | what |
|---|---|
| `0c7248886` | COMMIT 1, RP: the knowledge stamps render after `mf_art_end` over marks. Zero movers. |
| `c10643bbb` | COMMIT 2, the union over attempts and compound parts; abi 78 -> 79 |
| `0816793d7` | the recursion-identity (B) self-pin to `c10643bbb` |
| (this one) | this report and `rpunion_evidence/` |

## 1. Commit 1 — RP (`0c7248886`)

- `emit_info_def` (src/gen/emit_dfa.c) no longer writes the
  `#define <PREFIX>_FINDINGS` line or the `.findings = …` initializer. It
  writes a MARK at each of their byte positions: `pcrec_emit_ks_mark`, the
  second mark kind beside `pcrec_emit_memfn_mark`. The marks are a
  placeholder-lead line, `\x01K\n` for the define and `\x01k\n` for the
  initializer. The text of the two lines is `pcrec_emit_findings_line`,
  beside `emit_info_def`, which keeps the escaper it uses
  (`emit_c_string_literal`) private to that file.
- `pcrec_memfn_stamps_render` (src/gen/memfn_stamps.c) runs these steps in
  order: the libc scan, `mf_stamps`, the kit lines' splice, the reach
  table, `pcrec_memfn_art_end`, and then `ks_stamps_render`.
  `ks_stamps_render` reads `pcrec_find_stamp` at that point, after every
  reader, renders both lines and splices them over their marks. An artifact
  without `rx_info` (an entry request that omits it) holds neither mark. An
  artifact with `rx_info` holds each mark exactly once. Any other count is an
  internal-error refusal. A mark that is never replaced also fails the
  prefix render as a stray lead byte, so a lost splice cannot ship.
  `splice_mark` now takes the mark it replaces, and `mark_count` is new.
- Both engines and the compound shell go through the one info writer: the
  DFA calls `emit_info_def` directly, the VM epilogue reaches it through
  `pcrec_emit_info`, and the shell is the DFA emitter's shell branch. So all
  three write the marks and are rendered at the one point.
- §3.3 rule 9's refusal check has no case before B3b, because no routed kit
  row consults a kind yet. Its place is a comment after `art_end`.

## 2. RP zero-mover evidence (C-RP)

REF = this branch point's own build (`184fc9110`, main's tip,
`build/ref/pcrec.main`). NEW = `0c7248886` (`build/ref/pcrec.rp`).

**(a) G1-E1's emit_sweep product**, run with e1build's own driver
(`docs/dev/lanes/e1build_evidence/g1e1_sweep.sh TREE REF NEW SCRATCH 4`):
every stream, the arms default, `-fno-req-byte`, the deny-pf arm and the VM
deny arm × byte/utf8, and the analysis cells none, weblog, `-I` mine and
l1none (utf8 only). The summary is `rpunion_evidence/crp_summary.tsv`.

| enc | arm | cells | streams | movers | asymmetric | run rc |
|---|---|---|---|---|---|---|
| byte | default / `-fno-req-byte` / deny-pf / VM deny | none, weblog, mine | 11-12 each | **0** | **0** | 0 / 1 / 1 |
| utf8 | default / `-fno-req-byte` / deny-pf / VM deny | none, weblog, mine, l1none | 12 each | **0** | **0** | 0 / 1 / 1 / 1 |

**28 runs, 0 movers and 0 asymmetric refusals on every stream of every run**
(3,164 s wall at `-j4`). Every rc 1 is the same instrument floor e1build
recorded, identical on both sides. `emit-ir-vm` reaches 0 because
`--emit-ir` refuses `--analysis` (e.g. `es_byte_default_weblog.log`:
`REACH FLOOR VIOLATION: 0 < floor 4920`). On the l1none cells, stream 1
reaches 1,905 because the asking compiles refuse on both sides (§3.7.4a's
population, compared as keys). Every run with no analysis cell has rc 0.

**(b) Artifact census, unmasked** (`rpunion_evidence/census.py REF NEW`,
output `census_rp.out`). It covers emit_sweep's corpus population, 5,275
distinct (file, pattern) pairs, in 9 arms: 4 arms × byte/utf8 plus
`--engine=vm`. Result: **0 movers and 0 asymmetric refusals**. Each arm has
4,834 to 4,857 identical artifacts and 418 to 441 refused on both sides.

**(c) The compound witnesses.** Every row of `tests/compound/admitted.tsv`
(97 rows) was compiled under {default, `-fno-req-byte`, deny-pf} ×
{no analysis, `--analysis weblog`}, comparing `.c`, stderr and rc. That is
**582 compiles, all 582 compounds (`_COMPOUND "split"`), 0 differ.**

## 3. Commit 2 — the union (`c10643bbb`)

- **The rule** (D167 addendum 3; §3.7.3a item 4): `<PREFIX>_FINDINGS` and
  `rx_info.findings` list a query iff ANY attempt of the compile asked it,
  or, on a compound shell, P's compile or any part's compile asked it. The
  list is rendered once, at RP's point.
- **The mechanism.**
  - `compile_driver` owns `unsigned find_union`. It lends it to every
    attempt as `Ctx.find_union`, the same pattern as `dfa_memo`.
  - `job_cleanup` runs at the end of every attempt (success or `longjmp`).
    It ORs the attempt's asks into `find_union` before the attempt's record
    is freed. The asks come from `pcrec_find_asked`, one `PCREC_FQ_BIT` per
    query, so the mask grows with `find_queries[]`.
  - A part's compile writes its own union into
    `PcrecPartFacts.find_consulted` when it succeeds. The shell's `facts[]`
    copy carries it.
  - `ks_consulted` (memfn_stamps.c) ORs together this attempt's asks, the
    earlier attempts' union and the parts' sets.
  - `pcrec_find_stamp(cx, consulted)` now renders a consulted SET. If
    another attempt or a part was the asker, it derives this attempt's memo
    (non-raising). A consulted answer that cannot be derived refuses with
    the asker's own text (rule 9). This cannot happen today: the asker
    already refused.
- **The abi event: 78 -> 79.** These are the readers of the number, found
  by grep (`(abi|ABI)…78` over src/lib/cli/tests/scripts/docs/spec/memfn,
  then each hit read):
  - `src/gen/emit_dfa.c:54` `PCREC_ARTIFACT_ABI`. This one constant feeds
    `.abi =`, the generated-by line, the K80 `#if`/`#error` and
    `PCREC_RX_ABI_H`.
  - `docs/spec/match_api.md`: five sites. These are the K80 `#if`, the
    `#error` text and `#define PCREC_RX_ABI_H` in §1, the `rx_info` row 1
    value, and §6¶17's "It is `79` on every artifact".
  - `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=79`, plus its failure
    message's transition list (`78->79` appended).
  - `tests/mech/sabotages/S693_abi_not_bumped.sh`: re-aimed, with
    BEFORE 79 and AFTER 78.
  - `docs/dev/history/abi_changelog.md`: a new top entry; the old 78
    paragraph is now "was".
  - `tests/codegen/run_recursion_identity.sh` FILEPIN, self-pinned to
    `c10643bbb` (`0816793d7`) by the self-pin convention. The manager
    re-pins it to the merge.
  - Not readers: `scripts/emit_sweep.py:2101` (a dated tag-floor history
    line), `memfn/docs/responses.md` (history), and design CLAUDE.md
    mentions (historical measurements).
  - The abi digit's width is unchanged (78 -> 79), so no byte-count pin
    moves on that account.
- **Spec hunks (D80).**
  - `findings.md` 5¶2: a query counts if any attempt asked it, a discarded
    retry included. On a compound, P's compile and every part's count.
  - `findings.md` 5¶4: "…on any attempt".
  - `match_api.md` `rx_info` row 28: "(on any attempt)".
  - `match_api.md` 6.3.10¶11: the union sentence, and "the search-code kit
    included (its artifact end)" for the render point.
  - `match_api.md` 6.3.12's table: `_FINDINGS` leaves the pure "pattern"
    row for its own row, "pattern, over P and the parts".
  - B3b's CONSULTED-wording hunks (§3.7.9) are NOT made here. They belong
    with the kit's OR.
- **Other edits.**
  - S314 is re-aimed. Its anchor line is gone: the stamp takes the
    consulted set, and the plant keeps that set in a static.
  - C-PERT: the F-5 bucket is retired (see §5).
  - `src/gen/CLAUDE.md` and `src/core/CLAUDE.md` gain entries, and
    `tests/findings/CLAUDE.md` is updated.

## 4. The union's mover census

`rpunion_evidence/census.py REF=pcrec.rp NEW=pcrec.union --mask-abi`
(output `census_union.out`). It uses the same 5,275 × 9 arms as §2(b). The
abi number is masked on lines that name the abi, and the unmasked control
(`--every 200`) shows every artifact moving on those lines alone.

| arm | movers (stamp lines only) | other movers | asymmetric |
|---|---|---|---|
| default byte / utf8, `--engine=vm`, the VM deny arm byte / utf8 | 0 | 0 | 0 |
| `-fno-req-byte` byte | 27 (all compound shells) | 0 | 0 |
| `-fno-req-byte` utf8 | 31 (29 compound shells + the 2 F-5 witnesses) | 0 | 0 |
| deny-pf byte | 27 (compound shells) | 0 | 0 |
| deny-pf utf8 | 29 (compound shells) | 0 | 0 |

**114 movers, every one moving only the two knowledge-stamp lines, `""` ->
`"byte-rate=…"`. 0 other movers and 0 refusal asymmetries.** Beyond the abi
digits:

- **The 2 F-5 witnesses, as expected:** `(\p{Xwd})x`
  (`tests/uprops/size_ladder_prefilter_drop.rxt`) and `x(\p{Xwd})y`
  (`tests/utf8/wclass_illformed.rxt`) under `-e utf8 -fno-req-byte`. Both
  ship from a retry (`ENGINE_SEL "size-cap-retry"`) and now read
  `"byte-rate=none"`.
- **112 compound shells, NOT in the brief's expectation** (departure D5,
  §7). Under the two `-fno-req-byte` arms the split parts' compiles ask the
  byte-rate, because each part writes a DFA body whose readers ask. P's
  shell attempt writes no body and asks nothing, so the shell stamped `""`.
  §3.7.3a item 4 rules that the shell's stamp is the union of P's attempt
  and every part's, so these now list `byte-rate=default:…` (or `none`
  under utf8 where nothing answers).

## 5. C-PERT before and after

`tests/findings/c_pert.py`, run on both binaries at `--every 16` (the
`make test` slice) and `--every 1` (the full population). Outputs are
`rpunion_evidence/cpert_{rp,union}_{16,1}.out`.

| binary | slice | verdict | `-fno-req-byte` utf8: FAIL-moved / consulted-moved / consulted-same / quiet |
|---|---|---|---|
| RP (`pcrec.rp`, before) | 16 | **rc 1**: FAIL moved × 2, the F-5 witnesses | — |
| RP (before) | 1 | **rc 1**: the same 2 FAILs (42,200 artifacts × 3 compiles) | 2 / 484 / 2,589 / 1,780 |
| union (`pcrec.union`, after) | 16 | **rc 0**: both PASS lines | — |
| union (after) | 1 | **rc 0**: no artifact moves with data its stamp omits, and power floors hold in all 8 arms | 0 / 486 / 2,618 / 1,751 |

- **The pins are updated.** The `F5_PIN` exact-membership exception bucket
  (selected by `ENGINE_SEL "size-cap-retry"`) is gone. Such an artifact
  now FAILs `moved` like any other. The two former witnesses
  (`F5_WITNESSES`) are still always added to the population. Each must now
  read `consulted-*` AND still ship from a retry: this keeps the population
  the fix is about reached (K35), and it is the check's failing direction.
  The RP binary reads red on it, as the table shows.
- **The two witnesses now pass:** after the fix both are `consulted-moved`
  (+2 power). The power floors are minimums and did not need re-cutting.
- **The compounds read `consulted-same`, not `consulted-moved`.** Separately
  measured with the RP binary: under the two deny arms, perturbing the
  byte-rate data (`c_pert`'s reversed-rank `default.rxt`, same name and
  stop) moves no byte of any of the 194 admitted-compound artifacts. So the
  parts ask but their answer moves nothing here. That is why the
  prototype's "no compound FAIL" held while the shell's stamp was still
  `""`.

## 6. Suites run (this box, `-j4`, beside the kit's runs and this lane's own sweep)

All of these ran on the union tree (`c10643bbb` + `0816793d7`), at
`make -j4 test-X`. Logs are in `build/ref/suites/` (worktree-local,
gitignored).

| target | verdict |
|---|---|
| `make strict` (after each commit) | clean |
| `test-findings` | green (152 PASS, 0 FAIL; §15 C-PERT included) |
| `test-codegen` | green (35 checks, 0 failed; 16/16 scripts; ABI_EXPECT 79 holds) |
| `test-registry` | green (79 / 0) |
| `test-rxtsource` | green (298 / 0) |
| `test-spec-history` | green (145 / 0) |
| `test-plan-lint` | green (2 / 0) |
| `test-memfn-stamps` | green (25 / 0) |
| `test-recursion-identity` (the (B) gate at the self-pin) | green, 18/0, 1,924 s: (B) 0 differing vs the self-pin across 3,866 call-free patterns; (A) program region vs `ac4917d` holds, with only the named exceptions; the VM positive control refuses 420/420 |

The verdict was read from make's `*** [...test-X] Error` lines (none) and
from each suite's own failed count.

**Sabotage, by hand rather than by mech** (mech is the manager's):

- **S314, re-aimed.** Planted in a `git archive HEAD` scratch tree. The
  `multi.rxt` fixture's `t_quiet` then stamps
  `byte-rate=default:1822fb973b95a4da`, where findings §6 #22 requires `""`
  (DETECTED shape). The clean union binary stamps `""` (its REACH witness
  holds).
- **The union's own failing direction** is C-PERT's witness check, shown red
  on the pre-union binary in §5.

## 7. Departures (the code's facts win; none moves a byte in commit 1)

- **D1. The mark letters are `K`/`k`, not a hex letter.** My first build
  used `\x01F`/`\x01f`. C reads `\x01F` and `\x01f` as the single byte
  0x1F, so both marks were one string. The mark count caught it at once as
  an internal error, and no artifact was compared from it. `ks_marks[]`'s
  comment states the rule.
- **D2. The order inside the pass.** §3.7.3a item 1 lists the order as
  "`mf_art_end`, rule 9, pcrec's knowledge stamps, then the splices". Here
  the KIT's lines (and `SIMD_GUARDED_BYTES`) still splice BEFORE
  `mf_art_end`, as before. Only pcrec's knowledge stamps render after it.
  The reason: no heap `StrBuf` is held across `mf_art_end`, which can
  refuse by `longjmp`, so nothing leaks. Nothing in the kit's lines depends
  on the art's end. This moves zero bytes either way.
- **D3. Rule 9 has no code yet.** No routed kit row consults a kind before
  B3b. There is a comment at its place.
- **D4. The parts' hand-up is in commit 2, not commit 1.** The brief has
  commit 1 take §3.7.3a item 4's path. In commit 1 the shell writes the
  marks and renders at RP with P's own record, which is today's value and
  zero movers (§2(c)). Item 4's union of P and the parts is the union
  event, because it moves bytes (§4), so it ships with commit 2's abi bump.
- **D5. The union moves 112 compound shells beyond the 2 F-5 witnesses**
  (§4). The brief expected only the F-5 class. The note rules the parts'
  union (§3.7.3a item 4: "Its stamp is the union of what P's attempt and
  every part's attempt consulted"), so I built it as written and did not
  stop. **This is the one point the manager may want to confirm.** If the
  shell should carry P's own union only, delete the parts loop in
  `ks_consulted` (memfn_stamps.c, two lines) and the
  `PcrecPartFacts.find_consulted` line in compile.c. The census then drops
  to the 2 witnesses, and the spec rows return to "pattern".
  RULED by the manager 2026-10-17: keep the union over P and every part (the stamp means CONSULTED; the parts' readers asked).
- **D6. `stamp_kinds.c` keeps `FINDINGS` as `SK_PATTERN`.** The compound
  filter passes through the value `ks_consulted` computed, so I added no
  second union kind beside `SK_PARTS_UNION` (whose value is a sorted list
  of the parts' forms, a different shape). The spec's 6.3.12 table gives
  `_FINDINGS` its own row so the contract states the union.
- **D7. No new sabotage id.** The brief gave no range. Two plants fit: "the
  attempt's asks are not harvested into `find_union`" (detector: C-PERT
  §15's witness check, already shown red on the pre-union binary) and "the
  shell ignores the parts' sets" (detector: this lane's census only; no
  `make test` arm compiles a compound under `-fno-req-byte`). The second
  needs a test cell before it can have a row: findings §6, a split pattern
  under `-fno-req-byte` stamping `byte-rate=…`. That cell is OFFERED, not
  built (D77: say the word).
- **D8. `_MEASURES` does not exist yet** (M0). The render point is ready
  for it (§3.7.3a item 2: the same call), and nothing is rendered for it.
- **D9. The sibling edit to `measure_sets.md`** (§3.5, §4.2, §9.2 part 5:
  the same render-point sentence) is still OWED, as the note says. It is
  not made here.
- **D10. CLAUDE.md placement.** The directory entries describing RP landed
  in commit 2, together with the union's, not in commit 1.

## 8. Heavy validation owed (the manager schedules)

- The full `make test` through `scripts/perfrun` on the merge. The abi
  digit moves every artifact. Byte counts do not move (same width), but run
  the whole suite for the pins nobody greps.
- Mech rows: S693 (re-aimed), S314 (re-aimed, validated by hand only),
  S991, S1034 and S996 (they anchor in findings.c near the changed stamp
  function; anchors verified present), S513-S517 and S528 (memfn_stamps.c
  anchors verified present).
- `make asan` over `test-findings` and `test-memfn-stamps`. The pass now
  holds two more short-lived `StrBuf`s, and `find_union` is written from
  `job_cleanup` on the `longjmp` path.
- The battery's `recidentity` stage with FILEPIN re-pinned to the merge.
- pcrec-bench: abi 79 is a re-pin event for its pinned tier. Movers beyond
  the digit exist only in deny arms, which the bench does not compile at
  default flags.

## 9. Reproduce

    REF=build/ref/pcrec.main RP=build/ref/pcrec.rp U=build/ref/pcrec.union
    bash docs/dev/lanes/e1build_evidence/g1e1_sweep.sh $PWD $REF $RP SCRATCH 4    # C-RP
    python3 -I docs/dev/lanes/rpunion_evidence/census.py $PWD $REF $RP            # C-RP, artifacts
    python3 -I docs/dev/lanes/rpunion_evidence/census.py $PWD $RP $U --mask-abi   # the union's census
    python3 -I tests/findings/c_pert.py $PWD $U SCRATCH --every 1                 # C-PERT after
