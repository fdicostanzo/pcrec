# sbscope — scoping the single-byte FIND's move into the kit (D161 addendum 14)

Lane sbscope, 2026-10-14, opus. READ-ONLY scoping: no `src/` or `memfn/` edit,
no timing. Facts and a scope, no design rulings. Code of record: main
`711cf603a` (abi 78), read from a detached worktree. The kit branch
`lane/memfn-r17` (`4d6d2c255`, abi 77, R17-b built) is cited where it differs.
Census: `docs/dev/lanes/sbscope/census.py` over main's build, pcrec-bench
`25480b47`.

## 0. Answers first

1. **pcrec emits no `memchr` text anywhere on main.** Every libc call in an
   artifact is written by a kit row (`pffind.c`, `precheck.c`, `ofsskip.c`,
   `runcmp.c`). What pcrec still decides is the FORM CLASS, through how it
   states the site. A one-member set goes as a `term_byte` with no table, so
   the kit's `pf_memchr*` rows apply. A larger set goes as a `term_set` with a
   `table_ref`, so `pf_walk*` applies. The VM hat always goes as a table (the
   Q-R5 ruling). pcrec also writes form-dependent text around the site (a guard
   before memchr, a test after the walk). The decision is `cand_derive`'s
   `use_memchr = count == 1` (§1).
2. **"No pre-scan" splits by consumer.** On DFA consumers it is answer- and
   give-up-identical: the DFA loop walks every byte. On a budgeted VM consumer
   it is NOT: the VM hat and the VM-route pre-check are ONE_WAY rows, and
   dropping them turns answers into give-ups. The axes ledger already pins
   this: GIVEUP1 groups E and F5. D158 forbids that direction (§2).
3. **The move can be zero-mover at default flags for the one-byte sites.**
   That needs 8 stated facts or read-backs (§3, P1-P8). Most are already
   designed on the kit branch: R17-a's table offer/`reads_table` and
   `includes`. The blockers are three:
   - pcrec readers that price or name the scan FORM: G1, R4,
     the handoff's K admission, `landing` L4, the stamps and `<string.h>`;
   - the kit rendering the guard/post-test text;
   - the default no-data row set reproducing today's count-based rule, not
     R17-b′'s LINER default (R7 = V1).
4. **libc today:** `memchr` and `memcmp`, plus `strlen` in the vars helpers.
   No `memrchr`, no `memmem`. No deny reaches the DFA `memchr` prefilter rows
   or MLINE. A libc deny falls to the generic row everywhere except three
   places with no libc-free row today: the offset-skip FUNC's BODY slot,
   MLINE's back FIND (generic never serves its LOOP_EXIT `on_miss`), and
   runcmp's exact compare outside the overlap lengths (§4).
5. **MLINE already has its D161 shape.** `window_contract.md` §2.5 (D161
   add. 7) designs it as a context predicate, not a span. The context check
   and the edge stay pcrec's. Frank would be confirming that the kit may also
   pick NONE there. It is answer-safe because the ENG_ATTEMPT DFA has no
   budget (§5).
6. **Requests and work:** pcrec-side P1-P8 and kit-side K1-K8, sized (§6).
7. **Population (§7).** In the corpus, 1,790 of 5,336 compiled artifacts carry
   at least one single-byte search, and 3,369 carry a start-search site at all.
   In the bench, 74 of 343. Of the 172 compiling rwquest questions, 74 carry a
   single-byte search. Counted by start form instead, the 172 split as:
   - 34 take a one-byte prefilter;
   - 23 take MLINE;
   - 46 take an offset/run row (the kit's memchr bodies);
   - 37 take a set walk;
   - 25 take the handoff re-entry;
   - 5 take the VM hat.

   The ruling's "92 of 177" is not reproduced by any class here; §7.3 has the
   candidates.

## 1. The decision inventory (main `711cf603a`)

All in `src/gen/emit_dfa.c` unless named. Since [START-TABLE] C3 the old
`dfa_pfs[]` is the NEXT slot of `cand_rows[]`.

### 1.1 The derivation that makes every one-byte choice

| what | where | rule | facts read |
|---|---|---|---|
| `cand_derive` | :4290 | `usable = 0 < count < 256`; `use_memchr = usable && count == 1` | the 256-entry set |
| `cand_from_escapes` (DFA) | :4309 | bytes on which the start state moves | `Dfa` transitions |
| `cand_from_live_seeds` (ATTEMPT) | :4331 | predecessor bytes whose seed is live, offset 1 | `s1u[]` |
| `unanch_start` | :4470, kind at :4587 | `kind = use_memchr ? DFA_PF_MEMCHR : DFA_PF_BYTE_CLASS`, gated on `!start_acc && usable`; `views` = the D11 bound | both machines, view flags, `start_acc` |

`DFA_PF_MEMCHR` is a FACT about the set ("one member") named after a method.
Every row below that "chooses memchr" is reading that count.

### 1.2 NEXT rows (`cand_rows[]`, :9123-9220)

Each row's emitter states a site through `pcrec_emit_find` (:6490) →
`find_site` (:6443). Today's FORM lever is the term encoding at :6505:
`PF_SCAN_BYTE → PCREC_FIND_MEMCHR` (`term_byte`, no table); otherwise
`term_set` + `table_ref`.

| row (listed order) | route | predicate (line) | facts the predicate reads | site as stated today | form text pcrec writes around the site |
|---|---|---|---|---|---|
| `run-pinned(-bounded)` | DFA | `pf_run_applies_common` :6651 | run pin, `kind == DFA_PF_MEMCHR && cand.byte == run byte` (no k-set) | OFS FUNC (kit `fn_rows`) | — |
| `offset-set(-bounded)` | DFA | `pf_ofs_applies` | `kind != NONE`, `ofsk.nsel > 0` (prefix_k.c) | OFS FUNC, scan byte at k* | — |
| `handoff-reentry` | DFA | `pf_handoff_applies` :7943 → `req_landmark_admits` :7920 | FIRST = handoff, landmark hit ppm h, **mass of the row below's set m** | PRE site's 2nd use (ASSIGN) | — |
| `first-memchr-bounded` | DFA | :7186 = `pf_dfa_start_set` :7153 && `views` && `t.use_memchr` | start_set S, E, seeded, `T ⊊ E` | `term_byte`, end_back 1 | `if (pos + 1 < n) { size_t skip_from…; FIND; reseed }` |
| `first-class-bounded` | DFA | :7184 | same, any count | `term_set` + `start_bytes` table | `skip_from; FIND; reseed` (no guard) |
| `first-class` (VM hat) | VM | `pf_vm_start_applies` :7310 | route VM, no hybrid, BOUND not one, S not nullable, `\|S\| < 256` | `term_set` + `start_set` table, **always** (Q-R5: "table form only, at any \|S\|", :7334) | `if (attempt_position >= n) return 0;` after |
| `memchr-bounded` | DFA | :6339 `kind == MEMCHR && views` | count, views | `term_byte`, end_back 1, EXCLUDED | `if (pos + 1 < n) { FIND }` |
| `memchr` | DFA | :6342 `kind == MEMCHR` | count | `term_byte`, EXCLUDED, `on_miss "return 0;"` | `if (pos >= n) return 0;` BEFORE |
| `byte-class-bounded` | DFA | :6345 | count, views | `term_set` + `can_begin_match`, NOP | — |
| `byte-class` | DFA | :6348 | count | same | `if (pos >= n) return 0;` AFTER |
| `pred-memchr` (MLINE) | ATTEMPT | `cand_pred_memchr_applies` :8903 → `attempt_cand` :4352 (memchr-or-nothing by charter) | live seeds, BOUND not one | `term_byte` at offset −1, floor `start`, AT_N, `on_miss "break;"` (:12977) | `if (start > X && s[start-1] != '\n') { … }` (the context check) |
| `next-none` | all | always | — | no site | — |

The VM hybrid's inlined `<prefix>_prefilter` is this same emitter on the same
`job->dfa`, so the DFA rows serve the hybrid unchanged (census `PF:HYB:*`).
The VM hat is emitted through `pcrec_emit_vm_start_seek` (:7433), which is
called from `emit_vm.c:13477` (the entry) and `emit_vm.c:13572` (each retry).

### 1.3 The other single-byte choices

| site | where pcrec decides | what it decides | kit side today |
|---|---|---|---|
| PRE (presence) | PRESENCE rows :9055-9082 (`none`, `one-attempt` G2 :7690, `dominated` G1 :7694 → `req_byte_dominated_by` :7664, `set-leads` :7718, `emitted`) | WHETHER a pre-check runs, and on the VM route with no DFA scan, the whole-set and whole-run tests (K65/K66) | `precheck.c` renders `!memchr(...)` per byte, the `rq_set` loop, the pair arm |
| set-leads lead | `req_set_leads_applies` :7718 | a rarer set pick searched before the run | the same memchr |
| FIRST handoff | `req_handoff_applies` | whether the gate's first hit moves the scan start | `precheck_assign_byte` (R-15, one `memchr`) / `precheck_assign` |
| OFS / run-pinned | `prefix_k.c` (k*, the set, the scan byte); the rows above | which offset is scanned | `fn_rows` BODY `fn-pair` / `fn-memchr` (both memchr), SIMD PREFIX `vrun-*` |
| RETRY density (R4) | `pcrec_dfa_cand_ppm` :7561 | prices the scan form: byte → that byte's ppm; set → mass; NONE/ATTEMPT → 10^6 | — |

### 1.4 pcrec READERS of the scan form

These are the facts a kit-owned form has to feed back. Each reads the NEXT
selection, never the kit:

- **G1** (`dfa_cand_scan` :7515, `req_byte_dominated_by` :7664) reads `memchr_form` and the scanned byte. Its density arm requires a `memchr` form.
- **R4** (`pcrec_dfa_cand_ppm` :7561) reads `PF_SCAN_BYTE`/`SET`/`NONE`.
- **The handoff's K admission** (`req_landmark_admits` :7920) reads the mass of the row below's scan set, and `m = 10^6` when there is no scan.
- **`landing` L4** (`start_landing_applies` :8544) requires the NEXT row to have a block (`u.pf.emit != NULL`). `pf_close` (:6375) writes `landing_position` inside that block.
- **The stamp** `<PREFIX>_DFA_PREFILTER` (`dfa_prefilter_name` :13935) is a method name. On ATTEMPT it reads `"memchr"`/`"none"` at :13957. It is written BEFORE the body exists. The same holds for `RX_VM_START_SCAN` and the `rx_info` mirror.
- **`<string.h>`** (`pcrec_emit_prologue` :13485, :13495) reads the ATTEMPT route's memchr form. On the DFA route it is unconditional.
- **The run pin** (`pf_run_applies_common` :6667) reads `kind == DFA_PF_MEMCHR`. That is the count fact; only its name is a method.

### 1.5 What the kit already receives (`mf_site`/`mf_term`, main `MF_SITE_ABI` 10)

**Received:**
- the set's bits; the offset (0, or −1 for MLINE); `table_ref` (whether a table is offered);
- `end_back` (the D11 bound); `empty` (EXCLUDED / NOP / AT_N); `on_miss` + `on_miss_leaves`;
- `use`; `consumer` (MF_C_ENGINE for every PF/MLINE site, so it does not distinguish them);
- `span_lo`/`span_hi` (UNBOUNDED); `rank` (RUN terms only);
- the term `ppm_lo`/`ppm_hi`, which pcrec fills as `[0, MF_PPM_FULL]`, i.e. no density (`memfn_sites.c:223-224`).

**Kit branch adds** (R17-a, `MF_SITE_ABI` 11/12): W0-W2, `decl_point`, the stem, `mf_locals`, and `mf_defined.reads_table`/`includes`.

**Missing for a kit-chosen form:**
- (a) the table offer on one-member sites;
- (b) a consumer kind;
- (c) the effort fact (§2);
- (d) form-neutral miss/guard statements;
- (e) a define-time read-back of the kit's form class.

All of these are listed in §6.

## 2. What "no pre-scan" means at each site

| site | without the scan, who walks every position | answer-safe as is? | give-up identity |
|---|---|---|---|
| DFA PF (`memchr*`, `byte-class*`) | the DFA transition loop from the start state | yes: every PF comment says "speed only". The unbounded memchr's early `return 0` becomes the loop running to `n` and returning 0 | identical: the DFA engine has no budget |
| DFA hat (`first-*-bounded`) | the seeded DFA loop. No skip means no re-seed is needed (`pf_emit_moved_reseed` runs only where the skip moved) | yes | identical |
| VM hybrid's prefilter (`PF:HYB:*`) | the hybrid's own DFA steps every byte and still hands the VM the same candidates | yes | identical for attempts. **But** R4 (`pcrec_dfa_cand_ppm`) prices the scan: NONE reads 10^6, so the RETRY row (adaptive vs adaptive-dense) may move. Both are ONE_WAY rows. Moving between them is allowed and is a mover |
| **VM hat** (`first-class`) | the VM attempt loop tries every position | answers identical under unbounded budgets | **NOT identical**: each extra attempt spends the per-call budget (f3search: steps/frames are per call). That is exactly the deny arm `-fno-start-set`, which has its own GIVEUP1 group F5 (22 cells, `tests/startset/giveup.rxt`). A kit default of NONE there moves today's answers to give-ups, which D158 forbids |
| MLINE (`pred-memchr`) | ENG_ATTEMPT's attempt loop runs an attempt per position. A skipped start "would have jumped straight to the dead label" (:12934 comment), so each one is O(1) | yes | identical: a DFA attempt has no budget |
| PRE on a DFA route | the DFA scan | yes; G1 already drops it when it is dominated | identical |
| **PRE on a VM route with no DFA scan** (K64/K65/K66) | the VM's attempts | answers identical under unbounded budgets | **NOT identical**: the pre-check is "the only linear no-match proof" (:7504; the emitted note at :1446). GIVEUP1 groups E (45 cells, `-fno-req-byte`) and F (12, `-fno-req-run`) pin the deny arms' give-ups |
| FIRST/NEXT handoff | the scan from `startpos` | yes | group F4 is EMPTY by construction (Q10) |
| OFS / run-pinned | the scan at offset 0 (the rows below) | yes | the DFA route only |

Pcrec-side changes "no pre-scan" needs even where it is answer-safe:

- **`landing` (L4).** Two ways: the NEXT block (`pf_open`/`pf_close`) must
  survive with the kit's NONE pick inside it, so that `landing_position` is
  still stored; or L4 must read the kit's pick and decline. Keeping the block
  makes the store run on every start-state byte. Its correctness under the §2.4
  theorem is UNCHECKED here.
- **G1 is one decision split across two sites.** It drops the presence check
  BECAUSE the scan tests the same byte. If the kit then drops the scan, both
  are gone. That is answer-safe on DFA routes, but the cost argument G1 made
  no longer holds. Under D161 add. 3 the scan and the presence gate are one
  window-search site; pcrec deciding G1 while the kit decides the scan is the
  seam's cross-site coupling.
- **Pricing readers.** R4 and the K admission price a scan that may not run.
  This is a5inv F1's shape: a price read off a scan the artifact does not
  carry.

**K65-class (a pick that decides a VM give-up).** The pre-check's PICK
(`req_set_pick`) decides give-up only where a single member is tested. K65
fix (a) already tests EVERY member on the no-scan VM route
(`emit_req_set_rest`). So a kit-chosen FORM of the presence test (memchr vs a
byte loop vs SWAR) is give-up-neutral as long as it tests the same predicate.
Only a kit-chosen NONE is not.

## 3. The zero-mover first step

**Question:** from stated facts, with a default no-data row set, can the kit
reproduce today's choices byte for byte at SIMD-off?

**Answer:** yes for every one-byte site at default flags, given the eight items
below. Two kit-side conditions apply as well.

The default no-data row set must be TODAY'S RULE, keyed on count and consumer:
- one member, not a VM attempt seek → the libc row (`memchr`, `memchr_back` at offset −1);
- otherwise → the set form.

Relative to main, the set form is the table walk. Relative to the kit branch,
it is R17-b's `pf_terms_mask` where a cover exists.

R17-b′'s R7 (LINER = V1 at SIMD-off, `r17b_prime.md` §1.1) is NOT that rule.
Neither it nor any other R17-b′ row has a memchr form or a NONE form (its
`FF_NONE` means "row dropped"). So either one-byte sites sit outside R7, or
the default reads as "LINER for a one-term cover is the libc row". That is a
ruling, and per D149 / `pcrec-no-silent-defaults` it is an UNMEASURED
DEFAULT that needs a label.

The facts pcrec must state, or read back, for byte identity:

| # | fact | sites | today | why identity needs it |
|---|---|---|---|---|
| F1 | the candidate set as a SET term, one member included, plus the table offer on every PF/VM-hat site; the kit's `reads_table` decides emission | PF, VM hat | `term_byte`, no table, for one member | otherwise pcrec's encoding IS the form choice. R17-a's `reads_table` (kit branch) is the emission half |
| F2 | the miss behaviour as hooks, not as pcrec text: `empty` + `on_miss "return 0;"` for the unbounded rows; the n−1 clamp and the `if (pos + 1 < n)` wrapper for the bounded memchr rows; the walk's post-test | PF (6 rows), VM hat | pcrec writes the guard BEFORE memchr (:6536), the test AFTER the walk (:6570), the wrapper (:6556, :7233) | the guard/test placement differs by form; the kit must write it for the text to stay identical |
| F3 | the DFA hat's re-seed as text placed INSIDE the kit's guard (an "after" hook) | `first-*-bounded` | pcrec writes `skip_from` + re-seed inside its own wrapper | the memchr form wraps; the walk form does not |
| F4 | the consumer kind: DFA scan restart / DFA hat (re-seeding) / VM attempt seek / ATTEMPT predecessor seek | PF, VM hat, MLINE | `MF_C_ENGINE` for all | reproduces Q-R5 (the VM hat keeps a table at \|S\| = 1: memchr per failed attempt measured ×0.6 at 80% density, :7331) |
| F5 | the define-time read-back of the kit's form class (none / one-byte scan / set scan) | every reader in §1.4 | the readers read pcrec's row | G1's `memchr_form`, R4, the K admission, `landing` L4, `<string.h>` (the kit branch's `includes` covers this one) and the stamps all run BEFORE or OUTSIDE the body; the stamp is written before it exists |
| F6 | the PF comment as kit text, or pcrec's comment made method-neutral | PF | `pf_comment_memchr` (:6387): "…so one memchr() replaces the steps", NONESSENTIAL | identical under the default `-fno-comments`; the `-fcomments` arm moves unless the kit renders it |
| F7 | the stamp spelling: keep `RX_DFA_PREFILTER`'s values as pcrec ROW identities (they already are: on the kit branch, `[ab]\d+z` stamps `"byte-class"` while the kit renders `pf_terms_mask`) | stamps, `rx_info` | method names | no byte moves if the values stay row names; renaming them is an abi event |
| F8 | the effort fact (§2): skipping this site can change a budgeted engine's work | VM hat, PRE on a no-scan VM route | not stated | not needed for identity. It is needed for any NONE row to be D158-safe |

**Where it cannot be zero-mover:**

- **The `-fcomments` arm**, unless F6 moves the comment into the kit.
- **Set sites relative to main.** The kit branch's R17-b already moved them:
  its own abi 77 event, separate from this one. The one-byte sites are
  untouched by R17-b, so they are zero-mover against both baselines.
- **The VM hat at |S| = 1** (112 corpus / 8 bench). Main renders a table walk,
  the kit branch `pf_terms_mask` (checked on `(x[a-z]+)y\1`). The baseline is
  whichever branch lands first.
- **Any NONE pick.** It moves by definition, and it is a separate event behind
  F8.

## 4. The libc row and its deny

| libc call | written by (kit row) | sites | population (corpus artifacts carrying it) |
|---|---|---|---|
| `memchr` | `pffind.c` `pf_memchr`, `pf_memchr_bounded`, `pf_memchr_back`; `precheck.c` `precheck`/`precheck_assign` (`!memchr`, the `rq_set` loop, the pair arm), `precheck_assign_byte` (R-15); `ofsskip.c` `fn-memchr`, `fn-pair` | PF, MLINE, PRE, set-leads, handoff, OFS/run-pinned | 2,576 (`RX_MEMFN_LIBC` contains memchr) |
| `memcmp` | `runcmp.c` row `memcmp` (the exact compare's total fallback; `overlap` is libc-free for lengths 3, 5-7 and 9-15) | VERIFY (OFS/PRE run compare), VMRUN | 276 |
| `strlen` | the `${...}` vars helpers (not a search) | — | 45 |
| `memrchr`, `memmem` | none | — | 0 |

**Existing denies that touch these:**
- `--memfn=no-precheck-assign-byte`: the handoff's ASSIGN falls to `generic`, which is libc-free.
- `-fno-run-overlap` (bit 43): MORE `memcmp`, not less.
- `-fno-offset-skip` / `-fno-run-prefilter`: the OFS rows fall to the `memchr`/`byte-class` rows.
- `-fno-start-set`: today's no-scan arm for the VM hat and the DFA hat.
- `-fno-req-byte` / `-fno-req-run` / `-fno-req-set-lead` / `-fno-req-handoff`: remove the PRE family.

**No deny reaches the plain `memchr`/`memchr-bounded` prefilter rows or
MLINE's `pred-memchr`.** There is no kit-wide libc deny.

How a "libc suppressed" deny would fall back. Its rows are derivable as every
row that calls `mf_art_note_libc`.

| site | fallback today | gap |
|---|---|---|
| PF one-byte | `generic` (a FIND byte loop), or, with F1's table offer, `pf_walk`/`pf_terms_mask` (a one-term cover) | none, given F1 |
| MLINE | **none**: MLINE's `on_miss` is LOOP_EXIT (`break;`), a class the generic row never serves (RULED Q-R7-3, m4_report.md); `pf_memchr_back` is the only row for the shape | a libc-free back FIND row is needed (K5) |
| PRE / set-leads / handoff | `generic` (ALL_PRESENT, ASSIGN) | none |
| OFS / run-pinned FUNC | **none**: `fn_rows` BODY has only `fn-pair` and `fn-memchr`, both memchr; `generic` is not a BODY row | a libc-free BODY row is needed (K5) |
| VERIFY / VMRUN | `overlap` for 3, 5-7 and 9-15 | **lengths outside that set**: `memcmp` is the total fallback, so a libc-free exact compare is needed (K5) |

The libc row's measured constants carry `libc:<name>@<version>` in their
measurement-set provenance (D166). No libc row has a measured constant
today: R17-b′ §3.3 reads "R0 + R7 under today's data".

## 5. MLINE specifically

**Today** (`emit_attempt`, the guard at :12967, the site at :12977):

- pcrec writes the CONTEXT CHECK `if (start > X && subject[start - 1] != '\n') {`.
  X is `search_from` under a `\G` family, else 0. That X is the [M6.2]
  wave D lost-match rule, sabotage S82.
- Inside it, the kit's `pf_memchr_back` site: FIND/STMT/ASSIGN over `{\n}` at
  offset −1, floor `start`, `empty` AT_N, `on_miss "break;"` (LOOP_EXIT), and
  result = hit + 1.
- `attempt_cand` (:4352) is "memchr-or-nothing by charter". It derives the set
  generally, and `use_memchr` gates it. The set is always one byte today,
  because `\b`/`\B` keep a view alive.

**What the `\n` stop plus the context check needs:**

1. The edge stays pcrec's: offset 0, and `startpos` under `\G`. The check reads
   `s[start - 1]` and is only in range because `offset >= 1`.
2. The site is a context predicate, NOT a span. `window_contract.md` §2.4/§2.5
   (D161 add. 7) spells it `move_back −1 / overshoot 0`, "stream from
   edge + 1; candidate = the hit + 1; the edge is pcrec's". So it fits D161
   add. 3's FIND shape as the context-predicate degenerate case, which is
   already designed.
3. The kit needs F4 (the consumer: an ATTEMPT predecessor seek) to tell MLINE
   from a forward PF.
4. A libc-free row (§4): none exists today, since generic never serves LOOP_EXIT (Q-R7-3).
5. Nothing more for a zero-mover move: R-7/M4 already delegated the site.

**What Frank would be confirming:**
- (a) MLINE is "a single-byte search site" under addendum 14, so the kit's
  table may also pick NONE for it. That pick is answer- and give-up-safe
  (§2: an ENG_ATTEMPT attempt has no budget). Its cost is one dispatch per
  non-candidate start, plus the quadratic crossing arm (§3.7.1), which D63
  already does not rescue.
- (b) The context check and the edge stay pcrec's text.
- (c) The population is 23 of the 172 compiling rwquest questions (the ruling
  says 24 of 177), 52 corpus and 2 bench.

## 6. Requests and work, sized

### 6.1 pcrec-side (facts only, D157; for main to file as R-n)

| id | request | sites (DELEG_SITES / manifest) | size |
|---|---|---|---|
| P1 | state the PF/VM-hat candidate set as a SET term at every count, with the table offer (F1). Needs R17-a's `reads_table` on main | PF (all NEXT rows on CR_DFA, the hybrid prefilter, the VM hat) | S |
| P2 | state the miss/guard behaviour as hooks rather than text (F2, F3: `empty` + `on_miss`, the bounded wrapper, an in-guard "after" text for the DFA hat's re-seed) | PF | M |
| P3 | state the consumer kind (F4) | PF, MLINE | S |
| P4 | state the effort fact (F8): the site removes attempts of a budgeted engine | PF (VM hat), PRE (no-scan VM route) | S |
| P5 | read the kit's form class back at define time, and re-point the six §1.4 readers at it: G1, R4, the K admission, `landing` L4, the stamps/`rx_info`, `<string.h>` | PF, PRE (G1), MLINE (`<string.h>`) | M |
| P6 | state the prior's mass for each term (`ppm_lo`/`ppm_hi`, today `[0, 10^6]`) | PF, MLINE, PRE | S |
| P7 | rename the method-named fact `DFA_PF_MEMCHR`/`use_memchr` to the count it is, and make the stamp values pcrec's row identities (F7) | PF | S, no byte |
| P8 | move the PF comment into the kit or make it method-neutral (F6) | PF | S |

### 6.2 Kit-side work list

| id | work | size |
|---|---|---|
| K1 | the candidate-finder table gains the one-byte rows: a libc `memchr` row (with its `libc:` provenance), libc-free one-byte forms (`pf_terms_mask` over a one-term cover already applies when `decl_point` is offered; a walk; SWAR) and a NONE row gated on F8 | M |
| K2 | the default no-data row set reproduces today's rule (§3); R7 LINER excludes one-member covers, or is ruled to be the libc row there | S (+ a ruling) |
| K3 | the rows render the guard, post-test and bounded wrapper themselves (P2) | M |
| K4 | `mf_result` reports the form class at `mf_define` (P5) | S |
| K5 | the libc class deny (`--memfn=no-libc` or a derived class), plus the three missing libc-free rows: an OFS BODY row, a back FIND for MLINE's LOOP_EXIT shape, and an exact compare for every length | M |
| K6 | G2: the one-byte families, NONE answer identity at DFA consumers, NONE refused where F8 holds, and MLINE's generic fallback shape | M |
| K7 | the PF comment (P8), if it moves | S |
| K8 | measurement sets: the libc row's constants keyed `libc:<name>@<version>` (D166), and whether NONE ever pays on a DFA consumer, which is Frank's point 2 and has no measurement today | L |

**Sequencing fact.** P1+P2+P3+P5 with K1-K4 is the zero-mover event. The NONE
row (P4, K1's NONE, K6) is a separate event. So is the libc deny (K5).

## 7. Population (census `docs/dev/lanes/sbscope/census.py`)

**Method.** Each artifact is compiled `-p rx --features all -o -` with main's
`build/pcrec`, and its stamps are read off the emitted text. Corpus: every
`pattern`/`pattern-esc` line, enumerated by `emit_sweep.enumerate_corpus`.
Default flags apply, as in emit_sweep: a block's own encoding and flags are not
used. Bench: `bench/*/patterns/*.rx`, with the utf8 set under `-e utf8`.
rwquest: the flags are mapped (`i`→`-i`, `utf`→`-e utf8`, `ucp`→`--ucp`,
`m`/`s`→ an inline prefix).

**Results.** `census_summary.txt` has the full output, and
`rwquest_forms.tsv` has one row per question.

| population | compiles | ok | ≥1 single-byte search | ≥1 start site |
|---|---|---|---|---|
| corpus | 5,790 | 5,336 | 1,790 | 3,369 |
| bench | 367 | 343 | 74 | 278 |
| rwquest | 177 | 172 | 74 | 170 |

The 5 refused rwquest rows (N06, N11, N12, N13, N25) are UCP `\b` under utf8,
which is not built (U3/U4). 56 corpus artifacts are COMPOUND; their parts are
not inspected.

### 7.1 Per class (artifact counts; one artifact can be in several)

| class | meaning | corpus | bench | rwquest |
|---|---|---|---|---|
| SB-PF-DFA | `memchr`/`memchr-bounded`/`first-memchr-bounded`, DFA body | 581 | 35 | 16 |
| SB-PF-HYB | the same rows, inside a VM hybrid's prefilter | 626 | 8 | 18 |
| SB-MLINE | `pred-memchr` | 52 | 2 | 23 |
| SB-PRE | a one-byte presence pre-check (`emitted`, no run) | 648 | 29 | 19 |
| SB-HANDOFF | the handoff whose landmark is the one byte | 226 | 6 | 6 |
| SB-VMHAT-1 | the VM hat at \|S\| = 1 (a table walk on main, Q-R5) | 112 | 8 | 1 |
| OFS-DFA / OFS-HYB | `offset-set*`/`run-pinned*`: a one-byte scan at k*, its body the kit's memchr rows | 349 / 318 | 69 / 15 | 38 / 8 |
| SET-PF-DFA / SET-PF-HYB | `byte-class*`/`first-class-bounded` | 764 / 241 | 102 / 16 | 29 / 8 |
| SET-VMHAT | the VM hat, any size | 257 | 17 | 5 |
| NEXT-HANDOFF | the re-entered handoff row | 181 | 14 | 25 |
| RUN-PRE / RUN-HANDOFF | a run pre-check / run landmark | 341 / 264 | 58 / 46 | 76 / 50 |

DFA candidate-table sizes in the corpus (`can_begin_match`/`start_bytes`):
| set size | 2 | 3-4 | 5-8 | 9-16 | 17-64 | 65-255 |
|---|---|---|---|---|---|---|
| tables | 319 | 90 | 48 | 91 | 201 | 256 |

VM hat tables in the corpus:
| set size | 1 | 2 | 3-4 | 17-64 | 65-255 |
|---|---|---|---|---|---|
| tables | 112 | 62 | 5 | 57 | 21 |

### 7.2 The 172 compiling rwquest questions by START form (one each)

| start form | questions |
|---|---|
| one-byte prefilter (SB-PF) | 34 |
| MLINE | 23 |
| offset/run row (OFS) | 46 |
| set walk (SET-PF) | 37 |
| handoff re-entry | 25 |
| VM hat | 5 |
| none | 2 |

Single-byte search anywhere in the artifact (any SB-* class): 74. SB ∪ OFS:
120. libc `memchr` in the artifact: 143.

### 7.3 The ruling's "92 of 177"

Not reproduced. Candidate definitions give 74 (SB-*), 120 (SB ∪ OFS),
143 (`RX_MEMFN_LIBC` ∋ memchr), 57 (one-byte PF + MLINE start forms)
and 103 (with the OFS start forms). The ruling's "24 of 177" MLINE count is 23 here, out of 172 that
compile. The source of 92 should be named before it is cited again.

## 8. Standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime:** relevant only to K8. Every number here is a compile
   census with no timing.
2. **Independent control:** the census reads stamps the compiler writes, so the
   classes inherit the stamps' meaning. The F7 finding is the caveat: on the
   kit branch the stamp names pcrec's row, not the kit's form.
3. **What moves when data is regenerated:** nothing at the zero-mover step. A
   NONE or libc row reading measured constants moves only with a ruled set
   change (D166).

## 9. Files

- `docs/dev/lanes/sbscope/census.py` — the census (self-documenting header)
- `docs/dev/lanes/sbscope/census_summary.txt` — its output at main `711cf603a` / bench `25480b47`
- `docs/dev/lanes/sbscope/rwquest_forms.tsv` — one row per rwquest question
- `docs/dev/lanes/sbscope/CLAUDE.md`
