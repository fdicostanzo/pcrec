# winreq — ONE window-request list for D161 addendum 14 (single-byte FIND + presence + handoff, merged)

Lane `winreq`, 2026-10-14 (docs only: no `src/` or `memfn/` edit, no build, no timing).
Branch `lane/memfn-winreq`, cut from `lane/memfn-r17`. Inputs: `sbscope_report.md`
(main `711cf603a`, abi 78), `pcscope_report.md` (main `4e6464777`), the kit's last
notices (`memfn/docs/responses.md`, incl. sbscope's CORRECTED coverage), `r17b_prime.md`,
and, read from main: D157, D158, D161 add. 1-14, D162, D165, D166,
`window_contract.md` (rev 2.1), `litscan_k82b.md`, requests R-18 (on this branch) and
R-19/R-20 (**main only**: this branch's `requests.md` stops at R-18). File:line cites are
the scoping lanes' (main `711cf603a` / `4e6464777`); re-grep at filing.

The three rulings this list serves: (a) single-byte sites are the kit's (D161 add. 14);
(b) the presence pre-check and the candidate find are ONE window request, EMPTY = NOMATCH,
K65-class give-up conversions preserved; (c) "it can decide to include the prescan or not
based on the information sent": the pre-scan is a ROW in the kit's knowledge-filtered table.

## 0. Answers first

| | count |
|---|---|
| pcrec-side items (§1) | **11**: 7 facts, 3 pcrec-side changes, 1 control (+ 4 dependencies already filed or contract-owned, not new) |
| kit-side items (§3) | **13** |
| contract-revision items (§4) | **16** |
| rulings (§5) | **12** (Q-PC-1..4 folded in) |
| sabotage ids (§7) | **17** needed; at most 10 fit S871-S880, 0 fit S911-S922 |

Four findings the merge produced (the reports do not state them):

1. **sbscope's "effort fact" (F8) IS pcrec-side `need`.** window_contract §2.4 rule 4 already says an
   all-positions stream is legal iff no span is REQUIRED. `need = REQUIRED` on span 0 (VM hat) is the
   effort fact; NONE's safety per consumer needs no new field (PR-4).
2. **sbscope's "consumer kind" (F4) IS R-19's `site_kind`, which R-19 GATES** on [REGIME-LANDINGS]
   (D77). The zero-mover one-byte step needs it NOW (Q-R5 at |S|=1, MLINE), and the contract's S3
   retires the unread `mf_site.consumer`. Both need a ruling (Q-WR-8).
3. **sbscope P6 (state the prior's mass per term) is dead on arrival:** D162 add. 3 and contract S3 retire
   `ppm_*`; the analysis object's always-present frequency kind replaces it. It is dropped to dependency E-1.
4. **The pre-scan row cannot be priced from E, N, M alone.** A discard gate pays only by rejecting
   (`litscan_k82b.md` §0.3), and what rejection saves is the CONSUMER's per-byte scan cost: a consumer
   price, which D161 add. 6 dropped (§2, Q-WR-9). Until a price exists the row's total default is KEEP.

## 1. ONE pcrec-side request list (facts only, D157)

### 1.1 Dedupe (new id → source ids)

| new | sbscope | pcscope | note |
|---|---|---|---|
| PR-1 | P1 | | |
| PR-2 | P2 | | F2 + F3 (guard, post-test, wrapper, re-seed placement) |
| PR-3 | P3 | P5, P6 | consumer kind + one-start + body-decides-presence + skip-barred; widens R-19's GATED `site_kind` |
| PR-4 | P4 | P2 | effort fact = `need` per span (finding 1) |
| PR-5 | | P1 | |
| PR-6 | | P3 | |
| PR-7 | | P4 | |
| PR-8 | | P7 | |
| PR-9 | P5, P7 | P9 | form read-back + stamp spelling + rename + stamp source |
| PR-10 | P8 | | |
| PR-11 | | P8 | a CONTROL, not a fact |
| (dropped) E-1 | P6 | | contract S1 / D162 add. 2-3; not a new request |

17 source ids = 16 mapped to 11 items + 1 dropped. Not listed again because already filed or owned elsewhere:

| dependency | cited at | status |
|---|---|---|
| `mf_site.body` (call mode) and the start hook | **R-19** (main `requests.md:418`) | filed 2026-10-14, acked; pcrec's presence builders (`req_site_define` `:1532`) and MLINE (`:12977`) are "builders" and must state both: confirm R-19's "every builder" covers them; the PRE composite's storage point (`:1648`, `emit_vm.c:13214`) is not one of R-19's three FIND points |
| `mf_measures`, `consulted`, form hash, reader declarations, method cards | **R-20** (main `requests.md:434`) | filed; the libc row and the pre-scan gate need cards under R-MS5 (KW-12) |
| E-1 `mf_analysis`: byte-rate kind, always present, with provenance | window_contract S1 / D162 add. 2-3 | unbuilt on every branch; a pcrec abi event; PRECEDES PR-5..PR-7's ST3 |
| spans for every bounded span relative to the origin | **R-18** (`requests.md:392`) / `span_facts` producer | the presence class is the part R-18 does not cover (it says "presence sites carry no window", superseded by add. 14's clarification) |

### 1.2 The list

Steps (the "trigger" column): **ST1** facts stated, shadow comparator, zero movers; **ST2** one-byte rows
replace, zero movers; **ST3** presence + handoff replace, zero movers; **ST4** pre-scan row priced (a mover,
its own abi event); **ST5** libc deny; **ST6** R17-b′ dispatch rows.

| id | kind | the fact | where pcrec has it today (main) | size | trigger | D157 check |
|---|---|---|---|---|---|---|
| PR-1 | fact | the candidate set as a SET term at every count (one member included), plus the table offer, on every PF/VM-hat site | `cand_derive` `emit_dfa.c:4290` (`use_memchr = count == 1`); term encoding `:6505` (`PF_SCAN_BYTE` → `term_byte`, no table); `find_site` `:6443`, `pcrec_emit_find` `:6490`. Kit side: R17-a `reads_table`/`includes` on this branch | S | ST2 | OK: states the set and that a table exists. Today's one-member `term_byte` encoding IS a form choice; removing it is the fix |
| PR-2 | fact | the miss and move behaviour as hooks: what the consumer needs when the subject is at or past `n` (`empty` + `on_miss`), the bound `n - 1` for bounded rows, a hook that runs when the candidate differs from the start (the DFA hat's re-seed `skip_from`) | guard BEFORE memchr `:6536`; test AFTER walk `:6570`; wrapper `:6556`, `:7233`; re-seed `pf_emit_moved_reseed`; `if (attempt_position >= n) return 0;` for the VM hat | M | ST2 | **REWORDED.** sbscope worded F2/F3 as text pcrec "places inside the kit's guard", which presumes the kit has a guard. Stated as consumer facts (empty-at-n, bound, "if moved, then X"), the kit places them |
| PR-3 | fact | the consumer kind: DFA forward scan / DFA hat / hybrid prefilter / VM attempt seek / ATTEMPT predecessor seek; plus, from pcscope: one start (BOUND `one`), body decides presence (LOCATE `whole`), skipping barred (`use = DISCARD`) | `MF_C_ENGINE` for every PF/MLINE site (`memfn_sites.c`); G2 `req_route_one_attempt` `:7623`; `whole` `:7664`; Q10 collapsed hybrid `:7843` (`use` exists) | M | ST2 (kind), ST3 (rest) | **REWORDED.** sbscope's "reproduces Q-R5 (VM hat keeps a table at \|S\|=1)" names a form; the fact is the kind, the default row reproduces Q-R5. Alternative for the pcscope half: pcrec withholds presence there (Q-WR-4) |
| PR-4 | fact | `need` per span: REQUIRED exactly where dropping, narrowing or answering unconstrained over the span could let a budgeted engine do more work on an input the denied build answers; OPTIONAL elsewhere. Covers pcscope P2 (no-DFA-scan routes incl. framed one-attempt VM per K64) and sbscope F8 (VM hat span 0, no-scan VM pre-check) | `pcrec_artifact_has_dfa_scan` `:469`; gate need at `req_site_define` `:1532` (set-leads lead OPTIONAL on a DFA-scan route, REQUIRED otherwise; every other predicate REQUIRED) | S | ST3 (presence), ST4 (NONE) | OK: a fact about the consumer. D158 is its source |
| PR-5 | fact | presence spans UNPICKED: every necessary-set member as its own one-byte presence span, and the whole run with its mask, each with `need` (not just the pick and the prior-cut window) | pick `req.c:709`; window `req.c:667`; whole run + mask + `whole_maxoff` `req.c:638`; sent today: the pick, the window, and (no-DFA routes only) K65 rest `:1413`, K66 whole `:1112` | M | ST3 | OK. Keep `req_set` asked only where today asks (the `--emit-facts` `used` column, Q-WR-12) |
| PR-6 | fact | offsets relative to the chosen origin: `req_set_maxoff`, `whole_maxoff` as offsets; K as `h_max`; presence `omin` (NEW walk half; 0 is a sound under-estimate) | `req_set_maxoff` `req.c`, `rb_union` `:189`; `req_landmark_maxoff` `req.c`; omin does not exist | M | ST3 (omin 0), ST4 (true omin) | OK |
| PR-7 | fact | each set member's position in pattern order (the order the leftmost/rightmost distinction reads) | `rightmost` in `pcrec_find_set_pick` `findings.c:476` (tiebreak) | S | ST3 | **REWORDED.** pcscope called it "the tiebreak", a pick rule (method). Stated as a per-member order fact; if PR-6's per-member offsets are sent it may be derivable and PR-7 retires |
| PR-8 | change | emission order: the presence verdict is decided before pcrec's context-edge attempt (`(?m)^` at `search_from`/0) | today's order: pre-check at the entry; edge attempt after (`emit_dfa.c:12376` region) | S | ST3 | OK: an obligation on pcrec's text, not a kit statement. Witness W2 |
| PR-9 | change | pcrec's readers of the scan FORM read the kit's define-time result stated as facts (which bytes the scan proves, whether a scan precedes the engine, the includes), not a form name: G1 (`dfa_cand_scan` `:7515`, `req_byte_dominated_by` `:7664`), R4 (`pcrec_dfa_cand_ppm` `:7561`), the handoff K admission (`req_landmark_admits` `:7920`), `landing` L4 (`start_landing_applies` `:8544`), `<string.h>` (`:13485`), the stamps (`dfa_prefilter_name` `:13935`, `REQ_BYTE` `:13659`, `REQ_RUN`, `REQ_WHY` `:13713`, `REQ_HANDOFF` `:13722`), `--emit-facts` `used`/`why`, the trace records, and the `--list-axes` `req-admit`/`req-use` rows. Also: rename the method-named count fact (`DFA_PF_MEMCHR`, `use_memchr`) to the count it is; stamp VALUES stay pcrec row identities | as listed | M | ST1 (shadow), ST2/ST3 (switch) | **REWORDED.** sbscope/pcscope call the result a "form class", which names a method. G1's need ("the scan tests byte b") IS window_contract's PROVEN-facts statement (D161 add. 8); `<string.h>` is R17-a `includes`. Stamp source: pcrec shadow through ST3, then a kit result with identical values |
| PR-10 | change | the PF comment (`pf_comment_memchr` `:6387`, "one memchr() replaces the steps") made method-neutral, or moved to the kit | `:6387` | S | ST2 | OK once neutral. `-fcomments` moves unless the kit renders it (Q-WR-11) |
| PR-11 | control | the claim "every DFA-scan front enforces the necessary set and run" checked as a census over collapsed hybrids, with a planted collapse that drops `rmin` | argument + one probe only (`nfa.c:803`, `:818-821`; W4) | M | ST3 (gates PR-4's OPTIONAL) | not a fact, a pcrec check. Share no source with the walk (learnings §3) |

## 2. The knowledge that PRICES the pre-scan row (ruling c)

The row's candidates: **fused** (the scan's hit is handed on as the candidate, `litscan_k82b.md` twin T3), **discard
gate** (the hit is thrown away), **none**. Fused costs nothing extra and needs no price (the landmark is a span with a
bounded head). **None** is legal only where `need` is OPTIONAL (§0 finding 1). The row is a real choice only for a
presence span that is OPTIONAL and not on the candidate path (unbounded offset): the discard gate against none.
Population at default (pcscope §7): 420 corpus artifacts emit a presence check, 248 are give-up-exposed, so **172
are OPTIONAL-capable** (132 one byte, 40 run window); utf8 443 / 256 / 187; `--engine=vm` 0 (all 2,299 exposed);
rwquest **38 of 39** (only M04 is exposed). The row is rare on the corpus and common on the blinded population.

Notation clash: the regime key **E** is the analysis object (frequency + landings); `litscan_k82b.md` writes **E** for the
engine's ns/B. Below, **E** is the key and **e_eng** the engine cost.

| knowledge | prices | pcrec has it TODAY? | NEW? | producer |
|---|---|---|---|---|
| **E: frequency of the necessary byte / set member** (absence probability over N is `(1-rho)^N`, `x = rho*N`) | rejection chance | **Yes inside pcrec:** `pcrec_find_byte_rate(cx)`, the shipped `src/findings/default.rxt` prior, bundles via `--analysis`. **No at the kit:** a set FIND site gets nothing; RUN sites get `rank_*` (retiring at S3) | the OBJECT is new | window_contract S1 `mf_analysis` (always present, D162 add. 2). Provenance `prior-authored` / `prior-none` / `measured`: the kit reads only `measured` as evidence (D162 add. 3). **Under `-e utf8` the kind is `prior-none` with no table** until [U8-PICK]/D160 lands (§3.2 of the contract) |
| **E: rarity of a necessary RUN** (markov1) | rejection chance for run presence | **No.** NONE answer is cardinality; the prior is off ~12,000x on `(?i)cat` (k82b §0.2); bundles carry no bigrams | NEW | [REGIME-LANDINGS] / [FINDINGS] B4: the `run-rarity` kind (contract §0.8 moved W10 here); pcrec-analyze counts bigrams already |
| **E: landings** (joint rates per stop, predictability) | multi-position stops, burstiness | **No** | NEW, gated | [REGIME-LANDINGS] (not started). Predictability is filed, trigger = a cell flipping on it (D161 add. 11) |
| **N, the call span** (`n - start`) | the gate's scan length W | **No at the kit.** pcrec has the text at the three FIND storage points | NEW at the PRE composite's entry | R-19 start hook, extended to `emit_dfa.c:1648` / `emit_vm.c:13214`. In find-all through `_search` N is the REMAINING subject (r17b′ §2.4), so a discard gate re-reads it every call (k82b: "W is decisive") |
| **M, the call mode** | whether a verdict can be amortised | **No** (presumed) | NEW | R-19 `mf_site.body`: ONESHOT now, ITER from the D165 `next` body |
| `need`, bounded-offset-or-not, K (P) | whether the row is legal and fused | partly (§1) | NEW as kit-visible | PR-4, PR-5, PR-6 |
| **e_eng, the consumer's cost per byte on this route** | what a rejection saves | **No.** k82b §1.3: "no calibration exists", "the weak term" | NEW, **a consumer price** | none: D161 add. 6 dropped consumer price; add. 11 filed it with trigger "a TUG cell measured losing for want of it". Q-WR-9 |
| the kit's own `f`, `beta`, `s` for memchr / the libc row | the gate's own cost | not pcrec's | NEW | the kit's D166 set. r17b′ §3.2's 18 quantity families hold NONE for memchr or a pre-scan gate (KW-12). k82b's Mac/Linux numbers are method-mixed, not a set |

**State bytes to carry "present" across `next` calls** (M = ITER). What soundness needs is not a bit. A verdict
"span occurs at p >= lo" stays true only while `lo + omin <= p` (pcscope §3.3: the range reply `hi' = p - omin`,
minimum over the REQUIRED spans); past it the next call must re-verify. So one `size_t` (8 B) is needed.

| layout | bytes (align 8) | padding | verdict |
|---|---|---|---|
| D165 add. 1: `base`, `top`, u64 mask | 24 | 0 | three full words |
| + the kit's previous-span word (r17b′ §8, D161 add. 11 item 3.4) | **32** | 0 | the kit's proposal |
| r17b′ §8's own wording "24 B cache + the form byte ... plus the previous span" | 33 -> **40** if the form byte lives in the buffer | 7 | **a single flag bit fits this padding for free, but a bit is insufficient (above)**; §8's "= 32" holds only if the form byte is recomputed per `next` |
| 32 + presence `valid_until` | **40** | 0 | the cost of carrying the verdict |
| 40 + the form byte in the buffer | **48** | 7 | the worst case |

S is a public-header constant and raising it is an abi event (D165 item 4); zeroing is the row's declared bytes,
not a memset of S (item 5). `rx_iter`'s own fields (`rc`, `lo`, `s`, `n`, the validity word) are not designed and
sit outside S. **Whether the kit carries presence at all is its method (D157);** pcrec's facts are `body = ITER`
and S. Without the carry, find-all re-verifies presence per call over `[lo + omin, n)`: walk_survey's K5 quadratic,
the thing Q-PC-4 would remove (Q-WR-6).

**Total default (D162 ruling 2).** Row conditions that need `measured` E, N or `e_eng` skip when absent, exactly as
r17b′ §3.4's rows do. The row that decides with none of them is today's rule: KEEP the pre-scan. A dispatch row that
would compare N must pay for its compare (r17b′ §2.5), and the two quantities that decide it (M16/M17) are ABSENT
from every run, so no N-dispatch is emitted today. The pre-scan row is `needs {P, E, A, N, M}`: with E prior-only it
reads KEEP at compile time.

## 3. ONE kit-side work list

| id | work | source | size | note |
|---|---|---|---|---|
| KW-1 | candidate-finder table gains the one-byte rows: the libc `memchr` row (with its `libc:<name>@<version>` provenance), libc-free one-byte forms (`pf_terms_mask` over a one-term cover applies once `decl_point` is offered; a walk; SWAR), and a NONE row legal under KW-6's applicability rule | sbK1 | M | NONE needs PR-4; MLINE's `pf_memchr_back` is the only row for the back-FIND shape (Q-R7-3) |
| KW-2 | default no-data rows reproduce TODAY's rule (one member and not a VM attempt seek -> the libc row; else the set form). R7 LINER excludes one-member covers, or is ruled to be the libc row there | sbK2 | S + ruling | Q-WR-1. Neither R17-b′ nor R7 has a memchr or NONE form |
| KW-3 | rows render the guard, post-test, bounded wrapper and the moved-hook text themselves; the PF comment moves or is method-neutral | sbK3, sbK7 | M | PR-2, PR-10. `-fcomments` is the only arm that moves |
| KW-4 | `mf_result` reports at `mf_define` what pcrec's readers need: bytes proven, whether a scan exists, the includes | sbK4 (+ pcP9) | S | PR-9. The contract's PROVEN facts (add. 8) are the carrier |
| KW-5 | the PRESENCE span class in the window site: field spelling, refusal rules, `MF_SITE_ABI` bump, G2 refusal cases | pcK1 | M | contract C-1, C-2. `MF_MOVE_UNBOUNDED` stays permanently refused |
| KW-6 | stream obligations G-1 (empty => NOMATCH for REQUIRED spans), G-2 (decided before the first element), the range-form unconstrained reply, and the APPLICABILITY rule (K96): a row that drops, narrows or answers unconstrained over a REQUIRED span does not apply | pcK2 | M | the same rule gates KW-1's NONE row |
| KW-7 | default rows reproduce the PRE composite (`precheck`, `precheck_assign`, `precheck_assign_byte`) inside the merged site at its several uses (entry, re-entry, VM `_run`, in-loop find), zero movers | pcK3 | L | one request, several uses; `mf_locals` already gives one handle |
| KW-8 | port pcrec's five prior-priced picks verbatim, with a shadow comparator: set pick (with member order), run scan index / window start, set-leads, G1 (identity / `run_verified` / density), landmark admission | pcK4 | L | needs E-1 first or a NULL analysis would move bytes (D162 LINER) |
| KW-9 | the libc class deny (`--memfn=no-libc` or a derived class) and the three missing libc-free rows: the OFS BODY row, a back-FIND for MLINE's LOOP_EXIT shape, an exact compare for lengths outside `overlap`'s | sbK5 | M | Q-WR-7 |
| KW-10 | G2 families: one-byte (count rule, NONE answer identity at DFA consumers, NONE refused where `need` REQUIRED, MLINE generic shape) and presence (absent-at-end lazy discovery, REQUIRED-all on proof routes, re-asked ranges with `omin < 0`) | sbK6, pcK5 | L | plants must reach NON-DFA routes (a DFA-route-only green is vacuous, §2.1) |
| KW-11 | a `--memfn=no-...` option for the set-leads row; registry floor moves | pcK6 | S | `-fno-req-set-lead` is the pcrec deny it replaces (Q-WR-12) |
| KW-12 | measurement sets: the libc row's constants keyed `libc:<name>@<version>` (D166); the pre-scan gate's quantities (`f`, `beta`, `s`, and a route cost if Q-WR-9 allows); whether NONE ever pays on a DFA consumer (Frank's point 2, no measurement today) | sbK8 | L | method cards under R-20's R-MS5. The first embedded set needs a new run (`zen4-grid2`, r17b′ Q-R17P-7) |
| KW-13 | **the pre-scan row itself:** `needs {P, E, A, N, M}`, candidates fused / discard gate / none, total default KEEP, price from `measured` E only | ruling (c) | M | NEW; conditions per §2 |

Counts: 13 items (14 source ids merged, one new). Sequencing fact from sbscope: P1+P2+P3+P9 with KW-1..KW-4 is
ONE zero-mover event; the NONE row (KW-1's NONE, KW-6, KW-13) and the libc deny (KW-9) are separate events.

## 4. Contract revisions: `window_contract.md` (rev 2.1 on main) as ONE list

| id | section | change | from |
|---|---|---|---|
| C-1 | §2.2 | add the PRESENCE class beside "bounded span" and "context predicate": it carries `omin`, has NO `omax`, and has its own binding rule. Split "below the origin" into necessary-before-origin (a bounded negative offset) and CONTEXT | pcscope §3.1, §4 |
| C-2 | §2.3 | carve presence out of the "bounded only" rule as its own class; `MF_MOVE_UNBOUNDED` and `window_stated 0` stay refused | pcscope §3.1 |
| C-3 | §2.4 | delete the `ALL_PRESENT -> VERDICT` row; add (i) range binding, EMPTY => NOMATCH, (ii) G-2 decided-first, (iii) per-candidate use as a PERMISSION, (iv) the range form of an unconstrained reply (`hi' = p - omin` per REQUIRED span). "A bounded span's presence is part of FIND" becomes "every span's presence is part of FIND" | pcscope §3.2-3.3, §4 |
| C-4 | §0 item 2 | delete "Presence sites keep the VERDICT reply" | pcscope §4 |
| C-5 | §2.5 table | rewrite the "run pre-check (unbounded offset) -> VERDICT" row and the K82/L1 row (origin = the landmark, framing (a)) | pcscope §3.4, §4 |
| C-6 | §5.4a | T-PRES superseded: `dominated` becomes the kit's, `presence` stops being a separate site, `none` stays pcrec's sub-problem choice (or is the kit's per PR-4/Q-WR-4) | pcscope §4 |
| C-7 | §11 and R-18 as filed | the R-18 outline and `requests.md:392-416` ("presence sites carry no window", "serve every degenerate site") change in step; ledger edit is main's | pcscope §4 |
| C-8 | §13 unlock (c) | "presence as a chain link" is now the contract; its trigger dissolves | pcscope §4 |
| C-9 | §2.3 (new rule) | the APPLICABILITY rule for REQUIRED spans (KW-6) | pcscope §4 |
| C-10 | §2.4 / §10 | a per-consumer statement of G-5's give-up direction (Q-WR-3) | pcscope §2.2 |
| C-11 | §7 (S3 retirement list) | do not retire `mf_site.consumer` without its replacement: PR-3's kind. Today it states `MF_C_ENGINE` everywhere and is unread; `need` per span carries the give-up fact, a kind carries the rest | pcscope §4, sbscope F4 |
| C-12 | §2.4 (new table) | NONE's safety per consumer: answer- and give-up-safe on DFA PF, DFA hat, the hybrid's inner prefilter and MLINE (ENG_ATTEMPT has no budget); NOT on the VM hat or the no-DFA-scan VM-route pre-check (GIVEUP1 groups F5, E, F). It follows from rule 4 once PR-4 states `need`; the table is the worked statement | sbscope §2 |
| C-13 | §5.5 or §2.3 | the VM-route EXCLUSION: a site on a route with no DFA scan carries REQUIRED presence (K64/K65/K66) and a REQUIRED VM-hat span 0 | sbscope §2, pcscope §2.1 |
| C-14 | §2.3 | the EFFORT fact is `need` (finding 1): one sentence tying REQUIRED to "could let a budgeted engine do more work where the denied build answers" (D158) | sbscope F8 |
| C-15 | §3.3 | an evidence-reading row (a priced pre-scan, D162 add. 1's density decline) reads only `measured` provenance; a `prior-*` kind selects the total default | ruling (c), D162 add. 3 |
| C-16 | §2.1 / §2.2 | the member order (PR-7) and per-member offsets (PR-6) as span fields, or noted derivable | pcscope P3, P4 |

## 5. Rulings needed (Frank / main), each with a recommendation

| id | question | recommendation |
|---|---|---|
| Q-WR-1 | The default no-data rows: reproduce TODAY's count rule (one member -> libc row, else set form) with an UNMEASURED-DEFAULT label, or R7 LINER (neither has a memchr or NONE form)? | Today's rule, labelled per D149 and `pcrec-no-silent-defaults`, replaced when a measured libc row exists (KW-12). LINER applies to covers of 2 or more terms. Zero-mover first |
| Q-WR-2 | MLINE (`(?m)^`, `pred-memchr`) in scope of add. 14? (main's extension, Frank to confirm) | Yes: it is D161 add. 7's context predicate and window_contract §2.5 already designs it; edge stays pcrec's. NONE for MLINE is answer-safe but pays one dispatch per non-candidate start and the quadratic crossing arm; no NONE row until measured |
| Q-WR-3 | G-5's give-up direction: D148 Q6 ALLOWS a stream to turn a give-up into an answer (start-set hat); the K82 handoff's Q10 FORBIDS any move, "no exception". One rule or per consumer? (= Q-PC-1) | D158 (2026-10-09, postdates both) is the single rule: answer -> give-up never, give-up -> answer allowed and direction-checked by GIVEUP1. Keep Q10's stricter posture for ST3 only (zero-mover cannot move either way) and relax it at ST4 per measured cell |
| Q-WR-4 | G2's structural decline and LOCATE `whole`: state as consumer facts (kit declines) or pcrec withholds presence there (sub-problem choice, add. 4)? (= Q-PC-2) | Withhold at ST3 (fewer fields, zero-mover either way). Add the facts when KW-13 needs them, which is where ruling (c) says the information should flow |
| Q-WR-5 | Handoff framing: origin = the landmark (a, zero-mover) first, origin = match start (b, a byte move behind its own deny) later? (= Q-PC-3) | Yes. (b) changes what the DFA consumes (a lower bound `c - K` today) |
| Q-WR-6 | Per-candidate cut-off (stream ends after the last occurrence - `omin`) as the find-all default: removes walk_survey's K5 quadratic; needs R-19 `body = ITER` and 8 more state bytes (§2: S 32 -> 40 B) (= Q-PC-4) | Yes as a PERMISSION the kit exercises, sequenced after the D165 build; S is raised once, with R17-b″'s 32 B |
| Q-WR-7 | RULED (Frank, via main, 2026-10-14): NOT a blocker. "there is no switch for libc-free yet. its not a priority but this gives it a path." | Recorded as REMAINING WORK FOR A FUTURE libc-free DENY (KW-9): the OFS FUNC BODY (`fn-pair`, `fn-memchr` are both memchr), MLINE's back FIND (LOOP_EXIT, a class the generic row never serves), and runcmp's exact compare outside the overlap lengths. When the deny is built, it is refused naming the site until its row exists (add. 14 point 4) |
| Q-WR-8 | `site_kind` is GATED in R-19 on [REGIME-LANDINGS]; sbscope F4 needs the consumer kind at ST2. And S3 retires `mf_site.consumer` | Ungate it for the kinds the ST2 default rows read (categorical, not a price); re-plan S3 so `consumer` is replaced, not dropped (C-11) |
| Q-WR-9 | The pre-scan row's benefit is the consumer's saved scan: a consumer price, which add. 6 dropped (add. 11 filed it, trigger "a TUG cell"). Price it, and with what? | Default KEEP unless `need` is OPTIONAL AND E is `measured`. Pricing waits for the trigger; if it fires, the cost enters as a per-route constant in the D166 set (a measurement, not a pcrec price), and add. 6 gets a dated addendum. No new pcrec statement |
| Q-WR-10 | Sequencing and baselines. R17-b′ gets a FRESH branch from a main containing R-19 (kit ack); lane/memfn-r17 stays the record branch (merge into main aborted at 17 conflicts). ST2's set-form baseline differs by branch: the VM hat at \|S\|=1 (112 corpus / 8 bench) is a table walk on main, `pf_terms_mask` on the kit branch | Land ST2 on main's baseline and treat R17-b′'s set-site move as its own abi event; ST3 after E-1. Two zero-mover events, not one |
| Q-WR-11 | `-fcomments`: the PF comment moves into the kit, or stays pcrec's, method-neutral | main's call (answer-free): make it method-neutral in pcrec (PR-10), accept no `-fcomments` byte move |
| Q-WR-12 | `--emit-facts` `used` column and the registry: sending the whole set everywhere flips `used` on thousands of artifacts; `req-admit`/`req-use`/`prefilter handoff` rows and `-fno-req-set-lead` move when their rows become the kit's | main's call: ask `req_set` only where today asks; flip the `used` column and the deny (to `--memfn=no-...`, KW-11) in the SAME commit as the row move, as a declared registry event |

## 6. Zero-mover feasibility, merged

Both scoping lanes find the step zero-mover at default flags. Preconditions, by step:

| precondition | ST2 one-byte | ST3 presence + handoff | source |
|---|---|---|---|
| E-1 analysis object first, with each encoding's NONE (byte-rate; `prior-none` under utf8) | not needed (count rule reads no E) | **required**: a NULL analysis makes D162's LINER default pick differently from today's prior-read picks | pcscope §5.1 |
| default rows port today's decisions verbatim, with a shadow comparator | the count rule (KW-2) | the five priced picks + K65/K66 as REQUIRED-all + gate `need` (KW-8) | both |
| use points kept (entry, re-entry, VM `_run`, in-loop find), one request with several uses | `pcrec_emit_find` sites | `emit_dfa.c:1648`, `:1690`, `emit_vm.c:13214` | pcscope §5 |
| facts F1-F7 / PR-1..PR-4, PR-9 stated or read back | yes | PR-4..PR-9 | sbscope §3 |
| origin = the landmark (framing a) | n/a | yes | pcscope §3.4 |
| stamps read pcrec's shadow, or a kit result with identical values | stamp VALUES stay row identities (F7) | `REQ_BYTE/RUN/WHY/HANDOFF` read pcrec's derivation | both |
| `-fcomments` | the PF comment is the only mover (PR-10) | n/a | sbscope F6 |
| `--emit-facts` `used`: ask `req_set` only where today asks | n/a | yes (Q-WR-12) | pcscope §5 |
| presence before the edge attempt (PR-8) | n/a | yes | pcscope W2 |
| baseline | untouched by R17-b: zero-mover against BOTH branches | main only; set sites moved by R17-b | sbscope §3 |

**Can never be zero-mover:** the `-fcomments` arm unless the kit renders the comment; the VM hat at \|S\|=1 (baseline is
whichever branch lands first); any NONE pick, by definition (ST4, separate event behind PR-4); framing (b) of the handoff;
the `--emit-facts` `used` column if the whole set is sent everywhere; the `--list-axes` `req-admit`/`req-use` rows and
`-fno-req-set-lead` when their rows move (registry event, no artifact bytes); any reordering that asks presence after the
edge attempt (W2); the compound route (`REQ_WHY "compound"`, 48 artifacts) is out of scope.

## 7. Sabotage id needs

**17 rows.** Every presence-side plant must reach a route with NO DFA scan in front, or it reads green vacuously
(pcscope §2.1; `learnings.md` §3 [MECH-REACH]).

| # | plant | detector | origin |
|---|---|---|---|
| SW-1 | K65-narrow: a REQUIRED set answered by one member on a non-DFA route | give-up (W1) | pc |
| SW-2 | K66-window: a REQUIRED run answered by its window only | give-up | pc |
| SW-3 | decided-late: a candidate yielded before all REQUIRED spans verified | give-up (G-2) | pc |
| SW-4 | edge-first: the edge attempt emitted before the presence verdict | give-up (W2) | pc |
| SW-5 | unconstrained on REQUIRED: an all-positions stream where span 0 is REQUIRED (also sbscope's "NONE on the VM hat") | give-up (W3, GIVEUP1 F5) | pc + sb |
| SW-6 | `omin` mis-signed | answer | pc |
| SW-7 | unbounded one-byte row loses its `pos >= n` guard | ASan over-read | sb |
| SW-8 | bounded row loses the `n - 1` clamp / wrapper | ASan | sb |
| SW-9 | the DFA hat's re-seed after a moved skip dropped | lost match (ssedge's mutants) | sb |
| SW-10 | VM hat at \|S\|=1 rendered with memchr per attempt | structural census only, declared (Q-R5, perf-only) | sb |
| SW-11 | the form read-back says "scan present" when NONE was chosen, so G1 drops presence on a proof-only route | give-up (K65) | sb |
| SW-12 | the `MEMFN_LIBC` stamp omits a libc symbol the rendered text still calls | C11 `nm -u` | sb |
| SW-13 | the libc row used under a stale `libc:` key | staleness listing | sb |
| SW-14 | MLINE stream opens at the edge, reading `s[start - 1]` at offset 0 | ASan | sb |
| SW-15 | the pre-scan row prices from a `prior-*` kind as if `measured` | listing / per-set manifest | new (ruling c) |
| SW-16 | a carried presence verdict not invalidated when `lo' > valid_until` | answer | new (§2) |
| SW-17 | member order swapped in a tie (PR-7) | shadow comparator, not answers | pc |

Fit against existing reservations (`requests.md` main, grep for "Sabotage ids"):

| block | owner | free for these? |
|---|---|---|
| S871-S880 (10) | R-18 (window site), pcscope says it "fits the obvious rows" | at most **10** (SW-1..SW-6 plus four), and only if R-18's own window-chain rows do not use them; R-18's build is behind this request |
| S911-S922 (12) | R17-b′ SB1-SB12 (r17b′ §6.5 fills all 12; R-19's rows are inside them) | **0** |
| S820-S843 | R-17 / R17-b / r17d | 0 (used) |
| S943-S963 | [MEASURE-SET] pcrec-side (R-20) | 0 |

Highest S-id cited in main's design docs is S963. Recommend asking main for a fresh block of **17** starting at S964
(verify against `tests/mech` and `worktrees/*/tests/mech` at filing, per BOILERPLATE); if S871-S880 stays free it
absorbs 10 and the new block shrinks to 7.

## 8. Standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime:** relevant to KW-12/KW-13 only. Every number here is a compile census from the scoping
   reports; nothing was timed. The pre-scan row cannot be priced from them (§2).
2. **Independent control:** PR-11 and SW-1..SW-6 are the controls that do not share a source with the walk (the
   census reads artifacts; the plants run non-DFA routes). The stamps-as-census caveat of sbscope §8 stands.
3. **What moves when data is regenerated:** nothing at ST1-ST3 (the default rows read no measurement). A measured
   libc row or priced pre-scan moves selections only with a ruled set change (D166).
