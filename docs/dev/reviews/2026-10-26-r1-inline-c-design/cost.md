# COST critic, inline-c

Lens: cost and overlap (D77, D153) plus the measurement standing questions of
docs/design/CLAUDE.md applied to goal 3b, stage 2's card and stage 4's card.
Subject: the frozen copy of inline_c.md (rev 0). Read-only; probes under
/tmp/claude-1001/crit-inline-c/probes/cost/ (compiles of callout-free
patterns only). No denylisted file was opened and none auto-injected.

## Cost ledger (what each stage costs, buys, and is triggered by)

Counts are from the note's own §8-§9 text unless marked "grep".

| stage | code | abi event | spec files touched | sabotage rows | what it BUYS | trigger (D77) |
|---|---|---|---|---|---|---|
| 1 call site, extern-bound | parser node, VE_CALLOUT producer in emit_vm.c, marked-set union, return-table rows, one pf_admits row, a rule across the optimizer passes (COST-1: grep says ~19 src files), position table, namespace row | yes (stamp `_CALLOUTS`, rows 9-10) | match_api.md (3 sections + new callouts section + stamp table), cli.md, pcre2_compliance.md | 7 (S-IC1..6b) | composable callouts (named bindings, artifact-as-callout); nothing for the casual C user alone | Frank's Q2 ("callout call site is the first build step"): a ruled direction, but the plan row [M4-CALLOUTS] still reads unscheduled boonies; no measured need exists or is claimed |
| 2 embedded C | `(?{` C scanner, tag grammar, generated function/macro set/#line, `code-header`, `--allow-code`, `pcrec_options` member, `_CODE` stamp, ~5 entry-point refusal tests | yes | match_api.md, rxt_format.md (2 sections), cli.md, compliance, tuning none, guide page | 5 | goals 1 and 4: the actual headline feature | Frank's UC-1/UC-3 asks (requirements §8) |
| 3 pins + reviewer view | in-tree SHA-256, provenance chain through include/lib, rules 5.4/5.5, `--list-callouts` | no | rxt_format.md (2), cli.md | 3 | reached-file code (a lib with code). Stage 2 alone refuses ALL reached code, so nothing in stages 1, 2, 4, 5 needs it | none named: no user with a code-bearing lib is cited (COST-7) |
| 4 verify | prefilter language rule, 7-row eligibility table, new axis + flag bit, `scan-end` attempt row, `_CALLOUT_VERIFY` stamp | yes | tuning.md, match_api.md (2) | 3 | goal 3b only | goal 3b is unmeasured; Q4 rules the mode, not the build (COST-4, COST-5) |
| 5 PCRE2 wrapper | one macro in every callout artifact's `.h` | rides stage 1 or its own | match_api.md | 1 | porting of PCRE2-convention functions; Frank: "I doubt this would ever come up" (Q6) | none (COST-9) |

Totals: 19 sabotage rows (S-IC1..18 plus 6b), 4 abi events (1, 2, 4, 5; 5 may
ride 1), 8 spec files touched, 1 new `pcrec_options` member, 1 new axis (flag
bit), 5 new stamps/macros families, 3 new CLI options plus a `--list-*`.

## Findings

### COST-1  Stage 1's "one rule, every pass" has no shared predicate to read; the stage is a ~19-file cross-cutting change the note prices as one row
- status: CONFIRMED. `git grep -c A_BREF -- src` at main: internal.h 21, emit_vm.c 19, atomic.c 16, possessify.c 12, revdet.c 10, mrl.c 8, mod_backrefs.c 6, select_engine.c 6, and one to three each in lower_enc, derive, altcls, nfa, widths, startanch, endwin, startset, req, callgraph, parse, definitions, ctxnode, mod_*: about 19 `src/` files, no one capture-reading-consumer predicate (the nearest, `pcrec_ast_crosses_attempts`, internal.h:8004, answers the attempt-scope question, a different one).
- severity: maintenance (cost) and answer (a pass missed is a miscompile: S-IC3, S-IC6b)
- effort: section rewrite of §1.8 and §9.1 stage 1; build cost is the whole point
- blast radius: stage 1's "zero movers" claim (§8.1, goal 3a) now depends on a refactor of passes that currently each treat `A_BREF` locally being byte-identical for every non-callout pattern
- where: inline_c §1.8 ("each pass already answers for A_BREF ... the build lane makes each pass's fact table read the callout through that same predicate"), §9.1 stage 1
- argument: the sentence presents the unification as something the passes already support. They do not: each pass tests `A_BREF` at its own sites. So stage 1 is two pieces of work, (a) introduce the shared "capture-reading consumer, width W" predicate and move ~19 sites onto it, then (b) add the callout. (a) is a remodel in its own right, with its own zero-mover risk to every backreference pattern, and it touches files under in-flight rows (COST-8). Costlier must prove more; the note does not price (a), and a test for each site is not listed (S-IC3 and S-IC6b cover two of ~19).
- proposed fix: add a census paragraph (list the passes that must read the predicate, one test row each, drawn from a grep like the one above) and split stage 1 into 1a (the predicate, zero-mover, on `A_BREF` alone) and 1b (the callout).

### COST-2  The "call-site return table" the note extends already exists, in a different file, with a different convention and its own table-kit obligations
- status: CONFIRMED. `src/gen/emit_compound.c` `callsite_rows[]` (compound.md §A.14): rows `span r > 0`, `nomatch r == 0`, give-up, internal, utf, startpos, unset-var, `reserved r < 0` trap; rows emitted by `can_return(PcrecPartFacts)`; the table is a table-kit root ("C1 trace site key `compound-callsite`, a `TABLE_ROOTS` root, a reach witness per row"). The note's §1.6 has success `>= 0`, fail `-1`, rows 9-10 checked BEFORE row 1.
- severity: design / maintenance
- effort: paragraph edit (§1.6) plus a build cost the note omits: lift the table out of emit_compound.c, reconcile the convention, add a width-class fact to the callee facts
- blast radius: the compound's B4 controller output (abi 77+) if the shared table's convention moves; a `reserved: r < 0` row would trap a callout's `-1`
- where: inline_c §1.6 ("`match_api.md` §4¶10 ... a callout site is the table's second producer"); compound.md §A.14; emit_compound.c lines ~15-90
- argument: the note says "extends match_api.md §4¶10" and never cites §A.14 or the built table. As written, "rows 9 and 10" is not an addition to a table the VM emitter can call: the table is private to emit_compound.c, keyed on a `PcrecPartFacts` struct that has no width class, emits through combinator statements (`succ`/`prop`/`fail`), and has `-1` in the trap row. House rule "one table per slot: no private copy" (docs/dev/guide/architecture.md) cuts both ways: copying the table into emit_vm.c is the failure mode; lifting it is real work in a file COMPOUND/ENTRY-TABLE are editing.
- proposed fix: state in §1.6 which file owns the table after stage 1, that the convention differences are reconciled there (a callout returns `-1` for fail; a part returns `0`), and add "lift `callsite_rows[]` to the shared emit layer" to stage 1's list with its own zero-mover check against B4's artifacts.

### COST-3  `verify`'s `scan-end` is a second implementation of what compound.md already designs as `locate-then-finish(L; external verifier)`
- status: CONFIRMED by text. compound.md §A.2 type-check paragraph: "an external callee of type `verify-at` (a pcrec-compiled or caller-bound matcher with the `rx_matchfn` shape) type-checks as the finisher of `locate-then-finish(Q; external verifier)`, because a callout and a part are one thing at two binding times (alignment §4, unlock U6). No client uses it yet"; the combinator table row `locate-then-finish(L; V)` ("the hybrid's shape, across parts"); plan [COMPOUND] clients list "DFA-locate + VM-finish". The note's §4 and §10a-4 never mention it.
- severity: design / maintenance
- effort: section rewrite of §4.2 (or a ruling that it stays); no code yet
- blast radius: stage 4's attempt row, its 7-row eligibility table, the axis, and the entry emission under [ENTRY-TABLE]
- where: inline_c §4.2 ("The hybrid's attempt loop gains one row, `scan-end`"), §10a conflict 4; compound.md §A.2, D163
- argument: D163 rebuilt MATCH-SPLIT as a composite precisely so locate/finish pairs stop being new rows in the hybrid. The note adds a new hybrid-private mechanism for locate-then-verify-then-fallback, beside a combinator whose type check was widened in advance for this exact callee. Per memory "general mechanisms, not special cases" and "forest for trees", at the second member the unification question is the standing one. Conflict 4's reading (a) (stay a VM hybrid, F7 literal) answers F7, not this. If verify is a compound client, F7 also needs its own reading (a compound's finisher is a VM part: still VM-only, arguably).
- proposed fix: add a conflict row 8 to §10a naming compound.md's U6 and ask the manager to rule hybrid-row vs compound-client BEFORE stage 4 is briefed; the answer moves the stage's cost and which remodel it overlaps.

### COST-4  Stage 4 is built ahead of a measured need, and the note's own flagship example is ineligible for its speed benefit
- status: CONFIRMED (text plus probe). The requirements' UC-1b (`^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$(?C{ return all_le255(RX_SUBJ, ctx->caps, 4) ... })`) reads four captures. Under inline_c §4.3 row 5 an artifact with `NCAPS > 1` is "hybrid without `scan-end`: the VM walks `[s, ...)` for the captures"; §4.2 step 1 builds the tail view with `ncap = 1`; §4.5 says a capture-reading segment gains only "when [CAP-SPAN] places captures", and [CAP-SPAN] is `STATE:not-started`, unscheduled. Probe: `build/pcrec -p rx --emit-main --pattern '^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'` stamps `RX_ENGINE "vm"`, `RX_ENGINE_WHY "capture group at pattern offset 1"`, `RX_VM_RESEED "exact"`; the capture-free `^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$` stamps `RX_ENGINE "dfa"` (a plain DFA, so what row 4 `no-scan` means for it is not stated).
- severity: speed / design
- effort: section rewrite of goal 3b and §9.1 stage 4; a measurement, not a build, to settle it
- blast radius: goal 3b, stage 4's whole cost (7 table rows, axis flag bit, attempt row, 3 sabotage rows, abi event, 3 spec hunks)
- where: inline_c goal 3b, §4.3 rows 4-6, §4.5, §9.1 stage 4, test "UC-1b answers equal UC-1a's"
- argument: the eligible population is: segments in the tail only, reading no capture group, in a pattern with no capture group at all, whose erased scan is built and proves the end, with a W_PRED erasure. The note counts none of it (K35: nobody counts the population). The headline validator (octet <= 255, which needs the digits' groups) falls out. Stage 4's own UC-1b test would pass by downgrade (answers equal) while proving nothing about speed, so the stage can land with goal 3b unfalsified. D77's shape is: name the measurement that would trigger the build. Q4 (Frank) rules the MODE, "verify first"; it does not order the build ahead of a census. Also [POSTFACT] tier 1 (plan.md: regular predicates such as a numeric range over a digit span LOWER INTO THE AUTOMATON) covers UC-1's octet case without C; the note does not cite [POSTFACT].
- proposed fix: gate stage 4 on a hand-built prototype (existing hybrid artifact of the erased pattern plus a hand `scan-end` wrapper, kit-style card) and a census of how many requirements/bench validation shapes pass rows 2-6; cite [POSTFACT]; until then list stage 4 as "designed, unscheduled" like `post`.

### COST-5  Goal 3b is not measurable as stated: no comparator that fails the same way, no margin, a regime that favours the claim
- status: CONFIRMED (text). Goal 3b: "on a veto-free subject, a `verify`-eligible artifact's search time is within the A/A floor of the same pattern's callout-free artifact plus one direct call per match (dev box)".
- severity: speed / doc
- effort: paragraph edit
- blast radius: stage 4's go/no-go
- where: inline_c goal 3b; standing question 1 (stage 4 clause); §9.1 stage 4 card
- argument, per the standing questions:
  1. Regime. Veto-free, warm, dev box (Zen 4) only; the note itself says the regime flips the decision (veto-heavy is slower than inline) yet the goal measures only the favourable end and has no veto-rate crossover stated, though stage 4's card lists "veto-heavy". The decision (default mode, user declaration) is unaffected by the numbers, so the card informs only the guide, not a gate.
  2. Control. "The same pattern's callout-free artifact" is a different engine: the stamp probe above shows the callout-free capture-free pattern is `RX_ENGINE "dfa"`, while a callout artifact is a VM hybrid by F7/§10a-4, whose scan is the prefilter's "forward+reverse DFA pair" (select_engine.c PFA_NOTE_NULLABLE_EXACT wording). Two scans versus one is a plausible 1.3-2x, not "within the A/A floor". Nothing says what the callout-free artifact's engine is allowed to be, nor whether the DFA-twin or `--engine=vm`-twin is the control.
  3. "A/A floor" has no pinned number in this note, and "plus one direct call per match" needs a hand-written control loop someone must author; the predicate's own cost, if non-trivial, swamps the overhead being measured (use an empty predicate).
  4. What moves on regeneration: nothing is pinned; a re-measure on a different box changes whether the goal holds. No consequence is stated for a miss. docs/dev/guide/architecture.md: "a measurement that misses a goal is a finding against the design"; the note should say stage 4 is cut or downgraded.
- proposed fix: rewrite 3b with (i) the twin named (DFA artifact AND `--engine=vm` artifact), (ii) an empty-predicate control, (iii) a margin and the A/A source (bench's floor, or the card's own repeat spread), (iv) the consequence of a miss.

### COST-6  Stage 2's per-fire card compares unlike programs and "decides nothing", so it cannot fail
- status: CONFIRMED (text). Standing question 1: "the per-fire cost of a call site against the same predicate hand-written in the caller after a plain search ... it confirms Frank's 'the only cost is the drop into vm' and nothing else is decided by it."
- severity: speed / doc
- effort: paragraph edit
- blast radius: none to the design (no decision rests on it); matters for what the card is for
- where: inline_c standing questions 1, §9.1 stage 2 ("Measurement card: per-fire cost")
- argument: the control (DFA plain search, then the predicate once, by hand) runs a different engine and a different number of calls than the site (VM, one call per fire, fires unspecified in count); the difference is the drop into the VM plus the per-fire cost, which is exactly what the card claims to separate. A card that isolates per-fire cost needs the VM-without-site twin (same pattern, `--engine=vm`, the segment replaced by a trivially passing one) and a counted fire number n (the DT-4.1 counting binding gives it). Also the direct call of a `static` function is inlined by gcc into the VM body: the card should record the VM's code-size and the non-site paths' time in a callout-bearing artifact (the user's code inlined can pessimise the VM's register allocation), which the hand-after-search control cannot show. With no threshold and "decides nothing", the card has no way to fail; a card that is built should be pre-registered with the margin at which Q2's "one call site, direct call" row (§1.4 row 1) would be reconsidered.
- proposed fix: replace the control with the `--engine=vm` twin plus counted fires; state the single decision it can move (e.g. keep row 1 as a direct call versus an indirect call through a table), or drop the card from stage 2 and attach it to stage 4 only.

### COST-7  Stage 3 is built ahead of any named need, and its SHA-256 collides with an existing pin spelling and an existing "pcrec checks neither" rule
- status: CONFIRMED. (a) rxt_format.md §1.6¶7-8 already spells a pin `sha256 <hex64>` (case-insensitive) and rules "**`pcrec` checks neither the hash nor the 64-digit syntax** ... both are the harness legs'"; `git grep -il sha256 -- src` finds only field names (internal.h, findings_dump.c, schema_dump.c), no hasher; the harness computes digests with `sha256sum`. The note's §5.3 introduces `sha256=<64 lowercase hex digits>` (a second spelling, lowercase-only) and §5.5 "a small in-tree FIPS 180-4 implementation under `src/core/`". (b) §9.1 itself says "stage 2 is safe alone" because ALL reached code is refused before stage 3.
- severity: maintenance / trust (a hasher in the compiler is the compiler's own security-relevant code; the §1.6¶8 principle is deliberately reversed)
- effort: paragraph edit (spelling) plus a ruling (need)
- blast radius: rxt_format.md §1.1 and §1.6¶8 and `--list-schema`; the TCB of the compiler; the harness's digest check (two legs would disagree on case)
- where: inline_c §5.3, §5.5, §8.2 stage 3 row, §9.1 stage 3
- argument: Q5 (Frank) rules the pinning design; it does not rule when to build it. Stage 3 serves a user who has a code-bearing `lib`/`include` file; none is cited in the requirements' use cases (UC-1, UC-3 are single local files). With stage 2 landed and refusing reached code, the safe default is already complete. D77 says wait and name the measurement (here, a named user or a requested lib). If stage 3 is kept, the spelling should reuse §1.6¶7's `sha256 <hex64>` shape (or the note must justify the second spelling) and §1.6¶8's "pcrec checks neither" must be edited in the same hunk (the note's §8.2 lists §1.1 and §1.13 only).
- proposed fix: mark stage 3 "designed, trigger: a first reached file that holds code" and have §5.3 cite §1.6¶7's spelling and case rule; add §1.6¶8 to the spec-hunk list.

### COST-8  No D153 "remodel overlap" statement; at least four in-flight rows touch the sites stages 1 and 4 edit; stage 4 spends a flag bit the note elsewhere protects
- status: CONFIRMED. `grep -nE "^[[:space:]]*- \[[^]]*\] STATE:started" docs/dev/plan.md` (INLINE-C row not read) lists: [COMPOUND] and [ENTRY-TABLE] (E1-prime next; entries, emit_compound.c, abi 77-80), [MATCH-SPLIT], [MEMFN] with [MEMFN-ROWCON] and [OPT-LITSCAN] (VM per-byte literal chain = [OPT-VMLIT]; D153's "memfn zero-mover migration steps, e.g. R4h M3 in-loop migrate"), [OPT-REVEND] (B3 match-end mark, abi 78; the `exact` end proof verify's row 6 reads), [REGIME], [ENG-TACTICS], [DD-11.5] (a new `A_CTX` node class through the same passes), [NULLABLE-ANCH], [VAR] (rx_ctx vars), [FINDALL-NEXT] (entries, `rx_info`), [UCP]/[UPROP-MORE] (registry).
- severity: maintenance
- effort: paragraph edit (an overlap table) plus sequencing in the build brief
- blast radius: stage ordering, the identity gate's re-pin windows (each stage has an abi event; the stage 1/2/4 stamps all move the `PCREC_RX_ABI_H` line of every artifact)
- where: inline_c §9 (no overlap column), §8.1 (abi events), §9.1 stage 4's axis
- argument: D153 sets the rule "a row touching a remodel site sequences behind it" and asks for a "remodel overlap column" on candidate lists. Stage 1 edits emit_vm.c's VM body and ~19 pass files (COST-1) and lifts a table out of emit_compound.c (COST-2): the [COMPOUND]/[ENTRY-TABLE] and kit-migration lanes are editing those same files. Stage 4 edits the hybrid search entry (the entries remodel) and consumes `RX_VM_RESEED "exact"` as [OPT-REVEND] is changing its forms. Separately: the axis `-fno-callout-verify` takes a `flags` bit (the existing axes are bits 50-56, plan.md records 57 as a pending candidate and a HARD [IFACE-PUSH] trigger at <= 4 free bits). §5.1 spends words keeping `--allow-code` off the word for exactly this reason, but stage 4's own deny flag is silent about the bit. Abi accounting: four events (1, 2, 4, 5); the three stamps are callout-only, and bundling stages 1 and 2 (and stage 5) into one landing would halve the re-pin churn at no loss of independence if they are briefed together.
- proposed fix: add a remodel-overlap table to §9 (stage by in-flight row, with "wait / ride / none"); state the flag-bit cost of stage 4's axis or use a valued/table switch instead of a bit; say which stages share an abi bump.

### COST-9  The gates have thin failing witnesses: goal 3a, goal 2's population, and stage 5 and the stage 3 scope
- status: SUSPECTED (what would confirm: read the build lane's S-IC list against §9.1 and count populations at stage close)
- severity: trust / maintenance
- effort: paragraph edit
- blast radius: goals 2 and 3a
- where: inline_c goal 3a, goal 2, §8.1, §9.1 sabotage lists, §9.1 stage 5
- argument: (3a) "zero byte movers other than the abi line" holds trivially for the existing corpus because no corpus pattern contains a site (§8.1: "every `(?C` is refused"). The gate has a way to fail only if the shared-pass refactor (COST-1) or the marked-set union changes non-callout output; no sabotage row witnesses that (S-IC2 removes a mark at a callout site; no row marks enclosing groups unconditionally and asserts the gate moves). (goal 2) "zero disagreements over the callouts corpus": the corpus is written by the stage's author and its case count is "declared in the report", not set in the note; K35 asks that the population be counted in the note or its gate. The shared item is the predicate text (acknowledged in §9.2), and the NO_AUTO_POSSESS|NO_START_OPTIMIZE flags remove only PCRE2's start and possessification optimizations; whether libpcre2 has any further answer-moving optimization with a callout in the pattern (e.g. its auto-callout paths, minimum-length checks) is not probed in the note, only P7 is. (stage 5) the wrapper is under "Q6 ... I doubt this would ever come up"; its cost is small (a macro, one abi rider, one sabotage), but D77 says unbuilt until needed; as a rider on stage 1 the cost is minimal, as its own landing it is not.
- proposed fix: add one sabotage row that makes the marked set unconditional and asserts the identity gate goes red; state a minimum corpus size and the optimization-sensitive shapes (P7-P10) in goal 2's measurable form; list stage 5 as ride-along or unscheduled.

### COST-10  Overlap with plan rows the note does not cite: [POSTFACT], [BREF-SPAN], [MATCH-EVENTS], and [M4-CALLOUTS]' own triggers
- status: CONFIRMED (grep). plan.md [POSTFACT] (filed 2026-10-13 Frank: lower regular predicates such as numeric ranges into the automaton; non-regular as inline assertions at their placement point, "callout semantics"); [BREF-SPAN] (a superset DFA plus a span-equality check, the same locate-then-check shape as verify); [MATCH-EVENTS] trigger text: "module `callouts` building (design both together so the binding surface ...)"; [M4-CALLOUTS] still describes a `pcre2_callout_block` extern as the step-2 ABI (the note's §10a-2 already recommends amending it).
- severity: design
- effort: paragraph edit
- blast radius: scope of stage 4 and the binding surface of stage 1
- where: inline_c §4.5/stage 6 (cites [MATCH-EVENTS] only as a later row), §9; plan.md rows above
- argument: [POSTFACT] answers UC-1 (the headline validator) for the regular tier with no C and no VM; the note's value for stage 4 over [POSTFACT] tier 1 is the non-regular predicates only, a smaller population that the cost ledger above has to justify (COST-4). [BREF-SPAN] and verify are two cases of "superset DFA plus verify, VM on failure", a third member for the "forest for trees" count (memory: propose unification at ~3 members); [MATCH-EVENTS]' own trigger asks that the binding surface be designed together with callouts, and the note decides `rx_callout_ref`/`user` for code segments (NULL, §3.5) without a line on events.
- proposed fix: add a "related rows" paragraph naming the three and stating what each decides for stage 4 and for the binding rows; the manager already owns the [M4-CALLOUTS] amendment.

## PROBED-AND-HELD

- Stage 1 position table (§1.9 rows 1-4 refuse by name) versus the registry: `(?C` is `GROUP_XA_CALLOUT`, `VM_ONLY`, module `callouts`; the three-row claim in §1.1 matches registry.c lines 281-286 and 1019-1026 (1 source read, as stated).
- Namespace row 2 `callout-bindings` "reserved with its first producer": compile.c lines 156-157 say exactly that (1 check, holds).
- `VE_CALLOUT` reserved with no producer, `--emit-ir` `callout-sites` empty: emit_vm.c lines 283, 9463-9466, 9684, 9958-9961 (4 sites, as stated).
- §8.1's "rx_ctx unchanged, rx_info no new member, pcrec_options one member, no flags bit" does not collide with [IFACE-PUSH]: the row says "a capability/optimization row that needs a new field or stamp adds it the usual way (D76 ritual), not a remodel" (1 row read; the one stage-4 axis bit is COST-8).
- The abi-event accounting in §8.1 (stage 3 not an event; the number "next at landing"; readers by grep including registry/codegen/rxtsource) matches D76/D94 and CLAUDE.md's situation index (2 sources).
- §4.4's soundness argument steps 1-5 (leftmost start, first fire, all-pass, veto, no match) hold for pure tail segments under the stated rows (checked as an argument, not run; the answer-side lenses own the deeper probes).
- Existing prefilter language statement: `RX_VM_RESEED` is a per-artifact stamp (match_api.md §6.3.5¶5-7, 3 reads); row 6's use of it on the erased pattern is consistent with §1.8's width-class erasure.
- Probes run: 3 callout-free pattern compiles (`^(\d{1,3})...$`, the capture-free twin, a `\b` form) for engine and stamps, plus 1 `--engine=vm` compile; results as quoted in COST-4.
- Overlap greps: 13 `STATE:started` rows listed in COST-8 against the touched-site list; D153 and D77 read in full (2 decisions).

## DONE
