# r17b critic B: contract and same-commit package

Subject: commit 174f3e320 (branch lane/r17b) against 010b612c9. Read-only. Probes used
`/home/pcrec/projects/pcrec/worktrees/r17b/build/pcrec` (built at HEAD) and `-o -`. No suite was run.

Counts: **BLOCKER 0, SHOULD 9, NIT 8.** Everything the lane's own checks cover holds as far as I could
reproduce it. The findings are in the package around the byte move: one measured compile-time cost,
three stale or broken spec/listing surfaces, and a slot25 script that does not judge everything the
report says it judges.

## Verdict by lens item

1. abi 76 to 77 readers: complete for everything that cites the number. Nothing missed there. Gaps are
   in the readers that do not cite it (S2, S9) and in one CLAUDE.md ledger (N1).
2. Spec hunks: method-blind where it counts (match_api, tuning §2.42, cli, rxt_format). Three
   caller-visible surfaces still contradict the new reality (S4, S5, S6).
3. N6: correct on every route probed (below). No finding.
4. options.def and the floor literal: correct.
5. Census independence: mostly independent, with one free pass (S3, S8).
6. keeps_storage and MF_SITE_ABI 12: acceptable, with a D157 naming nit (N4) and an unlock (U3).
7. C15/C16 and headers: clean. CLAUDE.md gaps are minor (N1).
8. slot25: judges the byte move through the census only; several omissions (S2, S3).

## SHOULD

**S1. Compile time up 3-7x on every `\w`-shaped set (measured).**
`mf_set_terms` runs an uncached bounded search at each define. Wall time per compile, tip vs
`--memfn=no-pf-terms-mask`, `--features all`, mean of 3:

| pattern | tip | deny |
|---|---|---|
| `\w+x` | 26 ms | 7 ms |
| `\W+x` | 44 ms | 12 ms |
| `(\w+)\s+\1` | 24 ms | 5 ms |
| `\b\w+@\w+\.\w+\b` | 24 ms | 7 ms |
| `[\w.]+@[\w.]+` | 50 ms | 7 ms |

`[^a-z]+x` and `(?i)\b(?:foo|bar)\w*\b` do not move (7 ms). The report (§6.2) records `\w` at 1,486 nodes
and `\W` at 25,763 nodes (75 ms). Nothing memoizes across the size ladder's re-emits, and `src/opt/dfamemo.c`
is the house precedent for exactly that. Nothing in the light list times a compile (`GCC-TIME` and
`COMPILE-SPEED` in `tests/bench` were not run). `\w` is the commonest set in the corpus.
Trigger to fix: before the merge battery. A set-keyed memo, or a prime-cube fast path for the sets the
corpus actually has, removes it; see U2.

**S2. slot25 omits two controls the package depends on.**
`/home/pcrec/projects/pcrec/worktrees/memfn-slot/slot25/run.sh` has no `test-axes` (the report header
lists it as OWED to slot25: `docs/dev/lanes/r17b_report.md:15`) and no `test-recursion-identity`
(the D76/D94 identity gate). `grep -i -E 'axes|recursion|identity'` finds only comments.
The FILEPIN is deliberately unmoved, as opt5i's precedent allows (`run_recursion_identity.sh:1244`, still
`337f9a6e`), but then the gate must be named as owed to main at merge with its trigger. Neither the report
(§3 says "owed at the merge") nor the script schedules it. A new emitted loop in ~2,900 artifacts is
exactly what the axes sweep (deny/force answer identity) exists for.

**S3. slot25's verdict does not judge what its header claims.**
- Census: `verdict.txt` keeps only `^BAD` and the count of `coverable-declined` lines. There is no floor on
  movers per arm and no ceiling on declined. A kit that declined every coverable set reads `BAD 0`. See S8.
- `alpha_r17b.sh:141-142`: `DENY!=BASE` and `NEW==BASE` are echoed but do not set `rc`. Only
  `ANSWER DIFF` does (`:147`). The slot25 header says "check rc 0 (answers identical, DENY==BASE)".
  `rc 0` does not imply `DENY==BASE`, so the noise floor can silently be invalid.
- `sw trace ... --streams c-default,c-vm` compares `.c` with the abi digit moved on every artifact.
  The SWEEP line will print thousands of movers. It is unclear what judges them (the census is the only
  predicted-mover reader). Make the intended read explicit or drop the .c streams from that call.
- No automated `dumps == exactly one row` check; a human has to read it.
- The noise floor is a single |deny - base| difference of the same program, with no spread; compare the
  house's earlier alpha bands (`k82alpha`: "controls spread 0.013 ns/B"). A one-sample floor yields
  spurious WIN/REGRESSION.

**S4. registry.md breaks its own table.**
`docs/spec/registry.md (line 166)` is a blank line between `precheck-assign-byte` (`:165`) and the new
`pf-terms-mask` row (`:167`), so the row renders outside the table (verified with `cat -A`).
The floor check reads only the `memfn section floor: 7` literal, so nothing catches it.

**S5. tuning.md §2.43¶3c is false.**
`docs/spec/tuning.md (line 958)` says "The one today is `--memfn=no-precheck-assign-byte`". There are now two
scalar rows (`pf-terms-mask`, registry.md §6¶8a). That is a D80 miss for a caller-observable switch: no
tuning hunk was written for `--memfn=no-pf-terms-mask` at all, where R-15 wrote ¶3c for its row.

**S6. `--list-axes` still promises a 256-entry table.**
`src/gen/emit_dfa.c:9245` (`first-class-bounded`: "a 256-entry start_bytes table walk stopped at n-1")
and `:9255` (`first-class`: "seeks the next byte of S, as a 256-entry table"). Both print in
`build/pcrec --list-axes` (rows prefilter 7 and 8) and are false for every set with a cover of at most four
terms. The match_api, tuning and cli hunks were carefully reworded to "the kit's form"; the listing text was
not. Changing it is a declared listing event (C7 style, `listing_declared_*.tsv`), which may be why it was
skipped. If so, say so in the report; today it is a stale statement shipped with the byte move.

**S7. The pcrec to kit hand-off has no pcrec-side mutation test and no artifact-level semantic control.**
- The design's S841 ("pcrec builds `set` from the wrong table", setfind.md rows around 2456) is not built;
  the report lists S820-S843 as owed to a follow-up (§8). Meanwhile the structural start-set checks and
  mech rows S478/S481/S504 were re-aimed to the DENY arm (`tests/startset/startset_lib.py:35`), so they no
  longer exercise the default hand-off.
- What still protects the hand-off: N4's door, which fires in the probe build only (`test-memfn-rank`
  counts it against floors), the vmhat/dfahat answer differentials (reference = the deny arm, good), and the
  corpus answers in `make test` (owed).
- Missing pcrec-side check (as far as I could find): for each mover artifact, compile its
  `<stem>__member` and `__mask` and compare them over all 256 bytes (and a tail block) with the deny
  artifact's table. `setfind_check.py` and the census only test marker presence and the absence of a table.
  G2 checks the kit against G2's own generated sets, and its header says it is "NOT written blinded": the
  set families are the row author's alphabet, and the D27 reasoning in CLAUDE.md applies. See U1.

**S8. The node budget is a visible selection constant, and both independent controls excuse it.**
Report §6.2: T3's condition (a corpus set above BUDGET/4) holds, `\W`-shaped sets (39 byte, 44 VM
artifacts) decline, and a ruling is owed. `MF_SET_BUDGET 4096` is `UNMEASURED DEFAULT` (`kit.h:331`).
Which artifacts are movers now depends on search effort, not on a fact. The census lets any coverable set
decline (`r17b_movers.py:163`, outcome `coverable-declined`) and counts it without a ceiling; G2's
MUSTRENDER guarantees only families of at most two terms. So a regression that declines every 3- and
4-term set passes the census and MUSTRENDER; the only catch is G2's chosen-count floor (2,448) and the
N2 pcrec floors, which are still PLACEHOLDER (`row_floors.tsv`, report §8). Rule on S8 before merge,
because it changes which artifacts carry the byte move.

**S9. Emitted size and the refusal set move; only the corpus was audited.**
The W8 sub-block plus per-site text adds about 2.2 KB per set-site artifact (cpset manifest
`[a-z]+@[a-z]+` 27,859 to 30,040) and these bytes count toward `max_emit_bytes` and the ladder
(unlike RQ-3's guarded SIMD bytes). Measured: `(?:[a-z][0-9]){1,13000}` now refuses at 1,039,131 bytes;
`tests/resource/run_resource_tests.sh:317` pins 1,034,779 (documentation only: the check greps for
"bytes of emitted C source", so it does not go red). The census raises `BAD-refusal-moved` only over the
corpus, which has no near-cap population. The earlier abi 76 event already shifted emit_sweep's
`VARIANT_PINS` tag floors under lowsize/lowboth (`memfn/docs/responses.md` slot24 notice, item 2); R17-b
shifts the same readers by more. slot25's `variants` sweep judges "0 movers" for those streams
(`run.sh:` header), so it will read red for a legitimate cause, or the pins will be refreshed with no
prediction behind them. The reader class is not in the report's §3 table (the "second reader class" the
CLAUDE.md abi row warns about). Add a predicted-mover manifest for the lowered-cap variants (see U4).

## NIT

- **N1.** `tests/codegen/CLAUDE.md` carries a re-pin ledger entry per abi bump (`ABI_EXPECT` 74 at :4115,
  75 at :4134) and was not touched, though six codegen scripts and a manifest changed. Same for
  `tests/assertions/CLAUDE.md` (`run_mline_diff.sh`). `tests/mech/sabotages/CLAUDE.md` does not list rows, fine.
- **N2.** The W8 block emits `_Static_assert` (C11). The default DFA artifact compiled clean under
  `gcc -std=gnu99 -Wall -Wextra -pedantic-errors`; with the stateful form it fails
  (`<stdin>:266:1: error: ISO C99 does not support '_Static_assert'`), the deny artifact stays clean.
  Not promised anywhere (README says gcc dialect), but it is a silent regression of a property the
  b2fix lane cared about for the public header. `__extension__` or an `#if` fallback fixes it.
- **N3.** match_api §6.3.10¶3's first sentence still reads "what the search-code kit rendered" while ¶4 defines
  `"none"` as identity to the SIMD-off compile. An artifact with the stateful form reads `RX_MEMFN_FORMS "none"`
  (verified). Consistent with ¶4, misleading with ¶3; tighten the lead sentence.
- **N4.** D157 and `mf_result.keeps_storage` (`memfn.h`, `compose.c:688`, `emit_dfa.c:5531`): the kit reports its
  method ("storage kept at the declaration point") and pcrec changes its own emitted heads (const `subject`,
  `subject_length`) in response. pcrec's identifiers and comments say "stateful site"/"storage". Not a
  pcrec-to-kit leak, but it is the reverse flow and it names the kit's method. A stated fact in `mf_site`
  would be cleaner; see U3.
- **N5.** registry.md `pf-terms-mask` row (`:167`) describes the kit's method ("popped from a per-call cache of the
  next block's members, the block refilled when ..."), while the match_api rows say only "its form is the kit's".
  The `--list-axes` desc of the same row (options.def) has the same shape. Registry rows are the kit's own
  documentation (vrun-pad is similar), so this is precedent-consistent; the point is that the spec now promises
  a cache.
- **N6.** `test-spec-history` is left red at the tip (144/1: line-number citations in
  `slot24_triage.md` and `responses.md:2303`, kit-owned files, reported). Two lines to fix.
- **N7.** `valid_prefix` folds case with `tolower`, which is locale-dependent (`compile.c:150-163`). None of the
  letters in `pcrec_mfk` change under any locale, so harmless today; `(c | 0x20)` style would not depend on it.
- **N8.** The FILEPIN `337f9a6e` still reads as seambuild's "branch's last src commit" and a gate (B) comparison
  against it would count every R17-b mover. Owed, as the report says; just make the owed item explicit in
  slot25 (see S2).

## N6 probes (item 3)

Built binary, `-p PREFIX --pattern a -o -`:

| prefix | result |
|---|---|
| `pcrec_mfk`, `PCREC_MFK`, `PCREC_MFK_x`, `Pcrec_Mfk_`, `pcrec_mfk_`, `pcrec_MFK_a`, `pcrec_mfk_` + 40 chars | refused: "symbol prefix '...' is reserved: the search kit's shared stem is pcrec_mfk_ (pattern offset 0)" |
| `pcrec_mfkx`, `pcrec_mf`, `_pcrec_mfk_`, `xpcrec_mfk_`, `pcrec`, `pcrec_mfj` | accepted |
| `pcrec_mfk-` | refused as invalid (the identifier check comes first), correct |

`valid_prefix` is called once in `compile_driver` (`src/core/compile.c:2151`) for every route, so the CLI `-p`,
`.rxt` targets (explicit and derived) and `pcrec_options.prefix` all pass through it. `run_setfind.sh` covers the
three routes, including the near misses (S854 DETECTED). The tier is right under D26: a reserved-name refusal with
its own message, nothing modelled on PCRE2 wording. Two artifacts with different prefixes concatenated into one
TU compile clean under `-Wall -Wextra -Werror` (checked: two `#ifndef PCREC_MFK_W8_H` blocks, deduplicated).

## Other facts checked

- Spec wording: no spec sentence promises `can_begin_match` or `start_bytes` unconditionally. All four
  occurrences (match_api.md (line 1672), 1674, 1680, 2035) read "emitted where that form reads it".
- Sub-block placement matches ¶7a: after the shared-ABI block and the forward accessors, before the first
  `struct <stem>__c`. Block bytes carry no comment, so `-fcomments` cannot make two copies differ.
- `-bounded` forms: the bounded site's `hi` is `c->n - 1` and the call is guarded by `n - pos > 1`, so the D11
  stop at `n - 1` survives (match_api 6.3.4¶4 stays true).
- registry floor: 7 rows in `--list-axes` `#section memfn`, literal 7 in registry.md. Equal.
- C15/C16: `nm -g --defined-only build/libpcrec.a` shows no symbol without the `pcrec_` prefix. New externs in
  terms.c and mfk.c are MF_NS'd (nm clean), everything else static. SPDX and Provenance headers present on
  terms.c and mfk.c; `memfn/PROVENANCE.md` rows added.
- `MF_SITE_ABI` 12 is read by `compose.c:549` (`s->abi != MF_SITE_ABI`), which is the real handshake. Nothing else pins 11.
- Census independence (item 5): `r17b_movers.py` reads emitted C only, does its own cube/arc cover search in
  Python from the definitions, and does not import `moved`. It does share the design's definitions (K = 4, cubes
  plus arcs plus complement) and `emit_sweep`'s enumeration. Its checks are presence checks (kit marker, no table), not
  semantic ones. G2's oracle (byte loop over G2's own bitmap) is independent of terms.c.

## Unlocks

- **U1. Artifact-level cover equivalence (trigger: before slot25).** For every mover in the census compile a
  tiny driver that `#include`s the artifact and evaluates `<stem>__member(x)` for x in 0..255, and
  `<stem>__mask` over all lane shapes, comparing with the deny artifact's table from the same pattern. It is
  about 40 lines of python plus gcc, and it is the pcrec-side control for "the set handed to the kit is the
  table pcrec names" over the 505 real sets (the real `\w`-with-UCP and Latin-1 sets G2's alphabet may not
  produce). It also lets S841 become a real mech row.
- **U2. Memoize or derive the cover (trigger: S1 or the budget ruling).** Key a memo on the 32-byte set (K and
  the sink-independent result), as dfamemo does across retry attempts; the cover is a pure function of the set.
  This removes the 3-7x and makes the T3 budget a cost bound rather than a selection constant, which is the
  design's own stated resolution (§3.3).
- **U3. State the requirement as a fact (trigger: the second stateful row, or the next MF_SITE_ABI move).** Let
  the site carry `inputs_stable` (pcrec's fact: `s` and `n` are not reassigned over the site's range) and have the
  kit decline where it is unstated, instead of a reverse `keeps_storage` report that makes pcrec rewrite heads. It
  closes the report's own §6.1 gap ("the design never says how pcrec learns a site is stateful") and fails safe.
- **U4. A predicted-mover manifest for size-driven movers (trigger: slot25's variants sweep).** The census can
  compute each mover's byte delta (a mover grows by the W8 block once per artifact plus a per-site amount; a
  non-mover must be byte-identical). A manifest of artifacts within delta of a cap, per variant, turns "0 movers"
  into a checkable prediction.
- **U5. Census floors (trigger: slot25).** Print and floor movers per arm and cap declined at the 39/44 the
  report lists, so `BAD 0` means something.
- **U6. More than four terms (trigger: coverable-declined greater than ~100 or a bench set above 4 terms).**
  Only then consider a nibble-lookup row; not before (D77).
