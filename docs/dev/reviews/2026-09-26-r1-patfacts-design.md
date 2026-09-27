# 2026-09-26 r1 — D6 panel on the [PATFACTS] step-2 design

Subject: `lane/pfdesign` at b0949d52 (`docs/design/patfacts/design.md`,
`inventory.md` "Delta 2026-09-26", `docs/dev/lanes/pfdesign_report.md`).
Three read-only critics, none ran `make`:
- **pfcrit-arch** (opus): architecture and migration soundness, plus Frank's
  relocation question.
- **pfcrit-checks** (sonnet): checks, gates and sabotage.
- **pfcrit-fidelity** (sonnet): fidelity to the code. It sampled ~55
  citations: 52 exact, 2 imprecise, 1 miss.

Dispositions: **FIX** = the revision lane applies it; **RULE** = goes to
Frank; **NOTE** = recorded, no change needed.

## Frank's question (raised 2026-09-26 evening) and the relocation verdict

Frank asked whether keeping each analysis in its first consumer's pass file
"cause[s] crazy interdependencies when area A writes the analysis but it's
used by unrelated area B or even C". §4.2 says "the derivations do not
move files". The [OPT-REQRUN-ENC] incident is the example: the run pick
evolved inside `reqbyte.c` as a REQPOS-specific choice and silently
diverged.

pfcrit-arch verdict: **ADOPT WITH CARVE-OUTS.**
- No core fact needs a pass's internals. `rb_walk` and its lattice
  (reqbyte.c:164-380) read only the Ast. The k-set walk (prefix_k.c:195,
  :248) reads only the Nfa. endwin and startanch read the Ast plus the
  encoding descriptor.
- The one real coupling is the pin as used today. It is gated on
  unanch_start's DFA start-state verdict (emit_dfa.c:3632, :3719). The
  cure is to make the pin a pure NFA+window fact and make the kind gate an
  explicit CONSUMER obligation, as pf_run_applies_common already does
  (:5294).

Carve-outs, all adopted:
- **(a)** Split `core/internal.h` FIRST. Derivation declarations move to a
  facts-private header. Otherwise "consumers include only facts.h" passes
  vacuously, because every file includes internal.h.
- **(b)** Derived and rate readers (rb_pick, rn_scan_index,
  rn_window_start, set_ppm) go with B1's rate primitives, not with the
  walk files.
- **(c)** Decisions stay in their passes: G1 `req_byte_dominated_by` and
  the offset-k SELECTION.
- **(d)** The encoding descriptor is a declared layer input (endwin.c:156).
- **(e)** One relocation per commit, each under the zero-movers gate.

**Manager recommendation: adopt → RULE (Frank, Q11).** The revision drafts
it as the proposed layout.

## Findings

| # | critic | sev | finding | disp |
|---|---|---|---|---|
| A1 | arch | BLOCKER (3.2) | The E1 lazy memo plus in-place `pcrec_lower_enc` (compile.c:1488) makes E1 answers depend on ask time. cwmax(`é`) computes 2 (bytes) on the lowered tree while labelled characters, and §3's E1 cross-check would fire on every non-ASCII utf8 pattern. | FIX: force E1 facts eagerly at the E1 seal, and drop root cwidth from E1. Its one reader, endwin.c:172, runs at E2 and is gated to single-byte encodings. See A8. |
| A2 | arch | MAJOR | 3.4 is the likeliest byte-mover and is unflagged. (i) The pin is gated on DFA start state (emit_dfa.c:3719), so a pure NFA pin is true where today's is 0. (ii) The "core" walk reads the prior (prefix_k.c:444, :476). | FIX: flag 3.4 as a possible mover. State the kind gate as a consumer obligation on every pin row. Move ppm into the selection half so core stays prior-free. |
| A3 | arch | MAJOR | The E3 seal is undefined on ENG_ATTEMPT: a forward NFA is built (compile.c:1539) but never wrapped (:1651 vs :1694). §11.4's "absent / decline:no-forward-nfa" is false there. | FIX: per-branch seal, plus a named decline token for the unwrapped route. Never force E3 there. |
| A4 + C2 + C3 | arch, checks | BLOCKER (check) | The §4.2 one-caller grep is file-granular: blind when owner and consumer share a file (prefix_k.c). It can't tell root from subtree calls. It is blind to RE-DERIVATIONS (R13/R4/R12). Its target list is hand-kept. Its sabotage re-inserts the grepped string. | FIX: superseded by the relocation. Use an include-graph check over the facts-private header (after the internal.h split). The sabotage row adds that include, independent of any grep string. The target list is generated from facts.def's owner column by a plain-text scan. Re-spelling is controlled by the layer's shape (helpers private) and stated as residual. |
| A5 | arch | MAJOR | §8.1's fallback (B1 lands first, editing today's sites) contradicts D125 addendum 1 reason (2). | FIX: delete the fallback. 3.0 is a hard prerequisite of B1. |
| A6 | arch | MAJOR | S2a exercises no memo, epoch or deny (a node pure function). The pattern-grain machinery has no first customer beyond migration. | FIX: say so plainly in §0/§8. RULE is folded into Q6: build S2a now, or wait for S2b as the real customer. Manager view: keep 3.0 + B1 as the machinery's customers (B1 uses the deny and the rate accessor); S2a stays independent. |
| C1 | checks | MAJOR | §9's "a mover in a no-abi step is a FINDING, never an abi bump" has no rule for a genuinely cosmetic move, which D76 absorbs as an abi event. | FIX: a classification procedure. SEMANTIC movers (a value, stamp or code path differs) are a K-row. SCAFFOLDING movers (text, comment or layout only) are the ordinary D76 ritual, with the diff attached to justify the class. |
| C4 | checks | MAJOR | The dump's completeness count could come through the same X-macro path as the printer. | FIX: the count comes from a plain-text scan of facts.def row markers, never through the macro path. |
| C5 | checks | MAJOR | The why-truthfulness oracle is facts.def's own deny column, which also drives the deny logic. | FIX: the oracle is tuning.md's per-flag consumer lists (§7.2, hand-written, D80). |
| A10 | arch | MAJOR | The non-perturbation check (§11.6-1) cannot fail at birth: it lands in 3.0, where forcing a pure memo moves nothing. | FIX: born with B1. Its failing direction is shown by the sabotage "force before stamps" on a B1 fact whose `used` changes a stamp. |
| F4 + F5 | fidelity | MAJOR→MINOR | S2a's run is empty under caseless (`[Aa]` is not a singleton; cpset.c:305), and the design never mentions caseless. The definition also omits the `k == A_CLASS` guard every pcrec_cls_single caller uses (union read on A_VAR/A_BREF). | FIX: state "exact only; caseless is [OPT-LITSCAN] S4's" (this is by row design, not a hole), and write the A_CLASS guard into the definition. |
| A7 | arch | MINOR | `fit.lang_nullable` and `fit.prefilter_has_collapsible_rep` stay as copies beside their accessors, the dual home §5.4 forbids. | FIX: migrate them with their E1 accessor. |
| A8 + F2 | arch, fidelity | MINOR | Node-grain calls are listed as consumers of pattern facts (startanch.c:84, endwin.c:88, mod_lookaround.c:534). startanch.c:80 is rejected-alternative prose. | FIX: correct the §1 table. Drop root cwidth from E1 (no E1 consumer, D77). |
| A9 | arch | MINOR | END_WINDOW (emit_dfa.c:8567) is missing from §11.5's renderer list. | FIX: add it. |
| A11 | arch | MINOR | Forcing after emission can REFUSE a completed compile (arena OOM longjmp, the epoch guard's ctx_fail). | FIX: the force loop is guarded. Spec promise: "never refuses a compile that succeeded". |
| A12 | arch | MINOR | Decision capture assumes one stamp primitive, but raw printf stamps exist (emit_dfa.c:8966, 15 sites in emit_vm.c). | FIX: capture scoped to the final attempt's artifact buffer. Check 4 already catches misses. Name the raw sites. |
| A13 | arch | NIT | endwin.c:156 reads `cx->opt->encoding`, against §0.5(a). | FIX: covered by carve-out (d). |
| C6 | checks | MINOR | The E1 invariance sabotage covers kind-mask only; nullability has no witness (width is dropped per A1). | FIX: add a nullability sabotage row. |
| C7 | checks | NIT | assertions_design §8.4 is miscited. The real precedent is [M5-SEAM] DD-12(7) (run_codegen_tests.sh ~1029-1057). | FIX. |
| F1, F3 | fidelity | NIT | compile.c:1678 → 1681/1683; emit_dfa.c:7427 → ~7398-7423. | FIX. |

**HELD** (verified by pfcrit-arch and pfcrit-fidelity):
- The per-attempt reset: Ctx per iteration, Job calloc, one setjmp.
- No emitter mutates the AST after lowering.
- Kind-presence and nullability are lowering-invariant.
- The epoch line numbers.
- 3.0's zero-movers claim.
- §7.2's deny witness table, reproduced byte-for-byte.
- §6.3's NONE-per-question-kind reclassification, which is arithmetically consistent with the code.

**Also owed (manager):** the reqrunenc2 amendment to reqpos_2b.md §2.3
says rb_pick "keeps its leftmost fallback". It is rightmost. Fix on main
after reqrunenc2 merges.

## Next

1. A fresh revision lane applies every FIX and drafts the relocation as
   the proposed layout, with Q11.
2. Frank rules Q1-Q11.
3. Step 3.0 opens.
