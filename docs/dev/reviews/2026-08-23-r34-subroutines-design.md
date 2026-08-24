# R34 — adversarial panel on the [DD-14] subroutines design (2026-08-23)

Subject: `docs/design/subroutines_design.md` at lane/dd14design e5181e6
(2,159 lines, §0-§14) + `subroutines_measurements/`. Panel: C1 semantics vs
the oracle (opus), C2 mechanism vs the real emitter (opus), C3 charter
coverage / internal consistency / doc staleness (sonnet). Brief:
the manager's scratchpad `brief_r34_critic.md` (reproduced in spirit by the
lens descriptions below). Critics read-only, never ran `make`; every
contested claim measured on BOTH sides against libpcre2 10.46 via the
lane's own `sr_oracle.py` and against `prototype/callproto.c` rebuilt from
source. ROUND 1 STATUS: findings dispatched to the design lane 2026-08-23
~21:2x; dispositions below are the manager's triage, the FIXED column is
filled in from the lane's round-1 report.

## Triage

| id | sev | claim | disposition | fixed |
|---|---|---|---|---|
| LENS1-1 | HIGH | a call whose TARGET is inside a lookaround/atomic group is a missing construct family; emit-once-and-jump miscompiles three measured cells | ACCEPT — callee body is its own region; SPLICE-lexical + CALL-linkage mandatory for wrapped targets; §6.4 re-argued for nested groups | |
| LENS1-2 | HIGH | `minw` gloss "min over non-recursive branches" miscompiles under indirect recursion (`"xb"` witness) | ACCEPT — least fixpoint over the SCC-condensed call graph (= LENS2-6) | |
| LENS1-3 | MED | §5.5 cites `a\|ab` which cannot match "xyxy" | ACCEPT (= LENS2-10) | |
| LENS1-4 | MED | leading-zero absolute calls `(?01)`=group 1, `(?00)`=root — fourth missing family; naive `(?0)`-row wiring miscompiles | ACCEPT — rows, resolver rule for both doorways, ASK 3 note | |
| LENS1-5 | MED | depth capacity never converted to a user-facing subject size (1024 ≈ 2 KB vs PCRE2's 800 KB) | ACCEPT — §5.6/ASK 2 state default + implied sizes | |
| LENS1-6 | LOW | §3.4 silent on `\G` / non-zero start inside a callee (measured: composes) | ACCEPT — one row | |
| LENS2-1 | HIGH | restore set W is capture-slots-only; PENDING and CUT_MARK slots un-restored = lost match / five false matches (two-build prototypes) | ACCEPT — W = every slot the transitive body can write minus 0/1; cells + rows per family; re-price P-5 | |
| LENS2-2 | HIGH | `A_CALL.body` is a back edge; §4.4's naive descents hang the compiler on `(a(?1))` | ACCEPT — per-site decline vs descend-through-graph; visited-set row | |
| LENS2-3 | MED | `call_mark` missing from §5.1's listing; field/line counts disagree | ACCEPT | |
| LENS2-4 | MED | S-SR2's "one added line" is two; one changes no answer (masking) | ACCEPT — anchor call_top; codegen row for call_depth | |
| LENS2-5 | MED | "exactly two `goto *`" false both ways | ACCEPT — 1 + one per shared callee body | |
| LENS2-6 | MED | `minw` fixpoint not expressible as a bare arm; gloss undefined for `^(a(?1)?b)$` | ACCEPT (with LENS1-2) | |
| LENS2-7 | MED | run_state_init / reset_for_next_attempt missing from the ERR_FLOOR/run-state site list | ACCEPT | |
| LENS2-8 | MED | two wave numbering schemes, contradictory; A2's bar depends on E's gate | ACCEPT — one scheme | |
| LENS2-9 | MED | arm budget is 27 sites, not "ten files" | ACCEPT — 27-row site table | |
| LENS2-10 | MED | §5.5's MEASURED cite measured a different pattern | ACCEPT | |
| LENS2-11 | MED | S-SR9's budget backstop assumption vs frameless rungs (unmeasured) | ACCEPT — per-rung statement; possessive spelling in the detector | |
| LENS3-1 | HIGH | §0.2 + docs/design/CLAUDE.md invert the size result (CALL is smallest; SPLICE is faster) | ACCEPT | |
| LENS3-2 | MED | k=0 control silent on CALL's 708-vs-779 baseline | ACCEPT — explain or extend | |
| LENS3-3 | MED | P11/P13 internal.h citations drift +86 lines under D70 | MANAGER — re-verify at rebase onto post-D70 main | |
| LENS3-4 | MED | plan.md DD-11 row's walk-up phrasing contradicts the 2026-08-23 ruling | MANAGER — FIXED main 573eca7 | yes |
| LENS3-5 | LOW | §0.2's 45/4/0 omits the 1 excluded cell | ACCEPT | |

Convergences: LENS1-2 = LENS2-6 (two critics, two witnesses, one defect);
LENS1-3 = LENS2-10. Confirmed by re-measurement (not refuted): the four
load-bearing semantics measurements of §3, capture transparency (126 cells /
48 paired firings / 0 violations), §5.9's executed prototype (45/4/0/1 and
the BROKEN_ARRAY 47/3 reproduced by BOTH C1 and C2 from source), the eight
ERR_FLOOR sites, the ten-file census, six sabotage detectors, P-3's first
half (16 shapes, no counterexample), the DEFINE substitute (147 cells / 0).

## The reports (condensed by the manager from the critics' in-message deliveries)

### c1_report.md
# R34 C1 (lens 1: semantics vs the oracle, opus) — received 2026-08-23 ~21:2x
Instrument: libpcre2 10.46 via sr_oracle.py; callproto.c rebuilt in scratch (scratchpad/r34/lens1/).
LENS1-1 HIGH — MISSING CONSTRUCT FAMILY: a call whose TARGET is lexically inside a lookaround or atomic group. MEASURED 10.46: ^ab(?<=(ab))(?1)$ on "abab" → (0,4) g1=(0,2) (callee runs FORWARD, consuming, though its home is a lookbehind); ^(?!(z|zy))x(?1)c$ on "xzyc" → (0,4) (callee RETRIES into zy inside a negative-lookahead cut region); ^(?>(a|ab))z(?1)c$ on "azabc" → (0,5) (callee gives back a→ab though its home is atomic); also ^q(?>(a|ab))?z(?1)c$/"qzabc" (0,5), ^(?=(a|ab))..(?1)$/"abab" (0,4), ^((?=(b))|a)+(?2)$/"ab" (0,2); controls isolate the wrapper. Emit-once-and-jump miscompiles all three (back-step / cut). §6.4's k=1 argument covers the lookaround body as a whole, not a group NESTED in it (two use sites). FIX: §5.4 — a callee body is emitted as its OWN region (cut-free, back-step-free, forward) independent of its lexical wrapper; SPLICE-lexical/CALL-linkage becomes MANDATORY when the target is inside a lookaround/atomic; re-argue §6.4 for nested groups; cells to inlookaround.rxt; a sabotage row for the atomic-target cell.
LENS1-2 HIGH — §4.4's minw gloss "minimum over the non-recursive branches" MISCOMPILES under indirect recursion: ^(?(DEFINE)(?<g>(?&h)b)(?<h>x|(?&g)))(?&g)$ on "xb" → (0,2) on 10.46 (also "xbb".."xbbbb"); g has NO non-recursive branch → gloss gives ∞ → MRL prune → NOMATCH. True least fixpoint minw(h)=1, minw(g)=2. Control: ^(?(DEFINE)(?<g>a(?&g)b))(?&g)$ never matches (∞ right there). Converges with C2's LENS2-6. FIX: delete the gloss; init every group ∞, iterate the call graph to convergence; corpus cell "xb"; §12 has NO prediction covering minw/maxw — add one.
LENS1-3 MED — §5.5's cited a|ab pattern is NOMATCH on "xyxy" (= C2's LENS2-10); fix to x|xy.
LENS1-4 MED — FOURTH missing spelling family: leading-zero absolute calls. MEASURED: ^(a)(?01)$/"aa" (0,2); (?001), (?0001) compile; ^(a(?01)?b)$/"aabb" → (0,4) (= group 1) while ^(a(?00)?b)$ → nomatch (= root); \g<01>, \g<00>, \g<-01> same. Rule: parse the whole digit run as decimal, value 0 = root. Registry's (?0) row ("synonym for (?R)") makes the naive 0-doorway wiring a MISCOMPILE for (?01). FIX: §2.2 row, §8.1 fourth family (re-opens ASK 3 for the 0 doorway), state the resolver rule at §2.4 for BOTH doorways; corpus pair.
LENS1-5 MED — depth capacity never converted to a user-facing subject size: ^(a(?1)?b)$ needs nesting n; at the prototype's 1024 pcrec refuses at n≈1024 (2 KB subject) where PCRE2 does 800 KB in 0.4 s. Other direction NOT refuted: on runaways (^(a|(?1)a)$ on aⁿb) PCRE2's −52 costs 0.0002/0.012/0.30/35.9 s at n=100/1k/5k/50k; the prototype gives up in 0.00 s. FIX: §5.6/ASK 2 state the default and the implied subject sizes for both canonical shapes; P-3 carries the 2 KB-vs-800 KB pair.
LENS1-6 LOW — §3.4 never mentions \G / non-zero start; measured: (?(DEFINE)(?<g>\Ga))(?&g) on "xa" is (1,2) at start=1, nomatch at 0; \A/\z inside a callee refer to the subject. FIX: one row in §3.4.
COULD NOT REFUTE (all re-run): §3.1 H-RESTORE (callout-observed), inheritance, per-level/after-failed-call, CAPTURE TRANSPARENCY (126 cells/48 paired firings + 10 deterministic pairs, 0 violations; holds through a lookaround in the callee); §3.2 backtrackable + four atomic controls + the cost bisection (1.33/1.60/1.88/1.99); §3.3 in full (199 at offset 0; n+2 give-up); §3.4(b) \K (+ (a\K(?R)?b) on "aabb" → (2,4) g1=(0,4)); §3.4(c) (?J) across ALL FOUR call spellings (uniform — doc could say so); §3.4(d) lookbehind widths incl. ^(?(DEFINE)(?<g>a(?&g){0}b))ab(?<=(?&g))$ = ERR 125 on PCRE2 too; §2.1/2.3/2.4/2.6 all exact; mutual recursion needs no new rule; §2.5's substitute 147 cells / 0 disagreements; §5.9's run reproduced exactly (45/4/0/1; BROKEN_ARRAY 47/3); §12 P-3 attacked with 16 shapes — no counterexample; §8.3's exemption reasoning correct (note: no pair is recursive, so 21×–350× is non-recursive shapes only).
Own ledger: 6 (import path; three-not-four controls; stack-paired callouts across backtracking bodies = not evidence; a VACUOUS §2.5 row with a mistyped \3 caught only by a per-row match-count guard; an anchored lookbehind cell that could never match; the h-branch order that would have "confirmed" the gloss).

### c2_report.md
# R34 C2 (lens 2: mechanism vs the real emitter, opus) — received 2026-08-23 ~21:1x
Scratch: scratchpad/r34/lens2/ (pendproto.c+cmp.py, markproto.c+cmp2.py; two builds each differing in ONE #define, vs libpcre2 10.46 via sr_oracle.py).

LENS2-1 HIGH — §5.3's W is CAPTURE-slots-only; pcrec has five other activation-private slot families (vm_slot_name emit_vm.c:645-697: SLOT_EMPTY_GUARD, SLOT_SPAN_LOW, SLOT_CUT_MARK, SLOT_REVDET{ENTRY,LOW,HI}, SLOT_COUNTER, SLOT_GROUP<n>_PENDING), each written at a lexical construct's ENTRY and read at its EXIT; "re-initialised at its own entry label" (inherited from lookaround_design §6.4(2)) holds for sequential re-entry, NOT recursive re-entry. MEASURED: (a) PENDING (publish-at-close, emit_vm.c:722-755, A_CAP arm :4531-4566): ^(a(?1)?b)\1$ — W={2,3}: 11 agree / 2 DISAGREE (LOST MATCH on "aabbaabb", "aaabbbaaabbb"); W+PENDING: 13/0. (b) CUT_MARK (vm_atomic :4243-4285, RX_CUT :5783-5785, one mark slot per LEXICAL atomic group): ^((?>a(?1)?))a$ — W as written: 4 agree / 5 DISAGREE (FALSE MATCHES on "aa".."aaaaaaaa": level-2 cut overwrites MARK0, level-1 cut is a no-op → non-atomic language); W+mark: 9/0. (c) EMPTY_GUARD ARGUED (§2.6's own guard, :3908/:3923). (d) P-2's own candidates LOOK_MARK/_POS fail the same way for a recursive call inside a lookaround (ARGUED, M6.6.2 unlanded). Lane corpus has ZERO cells with a marked group spanning a call or an atomic group live at two depths. FIX: W(g) = every slot any node in g's transitive body can WRITE, minus slots 0/1 (general rule; keeps the \K exclusion); derive from callgraph.c SCC pass + vm_count_slots; both prototypes become tests/recursion/ cells; a sabotage row per slot family; re-derive §5.7's 2·|W| and re-price P-5.
LENS2-2 HIGH — A_CALL.body (const Ast*, SHARED) is the AST's first Ast*→Ast* back edge; §4.4 tells pcrec_minw (mrl.c:85), pcrec_has_atomic (atomic.c:37) and pcrec_has_bref (:295) — no context/memo/visited set anywhere (grep visited|cycle|acyclic: one unrelated hit) — to DESCEND into .body → (a(?1)), (a\g<1>?b), any (?R) = COMPILER stack overflow in predicates asked of EVERY pattern (atomic.c:264, select_engine.c). callgraph.c/SCCs already scheduled for two consumers. FIX: §4.4 states per row descend-THROUGH-THE-GRAPH (SCC-aware, memoised) vs decline; own sabotage row (drop the visited set → hang; no answer-comparison row can detect a dead process).
LENS2-3 MED — §5.1's RX_CALL listing omits `call_mark` (callproto.c has it); counts disagree: fail label "two lines" (§5.1) vs "one added line" (§5.9, §6.6, callproto comment); "two new fields" (§11) vs three (§5.1). FIX: add the line; settle three fields / two lines everywhere.
LENS2-4 MED — S-SR2 "delete the one added line" is two lines; deleting the call_depth line changes no answer → ambiguous anchor (replace.py refuses) or GREEN ON A BROKEN COMPILER. FIX: S-SR2 anchors the call_top line; call_depth gets a CODEGEN row (or dies with ASK 1).
LENS2-5 MED — §5.8/S-SR13/P-9 "exactly two goto *" false both ways: one shared RX_RETURN per callee body → N callees = N+1 (measured call-free = 1 holds); after wave G a spliced call-bearing artifact has 1. FIX: "one at the fail label + one per emitted SHARED CALLEE BODY", S-SR13 asserts the relation.
LENS2-6 MED — §4.4's minw rule "minimum over the non-recursive branches" is undefined for ^(a(?1)?b)$ (the headline aⁿbⁿ; recursion under ?, no alternation) and for ^(a(?1)b)$ (no non-recursive branch; compiles on 10.46, matches nothing — least solution ∞/empty); pcrec_minw's bare signature cannot express a fixpoint; mutual recursion = system. (Also pcrec_maxw does not exist — P13 — yet §11 B+C reads "minw/maxw's arms" as symmetric.) FIX: Kleene iteration from ∞ downward over the SCC-condensed call graph, memoised, empty-language explicit, through callgraph.c; one mechanism, three consumers (W, vm_nullable, minw).
LENS2-7 MED — all eight ERR_FLOOR sites resolve exactly (no D70 drift); MISSING: <prefix>_run_state_init (emit_vm.c:5833) and <prefix>_reset_for_next_attempt (:5848) must init/reset call_top=CALL_TOP_NONE and call_depth=0 (callproto sets the sentinel by hand in main()). FIX: add both to §5.6's list and wave B+C.
LENS2-8 MED — two wave numbering schemes (1/3 in §6.3, §8.2, §8.3, §9.2, S-SR17 vs A/A2/B+C/D/E/F/G in §11) contradicting: §8.1 says quant fix is "wave B", §11 says F; §8.2's "wave 1" = E; "wave 3" = G. And wave A2's landing bar needs the identity gate, a wave E deliverable. FIX: one scheme; move the gate into A2 or drop it from A2's bar.
LENS2-9 MED — §4.4's arm budget is 27 kind-switch sites (emit_vm.c 8, atomic.c 5, revdet.c 5, possessify.c 3, six ×1), not "ten files"; 14 default: arms; the four named -Wswitch-invisible sites verified. FIX: a 27-row site table with per-site decline / descend-through-graph / descend-lexically.
LENS2-10 MED — §5.5 cites "^(?(DEFINE)(?<g>a|ab))(?&g)(?&g)y$ on "xyxy" MEASURED (0,4)" — that pattern is NOMATCH; T3/probe_callproto.py use x|xy. callproto.c's header has the same stale a|ab. Conclusion unaffected. FIX: correct §5.5 and the header.
LENS2-11 MED (unmeasured) — S-SR9 predicts ERR_STEPS/_FRAMES for ^(?(DEFINE)(?<g>a?))(?&g)*$; steps count backtrack resumptions only (emit_vm.c:6039-6046: forward progress is FREE); frameless rungs (vm_poss_star charges RX_CHARGE_WORK; PCREC_WORK_BUDGET_NONE rides --fno-step-budget) may admit a zero-width possessified call with neither frame nor charge. FIX: §2.6 states per rung which budget bounds a nullable callee under * / *+ / {n,}; S-SR9 adds the possessive spelling; rung admission declines call-bearing bodies until §5.7 says otherwise.
COULD NOT REFUTE: §5.2's clobber + frame-as-call-record (re-ran probe_callproto.py from clean TMPDIR: 45/4/0/1 excluded; BROKEN_ARRAY 47/3 exactly as §5.9); §5.3's LIFO "saves cannot be rewound while live" (survives RX_CUT, :2063-2068); §5.1's rx_fail resume_label needs no frame-kind branch (zero-frame callee walked); RX_CUT inside a callee vs caller frames (once LENS2-1 is fixed); the eight ERR_FLOOR sites; §5.7/§5.8 citations; P-9's call-free half = 1 goto *; §4.4's ten-file census; six sabotage detector predictions oracle-checked (S-SR1/3/5/6/14 incl. err 143 without (?J)/15); §6.4's k=1 no-lookaround-body-as-call.
Own ledger: 4 (nearly filed §5.5 as a probe defect; hand-trace predicted resurrection, measurement showed a no-op cut; first pendproto had three groups; two-build discipline added after the first draft).

### c3_report.md
# R34 C3 (lens 3: charter coverage / consistency / staleness, sonnet) — received 2026-08-23 ~21:1x
LENS3-1 HIGH — §0.2 (and docs/design/CLAUDE.md's index entry) says "SPLICE smaller and faster at one site"; §6.2's table says CALL is SMALLER at every k (k=1: SPLICE 1001, HYBRID 1090, CALL 804); only TIME supports SPLICE (0.57 s vs 0.64 s). §6.4 has it right ("CALL is 197 bytes smaller and 10-12% slower"). FIX: rewrite §0.2's clause + CLAUDE.md entry.
LENS3-2 MED — §6.2's k=0 reachability control asserts SPLICE==HYBRID (779=779) but CALL's k=0 baseline is 708 (−71 B, 9%) and unexplained; confounds the ~80 B/site slope. FIX: explain or extend the control.
LENS3-3 MED — P11 (internal.h:1843-1904) and P13 (internal.h:2381) are exact at eacac76 but drift +86 lines under D70 (pcrec_minw decl 2381→2467 in lane/d70union); the charter's rebase note names only emit_vm.c. FIX: re-verify P11/P13 at rebase (manager).
LENS3-4 MED — plan.md's DD-11 GENERALIZED block still says "a construct searches up the tree for a rebinding" (walk-up), contradicting Frank's 2026-08-23 ruling (propagate/capture-at-build, never walk-up); §7 of the design is correct. FIX: annotate the plan.md row (manager).
LENS3-5 LOW — §0.2's 45/4/0 omits §5.9's "1 excluded" (50 cells). FIX: mention it.
VERIFIED: 26 registry rows carry module recursion (hand-counted: 1+1+1+1+9+1+1+9+1+1); ASK 3's 19-rows/17-deleted arithmetic; 17 sabotage rows; 10 instrument defects (+1 compiler-caught); 8 ERR_FLOOR sites all resolve; P11/P12/P13; syntax_dump.c:544-575 description; 1175/1175 figure; §7 honours the ruling; emit_vm.c citations still resolve under D70 so far.
Own ledger: 3 defects (GROUP macro token-pasting hid 24 rows from `grep M_recursion`; RX_TRAIL twice = traced/untraced pair; case-sensitive grep false zero).

### The lane's own delivery
# dd14design lane deliverable (received 2026-08-23 ~20:5x EDT)
Branch lane/dd14design at e5181e68803bacf7f4d299f87784d706dc383e90; 15 commits, 7,636 insertions, 26 files, all under docs/design/.
Sub-lane: ONE sonnet general-purpose subagent for probe_prefilter.py / probe_population.py; wrote build artifacts to /tmp/sr_pf (SCOPE DEVIATION, cleaned by the lane); lane spot-checked its 21x at 16.9x with its own driver.
Surprising MEASURED results: no compile-time left-recursion refusal in 10.46 (err 140 is a VERB-name error); "refuse recursion at an ancestor's position" is a MISCOMPILE (^(a|(?1)a)$ recurses 199 deep at offset 0 and matches); rc -52 give-up depth tracks subject (n+2), predicate unpinned; callee writes captures, return restores (callout-observed); \K NOT restored by return (^(a\Kb)(?1)$ on "abab" -> (3,4)); call vs backref resolve a duplicated name DIFFERENTLY (call = first declaration statically; \k = first SET member) so A_CALL must not reuse A_BREF refs[]; \g<0>/\g'0' = (?R), no registry row; missing row families (?10)+ (?-10)+ (?+2..9), quant column wrong on nine rows; (?R) re-runs anchors (target = AST root); (?(DEFINE) substitute ^(?!)(?<w>X)|^BODY$ exact 11/11; call BACKTRACKABLE on 10.46 (four atomic controls); linkage prototype splice ~300 B / hybrid ~80 / call ~80 per site, splice fastest+smallest at k=1; prefilter loss 21x-350x on call-bearing patterns; population 6 call spellings in 2,161 corpus lines; mechanism BUILT (prototype/callproto.c): 45 agree / 4 agreed-refused / 0 disagree; separate-array design wrong 3/50 incl. a false match; own bug found: W(g) must include g's own slots.
Ten instrument defects in the lane's ledger (§0.3, out/CLAUDE.md).
ASKs: 1 keep PCREC_ERR_RECURSE (rec KEEP); 2 RX_CALL_DEPTH default (rec (c) large, stamped); 3 registry row granularity (rec (b) collapse to (?N)/(?+N)/(?-N)); 4 DEFINE refusal hint (rec (c) compliance page); 5 single-oracle D27 corpus (rec PROCEED with SPLICE-vs-LINKAGE control as wave-G bar).
Unsettled: exact -52 predicate (needs PCRE2 source); 2.0x cost attribution (ARGUED); P-2 non-capture slots (awaits M6.6.2); wave G prefilter window-end hazard (landing bar); post-wave-F row count (depends on ASK 3).
