# Every exported entry as a compound controller over shared PARTS, and the dial deciding what is inline (ASSESSMENT / DESIGN NOTE, revision 2)

Status: PROPOSED, assessment and design only, nothing built. **Revision 2** (lane `cmprev`,
2026-10-16, from main `7ee8d7ae7`, abi 78) applies Frank's rulings on revision 1's Q1-Q5
(D163 addendum 7): read §R2 first. Revision 1: lane `cmpentry`, 2026-10-14, from main
`d6e7fa993`, abi 78. Charter: Frank, 2026-10-14: "we have compound artifacts. are
these pieces better composed in compound functions from parts? we issue several function
interfaces, would these parts compose into the individual compound functions?" and "we have
the dial controller. if we set it all up as compounds, the dial could decide whats inline".
The model assessed is the manager's framing, Frank-endorsed: every exported entry is a
compound controller (D163, `compound.md`) over a small set of shared parts, and the
INLINE-vs-SHARED layout of those parts is a row of the dial's pinned table ([OPT-DIAL], D103).

Evidence is compile-only plus clockless instruction counts: gcc 15.2 `-O2` on the Linux dev
box (Zen 4), `.text` and per-function sizes from `nm`/`size`, call edges from `objdump -dr`,
and dynamic instruction counts (Ir) from `valgrind --tool=callgrind`. No clock was read. The
probes and their outputs are in `compound_entries/` (own CLAUDE.md).

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
   (`entries.c:157`).
4. **The per-call cost of a shared part is small, and so is the byte saving (§2.2).** A
   static part call costs 5-29 instructions per call over the inlined form (callgrind; split's
   Q about 5, the VM hybrid's prefilter about 25-29). Sharing a multi-caller part saves 0-160 B
   of `.text` (0-5%); inlining every copyable part costs +4% to +21% of `.text` and saves
   2-13% of instructions. An exported sibling call through the PLT costs about 4.8
   instructions per call more than the same call bound locally, in lost optimization as well
   as the stub (§2.3).
5. **The dial row (§3), revised for D163 addendum 7.** The VM entry chain
   (`--vm-entry-shape`, tuning.md §2.21) ALREADY IS this row for one family, with a size
   term the dial moves. ONE `part-layout` row generalizes it over the sibling family (§3.1:
   eight members today), with five DISTINCT pinned policies (§3.2): `−2` `all-shared`
   (one out-of-line body per multi-caller part, wrappers forward to it); `−1`
   `shared-but-inner` (as `−2`, except a part called from inside a per-candidate loop is
   inlined); `0` `as-emitted` (no attribute, byte-identical to no flag); `+1` `hot-inline`
   (a part whose hottest edge ranks at or above the threshold `θ_hot` is inlined, the rest
   shared; `θ_hot` is the one value read from the measurement set, and absent from the set
   the position DECLINES to `as-emitted` with a stamped reason); `+2` `all-inline` (every
   copyable part inlined). Hotness is the combinator's EDGE RANK (per-candidate / per-call /
   conditional / rare), read off `entry_rows[]`, with no profile. The decision is one
   declared first-match table (§3.4) whose constraint rows (label table, computed goto, a
   single caller, the encoding seam) come before any position row. Each non-zero position's
   CELL stays `†` until its own ruled diff with a size AND time measurement (D103 item 3);
   the policies define what that diff would switch on.
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
   recommendation is E0 now (before I1), the layout row's mechanism at all-em-dash cells, and
   cells only when a measurement asks for one.

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
| **H4 `info` and `main` are not static** | — | `entries.c:157-160` refuses the request | every artifact |

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

## 3. The dial row

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
- **I4. The `0` layout is the owning design's layout** [r3 F3, CE-11]. At `0` every function
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

### 3.2 The five positions: five pinned policies

A position's POLICY is pinned (D103, Q1): it is the definition of what the position does,
fixed in tuning.md §5.4's row, and it changes only by a ruled diff. Whether the position's
CELL is live (moves bytes) is a separate fact: every non-zero cell stays `†` until its own
ruled diff cites a size AND a time measurement (D103 item 3). The policies below are what
those diffs switch on.

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

**The five policies:**

| position | policy token | layout of a subject part with two or more callers | what decides it | cell today |
|---|---|---|---|---|
| −2 `min-size` | `all-shared` | one `static noinline noclone` body; each wrapper that calls it is a tail-forward where `forwardable` holds, and keeps its adaptation and a call where it does not (§3.4 W-table) | caller count | `†` |
| −1 `size` | `shared-but-inner` | as `−2`, except a part of rank R3 is `always_inline` into each caller | caller count, rank = R3 | `†` |
| 0 `balanced` | `as-emitted` | the owning design's layout (I4); byte-identical to no flag | nothing (D103's no-op cell) | live (the default) |
| +1 `speed` | `hot-inline` | a copyable part of rank ≥ `θ_hot` is `always_inline`; every other part keeps its `0` layout. With `θ_hot` absent from the active set, or `none`, the WHOLE ARTIFACT takes the `0` layout, stamped (§3.3, rows T1/T2) | rank, `θ_hot` from the set | `†` |
| +2 `max-speed` | `all-inline` | every copyable part `always_inline` into every caller | copyability | `†` |

A subject part with ONE caller keeps its `0` layout at every position (§3.4 row P3): it is
never shared, and no position adds an attribute to it [r3 CE-1]. `+1` never shares a part
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

### 3.3 `θ_hot`: the one value a position reads from the measurement set

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
- **When the set has no `θ_hot`**, `+1` does not presume one (no silent defaults). Artifact
  row T1 (§3.4) gives the whole artifact the `0` layout and stamps
  `<PREFIX>_PART_LAYOUT_WHY "threshold-unmeasured"`. This is TODAY's state: no set carries the
  inputs. The only measurement is revision 1's callgrind Ir on Zen 4 (5-29 Ir per call,
  §2.2), which is an instruction count, not a cost in set units, and is LABELLED UNMEASURED
  for the set. Both stamps are reachable only once `+1`'s cell is live (§3.4.1).
- **What moves when the set changes.** Only `+1` artifacts, through `θ_hot`. `−2`, `−1`, `0`
  and `+2` read nothing from the set. A default-set change carries its mover census (D166
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

**The artifact table, evaluated once per artifact before any part** [r3 CE-1, CE-12, F3].

| # | row | conjuncts (all hold) | effect | stamp |
|---|---|---|---|---|
| T0 | `as-emitted` | position = 0, or the position's cell is `†` | every function keeps its `0` layout (I4); the part table is not consulted | none |
| T1 | `speed-unmeasured` | position = +1; the active set has no `θ_hot` | as A0 | `_WHY "threshold-unmeasured"` |
| T2 | `speed-none` | position = +1; `θ_hot` = `none` | as A0 | `_WHY "no-material-rank"`, `_THETA "none"` |
| T3 | `per-part` | (otherwise) | consult the part table for each part | `_THETA` at `+1` |

T0 makes `0`, and every position whose cell is still `†`, byte-identical by construction:
nothing below it runs. Because T1 and T2 sit above the part table, a `+1` decline gives the
`0` object exactly. In revision 2 it did not: L1-L4 ran first and L4 added `always_inline`.

**The part table, evaluated per subject part at a live non-zero position.** Constraint rows
P1-P3 come before every position row, so no position overrides them (Q2). Each position ends
in an unconditional row, so the table is total.

| # | row | conjuncts (all hold) | layout written | evidence |
|---|---|---|---|---|
| P1 | `owned` | the function is in the OWNED class (§3.1): A1's helpers and matcher (its rung's attribute), A2's `_deep` (`noinline`, load-bearing), A4's seam (`static inline`) | its owner's attribute, unchanged | [r3 CE-1, CE-2, LK-6]; [OPT-1]; [LOSS-REVIEW] candidate 1 |
| P2 | `not-copyable` | `copyable(part)` is false | `static noinline noclone`, one body | gcc errors (§2.1 H1, H2); [r3 LK-4, LK-3] |
| P3 | `single-caller` | `callers(part)` = 1 | its `0` layout (no attribute added) | H3: sharing measured +112 B for nothing; [r3 CE-1] |
| P4 | `min-size` | position = −2 | `static noinline noclone`; wrappers by the W-table | §3.2 |
| P5 | `size-inner` | position = −1; rank = R3 | `always_inline` | §3.2 |
| P6 | `size` | position = −1 | `static noinline noclone`; wrappers by the W-table | §3.2 |
| P7 | `speed-hot` | position = +1; rank ≥ `θ_hot` | `always_inline` | §3.3 |
| P8 | `speed` | position = +1 | its `0` layout | §3.2; Q8 |
| P9 | `max-speed` | position = +2 | `always_inline` | §3.2 |

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
  position may override it. A1's attributes are the `--vm-entry-shape` row's: until the
  ruled diff that migrates A1 under this row, the two dial rows are CO-RESIDENT on a VM
  artifact with DISJOINT subjects [r3 CE-2, F7]. P1 excludes A1's functions from every
  position row, so the two rows never write the same function. That disjointness is
  checked (§3.6), and without it the `−2` row would write `static noinline` on a matcher
  the `inline` rung marks `always_inline`.
- **The seam inside P1** [r3 LK-6]. A seam body is a small loop with no label table and no
  computed goto, so `{seam} ∩ {not copyable}` is empty. A fixture asserts it, because P1's
  owner attribute (`static inline`) on a non-copyable body would be a build error.
- **P2 adds `noclone`** [r3 LK-3]. `noinline` does not stop ipa-cp (`.constprop`), ipa-sra
  (`.isra`) or partial-inlining (`.part.N`) clones; K24 found `noclone` on the callee was
  the only cure. P2, P4 and P6 write it under `__has_attribute`, A3's spelling. The linkage
  critic's three-caller test did not clone, so the observable is carried by a check that
  counts clone symbols per part, not by an argument (§3.6).
- **Every row writes only on a STATIC function** [r3 LK-9]. gcc rejects `always_inline` on
  an exported callee under `-fPIC` ("function body can be overwritten at link time").
  Exported entries are never parts (§3.1), and I3 gives every multi-entry body a static twin
  before a cell lays it out. A negative test (§3.6) plants `always_inline` on an exported
  callee and expects the `-fPIC` build to fail.

**The wrapper table, at `−2` and `−1` only** [r3 LK-2]: for each wrapper that calls a body
P4 or P6 shared.

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

#### 3.4.1 What a caller can observe, per position

| observable | −2 | −1 | 0 | +1 | +2 |
|---|---|---|---|---|---|
| answers, captures, give-up codes | identical | identical | identical | identical | identical |
| refusal set, every stamped selection | identical (I5) | identical | identical | identical | identical |
| `RX_TUNE` | `"min-size"` | `"size"` | `"balanced"` | `"speed"` | `"max-speed"` |
| `<PREFIX>_PART_LAYOUT_WHY` (proposed) | absent | absent | absent | `"threshold-unmeasured"` (T1) or `"no-material-rank"` (T2); absent on T3 | absent |
| `<PREFIX>_PART_LAYOUT_THETA` (proposed) | absent | absent | absent | the `θ_hot` used (`"R3"`, `"R2"`, `"R1"`, `"none"`); absent on T1 | absent |
| object symbols (`nm`) | one local symbol per shared subject part; owned symbols as at `0` | the same, R3 subject parts absent | the owners' choices (A1 and A2 already decide some symbols) and gcc's | subject parts of rank ≥ `θ_hot` absent | copyable subject parts absent |
| layout flips with `-fPIC` (F-2) | no, for subject parts | no, for subject parts | yes, as today | no, for parts it inlines; the rest as at `0` | no, for subject parts |
| time | the cell's cited cost (Q3: not gated) | the cell's cited cost | the default | gated at parity (Q3) | gated at parity |

The "no flip" rows hold only for parts with no exported-sibling edge, which I3 guarantees
before a cell is live [r3 LK-5]. Without I3 a hot part that calls `<p>_next_pos` or
`<p>_valid_upto` (F-1) still pays the PLT under `-fPIC`.

**The stamps state only what the position does not** [r3 LK-7, CE-12]. `RX_TUNE` already
names the position, and the policy is a pure function of the position apart from `θ_hot` and
the decline. So revision 2's `<PREFIX>_PART_LAYOUT` (the policy token) is dropped. Only the
decline reason and the `θ_hot` used are stamped, and only by `+1`. Both appear with `+1`'s
first live cell, in that cell's abi event:
- the D80 spec hunks (tuning.md §5.3 for the stamp, §5.4 for the row, `match_api.md`
  §6.3.11's stamp list);
- the D94 reader grep (`stamp_kinds.c`, `memfn_stamps.c`, the registry's stamp tests);
- `make test-codegen` and the registry suites, per the root CLAUDE.md abi row.

There is no `rx_info` mirror (tuning.md §5.3¶2: nothing at run time behaves differently).

### 3.5 Interaction with the iterator's parity gate and the mode M

- **The parity gate** (D165 item 5, `findall_iter.md` §5.3): `next` at parity or better than
  today's `_search` loop on dense tiny matches. **RULED (Q3):** the gate binds positions
  `0`, `+1` and `+2`; at `−1`/`−2` the gap is that cell's cited time cost, reported, not
  gated. `__find` is rank R2 (one call per `_search` or `_next`), so `−1` shares it like
  `−2` does. Only the internal batch fill (R3, HELD) would separate them on an iterator
  artifact [r3 F4]. `+1` inlines `__find` when `θ_hot` ≤ R2. Otherwise (`θ_hot` = R3, or
  T1/T2's decline) `__find` keeps its `0` layout, which is §2.2's design of record, so `+1`
  is never slower than `0` on it [r3 F3, Q8 note].
- **M folds only where the locate part is inlined.** `findall_iter.md` §4.2 makes the call
  mode M a parameter of `__find`: a compile-time constant in each entry when inlined, one
  runtime branch per call when shared. So the layout row also decides whether the kit's
  dispatch on M (regime_tables.md R1-R3) costs a branch: it costs one at `−2`/`−1`, at P2
  (the attempt route's label-table body, shared at every position), and wherever `__find`
  is shared at `0` by §2.2. The size positions pay that branch knowingly, as part of their
  cited cost.
- **The kit's helpers (A7) are the kit's** (D157: pcrec sends facts, not methods).
  pcrec can tell the kit the dial position as a fact (it already does for the class kit,
  D131); how the kit lays out its helpers is its choice. A request, not a pcrec cell.

### 3.6 Checks (each with its independent control)

- **`0` is byte-identical** [r3 CE-10]: `scripts/emit_sweep.py` against pre-E1 main, every
  stream. That is the only control cited. `run_tune_dial.sh` section 1 checks one pattern
  and both sides go through the same `tune.c` resolver, so it is not an independent control.
- **A non-zero cell's layout is read from the OBJECT and judged against an expected set
  that shares no code with the table** [r3 CE-7, CE-8]. A separate evaluator, a script under
  `tests/` that links nothing from `src/`, computes the expected layout per artifact from
  three inputs:
  - the call graph of a COPY of the emitted C with every `always_inline`, `noinline` and
    `noclone` deleted by text, compiled `-O2 -fno-inline` and read from `objdump -dr`
    relocations. It is needed because under `-fno-inline` an `always_inline` function is
    still inlined and shows no edge; the stripping happens in the checker, so the emitter
    and its bytes do not move;
  - the owners' attributes, read from the ORIGINAL emitted text, to fold owned
    `always_inline` functions into their callers (the `callers` definition, §3.2);
  - the hand-written rank fixture, and the position's policy text from tuning.md §5.4.

  `nm` on the real object must show each shared subject part as one local symbol and each
  inlined one absent. The compiler is the judge of what was inlined; the evaluator is the
  judge of what should have been.
- **The rank fixture is a precondition of E1** [r3 LK-1]. It is hand-written from the emitted
  C, names one witness artifact per rank, and lands with E0's rank column. A rank with no
  witness (R3 and R1 today, §3.2) is reported UNWITNESSED, never passed. The census reports
  `callers` as distinct functions, never call sites.
- **Synthetic witnesses carry a hand-written expected layout** [r3 CE-7, Q9 note]. Where a
  row has no corpus population, a synthetic artifact exercises it. Its expected `nm` set is
  written by hand in the fixture, and the result is read from the object. The synthetic
  witness is never also the control.
- **H1/H2 and LK-9 by construction**: a planted `always_inline` on an attempt body must fail
  the build, and so must one on an exported callee under `-fPIC`. The gcc error is the
  detector.
- **Clones** [r3 LK-3]: per artifact and position, count `.constprop`, `.isra` and `.part.N`
  symbols derived from each shared part's name; any is a failure.
- **A1 and the layout row are disjoint** [r3 CE-2]: per VM artifact and position, the set
  of functions P1 assigns to A1 and the set any position row writes are disjoint, checked on
  the emitted text.
- **The seam is copyable** [r3 LK-6]: the fixture of §3.4.
- **Stamp neutrality** [r3 CE-9]. `make test-axes` compares answers and refused-key sets
  (DIAL-S3), not stamps. The new arm diffs every `#define <PREFIX>_*` except
  `<PREFIX>_TUNE` and `<PREFIX>_PART_LAYOUT_*` between a position's artifact and the SAME
  position's artifact built from the cell diff's parent (where the layout cell is `†`). The
  parent is the control because other dial rows (A1's term, λ, the ladder) legitimately move
  stamps between positions. While every cell is `†` the arm compares an artifact with
  itself, so it is reported UNREACHED until the first live cell.
- **Length neutrality on every emitter** [r3 LK-8]: the near-cap witnesses (the lowered-cap
  manifests of `r17c_nearcap.py`, the K59 and `[ART-SIZE]` witnesses) refuse and select
  identically at every position on the VM, DFA and compound emitters. This tests I5.
- **The decline is visible**: a `+1` compile against a set without `θ_hot` carries
  `_WHY "threshold-unmeasured"`, and its object equals `0`'s.
- **The attribute census**: every `__attribute__((always_inline|noinline|noclone))` and every
  `static inline` in an emitted artifact belongs to a row of §3.4 or a class of §3.1. An
  unlisted writer fails. This is the "single attribute-writing table" unlock's check, built
  at E1 even though the writers themselves stay where they are (§5.3).
- **Totality and population, per row** [r3 CE-4]: every (subject part, position) in the
  census reaches exactly one row, and each row's population is counted per position (K35).
  A row whose population is zero is listed with its reason.

**Sabotage, PROPOSED ids** (S983 is the next free id; the manager allocates):

| proposed id | plant | detector |
|---|---|---|
| S983 | P1 drops `_deep` (A2) | the object check: `_deep` must stay a local symbol at every position |
| S984 | P1 drops A1's functions | the A1-disjointness check; the `-Werror` harness compile (gcc's conflicting-attribute warning) |
| S985 | T1/T2 moved below the part table | emit_sweep: `+1` without `θ_hot` must equal `0` byte for byte |
| S986 | P2 dropped | the build: gcc refuses `always_inline` on a label-table body at `+2` |
| S987 | `noclone` dropped from P2/P4/P6 | the clone-symbol count |
| S988 | `forwardable` always true | the build and answer checks on the compound `_match` at `−2` |
| S989 | `callers` counts call sites | the evaluator's expected set against `nm` on a two-site, one-function part |
| S990 | `θ_hot = none` read as R3 | the `none` witness: `+1`'s object must equal `0`'s and carry `_THETA "none"` |
| S991 | the layout pass rendered before the size caps | the near-cap refusal arm |
| S992 | the rank column's R3 cell read as R2 | the rank fixture |

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
(`entries.c:58-107`). The proposal adds the controller as a column, so the edges are DERIVED:

```c
typedef struct {
    PcrecEntry entry;            /* the exported (or kept) entry this row defines   */
    bool (*when)(const PcrecEntryShape *s);   /* the shape this row serves        */
    CompComb comb;               /* locate-then-finish, finish-at, forward,          */
                                 /* first-nonzero, select-by-arg, dispatch, iterate  */
    const PartRef *parts; int nparts;   /* the static parts / in-Job rows it calls */
    CallMode mode;               /* ONESHOT, ITER: a constant per entry (§3.5)       */
} EntryRow;
```

- **The edges are the rows' part references**, so the closure reads what the controller
  calls. `entries.c` missed the `rev-end` tie's `search -> match` edge in B0 and the check
  found it (cpb02 finding 1); a derived list cannot drift from the emitter that uses it.
- **Each combinator has ONE emitter** (`emit_compound.c` has the first, `first-nonzero`).
  `forward` is today's `emit_in_entry_defs` and the VM's forwards; `finish-at` is axis G's
  dispatch; `locate-then-finish` is the body. Moving them under the table is a re-spelling,
  byte-identical (§5.1 E0c).
- **The layout row (§3) is applied once, by the table**, to every part reachable from more
  than one entry.
- **It is D88 addendum 1 stated as data**: one exported call interface per file is the set of
  EXPORTED rows, and everything else is KEPT STATIC or OMITTED by the closure.

### 4.2 What the iterator design would change to be expressed as a controller

| iterator piece (`findall_iter.md`) | as a row of the table |
|---|---|
| `__find(…, M)`, one body, two entries (§2.1) | the search controller's body as a part, called by `_search` (M = ONESHOT) and `_next` (M = ITER) |
| §2.2's two-row rule (`shared` for a label table, else `inline`) | the layout table's L0 at `0` plus L1 elsewhere (§3.4, §3.8): the same answer, no separate table |
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
| **E0a** | `entry_rows[]` beside today's emitters; the derived edge set held against `entries.c`'s hand list for every corpus artifact (the trace-build both-walks oracle shape, `stc2`) | ZERO | none |
| **E0b** | the closure reads the derived edges; the hand list deleted | ZERO | none |
| **E0c** | each emitter's entries written through the row's combinator emitter | ZERO (emit_sweep, every stream) | none |
| **E1** | the layout row: §3.4's table L0-L11 as a declared first-match table, read by `entry_rows[]`, every non-zero cell `†` (so every position emits as `0`); the rank fixture and caller-count check (§3.6) | ZERO | none |
| **E1′** | each cell, by its own ruled diff with its size and time measurement; the first one adds `<PREFIX>_PART_LAYOUT` (§3.4.1) and applies I3 to the DFA wrappers | that position's artifacts | one per cell diff (bytes move at that position) |
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
   object against tuning.md §5.4's text. H1/H2 are gcc's own errors. Population: the 233
   label-table artifacts (`findall_iter.md`'s census), the 97 admitted compounds
   (`admitted.tsv`), VM framed/frameless from the size log; a K35 floor per part class at E1.
3. **What moves when regenerated — RELEVANT.** E0 and E1 move nothing (emit_sweep). A cell
   diff moves that position's artifacts and is an abi event with D94's reader grep. Q1 ruled
   `θ_hot` into the measurement set: once `+1` is live, a set change moves `+1` artifacts
   only (no other position reads the set), with D166's mover census in the same commit.

### 5.3 Unlocks (each with its trigger)

| # | unlock | trigger |
|---|---|---|
| U1 | the layout row's non-zero cells (their policies are fixed by §3.2; each lifts from `†` by its own diff) | a measured short-call cell where `C_part` is material (the parity gate's `I_shared` arm, or a bench cell traced to a shared part); `+1` additionally needs `θ_hot`'s inputs in a set |
| U2 | `rx_entries` (one struct of entry pointers, [V-E] item 1, [ART-MGR] S1): the EXPORTED rows are its fields | [IFACE-PUSH] |
| U3 | the public [EMIT-ENTRIES] request (a caller names the entry set): the rows already carry it | [IFACE-PUSH] |
| U4 | one-attempt `_match` on every attempt route (`compound.md` A-U1): a `finish-at` row swap | `locate_finish.md` Q7's measurement |
| U5 | captures on demand as a `select-by-arg` row | B7's trigger (`compound.md` §D.1) |
| U6 | artifact-grain arch dispatch | D144 add. 4: a SIMD form that must ship beside its scalar form |
| U7 | shared tables between parts (`compound.md` U6) | a compound pushed to `drop-compound` by size |
| U8 | the dial position passed to the kit as a fact for its helper layout | a kit request; the class kit's D131 is the precedent |
| U9 | an exemplar-refined edge rank (the analysis object says how often a conditional edge fires) | a bench cell traced to an R1 part that `+1` left out of line (Q7) |
| U10 | an explicit override spelling for the row (a `--part-layout=` value, `--vm-entry-shape`'s precedent) | [IFACE-PUSH] (§3.7) |

### 5.4 Revision 1's questions: RULED (D163 addendum 7)

| Q | ruling | applied in |
|---|---|---|
| Q1 pinned cell or measured selection | the POLICY is a pinned cell per position (D103); only `hot-inline`'s threshold comes from the set (D166), with its mover census; a D103 clarification | §3.2, §3.3 |
| Q2 `balanced` | stays as emitted; FIVE distinct positions; hard constraints are rows no position overrides | §3.2, §3.2.1, §3.4 |
| Q3 parity gate | binds `0`, `+1`, `+2`; at `−1`/`−2` the gap is the cell's cost | §3.5 |
| Q4 E0 before I1 | yes; then the short `findall_iter.md` revision, its panel, then I1 | §5.1, §3.8 |
| Q5 exported-to-exported calls | never; static twins; applied where a change already moves the bytes | §3.0 I3 |

### 5.5 Questions for Frank from this revision (discussion: problem, forces, leaning)

**Q6. What does `+1` do when the set has no `θ_hot`: decline to the `0` layout, or refuse?**
*Problem:* no set carries `θ_hot`'s inputs today, and none will until a quiet-box run measures
`C_part` per rank. So every `+1` compile meets a missing value. Using a presumed value would
be a silent default. *Forces:* a refusal makes the gap loud but breaks every `--tune=speed`
build until a set lands, over a choice that cannot change an answer. A decline keeps the
build working and is visible only if someone reads the stamp. tuning.md §2.21¶3's rule ("a
value the artifact cannot honour is a selection outcome, never a refusal") covers the
nearest case. *Leaning:* decline (L8), with the `_WHY` stamp, and the listing showing the
missing row as the reason. The cell is `†` anyway until its diff, so the decline is only
reachable once `+1` is live against a set that lacks the row (a rolled-back or user set).

**Q7. Is a static edge rank enough to say what is hot, or should the analysis object refine it?**
*Problem:* rank reads the combinator: inside the loop, once, conditional, rare. A conditional
edge (R1) can be hot in practice. One example is the NOTEMPTY retry on a pattern whose matches
are mostly empty. The exemplar bundle (D162) could measure how often such an edge fires.
*Forces:* a static rank is free, needs no profile and gives the same layout for the same
pattern on every box. Only `θ_hot` moves, and it moves with the set. An exemplar-refined rank
would make the layout depend on the analysis object as well, which an artifact already
depends on (D166's (pattern, options, analysis, measurements)). But it adds a reader to that
object for a few-percent effect. *Leaning:* static rank now. File the exemplar refinement as
an unlock (U9 below), triggered by a bench cell traced to an R1 part that `+1` left shared.

**Q8. At `+1`, are the parts below `θ_hot` left to gcc, or shared?**
*Problem:* revision 1 said cold parts "stay shared". This revision leaves them as at `0`
(no attribute), so `+1` never shares something `0` would have inlined. *Forces:* leaving
them to gcc keeps `+1` a pure speed-leaning step from `0`. The cost is that `+1`'s cold
parts still flip with `-fPIC` (F-2), as they do at `0`. Sharing them makes `+1`'s whole
layout pcrec's own, with no flip, but can make `+1` slower than `0` on a cold part gcc
would have inlined. That inverts the dial on that part. *Leaning:* leave them to gcc, as
§3.2 and row L10 state. Revisit only if a bench cell shows the `-fPIC` flip costing
something at `+1`, which is the same trigger Q2 keeps for `0`.

**Q9. A position that differs from its neighbour on no corpus artifact: report it, or reshape the policy?**
*Problem:* §3.2.1 shows each adjacent pair disagrees on a named part class, but the corpus
may not carry every class. For example, `−2`/`−1` differ only on a multi-caller R3 part.
*Forces:* reshaping a policy until each pair has a corpus population ties the dial's
meaning to today's corpus. Keeping it means a caller's pattern with that class gets the
promised layout even though no corpus case exercises it. D103 already accepted a
declared-vacuous `+2`. *Leaning:* keep the policies as defined. E1's census reports each
pair's population with a K35 floor. A pair with zero population is listed with its reason,
and a synthetic witness per part class carries the check (§3.6) so no row ships UNREACHED.

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
