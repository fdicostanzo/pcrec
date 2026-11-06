# FIXIND findings

(fix-induced lens; subject docs/design/vlookbehind.md rev 4 @2ef0d1818, build tree 80341284e at
worktrees/crit-vlb4, build/pcrec + build/libpcrec.a. Scratch artifacts, reader and sweeps:
/var/tmp/pcrec-pcrec/scratch/crit-vlb4/fixind/{art,src,defs.txt,blocks_all.tsv}.)

## Findings

### FIXIND-1 — DD12a(i)'s derivation cannot key the UCP caseless compare by entry; rule (b) as written goes red on a corpus pair. CONFIRMED (design; effort S; blast: DD12a(i) only)
§5.6 "DD12a(i) reads region (1) FROM THE SEAM", item 3 (design.md:1462-1476 of 2ef0d1818).
- The byte backend has TWO entries that define `$_span_match_caseless` (SPAN_CASELESS 1u<<2 and
  SPAN_CASELESS_UCP 1u<<7; src/enc/enc_byte.c:350-355), and the UCP entry's helper symbols
  `span_ci_fold` / `span_ci_fold_pairs` are the SAME names utf8's SPAN_CASELESS defines
  (enc_utf8.c:166-200). Measured with a reader linked against build/libpcrec.a
  (src/dump.c over `pcrec_enc_backend_{byte,utf8}.entries`, the rule applied by src/rule.py):
  byte UCP -> {span_ci_fold(, span_match_caseless(} + enc.c's table; utf8 SPAN_CASELESS ->
  {span_ci_fold_pairs[, span_ci_fold(, span_match_caseless(}. So "symbol -> entry" is not a
  function within byte, and "counter KEY = the entry" is undefined for `span_match_caseless`.
- Rule (b) ("presence per entry; one-sided only where the reader lists the entry in that backend
  alone") on `(*UCP)(?i)(a+)\1` (tests/backrefs/caseless_ucp.rxt:262; ASCII pattern and subjects,
  so it is DD12a(i) population block 718 of 4,843): byte side = {SPAN_CASELESS_UCP}, utf8 side =
  {SPAN_CASELESS, DECODE}. UCP (byte-only) and DECODE (utf8-only) are admitted; SPAN_CASELESS is in
  BOTH backends, so its utf8-only presence is NOT admitted -> red. The UCP entry is a SUBSTITUTE
  for SPAN_CASELESS (enc.h:230-241: "in the mask INSTEAD of it"), which the rule has no word for.
- Pre-existing, same pair: today's SIG_RE has `static\s+unsigned` and `static\s+const\s+unsigned`
  but not `... unsigned char`, so the byte UCP heads `static const unsigned char
  rx_span_ci_fold_pairs[][2] =` (written by enc.c:133) and `static unsigned char
  rx_span_ci_fold(` are NOT excised. Emulated with the file's own excise()/comments_only()/
  diff_is_data_only()/form_moved() (src/pairdiff.py over run_encoding_checks.sh:424-1834):
  widens False, comments_only False, data_only False, offender = the fold-table line, moved [] ->
  STRICT-bucket divergence in a full sweep (ENC_MAX_BLOCKS=0). Rev 4's "after ANY return-type
  tokens" head matcher repairs the excision half; the keying/rule-(b) half above is new.
- Fix: compare per SYMBOL set (key = symbol, entry only for the floor), or have the reader print a
  `stands-for` column (UCP -> SPAN_CASELESS) that rule (b) reads.

### FIXIND-2 — rule (a)'s derived floor is red on every default-slice run: the byte-only UCP entry has no explicit witness. CONFIRMED (check correctness; effort XS; blast: DD12a(i) default runs)
§5.6 item 3 ("rule (a)'s floor: every entry the reader lists is reached at least once ... on the
side(s) that carry it") and item 4 (only `(?<=a{1,2})x` joins the explicit list).
- The reader lists SPAN_CASELESS_UCP for byte. DD12a(i) compiles plain `--pattern` (no `--ucp`),
  so only a `(*UCP)` verb reaches it. Rebuilding the population with the script's own extractor
  (lines 95-163): exactly ONE block reaches it, index 718 `(*UCP)(?i)(a+)\1`; the default
  ENC_MAX_BLOCKS is 250 (run_encoding_checks.sh:70). The explicit witnesses
  (`a*`, `(?i)(?<=a)(b)\1x`, `(?<=a)(b)\1x`, `^${v}$`, `(?i)(?<=ab)(b)\1x`; line 1531) reach
  SPAN, SPAN_CASELESS, DECODE, BACK_STEP, VAR_VALID, never UCP.
- Fix: add `(*UCP)(?i)(a)\1x` (or similar) to the explicit list in the same change — the design's
  own "a new entry cannot pass DD12a(i) without a witness" applied to the existing entries.

### FIXIND-3 — more hand lists of seam entry names than §5.6 / U6 name; two exact population guards move. CONFIRMED (maintenance; effort S; blast: partlayout census, [M5-SEAM] guards)
§5.6 "Other readers of the new entry", §6 U6.
- tests/partlayout/writers.tsv:29 row A4 is the hand CLASS MAP of every `static inline` writer:
  `^P_(span_match|span_match_caseless|span_ci_fold|span_ci_decode|back_step|decode|var_valid|bref_match|bref_match_caseless)$`;
  its header: "a function that carries an attribute and matches no row ... the census FAILS ...
  never discovered". `rx_fwd_step` matches no row (A6's `(forward|reverse|...)_step` does not
  match `fwd`). Latent today: run_partlayout.py's census runs over the FROZEN
  tests/partlayout/population.txt (395 lines, 87 lookbehinds, none `range`), so it stays green
  until the population is re-derived or a range cell is added; then red. (A4 is already stale:
  span_ci_decode, bref_match*.)
- run_partlayout.py:538 sec_seam's name regex (`span_match\w*|back_step|decode|bref_match\w*`)
  and its pattern list: fwd_step's body is never checked for label tables (coverage gap, green).
- run_codegen_tests.sh:1606 `resid_backdecl -ne 7` (EXACT): `residlbrange` (back_step:3) and its
  `-e utf8` twin make it 9; the design does not state the edit (the build finds it at once).
- run_codegen_tests.sh:1665-1673 [LOSS-REVIEW c1] -fPIC nm arm: EXACT 7 fixtures, none a `range`
  lookbehind, so "fwd_step is never exported" is unchecked at object level even after
  INLINE_RESID gains it (the reach grep at 1650 still passes on the old fixtures).
- (Checked, safe: run_dfa_uniform_fold.sh:120's `_step(` matcher is keyed on a `_state` return
  type after [SEAMBUILD] hit exactly this with back_step; `size_t rx_fwd_step(` does not match.)

### FIXIND-4 — `size_t <p>_lb_count;` is the only frame local with no initializer. SUSPECTED (build/-Werror; effort XS)
§5.6 "`K_i`'s declaration and name": `pcrec_vm_stmt_frame` declares `size_t <p>_lb_count;`.
Every existing frame local is initialized (vm_stmt.c:1188 `span_cursor = 0`, 1218-1220 the rv
locals `= 0`/`-1`, revdet arrays `{0}`), and the matcher is a computed-goto function built
`-Wall -Wextra -Werror` by the harness. If any address-taken label (an RX_PUSH target) sits between
the write at `L_b_i` and a read, gcc's -Wmaybe-uninitialized may fire at -O2. Confirm: compile
`residlbrange` (both encodings) at -O2/-O3 with the harness flags. Fix: `= 0`, the precedent.

### FIXIND-5 — W-low's plant, as re-spelled, is a 4-5-site edit; the matrix carries at most 2. SUSPECTED (maintenance; effort S)
§7 W-low: plant = a second `VmLocalKind` member + its `vm_local_name` arm + a frame declaration +
the write via VK_LSET + the exhaustion test reading it (vm_stmt.h, vm_stmt.c x2, emit_vm.c x2).
Sabotage rows are SAB_BEFORE/SAB_AFTER with an optional SAB_*2 (41 of 1,102 rows). Either say
W-low is a one-off scratch-tree plant, or use a 1-edit equivalent with the same semantics
(untrailed LO): e.g. `vm_set_line` (vm_stmt.c:283-284) rendering a plain
`slot_values[...] = v;` for `SLOT_LB_LO*` names. The answer cell and the "RX_SET of SLOT_LB_LO<j>"
codegen detector both see either form.

### FIXIND-6 — `pcrec_enc_entry_symbols` re-states enc.c's UCP special case. CONFIRMED (design; effort S; low)
§5.6 item 1 ("plus what enc.c itself emits beside a row ... It sits beside the code that emits those
symbols, so the list cannot drift"). The table is emitted by `if (t->id == PCREC_ENCE_SPAN_CASELESS_UCP)
enc_emit_latin1_fold_table(...)` (enc.c:156-157); the new function must carry a SECOND copy of that
condition. Beside is not the same as derived: a change to the emission conditional does not move
the symbol list. General form: one per-row "side emission" hook (or a symbol sink in
`pcrec_enc_emit_text`) read by both.

## PROBED-AND-HELD
- Next free bit: ids in use 1u<<0..1u<<7 (enc.h:153-241); 1u<<8 is free; `unsigned` everywhere.
  No emitted text, stamp, listing or test reads a mask's numeric value (grep of enc_mask / PCREC_ENCE_
  over src cli lib tests tools); entries.c:345 `entry_enc` lists only the three OUTLINE caller
  entries. Every loop over a backend's rows (mask_close, emit_decls, enc_emit_inline_defs,
  enc_is_twinned, emit_twins, emit_defs, residual_sites, has_entry, engine_callable) is gated on the
  mask or skips inline rows, so an artifact without the bit cannot move. Measured: back_step present
  only in the 2 lookbehind artifacts of 22 probe artifacts. Note: the new row's `decls` must be ""
  (the loops' sentinel is `t->decls == NULL`; a NULL would silently truncate utf8's table before
  VAR_VALID) — enc.h:138 states it for inline rows, the design does not repeat it.
- engine_callable: readers are emit_vm.c's three consults for their own ids (7391, 8828, 8889); none
  enumerates; adding a `true` row changes no existing reader. enc.h's reason for next_pos (the
  automaton's self-loop) does not apply to a lookbehind candidate step (no automaton
  representation, back_step's case) — the distinction holds; emit_vm.c:13342 already records that
  the next_pos rationale fails at the VM retry loop.
- Item (4): `(?<=a|bc)x` stamps `RX_VM_PROGRAM_BYTES 2628ULL` under byte and utf8, also with
  -fno-comments, though utf8's back_step body is ~25 lines longer; program bytes are the body buffer
  only (`pcrec_vm_stmt_program_bytes` = `pcrec_sb_len_decide(sb->b)`, vm_stmt.c:1047), and the inline
  defs are emitted ahead by `pcrec_emit_residual_inline`. A stamp regression routes the pair to
  DD12a(i)'s K50 form class, where the manifest's unlisted-member guard (1962-1968) turns it red.
- Item (5): enc_emit_inline_defs wraps decls_doc and defs_doc in PCREC_CMT_NONESSENTIAL
  (enc.c:160-169); `-fno-comments` lbalt: 0 back-step doc lines under both encodings. Caveat:
  comments INSIDE `defs` survive (utf8 back_step keeps 5); the proposed fwd_step bodies have none.
- Symbol rule over today's 13 rows (6 byte, 7 utf8): derived names = SIG_RE's names minus
  span_ci_decode, exactly; plus non-symbols the rule correctly skips (`#define $_BACK_STEP_NONE`,
  identical text both sides; `@site@` lines; `#define rx_VALID_LB` from emit_dfa.c, a pattern fact,
  identical). Twins `<p>__<sym>` and forwarders are covered by the head matcher's `__` form.
  One-backend entries are exactly var_valid + decode (utf8) and SPAN_CASELESS_UCP (byte).
- Deleting `span_ci_decode` from SIG_RE: no backend defines it; the only other reader,
  run_wclass_census.sh:191, asserts its ABSENCE independently. Safe.
- K49 via the mask: VM artifacts carry next_pos (always in mask): forwarder `rx_next_pos` and static
  twin `rx__next_pos` (lbalt utf8 lines 627/189). `#include`-ing the artifact makes the static
  inline member callable; today's driver links with `extern` — the switch is mechanical. Floor 2
  per encoding is achievable once the witness compiles (today it is refused: "variable-length
  lookbehind is not implemented").
- Sweep (src/sweep.c): utf8 fwd_step body vs next_pos(s,b,pos) vs rev 3's advance text with @N=b vs
  min(next_pos(s,n,pos), b), every pos < b <= n, with reads instrumented to [pos+1, b):
  (a) K49's alphabet {41,C2,E0,F0,80,BF,FF}, lengths 0-5: 19,608 strings, 278,327 cells, 0
  disagreements on all three, 52,444 non-trivial (!= pos+1), 0 out-of-range reads;
  (b) all 256 bytes, lengths 0-3: 16,843,009 strings, 100,860,160 cells, 0 disagreements,
  12,599,296 non-trivial, 0 out-of-range reads.
- New record vocabulary: `u.seek` and VmLocalKind are read only by `vm_r_seek` (vm_stmt.c:453) and
  `vm_local_name` (473) switches, which have no `default` (a missing arm warns under -Wswitch /
  make strict) and the builders; no listing, dump, cost, record check or frame sizing reads them
  (grep over src tests tools). `vm_rec` memsets, so `byloc`/`x` default to 0/false at the six
  existing `pcrec_vm_b_seek` sites (4731, 5073, 5223, 5894, 7198, 7510); VmLocal's positional
  literals are untouched (no field added). S133's anchor (7198, 4-space) and S123's (7510,
  12-space) are each unique today.
- W13's plant is one argument in the one-line VSK_STEP_CHAR render (a one-edit row). W14 (i):
  [M5-SEAM]'s `inline_entries` + `calls_in_bodies` read `static inline` heads and body tokens, so
  dropping the bit and rendering `+= 1` reads 0 against `fwd_step:1` -> red; (ii) K49's tie -> red.
- DD12a(ii): `sigs_of`'s `(size_t|ptrdiff_t) [A-Za-z]+_(...)\(` matches forwarders/inline heads,
  not twins; a reader-supplied name list including fwd_step/valid_upto works unchanged.
- W-low's codegen detector is readable: slots render `RX_SET(RX_SLOT_<NAME>, ...)` today
  (lbalt.c:186-187), given §5.1b's name arm.

- Tree drift: 2ef0d1818..80341284e touches only tests/memfn/* and one S1079 row; no file this
  lens cites (src/enc, src/gen, tests/codegen, tests/partlayout, tests/mech S133/S123) differs.

## Standing questions
- Sibling family: YES. `next_pos`, `advance`, `fwd_step` are three spellings of "the next boundary";
  K50's `start_cls`/`start_guard` is a fourth spelling of the boundary PREDICATE, and
  `valid_upto`'s raw step-back a fifth (backward, PCRE2's walk). At three members the forest rule
  applies: one declared per-backend boundary predicate from which next_pos/fwd_step bodies are
  generated (advance too, if the byte "predicate is constant" case renders `@P++;` so no byte
  artifact moves). Not for stage 1; trigger: a third backend, or any edit to one spelling.
- General form + unlocks: the enc_entry_list reader is the general answer for EVERY hand list of
  seam names (SIG_RE, TWINNED, sigs_of, partlayout writers.tsv A4 and sec_seam, the c1 nm list;
  INLINE_RESID stays hand-written by its own R32 ruling). Unlock: writers.tsv A4 generated from the
  reader; trigger: the next seam entry. A second unlock: an engine-callable character step lets
  other VM constructs step one character without an automaton (A-REV's reverse DFA in a VM
  lookbehind, a VM `\X`); trigger: the first such client.
