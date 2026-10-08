# decfbB0c report: B0 items 7 (`--order`) and 9 (fallback call graph)

Base `6ebe14d7` (lane/decfbB0c off lane/decfbB0; src moved since `42ab7c25`).
No change under src/, cli/, lib/. emit_sweep.py untouched.

## Item 7: `scripts/trace_diff.py --order SLOT=ordered|set`
Design: repeatable; SLOT = the record's first field. Records are partitioned
by slot per (pattern, arm). A slot named `ordered` is compared as the
sequence of that slot's records only (other slots interleaved between them do
not matter); `set` compares its SET; every unnamed slot follows the default
(`--unordered` -> set, else ordered) and the unnamed slots are compared
together as one subsequence (cross-slot order among them still held). With no
`--order` the code path is the old one. API: `compare(a, b, ..., order={slot:
"ordered"|"set"})`, signature backward compatible (new trailing kwarg); a bad
mode in the API raises ValueError, a bad CLI spelling (`X=sorted`, `X`, `=set`)
exits 2.

Tests (`scripts/tests/trace_diff.py.test`, pure python): 30 checks, 30 pass
(was 17; 13 new). New: clean twin; X-swap passes with X=set, FAILS with
X=ordered (also with Y=set, and under `--unordered` + `--order X=ordered`);
Y-swap passes with Y=set, fails with Y=ordered; the X-pair intact but
re-interleaved with Y passes with both ordered (interleaving ignored) and
fails by default; unordered default passes the X-swap; 3 bad spellings -> 2.
Case (ii) (reorder in an ordered slot, interleaved with a set slot, caught only
for the ordered slot) = `order-swap-x-caught-y-set` vs `order-x-ordered-y-swap-ok`.

S-I2 both ways (the fallback slot's order downgraded to SET): throwaway edit
making the parsed `--order` ignored (`order = {}` after parsing) -> 4 of 13 new
tests go red (order-swap-x-set-ok, order-x-ordered-y-swap-ok,
order-x-ordered-ignores-interleave, order-overrides-unordered; 26/30). Reverted;
30/30. In the real use (`--unordered` default, fallback slot `ordered`) the
detecting case is `order-overrides-unordered`.

## Item 9: `call_graph.py --family fallback`
`--family start` (default) BYTE-IDENTICAL: `cmp` of stdout (2,348 lines) and
stderr (`# sites 164`) before/after the edit; also `sabotage_anchors.py` on the
start inputs byte-identical before/after (tsv + summary) after its additions.

Fallback family. Roots (12): compile_driver (holds the T3 gate), fit_select,
fit_rung_denied, fit_rung_of, fit_collapse_applies, fit_anchored_applies,
fit_premul_applies, fit_prefilter_applies, fit_always, prefilter_decision,
size_term_choose, esel_of. Seeds are DERIVED by running state_readers.sh and
reading its `# E/L/R/RQ/S/V/D` header lines (exit 2 on an empty source, a
vanished root, a failing script): D names that are definitions = 14 seed
definitions; the rest of D (a local, lang_nullable_declinable) and E/R/S/RQ/L/V
are member/enum TOKENS matched as the script matches them (qualified `.`/`->`,
L only in compile.c). Reach from roots = 1,498 of 2,084 definitions, so the
start family's transitive "reaches a seed" gives 761 (compile_driver reaches the
whole compiler): useless. The family is therefore the ONE-hop direct readers of
the seeds plus the roots: **53 members** (14 seeds). Judgment call: it is a
superset with some incidental readers (pcrec_ast_stamp, pcrec_ctx_nomem, ...);
conservative for re-runs. fit_always is a one-line definition, which the start
parser never saw; one-line definitions are parsed in fallback mode only (to keep
the start output byte-identical).

sabotage_anchors.py: needed no consumer change for the graph; added
`--final LABEL` (re-run label of an untouched owner; fallback uses after-B6),
B0..B7 in the commit order (the summary's per-commit counts were blank), and
`--edit-names` (re-run at a commit whose edit-set text NAMES the owner, or which
rewrites a `def` the owner's body names): the plan-level forms of --step's
reach hop 0 / caller hop. All default-off.

Result (`dec_fallback/sabotage_anchors.{tsv,summary}`): 538 sites / 520 rows,
COUNT_MISMATCH 0, FAMILY_ROWS 85 = 11 RE-AIM + 74 RE-RUN (start graph: 126),
RE-RUN by commit B2 3, B3 12, B4 2, B5 14, after-B6 57. UNRESOLVED_SRC 1 =
S571 (memfn_sites.c:35), pre-existing, rc 2 as before. **RE-AIM: the same 11 rows
as design §4.4**, same commits (B2 S421/S423; B3 S253/S259; B4 S102/S165/S216/
S272/S612; B5 S238/S422).

RE-RUN vs rev 1's hand list (computed `rerun_at`; B0 has no B diffs, so
hunk/reach via `--step` cannot run until each B commit exists):

| row | owner | computed | verdict |
|---|---|---|---|
| S237, S252, S420 | fit_*_applies | B2 (edit-names: fit_rungs[] row lines name them) | reproduced; rev 1's B3 half is the walk call, no edit-set text names them: `--step` at B3 |
| S189 | build_anchored_dfa | after-B6 | MISSING B3: reads size_drop_rung written by a row; only `--step` B3 sees it |
| S191, S192 | size_term_choose | after-B6 | MISSING B3: called from a row's action; the edit set has no line naming it; `--step` B3 |
| S193 | compile_driver | B3+B5 | reproduced B3; B5 added (PFLW ternary/size_term_why are edited inside compile_driver) |
| S64, S176 | prefilter_decision | B3+B4 | B4 reproduced; B3 ADDED by token `retry_collapse` occurring in a COMMENT in prefilter_decision (select_engine.c:788): spurious, but the comment goes stale at B3 |
| S40 | pcrec_select_engine | B5 (calls-rewritten: esel_of is a `def` entry) | reproduced |
| S224, S225, S226 | vm_emit_stamps | B5 | reproduced |

ADDED (not in rev 1's list), all owner compile_driver, B3+B5: S166, S169, S178,
S257, S261, S306, S437, S440 (edit-set spans of both commits fall in its body;
rev 1's hand list missed them; genuine, as compile_driver is rewritten at B3
and B5). 57 further family rows re-run once after-B6 (emitters etc.: readers B
keeps on purpose, §2.1 class 4).

Non-vacuity (scratch copy under build/scratch, never the real src):
- esel_of renamed everywhere: rc 2 (state_readers: declared name vanished).
- compile_driver definition renamed: rc 2 (state_readers rc 1, call_graph
  fails closed). EngineFit typedef renamed: rc 2 (E empty). setjmp block
  respelled: rc 2 ("CATCH is EMPTY").
- `.chosen` renamed in emit_dfa.c only: family 53 -> 48 (emit_search_head,
  emit_unanchored, emit_attempt, ... drop out): seeds really drive membership.
- Owner resolution hard: scratch with S571 row removed -> rc 0; plant an
  unparseable file-scope line + a row anchoring it -> rc 2, "UNRESOLVED
  S999-plant".

state_readers.sh re-run: 417 lines (9 header + 408 code lines), the SAME 408 as
`42ab7c25` (rev 2 said 408); diff = the header sha and shifted line numbers
only (names and text columns identical after stripping line numbers). Committed.

Files: scripts/trace_diff.py, scripts/tests/trace_diff.py.test,
docs/design/start_table/{call_graph,sabotage_anchors}.py,
docs/design/dec_fallback/{call_graph_fallback.txt, sabotage_anchors.tsv,
sabotage_anchors.summary, state_readers.txt}, and the four CLAUDE.md files.
Commit message of 6ebe14d7 says "17 new tests": it is 13 new (30 total).
