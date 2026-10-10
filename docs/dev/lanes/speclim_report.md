# Lane speclim: limits.md and cli.md facts-only rewrite (report)

Lane speclim (sonnet), branch `lane/speclim` off main `33a2a429`, 2026-10-10. Plan row `[SPEC-CLEAN]`, the next two docs in density order. Method: the specreg lane (registry.md, table_contract.md). Not done here: docs/dev/plan.md (the manager's, at merge); full `make test`, mech, test-axes, san (box hold).

## 1. Survey, before and after

Counted by `tests/spec_history/spec_history.py` (marker lines outside fenced code; the "before" figures are the baseline rows removed).

| file | lines before | marker lines before (date/add/walk/narr/tagopen) | lines after | marker lines after |
|---|---|---|---|---|
| limits.md | 1161 | 48 (17/1/6/5/19) | 382 | 0 |
| cli.md | 1365 | 56 (25/1/10/7/13) | 424 | 0 |

No allowlist rows were needed. Both docs carry the generated contents block (`scripts/spec_toc.py --init`) and numbering (limits.md: 33 headings, 103 paragraphs; cli.md: 45 headings, 105 paragraphs). The old top-level section numbers were kept in both, so every existing `limits.md §N` / `cli.md §N` citation names the same topic:

- limits.md keeps §1 scope, §2 codes, §3.1-§3.9 and §3.4a (the sections `--list-limits` names in its `anchor` column), §4 worked example, §5 stack, §6 left recursion, §7 not limited, §8 size, §8a, §8b. The old unnumbered `###` subsections of §8 are §8.1-§8.8, and the old unsectioned §3.3 is §3.3.1-§3.3.5.
- cli.md keeps §1 (compile) with §1.1 (the file operand; 15 inbound cites), §2 (listings), §3 (diagnostics), §4 (does not do). The old unnumbered `###` flag entries of §1 are §1.2-§1.18, and the old §2/§3 `###` entries are §2.1-§2.14 and §3.1-§3.4. The old "Revision history" is not carried.

## 2. History moved (frozen)

`docs/dev/history/limits_record.md` and `docs/dev/history/cli_record.md`: the COMPLETE old text of each doc, verbatim, under a short header (the contract-bearing parts live on in the rewrite, the ledgers below say where; everything else is only there). The same text is in git at `33a2a429`. `docs/dev/history/CLAUDE.md`, `docs/dev/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md`, `docs/spec/CLAUDE.md` (the two entries rewritten to current facts) and `tests/spec_history/CLAUDE.md` are updated.

## 3. Code wins: disagreements resolved (each checked against a live `build/pcrec` of this branch, `--list-limits`, `--help` or the source)

limits.md:
1. "FOUR OF THESE SIX gain a raise surface": the live `override` column is `flag` for three of the six (`PCREC_MAX_NFA_STATES`, `PCREC_MAX_DFA_STATES_GOTO`, `PCREC_MAX_SUBSET_ELEMS`) and `none` for `PCREC_MAX_VM_NODES`, `PCREC_MAX_DFA_STATES_TABLE`, `PCREC_MAX_TABLE_ENTRIES`; the other raise-only flags are `--max-auto-dfa-elems` and the two emit caps (`raise_only_limits[]` in `cli/main.c`, six rows). Stated per row (§3.3.1, §3.3.2). The old text also said the table-engine cell is "short/unsigned short" with 65,535 the premultiplied dead sentinel: kept as "a 16-bit integer".
2. The size-cap examples `a{0,25000}`, `[a-z]{0,30000}`, `(a|b){0,30000}` and `a{1,31000}`: each compiles at default settings today under auto, vm and dfa (the `(a|b)` one needs `--no-captures` for dfa). The "refused since `abi` 11" narrative and the 1,103,367 / 1,323,371 / 1,333,109 / 1,367,865 figures are dropped; §8.8 states the rule only.
3. `--list-limits` "row 58 of 58": live has 73 rows (`limits_check.sh` pins the manifest). No count is stated.
4. The ladder table's "measured cost (Mac, directional)" column: measurements, not contract; dropped. Order, scope, deny flags and the `degrading` marking are kept and match `fit_rungs[]`.
5. "It is `PCREC_MAX_VM_NODES` (131,072, `src/ir/nfa.c:110-111`)", `emit_vm.c:87-88`, `lib/pcrec.h:301` and every other line citation: dropped, constants are named instead.
6. K33 stack figures (3,184 / 134,400 / 131,216 / 3,328 short / `_search_in` 144 B) re-measured with `make test-stackdepth` (5 pass, 0 fail) and unchanged; kept as the specimen's figures, with the command. The "D73 reads 131,296 B" note and the "this document previously said SIGSEGV" walkback are history.
7. The worked example (n = 342 matches 684 bytes, n = 343 gives up) re-run live: unchanged.
8. §8a table (`subject_ceiling` 512/341, 512/341, 43/23) re-run live with `--unroll=8` and `--unroll=1`: unchanged.
9. The `[PF-DROP]`/OPT-4 text that "the size rung is one row of the size-cap ladder" and "A `+2`-induced overflow has no rung": both still true (no such row in `fit_rungs[]`); the second is stated as a fact without the "recorded as a gap, not a promise" framing (§8.5).
10. "Both defaults land in `rx_info.step_budget`/`work_budget` as `-1` when disabled": re-verified (`--fno-step-budget` emits `-1`/`-1`).

cli.md:
11. Module roster: the doc said "The 18 module names"; live has 19 (`vars` is the 19th). The per-module status table (built / not built / partial) is replaced by the roster and the rule "read the `built` column", since statuses drift; live today: `ucp` and `unicode-props` are mixed, `branch-reset`, `callouts`, `comments`, `conditionals`, `extended-classes`, `misc` and `verbs` are unbuilt, the rest built.
12. "Six names exceed the emitted-artifact size cap under `--encoding=utf8` and refuse": live, `\p{L}`, `\p{Xwd}` and `\p{Unknown}` compile (with the large-artifact warning). Dropped.
13. `unicode-props` counts (45 category names, 171 scripts, 154 empty under byte): dropped, the rule is stated (the categories, the scripts of the pinned UCD except `Katakana_Or_Hiragana`). Re-verified live: the boolean properties, `bc=`, `\p{Foo}`, `\p{InGreek}`, `\p{Katakana_Or_Hiragana}`, `\p{Hrkt}` refuse; `\p{Greek}`, `\p{sc=Greek}` compile. The old claim that a one-letter-axis unknown name refuses "as an unknown NAME with no module clause" did not reproduce (`\p{Foo}` refuses with the module gap wording); not restated, wording being D26 tier 3.
14. `-i`: `--help` says "match case-insensitively (ASCII letters)"; the code folds by the encoding (re-verified: `-i -e utf8 'k'` matches U+212A, `-i --ucp '\xe9'` matches `\xc9`). The spec states the code (open question 1).
15. `--trace` has a flag arm in `cli/main.c` and an entry in `--help` but no section in the old doc (its §4 pointed at "§1" for it). Added as §1.12.
16. `--lib-path`: old §4 said "pcrec reads no library's CONTENTS"; the same doc's §1.1 said a `lib` file is read, and it is (a `lib` definition compiled: `\d requires module 'classes'` was raised from the library's pattern). §1.1.3 and §4 now say read.
17. `--version`: the doc pinned the literal `pcrec 0.2.0-beta`; live is the same today, but the string is a release value, so the spec states `pcrec <PCREC_VERSION>` and no literal.
18. `--list-families`: "measured floor 60", `--list-source` "nineteen columns", exit-3 "81 row blocks, 19 queries": counts, not contract; dropped.
19. `--list-definitions`' `definition` "or the literal `<builder>`": the live behaviour is registry.md §9 (specreg open question 1); cli.md just points at registry.md §9 for the columns.
20. `--list-limits`' `override` values: the old doc listed `flag | -D | none`; live also prints `flag+-D`. Added.
21. `--flavour`: re-verified the refusal text (`applies to --list-syntax, --list-definitions and --explain only`).
22. The `§4` "plan.md:580/581" line cites, "STATE:not-started/started" tags, `[DD-8]`/`[LIB]`/`[V-E]` row status: planning state, dropped; the facts (no multi-pattern unit, no `--lib FILE`, no `--emit-dot`) remain.
23. The `std1` source cite `enabled.c:80-85`, the `cli_parse` arm-name cites, the `compile.c:49-56` prefix cites: dropped; the behaviour is stated (60 / first char / alnum, `std1` = classes + modifiers).

## 4. Claims ledger

SUPERSEDED = not the live behaviour (§3); HISTORY = a past-state, dated or ruling statement moved to the record; N/A-DROP = a count, line number or measurement not stated; POINTER = the old text pointed at another doc, kept as a pointer.

### limits.md

| old § (lines) | claim | new |
|---|---|---|
| preamble 3-10 | spec not design; every number verified against a shipped surface | 0¶1 (verification statement HISTORY; `limits_check.sh` is the standing check) |
| 1 (12-26) | pcrec is AOT, adversarial hardening out of scope (D22); a give-up is never a false answer; code space is match_api.md §4 | 1¶1, 1¶2 |
| 2 (28-47) | four give-up codes with values; `PCREC_ERR_RECURSE` reserved, shares `PCREC_ERR_FLOOR`; `PCREC_ERR_INTERNAL` not a give-up; match_api.md §4 owns propagation | 2¶1 table, 2¶2 |
| 3.1 (53-62) | step budget 500,000,000, `PCREC_STEP_BUDGET_DEFAULT` sentinel, `--step-budget=N`, `--fno-step-budget` | 3.1¶1 (the ~50M steps/s and "~10 s" estimate N/A-DROP; "robustness bound, not a latency guarantee" kept) |
| 3.1 (63-74) | work budget 1,000,000,000, separate counter, `--work-budget=N`, one existence gate, `-1` when disabled | 3.1¶2, 3.1¶3 |
| 3.1 (75-97) | a literal run of 3+ bytes is one `memcmp` charged as one compare; 2-byte run unchanged; work budget unchanged in concatenation; island charge rule; node budget still pays per byte | 3.1¶4 (S2a / abi 41 / abi 43 and the measured "no corpus moves" HISTORY) |
| 3.2 (101-113) | defaults 2,048/3,072; macros and `rx_info` mirrors; `--backtrack-frames`; clamp at `VM_MAX_AUTO_*`; 0 on DFA | 3.2¶1 |
| 3.2 (114-117) | D73 kept the numbers; stack-frame reason; `_in` is the route | 3.2¶2 (the D73 ruling HISTORY) |
| 3.2 (118-135) | [OPT-1] two-step entry: fast buffer, escalate on `PCREC_ERR_FRAMES` only, answers identical, `-fno-tiered-entry`; measured 213-268 -> 45.6 ns, 98,512 -> 3,168 B | 3.2¶3; measurements N/A-DROP/HISTORY |
| 3.2 (136-150) | the tier is a bet: wasted attempt bounded by step/work budgets, up to twice the step budget, a cliff; the `((a)|(aa))+b` series; 25-byte boundary; use `_in` above | 3.2¶4 (the series and the boundary figure N/A-DROP, kept as the rule) |
| 3.3 (152-170) | six ceilings and defaults; `--list-limits` reproduces them; crossing one fails cleanly | 3.3.1 table, 3.3.1¶1 |
| 3.3 (172-197) | raise surface: three flags raise three ceilings, raise-only, `raise_only_limits[]`; TABLE not raisable (16-bit cell) | 3.3.2¶1-¶2; "FOUR OF SIX" SUPERSEDED (§3 item 1); n1budget_report pointer HISTORY |
| 3.3 (199-210) | SEL-1: under auto, a DFA-side ceiling is a selection outcome; NFA/VM have no fallback; `--engine=dfa`/`-fprefilter` keep the contract | 3.3.3¶1 |
| 3.3 (212-235) | optional anchored machine charged to the same three ceilings; no diagnostic, no fallback; the K53-SELRETRY size correction (dropped before a size cap refuses) | 3.3.3¶2 (the six property names and byte counts HISTORY) |
| 3.3 (237-263) | `PCREC_MAX_AUTO_DFA_ELEMS` 30,000,000; auto only; mandatory machines only; one stderr line; `--engine=dfa` unaffected; derived default, 24,050,003 witness | 3.3.4¶1 (derivation and witness HISTORY) |
| 3.3 (265-309) | OPT-4 prefilter-language retry after a size refusal; adds attempts never headroom; `-fno-prefilter-collapse`; PF-DROP; not for DFA engine; nullable language ships no prefilter | 3.3.4¶2; the K41 byte figures and the constant-deleted history HISTORY |
| 3.3 (311-321) | no compile-time bound; D45 is a harness policy | 3.3.5¶1 (D45 and `[TT-10]` HISTORY) |
| 3.4 (323-329) | buffer sizing is match_api.md §10.4 | 3.4¶1 POINTER |
| 3.4a (331-381) | `pcrec_limits_tsv`; header and `override` values; `unit` meaning including `bits`; selection knees unanchored; the six `max_*` raise-only; no macro duplicates | 3.4a¶1-¶5 (the LIM-OVR and abi 59 narrative HISTORY) |
| 3.5 (383-418) | 127-byte caps with named diagnostics; list elements uncapped; `from` nests 64; whole-file slurp uncapped; `pcrec_error.msg` 256 with `file:line:` first | 3.5¶1-¶4 |
| 3.6 (420-443) | `PCREC_MAX_VAR_NAME_LEN` 64, `PCREC_MAX_VAR_NEST_DEPTH` 8, word position only, compile time, not movable | 3.6¶1-¶3 |
| 3.7 (445-479) | find count 2^40; rate floor 2 ppm; chain 8; bundle 1,048,576; cpfreq rows 65,536; not movable | 3.7¶1-¶6 |
| 3.8 (481-505) | `PCREC_UCP_NARROW_MAX_INTERVALS` 128; which sets are refused under utf8; `(?aW)`/`(?aP)` lift it; UCP `\b`/`\B` refused under utf8 | 3.8¶1-¶2 (the 930-interval and 66 s witnesses N/A-DROP) |
| 3.9 (507-527) | `PCREC_MAX_CTX_SETS` 32, `PCREC_MAX_CTX_ATOMS` 16; decline like a state cap; message; not movable | 3.9¶1-¶3 |
| 4 (529-566) | `^(a(?1)?b)$` gives up at n = 343; the trail binds first (~2 frames, 9 trail entries per level) | 4¶1, 4¶2 |
| 5 (568-649) | entry frame under one page, deep path = entry + internal; headroom criterion; 128 KB vs 8 MB as examples; K33 open, narrowed; remedy `_in` | 5¶1-¶4 (the walkback sentences and the 131,296 note HISTORY) |
| 6 (651-679) | K34/D74: left recursion gives up where libpcre2 concludes; D74 not adopting the guard; bounded by the same frame budget | 6¶1-¶3 (the D74 cost argument condensed in 6¶2) |
| 7 (681-726) | not limited: compile time; the size term moves a tuned budget; step and work are not total effort; possessification trades counters; `PCREC_ERR_RECURSE` has no producer | 7¶1-¶5 (the 89/110 and 581/1,586 figures N/A-DROP) |
| 8 (730-764) | two caps in bytes without comments; `.o` ~17%; `-fcomments` cannot change a verdict; why two; emergency failsafes | 8.1¶1-¶4 (the 2,487-pattern corpus census and the K41 witness N/A-DROP; the large-count pattern examples SUPERSEDED, §3 item 2) |
| 8 prefix (766-795) | measured at a canonical two-byte prefix; the cap may be exceeded in real bytes; no stamp by value differs | 8.2¶1-¶2 (K79 history HISTORY) |
| 8 SIMD (797-816) | SIMD-guarded bytes excluded; `<PREFIX>_SIMD_GUARDED_BYTES`; no aggregate budget; stamp `0` | 8.3¶1-¶2 |
| 8 ladder (818-851) | ordered table `fit_rungs[]`, five rungs with engine scope and own deny, order by cost; `--size-cap=refuse` one predicate over degrading rows; SEL-1 rows outside its reach | 8.4¶1-¶4, table (cost column N/A-DROP) |
| 8 PF-DROP stamps (853-860) | `VM_PREFILTER "none"`, `ENGINE_SEL "size-cap-retry"`, `_WHY` text; not under `-fprefilter` or DFA-overflow retry | 8.5¶1 (the `\p{Xwd}` witness HISTORY) |
| 8 optional drop (862-938) | two optional contributors; stamps they leave; `"forced"` under `--engine=dfa`; stderr notes; same caps | 8.4¶3 (order), 8.5¶1-¶3 (population counts HISTORY) |
| 8 gap (940-959) | `+2`-induced overflow has no rung | 8.5¶4 |
| 8 overrides (961-978) | not deniable, raisable upward; stamps `MAX_EMIT_BYTES` / `MAX_EMIT_CODE_BYTES` (VM only); `--tune` never lowers a cap | 8.6¶1-¶2 |
| 8 warn (980-1011) | `--warn-emit-bytes=N` advisory; 250,000; 0 disables; the one non-raise-only; library field zero = off | 8.7¶1-¶3 |
| 8 oversized (1013-1075) | refuses, nothing written; options 0-5 in order | 8.8¶1-¶2; the "abi 11" and `--source` shipping narrative HISTORY |
| 8a (1077-1114) | `K` language-identical, depth not; `subject_ceiling` table; rule 1 (explicit `K` may lower), rule 2 (size term never lowers, `capacity-declined`) | 8a¶1-¶4 |
| 8b (1116-1161) | the three knees `--tune=N` moves, with values and override kinds; BAR as a percent ceiling; "row 58 of 58" | 8b¶1-¶4, table; row count SUPERSEDED |

### cli.md

| old § (lines) | claim | new |
|---|---|---|
| preamble 3-13 | scope and ownership split with tuning.md, limits.md, compliance | 0¶1 |
| 1 (17-43) | usage; operand is an input file; `--pattern`; they do not combine; `--` ends options; non-file operand refused by name; `--source` retired | 1¶1 |
| `--version` (45-63) | prints `pcrec <ver>`, exit 0, independent of `abi`, stamped in provenance, parsed like `-h` (refused in a config) | 1.5¶1 (version literal SUPERSEDED; the `cli_parse` rationale condensed) |
| `--pattern` (65-71) | one only, long form, no file operand | 1.3¶1 |
| `-o` (73-92) | `.h` derivation, `header_name`, `-o -` self-contained | 1.2¶1, 1.2¶2 (case numbers N/A-DROP) |
| `-p` (94-107) | identifier grammar, 60, refused not truncated, default `rx` | 1.6¶1 (source line cites N/A-DROP) |
| `-e` (109-152) | byte and utf8; menu on unknown; utf8 behaviour; startpos boundary; utf8 implies two modules; `(*UTF)`; byte `\x{}` error; per-compile scalar | 1.7¶1-¶5 |
| `-i` (154-204) | parse-time fold; per-encoding table; four consequences; Unicode 16.0.0 pin | 1.8¶1-¶4 (the "~1,500-entry / ~26 KB" detail N/A-DROP) |
| `--ucp` (206-252) | semantics; opt-in; `\h \v`; `(?a…)`; caseless; byte clamp; refusals | 1.9¶1-¶7 |
| `--pattern-esc` (254-285) | quoted escape form; refusals; `\x00` K9; changes only how the value is read | 1.4¶1-¶4 (the "[K98] until 2026-10-09" note HISTORY) |
| `--emit-main` (287-300) | appended `main()`; separate exit vocabulary 0/1/2/3 | 1.10¶1 |
| `--no-captures` (302-307) | `RX_NCAPS 1`, DFA | 1.11¶1 |
| `--engine` (309-339) | do-or-die; `vm` disables the prefilter; auto's one exception | 1.13¶1-¶2 |
| `--tune` (341-390) | ordinal and aliases; `=` form for negatives; out of range refused; every position answers identically; `RX_TUNE` always stamped; config `tune` | 1.14¶1-¶2 |
| budgets (392-402) | two counters, one gate, no `--fno-work-budget` | 1.15¶1 |
| `--warn-emit-bytes` (404-416) | advisory, 250000, 0 disables, may be lowered | 1.15¶4 |
| `--size-cap` (418-439) | refuse/degrade, bit 41, a policy not an axis, `--fast-or-fail` unknown | 1.15¶5, 1¶1 |
| `--memfn` (441-467) | opaque string; kit validation; carriers; composition; inert at `-fno-memfn-simd`; no abi event | 1.16¶1-¶6 |
| `--backtrack-frames` (469-476) | raises capacity, `1..1,000,000`, C stack | 1.15¶2 |
| `--features` (478-504) | list grammar, `std1`, `none`, unknown module refused by name, `requires module 'X'`, library lever | 1.17¶1-¶2 |
| module table (506-532) | 18 modules with status | SUPERSEDED (19 modules, rule not a table): 1.17¶3 |
| `unicode-props` (534-606) | categories, scripts, namespaces, refusals, `-i` rule, the six large names, Unicode pin | 1.17.1¶1-¶3 (counts N/A-DROP; the six names SUPERSEDED) |
| `-f` family (616-669) | hidden from `--help`; deny/force; engine-selecting three; `--work-budget` separate; `-futf-check`, `-fstartpos-guard=align`; `-fcomments` | 1.18¶1-¶3 (the long flag enumeration SUPERSEDED by a pointer to tuning.md, which owns the list) |
| 1.1 (671-731) | file operand compile mode; target list; implicit `rx`; library builds nothing; `-o` three forms; `--target`; `-I`/`--lib-path`; `lib <store>` refused | 1.1¶1, 1.1.1¶1-¶5, 1.1.2¶1 |
| 1.1 `-I` / `--analysis` (733-748) | analysis search path; fill-only `--analysis`; legality | 1.1.2¶1-¶2 |
| 1.1 lib (750-769) | lib read; closure order; dedup; duplicate refused; own scope; group visibility | 1.1.3¶1 |
| 1.1 composition (771-905) | configs later-wins; block directives; file wins on its axes; `--engine` the one exception; raw line same axis; flags union; `tune` not an exception and message; no `--force-tune`; `--analysis` fill-only; raw `pcrec` line re-parsed; `rx_info.name`; `FILE:LINE` | 1.1.4¶1-¶10, 1.1.3 (the w235/K86/D93/D123 attributions HISTORY) |
| 2 intro (906-919) | TEN dumps, no pattern/-o, table contract, count reconciliation | 2¶1 (the count reconciliation HISTORY) |
| `--list-syntax` (921-937) | 17 columns; `status`/`built` orthogonal; `family` | 2.1¶1 (the wave-E anecdote HISTORY; the 17 columns are registry.md §2) |
| `--list-verbs` (939-944) | two tables; `forms` measured | 2.2¶1 |
| `--list-families` (946-956) | one line per family; no `--flavour` | 2.3¶1 (the floor 60 N/A-DROP; `built` "ANDed" now "combined", the exact rule is registry.md §5) |
| `--list-axes` (958-975) | axis registry; memfn section; no `--flavour` | 2.4¶1 |
| `--list-definitions` (977-997) | columns, joins `--list-syntax`, takes `--flavour` | 2.5¶1 (the `<builder>` wording SUPERSEDED, pointer to registry.md §9) |
| `--list-limits` (999-1016) | columns and kinds; one source with the `#define`s; `limits_check.sh` | 2.6¶1 |
| `--list-schema` (1018-1053) | two sections; one derivation; trailer comments; no `--flavour` | 2.7¶1 |
| `--list-source` (1055-1079) | rows in file order; four sections; value slot; exit statuses; `--resolved` not built | 2.8¶1 |
| `--list-analyses`/`--list-analysis` (1081-1095) | as stated | 2.9¶1 |
| `--emit-ir` (1097-1121) | a query; VM-only; table-contract TSV; ir_listing.md; derives from the emitter's walk | 2.10¶1 |
| `--emit-facts` (1123-1146) | a query; per-encoding compiles; refuses `--flavour`; two sections; debug listing | 2.11¶1 |
| `--explain` / `--flavour` (1148-1156) | cross-source query; exit 3 on dissent; only `pcre2` | 2.12¶1, 2¶1 |
| `--count-groups` (1158-1165) | parse only; prints the count | 2.13¶1 |
| `--probe-ask` (1167-1180) | internal, test-only; CONSTRUCT is its own second argument | 2.14¶1 |
| 3 exit codes (1184-1201) | 0 / 1 / 3 and the separate vocabularies | 3.1¶1-¶2 (the case11 sweep counts N/A-DROP) |
| 3 class tag (1203-1230) | position stable, four closed classes, sentence not a contract, stderr only | 3.2¶1-¶4 |
| 3 D26 tiers (1232-1259) | four tiers restated caller-side | 3.3¶1-¶4 |
| 3 requires module (1261-1267) | the permanent discharge | 3.4¶1 |
| 4 (1269-1301) | no runtime; no multi-pattern unit; no `--lib FILE`; `--emit-ir` ships, `--emit-dot` does not; `--trace` ships | 4¶1-¶4 (the plan-row status SUPERSEDED/N/A-DROP; the `--lib-path` "reads no contents" clause SUPERSEDED, §3 item 16) |
| revision history (1303-1365) | dated change log | HISTORY (cli_record.md) |

## 5. Citations re-pointed

- Citation scan: limits.md 283 citations scanned (floor set 140), cli.md 96 (floor 48); floors in `tests/spec_history/cite_floors.tsv` are half of measured.
- Line-number citations rewritten: for `limits.md:NNN` six sites (`docs/design/dec_fallback.md`, `docs/dev/lanes/iface_digest.md`, `rel13_report.md`, `rel1pre_facts.md` x3) became section numbers (`rel1pre_facts.md`, `dec_fallback.md`) or "the old `limits.md` line 779" (the two that quote a defect in text that no longer exists). For `cli.md:NNN` 27 sites in `docs/design/`, `docs/dev/lanes/` and `docs/dev/reviews/` (frozen design, lane and review prose) became "`cli.md` (old line NNN)", which names the old file's line without being a citation of the new one. `studies/specclean/*.tsv` also carry five `cli.md:NN` strings; they are frozen data and the check does not scan them, so they were not edited.
- Two false positives of the citation scan were reworded (a design script's "its limits (§4.3 ...)" and `docs/dev/spec_survey.md`'s "or point to limits.md), §6.3": a spec name followed by a `§`); three more where the short form `SN` matched ("S11" in `w12_report.md`, "(`cli.md`), §15" in a review).
- Section-name cites of limits.md in `src/core/CLAUDE.md` ("The size-cap ladder", "Size limits and the prefix") now give the number (§8.4, §8.2). Comment-only mentions in `src/` and `tests/` name the doc or a section that still resolves (`§3.1`-`§3.9`, `§8`, `§8a`, `§5`); `src/core/compile.c`'s refusal text quotes the heading "Handling an oversized artifact" (limits.md §8.8), which still exists by that name; changing the quoted text is a diagnostic change, not made here.
- Not edited (append-only ledger): `memfn/docs/responses.md:148` ("registry.md §6 / table_contract.md rule 5 / cli.md"), a bare `cli.md` mention with no section. `requests.md` cites neither doc by section.

## 6. Baseline and floors

- `tests/spec_history/baseline.tsv`: the `limits.md` (5 rows) and `cli.md` (5 rows) lines removed; both docs are held at zero markers with no allowlist row.
- `tests/spec_history/cite_floors.tsv`: `limits 140`, `cli 48`.
- Checks that read these docs' text: only `tests/registry/limits_check.sh` (part 2 finds each anchored value, comma-grouped, inside the section named by the `anchor` column). The new limits.md keeps every number in its anchored section (3.1, 3.2, 3.3, 3.5, 3.6, 3.7, 3.8, 3.9, 8); the section extraction matches the heading by its leading number, so the §8 text includes §8.1-§8.8 and ends at `## 8a.`. `docs/spec/CLAUDE.md`'s limits entry says so. No check reads cli.md's text.

## 7. Validation

- `make strict`: `strict: whole tree compiles clean with -Werror -Wshadow`.
- `make test-spec-history`: `checks passed: 100` / `checks failed: 0` (was 82/0 at specreg; adds limits and cli numbering/toc/cites and their zero marker counts).
- `bash tests/registry/limits_check.sh` (the file `run_registry_tests.sh` chains): `checks passed: 37` / `checks failed: 0`.
- `make test-cli` (6 s per docs/testing.md): `cases failed: 0`.
- `make test-stackdepth` (used to re-measure §5): `checks passed: 5`, `checks failed: 0`, `known states pinned: 1`.
- NOT run (box hold): `make test`, mech, test-axes, san. No file under `src/`, `cli/` or `lib/` changed except `src/core/CLAUDE.md` (docs); no emitted byte, no `--help` text, no abi.

## 8. Open questions (not resolvable by reading the code; not guessed)

1. `cli/main.c`'s `--help` says `-i` is "match case-insensitively (ASCII letters)", but the code folds by encoding (Unicode simple fold under `-e utf8`; Latin-1 pairs under `--ucp`). The spec states the code. The help line is `--help` output, so changing it is a contract event for the owner of `cli/main.c`.
2. `tests/registry/limits_check.sh`'s header and `src/core/limits.def`'s comments still describe the pre-rewrite limits.md text in places (for example "limits.md §3's prose"); the anchors still resolve, so left (comment-only, other CLAUDE.md and header maintenance).
3. `docs/spec/CLAUDE.md`'s `rxt_format.md` and other entries carry dated bracketed narrative of their own; they are other docs' entries, left.
4. `src/core/compile.c` quotes the heading "Handling an oversized artifact" in a diagnostic. It resolves by heading text today; a refusal that cited `limits.md §8.8` would survive a heading rename, at the price of a diagnostic-text change.
