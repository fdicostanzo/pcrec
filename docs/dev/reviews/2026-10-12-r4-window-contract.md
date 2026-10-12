# 2026-10-12 r4 — D161 window contract note (docs/design/memfn/window_contract.md), light D6 panel

Critics (read-only, no make): wcpanel1 (opus, semantics/exactness), wcpanel2 (sonnet, flexibility / facts-not-methods / interface).
Verdict: the shape holds (keyed analysis kinds; one-origin site; [L,U] reply; additions do not break layout). Revision owed: 1 blocker, 10 majors. Dispositions PROPOSED by the manager; R2 (the proven channel) needs Frank.

## Semantics (wcpanel1)
| id | sev | finding | disposition |
|---|---|---|---|
| E1 | BLOCKER | "FIND miss = NOMATCH" (§2.4) is false for the MLINE row: `(?m)^abc` matches at 0 with no `\n` before it; today pcrec skips the FIND at the edge (emit_dfa.c:12376; `\G` makes search_from the edge). Any negative-offset span at lo == 0 / search_from. | Necessity "for every m > edge" with an explicit edge-exempt bit, or keep negative-offset spans off window sites; qualify NOMATCH-on-miss. |
| E2 | MAJOR | The producer cannot carry `start_set` or the k-set (`a?bcd`: start {a,b}, kset {a,b},{b,c},{c,d}; `a*bc`): unions over paths at a fixed offset. §5.1 "absorbs" and §8.1(iii) overstate; C-SP1/2 pass vacuously there. | Keep start_set/kset as facts, or a third span kind (offset-pinned union) per unlock (b); non-vacuity floors on C-SP1/2. |
| E3 | MAJOR | T-CUT makes presence exclusive with segment-0; `a.*zxq` never sends the `zxq` reject (reqpos_2b's measured win, 1.46 of 10.284). | Presence its own column/table (unlock (c): a zero-cost first link). |
| E4 | MAJOR | T-PROOF `dfa-exact-prefix`: δ*(s0, bytes) is not constant on seeded/context machines (`\b`, `(?m)^`, `\G`, lookbehind before L; emit_dfa.c:12398-12410). VM row must not skip an interleaved assertion or move the WORK meter (D158). | Decline on seeded/viewed machines (or key by seed class); VM conjunct "no assertion, no meter change". Moot if R2 removes the channel. |
| E5 | MAJOR | Range underspecified: starts vs occurrences under move_back > 0; reads below lo for negative offsets; utf8 round-up of L and U+1 (litscan_k82h Claim 3). | Define all three in §2.3. |
| E6 | minor | Sequence rule held (no counterexample) but is a TIGHT HULL, not exact; soundness needs omin/omax as prefix sums (pcrec_minw under-estimates; rn_tail_off takes subtree maxw). | State the obligation in §5.2; under-estimate plant in C-SP4; say "tight hull". |
| E7 | minor | Resume at U+1 sound only if the consumer rejects every start in [L,U] for ANY match; 2-chain U ambiguous. | Window = intersection over the spans used; proof position defined only when L came from span k unclamped. |
| E8 | minor | req_set_maxoff is a min across factors; C-SP3 must compare against the min over that byte's spans. | Fix C-SP3. |
Family: span_facts is the newest member of the position-pin fact family (start_set, kset, run_pin, end_pin, compound's split facts, landmark K); compound.md U3 already proposes unifying it — specify span_facts as that family's member, not a parallel producer. Unlocks: (a) end-origin spans (trigger: first kit-delegated reverse walk / [OPT-ENDWIN-ENC]); (b) offset-pinned union spans with per-group spans_seq (trigger: S4's offset-k move); (c) presence as a chain link (trigger: first a.*zxq-shaped cell with both).

## Flexibility / facts-not-methods (wcpanel2)
| id | sev | finding | disposition |
|---|---|---|---|
| R1 | MAJOR | S1 is not zero-mover: building the object forces `byte_rate_asked` (findings.c:373-381), so `<PREFIX>_FINDINGS` / `rx_info.findings` move from "" on artifacts with no prior asker; the stamp is a consumption record; digest regeneration moves bytes; run-rarity not in the stamp. | S1 is an abi event with a mover census and a D80 hunk; the stamp means "offered", one entry per kind. |
| R2 | MAJOR | `mf_result.proven` makes pcrec's bytes depend on the kit's method (varies with -fmemfn-simd and --memfn= denies: breaks C18/RQ-3 neutrality, reads method back, D157), and is redundant: a REQUIRED span's positions are proven by definition. | Delete direction (2); pcrec promotes a span to REQUIRED to rely on it; Q12.2 and the occurrence out-hook disappear. **Frank's call** ([KIT-VERIFY] direction 2 was his). |
| R3 | MAJOR | §4 specifies the kit's method (resume semantics, G2 family, 3+-link mechanics); §11 lists a kit output as a pcrec capability. | Keep only facts (pairwise distance under spans_seq; reply totality); §4.1 as the quoted D161 add. 5 ruling. |
| R4 | MAJOR | Silent zeros: `mf_prov.source` PRIOR_AUTHORED = 0; `mf_need` MF_REQUIRED = 0 now binding; spans_seq cannot state "not sequential"; byte-rate "present" with a NULL payload under utf8. | UNSTATED sentinels; tri-state or alt_group; invariant payload non-NULL iff present && source != NONE, checked at define. |
| R5 | MAJOR | S2/S3 leave the NONE rule spelled twice (pcrec's picks stay until S4) with nothing comparing them (R13 shape). | Keep the shadow until S4, or move the picks first. |
| R6 | MAJOR | S3 touches more than stated: D27-blinded G2 generators (g2_gen.c, g2_simd_gen.c — needs a blinded lane), arm_fixtures, memfn_sites, run_rank/rank_check, six `consumer` setters; `plan_hint` is READ by kit arms (retire only at S4). | List them; a blinded lane for G2. |
| R7 | minor-major | "Permanently refused" UNBOUNDED move/over is a compose.c code change (compose.c:405 exempts it on lane/memfn-r17) + a refusal test; explain span_hi UNBOUNDED legal vs move refused. | State as a kit change. |
| R8 | minor | Name collisions: "W8" (built SWAR block vs rejected span index); "span" vs mf_site.span_lo/hi. | Rename. |
| R9 | minor | Event-table gaps: need/preds re-reading on FIND is an MF_SITE_ABI event; no row for mf_prov/mf_akind layout or a per-site analysis slot; mixed NULL/non-NULL analysis in one art. W7 is an MF_SITE_ABI event. | Add rows. |
| R10 | gaps | Setfind §9.2's decline arm needs a per-site call-pattern/activation fact (no slot filed); mf_prov lacks evidence strength (exemplar size). T-MEMO row 1 is a trigger, not a predicate; T-CUT rows lack a deny column (D46). | File both facts with triggers; label/fix the tables. |
Verdicts on the kit's proposals: W8-span-index and W9 rejections sound (U+1 resume checked for a non-span-0 locator); W10 to the analysis object sound; storage, W0-W3, N5, N6 agreed (R7 caveat); W7 agreed (an MF_SITE_ABI event).
