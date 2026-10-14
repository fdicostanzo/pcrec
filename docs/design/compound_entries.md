# Every exported entry as a compound controller over shared PARTS, and the dial deciding what is inline (ASSESSMENT / DESIGN NOTE, revision 1)

Status: PROPOSED, assessment and design only, nothing built (lane `cmpentry`, 2026-10-14,
from main `d6e7fa993`, abi 78). Charter: Frank, 2026-10-14: "we have compound artifacts. are
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
5. **The dial row (§3).** The VM entry chain (`--vm-entry-shape`, tuning.md §2.21) ALREADY IS
   this row for one family, with a size term the dial moves. This note proposes ONE
   `part-layout` row that generalizes it over the sibling family (§3.1: eight members today).
   Proposed cells: position `0` = today's bytes exactly (no attribute; gcc decides), so the
   dial's no-op acceptance cell holds; `−2`/`−1` = `shared` (every multi-caller part
   `noinline`); `+1` = hot parts `always_inline`; `+2` = every copyable part `always_inline`.
   Every non-zero cell is `†` (an em-dash pending its time measurement) until the D166 set
   carries the two quantities it reads: the static-part call cost and the part's object
   bytes. Constraint rows the dial cannot override: H1-H5 (§3.3).
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
| VM hybrid `(a|ab)(c|bcd)(d*)` (framed, `plain`) | 3,033 / 2,859 | `match_anchored`, `search_run` | `_search`→`_search_in`, `_*_in`→sibling |
| VM forced `(a)b` | 1,443 / 1,421 | none | `_*_in`→sibling |
| VM vars `a${v}b` | 1,558 / 1,662 | none | `_search`→`_search_in` and the forwards |

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
not time; §3.4 says what the cells need beyond them.

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
through a STATIC part, never through an exported sibling (§3.3 H5).

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

### 3.1 The sibling family: eight places that decide inline or shared today

| # | member | where | decided by |
|---|---|---|---|
| 1 | the VM entry chain (`plain`/`shared`/`forward`/`inline`) | `emit_vm.c:10961-10998`; tuning.md §2.21 | a size term (4,096 / 8,192 at `+1`), the dial's existing row |
| 2 | the hybrid's embedded DFA search | `emit_vm.c:12773` | the closure (B0): static, gcc decides inlining |
| 3 | the encoding seam (`_span_match*`, `_back_step`) | `src/enc/enc.c:191` `inline_def` | fixed `static inline` ([LOSS-REVIEW] candidate 1) |
| 4 | the kit's FUNC helpers and D155 selector | `memfn/src/ofsskip.c` (`<fn>__body`, the selector) | the kit (`static inline`) |
| 5 | the iterator's `__find` | `findall_iter.md` §2.2's two-row table | static label table → `shared`, else `inline` (designed) |
| 6 | compound parts | `emit_compound.c:101` | gcc |
| 7 | the DFA `_in` and `_match_caps` wrappers | `emit_dfa.c:2727`, `:2788` | gcc, and the link regime (§1.3) |
| 8 | `noclone` on search heads | `pcrec_emit_search_head` (K24) | fixed: stop gcc's partial-inlining split |

Eight members is past the unification threshold (memory `pcrec-forest-for-trees`). The
general form is ONE row: a part's layout as a function of (its callers, its copyability, the
dial position), applied by the entry table at every place one body is reachable from more than
one entry. Members 1 and 5 are the only ones with a decision today; the rest are fixed or
gcc's.

### 3.2 The proposed row

A row of tuning.md §5.4, in its format (a value or an em-dash; `†` = pending a named
measurement):

| axis | −2 `min-size` | −1 `size` | 0 `balanced` | +1 `speed` | +2 `max-speed` | why |
|---|---|---|---|---|---|---|
| part layout | `shared` `†` | `shared` `†` | **as emitted** (no attribute; gcc decides) | `hot-inline` `†` | `inline` `†` | §3.1's eight members as one row; H1-H5 (§3.3) are not cells; `†` = the call cost and part bytes of §3.4 are not in a measurement set |

- **`as emitted` at `0`** keeps D103's no-op acceptance cell: `balanced` is byte-identical to
  no flag, so this row adds nothing at `0` by construction. gcc's default is in effect
  "single-caller inline, multi-caller shared, uncopyable shared", which is close to
  `hot-inline` without the hot test.
- **`shared`**: every part with two or more callers `noinline`; `_in` and `_match_caps`
  wrappers tail-jump to their sibling's static body. Measured on one framed VM: −5.2% `.text`
  at +3.9% Ir; on the frameless hybrid it is a no-op (gcc already shared).
- **`hot-inline`**: a part reached on every call (the controller's locate part, the advance,
  the retry R on a `reports_empty` artifact) `always_inline` into each caller; a part reached
  once per find-all or on a rare edge (split's F after the floor, a `rev-end` tie's
  `verify-at`, the reverse walk) stays shared. Hotness is read off the combinator's edge kind
  (per call / per match / per find-all / rare), so it needs no profile.
- **`inline`**: every copyable part `always_inline`. Measured: +4.4% to +21.2% `.text` for
  −2% to −13% Ir.
- **An explicit `--vm-entry-shape=N`** keeps overriding member 1, as today (tuning.md
  §2.21¶7). Member 1's own term becomes this row's term for VM bodies; its cells (4,096 at
  `0`, 8,192 at `+1`/`+2`) carry over unchanged.

### 3.3 Constraint rows: what the dial cannot override

| id | constraint | evidence | effect |
|---|---|---|---|
| H1 | a body with a static label table is never copied | gcc error (§2.1) | always `shared` at every position; findall_iter.md §2.2's `shared` row |
| H2 | a body with a computed goto is never inlined | gcc error (§2.1) | always `shared`; the VM chain's rungs 2-4 already fall back (tuning.md §2.21¶3) |
| H3 | a single-caller part is never `shared` | +112 B for nothing (§2.1) | the `shared` cell applies to parts with ≥ 2 callers only |
| H4 | `info` and `main` are not static | `entries.c:157` | unchanged |
| H5 | an entry never reaches a shared body through an exported sibling | 4.8 Ir/call through the PLT (§2.3) | the shared body is a STATIC part (the iterator's `__adv` shape); not a dial cell |
| H6 | the emitted-size caps and every length decision read the layout-neutral length | D84; [EMIT-VERB]/RQ-3's decision view (`pcrec_sb_len_decide`, `emit_vm.c:10963`) | attribute text is bracketed out of every size decision, so no position moves the refusal set or a selection (tuning.md §5.5's acceptance) |
| H7 | `noclone` stays on every search head | K24 | member 8 is not a cell |

H6 is what makes the row safe to add: the layout moves OBJECT bytes; the caps measure emitted
C bytes, and the few bytes of attribute text are excluded from every decision the same way
`-fmemfn-simd`'s guarded bytes are.

### 3.4 The measurement it needs (D166 set quantities)

The cells read two quantities per part class, which belong in the measurement set (D166):

| quantity | unit (D166 item 2: relative) | measured here | owed |
|---|---|---|---|
| `C_part`: one static part call over the inlined form | per call, in units of the scalar walk's per-byte cost | 5-29 Ir per call (callgrind, Zen 4) | ns per call, short-call regime, per box (a quiet slot) |
| `C_plt`: an exported-sibling call over a static part call | per call | ≈ 4.8 Ir per call (one witness) | ns per call, `.so` regime |
| `b_part`: the part's object bytes | bytes | the per-function sizes in `layout.tsv` | the corpus distribution by part class |

The proposal rubric (D103 item 2) for a cell: `inline` is argued where `C_part · calls per
byte` is material against the walk and the extra `.text` is `(k − 1) · b_part` against the
position's size budget. Each `†` lifts only by its own ruled diff citing a two-axis
measurement (size AND time), never when the measurement lands (D103 item 1).

**A tension to rule (Q1).** D103 pins dial cells; D166 lets measured selections move with the
set. This row can be either: a pinned POLICY per position (`hot-inline`), with the threshold
inside it read from the set; or a pinned cell with a pinned threshold. §6 Q1.

### 3.5 Interaction with the iterator's parity gate and the mode M

- **The parity gate** (D165 item 5, `findall_iter.md` §5.3): `next` at parity or better than
  today's `_search` loop on dense tiny matches. At `shared`, `next` calls a shared `__find`
  once per match (the gate's `I_shared` arm); the twin prices it at a smaller constant
  `.text` (+832-989 B instead of +997-2,587 B). The gate is stated against the DEFAULT
  build. The proposal: the gate binds positions `0`, `+1` and `+2`; at `−1`/`−2` the gap is
  that cell's cited time cost, reported, not gated (§6 Q3).
- **M folds only where the locate part is inlined.** `findall_iter.md` §4.2 makes the call
  mode M a parameter of `__find`: a compile-time constant in each entry when inlined, one
  runtime branch per call when shared. So the layout row also decides whether the kit's
  dispatch on M (regime_tables.md R1-R3) costs a branch. This is a second reason the
  locate part is `hot`.
- **The kit's helpers (member 4) are the kit's** (D157: pcrec sends facts, not methods).
  pcrec can tell the kit the dial position as a fact (it already does for the class kit,
  D131); how the kit lays out its helpers is its choice. A request, not a pcrec cell.

### 3.6 Checks (each with its independent control)

- **The `0` cell is byte-identical**: `scripts/emit_sweep.py` against main, every stream;
  `run_tune_dial.sh` section 1 already asserts `balanced` = no flag.
- **Each non-zero cell's layout is recovered from the OBJECT, not from pcrec**: `nm` must show
  each `shared` part as exactly one local symbol and each `inline` part absent; the expected
  set is read from tuning.md §5.4 (`run_tune_dial.sh`'s rule: never from `tune.c`). The
  compiler is the independent judge of what was inlined.
- **H1/H2 by construction**: a planted `always_inline` on an attempt body must fail the build
  (the gcc error is the detector).
- **H6 neutrality**: every position's refusal set and every stamped selection equal `0`'s
  over the corpus (`make test-axes` sweeps the dial already).

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
| §2.2's two-row rule (`shared` for a label table, else `inline`) | the layout row at `0` plus H1 (§3.2-§3.3): the same answer, no separate table |
| the NOTEMPTY retry (§3.3) | `first-nonzero(R@q, SEARCH@next_pos(q))`: split's combinator, with R = FINISH `verify-at` on the notempty root (an in-Job machine role, `compound_place` row 3) on the DFA, or the VM's guarded attempt |
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
| **E1** | the layout row: mechanism + H1-H7, every non-zero cell `†` (em-dash) | ZERO | none |
| **E1′** | each cell, by its own ruled diff with its measurement | that position's artifacts | one per cell diff (bytes move at that position) |
| I0 | `findall_iter.md` §6.9, unchanged | ZERO | none |
| I1 | `next` as an `iterate` row; the retry as `first-nonzero`; the STATE part | every artifact | ONE (as designed) |
| F-1 fix | the compound controller calls static twins of `_next_pos`/`_valid_upto` | compound artifacts (97 corpus, bench 0) | fold into I1, which adds `__adv` anyway |

Remodel overlap (memory `pcrec-remodel-first`): E0 touches the three entry emitters and
`entries.c`, exactly where I1 and B5-B8 work. It goes first or it is re-done.

### 5.2 The standing design questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — RELEVANT.** Every number is gcc 15.2 `-O2` on x86-64 (the Linux dev
   box). `.text` and function sizes are compile-only; instruction counts are callgrind Ir,
   deterministic, with no clock. Ir is not time: it ignores branch prediction, cache and the
   PLT's indirect jump cost, so a cell needs ns before it lifts (§3.4). Two regimes flip a
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
   diff moves that position's artifacts and is an abi event with D94's reader grep. If Q1
   rules the threshold into the measurement set, a set change moves selections at non-zero
   positions only, with D166's mover census.

### 5.3 Unlocks (each with its trigger)

| # | unlock | trigger |
|---|---|---|
| U1 | the layout row's non-zero cells | a measured short-call cell where `C_part` is material (the parity gate's `I_shared` arm, or a bench cell traced to a shared part) |
| U2 | `rx_entries` (one struct of entry pointers, [V-E] item 1, [ART-MGR] S1): the EXPORTED rows are its fields | [IFACE-PUSH] |
| U3 | the public [EMIT-ENTRIES] request (a caller names the entry set): the rows already carry it | [IFACE-PUSH] |
| U4 | one-attempt `_match` on every attempt route (`compound.md` A-U1): a `finish-at` row swap | `locate_finish.md` Q7's measurement |
| U5 | captures on demand as a `select-by-arg` row | B7's trigger (`compound.md` §D.1) |
| U6 | artifact-grain arch dispatch | D144 add. 4: a SIMD form that must ship beside its scalar form |
| U7 | shared tables between parts (`compound.md` U6) | a compound pushed to `drop-compound` by size |
| U8 | the dial position passed to the kit as a fact for its helper layout | a kit request; the class kit's D131 is the precedent |

### 5.4 Questions for Frank (discussion: problem, forces, leaning)

**Q1. Is "what is inline" a pinned dial cell (D103) or a measured selection (D166)?**
*Problem:* D103 pins dial cells (a cell never moves because a measurement lands); D166 says
decision measurements live in versioned sets and selections move when the set changes.
"Inline where the call cost is material against the part's bytes" is naturally the second.
*Forces:* a pinned cell is predictable across releases (D103's reason); a measured threshold
tracks hardware, which matters more here than elsewhere because call cost differs between Zen
4, Zen 1 and the M1. *Leaning:* pin the POLICY per position (`shared`, `hot-inline`,
`inline`) and let the one threshold inside `hot-inline` come from the set, with D166's mover
census. Positions `−2`, `−1`, `0` and `+2` read no threshold, so only `+1` moves with a set.
Recorded as a D103 clarification.

**Q2. Should `balanced` stay "as emitted", or become explicit `hot-inline`?**
*Problem:* the framing has `balanced` = hot parts inline. Today's `0` is gcc's choice,
which already comes close, and the dial's no-op cell requires `0` to be byte-identical to no
flag. *Forces:* explicit `hot-inline` at `0` makes the layout pcrec's decision in the default
build (it stops depending on `-fPIC`); it is an every-artifact mover and an abi event with no
measured gain. *Leaning:* keep `0` as emitted; put `hot-inline` at `+1`; revisit `0` if the
`-fPIC` layout flip shows up in a bench cell.

**Q3. Does the iterator's parity gate bind at the size positions?**
*Problem:* D165 item 5 says `next` must be at parity with today's loop on dense tiny matches;
at `shared`, `next` makes one internal call per match. *Forces:* the size end explicitly
trades speed for bytes, and a gate there would forbid the cell it is meant to price.
*Leaning:* the gate binds `0`, `+1`, `+2`; at `−1`/`−2` the measured gap is the cell's cited
cost.

**Q4. Should E0 (the entry table) land before the iterator's I1?**
*Problem:* the iterator panel was held for this lane. If I1 builds first, E0 later re-spells
I1's entries; if E0 builds first, I1 waits for a zero-mover refactor of three emitters.
*Forces:* remodel-first (D153) ranks in-flight refactors ahead; E0 is mechanical and gated by
emit_sweep; the iterator design needs only a short revision (§4.2's table) to be expressed as
rows. *Leaning:* E0 first, then a short revision of `findall_iter.md` (the retry as
`first-nonzero`, `__find`'s layout from the row), then its panel, then I1.

**Q5. Should an exported entry ever call an exported sibling?**
*Problem:* today four kinds do (`_match` → `_search` on `search-filter`, `_match_caps` →
`_match`, the `_in` forwards, the compound controller → `_next_pos`/`_valid_upto`). In a
shared object each is a PLT call. *Forces:* routing them through static twins costs a few
bytes of text per artifact and is an abi event wherever it moves bytes; the measured gain is
about 4.8 instructions per call on one witness. *Leaning:* adopt H5 as a rule, applied where
an event already moves those bytes (I1 for the residual twins, E1′ for the wrappers), never as
its own every-artifact event.

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
