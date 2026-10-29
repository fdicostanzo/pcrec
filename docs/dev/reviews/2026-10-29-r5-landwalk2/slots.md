# crit-landwalk2 / slots — slot, row, conjunct, hand and take-cell trace

Subject: docs/dev/lanes/p1dsg2_report.md @ 99447aa2a (rev 1). Code: the review tree
worktrees/crit-landwalk2 (main 02a054851). Line numbers are that tree's. Probe dir:
/var/tmp/pcrec-pcrec/scratch/crit-landwalk2/slots/ (16 pcrec compiles, 1 libpcre2 run).

## Findings

### SLOT-1 — L6/L8 read NEXT from a LOCATE predicate: a read cycle, and two self-consistent answers
- CONFIRMED (code trace + stamps). Severity: answer/design. Effort: medium (needs a
  mechanism the table does not have). Blast radius: every pattern reaching L6. Subject:
  §Admission table L6, L8; §Selection rule.
- The cycle in today's code. L6 is `CAND_READ(LOCATE, NEXT)`. Selecting NEXT reaches
  `handoff-reentry`'s predicate `pf_handoff_applies` (emit_dfa.c:9040), which reads FIRST
  (`req_use_read`, :9045). FIRST's `handoff` predicate `req_handoff_applies` (:8790) reads
  PRESENCE (`req_admit_read`, :8794) AND the path (`cand_path_members`, :8796, which selects
  LOCATE). PRESENCE's `dominated` predicate reads LOCATE's `whole`
  (`CAND_READ(PRESENCE, LOCATE, "req-whole")`, :8590). Both routes re-select LOCATE, whose
  walk reaches `landmark-walk`'s predicate, so L6 runs again. That is unbounded recursion: the
  trace build trips `table-read-recursion` and a release build overflows the stack. It
  happens at compile time as well, because the PRE gate runs in compile.c before ML is built.
- `cand_nodes[LOCATE]` declares no `reads` (:9936-9938). The design adds the edge
  LOCATE→NEXT without naming it. The `under` deny bits that break the existing
  PRESENCE→NEXT cycle cannot be reused here. `cand_read` (:11638-11643) ORs `under` into ONE
  `cand_select`. The nested reads build their own flags from `cx->opt->flags`
  (`cand_path_members`, `req_admit_read`), so a deny never propagates down the chain.
- The semantic half is worse than the recursion. The walk sets `u.locate.whole`, so
  PRESENCE becomes `dominated`, so FIRST loses `handoff` (its first conjunct is "a
  pre-check is emitted"), so NEXT loses `handoff`. The NEXT that L6 reads therefore depends
  on whether the walk is selected.
  - Witness: kv-quoted, `\b[a-z_][a-z0-9_]{0,31}="(?:[^"\\]|\\.)*"`
    (`--features all`; slots/kv.c, slots/kv_noh.c).
  - Today it stamps `RX_REQ_WHY "emitted"`, `RX_DFA_PREFILTER "handoff"`.
  - With the handoff out of the way it stamps `RX_DFA_PREFILTER "first-class-bounded"`, which
    is not in L6's decline set.
  - So kv-quoted has TWO fixed points. Walk unselected: NEXT = handoff, so L6 declines,
    which is consistent. Walk selected: PRESENCE is dominated, NEXT = first-class-bounded,
    so L6 passes, which is also consistent.
  - The design's "kv-quoted declines by L6" holds only under an evaluation order the
    design never states.
- What would fix it: L6/L8 must read the NEXT/start set of the COMPOSITE path, the one the
  walk would replace, with the walk transparent. That is a counterfactual read. Either
  (a) a deny that propagates through nested selections (new: today `under` is one level), or
  (b) a compile-time memo taken under `PCREC_NO_LANDMARK_WALK` before the LOCATE selection,
  in the shape of `pcrec_cover`'s keyed memo (known.c:397-415). Either way the design must
  declare the read edge and say which fixed point is meant.
- Repro: read the cited lines. Stamps: `build/pcrec -p rx --features all [-fno-req-handoff]
  -o kv.c --pattern "$(cat pcrec-bench/bench/loglines/patterns/kv-quoted.rx)"`, then
  `grep '#define RX_' kv.c`.

### SLOT-2 — `table-progress-rank` FIRES on the proposed DFA LOWER cell; the design states it passes
- CONFIRMED (code). Severity: design (the build fails its own self-check, or the check is
  silently weakened). Effort: small. Subject: §A2 "Why LOWER", bullet `table-progress-rank`.
- The check (emit_dfa.c:11366-11391) fails when a FIN_SEARCH row's non-AT take hand on a
  DFA/ATTEMPT route satisfies `!(hand & ~fb->hands)`, where `fb` is the fallback LOCATE row.
  That condition is "the fallback can hand this hand back". `fb` is `composite`, whose
  `.hands = CT_LOWER` (:10217-10218). `CAND_HAND_LOWER = CT_LOWER` (:9812).
  A LOWER take cell on `search-from`'s DFA route therefore trips `table-progress-rank`.
- The design reads "LOWER ⊆ composite.hands" as the PASS reason. It is the FAIL condition.
  The VM cell that exists today escapes only because the loop skips `rt == CAND_ROUTE_VM`.
- The check reads the composite's NEXT-side `.hands`, not the hands it gives FINISH
  (`u.locate.fin = CT_START`), so it is conservative here. The build must still change the
  check, for example to read the fallback's FINISH hands (`u.locate.fin`, or the proposed
  `gives[]`). That is a change in kind, and the design must state and argue it, not claim
  "unchanged in kind".

### SLOT-3 — An AT handed by a LOCATE row breaks the "AT = the caller's once-per-call ask" premise in four places; `locate-at-recursion` patches one
- CONFIRMED (code + spec text). Severity: design/maintenance. Effort: small-medium.
  Subject: §A2 table row AT, "The row declares its hands", "locate-at-recursion".
- Today AT has exactly one producer, "the `caller` locator of the match-here entry"
  (locate_finish.md §1.2 table, line 254; "`caller` always asks a point", :258). Code relies
  on that in four places:
  1. `cand_takes` (emit_dfa.c:10647) lets FINISH take AT only on `s->point`.
  2. The rank inequality exempts AT because "`AT` is the match-here entry's E-FC (`entry`,
     once per call), not a relocate" (:11373-11376).
  3. `cand_nodes[FINISH].entry = CN(LOCATE)` (:10039) exempts that edge from the acyclicity
     walk on the same "once per call" premise.
  4. Every search-body FINISH ask hard-codes `.point = false`: `cand_finish_ask` (:10780),
     `cand_path_of` (:11943), `dfa_search_calls_match` (:13601).
- A per-hit AT from `landmark-walk` is neither once per call nor the caller's. Marking it
  `point = true` (as the design proposes) makes it pass filter 1 by impersonating the caller.
  It then rides the exemptions in 2 and 3, which is exactly why the static closure cannot see
  the SLOT-4 self-cycle the design describes.
- `locate-at-recursion` is a parallel check for that hole. Placed "beside
  `table-finish-not-total`", it runs in the static `cand_path_selfcheck`, where there is no
  Ctx and no `anchored_ok`. Statically the last AT taker on DFA is always `search-from`
  (FIN_SEARCH), so the check either always fires or must become a per-compile path check
  (beside `path-needs-unbuilt`, :11950). The design names neither.
- General form: make the hand's ASKER part of the progress model. A LOCATE row's per-hit
  return (verify-at NOMATCH → next hit) is a `raise` edge on the hit cursor, and the AT
  exemption applies only to the caller's ask. That closes the hole in the existing check and
  deletes the need for a new one.
- The design also leaves three emitter call sites out of Build plan step 4: `cand_finish_ask`,
  `cand_path_of`'s LOCATE-hands loop and `dfa_search_calls_match`, all `point = false` today.

### SLOT-4 — L1 `route` as worded passes VM-hybrid prefilter bodies; only L10 declines them, by accident, after ML is built
- CONFIRMED (code + compile + libpcre2). Severity: answer-latent (stage 2) / size (stage 1) /
  doc. Effort: small. Subject: §Admission L1, L3; §A1 "BOT-family ... declines on stage 1 by
  the route".
- `cand_route_of` (emit_dfa.c:3835) is CAND_ROUTE_DFA for every non-ATTEMPT engine, VM
  hybrids included. A CR_DFA LOCATE row IS selected on a VM hybrid's inlined prefilter body:
  `(?=[a-z]*b)[a-z]+@x$` stamps `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"`,
  `RX_DFA_SCAN "rev-end"`. `cover` needs its C1 `finisher-dfa` (known.c:181) for exactly this
  reason. "The body is CR_DFA, i.e. ENG_UNANCH" therefore does not exclude VM-finisher
  artifacts.
- Witness: `(?![a-z]*b)[a-z]+@x` (slots/hybrid_witness.c; slots/pcre2_check.py).
  - pcrec stamps: VM hybrid; NEXT `byte-class`, so L6 passes; L7 passes (`@` ∉ [a-z]).
  - libpcre2 10.46 on "ba@x" gives (1,4).
  - ML over the erased prefilter P = `[a-z]+` gives s*(j) = 0. One VM attempt at 0 fails, so
    per-hit answers NOMATCH, which is wrong.
- On stage 1 it declines only at L10. `build_anchored_dfa` returns because the VM finisher
  declares no `CAND_MA` need (compile.c:386), so `anchored_ok` is false. That is a POST row,
  so ML has already been built and the listing names `anchored-A`, not `route`.
- L3's "VM-routed, so L1 catches them first" is untrue for hybrids. Stage 2's L10 (verify-at
  is always available on VM) would open the hole.
- Fix: L1 is cover's C1 (`pcrec_cand_finisher_dfa`), plus the row's own `.routes = CR_DFA`.

### SLOT-5 — L8 is not "`req_landmark_admits` with another K": its `h` is hard-wired to the pre-check's landmark, and it needs a NEXT-shaped selection
- CONFIRMED (code). Severity: design/answer-of-selection. Effort: small. Subject:
  §Measurement card "The rarity row"; §Selection rule step 2.
- `req_landmark_admits(s, k)` (emit_dfa.c:9016) takes `h` from `req_landmark_hit_ppm`
  (:8956), which reads the FACTS `req_byte`/`req_run`, the handoff's landmark. It does not
  read the landmark L the choice rule picked.
- Where L ≠ the fact's landmark, the row prices the wrong byte. The design's own S1 witness
  is such a case: dup-param picks `=` over `req_byte` `&`, `RX_REQ_BYTE "38"`. The choice
  rule's step 2 ("largest margin" per candidate) cannot be computed at all: the primitive has
  no landmark parameter.
- `m` comes from `req_start_set` (:8979-8985), which re-selects NEXT and calls
  `cand_row_scan(..., s->us, ...)`. A LOCATE `CandSel` carries `.us = NULL`
  (`cand_locate_sel`), so it must build NEXT's `UnanchStart`. That is a NEXT read, so it
  falls under SLOT-1.
- The general form is right: the primitive takes the landmark's byte-set mass as a parameter,
  which is [PRIOR-COST-UNIFY]'s shape. It is a generalisation of an existing function, though,
  not "no new predicate". The design should say so and name the new parameter.

### SLOT-6 — `lmwalk_conj[]`: the claimed shape matches no existing table, and L0/L1 duplicate fields `cand_rows[]` already has
- CONFIRMED (code). Severity: maintenance/design. Effort: small. Subject: §Admission
  "Shape", L0, L1; §Mechanism "Deny".
- The design calls `{ cid, id, phase, kind, holds, desc }` "`cover_conj[]`'s shape", but the
  two existing tables differ:
  - `CoverConj` is `{ cid, id, kind, holds }`, with no phase and no desc (known.c:368-373).
  - `split_conj[]`'s `CompConj` is `{ id, name, phase, holds, reads, nreads }`, with phase
    and a declared `reads` column (compound.c:248-258).
  - The proposed third member is a hybrid of the two. That is the [ROWCONJ] drift the plan
    row exists to stop.
- `CompConj` already has a `reads` column. That is exactly where L6's NEXT read (SLOT-1)
  would be declared. Building `lmwalk_conj` in `CompConj`'s shape adds no fourth spelling.
- L0 `denied` puts the deny inside the predicate. `cand_rows[]` already has `.c.deny`, which
  `cand_select` reads (emit_dfa.c:10574), and `rev-end` uses it with the listing's 4th field
  (`PCREC_NO_REV_END`). The F0 precedent is a FORM table's whole-form flag, not a row's deny.
  The ladder rung's OR'd flag and any SLOT-1 "walk transparent" read both need the deny in
  `.c.deny`, where `cand_select` skips the row.
- L1 `route` restates `.routes = CR_DFA`, and the restatement is also wrong (SLOT-4).
- Fix: put the deny on `.c.deny` (with the listing field), make L1 `finisher-dfa`, and keep
  only true admission facts as conjunct rows.

### SLOT-7 — `compound_place[]` row 0 `step-table` cannot be evaluated or witnessed in code; it has one member
- CONFIRMED (code). Severity: design (a special case dressed as a row). Effort: small (a doc
  hunk instead). Subject: §Placement.
- `compound_place[]` takes a `CompPart` (compound.c:273-305). It is asked only of
  `compound_rows[]` parts at table build (:348). "Review asks it of every in-Job candidate" is
  a review procedure, not code. ML is never a `CompPart`.
- Conjuncts (b) "no entry, no FINISH" and (c) "hands a POSITION" are not functions of a
  `CompPart`'s fields. Every part HAS an entry, typed by `bound` (`part_type`, :315). So row 0
  is unreachable for every `CompPart`, and the house table's per-row reach witness
  (compound.md §A.2, line 322) cannot exist.
- Does it silently move existing machines? No:
  - split's Q and 4c's searches fail (b) and keep row 1.
  - A is FINISH's machine and `rev-end-relaxed` is a rewrite.
  - MR is ambiguous under (a): the whole tree is the improper concat prefix. It would land
    on row 0 or row 3, and both mean in-Job.
  - So nothing moves. The row's whole effect is "ML is in-Job".
- Simpler general form: amend row 3's text (compound.md §A.2) from "P's tree under erasure"
  to "P's tree, or a cut of it that an in-Job row walks, under erasure, P's options". Row 1's
  "different tree" then means a REWRITE. No code row, no dead predicate, the same placement.

### SLOT-8 — The new ladder rung "before drop-anchored" collides with the SDR ordinal, and with the ruled APPEND order
- CONFIRMED (code). Severity: design. Effort: small. Subject: §Size "The size-cap ladder".
- The drop rungs compose through ONE ordinal, `size_drop_rung`: "a rung means every
  contributor up to and including this one is dropped" (internal.h:3109-3111). The order is
  RULED: APPEND, with `SDR_NO_ANCHORED` staying rung 1 (Frank 2026-09-17, internal.h:3119-3121).
- `fit_anchored_applies` requires `size_drop_rung == SDR_NONE` (compile.c:1097). A rung
  placed before it that sets an SDR value either:
  - stops drop-anchored from ever firing after it, which defeats the "dominance" order; or
  - renumbers SDR against the ruling.
- The working shape is drop-premul's: `FIT_SDR_KEEP` plus the row's deny bit OR'd through
  `sets` (compile.c:1371), with `.c.deny` on the row (SLOT-6). The design must say this.
- `COMPILE_MAX_ATTEMPTS` (compile.c:672) and `fit_tables_selfcheck`'s formula (:1453) grow by
  one. Neither is in Build plan step 6/7's reader list.

### SLOT-9 — `-fno-anchored-dfa` would also switch the walk off; tuning.md §2.15 is not in the reader list
- CONFIRMED (spec text + L10). Severity: doc (caller-observable coupling). Effort: small.
  Subject: §Admission L10; Build plan step 7.
- §2.15¶1 says the flag denies "the ANCHORED MACHINE behind `<prefix>_match`", and its
  stamp column names only `<PREFIX>_DFA_MATCH` (tuning.md:125, :335-341).
- Under L10 the flag also moves `RX_DFA_SCAN` from `landmark-walk` to `unanchored` and
  costs the search entry ×44. Rung 3's stderr note ("loses the [OPT-2] fast path") would
  likewise understate a drop that now also removes the walk.
- Step 7 lists match_api, the tuning "new section" and limits §8.4. It does not list §2.15¶1/¶3,
  the line-125 table row, the §5.4 dial exclusion (:1316) or the `drop-anchored` note text
  (compile.c:1365-1368).

### SLOT-10 — `dfa_search_calls_match` and the entry-shape table know one `_search`→`_match` caller, the rev-end tie
- SUSPECTED. Severity: maintenance/answer-at-link. Effort: small. Subject: Build plan step 4;
  §Remodel overlap [ENTRY-TABLE].
- `search_match` (entries.c:110, 115; internal.h:8185) is set only by
  `dfa_search_calls_match` → `revend_tie_asked` (emit_dfa.c:13585-13612), keyed on ENDSET.
- If the walk's AT→verify-at is emitted as a call to `<prefix>_match` (the rev-end tie arm's
  precedent), the part references (`pr_dfa_search`/`pr_dfa_find`, entries.c:135-146) miss
  the edge.
- What would confirm it: the build's choice of inline anchored run versus `_match` call. The
  design names `entry_rows[]` (E1-prime, not yet in code) but not today's `search_match`
  derivation.

### SLOT-11 — `lmwalk_forms[]` on stage 1: one reachable row, and F2 is not a total fallback on DFA
- CONFIRMED (text vs `revend_forms[]`). Severity: maintenance (D77). Effort: trivial. Subject:
  §Admission "The form table".
- `revend_forms[]` ends in an always row (`overflow`, `rf_always`, emit_dfa.c:13509-13520).
  `lmwalk_forms`' last row F2 is "otherwise (VM only)", so on DFA the table has no total
  fallback, and on stage 1 F1 is the only reachable row.
- Under D77 (and D10's "stage 1 has one form") the table belongs to stage 2. Stage 1 should
  build the F1 hands directly and leave the form table to [LANDWALK-VM].

## (a) GOALS

- G1 (answers) is checkable: libpcre2 differential, the A1 table, the D27 cell. But SLOT-1's
  two fixed points and SLOT-4's hybrid make G1 depend on evaluation order and on L10's
  accidental role, so the design does not yet serve G1 first.
- G2 is checkable (cell 1, ±1%).
- G3 ("no new mechanism") is NOT met as written:
  - SLOT-1 needs a propagated deny or a memo read;
  - SLOT-2 changes a self-check;
  - SLOT-3 adds a parallel check plus a `point` impersonation;
  - SLOT-5 generalises the K primitive;
  - SLOT-7 adds a code row with one member.
  Each is small, but G3's claim should be restated as "these N small generalisations".
- G4 is checkable (the `lwcall` cells, the census). The order G1 > G2 > G3 > G4 is otherwise
  honoured.

## (b) SIBLING OF A FAMILY

- `lmwalk_conj[]` is the THIRD conjunct table (`cover_conj[]`, `split_conj[]`), in a third
  shape (SLOT-6). [ROWCONJ] is filed. Building the third member in `CompConj`'s shape now
  costs nothing and keeps the unification a rename.
- The AT hand gets a second producer (SLOT-3). `search_match` gets a second caller
  (SLOT-10). The `whole`-answering LOCATE rows become four (`empty`, `rev-end`, `cover`,
  `landmark-walk`), all read by PRESENCE `dominated`, whose desc lists them by name
  (emit_dfa.c:10258). That desc should say "a LOCATE row with `whole`", not a list.
- The landmark K-admission gets its second reader (SLOT-5), which is the [PRIOR-COST-UNIFY]
  sibling the design names.

## (c) GENERAL FORM + UNLOCKS

- General form: a LOCATE row is "seeded walk(s) over a reverse machine of a CUT of P, then a
  hand per seed": `rev-end` (seeds n/n−1, the cut is the whole P) and `landmark-walk` (seeds
  j+|L|, the cut is P·L) are two parameterisations. `emit_rev_end_one_seed` already serves
  both (D10).
- Unlock U-a: the counterfactual-selection read SLOT-1 needs ("what would slot X select if
  row R were denied", memoised per compile). The rarity row reads the composite's NEXT, and
  the handoff's G1 already does this one level deep with `under`. Trigger: the second
  predicate that must read a slot "as if" another row were off. SLOT-1 is the first, G1 the
  zeroth.
- Unlock U-b: asker-typed hands (SLOT-3). The progress model keys AT's exemption on the
  asker, so any LOCATE row may hand per-seed point asks with no parallel check. Trigger: a
  second LOCATE row that hands AT, e.g. [LANDWALK-FWD] or a cover-style per-candidate
  verify.
- Unlock U-c: the K primitive over an arbitrary landmark set (SLOT-5). It gives every
  seeded-from-a-landmark row one price. Trigger: the stage-1 build itself, since L8 needs it.

## PROBED-AND-HELD

- `verify-at`/`search-from`/`prio-const`/`nomatch`/`report` take cells per route are exactly
  as §A2 cites them (emit_dfa.c:10589-10630; 5 rows × 3 routes checked).
- The FINISH totality check: LOWER added to `asked[DFA]`, last taker `search-from`
  (`cand_always`, DFA needs `.mach = 0` ⊆ `always_built = MF|MR`) → passes (:11401-11430).
  1 hand × 1 route.
- `cand_path_finish`'s relocate (:11894-11908): a non-AT hand at FIN_SEARCH with
  `reloc >= 0` adds the fallback's machines and cells, not its front. LOWER → composite adds
  MF, NEXT, RECOVER, with no cycle through the visited set. As the design says.
- `.needs { CAND_ML, 0, CN(PRESENCE) }` has `rev-end`'s shape (`{ CAND_MR, RECOVER,
  PRESENCE }`). `whole` makes PRESENCE `dominated` (:8590). Held, apart from SLOT-1's
  consequence.
- `cand_locate_hands`'s `h[3]` holds {AT, LOWER, NOMATCH} (3 ≤ 3). Held, but `gives[]` must
  keep that bound or `h` grows.
- `dfa_member_machines` is `out[3]` over MF/MR/MA (:4888-4896), and its 3 readers (:4901,
  :4973, :5034) take the count, so `out[4]` with ML is a local change.
- `cand_list_stamp(LOCATE)` is `RX_DFA_SCAN` on every route (:12157). Held.
- The deny bits: bits 40-56 allocated (55 absent, the kit's per D164 add. 5), 57-63 free =
  7. The design's count holds.
- `drop-anchored` with the walk: `pcrec_cand_drop_anchored_shrinks` (:11663) toggles
  `anchored_ok`. L10 then declines the walk, so the members go {ML,MA,MF,MR} → {MF,MR}, a
  strict subset, and the rung applies. ¶2a needs no change. Held, by reasoning.
- `-fno-anchored-dfa` → `build_anchored_dfa` returns before building (compile.c:387), so
  `anchored_ok` is false and L10 declines. The A2 sabotage cell is reachable as described.
- Find-all `next`: R is never nullable (L non-empty), so `nedfa` is not built
  (compile.c:430-446). The per-call hit cursor and `reach` are restarted by `__find`
  (`pr_dfa_find`). No cross-call state. Held.
- Bench stamps re-read: 5b `RX_DFA_PREFILTER "byte-class"`, `RX_REQ_WHY "emitted"`,
  `RX_DFA_MATCH "unwrapped"`; kv-quoted `handoff` (K 32). Both match §Baselines. 2 patterns.
- VM-only witnesses `(a+)X\1`, dup-param, `x(a+)X\1$`, `[a-z]+@([a-z]+)\.\1`: all
  `RX_ENGINE "vm"`, `RX_VM_PREFILTER "none"`, no DFA body, so no LOCATE on CR_DFA, and L1's
  stated decline holds for them (4 patterns). It fails only for hybrids (SLOT-4).
- `compound_place[]` against MR, A, Q, 4c and `rev-end-relaxed`: no placement moves
  (SLOT-7). 5 machines.
