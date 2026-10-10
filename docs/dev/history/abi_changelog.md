# The `abi` change log

What each `abi` bump changed in the emitted scaffolding, newest first. A
RECORD, not a contract: the contract is `docs/spec/match_api.md` (the current
`abi` number, what a bump means, and every current fact these entries
describe). Until 2026-10-09 this log lived in `docs/spec/match_api.md` §6
(D76 addendum, [REVW.A1]); the facts-only rewrite (lane specclean) moved it
here verbatim, from the paragraph that introduced it down to the oldest entry.

**A bump adds its entry at the top of the list below, in the bump's own
commit**, beside the spec's `rx_info.abi` sentence and the D94 ritual's other
readers. Entries are history: past tense is correct here, and an entry is
never rewritten to match later behaviour.

---

**THIS PARAGRAPH IS THE `abi` CHANGE LOG, and it is the only one** (D76
addendum, [REVW.A1], 2026-09-19). Every bump's own D76/D94 ritual carries a
`docs/spec/` hunk, so the ritual maintains this narrative by construction —
which is why it is gap-free from `2` to `42` while the three narrative copies
that lived in `src/gen/emit_dfa.c`, `src/gen/CLAUDE.md` and the codegen
suite's failure message had each drifted. Those are now a pointer, a pointer,
and a check's message copied FROM here. **A bump updates this paragraph, in
the bump's own commit.**

- **`rx_info.abi` is `73` on every artifact today (lane revbuild bumped it
  from 72, 2026-10-10: [OPT-REVEND] L2 with stage 2 folded in, D156; built
  as 72 and renumbered at the merge of the kit's R-12, which took 72).** An end-pinned
  DFA body (`$`/`\Z`/`\z`, no `(?m)`, no `\G`, not optional) searches by the
  reverse-from-end walk: `<PREFIX>_DFA_SCAN` reads `"rev-end"`, the artifact
  carries no forward machine (a tie with no anchored machine keeps it for
  the relocate), and the walk's seeds, dead-seed skip and tie arm are new
  emitted text. The generated stamp rule (`<PREFIX>_DFA_START`, WINDOW,
  FIRST, NEXT and the pre-check stamps read their slot's ABSENCE value where
  the path does not ask the slot) moves `<PREFIX>_DFA_START` to
  `"attempt-start"` on attempt/empty bodies; an empty body's `<prefix>_match`
  is the `"nomatch"` form; a whole-window pre-check ahead of a walk that
  answers presence itself reads `<PREFIX>_REQ_WHY "dominated"` and is not
  emitted. An exact VM hybrid's inlined prefilter walks too (stage 2) and its
  VM entry asks FINISH; the `-fno-rev-end` deny and the `locate` axis are
  new. No struct offset moves and no answer moves.

- **`rx_info.abi` was `72` (lane vmlazy bumped it
  from 71, 2026-10-09; `71` is [MEMFN] RQ-3's, landed first: [MEMFN] R-12
  — THE VMLAZY NORMALIZATION, `docs/dev/lanes/r12scope_report.md` §1.5,
  `docs/dev/lanes/vmlazy_report.md`).** The VM cursor rung's LAZY arm
  spells its rmin prefix (the loop's mandatory iterations) the way the
  rung's possessive and greedy arms spell theirs: a span scan capped at
  rmin iterations, then the reach test `if ((ptrdiff_t)<prefix>_span_cursor
  < slot_values[<low>] + <rmin*W>) goto <prefix>_fail;`. It was a counted
  loop that failed inside the loop at the first short block. The two forms
  stop at the same block and fail on the same inputs, and the step and
  work budgets are charged the same, so no answer moves. Only artifacts
  whose VM program has a lazy quantifier with `rmin > 0` on the cursor rung
  move beyond their abi digits, and on those
  `<PREFIX>_VM_PROGRAM_BYTES` moves with the text. No stamp is added, no
  struct offset or `rx_info` member moves, and no symbol a caller links
  against changes.
- **`rx_info.abi` was `71` (lane rq3 bumped it from
  70, 2026-10-09: [MEMFN] RQ-3, D155 addendum 2; rq3 was built on `69` and
  re-landed on R4e′.0b's `70`).** ONE stamp line is added
  to every artifact, both engines, directly after `<PREFIX>_MEMFN_LIBC`:
  `<PREFIX>_SIMD_GUARDED_BYTES` (§6.3), the artifact's CPU-guarded byte
  count. It reads `0ULL` on every artifact, since no SIMD form exists and
  `-fmemfn-simd` is inert. No other byte moves: every length decision now
  reads the SIMD-off length (`len_uncut` minus the guarded bytes; the caps'
  measure minus the guarded text's), which equals the old reading wherever
  nothing is guarded, and the sweep against `abi` 69 read zero movers
  outside the new line. No struct offset moves and no answer moves.
- **`rx_info.abi` was `70` (lane r4e0b bumped it
  from 69, 2026-10-09: [MEMFN] R4e′.0b — THE ROUTING, D155 item 6,
  `docs/design/memfn/integration.md` §R4.9.2.5/§R4.9.2.6).** Every
  offset-skip/pre-check function (`<prefix>_reqrun`, `<prefix>_reqrun_whole`,
  `<prefix>_ofsskip`) keeps its loop, byte for byte, under the head
  `<prefix>_<fn>__body`, and the function itself becomes one call to it,
  `return <prefix>_<fn>__body(subject, n, pos[, tables]);`: the SIMD-off
  shape that a later CPU-guarded helper adds `#if` arms above (the floor
  rule). Both are `static inline` in the `.c`, so no symbol a caller links
  against changes, no stamp is added or changes value, no struct offset or
  `rx_info` member moves and no answer moves; an artifact with no such
  function differs from `abi` 69 in its abi digits alone.
- **`rx_info.abi` was `69` (lane decattr bumped it
  from 68, 2026-10-09: [DEC-VAR-ATTRIB] + [DEC-COLLAPSE-WASTE], one event —
  `docs/design/dec_fallback.md` §5.1, §5.2, §6.1).** Two stamp VALUES move,
  no stamp is added. (1) A `${...}` pattern's `<PREFIX>_ENGINE_SEL` reads
  `"selected"` where a nullable one read `"declined-nullable-default"` (F1:
  its variable, not a nullability decline, turns the prefilter off). (2) A
  collapse rung is no longer offered on an attempt the collapse cannot help
  (no collapsible repeat; nullable but not `empty_admits`), so on a compile
  that drops the prefilter for size `<PREFIX>_VM_PREFILTER_WHY`'s
  `size cap retry, hybrid N > CAP` figure is the exact artifact's rather than
  the wasted retry's (`-e utf8 (\p{Xwd})`: `1028613` -> `1028607`). Every
  other artifact differs from `abi` 68 in its abi digits alone, and no answer
  moves. `--emit-ir` (not an artifact) moves too: `no-variable` and
  `no-size-cap` join the `prefilter` vocabulary (`ir_listing.md`).
- **`rx_info.abi` was `68` (lane nullanch2 bumped it
  from 67, 2026-10-08, re-landing lane nullanch1's change after R4h's layout
  normalization took 67: [NULLABLE-ANCH] — THE ANCHOR-AWARE NULLABILITY
  DECLINE, `tuning.md` §2.17).** Both prefilter declines read the new E1
  fact `empty_admits` instead of bare nullability, so a nullable pattern whose
  every empty path crosses a non-multiline `^`/`\A` AND `$`/`\Z`/`\z` keeps
  its exact hybrid prefilter. On a mover `<PREFIX>_ENGINE_SEL` reads
  `"selected"` (was `"declined-nullable-default"`), `<PREFIX>_VM_PREFILTER`
  `"hybrid"` (was `"none"`), and the prefilter's tables, scan and
  `<PREFIX>_VM_PREFILTER_LANG` appear (measured movers: exactly five of 4,262
  compiled corpus+bench patterns, `docs/dev/optloop/nullanch/movers_result.txt`
  — bench `evil-alt-nested` and `trim-nested-star`, corpus `^(a{2,4})?$`,
  `^(a?)(?1)*$`, `^(?:(?<g>a?)){0}(?&g)*+$`); every other artifact differs
  from `abi` 67 in its abi digits alone. No stamp is added, no struct offset
  moves, no `rx_info` member changes and no answer moves (a near-miss that
  exhausted the step budget now answers `nomatch`, K65's direction).
- **`rx_info.abi` was `67` (lane advnorm bumped it
  from 66, 2026-10-08: [MEMFN] R4h's layout-normalization pre-commit,
  Q-R4h-1 (b)).** The five in-loop ADVANCE sites are rewritten, text only,
  to the memfn kit's ADVANCE layout
  (`tests/memfn/pins/r4h_target/`): the DFA stay skips (forward and
  reverse), the scan-edge loops (unbounded and counted, both directions) and
  the VM span scan now spell `while ((MORE)[ && CNT < NULL] && (MEMBER)) {`
  with the step (and the counter increment) on their own lines in a braced
  body, and the cap as `%lluULL` rather than `%dUL`. No stamp, no `rx_info`
  member, no struct offset, no object byte and no answer moves; an artifact
  with none of the five loops differs by the abi digits alone. The emitted
  text is larger by tens of bytes per loop, so a size-cap refusal near its
  cap and the VM entry-shape knee can flip on a few artifacts.
- **`rx_info.abi` was `66` (lane possbuild bumped it
  from 65, 2026-10-07: [ART-POSS-ARMS], `docs/design/poss_arms.md` rev 2.1
  §9 — two possessify ARMS).** Arm A values a context gate (`\b`, `\B`, a
  one-character lookaround) in a quantifier's follow by what it can admit
  next; arm B reads a backreference's FIRST from its groups. Both widen which
  quantifiers the VM possessifies (and which atomic groups the free
  discharge deletes), so on a MOVER the possessified loop's emitted body,
  `<PREFIX>_VM_STRATS`, `rx_info`'s `frame_capacity`/trail VALUES and
  `<PREFIX>_VM_FRAMELESS` move (measured movers: §5.2 of the note, 3 bench
  and 3 corpus patterns; `doubled-word` becomes frameless). Every VM
  artifact gains `<PREFIX>_VM_POSS_ARMS` (§6.3), `0x0u` where no arm was
  needed. On a route flip `RX_ENGINE` itself moves (`\w++\b` is
  discharged and DFA-routed; none measured in the corpus).
  `-fno-poss-ctx-follow -fno-poss-bref-first` restores the abi-65 program
  apart from the abi digits and the new stamp line. No struct offset moves,
  no `rx_info` member is added, and no answer moves.
- **`rx_info.abi` was `65` (lane flagbits bumped it
  from 64, 2026-10-06: [FLAGBITS], K92 -- `rx_info.flags`' strategy mask
  is DERIVED from `src/core/axes.def`).** `-fno-size-term` (bit 18) and
  `-fno-scan-edge` (bit 21) were the two strategy deny bits the hand-kept
  mask had never listed, so each moved `.flags` on EVERY artifact it was
  passed to (`.flags = 262144` / `2097152` against `0` on `abc`, where
  neither can act). The mask is now every axis bit except the named kept set
  (`tuning.md` §2, "THE `rx_info.flags` RULE"), so both bits are masked and a
  future axis is masked on arrival. The only bytes that move are the `.flags`
  literal of an artifact built with one of those two denials (and the abi
  digits); a default artifact differs by the abi digits alone. No struct
  offset moves, no stamp is added, no program text moves and no answer moves.
- **`rx_info.abi` was `64` (lane ssbuild3 bumped it
  from 62, 2026-10-06; `63` is the memfn kit's R4a′: [START-SET] stage 3 —
  THE DFA HAT, `docs/design/startset.md` §2 F, §4.1, §6.4, D148 + addenda
  1-2).** The candidate table gains two DFA-route rows, `first-memchr-bounded`
  and `first-class-bounded` (`tuning.md` §2.42; `match_api.md` §6.3's `RX_DFA_PREFILTER`
  values). On a SEEDED forward DFA scan (a `\b`, a lookbehind, a `(?m)`
  context) whose plain bounded skip tests the start state's escape set `E`,
  and whose start set `S` cannot match empty and is a proper subset of `E`,
  the skip tests `S` instead — one byte by `memchr`, several by a 256-entry
  `<prefix>_start_bytes` table — and, where it moved, re-seeds the scan state
  from the byte before its landing. A VM hybrid's inlined prefilter takes it
  too. `-fno-start-set` restores the `abi`-62 `-fno-start-set` program (no
  VM hat either) apart from the abi digits. No struct offset moves, no `rx_info` member is added or changed, no
  stamp is added (`RX_DFA_PREFILTER`/`rx_info.prefilter` gain the two
  values), and no answer moves.
- **`rx_info.abi` was `63` (lane memfnbump bumped it
  from 62, 2026-10-06: [MEMFN] R4a′ — THE KIT'S TWO STAMPS,
  `docs/design/memfn/integration.md` §R4.3.3, §18, §22; D147 addendum 10,
  Q53, Q55).** Every artifact of both engines gains two stamp lines,
  written by pcrec-memory-functions (`memfn/`, D146/D147) directly after
  `<PREFIX>_RUN_WORDS`: `<PREFIX>_MEMFN_FORMS` (`"none"` on every artifact
  until the kit's first SIMD-on form) and `<PREFIX>_MEMFN_LIBC` (the
  artifact's source-level inventory of C library calls, or `"none"`; §6.3).
  The two lines render before the emitted-size measurement, so a size-cap
  retry's quoted size of its discarded attempt (`_PREFILTER_WHY`) includes
  them. No struct offset moves, no `rx_info` member is added or changed, no
  program text moves, and no answer moves.
- **`rx_info.abi` was `62` (lane ssbuild2 bumped it
  from 61, 2026-10-05: [START-SET] stage 2 — THE VM HAT,
  `docs/design/startset.md` §2 V, §4.2, §8, D148 + addenda 1-2).** The
  candidate table (`dfa_pfs[]`; the NEXT rows of `cand_rows[]` since
  [START-TABLE] C3, no abi event) gains its first row serving the VM route,
  `first-class` (`tuning.md` §2.42, listed live by `--list-axes` on the
  `prefilter` axis with the `RX_VM_START_SCAN` stamp): a VM artifact with no
  DFA prefilter, an unanchored pattern, and a start set `S` (the `start_set`
  fact) that cannot match empty and has fewer than 256 members SEEKS the next
  byte of `S` — a 256-entry table — before its first attempt and after each
  failed one, instead of attempting at every position. The seek sits after
  the range guard, K50, `rx_valid_upto` and the K65/K66 pre-check, so a
  pre-check NOMATCH and a `PCREC_ERR_UTF` are unchanged. Every artifact of
  both engines gains one stamp line, `<PREFIX>_VM_START_SCAN`
  (`"first-class"` or `"none"`, §6.3). `-fno-start-set` (bit 47, masked out
  of `rx_info.flags`) restores the `abi`-61 program apart from the abi digits
  and that stamp's `"none"`. No struct offset moves, no `rx_info` member is
  added or changed, and no answer moves; a give-up the skipped attempts would
  have hit may become the answer (§3.1).
- **`rx_info.abi` was `61` (lane k82hbuild bumped it
  from 60, 2026-10-05: [K82] (B) — THE HANDOFF, `docs/design/litscan_k82h.md`
  revision 2 and its rulings).** A new two-row first-match table, axis
  `req-use` (`tuning.md` §2.41, listed live by `--list-axes`), decides what a
  search body does with an emitted run pre-check's answer. Its `handoff` row
  keeps the pre-check's first window hit `c` (the LEFTMOST occurrence at or
  after `startpos`, now a written contract of the search block) and begins
  the body's scan at `max(startpos, c − K)`, `K` the window's maximum BYTE
  offset from the attempt start — a new core fact on the necessary-run walk,
  `req_run_maxoff` in `--emit-facts` — rounded up to a character start under
  a multibyte encoding, only when it moved. The three bodies with a DFA scan
  read it at their one start site (the DFA unanchored scan and its seed, the
  DFA attempt loop's first start, the VM hybrid's first prefilter call); `\G`
  keeps reading `startpos`. Every artifact of both engines gains one stamp
  line, `<PREFIX>_REQ_HANDOFF` (`"<K>"` or `"none"`, §6.3).
  `-fno-req-handoff` (bit 46, masked out of `rx_info.flags`) restores the
  `abi`-60 program apart from the abi digits and that stamp's `"none"`. No
  struct offset moves, no `rx_info` member is added or changed, and no answer
  or give-up moves.
- **`rx_info.abi` was `60` (lane k82fix bumped it
  from 59, 2026-10-04: [K82] (A)+(C) — THE RARER GUARD LEADS, AND PICK'S
  NONE ANSWER PRICES SIZE, `docs/dev/lanes/k82fix_report.md`).** (A) The
  whole-window pre-check's admission (`tuning.md` §2.29) is a first-match
  row table, `none` / `one-attempt` / `dominated` / `set-leads` / `emitted`,
  listed live by `--list-axes` as axis `req-admit`; its new `set-leads` row
  (§2.40) emits the necessary SET's pick's one-byte check in FRONT of the run
  search where that byte is strictly rarer than the run's scan member (one
  PICK over the two guards, the run first, so a tie keeps the run alone), and
  on the no-DFA-scan VM route the K65 whole-set half then skips that byte.
  `-fno-req-set-lead` (bit 45, masked out of `rx_info.flags`) restores the
  `abi`-59 program apart from the abi digits. (C) `pcrec_find_pick`'s NONE
  answer is the argmin of MASS's uniform mass (cardinality), ties to the
  reader's rightmost (`findings.md` §4): under NONE (every `-e utf8`
  artifact under the default analysis) a masked run scans an EXACT position
  before a two-member pair, which moves `<PREFIX>_REQ_RUN`'s `@idx` (and
  where the scan member becomes exact, `<PREFIX>_REQ_BYTE`) on exactly those
  runs; every candidate list of bytes alone is unchanged. `<PREFIX>_REQ_WHY`
  keeps its four tokens (a `set-leads` artifact reads `"emitted"`).
  **Movers**, byte-diffed against `abi` 59 before the bump over every corpus
  pattern (auto and `--engine=vm`) and every pcrec-bench export (four compile
  configs), against a prediction recomputed from `--emit-facts` and the
  shipped ppm (`docs/dev/optloop/s4/k82fix/k82_movers.py`): (A) 7 bench
  patterns (`wild-secrets-username-password-pair`, `stack-frame`, `cls-h`,
  `cls-n-uc`, `cls-s-lc`, `cls-v`, `mod-s`, 28 artifact-configs) and 13
  corpus (pattern, flags) pairs (24 artifact-configs); (C) `alt-shared-char`
  (4) and 3 corpus patterns (6); 0 off the diagonal; `-fno-req-set-lead`
  identical to `abi` 59 on every non-(C) artifact. No struct offset moves,
  no `rx_info` member is added or changed, and no answer moves.
- **`rx_info.abi` was `59` (lane c3build bumped it
  from 58, 2026-10-03: `[OPT-LITSCAN]` S4 C3 — THE CASELESS NECESSARY RUN,
  `docs/design/litscan_s4.md` §2.3).** The necessary-run analysis
  (`src/facts/req.c`) admits, beside a single byte, a POSITION whose byte set
  is one two-member cube `(T, K)` (a caseless letter `[Ss]`, `[jk]`, an
  alternation's one-bit hull), ranks runs by information (`Σ popcount(K)`),
  floors them at `PCREC_MIN_REQ_RUN_BITS` (16) and takes an alternation's
  common head and tail as the cube hull of its branches
  (`docs/spec/tuning.md` §2.28, §2.39). On an artifact whose `req_run` is
  masked, the run pre-check's blocks (`<prefix>_reqrun`, and on the
  no-DFA-scan VM route `<prefix>_reqrun_whole`) compare the run masked
  through the run compare's new `words` row (`(<prefix>_w4(subject + cand) &
  <prefix>_w4("\337\337\337\337")) == <prefix>_w4("SELE")`; `bytes` under
  `-fno-run-overlap`), and a block whose scan member is a pair scans both
  members as two `memchr` streams leapfrogged inside its one guarded loop;
  its emitted comments name the mask; `<PREFIX>_REQ_RUN` gains a `/mask`
  suffix (§6.3); `<PREFIX>_REQ_BYTE` becomes the set's pick where the run's
  scan member is a pair; `<PREFIX>_REQ_WHY` may read `"emitted"` with
  `<PREFIX>_REQ_BYTE "none"`; the K65 whole-set half tests every set member
  the run's EXACT positions do not prove. **Movers:** an artifact's program
  moves if and only if its `req_run` fact is masked — measured at landing,
  byte-diffed against `abi` 58 over every corpus pattern (auto and
  `--engine=vm`) and every pcrec-bench export (four compile configs): 30
  corpus and 11 bench artifacts on the auto route, 0 off the diagonal; every
  other artifact differs from `abi` 58 in its abi digits alone.
  `-fno-req-run-fold` (bit 44, masked out of `rx_info.flags`) restores the
  `abi`-58 program apart from those digits. **Invariants:** every masked
  position is canonical (`T & ~K == 0`, `popcount(K)` 7 or 8; the compiler
  refuses a non-canonical position as an internal error); every search of the
  pair arm sits inside the block's `while (pos + maxk < n)` guard; a run pin
  covers exact positions only, so no masked run enters `dfa_pfs[]` (the NEXT
  rows of `cand_rows[]` since [START-TABLE] C3). No struct
  offset moves, no `rx_info` member is added or changed, and no answer moves.
- **`rx_info.abi` was `58` (lane s4build bumped it
  from 57 at the lane/r1land landing (its own branch took 56 from 55), 2026-10-03: `[OPT-LITSCAN]` S4 C1 — THE RUN COMPARE,
  `docs/design/litscan_s4.md` §1.3).** Every literal-run compare in emitted
  C (the offset-skip block's run term, which is also the run pre-check's
  compare, the VM's literal run and the island's single-child chains) is now
  written by ONE emitter function with a first-match row table
  (`src/gen/runcmp.c`, `docs/spec/tuning.md` §2.38). An EXACT run of length
  3, 5-7 or 9-15 — where gcc's constant `memcmp` decomposes into 2-4
  non-overlapping pieces — takes the `overlap` row: two overlapping
  natural-width words, the last at offset `L - W`, each loaded by a
  `static inline uint<8W>_t <prefix>_w<W>(const void *)` `memcpy` helper and
  compared against the same load of a string literal, joined by `&&` in
  offset order (`<prefix>_w4(subject + cand) == <prefix>_w4("/use") &&
  <prefix>_w4(subject + cand + 1) == <prefix>_w4("user")`). Every other
  length keeps the constant-length `memcmp` byte for byte. The helpers are
  emitted only where an artifact writes a word row, once each, ahead of
  their first use. Every artifact of both engines gains one stamp line,
  `<PREFIX>_RUN_WORDS` (§6.3, a count of the compares the overlap row
  wrote), emitted after the engine body. **Movers:** an artifact's program
  moves if and only if it writes a run compare at an overlap length; every
  other artifact differs from `abi` 55 in its abi digits and the
  `RUN_WORDS 0` line alone. `-fno-run-overlap` (bit 43, masked out of
  `rx_info.flags`) restores the `abi`-55 program apart from those two.
  **Invariants:** every word lies inside the run (`o + W <= L`), each
  word's constant is a string literal (never an integer literal of the
  target's byte order), and the compare reads exactly the bytes the caller's
  existing bounds guard covers. No struct offset moves, no `rx_info` member
  is added or changed, and no answer moves.
- **`rx_info.abi` was `57` (lane vedge bumped it from
  56 at the lane/r1land landing (its own branch took 56), 2026-10-03: [OPT-VEDGE] — THE VIEW-TOLERANT SCAN EDGE).** The scan
  edge (`docs/spec/tuning.md` §2.18) refused every counted chain that
  touched a position view, so the `(?:[a-z]{0,n})\z` whole-subject form
  walked its table once per byte on both passes. It now takes the edge in
  two more cases (§2.37, `-fno-view-edge`): on the forward and anchored
  machines, a chain whose members carry only an END (`\z`) view, which the
  scan's own stop at `n` evaluates; and on any machine, a chain whose head
  is another state's view target, which now starts one state later instead
  of being refused. Artifacts whose `<PREFIX>_DFA_SCAN_EDGE` value or edge
  set changes move (the scan-edge loop text, smaller tables); every other
  artifact differs from `abi` 56 in its abi digits alone. No struct offset
  moves, no `rx_info` member is added or changed, and no answer moves.
- **`rx_info.abi` was `56` (lane rsform bumped it
  from 55, 2026-10-03: [OPT-HYB-RESEED-FORM] A1 — A START-ANCHORED HYBRID
  STOPS CARRYING AN UNREACHABLE ADAPTIVE RETRY).** `<PREFIX>_VM_RESEED`
  gains the value `"anchored"` (§6.3, `tuning.md` §2.35): a hybrid whose
  `<PREFIX>_VM_START` is not `"unanchored"`, and whose retry was adaptive
  through `abi` 55, now takes the pre-`abi`-49 retry. Its attempt loop
  already stopped after the first attempt ([OPT-ANCHOR-VM]), so the
  adaptive tail and its two per-call locals were text no call could reach;
  they are no longer emitted, and the artifact's C equals its
  `-fno-hyb-reseed` artifact's byte for byte. Only those artifacts move
  (48 in the byte corpus under `--features all`, all formerly
  `"adaptive-dense"`); every other artifact differs from `abi` 55 in its abi
  digits alone. No struct offset moves, no `rx_info` member is added or
  changed, and no answer moves, give-ups included: the attempt set is the
  one attempt it always was.
- **`rx_info.abi` was `55` (lane k78 bumped it from
  54, 2026-09-30: K78 — A DFA ARTIFACT'S DEAD-GROUP FILL MOVES FROM THE
  SEARCH ENTRY TO ITS SUCCESS PATHS).** A DFA artifact whose
  `<PREFIX>_NCAPS` is 2 or more promises groups that no match can set
  (each is reached only through a subroutine call, or sits under a `{0}`),
  and `<prefix>_search` reports them as `PCREC_UNSET`. Through `abi` 54 that
  fill ran once at the top of `<prefix>_search`, before any answer, so a
  no-match (and `startpos > n`) returned `0` with `caps[1..NCAPS-1]`
  overwritten, against §3.1's "`caps` left untouched" (witness
  `(?(DEFINE)(?<x>\b))b(?&x)` over `"zz"`). The fill is now emitted on each
  success path, after the `caps[0]` write and before `return 1`: the
  reverse-pass and pinned unanchored forms and the per-start attempt form.
  Only DFA artifacts with `<PREFIX>_NCAPS >= 2` move; every other artifact
  differs from `abi` 54 in its abi digits alone. No struct offset moves, no
  `rx_info` member is added or changed, and no successful answer moves. The
  VM, the VM hybrid, the anchored `_match_caps` entries and the `_in`
  spellings already left `caps` untouched on every non-success return and
  are unchanged (checked by `tests/codegen/run_nomatch_caps.sh`).
- **`rx_info.abi` was `54` (lane k7980 bumped it
  from 53, 2026-09-30: K79 AND K80 — NO SELECTION READS THE PREFIX, AND THE
  SHARED BLOCK REFUSES A MIXED-ABI TRANSLATION UNIT).** (1) K80: the shared
  block's guard now carries the abi as its value, `#define PCREC_RX_ABI_H 54`,
  and the block opens with
  `#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) != 54` / `#error …`,
  so a translation unit that includes artifacts of two different abis fails
  to compile, naming the cause, where it used to compile the second against
  the first one's types. The same-abi case is unchanged: the first block
  wins and every later one is skipped. The `+ 0` makes the test refuse a
  pre-54 artifact included FIRST (its guard is defined empty); a pre-54
  artifact included AFTER a 54 one is the one order that stays silent, since
  that artifact's own `#ifndef` was written before this rule existed. (2)
  K79: the compiler emits every artifact under a fixed two-byte placeholder
  prefix and writes the caller's `-p` spelling only onto the finished text,
  so every size-predicated selection (the VM entry shape, the size term's
  trigger and ladder, the emitted-size caps) is decided on the text at a
  canonical prefix length, and the same pattern under the same options gets
  the same artifact whatever its prefix, differing only in spelling
  (`docs/spec/limits.md` "Size limits and the prefix"). At `-p rx` no byte
  moves but this digit and the guard lines; under a prefix of any other
  length, `<PREFIX>_VM_PROGRAM_BYTES` now reports the canonical length (it
  counted the prefix's bytes before), and an artifact whose selection had
  crossed a size knee because of its prefix takes the default-prefix
  selection. `rx_info.name`'s default is still the prefix. No struct offset
  moves, no `rx_info` member is added or changed, no answer moves.
- **`rx_info.abi` was `53` ([CLS-TREE] S2's review
  fixes bumped it from 52, 2026-09-30, renumbered by the manager at merge:
  THE SCAN EDGE'S RUN TEST IS THE CLASS-FORM TABLE'S ANSWER, AND THE KIT IS
  TAKEN ONLY WHERE IT IS SMALLER — D139).** A DFA scan edge no longer
  chooses its class test: it asks `src/gen/clskit.c`'s class-form table at
  the scan site and writes the answer through the emitters a VM class read
  uses (`docs/spec/tuning.md` §2.18). Three things move. (1) At EVERY
  position, a scan edge over a byte range not starting at 0 is spelled
  `(unsigned)(b - lo) <= span u`, the VM's spelling, where it read
  `(unsigned char)(b - lo) <= span`; measured over the corpus's 3,131
  compiling default-route artifacts, 79 move, by this spelling alone, and a
  VM artifact whose class is a range from 0 is `b <= hi` (1 of 3,131 on
  the forced VM). (2) At `--tune=-2`/`-1` a scan edge's ASCII case pair is
  the fold compare (`<PREFIX>_DFA_SCAN_EDGE "fold"`, §6.3) where it read a
  256-byte table. (3) At `-2`/`-1` a byte class takes its kit matcher only
  where the kit, written once per read, is smaller than the table its site
  reads (`byte-kit`, `docs/spec/tuning.md` §2.33), and a byte kit whose set
  spans 0..255 carries no always-false bound. No struct offset moves, no
  `rx_info` member is added or changed, no answer moves.
- **`rx_info.abi` was `52` ([CLS-TREE] S2's SECOND
  event bumped it from 51, 2026-09-30, renumbered by the manager at merge:
  THE DFA SCAN EDGE'S CLASS BODY JOINS THE KIT AT THE SIZE-LEANING
  POSITIONS).** Axis I (the scan edge's run-extension body) gains a third
  object, `kit`: at `--tune=-2`/`-1` an edge whose class is on the class-form
  table's `byte-kit` row (not one interval, not an ASCII fold pair) tests its
  run with a file-scope `static inline` `<prefix>_<machine>_scankit<N>` where
  it read a 256-byte table, and `<PREFIX>_DFA_SCAN_EDGE` gains the value
  `"kit"` (§6.3). DFA artifacts and VM hybrids at those positions move; no
  artifact at `0`/`+1`/`+2` moves but for this digit, no struct offset moves,
  no `rx_info` member is added or changed, no answer moves, and
  `-fno-cls-kit` restores the abi-51 body.
- **`rx_info.abi` was `51` ([CLS-TREE] S2 bumped it
  from 50, 2026-09-30, after lane uvbuild's `50`; renumbered by the manager
  at merge: THE VM'S BYTE-CLASS TESTS ARE CHOSEN BY THE KIT'S
  CLASS-FORM TABLE).** The VM's per-class byte shape classifier retired into
  `src/gen/clskit.c`'s first-match table (`docs/spec/tuning.md` §2.33 and
  §5.4's λ row). At `--tune=-2`/`-1` a byte class that is neither one
  interval nor an ASCII fold pair is tested by a `static inline`
  `<prefix>_class_kit<N>` where it read a 32-byte bitmap (unless the artifact
  takes the shared atom table), and `<PREFIX>_VM_CLS_KIT` counts those
  matchers too (§6.3). At `0`/`+1`/`+2` a byte class's test is unchanged. At
  every position, a WIDE class whose set is one interval of code points at
  or below U+00FF (`-e utf8` `[\x{e0}-\x{ff}]`) is one range compare where
  it read a `B1` table — the one default-position mover, ten triples of
  `scripts/cls_identity.py`'s 16,009 (`docs/dev/lanes/clss2_report.md`). No
  struct offset moves, no `rx_info` member is added or changed, no answer
  moves, and `-fno-cls-kit` restores the abi-50 byte tests at `-2`/`-1`.
- **`rx_info.abi` was `50` ([UTF-VALID] bumped it
  from 49, 2026-09-30: THE OPT-IN SUBJECT UTF-8 CHECK AND THE START
  ALIGNMENT, ONE EVENT, D133).** Default-off artifacts move too, by exactly
  three additions (utf_valid_design.md §6): the shared `PCREC_RX_ABI_H`
  block gains `#define PCREC_ERR_UTF (-9)` (§4); every artifact gains the
  `<PREFIX>_UTF_CHECK` stamp (§6.3) and the exported
  `<prefix>_valid_upto` entry with its declaration (§3.1.2), plus the
  `.c`-only `<prefix>_VALID_LB` macro its body reads; and a `-e utf8`
  artifact carrying a `${name}` variable has its `<prefix>_var_valid`
  re-spelled on the new entry (one validator, D133 Q7). A `-futf-check`
  artifact under `-e utf8` gains ONE precheck line at each of the entries'
  caller-position sites (§3.1); a `-fstartpos-guard=align` artifact under
  `-e utf8` carries the alignment in place of the K50 refusal and its
  `<PREFIX>_STARTPOS_GUARD` reads `"align"`. The two new bits
  (`PCREC_FORCE_UTF_CHECK`, bit 39; `PCREC_FORCE_STARTPOS_ALIGN`, bit 40) are
  CONTRACT bits: kept in `rx_info.flags`, masked only under `byte`, where
  both are inert and a `byte` artifact is byte-identical under either. No
  struct offset moves, no `rx_info` member is added, and no default
  artifact's answer moves.
- **`rx_info.abi` was `49` ([OPT-HYB-RESEED] bumped
  it from 48, 2026-09-30: THE VM HYBRID'S RETRY RE-SEEDS ADAPTIVELY).** A VM
  hybrid whose prefilter answers for a LARGER language than the pattern's (a
  lookaround or an atomic cut erased, or the `[OPT-4]` count collapse) used
  to step one character after a failed attempt wherever no MRL clamp existed,
  walking every character to the subject end once one prefilter answer
  failed. Its retry now either steps or asks the prefilter again, chosen per
  CALL from the gaps the prefilter's own answers jump (`docs/spec/tuning.md`
  §2.35, `docs/design/hyb_reseed.md`); an exact-language hybrid and a
  clamped one keep their retry byte for byte. That is an emitted-text move
  for identical inputs and so an `abi` event (D76). Every hybrid artifact
  gains ONE stamp line, `<PREFIX>_VM_RESEED` (§6.3), naming the row that
  fired; a non-hybrid artifact gains nothing but this digit. No struct
  offset moves, no `rx_info` member is added or changed, and no match,
  no-match or span moves. A GIVE-UP can: the adaptive retry runs a subset of
  the attempts the abi-48 retry ran, so a call that gave up
  (`PCREC_ERR_STEPS`/`_WORK`) under a budget can now answer, and never the
  reverse (tuning.md §2.35 states why, and why clamped hybrids are kept on
  the old retry to hold that direction). The new deny bit
  (`-fno-hyb-reseed`, `PCREC_NO_HYB_RESEED`, bit 37) is MASKED out of
  `rx_info.flags`, so under it an adaptive hybrid's program is the abi-48
  program apart from its `VM_RESEED` line and this digit
  (`docs/dev/lanes/reseed_report.md` has the identity sweep).
- **`rx_info.abi` was `48` ([CLS-TREE] S4 and
  [OPT-CLSPACK] bumped it from 47 TOGETHER, ONE event, 2026-09-30: A WIDE CLASS
  ON THE VM IS ONE DECODE AND ONE CLASS-MATCHER FUNCTION, AND MANY TABLE-READ
  BYTE CLASSES SHARE ONE ATOM TABLE).**
  - *The wide-class kit ([CLS-TREE] S4).* A class with more than one member,
    some member of which encodes deeper than one code unit (`-e utf8`:
    `\p{L}`, `[^a]`, `.`, `[é-ü]`), is tested by a VM program as
    `<prefix>_decode` followed by `<prefix>_wcls<N>`, where it was the lowered
    byte alternation (`docs/spec/tuning.md` §2.33). `<prefix>_wcls<N>` is a
    `static inline` function whose form the `--tune` class table picks (§5.4's
    λ row). `<prefix>_decode` is a new encoding-seam entry. It is `static
    inline`, DECLARED NOWHERE, and emitted ahead of the program, and the utf8
    caseless span compare calls it in place of the private decoder it carried.
    So every utf8 caseless-backreference or caseless-variable artifact moves
    too, with no answer change. Every VM artifact gains a
    `<PREFIX>_VM_CLS_KIT` line (§6.3).
    - Wide classes that refused on the VM's code cap now COMPILE: `\P{Unknown}`
      under `--engine=vm` (K55), and the K53 sets under `--engine=vm`. This is a
      refusal-set move.
    - The new deny bit (`-fno-cls-kit`, `PCREC_NO_CLS_KIT`, bit 36) is MASKED
      out of `rx_info.flags`. It denies the whole kit, the atom table below
      included.
  - *The shared atom table ([OPT-CLSPACK]).* A VM program whose byte classes
    that read a table (no singleton, range or fold-pair compare covers them)
    number at least 11, and whose byte partition has at most 64 atoms, emits ONE
    `static const unsigned char <prefix>_class_atoms[256]` and one `static
    inline` matcher `<prefix>_class_atom<N>` per such class (one load, one shift
    of a 64-bit immediate), in place of a `<prefix>_class_bitmap<N>[32]` per
    class, and the program calls the matcher where it read the bitmap
    (`docs/spec/tuning.md` §2.34). Every VM artifact gains a
    `<PREFIX>_VM_CLS_ATOMS` line (§6.3). The table is selected after the entry
    rung, so the program length the rung's knee compares is unchanged.
    - The new deny bit (`-fno-cls-pack`, `PCREC_NO_CLS_PACK`, bit 38) is MASKED
      out of `rx_info.flags`; it denies the atom row alone.
  - That is an emitted-text move for identical inputs, and so an `abi` event
    (D76). The kit moves the program and tables of the artifacts the wide-class
    route reaches; the atom row moves them ONLY on artifacts it fires for;
    every other VM artifact moves by the two stamp lines alone.
  - No struct offset moves and no `rx_info` member is added or changed.
  **VERIFIED BY AN IDENTITY SWEEP** (`scripts/cls_identity.py`, CLSIDENT_PLACEHOLDER
  triples at both encodings): under `-fno-cls-kit` every artifact equals the
  abi-47 base with the two new stamp lines removed. There are two exceptions,
  both expected. The 19 utf8 caseless span-compare artifacts move by the
  decoder's relocation. And one bench artifact's size-retry WHY text quotes a
  byte count that includes the stamp line (`docs/dev/lanes/s4build_report.md`).
  **VERIFIED BY A MOVER CENSUS** (`docs/dev/lanes/clspack_census.py`,
  `docs/dev/lanes/clspack_report.md`): the atom row's program/table movers are
  exactly the artifacts whose base emitted at least 11 bitmaps with at most 64
  atoms, by ID.
- **`rx_info.abi` was `47` ([K73] bumped it from 46,
  2026-09-29: THE OFFSET-0 START RULE IS EMITTED TEXT).** Under an encoding
  that restricts where a match may begin (`utf8`), a NULLABLE pattern's
  artifact gains one line at each caller-facing body — the unanchored DFA scan
  (the DFA artifact's entry and a VM hybrid's internal prefilter) seeks
  `search_from` past leading continuation bytes at offset 0, ENG_ATTEMPT's
  start loop skips offset 0 there, the VM seeks its first `attempt_position`,
  and the anchored match-here bodies answer `-1` (§3.1's two new bullets). A
  non-nullable pattern gains none of it, by [K50-NULLGATE]'s proof: a match
  that consumes a byte already begins on a character start. SEPARATELY, the
  DFA's `"unwrapped"` `<prefix>_match` (§3.2) gains the [K50] caller-startpos
  guard it had never carried — §3.1 promised it, and the entry answered a
  mid-character `ctx->pos` instead of refusing it; that moves every `utf8`
  DFA artifact of that form, nullable or not. ENG_ATTEMPT's existing
  `continue` gate loses a dead `start == 0 ||` clause (the backend's start
  predicate no longer carries the offset-0 exemption; the guard composes it).
  No `byte` artifact moves beyond this number, no struct offset moves, no
  `rx_info` member is added or changed, and answers move only on subjects that
  begin with a continuation byte (to libpcre2's) and on mid-character
  `ctx->pos` at the unwrapped DFA `_match` (to the promised refusal).
- **`rx_info.abi` was `46` ([UCP] U2 bumped it from
  45, 2026-09-29: A ONE-CHARACTER LOOKAROUND IS A CONTEXT NODE, AND MOVES VM
  -> DFA).** A lookaround whose body's LANGUAGE is a set of single
  byte-expressible characters (`(?<=\$)`, `(?!y)`, `(?=[ab])`, the non-atomic
  and alpha spellings) is lowered to the same context node `\b`/`\B` build
  (`docs/spec/tuning.md` §2.32, T3), which the DFA carries on its class axis
  and the VM tests as one guarded byte read — so a pattern whose only
  DFA-excluding construct was such a lookaround gets a DFA artifact for
  identical inputs, and a VM artifact that keeps its captures gets the
  one-read test in place of the lookaround sub-match. That is an emitted-text
  move for identical inputs and so an `abi` event (D76/K64). UCP `\b`/`\B`
  under `-e byte` COMPILE (the Latin-1 word set is byte-expressible), where
  they were refused — a refusal-set move. No struct offset moves, no
  `rx_info` member is added or changed, and the new deny bit
  (`-fno-ctx-node`, `PCREC_NO_CTX_NODE`, bit 35) is MASKED out of
  `rx_info.flags`, so no artifact without such a lookaround moves under it.
  **VERIFIED BY AN IDENTITY SWEEP** over every corpus `pattern` line at
  `--features all`, both encodings, base (main) vs this change, `-o -`:
  every differing artifact is either a named mover — each one reverts to the
  base artifact BYTE FOR BYTE under `-fno-ctx-node` — or one of the five UCP
  `\b`/`\B` patterns; every other artifact (every `\b`, `\B`, `(?m)^/$` and
  K50-gated utf8 machine included) is byte-identical apart from this digit.
  The movers are pinned by NAMED manifest, `tests/ucp/ctxnode_route.tsv`
  (`docs/dev/lanes/ucpu2_report.md` §4 has the counts).
- **`rx_info.abi` was `45` (module `ucp` bumped it
  from 44, 2026-09-28/29: ADDING A MODULE MOVES THE `--features all`
  SCAFFOLDING, EVEN WITH NO OTHER EMITTED CHANGE).** [UCP] U0+U1 landed
  module `ucp` (`(*UCP)`, `--ucp`, `flags u`) with the row's own default
  answer to Q-A ("no bump — no UCP-free artifact moves, and stamps keep
  the requested set") — but under `--features all` every module's name
  joins `PCREC_FEATURE_MODULES`, which is emitted SCAFFOLDING regardless
  of whether the requesting caller ever asked for the new module, and
  D76/D94 plus the `vars` precedent (`d755a9445`, abi 31 -> 32, the same
  landing that added module `vars`' own name to the same stamp) make that
  an `abi` event on its own. Manager ruling overrides Q-A. **VERIFIED BY
  DIFFING** the `abc` artifact against a scratch build of main `7a756066`
  at the same `-o` basename: the only changed line is
  `PCREC_FEATURE_MODULES`'s value gaining `,ucp` (4 bytes) — no struct
  offset moves, no `rx_info` member is added or changed, and NO ANSWER
  MOVES on any artifact, UCP-free or otherwise: a byte-for-byte identical
  compile at every other flag combination (`docs/dev/lanes/
  ucpu1_report.md` §3's identity-gate numbers, unchanged by this bump).
  `tests/codegen/run_cpset_structure.sh` CHECK 3's manifest is the
  detector — its `--features all` census reads exactly +4 on all twelve
  sample rows, the same `,vars`/+5 shape one bump before it.
- **`rx_info.abi` was `44` ([FIND-TIE] bumped it from
  43, 2026-09-28: A PICK'S DATA TIE FOLLOWS ITS NONE ORDER, IN THE RUN
  READER).** The necessary RUN's scan-member pick (`pcrec_find_run_scan_index`,
  `src/core/findings.c`) built its candidate order in the run's own
  left-to-right byte order, so a DATA tie (two or more run bytes sharing the
  argmin) went to the LEFTMOST of them while the reader's own NONE answer
  (`[OPT-REQRUN-ENC]`, abi 38, below) is the RIGHTMOST — the one reader in
  this file whose data-tie arm disagreed with its own NONE arm, matching
  `pcrec_find_set_pick`'s already-consistent `[rightmost, 255..0]` order
  instead (D126 Q4: a tie carries no information, so its answer should equal
  the question's NONE answer). Ties to the rightmost now: the candidate order
  is `[n-1, n-2, ..., 0]`, so `pcrec_find_pick`'s own earliest-candidate tie
  rule lands on the run's positional rightmost tied member. Found on the
  shipped ASCII-only `weblog`/`log` bundles under `-e utf8`, where every byte
  >= 0x80 ties at the 2 ppm floor: naming an analysis re-created
  [OPT-REQRUN-ENC]'s lead-byte defect one call down (`кириллица+` scanned
  0xD0, `[a-z]+@é` scanned 0xC3 — both fixed). **MOVES ON THE DEFAULT PATH
  TOO**, under BOTH encodings: the built-in `default` analysis declares
  `byte`-rate data, so a compile naming no analysis at all can also hit a
  data tie whenever the shipped table's own counts tie (every zero-count
  byte sits at the same 2 ppm floor) — `é@` under `byte` with no analysis
  moves `RX_REQ_BYTE` "195" -> "169" and `RX_REQ_RUN` "c3a940@0" ->
  "c3a940@1" (measured; the corpus-wide default-path mover count is owed,
  see this row's plan.md entry). `<PREFIX>_REQ_RUN`'s `@idx` and, on some
  artifacts, its WINDOW OFFSET both move with the pick (the truncation
  window is re-derived around whichever member the pick names — the window
  MASS rule itself, `pcrec_find_run_window_start`, is untouched and still
  ties leftmost, matching its own NONE). No struct offset moves and no
  `rx_info` member is added or changed; the bump moves the emitted
  `memchr`/`memcmp` TARGET BYTE and the `<PREFIX>_REQ_RUN` stamp's `@idx`
  VALUE, the same stamp-VALUE-and-emitted-text shape `[OPT-REQRUN-ENC]`
  bumped for (abi 37 -> 38, below). NO ANSWER MOVES: every byte of a
  necessary run or set is necessary regardless of which member is scanned,
  so the choice can only move a speed.
- **`rx_info.abi` was `43` ([OPT-LITSCAN] F5 bumped it
  from 42, 2026-09-28, D127: A TWO-BYTE VM LITERAL RUN KEEPS THE BYTE
  CHAIN).** S2a's one-compare form (abi 41) applied to every VM literal run
  of two or more consecutive one-byte literals; the `[B108]` read
  (`docs/dev/optloop/b108_reading.md`) measured a two-byte run's compare as
  the smallest gain in the whole L-sweep on a matching subject (0.929x) and
  a real per-call regression on a failing one (`asr-lb-fixed`, +30% — a
  two-byte compare amortizes nothing a two-node early-exit byte chain does
  not already have). The floor moves from two bytes to three, in
  `pcrec_lit_run`'s own predicate (`src/core/cpset.c`) — the one node-grain
  fact the VM's chain emission, cost walk and slot walk all share — so a
  declined two-byte pair falls through to the ordinary per-element path,
  which IS the pre-S2a byte chain; no new deny flag, `-fno-lit-run`
  unchanged. The movers are exactly the VM (or VM-hybrid) artifacts whose
  ONLY lit-run sites were two-byte runs, which now return to the byte chain
  and lose `<PREFIX>_VM_LIT_RUNS`' count for that site along with the
  compare's bytes; an artifact with no two-byte-only site is unaffected.
  `<PREFIX>_VM_PROGRAM_BYTES` moves with the program text on every mover; no
  struct offset moves and no `rx_info` member is added or changed. NO ANSWER
  AND NO GIVE-UP MOVES: the byte chain accepts exactly the bytes the compare
  accepted, and the step, work and node budgets charge what the compare
  charged (`limits.md` §3.1, narrowed to say so only where the compare
  replaces a real chain). The island's single-child trie chain is untouched
  (a different mechanism sharing only the P4 primitive).
- **`rx_info.abi` was `42` (K69 bumped it from 41,
  2026-09-27: A CALL'S NULLABILITY IS THE LEAST FIXPOINT).** A subroutine
  call is nullable iff its callee's minimum width is 0 (`u.call.minw`'s own
  least fixpoint, published by the call graph before the pattern-facts E1
  seal); the emitter used to iterate a GREATEST fixpoint of its own, which
  read a callee whose cycle escapes only through the call as nullable
  (`(a|(?1))`, whose group matches exactly `a`). A quantifier over such a
  callee (`(a|(?1))*?b`, `(?(DEFINE)(?<g>a|(?&g)))x(?&g)*?y`) no longer
  carries the empty-iteration guard it could never need: one slot, its
  `RX_SET` and its compare leave the VM program, so on exactly those
  artifacts the slot legend and `<PREFIX>_NSLOTS` lose the
  `<PREFIX>_SLOT_EMPTY_GUARD<n>` entry and `<PREFIX>_VM_PROGRAM_BYTES`,
  `<PREFIX>_FAST_TRAIL`/`<PREFIX>_FAST_FRAMES` and `rx_info.subject_ceiling`
  move with the program. A callee that really is nullable — directly, or
  through another call — keeps its guard. No stamp, declaration or `rx_info`
  member is added, no struct offset moves, the E1 `nullable` fact
  (`--emit-facts`) reads what it read, and NO ANSWER AND NO GIVE-UP MOVES:
  the guard only ever stopped an empty iteration, which a non-nullable
  callee cannot perform. MEASURED over pcrec-bench's capability patterns ×
  4 configs and every corpus pattern × {auto, `--engine=vm`}, under `byte`
  and `utf8` and eight deny sets: the movers are exactly the quantified
  left-recursive calls of `tests/recursion/k69.rxt`, and nothing else.
- **`rx_info.abi` was `41` (`[OPT-LITSCAN]` S2a
  bumped it from 40, 2026-09-27: A VM LITERAL RUN IS ONE EXACT COMPARE).**
  In a VM program, two or more consecutive one-byte literals on one
  concatenation are consumed under ONE label by one bounds check and one
  constant-length compare, `if (scan_position + L <= subject_length &&
  !memcmp(subject + scan_position, "<run>", L))`, where the per-byte chain
  wrote `L` labels; an alternation island's single-child trie chain is the
  same compare at its node's depth (`tuning.md` §2.31). The artifact gains
  `#include <string.h>` where nothing else in it needed one. EVERY VM
  artifact (a hybrid included) gains ONE stamp line, `<PREFIX>_VM_LIT_RUNS`,
  the count of run compares written (§6.3), and the new deny axis
  `-fno-lit-run` (`PCREC_NO_LIT_RUN`, bit 33, masked out of `rx_info.flags`)
  restores the abi-40 program exactly. No struct offset moves and no
  `rx_info` member is added or changed. Stamp VALUES that move with the
  program text: `<PREFIX>_VM_PROGRAM_BYTES`
  on every mover; `<PREFIX>_VM_ENTRY_SHAPE` where the smaller program now
  fits the inline entry rung (3 corpus artifacts); the byte count
  `<PREFIX>_VM_PREFILTER_LANG_WHY` quotes (1 bench pattern). MEASURED over
  pcrec-bench's capability patterns × 4 configs and every corpus pattern ×
  {auto, `--engine=vm`}, past the new stamp line: 63 bench and 1,018 corpus
  artifact-configs' programs move, each exactly an artifact whose VM program
  writes a run compare; one bench
  pattern refused by the emitted-code cap at abi 40 now compiles under
  `--engine=vm` (666,632 → 482,736 bytes of code). NO ANSWER AND NO GIVE-UP
  MOVES at the default budgets: the compare accepts exactly the bytes the
  chain accepted, and the step, work and node budgets charge what the chain
  charged (`limits.md` §3.1). The `--emit-ir` listing gains the `compare` op
  (`ir_listing.md`).
- **`rx_info.abi` was `40` (`[FINDINGS]` B1 bumped it
  from 39, 2026-09-27: THE BYTE-RATE IS DATA, EVERY ARTIFACT STAMPS WHERE ITS
  FINDINGS CAME FROM, AND OFFSET-k'S RATE READ TAKES THE GATE).** One D123-2
  abi event for three things. (1) Every artifact of both engines gains ONE
  stamp line, `<PREFIX>_FINDINGS` (§6.3), written beside the `rx_info`
  definition, and `rx_info` gains ONE APPENDED member, `findings` (§6), with
  its initializer line — no existing member's offset moves. (2) The
  byte-frequency prior the necessary-byte pick, the run's scan member and
  window, G1's density rule and the offset-k selection read is DATA now
  (`src/findings/default.rxt`, `docs/spec/findings.md`): the shipped default
  normalizes to the old table exactly, so under `-e byte` no other emitted
  byte moves — MEASURED ZERO movers under the named-lines gate over pcrec-bench's
  capability patterns and every corpus pattern, `-e byte` × {default,
  `-fno-req-byte`, `-fno-req-run`, `-fno-offset-skip`}. (3) The offset-k
  selection's rate read had NO encoding gate; it now takes the one the data
  declares, so under `-e utf8` (where the default declares nothing) it ranks
  offset sets by CARDINALITY, the MASS kind's NONE answer: the
  `<PREFIX>_DFA_PREFILTER_OFFSETS` stamp, sometimes `<PREFIX>_DFA_PREFILTER`'s
  form, and on some of those artifacts G1's `<PREFIX>_REQ_WHY`
  (`emitted`↔`dominated`) move, with the program text they name — the named
  per-artifact manifest `tests/findings/manifests/b1_utf8_movers.txt`. NO
  ANSWER AND NO GIVE-UP MOVES on any artifact: every set the offset-k
  selection ranks is necessary, so the rate chooses cost only (findings design
  §6.2a), and the utf8 movers were measured answer- and give-up-identical
  against the previous build.
- **`rx_info.abi` was `39` (`[K68]` bumped it from 38,
  2026-09-26: THE THREE BATCH-1 WHOLE-WINDOW PRE-CHECK BITS ARE MASKED OUT OF
  `rx_info.flags` LIKE EVERY OTHER TESTING/TUNING DENIAL.** `[OPTLOOP.1.impl]`
  BATCH 1 landed `PCREC_NO_VM_ANCHOR_BOUND`/`PCREC_NO_END_WINDOW`/
  `PCREC_NO_REQ_BYTE` (bits 28-30) OUTSIDE `emit_info_def`'s
  `strategy_denials` mask, deferring the omission "to their own delivery" —
  which never came until now (`docs/dev/known_issues.md` K68, found by
  pcrec-bench re-pinning I-111, fact-found by lane `bit30`). §6.3's rule for
  the mask is that `flags` records the request "with the testing/tuning
  denials masked OUT, because an axis that changes no answer must not make
  two identically-behaving artifacts differ in their reflection surface" —
  and all three bits are exactly that: each is ANSWER-IDENTITY-PRESERVING by
  its own `lib/pcrec.h` comment (the removed attempts, window or check are
  ones that would have run and failed). Unmasked, each moved five bytes of
  `rx_info.flags` on EVERY artifact including ones it cannot act on — the
  identical defect the `-fno-prefilter-collapse` comment
  (`src/gen/emit_dfa.c`) records as MEASURED on bit 19. Repro (`ec79d98c`):
  router-prefix-order (`/user|/users`) has baseline `.flags = 2`; before this
  fix it read `1073741826` under `-fno-req-byte`, `536870914` under
  `-fno-end-window`, and `268435458` under `-fno-vm-anchor-bound`. No struct
  offset moves, no `rx_info` member is added or changed, no emitted PROGRAM
  byte moves and NO ANSWER MOVES on any artifact — the fix is a reflection-
  surface correction, not a behavioural one. No pcrec-side check pinned the
  old unmasked value (confirmed by grep: no test in the tree asserted a
  numeric `rx_info.flags` value under any of the three deny flags), so this
  bump re-pins nothing beyond the abi digit itself and `tests/codegen/
  run_prechecks.sh`'s bit-30/29/28 "denial leaves no trace" sections
  (§1.2/§2.2/§3.2), which already asserted the stamp and emitted-text halves
  and needed no change.
- **`rx_info.abi` was `38` (`[OPT-REQRUN-ENC]` bumped
  it from 37, 2026-09-26: THE RUN'S `!bytekey` DECLINE IS RIGHTMOST, NOT
  LEFTMOST.** `src/opt/reqbyte.c`'s `rn_scan_index` chose the necessary
  RUN's leftmost member under every encoding its byte-frequency prior is
  not keyed to (every encoding but `byte` — today, `-e utf8` alone); it now
  returns the RIGHTMOST member instead, matching `rb_pick`'s own `!bytekey`
  fallback exactly (`docs/dev/optloop/reqrunenc_census.md`'s D77 census,
  re-measuring `reqpos_2b.md` §2.3's own ratified leftmost rule against
  pcrec-bench's O-60 finding). A `-e utf8` run is built from complete
  lowered UTF-8 code-unit sequences, so its leftmost byte is a UTF-8 LEAD
  BYTE whenever the run opens mid-character — shared by every character in
  that script block, so the emitted `memchr` stopped on nearly every byte
  of a non-Latin subject rather than the rare one the literal needs
  (measured: the run path fires on 12.0%/28.3% of the corpus/bench under
  `-e utf8`, and the old leftmost pick was a lead byte on 12.0%/20.7% of
  those). A byte-range-aware "skip lead bytes" candidate was measured
  BYTE-IDENTICAL to the rightmost one on the entire real `-e utf8`
  population (912/912 runs, bench+corpus), so the rightmost rule is taken
  with no new byte-range logic — one mechanism, two call sites. No new
  stamp, no new declaration and no `rx_info` layout move: the bump moves
  the emitted `memchr`/`memcmp` TARGET BYTE and the `<PREFIX>_REQ_RUN`
  stamp's `@offset` VALUE, on 236 of 1,167 bench and 763 of 10,818 corpus
  artifact-configs under `-e utf8` (every artifact whose run's leftmost
  member is not already its rightmost) — `reqbyte_freq_pick.md`'s
  `[OPT-FREQPICK]` precedent for a stamp-VALUE-only move, and K64fix's own
  precedent for treating a stamp-VALUE-and-emitted-text move as an `abi`
  event even with no new scaffolding. NO ANSWER MOVES: every byte of every
  run is a byte every match must contain regardless of which member is
  scanned, so the choice can only move a speed. `byte`-encoding artifacts
  are untouched BY CONSTRUCTION (`!bytekey` gates the whole candidate
  difference), which is what makes the `-e utf8` identity gates a free
  control rather than a claim resting on this note alone.
- **`rx_info.abi` was `37` (`[OPT-LITSCAN]` S1 step 6
  bumped it from 36, 2026-09-26: THE RUN PRE-CHECK IS A CALL OF THE ONE
  SEARCH BLOCK.** The necessary-run pre-check's scan loop (`[OPT-REQPOS]` tier
  2b), and `[K66]`'s whole-run loop where the route emits one, each become a
  file-scope `static inline size_t <prefix>_reqrun` / `<prefix>_reqrun_whole
  (subject, n, pos)` written by the SAME emitter as the `<prefix>_ofsskip`
  prefilter block — the run as one term at offset 0, scanned on its member at
  that member's offset (`docs/design/litscan_s1.md` §7.2 step 6) — returning
  the first position at which the run begins inside `[pos, n)`, or `n`; the
  search entry's pre-check is one line per block, `if (<prefix>_reqrun(
  subject, subject_length, search_from) >= subject_length) return 0;`. The
  standalone empty-window `return 0` goes: the block's loop guard `pos + L-1 <
  n` is false on an empty window, so its `memchr` is never reached there
  (`[K27]`'s `memchr(NULL, c, 0)` obligation, discharged by the guard). No
  stamp, no stamp VALUE, no declaration (the two helpers are `static`) and no
  `rx_info` layout moves, and NO ANSWER MOVES: the block examines exactly the
  candidate starts the loop did, `[K65]`'s `rq_set[]` half and every other
  line of the entry are unchanged. MEASURED over `docs/dev/optloop/s1/
  s1step6_movers.py`'s populations at `54bb1159`: every artifact whose base
  stamps `REQ_WHY "emitted"` with a `REQ_RUN` moves and no other does, with
  its stamps identical and, once the old loop(s) and the new block(s)/call(s)
  are removed from each side, the rest byte-identical — 236 of 1,167 bench
  artifact-configs (caps/nocaps, each also `--engine=vm`) and 763 of 10,818
  corpus ones (auto, `--engine=vm`, `-e utf8`). `-fno-req-run` still
  restores the one-byte check and `-fno-req-byte` removes the whole mechanism.
- **`rx_info.abi` was `36` (`[OPT-LITSCAN]` S1 bumped
  it from 35, 2026-09-25: A PINNED NECESSARY RUN IS VERIFIED INSIDE THE DFA
  PREFILTER, AND A PRE-CHECK THE PREFILTER DOMINATES IS NOT EMITTED.** Two
  changes, one event (`docs/design/litscan_s1.md`). (1) `[OPT-PRECHECK-ADMIT]`'s
  G1 now reads the scan byte of every `<prefix>_ofsskip` prefilter, not only
  the `memchr` forms, and elides a RUN pre-check where the prefilter's test
  verifies the whole run at its pin (`docs/spec/tuning.md` §2.29). (2) Two new
  `RX_DFA_PREFILTER` values, `"run-pinned"` and `"run-pinned-bounded"` (§6.3;
  `rx_info.prefilter` mirrors them), selected ahead of every other form where
  the run sits at a fixed offset from every match's start and the scan already
  runs on its scan member there: the offset-skip block then compares the whole
  run as one constant-length `memcmp`, and its OFFSETS may start `0*`. New
  axis bit 32, `PCREC_NO_RUN_PREFILTER` / `-fno-run-prefilter` (`tuning.md`
  §2.30), masked out of `rx_info.flags`; `-fno-offset-skip` removes the new
  rows too. Measured over the lane's census populations at the landing base
  `27a63314`: 505 of 3,583 compilable corpus artifacts and 110 of 598 bench
  artifact-configs (both auto configs) move, by id exactly the census's classes (327 corpus
  elisions with the program otherwise unchanged, 178 run-row selections;
  `docs/dev/optloop/s1/s1build_movers.txt`). No answer moves: every
  refusal the new test makes is a byte the offset walk proves every match
  carries there, and the elided pre-check's NOMATCH is still reached with no
  attempt. `-fno-run-prefilter` restores the pre-S1 artifact on every
  run-row artifact; the admission elisions have no axis.

- **`rx_info.abi` was `35` (`[K66]` bumped it from 34,
  2026-09-25: WHERE NO DFA SCAN RUNS IN FRONT, A RUN LONGER THAN ITS WINDOW IS
  COMPARED WHOLE.** `[OPT-REQPOS]` truncates a necessary run longer than
  `PCREC_MAX_REQ_RUN_EMIT` (8) to the window `[OPT-FREQPICK]`'s prior picks,
  and on a VM artifact with `<PREFIX>_VM_PREFILTER "none"` the pre-check is
  the call's only linear NO-MATCH PROOF, so a subject holding that window but
  not another slice of the run answered `PCREC_ERR_STEPS` under one prior and
  NOMATCH under another: `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` on `"e"` + 36 `a`s
  + `"~#~#~#~#"` gave up under `-e byte` (window `~#~#~#~#`) and answered
  NOMATCH under `-e utf8` (window `eeeeeeee`) — filed as `K66`. Such an
  artifact now follows the window's scan loop with a second scan loop of the
  same shape comparing the WHOLE run (`emit_req_run_rest`,
  `src/gen/emit_dfa.c`, reading `ReqRun.whole`/`whole_len`/`at`, which
  `pcrec_req_byte` now publishes beside the window it cuts from them), and
  `[K65]`'s `rq_set[]` block drops every byte of the whole run. No new stamp,
  no stamp VALUE (`<PREFIX>_REQ_RUN` still names the window), no declaration
  and no layout change: the bump moves emitted PROGRAM TEXT only, on 12 of
  6,642 measured artifact-configs (2 of 256 bench configs +
  10 of 6,386 corpus configs over 3,193 distinct patterns x `--features
  all`/`+ --engine=vm`), every one `VM_PREFILTER "none"` with a run of 9 to
  11 bytes, each gaining the 13-line compare and losing its 6-line `rq_set`
  block; 2 are on the AUTO route. **The FOURTH bump in this list whose change
  moves an ANSWER**, and again only in the direction of REPAIR: a give-up
  becoming a NOMATCH, never the reverse. `-fno-req-run` and `-fno-req-byte`
  still remove it. `docs/spec/tuning.md` §2.29 states the rule.

- **`rx_info.abi` was `34` (`[K65]` bumped it from 33,
  2026-09-25: THE PRE-CHECK TESTS THE WHOLE NECESSARY SET WHERE NO DFA SCAN
  RUNS IN FRONT.** On a VM artifact with `<PREFIX>_VM_PREFILTER "none"` —
  every backreference- or linked-call-bearing pattern on the auto route and
  every `--engine=vm` build without `-fprefilter` — the necessary-byte
  pre-check is the call's only linear NO-MATCH PROOF, and it tested one
  member of the necessary set, the one `[OPT-FREQPICK]`'s prior picked. So a
  hostile subject lacking a DIFFERENT member answered `PCREC_ERR_STEPS` (or
  `PCREC_ERR_WORK`) under one pick and NOMATCH under another:
  `(x?)([a-z]+)+Z.@\1` on 31 `a`s + `"Zb"` gave up under `-e byte` (pick
  `Z`) and answered NOMATCH under `-e utf8` (pick `@`) — filed as `K65`.
  After the byte check or the run check, such an artifact now emits one
  6-line block — a `static const unsigned char rq_set[]` of every necessary
  byte the first half did not test, and a loop `memchr`-ing each — any
  absent member answering NOMATCH (`emit_req_set_rest`,
  `src/gen/emit_dfa.c`, reading a new `Job.req_set` that `pcrec_req_byte`
  publishes from the walk it already ran). No new stamp, no stamp VALUE, no
  declaration and no layout change: the bump moves emitted PROGRAM TEXT
  only, on 452 of 6,642 measured artifact-configs (30 of 256 bench configs
  + 422 of 6,386 corpus configs over 3,193 distinct patterns x `--features
  all`/`+ --engine=vm`), every one a pure 6-line insertion, every one
  `VM_PREFILTER "none"`, none a DFA artifact or a hybrid; 48 are on the AUTO
  route. **The THIRD bump in this list whose change moves an ANSWER**, and
  again only in the direction of REPAIR: a give-up becoming a NOMATCH, never
  the reverse. `-fno-req-byte` still removes the whole mechanism.
  `docs/spec/tuning.md` §2.29 states the rule.

- **`rx_info.abi` was `33` (`[K64]` bumped it from 32,
  2026-09-25: G2'S ONE-ATTEMPT ADMISSION RULE GAINS A LINEARITY CONJUNCT.**
  `[OPT-PRECHECK-ADMIT]`'s G2 rule (`abi` 31) declined the necessary-byte
  pre-check wherever the VM's own route tries at most one start position,
  arguing the attempt reads no more than the check would scan — true of a
  DFA and false of a backtracking VM program, where the pre-check is also
  the NO-MATCH PROOF bounding the call: a framed, unguarded, `^`-anchored
  forced-VM one-attempt program (`^([a-zA-Z0-9._%+-]+)+@` over a long run
  with no `@`) spent its whole step budget and gave up (`PCREC_ERR_STEPS`)
  where PCRE2 and the fixed compiler answer NOMATCH — filed as `K64`.
  `req_route_one_attempt` (`src/gen/emit_dfa.c`) now additionally requires
  the one attempt to be LINEAR: an EXACT-language hybrid DFA in front (an
  exact match is itself the no-match proof; a count-collapsed superset is
  not), or a frameless VM program, which cannot backtrack at all — a new
  `Job.vm_frameless` field (`src/core/internal.h`), published by
  `vm_plan_entry` (`src/gen/emit_vm.c`) beside its own derivation of
  `has_push`. No new stamp, no declaration and no layout change: the bump
  moves a STAMP VALUE (`<PREFIX>_REQ_WHY` `"one-attempt"` -> `"emitted"`)
  and the emitted PROGRAM TEXT it names, on the population the narrowing
  gives its pre-check back to — 176 of 6,634 measured artifact-configs (256
  bench configs + 6,378 corpus configs over 3,189 distinct patterns x
  `--features all`/`+ --engine=vm`), every one `VM_FRAMELESS 0` /
  `VM_PREFILTER "none"` / `VM_START` anchored-or-`gstart`, gaining either
  the 5-line byte check or the 16-line run check (plus
  `#include <string.h>` where nothing else in the body calls `memchr`), and
  none of them a hybrid — including 41 on the AUTO route (backreference and
  linked-call VM artifacts, which decline the hybrid outright and so have
  the K64 hazard too). **This is the SECOND bump in this list (after
  `[K50]`'s `23 -> 24`) whose change moves an ANSWER rather than only a
  speed or a byte count**, and only in the direction of REPAIR: a give-up
  becoming a NOMATCH within the same step budget, never the reverse.
  `-fno-req-byte` still removes the whole mechanism on both routes.
  `docs/spec/tuning.md` §2.29's G2 paragraph and Answer-identity paragraph
  are corrected in the same change.

- **`rx_info.abi` was `32` (`[VAR]` bumped it from 31,
  2026-09-23: THE CALLER-VARIABLE SURFACE.** Module `vars` gives a pattern
  `${name}`, whose bytes the CALLER supplies per call, and the surface it
  needs lands in one event. On EVERY artifact of BOTH engines: a new
  fixed-literal ABI type `rx_var {name, p, len}` in the shared
  `PCREC_RX_ABI_H` block; TWO fields appended to `rx_ctx`
  (`const rx_var *vars; size_t nvars;`), so no existing member's offset moves
  and — the point of putting them there — **`rx_matchfn`'s signature is
  UNTOUCHED and a var-bearing artifact's `<prefix>_match` is still an
  `rx_matchfn` byte for byte**; `#define PCREC_ERR_UNSET_VAR (-8)`, the THIRD
  below-the-floor code and `PCREC_ERR_STARTPOS`'s shape exactly (a caller
  REFUSAL: nothing attempted, `caps` untouched); and TWO members appended to
  `rx_info` (`const char *const *vars; int nvars;`), the variable-NAME table on
  `rx_info.groups`' model. **A var-free AND backreference-free artifact's whole
  change is the `abi` digit (a same-length substitution) and those two
  `rx_info` initializer lines — MEASURED at exactly +34 bytes on four witnesses spanning 13 KB to
  762 KB at the same `-o` basename, six changed lines each and no emitted
  program byte among them.** On a VAR-BEARING artifact only: `<PREFIX>_NVARS`
  and one internal `<PREFIX>_VAR_<NAME>` index macro per name (the ARTIFACT's
  own index into its names table, never something a caller writes — variables
  are passed BY NAME, because an index is meaningless across separately
  compiled artifacts); a `<prefix>_var_names[]` table `rx_info.vars` points
  at; a `<prefix>_vars_resolve` static that scans the caller's array ONCE PER
  CALL and evaluates each distinct expansion; **no new compare entry at all** — the
  encoding seam's existing pair is GENERALISED and RENAMED
  `$_span_match`/`$_span_match_caseless`, taking the reference side as a
  POINTER AND A LENGTH instead of a pair of offsets, so ONE pair serves a
  backreference (which passes `subject + start, end - start`) and a variable
  (which passes the caller's resolved value); under a multi-byte encoding a
  fifth entry `$_var_valid` joins them. **Every artifact carrying a
  backreference therefore moves too**: its residual's NAME and signature
  change, which is emitted text and is part of this bump rather than a
  separate one; and a trailing
  `const rx_var *vars, size_t nvars` pair on `<prefix>_search` and its `_in`
  siblings — which are NOT `rx_ctx`-shaped and so cannot read the ctx,
  `<prefix>_search_in`'s own trailing-descriptor precedent (D18, §10.2), with
  the descriptor staying LAST. NO ANSWER MOVES on any artifact that mentions
  no variable, and a var-bearing pattern could not be compiled at all before
  this bump. `docs/spec/vars.md` is the module's own contract page.

- **`rx_info.abi` was `31` (`[OPT-PRECHECK-ADMIT]`
  bumped it from 30, D119 / the `[OPTLOOP.1]` ledger reading §6, ratified
  2026-09-23: ADMITTING THE WHOLE-WINDOW PRE-CHECKS BY COST.** EVERY artifact
  of BOTH engines gains one shared-prologue stamp line, `<PREFIX>_REQ_WHY` — a
  closed four-token set (`"emitted"`, `"none"`, `"one-attempt"`,
  `"dominated"`) saying whether the artifact acted on what `abi` 29's and 30's
  analyses found, and if not which of two measured declines applies. It is a
  SEPARATE stamp rather than a wider `<PREFIX>_REQ_BYTE` value, in
  `<PREFIX>_ENGINE` / `<PREFIX>_ENGINE_WHY`'s shape: the `REQ_BYTE`/`REQ_RUN`
  pair keeps naming what the ANALYSIS found, so neither value space moves and
  no existing reader of either changes. On the two declined populations the
  artifact LOSES emitted text rather than gaining it — the three-line `memchr`
  pre-check (or `abi` 30's scan loop) goes, and with it the
  `#include <string.h>` on an artifact whose body calls no other `memchr`.
  The two rules are `tuning.md` §2.29's: G2 declines where the search route
  tries ONE start position (the DFA's `start_max` rows reading the literal `0`
  or `search_from`; the VM's `<PREFIX>_VM_START "anchored"`/`"gstart"`), which
  is the rule the candidate-start prefilter already applies to itself; G1
  declines where the artifact's own single-byte `memchr` prefilter already
  scans a byte at least as rare. No struct offset moves, no `rx_info` member
  is added or changed, and NO ANSWER MOVES — a declined pre-check is a check
  not run, and it could only ever have returned the answer the engine below it
  then returns anyway, which is why both of this change's sabotage rows are
  structural. `-fno-req-byte` still removes the whole mechanism.

- **`rx_info.abi` was `30` (`[OPTLOOP.2]` batch 2
  bumped it from 29, D119: THE NECESSARY LITERAL RUN AND ITS SCAN PICK.** One
  bump for two mechanisms, which land as one event because their populations
  overlap and two bumps would re-pin the same manifests twice
  (`docs/design/reqpos_2b.md` §7 item 5). EVERY artifact of BOTH engines gains
  one shared-prologue stamp line, `<PREFIX>_REQ_RUN` — the run's bytes as
  lowercase hex, then `@`, then the scanned member's index within them, or the
  token `"none"` at `L < 2`, the same `"none"`-member shape its two siblings
  have and for the same reason. On the population the run analysis reaches
  (18.6% of pcrec's own `.rxt` corpus) the three-line `memchr` pre-check
  `abi` 29 described is REPLACED by a scan loop of about ten lines: one
  `memchr` for the run's rarest member, one constant-length `memcmp` of the
  run at each hit, and a window guard of one or two conjuncts depending on
  whether the scanned member is the run's first byte. On the DISJOINT
  population where the pattern has a necessary byte and no run, the emitted
  text is that same three-line check with, on 13.60% of the corpus, a
  DIFFERENT decimal in it: `[OPT-FREQPICK]` chooses the member of the
  necessary set that a subject is least likely to contain rather than PCRE2's
  rightmost one, and PCRE2's rule survives as the tiebreak. No struct offset
  moves, no `rx_info` member is added or changed, and NO ANSWER MOVES: every
  byte of every run is a byte every match must contain, so both the wider
  check and the different pick can move a speed and nothing else.
  `-fno-req-run` restores `abi` 29's emitted text on the run population
  exactly, and `-fno-req-byte` restores the pre-batch-1 text on both
  (`tuning.md` §2.27-§2.28). The flags enum in `lib/pcrec.h` is respelled
  `1ull << N` in the same change, because `PCREC_NO_REQ_RUN` is bit 31 and
  `1u << 32` is undefined behaviour; no VALUE moved and `pcrec_options.flags`
  was already `uint64_t`.

- **`rx_info.abi` was `29` (`[OPTLOOP.1]` batch 1
  bumped it from 28, D119: THE THREE WHOLE-WINDOW PRE-CHECKS.** One bump for
  three mechanisms, because they are one emitted-scaffolding event on one
  landing. EVERY artifact of BOTH engines gains two shared-prologue stamp
  lines — `<PREFIX>_END_WINDOW` and `<PREFIX>_REQ_BYTE`, each a string
  carrying a number or the token `"none"`, since `0` is a legal value of both
  facts and no number is free to mean "declined" — and every VM artifact
  gains a third, `<PREFIX>_VM_START`. On the populations the three analyses
  actually reach, the artifact additionally gains emitted PROGRAM text: a
  `const size_t attempt_max = search_from;` declaration with the attempt
  loop's existing continue test rewritten to read it ([OPT-ANCHOR-VM]); a
  two-line clamp raising `search_from` to `subject_length - W` at both
  engines' search entries ([OPT-ENDWIN]); and a three-line `memchr`
  pre-check at those same two places, plus a `#include <string.h>` on a VM
  artifact that had none ([OPT-REQBYTE]). No struct offset moves, no
  `rx_info` member is added or changed, and NO ANSWER MOVES on any of the
  three — two of them remove only attempts the artifact would have run and
  FAILED, and the third moves a search's start position only within a window
  it has proved no match can begin before. Each of `-fno-vm-anchor-bound`,
  `-fno-end-window` and `-fno-req-byte` restores the pre-mechanism text on its
  own population exactly (`tuning.md` §2.25-§2.27).
  The bump before it was [REL-1.4], from 27 (D115: THE VERSION STAMP. The essential generated-by line —
  already the one line D112 keeps under every `-fcomments` setting —
  now also names `PCREC_VERSION` (`lib/pcrec.h`, a semver string
  independent of `abi`: it versions the tool, `abi` versions one
  artifact's emitted scaffolding) beside the abi digit: `/* Generated by
  pcrec 0.1.0-beta (abi 28). Pattern: ... */`. `pcrec --version` prints
  the same string (`docs/spec/cli.md`). No struct offset moves, no
  `rx_info` member is added or changed, and no answer moves at all — the
  comment TEXT is the only thing that changed, on every artifact of both
  engines regardless of `-fcomments`, because the line it rides is the
  ESSENTIAL class the switch never removes.)
  The bump before that was [EMIT-VERB]:
  THE EMITTED-COMMENT AXIS. A default artifact no longer carries
  its NON-ESSENTIAL prose — every comment LINE leaves every artifact of
  both engines except the generated-by/pattern-echo provenance line and
  the shared `PCREC_RX_ABI_H` type block's doc-comments, which are the
  ESSENTIAL class D112 defines; `-fcomments` restores the rest, and both
  bits are masked out of `rx_info.flags`. Measured 44.2 % of a default
  artifact's source bytes over the 3,517 compiling corpus patterns (DFA
  45.6 %, VM 43.1 %). It is the first bump that REMOVES emitted text, and
  the only one whose whole population is bytes the C compiler discards:
  the OBJECT FILE is byte-identical under both settings on 3,517 of 3,517
  corpus artifacts, the comment-EXCLUDED source size is identical, and
  every emitted `#define` is identical — so no cap, no refusal and no
  answer moves. See `docs/spec/tuning.md` §2.24.
  **Same-day rider (D112 item 2):** the ESSENTIAL generated-by line ALSO
  gained the abi digit (`/* Generated by pcrec (abi 27). Pattern: ... */`),
  riding this still-open bump rather than taking a second one (D76/D94's
  addendum shape) — `rx_info.abi`'s VALUE, every struct offset and every
  answer are unchanged; the comment TEXT is the only thing that moved.
  The bump before it was [OPT-DIAL]:
  THE SPEED-VS-SIZE DIAL. Every artifact of both engines gains
  exactly one line in the shared prologue, `#define <PREFIX>_TUNE
  "<token>"` — a closed five-token selection stamp, 23-28 bytes by token.
  Nothing else moves at the default position `balanced`: STRUCTURAL rather
  than measured, because every cell of that row in `src/core/tune.c` is
  the em-dash sentinel and its deny mask is empty, so there is no code
  path on which a `balanced` build can differ from one built with no
  `--tune` flag at all. A non-default position may move far more, which is
  the dial's own point, but no struct offset moves, no `rx_info` member is
  added or changed, and no answer moves at any position — that invariance
  is the dial's own acceptance criterion (`src/core/tune.c`'s own header),
  not a claim this document is first to make. `25` was
  [PORTFIX], which bumped it from 24: A CLANG-COMPATIBILITY LABEL FIX.
  Every scan-edge-bearing DFA machine
  (or VM-hybrid inlined prefilter), of either direction, gains a trailing
  `;` on its `scan_views` and `scan_edge` labels — closing a label-
  immediately-followed-by-a-declaration shape (`view_decl`'s
  `<dir>_view_state` assignment) that gcc accepts as a long-standing
  `-std=gnu11` extension and clang 21 rejects under `-Werror` as
  `-Wc23-extensions` (docs/dev/lanes/anchtriage_report.md §1). An artifact
  with no scan edge at all gains nothing, exactly as `-fno-scan-edge`
  already excuses it from every earlier scan-edge bump, and no answer moves
  on either compiler. The VM PROGRAM REGION is unmoved — both labels live
  inside `pcrec_emit_dfa_engine`, above the region a VM hybrid inlines its
  prefilter through, or in a file with no such region at all on a
  non-hybrid DFA artifact — so `tests/codegen/run_recursion_identity.sh`'s
  comparison (A) needs no new deny-axis IFF, [OPT-EDGE] STEP 1's own abi-
  18-19 bump's precedent. `24` was [K50], which bumped it from 23:
  CANDIDATE MATCH STARTS ARE THE ENCODING'S CHARACTER BOUNDARIES. Every
  artifact of both engines gains one line in the shared ABI block —
  `#define PCREC_ERR_STARTPOS (-7)`, §4's second below-the-floor code — and
  NO `byte` artifact moves in any other way. Under `utf8` the unanchored
  machine itself moves (the boundary gate is a real automaton state), an
  `ENG_ATTEMPT` artifact's start loop gains a boundary `continue`, and every
  artifact's entries gain the caller-startpos guard §3.1 documents. It is
  the first bump in this list carried by a change that moves an ANSWER —
  K50 was a wrong-answer defect, not a shape change — so unlike every deny
  flag before it, `-fno-startpos-guard` restores only the CALLER-side
  semantics and not identity. `23` was [FORM-CHAR] STEP 1: the VM's
  ASCII-FOLD CLASS TEST — a two-member pool class that
  is an ASCII fold pair (differing only in bit 0x20, both letters, what
  D23's parse-time caseless folding produces) tests as
  `(byte | 0x20) == lower` and its 32-byte `class_bitmap` table is not
  emitted; every VM artifact gains a `<PREFIX>_VM_CLS_FOLDS` line whatever
  its value (§6.3); the VM PROGRAM REGION moves on exactly the fold-bearing
  population, the second change ever to do so, and
  `tests/codegen/run_recursion_identity.sh`'s comparison (A) carries the
  fold as a second deny-axis IFF on the island's own terms; no answer moves
  — `-fno-cls-fold` sweeps the axis, `docs/spec/tuning.md` §2.22 is the
  contract. `22` was [CC-DIFF] STEP 2's, which bumped it
  from 21: the VM ENTRY SHAPE — two stamps on every VM artifact,
  `<PREFIX>_VM_ENTRY_SHAPE` and `<PREFIX>_VM_PROGRAM_BYTES`, and the entry
  chain's shape at rungs `shared`/`forward`; the VM program region is unmoved;
  `_VM_PROGRAM_BYTES` deliberately costs STEP 1's "framed artifacts are
  byte-identical" property, see §6.3. 21 was [OPT-EDGE] STEP 1.1, which bumped
  it from 20: the scan-edge ENTRY DISPATCH — the entry-seed check generalised
  to `is_stop && !is_dead`, precondition (8) requiring the seed AND a
  prefilter reseed — so the entry block's shape moved on every edge-bearing
  artifact and nothing else. 20 was [DD-13b.W1.3]'s COMPOSITION bump from 17;
  18 and 19 were spent by other changes merging ahead of it.)** On a COMPOSED artifact (`pcrec --source`) `groups[]` gains
  rows the target pattern did not declare, each carrying a non-NULL `ref`
  naming the definition it came from; the array's sort key gains a leading
  SCOPE term, so `nnames` counts the caller-scope prefix and §6's algorithm
  is correct unchanged while `nentries` counts the whole array; `ngroups`
  reads the primary pattern's own count; and a delivering call site retains
  what its callee matched. **Every one of these is invisible on a
  non-composed compile**, which is why no artifact built without `--source`
  moved a byte. See "Composition" above.

  **The `19` it replaces was [OPT-EDGE] STEP 1's** (taken from 18): on any DFA
  machine carrying a SCAN EDGE the edge heads are renumbered to the machine's
  TOP rows, the machine emits one extra accessor `<prefix>_<m>_is_stop`
  (folded to the constant `1` where every state is a head), the loop's ONE
  per-iteration state test now answers "dead OR a head", and the per-edge
  `if (state == HEAD && …)` blocks move off the generic path onto an edge
  path reached only from that test. So an edge-bearing machine's emitted
  state NUMBERS move, and an artifact with NO scan edge — which includes
  every `-fno-scan-edge` build — is byte-identical to abi 17. A new
  precondition (8) also refuses a head that any SEED family names, which
  costs 11 of 2,539 corpus artifacts an edge (10 of them all of theirs, every
  one a `\b`/`\B` pattern) and moves those artifacts'
  `<PREFIX>_DFA_SCAN_EDGE` to `"none"`. No answer moves on any of it;
  `docs/spec/tuning.md` §2.18 is the contract.

  **The `18` it replaces was [ENG-ISL] STEP 1's, the VM's ALTERNATION ISLAND
  (bumped from 17 the same day).** A flat alternation whose
  whole subtree matches a finite set of literal byte strings is lowered as a
  TRIE over those strings' bytes — a byte compare at a node with one child, a
  `switch` at a node with several, one try site per node where an alternative
  ends — instead of `vm_alt`'s chain of one resume frame per untried branch.
  Every VM artifact gains a `<PREFIX>_VM_ALT_ISLANDS` line whatever its value
  (§6.3), and on any artifact that takes an island the emitted PROGRAM changes
  shape. **It is the first bump whose change reaches the VM program region
  itself**: every earlier one moved stamps, an entry chain, DFA tables or a
  prefilter, all of which sit above `goto <prefix>_L0;`. No answer moves —
  `-fno-alt-island` sweeps the axis — and
  `tests/codegen/run_recursion_identity.sh`'s comparison (A) now carries an
  IFF for it: a moved region is excused only where the artifact's own
  `<PREFIX>_VM_ALT_ISLANDS` reads > 0, and an artifact stamping one whose
  region did NOT move is a failure.

  The `17` it replaces was [CC-DIFF] STEP 1's TWO EMITTED-CODE SPELLINGS,
  taken as ONE event because both are emitter changes on the same landing.

  **(a) The VM entry chain's helpers carry
  `static inline __attribute__((always_inline))` on a FRAMELESS artifact.**
  The eight statics `<prefix>_run_state_bind`, `_run_state_init`,
  `_reset_for_next_attempt`, `_match_anchored`, `_report_captures`,
  `<prefix>_search_run`, `<prefix>_match_run` and `<prefix>_match_caps_run`
  gain the attribute if and only if `<PREFIX>_VM_FRAMELESS` is `1`. A FRAMED
  artifact (`<PREFIX>_VM_FRAMELESS 0`) is byte-identical to what abi 16
  emitted, this stamp aside. The gate is forced from two directions at once:
  gcc REFUSES `always_inline` on a function containing a computed goto, and a
  framed artifact is exactly the one that has one; and [CC-DIFF] STEP 0
  measured no benefit on framed cells and a mild regression on one. On a
  frameless artifact the effect is that `<prefix>_search_run` and
  `<prefix>_match_anchored` have no out-of-line copy left (`nm` lists neither),
  and `<prefix>_search`'s 152-byte frame, its four run-state binding stores
  and its `-fstack-protector-strong` canary go away with them.

  **(b) A DFA transition or accept table whose cells are ALL EQUAL is not
  emitted, and its accessor returns the constant.** `<m>_next_state` and
  `<m>_is_accepting` are affected; the accessor loses only its table
  parameter, keeping the state and class parameters so that a call site's
  `subject[pos++]` is still evaluated. `<PREFIX>_DFA_UNIFORM_FOLDS` counts
  what was folded, and is the supported way to observe it. `<PREFIX>_DFA_TABLE`
  keeps naming the ENCODING that was SELECTED — the selection still happens
  and still fixes the folded constant's value — so a `"premultiplied"`
  artifact reading `4` here carries no folded table at all.

  **No answer moves on either half**, which the corpus, the axis sweep and the
  bench's own subject sets are what sweep. `16` was [OPT-5] STEP 2, which bumped
  it from 15 with the START-PINNED SEARCH — `search_form` APPENDED to this
  struct and a `<PREFIX>_DFA_START` stamp on every artifact containing a DFA
  scan, plus, on every artifact whose forward machine's start state accepts
  unconditionally, the deletion of the whole REVERSE machine from
  `<prefix>_search`: its tables, its accessor block and its scan loop, with
  `<PREFIX>_DFA_TABLE` and `<PREFIX>_DFA_SCAN_EDGE` no longer folding a
  machine the artifact does not contain. [OPT-VMFL]'s
  `<PREFIX>_VM_FRAMELESS` rides the same bump rather than taking one of its
  own, adding one stamp line to every VM artifact and every hybrid. No
  answer moves; `15` was
  [DD-13b.W1.2], which bumped
  it from 14 by APPENDING `name` and `nentries` to this struct — two
  initializer lines on every artifact of both engines, no struct offset
  moved, no emitted program byte moved and no stamp VALUE changed; `14`
  was [CC-CLANG], which wrapped `emit_search_head`'s `noclone` line in an
  `__has_attribute` guard (three lines gained on every DFA and VM-hybrid
  artifact; gcc still emits the attribute, since it has it) and omitted
  the fail label's pop-and-resume `goto *` dispatch entirely on a FRAMELESS
  VM artifact — no `RX_PUSH` and no `RX_CALL` site anywhere in the program,
  e.g. `[a-z]{0,4096}` --engine=vm — where that dispatch was unreachable
  already and its `goto *` with no address-of-label expression in the
  function is what clang refuses and gcc accepts; `13` was [OPT-5] adding
  `<PREFIX>_DFA_SCAN_EDGE` (§6.3) to every artifact and,
  on any DFA scan whose machine carries a counted class run, by replacing
  that run's states with one in-loop scan block — the first bump to move a
  MACHINE and not only emitted text, `12` was [OPT-4]'s
  `<PREFIX>_VM_PREFILTER_LANG` and its companion
  `<PREFIX>_VM_PREFILTER_LANG_WHY` on every VM HYBRID and no other
  artifact kind, `11` [ART-SIZE]'s four size
  stamps `_UNROLL_K`/`_UNROLL_K_WHY`/`_MAX_EMIT_CODE_BYTES`/
  `_MAX_EMIT_BYTES`, `10` [ENG-ABS]'s anchored match-here form, `9`
  [OPT-K]'s offset-k candidate-start skip, `8` [ENG-FORM]'s opaque DFA
  state token and `7` [OPT-3]'s pre-multiplied DFA transition table),
  and is not yet a compatibility promise.** Being pre-v1 (§9), it is a layout version and
  nothing more: do not build version negotiation on it until v1 declares
  what a bump means. It moved `2` → `3` at [DD-14.FB] (§10.4), which
  inserted the four sizing fields after `subject_ceiling` and therefore
  moved every following offset — which is exactly what this member exists
  to announce. It moved `3` → `4` at [DD-13] (§6.3), which added the DFA
  artifact's three selection stamps. **THAT SECOND BUMP MOVED NO STRUCT
  OFFSET**, and the number still had to move: D76 rules `abi` the version
  of the EMITTED SCAFFOLDING as a whole, not of `struct rx_info` alone,
  because the thing it protects is
  `tests/codegen/run_recursion_identity.sh`'s whole-file comparison (B) —
  which a new `#define` line breaks exactly as a moved offset would. A
  bump is therefore always paired with a re-pin of that comparison to the
  change's last `src`-touching commit, in the same change.

  It moved `4` → `5` at [OPT-1], the two-tier default entries — the first
  bump at which NO DFA artifact's bytes moved at all, since the tier is
  emitted only by the VM path. And it moved `5` → `6` at [DD-13c], which is
  the first bump that is BOTH kinds of event at once: emitted scaffolding
  (the `"empty"` scan value, and the two `_DFA_*` lines every VM hybrid
  gained) AND a real struct change — `scan` and `prefilter`, appended at the
  END so that, unlike [DD-14.FB]'s insertion, **no existing member's offset
  moves**. It is also the mirror image of [OPT-1]'s: that bump reached VM
  artifacts only, this one reaches both kinds.

  **`abi` 7 → 8, [ENG-FORM] (2026-08-26, D82): the DFA scan's state becomes
  an OPAQUE TOKEN with an accessor block, and a caller sees exactly two
  things change.** (i) Every DFA artifact — and every VM hybrid, whose
  inlined `<prefix>_prefilter` is the same emitter's output — now carries, at
  FILE SCOPE immediately above its search function, one block per machine of
  the form `typedef <int|unsigned> <prefix>_<forward|reverse>_state;`
  followed by up to seven `static inline` accessors (`_step`, `_is_dead`,
  `_accepts`, `_accepts_class`, `_row`, `_view_live`, `_view_take`), and the
  scan loop below is written against them instead of indexing the tables
  itself. (ii) Several table and loop COMMENTS were unified across the
  forward/reverse pair. **NOTHING A CALLER CAN CALL, LINK, OR READ AS A
  VALUE MOVED**: the four entry points, the three `_in` entries, `struct
  rx_info` and all of its fields, `RX_NCAPS`, the buffer surface, and every
  `<PREFIX>_*` stamp — `RX_ENGINE`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`,
  `RX_DFA_TABLE` and their value sets — are unchanged, and
  `RX_DFA_TABLE`/`RX_DFA_PREFILTER` are now read directly off the emitter's
  chosen representation object rather than re-derived, so a stamp can no
  longer disagree with the loop it describes. The accessor names are
  prefix-derived like every other emitted identifier and are therefore
  subject to §1's prefix rules; they are NOT part of the frozen ABI block.
  Measured alongside the bump: the emitted matcher's `-O2` instruction
  sequence is unchanged on the hot loop's carried dependency chain, and every
  answer is byte-identical over the corpus and over 81,821 answer lines from
  the comparative bench's subjects.

  **`abi` 13 → 14, [CC-CLANG] (2026-08-31): clang-compatibility, and no
  answer moves.** Two independent scaffolding changes, bundled because both
  exist only so the SAME artifact gcc already accepts also compiles under
  clang, and neither is a caller-visible surface change. (i)
  `__attribute__((noclone))` (§6.3 K24's own fix) is now wrapped in an
  `__has_attribute` guard — three lines every DFA and VM-hybrid artifact
  gains, and gcc's emitted attribute is unaffected because gcc has it; the
  guard names no compiler, only the feature. (ii) A VM artifact whose
  program contains no `RX_PUSH` and no `RX_CALL` site at all (a
  counter-rung-only body — `[a-z]{0,4096}` --engine=vm is the probed
  witness) no longer emits the fail label's pop-and-resume `goto *`
  dispatch: `run->resume_depth` can never leave 0 in such a program, so that
  block was unreachable already, and its indirect jump with no
  address-of-label expression anywhere else in the function is exactly what
  clang's "indirect goto in function with no address-of-label expressions"
  refuses and gcc accepts. Every artifact that pushes at least one resume
  frame is byte-identical on this axis. Nothing a caller can call, link, or
  read as a value moved, and no answer changed on any corpus or bench
  pattern.

