# kit_proof — [KIT-VERIFY] U1: REPORT WITHOUT AN ENGINE, with D161 addendum 16's context spans

Status: DESIGN NOTE, **revision 2.1** (lane `u1rev21`, 2026-10-18, main `fa322a7f6`,
abi 80, `MF_SITE_ABI` 16, `MF_CLASS_V` 3). Revision 2.1 applies the re-check of revision
2 (same review file, section "Re-check of revision 2", all ACCEPTED); its changed text is
marked `[r3rc <id>]`. Read §R2.1 first. Revision 2 was lane `u1rev` (main `542b0cecb`);
revision 1 was lane `u1design` (main `a016b3bfa`).
Revision 2 applies every disposition of the D6 panel
`docs/dev/reviews/2026-10-18-r3-kit-proof-u1.md` (k3-family, k3-contract, k3-sound; all
findings ACCEPTED by the manager). Nothing under `src/` or `memfn/` changes. Text that
changed is marked `[r3 <id>]`, where `<id>` is `fam-`, `con-` or `snd-` plus the
critic's finding id. Read §R2 first.

Evidence: single-pattern `build/pcrec` compiles at main `542b0cecb`, the committed
kvcensus run (`docs/dev/kvcensus.md`, pin `2523cfe4b`), revision 1's SIZE-ONLY twin
(`kit_proof/cover_twin.py`), and revision 2's own instrument `kit_proof/conj.py`. That
script is the `cover_conj[]` table of §1.1 written as code over the emitted anchored
machine. Its output is `kit_proof/conj.txt`. It re-counts every population this note
cites (§1.2) and gives the `-fno-rev-end` arm and the witnesses. Nothing was timed. The
k3-sound critic's differential (`worktrees/.scratch-u1exact/coversim.py`, read and left
unmodified) is the prototype of check X1 (§6.4).

Inputs: D161 addenda 4-16 (16 is the ruling), D157, D158; reviews r2
(`2026-10-18-r2-kitverify-proof.md`) and r3 (above); `memfn/window_contract.md` §2-§5;
`memfn/r17b_prime.md` §1, §4.3-§4.6; `locate_finish.md` §1-§2, §5.1; `compound.md` §A.1
(`split_conj[]`); plan rows [KIT-VERIFY], [MATCH-KNOWN], [CAPS-KNOWN]; memfn R-25 (as
corrected in `memfn/docs/requests.md`).

---

## §R2.1. What revision 2.1 changed (re-check finding → section)

The re-check of revision 2 (k3-recheck, opus) cleared it with fixes: 1 BLOCKER, 3 MAJOR,
8 MINOR, three PARTIAL discharges and three new unlocks. All are ACCEPTED. Changed text
carries `[r3rc <id>]`.

| id | disposition | section |
|---|---|---|
| K1 (BLOCKER) | C9 becomes "no row at depth 0..k carries a non-identity eol view". `conj.py` implements it (`rows_by_depth`). `ab\|a$\n`, `ab\|a\Z\n` and `ab\|a$\n\z` join `witnesses.txt`, and all three DECLINE at `no-eol-view`. Under the plant "C9 tested at depth k only" (`CONJ_PLANT=c9-depth-k`, revision 2's C9) all three read `cover` and are wrong: `"a\n"` from 0 gives NOMATCH where PCRE2 gives (0,2). The admitted set is unchanged, 1,197 → 1,197 with no row newly declined: the census population is 0, as the critic said. §5.2 states that `span_facts` passes a mid-pattern `$`/`\Z` to the hull. S1136 is re-aimed to this plant. X0 gains a subject family because the critic's random subjects missed the `ab\|a$\n` cell | §1.1 C9, §5.2, §6.3 S1136, §6.4 X0, `kit_proof/conj.py`, `witnesses.txt` |
| M-A | C2 `origin-start` is RETIRED (UL-n1). It carried no weight, because the REPORT description is read off the machine. Its admitted patterns join U1. `conj.py` applies nothing after the table, so its `why` histogram is first-match in table order. U-ctxorigin's context joins are recounted: 12 / 9 corpus. Whole-cover patterns with no start-origin census site add 5 bench / 27 corpus native and 1 / 7 utf8. S1136 could not go red, and is RE-AIMED to K1's plant | §0, §1.1 C2, §1.2, §6.3 S1136, §8.3 |
| M-B | the harness lever's KIT-SIDE channel is named: `mf_preview(mf_art *, const char *step)`, a harness-only call on the `mf_reach` precedent. Its fence: only `pcrec_harness_compile` reaches it, which is the compound lever's one-global reserved-prefix entry, and it is not an `options.def` row, so no `--memfn=` spelling reaches it. Its wording is D157-neutral: pcrec names its own routing event, never a row or a form. §7's re-run condition becomes "if pcrec's row OR the kit text differs at B1 from Z2, B4 included" | §7 (Z2, "The harness lever's kit channel"), §4.3 R-26.6 |
| M-C | S1143 ships declared UNREACHED, with the argument (a nullable body fails C10, or has no span 0 for C13). S1139 is TWO edits: C9 dropped AND the eol view read as the end | §6.3 |
| m1 | C14 is EQUALITY on REPORT: `proven[d] = S_d` and every context set equals its stated set. `⊆` alone admitted an over-filter, which would miss a match. `kit-none` is "differs in either direction", with both directions named | §1.1 C14, §6.4 K35 |
| m2 | C8's `why` splits into `exact/machine-inexact` and `exact/producers-disagree`. The trace build asserts 0 of the latter | §1.1 C8, §6.4 K35 |
| m3 | a REPORT site states `mf_site.consumer = MF_C_RESULT` | §2.5, §4.1, §4.3 R-26.3 |
| m4 | lift item 2 names MLINE's stop predicate too. The carrier is spelled `const mf_pred *ctx; uint8_t nctx;` | §4.1 |
| m5 | the verdict for a CONTEXT term below `read_floor` but inside the subject is defined: no verdict exists, so a site that can produce such a term is REFUSED at define. A REPORT site states SUBJECT. S1137's detector moves accordingly | §3.5, §6.3 S1137 |
| m6 | X5 is byte identity "modulo the abi readers" | §6.4 X5 |
| m7 | the getwidth superset is stated PER ENCODING. getwidth counts characters, and `é\|ab` is fixed at 2 bytes under utf8 but (1, 2) in characters | §6.4 K35 |
| m8 | §8.4 Q2's stale PENDING label is deleted and the RULED text kept. fam-M7's claim is corrected: neither A1's verdict nor A5's moves in stage 1, and the field reads are [cand-no-name-strcmp] hygiene. The note now records that `conj.py` has no C5 | §8.4 Q2, §2.6, §1.1 C5, `conj.py` docstring |
| PARTIAL family M2 | `span_facts`' half of C8 is absent from `conj.py`, so `conj.py`'s C8 is the machine half only. OWED at Z2: the slice built and C8 run as two-producer equality on every admitted artifact | §1.5, §6.4, §7 Z2 |
| PARTIAL contract M5 | X0 and X1 (the independent per-position, per-byte libpcre2 oracle) and the getwidth K35 floor have NOT been run. The critic's re-check differential (1,197 patterns, 1,638,884 cells) is a precursor on the critic's instrument, not X0. OWED at step X0, before Z2 | §6.4, §7 X0 |
| PARTIAL contract B2, sabotage, sound B1 | discharged by M-B, M-C and K1 above | — |
| UL-n1 | drop C2: done here (trigger met) | §8.3 |
| UL-n2 | the default-build define/ask class check as a SHIPPED invariant for every REQUIRED kit site. Trigger: the next trace-only mismatch, or U2 | §8.3 |
| UL-n3 | `MkEnd` is exact for every view-free fixed-width DFA body once C9 covers the walk, which is UL-2's input. Trigger: UL-2's own | §8.3 |
| C1-C14 order | the order is total. `fact-denied` is a C13 failure detail, not a row | §1.1 |

**Admitted-set delta** (`conj.py` revision 2 vs 2.1 on one build at main `fa322a7f6`,
the critic's `admitted.py` shape over the census patterns): 1,197 → 1,197, nothing newly
declined. In `conj.txt` B every pattern that read `no-start-site` now reads `cover`
(`cover … no-start-site` lines). C and D move only by the three new witnesses.

**What revision 2.1 could NOT discharge** (also in the lane report): X0/X1 themselves (a
heavy differential, not run under the box rule); the getwidth floor's number; the
`span_facts` half of C8 (it needs the Z2 build); the K96 per-field `serves`/`uses` cells
(the kit's, at Z1).

---

## §R2. What revision 2 changed (finding → section)

Every finding id in r3, with the section that discharges it. All are ACCEPTED.

**k3-family (1 BLOCKER, 7 MAJOR, 6 MINOR, Q1-Q3, UL-0..UL-8)**

| id | disposition | section |
|---|---|---|
| fam-B1 | `exact_len` is stated over the SENT sets: the largest `L` such that span-0 positions `[0, L)` are all SENT and every sent set equals the producer's `S_d`. On 33 of 66 bench and 129 of 560 corpus stage-1 sites, span 0 sends fewer positions than `k` (`conj.txt` E) | §4.1, §5.2 |
| fam-M1 (Q2) | rows are distinct by WALK; the FACT (`MkKnown`) and the FINISHER (`FIN2 report`) are source-neutral. [PF-KNOW] det_all, start_landing U1 and U1b are one FINISH-on-VM mechanism, filed as [CAPS-KNOWN]. U-anch is a VERIFY-family member | §2.1, §8.2, §8.4 Q2 |
| fam-M2 | the producer is split. `S_d`, `exact_len` and the hull are priority-free and are the FIRST SLICE of `span_facts` (`src/facts/spans.c`). Only "the end is decided at `k`" and the context sets read A. Machine `S_d` vs `span_facts` `S_d` is a control | §1.5, §5.2, §6.4 |
| fam-M3 | `MkLang` is a PATTERN fact (`src/facts`), `MkEnd` a MACHINE fact read off A (gen), `MkKnown` a SUBJECT fact (`src/gen/known.c`) that holds a REFERENCE to the kit's class, keyed `(point, origin)`, with room for `(src, fact)` conjuncts and length bounds at the second member | §5.1 |
| fam-M4 | the admission is the listed first-match conjunct table `cover_conj[]` (the `split_conj[]` precedent, D163 add. 4). The helper derives knowledge only | §1.1, §5.1 |
| fam-M5 | stage 1 is `CR_DFA` only: `CR_ATTEMPT` has no counted population | §1.1 C1, §1.2 |
| fam-M6 (Q4) | `-fno-kit-proof` is a FACT deny (`CandList.fact_deny` precedent) that empties `MkKnown`; every consumer declines naturally; X5 becomes a byte-identity gate | §2.2, §6.4 X5, §8.4 Q4 |
| fam-M7 | `compound.c:199` and `:235` read LOCATE selections by name. They become typed row-field reads before or in B1 | §2.6, §7 |
| fam-Q1 | captures are OUT of U1, in [CAPS-KNOWN] (tag-determinism per accepting row; `caps == NULL` is compound's CAPTURES-ON-DEMAND client; O3 restated, not excepted) | §8.3, §8.4 Q1 |
| fam-Q3 | the `\b` reading is right for stage 1 and is labelled DFA-only. At U1b the facts-layer derivation becomes THE context fact and the machine reading its control | §3.2, §8.4 Q3 |
| fam-m1 | `rev-end` and `cover` populations are disjoint. Witnessed under `-fno-rev-end`: 8 bench / 75 corpus end-anchored bodies decline at `no-eol-view` | §2.3 |
| fam-m2 | RECOVER rows are not locators (rev 1's "fifth locator" count withdrawn) | §2.1 |
| fam-m3 | LOCATE gets a declared `kask` (the trace build aborts on an undeclared ask, S1019) | §2.2 |
| fam-m4 | D164's end mark moves A's accept depth, so `cover_conj[]` asserts an unmarked A (C5) | §1.1 |
| fam-m5 | T-PROOF becomes a fact-family note (window_contract §9 edit) | §2.1, §6.2 |
| fam-m6 | bit accounting: see con-bits (7 free, 6 after this one) | §6.1 |
| fam-UL-0..UL-8 | filed with triggers; UL-0 (the `span_facts` slice) is IN U1 | §8.3 |

**k3-contract (2 BLOCKER, 5 MAJOR, readers, bits, staging, sabotage, R-26 details)**

| id | disposition | section |
|---|---|---|
| con-B1 | R-26 gets a CARRIER: `mf_site.ctx[]` / `nctx`. The note states the refusals it lifts (`MF_SPAN_CONTEXT`'s reservation, `memfn.h:363-376`; the "pspans only" rule, `:458-462`), the term cap (`MF_MAX_CTX`, each entry ≤ `MF_MAX_TERM`), and window_contract hunks (§2.2 context paragraph `:331-335`, §2.3 rules, §2.4 reply, §11's R-18 outline `:1885`, §6.2 edit list) | §4.1, §4.3, §6.2 |
| con-B2 | Z2's evidence is B1's artifact. The kit's REPORT row lands UNROUTED before Z2 (the `fd_rows[].routed` precedent, `finder.c:964`). Z2 routes it only through the harness lever `build/pcrec-harness --harness=kit-proof`. The trace build decides as default does | §7 |
| con-M3 | every span-0 position and every context item of a REPORT site is REQUIRED. The DEFAULT build checks the defined class (`mf_defined`) against `S_d` and the context sets, and fails loudly (`pcrec_ctx_fail`, an internal error). NONE is not legal on REPORT | §2.5, §4.1, §4.3 R-26.3 |
| con-M4 | `span_lo` is not reused. A new field, `read_floor`, an enum with an UNSTATED zero | §3.5, §4.1 |
| con-M5 | X1 is an independent per-position, per-byte libpcre2 oracle, set-equal to the producer's sets. Its subjects are drawn from the whole byte alphabet, not from `S_d`. The K35 floor comes from an independent fixed-width definition (python `sre_parse` getwidth). `why` splits `kit-none` / `kit-denied` / `no-row` | §6.4 |
| con-readers | re-derived by grep at `542b0cecb`: S693, the form census floors and `KNOWN_VALUES`, `memfn_arm.py`'s `MEMFN_CLASS`, `match_api.md:1823` and §6.3.4¶12, the bench files to relay, emit_sweep's PINS, `cand_oracle_witnesses.tsv`, the startset manifests, `tests/endmark`, `tests/compound/check_linear.py` | §6.1 |
| con-bits | bit 55 is reserved for the kit (`lib/pcrec.h:1192`). Bits 57-63 are free (7); this one takes 57 and leaves 6 | §6.1 |
| con-staging | a C17 `pending` manifest row lands at Z2; `.list` lands at B1 (or Z2 is a declared `--list-axes` delta); B1 lands AFTER R17-b′'s B4 lockdown, so B4's `rows.tsv` / `row_floors.tsv` / routed census carry the REPORT row as unrouted; a measure-set regeneration that flips cover ↔ composite moves the form-census floors | §7, §8.1 (3) |
| con-sabotage | S1130-S1148 PROPOSED (the ledger is not edited here). S1138 is caught in the DEFAULT build (con-M3's check); S1137 now plants `read_floor`; S1132's reach is stated (`k` = first accept depth) with a `SAB_REACH` on the `cover` stamp. Rows are added for the six MISSING plants (deny unplumbed, `k ± 1`, `\G` decline dropped, nullable decline dropped, unstated `absent` read as 0, default-build define/ask mismatch) and for sound's three (eol view read as end, `e(⊥) :=` row 0, over-filter) | §6.3 |
| con-R26-details | MLINE: `prefix_stated` belongs to a BOUNDED span 0 only and is a refused-if-stated wildcard on MLINE's CONTEXT predicate. `kit_class` COPIES `proven0`/`proven_prev` from `proven[]` (equal by construction), and Q-R17P-25's trace check extends to every `d`. R-26's readers are listed per K96. `MF_MAX_SPAN_POS` is derived (`≥`, not "equal"). `MF_MAX_AHEAD` is 1 now (D77). The notation is now bytes-wise ⊆ and position-wise ⊇. §4.2's dangling "§8.4 Q3" is removed. R-25's census is corrected (524 of 650 OFS sites, done by the manager) | §4.1-§4.4 |
| con-unlocks | U-oracle, U-required, U-pop filed with triggers | §8.3 |

**k3-sound (1 BLOCKER, 4 MAJOR, 5 MINOR, unlocks)**

| id | disposition | section |
|---|---|---|
| snd-B1 | the end is a MACHINE conjunct, not an ordering claim. C7 requires that nothing accept below depth `k` in any form. C9 requires no eol view on the walk at `k`. C10 requires that at `k` only the end view and the class-indexed accept decide. `cover` is then correct whatever `rev-end`'s position or deny | §1.1, §2.3 |
| snd-M1 | `e(⊥)` is the EMITTED entry constant `X` of `search_from ? seed[…] : X`, asserted in the trace build. `(?<=x)cat` reads `X` dead, so absent FAILS | §1.1 C6, §3.2 |
| snd-M2 | conjunct C1 is on the FINISHER route (`cand_finish_of(cx) == CR_DFA`). K35 asserts `selected ⊆ engine dfa`. Recounted: 66 / 560 native, 46 / 413 utf8 | §1.1, §1.2, §6.4 |
| snd-M3 | `CR_ATTEMPT` is dropped from stage 1 (agrees with fam-M5); U-bisim filed | §1.1, §8.3 |
| snd-M4 | context joins recounted with the machine conjuncts: 80 / 65 corpus before the origin conjunct (the critic's count, reproduced), 68 / 56 with it; the 4 lazy non-covers decline at `end-at-k` | §1.2 |
| snd-m1 | "`\w` is ASCII on every encoding" corrected: false under `--ucp -e byte`. The mechanism is still exact, since it reads the machine | §3.3 |
| snd-m2 | = con-M4 | §3.5 |
| snd-m3 | `\G` is a conjunct (C3, a machine fact: no `N_GSTART` on the route's NFA) | §1.1, §1.3 |
| snd-m4 | find-all under utf8 cites K75's `next_pos(end − 1)` resume | §1.3 |
| snd-m5 | R-26.4's bar includes COMPLETENESS over proven OPTIONAL positions (obligation 1), with an over-filter plant | §4.3, §6.3 S1147 |
| snd-U-X0, U-z, U-bisim, U1b | U-X0 is IN the plan as step X0 before Z2; U-z, U-bisim filed; U1b → [CAPS-KNOWN] | §7, §8.3 |

**What revision 2 could NOT discharge** (also in the lane report): the X0 run itself (a
heavy differential, not run under the box rule); the getwidth K35 floor's number (its
instrument is designed, not run); the K96 per-field `serves`/`uses` cells of every arm
for the new fields (named here, the kit's to write at Z1).

---

## 0. Answers first

| question | answer |
|---|---|
| what U1 is | a search whose kit site PROVES the whole sub-problem at every candidate it yields returns the first candidate as the match, with no DFA, no start recovery and no handback (§1) |
| where it sits | ONE new LOCATE row, `cover`, after `rev-end` and before `composite`. It hands `SPAN`/`NOMATCH` to the EXISTING `FIN2 report`/`FIN1 nomatch`. The row is a WALK (the kit's stream). The FACT it reads (`MkKnown`) and the FINISHER are source-neutral `[r3 fam-M1]` (§2.1) |
| its admission | `cover_conj[]`, a listed first-match conjunct table (§1.1) `[r3 fam-M4]`: route, site, pattern and machine conjuncts, then the kit's |
| stage 1 population | `CR_DFA` finisher artifacts only `[r3 snd-M2, fam-M5]`. **66 bench / 560 corpus native sites, 46 / 413 utf8** (census sites, origin start, whole-cover). `cover_conj[]` admits 71 / 585 native and 47 / 420 utf8 whole-cover PATTERNS: the start-origin ones (66 / 558, 46 / 413) plus, with C2 retired, 5 / 27 and 1 / 7 with no start-origin site `[r3rc M-A]`. Context joins add 6 bench / 80 corpus native and 3 / 65 utf8, U-ctxorigin's 12 / 9 included `[r3 snd-M4, r3rc M-A]` (§1.2) |
| what the entry loses | the forward machine's tables and scan loop, the start recovery, the K82 handoff and any pre-check (`foobar` twin: `.text` 2,047 → 1,425 B, SIZE ONLY, §2.4) |
| the `\b` rewrite | READ off the route's anchored machine (seed table, emitted entry constant, class-indexed accept). For stage 1 it is DFA-only. At U1b a facts-layer derivation becomes the context fact and this reading its control `[r3 fam-Q3]` (§3) |
| the fact producer | split `[r3 fam-M2]`: `span_facts`' first slice (`src/facts/spans.c`, priority-free) gives `S_d`, `exact_len` and the hull. A reading of A gives the end at `k` and the context sets (§5.2) |
| facts pcrec states (R-26) | on a BOUNDED span 0: `prefix_stated`, `exact_len` (over the SENT sets `[r3 fam-B1]`), `consumable_len`. In the new carrier `mf_site.ctx[]` `[r3 con-B1]`: CONTEXT spans with `absent` and `consumable`. On the site: `site_kind` `MF_SK_REPORT` with every position REQUIRED `[r3 con-M3]`, and `read_floor` `[r3 con-M4]`. Every enum has an UNSTATED zero, refused where read (§4) |
| what the kit returns (R-26) | `mf_class.proven[d]` per origin offset; `proven0`/`proven_prev` COPIED from it (§4.2) |
| the deny | `-fno-kit-proof`, a FACT deny that empties `MkKnown` (one flag bit, 57; 6 left) `[r3 fam-M6, con-bits]` |
| captures | OUT of U1: [CAPS-KNOWN] (§8.3, §8.4 Q1, RULED) |
| events | Z0 R-25 → Z1 R-26's layout at zero movers → Zk the kit's REPORT row UNROUTED → X0 the libpcre2 oracle on the reading → Z2 pcrec's producer, row and emitter, routed only by the harness lever → `measure` → **B1** (after R17-b′ B4), the one byte-moving event (§7) |

---

## 1. WHOLE-COVER

### 1.1 The definition: `cover_conj[]` `[r3 fam-M4, snd-B1, snd-M1, snd-M2, snd-M3, snd-m3, fam-m4]`

A kit site's sub-problem is WHOLE-COVERED when every row of `cover_conj[]` holds, read in
order; the first failing row is the `why` (a first-match table with listed conjuncts, the
`split_conj[]` shape of `compound.c:238`, D163 addendum 4). pcrec decides them all at
compile time. None is decided per call. The order is TOTAL. `fact-denied` is a failure
detail of C13, not a row `[r3rc]`. The ids are stable: the retired C2 keeps its number,
so the sabotage rows and the other notes still cite C3-C14 correctly.

| # | id | kind | the conjunct | why it is needed |
|---|---|---|---|---|
| C1 | `finisher-dfa` | route | `cand_finish_of(cx) == CR_DFA` | on `CR_DFA` a group ≥ 1 is never live, so `FIN2`'s dead-group fill is the whole capture answer. The LOCATOR route would admit hybrids with live groups (5 bench / 126 corpus in revision 1's count) `[r3 snd-M2]`. `CR_ATTEMPT` is out: it has no counted population and no table reader (its machine is computed-goto) `[r3 snd-M3, fam-M5]` |
| C2 | ~~`origin-start`~~ | — | **RETIRED** `[r3rc M-A]` (was: the site's origin is the match start) | it carried no weight. `cover` does not reuse the census site: the REPORT description (§2.5) is built from `MkLang` and A at the match-start origin, so another origin on the site `cover` replaces changes nothing. Dropping it admits U-ctxorigin's 12 / 9 corpus context joins and 5 bench / 27 corpus native (1 / 7 utf8) whole-cover patterns with no start-origin census site, and all of them are inside the critic's 0-difference run (UL-n1). Its plant S1136 could not go red (0 / 1,221) and is re-aimed (§6.3) |
| C3 | `no-gstart` | machine | the route's NFA holds no `N_GSTART` (no `gstart_seed_state` is emitted) | `\G` makes `search_from` the only start; the machine cannot see it as a byte set `[r3 snd-m3]`. Today every `\G` body takes the attempt route, so C1 declines first and C3's plant is UNREACHED (§6.3 S1142). The row exists so the admission does not rest on that routing fact |
| C4 | `anchored-A` | machine | A (`job->adfa`) is built | the reading needs it; `anchored_ok` false or over the cap declines (4 corpus patterns, `conj.txt` B) |
| C5 | `unmarked-A` | machine | A carries no D164 `END_MARK` accept distances (asserted: a `tagged` form's lowering is not on A) | the mark moves A's accept depth, so `k` would not be the match width `[r3 fam-m4]`. Today such bodies are `rev-end` and C5 is an assertion. It is NOT in `conj.py`, which has no population for it `[r3rc m8]` |
| C6 | `entry-const` | machine | unseeded A: one entry. Seeded A: every live seeded entry is ONE row `r0`, and `e(⊥)` is the EMITTED entry constant `X` of `search_from ? seed[class(s[search_from − 1])] : X` (`emit_dfa.c:6246`). `X = r0` makes absent-before SATISFIES, `X` dead makes it FAILS; any other `X` declines | `e(⊥)` is not row 0: `(?<=x)cat` has `X` dead, and reading row 0 is wrong on 168 of 3,798 cells (`"cat"` from 0: (0,3) against nomatch) `[r3 snd-M1]`. The trace build asserts that the `X` the reading used is the one the emitter writes |
| C7 | `fixed-width` | machine | from `r0` there is a depth `k`, `1 ≤ k ≤ MF_MAX_SPAN_POS`, such that no row reached at a depth `< k` accepts in ANY form (plain, class-indexed, end view, eol view), and the rows at `k` are not empty | an accept below `k` is a shorter match. Reading a view accept as "not an end" was rev 1's hole `[r3 snd-B1]`. `k ≥ 1` also declines every nullable body, and C4 and C10 decline them all again, which is why its plant S1143 is UNREACHED `[r3rc M-C]` |
| C8 | `exact` | span fact | `exact_len ≥ k` on the producer's span 0, and the producer's `S_d` equals A's `S_d` for `d < k` | the language from the origin is `S_0 × … × S_{k−1}` for this artifact's encoding (kvp-contract S1: per encoding). The equality is fam-M2's control (§5.2). The `why` has two details `[r3rc m2]`. `exact/machine-inexact` means A's language from `r0` is not a product. `exact/producers-disagree` means `span_facts`' `S_d` ≠ A's `S_d`, two producers disagreeing about one language, which is a defect: the trace build asserts 0 of it. `conj.py` reads only the machine half (§R2.1, PARTIAL) |
| C9 | `no-eol-view` | machine | no row at ANY depth `0..k` of the walk carries a non-identity eol view `[r3rc K1]` | at `k` an eol view is neither "a byte follows" nor "the subject ends": reading it as the end is wrong on 19 of 3,777 cells (`cat$` under `-fno-rev-end`, `"ccat\n"` from 0: cover none, PCRE2 (1,4)), and not reading it gives NOMATCH on `"cat"` `[r3 snd-B1]`. BELOW `k` a mid-pattern non-multiline `$`/`\Z` followed by a consumed `\n` is a transition only under the eol view, which the plain walk cannot see. Revision 2 tested depth `k` only, so `ab\|a$\n` read `cover` with `k` = 2 and gave NOMATCH on `"a\n"` from 0, where PCRE2 gives (0,2) (likewise `ab\|a\Z\n` and `ab\|a$\n\z`). The census population is 0, so X0 on the admitted set could not have found it `[r3rc K1]` |
| C10 | `end-at-k` | machine | every row at depth `k` accepts, only through its class-indexed (or plain) accept or its end view, and none has a live successor | the end is `c + k` and no other priority end exists (O2). `abc|ab` and the four lazy context forms (`\w+?(?:)\b`, …) fail here |
| C11 | `after-agree` | machine | the rows at `k` agree on `C_k` (the bytes before which they accept) and on absent-after, and `C_k ≠ ∅` or absent SATISFIES | the after-context is then one per-position set with one absent rule (§3.2) |
| C12 | `utf8-start` | span fact | under `-e utf8`, `S_0` holds no continuation byte | a candidate is then a character start; the producer DECLINES rather than asserting (§1.3) |
| C13 | `report-served` | kit | the REPORT description (§2.5) has an applicable kit row: `mf_ask` returns a class, not a refusal | with every position REQUIRED, NONE is not a legal reply (§2.5). The failure detail is `no-row`, `kit-denied` or `kit-none` (§6.4) `[r3 con-M5]` |
| C14 | `proven` | kit | EQUALITY on a REPORT site `[r3rc m1]`: `proven[d] = S_d` for every `d < k`, and every context offset's proven set equals its stated set under its stated absent rule | `⊆` alone is not enough. `proven[d] ⊊ S_d` is an OVER-FILTER: the stream skips a candidate whose byte is in `S_d`, and with no engine behind REPORT that is a lost match. `proven[d] ⊄ S_d` is a false match. Equality is the same as `⊆` plus COMPLETENESS (R-26.4's obligation 1) at every REQUIRED position. REQUIRED-all makes it true by binding; the DEFAULT build checks equality and fails loudly on a mismatch in either direction (§2.5) `[r3 con-M3]` |
| — | `fact-denied` | deny | `-fno-kit-proof` empties `MkKnown`, so C13 reads no source | a FACT deny, not a row deny (§2.2) `[r3 fam-M6]` |

`cover` is the conjunction. The row's predicate walks the table (§2.2). The LOCATE order
(`empty` → `rev-end` → `cover` → `composite`) is not a conjunct: a body that an earlier
row takes is counted as `earlier-row` by the instrument, never by `cover_conj[]`.

The machine conjuncts (C3-C11, C5 excepted) are written as code in `kit_proof/conj.py` over kvdfa's
reader of the EMITTED tables. Its witnesses (`conj.txt` D) are: `foobar` k=6;
`foo|foobar` k=3; `in|instanceof` k=2; `abc|ab` → `end-at-k`; `ac|bd` → `exact`;
`ab|a$\n`, `ab|a\Z\n` and `ab|a$\n\z` → `no-eol-view` (K1; each reads `cover` under
the plant `CONJ_PLANT=c9-depth-k`) `[r3rc K1]`;
`\bcat\b` k=3; `\Bcat\B` k=3 with both absent rules FAILS; `(?<=x)cat` absent-before
FAILS; `(?m)done$` k=4; `cat$` → `earlier-row`, and under `-fno-rev-end` `cat$`, `cat\Z`
and `\bcat$` → `no-eol-view`; `\Gfoo`, `foo|\Gbar`, `(?m)^item` → `finisher-dfa`;
`\w+?(?:)\b` → `end-at-k`; `z(?=a)` k=1, absent-after FAILS.

### 1.2 Which sites qualify, counted (K35) `[r3 snd-M2, snd-M4, fam-M5]`

Recounted by `kit_proof/conj.py` (`conj.txt` A and B) from the committed kvcensus run.
Section A counts census SITES (origin start, whole-cover) by FINISHER route. Section B
runs `cover_conj[]` C1-C12 (C2 retired, C5 not in the script) on every census whole-cover
or context-join PATTERN, and nothing after the table: the `why` histogram is first-match
in table order `[r3rc M-A]`. Each admitted pattern is labelled `start-site` or
`no-start-site` by whether the census found a start-origin site for it. That label is a
count, not a conjunct.

| population (native / utf8) | bench | corpus | in stage 1? |
|---|---:|---:|---|
| `CR_DFA` sites, DFA_SCAN OFS | 42 / 31 | 196 / 193 | yes |
| `CR_DFA` sites, DFA_SCAN PF | 24 / 15 | 364 / 220 | yes |
| **stage-1 sites** | **66 / 46** | **560 / 413** | |
| … of which span 0 sends fewer positions than `k` (`conj.txt` E) | 33 / 33 | 129 / 160 | yes; the REPORT description sends all `k` (§2.5) `[r3 fam-B1]` |
| patterns `cover_conj[]` admits (C1-C12), with a start-origin census site | 66 / 46 | 558 / 413 | yes |
| … with no start-origin census site (C2 retired, UL-n1) | 5 / 1 | 27 / 7 | yes `[r3rc M-A]` |
| … dead groups only (`CR_DFA`, NCAPS ≥ 2) | 1 / 1 | 8 / 7 sites | yes (FIN2's fill; witness bench `syntax/rec-define`) |
| context joins admitted (C1-C12, a start-origin site) | 6 / 3 | 68 / 56 | yes (§3) |
| context joins admitted with no start-origin site (U-ctxorigin's, recounted) | 0 / 0 | 12 / 9 | yes `[r3rc M-A]` (was NO in revision 2) |
| **admitted patterns, all** | **77 / 50** | **665 / 485** | the `cover` population (B1's movers) |
| context joins declined at `end-at-k` (the lazy forms) | 0 / 0 | 4 / 4 | never |
| whole-cover on a VM finisher (DFA_SCAN on a hybrid, DFA_HAT, HYB_PF, VM_ATTEMPT) | 11 / 7 sites | 390 / 138 sites | NO: [CAPS-KNOWN] |
| context joins on the VM | 4 / 3 | 23 / 19 patterns | NO: [CAPS-KNOWN] with U1b's facts-layer reading |
| anchored or end-anchored with no kit site | counted in kvcensus §6 | | NO: U-anch (a VERIFY-family member, §8.2) |

The context-join counts are the k3-sound critic's 80 / 65 corpus patterns, reproduced:
68 + 12 = 80 and 56 + 9 = 65, and with C2 retired all 80 / 65 are admitted. The admitted
total, 77 / 665 native and 50 / 485 utf8, equals the critic's `eolwalk.py` counts over
the same census. Deduplicated by (flags, pattern) it is the 1,197 patterns of the
critic's 0-difference run `[r3rc M-A]`. The census's text-based 84 / 69 included the 4 lazy
non-covers. Revision 1's 71 / 686 had counted the hybrids' DFA_SCAN and DFA_HAT sites,
whose finisher is the VM. Its "DFA_HAT 6" row was wrong for the same reason: every
DFA_HAT whole-cover site sits on a VM-engine artifact.

**Instrument defect, recorded.** `conj.py`'s first run passed the pattern to argv as a
Python `str`, which is re-encoded as UTF-8, so 8 utf8-born corpus patterns compiled as
different bytes and read `exact` (the `startset/` note recorded the same defect class in
the census). The pattern now goes to argv as its own bytes, and all 8 are admitted.

### 1.3 Find-all, empty matches, `search_from`, `\G`, guards, utf8

- **Find-all.** `_search` stays one-shot. The match_api §3.1.3 loop calls it again from
  the returned end `c + k`. The stream is ascending and complete from `lo`, so the next
  call's first candidate is the next leftmost match. Under `-e utf8` the loop resumes at
  `next_pos(end − 1)` (K75, `docs/dev/k75_measurement.md`), and since `c + k` is a
  character boundary (below) that resume is `c + k` itself `[r3 snd-m4]`.
- **Empty matches** cannot occur: C7 needs `k ≥ 1`, which declines every nullable body.
- **`search_from`.** Every candidate is `≥ search_from`. Context reads go below
  `search_from` down to the subject start (PCRE2's lookbehind and `\b` semantics,
  `locate_finish.md` O5), under `read_floor` (§3.5). The `search_from > subject_length`
  return stays in front of the site.
- **`\G`** declines through C3 (and today through C1) `[r3 snd-m3]`. That case is the
  anchored sibling, U-anch.
- **Guards.** The K50 `PCREC_ERR_STARTPOS` prologue and the `-futf-check` validation run
  before the site, unchanged. `cover` adds no refusal and no give-up.
- **utf8 alignment.** A candidate is a character start because C12 keeps continuation
  bytes out of `S_0`. The end `c + k` is a character boundary because the lowered machine
  accepts only after whole characters (O6). A context byte at `−1` may be a continuation
  byte of the preceding character, and its verdict is still exact (§3.3).

### 1.4 The give-up surface (D158)

On `CR_DFA` nothing is budgeted: not the DFA, not the kit's stream, not the deny arm. The
posture cell is N/A (`locate_finish.md` §1.5 rule (e)), and "an answer never becomes a
give-up" holds because neither arm can give up. `cover` adds no `PCREC_ERR_*` producer. An
EMPTY stream is NOMATCH outright: every context span states an `absent` rule, so no edge
is left for pcrec to try (`window_contract.md` §2.4's coverage rule; §4.3's hunk). The VM
and hybrid cells are [CAPS-KNOWN]'s.

### 1.5 Where `L` is read from: two producers `[r3 fam-M2]`

Revision 1 read everything off A and said the facts layer could not be the home, "an NFA
walk without priority would refuse `in|instanceof`". That was wrong in part. Priority can
prune a thread only after an accept, and C7 admits no accept below `k`. So for `d < k`
the reachable byte sets and the exactness of the prefix are properties of the LANGUAGE,
not of priority. `in|instanceof`'s language has the exact prefix `in` with no priority
read at all. What priority decides is that the end is at `k` (`in` accepts first, and A
kills the `instanceof` arm there), and which context the seed table encodes.

- **Priority-free, `span_facts`' first slice** (§5.2): `S_d`, `exact_len` and the hull of
  span 0 at the match-start origin, on the lowered tree, in `src/facts/spans.c`.
- **The machine reading** (`MkEnd`, §5.1): C3-C7 and C9-C11 off A. That is `k`, the end
  with no live successor, `C_{−1}` with absent-before via the emitted entry constant,
  and `C_k` with absent-after.
- **The join is C8**: `S_d` from both must agree for `d < k`. Two producers that share no
  code make that equality a real control (§6.4). `conj.py` has only the machine
  producer, so its C8 is `exact/machine-inexact` alone. The two-producer equality is
  OWED at Z2, when `span_facts`' slice is built, and it runs on every admitted artifact
  `[r3rc PARTIAL fam-M2]`.

**Where to attack §1.** (a) C7-C10 under leftmost-first priority: a body where A keeps a
live successor past a shadowed arm, or kills one PCRE2 keeps. (b) C8's join on a caseless
class under utf8 (`(?i)é`). (c) A view accept at a depth below `k` that kvdfa's
`acc_any` misses. (d) C1 on a DFA artifact with NCAPS ≥ 2 whose group is live. (e) C6 on a
machine with `N_GSTART` (C3 should have declined it first).

---

## 2. The row, the fact and the finisher

### 2.1 Rows by walk; fact and finisher source-neutral `[r3 fam-M1, fam-m2, fam-m5]`

`FIN2 report` already exists (`emit_dfa.c:9922`). It takes `SPAN` on `CR_DFA` and
`CR_ATTEMPT` and returns `(s, e)`. U1 adds a LOCATE row whose WALK is the kit's proven
stream from `search_from`. The stream's first element `c` is `[c, c]` with `D = {c + k}`,
which is `SPAN`. An exhausted stream is `I = ∅`, which is `NOMATCH`. So `cover` is one
LOCATE row, beside `empty`, `rev-end` and `composite` (`emit_dfa.c:9497-9527`). RECOVER's
`end-minus-width`/`landing` rows are not locators: revision 1's "fifth path-changing
locator" count is withdrawn `[r3 fam-m2]`.

**Distinct by walk, neutral in fact and finisher.** The "the match is fully known here"
members sit in three SLOTS:

| slot | members | what makes them distinct |
|---|---|---|
| LOCATE | `empty`, `rev-end`, `cover` | the WALK: none, reverse from `n`, the kit's stream |
| RECOVER | `pinned`, `end-minus-width`, `landing` | the start is read, not walked |
| FINISH on the VM | [PF-KNOW] det_all, start_landing U1 (fixed-margin captures), revision 1's U1b | one mechanism filed three times, now [CAPS-KNOWN] |

A row is named for its walk, so a second source of "fully known" (an exact hybrid's
prefilter, a constant-offset group map) is not a second source of `cover`. It is a
different walk with the same FACT (`MkKnown`, which is source-neutral) and the same
FINISHER (`FIN2 report`, extended to the VM and hybrids by [CAPS-KNOWN]'s group map).
U-anch (`^item`, `^\d{5}$`) still tests the bytes at one position, so it belongs to the
VERIFY family and is not a "known" case.

**T-PROOF becomes a fact-family note** `[r3 fam-m5]`. `window_contract.md` §9 drafted
T-PROOF as its own first-match table (`report` → `dfa-exact-prefix` →
`vm-literal-prefix` → `verify-rest` → `ignore`). Those rows consume one proof in
different slots, so they are not alternatives to one decision:

| T-PROOF member | its slot | lands |
|---|---|---|
| `report` | LOCATE `cover` → FINISH `FIN2`/`FIN1` | U1 |
| `dfa-exact-prefix` | NEXT → VERIFIER entry state | U2, held |
| `vm-literal-prefix` | the VM entry | U3, no population |
| `verify-rest` | a kit VERIFY site beside NEXT | filed |
| `ignore` | every row that reads no proof | the default |

What they share is the FACT (`MkKnown`) and its one deny. §9's table becomes a note
listing the members and their slots (§6.2).

### 2.2 The row

```c
/* [KIT-VERIFY] U1 `cover` (kit_proof.md §2): the kit's site PROVES the whole
 * fixed-width sub-problem, context included, at every candidate it yields
 * (every position REQUIRED, a REPORT site), so the first candidate IS the
 * leftmost match: SPAN [c, c + k]; an exhausted stream is NOMATCH. No machine
 * runs. Admitted by cover_conj[] (§1.1), read in order. After `rev-end`,
 * before `composite`. Denied through the FACT: -fno-kit-proof empties
 * MkKnown, so C13 reads no source (CandList.fact_deny). */
{ .c = { "cover", 0, locate_cover_applies }, .slot = CAND_SLOT_LOCATE,
  .routes = CR_DFA, .tok = "cover", .map = CM_NONE,
  .hands = CT_START | CT_VERDICT,
  .kask = { [CAND_SLOT_LOCATE] = CAND_ON(CAND_ROUTE_DFA) },          /* [r3 fam-m3] */
  .needs = { [CAND_ROUTE_DFA] = { 0, 0, CN(CAND_SLOT_PRESENCE) } },
  .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_cover },
                .scan = { [CAND_ROUTE_DFA] = "cover" },
                .whole = true, .fin = CT_START | CT_VERDICT } },
/* .list = { [CAND_ROUTE_DFA] = { "locate", 2, "cover" } } and the listing's
 * fact_deny PCREC_NO_KIT_PROOF land at B1 (§7) */
```

- **Routes:** `CR_DFA` only `[r3 snd-M2, snd-M3]`.
- **Predicate** `locate_cover_applies` walks `cover_conj[]` and returns false at the first
  failing row, recording its id as the CANDTRACE `why`. The kit conjuncts (C13, C14) read
  the pure define-time ask of the REPORT description (§2.5). That ask is a DECLARED read,
  `kask[LOCATE] = CAND_ON(DFA)`. An undeclared ask aborts the trace build (S1019's
  detector), so the declaration is a deliverable, not a comment `[r3 fam-m3]`. The site's
  description depends on the language facts only, never on FIRST's or NEXT's selection,
  so no edge points forward and `table-read-cycle` holds (`r17b_prime.md` §4.5 rule 5).
- **The deny is a FACT deny** `[r3 fam-M6]`: `.c.deny` is 0, and the listing carries
  `fact_deny = PCREC_NO_KIT_PROOF` (`emit_dfa.c:11325`'s merge,
  `CandList.fact_deny`'s shape, which `vm-anchor-bound` and `end-window` use). Under the
  deny `MkKnown` is empty, so C13 fails with `fact-denied` and every later T-PROOF member
  declines the same way, with one bit and no per-row field. A denied artifact is the
  composite path's artifact byte for byte (X5, §6.4).
- **Needs:** no machine, and PRESENCE (as the front, answered by `.whole`, so
  `RX_REQ_WHY` reads `dominated`). The match-here entry keeps its own FINISH (`FIN3
  verify-at` on A), so A stays a member where it is built today, and F and R drop out.
- **Totality:** `cover` hands `SPAN` and `NOMATCH`, which `FIN2`/`FIN1` take on `CR_DFA`
  (`emit_dfa.c:9915-9925`).
- **Listing slot:** the `locate` axis lists `rev-end` 1, `cover` 2, `unanchored` 3 from
  B1. That re-numbers `unanchored`'s listing index, a declared `--list-axes` move (§7).

### 2.3 `rev-end` and `cover` are disjoint `[r3 fam-m1, snd-B1]`

By default an end-pinned body selects `rev-end` (earlier in the order), so `cover` never
sees it. Under `-fno-rev-end` it reaches `cover_conj[]` and declines at `no-eol-view`
(C9): 8 bench / 75 corpus native and 7 / 69 utf8 patterns (`conj.txt` C, e.g. `\d+$`,
`\s+$`, `.*\.txt$`). The other end-anchored bodies decline earlier (`fixed-width`,
`exact`, `entry-const`, `anchored-A`). Only `\z` bodies survive the deny: 1 bench / 10
corpus (`done\z`, `b\z`). That is correct: an end view with an empty `C_k` and absent
SATISFIES is exactly `\z`, so those artifacts are `cover` artifacts in the deny arm. That
is the U-z unlock's population (§8.3). Since the conjuncts read the machine, `cover` stays
correct whatever `rev-end`'s position or deny.

### 2.4 The emitted entry

Today `foobar` (abi 80) declares three forward tables, runs the forward scan loop with
`rx_ofsskip`, steps the DFA six bytes from the candidate and recovers `start = end − 6`.
`\bcat\b` adds a K82 `rx_reqrun` handoff, a seed-table read at every candidate and a
class-indexed accept. Under `cover`:

```c
int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from,
              ptrdiff_t (*capture_spans)[2])
{
    if (search_from > subject_length) return 0;
    size_t cand = rx_cover(subject, subject_length, search_from);  /* the kit's site */
    if (cand >= subject_length) return 0;
    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)cand; capture_spans[0][1] = (ptrdiff_t)(cand + 6); }
    return 1;
}
```

A dead-group artifact gets FIN2's existing `PCREC_UNSET` fill under the same `if`. The
startpos and utf-check prologues stay in front. **Removed from the search path:** the
forward machine's tables and helpers, the scan loop, the scan-edge peel, the start
recovery, the K82 handoff, the presence pre-check and the seed-state read. **Kept:**
`_match`/`_match_caps` on A, `_next_pos`, `_valid_upto`, `rx_info`, and the kit's text.
Size (revision 1's twin, SIZE ONLY): `foobar` `.text` 2,047 → 1,425 B, `rx_search` 100
→ 61 instructions. The kit's text is unchanged there because `run-pinned` already compares
every byte. On a one-byte PF site (`\d{4}`) the kit's text grows by the verification the
REPORT description requires.

### 2.5 The REPORT description: every position REQUIRED, checked in the default build `[r3 con-M3]`

A site's facts must be TRUE (D161 add. 4), and `site_kind` names the consumer. On a
`cover` artifact nothing consumes the candidate except `FIN2`, so the honest kind is
`MF_SK_REPORT`.

**REQUIRED-all.** Revision 1 left positions 1..k−1 and the context OPTIONAL. That is a
miscompile path: obligation 4 lets a candidate fail an OPTIONAL span, and there is no
engine behind REPORT to reject it. So on a REPORT site:

- every span-0 position `0..k−1` is REQUIRED;
- every context item is REQUIRED.

That is T-NEED's "a consumer that cannot skip" (`window_contract.md` §2.3), consistent
with D161 add. 16. Binding then makes `proven[d] ⊆ S_d` true by construction. NONE is not a
legal reply (obligation 6: an unconstrained reply is legal only when span 0 is OPTIONAL or
absent). The kit's row either serves the site or does not apply (K96).

**The cycle closes through the PURE ask** (`r17b_prime.md` §4.5 rule 1):

1. During LOCATE's selection pcrec asks the REPORT DESCRIPTION. That is span 0 = `S_0..
   S_{k−1}`, all REQUIRED, `consumable_len = k`; each context span REQUIRED with
   `consumable` YES and its `absent` rule; `site_kind` REPORT; `consumer`
   `MF_C_RESULT` (the candidate is the result, and no engine consumes it) `[r3rc m3]`;
   `read_floor` SUBJECT.
2. If `cover_conj[]` passes, the row is selected and that same description is DEFINED.
   **The DEFAULT build** reads `mf_defined`'s class and compares it, for every `d < k`
   and every context span, against the stated sets, for EQUALITY (C14) `[r3rc m1]`. Any
   difference, in either direction, is `pcrec_ctx_fail`
   (an internal error, never a silent fallback). The trace build's re-ask agreement
   (rule 2) stays as a second detector.
3. If not, `cover` declines and the composite's own description is asked and defined as
   today. Every non-`cover` site is byte-identical (Z2's gate).

This is not the rejected `mf_ask` two-pass of r2 (add. 16): `need` is not forced by a
price. The REPORT description's `need` is the TRUE consumer fact of a REPORT consumer.
U-required (§8.3) is the follow-on: with REQUIRED-all the kit's proof adds nothing beyond
"a row applies", so pcrec's language test plus the measured gate could replace the ask.

### 2.6 `compound.c`'s name reads become field reads `[r3 fam-M7]`

`compound.c:199` (A1: `strcmp(…LOCATE…, "composite")`) and `:235` (A5:
`strcmp(w->facts[SPLIT_Q].locate, "rev-end")`) read LOCATE selections by NAME, which
[cand-no-name-strcmp] forbids. Revision 2 said that a part which selects `cover` changes
both verdicts. That overstated it `[r3rc m8]`, and in stage 1 neither verdict moves. A1
reads LOCATE on `CAND_ROUTE_ATTEMPT`, where `cover` (routes `CR_DFA`) is never listed.
A5 is false unless Q selects `rev-end`, and a Q that selects `cover` would otherwise have
reached `composite`, which fails A5 too, because `cover` sits after `rev-end` in the
order. So the change is [cand-no-name-strcmp] hygiene, and a later row on the attempt
route would make it necessary. Before or in B1 they become typed reads of the selected
row:

- A1 asks "P's plain compile attempts every start": the selected LOCATE row hands
  `CAND` to NEXT (`.hands`/`.needs`), which `composite` does and `cover` does not;
- A5 asks "Q is end-pinned": the selected LOCATE row's walk is seeded at the subject
  end (a `.u.locate` walk attribute that `rev-end` declares).

This is UL-4. Neither population moves, and B1's identity gates cover both.

### 2.7 Stamps (the generated rule, `locate_finish.md` §5.1)

| stamp | on a `cover` artifact | why |
|---|---|---|
| `RX_DFA_SCAN`, `rx_info.scan` | `"cover"` (NEW value) | LOCATE's listed name |
| `RX_DFA_START` | `"attempt-start"` | RECOVER not asked (its absence value, `cand_absent[]`); `match_api.md:1823`'s definition gains `"cover"` (§6.2) |
| `RX_END_WINDOW`, `RX_REQ_HANDOFF`, `RX_DFA_PREFILTER`, `_PREFILTER_OFFSETS` | `"none"` | not asked |
| `RX_REQ_WHY` | `"dominated"` where `REQ_BYTE ≠ "none"` | PRESENCE asked, `.whole` |
| `RX_REQ_BYTE`, `RX_REQ_RUN` | unchanged | pattern facts |
| `RX_DFA_TABLE`, `_UNIFORM_FOLDS`, `_SCAN_EDGE` | folded over the members (A only) | the member fold |
| `RX_DFA_MATCH`, `rx_info.match_form` | unchanged | the match-here entry's own FINISH |
| the kit's site record | the site's own record | a new emitter call site (C17, §7) |

**Where to attack §2.** (a) `cover` as a locator, tested against `locate_finish.md`
§1.2's product. (b) A reader of "is F a member" on a `cover` artifact that assumes F.
(c) The ask under the size ladder: is a rung re-emit's ask the first one's? (d) The
default-build check: a kit class that is narrower than `S_d` at some position.
(e) Whether A1's field read admits a row that is not `composite` but also hands CAND.

---

## 3. Context spans before and after the origin

### 3.1 What exists today

pcrec does not rewrite `\b` by position (kvcensus §0). `mod_assertions.c:131-134` lowers
it to `A_CTX(W, BOUNDARY)`. The VM tests both sides, and the DFA gets the positional
effect from its SEED TABLE and class-indexed accept. Two partial forms ship: MLINE's
`{\n}` CONTEXT predicate at `−1`, and the 23 `scan-restart/ctx` sites, which send a
width-1 lookbehind as a shifted origin.

### 3.2 It is READ, not lowered: stage 1 is DFA-only `[r3 fam-Q3, snd-M1]`

Frank's ruling (add. 16): "a rewrite of `\b` automatically gets added to the sent span".
For stage 1 that is a STATED FACT read off the route's anchored machine:

- **Before the origin.** For each predecessor class `p` the machine enters at `e(p) =
  seed[p]`. At the subject start, and at `search_from = 0`, it enters at `e(⊥) = X`, the
  constant the emitter writes into `search_from ? seed[…] : X` (`emit_dfa.c:6246`;
  revision 1 wrongly said row 0). `C_{−1} = {b : e(class(b)) is live}`. It is
  EXPRESSIBLE iff every live entry is one row `r0`. Absent-before is SATISFIES iff
  `X = r0` and FAILS iff `X` is dead. Any other `X` declines (C6).
- **After the end.** `C_k = {b : every row at depth k accepts before class(b)}`,
  expressible iff the rows agree and none has a live successor (C10, C11). Absent-after
  is SATISFIES iff every row accepts at the subject end, through its end view (C9 keeps
  eol views out).

This is the positional rewrite. One reading covers `\b`, `\B`, `(?m)$`, the width-1
lookbehinds and the trailing lookaheads the DFA admits. It is computed from the machine
the engine runs, so it is an equivalence by construction. Its control is libpcre2 (X1).

**Labelled DFA-only.** VM-only patterns get no context fact from this reading. At U1b
([CAPS-KNOWN]) a facts-layer derivation (a reading of the leading/trailing `LOOK` and
`A_CTX` nodes) becomes THE context fact, and the machine reading becomes its control on
the DFA side. A true lowering, a neighbour-set assertion fold (the definitions_table `\b`
row plus possessify's arm-A valuation), is filed as UL-6, BOONIES-style (§8.3).

Why not lower it now: a tree rewrite moves every engine's bytes and the `--emit-ir`
listing on every `\b` artifact for no answer change. It is a second spelling of what the
seed table encodes (D122, memory `pcrec-general-mechanisms-not-special-cases`), and its
safety would rest on a case analysis rather than on reading the machine.

### 3.3 What is expressible (stage 1 = `CR_DFA`)

| item | per-position form | `absent` | stage 1 |
|---|---|---|---|
| `\b` before a word / non-word byte | `C_{−1} = ¬W` / `W` | SATISFIES / FAILS | yes |
| `\B` before a word / non-word byte | `C_{−1} = W` / `¬W` | FAILS / SATISFIES | yes |
| `\b`/`\B` after the end | `C_k` (the mirror) | the mirror | yes |
| `(?<=X)`, X a byte set | `C_{−1} = X` | FAILS (`X` = dead) | yes, where the DFA admits it |
| `(?<!X)`, X a byte set | `C_{−1} = ¬X` | SATISFIES | yes |
| `(?m)$` | `C_k = {\n}` | SATISFIES | yes |
| `(?=X)` / `(?!X)` width 1 after the end | `C_k = X` / `¬X` | FAILS / SATISFIES | yes |
| `(?m)^` | `C_{−1} = {\n}` | SATISFIES | NO in stage 1: `(?m)^` bodies take `CR_ATTEMPT` (C1, `conj.txt` D) `[r3 snd-M3]`; U-bisim |
| `\z` after the end | `C_k = ∅` | SATISFIES | only in the `-fno-rev-end` arm today (§2.3); U-z |
| lookbehind of fixed byte width > 1 | `C_{−w}..C_{−1}` | FAILS | NO: the DFA reads one seed byte (the census misread width-2/3 lookbehinds such as `(?<=ab)z|\bw`; the machine reading declines them) `[r3 snd-M2]` |
| a negative of width > 1 | a disjunction | — | never (add. 16) |
| non-multiline `$`/`\Z` | not per-position | — | never; `rev-end`, or C9 under its deny |
| UCP `\b` under utf8 | — | — | refused by the parser today |

**utf8 and `\w`** `[r3 snd-m1]`. Revision 1 said "`\w` is ASCII on every encoding". That
is false under `--ucp -e byte`, where `\w` includes Latin-1 letters. The mechanism does
not depend on it: the context set is read off the machine, which encodes whatever `\w`
means for this artifact's options. Under `-e utf8` UCP `\b` is refused, so `\w` is ASCII
there. A continuation byte is then a non-word byte, and PCRE2's verdict on the preceding
multi-byte character (non-word under ASCII `\w`) equals the one-byte verdict.

### 3.4 The absent-byte bit

At `c = 0` there is no byte at `−1`, and at `c + k = n` none at `k`. `absent` says whether
the context HOLDS there. It is stated per CONTEXT span, with an UNSTATED zero. Once every
context span states it, no position is uncovered, so pcrec's EDGE attempt is not needed on
a `cover` artifact. An exhausted stream is NOMATCH outright, and the edge code is not
emitted (`window_contract.md` §2.4's coverage paragraph gains this case, §6.2). MLINE's
predicate is restated at Z1 as CONTEXT with `absent` FAILS and `consumable` NO, which is
exactly today's behaviour (U-mline retires its edge later).

### 3.5 Reads before `search_from`: `read_floor` `[r3 con-M4, snd-m2]`

The kit may read `subject[c − 1]` when `c = search_from > 0`. That is the real byte
before the start, which PCRE2 reads (O5). It may never read before the subject start,
where `absent` decides. Revision 1 stated this bound as `span_lo` = 0. That field is a
LENGTH bound on the proven range today, and its zero is a used value, so the reuse was a
second meaning on one field. Revision 2 adds a field:

`read_floor` (`mf_site`, new; enum `mf_read_floor`): `MF_FLOOR_UNSTATED = 0` (refused
on a site that carries a CONTEXT term below the origin, a wildcard elsewhere),
`MF_FLOOR_SUBJECT` (reads may go down to offset 0 of the subject), `MF_FLOOR_LO` (reads
stay `≥ lo`). The obligation is `window_contract.md` §2.3's "Reads" rule with the floor
named: every read lies in `[floor, n)`. The field states WHICH floor, never a number.

**Below the floor but inside the subject** `[r3rc m5]`. Under `MF_FLOOR_LO` a CONTEXT term
at `c − 1` with `c = lo > 0` names a byte that exists but may not be read. Neither `absent`
rule applies, because the byte is not outside the subject, and no reading of it is
allowed, so the term has NO verdict. A site that can produce such a term is therefore
REFUSED at define: `MF_FLOOR_LO` together with a CONTEXT term at a negative offset is a
refusal, naming `read_floor`. Only `MF_FLOOR_SUBJECT` admits a below-origin term, and
under it the only positions below the floor are those below 0, where `absent` decides. A
REPORT site states SUBJECT (§2.5). MLINE states SUBJECT today, so the rule moves nothing.

### 3.6 How the readers see it, and one-way safety

- **DFA:** a `cover` artifact runs no DFA in `_search`. A non-`cover` artifact sends no
  context span in stage 1, so no kit text moves there (U4 sends them as filters later).
- **VM:** nothing reads the fact in stage 1.
- **Listings:** `--emit-ir` is unchanged. `--emit-facts` gains the `span_facts` slice
  (Z2) and the `MkKnown` member row (B1), each with a `facts_listing.md` hunk.
  `--list-axes` gains `cover` and `kit-proof` at B1.
- **One-way safety.** A context span used as a FILTER is an equivalence, so it drops no
  match. Used as a PROOF, it is consumed only through `cover_conj[]`. An item that cannot
  be read exactly declines the row, and a decline is today's path. An OVER-stated set is
  a wrong answer. Three checks guard that direction: X0/X1 against libpcre2, the
  default-build class check (§2.5), and the plants S1130, S1139 and S1140.

**Where to attack §3.** (a) A seed table whose live entries agree on the row but whose
accept depends on the predecessor class deeper than `−1`. (b) `X` under a size-ladder
rung whose emitter writes a different constant. (c) `C_k` on rows with an end view that
accepts while the plain row does not. (d) A width-1 lookbehind over bytes ≥ 0x80 under
utf8.

---

## 4. The facts pcrec states and what the kit returns: R-26

### 4.1 What pcrec states `[r3 con-B1, con-M3, con-M4, fam-B1, con-R26-details]`

| fact | carrier | values (UNSTATED zero, refused where read) | Z1 (today's truth) | a `cover` site (B1) |
|---|---|---|---|---|
| `prefix_stated` | `mf_pred` of a BOUNDED span 0 | `MF_PREFIX_UNSTATED` 0 (refused on a FIND site's BOUNDED span 0), `MF_PREFIX_STATED`. On any other predicate (MLINE's CONTEXT stop, a `ctx[]` entry, a `pspans` entry) it is a wildcard and must be 0 (refused otherwise) | STATED on every BOUNDED span 0 | STATED |
| `exact_len` | the same | read only when STATED: `0..MF_MAX_SPAN_POS`. The largest `L` such that span-0 positions `[0, L)` are all SENT and the cross product of the SENT sets over `[0, d]` equals the sub-problem's length-`(d+1)` prefixes for every `d < L`, for this artifact's encoding `[r3 fam-B1]`. An under-statement is sound | 0 on every site (sound) | `k` |
| `consumable_len` | the same | read only when STATED: `0..exact_len` (more is refused): "if you prove `[0, N)`, my consumer will not re-test those positions" | 0 everywhere | `k` |
| `ctx[]`, `nctx` | `mf_site`, NEW (appended last), spelled `const mf_pred *ctx; uint8_t nctx;` `[r3 con-B1, r3rc m4]` | `nctx` 0 = no context span; else `ctx[0..nctx)` are `mf_pred`s with `span_class` CONTEXT, each term at an offset in `[−MF_MAX_BACK, 0)` or `[k, k + MF_MAX_AHEAD)`, at most `MF_MAX_CTX` entries. A `ctx[]` entry on a site with no BOUNDED span 0 is refused | `nctx` 0 on every site | one entry per context item |
| `span_class` CONTEXT | `mf_pred` | the reserved value, now built: on MLINE's stop predicate and on `ctx[]` entries, nowhere else | MLINE | each `ctx[]` entry |
| `absent` | a CONTEXT `mf_pred` | `MF_ABSENT_UNSTATED` 0 (refused on CONTEXT, must be 0 elsewhere), `SATISFIES`, `FAILS` (§3.4) | MLINE: FAILS | per §3.3 |
| `consumable` | a CONTEXT `mf_pred` | `UNSTATED` 0 (refused on CONTEXT, must be 0 elsewhere), `YES`, `NO` | MLINE: NO | YES |
| `need` | per term (built) | unchanged. On a REPORT site EVERY span-0 and context term is REQUIRED (refused otherwise) `[r3 con-M3]` | as today | all REQUIRED |
| `site_kind` | `mf_site` (built) | adds `MF_SK_REPORT` | — | REPORT |
| `consumer` | `mf_site` (built, `mf_consumer`) | unchanged: `MF_C_RESULT` / `MF_C_ENGINE`. A REPORT site states `MF_C_RESULT` (refused otherwise) `[r3rc m3]` | as today | `MF_C_RESULT` |
| `read_floor` | `mf_site`, NEW `[r3 con-M4]` | §3.5's enum; UNSTATED refused on a site with a below-origin CONTEXT term | MLINE: `MF_FLOOR_SUBJECT` (today's reads-below range) | `MF_FLOOR_SUBJECT` |

`consumable_len` is one number, as Frank ruled. CONTEXT spans get their own `consumable`
bit because they are not part of span 0's prefix.

**The carrier and what it lifts** `[r3 con-B1]`. Today `mf_site` has `pred`, `preds[]`
(ALL_PRESENT/DENSE only) and `pspans` (ALL_PRESENT only). `span_class` BOUNDED/CONTEXT is
RESERVED and refused (`memfn.h:363-376`). The class is stated on `pspans` entries only
(`:458-462`). R-26 lifts:

1. CONTEXT's reservation, on MLINE's stop predicate and on `ctx[]` entries;
2. the "`span_class` is stated on `pspans` only" rule, for `ctx[]` entries AND for
   MLINE's stop predicate (`mf_site.pred`), which states `span_class` CONTEXT from Z1
   `[r3rc m4]`;
3. the refusal of `MF_SK_REPORT` at the finder gate (`finder.c`).

BOUNDED on span 0 is R17-b′ B3b's statement (memfn.h: "span 0's class from B3b"), so R-26
lands after B3b (§7).

**The term cap.** Span 0 holds at most `MF_MAX_TERM` (32) terms and `k ≤
MF_MAX_SPAN_POS`. Revision 1 needed `k = 32` plus two context terms in one predicate.
With `ctx[]` each context item is its own predicate, so the cap is per predicate:
`MF_MAX_CTX` entries, each at most `MF_MAX_TERM` terms. `MF_MAX_CTX` is a SHAPE bound,
derived as `MF_MAX_BACK + MF_MAX_AHEAD` (one entry per offset).

### 4.2 What the kit returns `[r3 con-R26-details]`

`mf_class` (`MF_CLASS_V` 3 → 4, appended LAST):

```c
/* (MF_CLASS_V 4, R-26; kit_proof.md §4.2) the PER-OFFSET PROOF: proven[d - MF_PROOF_LO]
   is a bitset (mf_term.set's layout) such that at EVERY candidate the site yields, the
   byte at offset d from the candidate lies in it, OR offset d lies outside the subject
   and the CONTEXT span covering d states absent SATISFIES. All ones = nothing proven.
   It states only what the committed form TESTS (R-25).
   Byte-wise: proven[d] is a SUBSET of the set of any REQUIRED term at d (binding makes
   that true). Position-wise: the proven positions are a SUPERSET of the REQUIRED ones.
   Equal under -fno-memfn-simd, -fmemfn-simd at every level and every layer:
   LAYER-INVARIANT. A --memfn= deny may change it: DENY-VARIANT.
   proven0 and proven_prev are COPIED from proven[0] and proven[-1] by kit_class, so
   they are equal by construction; Q-R17P-25's trace check runs for every d. */
#define MF_PROOF_LO (-MF_MAX_BACK)
#define MF_MAX_FWD  (MF_MAX_SPAN_POS + MF_MAX_AHEAD)
uint8_t proven[MF_MAX_FWD - MF_PROOF_LO][32];
```

- **Bounds.** `MF_MAX_SPAN_POS` is a SHAPE bound DERIVED from `MF_MAX_TERM` (`#define
  MF_MAX_SPAN_POS MF_MAX_TERM`), and pcrec asserts `PCREC_MAX_REQ_RUN_SCAN ≤
  MF_MAX_SPAN_POS` where it fills span 0. Revision 1 said the two were "equal"; the
  relation that matters is `≥`, with one 32 derived from the other. `MF_MAX_BACK` is 8
  (CHOSEN, `memfn.h:150`). **`MF_MAX_AHEAD` is 1** `[r3 con-R26-details]`: the stage-1
  after-context width is 1, and a wider bound waits for a measured need (D77). Its
  trigger is a declined site, counted at Z2 or later, whose after-context is wider than
  1. The array is `(32 + 1 + 8) × 32` = 1,312 B per class.
- **`proven0`, `proven_prev`** stay as fields, because G1, R4, `landing` L4 and kit P2
  read them. `kit_class` COPIES them from `proven[]`, so the invariant holds by
  construction rather than by assertion. Retiring them is a later zero-mover cleanup
  under [MATCH-KNOWN].
- **Language vs membership.** `proven[d]` is a MEMBERSHIP fact. pcrec uses it as a
  language proof only for `d < exact_len`.
- **Whether to serve is the kit's.** With REQUIRED-all a REPORT site leaves the kit no
  choice about WHAT to prove, only whether a row applies (C13). Revision 1's reference to
  a "§8.4 Q3" on consumer price pointed at nothing and is removed `[r3 con-R26-details]`.

### 4.3 R-26, drafted (main files it after R-25 and after R17-b′ B3b; facts only, D157)

> **R-26 (draft, pcrec manager) — the per-offset proof, prefix exactness, CONTEXT spans
> in `mf_site.ctx[]` with an absent rule, the read floor, and the REPORT consumer**
>
> **Customer:** [KIT-VERIFY] U1, `docs/design/kit_proof.md` rev 2 (D161 add. 16; reviews
> r2, r3; census docs/dev/kvcensus.md). **After R-25** (`proven0` honours `need`; 524 of
> 650 native OFS sites send OPTIONAL offset-0 terms today) and **after R17-b′ B3b**
> (span 0's BOUNDED class).
>
> | item | what pcrec needs (facts) | landing bar |
> |---|---|---|
> | R-26.1 | a BOUNDED span 0 of a FIND site carries `prefix_stated`, `exact_len`, `consumable_len` (kit_proof.md §4.1). `prefix_stated` UNSTATED is refused there; on every other predicate it must be 0. `consumable_len > exact_len` is refused | one `MF_SITE_ABI` event, readers by grep. ZERO artifact movers on every emit_sweep arm, with pcrec stating STATED / 0 / 0 on every site in the same change |
> | R-26.2 | `mf_site.ctx[]`/`nctx` (appended last): CONTEXT predicates with `absent` and `consumable` (UNSTATED refused there, 0 required elsewhere), offsets in `[−MF_MAX_BACK, 0)` or `[k, k + MF_MAX_AHEAD)`, at most `MF_MAX_CTX`, refused on a site with no BOUNDED span 0. MLINE's stop predicate states `span_class` CONTEXT, `absent` FAILS, `consumable` NO. COMPLETENESS and BINDING read `absent`: under SATISFIES a candidate whose context offset lies outside the subject is yielded when the other spans hold, under FAILS it is not. `read_floor` (enum, §3.5): reads lie in `[floor, n)`; `MF_FLOOR_LO` with a CONTEXT term at a negative offset is refused, since such a term has no verdict inside the subject `[r3rc m5]` | MLINE's restatement: zero movers. A G2 fixture per `absent` value at `c = 0` and at `c + k = n`, completeness checked by the byte-loop oracle. A refusal fixture per UNSTATED field (`absent`, `consumable`, `read_floor`, `prefix_stated`), including "UNSTATED `absent` read as 0" |
> | R-26.3 | `site_kind` `MF_SK_REPORT`: the candidate is the answer, with no engine behind it; the site states `consumer` `MF_C_RESULT` (refused otherwise) `[r3rc m3]`. Every span-0 and context term is REQUIRED (refused otherwise). NONE is not a legal reply: a row that cannot serve every REQUIRED term does not apply (K96). On a REPORT site binding and completeness together make `proven[d]` EQUAL to the REQUIRED term's set at every `d`; the host checks equality (C14) `[r3rc m1]` | refused before R-26. The finder gate (`finder.c`) admits it wherever a REPORT row exists. A fixture with one OPTIONAL term on a REPORT site, refused |
> | R-26.4 | `mf_class.proven[]` (kit_proof.md §4.2). `kit_class` COPIES `proven0`/`proven_prev` from it | `MF_CLASS_V` 4. G2: at every candidate of every generated site, every proven offset holds, including negative offsets, offsets after the span, and the absent rule. **COMPLETENESS**: a site whose form proves an OPTIONAL position yields every covered position where all spans hold (obligation 1), with an over-filter plant (a form testing a narrower set than the term) caught by the byte-loop oracle `[r3 snd-m5]`. C-PROOF: identical across SIMD off and every live level. The Q-R17P-25 trace check is extended to every `d` |
> | R-26.5 | declarations: `MF_MAX_SPAN_POS` (derived from `MF_MAX_TERM`; pcrec asserts `PCREC_MAX_REQ_RUN_SCAN ≤` it), `MF_MAX_AHEAD` 1 (D77, labelled with its trigger), `MF_MAX_CTX` (derived), `MF_PROOF_LO`, `MF_MAX_FWD` | declarations only |
> | R-26.6 | the kit's REPORT row lands UNROUTED (`fd_rows[].routed` false, `finder.c:964`). The host states, through `mf_preview(art, "R-26.6")` (kit_proof.md §7, `[r3rc M-B]`), that an art is a harness PREVIEW of that routing step and is never shipped; on such an art the kit decides as it will once the step routes | zero movers on every arm; `mf_preview` refused after the first define, twice, or for a step the kit does not name; no `options.def` row for it, so `mf_opts_check` refuses any `--memfn=` spelling of it; the row's G2 fixtures run in the kit's suite |
>
> **Readers the kit updates (K96, per field: class and `serves`/`uses`)**: `fields.def`
> (one `MF_FIELD` row per new field, with `cl_*` classify functions in `gate.c`), every
> arm's `[FLD_x] =` contract table (`ofsskip.c:753`, `pffind.c:364`, `precheck.c:362`,
> `runcmp.c:553`, `vrun.c:470`, `generic.c:814`, `mismatch.c:247`, and `finder.c`'s
> `[FLD_site_kind]` gate at `:205`), and `memfn/tests/g2/g2_gen.c`/`g2.h` (generation of the new
> fields and the REPORT kind).
>
> **Not asked:** any method. Which row serves REPORT and with which form is the kit's
> (D157, D161 add. 6).
>
> **Sequencing:** R-25 → R17-b′ B3b → R-26.1-R-26.5 at zero movers (Z1) → R-26.6 (Zk) →
> pcrec's Z2 → B1, which routes the REPORT row together with pcrec's abi event (a kit byte
> move is a pcrec abi event in the same commit).
>
> **Sabotage ids:** pcrec-side S1130-S1148 PROPOSED (kit_proof.md §6.3). Kit-side ids
> on request: a form claiming an untested offset; an absent-SATISFIES candidate dropped;
> an absent-FAILS candidate yielded; a proof bit set only by a SIMD row (C-PROOF); an
> over-filter on an OPTIONAL position; an UNSTATED field accepted.

### 4.4 R-25 first

R-25's fixture is the `d = 0` instance of R-26.4's "states only what the committed form
TESTS". Landing R-26 first would carry R-25's latent over-claim into every offset. The
census figure in R-25 is corrected in `memfn/docs/requests.md` (524 of 650 native OFS
sites send OPTIONAL offset-0 terms; the zero-mover bar is MEASURED).

**Where to attack §4.** (a) A field whose zero is used rather than refused or wildcarded.
(b) `ctx[]` against a future multi-span window site that also has context: does one
carrier serve both? (c) `read_floor` on MLINE: does stating SUBJECT move any kit text?
(d) Is `proven ⊆ tested` checkable by G2 from outside the kit?

---

## 5. The producers, the record and the helper

### 5.1 Three records and one helper `[r3 fam-M3, fam-M4]`

[MATCH-KNOWN] is "ONE general record of what is ALREADY KNOWN about the subject at each
point of the emitted matcher". Its trigger is reached: [KIT-VERIFY] is the third consumer
(kvp-unlock B1). Revision 2 separates what is known about the PATTERN, what is read off a
MACHINE, and what is known about the SUBJECT:

```c
/* src/facts/known.h -- a PATTERN fact: span_facts' first slice at the
   match-start origin (§5.2). Priority-free, on the lowered tree. */
typedef struct {
    uint8_t  stated;                    /* MK_LANG_UNSTATED 0, MK_LANG_STATED       */
    uint8_t  exact_len;                 /* 0..MF_MAX_SPAN_POS                       */
    uint8_t  set[MF_MAX_SPAN_POS][32];  /* S_d, d < exact_len                       */
} MkLang;

/* src/gen/known.c -- a MACHINE fact: the end at k and the context, read off the
   route's anchored machine A (C3-C7, C9-C11). */
typedef struct {
    uint8_t  k;                         /* 0 = no fixed end (declined)              */
    uint8_t  ctx_before[32], ctx_after[32];
    uint8_t  absent_before, absent_after;   /* MK_ABS_UNSTATED 0, SATISFIES, FAILS  */
    uint8_t  set[MF_MAX_SPAN_POS][32];  /* A's S_d, the C8 control                  */
    const char *why;                    /* the failing cover_conj[] id, or NULL     */
} MkEnd;

/* src/gen/known.c -- a SUBJECT fact: what is known at one point, relative to an
   origin. A REFERENCE to the kit's answer, never a 1,312 B copy. Keyed (point,
   origin); room for (src, fact) conjuncts and length bounds at the second member
   (UL-7). */
typedef enum { MK_AT_UNSTATED = 0, MK_AT_KIT_CANDIDATE } MkAt;
typedef enum { MK_SRC_UNSTATED = 0, MK_SRC_KIT_PROOF } MkSrc;
typedef struct {
    MkAt            at;
    MkSrc           src;
    const mf_class *cls;                /* NULL = nothing known (the fact deny)     */
} MkKnown;

/* What follows from the three: knowledge, not admission. */
typedef struct {
    uint8_t prefix;       /* largest L <= exact_len with proven[d] ⊆ S_d, d < L     */
    int8_t  suffix_lo;    /* first offset of the trailing proven run, or -1         */
    uint8_t ctx_proven;   /* bit 0: before, bit 1: after                            */
} MkDerived;

MkDerived pcrec_known_derive(const MkLang *, const MkEnd *, const MkKnown *);
```

- **Admission is `cover_conj[]`; the helper derives knowledge.** Revision 1's helper
  returned `cover` and a `why` that mixed the two. The `why` is now the first failing
  `cover_conj[]` row (§1.1). C14 reads `MkDerived.prefix ≥ k` and `ctx_proven`.
- **Pure** and memoised per site per compile.
- **Readers in U1:** `locate_cover_applies` (through C13, C14) and `emit_cover` (`k`).
  It writes the CANDTRACE record `KNOWN <site> prefix=… why=…`, which the K35 count reads.
- **Readers later**, each a T-PROOF family member: U2 reads `prefix`, U4 reads
  `ctx_proven`, and [PF-KNOW]'s trailing segment reads `suffix_lo`.

### 5.2 The producers `[r3 fam-M2, fam-B1, con-M5]`

**UL-0, `span_facts`' first slice, built IN U1.** `window_contract.md` §5.2 specifies
`span_facts` (owner `src/facts/spans.c`, a member of the position-pin family §5.6) as
HULL spans on the lowered tree. Its first slice is span 0 at the match-start origin of
the root segment: `S_d` for every position and `exact_len`, the largest `L` for which the
per-position sets' cross product equals the language's length-`L` prefixes. It is
priority-free (§1.5). It reads no prior and no option except through the lowered tree
(encoding, `-i`, `--ucp`). Its controls are its siblings (the k-set's offset-0..k
union, `start_set`), the machine reading (C8), and X0's libpcre2 sets.

**A mid-pattern `$`/`\Z` passes through to the hull** `[r3rc K1]`. `span_facts` reads
bytes. A zero-width assertion constrains WHERE a byte may stand, and not WHICH byte, so a
non-multiline `$` or `\Z` inside the span is passed through, as every zero-width node
is. On `ab|a$\n` the slice states `S_0 = {a}`, `S_1 = {b, \n}` and `exact_len` 2, which
is a true HULL fact: the byte language is the product. It does not say that `a\n` matches
anywhere but at the subject end. The slice's `exact_len` is therefore never a cover
admission by itself. The position constraint lives on A as an eol view, and C9 declines
the body on A's walk. C8's equality of the two producers' `S_d` holds on such a body, so
C8 cannot catch it, and C9 is the conjunct that must.

**Z2's statement on every start-origin FIND site** `[r3 fam-B1]`. `exact_len` is stated
over the SENT sets, not over the language. It is the largest `L` such that span-0
positions `[0, L)` are all sent and every sent set equals `MkLang.set[d]`. A site whose
span 0 sends one term (`foobar`'s PF site, or `\d{16}`'s `0R`) states `exact_len ≤ 1`
however long the exact prefix is. On 33 of 66 bench and 129 of 560 corpus native stage-1
sites, span 0 sends fewer positions than `k`. This is zero movers while `consumable_len`
stays 0 there. The REPORT description (§2.5) sends all `k` positions from `MkLang`
itself, so on a `cover` site the sent span and `S_d` are one producer's output by
construction. Sites with any other origin state 0.

**The machine reading (`MkEnd`)** is the walk of §1.1 C3-C11 over A, once per artifact,
at most `MF_MAX_SPAN_POS` + 1 deep. It runs in gen, beside the emitter, because it reads
the built machine.

### 5.3 What of [MATCH-KNOWN] this builds, and what it defers

| [MATCH-KNOWN] | U1 builds | deferred (each to its own trigger) |
|---|---|---|
| the record | `MkKnown` (reference, `(at, src)` with UNSTATED zeros) | the `(point, origin)` key with `(src, fact)` conjuncts and length bounds (UL-7, the second member); other points (a VM pc, a DFA state) |
| members | `MK_SRC_KIT_PROOF` | [PF-KNOW]'s prefilter proof and [CAPS-KNOWN]'s group map; K23 `minw`; [START-LANDING]; the D164 end set; the K82 landmark |
| pattern facts | `MkLang` = `span_facts`' first slice | the rest of `span_facts` (window_contract §5.2) |
| derivations | `prefix`, `suffix_lo`, `ctx_proven` | containment ("is X proven at d"), retiring the three "dominated" spellings |
| listing | the `span_facts` slice (Z2) and the member row (B1) in `--emit-facts` | the record's own section at the second member |

**Where to attack §5.** (a) Does `span_facts`' slice equal the machine's `S_d` on every
admitted artifact (C8), including caseless utf8? (b) Does any reader compute `prefix`
privately (G1's domination test, `landing` L4)? (c) `MkKnown` as a reference: is the
`mf_class` alive for every reader's lifetime (define-time memo)?

---

## 6. Events, readers, spec hunks, sabotage rows, checks

### 6.1 The events and their readers (re-derived BY GREP at `542b0cecb`; re-grep at the build commit) `[r3 con-readers, con-bits]`

| event | step | readers (grep) |
|---|---|---|
| `MF_SITE_ABI` 16 → +1 (R-26 layout: `ctx[]`, `read_floor`, the prefix fields, REPORT) | Z1 | `memfn/include/memfn.h:39` (the history); `src/gen/memfn_sites.{c,h,def}`; `src/gen/CLAUDE.md`; `memfn/src/fields.def` and `gate.c` classify; the arms' `[FLD_x]` tables (§4.3); `memfn/tests/g2/g2_gen.c`, `g2.h`; `tests/memfn/run_finder.sh`, `rows_check.py`, `form_checks.py`, `run_arm_pins.sh`, `prov_check.c`, `site_manifest.tsv` |
| `MF_CLASS_V` 3 → 4 | Z1 | `memfn/src/compose.c:297`, `:305`, `:818-828` (Q-R17P-25), the trace re-ask (`mf_defined`'s class) |
| pcrec abi 80 → +1 (B1: the `cover` entry, the kit's REPORT text, the stamp value) | B1 | `src/gen/emit_dfa.c:54` `PCREC_ARTIFACT_ABI` (emitted at `:138`); `docs/spec/match_api.md` abi sentences and §6¶17; `docs/dev/history/abi_changelog.md`; `src/gen/CLAUDE.md`; `tests/codegen/run_codegen_tests.sh`; `tests/codegen/run_recursion_identity.sh` (the (B) pin); **`tests/mech/sabotages/S693_abi_not_bumped.sh`** (`ABI_EXPECT`, re-aimed every bump); the byte-identity gates' pins (re-pinned by recompiling their witnesses, since byte COUNTS move without citing the number, coding_guide §3.1); then the suites that count (registry, codegen, rxtsource, D94 addendum) |
| `RX_DFA_SCAN`/`rx_info.scan` + `"cover"` | B1 | `match_api.md:1279` (§6 row 20), §6.3.4 and **`:1823`** (`"attempt-start"`'s definition gains `"cover"`) and **¶12** ("the four forms are answer-identical" names RECOVER forms; checked, `cover` recovers nothing); **`tests/codegen/run_form_census.sh`** floors (`:307-308` `D:RX_DFA_SCAN=unanchored` 1400, `:368` `rev-end` 200) and `KNOWN_VALUES` (`:470`): the `unanchored` floor drops at B1 (re-derive by an A/B count), and `"cover"` gets a floor on first sight (K35); **`tests/axes/memfn_arm.py` `MEMFN_CLASS`**: every kit deny that removes the REPORT row becomes a `cover` → composite mover, so its `ASSERT_ZERO` cells are re-measured; `tests/codegen/cand_oracle_witnesses.tsv`; `tests/codegen/run_dfa_stamps.sh`, `run_rev_end.sh`, `run_search_pinned.sh`, `run_nomatch_caps.sh`, `run_prechecks.sh`, `run_scan_edge_census.sh`; `scripts/emit_sweep.py` (its PINS); `tests/startset/manifests/manifest_s3_dfa.tsv` (+ `_s2_vm_*`), `startset_checks.py`, `dfahat_checks.py`; `tests/endmark/` (`b3_population.tsv`, `mover_census.py`, `run_b3_checks.sh`); `tests/compound/check_linear.py`; `src/core/compound.c:199`, `:235` (§2.6); `tests/registry/axes_registry_check.sh`, `run_registry_tests.sh`; `tests/memfn/site_census.py`, `site_manifest.tsv`, `run_deleg_sites.sh`, `c10_onebyte.tsv`, `c10_presence.tsv`, `finder_check.py`; `tests/revend/gen_rev_end.py`, `window_twin.py`; mech anchors that quote the scan stamp (S490, S738, S768, S770, S773, S910, S1091 and the rest of the grep's 21 `tests/mech/sabotages` files) |
| bench relay (D78 `[inbox]` note) | B1 | pcrec-bench (read-only here): `testees/pcrec/adapter.py`, `pcrecbench/report.py`, `tools/selfcheck.py` (the closed scan enum); **`testees/pcrec/list_axes.tsv`** (the `locate` axis, re-indexed); **`catalogue/rules.toml:43-60`** (the RECOVER/scan sets it records); **`bench/capability/gen_patterns.py:650`** (the emit-side deny rows: `-fno-kit-proof` joins them) |
| a new flag bit `PCREC_NO_KIT_PROOF` | B1 | `lib/pcrec.h` (bits 0-54 and 56 used; **bit 55 reserved for the kit's `-fno-kit-size-drop`** (`:1192`); bits 57-63 free = 7; this takes **57** and leaves **6**, above [IFACE-PUSH]'s hard trigger of ≤ 4); `src/core/axes.def` (the listing's `fact_deny`, the strategy mask); `docs/spec/tuning.md`, `cli.md`; `--list-axes` |
| the site manifest's row for `emit_cover`'s call site | Z2 (`pending`), B1 (`delegated`) | `tests/memfn/site_manifest.tsv`, `site_manifest_check.py` (C17), `site_census.py` |
| `--list-axes` `locate` re-index (`unanchored` 2 → 3) and the `kit-proof` axis | B1 | `tests/registry/axes_registry_check.sh` and the listing pins; the bench's `list_axes.tsv` |

### 6.2 Spec hunks owed (D80), each in its step

- **Z1:** none for callers. The kit's `memfn.h` comments are the contract text.
- **Z2:** `facts_listing.md`, the `span_facts` slice in `--emit-facts`.
- **B1:**
  - `match_api.md` §3.1¶21 ("four forms to recover the match start" becomes five,
    `cover` recovering nothing);
  - `match_api.md` §6 row 20, §6.3.4, `:1823` (`"attempt-start"` includes `"cover"`),
    and §6.3.4¶12 checked;
  - `tuning.md`: an entry for `cover` and the `-fno-kit-proof` FACT deny (the D158
    preamble covers it; no ONE_WAY marker, nothing is budgeted);
  - `cli.md`: the flag; `facts_listing.md`: the `MkKnown` row; abi §6¶17.
- **Sibling design edits (not spec)** `[r3 con-B1, fam-m5]`:
  - `window_contract.md` §2.2's context paragraph (`:331-335`, "context predicates are
    not spans"): a CONTEXT span in `ctx[]` IS a span of the REPORT site, so the paragraph
    distinguishes MLINE's stop predicate from a REPORT site's `ctx[]`;
  - §2.3: REQUIRED-all on REPORT; `read_floor` names the "Reads" rule's floor;
  - §2.4: the coverage rule gains "every context span states `absent`, so no edge";
    REPORT joins the NONE-safety paragraph as the kind on which NONE is NOT legal;
  - §6.2's edit list gains these; §11's R-18 outline (`:1885` "Facts pcrec will NOT
    state") is checked against R-26;
  - §9's T-PROOF row becomes the fact-family note (§2.1); §2.2's `byte_form` paragraph
    is superseded by `exact_len`; §4.3's per-span `proven` bitmask is superseded by
    `proven[]`.

### 6.3 Sabotage rows (PROPOSED from S1130, the next free main id per `worktrees/.mgr/sabotage_ids.txt`; the ledger is not edited here) `[r3 con-sabotage]`

Each row names its REACH witness ([MECH-REACH]): a `SAB_REACH` asserting `RX_DFA_SCAN
"cover"` on the witness. The expectation comes from libpcre2 or from a check that does
not read the row's predicate.

| id | plant | witness | caught by |
|---|---|---|---|
| S1130 | the reading states `C_{−1}` as every byte | `\bcat\b` on `"concat"`: PCRE2 nomatch, the plant (3,6) | X1 |
| S1131 | C8 skipped (`exact_len := k`) | `ac\|bd` on `"ad"`: PCRE2 nomatch | X0, X1 |
| S1132 | C10's no-live-successor test dropped | `abc\|ab` on `"abc"`: PCRE2 (0,3), the plant (0,2). Reaches because `k` = the first accept depth (2), so C7 passes | X1 |
| S1133 | absent-before flipped | `\bcat` on `"cat"`: PCRE2 (0,3), the plant 0 | X1 |
| S1134 | absent-after flipped | `(?m)done$` on `"done"`: PCRE2 (0,4), the plant 0 | X1 |
| S1135 | the report skips the dead-group fill | bench `syntax/rec-define` on `"12:34"`: group 1 left unwritten | the group check (`run_nomatch_caps.sh`'s shape) |
| S1136 | RE-AIMED `[r3rc M-A, K1]` (was: C2 dropped, which could not go red, 0 / 1,221, and C2 is retired): C9 tested at depth `k` only (revision 2's C9, `conj.py`'s `CONJ_PLANT=c9-depth-k`) | `ab\|a$\n` on `"a\n"` from 0: PCRE2 (0,2), the plant NOMATCH; also `ab\|a\Z\n`, `ab\|a$\n\z` (`witnesses.txt`). MEASURED on the critic's `coversim.py` | X0, X1 (the subject family "each literal path at the subject end", §6.4) |
| S1137 | `read_floor` stated as `MF_FLOOR_LO` on a cover site | `\bcat\b`: under §3.5's rule the kit refuses the site, so C13 fails and `cover` declines. If the refusal were also gone, `"concat"` from 3 gives PCRE2 nomatch and the plant (3,6) | the kit's R-26.2 refusal fixture (`MF_FLOOR_LO` with a below-origin CONTEXT term), then X1's `search_from` sweep `[r3rc m5]` |
| S1138 | the emitter defines the composite's description while the predicate read the REPORT ask | `foobar` | the DEFAULT build's class check (§2.5), then the trace agreement |
| S1139 | TWO edits `[r3rc M-C]`: C9 dropped AND an eol view at `k` read as the end. With C9 dropped alone, C11 declines every witness (`after-agree`), so that plant cannot go red | `cat$` under `-fno-rev-end` on `"9cat\n"` from 0: PCRE2 (1,4), the plant none (9 cells of 1,495); `cat\Z` 1 of 1,524. MEASURED with the critic's `x0lite_p.py` plant `C9E` | X1's deny arm |
| S1140 | `e(⊥) :=` row 0 | `(?<=x)cat` on `"cat"`: PCRE2 nomatch, the plant (0,3) | X1 |
| S1141 | C1 keyed on the LOCATOR route | bench `syntax/grp-named-quote` (`(?'w'cat)`, a hybrid): group 1 unwritten | the group check; K35's `selected ⊆ engine dfa` |
| S1142 | C3 dropped | none reaches: every `\G` body takes `CR_ATTEMPT`, so C1 declines first | ships declared UNREACHED with that argument; flips to a witness if a `CR_DFA` `\G` body appears |
| S1143 | C7's `k ≥ 1` dropped (nullable admitted) | NONE REACHES `[r3rc M-C]`. A nullable body has `k` = 0, so its rows at `k` are the entry. If the language holds any non-empty string the entry has a live successor and C10 declines (`a?`, `a*`, `[ab]?`, `(?:ab)?`, `b?\z`). If the language is `{ε}` alone (a zero-width body: `(?:)`, `(?=a)`, `\b`, `$` under the deny) no anchored machine is built and C4 declines. If either got through, `k` = 0 leaves no BOUNDED span 0, so R-26.2 refuses the REPORT site and C13 fails. MEASURED: 21 nullable probes under the plant all decline, at C4 or C10 | ships declared UNREACHED with this argument; flips to a witness if a nullable body ever passes C4 and C10 |
| S1144 | `emit_cover` reports `c + k + 1` | `foobar` on `"foobarx"` | X1 |
| S1145 | the fact deny unplumbed (`-fno-kit-proof` leaves `MkKnown` filled) | any `cover` artifact under the deny | X5 (byte identity) |
| S1146 | the kit reads an UNSTATED `absent` as 0 | a REPORT fixture with `absent` UNSTATED | R-26.2's refusal fixture (kit-side) |
| S1147 | an over-filter: the kit tests a narrower set at an OPTIONAL position | a G2 site with a proven OPTIONAL position | R-26.4's completeness oracle (kit-side) `[r3 snd-m5]` |
| S1148 | a REPORT site states a position OPTIONAL | `\d{4}` (a one-term PF site today) | R-26.3's refusal, and the DEFAULT build's class check |

The plants for "deny unplumbed" (S1145), "`k ± 1`" (S1144), "`\G` decline dropped"
(S1142), "nullable decline dropped" (S1143), "unstated `absent` read as 0" (S1146) and
"default-build define/ask mismatch" (S1138, now default-caught) are the six con-sabotage
named as MISSING. S1139, S1140 and S1147 are sound's. Two rows ship declared UNREACHED,
S1142 and S1143, each with its argument. S1136 is the re-check's K1 plant `[r3rc]`.

### 6.4 Checks, each against a source the subject does not share `[r3 con-M5, snd-M2, fam-M2, fam-M6]`

- **X0, the reading against libpcre2, BEFORE Z2** (U-X0). It runs on `conj.py`'s
  reading (the prototype of `MkEnd` + `MkLang`). Two parts:
  - **Per-position, per-byte sets.** For every admitted artifact, every position `d <
    k` and every byte `b` of 0..255, libpcre2 decides whether some match begins with a
    prefix carrying `b` at `d` (hard partial matching, kvcensus's `kvpcre`, with
    truncated-UTF-8 completion). The same probe gives `C_{−1}` with the absent-before
    rule (a one-byte prefix `b` before the body; an empty prefix at offset 0), and `C_k`
    with absent-after (anchored match length plus one following byte). The result must
    be SET-EQUAL to the reading's `S_d`, `C_{−1}`, `C_k` and absent bits. An
    UNDER-stated set fails here, where a differential drawn from `S_d` could never test
    it.
  - **The differential** (coversim's shape): the `cover` entry simulated against
    `pcre2_match` at EVERY `startoffset` plus the find-all loop. Subjects come from the
    WHOLE byte alphabet, from bytes adjacent to each set's edges, and from the pattern's
    literals, never only from `S_d`. Also `c = 0`, `c + k = n`, `search_from` inside and
    after a match, ill-formed utf8, and the `-fno-rev-end` arm. The family includes
    EACH LITERAL PATH OF THE BODY PLACED AT THE SUBJECT END, alone and after one
    whole-alphabet byte `[r3rc K1]`. The critic's random draw (150 subjects, seed 7)
    never produced the `ab|a$\n` cell `"a\n"` from 0, and read 0 differences on a
    pattern the plant gets wrong. A `$`/`\Z` body is wrong only where its literal path
    ends the subject, so that cell has to be generated, not hoped for.

  At Z2 the producer is diffed record by record against X0's reading and against
  libpcre2. The k3-sound run (1,057 configs / 4,029,044 cells and 501,250 context cells,
  0 differences beyond U1; six failing controls red) and the re-check's run (1,197
  admitted patterns, 1,638,884 cells, 0 differences beyond U1) are X0's PRECURSORS on
  the critic's instrument. **X0 itself has NOT been run** `[r3rc PARTIAL con-M5]`. In
  particular its per-position, per-byte set-equality part has no precursor at all,
  because the critic's runs are differentials drawn through the reading. It is OWED at
  step X0 (§7), before Z2, on `conj.py` revision 2.1's reading.
- **X1, the same oracle on the BUILT artifacts** (Z2's harness-routed builds and B1's
  default build): every `cover` artifact compiled, run against libpcre2 10.46 with the
  X0 subject families.
- **X2, the plants** (§6.3), each with its reach witness. X2 checks that X0/X1, the
  default-build check and X5 can fail.
- **X3, the trace build's run-time re-test** of every consumed proven offset, context
  included, against the stated sets (`window_contract.md` §4.3).
- **X4, C-PROOF** (kit-side): `proven[]` identical across SIMD off and every live level.
- **X5, the deny twin, a BYTE-identity gate** `[r3 fam-M6]`. Under `-fno-kit-proof`
  every artifact is byte-identical to the default artifact of B1's parent commit (the
  composite path), MODULO THE ABI READERS `[r3rc m6]`: the `PCREC_ARTIFACT_ABI` value
  B1 bumps (its emitted line and `rx_info.abi`), plus `rx_info.flags` masked by the
  strategy mask. Every other byte must be equal. That is stronger
  than answer identity, and it holds because the deny empties the fact that every proof
  consumer reads. `make test-axes` gets the `-fno-kit-proof` arm as well.
- **The C8 control** `[r3 fam-M2]`: `span_facts`' `S_d` against A's `S_d` on every
  admitted artifact. The two producers share no code.
- **K35, who counts the population** `[r3 con-M5, snd-M2]`:
  - **an independent denominator**: python's `sre_parse` getwidth gives `(min, max)`
    over every corpus and bench pattern python parses. getwidth counts CHARACTERS, so
    the superset is stated PER ENCODING `[r3rc m7]`. Native: the pattern is parsed as
    a latin-1 `str`, where a character is a byte, and `min == max ≥ 1` is the
    fixed-width superset. utf8: the pattern bytes are parsed as a UTF-8 `str`. A body
    of fixed BYTE width `k` has character widths in `[⌈k/4⌉, k]`, so the superset is
    `1 ≤ min` and `max ≤ 4·min`. `é|ab` (pattern bytes `C3 A9 7C 61 62`) is 2 bytes
    wide on both arms. Native's latin-1 parse reads (2, 2). utf8's character parse reads
    (1, 2), which is inside the utf8 superset and outside `min == max`. It is computed
    outside pcrec, so the rule is "every
    fixed-width pattern with a start-origin `CR_DFA` site is selected or carries a named
    `why`", and an empty stratum shows (U-pop extends it to every start-row family). The
    instrument is designed here, not run (box rule; §R2);
  - **`selected ⊆ engine dfa`**, asserted;
  - **the `why` histogram**, first-match in table order (`conj.py` applies nothing
    after the table, §1.2) `[r3rc M-A]`. C8's failure is split two ways, as
    `exact/machine-inexact` (A's language is not a product) and
    `exact/producers-disagree` (the two producers' `S_d` differ, which the trace build
    asserts is 0) `[r3rc m2]`. C13's failure is split three ways: `no-row` (no kit row
    serves REPORT: the finder gate admits none), `kit-denied` (a row exists and a
    `--memfn=` deny, a SIMD level or the kit's size drop removed it), and `kit-none` (a
    row applies but the class DIFFERS from the stated set at some offset, either
    `proven[d] ⊄ S_d`, which is a false match, or `proven[d] ⊊ S_d`, which is an
    over-filter and a lost match) `[r3rc m1]`. With REQUIRED-all `kit-none` is a contract
    violation, which the default-build check turns into `pcrec_ctx_fail`; expected 0.
    `fact-denied` is C13's detail in the `-fno-kit-proof` arm.

**Where to attack §6.** (a) A reader of the abi number or the scan vocabulary that the
grep misses (the byte-count class is the known one). (b) X0's per-byte probe for `C_k`
when the body is followed by a lookahead. (c) Whether X5's byte identity survives the
`.list` move (the listing is not an artifact byte). (d) The getwidth denominator on
PCRE2-only syntax that python refuses.

---

## 7. Staging `[r3 con-B2, con-staging]`

| step | what | who | movers | gate |
|---|---|---|---|---|
| **Z0** | R-25: `proven0`/`proven_prev` honour `need` | kit | 0 (MEASURED, R-25's bar) | R-25's own bar |
| (kit) | R17-b′ B3b: span 0's BOUNDED class, PRES routed | kit | per B3b | B3b's |
| **Z1** | R-26.1-R-26.5's layout; pcrec states today's truth on every site (`prefix_stated` STATED, `exact_len` 0, `consumable_len` 0, `nctx` 0; MLINE as CONTEXT/FAILS/NO with `read_floor` SUBJECT) | kit (+ the builder lines) | 0 | emit_sweep 0 movers on every arm; G2 extensions; one `MF_SITE_ABI` event |
| **Zk** | R-26.6: the kit's REPORT row lands UNROUTED (`fd_rows[].routed` false), so the proving TEXT that B1 ships exists from here on | kit | 0 | kit suite; the row's G2 fixtures |
| **X0** | the libpcre2 oracle on the reading (`conj.py`'s shape, §6.4) | lane | — | set-equality and differential at 0 differences; plants S1130/S1131/S1136/S1139/S1140 red on the reading (S1143 is UNREACHED) `[r3rc]` |
| **Z2** | pcrec: `span_facts`' first slice; `MkLang`/`MkEnd`/`MkKnown`; `cover_conj[]`; the `cover` row and `emit_cover`; the default-build class check; true `exact_len` over the sent sets on every start-origin FIND site; the `--emit-facts` slice; `compound.c`'s field reads (§2.6). **Routing:** the default build and the trace build both decline `cover` (the trace build decides as the default does). Only `build/pcrec-harness --harness=kit-proof` routes both pcrec's row and the kit's REPORT row (the `--harness=no-compound` lever's shape, `compile.c:3351`); the kit side through `mf_preview` (below) `[r3rc M-B]`. **C17:** `emit_cover`'s door call site lands with a `pending` row in `site_manifest.tsv`, so rule 1 stays green. **`.list`:** the row carries no `.list` at Z2. If the self-check requires one, Z2 is a declared `--list-axes` delta (B3b's precedent) | pcrec | 0 (default build) | emit_sweep 0 movers; X1 and X3 on the harness-routed artifacts, which are B1's artifacts (same pcrec row, same kit text); K35; the agreement assertion |
| **measure** | directional hand timing on the dev box, in a window cleared with Frank (memory `pcrec-box-shared-with-frank`): harness-routed `cover` artifacts against default on lit-l8, year4, file-ext-order, hex8-bounded, `match`/`search_short`/`throughput` | lane | — | [KIT-VERIFY]'s D77 trigger; GO/NO-GO for B1 |
| (kit) | R17-b′ B4, the LOCKDOWN (set-site routing, M0's stamp, the size rung) | kit | B4's census | B4's |
| **B1** | THE ONE BYTE-MOVING EVENT, **after B4**: the REPORT row routed in the default build together with pcrec's row; `PCREC_NO_KIT_PROOF` (bit 57) and the listing's `fact_deny`; `.list`; the `"cover"` stamp; the C17 row `pending` → `delegated`; abi +1 with every §6.1 reader; spec hunks §6.2; S1130-S1148 land; the bench `[inbox]` note | pcrec + the kit's routing in one commit | the `cover` population (77 bench / 665 corpus native, 50 / 485 utf8 patterns, §1.2) `[r3rc M-A]` | the full battery (the manager's), mech for every new and moved anchor, `make test-axes` with the new arm, X5 |
| **official** | the bench's verdict on the targeted hardware (D144 add. 4) | bench, via main | — | — |

**Why B1 lands after B4.** Row edits are free until the lockdown (B4). The REPORT row is
added at Zk, before B4, as an UNROUTED row, so B4's committed `rows.tsv`,
`row_floors.tsv` and routed census record it as unrouted, and B4's one censused mover is
unchanged. B1 is then its own routing event after lockdown, with its own census, like
the S1/P1 rows R17-b′ adds after lockdown. Landing B1 before B4 would make B4's census
carry `cover`'s movers and re-open B4's predicted-mover manifest.

**Why Z2 routes through the harness, not the trace build.** In revision 1 the kit's
proving text landed only at B1, so X1, X3 and the GO/NO-GO at Z2 priced text that would
not ship, and routing in the trace build broke "the trace build decides as the default
does". Here the kit's row exists from Zk and the harness lever routes the same row and
the same pcrec code that B1 routes, so Z2's evidence IS B1's artifact. **The re-run
condition** `[r3rc M-B]`: B4 lands between Z2 and B1. If pcrec's row OR the kit's text
differs at B1 from what Z2 measured, X0, X1, X3 and the measurement re-run at B1, B4's
changes included. The comparison is mechanical: the harness-routed artifacts of Z2's
witness set, re-emitted at B1's parent and diffed byte for byte against Z2's.

**The harness lever's kit channel** `[r3rc M-B]`. `routed` is a compile-time bit of the
kit's own table (`finder.c:153`, read at `:964`), so a pcrec harness flag alone cannot
route the REPORT row. pcrec needs a kit-side channel, and the kit already has the shape:
`mf_reach` (memfn.h, R-MS6), a TEST-HARNESS call made once on an art before its first
define and never on a shipped compile, reached from `PcrecHarnessOptions.arm_reach` by
`--harness=arm-reach` (`memfn_sites.c:90`). The channel is one more such call:

```c
/* (R-26.6) THE ROUTING PREVIEW: a TEST-HARNESS facility, never called by a
   shipped compile. The host states that this art is a harness preview of the
   kit's routing step `step` (R-26's "R-26.6"); its artifacts are evidence and
   are never shipped. What the kit decides on such an art is the kit's.
   Called at most once, before the first define; refused after, twice, or for
   a step the kit does not name. */
int mf_preview(mf_art *, const char *step);
```

- **Field and call.** `PcrecHarnessOptions` gains `unsigned kit_proof : 1`, set only by
  `build/pcrec-harness --harness=kit-proof`. `memfn_sites.c`'s art setup calls
  `mf_preview(job->mf, "R-26.6")` when the bit is set, beside the `mf_reach` call, and
  pcrec's own `cover` row reads the same bit in its predicate.
- **The fence.** No shipped build reaches it, because the bit is set only through
  `pcrec_harness_compile`. That entry is the compound lever's: it carries the reserved
  prefix that `ns_reserved[]` row 3 refuses to callers, and `run_lever_fence.sh` holds the
  archive to exactly ONE global under that prefix (compound.md §A.11). The new bit rides
  the same entry, so it adds no global and the fence's count is unchanged. No
  uninterpreted `--memfn=` option reaches it either. `opts` passes through to
  `mf_opts_check`, which parses only the kit's `options.def` rows, and `mf_preview` is
  not one of them, so a `--memfn=` spelling of it is refused. The kit's G2/finder suite
  carries that refusal as a fixture (R-26.6's bar). A preview art writes no stamp of
  its own, and pcrec stamps a harness-built artifact as it stamps any other. That is why
  no gate may read a harness artifact as a default one (§7's "where to attack" (a)), and
  why the X1/X3 runs name `build/pcrec-harness` in their command.
- **D157-neutral wording.** pcrec states a FACT about its own build, namely that this
  art previews routing step R-26.6 and is never shipped. It does not name a row, a form
  or a routing decision. Which rows the kit routes on a preview art, and how, is the
  kit's (D157, D161 add. 6).

**Where to attack §7.** (a) Does any gate read a harness-built artifact as a default
one? (b) Does Z1's MLINE restatement (`read_floor` SUBJECT) move any kit text? (c) Can
B1 split into pcrec's entry and the kit's routing? It cannot: one depends on the other's
proof. (d) Does a kit row added before B4 move B4's `row_floors.tsv` floors?

---

## 8. Standing questions, the sibling family, unlocks, questions for Frank

### 8.1 The three standing questions (`docs/design/CLAUDE.md`)

1. **The measurement regime: RELEVANT.** Every payoff figure is DERIVED, from armread's
   Zen 4 constants (kvcensus §6) and the compile-side counts. The size twin is size only.
   The regime that could flip the decision is the kit's side. On a one-byte PF site in a
   dense regime (`\d{4}` over digit-dense text) the REPORT description's added
   verification runs on every false candidate. The `measure` step is a short, directional,
   same-box run over `match`, `search_short` and `throughput`, and the official verdict
   is the bench's (D144 add. 4). Savings are per MATCH, so a sparse `throughput` cell
   should read near null, which is expected.
2. **The independent control: RELEVANT.** §6.4. X0/X1 read libpcre2 with per-byte sets
   and full-alphabet subjects. The C8 control compares two producers that share no code.
   X5 is byte identity. K35's denominator comes from python. X2 plants the failing
   directions with reach witnesses. `conj.py`'s recount shares kvdfa with the census and
   the critic, so it is a RECOUNT, not a control.
3. **What moves when data is regenerated: RELEVANT.** The kit's row choice may read the
   analysis object or a measure set (D162, D166). Regenerating either can flip an
   artifact between `cover` and `composite`. Its answers stay identical and its bytes
   move, which is an abi event (D162 ruling 1). It also moves `run_form_census.sh`'s
   `RX_DFA_SCAN` floors, `memfn_arm.py`'s classes and the startset manifests, so each
   regeneration carries their re-derivation `[r3 con-staging]`. `RX_DFA_SCAN` shows the
   flip and the [KNOW-SRC] `consulted` stamp shows the data was read. Regenerating the
   census moves nothing: it is evidence, not an input.

### 8.2 The SIBLING-FAMILY lens `[r3 fam-M1]`

- **"The match is fully known here":** three slots (§2.1). Rows are distinct by WALK.
  The FACT (`MkKnown`) and the FINISHER (`FIN2 report`) are source-neutral. The VM-side
  members fold into [CAPS-KNOWN]'s one FINISH `report` with a group map (UL-1). U-anch is
  a VERIFY member.
- **Context as a per-position fact:** MLINE's `{\n}`, the 23 shifted origins, the seed
  table, the VM's `A_CTX`, the `-bounded` view family, D164's end set. The machine
  reading is the DFA-side general form for stage 1. The facts-layer reading takes over at
  U1b (UL-8). D164's END_MARK tail is the after-end context span's general form (UL-5).
- **The absent rule:** `\A`/`^`, `\z`, MLINE's edge, `\G`'s `search_from`, now one enum
  per CONTEXT span.
- **The proven family** (kvp-unlock's 12 members) belongs under [MATCH-KNOWN] (§5.3).
- **The position-pin family:** `span_facts`' first slice joins it as its newest member
  (window_contract §5.6), built here (UL-0).

### 8.3 UNLOCKS, each with its trigger (filed, not designed beyond it)

| id | unlock | trigger (D77) |
|---|---|---|
| UL-0 | `span_facts`' first slice | **IN U1** (Z2) |
| UL-1 / U1b → **[CAPS-KNOWN]** | one FINISH `report` on the VM and hybrids with a tag-determinism group map, folding [PF-KNOW] det_all, start_landing U1 and U1b. Frank's PARTIAL determinism: determined groups written, the VM entered after the determined part. `caps == NULL` callers are compound's CAPTURES-ON-DEMAND client. Population: 85 corpus + 3 bench hybrids with fixed-offset groups (`(?'w'cat)`, bench `grp-named-quote`) | the plan row's own: a compile-only census per GROUP (D142's trigger; the census is its first step) |
| UL-2 | `end-minus-width` reads the priority width (census via kvdfa.whole) | a RECOVER decline counted where the priority width is fixed and the language width is not |
| UL-3 | X5 as byte identity | **IN U1** (B1) |
| UL-4 | typed LOCATE reads in compound.c | **IN U1** (§2.6, by B1) |
| UL-5 | the after-end context span = D164's END_MARK tail (D164's L-table extension) | a `tagged` (F2) body with a kit site that C5 declines |
| UL-6 | a neighbour-set assertion fold as a true lowering of `\b` (definitions_table + possessify arm A) | BOONIES: a VM-only `\b` cell where the context test shows in the profile |
| UL-7 | `MkKnown` keyed `(point, origin)` with `(src, fact)` conjuncts and length bounds | the second [MATCH-KNOWN] member |
| UL-8 | the facts-layer context fact (the leading/trailing `LOOK`/`A_CTX` reading) | U1b ([CAPS-KNOWN]) |
| U-X0 | X0 before Z2 | **IN U1** (§7) |
| U-z | `cover` serves `\z` bodies where `rev-end` declines (`cat\z` exact; 1 bench / 10 corpus in the deny arm today, `conj.txt` C) | a `\z` cell `rev-end` declines in the default build |
| U-bisim | admit ATT for `(?m)^` by bisimulation (row identity declines; S-set comparison unsound; BOUND is answer-bearing on ATT) | a `(?m)^` cell on the attempt route in a losing bench cell |
| U-oracle | one libpcre2-probed language-fact oracle for every [MATCH-KNOWN] language fact | the second such member, or an X0/X1 under-claim |
| U-required | REQUIRED-all REPORT needs no ask: pcrec's language test plus the measured gate | a Z2 `why` `kit-none` > 0 on a bench cell, or a measure-set regeneration that flips a cover artifact |
| U-pop | the getwidth superset as the K35 denominator for every start-row family | the next row counted from pcrec's own machines |
| U-anch | anchored whole-cover with no kit site (VERIFY family) | a validator cell (`^\d{5}$`) in the `match` regime where A's `k` steps show |
| U2 | the DFA entry past the proven prefix | a timed class-led cell (median consumable 1) |
| U4 | context spans to seeded DFA_SCAN/DFA_HAT sites as a filter | a measured seeded `\b…` cell |
| U-mline | MLINE states `absent` SATISFIES and pcrec's edge retires | a `(?m)^` cell whose edge attempt is measured |
| U-ctxorigin | re-express the 23 shifted-origin sites with origin = the match start | **its `cover` half is IN U1** `[r3rc M-A]`: with C2 retired, the 12 / 9 corpus context joins are admitted (`conj.txt` B, `no-start-site`). What is left is the non-`cover` shifted-origin sites themselves. Trigger: one such site in a losing bench cell |
| UL-n1 | retire C2 `origin-start` | **DONE in revision 2.1** (the trigger, a conjunct with no weight, was met) |
| UL-n2 | the default-build define/ask class check (§2.5 step 2) as a SHIPPED invariant for EVERY REQUIRED kit site, not only REPORT sites | the next trace-only define/ask mismatch, or U2 (the first non-REPORT reader of a REQUIRED proof) |
| UL-n3 | `MkEnd` is exact for every view-free fixed-width DFA body once C9 covers the walk, which makes it UL-2's input (the priority width with no separate census) | UL-2's trigger: a RECOVER decline counted where the priority width is fixed and the language width is not |
| U-iter | the D165 iterator drives `cover`'s stream | D165's build |
| U-match | `_match` on a `cover` artifact via a kit VERIFY of `k` positions | a `match`-regime cell on a `cover` artifact |
| U-union | offset-pinned union spans raise `exact_len` through a narrow multi-byte class | the first losing utf8 cell inside a `cover` consumer's prefix |

### 8.4 Questions for Frank

**Q1, captures in U1: RULED** (Frank, session 117): separate. Captures are not in U1.
They are plan row [CAPS-KNOWN] (`docs/dev/plan.md`), including his partial-determinism
point. For `(abc)(\w+)` group 1 is determined, so the finisher writes it and enters the
VM after the determined part, at a compile-time VM state with no open choice, no skipped
assertion and no meter change. Stage 1 is `CR_DFA` only, where dead groups are FIN2's
existing fill. O3 ("only the VM hat writes groups ≥ 1") is RESTATED in [CAPS-KNOWN] as
"groups are written by the finisher from a per-row table", not given an exception.

**Q2, is `cover` source-neutral?** *Panel's answer:* neutral in
the FACT and the FINISHER, not in the ROW (fam-M1). A row is a walk. A second source of
"fully known" is a different walk (an exact hybrid's prefilter, a group map), so it gets
its own row in its own slot, reading the same `MkKnown` and finishing through the same
`FIN2 report`. Naming the row after its walk (`cover`, the kit's stream) is then not a
special case. **RULED (Frank, 2026-10-18), stronger than the panel** (revision 2.1 deletes
the stale PENDING label and keeps the ruling `[r3rc m8]`): every mechanism is a
FACT PRODUCER stating what it adds at a point into one keyed record, and ONE static evaluator
walks the engine program over it ("walking a VM and seeing what's left"); rows stay distinct by
their runtime walk. ORDER MATTERS: for `\d{10}$` the forward digit facts applied before
rev-end's end fact lose the end fact, so the evaluator sees every producer's facts before the
runtime order is chosen (position-pinning facts first). U1 is the first instance (one producer,
the DFA evaluator); [MATCH-KNOWN]'s charter carries the architecture.

**Q3, the `\b` "rewrite" as a reading.** *Panel's answer, PENDING FRANK'S RULING:* the
reading is right for stage 1, labelled DFA-only. At U1b the facts-layer derivation
becomes THE context fact and the machine reading its control (fam-Q3). A true lowering,
the neighbour-set assertion fold, is filed BOONIES-style (UL-6). *Leaning:* as the panel
answers.

**Q4, one deny for the proof family.** *Panel's answer, PENDING FRANK'S RULING:* one FACT
deny, `-fno-kit-proof`, that empties the proof (fam-M6). Every consumer of `MkKnown`
declines naturally, so one bit serves `cover` and every later T-PROOF member with no
per-row field, and X5 becomes a byte-identity gate. Denying `cover` alone once U2 lands
would be a per-row split, filed with its trigger (a measurement that needs it).
*Leaning:* as the panel answers. Bit 57, leaving 6.

The answer-free choices are made in the note: the row spelling `cover`, `MF_SK_REPORT`,
the carrier name `ctx[]`, `read_floor`'s enum, the harness lever's spelling, and the
sabotage numbering.

**Where to attack §8.** (a) A cell where `cover` is SLOWER (the REPORT description's
verification on a dense false-candidate stream the DFA would reject in one step). (b)
Whether a FACT deny can express "deny `cover`, keep U2". (c) Does each unlock's trigger
name a measurement that exists rather than one that needs building first?
