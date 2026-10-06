# LIGHT D6 panel — the unified start table (docs/design/start_table.md), 2026-10-06

Two read-only critics; their full files beside this one:
`2026-10-06-r-starttable-crit-sound.md` (opus, soundness of the no-mover claim)
and `2026-10-06-r-starttable-crit-checks.md` (sonnet, the controls that prove it).

**Verdict: no BLOCKER; NOT build-ready.** Neither critic found an input on which
the refactor, as written, moves an answer past all of its own controls. Both
found the inventory and the proof incomplete. Every finding is ACCEPTED; the
revision lane `starttabrev` applies them, then a focused re-check.

## Dispositions (all ACCEPT, fix in the revision)

| id | finding | disposition |
|---|---|---|
| sound M1 | VM hybrids with an ENG_ATTEMPT prefilter (any `^`/`\A`/`\G` pattern) are attempt-route customers, misfiled as DFA; such an artifact asks BOUND on two routes; D-2b occurs inside one artifact; the census double-counts | re-inventory by `job->engine` of the PREFILTER, not `fit.chosen`; per-(slot, route) within one artifact made explicit; census fixed |
| sound M2 | K65 set-rest (`emit_req_set_rest`, emit_dfa.c:1265) and K66 whole-run (`req_run_tests`, :1035) are presence decisions missing from the inventory (S277/S278/S316 sit on them) | add as rows; C1 trace covers them |
| sound M3 | offset-set admission lives in src/opt/prefix_k.c (cost-model bar, "move off offset 0", reads the prior); not mentioned; S187/S188 uncovered | bring into the row's predicate; census + anchors |
| sound M4 / survey | a fifth disagreement D-4: run pin vs offset-k pick — run-pinned unreachable when the pickers disagree, systematic under utf8 (`abc$`) | list as D-4; preserved by the no-mover refactor; its fix is a separate ruled change ([TIE-ALIGN] re-scope) |
| sound M5 | P2, R3, N7, `attempt_cand` restate BOUND's predicate instead of reading it through the walk; §1.3's "none restates" is false | make them readers of BOUND; add TYPED HANDOFFS between slots (Frank's re-entry question: VM failure → retry → prefilter; reverse walk → next; window → verifier; handoff → scan start) as a checked slot graph |
| sound M6 / checks M1 | ≥9-10 sabotage rows need re-aiming, not 6 (S169, S263, S371, S222, ...); 9 `SAB_FILE2` rows outside the 207; family list hand-written | derive the family from the call graph; a per-commit gate "every SAB_BEFORE occurs exactly once in the child tree" |
| checks M2 | C0 cannot fail on its own plumbing: dropping `--extra -e utf8` on both sides passes | floor per arm on patterns that DIFFER from default (the critic's measured deny deltas 8..604 are the seed) |
| checks M3 | trace under-specified | per-pattern ordered key; reference regenerated from the parent every commit; print at the walk's return; the trace build never the byte-sweep build; the C2 both-walks oracle tests only the filter (predicates shared by pointer) — say so and add an independent control |
| checks M4 | §3.4's gap list stale: set-leads IS byte-visible (`-fno-req-set-lead` 14 byte / 8 utf8); B1/B2 no anchor; H1 census reads a constant; P4/P5 share "emitted"; row_census has no deny arm (R6 reach asserted, not counted) | per-row control = deny-delta count; add the deny arm; anchors/witnesses for B1/B2/H1/P4/P5 |
| sound m1-m6, checks minors | C5 leaves stamps/listing reading facts directly (two derivations); `dfa_search_is_pinned` readers compare row pointers; `match` axis projection vs §2.5; `-fprefilter-collapse` arm omitted; trace mapping self-authored for inline sites; `strcmp(spec,"all")` trips the widened name check; new checks lack sabotage rows; emit_sweep floors stale; argv streams drop flags/-i; `used` is per-fact; no witness injection; registry.md:267 names `dfa_select` | fix or state in the revision, each line by line |

## Lesson

The design's "selection identity by construction" held for every site it
NAMED; both critics found sites it did not name. For a no-mover refactor the
inventory is the claim — derive it (call graph, deny deltas, anchors), never
hand-list it.
