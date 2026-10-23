# Critic round "iter" -- lens SLOT (slot tracing, ruling check, siblings, general form)

Reviewer note: the brief named `/tmp/claude-1001/crit-iter/slot.md` as the lens file, but it did not
exist at start. I worked from the lead's message (ONE QUESTION + RULING CHECK + STANDING QUESTIONS)
and write my output here, at `<lens>.md`. Review tree: worktrees/crit-iter @ 588714855 (BASE 02f357b39).
Scratch: /tmp/claude-1001/crit-iter/slot/.

## Findings

### SLOT-1 -- the iterator's VM storage binding is a second spelling of `forward`'s OWN/OWN_TIERED/EMPTY/CALLER emitters
CONFIRMED (text). Severity: maintenance. Effort: small-medium (abi event: emitted text moves). Blast radius: every VM artifact's iterator.
- `src/gen/emit_iter.c:271-330` (`emit_step_own`) writes the own-storage binding for OWN, OWN_TIERED (fast tier,
  `if (r != FRAMES) return r; TIER_NOTE(); return __step_deep(...)`, plus a `noinline` deep tier) and EMPTY.
  `emit_iter.c:353-361` (`emit_one`) writes the caller-storage bind (`run_state_bind(&run, b->frames, b->nframes, b->trail, b->ntrail)`).
- These are `fwd_own` (`src/gen/emit_comb.c:156-277`) and `fwd_in`'s CALLER arm (`emit_comb.c:85-112`) re-spelled.
  `fwd_own`'s own header (emit_comb.c ~118-140) says why it exists: the three entries "were already three
  near-copies ... adding the tier to each in place ... is the parallel-mechanism shape Frank's standing direction
  rules out, and it is the shape sabotage row S-FB2 exists for". The iterator adds a fourth copy of exactly that
  escalation, outside `fwd_sigs[]`, and S-FB2 does not reach it.
- The selection of the binding is also duplicated: `en->fwd_entries ? PCREC_FWD_EMPTY : pl->tiered ?
  PCREC_FWD_OWN_TIERED : PCREC_FWD_OWN` at `src/gen/emit_vm.c:13795` (entries) and again at `emit_vm.c:13935`
  (`vm_emit_iterator`).
- Guide: architecture.md "One table per slot: no private copy of a declared mechanism"; "Build the general form;
  no parallel mechanisms". `PcrecIterText.own` reuses the enum (the table's LABEL) but not the emitter -- the
  "keying rules on a label" variant of narrowing.
- Fix shape: compute `PcrecFwd own` once in `vm_emit_entries`, hand it to `PcrecIterText`, and make the step a
  `fwd_sigs[]` row (ret/name/params/runargs are already that table's columns) so `__step_own`/`__step_deep` are
  `fwd_own`'s output. (EMPTY differs in spelling only: step_own binds `(void*)0,0` directly where `fwd_own`
  forwards through `<p>_no_buffers`; same answer.)

### SLOT-2 -- the retry R is the anchored match-here body, copied in both engines (and the VM copy has already drifted)
CONFIRMED (text). Severity: maintenance. Effort: medium. Blast radius: every reports_empty artifact's retry text.
- VM: `vm_emit_retry` (`src/gen/emit_vm.c:13887-13921`) is the third copy of the anchored attempt beside
  `vm_emit_match_run`/`vm_emit_match_caps_run` (`emit_vm.c:13609-13716`): ctx setup, start-zero, run_state_init,
  vars resolve, `_match_anchored`, `_report_captures`. The design note says so itself ("`<prefix>_match_caps_run`'s
  body with `run->notempty` set", findall_iter.md as-built ~l.1748).
  Drift already present: `_match_caps_run` resolves the variables BEFORE the offset-0 rule (K129, emit_vm.c:13701-13703,
  "above the offset-0 rule's NOMATCH answer, in the search entry's own order"); `__retry` emits start-zero first and
  resolves after `run_state_init` (emit_vm.c:13908-13913). Not observable today (q is always a character start and
  the previous step already resolved the variables), which is exactly how copies drift unseen.
- DFA: `dfa_dir_retry` (`src/gen/emit_dfa.c:13936-13955`) is `dfa_dir_anchored` (`emit_dfa.c:9137-9155`) with the
  names and banner changed; `pcrec_emit_dfa_retry` (`emit_dfa.c:13963-13989`) re-spells the untagged half of
  `emit_anchored_match_def` (tables, `scan_position`/`last_accept_position`, `emit_scan_loop`, the -1 test).
- The general form is already in this change: `_search` was split into caller-position prologue + body (`__find`)
  so `_next` could run the body with no prologue. The anchored entries did not get the same split; the retry got a
  copy instead. With `_match_caps_run = prologue ; __match_body(run)` the VM retry is `__match_body` with notempty
  armed, and the DFA anchored body parameterized by (machine, DfaDir) serves both `_match` VERIFY and the retry.
- Guide: "Build the general form; no parallel mechanisms" ("Two callers of one mechanism is fine; two mechanisms is not").

### SLOT-3 -- the retry-strategy choice (none / dfa-root / vm-guard) is an if-chain over five sites with three different gates
CONFIRMED (text; the gate disagreement is reachable only through a library entry request that omits `next`).
Severity: maintenance / observability. Effort: small-medium. Blast radius: compile.c, emit_dfa.c, emit_vm.c, the stamp.
- Sites and their gates:
  1. `src/core/compile.c:353-363` `build_notempty_dfa`: `fit.chosen == DFA && !part && reports_empty` -- NOT gated on
     `next` being emitted, and NOT routed through the path derivation's NEEDS half that gates the sibling machine
     (`build_anchored_dfa`, compile.c:307: `pcrec_cand_finish_needs(cx, CAND_MA)`, plus its deny `-fno-anchored-dfa`).
  2. `src/gen/emit_dfa.c:15729-15736`: `emitted(NEXT) && retry_ok`.
  3. `src/gen/emit_vm.c:11864`, `:12617`, `:12935` (the `notempty` field, its init, the accept guard): `reports_empty` only.
  4. `src/gen/emit_vm.c:13930-13944` `vm_emit_iterator`: `emitted(NEXT) && reports_empty`.
  5. the stamp, `emit_dfa.c:15006-15010`: its own ternary, `!emitted(NEXT) || !reports_empty ? "none" : retry_ok ?
     "dfa-root" : "vm-guard"` -- "vm-guard" is "anything that is not retry_ok", not the VM row's verdict.
- Consequence: an artifact built under a request without `next` stamps `"none"` while its VM text still carries the
  `notempty` field and accept guard, and its DFA build still pays the retry machine (see SLOT-4). The stamp re-derives
  the choice rather than printing the winner (the stamp-catalogue rule in emit_dfa.c's DD-13 comment: "read off the
  same derivations the loop is emitted from, never a second copy of their conditions").
- Guide: "Decisions are declared tables, not if-chains" (organized/observable, winner printable); "One table per
  slot" (machine builds are declared by FINISH rows' NEEDS). Fix shape: a three-row retry table (predicate over
  next-emitted, reports_empty, engine; action names the machine it needs, feeding NEEDS); the emitters and the stamp
  read its winner.

### SLOT-4 -- the mandatory retry machine shares the subset budget whether or not anything iterates
SUSPECTED. Severity: speed (engine/finish-form movers). Effort: small to confirm. Blast radius: reports_empty DFA patterns near the subset cap.
- `build_notempty_dfa` runs on every reports_empty DFA artifact, before the optional anchored machine, and is
  MANDATORY (compile.c:343-352): its overflow is the DFA engine's. So a pattern whose `dfa`+`rdfa` fit but
  `dfa`+`rdfa`+`nedfa` do not now leaves the DFA (to the VM) for every caller, including `_search`-only callers;
  and one near the cap can now lose `adfa` (the `_match` `unwrapped` VERIFY form) to the retry machine.
- Would confirm: a census over the nullable/`\K` corpus patterns compiled by BASE and SUBJECT comparing
  `RX_ENGINE`, `RX_ENGINE_SEL` and the `_match` finish-form stamp; plus `--max-dfa-states`-lowered runs to find the
  margin. Not run (a >50-compile sweep is box-queue work; I am read-only). The design accepted the cost implicitly
  (no measurement named); per "Build under measurement", it should name the census.

### SLOT-5 -- the entry table misdeclares the iterator's call graph
CONFIRMED (text + emitted code). Severity: maintenance (no answer effect found). Effort: small. Blast radius: entries.c, part_layout callers.
- `pr_next_vm` (`src/gen/entries.c:194-198`) declares NEXT -> SEARCH_RUN. `_next` never calls `<p>_search_run`: it
  calls `<p>__find` and `<p>__retry` (emitted `${v}x` utf8, scratch slot/v.c:498 `rx__find(...)` in `rx__step`;
  `rx_search_run` is called only by the `_search` rungs). The VM `__find` and both engines' `__retry` have no row.
- Two different functions are named `<p>__find`: on the DFA it is `PCREC_ENTRY_FIND` (a row, entries.c:209/216); on
  the VM it is an unlisted static. Same name, two models.
- `<prefix>_next_n` is an exported, spec-listed entry (the branch spec, entry list, rx_info field 31) with no PcrecEntry and
  no row: it rides NEXT's row (emit_iter.c:381-383 "no entry of their own"), so no request can export one without
  the other and `part_callers_rank` (part_layout.c:389) counts NEXT as one caller while the emitter writes four
  holders of the step (`_next`, `_next_n`, `__one_local`, `__step_deep`).
- Guide: "One table per slot" (narrowing: two caller-visible entries mapped onto one row); "A row checks its own
  contract" (give every row a population). Today P3 (`callers == 1`) is the only reader of the count and NEXT makes
  it >=2 either way, so I found no layout or answer effect.

### SLOT-6 -- `EntryMode` is an unread column, and its one new value already mislabels a row
CONFIRMED (text). Severity: maintenance. Effort: trivial.
- entries.c:55-58: EM_ITER is "recorded for the kit's mode fact ... nothing reads it". The DFA FIND rows
  (entries.c:209, :216) are EM_ITER, but `<p>_search` runs FIND one-shot on every call. Guide: "Build under
  measurement" (a column ahead of its reader) and "Decisions are declared tables" (observable).

### SLOT-7 -- the third member of "bytes no length decision reads" has arrived; unification was deferred to a fourth
CONFIRMED (text). Severity: maintenance. Effort: medium (pure refactor, zero movers expected). Blast radius: sb.c, internal.h, compile.c, emit_compound.c.
- Members: the SIMD bracket (`simd_guarded`/`simd_size`), the part-layout marks (`layout_bytes`, [ENTRY-TABLE] E1),
  and now the scaffold bracket (`scaf_guarded`/`scaf_size`) plus a fourth shape, `pcrec_sb_scaffold_putc`'s
  mid-line single byte (sb.c:268-279). `pcrec_sb_len_decide` (sb.c:303-310) subtracts all three.
- The as-built note (findall_iter.md ~l.1758) files the "shared bracket with a kind field" for "the next third
  member" -- but `layout_bytes` already makes scaffold the third. Each member is hand-carried at seven sites:
  `StrBuf`, `pcrec_sb_splice`, `len_decide`, `size_decide`, `PcrecPartFacts` (internal.h:7931-7935),
  `part_splice` (emit_compound.c:107-110), compile.c:3367-3368.
- Guide: "Notice siblings of a decision family" (~three members -> propose the unified table).

### SLOT-8 -- stale slot text
CONFIRMED. Severity: doc. Effort: trivial.
- `src/gen/emit_iter.c:1-2`: "as cut by the I1 ruling: no batch ABI, no `next_n`" -- the file emits `_next_n`.
- docs/design/findall_iter.md §2.4 table (l.637) assigns `__var_valid` to "`__enter`'s once-per-iterator variable
  check (§3.7)"; the as-built note (l.1755) and the code say variable resolution stays per search (emitted v.c:317,
  `rx_vars_resolve` inside `rx__find`, run every step).

### SLOT-9 -- dead residual-site plumbing left behind by the twins
CONFIRMED (text). Severity: maintenance. Effort: trivial.
- `pcrec_enc_emit_defs` (enc.c:307-325) now `(void)`s `sites`/`nsites`, but `emit_residual_defs` still computes
  `residual_sites(cx, enc, false, &ns)` to pass them (emit_dfa.c:3579-3583). The static `enc_emit_defs`' out-of-line
  arm and its `drop`/`stat` parameters are dead (its one caller, enc.c:334, passes `true, ..., 0, 0`). A future
  out-of-line site fails loudly in `pcrec_enc_emit_twins` (good), so this is only clutter.

### SLOT-10 -- ruling check: `<PREFIX>_ITER_RETRY`'s values name mechanisms (D174)
CONFIRMED (text). Severity: doc / contract. Effort: trivial (rename before landing) or a ruling.
- Values `"dfa-root"` / `"vm-guard"` (the branch spec's stamp section, emit_dfa.c:15006-15010) name an engine and a
  construction. The caller sees the same behaviour in both (an empty match retried at its position). D174 binds
  "a stamp" and "new names ... from 2026-10-22"; the stamp was named in I1 (2026-10-21) but has not shipped (the
  branch has not landed), so "already shipped stay" does not cover it. Either name by behaviour (`"none"`/`"retry"`)
  or the manager rules this an engineering-observability stamp exempt like `_DFA_SCAN`; today it is neither.

## Ruling check (the rulings the work relies on)
- **D171** (fixed setup cost accepted; dense cells still gated): consistent with the guide's "A design states its
  goals" -- the dense-cell parity is a checkable goal and the accepted cells are named. Its "batch cell is off" is
  superseded by D175; D171's gloss points at I4 but carries no forward pointer to D175 (minor doc).
- **D173** (subst as an independent element over an rx SHAPE, driven by the iterators): served -- `rx_nextfn` /
  `rx_nextnfn` are shared shapes and `rx_info.next`/`.next_n` reach them generically. Caveat: caller storage is bound
  only through the per-prefix `<prefix>_iter_buffers` setter (`rx_iter.bufs` is `const void *`), so a generic
  element cannot supply storage to an artifact it did not compile against; it gets the artifact's own. Acceptable
  under D77 until a subst lane names a storage need.
- **D174**: see SLOT-10 (the one new caller-facing name that does not describe behaviour). `PCREC_ERR_ITER`,
  `rx_iter`, the setters: fine.
- **D175** (drop RX_FOREACH, keep `_next_n`): measured (job 599), satisfies "Build under measurement". The coupling
  it leaves -- `next_n` with no entry row of its own -- is SLOT-5.
- **Design-note rulings**: "variable resolution stays per search" (as-built, trigger U-I2-6 = a measured share)
  holds under "Build under measurement"; "scaffold bracket second beside RQ-3, unify at the third member" is
  miscounted (SLOT-7); "`__find` always_inline except the attempt route's label-table body" is a private layout rule
  (`find_body_shared`, emit_dfa.c:1963) beside the part-layout table, admitted in-code ("the part table's class
  `find` has no subject yet") -- acceptable as a declared deferral, but it is the second engine-private layout rule
  for the same slot (the VM `__find` inherits `en->ai`, emit_vm.c:13158).

## Standing questions
**Siblings of a family.**
- Retry strategy (SLOT-3) is a new decision family member written as conditions; with the entry shapes and the
  FINISH rows already tabled, it belongs as rows.
- Machines built per need: `adfa` is NEEDS-derived from FINISH rows; `nedfa` is hand-gated (SLOT-3 item 1). Same family.
- Length-excluded byte classes (SLOT-7): three members.
- `reports_empty` is a correct sibling of `nullable`/`empty_masks` in widths.c, declared in facts.def (one table)
  and E1-cross-checked against `nullable`. The E3 `width` fact (kset.c, UNANCH-only, no `\K` view) cannot serve it.
- Version numbers: `PCREC_ITER_LAYOUT` (emit_iter.c:45) is a second layout counter beside `PCREC_ARTIFACT_ABI`.
  Any rx_iter layout change is also an abi event, so the abi ritual's "every reader of the number" grep must also
  find this one; worth a line in coding.md §3.1's site list.

**General form + unlocks.**
- General form: every entry = caller-position prologue ; body, and the iterator = bind (prologue once) ; loop (body,
  advance, retry), where the retry is the anchored body under a NOTEMPTY_ATSTART root. This change built the split for
  `_search` only.
- Unlock 1 (SLOT-2's split for the anchored entries): retry = anchored body with notempty, both engines; and a
  "sticky"/anchored iteration (PCRE2_ANCHORED global, a tokenizer loop: each match must begin where the last ended)
  costs one STEP variant. Trigger: a tokenizer/lexer user or a subst lane (D173) asking for contiguous matches.
- Unlock 2 (the notempty root is a general matcher option): `Dfa.notempty` + the VM `notempty` guard are
  PCRE2_NOTEMPTY_ATSTART; with a NOTEMPTY (any position) variant they become one-shot match options. Trigger: a
  caller or subst request for NOTEMPTY semantics, or a PCRE2-compat census row that needs them.
- Unlock 3 (bind slot as a resolved-state record): hoisting variable resolution (U-I2-6) and any other per-iterator
  invariant (the `-futf-check` of variable values) into bind. Trigger: as filed, a measured resolution share on a
  var-bearing find-all cell.
- Unlock 4 (SLOT-7): one excluded-bytes record with a kind field; trigger: fired now (third member).
- Unlock 5 (SLOT-1): the step as a `fwd_sigs[]` row makes any future entry with own storage (subst's driver, a
  `_next`-style `_match` iterator) a row, not a fifth copy of the tier escalation.

## PROBED-AND-HELD
- One search body: `_search` and `_next` share `<p>__find` in both engines (emit_comb.c:539-553 DFA/compound,
  emit_vm.c:12527-12546 + 13151-13163 VM); no second start-scan in emitted text for 6 patterns (`a*`, `^a*|b$`
  split compound, `${v}x` utf8, `(a)\1`, `(a|b)*c\1|x*`, `\Ga*|b$`).
- One advance rule: `<p>__step` (emit_iter.c:212-259) is the only find-all advance in emitted code; it and the
  compound controller both call the `__next_pos` twin; `pcrec_emit_main` (emit_dfa.c:15287) has no loop.
- Bind checks use the one prologue emitter (`pcrec_emit_startpos_guard`, emit_iter.c:116-138), so codes and order are
  `_search`'s.
- The notempty machine uses the one DFA builder (`pcrec_build_min_dfa` with `Dfa.notempty` as an input) and the memo
  keys on it (dfamemo.c:75-80, :158); dfa.c's change is a start-root flag, not a second construction.
- Split compounds with a nullable floor arm get the retry (`^a*|b$`, `\Ga*|b$` with --features all: `RX_COMPOUND
  "split"`, `RX_ITER_RETRY "dfa-root"`, `__retry` present).
- `next`/`next_n` declarations and definitions follow the entry linkage mechanism (`ENTRY_DECL`,
  `pcrec_entry_storage(cx, PCREC_ENTRY_NEXT)`), and `rx_info.next`/`.next_n` are set exactly where NEXT is emitted.
- VM `__find` layout vs BASE on a large artifact (`(a|b)*c\1|x*`): `_search_run` inlines into `rx_search`, `__find`
  stays one static -- the same call depth BASE had through `rx_search_run` (gcc -O2, nm/objdump).
- `reports_empty` analysis (widths.c:392-517): the `\K`-tail algebra, `A_REP`, `A_CALL` (conservative when any
  `\K` exists) and lookaround handling are sound in the direction that matters; E1 cross-check `nullable =>
  reports_empty` present (facts.c:302).
