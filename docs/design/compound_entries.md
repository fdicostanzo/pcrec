# Every exported entry as a compound controller over shared PARTS, and the dial deciding what is inline (ASSESSMENT / DESIGN NOTE, revision 4)

Status: PROPOSED, assessment and design only, nothing built. **Revision 4** (lane
`cmprev4`, 2026-10-16, from main `8eec6f874`, abi 78) applies D163 addendum 8: the part
layout becomes CALLER-SETTABLE CONTROLS, and the dial's five positions become PRESETS over
them. Read §R4 first. **Revision 3** (lane
`cmprev2`, 2026-10-16, from main `74ac73f7f`, abi 78) answers the D6 panel
`docs/dev/reviews/2026-10-16-r3-compound-entries.md` (3 blockers, 15 majors, 9 minors, all
ACCEPTED by the manager): read §R3 first. **Revision 2** (lane `cmprev`, 2026-10-16, from
main `7ee8d7ae7`, abi 78) applied Frank's rulings on revision 1's Q1-Q5 (D163 addendum 7),
§R2. Revision 1: lane `cmpentry`, 2026-10-14, from main `d6e7fa993`, abi 78. Charter: Frank,
2026-10-14: "we have compound artifacts. are these pieces better composed in compound
functions from parts? we issue several function interfaces, would these parts compose into
the individual compound functions?" and "we have the dial controller. if we set it all up as
compounds, the dial could decide whats inline". The model assessed is the manager's framing,
Frank-endorsed: every exported entry is a compound controller (D163, `compound.md`) over a
small set of shared parts, and the INLINE-vs-SHARED layout of those parts is a row of the
dial's pinned table ([OPT-DIAL], D103).

Evidence is compile-only plus clockless instruction counts: gcc 15.2 `-O2` on the Linux dev
box (Zen 4), `.text` and per-function sizes from `nm`/`size`, call edges from `objdump -dr`,
and dynamic instruction counts (Ir) from `valgrind --tool=callgrind`. No clock was read. The
probes and their outputs are in `compound_entries/` (own CLAUDE.md). Revisions 2 and 3
measured nothing new; revision 3's facts about the emitters were read from the source at
`74ac73f7f` and are cited by symbol.

---

## R4. What revision 4 changed (D163 addendum 8, ruling → section)

D163 addendum 8 (Frank, 2026-10-16): "we need to have this be switches or a --X=y type
parameter so that someone can set this directly. then the tuner simply dials in the
switches. in practice, this is a huge impact on .o size and should have finer grain
control." Revision 3 decided the layout from the POSITION (rows P4-P9 each named a position).
Revision 4 decides it from CONTROLS, and a position only supplies default control values.

| ruling item | what changed | where |
|---|---|---|
| controls finer than the five positions | THREE valued controls: `--part-layout=CLASS:V` (per part class: `auto`, `shared`, `inline`), `--part-inline-rank=R` (a rank threshold: `none`, `R3`..`R0`, `measured`), and `--part-residual=V` (the layout of every subject part no class value and no threshold decided). Four classes: `prefilter`, `compound`, `find`, `wrap`. The owned VM entry chain keeps its existing control, `--vm-entry-shape=N` | §3.2.2 (the controls), §3.2.3 (why this grain) |
| the positions become presets | each position is a declared row of control values in the dial's pinned table, first-match by position (D103's shape). The rows set only the threshold and the residual; every class cell is em-dash. A `†` cell resolves as unset | §3.2.4 |
| an explicit switch overrides the preset | each control resolves on its own: the caller's value if set, else the preset's. No provenance-dependent ordering is needed, because the presets never set a class value | §3.2.4, §3.4 (row K) |
| the part table | the position rows P4-P9 become control rows: P4-P6 (class value), P7 (rank ≥ threshold), P8-P10 (residual). Constraint rows P1-P3 still come first, so no control overrides them | §3.4 |
| how a held request is reported | a constraint row that holds an explicit request is a selection outcome, never a refusal (tuning.md §2.21¶3's rule). It is stamped (`/held` on that class's token in `<PREFIX>_PART_LAYOUT`) and listed per part by `--emit-facts` | §3.4.2 |
| Q6 RULED | `+1` with no `θ_hot` falls back to the `0` layout, with the two stamped reasons. Under switches the decline belongs to the threshold VALUE `measured`, not to the position: T1/T2 resolve it to `none`. With `+1`'s preset alone the object is `0`'s exactly | §3.3, §3.4 (T1/T2), §5.4 |
| `θ_hot` gets a direct manual setting | `--part-inline-rank=R2` (say) bypasses the measurement set. Only the value `measured` reads it | §3.3 |
| .o size | each control's expected size and speed direction, with numbers from three new SCRATCH-GRADE compile-only probes; every time number is labelled UNMEASURED | §3.2.5, `compound_entries/rev4_*` |
| the override spelling was filed to [IFACE-PUSH] as U10 | SUPERSEDED: the controls are designed now. They are valued parameters, so they consume no flag bits; the CLI spelling and the field representation are proposals that [IFACE-PUSH] may respell | §3.7, §5.3 (U10 struck) |
| stamps | `<PREFIX>_PART_LAYOUT` returns (revision 3 dropped it because a position determined the layout; it no longer does). It is written only on an artifact where some control resolves to a non-trivial value. `_THETA` folds into its `rank=` token. `_WHY` stays, for the decline | §3.4.1 |
| Q7-Q9 | reframed for the switch form, still as discussion with leanings. Q9 changes most: every row is now reachable by flags on corpus artifacts, so synthetic witnesses shrink to rows whose SUBJECT the corpus lacks | §5.5 |
| NEW-DATASET lens | every new item (the preset columns, the class table, the fields, the stamp vocabulary, the listing section) names its home and its contract section | §3.9 |
| D80 | the spec hunks are listed as OWED AT E1, because the controls are caller-observable from E1 (not from E1′). `docs/spec/` is not written now | §3.9, §5.1 |

Unchanged from revision 3: the invariants I1-I5, the part population (§3.1), edge rank and
`callers` (§3.2), the constraint rows P1-P3, the wrapper table, the checks' independence
(§3.6), the iterator's consumption (§3.8, renumbered rows only), §4 and the findings. E0 is
unaffected (addendum 8: "E0 ... is unaffected").

**Measured in revision 4** (scratch-grade, compile-only, no clock): `.text` and whole-`.o`
bytes per part class (`results/rev4_osize_cls.tsv`), per witness and link regime
(`results/rev4_osize.tsv`), and the owned VM entry chain at its four rungs on three larger
witnesses (`results/rev4_vmshape_o.tsv`). §3.2.5 reads them.

Sabotage: revision 3's S999-S1008 are re-aimed at the renumbered rows. Three new plants
(precedence, held reporting, preset resolution) have NO ids; the manager allocates them
(§3.6).

---

## R3. What revision 3 changed (panel r3, finding → section)

The three blockers had one root. Revision 2's table did not respect attributes the emitters
already write: L0 assumed "no attribute" at `0`, and L4 ran before `+1`'s decline. One
restructuring discharges all three:
- an ARTIFACT table evaluated first (T0 `0` and `†` cells, T1/T2 `+1`'s declines);
- an OWNED constraint row P1 ahead of every part row;
- I4: the `0` layout is the owner's layout.

| finding | sev | what changed | where |
|---|---|---|---|
| CE-1 | BLOCKER | `+1`'s decline is artifact row T1, ahead of every part row, so it gives the `0` object exactly. The load-bearing [OPT-1] `_deep` `noinline` is OWNED (row P1), kept at every position. P3 (single caller) keeps the `0` layout and adds no attribute | §3.4 (T1, P1, P3), §3.1 (A2) |
| CE-2 (+F7) | BLOCKER | A1 (the VM entry chain) is OWNED by P1, so no position row writes its functions. The two dial rows are "co-resident, not unified", with disjoint subjects, and that is checked | §3.4 (P1 note), §3.7, §3.6 (disjointness) |
| F3 (+CE-11) | BLOCKER | I4: the `0` layout is the owning design's (today's attributes, and after I1 `findall_iter.md` §2.2's). T0 replaces L0. §2.2's table is KEPT as the `0` cell's content. P2 keeps §2.2's explicit `static noinline` on label-table bodies | §3.0 I4, §3.4 T0, §3.8 |
| CE-3 (+F2) | MAJOR | the part population is enumerated in three classes (subject / owned / not a part) and every emitted function must fall in one; `_deep`, clskit's `<p>_wcls%d`, the DFA state helpers and the λ row are named | §3.1 |
| CE-4 | MAJOR | each adjacent pair has an emitted witness or is UNWITNESSED with its candidate population; `<p>__q_match` withdrawn (not emitted); the 25-29 Ir figure labelled R2; the census counts per ROW | §3.2 (rank table), §3.2.1, §3.6 |
| CE-5 | MAJOR | `0`/`+1` declared-coincident until a set carries `θ_hot` | §3.2.1 |
| CE-6 | MAJOR | `θ_hot`'s domain gains `none` (stamped); revision 2's "R3 by argument" removed | §3.3, §3.4 T2 |
| CE-7 (+Q9 note) | MAJOR | the expected layout comes from a separate evaluator (stripped `-fno-inline` call graph + owners' attributes + hand rank fixture + policy text), never from the table's derivation; synthetic witnesses carry hand-written expected sets | §3.6 |
| CE-8 | MAJOR | `callers` = distinct functions holding a call site after owned `always_inline` functions fold into their callers; the census compile strips attributes by text in the checker | §3.2, §3.6 |
| CE-9 | MAJOR | a stamp arm diffs every `<PREFIX>_*` except `TUNE`/`PART_LAYOUT_*` against the same position on the cell diff's parent; UNREACHED until the first live cell | §3.6 |
| LK-1 | MAJOR | `entry_rows[]` does not exist; E0 ADDS a per-edge rank column (new data, a shape predicate) and its hand fixture, a precondition of E1 | §3.0 I2, §4.1, §5.1 E0a |
| LK-2 | MAJOR | the per-wrapper legality predicate `forwardable(w)` and the fallback row W2 (`adapt`), with witnesses | §3.2, §3.4 W-table |
| LK-3 | MAJOR | P2/P4/P6 write `noclone` with `noinline`; a check counts clone symbols per part | §3.4, §3.6, S1003 |
| LK-4 (+SIB-1) | MAJOR | one legality fact `copyable(part)`: label table, or computed goto, which on the VM is `may_attr = !has_push`, read rather than re-derived; other refusal causes have zero population, held by the census | §3.4 P2 |
| LK-5 (+CE-13) | MAJOR | I3 is a precondition of the first live cell; the `-fPIC` "no flip" row is qualified | §3.0 I3, §3.4.1, §5.1 E1′ |
| LK-7 (+CE-12) | MAJOR | `<PREFIX>_PART_LAYOUT` dropped (`RX_TUNE` names the position); only `_WHY` and `_THETA` are stamped, by `+1`, from its first live cell, with D80 hunks, D94 readers and the suites named | §3.4.1, §5.1 E1′ |
| F1 | MAJOR | honest recount: one built decision (A1), one designed (§2.2), four fixed writers, the kit's; "past the unification threshold" DROPPED | §3.1, §0 item 5 |
| F4 (+LK-1, CE-4 on R3) | MAJOR | every `findall_iter.md` §2.1 helper listed with callers, rank and row; the retry is not a part; the batch-fill R3 witness HELD with Q2 | §3.8, §3.2 |
| CE-10 | MINOR | the `0` check cites only `emit_sweep.py` against pre-E1 main | §3.6 |
| CE-12 | MINOR | (with LK-7) the decline is an artifact-level row evaluated once | §3.4 T1/T2 |
| CE-13 | MINOR | (with LK-5) the `−1`/`0` pair has no DFA-wrapper population until I3 | §3.2.1, §3.0 I3 |
| LK-6 | MINOR | the seam is inside P1; a fixture asserts {seam} ∩ {not copyable} = ∅ | §3.4, §3.6 |
| LK-8 | MINOR | I5: the layout is rendered after every length decision on every emitter (the K79 render's position); the near-cap refusal check runs on VM, DFA and compound | §3.0 I5, §3.6 |
| LK-9 | MINOR | rows write only on static functions; a negative `-fPIC` test | §3.4, §3.6 |
| F5 | MINOR | §2.2's `I_shared` trigger kept as U1's trigger | §3.8, §5.3 U1 |
| F6 | MINOR | `pcrec_sb_len_decide` and H4 cited by symbol; new citations by symbol | §0 item 3, §2.1, §3 |
| Q6-Q9 notes | — | folded into the questions | §5.5 |
| SIB-2, family sibling | — | `θ_hot` and A1's size term named as sibling cutovers; λ, `--vm-entry-shape`, `-fno-tiered-entry` named as the row's siblings | §3.1, §5.3 U-B |
| unlocks | — | U-T (one attribute-writing table; its check built at E1), U-A, U-B, UNL-1, UNL-2, F5's trigger | §5.3 |

Sabotage ids in §3.6 are PROPOSALS (S999-S1008, allocated by the manager 2026-10-16).

---

## R2. What revision 2 changed (D163 addendum 7, ruling → section)

| ruling | what it says | where it lands |
|---|---|---|
| model | every exported entry is a compound controller over LOCATE / FINISH / STATE parts; one `entry_rows[]`, the controller a column, edges derived | unchanged (§1, §4); restated as an invariant in §3.0 |
| Q1 | the part-layout POLICY is a pinned dial cell per position (D103); only `hot-inline`'s threshold is read from the measurement set (D166), with its mover census | §3.2 (policy per position), §3.3 (the threshold `θ_hot`, its derivation inputs, its decline when absent) |
| Q2 | `0` stays as emitted; FIVE DISTINCT layouts; hard constraints are rows no position overrides | §3.2's five policies and §3.4's first-match table (constraint rows first); §3.2.1 shows where adjacent positions differ and which population makes them differ |
| Q3 | the iterator's parity gate binds `0`, `+1`, `+2`; at `−1`/`−2` the gap is the cell's stated cost | §3.5 (marked RULED) |
| Q4 | E0 before I1; then a short revision of `findall_iter.md`, its panel, then I1 | §5.1 (order unchanged); §3.8 lists what that revision consumes from this row, without editing `findall_iter.md` |
| Q5 | no exported entry calls an exported sibling; static twins; applied where a change already moves the bytes | §3.0 invariant I3; §3.4 keeps H5 OUT of the layout table (it is a linkage rule of `entry_rows[]`, not a position) |
| brief | sibling-of-a-family lens | §3.7 |

Revision 1's §3.2 (a four-policy row with `−2`/`−1` both `shared`) and its §5.4 Q1-Q5 are
superseded; §5.4 now records the rulings and §5.5 carries this revision's own questions
(Q6-Q9).
Nothing measured in revision 1 moved, and nothing new was measured: this revision is a
design-text change.

---

## 0. Answers first

1. **The model fits every exported entry today, with one exception and three gaps (§1).**
   Every matcher entry (`_search`, `_match`, `_match_caps` and their `_in` siblings) is
   already a small expression over a body: `locate-then-finish`, `finish-at-position`, or
   `forward-to-sibling`. The exception is the residuals (`_next_pos`, `_valid_upto`,
   `_var_valid`), which are leaf parts, not controllers. The gaps are the STATE part
   (`rx_iter`, designed, not built), the kit's stream state (D165 add. 1: it needs the state
   part to exist), and captures-on-demand (`select-by-arg`, a filed compound client). Give-up
   codes, callouts/vars and `-futf-check` are already the call-site code table, the vars
   channel and the controller prologue, respectively.
2. **Today each emitter writes its own entries, and gcc decides the layout (§1.3, §2).** The
   DFA emitter, the VM emitter and the compound shell each write their entries by hand
   (`emit_dfa.c:14221-14267`, `emit_vm.c:13779`, `emit_compound.c:115-192`), and
   `entries.c:58-107` restates the call edges in a hand list. No pcrec decision says what is
   inline. gcc decides, and its decision FLIPS with the link regime: under `-fPIC` gcc cannot
   inline one exported entry into another, so the same artifact is 1.5-20% smaller on eight
   of nine witnesses (6.7% larger on the vars witness) and pays a PLT call on every
   exported-to-exported edge (measured, §1.3, §2.3).
3. **What cannot inline (§2.1).** Two hard constraints, both measured as gcc errors: a body
   that keeps label addresses in a static table cannot be copied (the DFA attempt route, which
   includes split's F part: "can never be copied because it saves address of local label in
   a static variable"), and a body with a computed goto cannot be inlined (the framed VM's
   `match_anchored`). Two soft ones: a part with ONE caller must never be shared (it costs
   +112 B and saves nothing, measured on split's Q), and `info`/`main` cannot be static
   (`pcrec_entry_shape`'s request check). A third hard constraint is already in the tree:
   the VM's `has_push` (`vm_plan_entry`'s `may_attr`) is the computed-goto fact (§3.4).
4. **The per-call cost of a shared part is small, and so is the byte saving (§2.2).** A
   static part call costs 5-29 instructions per call over the inlined form (callgrind; split's
   Q about 5, the VM hybrid's prefilter about 25-29). Sharing a multi-caller part saves 0-160 B
   of `.text` (0-5%); inlining every copyable part costs +4% to +21% of `.text` and saves
   2-13% of instructions. An exported sibling call through the PLT costs about 4.8
   instructions per call more than the same call bound locally, in lost optimization as well
   as the stub (§2.3).
5. **The layout controls and the dial's presets (§3), revised for D163 addendum 8.** The
   layout of a PART (a callable static body reached from entries: copied into each caller,
   or one out-of-line static body they call) is set by three caller-settable VALUED controls
   (§3.2.2):
   - `--part-layout=CLASS:V`: per part class (`prefilter`, `compound`, `find`, `wrap`), one
     of `auto` (the owner's `0` layout, I4), `shared` or `inline`;
   - `--part-inline-rank=R`: a copyable part whose hottest edge ranks at or above `R` is
     inlined; `measured` reads `θ_hot` from the measurement set;
   - `--part-residual=V`: the layout of every part that no class value and no threshold
     decided.

   The dial's five positions are PRESETS: rows of control values in the pinned policy table
   (§3.2.4). `−2` = residual `shared`; `−1` = residual `shared` + rank `R3`; `0` = nothing set
   (byte-identical); `+1` = rank `measured` (with `θ_hot` absent or `none`, it falls back to
   the `0` layout, stamped: Q6, RULED); `+2` = residual `inline`. An explicit control beats
   the preset's value for that control. The VM entry chain, [OPT-1]'s `_deep` and the
   encoding seam stay OWNED: no control names them, and a constraint row keeps them ahead of
   every control row. The VM entry chain's own control is the existing `--vm-entry-shape=N`
   (§3.1). Hotness is an EDGE RANK (per-candidate / per-call / conditional / rare), a new
   column `entry_rows[]` must carry, with no profile. The decision is an artifact table
   (control resolution, then `measured`'s declines, then the all-`auto` short cut) and a
   per-part table whose constraint rows (owned, not copyable, single caller) come before
   any control row (§3.4). A request a constraint holds is stamped and listed, never
   refused. Explicit controls are live from E1; each preset CELL stays `†` until its own
   ruled diff with a size AND time measurement (D103 item 3). The controls move `.o` size
   by up to +18% `.text` (the prefilter class, inline) and the owned VM entry chain by up
   to +86% (`--vm-entry-shape`, inline against plain); these are compile-only scratch
   numbers, and every time effect is UNMEASURED (§3.2.5).
6. **Convergence (§4): yes, one declared entry table, `entry_rows[]`.** It is [EMIT-ENTRIES]'
   table with the controller made a column: each row names an entry, its combinator, its
   parts and its mode. The edge list is DERIVED from the rows instead of hand-written
   (`entries.c` missed the `rev-end` tie edge once, cpb02 finding 1). The iterator's stages
   fit it with three changes: `__find(M)` is a part whose layout the row decides; the
   NOTEMPTY retry is `first-nonzero(R@q, body@next_pos(q))`, which is split's own combinator;
   `next` is a new combinator, `iterate`, over the state part. The compound's B-steps become
   rows. **The iterator can stay zero-mover up to I0**, and I1 stays ONE abi event, provided
   the entry table lands first as a zero-mover (E0, §5.1).
7. **Is it worth building?** The layout row on its own is low-impact: the measured effects are
   a few percent either way. The value is the one entry table: one place that says what each
   exported call is, derived edges, and one place for every later entry (`next`, `next_n`,
   captures-on-demand, arch dispatch). The layout row is cheap once the table exists. The
   recommendation is E0 now (before I1), then the controls' mechanism (E1: explicit controls
   live, every preset cell em-dash), and preset cells only when a measurement asks for one.
   Revision 4 adds one reason to build E1 that revision 3 lacked: the controls give a caller
   direct `.o`-size control that the five positions could not (§3.2.5).

---

## 1. The entry map

### 1.1 The parts

| part | what it is | emitted today as |
|---|---|---|
| **LOCATE** | the candidate finder: the kit's one window request (D161 add. 3/7/9/11/14 and its clarification: pre-scan, presence and candidate search are one request) plus pcrec's own locators (`cand_rows[]` LOCATE: `composite`, `rev-end`, `empty`) | inside the search body; kit sites as `static inline` FUNC helpers (`rx_ofsskip`/`rx_reqrun` and their `__body` + D155 selector) |
| **FINISH** | one of four rows on the DFA or VM hat (`locate_finish.md` §1.3: `nomatch`, `report`, `verify-at`, `search-from`) | inside the search body; `verify-at` as `_match`'s body (`unwrapped`), the VM's `match_anchored` |
| **STATE** | `rx_iter` (D165; `findall_iter.md` §1) | not built |
| **residual** | the encoding's `_next_pos`, `_valid_upto`, `_var_valid` and the inline seam (`_span_match*`, `_back_step`) | exported leaves; the seam `static inline` since [LOSS-REVIEW] candidate 1 (abi 76) |
| **prologue** | the startpos guard, `-futf-check`, `startpos > n` | written into each entry head (`pcrec_emit_search_head`, `emit_dfa.c:1836`); owned by the controller on a compound (`compound.md` §A.6) |
| **sub-machine** | a compound part (`<p>__<role>_search`), the hybrid's embedded DFA (`rx_prefilter`), the VM `_run` bodies | `static` functions (`emit_compound.c:101`, `emit_vm.c:12773`) |

### 1.2 Every exported entry as a combinator

The combinators are `compound.md` §A.2's five plus two this map needs: `forward` (call a
sibling with the same answer, binding storage or not) and `iterate` (§4.2).

| entry | combinator | parts | emitted today |
|---|---|---|---|
| `<p>_search` | `locate-then-finish(LOCATE; FINISH)` behind the prologue | LOCATE, FINISH, residual | DFA: the body IS the entry (`pcrec_emit_dfa_engine`, `emit_dfa.c:13806`); VM: `_search` → `_search_run` → `match_anchored` (`emit_vm.c:13779`, rung-dependent); compound: `first-nonzero(F@f, Q@next_pos(f))` (`emit_compound.c:115`) |
| `<p>_match` | `finish-at-position` = FINISH `verify-at` at `ctx->pos`, or `search-from` + filter | FINISH, or the whole search | DFA axis G: `unwrapped` (own body), `search-filter` (calls `_search`, `emit_dfa.c:2689`), `nomatch`; VM: the anchored body; compound: F's one attempt (`emit_compound.c:156`) |
| `<p>_match_caps` | `finish-at-position` + delivery | as `_match` | DFA: delegates to `_match` (own forms) or calls `_search` (`emit_dfa.c:2727`); VM: its own `_run`; compound: F's attempt + copy |
| `<p>_*_in` (×3) | `forward(storage)` | the un-suffixed sibling | DFA: inert, calls the sibling (`emit_dfa.c:2788`); VM: binds the caller's buffers, or the sibling forwards to it (rungs `shared`/`forward`, tuning.md §2.21) |
| `<p>_next_pos`, `<p>_valid_upto`, `<p>_var_valid` | leaf (residual) | — | `pcrec_emit_residual` (`src/enc/`) |
| `<p>_info` | data, one per artifact (D88 add. 1) | — | `emit_info_def` |
| `main` | a driver over `_search` | — | `pcrec_emit_main` |
| `<p>_next` (designed) | `iterate(STATE; first-nonzero(R@q, SEARCH@next_pos(q)))` | STATE, the search controller, the retry R | `findall_iter.md` §2.1, not built |
| `<p>_next_n` (held) | `iterate` with a batch sink | as `next` | `findall_iter.md` §2.3, HELD (its Q2) |

**Compound controllers are the same table's rows with parts instead of an in-Job body.** Split
is `first-nonzero` over two parts; captures-on-demand (§D.1) is `select-by-arg(caps == NULL;
N, C)`; arch variants (§D.5) are `dispatch(level; …)`. `compound_place[]`
(`compound.c:278`) already says when a second machine is a part and when it is an in-Job row;
that rule needs no change.

### 1.3 As emitted: which entry calls which, and what gcc did with it

`compound_entries/results/entries.tsv` (probe `probe_entries.py`) lists every function in the
object of ten witnesses, in two regimes, with its size and its call edges. Nine of them:

| witness | `.text` fn bytes `-O2` / `-O2 -fPIC` | static parts gcc kept out of line | exported → exported edges |
|---|---|---|---|
| DFA `abc` (`unwrapped`) | 641 / 609 | none | `_match_caps`→`_match`, `_*_in`→sibling |
| DFA `^ab|cd` (attempt, `search-filter`) | 951 / 757 | none (the body is `_search`) | `_match{,_caps}{,_in}`→`_search` (4 edges) |
| DFA `\d+$` (`rev-end`) | 761 / 729 | none | `_match_caps`→`_match`, `_*_in`→sibling |
| compound `^\s+|\s+$` (split) | 1,206 / 1,021 | `rx__f_search` (402 B, 5 callers); Q inlined into `_search` | `_*_in`→sibling; under `-fPIC` also `_search`→`_next_pos` |
| compound, `-e utf8 -futf-check` | 1,737 / 1,672 | `rx__f_search`; gcc split `_valid_upto` into `.part.0` | under `-fPIC`: `_search`, `_match`, `_match_caps` → `_valid_upto`, `_next_pos` |
| VM hybrid `(a)b` (frameless, `inline`) | 1,400 / 1,378 | `rx_prefilter` (2 callers) | `_*_in`→sibling |
| VM hybrid `(a|ab)(c|bcd)(d*)` (framed, `plain`) | 3,033 / 2,859 | `match_anchored`, `search_run` | `_*_in`→sibling (their NULL-descriptor arm) |
| VM forced `(a)b` | 1,443 / 1,421 | none | `_*_in`→sibling |
| VM vars `a${v}b` (`forward` rung) | 1,558 / 1,662 | none | `_search`→`_search_in`, `_match{,_caps}`→`_in` (the forwards); under `-fPIC` also `_*_in`→sibling |

Two things the table shows that no document records:

- **gcc's layout depends on the link regime.** Without `-fPIC` gcc copies `_match` into
  `_match_in` and `_match_caps` into `_match_caps_in` (110 B and 142 B copies on the attempt
  route and on split). With `-fPIC` it cannot (an exported function is interposable), so the
  `_in` entries become 9-byte tail jumps: the function bytes fall 1.5-20% on eight witnesses
  and rise 6.7% on the vars witness. The same emitted C therefore has two layouts, and pcrec
  chose neither.
- **Exported entries call exported siblings.** Under `-fPIC` every such edge is a call through
  the PLT. B4's controller is one: it calls `<p>_next_pos` (`emit_compound.c:129`) and,
  under `-futf-check`, `<p>_valid_upto` from P's prologue (`pcrec_emit_search_head`, called at
  `emit_compound.c:122`), both exported, so in a shared object the compound's search makes
  one or two interposable calls per call (finding F-1).

### 1.4 The gaps

| gap | state today | what fills it |
|---|---|---|
| **the STATE part** | not built; `findall_iter.md` §1.3's storage-row table is designed | I1 (§5.1); the parts that hold rows SUM in a compound (D165 item 4) |
| **the kit's stream part** | the kit's FIND sites are FUNC helpers inside the body (`static inline`), stateless; R17-b's stateful mask (`mask8_swar`) lives on the kit's branch and needs the iterator's region (D165 add. 1) | I2 (R17-b″): the kit's site gets a region of `st`; the mode M reaches the kit's dispatch (§3.6) |
| **captures** | `_match_caps` is its own entry; `_search` delivers captures when given `caps`; captures-on-demand is a filed client (`compound.md` §D.1, B7) | a `select-by-arg` row of the entry table; `CompPart.groups` (built at B4) is the slot map |
| **callouts / vars** | vars change `_search`'s signature (`match_api.md` §3¶3; 18 corpus patterns); `rx_ctx` entries read vars from ctx; callouts unbuilt; the call-site code table (`emit_compound.c:56`) is shared by design | `rx_iter` carries vars, so `next` is uniform (`findall_iter.md` F8); callouts are a callee kind of the same table (`compound.md` §A.2's typed external callee) |
| **give-up codes (D158)** | DFA parts never give up; the call-site table emits rows 1, 2, 8; one meter per exported call is ruled (D163 add. 6 Q1) | VM parts light rows 3, 4, 7 (B6); an iterator call's retry has its own budget (`findall_iter.md` §3.4) |
| **utf-check** | one prologue per entry; on a compound, ONE prologue computed from P, parts guards-off | unchanged: the prologue is the controller's, never a part's; the iterator validates once per iterator (`findall_iter.md` U2) |

---

## 2. Inline or shared: what can move, what it costs

### 2.1 What cannot be inlined, and what must not be shared

Probe `probe_layout.py` forces each static part `always_inline` and records gcc's refusals
(`results/layout.tsv`):

| constraint | witness | gcc's words | population |
|---|---|---|---|
| **H1 a static label table** | split's F part; every DFA `attempt`-scan body | "function 'rx__f_search' can never be copied because it saves address of local label in a static variable" | 233 of 4,243 compiled byte corpus artifacts carry it in `_search` (`findall_iter.md` F5); every split compound's F (97 admitted (pattern, arm) rows, `tests/compound/admitted.tsv`) |
| **H2 a computed goto** | the framed VM's `match_anchored` | "function 'rx_match_anchored' can never be inlined because it contains a computed goto" | every framed VM artifact; the entry chain's rungs 2-4 already decline on it (tuning.md §2.21¶3) |
| **H3 a part with one caller is never shared** | split's Q (one caller, `_search`) | — (not an error: a measured loss) | shared costs +112 B `.text`, Ir −11 to +5 per iteration over four subjects (a few instructions either way) |
| **H4 `info` and `main` are not static** | — | `pcrec_entry_shape` (`entries.c`) refuses a request that keeps them static | every artifact |

H1 decides split by itself: F must be shared across its five callers, and Q is single-caller,
so gcc's default (F out of line, Q inlined) is the only sensible layout. The dial has nothing
to decide on the one compound built today.

### 2.2 The cost of a shared part, measured

`results/layout.tsv`: three layouts of the same artifact. `gcc` is as emitted; `shared` marks
every part `noinline`; `inline` marks every copyable part `always_inline`. Ir is callgrind's
instruction count per driver iteration: a find-all with `_search` and the spec's advance, then
one `_match` probe per position (`drv.c`).

| witness | layout | `.text` B | subject | Ir / iter | vs `gcc` |
|---|---|---|---|---|---|
| split `^\s+|\s+$` | gcc | 1,256 | `"  ab cd  "` | 1,116 | — |
| | shared | 1,368 | | 1,110 | +112 B, −0.5% |
| | inline (F refused) | 1,256 | | 1,113 | = gcc |
| VM hybrid frameless `(a)b` | gcc = shared | 1,448 | `"abab…"` ×4 | 1,998 | — |
| | inline | 1,512 | | 1,733 | +64 B (+4.4%), −13.3% |
| | gcc = shared | 1,448 | `"xxxx"` | 238 | — |
| | inline | 1,512 | | 213 | −10.5% |
| VM hybrid framed `(a|ab)(c|bcd)(d*)` | gcc | 3,096 | `"abcdabcd"` | 1,818 | — |
| | shared | 2,936 | | 1,889 | −160 B (−5.2%), +3.9% |
| | inline (`match_anchored` refused) | 3,752 | | 1,782 | +656 B (+21.2%), −2.0% |

Per call: the frameless hybrid's prefilter is called on each of 9 `_search` calls per
iteration, so inlining it saves about 29 instructions per call (25 on the sparse subject).
Split's Q, called once per `_search`, moves about 5 either way. These are instruction counts,
not time; §3.3 says what the cells need beyond them.

### 2.3 Sharing through an exported sibling: the PLT

`probe_plt.sh` (`results/plt.tsv`): the same artifact linked statically, as a shared object
(default visibility) and as a shared object built `-fno-semantic-interposition` (the
artifact's own sibling calls bound locally). The last two differ only in the artifact's
INTERNAL exported-to-exported edges; the driver's calls go through the PLT in both.

| witness | static | `.so` | `.so` local binding | internal-edge cost |
|---|---|---|---|---|
| DFA attempt `^ab|cd` (`_match` → `_search`) | 1,353 | 1,424 | 1,381 | 43 Ir / 9 `_match` calls ≈ 4.8 per call |
| DFA `abc` (`unwrapped`: no internal edge on the path) | 965 | 997 | 997 | 0 |
| split (static parts) | 1,116 | 1,144 | 1,146 | none measurable (±2; the controller's one `_next_pos` call per search) |

So a part shared through a static function costs only its call; a part shared through an
exported entry costs the PLT stub and the optimization gcc may not do across an interposable
symbol. The rule that follows is not a dial question: an entry should reach a shared body
through a STATIC part, never through an exported sibling (§3.0 I3).

### 2.4 The existing row, measured the same way

`probe_vmshape.sh` (`results/vm_entry_shape.tsv`), `--vm-entry-shape=1..4` on a frameless
VM `(a)b` (it writes a capture slot, so the forward rungs are illegal and fall back by intent:
`shared`→`plain`, `forward`→`inline`):

| witness | rung | `.text` B | Ir / iter dense | sparse |
|---|---|---|---|---|
| hybrid `(a)b` | `plain` | 1,832 | 2,415 | — |
| | `inline` | 1,448 | 1,998 | — |
| forced VM `(a)b` | `plain` | 1,736 | 2,099 | 227 |
| | `inline` | 1,496 | 1,432 | 200 |

On a small artifact `plain` is BOTH larger and slower: each of six entries carries its own
frame and stack-protector canary. "Shared" is not automatically the size end; the size end is
whatever is smaller, and that depends on the part's size against the per-entry scaffolding.
This is why the existing row keys on a size term (program bytes against 4,096) and not on a
fixed rung.

---

## 3. The layout controls and the dial's presets

### 3.0 The invariants the row works inside (kept from revision 1, ruled by D163 addendum 7)

- **I1. Every exported entry is a compound controller over parts** (LOCATE, FINISH, STATE,
  the residual leaves, the controller's prologue; §1). The part-layout row decides only how a
  part's body is LINKED into its callers: a copy in each caller, or one out-of-line static
  body they call. It never decides which parts exist or what they compute, so every position
  is answer-identical by construction (§3.6's acceptance still checks it).
- **I2. E0 before I1, and E1 after E0.** The row reads each part's callers and each edge's
  rank (§3.2) off `entry_rows[]` (§4.1). **`entry_rows[]` does not exist yet** [r3 LK-1]:
  the only edge source today is `entries.c`'s `entry_edges[]`, which holds `{from, to,
  shape-predicate}` between entry ids, with no combinator and no rank. E0 must therefore ADD
  a rank column to every edge. That is new data written by hand from the emitters' call
  sites, not a derivation, and it carries its own hand-written fixture (§3.6, a precondition
  of E1, not a check made after it).
- **I3. No exported entry calls an exported sibling** (H5, Q5). A body reached from more than
  one entry is a STATIC part; the wrappers reach it through static twins. Applied where a
  change already moves the bytes (I1 for the residual twins, including F-1's `_next_pos` and
  `_valid_upto`; the first live cell diff for the wrappers), never as its own every-artifact
  event. It is a linkage rule of `entry_rows[]` that holds at every position where it is
  applied, so it is not a row of the layout table. **It is a precondition of the first live
  cell** [r3 LK-5, CE-13]: a cell may lay out a part only if every exported-to-exported edge
  into or out of that part has its static twin, either from I1 or from the cell's own diff.
  Until then the DFA wrappers are exported entries, not parts, and no position moves them.
  **[r4] The same holds for an explicit control.** A part is in a class's SUBJECT set only
  once its exported-sibling edges have static twins. Until I3 the `wrap` class has no
  subject, so `--part-layout=wrap:V` is accepted and lays out nothing, and the census
  reports that with its reason (§3.4.2).
- **I4. The `0` layout is the owning design's layout** [r3 F3, CE-11]. [r4] The control
  value `auto` means exactly this layout. At `0` every function
  keeps the attributes its emitter writes today (§3.1's writers) and, after I1, the iterator's
  `findall_iter.md` §2.2 attributes, which are that design's `0` cell. "As emitted" in this
  note always means this: the part's `0` layout, written by its owner, which is often but not
  always "no attribute".
- **I5. The layout is rendered after every length decision** [r3 LK-8]. The rows' attribute
  text and the `−2`/`−1` forwarding wrappers are written by one pass over the assembled
  artifact AFTER the emitted-size caps, the size term, the VM entry-shape term and every
  other length decision have read the text, as the K79 prefix placeholder is rendered last
  (`pcrec_sb_render_prefix`). No decision can read layout bytes, on the VM, DFA or compound
  emitters alike, so H6 holds by construction and §3.6 checks it on the near-cap witnesses.
  The caps bound the `0`-layout text; a cell diff reports its layout delta on its size axis.

### 3.1 The family: who writes inline/shared today [r3 F1, CE-3, F2]

Revision 2 counted "eight deciders". A grep of `src/` and `memfn/src/` for every emitted
`always_inline`, `noinline`, `noclone` and `static inline` finds the real sites. They fall
into three groups.

**Group A: sites that write an attribute or a linkage today.**

| # | writer | where (by symbol) | what it writes | decided per artifact? |
|---|---|---|---|---|
| A1 | the VM entry chain (`plain`/`shared`/`forward`/`inline`) | `emit_vm.c` `vm_plan_entry` (`en->ai`, `en->ai_body`); tuning.md §2.21 | `always_inline` on the thin helpers and the matcher body, or `noinline` on the matcher body (`shared` rung), or nothing | **yes**: a size term (4,096; 8,192 at `+1`/`+2`), the dial's existing row, gated by the legality fact `may_attr = !has_push` |
| A2 | [OPT-1]'s deep tier `<name>_deep` | `emit_vm.c`, the `tiered` arm of the entry emitter | `static __attribute__((noinline))`, load-bearing: "inlined, these arrays would be back on the entry's own frame" | whether `_deep` exists (`-fno-tiered-entry`, tuning.md §2.12); the attribute is fixed |
| A3 | K24's `noclone` on every search head | `emit_dfa.c` `emit_search_head` (behind `pcrec_emit_search_head`) | `__attribute__((noclone))` under `__has_attribute` | no: fixed |
| A4 | the encoding seam (`_span_match*`, `_back_step`, utf8 `_decode`) | `src/enc/enc_byte.c`, `enc_utf8.c` templates (`inline_def`) | `static inline` | no: fixed ([LOSS-REVIEW] candidate 1, abi 76) |
| A5 | the class kit's predicates `<p>_wcls%d` | `clskit.c` (the seven matcher emitters), called from the VM emitter's class section | `static inline` | no: fixed (the λ row picks the FORM, not the linkage) |
| A6 | the DFA machine's state helpers (`_step`, `_is_stop`, `_accepts`, `_accepts_class`, `_is_dead`, `_row`, `_view_live`, `_view_take`) | `emit_dfa.c`, the machine-helper emitter | `static inline` | no: fixed |
| A7 | the kit's FUNC helpers and D155 selector | `memfn/src/ofsskip.c` and siblings | `static inline` | the kit's (D157) |

**Group B: designed, not built.** The iterator's `__find`, `__adv`, `__step`, `__enter`
(`findall_iter.md` §2.1-§2.2): `__find` is `always_inline` or `static noinline` by §2.2's
two-row table; the other three are `always_inline`.

**Group C: no attribute; gcc decides, and the link regime (§1.3).** The hybrid's embedded
DFA search `<p>_prefilter` (emitted by `pcrec_emit_dfa_engine`, so it carries A3's
`noclone` and nothing else), compound parts `<p>__<role>_search` (`part_splice`), and the
DFA `_in`/`_match_caps` wrappers. Revision 2 called these "members 2, 6, 7"; they have no
decision in the code [r3 F1].

**The honest recount.** Decisions about inline-vs-shared that vary per artifact: ONE built
(A1) and ONE designed (§2.2). A2's existence varies but its attribute does not. Fixed
writers: A3-A6, plus the kit's A7. Revision 2's "eight members is past the unification
threshold" does not survive the recount: two decisions are below the `~3` trigger of memory
`pcrec-forest-for-trees`, so that argument is DROPPED. The row is justified by its charter
(Frank, 2026-10-14: "the dial could decide what's inline") and by the entry table it rides
on (§4), not by a family size.

**The siblings the row sits beside** [r3 F2, family sibling statement]. Four existing rows
or axes decide how a body is laid out or what form a body takes, by a size or speed trade:
- tuning.md §5.4's **λ row** (the class-matcher form `P3`/`K`/`P2`/`B1`; A5 is its output);
- the **`--vm-entry-shape` term row** (A1);
- the **`-fno-tiered-entry` axis** (A2's existence, tuning.md §2.12);
- the **`[ART-SIZE]` ladder rows** (bar, threshold).

The layout row is the fifth, not "a new family". Its threshold `θ_hot` (§3.3) and A1's size
term are both position-indexed cutovers on an unmeasured quantity [r3 SIB-2], so both fall
under memory `pcrec-suspect-tuning-constants`, and both belong in one row table once A1
migrates (unlock U-B, §5.3).

**The part population** [r3 CE-3]. The table's subject is a PART: a callable static body
reachable from one or more entries. Every function the emitters write is in exactly one of
three classes, and E1's census checks that the classes cover every emitted function:

| class | functions | rows that touch it |
|---|---|---|
| **subject** (the layout row decides it at non-zero positions) | the hybrid's `<p>_prefilter`; compound parts `<p>__<role>_search`; after I1, `__find`, `__adv`, `__step`, `__enter`; after I3, the static twins of wrapper bodies and residual leaves | §3.4's P2-P9 |
| **owned** (an owner writes its attribute; the row keeps it at every position) | A1's thin helpers (bind, init, reset, report_captures, the three `_run`s) and matcher body; A2's `_deep`; A4's seam | §3.4's P1 |
| **not a part** (an expression helper inside one part's body, or not static) | A5's `<p>_wcls%d`; A6's DFA state helpers; A7's kit helpers; every exported entry; `info`; `main` | none; A3's `noclone` is an orthogonal attribute on entries and is kept (H7) |

A function that fits none of the three classes is a census failure, not a default.

**[r4] The control classes.** Revision 4 splits the SUBJECT class into four CONTROL classes,
one per kind of part, because their size and speed trades differ (§3.2.5). Each subject
function is in exactly one control class, and the census checks that too:

| control class | subject functions | owner of the part's `0` layout |
|---|---|---|
| `prefilter` | the hybrid's `<p>_prefilter` | gcc (group C) |
| `compound` | compound parts `<p>__<role>_search` | gcc (group C) |
| `find` | after I1, the iterator's parts: `__find`, `__step`, `__enter` | `findall_iter.md` §2.2 for `__find`, §2.1's `always_inline` for the other two (group B) |
| `wrap` | after I3, the static twins of wrapper bodies and of the residual leaves (the iterator's `__adv` is one) | gcc, or `findall_iter.md` §2.1's `always_inline` for `__adv` |

The OWNED and NOT-A-PART functions have no control class, so no control can name them.
That is the first half of "no control overrides a load-bearing row". The second half is the
constraint rows' place in the part table (§3.4). The owned VM entry chain (A1) already has a
caller-settable control, `--vm-entry-shape=N` (tuning.md §2.21). It is that class's control
and is not respelled here (§3.7; unlock U-B).

### 3.2 Edge rank, the five policies, and the controls that express them

A position's POLICY is pinned (D103, Q1): it is the definition of what the position does,
fixed in tuning.md §5.4's row, and it changes only by a ruled diff. Whether the position's
CELL is live (moves bytes) is a separate fact: every non-zero cell stays `†` until its own
ruled diff cites a size AND a time measurement (D103 item 3). [r4] Since D163 addendum 8 a
policy is no longer a mechanism of its own. It is a PRESET: a row of values for the
caller-settable controls of §3.2.2 (§3.2.4). The table of five policies below says what each
preset MEANS. §3.2.4 says how it is spelled in controls, and the part table (§3.4) reads only
controls.

**Hotness is an edge rank, carried by `entry_rows[]`, not a profile.** Each edge from a
function to a part has a rank, given by the call site's place in the controller. E0 adds the
rank as a column of every edge (I2, [r3 LK-1]); where one edge has call sites of two kinds,
the column is a shape predicate (as `entry_edges[]`'s `when` already is) and the edge takes
the higher rank. A part's rank is the highest rank among its in-edges.

| rank | edge kind | calls of the part per exported call | witnesses |
|---|---|---|---|
| R3 `inner` | inside a per-candidate or per-attempt loop | unbounded; grows with the subject | the hybrid's `_search_run` → `<p>_prefilter` edge on an artifact whose retry re-enters the prefilter: an MRL clamp (`nclamp > 0`) or an ADAPTIVE re-seed row (`hyb_reseed.md`, the `retry_win`/`retry_seed` text in the VM emitter). UNWITNESSED among this note's measured artifacts: `(a)b`'s prefilter is called only from the entry [r3 CE-4]. The iterator's internal batch fill is ruled as a direction (D165 add. 2 Q2) but not designed in `findall_iter.md`, so it is HELD with `findall_iter.md`'s Q2 and is not a witness [r3 F4] |
| R2 `per-call` | once on every call | 1 | the same `_search_run` → `<p>_prefilter` edge where no retry re-enters (the `(a)b` hybrid, measured); split's Q from `_search`; `__find` from `_search` and `_next` (designed) |
| R1 `conditional` | on a data-dependent subset of calls | at most 1 | split's F (while the floor can be live). F is not copyable (H1), so no position row moves an R1 part today: R1 has no movable witness |
| R0 `rare` | an error, tie or fallback path | about 0 | the DFA `rev-end` tie's verify (`entry_edges[]`'s `SEARCH → MATCH` edge, `sh_dfa_tie`). It is an exported-to-exported edge today, so it becomes a part only by I3 [r3 CE-4]: revision 2's `<p>__q_match` is not emitted by any `src/gen` file |

**Callers** [r3 CE-8]. `callers(part)` is the number of distinct functions that hold a call
site to the part, counted in the emitted C after every function an OWNED row makes
`always_inline` is folded into its callers. It counts functions, not call sites: the
prefilter's two sites inside one `_search_run` are one caller. It depends on the owner's
decision: on the `(a)b` hybrid at a forward or inline rung, `_search_run` folds into
`_search` and `_search_in`, so the prefilter has two callers; at the `plain` rung it has one.

**The five policies** (what each preset means; [r4] the last column is its spelling in controls, §3.2.4):

| position | policy token | layout of a subject part with two or more callers | what decides it | cell today | [r4] preset row |
|---|---|---|---|---|
| −2 `min-size` | `all-shared` | one `static noinline noclone` body; each wrapper that calls it is a tail-forward where `forwardable` holds, and keeps its adaptation and a call where it does not (§3.4 W-table) | caller count | `†` | residual `shared` |
| −1 `size` | `shared-but-inner` | as `−2`, except a part of rank R3 is `always_inline` into each caller | caller count, rank = R3 | `†` | residual `shared`, rank `R3` |
| 0 `balanced` | `as-emitted` | the owning design's layout (I4); byte-identical to no flag | nothing (D103's no-op cell) | live (the default) | nothing set |
| +1 `speed` | `hot-inline` | a copyable part of rank ≥ `θ_hot` is `always_inline`; every other part keeps its `0` layout. With `θ_hot` absent from the active set, or `none`, the threshold resolves to `none` and, with no explicit control, the WHOLE ARTIFACT takes the `0` layout, stamped (§3.3, rows T1/T2; Q6 RULED) | rank, `θ_hot` from the set | `†` | rank `measured` |
| +2 `max-speed` | `all-inline` | every copyable part `always_inline` into every caller | copyability | `†` | residual `inline` |

A subject part with ONE caller keeps its `0` layout at every position and under every
control (§3.4 row P3): it is never shared, and nothing adds an attribute to it [r3 CE-1]. `+1` never shares a part
that `0` would have let gcc inline: a speed position that shared more than the default would
not be speed-leaning.

The forwarding in `−2`/`−1` is part of the policy, and it is legal only per wrapper [r3
LK-2]. F-5 measured that one body behind six entries that each keep a frame and a canary
(`plain`) is LARGER than `inline` on a small VM artifact. gcc 15.2 `-O2` turns a wrapper into
`jmp body` only when its argument list passes through unchanged. A wrapper that adapts its
arguments keeps a frame and a `call`: the compound `_match` builds a local
`capture_spans[NCAPS][2]` from `ctx` (`emit_first_nonzero_match`), and with
`-fstack-protector-strong` it also carries a canary. So `−2` does not claim a smaller object
on every artifact. Each cell diff's size axis states it per artifact class.

#### 3.2.1 Where adjacent positions differ [r3 CE-4, CE-5, CE-13]

Each adjacent pair differs on a named part class. Revision 2 called this "distinct by
construction"; that is true of the policies and says nothing about populations. Below, each
pair has a named emitted witness or is marked UNWITNESSED, with the population that would
make it live:

| pair | they disagree on | witness, or UNWITNESSED |
|---|---|---|
| −2 / −1 | a copyable multi-caller subject part of rank R3 | **UNWITNESSED.** Candidate population: hybrids whose retry re-enters a copyable prefilter (an MRL clamp or an adaptive re-seed row). Revision 2's "25-29 Ir per call" for `(a)b`'s prefilter is an R2 (entry) number, not an R3 one |
| −1 / 0 | a copyable multi-caller subject part that the `0` layout inlines | **UNWITNESSED today.** On `(a)b` gcc already keeps the prefilter out of line ("gcc = shared", §2.2), so `−1` changes its text and not its object. The DFA wrappers have no population until I3 makes them parts [r3 CE-13]. The designed witness is `__find` on a non-attempt artifact after I1: `always_inline` at `0` (§2.2) and shared at `−1` (the parity gate's `I` and `I_shared` arms) |
| 0 / +1 | a copyable part of rank ≥ `θ_hot` that the `0` layout keeps out of line | **DECLARED-COINCIDENT until a set carries `θ_hot`** [r3 CE-5]: no set does, so `+1` takes the `0` layout on every artifact (row T1), as D103 treated `+2`. Once `θ_hot` ≤ R2: `(a)b`'s `<p>_prefilter` (R2, two callers at the forward rung, kept out of line by gcc, measured −13.3% Ir dense when inlined) |
| +1 / +2 | a copyable multi-caller part ranked below `θ_hot` | with `θ_hot` = R3: `(a)b`'s `<p>_prefilter` (R2), left at `0` by `+1` and inlined by `+2`. With `θ_hot` ≤ R2: UNWITNESSED until I3 turns the `rev-end` tie's verify into a static R0 part |

On split alone every position coincides (F-4: P2 pins F and P3 keeps Q). E1's census counts
each ROW's population per position, not each part class (§3.6), so a row with zero
population is reported with its reason.

#### 3.2.2 The controls [r4, D163 addendum 8]

The layout is set by three caller-settable controls. All three are VALUED parameters: a CLI
`--X=y` and a `pcrec_options` field, like `--unroll=K` and `--vm-entry-shape=N`
(tuning.md §2.10, §2.21). None is a flag bit. The spellings below are PROPOSALS: addendum 8
leaves the final CLI spelling and the field representation to the interface rules
([IFACE-PUSH], [FLAG-ACCESS]), and §3.7 gives the reasoning against the alternatives.

| # | control | CLI (proposed) | `pcrec_options` field (proposed) | values | subjects | rows that can hold it (§3.4) |
|---|---|---|---|---|---|---|
| C1 | class value, `prefilter` | `--part-layout=prefilter:V` | `part_layout`, the `PCREC_PART_PREFILTER` slot | unset (0), `auto`, `shared`, `inline` | `<p>_prefilter` | P3 where the prefilter has one caller (the `plain` rung; a framed hybrid, where `_search_run` is its only caller). P2 if a prefilter's own scan is ever the attempt route (none today: the prefilter is an unanchored scan) |
| C2 | class value, `compound` | `--part-layout=compound:V` | the `PCREC_PART_COMPOUND` slot | as C1 | `<p>__<role>_search` | P2 for split's F (label table), P3 for split's Q (one caller): **every member is held today** (F-4) |
| C3 | class value, `find` | `--part-layout=find:V` | the `PCREC_PART_FIND` slot | as C1 | `__find`, `__step`, `__enter` (after I1) | P2 for `__find` on the attempt route (233 byte corpus artifacts); P3 for `__step`/`__enter` (one caller each) |
| C4 | class value, `wrap` | `--part-layout=wrap:V` | the `PCREC_PART_WRAP` slot | as C1 | static twins of wrapper bodies and residual leaves (after I3), `__adv` | P3 for `__adv`; no subject before I3 (§3.0 I3) |
| C5 | rank threshold | `--part-inline-rank=R` | `part_inline_rank` | unset (0), `none`, `R3`, `R2`, `R1`, `R0`, `measured` | every subject part whose class value is unset | P1-P3, then a class value (P4-P6) |
| C6 | residual | `--part-residual=V` | `part_residual` | unset (0), `auto`, `shared`, `inline` | every subject part that no class value and no threshold decided | P1-P3, P4-P7 |

- **Values.** `auto` is the owner's `0` layout (I4): the attribute the owning design writes,
  often none. `shared` is one `static noinline noclone` body; a wrapper that calls it takes
  the W-table (§3.4). `inline` is `always_inline` into each caller. Unset (the field's 0)
  means "the preset decides", which is a defined meaning, not a presumed value (memory
  `pcrec-no-silent-defaults`): with no preset value either, the control is inert.
- **The threshold.** `R3` inlines a copyable part whose hottest in-edge is R3 (an inner
  loop), `R2` adds per-call parts, `R1` conditional ones, `R0` every copyable part. `none`
  inlines nothing by rank. `measured` reads `θ_hot` from the active measurement set (§3.3);
  it is the only value that reads the set and the only one that can decline (Q6, RULED).
  The set's derivation never yields `R0` (§3.3), but a caller may type it.
- **Multiple classes in one flag.** `--part-layout=prefilter:shared,find:inline`. Each class
  is its own axis. On the command line a later value for the same class wins; across
  sources the general file-wins rule (cli.md §1.1.4¶4) applies per class, so a file that
  sets `find:` does not unset the command line's `prefilter:`. A config's raw
  `pcrec --part-layout=...` line carries all three; typed `.rxt` rows are not proposed
  (format spelling is the manager's, memory `pcrec-dd13b-syntax-is-managers`, and the raw
  line suffices).
- **The owned VM entry chain** is not a class here. Its control already exists:
  `--vm-entry-shape=N`, whose rungs are its class values under other names (`plain` ≈ no
  attribute, `shared`, `forward`, `inline`). Giving it a second spelling as
  `--part-layout=vm-entry:V` would be a parallel mechanism over one field. Joining the
  spellings is unlock U-B's, at the ruled diff that migrates A1 (§5.3).
- **What no control can name**: A2's `_deep` (load-bearing), A4's seam, A3's `noclone`,
  the kit's helpers (D157), and every not-a-part function (§3.1). They are not in any class,
  so they cannot be requested, and P1 keeps the owned ones ahead of every control row
  regardless.

#### 3.2.3 Why this grain [r4]

The manager's leaning was "by PART CLASS plus an explicit RANK THRESHOLD". Revision 4 keeps
it and adds the residual mode, because the leaning alone cannot spell `−1` and `+2` without
the presets setting class values (below). The alternatives, and the evidence against each:

| grain | for | against |
|---|---|---|
| one switch (`shared`/`inline` everywhere) | simplest; it is what `−2`/`+2` mean | it is what the five positions already are; addendum 8 asks for finer control. And the classes trade differently: the prefilter class costs 0 to +18% `.text` inlined, the `find` class's `_next` is 433-1,079 B inlined against 321-666 B shared, and the compound class has no movable member at all (§3.2.5) |
| per function (name each part) | finest | a part's name is pattern-dependent (`<p>__q_search` exists only on split), so a caller cannot name it before compiling, and a build script cannot carry it across patterns |
| per rank only | one value; it is `θ_hot`'s own unit | it cannot keep the prefilter shared while inlining `__find`, which both rank R2 on the `(a)b`-class hybrid with an iterator. And rank says nothing about size, which is Frank's stated concern |
| per class only | direct `.o` control per kind of part | `−1` ("shared except the inner loop") and `+1` ("inline the hot parts") cut ACROSS classes by rank. Without a threshold the presets would need a `hot` value per class plus a below-threshold fallback per class: more values, same expressive power |
| per size cutover (inline a part only if its body is under N bytes) | A1's term already has this shape; it speaks `.o` size directly | the layout pass sees SOURCE bytes and the inlined copy's object bytes are 0.55× to 1.75× the standalone body's on the scratch witnesses (§3.2.5), so a source cutover would need a measured conversion, which is a suspect constant (memory `pcrec-suspect-tuning-constants`). FILED as unlock U-S, with a trigger |
| **class + threshold + residual** (chosen) | the class value is absolute and per kind; the threshold cuts across classes by hotness; the residual is the default for the rest. Each of the five presets is one or two control values (§3.2.4), and no preset sets a class value | three controls instead of one |

The residual is the "residual sharing mode" the manager's leaning left open. Without it, `−1`
would be "every class `shared` plus rank `R3`", and a class value set by a preset would then
have to lose to the threshold while a class value set by a caller wins. That is an ordering
that depends on where a value came from. With the residual, the presets never set a class
value, and every control means the same thing whoever sets it.

#### 3.2.4 The presets: the dial's rows of control values [r4]

Each position is a row of the dial's pinned policy table (tuning.md §5.4, D103), and its
cells are control values. The table is first-match by position: one row per position, and
no row reads another. **Home**: three new columns of `src/core/tune.c`'s `TUNE_TABLE`
(`part_inline_rank`, `part_residual`, and one class-value column per class), whose contract
copy is tuning.md §5.4. The existing `--vm-entry-shape` term column is the A1 class's
preset, which the table already carries.

| position | `part_residual` | `part_inline_rank` | class values (C1-C4) | `--vm-entry-shape` term (existing) | cell today |
|---|---|---|---|---|---|
| −2 `min-size` | `shared` | — | — | — | `†` |
| −1 `size` | `shared` | `R3` | — | — | `†` |
| 0 `balanced` | — | — | — | **4,096** | live: every layout cell em-dash |
| +1 `speed` | — | `measured` | — | **8,192** | `†` |
| +2 `max-speed` | `inline` | — | — | **8,192** | `†` |

- **Resolution.** For each control: the caller's value if set, else the preset's cell, else
  unset. A `†` cell is an em-dash until its own ruled diff, so today every position
  resolves every layout control to unset, and an artifact's layout changes only when the
  caller sets a control. This is tuning.md §1¶9's rule ("an explicit per-axis flag beats the
  dial wherever a spelling exists") applied to three more axes. Every control now has a
  spelling, so no layout cell is one "no spelling could override".
- **Why no preset sets a class value.** A class value is absolute (P4-P6 run before the
  threshold). If a preset set one, the threshold could never reach that class at that
  position. The columns exist so a future ruled cell CAN set one (say, `−1` sharing `find`
  only once the parity gate prices it), and that cell diff then states which classes it takes
  out of the threshold's reach.
- **What `+2` means against `+1` on this row.** With `θ_hot` absent, `+1` is the `0` layout
  and `+2` inlines every copyable part, so the two differ wherever a copyable multi-caller
  part exists (the `(a)b`-class prefilter today).
- **The presets are checked like the rest of the table.** `run_tune_dial.sh` reads each
  position's expected control values from tuning.md §5.4, not from `tune.c` (§3.6).

#### 3.2.5 Expected size and speed direction, per control [r4]

Size is read from three SCRATCH-GRADE probes (lane `cmprev4`: one run, compile-only, gcc 15.2
`-O2`, x86-64, the Linux dev box; `compound_entries/rev4_*`). Every speed entry is an
instruction count (callgrind Ir, revision 1's §2.2) or an argument, and is **UNMEASURED as
time**. "`.o`" is the whole object file, which also carries the symbol table and
`.eh_frame` (each out-of-line function adds an FDE, 24-56 B here).

| control value | `.text` / `.o` direction | measured (scratch unless noted) | speed direction | evidence for speed |
|---|---|---|---|---|
| `prefilter:inline` | UP | `(a)b` +64 B (+4.4%) / `.o` +160 B; `(foo\|bar\|baz\|qux\|quux)\d+` +320 B (+8.9%) / +352 B; `([a-z]+)@([a-z]+)\.com` +704 B (+17.9%) / +1,112 B (+12.4%). The inlined copy is 0.55× to 1.75× the standalone body | faster per call | −5 to −29 Ir per call; `(a)b` −13.3% Ir dense (revision 1, MEASURED Ir). Time UNMEASURED |
| `prefilter:shared` | 0 where gcc already keeps it out of line (all three witnesses above); where it has one caller, held by P3 (shared there would cost +128 B, measured, framed `(a\|ab)(c\|bcd)(d*)`) | as left | 0, or +5 to +29 Ir per call where it moves | as left |
| `compound:` any | 0: every member is held today (F by P2, Q by P3) | split: shared would cost +112 B / `.o` +208 B, which P3 prevents | 0 | F-4 |
| `find:inline` / `find:shared` | inline UP, shared DOWN | `_next` 433-1,079 B inlined against 321-666 B shared (`findall_iter.md` twin, MEASURED compile-only, not scratch) | inline faster, by the parity gate's `I` vs `I_shared` arms | owed (the parity gate, `findall_iter.md` §5.3) |
| `wrap:shared` (W1 forwards) | DOWN | proxy: gcc's own `-fPIC` layout turns the `_in` copies into 9 B tail jumps: split 1,256 → 1,080 B (−14%), DFA attempt 984 → 808 B (−18%), frameless hybrid 1,448 → 1,416 B (−2.2%); +6.7% on the vars witness (revision 1, MEASURED) | about 0 for a W1 forward (one `jmp`); a W2 wrapper keeps a frame and a call | revision 1 §1.3, §2.3 |
| `wrap:inline` | UP | the non-`-fPIC` layout gcc already picks on most witnesses (the 110-142 B copies) | about 0 | — |
| `part-inline-rank` lower (`none` → `R3` → … → `R0`) | monotone UP: each step adds the parts of the next rank, each at its class's `inline` cost | the sum of the class rows above over the newly reached parts | monotone faster per call, a few % Ir at most on the measured witnesses | revision 1 §2.2 |
| `part-residual:shared` | DOWN or 0 | as the class `shared` rows over the parts it reaches; F-5 caveat: on a small VM artifact one body behind framed entries can be LARGER | slower per call by the call | as above |
| `part-residual:inline` | UP | as the class `inline` rows | faster per call | as above |
| (owned, existing) `--vm-entry-shape` `plain` → `inline` | UP, the largest lever | `([a-z]+)@([a-z]+)\.com` 2,808 → 3,928 B (+40%) / `.o` +7.7%; `(\d{3})-(\d{3})-(\d{4})` 3,432 → 5,832 B (+70%) / +22.6%; the HTTP request-line witness 3,544 → 6,600 B (+86%) / +23.7% | faster: `inline` measured at `forward`'s time, `shared` at `plain`'s (tuning.md §2.21¶4) | `ccd2_report.md` |

Three readings:

- **Frank's "huge impact on .o size" holds most strongly for the class that already has a
  control.** The owned VM entry chain moves `.text` by 40-86% between its end rungs on these
  witnesses. Among the new classes, the prefilter class moves up to 18% and the `find`
  class's `_next` 35-62%. The compound class moves nothing today.
- **Relative is large, absolute is small** on every measured witness: hundreds of bytes,
  at most about 3 KB. No artifact near the emitted-size caps was measured. Whether a class
  value moves a near-cap artifact by tens of KB is UNMEASURED; E1's census owes it (§3.6).
- **Link regime.** Under `-fPIC` the `shared`/`inline` deltas for the prefilter class are
  the same within 8 B (`results/rev4_osize.tsv`). The `wrap` class is where the link regime
  matters: gcc already forwards there under `-fPIC` (F-2), so `wrap:shared` buys its size
  mainly in a static link.

### 3.3 `θ_hot`: the one value a control reads from the measurement set

[r4] `θ_hot` is now what the threshold control's value `measured` reads. It is no longer a
property of a position: `+1`'s preset holds `measured`, and a caller may type it at any
position. A caller who types a rank (`--part-inline-rank=R2`) sets the threshold DIRECTLY,
and the set is not read. That is the direct manual setting addendum 8 asks for, and it
makes the threshold reproducible across boxes for a caller who wants that. Everything below
applies to `measured` only.

- **What it is.** The lowest edge rank that `+1` inlines, or `none`. Its domain is
  {R3, R2, R1, `none`} [r3 CE-6]. R0 is never in it, so `+1` never inlines a rare-edge part
  and stays distinct from `+2` wherever an R0 part exists. `none` means the set measured
  every rank and found none material: `+1` then inlines nothing beyond `0`, and says so in
  its stamp.
- **Why it comes from the set** (Q1). A shared part's call cost is hardware-dependent. Zen 4,
  Zen 1 and the M1 differ, which is what D166 sets exist for. The policy that reads it is
  pinned. A static rank makes the same layout for the same pattern on every box with the same
  set; only `θ_hot` moves, and it moves with the set (Q7 note).
- **Its derivation**, a DERIVED row of the set (D166 item 2, the closed derivation registry of
  `measure_sets.md`). The inputs are, per rank r, the measured overhead of reaching a shared
  static part over its inlined form, per exported call, on the set's reference short-call
  cell, in units of the scalar walk's per-byte cost; and the materiality bar `y` (tuning.md
  §5.2). `θ_hot` is the lowest r whose overhead is material against that cell's walk. The
  overhead grows with rank, so the derived value is monotone: if R1 is material, so are R2
  and R3. **If no rank is material on the reference cell, the derived value is `none`.**
  Revision 2 derived R3 here from an argument about longer subjects; that let an argument
  override a measurement that said nothing was material, which is a presumed value [r3
  CE-6]. A set that wants R3 to count at long subjects carries a measured long-subject cell
  as a second input row, and the derivation reads it like any other.
- **When the set has no `θ_hot`**, `measured` does not presume one (no silent defaults).
  **RULED (Q6, D163 addendum 8): fall back to the `0` layout, with two distinct stamped
  reasons.** Under switches, artifact row T1 (§3.4) resolves the threshold to `none` and
  stamps `<PREFIX>_PART_LAYOUT_WHY "threshold-unmeasured"`. With `+1`'s preset alone, every
  other layout control is unset, so the artifact takes the `0` layout exactly (row T0).
  An explicit class value or residual still applies: the ruling made the position fall back,
  and an explicit control beats the position (addendum 8). This is TODAY's state: no set carries the
  inputs. The only measurement is revision 1's callgrind Ir on Zen 4 (5-29 Ir per call,
  §2.2), which is an instruction count, not a cost in set units, and is LABELLED UNMEASURED
  for the set. [r4] Both stamps are reachable from E1, by `--part-inline-rank=measured`;
through `+1`'s preset only once that cell is live (§3.4.1).
- **What moves when the set changes.** Only artifacts whose threshold resolves to
  `measured` (today: `+1`'s preset, or a caller who typed it), through `θ_hot`. No other
  control value reads the set. A default-set change carries its mover census (D166
  item 1, Q1), and at `0` no set change can move a byte.

The quantities the cells need, owed per box (unchanged from revision 1, named as the
inputs above):

| quantity | unit (D166 item 2: relative) | measured here | owed |
|---|---|---|---|
| `C_part(r)`: one static part call over the inlined form, per rank | per call, in units of the scalar walk's per-byte cost | 5-29 Ir per call (callgrind, Zen 4; R2 only; UNMEASURED in set units) | ns per call, short-call regime, per box (a quiet slot); R3 needs a witness first (§3.2.1) |
| `C_plt`: an exported-sibling call over a static part call | per call | ≈ 4.8 Ir per call (one witness) | not read by any row: I3 removes the edge instead of pricing it |
| `b_part`: the part's object bytes | bytes | the per-function sizes in `layout.tsv` | the corpus distribution by part class, for each cell diff's size axis |

A cell diff (E1′) is argued with D103's rubric. `inline` is argued where `C_part · calls` is
material against the walk and the extra `.text`, `(k − 1) · b_part`, fits the position's size
budget. The diff cites both axes.

### 3.4 The declared tables

The decision is two first-match tables and one small wrapper table. Every conjunct is listed,
so the listing can show it (D163 add. 4), and there is no if-then logic outside the tables.
[r4] The position appears in no row of either table. It reaches them only through the
preset cells that row K reads.

**The artifact table, evaluated once per artifact before any part** [r3 CE-1, CE-12, F3; r4].
Unlike the part table it applies EVERY row in order (K, then T1 or T2 at most once, then T0
or T3), because K and T1/T2 compute values that T0/T3 read.

| # | row | conjuncts (all hold) | effect | stamp |
|---|---|---|---|---|
| K | `resolve` | (always) | each control C1-C6 := the caller's value if set, else the position's preset cell (§3.2.4; a `†` cell is an em-dash), else unset | — |
| T1 | `rank-unmeasured` | the threshold resolved to `measured`; the active set has no `θ_hot` | the threshold := `none` | `_WHY "threshold-unmeasured"` |
| T2 | `rank-none` | the threshold resolved to `measured`; `θ_hot` = `none` | the threshold := `none` | `_WHY "no-material-rank"` |
| T0 | `as-emitted` | every class value is unset or `auto`; the threshold is unset or `none`; the residual is unset or `auto` | every function keeps its `0` layout (I4); the part table is not consulted | `_WHY` only if T1/T2 fired |
| T3 | `per-part` | (otherwise) | consult the part table for each part | `<PREFIX>_PART_LAYOUT` (§3.4.1) |

T0 makes `0` with no control, every position whose cells are still `†`, and an all-`auto`
request byte-identical by construction: nothing below it runs. Because T1/T2 run before T0,
`+1`'s preset with no `θ_hot` reaches T0 and gives the `0` object exactly (Q6, RULED). In
revision 2 it did not: L1-L4 ran first and L4 added `always_inline`. In revision 3, T1/T2
were decided by the position; in revision 4 by the threshold's value, so a caller's
`--part-inline-rank=measured` declines the same way.

**The part table, evaluated per SUBJECT or OWNED function (§3.1) when T3 fires.** Constraint
rows P1-P3 come before every control row, so no control overrides them (Q2): P1 keeps every
owned function out of the control rows. The table ends in an unconditional row, so it is
total.

| # | row | conjuncts (all hold) | layout written | evidence | revision 3 row |
|---|---|---|---|---|---|
| P1 | `owned` | the function is in the OWNED class (§3.1): A1's helpers and matcher (its rung's attribute), A2's `_deep` (`noinline`, load-bearing), A4's seam (`static inline`) | its owner's attribute, unchanged | [r3 CE-1, CE-2, LK-6]; [OPT-1]; [LOSS-REVIEW] candidate 1 | P1 |
| P2 | `not-copyable` | `copyable(part)` is false | `static noinline noclone`, one body | gcc errors (§2.1 H1, H2); [r3 LK-4, LK-3] | P2 |
| P3 | `single-caller` | `callers(part)` = 1 | its `0` layout (no attribute added) | H3: sharing measured +112 B for nothing; [r3 CE-1] | P3 |
| P4 | `class-shared` | the part's class value = `shared` | `static noinline noclone`; wrappers by the W-table | §3.2.2 C1-C4 | — |
| P5 | `class-inline` | the part's class value = `inline` | `always_inline` | §3.2.2 | — |
| P6 | `class-auto` | the part's class value = `auto` | its `0` layout | §3.2.2; I4 | — |
| P7 | `rank-hot` | the threshold is a rank; the part's rank ≥ it | `always_inline` | §3.2.2 C5, §3.3 | P5 (`−1`, R3), P7 (`+1`) |
| P8 | `residual-shared` | the residual = `shared` | `static noinline noclone`; wrappers by the W-table | §3.2.2 C6 | P4 (`−2`), P6 (`−1`) |
| P9 | `residual-inline` | the residual = `inline` | `always_inline` | §3.2.2 C6 | P9 (`+2`) |
| P10 | `residual-auto` | (otherwise: the residual is `auto` or unset) | its `0` layout | I4; Q8 | P8 (`+1`) |

**The two constraint kinds.** P1 and P2 are HARD: P1 is a load-bearing owner's attribute
(A2's `_deep`: inlined, its arrays move onto the entry's frame) or another row's subject
(A1, CE-2); P2 is a gcc error. P3 is a MEASURED POLICY row: sharing a single-caller part is
a measured loss (H3), and an inline request on one adds nothing gcc does not already do at
`-O2` (a static function called once is inlined). A later ruled diff may relax P3; a control
may not. Both kinds hold a request the same way, and §3.4.2 says how that is reported.

- **`copyable(part)` is ONE legality fact** [r3 LK-4, SIB-1]. It is false where the body
  defines a static label table (the DFA attempt route, H1) or contains a computed goto (H2).
  On the VM, H2 is `has_push`: `vm_plan_entry`'s own invariant is that the `goto *` count is
  `(has_push ? 1 : 0)` plus shared-callee bodies, both terms of `has_push`, so `may_attr =
  !has_push` already IS this fact for VM bodies. P2 reads `may_attr` and the label-table
  fact; it does not compute a second copy of either. gcc's other refusal causes (`alloca`,
  `setjmp`, variadic functions, recursion through the part) appear nowhere in emitted text
  at this tip (grep of `src/gen`, `src/enc`, `memfn/src`). E1's census holds that population
  at zero, and a planted one fails the build. Member A1 consumes the same fact when it
  migrates (U-B).
- **P1 comes first** [r3 CE-1, CE-2]. A2's `noinline` on `_deep` is load-bearing (inlined,
  its arrays sit on the entry's frame and gcc probes every page on every call), so no
  position and no control may override it. A1's attributes are the `--vm-entry-shape` row's: until the
  ruled diff that migrates A1 under this row, the two dial rows are CO-RESIDENT on a VM
  artifact with DISJOINT subjects [r3 CE-2, F7]. P1 excludes A1's functions from every
  control row, so the two rows never write the same function. That disjointness is
  checked (§3.6), and without it `--part-residual=shared` (or `−2`'s preset) would write
  `static noinline` on a matcher the `inline` rung marks `always_inline`.
- **The seam inside P1** [r3 LK-6]. A seam body is a small loop with no label table and no
  computed goto, so `{seam} ∩ {not copyable}` is empty. A fixture asserts it, because P1's
  owner attribute (`static inline`) on a non-copyable body would be a build error.
- **P2 adds `noclone`** [r3 LK-3]. `noinline` does not stop ipa-cp (`.constprop`), ipa-sra
  (`.isra`) or partial-inlining (`.part.N`) clones; K24 found `noclone` on the callee was
  the only cure. P2, P4 and P8 write it under `__has_attribute`, A3's spelling. The linkage
  critic's three-caller test did not clone, so the observable is carried by a check that
  counts clone symbols per part, not by an argument (§3.6).
- **Every row writes only on a STATIC function** [r3 LK-9]. gcc rejects `always_inline` on
  an exported callee under `-fPIC` ("function body can be overwritten at link time").
  Exported entries are never parts (§3.1), and I3 gives every multi-entry body a static twin
  before a cell lays it out. A negative test (§3.6) plants `always_inline` on an exported
  callee and expects the `-fPIC` build to fail.

**The wrapper table** [r3 LK-2]: for each wrapper that calls a body P4 or P8 shared (in
revision 3, at `−2` and `−1` only).

| # | row | conjuncts | wrapper written | witness |
|---|---|---|---|---|
| W1 | `forward` | `forwardable(w)`: the wrapper's parameters pass to the body unchanged and in order, with no local array and no adapted argument | `return body(args);`, which gcc compiles to `jmp body` with no frame | the `_search_in`/`_search` shape (measured: identical argument lists compile to `jmp`) |
| W2 | `adapt` | (otherwise) | the wrapper keeps its adaptation and calls the body: a frame, a `call`, a canary under `-fstack-protector-strong` | the compound `_match` (`emit_first_nonzero_match`: a local `capture_spans[NCAPS][2]`, `caps` adapted) |

W2 is the fallback revision 2 left implicit: it fell back silently to `plain`'s shape [r3
LK-2]. The VM chain's `may_fwd` is a sibling fact (it adds the storage condition: the
artifact writes no working storage), and joining the two is unlock UNL-2.

**Not rows of these tables, and why:**

| item | where it lives |
|---|---|
| H4: `info` and `main` are not static | they are entries, not parts (`pcrec_entry_shape`'s request check) |
| H5 / I3: no exported-to-exported call | a linkage rule of `entry_rows[]` (§3.0) |
| H6: layout text is excluded from every length decision | I5: the layout pass renders after every decision, on every emitter |
| H7: `noclone` on every search head | an orthogonal attribute (A3, K24), kept at every position |
| the kit's FUNC helpers (A7) | the kit's (D157); pcrec can pass the position as a fact (U8) |
| A1's migration under this row | its own ruled diff: `−2`/`−1` take the `shared` rung where it is legal and AUTO's term otherwise (F-5: `plain` is not the size end below the term); `+2` takes `inline` on a frameless artifact. Until then, P1 |

#### 3.4.1 What a caller can observe [r4: per control, not per position]

| observable | every control value, every position |
|---|---|
| answers, captures, give-up codes | identical (I1: layout never decides which parts exist or what they compute) |
| refusal set, every stamped selection other than the layout's own | identical (I5: the layout renders after every length decision) |
| `RX_TUNE` | the position's token, as today; it no longer determines the layout |
| `<PREFIX>_PART_LAYOUT` (proposed) | absent when T0 fires. Otherwise the RESOLVED non-trivial controls, in a fixed order: `residual=V`, `rank=R` (`rank=R@set` when it came from `measured`), then each class with a set value as `CLASS=V`, with `/held` appended when a constraint row held at least one part of that class (§3.4.2). Example: `"residual=shared;rank=R3;find=inline/held"` |
| `<PREFIX>_PART_LAYOUT_WHY` (proposed) | `"threshold-unmeasured"` (T1) or `"no-material-rank"` (T2); absent otherwise |
| object symbols (`nm`) | one local symbol per part a `shared` row wrote; no symbol for a part an `inline` row wrote; the owners' choices for owned parts; gcc's own for `auto` |
| layout flips with `-fPIC` (F-2) | no, for a part a `shared` or `inline` row wrote; yes, for an `auto` part, as today |
| time | each control value's cost (§3.2.5); the parity gate binds presets `0`, `+1`, `+2` only (§3.5) |

- **Why `<PREFIX>_PART_LAYOUT` returns** [r4]. Revision 3 dropped it (LK-7) because the
  layout was a pure function of the position plus `θ_hot`, and `RX_TUNE` already named the
  position. Under switches the layout is a function of six controls, five of them not
  recorded anywhere else, so D46's observability rule needs a stamp. It is written ONLY when
  T3 fires, so an artifact with no layout control (every artifact today, and every one at
  `0`) is byte-identical: E1 moves no default artifact.
- **`_THETA` is folded into the `rank=` token** (`rank=R2@set`), so revision 3's `_THETA`
  stamp is withdrawn. `_WHY` stays a separate stamp because Q6's ruling names two stamped
  reasons, and a decline can happen with T0 firing, where `_PART_LAYOUT` is absent.
- **Both stamps are caller-observable from E1**, not from `+1`'s first live cell as revision 3
  had it: a caller can type `--part-inline-rank=measured` or `--part-layout=...` at E1. So
  their D80 hunks (tuning.md §5.3, `match_api.md` §6.3's stamp list), D94's reader grep
  (`stamp_kinds.c`, `memfn_stamps.c`, the registry's stamp tests) and `make test-codegen`
  plus the registry suites are E1's (§3.9, §5.1).
- **No `rx_info` mirror** (tuning.md §5.3¶2: nothing at run time behaves differently).
- **The stamp grammar is a proposal.** Its spelling is the manager's call and [STAMP-REVIEW]
  may respell it; the content (resolved values, source of the rank, `/held`) is what this
  note fixes.

#### 3.4.2 How a held request is reported [r4]

A caller can ask for something a constraint row will not do: `compound:inline` (split's F
has a label table, P2), `prefilter:shared` on a framed hybrid (one caller, P3), `wrap:V`
before I3 (no subject). The rule is tuning.md §2.21¶3's: **a value the artifact cannot honour
is a selection outcome, never a refusal.** A refusal would break a build over a choice that
cannot change an answer, and a build script setting one control across many patterns would
fail on every pattern where the class happens to be held. It is reported at three levels:

| level | what it shows | where |
|---|---|---|
| the stamp | `CLASS=V/held` when at least one part of the class was held by P1-P3; a class with NO subject in the artifact is written `CLASS=V/none` | `<PREFIX>_PART_LAYOUT` |
| the listing | one row per subject and owned function: its control class (or `owned`), callers, rank, `copyable`, the row that fired, the layout written | a new `part-layout` section of `--emit-facts` (cli.md §2.11) |
| the census | per (class, value), how many parts each row fired on, corpus-wide | E1's per-row census (§3.6) |

No stderr note: a held request is not an error, and the VM entry chain's fallback rungs emit
none either. The stamp makes it visible to a build script, and the listing to a person.

### 3.5 Interaction with the iterator's parity gate and the mode M

- **The parity gate** (D165 item 5, `findall_iter.md` §5.3): `next` at parity or better than
  today's `_search` loop on dense tiny matches. **RULED (Q3):** the gate binds positions
  `0`, `+1` and `+2`; at `−1`/`−2` the gap is that cell's cited time cost, reported, not
  gated. `__find` is rank R2 (one call per `_search` or `_next`), so `−1` shares it like
  `−2` does. Only the internal batch fill (R3, HELD) would separate them on an iterator
  artifact [r3 F4]. `+1` inlines `__find` when `θ_hot` ≤ R2. Otherwise (`θ_hot` = R3, or
  T1/T2's decline) `__find` keeps its `0` layout, which is §2.2's design of record, so `+1`
  is never slower than `0` on it [r3 F3, Q8 note]. [r4] The gate binds the PRESETS `0`, `+1`
  and `+2`, not a caller's explicit controls: a caller who types `find:shared` (or
  `--part-residual=shared`) asks for the `I_shared` layout and takes its cost, as a caller
  who types `--vm-entry-shape=1` takes `plain`'s. The gate's two arms are exactly those two
  control values, so it measures what the controls do.
- **M folds only where the locate part is inlined.** `findall_iter.md` §4.2 makes the call
  mode M a parameter of `__find`: a compile-time constant in each entry when inlined, one
  runtime branch per call when shared. So the layout controls also decide whether the kit's
  dispatch on M (regime_tables.md R1-R3) costs a branch: it costs one wherever `__find` is
  shared (`find:shared`, a `shared` residual, `−2`/`−1`'s presets), at P2 (the attempt
  route's label-table body, shared under every control), and wherever `__find` is shared at
  `0` by §2.2. A size-leaning control pays that branch knowingly, as part of its cited
  cost.
- **The kit's helpers (A7) are the kit's** (D157: pcrec sends facts, not methods).
  pcrec can tell the kit the dial position as a fact (it already does for the class kit,
  D131); how the kit lays out its helpers is its choice. A request, not a pcrec cell. [r4]
  The resolved layout controls are facts of the same kind; whether the kit wants them is
  its request to make (U8).

### 3.6 Checks (each with its independent control)

[r4] Revision 3's checks keyed on the POSITION; revision 4's key on the RESOLVED CONTROLS, and
the position enters only through the preset check. Because explicit controls are live from
E1, every row is reachable at E1 by flags on corpus artifacts. Revision 3's arms that were
UNREACHED "until the first live cell" are reached at E1.

- **`0` is byte-identical** [r3 CE-10]: `scripts/emit_sweep.py` against pre-E1 main, every
  stream. That is the only control cited. `run_tune_dial.sh` section 1 checks one pattern
  and both sides go through the same `tune.c` resolver, so it is not an independent control.
  [r4] The same sweep with `--part-layout=prefilter:auto,compound:auto,find:auto,wrap:auto
  --part-residual=auto --part-inline-rank=none` must also be byte-identical (T0).
- **A layout is read from the OBJECT and judged against an expected set that shares no code
  with the tables** [r3 CE-7, CE-8]. A separate evaluator, a script under `tests/` that links
  nothing from `src/`, computes the expected layout per artifact and control setting from
  four inputs:
  - the call graph of a COPY of the emitted C with every `always_inline`, `noinline` and
    `noclone` deleted by text, compiled `-O2 -fno-inline` and read from `objdump -dr`
    relocations. It is needed because under `-fno-inline` an `always_inline` function is
    still inlined and shows no edge; the stripping happens in the checker, so the emitter
    and its bytes do not move;
  - the owners' attributes, read from the ORIGINAL emitted text, to fold owned
    `always_inline` functions into their callers (the `callers` definition, §3.2);
  - the hand-written rank fixture and a hand-written class map (function-name pattern →
    control class, from §3.1's table);
  - [r4] the RESOLVED controls, computed by the evaluator from the compile's own arguments
    and tuning.md §5.4's preset rows (read from the spec text, as `run_tune_dial.sh` does),
    never from `tune.c`, and the row order from the spec's prose.

  `nm` on the real object must show each shared subject part as one local symbol and each
  inlined one absent. The compiler is the judge of what was inlined; the evaluator is the
  judge of what should have been.
- **The rank fixture is a precondition of E1** [r3 LK-1]. It is hand-written from the emitted
  C, names one witness artifact per rank, and lands with E0's rank column. A rank with no
  witness (R3 and R1 today, §3.2) is reported UNWITNESSED, never passed. The census reports
  `callers` as distinct functions, never call sites.
- **Corpus first, synthetic only where the corpus has no SUBJECT** [r3 CE-7, Q9; r4]. With
  controls live, a row is exercised by setting the control that reaches it on a corpus
  artifact that has a subject of that class: P5 by `prefilter:inline` on the `(a)b`-class
  hybrids, P8 by `--part-residual=shared`, P7 by `--part-inline-rank=R2`, P2 by
  `compound:inline` on split. A synthetic artifact is used only where NO corpus artifact has
  the subject (an R3 prefilter re-entered by the retry, an R1 copyable part, a copyable
  multi-caller compound part). Its expected `nm` set is written by hand in the fixture, and
  the result is read from the object. The synthetic witness is never also the control.
- **Preset resolution** [r4]. For each position, the evaluator's resolved controls (from
  tuning.md §5.4) and the artifact's `<PREFIX>_PART_LAYOUT` agree, over the corpus. While
  every layout preset cell is `†`, every position must resolve to T0 and carry no
  `_PART_LAYOUT` stamp. That is a real check today: it fails if a `†` cell leaks.
- **Precedence** [r4]: a fixture of control combinations with hand-written expected rows per
  part: an explicit value beats the preset's for the same control; a class value (P4-P6)
  beats the threshold (P7); the threshold beats the residual (P8-P10); `measured` declines
  only through T1/T2.
- **Held requests are reported** [r4]: `compound:inline` on split stamps `compound=inline/held`
  and lists P2 for F and P3 for Q in `--emit-facts`; `wrap:shared` before I3 stamps
  `wrap=shared/none`. Expected strings are hand-written.
- **H1/H2 and LK-9 by construction**: a planted `always_inline` on an attempt body must fail
  the build, and so must one on an exported callee under `-fPIC`. The gcc error is the
  detector.
- **Clones** [r3 LK-3]: per artifact and control setting, count `.constprop`, `.isra` and
  `.part.N` symbols derived from each shared part's name; any is a failure.
- **A1 and the layout controls are disjoint** [r3 CE-2]: per VM artifact and control
  setting, the set of functions P1 assigns to A1 and the set any control row writes are
  disjoint, checked on the emitted text.
- **The seam is copyable** [r3 LK-6]: the fixture of §3.4.
- **Stamp neutrality** [r3 CE-9; r4]. `make test-axes` compares answers and refused-key sets
  (DIAL-S3), not stamps. The new arm diffs every `#define <PREFIX>_*` except
  `<PREFIX>_TUNE` and `<PREFIX>_PART_LAYOUT*` between an artifact built WITH a layout
  control and the same compile WITHOUT it. Revision 3 used the cell diff's parent as the
  control and was UNREACHED while every cell was `†`; with controls live, the no-control
  build is the control and the arm is reached at E1. A preset cell's own diff keeps
  revision 3's parent-based arm, because other dial rows (A1's term, λ, the ladder)
  legitimately move stamps between positions.
- **Answer identity**: `make test-axes` sweeps the controls as value axes, on
  `--vm-entry-shape`'s tiered precedent (tuning.md §2.21¶6): every run sweeps
  `--part-residual=shared` and `--part-residual=inline` (the two ends); `AXES_FULL=1` sweeps
  each class value and each rank value. The summary prints its tier.
- **Length neutrality on every emitter** [r3 LK-8]: the near-cap witnesses (the lowered-cap
  manifests of `r17c_nearcap.py`, the K59 and `[ART-SIZE]` witnesses) refuse and select
  identically under every control setting on the VM, DFA and compound emitters. This tests
  I5. [r4] The same witnesses carry the owed near-cap SIZE reading (§3.2.5): each class's
  `.o` delta on the largest artifacts, recorded, not gated.
- **The decline is visible**: a compile with the threshold resolving to `measured` against
  a set without `θ_hot` carries `_WHY "threshold-unmeasured"`; with no other control its
  object equals `0`'s and it carries no `_PART_LAYOUT`.
- **The attribute census**: every `__attribute__((always_inline|noinline|noclone))` and every
  `static inline` in an emitted artifact belongs to a row of §3.4 or a class of §3.1. An
  unlisted writer fails. This is the "single attribute-writing table" unlock's check, built
  at E1 even though the writers themselves stay where they are (§5.3).
- **Totality and population, per row** [r3 CE-4]: every (subject part, control setting) in
  the census reaches exactly one row, and each row's population is counted per control value
  and per preset (K35). A row whose population is zero is listed with its reason.

**Sabotage, PROPOSED ids** (S999-S1008 allocated by the manager 2026-10-16, re-aimed for
revision 4's rows; three new plants have NO id yet and need three from the manager):

| proposed id | plant | detector |
|---|---|---|
| S999 | P1 drops `_deep` (A2) | the object check: `_deep` must stay a local symbol under every control setting |
| S1000 | P1 drops A1's functions | the A1-disjointness check under `--part-residual=shared`; the `-Werror` harness compile (gcc 15.2 warns "ignoring attribute 'noinline' because it conflicts with attribute 'always_inline'" [-Wattributes], checked on a two-line probe in revision 3's scratch) |
| S1001 | T1/T2 moved below T0 (or T0 evaluated before them) | emit_sweep: `+1` without `θ_hot` must equal `0` byte for byte and carry `_WHY` |
| S1002 | P2 dropped | the build: gcc refuses `always_inline` on a label-table body under `compound:inline` |
| S1003 | `noclone` dropped from P2/P4/P8 | the clone-symbol count |
| S1004 | `forwardable` always true | the build and answer checks on the compound `_match` under `wrap:shared` (after I3) |
| S1005 | `callers` counts call sites | the evaluator's expected set against `nm` on a two-site, one-function part |
| S1006 | `θ_hot = none` read as R3 | the `none` witness: the object must equal `0`'s and carry `_WHY "no-material-rank"` and no `rank=R3@set` |
| S1007 | the layout pass rendered before the size caps | the near-cap refusal arm |
| S1008 | the rank column's R3 cell read as R2 | the rank fixture |
| (new, id owed) | row K takes the preset's cell over a set caller value | the precedence fixture |
| (new, id owed) | P7 placed above P4-P6 (the threshold beats a class value) | the precedence fixture: `prefilter:shared --part-inline-rank=R2` must keep the prefilter shared |
| (new, id owed) | the `/held` marker dropped | the held-request fixture's hand-written stamp |

### 3.7 Which family the row belongs to (the sibling-of-a-family lens)

| candidate family | member? | why |
|---|---|---|
| **the dial's policy table** (tuning.md §5.4, D103) | **YES: one more row of it** | It is a speed/size trade with a pinned policy per position. Its acceptance is the dial's: answer identity at every position, `balanced` byte-identical. It is the first row whose cell reads a value from a measurement set (`θ_hot`, Q1's D103 clarification). Its nearest siblings in that table are the λ row, the `--vm-entry-shape` term row and the `-fno-tiered-entry` row (§3.1) [r3 F2] |
| **the inline/shared writers** (§3.1) | **co-resident, not unified** [r3 CE-2, F7] | Two decisions exist (A1, §2.2) and four fixed writers. The row SUBJECTS are group C plus the designed iterator parts; the owners A1, A2 and A4 are kept by P1. `findall_iter.md` §2.2's table stays as the `0` cell's content (§3.8). A1 joins only by its own ruled diff (§3.4). Until that diff lands, two dial rows lay out parts on a VM artifact with disjoint subjects, which §3.6 checks |
| **`entry_rows[]` and `compound_place[]`** (§4.1, `compound.md` §A.2) | **sibling, not merged** | All three answer "where does a part's body live". `compound_place[]` decides whether a second machine is an in-Job row or a compound part (machine composition); `entry_rows[]` decides which parts an entry calls (the edges); this row decides how an existing part is linked to its callers. The layout row reads `entry_rows[]`'s edges and is applied by it. Merging it with `compound_place[]` would mix a semantic choice (which machines) with an answer-free one (copies) |
| **engine selection** (`select_engine.c`, `--engine`) | no | Engine selection chooses the machine and can move answers and refusals (GATE 2). Part layout sits below the machine and moves neither |
| **the deny/force axes** (`axes.def`, tuning.md §2) | no | It is not a bit and has no deny or force spelling, like `--vm-entry-shape`'s value field and the `[ART-SIZE]` ladder's parameters. An explicit override spelling (a `--part-layout=` value, `--vm-entry-shape`'s precedent) is caller-observable CLI, so it is FILED for [IFACE-PUSH] and not designed here. `make test-axes` sweeps the row through the dial's existing arm, plus the stamp arm (§3.6) |
| **`regime_tables.md`** | no; a neighbour with two shared edges | Regime rows are run-time form selection inside the LOCATE part, owned by the kit (D157); this row is compile-time linkage of whole parts. Shared edge 1: this row decides whether M is a compile-time constant in the kit's dispatch (§3.5). Shared edge 2: both read the measurement set, through the same knowledge key A (regime_tables.md §2), so a set change re-selects both, in one mover census |

So the row is a dial row (D103) whose subjects are the parts gcc lays out today. It sits
beside the owners and does not absorb them, and it is applied by `entry_rows[]`. It is a
sibling of `compound_place[]` under that table, not a new family and not a new axis.

### 3.8 Where the iterator consumes this row (for `findall_iter.md`'s short revision; not edited here)

Q4 puts a short revision of `findall_iter.md` after E0. This is what that revision would
read from this row. This note does not edit `findall_iter.md`.

| `findall_iter.md` piece | what it becomes under the row |
|---|---|
| §2.2's two-row emission rule (`shared` for a label table, else `inline`) | **KEPT, as the `0` cell's content** [r3 F3]: by I4 it is `__find`'s `0` layout, and T0 leaves it untouched. At non-zero positions `__find` is a subject part: P2 for the attempt route (the same `static noinline` as §2.2's `shared` row, now with `noclone`), then the position's row. §2.2's explicit `static noinline` is what makes `_search` a 9-byte tail jump, and P2 keeps it |
| §2.2's trigger: "inline until `I_shared` is measured" (D77) | **KEPT, as unlock U1's trigger** [r3 F5]. `I_shared` is the `−1`/`−2` layout of `__find`, and the gate measures it anyway (Q3). If `I_shared` is within the noise floor of `I`, promoting "shared for every body" to the `0` cell is a ruled diff of the ITERATOR's design, not of this row |
| `__find` | callers `_search` and `_next` (`_next_n` HELD): 2; rank R2 (R3 only with the HELD internal batch fill, D165 add. 2 Q2); rows P2/P4/P6/P7/P8/P9 by route and position |
| `__adv` (the residual's static twin) | I3's static twin; called from `__step`, which folds into `_next`: 1 caller; rank R2; P3 (keeps §2.1's `always_inline`) |
| `__step` | 1 caller (`_next`); rank R2; P3 [r3 F4] |
| `__enter` | 1 caller (`_next`); rank R2; P3 [r3 F4] |
| the NOTEMPTY retry R | NOT a part: it is a body inside `__step` with no symbol of its own [r3 F4]. Revision 2's "`θ_hot` = R1 inlines the retry" is withdrawn. If the retry becomes its own static part (the `first-nonzero` emitter's shape, §4.2), it is rank R1 and a subject |
| `_next_n`'s calls | HELD with `findall_iter.md` Q2 (D165 add. 2 Q2 reframes it as internal batching) |
| the parity gate's `I` and `I_shared` arms (§5.3) | `I` = the `0` / `+1` / `+2` layout of `__find`; `I_shared` = the `−2` / `−1` layout. The gate binds the first (Q3) |
| M as a constant (§4.2) | constant where `__find` is inlined, a branch where it is shared (§3.5) |

---

## 4. Convergence: one declared entry table

### 4.1 `entry_rows[]`

[EMIT-ENTRIES] already has the entry ENUM and a linkage closure over a hand-written edge list
(`entries.c`'s `entry_edges[]`: `{from, to, when}` between entry ids, with no combinator
and no rank). **`entry_rows[]` does not exist** [r3 LK-1]. The proposal adds the controller
as a column, so the edges are DERIVED, and adds a RANK to every part reference, which is new
data, not a derivation:

```c
typedef struct {
    PartId part;                 /* the static part or in-Job row called            */
    EdgeRank (*rank)(const PcrecEntryShape *s);   /* R0..R3 for this shape (§3.2):  */
                                 /* a shape predicate, as `when` is, because one     */
                                 /* edge can hold call sites of two kinds (the       */
                                 /* prefilter's entry call R2, its retry re-seed R3) */
} PartRef;

typedef struct {
    PcrecEntry entry;            /* the exported (or kept) entry this row defines   */
    bool (*when)(const PcrecEntryShape *s);   /* the shape this row serves        */
    CompComb comb;               /* locate-then-finish, finish-at, forward,          */
                                 /* first-nonzero, select-by-arg, dispatch, iterate  */
    const PartRef *parts; int nparts;   /* the static parts / in-Job rows it calls */
    CallMode mode;               /* ONESHOT, ITER: a constant per entry (§3.5)       */
} EntryRow;
```

The rank cells are written by hand from the emitters' call sites, so they need an
independent check from the start: the hand-written rank fixture lands with them in E0 and is
a precondition of E1 (§3.6). Some rank sources are call sites INSIDE a body that the edge
list does not see today, such as the hybrid's retry re-seed in `_search_run`'s text. The
rank predicate reads the same facts the emitter reads to write that site (`nclamp`, the
re-seed row), never a scan of the text.

- **The edges are the rows' part references**, so the closure reads what the controller
  calls. `entries.c` missed the `rev-end` tie's `search -> match` edge in B0 and the check
  found it (cpb02 finding 1); a derived list cannot drift from the emitter that uses it.
- **Each combinator has ONE emitter** (`emit_compound.c` has the first, `first-nonzero`).
  `forward` is today's `emit_in_entry_defs` and the VM's forwards; `finish-at` is axis G's
  dispatch; `locate-then-finish` is the body. Moving them under the table is a re-spelling,
  byte-identical (§5.1 E0c).
- **The layout row (§3) is applied once, by the table**, to every SUBJECT part (§3.1's
  population), after every length decision (I5).
- **It is D88 addendum 1 stated as data**: one exported call interface per file is the set of
  EXPORTED rows, and everything else is KEPT STATIC or OMITTED by the closure.

### 4.2 What the iterator design would change to be expressed as a controller

| iterator piece (`findall_iter.md`) | as a row of the table |
|---|---|
| `__find(…, M)`, one body, two entries (§2.1) | the search controller's body as a part, called by `_search` (M = ONESHOT) and `_next` (M = ITER) |
| §2.2's two-row rule (`shared` for a label table, else `inline`) | the `0` cell's content (I4), kept; at non-zero positions the part table's P2 and position rows (§3.4, §3.8) |
| the NOTEMPTY retry (`findall_iter.md` §3.3) | `first-nonzero(R@q, SEARCH@next_pos(q))`: split's combinator, with R = FINISH `verify-at` on the notempty root (an in-Job machine role, `compound_place` row 3) on the DFA, or the VM's guarded attempt |
| `__step`, `__enter`, `__adv` | `iterate(STATE; …)`: `__enter` is the state part's bind/check, `__adv` the residual's static twin (H5) |
| the storage-row table (§1.3) | the STATE part's declared rows; a compound's parts SUM (D165 item 4) |
| `next_n` (§2.3) | another `iterate` row with a batch sink, behind Q2's trigger |

The one real change: the retry stops being iterator-specific machinery and becomes a use of a
combinator that already exists. Everything else is the same code under a row.

**Can it stay zero-mover?** I0 is already zero-mover (facts, `iter_rows.def`, tests,
`findall_iter.md` §6.9). I1 is one abi event whatever its spelling, because it adds an
exported symbol to every artifact. Expressing I1 as a row moves nothing beyond I1's own event
IF the table already exists, which is why E0 goes first (§5.1).

### 4.3 The compound's B-steps as rows

| step (`compound.md` §F) | as a table row |
|---|---|
| B4 split (built) | `first-nonzero` row on the compound shape; its controller emitter is the first combinator emitter |
| B5 S+F | the same row, wider admission |
| B6 VM parts | the call-site table's rows 3, 4, 7 (no table change) |
| B7 captures on demand | a `select-by-arg` row: the first run-time selector, emitted as a first-match row list (D163 add. 4) |
| B8 the cross-call hook | dissolves into the STATE part (`findall_iter.md` F7) |
| §D.5 arch variants | a `dispatch` row: the artifact-grain twin of the kit's site-grain selector (D155) |

### 4.4 Arch dispatch and the regime table

- **The regime table's run-time rows** (regime_tables.md R1-R4: N, M, H) are kit-owned and
  live INSIDE the locate part (the kit's site). In this model they are a `dispatch` on call
  facts inside one part, not an entry-level combinator. pcrec's share is the knowledge
  plumbing: M as a constant per entry (§3.5), N at the storage point, H's region in `st`.
- **Arch dispatch has two grains.** The kit's D155 selector chain is the SITE grain (built,
  inside FUNC helpers). `compound.md` §D.5 is the ARTIFACT grain (a `dispatch(level)` row over
  whole parts, keyed on the D166 measurement set and the ISA), filed behind D144 add. 4. The
  entry table gives the artifact grain a home without a second mechanism.

---

## 5. What moves, the path, and the rest

### 5.1 Stages (implement-then-replace)

| stage | what | movers | abi |
|---|---|---|---|
| **E0a** | `entry_rows[]` beside today's emitters; the derived edge set held against `entries.c`'s hand list for every corpus artifact (the trace-build both-walks oracle shape, `stc2`). ADDS the rank column (new data, §4.1) and its hand-written rank fixture, one witness per rank or UNWITNESSED [r3 LK-1] | ZERO | none |
| **E0b** | the closure reads the derived edges; the hand list deleted | ZERO | none |
| **E0c** | each emitter's entries written through the row's combinator emitter | ZERO (emit_sweep, every stream) | none |
| **E1** | the layout row: §3.4's artifact table T0-T3, part table P1-P9 and wrapper table W1-W2 as declared first-match tables, read by `entry_rows[]` and rendered after every length decision (I5); every non-zero cell `†`, so T0 makes every position emit as `0`. The checks of §3.6 that can run at `†`: the separate evaluator, the attribute census, the A1-disjointness and seam fixtures, the per-row population census; the stamp arm is UNREACHED | ZERO | none |
| **E1′** | each cell, by its own ruled diff with its size and time measurement. PRECONDITION: I3 holds for every part the cell lays out, from I1 (residual twins, F-1) or from the cell's own diff (wrapper twins) [r3 LK-5]. `+1`'s first live cell adds `<PREFIX>_PART_LAYOUT_WHY`/`_THETA` with their D80 hunks (tuning.md §5.3/§5.4, `match_api.md` §6.3.11) and D94's reader grep (`stamp_kinds.c`, `memfn_stamps.c`, the registry's stamp tests), then `make test-codegen` and the registry suites [r3 LK-7] | that position's artifacts | one per cell diff (bytes move at that position) |
| I0 | `findall_iter.md` §6.9, unchanged | ZERO | none |
| I1 | `next` as an `iterate` row; the retry as `first-nonzero`; the STATE part | every artifact | ONE (as designed) |
| F-1 fix | the compound controller calls static twins of `_next_pos`/`_valid_upto` | compound artifacts (97 corpus, bench 0) | fold into I1, which adds `__adv` anyway |

Remodel overlap (memory `pcrec-remodel-first`): E0 touches the three entry emitters and
`entries.c`, exactly where I1 and B5-B8 work. It goes first or it is re-done.

### 5.2 The standing design questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — RELEVANT.** Every number is gcc 15.2 `-O2` on x86-64 (the Linux dev
   box). `.text` and function sizes are compile-only; instruction counts are callgrind Ir,
   deterministic, with no clock. Ir is not time: it ignores branch prediction, cache and the
   PLT's indirect jump cost, so a cell needs ns before it lifts (§3.3). `θ_hot` is read in
   the set's reference short-call regime; a long-subject regime would rank fewer edges as
   material, which is why the threshold is a set row and not a constant. Two regimes flip a
   decision: the link regime (static vs `-fPIC`, measured to flip gcc's own layout) and the
   compiler (clang inlines the VM chain where gcc stops, `ccdiff_step0.md`). Zen 1 and the Mac
   are the bench's official verdict (D144 add. 4).
2. **Independent control — RELEVANT.** The derived edges are checked against the hand list
   (E0a) and then against the object's own call graph (`objdump -dr`, as this lane's probe
   does), which shares no source with pcrec. A layout cell is checked from `nm`'s view of the
   object against a separate evaluator's expected set, built from an attribute-stripped
   `-fno-inline` call graph, the owners' attributes, the hand rank fixture and §5.4's
   policy text; it shares no code with the table (§3.6, [r3 CE-7, CE-8]). H1/H2 are gcc's
   own errors. Population: the 233 label-table artifacts (`findall_iter.md`'s census), the
   97 admitted compounds (`admitted.tsv`), VM framed/frameless from the size log; a K35
   floor per ROW and position at E1 [r3 CE-4].
3. **What moves when regenerated — RELEVANT.** E0 and E1 move nothing (emit_sweep). A cell
   diff moves that position's artifacts and is an abi event with D94's reader grep. Q1 ruled
   `θ_hot` into the measurement set: once `+1` is live, a set change moves `+1` artifacts
   only (no other position reads the set), with D166's mover census in the same commit.

### 5.3 Unlocks (each with its trigger)

| # | unlock | trigger |
|---|---|---|
| U1 | the layout row's non-zero cells (their policies are fixed by §3.2; each lifts from `†` by its own diff) | a measured short-call cell where `C_part` is material: the parity gate's `I_shared` arm, which is `findall_iter.md` §2.2's own D77 trigger, kept [r3 F5], or a bench cell traced to a shared part. `+1` additionally needs `θ_hot`'s inputs in a set |
| U2 | `rx_entries` (one struct of entry pointers, [V-E] item 1, [ART-MGR] S1): the EXPORTED rows are its fields | [IFACE-PUSH] |
| U3 | the public [EMIT-ENTRIES] request (a caller names the entry set): the rows already carry it | [IFACE-PUSH] |
| U4 | one-attempt `_match` on every attempt route (`compound.md` A-U1): a `finish-at` row swap | `locate_finish.md` Q7's measurement |
| U5 | captures on demand as a `select-by-arg` row | B7's trigger (`compound.md` §D.1) |
| U6 | artifact-grain arch dispatch | D144 add. 4: a SIMD form that must ship beside its scalar form |
| U7 | shared tables between parts (`compound.md` U6) | a compound pushed to `drop-compound` by size |
| U8 | the dial position passed to the kit as a fact for its helper layout | a kit request; the class kit's D131 is the precedent |
| U9 | an exemplar-refined edge rank (the analysis object says how often a conditional edge fires) | a bench cell traced to an R1 part that `+1` left out of line (Q7) |
| U10 | an explicit override spelling for the row (a `--part-layout=` value, `--vm-entry-shape`'s precedent) | [IFACE-PUSH] (§3.7) |
| U-T | ONE attribute-writing table: the owners' writers (A1's rung, A2's `_deep`, A3's `noclone`, A4's seam, A5/A6) become declared rows with owner and reason, so the table is the one place any linkage attribute is written. E1 already builds its CHECK (the attribute census, §3.6) and declares the owned rows; this unlock moves the writers [r3 unlock "single attribute-writing table"] | E1 itself for the check; the move waits for a writer that needs a position-dependent attribute |
| U-A | one `part_facts{callers, copyable, rank, forced_attr}` record per part as every row's input, so `_deep`, K24 and the seam read as rows rather than exceptions | the first non-zero cell going live |
| U-B | A1 migrates under this row: its size term and `θ_hot` become two cutovers of one row table (both position-indexed and unmeasured, [r3 SIB-2]); A1 consumes `copyable` instead of its own `may_attr` read; the λ row's form ladder and the layout rows share one "pick a form by size and speed" ladder | the ruled diff that migrates A1 (§3.4) |
| UNL-1 | the same edge rank drives `cold`/`hot` hints and `noclone` per part | a measured K24-style splitting loss on a part. Not before |
| UNL-2 | `forwardable(w)` (§3.4 W-table) and A1's `may_fwd` joined as one "forwardable" fact per entry | the first `−2` cell diff |

### 5.4 Revision 1's questions: RULED (D163 addendum 7)

| Q | ruling | applied in |
|---|---|---|
| Q1 pinned cell or measured selection | the POLICY is a pinned cell per position (D103); only `hot-inline`'s threshold comes from the set (D166), with its mover census; a D103 clarification | §3.2, §3.3 |
| Q2 `balanced` | stays as emitted; FIVE distinct positions; hard constraints are rows no position overrides | §3.2, §3.2.1, §3.4 |
| Q3 parity gate | binds `0`, `+1`, `+2`; at `−1`/`−2` the gap is the cell's cost | §3.5 |
| Q4 E0 before I1 | yes; then the short `findall_iter.md` revision, its panel, then I1 | §5.1, §3.8 |
| Q5 exported-to-exported calls | never; static twins; applied where a change already moves the bytes | §3.0 I3 |

### 5.5 Questions for Frank (revision 2's Q6-Q9, updated by the r3 panel; discussion: problem, forces, leaning)

The r3 panel read all four as sound and attached a note to each. The notes are folded in
below. None is ruled.

**Q6. What does `+1` do when the set has no `θ_hot`: decline to the `0` layout, or refuse?**
*Problem:* no set carries `θ_hot`'s inputs today, and none will until a quiet-box run measures
`C_part` per rank. So every `+1` compile meets a missing value. Using a presumed value would
be a silent default. *Forces:* a refusal makes the gap loud but breaks every `--tune=speed`
build until a set lands, over a choice that cannot change an answer. A decline keeps the
build working and is visible only if someone reads the stamp. tuning.md §2.21¶3's rule ("a
value the artifact cannot honour is a selection outcome, never a refusal") covers the
nearest case. The panel added two things. First, the decline must give the `0` object
EXACTLY, which revision 2's table did not (r3 CE-1). Revision 3 moves it to the artifact
table, ahead of every part row (T1). Second, the `_WHY` token is a caller-observable name,
so it needs its spec hunk and a D94 reader grep when the cell goes live (r3 LK-7). Revision
3 lists both in E1′. The panel's CE-6 also created a second decline: a set can say `none`
(no rank material). *Leaning:* decline, with T1's `"threshold-unmeasured"` and T2's
`"no-material-rank"` kept distinct, because they mean different things to a reader: "nobody
measured" versus "measured, and nothing pays". Both are reachable only once `+1`'s cell is
live against a set that lacks the row or says `none`.

**Q7. Is a static edge rank enough to say what is hot, or should the analysis object refine it?**
*Problem:* rank reads the combinator: inside the loop, once, conditional, rare. A conditional
edge (R1) can be hot in practice. One example is the NOTEMPTY retry on a pattern whose matches
are mostly empty. The exemplar bundle (D162) could measure how often such an edge fires.
*Forces:* a static rank is free and needs no profile. As the panel added, it also gives the
same layout for the same pattern on every box with the same set, which fits the amended
D166 tuple: only `θ_hot` moves, and it moves with the set. An exemplar-refined rank would
make the layout depend on the analysis object as well, which an artifact already depends on
(D166's (pattern, options, analysis, measurements)). But it adds a reader to that object for
a few-percent effect. The recount (§3.2) also weakens the case today: no R1 part is movable
(split's F is not copyable, and the retry is not a part). *Leaning:* static rank now. Keep
the exemplar refinement as U9, triggered by a bench cell traced to an R1 part that `+1` left
shared. That needs an R1 part that is a subject first.

**Q8. At `+1`, are the parts below `θ_hot` left at their `0` layout, or shared?**
*Problem:* revision 1 said cold parts "stay shared". Revisions 2 and 3 give them the `0`
layout (row P8), so `+1` never shares something `0` would have inlined. *Forces:* the
`0` layout keeps `+1` a pure speed-leaning step from `0`. The cost is that `+1`'s cold
parts still flip with `-fPIC` (F-2), as they do at `0`. Sharing them makes `+1`'s whole
layout pcrec's own, with no flip, but can make `+1` slower than `0` on a cold part gcc
would have inlined. The panel found where revision 2 inverted this. Revision 2 defined "as
at `0`" as "no attribute", so `__find` at `+1` with `θ_hot` = R3 would lose §2.2's
`always_inline` and be slower than `0` (r3 Q8 note, F3). Revision 3 defines the `0` layout
as the owner's (I4), so `__find` keeps §2.2's attribute and the tension is gone.
*Leaning:* the `0` layout, as P8 states. Revisit only if a bench cell shows the `-fPIC` flip
costing something at `+1`, which is the same trigger Q2 keeps for `0`.

**Q9. A position that differs from its neighbour on no corpus artifact: report it, or reshape the policy?**
*Problem:* §3.2.1 now shows how thin the populations are. `0`/`+1` is declared-coincident
until a set carries `θ_hot`. `−2`/`−1` has no witness: it needs an R3 subject, which means a
prefilter re-entered by the retry. `−1`/`0` has none until I1 (`__find`) or I3 (the DFA
wrappers). *Forces:* reshaping a policy until each pair has a corpus population ties the
dial's meaning to today's corpus. Keeping it means a caller's pattern with that class gets
the promised layout even though no corpus case exercises it. D103 already accepted a
declared-vacuous `+2`. The panel's note: a synthetic witness that is also the check's
control proves nothing (r3 CE-7, K35). Revision 3 gives each synthetic witness a hand-written
expected layout and reads the result from the object. *Leaning:* keep the policies as
defined. E1's census reports each row's population per position with a K35 floor. A pair or
row with zero population is listed with its reason, and a synthetic witness with a
hand-written expected `nm` set carries the check, so no row ships with a check that cannot
fail. This leaning matters more now than in revision 2: with populations this thin, the
practical first cell is likely `+2` on the `(a)b`-class hybrids (a copyable two-caller
prefilter that gcc keeps out of line), not the iterator.

---

## 6. Findings (for the manager)

- **F-1. B4's controller makes interposable calls.** `emit_compound.c:129` calls
  `<p>_next_pos`, and under `-futf-check` P's prologue calls `<p>_valid_upto`, both exported. Under `-fPIC`
  they are PLT calls on every compound search (`results/entries.tsv`, the `O2-fPIC` rows of
  `compound-split` and `compound-split-utf`). Not an answer defect. The iterator's static
  twin (`__adv`) is the fix's shape.
- **F-2. gcc's entry layout flips with `-fPIC`** (§1.3): `_match_in` is a 110-142 B copy
  without `-fPIC` and a 9 B tail jump with it; the function bytes fall 1.5-20% under `-fPIC`
  on eight of nine witnesses and rise 6.7% on the vars one.
  The bench builds shared objects (D88 item 3's `.so` unit), so the bench measures the
  `-fPIC` layout and the in-tree drivers the other.
- **F-3. gcc partially inlines `_valid_upto`** into a `.part.0` clone under `-futf-check`
  (`compound-split-utf`, `-O2`): K24's shape on a residual that has no `noclone`. Harmless
  as measured; listed because K24 was a measured throughput cost on `_search`.
- **F-4. On split, H1 leaves the dial nothing to decide**: F cannot be copied and Q has one
  caller. Any claim that the dial speeds up the built compound is false today.
- **F-5. "Shared" is not automatically smaller** (§2.4): on a small VM artifact the one-body
  `plain` rung is larger and slower than `inline`, because each entry carries its own frame
  and canary. A size end must be chosen by size, as the existing VM term does.
- **F-6. The NOTEMPTY retry is split's combinator** (§4.2): `first-nonzero(R@q,
  SEARCH@next_pos(q))`. The iterator and the compound share their one combinator emitter.
