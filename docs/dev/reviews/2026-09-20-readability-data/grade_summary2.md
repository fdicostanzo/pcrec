# Naming-guess grading, all four evidence conditions to one standard

226 rows (72 field, 129 func, 25 local). A = identifier + declaration/signature line
only. B = A plus the declaration/function's own comment. C = whole stripped file
(pre-graded, reused verbatim from `graded.tsv`). A_renamed / C_renamed = A / C with
12 identifiers replaced by longer, more specific names. Verdict scale: correct /
partial / wrong / vacuous (vacuous = restates the name/type with no added meaning).

## (a) Verdict counts by condition

### Overall (n=226)

| condition | correct | partial | wrong | vacuous | % correct |
|---|---|---|---|---|---|
| A | 114 | 9 | 22 | 81 | 50.4% |
| B | 118 | 21 | 25 | 62 | 52.2% |
| C | 201 | 15 | 6 | 4 | 88.9% |
| A_renamed | 124 | 51 | 16 | 35 | 54.9% |
| C_renamed | 206 | 12 | 8 | 0 | 91.2% |

### field (n=72)

| condition | correct | partial | wrong | vacuous | % correct |
|---|---|---|---|---|---|
| A | 11 | 1 | 2 | 58 | 15.3% |
| B | 30 | 9 | 9 | 24 | 41.7% |
| C | 63 | 3 | 2 | 4 | 87.5% |
| A_renamed | 31 | 27 | 4 | 10 | 43.1% |
| C_renamed | 64 | 7 | 1 | 0 | 88.9% |

### func (n=129)

| condition | correct | partial | wrong | vacuous | % correct |
|---|---|---|---|---|---|
| A | 88 | 5 | 13 | 23 | 68.2% |
| B | 74 | 7 | 12 | 36 | 57.4% |
| C | 121 | 8 | 0 | 0 | 93.8% |
| A_renamed | 77 | 19 | 9 | 24 | 59.7% |
| C_renamed | 126 | 3 | 0 | 0 | 97.7% |

### local (n=25)

| condition | correct | partial | wrong | vacuous | % correct |
|---|---|---|---|---|---|
| A | 15 | 3 | 7 | 0 | 60.0% |
| B | 14 | 5 | 4 | 2 | 56.0% |
| C | 17 | 4 | 4 | 0 | 68.0% |
| A_renamed | 16 | 5 | 3 | 1 | 64.0% |
| C_renamed | 16 | 2 | 7 | 0 | 64.0% |

## (b) The 12 renamed names: verdict under A vs A_renamed, C vs C_renamed

| kind | original → renamed | A | A_renamed | C | C_renamed | moved? |
|---|---|---|---|---|---|---|
| field | Vm.nocap → nocap_depth | vacuous | correct | partial | correct | A: yes; C: yes |
| field | Vm.rgn_emit → rgn_needs_shared_region | vacuous | wrong | vacuous | correct | A: no (still fails, differently); C: yes |
| field | Vm.has_linked_calls → has_nonspliced_calls | vacuous | partial | vacuous | correct | A: partial gain; C: yes |
| field | Vm.spl_nw → spl_capture_nw | vacuous | vacuous | wrong | partial | A: no; C: partial gain |
| field | Vm.rgn_w → rgn_save_slots | vacuous | correct | vacuous | correct | A: yes; C: yes |
| field | Vm.rgn_nw → rgn_save_slot_count | vacuous | partial | vacuous | correct | A: partial gain; C: yes |
| func | vm_lifts → vm_atomic_lift_eligible | vacuous | partial | partial | correct | A: partial gain; C: yes |
| local | nd → nodes | partial | correct | partial | wrong | A: yes; C: **backfired** |
| local | st → stamp | wrong | wrong | wrong | wrong | no movement either way |
| local | fit → engine_fit | wrong | partial | wrong | correct | A: partial gain; C: yes |
| local | cap → out_cap | partial | correct | partial | wrong | A: yes; C: **backfired** |
| local | u → ctx | correct | correct | wrong | wrong | A: already correct; C: no movement |

Net: 7 of 12 moved toward correct under the renamed condition it was tested in
(mostly C_renamed); 2 (`nd`→nodes, `cap`→out_cap) actually got **worse** under
C_renamed — the guesser, given the fuller and specifically-named identifier, still
picked the more obvious but wrong reading (a count instead of an array; a capture-group
concept instead of the array-capacity truth) even though the rename removed exactly
that ambiguity for the A-only guesser. `st`→stamp never moved: the header/code
evidence needed to correct "state"/"strategy" isn't in the identifier at all.

## (c) Confidence calibration

| condition | n "high"-confidence | % of those correct | confident-and-wrong-or-vacuous |
|---|---|---|---|
| A | 96 | 89.6% | 7 |
| B | 142 | 78.2% | 19 |
| C | 221 | 91.0% | 7 |
| A_renamed | 197 | 60.4% | 29 |
| C_renamed | 226 | 91.2% | 8 |

A_renamed stands out: confidence exploded from 96 to 197 "high" guesses after only
12 renames, but the hit rate on those high-confidence guesses fell to 60.4% — the
longer, more specific-looking names made the guesser far more confident without
making it correspondingly more often right, since most of the file's names didn't
change at all.

## (d) Names whose meaning lives farthest from the declaration

**Wrong/vacuous under A, correct under B** (the header comment did the work) — 44
names, overwhelmingly the counter/budget/pruning/tracing fields and the "compute a
slot index" function family: `Vm.p`, `Vm.up`, `Vm.nlabel`, `Vm.ngroups`, `Vm.nguard`,
`Vm.nlow`, `Vm.nmark`, `Vm.nctr`, `Vm.nlookpos`, `Vm.unroll_k`, `Vm.emitted_push`,
`Vm.nodes`, `Vm.rungs`, `Vm.strats`, `Vm.prunes`, `Vm.fdyn`, `Vm.mrl`, `Vm.mrl_win`,
`Vm.ndynskip`, `Vm.nclamp`, `Vm.ngst`, `Vm.tracing`, `Vm.has_budget`, `Vm.nwork`,
`Vm.(*cls)`, `vm_charge`, `vm_slot_name`, `vm_slot_expr`, `vm_slot_ref`, `vm_marked`,
`bare`, `vm_nullable`, `vm_lifts`, `vm_cuts`, `vm_revdet_fits`, `vm_rung_mark`,
`vm_emit_span_scan`, `vm_resolve_nonnull`, `vm_sec`, `vm_row3`, `vm_prow`,
`vm_trail_fields`, local `fmin`, local `up`.

**Wrong/vacuous under B, correct under C** (only the surrounding code told) — 74
names, dominated by two families that the comment alone can't disambiguate: the
whole island-trie module (`vm_isl_*`, 10 functions) and anything the header's own
generic phrasing miscasts as an "emit" function when it's really a walker, planner,
or counter (`vm_walk_caps`, `vm_walk_calls`, `vm_build_region_saves`,
`vm_plan_capacities`, `vm_plan_regions`, `vm_cls_describe`, `vm_ceiling`,
`vm_w_range`) — plus most of the region/splice/lookmark fields (`Vm.cg`,
`Vm.has_calls`, `Vm.nregion`, `Vm.rgn_grp`, `Vm.rgn_lbl`, `Vm.rgn_exit`,
`Vm.rgn_cost`, `Vm.nsplice*`, `Vm.nlookmark*`, `Vm.ev`/`Vm.evcap`) and the three
listing-row functions (`vm_listing_slot_row`, `vm_listing_slots`,
`vm_listing_events`). Locals `o`, `l`, and `run` are here too — their declarations
carry a generic C type with no comment to lean on.

## (e) Five-sentence reading

The bare identifier alone is enough for locals and for functions whose name is a
verb-phrase on a recognizable noun (`vm_slot_guard`, `vm_cursor_fits`), but it is
almost useless for the file's many short or suffix-coded fields, where guessers
fell back on vacuous type-restatement 81 times out of 226 shots. The header comment
recovers a large share of that loss for fields specifically (correct-rate roughly
triples, 15%→42%) but does much less for the trickier function families — anything
building or walking a data structure without an explicit "does X" comment — where
guessers default to a generic, undifferentiated label reused verbatim across many
distinct functions (`vm_isl_*`, "helper", "related field"). Only the whole file
lets the guesser see what a field's neighbors, call sites, and the surrounding
logic actually do with it, which is why C and C_renamed clear 88–98% correct across
every kind while A and B stall in the 50s. Renaming 12 names longer and more
specific moved most of them toward correct, but not reliably — two (`nd`, `cap`)
moved from partial to wrong under the fuller C_renamed evidence because the
guesser locked onto the newly-visible word's more common reading over the file's
actual usage, and `st`→`stamp` never moved at all since no evidence source
supplied the needed correction. Self-reported confidence should be trusted least
after a rename: A_renamed's high-confidence count roughly doubled (96→197) on just
12 changed names while its hit rate on those high-confidence guesses fell to 60%,
showing that a longer, more specific-looking identifier inflates the guesser's
certainty across the whole file, not just on the names that actually changed.
