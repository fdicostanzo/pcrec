# cover_cap.md — no length bound on the `cover` route's exact span ([COVER-CAP])

Status: PROPOSED, revision 1 (lane `covcap2`, 2026-11-15). DESIGN ONLY: no build go.
Plan row: [COVER-CAP] (set S3), from [EARNED-SKIP]'s measurement (lane skipmeas,
2026-11-11). Built on: `kit_proof.md` §1.1 (the `cover_conj[]` table), `ctx_span.md`
§11 N-1 (which foresaw the cap), `offset_k_skip.md` §3.3 (where the 24 came from).
Compiler read: main `1b75dba61` (`build/pcrec` of 2026-11-14 16:49; no `src/` or `memfn/`
change since).

**REVISION 1 (owner ruling, Frank 2026-11-15).** Rev 0 split the bound and gave the span
slice its own `PCREC_SPAN_EXACT_MAX = 32`. Frank's answer: "why any bound at all? why the
artificial constraint?" ... "agree. avoid arbitrary tuning constants like that." Both
numbers rev 0 worked with were borrowed. The 24 (`PCREC_PREFIX_K_MAX`) is the k-set
walk's compile budget. The 32 (`MF_MAX_SPAN_POS = MF_MAX_TERM`) is the kit's
term-array size, which comes from the VM's stride. Rev 1 removes the length bound. pcrec states as
long an exact span as the pattern's exact prefix proves. The span crosses the seam as a
counted list of any length. The one bound left on pcrec's side is the existing compile
budget, which is a sound under-statement and is labelled UNMEASURED (§3.3). Rev 0's text
is superseded in place. Its critic round is answered in §9.

## 0. Goals

Ranked; the higher goal wins a conflict.

1. **G1, answer identity (every caller).** No search, match or group answer moves on any
   corpus pattern, encoding or deny-flag arm. Form: `make test`, `make test-axes`
   (`--memfn=no-window-search` against default) and the new `test-kitproof` boundary
   rows (libpcre2 10.46 answers, §5.3), all green, 0 answer differences.
2. **G2, nothing else moves (every caller, reviewers).** Every artifact whose
   `<PREFIX>_DFA_SCAN` does not become `"cover"` is byte-identical, except for the `abi`
   stamp that the bump itself moves (§4.4). Form: `scripts/emit_sweep.py`
   main-before against the candidate. The movers it OBSERVES must EQUAL the list
   PREDICTED from the baseline (§5.2), in both directions.
3. **G3, no slower cell (bench users).** No mover cell is slower than before beyond the
   bench's A/A noise floor, in any regime or encoding. This includes the first-byte-fail
   subjects and the class movers whose text grows (§3.4). Form: the re-timing in §7, with
   before and after on the same box and bench pin. A loss here is NOT answered by a
   length cut-over, which would be a new hand-picked constant. It gets the one-pass rule
   (memory `pcrec-one-pass-loss-chasing`) and then an owner ruling.
4. **G4, no inherited length bound (maintainers, Frank's ruling).** After stage 2 (§3.5),
   every bound left on the cover path is either the problem's own limit or a compile
   budget with a stated derivation and a measurement plan. None is borrowed from another
   mechanism. Form: the §1 inventory has no pcrec-side row marked INHERITED. The census
   of §3.3 exists and says where the budget binds.
5. **G5, the long fixed shapes leave the engine (bench users with literals, hashes, ids
   and uuids of 25 or more positions).** `lit-l31`, `lit-l40`, `hex32`, `dig-exact-32`,
   `hex32-id`, `uuid` and `wild-validator-uuid-grok` match cells are faster beyond noise,
   in both encodings. EXPECTED size of the win (not the bar, and UNMEASURED): the
   24-position twin's cover/engine ratio, measured as one variable in §7's own before
   run. skipmeas's 30.0M → 4.4M is a stub's upper bound, not the cover's.
6. **G6, size reported (reviewers, users with size budgets).** Each mover's C bytes and
   `gcc -O2` `.text` are reported before and after. Any growth is listed with its slope
   per position. G6 holds if no mover grows, or if each growth is accepted by the owner
   (§8 Q2) once the kit has answered the size ask (§4.3 ask 2).

Non-goals: lookaround as a run ([REQ-LOOKAROUND], set S4); a trailing `$`/`\z` as a
length compare; captures inside a cover body (C1/C5 decline them, unchanged: the bench's
`wild-secrets-github-pat`, 93 positions, stays on the engine for that reason, because its
uncaptured twin covers); earned skip and [MATCH-KNOWN] (PARKED, Frank 2026-11-11); the
k-set walk's own 24 (§1.4: not on this path once the slice stops reading it).

## 1. The bounds on the cover path

Every bound met between "the pattern" and "the kit's text", found by reading the path
end to end (`pcrec_span_walk` → `cover_conj[]` → `cover_window` → the seam → the kit's
window family → the reply → `pcrec_cover_proof_diff`/`emit_cover`). The verdict column says what each bound is:
OWN means the problem's own limit, INHERITED means borrowed from another mechanism,
BUDGET means a compile budget, and SCRATCH means a size picked for storage. A bound
that is not binding is noted as such.

### 1.1 pcrec, the span slice (`src/facts/kset.c`, `src/facts/facts.h`)

| # | bound | site | verdict | rev 1 |
|---|---|---|---|---|
| P1 | the exact-prefix loop `d < PCREC_PREFIX_K_MAX` (24) | `kset.c:911` | INHERITED: the k-set walk's bound (`offset_k_skip.md` §3.3, chosen for the offset-k skip) | REMOVED: the loop runs until a depth is not exact, which always happens within the budget (§3.1) |
| P2 | the liveness horizon `depth >= 2 * PCREC_PREFIX_K_MAX` (48) | `kset.c:891`, comment `:578` | INHERITED and doubled. It is what makes a 49-byte literal list `span_facts 0` today (SOUND-1) | REMOVED: exploration stops only at the budget or when the subsets are exhausted |
| P3 | `MkLang.set[PCREC_PREFIX_K_MAX][32]`, `uint8_t exact_len` | `facts.h:305-306` | SCRATCH sized by P1. `uint8_t` caps the count at 255 | a COUNTED arena list (`exact_len` and a pointer to `exact_len` sets), with the count type wide enough for the budget (asserted) |
| P4 | `PCREC_SPAN_WALK_SUBSETS` (512 subsets) | `limits.def:393`, `kset.c:875` | BUDGET: a sound under-statement, already labelled UNMEASURED in its row | KEPT as the one compile bound, labelled, with a census owed (§3.3). Its description loses "2 x PCREC_PREFIX_K_MAX levels" |
| P5 | the set representation `uint8_t[32]` | throughout | OWN: 256 byte values | — |

### 1.2 pcrec, the machine reading and the conjuncts (`src/gen/known.c`, `known.h`)

| # | bound | site | verdict | rev 1 |
|---|---|---|---|---|
| M1 | `KN_CAP = MF_MAX_SPAN_POS` (32): `lv[KN_CAP + 1]`, `nlv[]`, `set[KN_CAP][32]` | `known.c:34`, `:41-45` | INHERITED from the kit's term bound | REMOVED: the walk's horizon is the slice's `exact_len` (§3.2). Rows and sets go in counted arena arrays, one per depth walked |
| M2 | the sentinel `w->k = KN_CAP` and `cc_width`'s `k <= KN_CAP - 1` | `known.c:132`, `:250` | an off-by-one on M1 (rev 0 §1.3), with two causes behind one value (SOUND-4) | REPLACED by three explicit outcomes (§3.2). Rev 0's C7 fix is kept in substance: the walk tests its last depth |
| M3 | rows per depth `cap = d->n * 4 + 8`, decline `fixed-width/rows` past it | `known.c:129`, `:157` | SCRATCH, a guess | sized from the machine: the count of virtual states (Σ over states of max(1, `scan_span`)), which no depth can exceed, so the decline cannot fire |
| M4 | `MkEnd.k` `uint8_t`, `MkEnd.set[MF_MAX_SPAN_POS][32]` | `known.h:24`, `:28` | INHERITED (M1) | counted, as P3 |
| M5 | `pcrec_cover_proof_diff` loops `[MF_PROOF_LO, MF_MAX_FWD)` over `cls->proven[]` | `known.c:510-533` | INHERITED from the seam (K4) | loops over the reply's counted proof range, which must reach `k` (§4.1) |
| M6 | `pcrec_known_derive` indexes `proven[d - MF_PROOF_LO]` for `d < exact_len`; `MkDerived.prefix` `uint8_t`, `suffix_lo` `int8_t` | `known.c:539-570`, `known.h:42-46` | INHERITED. Out of bounds once `exact_len` > 32, but it has NO caller (grep: only its declaration) | bounded by the counted proof range, with wider fields. The alternative is deleting it ([MATCH-KNOWN] is PARKED); the build picks, and both are two lines |
| M7 | `emit_cover`'s `scan_position + %d`; `req_run_in_cover`'s loop to `e->k` | `emit_dfa.c:14510`, `:16278` | OWN: `int`, length-driven | — |
| M8 | the trace build's ONE-WALK hull control `d < hull.nwalk` | `facts.c:391` | the hull's own reach (24): past it the slice has no hull check | unchanged. Past 24 the slice's controls are C8's machine equality and X0 (§5.1) |
| M9 | the listing and SPANSET printers | `facts.c:403`, `:945` | OWN: length-driven | unchanged. A long span gives a long debug line |

### 1.3 The seam (`memfn/include/memfn.h`, `MF_SITE_ABI` 29, `MF_CLASS_V` 10) and pcrec's mirror

| # | bound | site | verdict |
|---|---|---|---|
| K1 | `MF_WSPAN_POS = MF_MAX_SPAN_POS = MF_MAX_TERM = 32`: `mf_wspan.set[MF_WSPAN_POS][32]`, `table_ref[MF_WSPAN_POS]` | `memfn.h:277`, `:302`, `:653`, `:682-684` | INHERITED. `MF_MAX_TERM` is "the widest step a site may state", which comes from emit_vm.c's `VM_MAX_STRIDE` (32, `emit_vm.c:230`). A REPORT window is never translated to terms (window.c:1681, SOUND probed-and-held), so the term bound has no reader on this statement |
| K2 | `mf_wspan.len`, `core_lo`, `core_len` are `uint8_t` | `memfn.h:671-681` | SCRATCH: a 255-position cap behind K1 |
| K3 | `MF_WREACH` 64: `start + len <= MF_WREACH` | `memfn.h:667`, window.c:483 | CHOSEN (D77, "twice the longest piece"), and derived from K1. The after-context sits at offset `k`, so `k <= 63` |
| K4 | the proof range `[MF_PROOF_LO, MF_MAX_FWD) = [-8, 33)`, `mf_class.proven[MF_MAX_FWD - MF_PROOF_LO][32]` | `memfn.h:314-315`, `:1340` | INHERITED from K1 (`MF_MAX_FWD = MF_MAX_SPAN_POS + MF_MAX_AHEAD`). pcrec reads every offset of `[-1, k]` (C14) |
| K5 | `MF_WPLAN_MAX = MF_WREACH + MF_MAX_BACK` (72): `mf_wreply.plan[]`, `plan_term[]`, `plan_test[]`, `nplan` `uint8_t` | `memfn.h:1674`, `:1692-1707` | INHERITED from K3 |
| K6 | `MF_WMAX_SPAN` 32 spans per alternative | `memfn.h:658` | not binding: a cover states at most 3 spans. Its comment derives it from `PCREC_PREFIX_K_MAX` and calls the check an assert; it is a runtime check (`memfn_sites.c:584`; PREMISE-2). PREMISE-7's U1 (a `_Static_assert`) is noted, not taken here |
| K7 | pcrec's mirror `window_bounds_check` (K1, K3, K6) and the unchecked index `pcrec_memfn_wpos_bits(&sp, d, ...)` | `memfn_sites.c:534-594` | follows the seam. Until the seam changes, a statement with `k` > 32 would WRITE PAST `mf_wspan.set[32]` in `cover_window` before the loud check runs. That is why stage 1 carries the capacity row C15 (§3.5) |

### 1.4 The kit's own (`memfn/src/window.c`): the kit's to keep, remove or label

Listed as facts for the request (§4.3); how they move is the kit's call (D157).

| # | bound | site | note |
|---|---|---|---|
| W1 | `WF_NPOS = MF_WPLAN_MAX`: `wf_pos p[]`, `poff[]`, `pterm[]`, the plan's `off/set/core/table/grp[WF_NPOS]` | window.c:155, :183, :219-220, :1323-1354 | follows K5 |
| W2 | D-hors's shift table `uint8_t sh[256]`, `_Static_assert(MF_MAX_SPAN_POS < 256, ...)` | window.c:1850 | a shift is at most the window's length. Past 255 it needs a wider type, or a shift capped below the true one (shifting less is sound) |
| W3 | `run_bytes`' buffer `2u * MF_WSPAN_POS` | window.c:3006 | follows K1 |
| W4 | the legacy form `run[MF_MAX_TERM][MF_WSPAN_POS]`, `np > MF_MAX_TERM` → 0; C-run's `int8_t grp` (`_Static_assert` :1772) | window.c:1440-1463, :1772 | a form choice, not a refusal. Not reached by a REPORT site |
| W5 | the statement check `len <= MF_WSPAN_POS`, `start + len <= MF_WREACH` | window.c:481-484 | follows K1, K3 |

### 1.5 Adjacent, not on this path

- `PCREC_PREFIX_K_MAX` (24) itself. It stays the k-set walk's bound (the offset-k skip's
  hull, `win_offer_name`, the reseed statement, `run_pin`'s clip, which the spec states
  as `0:0+24` in `tuning.md` §2.30¶4 and `facts_listing.md` §4.1.2¶7). Its label is
  honest: chosen with headroom over a measured corpus maximum of 13 (`offset_k_skip.md`
  §3.3). It is one member of PREMISE-7's family ("a bound sized for one walk, borrowed
  by another reader"), filed in §8 as a plan row, not removed here.
- `PCREC_MAX_REQ_RUN_SCAN` (32, the required-run analysis). `req_run_in_cover` maps a
  run of at most 32 positions into a cover of any length (loops to `e->k`). Not a bound
  on the cover.
- `MF_MAX_BACK` (8): the before-context sits at -1. Not a length.

### 1.6 Why 24, and why 32 (kept short from rev 0)

The 24 was chosen on 2026-08-28 for the offset-k skip: "past two dozen bytes a
still-narrow prefix is vanishingly rare" (`offset_k_skip.md` §3.3). The span slice
inherited it when `kit_proof.md` built the slice as "the k-set walk, extended". The 32
is `MF_MAX_TERM`, sized for the VM's cursor-rung stride. Neither was ever measured for a
cover.

## 2. Premise, re-tested at `1b75dba61`

`limits.def:392` still has `PCREC_PREFIX_K_MAX 24`, and `memfn.h:277` still has
`MF_MAX_TERM 32`. Single compiles, `-p rx --features all`:

| pattern | enc | width | `span_facts` | route today |
|---|---|---|---|---|
| `lit-l31`, `lit-l40` | both | [31,31], [40,40] | 24 | unanchored |
| `[0-9a-f]{32}`, `\d{32}`, `\b[0-9a-f]{32}\b` | both | [32,32] | 24 | unanchored |
| bench `uuid` (`\b..{8}-..{12}\b`), `wild-validator-uuid-grok` | both | [36,36] | 24 | unanchored |
| `\b(github_pat_[0-9a-zA-Z_]{82})\b` | both | [93,93] | 0 (the 48 horizon) | unanchored |
| corpus `a{500}`, `[ab]{1000}`, `(?:ab\|ba\|aa\|bb){24}c` | both | [500,500], [1000,1000], [49,49] | 0 | unanchored |
| `a{20}`, `(?:ab\|ba\|aa\|bb){11}c`, a 24-letter literal | both | fixed | = width | **cover** |
| short twins: `\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{2}\b` (17), `[A-Fa-f0-9]{8}-(?:[A-Fa-f0-9]{4}-){2}[A-Fa-f0-9]{4}` (23), `\bgithub_pat_[0-9a-zA-Z_]{10}\b` (21) | both | fixed | — | **cover** |
| `\b(github_pat_[0-9a-zA-Z_]{10})\b` (the capture) | both | fixed | — | unanchored (C1/C5) |

So the slice's length is what stops every long fixed shape that has no capture, and the
short twins already cover.

## 3. The design

### 3.1 The span slice states as far as it proves

`pcrec_span_walk` (`kset.c:853`) loses P1 and P2. Exploration is breadth first and
expands every non-accepting subset. It stops when the subsets run out or the budget P4
is reached. The exact-prefix loop runs over depths until a depth is not exact (`!ok`) or
has no live subset (`!seen`). `MkLang` becomes counted (P3).

- **Termination.** There are at most `PCREC_SPAN_WALK_SUBSETS` subsets, each at one
  depth, so the exact loop runs over at most that many depths.
- **Soundness and monotonicity.** These are the critics' hand-executed argument (SOUND
  probed-and-held, at 2x24 → 2x32), and it holds unchanged with no horizon. Subsets are
  created in depth order: every subset at depth `D` exists before any subset at depth
  `D` is expanded. So exhausting the budget at a deeper level never prevents a
  shallower subset from being created. Every subset today's walk creates is created
  identically. Liveness only moves from unknown to known. So a set stated today is
  stated identically, and `exact_len` never shrinks. An under-statement was already
  sound (`facts.h:296`).
- **Compile work.** The worst case is unchanged: the budget was reachable before, by bushy
  patterns. Typical work grows for long bodies, which now walk to their accept instead
  of to depth 48. A literal costs one subset per position.

### 3.2 The machine reading walks as far as the slice

`kn_walk` (`known.c:126`) gets its horizon from the slice. `cc_width` (C7) reads the
stated slice, as C8 does (no `used` record, `facts_listing.md` §4.1¶2), and walks depths
`0..H` with `H = exact_len`. C8 can only admit `k <= exact_len`, so a deeper walk could
not change an admission. This gives the machine side the same one bound as the slice,
with no constant of its own, and it keeps work bounded on patterns whose width is huge
(`(?:a{1000}){1000}`). Rows and sets are counted arena arrays, allocated per depth walked
(M1, M4). Rows per depth are sized from the machine (M3).

The outcomes, spelled per SOUND-4 / PREMISE-6. At each depth `j <= H`, in order:

1. `nlv[j] == 0`, or `ended` was set at depth `j - 1` (a view-gated final newline): `k = j`.
2. some row at `j` accepts in any form: `k = j`.
3. the loop finishes `j = H` with neither: if `ended` was set at `H`, `k = H + 1`;
   otherwise the walk is PAST the slice, and `k = H + 1` with the flag `past`.

C7 holds for `k >= 1` with rows at `k`, or for `past`. Then C8 declines every
`k > exact_len` as `exact/producer-short`, which is what it is: the slice is short. The
`why` changes are bounded and named (§5.2). Bodies that today read `fixed-width` only
because of M2's sentinel (widths 32 and up) now read `exact/producer-short` (past the
budget) or cover. Bodies with `k > H` whose `machine-inexact` lay deeper than `H` now
read `producer-short`. Every outcome is still a decline, so no answer moves.

### 3.3 The one compile bound: `PCREC_SPAN_WALK_SUBSETS`, labelled

It stays at 512, with its row's existing label: "UNMEASURED: chosen as a compile budget,
not from a census". Rev 1 adds two facts to that label.

- **It is a cliff, not a cut.** Liveness is decided from the leaves. If the budget runs
  out before a body's accept, no subset on the way is known live, so `exact_len` is 0 —
  not the prefix the budget did reach. On a literal (one subset per position plus the
  root) the cliff falls at about 511 positions. The build MEASURES the exact value by
  bisection (L*) and does not pre-state it. Corpus `a{500}` lies below it, and
  `[ab]{1000}` lies past it and declines. That decline is sound: the body stays on the
  engine.
- **How it is measured.** A census over the committed population (corpus + bench) in a
  trace build gives, per compile: the subsets the slice used, whether the budget broke,
  `exact_len`, and the `width` fact. It is reported as two counts: compiles where the
  budget broke, and of those, compiles whose width is fixed and below the budget's
  literal reach (the ones the budget costs a cover). The same run records wall time for
  the slice. The census is a `boxqueue` job in the build lane, not a check. The bound is
  re-derived only if the census shows it binding on a pattern somebody runs (D77).

A per-depth "statement up to where liveness is known" would remove the cliff, but it needs
a liveness proof that does not reach the accept. That is not available on the NFA without
over-stating sets. It is filed as an idea, not designed here.

### 3.4 Size as a function of length (PREMISE-1, rulings file item 1)

The cover's text is the kit's. Measured on today's compiler at widths that already cover
(4 to 24). The arms are the same pattern by default (cover) and under
`--memfn=no-window-search` (the engine), so only one variable differs (COST-5). The
table gives `gcc -O2 -S` lines, as a slope per position over 4..24 and the value at 24:

| shape | enc | cover slope | engine slope | at 24: cover / engine |
|---|---|---|---|---|
| distinct-letter literal | byte | 30.3 | 60.9 | 1,293 / 2,013 |
| distinct-letter literal | utf8 | 33.3 | 60.6 | 1,628 / 2,555 |
| `[0-9a-f]{k}` | byte | 8.0 | 0 | 768 / 738 |
| `[0-9a-f]{k}` | utf8 | 24.7 | 0 | 1,337 / 1,237 |
| `\b[0-9a-f]{k}\b` | byte | 19.6 | 6.2 | 1,196 / 909 |
| `\b[0-9a-f]{k}\b` | utf8 | 30.6 | 6.2 | 1,712 / 1,356 |

(scratch `size.tsv`, 72 compiles. C-source bytes follow the same shape: a literal's cover
is 32% smaller at 24, and the class covers are 10-20% smaller in C but larger in `.s`.)

So the cover's text is LINEAR in `k` on every shape. The engine's is flat on a one-set
run, because the scan-edge pass deletes a counted run's interior states. Literals win
more as they grow, since the engine grows twice as fast. Class runs cross over near
`k = 20` and lose from there. Extrapolated (UNMEASURED, linear): `[0-9a-f]{100}` under
utf8 is about 3,200 lines against 1,237, and `a{500}` is on the order of 4,000 to 15,000
lines against a flat engine. The unbounded span therefore has a size cost that is the
kit's to answer. The fact that answers it is one pcrec already holds: which positions
carry the SAME set (a run of one set with a count). The engine exploits exactly that
fact. pcrec offers it in the request (§4.3 FACT 3), along with a table offer per
distinct set (FACT 4). It names no form (D157). G3 decides speed and G6 reports size.

### 3.5 Two stages

- **Stage 1 (pcrec only, today's seam).** §3.1-§3.3, plus one conjunct row:
  `C15 statement-fits` (kind `seam`, read right after C7). It holds when the statement
  fits the seam as it is: `k <= MF_WSPAN_POS`, the after-context's `k + 1 <= MF_WREACH`,
  and `k < MF_MAX_FWD`. pcrec carries no bound of its own. The only cap left is the
  seam's present capacity, read from the kit's own constants, and it exists so that
  `cover_window` never writes past `mf_wspan.set[]` (K7). Movers: the 25..32 shapes
  (§6).
- **Stage 2 (with the kit's delivery of §4.3).** The seam is counted. `C15` is RETIRED,
  the way C2 was: the id stays, absent. `cover_window` and `pcrec_cover_proof_diff` read
  the counted lists, and `pcrec_memfn_wspan`'s `uint8_t` casts go. Movers: everything
  up to the budget (§6).

Stage 1 alone already removes every INHERITED pcrec-side row (P1, P2, P3, M1, M2, M4).
Only C15's dependency on the seam is left, and the request removes it. Each stage is
one pcrec `abi` event (§4.4).

### 3.6 The standing questions

1. **Measurement regime: RELEVANT.** G3, G5 and G6 are measured. Every number here is
   either a compile count (`gcc -O2 -S` lines, C bytes; gcc 15.2, the 7700X dev box) or
   skipmeas's `instructions:u` (match regime, dense subjects). No decision here depends
   on the regime: the cover is answer-identical by proof. The open regime question is
   G3's, and it is sharper than in rev 0: a class cover's text grows with `k` (§3.4), so
   icache-bound regimes (short subjects, cold calls) can flip a gain into a loss, and
   §7 times them explicitly.
2. **Independent control: RELEVANT.** A selection widens and two producers grow. §5.1
   names, for each check, what it is checked AGAINST: libpcre2 10.46 (kitproof answers,
   X0); the engine route of the same compiler (the axes deny arm); the anchored DFA
   against the NFA slice (C8, two machines). The mover prediction comes from the
   BASELINE's decline records (§5.2). K35 is satisfied because the sweep counts the
   whole population and the kitproof floors rise by the rows added. [MECH-REACH] is
   satisfied because each new sabotage row names its witness, and the build checks the
   witness's reach on the clean tree (`tests/kitproof/reach.sh`).
3. **What moves on regeneration: RELEVANT.** `limits.def` gains no row. One description
   changes (P4), so the `--list-limits` text and `internal.h`'s generated block move.
   `limits_check.sh`'s manifest is names only, so it does not move. Regenerated by the
   build: `tests/kitproof/answers.tsv` (`gen_answers.sh`, new rows), the start-set mover
   manifest (`tests/startset/manifests/manifest_s3_dfa.tsv`: a pattern that becomes a
   cover leaves the DFA-hat movers), and the recursion identity gate's FILEPIN/ABASEPIN
   pins (§4.4). Not regenerated: `docs/dev/artifact_size_log.tsv`. Its re-archive is a
   separate gate commit from a clean full default run (`tests/size/CLAUDE.md`), and no
   per-mover size pin exists (COST-4).

## 4. The seam change, and the kit request draft

### 4.1 What pcrec needs across the seam (facts)

- pcrec STATES one window span of `k` positions, for any `k >= 1`, plus one context
  position before it (offset -1) and one after it (offset `k`).
- pcrec READS, for every offset from -1 to `k`, the set the kit's text tests there, and
  checks it equals what it stated (C14; `pcrec_cover_proof_diff`). Today that range ends
  at `MF_MAX_FWD` = 33.
- pcrec READS the reply's `stop` (`req_run_at`). Nothing else in `mf_wreply` is read on
  the cover path.

### 4.2 pcrec's side of the change (stage 2)

`cover_window` states the span as the counted form the kit chooses. Its sets come from
`MkEnd`'s counted array, and runs of one set are stated as runs if the kit takes FACT 3.
`pcrec_cover_proof_diff` loops over the reply's counted proof range and fails as today
on any difference. `window_bounds_check` mirrors the kit's new statement check. `C15` is
retired. M6 is bounded by the counted range. pcrec's other window sites (OFS, reseed,
the run pre-check) keep stating what they state: a counted list carries them unchanged.
The build confirms that every one is byte-identical in the sweep.

### 4.3 KIT REQUEST DRAFT (for main to file; facts only, D157; no build go yet)

> **R-n (DRAFT, pcrec manager) — a window span of any length ([COVER-CAP] rev 1)**
> - GO: none yet. The pcrec side has no build go. File on main's call; the kit-side
>   build waits on the owner's go for stage 2 (§8 Q1).
> - FACT 1. pcrec will state the cover's REPORT window site with span 0 of `k` exact
>   positions, where `k` is as long as the pattern's exact prefix proves. pcrec has no
>   upper bound of its own. In practice its compile budget caps a literal near 511
>   positions (UNMEASURED; pcrec's build measures it). Population today: 31-32 (`lit-l31`,
>   `hex32`, `dig-exact-32`, `hex32-id`, two corpus literals), 36 (the two bench uuids),
>   40 (`lit-l40`), 49 (corpus `(?:ab|ba|aa|bb){24}c`), 500 (corpus `a{500}`), each
>   under byte and utf8. Each has one context position at -1 and, where stated, one at
>   offset `k`.
> - FACT 2. pcrec reads the per-offset proof at every offset in `[-1, k]` and checks it
>   EQUALS its statement (C14). Today the proof range ends at `MF_MAX_FWD` = 33, and the
>   statement is refused past `MF_WSPAN_POS` = 32 and past `MF_WREACH` = 64.
> - FACT 3. On long spans many consecutive positions carry ONE set (`[0-9a-f]{100}`,
>   `\d{32}`, `a{500}`). pcrec measured the cover's text growing linearly with `k` on
>   every shape: about 8 (`[0-9a-f]`, byte), 25 (utf8) and 20-31 (`\b`-bounded) `gcc -O2 -S`
>   lines per position, against a flat engine on the same class runs. pcrec can state a
>   span as runs of `(set, count)`. That is the same facts, compressed, and it is your
>   call whether you want it.
> - FACT 4. pcrec can offer a table (the existing `table_ref` hook) for every distinct
>   set in the span. `cover_window` offers none today.
> - THE BOUNDS ON THIS PATH, as pcrec reads them (yours to keep, move or label): the
>   statement's `MF_WSPAN_POS` (= `MF_MAX_SPAN_POS` = `MF_MAX_TERM`, which comes from
>   pcrec's `VM_MAX_STRIDE`; a REPORT site is never translated to terms),
>   `mf_wspan.len`/`core_lo`/`core_len` (`uint8_t`) and `set[]`/`table_ref[]` (fixed),
>   `MF_WREACH`; the reply's `mf_class.proven[]` (`MF_MAX_FWD`, an `MF_CLASS_V` reader)
>   and `mf_wreply.plan[]`/`plan_term[]`/`plan_test[]` and `nplan` (`MF_WPLAN_MAX`);
>   inside window.c, `WF_NPOS`, D-hors's `uint8_t` shift (window.c:1850's assert) and
>   `run_bytes`' buffer. Which of these move, and whether each becomes counted, is yours.
>   This is an `MF_SITE_ABI` event (and an `MF_CLASS_V` event where the reply moves).
> - ASK. (1) A reply in responses.md: can the statement and the reply carry a span of any
>   length, and in what form you would take FACT 3/FACT 4. (2) Confirm or correct
>   FACT 3's slopes, and say whether a long one-set run can be rendered without per-position
>   text, and at what run-time cost (your form). (3) G2 cases past 32 positions, at
>   lengths you choose.
> - pcrec's side (ours): counted `MkEnd`/`MkLang`, C15 retired, the proof check over the
>   counted range, one pcrec `abi` event in the same landing.
> - Deliver: a kit branch for merge review, for one landing with pcrec's stage 2.

### 4.4 The `abi` events (COST-1, rulings file item 2)

Both stages are pcrec `abi` events: a bump, a re-pin of the recursion identity gate's
pins, an entry in `docs/dev/history/abi_changelog.md`, D94's grep of every reader of the
current number (107 at `1b75dba61`), and the suites that count (registry, codegen,
rxtsource). The gate's own rule says so. Its D76 block in
`tests/codegen/run_recursion_identity.sh` says that (B)'s pin "IS, by definition, the
commit that introduced the CURRENT `abi`". (B) compares whole files over every call-free
corpus pattern, and `litrun.rxt:1204`/`:1320` (stage 1), `d27_large_counts.rxt:6` and
`counterk.rxt:1917` (stage 2) are in that population and change their search bodies. A
re-pin without a bump would contradict that definition. Precedent for a no-bump re-pin
exists (span-arms R1, abi 98, recorded at the pin's own line). Rev 1 does not rely on
it. The cover's own landing bumped (abi 92). Stage 2 also moves kit bytes, and D146/D147
says a kit byte move is a pcrec abi event in the same commit. (A), the program region,
does not move: it is empty on DFA artifacts (critic verification).

### 4.5 Spec (D80), in the same change

Required, not recommended (COST-8). `facts_listing.md` §4.1.2¶7c states that the exact
prefix has no length bound beyond the walk's compile budget (`PCREC_SPAN_WALK_SUBSETS`,
`--list-limits`), and that past that budget it is 0. `match_api.md` §6.3.4¶2's
`"cover"` row names no bound and stays as it is. `cli.md` §2.6's `--list-limits` row
text follows P4's description. The abi changelog entry is §4.4's.

## 5. Answer-identity plan

### 5.1 The checks, and what each is checked against

| check | against | proves |
|---|---|---|
| `make test` (`.rxt` corpus, both encodings) | oracle-verified expectations (python `re` / libpcre2) | every mover's existing cases (`litrun.rxt:1204`, `:1320`; stage 2 also `d27_large_counts.rxt:6`, `counterk.rxt:1917`) answer as before through the cover |
| `make test-axes` | the same compiler under `--memfn=no-window-search` (`tuning.md` §2.43¶3d), whose artifact is the engine's | cover against engine on every corpus subject, every mover |
| `test-kitproof`, new rows (§5.3) | libpcre2 10.46 (`oracle.c`, committed `answers.tsv`) | the boundaries at every startoffset and the find-all loop |
| the default build's `pcrec_cover_proof_diff` (an internal error on any difference) | the kit's proof against the stated sets | the kit proves exactly what pcrec states, at every `k` |
| trace build: C8 `producers-disagree` assert; X0 (`kit_proof/x0`) on the SPANSET records of the movers | the anchored DFA; libpcre2's own sets | slice positions past the hull's 24 (M8). X0's cost grows with `k`, so it runs on the mover list only |
| `make asan` over the kitproof and litscan sections | AddressSanitizer | counted arrays replace fixed ones (P3, M1, M4, K1-K5): the overflow class this design touches (K7 shows it is real) |
| `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` | the clean tree | every kitproof witness still reaches its site after the row fires in new places |

### 5.2 Byte identity and the mover list (G2)

Run `scripts/emit_sweep.py` with main-before as the baseline against the candidate, over
the committed population, with `--trace`. Every artifact must be byte-identical except
for the `abi` stamp line (normalized on both sides, and the normalization named in the
deliverable) and the movers. Each mover differs by its route (`RX_DFA_SCAN` to
`"cover"`, `RX_DFA_PREFILTER` to `"none"`, `RX_DFA_START` to `"attempt-start"`) and the
text that follows from it.

The PREDICTED list is built from the BASELINE trace build's `KITPROOF` records and `width`
facts. It is every decision whose `why` is `fixed-width` or `exact/producer-short` and
whose `width` is `[k, k]` with `k >= 25`, kept to `k <= 32` for stage 1. The check is
predicted == observed, both directions. Each predicted pattern that stays on the engine
is listed with the candidate's `why`. The expected kinds are: the budget (`exact_len 0`,
the census names it); C9-C14; C1/C5 for captures; C15 at stage 1. Each observed mover
outside the prediction is read before landing.

A second, listing-only population moves too (SOUND-1, widened): every body whose
`span_facts` grows. These are the bodies listing 24 today whose exact prefix is longer,
and the fixed bodies listing 0 today because their accept lies past depth 48 (`a{500}`
0 → 500, `(?:ab|ba|aa|bb){24}c` 0 → 49, a 50-byte literal 0 → 50). Listing values
never shrink (§3.1). The sweep compares the trace's `span_facts` values the same way,
predicted from the baseline's `width` facts.

### 5.3 New witnesses (`tests/kitproof/cases.tsv`)

The lengths come from the brief: 24, 25, 32, 33, 40, 100 and 1000, for a literal and for
`[0-9a-f]{n}`, with `\b[0-9a-f]{n}\b` at 32, 40 and 100.

- `verdict` (`RX_DFA_SCAN`):
  - stage 1: cover at 24, 25 and 32; decline at 33, 40, 100 and 1000 (C15).
  - stage 2: cover at 24 through 100; decline at 1000 (the budget).
  - L* and L*+1, bisected by the build on a literal (the budget's cliff, §3.3), as
    observed, never pre-stated.
  - `\d{32}` under `u`.
  - a body whose last position carries a view-gated final newline (the `ended` path,
    PREMISE-6), with its observed `why` recorded.
- `facts` (`span_facts` count): 40-literal `40:`; 50-literal `50:` (0 today); 100-literal
  `100:`; 1000-literal `0` (pins the cliff); `a{30}(?:b{30}c|d)` `31:` (24 today).
- `answer`: at each length `n`, subjects of `n-1`, `n` and `n+1` bytes; a last-position
  near miss; a match at the subject end; two adjacent matches (find-all); every
  startoffset. Expectations come from libpcre2 via `gen_answers.sh`.
- The floors (24 verdict / 6 facts / 55 answer rows) rise by the rows added.

### 5.4 Sabotage rows (mech arm `kitproof`), told apart by their witnesses (SOUND-2, SOUND-3)

| plant | what it restores | unique witness | why only it flips |
|---|---|---|---|
| (a) the exact loop bounded again (`d < 32`) | P1 | `facts` 40-literal `40:` → `32:` | (b) and (c) leave the loop alone |
| (b) the horizon left at `2 * PCREC_PREFIX_K_MAX` (a half-applied build) | P2 | `facts` 50-literal `50:` → `0` | (a) states `32:` there, not 0. Every literal ≤ 48 is unaffected |
| (c) the machine walk stops one depth short (`j < H`) | M2's off-by-one | `verdict` 25-literal cover → decline | (a) and (b) leave every body ≤ 32 covering |
| (d) stage 1 only: C15 removed | K7 | the 40-literal compile goes red with `window_bounds_check`'s internal error (under ASAN, the overflow) | nothing else reaches a 40-position statement at stage 1 |

The verdict check reads only `RX_DFA_SCAN` (`run_cover.sh`), so the uniqueness comes
from the `facts` rows and the lengths, not from `why`. A `why` column on verdict rows
is not added: no plant needs it. The sabotage ids are the build's to take.

## 6. Movers estimate

Stage 1 is OBSERVED for the bench four (the rev 0 premise critic's planted V2 compiler, both
encodings). Everything else is PREDICTED: the width is fixed, there is no capture, the
24-wide twin covers today (§2), and the slice reaches the width within the budget. The
sweep's count is the count of record.

| population | stage 1 (≤ 32) | stage 2 (any length, up to the budget) |
|---|---|---|
| bench | `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`: 4 patterns x 2 encodings (observed under V2) | + `lit-l40` (40), `loglines/uuid` (36), `wild-validator-uuid-grok` (36): 7 x 2 |
| bench, NOT moving | — | `wild-secrets-github-pat` x 2 ids (capture; its uncaptured twin covers), `uuid-near-miss` x 2 (`^...$`, attempt route), `wild-secrets-slack-webhook-url` and `line-80` (variable width), `qnt-poss-plus` |
| corpus | `litrun.rxt:1204` (31), `:1320` (32) | + `d27_large_counts.rxt:6` `a{500}` (if below L*), `counterk.rxt:1917` `(?:ab\|ba\|aa\|bb){24}c` (49) |
| corpus, NOT moving | — | `d27_large_counts.rxt:37` `[ab]{1000}` (past the budget), `:29` `(ab){300}` (capture), the variable-width counted and possessive tests |
| outside both (rulepilot inventory) | `(?i)permission is hereby granted` (28), byte only: under utf8 the case folding gives variable width (PREMISE-3) | `req-<uuid>` (40) |
| `span_facts` listing values only | bodies listing 24 today with a longer exact prefix | + fixed bodies listing 0 today (accept past depth 48) |

kvcensus query (PREMISE-5), stated: rows of `docs/dev/kvcensus/patterns.tsv.gz` with
`status` ok, `exact` 1 and `span >= 25`. That gives bench 14 native / 13 utf8 and corpus
48 / 17. The census caps `span` at 32, so it cannot separate 32 from wider. Most corpus
rows are possessive or atomic tests that are variable width (C7/C10 decline them).

## 7. Re-timing plan (not run; a night window later, per stage)

- **Cells, generated, not hand-listed (COST-6).** §5.2's OBSERVED movers x the bench's
  regimes (`match-compliance`, `short-subject-search`, `large-subject-throughput`) x
  both encodings x the subject families each cell runs (litrun `mat`/`fbf`/`lbf`/`bnd`).
  The cell list is confirmed with the bench dev before booking (memory
  `pcrec-ask-bench-dev`). Stage 1 covers `lit-l31`, `hex32`, `dig-exact-32` and
  `hex32-id`. Stage 2 adds `lit-l40`, `uuid` and `wild-validator-uuid-grok`.
- **One variable.** Before is main at the build's base. After is main with the stage.
  Same dev box (7700X), same bench pin, same gcc/glibc, same night. §5.2 proves that the
  two builds' artifacts differ only on movers.
- **Controls (A/A).** `lit-l16` (cover on both) and a non-mover engine cell on both
  (`lit-l40` at stage 1). Also hit-dense and hit-sparse subjects, because the window
  find's cost depends on stop density.
- **G5's expectation, measured as its own variable.** The 24-position twin
  (`[0-9a-f]{24}` and a 24-letter literal) under default against
  `--memfn=no-window-search`, on the before compiler. Its ratio is the expected size of
  the gain. G5's bar is faster beyond noise.
- **Read.** G3 on every cell, with `fbf` and `short-subject-search` first. The class
  covers grow with `k` (§3.4), so the icache-bound cells are where a loss would show. A
  loss beyond noise gets one bounded effort, then a ruling, never a length cut-over.
  Size (G6) is read from the same build: C bytes and `.text` per mover.
- **Window.** Night, cleared with Frank, outside 20:00-01:00, booked through main and
  the bench inbox after the stage lands.

## 8. Questions for the owner (plain words)

1. **One step or two?** Step one changes only pcrec. It drops pcrec's own length limit
   and covers up to 32 positions, which is all the kit's interface carries today. That
   moves `lit-l31`, the 32-character hex and digit shapes, and `hex32-id`. Step two
   needs the kit to accept a span of any length, and then the uuids, `lit-l40` and the
   longer corpus shapes move too. Leaning: two steps. Step one's gain arrives first, and
   its re-timing is the evidence for the kit's work.
2. **Code size on long class shapes.** For shapes like `[0-9a-f]{n}` the cover's code
   grows with every position, while the engine's stays flat. At 32 positions that is
   modest (`hex32-id` is about 23% more machine code). At hundreds of positions it would
   be several times the engine's. Do you accept that growth at step one, and should step
   two wait until the kit has answered whether it can keep a long run of one character
   class compact? Leaning: accept it at step one (speed is measured, not assumed). Step
   two lands only with the kit's answer, and that answer is not a length limit.
3. **The one compile budget.** The span walk keeps its existing work budget (512 steps
   of its subset search). It is unmeasured. Past it, a body gets no proven prefix at
   all, so a 600-letter literal stays on the engine. Keep it as it is, and have the build
   count where it actually binds? Leaning: yes. Re-derive it only if that count shows a
   real pattern losing.
4. **Build go** for stage 1 (§3.1-§3.3 plus C15, §5's checks as the delivery bar), at
   opus tier because it is engine and facts code. Stage 2 needs its own go once the kit
   replies.

For main, not the owner: [DD-11.5] (STARTED) adds a producer into the same `MkLang`. Its
next step should rebase on the counted form. [DEC-LIMITS]'s trigger ("the next new
limit") does NOT fire, because rev 1 adds no limit row. A plan row for PREMISE-7's family
(per-offset bounds borrowed across walks: `run_pin`'s clip to 24, the K38-2 pre-check's
verified extent, `MF_WMAX_SPAN`'s derivation, `PCREC_CTX_ITEM_TERMS` in design) is
proposed for main to file, at BOONIES unless a measurement names a member.

## 9. Rev 0 round findings (`docs/dev/reviews` draft at scratch `crit-covcap/review.md`)

| id | finding (short) | rev 1 |
|---|---|---|
| COST-1 | "no abi event" was wrong; (B)'s whole-file pin moves | §4.4: both stages are abi events, bump and re-pin, citing the gate's own D76 rule. Rev 0's G5 "no seam event" is dropped |
| PREMISE-1 | class movers grow; "movers SHRINK" was false | §3.4: size per shape as a function of `k`, measured like-for-like; FACT 3/FACT 4 in the request; G6; §8 Q2 |
| SOUND-1 | a second listing population (bodies listing 0 because of the 48 horizon) | §5.2: listing movers widened. With no horizon, every fixed body below the budget lists its width |
| SOUND-2 | no witness reached the second bound | §5.3/§5.4: a witness per bound: the exact loop (40-literal facts), the horizon (50-literal facts), the machine walk (25-literal verdict), the seam (40-literal compile) |
| SOUND-3 | the two plants could not be told apart by verdict rows | §5.4: unique witnesses per plant, carried by `facts` rows and lengths. "Must not also trip" is dropped |
| SOUND-4 / PREMISE-6 | `kn_walk`'s sentinel has two causes | §3.2: three explicit outcomes. The sentinel is gone, and a verdict witness for the `ended` path is in §5.3 |
| PREMISE-2 | the reader table was incomplete | §1 is now an end-to-end inventory. The build edits the comments that become false: `known.c:31-33` (KN_CAP's "bounded by `PCREC_PREFIX_K_MAX`"), `facts.h:530-533` (a FIND-site `exact_len` reader that no longer exists), `kset.c:578`, the P4 description, `src/facts/CLAUDE.md`'s slice line, and design text in `kit_proof.md`'s slice paragraph, `ctx_span.md` §11 N-1 (closed by rev 1), `span_runs_sheet.md:497` and `patfacts/inventory.md:438`. `run_pin`'s `0:0+24` stays (§1.5) |
| PREMISE-3 | `(?i)permission is hereby granted` covers under byte only | §6: encoding named |
| PREMISE-4 / COST-7 cites | five known.c cites off by 1-6 lines | re-cited at `1b75dba61`: `cover_conj[]` :375, `cc_width` :247-250, the sentinel :132, `cover_window` :462, `pcrec_cover_proof_diff` :510 |
| PREMISE-5 | kvcensus counts did not reproduce | §6: query stated. Its counts are the critic's (14/13, 48/17) |
| PREMISE-7 | a family of borrowed bounds | members 1 (P1) and 6 (P2) are removed here. The rest are proposed as a plan row (§8, for main). U1 is noted at K6 |
| COST-2 | G4's 6M was picked | G5 is now "faster beyond noise". The 24-twin ratio is the expectation, measured as one variable (§7) |
| COST-3 | the C7 step built class shapes ahead of measurement (D77) | moot as a separate step: the class shapes come with removing the bound (G4's ruling). Their size risk is §8 Q2 |
| COST-4 | "re-pin" named a size pin that does not exist | §3.6 Q3: no per-mover size pin. The size-log re-archive is a separate gate commit |
| COST-5 | size numbers were not like-for-like | §3.4: same pattern, cover against `--memfn=no-window-search` |
| COST-6 | §5 named families, not regimes or encodings | §7: cells generated from observed movers x regimes x encodings |
| COST-7 overlap | [DD-11.5], [DEC-LIMITS] | §8, for main: DD-11.5 rebases; DEC-LIMITS does not fire |
| COST-8 | spec hunk only recommended; request carried method | §4.5 required; §4.3 respelled as facts, and the form is the kit's in every ask |

## 10. Contradictions found (STOP RULE: none; listed)

1. The brief's "compile work bounded by the subset budget, past which exactness is not
   claimed" is true, but the budget is ALSO a length cliff. Past it the slice states 0,
   not a shorter prefix (§3.3), so near 511 positions on a literal it acts as a length
   bound in effect. It is labelled, and measured by the census, not removed.
2. "No length bound" and today's seam cannot both hold at stage 1. A statement past 32
   writes out of bounds before the loud check (K7). Stage 1 therefore keeps one row (C15)
   that reads the KIT's present capacity, and stage 2 retires it.
3. The brief's boundary row at 1000 declines at every stage (the budget). It is still
   kept as an answer row and as the pin on the cliff.
4. Rev 0's C7 fix ("tests the rows at depth KN_CAP") does not apply in its rev 0 form,
   because there is no `KN_CAP`. Its substance stays: the walk tests its last depth
   (§3.2, outcome 3). The off-by-one becomes sabotage plant (c).
