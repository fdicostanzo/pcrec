# R-45 reply draft: window spans of up to 4095 positions ([COVER-CAP] stage 2)

Status: DRAFT rev 9 for the kit manager (lane formsfixe, 2026-11-17; the design text beside the
cards' script fixes, `memfn/tests/span_forms/cards.py`; no timing). Rev 9 applies the re-check of
rev 8's fixes, review r37 (`docs/dev/reviews/2026-11-17-r37-memfn-forms3.md`, its RULED section:
H1 and H2 as ONE mechanism, the twin contrasts, plus H3, H4 and H7 in the rule's text and the
script; H9 and H10 as text; H5, H6 and H8 are lane formsfixf's checks, not this text's; read
"Changes in rev 9" first). Rev 8 (lane formsfixc) applied the code
re-check on the fixes, review r36 (`docs/dev/reviews/2026-11-17-r36-memfn-forms2.md`, its RULED
section: G2-G8 in the rule's text and the script, G12-G14 as text; its G3 as SUPERSEDED by the kit
manager's rulings entry R1, `docs/dev/lanes/formsfixc_rulings.md`; read "Changes in rev 8"
first). Rev 7 (lane formsfixa) applies the code
round on the build, review r35 (`docs/dev/reviews/2026-11-17-r35-memfn-forms.md`, its RULED section: F2-F11 fixed in the
rule's text and the script, F1, F19, F21, F25, F27, F28 as text; read "Changes in rev 7" first).
Rev 6 (lane r45f, 2026-11-16, design only; no code, no timing) applies the fix-induced re-check of rev 5, review r25
(`docs/dev/reviews/2026-11-16-r25-memfn-r45e.md`, its RULED section: R5-1..R5-6 fixed, R5-7
and R5-8 noted; read "Changes in rev 6" first). Rev 5 (lane r45e) applied main's check of rev 4 (`git show lane/r45read:docs/dev/lanes/r45read_report.md`,
contradictions C1-C11, questions Q1-Q5) through the kit's answers Q2-Q5 that main accepted, and
records the owner's three rulings and main's five answers as RULED (read "Changes in rev 5"
first). Plan A (forms now) is the plan of record. Rev 4 (lane r45d) applied the fix-induced re-check review r23 as ruled
(`docs/dev/reviews/2026-11-16-r23-memfn-r45c.md`, its RULED section; read "Changes in rev 4"
first). Rev 3 (lane r45c) applied the re-check review r22
(`docs/dev/reviews/2026-11-16-r22-memfn-r45b.md`) as ruled. Rev 2 (lane r45b) applied review r20 (`docs/dev/reviews/2026-11-16-r20-memfn-r45.md`) as
ruled. Rev 1 was lane r45's draft (commit 280082b45).

Tree read: main `ea83fbc01` (worktree `worktrees/r45`); rev 3 re-counts every list it touches
at origin/main `56c315567`, whose code under `src/`, `memfn/`, `lib/`, `tests/` and `cli/` is
byte-identical to `ea83fbc01` (r22 "Subject"), so the cites hold at both. Every `file:line` below
also names its symbol, because lines drift on other branches (r20 F17). The request
is `memfn/docs/requests.md` R-45. pcrec's side is `docs/design/cover_cap.md` §11 (rev 5.2),
reviews r13 (`docs/dev/reviews/2026-11-15-r13-covs2d.md`) and r15
(`docs/dev/reviews/2026-11-15-r15-covs2e.md`), and r9's EMITTED-2
(`docs/dev/reviews/2026-11-15-r9-covs1.md`). The kit's 2026-11-15 ideas entries (long exact spans
(1)-(4), the owner's direction verbatim, the EMITTED-2 fact) are on the kit branch
`lane/memfn-k1108` (`git show lane/memfn-k1108:memfn/docs/ideas.md`, from line 797), not on main.

**THE BUILD STARTS FROM MAIN** (r20 F17). The kit branch `lane/memfn-k1108` carries no code of its
own since its merge base 9798d196, and it lacks stage 1 (`cc_fits`, `cover_window`). The kit's
build branch is cut from main, and it merges only onto a pcrec branch that already has
cover_cap.md §11.1 A1 (r20 F18). A1 is delivered on `lane/covs2afix` ("MkEnd stops copying",
ff3fc028e), and that branch has zero `MF_MAX_SPAN_POS` readers in `src/` and `lib/`.

**Sizes** come from one probe built at this tree (gcc 15.2, x86-64, `-std=gnu11`). It includes
`memfn/src/window.c` and adds the rev 2 layouts as twin structs. It was re-run for rev 2:
`/var/tmp/pcrec-pcrec/scratch/memfn/r45b/sz2.c` (lane scratch). Rev 1's probes and the critics' probes
are in `docs/dev/reviews/2026-11-16-r20-memfn-r45/` (`sz.c`, `prop.c`).
- Today: `mf_class` 2,932 B, of which `proven` is 1,312 B (41 rows; `MF_PROOF_LO` -8,
  `MF_MAX_FWD` 33); `mf_result` 3,000 B; `mf_wspan` 1,164 B; `mf_wreply` 532 B;
  `mf_run_reply` 4 B.
- Rev 2: class 1,640 B, result 1,712 B, `mf_wspan` 32 B, `mf_wreply` 136 B, `mf_run_reply` 8 B.

## Changes in rev 9 (by r37 finding id)

Review r37 re-checked rev 8's fixes (`lane/memfn-forms` e7584a7fd). Its two rule defects (H1,
H2) were masked on today's night shape, as r36's were (every real night takes step (5) while the
kit's NOT-WARM and short-subject methods are approximations), and go live when the bench's
methods arrive. Both are noise SHAPES rev 8's drills did not generate, and they share ONE
remedy, the twin contrasts: I's pool already times, in every C1-C2 cell, separate arms that are
one binary. `cards.py selftest` is the drill record (89 checks; lane formsfixe's report,
"Validation"). H5, H6 and H8 are lane formsfixf's checks (G2, compound, CLI), not this text's.

| id | change | where |
|---|---|---|
| H1 | The floor gains the TWIN term: per (regime, layer), `σ_c` = the RMS of the log-median contrasts of the hash-equal arms (I's pools, about 31 degrees of freedom), raised to its 95 % bound; `f(r, l)` = max(the A/A floor, the launch term, `exp(z(α / N) x σ_c,up) - 1`). It carries between-run noise (an offset an arm holds over its 5 launches), which the launch term cannot see and the night-wide A/A term dilutes. Rev 8's "one A/A pair per (regime, layer) ... eight times the A/A arms" is WITHDRAWN (its premise was false). χ² quantiles are now exact. Drill (xx), 300 nights each: per-arm offsets τ 1/2/3 % in one regime (A/A spared): 0.000, 0.000, 0.000; in every regime: 0.000, 0.000, 0.000; in every regime, A/A spared: 0.003, 0.000, 0.000. Control: τ 2 % in one regime under rev 8's rule, 0.663 (r37: 0.26-0.29) | §3 "The floor `f`" (the twin term), drill (xx) |
| H2 | The AGREEMENT GATE: a C1-C2 cell whose I's-pool arms' medians disagree beyond the cell's floor is VOID, re-run once, never a pick; a pool of two (I, H(64)) voids on any such disagreement. Rev 8's "one arm's transient moves the pooled median by a fraction of a sigma" is struck (false for a pool of two). Drill (xviii) gains the whole-arm (5-of-5) shift in the SMALLEST pools: I and H(64) at `hex64`, `uuid36`, `alt49`, at `f`, 1.5 `f`, 2 `f` (`f` the cell's own floor, 4.4 %): 0.000 to 0.003 in all 18 cases (I and H(64) x three patterns x three sizes). Control: I at `hex64`, 1.5 `f`, rev 8's rule, 0.403 (r37: 0.34). The gate's added void rate on pure noise: none measurable (nights with a first void: 0.000 with the gate and without under normal launches, 0.030 with and without under t(5); r37 asked that it stay within F3's 5 %) | §3 "A split that moves a median", drill (xviii) |
| H3 | A missing `same_as_I.json`, or one lacking any C1-C2 pattern x layer, or a head list without 64, is REFUSED (the night DEFECTIVE), never read as I-alone pools | §3 "A split that moves a median" |
| H4 | `cards.py c3`'s deny check uses H(64), the arm an ignored deny renders, as its reach arm, rendered over C3 and C4 whatever h\* the step times; VACUOUS (red) where H(64) loops nowhere | night order 2b |
| H7 | The identity check counts the patterns whose FROZEN lever-h\* bytes differ from lever-64's, prints it, and refuses at zero when h\* < 64 (`a{40}` passed rev 8's file-level refusal) | §3 "The identity check" |
| H9 | The owner's 14:35 passage is quoted whole, from "2. stage 2 is fine." | §3 "The owner's words" |
| H10 | (1) The floor's thin pool takes the LARGER of its own and the night's sigma; the bimodal test borrows. (2) R4 reads `max(f(near-miss, l), f(near-miss, off))` (C5 is timed at `off` only). (3) C3's bimodal test reads step 1's pool sigma | §3 "Bimodal, defined", "The floor `f`" |
| (fix-induced) | Drill (xv)'s G2 control (rev 7's floor on a 3x regime) turned off only the launch term; rev 9's twin term also sees a noisier regime, so the control read 0.000 and was blind. It now turns the twin term and the gate off too: 0.177 (accept > 0.15) | drill (xv) |
| NAMED LIMIT | Re-measured under rev 9: a FAST 3-of-5 split in H(8)'s arm at 1.5 `f` ships 8 in 27 of 100 nights (27 under rev 8). Recorded, not gated, as RULED | §3 "A split that moves a median" |

## Changes in rev 8 (by r36 finding id)

Review r36 re-checked rev 7's fixes on the build (`lane/memfn-forms` 31f98f49b). Its rule
findings were masked on today's night shape (every real night takes step (5) while the kit's
NOT-WARM and short-subject methods are approximations), and they go live when the bench's methods
arrive. `cards.py selftest` is the drill record (56 checks; lane formsfixc's report, "Validation").
G1, G9-G11 and G13's grid assert are lane formsfixd's (G2 and the checks), not this text's.

| id | change | where |
|---|---|---|
| G2 | The floor is PER (regime, layer): `f(r, l)` = max(the A/A floor, `exp(z(α / N) x sqrt(2) x 0.5355 x σ_up(r, l)) - 1`), with σ(r, l) the pool's launch sigma (the bimodal test's own pool) raised to its 95 % bound. A cell's comparisons use its own pool's floor. Noise drill (300 nights each, every regime read): P(h\* != 64) = 0.000 with one regime 2x, 0.000 with one regime 3x, 0.000 with the A/A cells 0.7x the arms, and 0.000 with the regimes at 0.5/1/3/0.7/2/1x. Control: the same 3x night under rev 7's floor gives 0.173 | §3 "The floor `f`", R1, drill (xv) |
| G3 | SUPERSEDED by rulings R1 (the RULED "tie the gate to f" cannot be built: below). I's reading in a cell is the median over the launches of EVERY arm whose built artifact hash-equals I's there. This is measured per layer when the cells are built, never inferred from `h >= k`, and a cell without I's own row is refused loudly. GAP_K is kept. A 3-of-5 split of I's arm (one cell, slow) at f, 1.5f and 2f: P(h\* != 64) = 0.000 each, over 300 nights. Control: 0.397 with I's arm alone at 1.5f. Converse: the same split in H(8) ships 8 in 0 of 100 nights at f and at 2f | §3 "Bimodal, defined", R1 (1), drill (xviii) |
| G4 | Step (4): h\* is the largest kept head that is the top or itself beat I beyond `f` in some cell read. A kept head with no win never ships (the tolerance is not transitive). Drills (x) and (xi) take H(16) at 0.975 so they keep their R3-2 point. New drill (xix). (ix) and R3-1 re-run unchanged: h\* = 32, MEASURED, both. Synthetic: a 5 % one-cell win of H(8) alone picks {8: 157, 64: 43} of 200 nights, and no head without a win ships (r36: 16 or 24 in ~12 %) | R1 (4), "Why the dominance step", drills |
| G5 | The labels' top is the LARGEST R0-SURVIVING head, never the constant 64. A pick that measured no win is CHOSEN; drills (viii) and (xvii) now read "h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of ..." | R1 (4), drills (viii), (xvii) |
| G6 | R3 reads only a class whose text moves for some surviving head (`lit40` and `abc60` are never movers). DERIVED is reachable: with H(1) 30 % faster wherever it loops, the rule prints DERIVED | R3 |
| G7 | `cards.py c3` checks the deny on C3's and C4's artifacts before it times anything, with L (h0) as the reach arm. That is the step where an ignored deny loops | night order 2b |
| G8 | The identity check refuses an EMPTY predicted-movers file at h\* < 64, as it refuses a missing one. Under `--census-limit` a smoke exits 4 before the empty-census FAIL | §3 "The identity check" |
| G12 | `\w{32}\B` loops at h\* <= 29 (the stretch 0 .. 30). It is byte-equal to the deny only at h\* 30-32 | §3 "Named witnesses"; rev 7's F27 row |
| G13 | The other families' straddle draw is respelled to the shipped draw | §3 "Answers, controlled by G2" |
| G14 | (SIMULATE-4) The void test reads every arm of the cell, I's included; MIN_POOL gets its sentence. (SIMULATE-7) N is 600 with every regime read and 400 on a real night, not about 700; t(5)'s false-split rate is about 3 x 10^-5 per arm. (F1 nit) One number, about 3,300; the cap applies on every route. (F25 nit) Quote 1 is given in full. (FIXIND-3, FIXIND-6) Comments in `memfn.h`, `window.c` and cli/CLAUDE.md, not this text | §3; Plan B |

## Changes in rev 7 (by r35 finding id)

Review r35 was the CODE round on the build of plan A (`lane/memfn-forms` 7506bca30). Its rule
findings are defects of THIS text as much as of the script (the script implemented rev 6
faithfully), so rev 7 changes the rule here and `cards.py` the same way, and `cards.py selftest`
is the drill record (lane formsfixa's report, "Validation", has its output).

| id | change | where |
|---|---|---|
| F2 | RULED (the floor is sized to its comparison count; the mechanism is the lane's): `f` = max(the largest A/A ratio, exp(z(α / N) x σ_up) - 1), σ the A/A cells' RMS log ratio raised to its 95 % upper bound, N the head-against-I comparisons the rule makes, α = 0.05; a head whose emitted text equals I's in a cell reads I's median there. The noise drill (108 C1-C2 cells x 9 heads, 300 nights): P(h\* != 64) = 0.033 under normal launch noise and 0.027 under t(5), against 0.487 under rev 6's floor | §3 "The floor `f`", R1 (1), drills (xv)-(xvi) |
| F3 | "Bimodal" is defined: an arm's launches split into two groups of two or more with a gap of more than 4.5 launch sigmas between them, the sigma pooled per regime and layer (a median). The unimodal drill: 2.0 % of nights void a cell (t(5) launches); a bimodal arm (2 of 5 launches 8 % slow) voids in 48 of 50 | §3 "A cell missing a regime" |
| F4 | C3 is timed at the PICKED h\*, after step 2 and before the identity check (night step 2b); until it is, R2's C3 half and R5 are NOT COMPUTED | R2, R5, night order |
| F5 | A cell gate failure (any card, C3 included) is R0 for that head; I's or an A/A arm's makes the night DEFECTIVE. Step (5)'s head is the LARGEST R0-SURVIVING head (64 when it survives), or no form ships. A C3 void is never dropped | R0, R1 (5), R5, drills (viii), (xii'), (xvii) |
| F6 | Drill (viii)'s last case (every finite head fails R0) is run: no form ships | drills |
| F7 | The re-run is a step: a cell void once is re-timed (every arm), merged over the first reading, and R1 waits for it; a cell attempted once never reaches step (5) | §3 "A cell missing a regime" |
| F8 | The kit's approximations of NOT-WARM and `short-subject-search` are not those regimes: their cells are VOID BY METHOD until the bench's methods arrive | §3 "The regimes' methods" |
| F9 | The identity check's census is read from its source (the sweep's corpus through the cover facts), both encodings; FROZEN is required and must differ from the rebuilt build; at h\* < 64 the predicted-movers file is required | §3 "The identity check" |
| F10 | Labels: MEASURED names its card rows and cells read; DERIVED is defined (R3); the "slower" grid-top label takes a colon, as drill (v) | R1 (4), R3 |
| F11 | NOT-WARM is calibrated on calls; `cards.py plan` prints each step's expected wall time | §3 "The added cells' cost" |
| F1 | Plan B's cap citation corrected: the binding cap is `PCREC_MAX_VM_EMIT_CODE_BYTES` (500,000), and the deny is refused past about 3,300 wide positions [rev 8: one number, the spec's] | §3 "Plan B", C4 |
| F19 | The force spelling's form-hash instance is NOT built (no reader); trigger named | §3 "The option" |
| F21, F25 | The owner's three rulings of 2026-11-16 and the build's h = 64 interim, each with its in-tree record; the owner's 15:00 sentence in full; the near-miss slug's polarity spelled out | §3 "The owner's words", "Scope", §7 |
| F27 | ~~`\w{32}\B` does not move at h\* <= 32 in this build~~ [rev 8, r36 G12: it loops at h\* <= 29 (the stretch 0 .. 30); the E-find probe at offset 31 keeps the after side out of the run, so it is byte-equal to the deny only at h\* 30-32] (the predictor stays a superset) | §3 "Which sites move" |
| F28 | The loop's minimum of two entries is DERIVED (a one-entry loop is a lone test plus a loop's overhead) | §3 "The forms" |

## Changes in rev 6 (by r25 finding id)

Code facts are re-read at origin/main `ed9677782` (fetched 2026-11-16 by lane r45f): the
segmenter in `memfn/src/window.c` (`merge`, `c_run`, `find_groups`), the cover statement in
`src/gen/known.c` (`cover_window`), and the trace records in `src/gen/memfn_sites.c`. Every drill
was re-run by lane r45f's script against the rule as written here (lane report, "Drills").

| id | change | where |
|---|---|---|
| R5-1 | RULED: the mover predicate is stated in the SEGMENTER's terms. Its unit is an ALTERNATIVE's positions keyed by offset, each the MEET of every span that states that offset (`merge`), not one stated span. A one-class-repeat segment is a maximal run of consecutive offsets carrying one byte-identical multi-member set, ACROSS span boundaries and into the after side. The bound is the largest stated OFFSET (32 today, the cover's after side), not "32 positions". Witnesses: `\w{32}\B` (offsets 0..32 carry `\w`, so it moves at h\* <= 32) and its kin. Re-derived: at the default width, nothing moves at h\* = 64; at h\* = 32 only the cover kin move; at h\* <= 24 every alternative whose run reaches h\* is a possible mover. "h\* >= 32 moves nothing" is withdrawn | §3 "Which sites move", Goal 4, §8 |
| R5-2 | RULED: a void cell never helps another head. Step (5) is new: steps (1)-(4) run over the cells READ, a void cell removes no head (it gives each head whose text is I there its ratio 1, and every other head no term), and their pick is RECORDED; but if any C1-C2 cell is void twice, h\* = 64, labelled with the void cells. So a void can never lower h\*, and it can never move a competitor. Rev 5's reading lowered h\* from 32 to 24 on r25's drill V; a "skip the void cell" variant lowered it in 35 of 200,000 random cases; step (5) lowered it in none | §3 R1, "A cell missing a regime", drills, §8 |
| R5-3 | RULED: the regimes fallback's lever reader is listed. If a regime's method cannot run on the kit's harness, the BENCH times that regime's card cells through `build/pcrec-harness --harness=span-head=N` (test-only, never a shipped compile); it is then a lever reader, with the bench-only question for main to relay. "The bench is NOT a reader" now reads "of the width cells" | §3 "The regimes' methods", "Its readers", "The bench" |
| R5-4 | RULED: the identity check's population is EVERY predicted mover at h\* (cover or not, from the sweep's prediction), plus every card pattern and every census cover. It compiles at pcrec level, so non-cover sites are inside it | §3 "The identity check", §6 Q2 |
| R5-5 | RULED: the predictor's input record does not exist on main. It is a NEW pcrec-side record, `MFWSTMT` (main's build), its fields listed, beside `MFPRES` under `PCREC_MF_ROUTE_TRACE`, plus the predictor's change and a trace-build pass in the sweep. It is on main's list | §3 "Which sites move", night order edits, §7 |
| R5-6 | RULED: §8 says "dominated (faster beyond `f` in at least one cell and never slower beyond `f`)", the body's wording; §0 likewise | §0, §8 |
| R5-7, R5-8 | NOTED. Step (5) also settles R5-7 (a), the label when a void forces h\*, and (b), dominance reads no void cell. R5-7 (c), the A/A floor with a regime missing, stays as cover_cap.md §11.4 row 1 rules it for B's floor (the night is void); the kit's cards follow that row | §3 R1 |

## Changes in rev 5 (by main's question id Q and contradiction id C, r45read)

Main's check `r45read` asked Q1-Q5 and listed C1-C11. The kit answered Q2-Q5 and main ACCEPTED
the answers (2026-11-16); rev 5 writes them in. The owner's rulings (Frank, 2026-11-16, via main):
**forms-now-or-next** = FORMS NOW (one joint landing); **keep-short-spans** = NO;
**near-miss-fix-later** = NO. Main's five answers are YES each, and **night-order-edits** is YES
unconditionally. R1's selection steps (1)-(4) did not change (rev 5 adds its input regimes and
the twice-void reading only); rev 4's drill script was re-run and its output is byte-identical
(lane r45e's report).

| id | change | where |
|---|---|---|
| Q2 / C10 | The dominance-cycle clause is RULED by the kit manager (2026-11-16): step (3) keeps the members of E dominated by the FEWEST other members. One rule text, committed here; it is the text night order step 1 commits before the run. Every "awaits our ruling" is gone | §0, §3 R1, §8 |
| Q3 / C1 | The possible-mover population is restated in full: EVERY window site, cover or not, whose stated span has a stretch of one repeated multi-member set reaching an offset at or past h\* (pre-check run spans and reseed alternatives included), not covers only. Since every window span pcrec states today has 32 positions or fewer, nothing moves when h\* >= 32 [superseded in rev 6, R5-1: the unit is the alternative's positions keyed by offset, and `\w{32}\B` moves at h\* = 32]. The facts main's sweep reads to predict the movers, from pcrec's own statements, are named | §3 "The stability trade" (now "Which sites move") |
| Q3 / C8 | The uuid shapes (`k` = 36) have no cover today, so they are not a form mover. A uuid cover is a WIDTH event (cover_cap.md §11.2's rule), and it renders in H(h\*) from its first appearance | §3 "Which sites move" |
| Q4 / C6 | R1 reads the NOT-WARM and `short-subject-search` regimes: C1-C2 (and C3, C5) time every cell in cover_cap.md §11.4's five regimes plus uniform random bytes, with §11.4's methods. R1's worst cell ranges over them, so a loss the loop form causes moves h, never main's width default. The added cells and their cost are stated, and a cell missing a regime is handled as §11.4 handles it | §3 the cards, R1, "Why each choice", §6 Q1 |
| Q5 / C3 | "The procedure" and the old F12 and FREEZE NOTE rows now say what night order step 3 says: the cards run on the frozen lever binary, and the width cells run on the REBUILT binary, after the identity check | §3 "The procedure", change tables, §7 |
| C4 | §4 states that the forms are not a near-miss fix (an H(h) still restarts one byte later). cover_cap.md's sentence is main's to edit (r45read E7) | §4 |
| C5 | §7 forms-now (RULED) states the predicted outcome's consequence plainly: on a measured tie, the landing ships today's bytes at every span of 64 or fewer, and loops only past 64 | §7 |
| C7 | "The option" says why `no-span-loop` is not the dial's always-inline option: it is the deny every byte-moving kit row carries (D144 item 4, pcrec's G1 arm). The dial cell stays separate. cover_cap.md §11.3's sentence is main's to edit (r45read E14) | §3 "The option" |
| C11 | The §11.6.1 edit text names the rebuild at h\* (one kit constant) and the identity check as their own step between the cards and the width night. Whether that commit takes a code round is main's call, listed in §7 | §3 night order edits, §7 |
| C2, C9 | Main's (cover_cap.md B4 and B5/§11.6.3 edits, r45read E10, E11, E14). The reply's facts are unchanged: the kit names no 32/64 bound, and the proof witness is two rows. Nothing to change here | none |
| ruled | §7 and §8 record the owner's three rulings and main's five answers as RULED. "Scope" records plan A as the plan of record; plan B stays as the record of the alternative and of A's fallback | §0, §3 "Scope", §7, §8 |

## Changes in rev 4 (by r23 finding id)

| id | change | where |
|---|---|---|
| R3-1 | RULED: a DOMINANCE step runs before the largest-h tie-break. Inside E, an h is removed when another member is faster beyond `f` in at least one cell and slower beyond `f` in none; h\* is the largest survivor. The rule needs one more clause to be total, so the lane adds it for the kit manager to rule. "Beyond `f`" is a tolerance, so dominance can be cyclic: the drill script found three heads, each dominated by another, and then nothing survives. The clause: keep the members dominated by the FEWEST others. This is exactly the ruled step whenever an undominated member exists. In a cycle it keeps the cycle and drops the heads that every member beats. Every drill (i)-(viii), the H(8)/H(32) drill, R3-2's drills and the cycle (ix) were re-run by a script against the rule as written (lane report, "Drills") | §3 R1, "Why each choice", drills |
| R3-2 | RULED: the false claim is replaced. A value that is not the minimum cannot move the threshold, so it cannot move any other value in or out of E. The threshold's dependence on the best value is inherent to "within `f` of the best", and it is accepted. A value that joins E can still move h\*, as the largest member or through the dominance step. Drills (x) and (xi) show each case | §3 "Why each choice", drills |
| R3-3 | RULED: when h\* is the grid top, it is labelled "h = grid top (64, CHOSEN), on a measured tie of every finite head" (or of the members of E, or "every shorter finite head measured slower"). The length where loops begin is then the grid's choice, checked only by R5. A loss filed by R5 against I or L is the TRIGGER that extends the grid past 64. Goal 3 and the drill summary say so | Goals, §3 the grid, R1, R5, drills, §8 |
| R3-4 | RULED: one wording everywhere: "cards cannot run" is decided by main, with Frank | §3 "Scope", §7, §8 |
| R3-5 | RULED: witness row (b) uses `[0-9a-f]{32}` with nothing after it. That is a cover at width 32: k = 32 meets stage 1's `k <= 32` (and `k <= W` at the default 32), and the main tree's `build/pcrec` emits `RX_DFA_SCAN "cover"` for it, while `{33}` and `{40}` emit no cover. The REACH line asserts the cover as well as the unstated after side | §1 row (b) |
| R3-6 | The head lever's readers gain the G7 fence's `ALLOW` regex (`tests/compound/run_lever_fence.sh`) wherever `--harness=span-head=` is spelled under a fenced directory. The bench is no longer a reader: B's width cells run on the REBUILT binary with h\* compiled in, AFTER the identity check passes, so the bench needs no harness option and no change | §3 "The head lever", night order, cover_cap edits |
| R3-7 | L and H render at EVERY window span, cover or not (§1's general carrier). The non-cover G2 families (reseed, pre-check, run) gain draws that straddle every finite grid h from 16 to 64, and G2-win's COUNTED line counts per FAMILY and per h | §3 "Answers, controlled by G2", §6 |
| R3-8 | NOTED, no ruling needed. Only (b) is applied: §8 now says an over-read below 4096 reaches B5. Items (a), (c), (d) and (e) are recorded in review r23 for the build | §8 |

## Changes in rev 3 (by r22 finding id)

| id | change | where |
|---|---|---|
| F1 | The kit's THIRD refusal is declared: the range self-check (`end` reaches one past the statement), on the ask path (a bare -1) and the define path (the named message), marked a self-check sharing its source with `end`. Witness row (a) reads the message through `mf_define`; row (b) names an after-UNSTATED cover and a REACH that holds the side unstated | §1 "The kit's refusals", "The short-range internal error" |
| F2 | RULED (i), the kit's proposal for main to confirm: the COVER ask passes proof storage up to the ceiling `MF_MAX_FWD` (4,104 rows), so every over-read lands where B5 reads it and B5 stays the independent control. The rev 2 sentence "lands inside the range" is corrected: at `mf_rows_need`'s minimum an over-read past the first following offset is a bare refusal, which is why the cover ask does not use the minimum | §1, §5 "Where the rows live", §7 |
| F3 | The range and its refusals are scoped to the offsets that CONTRIBUTE to a proof: window plan classes and old-field FIND terms. VERIFY, EXPR and other non-proving classes carry `proof_n` 0 (no rows, no refusal), so the 5000-byte VM run compare renders as today. `MF_MAX_FWD`'s derivation is re-worded to that scope. Old-field FIND keeps today's clip, stated as conservative | §1 table, "The proof range" |
| F4 | The define sizes its rows by the same rule (`proof_n` rows exactly) and refuses exactly where an ask given enough storage refuses; ask and define AGREE whenever the ask's storage holds `proof_n`. The kit's five internal producers are listed. The define's rows are added to the arena price | §5 "Where the rows live", "Stack and arena", §7 |
| F5 | `formhash.c`'s `fh_work.sp` is a listed kit-internal `mf_wspan` writer. `last_s` is the largest stated POSITION (a RUN term's `offset + run_len - 1`). `proof_n` 0 with `proof` NULL is the legal all-ones class (PRESENCE ask, NONE form, non-FIND class, the zeroed refusal) | §1 "Definitions", §5 (c), (e) |
| F6 | §5 (a) gains `d27_frame.c:1075, :1084, :1124, :1178`; the count is 22. G2's held reply copies (`g2_win_gen.c:1145, :1290`) are listed as holders sized by `G2W_NOFF`. Test reply rows come from the test's own storage, never the art's arena (`d27_frame.c:1094`) | §5 (a), (e), §8 |
| F7 | The census probe `docs/design/memfn/span_pick/probe/probe.c:101` is a listed caller (`run_link_checks.sh` compiles it `-Werror`). Only S3097 embeds a call in plant text; S3045 and S3064 need a REACH re-read only | §5 "pcrec's side" |
| F8 | G2's length DRAWS are the movers, not the twins: the REPORT family's draw (`g2_win_gen.c:433`) first, each draw site with its stated reach; a repeated-class shape straddles every finite grid h; G2-win prints a COUNTED line per grid h that fails at zero. `G2W_MAXPOS` becomes 128 (twice the largest finite h, which rev 2 mis-stated), and `G2W_NOFF`'s holders are listed | §3 "Answers, controlled by G2", §6 |
| F9 | RULED: the DEFAULT candidates are the FINITE h only. All-inline (`h >= k`) is TIMED as the dial's reference; any cell where it beats H(h\*) is dial evidence. All-inline can never become the default by this rule | §3 the rule (R1, R2), Goal 3 |
| F10 | RULED: ties break toward the LARGEST finite h among equals (the owner's prediction; the fewest movers; a tie buys no byte move). Every drill is re-run against the rule as written; (i) and (iv) corrected | §3 drills |
| F11 | R1 is deterministic: the equal set E = { h : W(h) <= (1 + floor) x min W }, non-chaining, over raw medians; W normalised against the always-timed I arm; the floor is the cards' own A/A floor; R1 reads C1-C2 only, C3 feeds R2. Drill (ii) rewritten. §4's trigger joins the table as R4 | §3 |
| F12 | RULED: a TEST-ONLY lever sets h on one binary (`mf_lever(art, "span-head=N")`, reached through pcrec's harness binary), its readers listed; an identity check (the lever at h\* is byte-equal to the shipped build at h\*) | §3 "The head lever" |
| F13 | A list of cover_cap.md edits for main (§11.4, §11.6.1, §11.6.4), conditioned on plan A; R1 and the night order apply under plan A only; `[0-9a-f]{64}` joins C2; which harness times the cards is stated | §3 "What a card needs", §7 |
| F14 | RULED: plan A's fallback, its costs (extra nights, a later and larger landing) and WHO decides "the cards cannot run" (main, with the owner; rev 4 restores the ruled "main, with Frank", R3-4) go inside the plan A question, in plain words, cross-referencing cover_cap.md §11.6.1 | §3 "Scope", §7, §8 |
| F15 | The kit's FORCE reader is named (a three-state option read; both spellings given: the deny wins, as tuning.md §2.43¶1); the unlisted readers are listed (registry.md §6¶7 and ¶8a's table, the CI shard tables, `cloud_units_plan.py`, `formhash.c`); the spec hunk's homes are named | §3 "The option" |
| F16 | (a) FIX: literal stretches render as one run compare in EVERY form and the head never splits one, so `lit-l31` is not a mover; the mover list is re-derived. (b) DOC: each owner question carries a bold plain-word slug. (c) DOC: plan A/B framed as "same end state, different interim default and cost" | §3 "The forms", stability trade, §7 |
| F17 | DOC: `mf_rows` named as the third member of the caller-owned output-list family, with the general form and its unlocks (each with a trigger) | §5 "Where the rows live" |
| F18 | DOC: `cover_window` is `known.c:583`; `:613-628` is `pcrec_cover_site`, which calls it | §1 |
| FREEZE NOTE | The night order (cards first on the frozen binary, h frozen by its rule, then the width cells; agreed with main 2026-11-16) is recorded here and in §8. [rev 4 R3-6, rev 5 Q5: the width cells run on the binary REBUILT with h\* compiled in, after the identity check; not on the cards' binary] | §3 "What a card needs", §8 |

## Changes from rev 1 (by r20 finding id)

| id | change | where |
|---|---|---|
| F1 | The proof range always reaches offset `k`. Its end is one past the statement, so it does not depend on whether the after side is stated | §1 "The proof range" |
| F2 | The range is sized from the larger of the stated and the TESTED offsets. A tested offset outside it is a kit refusal and is never clipped. "By construction" is restated as a kit promise that B5 checks | §1 |
| F3 | Rows get a real home: CALLER-SUPPLIED storage, `mf_rows`, a new parameter of `mf_ask` and `mf_wdecide`. Its size comes from a pure kit function of the statement, and the asks stay pure. Checked against seam principle 9 | §5 "Where the rows live" |
| F4 | One deep-compare rule. Every byte-for-byte and `offsetof` compare and every loop bounded by the old constants is listed with `file:line`. A NONE ask leaves `plan_test` NULL | §5 "Readers" (a), (b) |
| F5 | Every `proven[]` reader and every plant whose text moves is listed | §5 "Readers" (c), (d) |
| F6 | A host-storage rule for `mf_wspan` writers, and all 14 silently truncating `(uint8_t)` casts in pcrec and the kit (plus the test casts) | §5 "Readers" (e), (f) |
| F7 | S526 stays on `MF_MAX_TERM`. B2's control is cover_cap.md §11.6.3's reference compile. A kit-side 4094 plant is a NEW row, after B2 | §2 |
| F8 | Two witness rows: a kit row expects the kit's refusal by its message; a pcrec row bypasses that refusal and expects B5's text | §1, §6 |
| F9 | G2's twins (`G2W_MAXPOS`, `G2W_REACH`, `G2P_MAXRUN`) are movers, each tied to a kit name. The long cases get their own generator rows, and G2's runtime is priced | §3 "Answers", §6 |
| F10 | The PAIR row's readers are named. The force spelling selects L. A force cell is added to the answer-identity sweep | §3 "The option" |
| F11 | A combining rule replaces first-match. The default is H(h*). h* is picked by a declared tie-break over a grid that includes 0 and `>= k`. A cell where I wins is dial evidence. "Zero movers at 32" becomes a stability trade offered to the owner in plain words | §3, Goals, Q2 |
| F12 | h is a KIT constant, independent of pcrec's width default. The cards run first and set h first. SETTLED with main (ruling R1). [rev 5, Q5/C3: rev 1's "on the same frozen binary as §11.4's width cells" is superseded: the width cells run on the binary REBUILT with h\* compiled in, after the identity check (night order step 3)] | §3 "What a card needs", §7 answered |
| F13 | Plans A and B go to the owner in plain words. The kit recommends A, and B's lower cost is stated | §3 "Scope", open questions |
| F14 | L/H are defined over the EXISTING segmenter, so C-run stretches stay run compares and lit-l40 stays one compare. The PLAN row (shared segmenter) is stated | §3 "The forms", §7 |
| F15 | The near-miss skip follows D77 strictly: it is not in the first build. Its trigger is C1's near-miss column, and its form is D-hors generalised to every k | §4, open questions |
| F16 | Every constant is labelled. The "about 32" attribution to the owner is removed | throughout |
| F17 | The build starts from main, cites carry symbols, and the old Q4 is answered (retire now). The mfind caveat and the doc readers are listed | header, §1, §5 |
| F18 | The fallback ("keep `MF_MAX_SPAN_POS` 32") is withdrawn: the kit branch merges only onto A1 | header, §1 |
| F19 | DOC: about 12 `mf_wreply` stack holders, not 3. Arena rows count per compile, summed over the size-ladder attempts | §5 "Stack and arena" |
| F20 | DOC: 528 tests per 32 bytes (16.5 per byte), counting the failing test | §4 |

## Goals

In priority order; a conflict goes to the higher one.
1. **A cover of up to 4095 positions passes the seam.** pcrec's three conjuncts and its
   `_Static_assert` hold at `k` = 4095. Who benefits: pcrec's stage 2.
   Measurable: `cc_fits` is true at 4095 on the combined branch.
2. **No holder of a seam struct grows, and no check goes blind.** pcrec's stack holders stay at
   or below today's 23,456 B for 8 classes. No kit frame goes over 4 KB. No over-read is
   clipped out of B5's view. Who benefits: every compile, and B5.
   Measurable: `sizeof`; `run_link_checks.sh`; the two witness rows of §1 read DETECTED.
3. **The default long-span form is the one the owner asked for: loops, after an inline head
   that is MEASURED** [rev 2, F11; rev 3, F9; rev 4, R3-3]. Who benefits: users of long covers;
   the owner's dial. Measurable: every shipped `h` is a FINITE grid value with its card,
   labelled MEASURED or DERIVED if it is below the grid's top. If it IS the top, it is labelled
   "h = grid top (64, CHOSEN)" with the measured tie (or loss) that put it there. In that case
   the length where loops begin is the grid's choice, checked only by R5, and R5's loss is the
   trigger that extends the grid. All-inline is never the default by the rule (only the owner
   can make it so).
4. **Every byte the landing moves is either measured or offered to the owner as a choice.**
   [rev 2, F11: replaces rev 1's "zero movers at 32"]. Who benefits: users wanting stability.
   Measurable: the stage-2 sweep's mover list equals the list the owner accepted. [rev 5: the
   owner ruled one measured rule at every length (keep-short-spans = NO); the sweep's list is
   then every moved site inside the possible-mover predicate of §3 "Which sites move", and a
   moved site outside it is red. Rev 6, R5-1: the predicate is stated in the segmenter's
   terms, over each alternative's positions keyed by offset.]

Non-goals: no near-miss form in the first build (§4; D77); no periodic segment (§3); no timing in
this lane.

## 0. The answer in one paragraph

Yes. The kit carries spans of up to 4095 positions on EVERY window span, through one general
carrier with no per-site-kind bound.
- **Statement arrays** move out of the statement's struct into storage the host owns.
- **The reply's lists** (the proof rows and the plan) are COUNTED lists written into storage
  the CALLER supplies. A pure kit function sizes that storage from the statement, so the asks
  stay pure and the seam stays a document.
- **The proof range** reaches one past the statement, and also every offset the text tests. A
  text that tests past the caller's storage is refused, never clipped. The cover ask passes
  storage up to the ceiling, so every over-read of a cover lands where pcrec's B5 reads it
  [rev 3, F2]. Classes that prove nothing carry no rows [rev 3, F3].
- **The kit's working state** is sized by each site's extent, never by the ceiling.
- **`MF_MAX_TERM` and `MF_WMAX_SPAN`** stay 32 and are DECOUPLED from span length.
- **Sizes.** Every class and statement a host holds gets SMALLER: `mf_class` 2,932 B -> 1,640 B,
  `mf_wspan` 1,164 B -> 32 B.
- **abi.** This is one `MF_SITE_ABI` event (29 -> 30) carrying `MF_CLASS_V` 10 -> 11 and the
  asks' new parameter, inside the one joint pcrec `abi` event.
- **The three forms** (all inline, all loops, inline head then loops) sit over the kit's
  existing segmenter. Under the owner's direction the default is the head-then-loops form,
  with its head MEASURED by cards and chosen among FINITE heads only. A head that another head
  beats in some cell and never loses to is dropped, and ties among the rest go to the longest
  head. On a tie the head is the grid's top, 64, a CHOSEN value [rev 3, F9, F10; rev 4, R3-1,
  R3-3]. A cell with no reading never helps a head: if any is void twice, the head is 64
  [rev 6, R5-2] (the largest head that passed R0, 64 whenever it passed [rev 7, r35 F5]). The forms ride the joint landing: plan A, RULED by the owner (forms now, 2026-11-16)
  [rev 5] (§3 "Scope").
- **Readiness [rev 5].** Plan B's part (the carrier, the kit's per-extent working state, the
  two witness rows) was READY with rev 3's text fixes (review r22), and review r23 confirmed
  it. Plan A's rule is complete: r23's text fixes are applied (rev 4), and the dominance-cycle
  clause (keep the heads dominated (faster beyond `f` in at least one cell and never slower
  beyond `f`) by the fewest others) is RULED by the kit manager [rev 5, Q2; rev 6, R5-6].
  Rev 6 applies r25's text fixes (the mover predicate in the segmenter's terms, the void step).
  Nothing in the reply is open; §7 lists the rulings.
- **Dense near misses** (§4) are a complexity-class question: O(n·k) against the engine's O(n).
  Their fix is not built until a card shows the loss.

## 1. ASK (1): can the statement and the reply carry 4095? The three bounds

**Answer: yes. The kit declares the three bounds below. Each applies to EVERY window span,
not only to a REPORT site's span 0. The proof range is a per-reply count under a build-time
ceiling.**

| bound | name | value | kind | applies to |
|---|---|---|---|---|
| positions per span | `MF_WSPAN_POS` | 4095 | SHAPE BOUND, CHOSEN: the widest span pcrec states (the cover's `k`, its anchored ceiling less one). TRIGGER: a statement past it, refused naming `len` | every window span |
| reach | `MF_WREACH` | `MF_WSPAN_POS + 1` = 4096 | SHAPE BOUND, DERIVED: the longest span plus its after-context position, the widest statement pcrec makes. TRIGGER as today: a statement past it, refused naming `start` | every window span |
| proof range forward (ceiling) | `MF_MAX_FWD` | `MF_WREACH` = 4096 | SHAPE BOUND, DERIVED: every offset a WINDOW statement may state lies below it, so every offset a window plan class proves does too [rev 3, F3: scoped; an old-field VERIFY run may state 5000 bytes today, and it proves nothing] | every PROVING reply |
| proof range (per reply) | `mf_class.proof_n` | for a PROVING class: `end - MF_PROOF_LO`, where `end = max(last_s + 2, last_t + 1)`, clipped at `MF_MAX_FWD` [rev 2, F1, F2]; for every other class 0 [rev 3, F3, F5] | a COUNT per reply; the terms are defined under "The proof range" below | every reply |

What this means for pcrec's three conjuncts and its seam assertion:
- At `k` = 4095, `cc_fits` (`src/gen/known.c:336`) holds: `4095 <= 4095`, `4096 <= 4096`,
  `4095 < 4096`.
- B2's `_Static_assert` reads the three names above, so a `-D` raise of the ceiling fails the
  build. That is cover_cap.md §11.1 B2 as written. B2 is pcrec's code: it exists in no tree yet
  (r20 F7).

**Why every span, not REPORT-only (the general form; memory
`pcrec-general-mechanisms-not-special-cases`).**
- The 32 and 64 are not facts about non-cover sites. They are the CARRIER's sizes (`memfn.h:650-667`),
  DERIVED from pcrec's own truncation bound `PCREC_MAX_REQ_RUN_SCAN`. Once the carrier holds
  4095, a second, smaller name for "other sites" would be a parallel bound with no measured or
  derived source.
- The bound pcrec actually relies on for its own non-cover sites comes from pcrec's own
  construction. pcrec already asserts it against its own constants:
  `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS, ...)` (`emit_dfa.c:1446`, above
  `req_pres_spans`; still true at 4095). Its prefix walk is bounded by `PCREC_PREFIX_K_MAX`
  (24).
- So r15 FIND-11's worry ("every non-cover site's bound silently becomes 4095") is the intended
  reading. `window_bounds_check` (`src/gen/memfn_sites.c:590-600`) asks whether a statement
  fits the KIT, and every statement up to 4095 now does. B4 needs no site kind.
- Whether pcrec should keep its non-cover sites at 32 as its own invariant is an open question
  to main (§7).

**What the kit owes on its side, for a general carrier (K96: each row checks its own
contract).** Some kit paths keep a 32-shaped limit internally. Each one becomes a ROW CONTRACT
that declines, or a site refusal that names the field. None of them is a seam bound.
- **E-func and E-stmt** translate the plan into an old-field site, and `legacy_ok` already
  declines more than `MF_MAX_TERM` compares (`window.c:1463`).
  - `wf_legacy`'s run and mask buffers are sized `[MF_MAX_TERM][MF_WSPAN_POS]`
    (`window.c:1440-1441`). At 4095 they would be 262,080 B per prepare. They get their own
    bound `WF_LEGACY_POS` = 32 [rev 2, F16], DERIVED: today's `MF_WSPAN_POS`, which is the
    tested range of the old-field rows the plan translates into. `legacy_ok` declines a run
    longer than it.
  - The translated ranking stays under `MF_RANK_MAX` 32 (`memfn.h:286`). A longer R declines
    the legacy rows and reaches E-find or the floor.
- **The pre-check's run part.** `mf_run_reply`'s four fields widen to `uint16_t`.
  - All four widen [rev 2], `has_scan` included, so the struct has no padding byte for
    `emit_dfa.c:1665`'s by-value `memcmp` of `cls.run` to read (r20 PREMISE-2 aside). The
    struct is 8 B by the probe.
  - `run_part_terms` allocates by the run's length rather than `2 * MF_WSPAN_POS`
    (`window.c:3013`).
  - The writers that cast are §5 (f).
- **D-hors's shift table** is `uint8_t`, held by
  `_Static_assert(MF_MAX_SPAN_POS < 256, ...)` (`window.c:1850`, above `hors_table`). The
  shift becomes `uint16_t`: a 512 B table, built once per plan.
- **C-run's grouping** caps groups at `MF_MAX_TERM` (`window.c:1786`, `find_groups`; `int8_t grp`,
  `window.c:1354`). Past the cap, positions stay lone tests, which is correct and silent. §3
  re-reads this grouping as the general segmenter the forms use.

**The proof range [rev 2: F1, F2; rev 3: F1, F2, F3, F5].**
- **Which classes have one [rev 3, F3].** Only a PROVING class carries rows: a window plan class
  (`wf_plan_class`) and an old-field FIND class (`kit_class` proves only `MF_OP_FIND`,
  `compose.c:397-404`). Every other class (VERIFY, EXPR, a PRESENCE ask, a NONE-form class) has
  `proof_n` 0 and `proof` NULL, which by "outside the range = all ones" is the legal all-ones
  class; `proven0`/`proven_prev` are then the all-ones copies, read by value as today
  (`cand_class_eq`, `emit_dfa.c:7128-7129`). So the VM's 5000-byte run compare
  (`(x)\1(ab){2500}`'s VERIFY site, DELEG_VMRUN; `mf_term.run_len` has no cap) renders as today,
  asks for no rows, and meets no refusal.
- **Definitions.**
  - `last_s` is the largest POSITION the site STATES, in any span, after-context included. For
    an old-field site it is its terms' largest stated position: a RUN term at `offset` states
    `offset .. offset + run_len - 1` (`term_prove` walks `offset + j`, `compose.c:378-379`), so
    its contribution is `offset + run_len - 1` [rev 3, F5 (3)].
  - `last_t` is the largest offset the committed text TESTS: the plan's offsets, the offsets
    `wf_plan_class` loops over (`window.c:3840-3858`).
  - The range is `[MF_PROOF_LO, end)`, with `end = max(last_s + 2, last_t + 1)` clipped at
    `MF_MAX_FWD`.
- **It always reaches offset `k` (F1).** pcrec states the after-context span only when that
  side constrains (`cover_side_stated`, `known.c:563-569`; `cover_window`, `known.c:583`, called
  from `pcrec_cover_site`, `known.c:613-628` [rev 3, F18]).
  - After side unstated: `last_s = k - 1`, so `end >= k + 1`.
  - After side stated: `last_s = k`, so `end >= k + 2`, clipped to 4096 at `k` = 4095.
  - The rule is one past the STATEMENT, whatever the statement holds. It has no REPORT-site
    clause, and pcrec need not state an empty after span.
- **A tested offset is never clipped (F2).** The rows are computed from what the text TESTS, and
  the range is sized to hold them. Whether an over-read is SEEN by B5 depends on the caller's
  storage [rev 3, F2, corrected]:
  - at `mf_rows_need`'s minimum (storage ending at `min(MF_MAX_FWD, last_s + 2)`), an over-read
    at the first offset past the statement is inside the range, but one further out needs a row
    past the storage and the ask REFUSES (a bare -1: the ask is pure and sets no error,
    `memfn.h:1534-1537`). pcrec's `cc_served` (`known.c:413-424`) then records `refused`, the
    same detail `--memfn=no-window-search` produces, so a kit over-read defect would read like a
    legitimate decline;
  - therefore **the COVER ask passes proof storage up to the ceiling**, `MF_MAX_FWD -
    MF_PROOF_LO` = 4,104 rows (131,328 B, one cover ask per compile attempt) [RULED r22 F2 (i):
    the kit's proposal, for main to confirm]. Every over-read below the ceiling then lands inside
    the range, where B5 reads `under@j`/`over@j` by offset and byte and declines C14, as it does
    up to offset 32 today. B5 stays the independent control. Only a test at or past 4096 is
    refused, and no window statement reaches that far.
  - Other asks may pass the minimum: a non-cover site has no B5, and its refusal declines to the
    caller's existing route.
- **The kit's refusals [rev 3, F1: three, declared].** On a PROVING class the kit refuses its
  reply in three cases:
  - (R-out) a tested offset lies outside `[MF_PROOF_LO, MF_MAX_FWD)`;
  - (R-cap) the range needs more rows than the caller's storage holds (asks only: a define's
    rows are the art's, §5 "Where the rows live");
  - (R-short) the SELF-CHECK: the computed `end` is below `min(MF_MAX_FWD, last_s + 2)`, message
    "the proof range ends before the statement's following offset". It shares its source with
    `end` (the kit checking its own computation), so it is a self-check, not a control (§6 Q2).
  Each applies on BOTH paths: an ask returns a bare -1 (no message: the ask is pure); a define
  (`mf_define`/`mf_emit`) fails with the named message in `mf_art_error`, the only place a
  refusal's text is readable.
- **What "by construction" now means.** "The text tests no offset past the statement's first
  following offset" is the kit's PROMISE. B5 checks it, from pcrec's own `k` and statement
  (shared source: none). It is no longer a reason the range may stop early.
- **pcrec's B5.** It compares `[MF_PROOF_LO, MF_PROOF_LO + proof_n)` and treats every offset
  outside it as all ones. Its want past `k` is all ones too.
- **The short-range internal error** ("the kit's proof range ends at offset %d, before the
  cover's after-context at %d") stays as pcrec's defence. It is unreachable while the kit
  keeps the rule above, so it needs a plant. Its control is TWO rows [rev 2, F8; rev 3, F1]; one
  plant cannot do both, because R-short fires first and B5 is then never reached:
  - **(a) Kit row** (kit tests, its sabotage list): plant `end` cut to `last_s + 1`. Expect
    R-short BY ITS MESSAGE, read through `mf_define` (`mf_art_error`), never through an ask.
    Its control: the unplanted kit defines the same site.
  - **(b) pcrec row** (mech, combined branch, after B5): plant the same cut AND remove R-short
    (`SAB_FILE2` deletes that one check by its message text). Expect B5's named internal error
    BY ITS TEXT. It runs on an after-UNSTATED cover, `[0-9a-f]{32}` with nothing after it
    (`k` = 32, `last_s = k - 1` = 31, cut `end = k` = 32, so the range stops before `k` and B5
    fires); on an after-stated cover the cut end is `k + 1`, the range still reaches `k`, and
    the row would read UNDETECTED.
    - **Why `{32}` and not rev 3's `{40}` [rev 4, R3-5].** The row must take the cover with no
      width option. `[0-9a-f]{32}` is a cover at the default width 32: `k` = 32 meets stage 1's
      `cc_fits` (`k <= 32`), and stage 2's added C15 conjunct `k <= W` (cover_cap.md §11.1 A3)
      with `W` at the default `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH` = 32. Checked read-only with the main tree's `build/pcrec`
      (`-p rx`, emitted to the lane's scratch): `[0-9a-f]{32}` emits
      `#define RX_DFA_SCAN "cover"`, while `[0-9a-f]{33}` and `[0-9a-f]{40}` emit no cover.
      `{40}` would need `--window-search-width=40` or more, and without it the kit is never asked.
    - Its `SAB_REACH` asserts BOTH facts: the pattern takes the cover at the default width, and
      the cover states no after span (the cover's facts line, spelled at build time). Independence: B5 reads pcrec's `k`,
    never the kit's `last_s`, so (b) is the row whose expectation shares no source with the
    plant (learnings §3).
- **Old-field FIND sites [rev 3, F3].** The same `end` rule over their terms' stated positions.
  An old-field FIND term's text tests exactly its stated positions, so a position at or past
  `MF_MAX_FWD` keeps today's CLIP (`term_prove`, `compose.c:380`): the proof says nothing (all
  ones) there, which is conservative for every reader, and it moves nothing. R-out applies to
  window plan classes, whose TESTED set can differ from the stated one (the plan); that is
  where B5 must see an over-read.

**What retires: `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD`, NOW [rev 2, F17/F18: the old Q4 is
answered].**
- They exist only to define `MF_MAX_FWD` (`memfn.h:302-315`). `MF_MAX_AHEAD`'s one position
  (the after-context) is covered by `end`.
- Their code readers on main are `memfn.h:653` (`MF_WSPAN_POS`), `window.c:1850` (respelled
  above), and pcrec's `known.c:347-351` (`cc_exact`'s MkEnd check) and `known.h:27`
  (`MkEnd.set`). A1 on `lane/covs2afix` removes the pcrec ones.
- One more reader is a doc tool: `docs/dev/kvcensus/kvdfa.py:25` (`CAP = 32`, a comment-level
  reader).
- The kit branch merges only onto a branch with A1. Rev 1's fallback ("keep it 32 one more
  release") is withdrawn: with `cc_fits` admitting 4095, `known.c:347-351`'s internal error
  would fail every compile with a width above 32 (r20 F18).

## 2. ASK (2): do `MF_MAX_SPAN_POS`, `MF_WMAX_SPAN` and `MF_MAX_TERM` stay equal?

**Answer: no. They decouple. `MF_MAX_TERM` stays 32. `MF_WMAX_SPAN` stays 32 under its own
derivation. `MF_WSPAN_POS` becomes 4095, and `MF_MAX_SPAN_POS` retires (§1).**

- **`MF_MAX_TERM` 32** (`memfn.h:277`): the number of terms in one conjunction.
  - Its source is pcrec's VM stride and the strided ADVANCE (Q-R10-3), both unrelated to span
    length.
  - Its readers are unchanged: pcrec's three (VM stride, term count, ADVANCE stride) and the
    kit's (`ofsskip.c:115`, `gate.c:314,532`, `compose.c:470`, `generic.c:180`).
  - `mf_pred.term[MF_MAX_TERM]` (`memfn.h:722`) stays 2,560 B. Raising it to 4095 would make
    `mf_pred` about 330 KB, and `mf_site` larger still, on every holder.
- **`MF_WMAX_SPAN` 32** (`memfn.h:658`): spans per alternative, a COUNT of spans, not of
  positions. It is re-derived on its own line [rev 2, F16].
  - DERIVED bound: 25. pcrec's widest alternative is the reseed one, at most
    `PCREC_PREFIX_K_MAX` (24) walked offsets plus R.
  - Spelled 32: the derived 25 plus 7 of UNMEASURED slack, kept so that `mf_walt` and its
    readers do not move. `mf_walt.nspan` stays `uint8_t` (`memfn.h:689`).
- **`MF_WSPAN_POS` 4095**: its own literal, derived as in §1.

**What moves on pcrec's side** (each from cover_cap.md §11.1's lists, plus §5's reader lists):
- `form_checks.py` still parses a literal `#define MF_MAX_TERM 32`: no change.
- **Mech row S526 STAYS on `MF_MAX_TERM`** [rev 2, F7].
  - Its charter is integration.md §17.6, "MF_MAX_TERM lowered".
  - Once the bounds decouple, its k382mech shape (BUILD-REFUSED through `emit_dfa.c:1446`,
    which only bound `MF_MAX_TERM` through `MF_WSPAN_POS`'s derivation) would build clean and
    read UNDETECTED.
  - It returns to its pre-k382mech shape: plant `MF_MAX_TERM` 32 -> 31, `SAB_FILE2` removes
    `emit_vm.c`'s stride assert, and `SAB_EXPECT` DETECTED by C14's stride clause in
    `memfnforms` (`form_checks.py`, which reads `VM_MAX_STRIDE` from the source).
  - Its `SAB_REACH` today greps four lines, and two of them (`#define MF_WSPAN_POS
    MF_MAX_SPAN_POS`, `#define MF_MAX_SPAN_POS MF_MAX_TERM`) are deleted. The new REACH greps
    `#define MF_MAX_TERM 32`, `emit_vm.c`'s stride assert and C14's stride clause.
- **B2's control is cover_cap.md §11.6.3's reference compile** (checked by its message, hosted
  in `run_anchored_match.sh` §4c), not a kit plant. If a kit-side `MF_WSPAN_POS` 4095 -> 4094
  plant is still wanted, it is a NEW row, on the combined branch, ordered after B2, with a
  REACH that greps B2's assertion text. It is not S526.
- **`emit_dfa.c:1446` becomes non-binding** (32 <= 4095) and loses its witness. Its
  replacement is the pcrec-side assertion of the open question to main on non-cover bounds
  (§7). If main declines that, the assert should be named as witness-less in the stage-2
  checks list.
- **`PM_NPROOF 41`** (`tests/memfn/proof_meta.h:13`) and its `_Static_assert` (`proof_check.c:48`)
  go. **`G2W_NPROOF 41`** (`memfn/tests/g2/g2_win.h:23`) goes too. Their readers are in §5 (c).

## 3. ASK (3): the three forms, their cards, and the default

### The forms [rev 2: F14, defined over the existing segmenter; rev 3: F16 (a)]

The kit already has a span SEGMENTER: C-run's `find_groups` (`window.c:1766-1793`). It turns a
maximal stretch of plan positions sharing one compare into one RUN term, rendered by runcmp's
rows. Rev 2 does not add a second segmenter for L. It generalises this one:
- **Segments.** The segmenter's unit is the chosen ALTERNATIVE's plan positions in offset
  order, each the MEET of every span that states its offset (`merge`, C-MEET, and `plan_of`
  at origin/main `ed9677782`), not one stated span [rev 6, R5-1]. They form a sequence of
  segments, each of one KIND, chosen by one first-match row table:
  1. a LITERAL or cube stretch: today's C-run run compare, unchanged (`c_run` joins two
     positions only inside ONE stated span of two or more, never through a one-position span);
  2. a ONE-CLASS REPEAT: a maximal run of consecutive offsets whose positions carry one
     byte-identical multi-member set, the new loop row. It runs ACROSS stated-span boundaries,
     into a cover's before and after sides (RULED by the kit manager, 2026-11-16, r25 R5-1): a
     loop tests one set at every offset it covers, so a span boundary changes nothing it
     renders;
  3. a LONE test: anything else.
  A one-class repeat needs TWO or more entries [rev 7, r35 F28]: DERIVED, not tuned. A
  one-entry "loop" is the lone test plus a loop's set-up and exit, so two is the boundary by
  definition; a two-trip loop is fully unrolled by gcc -O2 (`-fopt-info-loop`, review r35), so
  the compiler takes the residual choice; the real cut-over is `h`, which the cards measure.
  A periodic segment, such as `(ab){500}`, is a fourth kind, NOT built. It is UNMEASURED.
  TRIGGER: a census row with a periodic span of 36 or more positions (36: DERIVED, the
  smallest census `k` past 32, uuid).
- **One knob, the inline head `h`.** Lone tests and one-class repeats at offsets before `h`
  render as today, in one `&&` chain. From `h` on, a one-class repeat becomes a loop.
- **Literal stretches are outside the knob [rev 3, F16 (a)].** A segment of kind 1 renders as
  ONE run compare in EVERY form, wherever it lies, and `h` never splits it: a literal stretch
  that straddles `h` stays one run compare. So a literal span is byte-identical in I, L and
  every H(h): `lit-l31` and `lit-l40` are never movers, and C2's `lit-l40` cell is the
  run-compare control (it measures the form, not a regression the kit built; r20 F14).
- **I = H(`h >= k`)**: today's text.
- **L = H(0)**: e.g. `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}` is 5 loops and 4 one-byte tests.
- **The general form's other unlocks** (filed with triggers; none in the first build):
  - a SIMD one-class-repeat segment reusing vrun's block/mask machinery. TRIGGER: C3 shows the
    scalar loop slower than I or than the engine at 500/1000 on hit-dense;
  - the class-truth-vector leaf shared with [POS-PARALLEL]/[SPAN-ISEL]. TRIGGER: that
    umbrella's stage 1 builds;
  - D-hors generalised to every tested offset (§4). TRIGGER: C1's near-miss column.
- **PLAN row (r20 F14, as ruled), for main to file:** "SHARED SEGMENTER: L's run finder and
  C-run's `find_groups` become one basic unit (segment kinds as a row table). TRIGGER: the
  first build of L." It is one unit, built once, with the build of L. It is not built as a
  separate refactor ahead of L.

### The head `h` and the default [rev 2: F11, F12, F16; rev 3: F9, F10, F11, F12]

- **h is a KIT constant** (D149: the cards' output, never a guess). It is INDEPENDENT of
  pcrec's width default (`PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`, `limits.def:187` on
  `lane/covs2afix`, 32 UNMEASURED until §11.4's night). Moving the width default never moves
  h, and h is never chosen to equal it.
- **Two readings the cards tell apart:**
  - **(a) death depth.** h near the expected depth at which candidates die under the art's
    byte rate, `E[D] = sum_i prod_{j<i} mass(S_j)`, about 1-2 for a hex or digit class on plain
    text. If the measured h* tracks (a) across the card classes, h becomes DERIVED from the
    byte rate and needs no constant.
  - **(b) code size.** h near the length below which the inline chain's size costs nothing
    measurable. The kit has no number for it: UNMEASURED.
- **The owner's words**, kept separate from the kit's, quoted in full [rev 7, r35 F25; rev 8, r36
  G14; rev 9, r37 H9: rev 8 labelled "the 14:35 passage whole, from "Also,"", but the passage
  opens two points earlier, and its point 3 is the dial §3 "The option" reads: now quoted whole]
  (2026-11-15, decisions.md D198 addendum 1 and `docs/dev/dev_journal.md`): at 14:35, "2. stage 2
  is fine. 3. we have a performance dial for pcrec. it could include some options for the kit.
  Also, I would default to sub span loops (excepting the
  measured head inline ) then measure if inline was faster than the other way around. Measure
  three: all inline, all loops, header inline then loops. Then the speed dial option can be
  always inline should it prove that is faster", and at 15:00, "I predict most all rx will only
  have a short span and will inline due to being under the inline head portion of the prover.
  Therefore, this issue is mostly moot".
  The short-span clause is the prediction drill (i) rests on. His words name no number. Rev 1's "about 32"
  was the kit's, and it is withdrawn.
- **The grid.** The DEFAULT candidates are the FINITE heads {0, 1, 2, 4, 8, 16, 24, 32, 64}
  [RULED r22 F9]. All-inline, I (`h >= k`), is TIMED in every cell as the REFERENCE: the
  denominator of R1's ratios and R2's dial arm. It is never a default candidate, so all-inline
  can become the default only as the owner's own ruled event. The grid is UNMEASURED: CHOSEN to
  resolve (a)'s predicted knee (1-2), to bracket the census lengths (24-64), and to include L
  (0). Note: at every C1-C2 length (64 or less), H(64) renders exactly I. So no C1-C2 cell tells
  64 apart from any longer head, and when h\* is 64 the length where loops begin is the GRID's
  choice, checked only by R5's C3 cells [rev 4, R3-3]. TRIGGER to extend the grid past 64 (a
  new card round over longer finite heads): a loss that R5 files against I or L.

**The decision rule: a COMBINING table (every row applies; none stops the others).** It applies
under plan A only [rev 3, F13]; under plan B no form ships and no h is chosen. Plan A is RULED
(forms now, 2026-11-16) [rev 5], so the rule applies.

| row | input | output |
|---|---|---|
| R0 gate | any form whose answers differ from the byte loop (G2) or from libpcre2 (pcrec's answer rows), or fail a card cell's own answer gate (python `re`) in ANY card, C3 included [rev 7, r35 F5] | that form is DEFECTIVE: it leaves the grid, is filed, and sets nothing. A gate failure is never a void. A gate failure of I or of an A/A arm (the reference itself) makes the night DEFECTIVE: no h is read from it |
| R1 default | every surviving FINITE grid value h; every timed cell c = (`k`, regime, layer) of C1 and C2 ONLY [rev 3, F11], in EVERY regime of the cards' list, NOT-WARM and `short-subject-search` included [rev 5, Q4/C6]; a cell void twice is read by step (5) [rev 6, R5-2] | (1) per h, `W(h)` = max over the cells READ of `t(H(h), c) / t(I, c)`, each `t` a raw median; `t(I, c)` is the median over the launches of EVERY arm whose built artifact hash-equals I's in that cell (I's POOL: I and each such head, measured per layer when the cells are built, never inferred from `h >= k`; a cell without I's own row is REFUSED loudly, never void) [rev 8, rulings R1, superseding r36 G3's RULED text]; where H(h)'s emitted text equals I's in a cell, `t(H(h), c)` IS that pooled reading: one text, one binary, one reading [rev 7, r35 F2]; a twice-void cell adds the term 1 for each head whose text is I there (`h >= k`) and no term for any other head. (2) The EQUAL set `E = { h : W(h) <= (1 + f_E) x min_g W(g) }`, computed once, never chained; `f_E` is the largest floor of the cells read (W is a worst ratio across cells) [rev 8, r36 G2]. (3) DOMINANCE [RULED r23 R3-1]: g DOMINATES h when `t(H(h), c) / t(H(g), c) > 1 + f(c)` in at least one cell c READ and `t(H(g), c) / t(H(h), c) > 1 + f(c)` in none, `f(c)` the floor of c's (regime, layer) [rev 8, r36 G2]. The dominated members of E are computed once, all against E, and removed together. In general, step (3) keeps the members of E dominated (faster beyond `f` in at least one cell and never slower beyond `f`) by the fewest others [rev 6, R5-6: one wording everywhere]. That is the undominated ones whenever any exist, which is the ruled step. When none exist (a cycle, possible because "beyond `f`" is a tolerance), it is those dominated least [RULED by the kit manager 2026-11-16, rev 5 Q2; the lane's rev 4 clause; rev 6 words "dominated" as above]. (4) **h\* = the LARGEST kept h that is the top or itself beat I beyond `f(c)` in some cell c read** [RULED r22 F10; rev 8, RULED r36 G4: a kept head that measured no win never ships; "the top" is the largest R0-surviving head, r36 G5]. If no kept head qualifies, h\* is the top. A pick that beat I is labelled "MEASURED (kit-grid@7 cards C1 span_cross, C2 span_pop; <n> cells read)" (DERIVED in place of MEASURED when R3 fires) [rev 7, r35 F10]. A pick that did not (the top) is CHOSEN: "h = grid top (64, CHOSEN), on a measured tie of every finite head" (or "of {" the members of E "}"), or "h = grid top (64, CHOSEN): every shorter finite head measured slower beyond `f`" (a colon, as drill (v)) [RULED r23 R3-3; rev 7, F10]. When R0 removed 64, the same labels lead with "h = <top>, the largest R0-surviving head (CHOSEN; the grid top failed R0)" [rev 8, r36 G5]. (5) **VOID** [rev 6, RULED r25 R5-2: a void cell never helps another head]: if any C1-C2 cell is void twice (or void by method), steps (1)-(4)'s pick is RECORDED with the card ids (it does not ship) and h\* is the LARGEST R0-SURVIVING finite head [rev 7, r35 F5]: 64 whenever it survives, labelled "h = grid top (64, CHOSEN): cell(s) <ids> void twice; the cells read picked H(<pick>)"; otherwise labelled "h = <h>, the largest R0-surviving head (CHOSEN; the grid top failed R0): cell(s) ...". If no finite head survives R0, no form ships (plan A's fallback, "Scope"). No void cell removes a head from E or from the dominance count, so a void can neither lower h\* nor move a competitor. Otherwise h\* is step (4)'s |
| R2 dial evidence | every cell of C1-C3 where I beats H(h\*) beyond `f`; C3's cells are timed at the picked h\* after step 2 (night step 2b), so until they are, R2's C3 half is NOT COMPUTED and the rule says so [rev 7, r35 F4] | filed as the evidence for the dial's always-inline option (cover_cap.md §11.3, unlock 2). R2 never changes R1's default |
| R3 derivation | h\* per card class against (a)'s `E[D]` for that class | if h\* tracks `E[D]` in every class, h becomes a derivation from the byte rate (§6 Q3); otherwise it stays a MEASURED constant. "Tracks" [rev 7, r35 F10]: each class's OWN pick (steps (1)-(4) over that class's cells read) is the surviving grid head nearest its `E[D]` (the larger on a tie), for every class with a cell read whose text MOVES for some surviving head [rev 8, r36 G6: a literal class, `lit40` or `abc60`, renders I at every head, so its own pick is the top on any data and could never track]; then the label reads DERIVED |
| R4 near-miss | C1's near-miss column: H(h\*) against C5 | a timed loss beyond `f` is §4's trigger (the skip's build); it never changes h\* |
| R5 long sanity | C3's cells, timed at the picked h\* (night step 2b) [rev 7, r35 F4]: H(h\*) against L and I at 500/1000 | a loss beyond `f` is FILED (with R2's evidence); it never re-picks h\*. It is the TRIGGER to extend the grid past 64 [RULED r23 R3-3]. A C3 cell void once is re-run; void twice it is RECORDED as not checked, never dropped. A C3 gate failure is R0 for its head (F5): at H(h\*) it removes h\* and the rule picks again, and C3 is timed at the new pick (F5's worse case: H(64) loops ONLY in C3, so its gate failure there must not read as a clean tie) |

- **Why each choice [rev 3, F11].**
  - The ratio is against I, an arm timed in every cell, so no value's W depends on which other
    values are on the grid (r22's drill: adding a losing h = 4 moved a best-normalised pick
    from 8 to 0; against I it stays 8).
  - **What a grid value can move [rev 4, RULED r23 R3-2; rev 3's "a never-picked value cannot
    move the pick" was false].** E's threshold is `(1 + f) x` the BEST W, so it depends on the
    grid's minimum, and that dependence is inherent to "within `f` of the best". It is accepted.
    - A value that is not the minimum cannot move the threshold. So it cannot move E's OTHER
      members, in or out.
    - A value outside E moves nothing (drill (vii)).
    - A value that becomes the new minimum moves the threshold, and with it E and h\* (drill
      (x)).
    - A value that joins E without being the minimum can still move h\*: as E's largest
      member, or by dominating the old h\* (drill (xi)).
    The grid is fixed before the cards run, so this is a property of the rule, not a way to
    steer it.
  - E is one threshold from the minimum, never a chain, so it is transitive by construction.
  - **Why the dominance step [RULED r23 R3-1].** I is the normaliser, and a head ties I in
    every cell where it renders exactly I (`k <= h`) or where candidates die at depth 0-1. So
    W(h) is about 1 for any head that wins in some cells and ties in the rest. Without step (3),
    such a head lands in E beside 64, and the largest-h tie-break throws its win away. R2 does
    not file it either, because R2 files only cells where I wins. Step (3) keeps every head
    that wins somewhere and loses nowhere, and drops the heads it beats. Between two such heads
    that each win in a different cell, the larger is kept: one h serves every length, and the
    larger head moves fewer bytes. When nothing dominates anything (the predicted tie), step (3)
    removes nothing, and h\* is still 64. **Kept is not won [rev 8, r36 G4].** "Beyond `f`" is a
    tolerance, not a transitive order: with H(8) 3-6 % faster than I in one cell, H(16) and H(24)
    can sit within `f` of H(8) there and within `f` of I everywhere. Then nothing dominates them,
    they are kept, and the largest kept head (24) shipped MEASURED although it won nowhere (r36:
    about 12 % of such nights). So step (4) ships only a kept head that itself beat I beyond `f`
    somewhere, or the top on a tie.
  - R1 reads C1-C2 only, because C3 times only I, L and H(h\*): it cannot feed the pick it
    depends on.
  - **Why R1 reads every regime cover_cap.md §11.4 reads [rev 5, Q4/C6].** A choice must hold
    in every regime its site can be in (K-1), and §11.4 B times the cover in five regimes:
    hit-dense, DENSE NEAR-MISS, NOT-WARM, miss-heavy and `short-subject-search`. If R1 read
    fewer, a loss the loop form causes in a regime R1 skipped would first show in §11.4 B as
    a width-rule loss (cover against engine, rows 5-6) and would lower main's width default,
    which is the wrong lever. With every regime in R1's worst cell, that loss raises W(h) for
    the losing head and moves h instead. The bound that results: at every C1-C2 cell,
    H(64) renders exactly I, so min W <= W(64), which is 1 within the A/A floor. A kept head
    therefore has W(h\*) <= (1 + f) x min W, so H(h\*) is no slower than I beyond about the
    floor in ANY regime at those lengths. §11.4 B's cells are all at those lengths (24-64) or
    literals (`lit-l40`, `a{500}`, which every form renders alike), so a width-rule loss there
    is one form I shows too, never one the loop form causes.
  - **A cell missing a regime [rev 5; rev 6, R5-2, R5-7].** As cover_cap.md §11.4's procedure:
    a C1-C2 cell missing a regime, or bimodal, is VOID and re-run once, and R1 waits for the
    re-run only. A cell still void after the re-run is read by step (5): h\* = the largest
    R0-surviving head (64 when it survives) [rev 7, F5], and the pick of the cells read is
    recorded, not shipped (no head ships on a missing reading).
    - **Bimodal, defined [rev 7, r35 F3].** cover_cap.md §11.4 leaves "spread" undefined (the
      bench's field); the cards define it, and a different field from the bench replaces it
      here. An ARM's 5 launches (log scale, sorted) are bimodal when they split into two groups
      of two or more with a gap of more than 4.5 launch sigmas between them; the launch sigma is
      pooled per (regime, layer) as the median of the arms' launch SDs over 0.9161 (the median
      SD of 5 normal draws, DERIVED), so one bimodal arm cannot inflate its own pool. The pool
      holds every timed arm of that regime and layer (C1, C2, C5 and the A/A arms); a pool of
      fewer than 10 arms (MIN_POOL, CHOSEN; unreachable on a real night, whose pools hold 92-105
      arms) borrows the night's pooled sigma for this test [rev 8, r36 G14 (SIMULATE-4)]; the
      floor's launch term (below) never borrows DOWN: it takes the larger of the pool's own sigma
      and the night's [rev 9, r37 H10 (1): rev 8 said "borrows" for both]. C3's cells read STEP
      1's pool sigma for their (regime, layer) [rev 9, r37 H10 (3)]. A cell is void when ANY of
      its arms is: I's arm, every arm of I's pool, and every head whose text differs from
      I's [rev 8: rev 7's "any arm whose text differs from I's" exempted I, which the script
      always tested]. 4.5 is CHOSEN from a simulation of 5 launches (2 x 10^7 draws): a false
      split has probability 1 x 10^-7 per arm under normal noise. Under t(5) it is about
      3 x 10^-5 per arm, because the pooled sigma reads 0.908 of the true one, so the effective
      gap is about 4.1 true sigmas [rev 8, r36 SIMULATE-7: rev 7 said 7 x 10^-6]; that agrees with
      the unimodal drill's 2-3 % of nights. Rev 6's script compared a range with twice the A/A floor
      times the median, which is not a bimodality test and voided 95 % of unimodal cells (r35
      F3). The drills (xvi) check both directions.
    - **A split that moves a median: I's pooled reading [rev 8, rulings R1, superseding r36 G3's
      RULED "tie the gate to f"].** A gap test cannot see a split that moves a median by about
      `f`. If 3 of an arm's 5 launches run slow by `s`, its median moves by the whole `s`, and the
      gap reads about `s` minus 1.7 launch sigmas. At a 1 % night `f` is about 4.4 launch sigmas,
      and a 4.5-sigma gap misses most splits from `f` to 1.5 `f`. Such a split in I's arm made
      every looping head "win" in that cell and shipped h\* = 24 in 54 of 100 nights (r36
      SIMULATE-2). Tying the gate to `f` cannot be built at 5 launches. Over 2 x 10^6 draws a
      unimodal arm fires "the median against the other group's mean beyond `f`/2" (2.1 sigmas)
      3.1 % of the time (t(5): 4.2 %), and a gap of `f`/2 fires 0.9 % (0.6 %). At about 1,100
      arms a night that voids cells on EVERY night, against F3's acceptance of 5 % of nights.
      Holding a false fire to 3 x 10^-5 per arm needs a threshold of about 3.4-3.8 sigmas, which
      voids a 3-of-5 split of size `f` only 61-82 % of the time. So the RULE reads I robustly
      instead: `t(I, c)` is the median over every launch of I's POOL, I and each head whose built
      artifact hash-equals I's in that cell (at least I and H(64) at every C1-C2 length, so 10 or
      more launches). Pool membership is MEASURED: `cards.py` hashes each built artifact per
      layer when the cells are built (`same_as_I.json`), and `h >= k` is the expectation, never
      the test. A cell whose I row is missing is REFUSED loudly and the night is DEFECTIVE; it is
      not void. So is a night whose pool RECORD is missing, or lacks any C1-C2 pattern x layer, or
      lists a head set without 64 at a C1-C2 length [rev 9, r37 H3: rev 8 refused a missing I ROW
      but read a missing record as I-alone pools, silently]. ~~One arm's transient then moves the
      pooled median by a fraction of a sigma.~~ [rev 9, r37 H2: false for a pool of TWO arms, I and
      H(64), which is every C1-C2 cell at `k` > 32 at the width R-45 exists for (`hex64`, `uuid36`,
      `alt49`). A whole-arm shift `s` (all 5 launches) puts 5 of the 10 pooled launches high, so
      the pooled median moves by about `s` / 2, each arm stays unimodal, and every looping head
      "wins" by that much: r37 measured P(h\* != 64) = 0.34 at 1.5 `f`.] A pool that holds 3 or
      more arms bounds one arm's transient to a fraction of a sigma; a pool of two cannot, and
      neither can say from the pooled median alone which arm moved. **The agreement gate [rev 9,
      RULED r37 H2]:** I's pool is ONE binary, so its arms' medians differ only by noise; where
      the largest over the smallest exceeds `1 + f(c)` (the cell's own floor, below, whose twin
      term already measures that noise), the cell is VOID, joins the re-run list (§"The re-run")
      and is never a pick. A pool of two voids on any such disagreement: it cannot tell which arm
      moved. [rev 10, r38 J1] The cell's own floor `f(c)` includes its pattern's twin term, and a
      cell whose pattern has no twin estimate voids here too. [rev 10, r38 J4 (2)] The gate reads
      the floor computed over the cells read BEFORE it gates, which includes the disagreeing
      pool's own contrast: a 2-arm contrast of `s` lifts its (regime, layer) twin floor to about
      0.86 `s`, and the gate still fires (0.90-0.92 of nights at 2 `f`, r38). A statement, not a
      defect. [rev 10, RECORDED LIMIT, r38 J3] The gate's threshold is sized by N, the HEAD
      comparison count, not by the gate's own test count (pools x arm pairs). On a degenerate
      night where every C1-C2 head is hash-equal to I (N = 0, `z` = 1.645: a no-op lever build,
      or R0 removing every moving head) it voids nearly every cell on pure noise (first-void
      0.983-0.993 of nights, 1-3 re-run rounds); the cost is re-run rounds, never a wrong h\*
      (P(h\* != 64) 0.000-0.003), and a healthy width-32 or width-4095 night never reaches it
      (0.000 first-void). Recorded, not built against.
      Only I's reading can make every head win or remove 64 (64 reads I's pool at every C1-C2
      length). A slow split in a head's own arm only makes that head lose. The residual is a FAST
      3-of-5 split in a head arm, which is outside the pool's reach and the gate's: it ships that
      head in 27 of 100 nights at 1.5 `f` (`cards.py selftest`'s RECORD line, not gated;
      27 of 100 under rev 8). A fast
      transient on 3 of 5 consecutive launches is not the shape interrupts, migrations or
      frequency drops take (they slow a launch). It is recorded, not built against. Drill (xviii)
      checks the pooled reading. C3 (R2's C3 half, R5) still reads I's own arm: C3 never feeds
      the pick.
    - **The re-run [rev 7, r35 F7].** A cell void once (missing, an arm void, bimodal) is
      re-timed WHOLE, every arm of it, in a later step of the same night (`cards.py rerun`),
      and the re-run's rows replace the first reading of that cell. The rule refuses to reach
      step (5) while any cell has been attempted once; a cell is void twice only when its
      re-run is void too. A gate failure is never re-run (it is R0, F5). [rev 10, r38 J4 (1)]
      `rule` lists the cells void once by a missing or void arm or a bimodal arm BEFORE the
      agreement gate runs, so a cell the gate voids only once those cells are read owes a
      SECOND `rerun` round (observed in 4 of 2,100 one-pattern nights; up to 3 rounds in J3's
      shape). Each round re-times only cells attempted once; no cell is re-timed twice, so the
      rounds end. `rule` names each owed round with `NEXT cards.py rerun RUNDIR`.
    - **Void by method [rev 7, r35 F8].** A cell in a regime whose method is the kit's
      approximation (below, "The regimes' methods") is void by method: it counts as void twice
      (no re-run can give it the bench's method) and step (5) reads it.
    - **Why not rev 5's reading.** Rev 5 read a twice-void cell as a loss (+infinity) for every
      head whose text differs from I there. That REMOVES the head from E, and through the
      fewest-dominators clause a removed head can free another: on r25's drill V (heads 8, 24
      and 32 in a dominance cycle, a `k` = 24 cell void twice), removing 8 broke the cycle and
      lowered h\* from 32 (the same cell read clean) to 24. Rev 5's claim "never below it" was
      false.
    - **Why not "skip the void cell".** Reading only the other cells and refusing a pick whose
      text differs from I in the void cell still lets a void HELP a head: a head whose loss was
      in the void cell drops its worst term, joins E and dominates a larger head. Lane r45f's
      search found 35 such cases in 200,000 random 4-cell outcomes (h\* below the same cells
      read clean); step (5) gave none, since it never ships anything but 64 under a void.
    - **What it costs.** A twice-void cell forfeits the cards' win for that night. The recorded
      pick says what the cells read showed; a later card night that reads the cell replaces
      the reading. If a regime's method is missing everywhere, every cell in it is void twice
      and step (5) fires on every head with the label above (R5-7 (a)). Dominance reads no void
      cell (R5-7 (b)). If a regime is missing from the `lit-l16` A/A cells, the floor `f` is not
      computable, and the cards follow cover_cap.md §11.4 row 1's reading for B's floor (the
      night is void) (R5-7 (c), noted).
- **The floor `f` [rev 7, RULED r35 F2: sized to the comparison count; rev 8, RULED r36 G2: per
  (regime, layer)].** The cards' own A/A
  cells (`lit-l16`, every regime READ and both layers, run with the cards on the same binary)
  estimate the noise of one ratio of two medians, which is exactly what a head against I is:
  `σ` = the RMS of `ln(t(aa) / t(aa-twin))` over those cells, raised to its 95 % upper bound
  `σ_up = σ x sqrt(n / χ²(0.05; n))` (n cells; the bound pays for estimating `σ` from about 8-12
  cells). N = the number of one-sided head-against-I comparisons the rule makes: every
  (surviving finite head, cell read) pair where the head's text differs from I's. Then
  `f = max(f_AA, exp(z(α / N) x σ_up) - 1)`, with `z(p)` the standard normal quantile at
  `1 - p`, α = 0.05 (CHOSEN: the ruled acceptance rate) and `f_AA` the largest A/A ratio, the
  floor cover_cap.md §11.4 reads (never undercut). A RATIO (so `1 + f` multiplies), never a
  difference.
  - **Per (regime, layer) [rev 8, RULED r36 G2].** The A/A term is one number for the night, and
    it assumes every cell's noise equals the pooled A/A noise. With one regime 3x noisier,
    P(h\* != 64) on pure noise was 0.31-0.37; with the A/A cells 0.7x the arms it was 0.15-0.16
    (r36 SIMULATE-1). So each cell's floor is `f(r, l) = max(f, exp(z(α / N) x sqrt(2) x 0.5355 x
    σ_up(r, l)) - 1)`. Here σ(r, l) is the pool's launch sigma (the bimodal test's own:
    the median of its arms' launch SDs over 0.9161). 0.5355 is the SD of the median of 5 normal
    draws, so `sqrt(2) x 0.5355 x σ` is the log SD of a ratio of two arms' medians (DERIVED).
    σ_up raises σ to its 95 % bound by the median estimator's relative error, 0.4754 / sqrt(n)
    over the pool's n arms (DERIVED: 1 / (2 f(m) m), with f the density of a 5-draw SD at its
    median m). A cell's comparisons (R1 (3)-(4), R2, R5) use its own (regime, layer)'s
    floor; E uses the largest floor of the cells read. R4 compares H(h\*) at (near-miss, layer)
    with C5's engine arm, which is timed at layer `off` only, so R4 reads the LARGER of the two
    floors, `max(f(near-miss, l), f(near-miss, off))` [rev 9, r37 H10 (2): rev 8 said "its own
    (regime, layer)'s floor"]. ~~**Why the launch-sigma bound, not a per-(regime, layer) A/A
    floor**: the night times ONE A/A pair per (regime, layer) ... Making it usable needs about
    eight A/A pairs per pool, eight times the A/A arms.~~ [rev 9, RULED r37 H1: WITHDRAWN. The
    premise was false: the night already times about 40 hash-equal arms in 9 pools per (regime,
    layer), I's pools, which is about 31 contrasts with no extra arm. And the launch term cannot
    see between-run noise (below).]
  - **The twin term [rev 9, RULED r37 H1 + H2, one mechanism with the agreement gate].** The
    launch term reads one arm's launch-to-launch scatter, so it cannot see an offset an arm
    carries over all 5 of its launches (between-run noise: placement, a frequency state, a
    cache layout fixed at exec). The A/A term sees that, but it is one night-wide number, and an
    offset in ONE regime dilutes into it: with a per-arm offset of 2 % in one regime, P(h\* !=
    64) on pure noise was 0.26-0.29 under rev 8 (r37 SIMULATE-1, VERIFY). The arms that measure
    it are already timed: every C1-C2 cell's I's pool (I and each head whose artifact hash-equals
    I's there) is ONE binary timed as separate arms, so the spread of its arms' log medians is
    launch noise plus between-run noise, the full noise of a head against I. Per (regime,
    layer), over the cells read: `σ_c = sqrt(2 x SS / df)`, SS the pools' summed squared
    deviations of `ln median` from their own pool mean and df the summed (arms - 1) (the RMS of
    the twin contrasts; about 31 at the expected pools, `h >= k`: 3 + 3 + 2 + 2 + 1 + 9 + 1 + 9
    + 1). It is raised to its 95 % bound `σ_c x sqrt(df / χ²(0.05; df))` (χ² now computed
    exactly, since df can be small), and the floor becomes `f(r, l) = max(f, the launch term,
    exp(z(α / N) x σ_c,up) - 1)`. Every term is a floor under the others: the A/A term keeps
    cover_cap.md §11.4's reading, the launch term needs no pool of two, and the twin term carries
    between-run noise per (regime, layer). The comparison against I's POOLED median has less
    noise than two single arms, so `sqrt(2)` is conservative.
  - **The twin term PER PATTERN [rev 10, RULED r38 J1].** Pooled per (regime, layer) over 9
    patterns, the twin term dilutes noise confined to ONE pattern: between-run offsets act per
    binary, i.e. per pattern kernel, and 18 of the 31 df come from `lit40`/`abc60`, which make no
    head-against-I comparison. Every arm of one pattern carrying its own 2 % offset gave P(h\* !=
    64) = 0.40-0.69 under rev 9 (r38 SIMULATE-1, VERIFY). So the twin term is ALSO computed at the
    finest level the night times twins: per pattern, over that pattern's own hash-equal pools in
    its cells read (its 12 (regime, layer) cells: df 12 at a 2-arm pool, 24 at a 3-arm pool, 36
    at `hex24`'s 4), by the same formula and the same `z(α / N)`. A cell's floor is `f(c) =
    max(f(r, l), twin(pattern))`: the per-pattern term is a floor IN ADDITION to the (regime,
    layer) one, never instead of it. A pattern whose cells read leave no pool of two (df 0) has
    no estimate: its cells are VOID through the agreement gate (re-run once, then void twice),
    never pooled up to a coarser level. (Reachable only by a pool record without the grid top,
    which H3 already refuses, so the clause is a guard.) The χ² bound already pays for a small
    df: at df 12 its factor is 1.52 (1.27 at df 31), so a pattern with few cells read gets a
    higher floor, not a borrowed one. On a 1 % night the A/A term (about 4.4 %) still binds; the
    per-pattern term binds only where one pattern is noisier (`selftest`'s class drill, drill
    (xxi)).
  - **Why this mechanism.** Rev 6 used `f_AA`, the max of about 12 A/A draws, as the threshold of
    every comparison, but the rule makes 600 of them with every regime read (108 C1-C2 cells x 9 heads, less the
    cells where a head is I: 50 per regime and layer) and 400 on a night with the two
    approximated regimes void by method [rev 8, r36 SIMULATE-7: rev 7 said "about 700"]. On pure noise H(64) is I at every C1-C2 cell, so h\* != 64 needs a
    head that is "faster beyond `f`" in some cell (it then dominates 64, or survives where 64
    does not); with a max-of-12 threshold over 400-600 chances that happens about one night in two
    (0.487 in rev 7's noise drill; review r35 measured 0.31-0.42 through the old script). A
    Bonferroni bound over N sizes the threshold to the chances actually taken, so a false win
    anywhere has probability at most α, whatever the cell count; it is one formula, needs no
    extra arm and no extra timing, and reads only what the night already times. The other two
    options were weaker here: a win "reproduced across layers or regimes" changes WHAT a win is
    (a regime-specific win, the case K-1 asks R1 to see, would never count), and per-cell A/A
    twins double the night's arms. Reading I's median where the text is I's removes comparisons
    that can only be noise. Its price is sensitivity: at a 1 % launch noise `f` is about 4 %, so
    a head must win by more than that somewhere; drill (xv)'s power line shows a true 10 % win
    picked in 60 of 60 nights (rev 8; rev 9, with the twin term: 60 of 60).
- **Why the largest h among equals [RULED r22 F10].** It is the owner's prediction (short spans
  stay inline under the head) and the fewest movers: a tie buys no byte move. "Less text" (rev
  2's reason for the smallest h) was asserted, never measured, and C4 is not an input to the
  rule.

**Drills, re-run against the rule as written [rev 3, F10, F11; rev 4, R3-1, R3-2, R3-3; rev
6, R5-2; rev 7, r35 F2-F7; rev 8, r36 G2-G5; rev 9, r37 H1-H3].** Rev 9's record is `cards.py
selftest` (89 checks; lane formsfixe's report); rev 8's was the same command (56 checks;
lane formsfixc's report); rev 7's was (every drill below, the
whole-night drills (xv)-(xvii) and the re-run, void-by-method and C3 cases; output in lane
formsfixa's report). Rev 4 re-ran every drill with a script that implements R0-R1 exactly as the table
states them; rev 6 re-ran every drill with a script that implements steps (1)-(5) as written
here, and drills (i)-(xi) give the results below unchanged (no drill has a void cell). The
scripts and their output are in lane r45d's and lane r45f's reports, "Drills". `f` = 0.025 unless stated. A
cell list is `(c1, c2, ...)` of `t(H(h), c) / t(I, c)`.
- **(i) I and H equal at `k` <= 32** (every ratio 1.00). E = every finite h, nothing is
  dominated, and h\* = 64, labelled "h = grid top (64, CHOSEN), on a measured tie of every
  finite head". Every span of 64 or fewer positions stays all-inline (no byte moves at today's
  covers), and longer spans loop after a 64-position head, a length that only R5 checks.
- **(ii) I faster beyond `f` in ONE cell (`k` = 24, one regime), ties elsewhere** (that cell
  1.10 for h < 24). W(h < 24) = 1.10. For h in {24, 32, 64}, H(h) is I at `k` = 24, so W = 1.
  E = {24, 32, 64}, nothing is dominated, and h\* = 64, labelled "grid top (64, CHOSEN), on a
  measured tie of {24, 32, 64}". R2 finds nothing in C1-C2 (H(64) is I there) and reads C3.
- **(iii) L faster everywhere beyond `f`** (H(0) 0.80, every other head 1.00). E = {0}, h\* =
  0, MEASURED: the default is L.
- **(iv) All within noise** (every ratio drawn inside ±1 %, under `f`). Nothing is faster
  beyond `f` anywhere, so nothing is dominated. As (i): h\* = 64, CHOSEN, on a measured tie of
  every finite head.
- **(v) I faster beyond `f` in some cells, tied elsewhere** (r22 F9's case; I wins both `k` =
  60 cells: 1.08 and 1.06 for every h < 60). E = {64}, and h\* = 64, labelled "grid top (64,
  CHOSEN): every shorter finite head measured slower beyond `f`". R2 then files every C3 cell
  where I beats H(64). All-inline at every length is reached only by the owner choosing the
  dial option.
- **(vi) Near-equal chain** (one cell at `k` = 60; W(0) = 0.94, W(1) = 0.92, W(2) = 0.90,
  W(64) = 1.00 because H(64) is I there, the others 1.12) [rev 4: rev 3's values put every head
  but 0-2 above I, including H(64), which is I at C1-C2 lengths]. The threshold is 0.9225, so
  E = {1, 2}. 2 does not dominate 1 (0.92 / 0.90 is inside `f`). h\* = 2, MEASURED. No chaining
  reading exists.
- **(vii) A losing value added** (`f` = 0.01; I's times (1.20, 1.20); h = 0 at (1.00, 1.10),
  h = 8 at (1.08, 1.00)). W(0) = 0.917 and W(8) = 0.900, so E = {8} and h\* = 8. Adding h = 4
  at (0.80, 2.00) gives W(4) = 1.667, outside E: E and h\* are unchanged.
- **(viii) A form fails G2.** R0 removes it, and R1 picks among the rest. On (ii)'s data with
  H(64) failing, E = {24, 32}, nothing is dominated, and h\* = 32, labelled "h = 32, the largest
  R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of {24, 32}" [rev 8, r36
  G5: rev 7 labelled this tie MEASURED; 32 won nowhere]. If every finite h
  fails, no form ships and plan A falls back (below); the rule prints "no form ships" and no h\*
  [rev 7, r35 F6: rev 6's script raised an error here].
- **(ix) A dominance cycle** (the case the lane's search found; three cells: H(8) = (0.95,
  1.02, 0.99), H(16) = (0.97, 0.99, 1.00), H(32) = (0.99, 1.00, 0.97), H(64) = (1.00, 1.00,
  1.00), the shorter heads losing). E = {8, 16, 32, 64}. 16 dominates 8 (at c2), 32 dominates
  16 (at c3), 8 dominates 32 (at c1), and all three dominate 64, so every member is dominated.
  The fewest-dominators clause keeps {8, 16, 32} (one dominator each) and drops 64 (three).
  h\* = 32, MEASURED. Without the clause the rule would have no answer here. A plain "skip the
  step" would have shipped 64, which every other member beats.
- **R3-1's drill: H(8) best in one cell, H(32) in another.** Cells: c1 (`k` = 24, hit-dense),
  c2 (`k` = 60, hit-dense), c3 (miss-heavy). H(8) = (0.80, 0.95, 1.00), H(32) = (1.00, 0.85,
  1.00), H(16) = H(24) = H(64) = (1.00, 1.00, 1.00), and the shorter heads lose. W(8) = W(16)
  = W(24) = W(32) = W(64) = 1.00, so E = {8, 16, 24, 32, 64}. H(8) and H(32) each dominate 16,
  24 and 64; neither dominates the other. Survivors {8, 32}, h\* = 32, MEASURED. Rev 3's rule
  gave 64 and dropped both wins. H(8)'s win at c1 is still not shipped (one h serves every
  length). It stays in the card's output; R2 does not file it, because R2 files only I's wins.
- **(x) R3-2: a new minimum moves the pick** (one cell; W(8) = 0.97, W(16) = 0.975, W(24..64) =
  1.00 [rev 8, r36 G4: rev 7's H(16) at 0.99 won nowhere beyond `f`, so step (4) would ship 8;
  at 0.975 it beats I beyond `f` and the drill keeps its R3-2 point]). E = {8, 16}, h\* = 16. Adding h = 4 at 0.95 makes it the minimum. The threshold falls
  to 0.974, so E = {4, 8} and h\* = 8: h = 4 is never picked, but the pick moves. Adding h = 4
  at 0.985 instead (not the minimum) gives E = {4, 8, 16} and h\* = 16, unchanged.
- **(xi) R3-2: a non-minimum value that joins E moves the pick by dominance** (two cells; H(8)
  = (0.97, 0.97), H(16) = (0.975, 0.975) [rev 8, as (x)], H(24..64) = (1.00, 1.00)). E = {8,
  16}, h\* = 16. Adding h = 12 at (0.985, 0.95), with W(12) = 0.985 and not the minimum: 12
  dominates 16 (at c2, 0.975 / 0.95 = 1.026), so E = {8, 12, 16}, survivors {8, 12}, h\* = 12.
- **(xii) r25's drill V: a void cell in a dominance cycle [rev 6, R5-2]** (`f` = 0.04; cells at
  `k` = 36, 40, 49 with H(8) = (0.90, 0.93, 0.95), H(24) = (0.95, 0.90, 0.93), H(32) = (0.93,
  0.95, 0.90), heads 0-4 and 16 at 1.20, plus a `k` = 24 cell). Read clean (every head ties I
  at `k` = 24): E = {8, 24, 32, 64}, the cycle keeps {8, 24, 32}, h\* = 32, MEASURED. The
  `k` = 24 cell void twice: under rev 5's reading E = {24, 32, 64}, kept {24}, h\* = 24 (the
  defect); under step (5) the cells read pick 8 (recorded) and h\* = 64, labelled "cell(s)
  `k` = 24 void twice". The `k` = 40 cell void twice instead: the cells read pick 32
  (recorded), h\* = 64.
- **(xii') Drill V's `k` = 24 void, with H(64) failed R0 [rev 7, r35 F5].** The cells read still
  pick 8 (recorded); h\* = 32, the largest R0-surviving head, labelled "h = 32, the largest
  R0-surviving head (CHOSEN; the grid top failed R0): cell(s) k24 void twice". Rev 6 shipped 64
  here, a head R0 had removed.
- **(xiii) r25's drill N: a NOT-WARM-only loss** (`f` = 0.02; `k` = 32; H(8) 0.90 hit-dense and
  1.20 NOT-WARM, H(16) and H(24) 0.99 hit-dense). W(8) = 1.20, so 8 is out of E; nothing in E
  is dominated, and h\* = 64, labelled "on a measured tie of {0, 1, 2, 4, 16, 24, 32, 64}". The
  loss moved h, not the width default.
- **(xiv) A regime's method missing** (drill N's hit-dense cell read; its NOT-WARM cells at
  `k` = 32 and 24 void twice). The cells read pick 8 (recorded); h\* = 64, labelled with both
  cells (R5-7 (a)).
- **(xv) Pure noise at the real cell count [rev 7, RULED r35 F2].** 108 C1-C2 cells (9
  patterns x 6 regimes x 2 layers, every regime read) x 9 heads, every arm's 5 launches drawn
  from one true time with 1 % log noise, A/A cells alike, each night through the whole rule
  (floor, voids, re-run, R1): over 300 nights P(h\* != 64) = 0.033 under normal noise and 0.027
  under t(5) noise (accept: <= 0.05); 0.487 with rev 6's floor and every other rev 7 change
  kept. Power: a true 10 % win of every head <= 8 where it loops picks h\* = 8 in 59 of 60
  nights. **Rev 8 [RULED r36 G2]:** under rev 8's rule (per-pool floors, I's pool, step (4)'s
  win) the same drills read P(h\* != 64) = 0.000 (normal) and 0.000 (t(5)), power 60 of 60.
  HETEROGENEOUS noise, 300 nights each, the same acceptance: one regime 2x (`random`) 0.000;
  one regime 3x (NOT-WARM) 0.000; the A/A cells 0.7x the arms 0.000; the regimes at
  0.5/1/3/0.7/2/1x 0.000. Control: the 3x night under rev 7's floor (the A/A term alone) reads
  0.173 (accept > 0.15: the drill sees the defect). **Rev 9 [RULED r37 H1]:** under rev 9's rule (the twin term and the agreement gate added) the same drills read P(h\* != 64) = 0.000 (normal) and 0.000 (t(5)), power 60 of 60, and the four heterogeneous nights 0.000 each. Their control now turns the twin term and the gate off too (rev 7's floor is the A/A term alone; rev 9's twin term also sees a noisier regime, so a control that left it on read 0.000 and was blind): 0.177 (the χ² quantile is now exact; rev 8 read 0.173).
- **(xvi) Unimodal launches must not void [rev 7, RULED r35 F3].** The same nights under t(5)
  launch noise: 2.0 % of nights void any cell once (0.017 % of cells), and the re-run reads
  them (accept: <= 5 %). Control: one arm with 2 of its 5 launches 8 % slow voids in 48 of 50
  nights. Rev 8: 3.0 % of nights (0.025 % of cells), because I's pool adds arms to each cell's
  void test; the control still voids in 48 of 50. Rev 9: 3.0 % of nights (0.025 % of cells), and the agreement gate adds none on pure noise (normal: 0.000 with and without it; t(5): 0.030 with and without); the control still voids in 48 of 50.
- **(xvii) A gate failure of H(64) in C3 [rev 7, r35 F5's worse case].** On a pure-noise night
  whose C3 cells at H(64) include one gate failure: H(64) is R0, the rule picks among the rest
  (here 32, labelled "h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on
  a measured tie of every R0-surviving head" [rev 8, r36 G5: rev 7 said MEASURED on noise]) and
  asks for C3 at the new pick; it never prints a
  clean "measured tie" at 64. With C3 clean at 64 the night completes (R2's C3 half and R5
  computed); before C3 is timed the rule prints "R2(C3)/R5 NOT COMPUTED at h\* = 64".
- **(xviii) A median-moving split of I's arm [rev 8, rulings R1; `selftest`'s (G3) lines].** On
  pure-noise nights at 1 % (`f` about 4.3 %), I's arm in ONE cell (C1 `hex32`, hit-dense, SIMD
  off) has 3 of its 5 launches slow by `f`, 1.5 `f` and 2 `f`. P(h\* != 64) = 0.000, 0.000 and
  0.000 over 300 nights each (accept: <= 0.05). Control: with I's own arm alone (rev 7's
  reading) the 1.5 `f` split gives 0.397 (accept > 0.15). Converse: the same split in H(8)'s
  arm ships 8 in 0 of 100 nights at `f` and at 2 `f`. RECORD (not gated): a FAST split in
  H(8)'s arm at 1.5 `f` ships 8 in 27 of 100 nights ("Bimodal, defined": the residual).
  **Rev 9 [RULED r37 H2; `selftest`'s (H2) lines]:** every rev 8 line above re-runs under the
  twin term and the gate (I's 3-of-5 split: 0.000 at `f`, 1.5 `f` and 2 `f`; its control 0.397; the converse 0 of 100 at `f` and 2 `f`). A WHOLE-ARM shift (all 5 launches) of I and of H(64) in
  the SMALLEST pools, the 2-arm pools (I, H(64)) at `hex64`, `uuid36` and `alt49` (hit-dense,
  SIMD off), slow by `f`, 1.5 `f` and 2 `f` with `f` the cell's own floor (median 4.4 % on a
  1 % night): P(h\* != 64) 0.000 to 0.003 in all 18 cases (I and H(64) x three patterns x three sizes) over 300 nights each (accept: <= 0.05). Control: I at
  `hex64`, 1.5 `f`, under rev 8's rule (no twin term, no gate): 0.403 (accept > 0.15). The
  gate's own cost on pure noise: none measurable (nights with a first void: 0.000 with the gate and without under normal launches, 0.030 with and without under t(5); r37 asked that it stay within F3's 5 %). RECORD (not gated): the FAST split above now ships 8
  in 27 of 100 nights.
- **(xx) Between-run noise [rev 9, RULED r37 H1; `selftest`'s (H1) lines].** Every arm of a
  regime carries its own offset `exp(N(0, τ))` over all 5 launches (a re-run draws fresh
  offsets), on 1 % launch noise, 300 nights each (accept: <= 0.05). One regime (NOT-WARM), the
  A/A cells spared, τ = 1, 2, 3 %: 0.000, 0.000, 0.000. Every regime, the A/A arms too: 0.000, 0.000, 0.000. Every
  regime, the A/A cells spared: 0.003, 0.000, 0.000. Control: τ 2 % in one regime under rev 8's rule:
  0.663 (accept > 0.15; r37 measured 0.26-0.29 through VERIFY).
- **(xix) A kept head without a win [rev 8, RULED r36 G4; `selftest`'s (G4) lines].** One cell
  (`k` = 60): H(8) = 0.97, H(16) = H(24) = 0.99, H(32) and H(64) = 1.00, the shorter heads
  losing; `f` = 0.025. E = {8, 16, 24} (threshold 0.994) and nothing is dominated (0.99 / 0.97
  is inside `f`). Rev 7 shipped 24, which won nowhere; rev 8 ships 8, MEASURED. On synthetic
  nights (a 5 % win of H(8) alone in C1 `hex32`, hit-dense, off) the picks over 200 nights are
  {8: 157, 64: 43}, and no head without a win ships (r36: H(16) or H(24) MEASURED in about 12 %).
- **Summary [rev 4, R3-3].** In every outcome but (viii)'s last, a FINITE h ships with its card
  ids. Below 64 it is MEASURED when it beat I beyond `f` in some cell (rev 8, G4), and CHOSEN as
  the largest R0-surviving head when R0 removed 64 and nothing won (G5). At 64 it is labelled "h = grid top (64, CHOSEN)" with the
  measured tie or loss that put it there: the head's length is then the grid's choice, checked
  only by R5, whose loss is the trigger to extend the grid. Under a twice-void cell (xii, xiv)
  the label names the void cells and the recorded pick [rev 6].

**Which sites move: the full possible-mover population [rev 3, F16 (a); rev 4, R3-1; rev 5,
Q3/C1, C8; was "The stability trade"].** The owner RULED keep-short-spans = NO (2026-11-16):
spans of 32 or fewer positions move when the cards measure a win, and the kit keeps no
all-inline exception. Under the rule, a span changes from today's all-inline text only if
h\* < 64, that is, if the cards measure a shorter head faster beyond the noise in SOME cell and
slower beyond it in NONE (it then dominates 64), or a shorter head is the only one within the
noise of the best.
- **The forms do not ask what kind of site a span belongs to** (§3 "Answers"). So the
  population is EVERY window site whose stated span the kit renders, cover or not:
  - REPORT (cover) sites: today `hex32`, `dig-exact-32`, `hex32-id` and every other class
    cover the corpus and the bench hold;
  - the pre-check's run spans (R-38 K38-2: the whole stored run, up to
    `PCREC_MAX_REQ_RUN_SCAN` = 32 positions);
  - the reseed alternatives and the prefix (k-set) sites' spans, within pcrec's construction
    bounds (`PCREC_PREFIX_K_MAX` = 24; every other window site at 32 positions, cover_cap.md
    §11.1 B4), and every other site that states window facts (`WF_STATES`).
- **The predicate, in the segmenter's terms [rev 6, R5-1; rev 5's per-span predicate was too
  narrow].** The unit is an ALTERNATIVE, not a span: every window alternative pcrec states,
  the site's own (`pcrec_memfn_window_stated`) and each pre-check part's
  (`pcrec_memfn_part_window_stated`). For an alternative, its position at offset `o` is the MEET
  (bitwise AND) of the sets of every span that states `o`, as the kit's `merge` computes it;
  pcrec states both meets the kit may test there, over every span and over the verify-YES spans
  only (`rd_set` tests the second on a PARKED-entry alternative without reseed). A site is a
  POSSIBLE mover at h\* iff one of its alternatives has a run of two or more CONSECUTIVE stated
  offsets `o .. o + n - 1` whose positions carry one byte-identical set under either meet, that
  set has two or more members, and the run's LAST offset is at or past h\*. Span boundaries do
  not end a run: a cover's after side at offset `k` (and its before side at -1) joins the
  `0 .. k - 1` run when its set is the same. A site with no such run keeps its text at every h:
  literal stretches are one run compare in every form (`lit-l31`, `lit-l40` never move), and
  lone tests render as today.
- **Named witnesses [rev 6, R5-1].** `\w{32}\B`: the cover states span `0 .. 31` with `\w` and
  its after side at 32 with `\w` (a non-boundary after a word byte needs a word byte; end of
  subject fails, so the side is core). Its positions `0 .. 32` are one run of `\w`. Checked
  read-only on the main tree's `build/pcrec` (`-p rx --features assertions,classes`): it emits
  `RX_DFA_SCAN "cover"`, and the chain tests `s[c + 32]` with the same `\w` range test as
  `+ 30`. It is a possible mover at every h\* <= 32. **In this build it moves at h\* <= 29 and
  not at 30-32 [rev 8, r36 G12; rev 7's "does not move at any h\* <= 32" was overstated]:** the
  plan's E-find probe sits at offset 31, so the probe's position splits the run (the plan tests
  a subset of the stated offsets, below, and a dropped offset splits a run). What is left is the
  31-position stretch 0 .. 30, which loops from any head h\* <= 29 (review r36 measured `_j =
  0; ... < 31` at head 0 and `_j = 8` at head 8). The probe at 31 keeps the after side out of
  the run, so at h\* 30-32 the text is byte-equal to the deny. The predicate stays a stated
  SUPERSET, so the predictor is not red on it at 30-32, where it is listed as a predicted site
  that does not move. It stays in main's predicted-movers file at every h\* <= 32: that file
  is the identity check's population at h\* < 64. Its kin: `\w{k}\B` and `\W{k}\B` at
  every cover width `k` (possible movers at h\* <= `k`), and any cover whose after side's set
  equals its last class. Not kin: `\d{32}\B` (cover; its after side is `\w`, not `\d`, so the
  run ends at 31) and `\B\w{32}` (no cover today; a before side at -1 never extends a run
  forward).
- **What follows: the largest stated OFFSET, not the span length [rev 6, R5-1].** The bound a
  run can reach is the largest offset pcrec states, not "32 positions": at the width default
  32, a cover's after side sits at offset 32 (`cover_window`); the pre-check run states
  `0 .. 31`; the prefix walk stays below `PCREC_PREFIX_K_MAX` (24); each window statement is
  bounded by `start + len <= MF_WREACH` (`window_bounds_check`). So the largest stated offset
  today is 32. Re-derived, at today's width default 32:
  - h\* = 64 (the predicted tie): NO site moves, cover or not; the sweep's prediction is empty.
  - h\* = 32: only the cover kin above move (a run reaching offset 32 needs the after side).
  - h\* <= 24: every alternative with a run reaching h\* is a possible mover, covers, pre-check
    runs and reseed or prefix alternatives alike. No value below 32 is claimed to move
    nothing.
  A width default raised past 32 by the width night adds covers whose runs reach `k` (and
  `k` itself, through an after side); those are width events (cover_cap.md §11.2), predicted by
  the same predicate on the rebuilt binary. Rev 5's "h\* >= 32 moves nothing" is withdrawn.
- **How main's sweep predicts it (the facts that select the sites).** The prediction reads
  pcrec's OWN statements, never the kit's reply or plan, so it does not share a source with
  what it controls: per window alternative, each stated span's offsets, verify and member sets
  (the `mf_wspan` pcrec writes), the alternative's entry and reseed facts, and h\*, the one
  number the cards publish. The predictor computes both meets per offset itself. The prediction
  is a SUPERSET by design: the plan tests a subset of the stated offsets (a dropped offset only
  splits a run into runs that end no later), the kit chooses one alternative of those
  predicted, and a run of a two-member, one-bit set (a cube, such as `[aA]`) stays a kind-1 run
  compare. The sweep's red is a moved site OUTSIDE the prediction; a predicted site that does
  not move is listed (the kit's MFTRACE names the segment row that took it), never red.
- **The record the prediction reads is NEW [rev 6, R5-5].** No record exposes these facts on
  main: the only statement record under `PCREC_MF_ROUTE_TRACE` in `src/gen/memfn_sites.c` is
  `MFPRES` (counts only), and `span_facts` is gone (cover_cap.md §3). So main's build adds one
  pcrec-side trace record, working name `MFWSTMT`, beside `MFPRES` in the same trace build and
  under the same switch, written from the `mf_site` pcrec defines (never from a kit reply). One
  line per stated span: site id; site kind; `site` or `part <i>`; alternative index; its entry
  (`MF_ENTRY_*`) and whether the site reseeds; span index; `start`; `len`; verify; `core_lo`;
  `core_len`; and the span's `len` sets, each as 64 hex digits. Main's build also changes the
  predictor (today `lane/covs2afix`'s `predict.py`, reading the `--emit-facts` `cover` section
  only) to read this record, and adds a trace-build pass over the sweep's corpus. It is on
  main's list (§7) beside E13. This replaces cover_cap.md §11.1's
  "Non-cover window sites: no predicted move; any move is red" for the joint landing (main's
  edit, r45read E13).
- **The uuid shapes are NOT form movers [rev 5, C8].** `k` = 36 takes no cover today (stage 1
  covers `k <= 32`), so its text today is the engine route's. It gains a cover only if main's
  width default reaches 36, which is a WIDTH event (cover_cap.md §11.2's rule), predicted by
  the width sweep. Such a cover renders in H(h\*) from its first appearance; it never moves
  "from today's all-inline text", because it has none. Rev 3-4 listed it wrongly.

### Scope: plan A or plan B [rev 2, F13; rev 3, F14, F16 (c); RULED: plan A]

**RULED (the owner, 2026-11-16, forms-now-or-next = FORMS NOW) [rev 5]: plan A is the plan of
record, one joint landing.** Every "under plan A" below is therefore the plan; plan B stays as
the record of the alternative and because A's fallback lands B's interim outcome. The two
plans end in the same place; they differ in which landing carries the forms, the
default users get in between, and the cost.
- **Plan A (owner-literal; the kit RECOMMENDS it).**
  - The kit builds the forms (the segment rows, the option row, the head lever, G2 per form)
    as instruments.
  - The cards run BEFORE the joint landing, on the combined-branch binary, and set h\*.
  - The landing ships H(h\*) as the default.
  - Reasons: the owner's direction names the default ("default to sub span loops"); plan B
    ships the opposite default (all inline) for at least one landing; and §11.4's night then
    times the cover in the form that will ship.
  - **A's costs [rev 3, F14]:** a kit timing slot BEFORE the landing (one night if the cards and
    the width cells fit one window, otherwise two); the landing waits for it; and the landing
    is larger (the forms, the option row, the head lever, G2's new rows, the card rows).
  - **A's fallback [rev 3, F14].** If the cards cannot run before the landing, A lands with the
    forms BUILT but OFF (every span all-inline, as today), and switches them on in a later
    change, which is a second pcrec abi event. That is rev 1's withdrawn hybrid minus the
    unmeasured head: A's cost with B's interim outcome. **Who decides** that the cards cannot
    run: main, with Frank [RULED r22 F14; rev 4, R3-4]. **The build's interim [rev 7, r35
    F21].** The build ships h = 64 as an UNMEASURED DEFAULT (CHOSEN, the cards' grid top) until
    the cards run: the kit manager's launch ruling for lane forms, recorded in
    `docs/dev/lanes/forms_report.md` Summary ("The shipped head is 64, labelled `UNMEASURED
    DEFAULT` (the grid top, set by the cards), so NOTHING MOVES at width 32") and the kit
    journal's 2026-11-17 03:00 line. It is not the fallback's "built but OFF": H(64) and OFF emit
    the same bytes for every stretch of 65 or fewer positions; past that H(64) loops where OFF
    does not, and past about 3,300 wide positions OFF (the deny) is refused where H(64) compiles
    (r35 F1). Which of the two a landing without cards carries is main's to record with Frank
    (a decisions.md or plan.md row, r35 F21's main-side part); this text records both. It is the same call as cover_cap.md §11.6.1's FALLBACK
    (land at 32 UNMEASURED, time on landed main); under A the cards precede the width night, so
    that fallback also fires this one.
- **Plan B (stage-2 minimal; cheaper).**
  - The joint landing carries the carrier (§1, §5), the per-extent working state, the two
    witness rows, and form I only. Kit bytes are unmoved at every width that covers today.
  - The forms, the option row, the lever and the cards are the NEXT kit unit.
  - B's honest advantage: it is smaller, it needs no kit timing slot before the landing, and
    it is READY NOW with rev 3's text fixes (review r22).
  - ~~Form I alone keeps the cover legal at every width~~ [rev 7, r35 F1: rev 6 named the wrong
    cap]. R-45 FACT's ~151 emitted C bytes per position extrapolates to ~630 KB at 4095; the
    BINDING cap is the emitted-code cap `PCREC_MAX_VM_EMIT_CODE_BYTES` (500,000; despite its name
    `src/core/compile.c` applies it on every route [rev 8, r36 G14: rev 7 called it the VM-route
    cap]), not `PCREC_MAX_EMIT_BYTES` (1,000,000). Measured by review r35 on the combined tree at
    width 4095: form I (the deny) is refused past about 3,300 wide positions (the spec's number;
    r35's probe `[0-9a-f]{3330}` emitted 510,342 bytes of code) where H(64) and L compile, and it warns at the 250 KB advisory cap
    where the default does not. Under plan B's text (form I the default) that is a live default
    refusal; the fit rung or the spec sentence is main's (r35 F1 PLAN). The spec states the
    deny's refusal (registry.md §6¶8a, tuning.md §2.43¶3d).
  - B's cost: until the next unit lands, users get all-inline on long covers, the opposite of
    the owner's stated default; and the width night times form I, not the form that will
    ship.

### The cards

Rows for `memfn/data/cards/kit-synthetic.tsv` and the kit's measurement script, each added in the
build that adds its form (memory `pcrec-new-method-needs-measurement-card`).

| card | forms | k (shape) | subjects (regimes) | layers | what it decides |
|---|---|---|---|---|---|
| C1 crossover | I, and H(h) for every finite grid h (0 = L) | 24, 32 (`[0-9a-f]{k}`, `\d{k}`: the stage-1 movers and their twins) | hit-dense (all members); DENSE NEAR-MISS (`k-1` members then a non-member, repeated: EMITTED-2's shape); NOT-WARM (the matcher not in L1/L2) [rev 5]; miss-heavy (plain text, death at depth 0-1); `short-subject-search` [rev 5]; uniform random bytes. The first five are cover_cap.md §11.4's regimes, timed by §11.4's methods | SIMD-off, and SIMD-on where a level admits it | R1 and R3 cells at the shipped default lengths; R4's near-miss column |
| C2 population | as C1 | 36 (uuid: `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}`), 40 (`lit-l40`, a literal: the run-compare control, one compare in every form), 49, 60 (the census rows' own patterns), 64 (`[0-9a-f]{64}`, §11.4's synthetic width cell) [rev 3, F13] | as C1 | both | R1 and R3 cells at the population's lengths |
| C3 long | I, L, H(h\*) | 500, 1000 (`[0-9a-f]{k}`, `a{k}`) | as C1 | both | R2's dial cells and R5 at length |
| C4 size | I, L, H(h\*) | 32, 500, 1000, 4095 (`[0-9a-f]{k}`, `a{k}`) | none (compile only) | both | emitted C bytes against 250,000 / 1,000,000 (the size-cap ladder, R-45 FACT cost) and the VM code cap 500,000 [rev 7, r35 F1], `gcc -O2 -c` time, RSS and `.text`. Recorded, no timing |
| C5 engine reference | none: pcrec's engine route on the same subjects (`--memfn=no-window-search`) | as C1-C3 | as C1 | n/a | the floor every form is read against in the near-miss regime (R4, §4) |

**The procedure** (kit timing, unofficial, per `memfn/CLAUDE.md` standing question 1):
- Linux, `taskset`-pinned, calibrated loops, at least 5 launches, median, with A/A controls
  (`lit-l16`) for the floor `f`.
- **Which harness and which binary [rev 3, F13; rev 5, Q5/C3].** The cards run on the KIT's
  harness (the kit's measurement script), in the same window as the width cells, which are
  the bench's, and FIRST. They run on the frozen combined-branch binary, h set through the
  head lever. The width cells do NOT run on that binary: they run on the binary REBUILT with
  h\* compiled in, after the identity check passes (night order step 3). h is a kit constant
  set by kit timing, labelled MEASURED with its card ids, not an official bench verdict; its
  official check is the width night that follows, which times the cover at h\* on the rebuilt
  binary. If main prefers the bench to run the cards, the rows above are its spec and nothing
  else changes.
- **The regimes' methods [rev 5, Q4/C6].** Each card times every cell in every regime of C1's
  list, by the method cover_cap.md §11.4 uses for its width cells: NOT-WARM's method is the
  bench dev's (D198 (f)), and `short-subject-search` is the bench's subject. The kit's card
  script takes both as the bench names them. If either cannot run on the kit's harness, the
  cells in that regime run on the bench, from the rows above, in the same window. A cell
  missing a regime follows R1's void reading, step (5) ("Why each choice").
  - **The kit's approximations are void by method [rev 7, r35 F8].** Until the bench names its
    methods, the card script carries approximations of the two regimes (NOT-WARM: each 4 KiB call
    after an untimed eviction sweep, timed on miss-heavy text only; `short-subject-search`:
    LF-separated records of 48-80 bytes). They are NOT those regimes, so their cells are VOID BY
    METHOD: read as void twice (no re-run gives them the bench's method), and step (5) reads
    them. A night without the bench's methods therefore ships the largest R0-surviving head (64)
    and records the pick of the four regimes read. Their A/A cells are not floor inputs. `cards.py
    run` times them only with `--with-approx`, a record the rule never reads. A regime whose
    bench method is ported into the script stops being void by method in that change.
  - **In that branch the bench READS the head lever [rev 6, R5-3].** The card cells time each
    H(h) on the frozen binary, so the bench compiles those cells through
    `build/pcrec-harness --harness=span-head=N`, the TEST-ONLY lever (never a shipped compile,
    no public flag). The bench is then a lever reader for those cells only; its width cells
    stay on the rebuilt binary through `build/pcrec` ("The bench" below).
  - **The bench-only question** (for main to relay, memory `pcrec-ask-bench-dev`): can the
    bench run its regime's method on cells compiled by `build/pcrec-harness` with that option,
    and if not, can the method be ported to the kit's card script? If neither, those cells are
    void twice, and step (5) reads them (h\* = 64, labelled).
  - **The G7 fence** does not scan pcrec-bench (a separate repository), so a bench-side
    spelling of `--harness=span-head=` needs no `ALLOW` entry; a pcrec-side script that spells
    it under a fenced directory does (below).
- **The added cells' cost [rev 5, Q4], UNMEASURED.** C1-C2 hold 9 patterns (C1: 4; C2: 5,
  counting the census rows at 49 and 60 as one pattern each), 10 arms (I and 9 finite heads)
  and up to 2 layers: 180 arm-cells per regime. Going from 4 regimes to 6 adds 360 arm-cells
  to C1-C2's 720 (+50 %). C3 adds 4 patterns x 3 arms x 2 layers x 2 regimes = 48, and C5 (the
  engine, one arm, one layer) adds 13 patterns x 2 regimes = 26. The A/A control (`lit-l16`)
  gains its two regimes per layer. About 440 added arm-cells in all, each at least 5
  launches. The cards' wall time is unmeasured, so whether cards and width cells fit one
  window stays the night order's "one night, or two" question; the added regimes make two
  nights more likely, not certain.
- **NOT-WARM's calibration and the wall time [rev 7, r35 F11].** A time-calibrated NOT-WARM
  launch (repeat until 50 ms of timed work) pays an untimed 32 MiB eviction sweep before every
  4 KiB chunk, about 50 passes of 256 sweeps per launch: 8-20 h a night by arithmetic. NOT-WARM
  is calibrated on CALLS instead: one pass over the subject's chunks per launch. `cards.py plan`
  prints each step's expected wall time from named per-launch costs (UNMEASURED: 0.08 s a
  launch, 4 ms an eviction sweep), for the window request; one launch's wall time in the cards'
  own window replaces them.
- G2's per-form answer check is R0, a precondition, not a card.

### The head lever and its identity check [RULED r22 F12]

h is compiled into the kit, so timing the grid on ONE binary needs a lever:
- **The lever.** `mf_lever(art, "span-head=N")` (N in 0..4095), the kit's test-only lever
  family (R-30, `memfn.h:1596-1617`): never called by a shipped compile, no `options.def` row
  (memory `pcrec-flag-follows-caller-effect`: no public flag for it). It sets h on that art. It
  is the family's first VALUED lever.
- **pcrec's reach.** A harness option on `build/pcrec-harness` only (`--harness=span-head=N`),
  a new field in the harness struct beside `run_tie_left` and `mfind`
  (`src/core/internal.h:176-206`), passed at the lever site in `memfn_sites.c:210-226`. Off on
  every shipped compile.
- **Its readers, each changed in the build:** `mf_lever`'s parse and its `memfn.h` comment (the
  list of lever names); the form renderer that reads h; pcrec's harness option parse, its
  struct field and the lever call; `cli/CLAUDE.md`'s harness-option line; G2 (one pass per grid
  h, §3 "Answers"); the kit's card script (C1-C2 time I, L and each H(h) through the lever);
  the identity check (below); and, ONLY in the regimes fallback, the bench's card cells for a
  regime the kit's harness cannot run [rev 6, R5-3]. The answer-identity sweep does not read it
  (it reads `--memfn=` cells).
- **The G7 fence is a reader too [rev 4, R3-6].** `cli/CLAUDE.md` binds every new harness option
  to the lever rules: one global under `pcrec_harness_`, no `lib/` header declaration, and no
  mention outside the fence allowlist. `tests/compound/run_lever_fence.sh` (c) reds on any
  `--harness=` spelling under `tests/`, `scripts/`, `cli/`, `docs/spec/` or `docs/guide/` that
  its `ALLOW` regex does not admit. So wherever the build spells `--harness=span-head=N` under
  those directories (a pcrec-side row, a script), the `ALLOW` regex and its comment gain that
  path in the same change. The kit's own card script and identity check live under `memfn/`,
  which the fence does not scan.
- **The bench is NOT a reader for the WIDTH cells [rev 4, R3-6; rev 6, R5-3: in the regimes
  fallback it reads the lever for its card cells only, above].** The width cells do not time
  through the lever.
  They run on the REBUILT binary with h\* compiled in, after the identity check passes (night
  order step 3). So the bench compiles through `build/pcrec` as §11.4 B already states, needs no
  harness option, and has nothing to change. This refined step 3 of the order agreed with main,
  and main CONFIRMED it (night-order-edits YES, 2026-11-16; rev 5, Q5) [rev 5: rev 4's
  alternative, the width cells on the lever binary, is withdrawn].
- **The identity check.** After the cards fix h\*, the build compiles h\* in, and a check
  asserts that the lever at h\* emits text BYTE-EQUAL to the shipped build at h\*. So the timed
  artifacts are the shipped artifacts, though the shipped compiler is a rebuild.
  - **Its population [rev 6, R5-4]: EVERY predicted mover at h\*, cover or not** (the sweep's
    prediction, §3 "Which sites move", over its corpus), plus every card pattern and every
    census cover. The lever is art-level (`memfn_sites.c`, the `mf_lever` call on the art), so
    it reaches pre-check runs, reseed and prefix alternatives and the cross-span covers too, and
    a divergence there must be seen. At h\* = 64 the prediction is empty and the population is
    the cards and the census covers.
  - **The census, read from its source [rev 7, r35 F9].** "Every census cover" is the sweep's own
    population (cover_cap.md §6: "the sweep's count is the count of record"): every corpus
    pattern (`scripts/emit_sweep.py`'s corpus enumeration) whose `--emit-facts` `cover` section,
    on the FROZEN binary, says `cover` in either encoding. The count is printed and zero fails
    (K35). A bench-only pattern reaches the check through main's predicted-movers file.
  - **How.** It compiles each pattern twice at pcrec level, the frozen binary's
    `build/pcrec-harness --harness=span-head=<h*>` and the rebuilt `build/pcrec`, and compares
    the emitted C bytes, in BOTH encodings (byte and `-e utf8`) and both layers [rev 7, F9]. The
    frozen build must be NAMED (an unnamed one would compare the rebuilt tree's own harness, and
    the frozen-to-rebuilt tie would be lost silently) and must differ from the rebuilt one; at
    h\* < 64 the predicted-movers file is REQUIRED and must be non-empty (it is the population
    there; an empty file at h\* = 32 and width 32 would pass on cards and census that no head
    can move, rev 8, RULED r36 G8), and the check refuses without it. A `--census-limit` run is a
    SMOKE: it exits 4, never a verdict, even when its truncated census is empty [rev 8, G8].
    **Its reach is the population that MOVES, not the file [rev 9, RULED r37 H7].** A non-empty
    file can still name no head-sensitive pattern (`a{40}` is byte-identical at lever heads 0,
    24, 32 and 64, both layers), and then identity at h\* < 64 runs over bytes no head can move.
    So at h\* < 64 the check first renders every pattern of its population (movers, cards, census)
    at lever h\* AND at lever 64 on the FROZEN binary (lever 64's bytes are what a head-blind
    check degenerates to), prints how many differ, and refuses at zero. [rev 10, RULED r38 J7]
    The count is printed and floored PER SOURCE (cards, census, movers), not pooled: at h\* < 64
    the PATTERNS file's own moving count must be nonzero, so a movers file that moves nothing
    (`a{40}`) fails even where a card moves (rev 9's pooled count passed it on card `hex32` at
    h 24). It lives with the kit's card script under `memfn/` (outside the G7
    fence); a pcrec-side copy under a fenced directory takes an `ALLOW` entry.

### Answers, controlled by G2 [rev 2, F9; rev 3, F8]

G2's twins of the kit bounds do not move by themselves, and none is asserted against the kit's
name: `G2W_MAXPOS 32` (`memfn/tests/g2/g2_win.h:17`), `G2W_REACH 64` (`:20`); `G2P_MAXRUN 32`
(`memfn/tests/g2/g2_pres.h:19`). And raising them alone changes no generated span: in G2-win the
twins only SIZE arrays (`g2_win_gen.c:126-127`, and via `G2W_NOFF` below); every span length is
a LITERAL draw, 9 positions at most today (r22 F8). So the build moves the DRAWS:
- **The draw sites and their stated reach.**
  - FAM_REPORT, the cover's family (`g2_win_gen.c:433`, `2 + rnd(7)` / `1 + rnd(8)` /
    `1 + rnd(5)` today): draws `k` in `1 .. G2W_MAXPOS`, so its spans straddle every finite
    grid h.
  - A NEW repeated-class shape in FAM_REPORT: one multi-member set over a stretch, at lengths
    `h - 1`, `h` and `h + 1` for every finite grid h >= 1 (a loop row's trigger; the random
    `rand_set` draw, `:216-231`, rarely repeats one class).
  - **The other families [rev 4, R3-7].** L and H render at EVERY window span, cover or not:
    §1's carrier and the segmenter apply to every span, and the forms do not ask what kind of
    site a span belongs to. So the reseed, pre-check and run families (their literal draws,
    `:291-:539`, listed by line in review r22's fixind file, FIXIND-6) must cross the grid heads
    too. Today their reach (up to 9) puts positions on both sides of heads 0-8 only. **As
    shipped [rev 8, r36 G13; rev 7 promised lengths `h - 1`, `h` and `h + 1` for heads 16-64]:**
    each family gains a STRADDLE draw at every finite grid head h from 1 to 64 (`g2_win_gen.c`
    `straddle()` over its head list): a one-class stretch starting at 0, 1 or 2 and ending at
    `h + 1` .. `h + 4`. A stretch ending at `h + 1` is the one-entry-past-the-head lone test,
    `h + 2` the minimal loop; the below-head case is the REPORT family's `k` = `h - 1`. It is no
    weaker than the promised draw. It reaches past 32, whatever §7's other-sites-at-32 decides
    for pcrec, because G2 tests the kit's forms, not pcrec's statements.
- **The twins** [formsfixb, ruling R1: DERIVED from the kit's bounds, `G2W_MAXPOS` = min(128, MF_WSPAN_POS), `G2P_MAXRUN` = min(64, MF_WSPAN_POS), the long row 1024 (4095 under the raise): 32 / 32 / 1024 in a tree before the raise]. `G2W_MAXPOS` 128 and `G2W_REACH` 256, CHOSEN: twice the largest finite h (64),
  so h = 64 has positions on both sides [rev 3: rev 2's 64 was twice 32, not twice the grid's
  largest]; reach twice the span, as today. Each carries
  `_Static_assert(G2W_MAXPOS <= MF_WSPAN_POS)` / `_Static_assert(G2W_REACH <= MF_WREACH)`.
  `G2P_MAXRUN` 64 with `_Static_assert(G2P_MAXRUN <= MF_WSPAN_POS)`; its draw already reads the
  twin (`g2_pres_gen.c:333`).
- **The COUNTED line (K35).** G2-win prints, per FAMILY and per finite grid h, "sites with a
  looped segment past h", and FAILS at zero for any pair [rev 4, R3-7: a total over all families
  let the REPORT family hide an empty one]. The population is counted by the generator's own
  output, not assumed from the draw.
- **Long cases.** `k` = 500 and 4095 are their OWN generator rows: a fixed handful of sites
  each, every form, not part of the random space.
- **Readers that size from the twins:** `g2_win_gen.c:126-127` (`set[G2W_MAXPOS][32]`,
  `table[G2W_MAXPOS]`); `g2_win.h:21` (`G2W_NOFF = G2W_REACH - G2W_LO`) and its holders
  `g2_win.h:50-51, :59` (`g2w_reply`'s `plan`/`plan_term`/`plan_test`) and `:108-115` (the
  reference's `plan`, `plan_term`, `toff`, `tset`, `tcore`); the copies into them,
  `g2_win_gen.c:1145` and `:1290` (bounded by the kit's `nplan`); `g2_win_ref.c:168-176, :199,
  :273-291, :398-405, :474, :492`; `g2_pres.h:61`; `g2_pres_gen.c:187-188, :295, :333`. The
  long rows (reach 4096) need their own storage, sized by their `nplan`.
- **Runtime, UNMEASURED.** `g2_win_ref.c` loops O(reach) per offset. With the REPORT draw
  reaching 128, a REPORT site costs about 4x today's at most, and so does each new
  straddle draw in the other families [rev 4]; each long row about 4096/128 = 32x
  a random site, times a handful. The build records G2-win's wall time before and after as a
  non-timing record. If it more than doubles, the long rows move to a separate opt-in G2
  section.

### The option [rev 2, F10; rev 3, F15]

- **The row.** The forms get the kit's FIRST `options.def` PAIR row (the kind is already parsed,
  `options.c:65`, and dumped, `src/dump/axes_dump.c:977/:1025`). Working name `span-loop`
  (kit-owned, arch-blind). It has three states:
  - unset: the default, H(h\*) (under plan A);
  - `--memfn=span-loop`: FORCES L, i.e. H(0) on every span. That is the most loop-rendering
    arm, so it is the answer-identity arm for the loop rows;
  - `--memfn=no-span-loop`: forces I, today's text, and is pcrec's G1 deny.
- **The deny is not the dial's always-inline option [rev 5, C7].** Every kit change that moves
  bytes carries its own deny row (D144 item 4; `memfn/CLAUDE.md`): it is the change's OFF arm
  for pcrec's G1 timing and the identity gates, an escape hatch, not a tuning choice. So
  `no-span-loop` exists whatever the cards show. The owner's "speed dial option ... always
  inline" stays a dial cell (`--tune=N`, cover_cap.md §11.3 unlock 2), filled only when R2
  files evidence. Both select I's text; they differ in purpose and in who reads them (the
  deny: the gates and any caller; the dial: the dial's cells). cover_cap.md §11.3's "not a
  `--memfn=` value" then reads true of the dial and false of always-inline as a spelling;
  that sentence is main's to edit (r45read E14).
- **The kit's FORCE reader [rev 3, F15].** Today the kit reads options only through
  `kit_opt_denied` (`options.c:73`, matching `no-NAME`; callers `compose.c:171`,
  `presence.c:277`, `vrun.c:239/288/303`). The build adds one three-state read, unset / forced
  / denied, over the same `opts` string, with `memfn.h:1922`'s doc. When both spellings are
  given the DENY wins, as pcrec's own pair rule (tuning.md §2.43¶1).
- **Its readers, each changed in the same build:**
  - `docs/spec/registry.md` §6¶8a: the sentence "The section's rows, each a `deny` row" and the
    section's `| name | denies |` table, which gains the pair row with its force described;
    §6¶7, whose identity gates read their rows from that section [rev 3]. The spec hunk names
    the pair row (D80).
  - §6¶8b: the `memfn` section floor 13 -> 14 (read by `tests/registry/axes_registry_check.sh:186-192`).
  - `tests/axes/memfn_arm.py:346-349`: a `MEMFN_CLASS` entry for `span-loop`, with its measured
    DIFFER/SAME counts per cell.
  - `tests/axes/memfn_arm.py:452-460` handles the force spelling only as the REFUSES control for
    `deny` rows (a pair row is correctly exempt). The build adds a FORCE cell,
    `--memfn=span-loop`, to the answer-identity sweep, so L runs over the whole corpus at pcrec
    level, not only in G2.
  - `tests/ci/measured_axes.tsv` and `cloud_axes_shards.tsv`: a deny cell and a force cell
    [rev 3]. `tests/ci/cloud_units_plan.py:64` may key memfn cells by a `no-` token
    (SUSPECTED in r22); the build checks it against the force spelling.
  - ~~`memfn/src/formhash.c:425` (`s->opts = e->deny`): the force spelling gets its own form-hash
    instance, so measurement-set staleness sees L's bytes; H at h\* is the default instance
    [rev 3].~~ NOT BUILT [rev 7, r35 F19]: no reader (D77). The cards are whole-artifact cells
    (kit-grid@7), so no card reads a `kit:form` hash. TRIGGER: a card that names
    `kit:form.span-*`. (`tests/ci/measured_axes.tsv`'s span-loop cells come with the next
    measured run, which generates that file.)
- **The spec hunks' homes [rev 3, F15].** The row and its states: registry.md §6¶8a. The
  caller-facing behaviour (what the force and the deny do, and dense near-miss subjects as the
  cover's known slow regime, §4): tuning.md §2.43¶3d, beside the window search's denies.
- **The dial.** pcrec's `--tune=N` can carry the always-inline option as a cell once R2 files
  evidence (cover_cap.md §11.3, unlock 2). The kit never reads the dial.

### What a card needs from the box: the night order [rev 2, F12; rev 3, F13, FREEZE NOTE]

- **The order of record (plan A, RULED).** Ruling R1 (kit manager, 2026-11-16, AGREED WITH MAIN
  2026-11-16; main's night-order-edits YES, unconditional since forms now [rev 5]; this
  section and §8 are its record):
  1. The form cards C1, C2 and C5, with the A/A cells, run on the frozen combined-branch binary,
     h set through the head lever; a cell void once is re-run in the same window (`cards.py
     rerun`) [rev 7, r35 F7]. The rule that picks h (R0-R5 above, the dominance-cycle clause
     included, as RULED in rev 5, and rev 7's floor) is committed before the run. **Inside a
     card's block each cell is timed in ROUNDS [rev 10, RULED r38 J2]:** one launch of every arm
     of the cell (card, pattern, regime, layer) per round, 5 rounds, each round in a fixed
     pseudo-random arm order derived from the cell's key (`cards.py` `round_arms`), after every
     arm's untimed gate run. Rev 9 timed arm-major (all 5 launches of one arm, then the next),
     and the cell list puts I first and its twins (h24, h32, h64 at `k` = 24) last in a
     pattern's block, so a step in box speed between them read as a head win: a +4 % step after
     `hex24`'s H(4) gave P(h\* != 64) = 0.15-0.18, +5 % 0.32-0.37 (r38 SIMULATE-2, VERIFY). In
     rounds every arm samples the same stretch of time: a step outside a cell's middle round moves
     every arm's median alike; inside the middle round it splits the arms at random (never twins
     against heads by construction), and the bimodal test, the twin terms and the gate read it.
     The order of the cells themselves, and the ruled night order (cards, freeze h, identity,
     width cells), are unchanged.
  2. h is frozen by that rule's reading.
  2b. C3 is timed at the frozen h\* on the same binary (`cards.py c3`), and R2's C3 half and R5
     read it [rev 7, r35 F4]; C4's size record is taken at h\* (no timing). Before it times
     anything, `cards.py c3` checks the deny on C3's and C4's artifacts: no arm-I artifact may
     carry a span loop, and H(64), the arm an ignored deny renders, is the reach arm that must,
     rendered over C3 and C4 whatever h\* the step times [rev 8, RULED r36 G7; rev 9, RULED r37
     H4: rev 8's reach arm L proved the loop text is readable, not that the defect's arm loops;
     at width 32 only C4's `hex32` at h0 loops, so an ignored deny read green]. This is
     the step where an ignored deny shows: I would render H(64), which loops past offset 64 at
     `k` = 500, and step 1's patterns never reach that. Where H(64) loops nowhere (width 32),
     the check is VACUOUS and refuses: no timing on a tree that cannot show the defect. A C3 gate failure at
     H(h\*) is R0 for h\*: step 2 picks again and 2b runs at the new pick (F5).
  3. The build compiles h\* in, and the identity check (above) proves that the rebuilt
     binary emits the same bytes as the lever at h\* on the frozen binary. Only then are the
     width cells (cover_cap.md §11.4 B) measured, on that REBUILT binary, through `build/pcrec`
     with no harness option [rev 4, R3-6]. The width night still varies ONE thing, because the
     identity check ties its bytes to the binary the cards timed, and the h grid is still timed
     on one binary.
  If both fit one window, the cards queue first and the width cells are not-before the cards'
  verdict. Otherwise it is two nights. Measured in the other order, two coupled selections
  would be read backwards, and the width evidence would go stale when h moved.
- **cover_cap.md edits for main, OWED (the owner chose plan A; main's night-order-edits YES)**
  [rev 3, F13; rev 5]. These are the reply's own edits; r45read lists more (E6-E14), which are
  main's:
  - §11.4: the header's "ONE night" becomes "one night, or two if the kit's cards and the width
    cells do not fit one window"; the forms paragraph ("not part of this night unless the kit
    asks for a slot") becomes "the kit's form cards run first in the same window, and gate B's
    cells (not-before their verdict); B's cells run on the binary rebuilt with h\* compiled in,
    after the kit's identity check passes; B's procedure is otherwise unchanged" [rev 4, R3-6];
    `[0-9a-f]{64}` is a card cell (C2) as well as a width cell.
  - §11.4 "Regimes" [rev 5, Q4]: the kit's cards time the same five regimes by the same
    methods (one sentence, so the two lists stay one list).
  - §11.6.1: TWO steps between (4) and (5) [rev 5, C11: rev 4 named only the first]:
    "(4a) the kit's form cards on the combined branch; h frozen by the kit's rule" and
    "(4b) h\* compiled in (one kit constant; any byte it moves, at h\* < 32, rides the joint
    landing's one pcrec abi event, Q36), then the kit's identity check passes". The width night
    (5) times (4b)'s binary, which code round (4) did not see; whether (4b) takes a review of
    its own is main's call (§7). The FALLBACK gains "and the forms land OFF (all-inline),
    switched on in a later abi event" (plan A's fallback above).
  - §11.6.4: the line "the kit's three-form cards' timing (kit-side)" is removed: it is a
    precondition of stage 2's landing.
  - §11.1 "The prediction" and "Unchanged": the possible-mover predicate of §3 "Which sites
    move" replaces "Non-cover window sites: no predicted move" (r45read E13; main's to word).
    [rev 6, R5-1, R5-5] The predicate is over each alternative's positions keyed by offset
    (runs cross span boundaries; `\w{32}\B` is its witness), and its input is the NEW
    `MFWSTMT` trace record, a main-side build item with the predictor change and a trace-build
    pass in the sweep (§3 "Which sites move"). The identity check reads the same prediction
    [rev 6, R5-4].
- C4 is a non-timing job: boxqueue, no window (memory `pcrec-kit-nontiming-runs-no-ask`).

## 4. ASK (4): the dense near-miss regime (no form asked)

**Reading: it is a complexity class, not a constant factor.** The cover's stream RESTARTs one
byte past a failed candidate (`mf_wstream` RESTART, `memfn.h:1666-1667`; EMITTED-2: "resumes one
byte later"). On a subject where every byte is a candidate and candidates die deep, each byte is
re-tested about `k/2` times.
- **The arithmetic at `k` = 32** [rev 2, F20]. On EMITTED-2's subject (31 digits + `g`, period
  32), the candidate at period offset `i` makes `32 - i` tests, the failing one included,
  because the `&&` chain evaluates it. That is 528 tests per 32 bytes, 16.5 per byte, against
  the engine's one transition per byte. The x6.65 in instructions (230.7 M vs 1,534.8 M) fits
  that. (Rev 1's 496 / 15.5 left the failing test out.)
- **Extrapolated.** The cost per byte grows linearly in `k`: about 2,048 tests per byte at
  `k` = 4095. Scaling EMITTED-2's ratio by `4095/32` gives roughly x850 against the engine
  (UNMEASURED, an extrapolation for scale only).
- **The consequence.** Under a width near the ceiling, a dense near-miss subject is the one
  regime where a long cover can lose by orders of magnitude.

**What the statement already allows (facts, D157).**
- The kit has every position's set. On a failure at offset `j` with byte `x`, no candidate
  `c + u` with `0 < u <= j` can hold, unless `x` lies in `S_{j-u}`.
- That is the bad-character rule over sets: D-hors's shift table (`hors_table`,
  `window.c:1846-1862`), which today is evaluated only at the window's LAST offset. The probe
  `build/pcrec -p rx --features all --pattern '\d{32}'` (r20 F14) shows the cover site uses
  RESTART, not D-hors. On EMITTED-2's period-32 subject, the last-offset table helps only 1
  candidate in 32.
- So the skip the regime needs is D-hors's GENERAL form (the table at every tested offset), not
  a new mechanism. It belongs to the same deny family (`window-skip`), and it applies to every
  window site at every `k`, not to L/H only.

**Disposition [rev 2, F15: D77 strictly; RULED by the owner 2026-11-16, near-miss-fix-later =
NO].**
- The first build carries NO skip.
- **The forms are not a near-miss fix [rev 5, C4].** Every form, I, L and every H(h), restarts
  one byte past a failed candidate; a loop tests the same positions a chain does. So the forms
  change the constant per test, never the O(n·k) count, and no form answers cover_cap.md
  §11.2's EMITTED-2 "kit" step. Until the skip's trigger fires and the skip is built, that
  order has no kit step to run (cover_cap.md §11.2 and §11.6.4's "the kit's rendering first"
  are main's to edit, r45read E7).
- The only MEASURED loss is EMITTED-2's: x6.65 in instructions at `k` = 32, in form I, inside
  the shipped default. cover_cap.md §11.4 reports instructions and never rules on them. The
  loss at `k` > 32 is an extrapolation.
- The TRIGGER is C1's near-miss column, H(h\*) against C5 at `k` = 24/32 (row R4 of §3's
  table [rev 3]), together with cover_cap.md §11.4 row 5's near-miss cells. Either one showing a
  timed loss beyond the floor triggers the fix. (Plan A is ruled, so the C1 column runs before
  the landing; only under A's fallback are the §11.4 cells the trigger alone.)
- The fix is one answer to cover_cap.md §11.2's EMITTED-2 order (one-pass, kit, then §9 Q8):
  D-hors generalised, at every `k`.
- Until it lands, the option's caller-facing spec hunk (tuning.md §2.43¶3d [rev 3, F15]) names
  dense near-miss subjects as the cover's known slow regime.
- The idea is logged in the kit's ideas log, unevaluated.

## 5. ASK (5): how the statement and the reply carry the longer span, and the abi events

**Design: the per-position arrays leave every seam struct.**
- STATEMENT arrays are owned by the HOST.
- REPLY lists are written into storage the CALLER supplies to the ask [rev 2, F3].
- Each array is a counted list, so the seam still reads as a document (§5 "Where the rows
  live").

| type | today | rev 2 | storage owner | size today -> rev 2 (probe) |
|---|---|---|---|---|
| `mf_wspan` (`memfn.h:669-685`) | `uint8_t len, core_lo, core_len`; `set[MF_WSPAN_POS][32]`; `table_ref[MF_WSPAN_POS]` inline | `uint16_t len, core_lo, core_len`; `const uint8_t (*set)[32]` and `const uint32_t *table_ref`, each `len` entries | HOST (§5 (e)) | 1,164 B -> 32 B per span; host arrays 36 B per position: 1,152 B at k=32, 18,000 B at 500, 147,420 B at 4095 |
| `mf_class` (`memfn.h:1288-1343`) | `proven[41][32]` inline (1,312 B); `mf_run_reply` of `uint8_t` | `proven[]` REMOVED; appended LAST: `uint32_t proof_n; const uint8_t (*proof)[32];` (rows for offsets `MF_PROOF_LO .. MF_PROOF_LO + proof_n - 1`); `mf_run_reply`'s four fields `uint16_t`; `proven0`/`proven_prev` stay by value, COPIED from rows 0 and -1 as today | an ask: the CALLER's `mf_rows`; a define (`mf_result`, `mf_defined`): the ART's arena, valid until it dies | 2,932 B -> 1,640 B; rows `proof_n x 32` B: 1,312-1,344 at k=32, 16,288-16,320 at 500, 131,328 at 4095 (the lower figure when the after side is unstated) |
| `mf_result` (`memfn.h:1346-1372`) | holds `mf_class` | unchanged, holds the smaller class | the art (a define) | 3,000 B -> 1,712 B |
| `mf_wreply` (`memfn.h:1695-1719`) | `uint8_t nplan`; `plan[72]`, `plan_term[72]`, `plan_test[72]` inline; `uint8_t run_len` | `uint16_t nplan`; `const int32_t *plan`, `const uint16_t *plan_term`, `const uint8_t *plan_test` (`nplan` entries); `uint16_t run_len`; a NONE ask leaves `plan_test` NULL (it is the frame part's) | the CALLER's `mf_rows` | 532 B -> 136 B; 7 B per plan entry: 287 B at k=32, 28,728 B at 4095 |
| `mf_walt`, `mf_pred`, `mf_term`, `mf_site` | — | unchanged (`MF_MAX_TERM` 32, `MF_WMAX_SPAN` 32) | — | unchanged |

### Where the rows live [rev 2, F3: a real mechanism; rev 3: F2, F4, F5, F6, F7, F17]

Today the asks are PURE on a const art, and they have no arena parameter. `mf_ask` and
`mf_defined` take `const mf_art *` (`memfn.h:1527-1538`), and so does `mf_wdecide`
(`memfn.h:1729-1737`). The NONE ask avoids the art's arena on purpose (`window.c:2768-2770`).
Rev 1's "the kit writes rows into the caller's arena during the ask" therefore had no
mechanism. The candidates were:
- **(i) an `mf_arena *` parameter on the asks.** Rejected. An arena is an allocation CALLBACK,
  and seam principle 9 (`docs/design/stream/manifesto.md`, "Every seam is a document") lets
  no callback cross a seam. Every ask would also leave memory behind in the arena, re-asks in
  trace builds twice over.
- **(ii) allocating through the const art.** Rejected: it breaks PURE.
- **(iii) CALLER-SUPPLIED storage. CHOSEN.**

The seam change:
```c
typedef struct {                 /* storage the CALLER owns; the kit writes, never allocates */
    uint8_t  (*proof)[32];  uint32_t proof_cap;    /* class rows (mf_ask)               */
    int32_t  *plan;  uint16_t *plan_term;  uint8_t *plan_test;
    uint32_t plan_cap;                             /* plan entries (mf_wdecide)          */
} mf_rows;
/* PURE: the storage a reply for `site` needs; a function of the statement alone */
int mf_rows_need(const mf_site *site, uint32_t *proof_cap, uint32_t *plan_cap);
int mf_ask(const mf_art *, const mf_site *, const mf_hooks *def, mf_class *out, mf_rows *rows);
int mf_wdecide(const mf_art *, const mf_site *, const mf_hooks *def, uint8_t call,
               mf_wreply *out, mf_rows *rows);
```
- **`mf_rows_need`** gives the MINIMUM a correct text needs:
  - `proof_cap = min(MF_MAX_FWD, last_s + 2) - MF_PROOF_LO` for a proving class (§1), 0 for any
    other [rev 3, F3];
  - `plan_cap` = the number of distinct offsets the site states, which is <= `MF_WPLAN_MAX`,
    since plan offsets are stated positions.
  A caller may pass MORE. The ceiling is the constant `MF_MAX_FWD - MF_PROOF_LO` (4,104 rows).
  **pcrec's cover ask passes the ceiling** [RULED r22 F2 (i), main to confirm], so every
  over-read reaches B5 (§1); every other caller may pass the minimum.
- **The asks** write only `*out` and the caller's `rows`. They refuse (-1) by §1's three
  refusals (R-out, R-cap, R-short), and on -1 they write nothing to `rows` and leave `*out`
  zeroed (`ask_sel`'s `memset`, `compose.c:1068`): `proof_n` 0 and `proof` NULL [rev 3, F5
  (4)]. A part a call does not fill may be NULL/0: `mf_ask` reads only the proof part, and
  `mf_wdecide` only the plan part. A NULL `rows` refuses, except for a non-proving class asked
  through `mf_ask`, which needs none.
- **The rows' lifetime is the caller's.** Two asks given the same storage overwrite each
  other, so a re-ask that must compare against an earlier reply (§5 (a)) uses its own
  storage.
- **The PURE contracts** (`memfn.h:1528-1537`, `:1729-1735`) change by one clause: "writes only
  `*out` and the caller's `rows`".
- **The define side is not an ask.** `mf_define`/`mf_emit` (`mf_result`) and `mf_defined` take
  their rows from the ART's arena, which the art has held since `mf_art_begin`, so no new
  callback. Those rows are valid until that arena dies, as every other define product is.
  [rev 3, F4] The define allocates EXACTLY `proof_n` rows by §1's rule (no caller cap, so R-cap
  cannot fire there), and refuses by R-out and R-short with their messages. Hence an ask and a
  define of the same site AGREE (the deep-compare rule below) whenever the ask's storage holds
  `proof_n`: always at the ceiling, and at the minimum whenever the text keeps the kit's
  promise. A disagreement at the minimum is a promise breach, which is what the ask-vs-define
  tests (`arm_fixtures.c:432`, `g2_win_gen.c:1358`) exist to see; they pass the ceiling only
  where they need agreement on a defective text.
- **The kit's internal producers [rev 3, F4].** Five kit paths make a class or a reply outside
  the two public asks, and each gets storage by one rule:
  - `define_sel` (`compose.c:1176-1209`: a stack `mf_class` filled by `wf_plan_class` or
    `kit_class`, then `r->cls = cls`): its rows come from the art's arena, sized `proof_n`;
  - `kit_legacy_arm` (`compose.c:325-339`: a stack class computed only to test that `kit_class`
    succeeds, then discarded): a kit-internal scratch of the ceiling size, freed before it
    returns. Its verdict does not move: old-field FIND keeps the clip (§1), so `kit_class`
    gains no new refusal;
  - `wdecide_framed` (`window.c:2708`, its `reply_of` at `:2733`): writes into the caller's
    `rows` it was handed;
  - `wf_agree`'s two holders `asked` and `held` (`window.c:2812-2839`; `held.plan_test[i]` is
    written at `:2836-2839`): each gets its own `calloc` plan storage of `nplan` entries, freed
    with `d`. The kit writes through its own non-const pointer; the reply's members stay `const`
    to every reader.
  - `formhash.c`'s `fh_work` (`:410-415`): see (e).
- **The family this joins [rev 3, F17, DOC].** `mf_rows` is the THIRD shape of caller-owned
  output lists in `memfn.h`: (1) an inline fixed-cap struct the caller owns (`mf_finder_listing`,
  `MF_FINDER_MAX` 32; and today's `proven[]`/`plan[]`); (2) a caller buffer plus its size (`char
  *err, size_t n`: `mf_opts_check`, `mf_target_parse`, `mf_family_parse`); (3) caller pointers
  plus caps with a pure need query (`mf_rows`/`mf_rows_need`). The next variable-length reply
  list picks one of these three, never a fourth shape. The general form is (3): `need(site) ->
  caps; ask(..., rows)`, with "outside the count = the list's neutral value" (all ones for proof
  rows). Its unlocks, none built now, each with its trigger:
  - `mf_finder_listing` onto rows+need. TRIGGER: the finder table reaching `MF_FINDER_MAX`;
  - `mf_class.pres[]` as a counted list. TRIGGER: a presence site stating more than
    `MF_MAX_PRES` spans;
  - the run-length proof (below, "Stack and arena") as a second ELEMENT KIND of the same list.
    TRIGGER: `covcost2`'s RSS share;
  - one serializer for every reply. TRIGGER: the first out-of-process kit consumer (the plan as
    a text seam).
- **Principle 9, checked.**
  - The request side carries two NUMBERS (the caps), which the reader can compute from the
    statement with `mf_rows_need`.
  - The reply side carries counted LISTS (`proof_n` rows; `nplan` entries), the same shape as
    today's `mf_walt.spans` and `mf_term.run`.
  - Nothing crosses that a text round trip could not carry: the pointers are where this
    process put the list.
  - Unchanged and out of scope: `mf_art_begin`'s `mf_arena` and `mf_hooks`' callbacks are
    existing seam debt. This change adds none.
- **pcrec's side.**
  - pcrec allocates `rows` from `cx->arena` at each ask: the ceiling for the cover ask
    (`known.c:418`), `mf_rows_need`'s minimum for every other.
  - Callers on main: `emit_dfa.c:7162, :8491, :8905, :11579` and `known.c:418` (`mf_ask`), and
    `emit_dfa.c:7719, :7758, :16325` (`mf_wdecide`). The `memfn_sites.h` prototype comment
    changes too.
  - Kit callers: `compose.c:1103` (`mf_ask`'s definition) and `window.c:2752` (`mf_wdecide`'s
    definition).
  - Tests: `g2_pres_gen.c:747, :760`; `g2_win_gen.c:926, :1015, :1076, :1140, :1271, :1358`;
    `arm_fixtures.c:476, :562, :1455, :2443, :2554, :2812, :2841-2842, :2860, :2870`;
    `d27_frame.c:527`; `proof_check.c:283, :526`; `proven_check.c:251`;
    `run_decide_check.c:207`. A test's reply rows come from the test's OWN storage, never the
    art's arena: `d27_frame.c:1094` (`ask_arena_no_growth`) counts the art arena's blocks
    across asks and would read red otherwise [rev 3, F6].
  - A design probe the link checks compile [rev 3, F7]:
    `docs/design/memfn/span_pick/probe/probe.c:101` (`mf_wdecide`, then `r.plan[i]` /
    `r.plan_term[i]` to `r.nplan`), compiled `-fsyntax-only -Wall -Werror` against
    `memfn/include` by `tests/memfn/run_link_checks.sh:264-275` on every run. It gains the
    `rows` argument in the same build, or the link check reds.
  - Mech rows [rev 3, F7]: S3097 embeds an `mf_wdecide` call in its plant text
    (`SAB_BEFORE`, the `emit_dfa.c:16325` line) and is RE-ANCHORED; S3045 and S3064 name the
    asks only in comments and DESC, so they need a REACH re-read only.
- **abi**: inside `MF_SITE_ABI` 29 -> 30 (below).

### Readers that move [rev 2, F4, F5, F6: found by grep at main ea83fbc01; rev 3, F5, F6: re-counted at origin/main 56c315567]

**The deep-compare rule (F4).** Two classes, or two replies, AGREE iff:
- every by-value member is equal; and
- each counted list has equal counts, and equal elements over that count.
A pointer value is NEVER compared, and nothing is read past a count. Each reader's member table
gains a "counted list" kind (count member, pointer member, element size). Each test keeps its
own compare, so a control never borrows the kit's.

**(a) Whole-struct and `offsetof` byte compares that become deep compares:**
- kit:
  - `compose.c:1261` (MF_TRACE: re-ask class vs held, `memcmp(&q, &r->cls, sizeof q)`; the
    re-ask gets its own heap `rows`, freed after);
  - `window.c:2779-2795` (`wr_members`/`wr_first_diff`) and `:2857` (`wf_agree`);
- pcrec: `emit_dfa.c:7756-7763` (PCREC_CAND_TRACE, `asked-plan-differs`; `again` gets its own
  `rows`);
- tests:
  - `g2_win_gen.c:1275` (`offsetof(mf_wreply, framed)`);
  - `g2_win_gen.c:1358` (whole class: ask vs define) [rev 2: not in r20's list];
  - `arm_fixtures.c:432` (whole class, `full` mode) [rev 2: not in r20's list];
  - `arm_fixtures.c:2355-2380` (`PUR_M`/`pur_diff`), `:2564-2566` (frame part == zero:
    `plan_test` NULL on NONE keeps it zero), `:2585`;
  - `d27_frame.c:485-506` (`g_member_mask`/`frame_part_zero`; NONE's `plan_test` NULL);
  - `d27_frame.c:529` (zero on refusal: holds, since pointers are NULL);
  - `d27_frame.c:1028, :1050, :1052, :1105` (repeated-ask whole compares) [rev 2: not in r20's
    list];
  - `d27_frame.c:1075` (`purity_same_class_text`, two compares), `:1084` (`purity_miss_class`),
    `:1124` (`purity_after_define`), `:1178` (`purity_after_unrelated_define`): whole-reply
    compares, which would read FALSE red once two asks use separate storage [rev 3, F6];
  - `d27_frame.c:1062, :1064` (`offsetof(mf_wreply, framed)`: `plan`/`plan_term` lie before
    `framed`).
- By value, unchanged but padding-free (§1): `emit_dfa.c:1665` and `g2_pres_gen.c:980` (`cls.run`).
- COUNT [rev 3, F6]: 22 compare sites (the 18 above r22 and its 4 added, `d27_frame.c:529`'s
  zero compare included, the by-value `cls.run` pair excluded), by `grep -rnE
  'memcmp\s*\(\s*&'` plus the `offsetof(mf_wreply|mf_class|mf_result|mf_wspan)` grep over
  `src memfn tests` at origin/main.

**(b) Loops bounded by an old constant, which become loops bounded by the count:**
- `compose.c:1267` (`MF_MAX_FWD - MF_PROOF_LO` over `proven`);
- `d27_frame.c:721, :726-729, :813` and `g2_win_gen.c:826-827` (`MF_WPLAN_MAX` past `nplan`:
  the "past nplan is NONE" checks RETIRE, because a counted list has no past);
- `proof_check.c:744` (`MF_MAX_FWD - MF_PROOF_LO`);
- `gate.c:627` (`j < MF_WSPAN_POS`, a clamp: still true);
- `known.c:649` (B5: pcrec's, cover_cap.md §11.1);
- the kit's working-state loops over `WF_NPOS`, which become loops over the decision's extent:
  `window.c:281, :318, :397, :707, :901, :1017, :1025, :1221, :1412`.

**(c) Readers of `proven[]` (F5), respelled to `proof`/`proof_n`:**
- kit:
  - `compose.c:395` and `:1088` (the two `memset(out->proven, 0xFF, sizeof ...)`: become
    "rows `[0, proof_n)` all ones");
  - `compose.c:406, :410-411` (`term_prove`);
  - `compose.c:1269-1276` (the trace copies check);
  - `window.c:3848, :3853-3857` (`wf_plan_class`).
  Inside the kit the writer holds a non-const pointer to the caller's or the art's storage;
  the struct's member is `const` to every reader.
- pcrec: `known.c:655` (B5).
- classes that prove nothing [rev 3, F5 (4)]: the PRESENCE ask (`compose.c:1086-1092`, "every
  proof all ones"), a NONE-form class (the MF_TRACE check `compose.c:1266-1271` loops the whole
  range for it today), a non-FIND class, and the zeroed refusal: each has `proof_n` 0 and
  `proof` NULL, and every loop above runs zero times on it.
- tests:
  - `proof_check.c:404` (the want `{ MF_MAX_FWD - 1, "ALL" }`: becomes "the last row in the
    range"), `:409-419`, `:729, :735` (the LAYER-INVARIANT compare: a deep compare over
    `proof_n`), `:744-746` (the generator dumps `proof_n` rows);
  - `proof_meta.h:13, :42` (`proven[PM_NPROOF]` becomes a count plus rows) and
    `proof_run.c:147, :205-210, :354-366`;
  - `g2_win.h:84`, `g2_win_run.c:188-193`, `g2_win_gen.c:1435-1436` (`G2W_NPROOF` becomes the
    site's `proof_n`).

**(d) Plants whose text moves (F5):**
- mech S1224 (`SAB_AFTER` writes `out->proven[0 - MF_PROOF_LO][0] &= 0xFE`: respelled to the
  kit's writable row pointer) and its twin `tests/memfn/run_proof.sh:45`;
- mech S1083 (`SAB_BEFORE` is the `memcpy(out->proven_prev, out->proven[-1 - MF_PROOF_LO], ...)`
  line, which is respelled);
- kit S1407 (`memfn/tests/run_g2_win.sh:155`, the `out->proven[d - MF_PROOF_LO][x] &=` line in
  `wf_plan_class`);
- S1221's anchor (`compose.c:379`) stays, but its REACH is re-read;
- S526 (§2) and S1131 (A1's).
Each re-anchored row's REACH is re-run (`REACH_ONLY=1`) in the build.

**(e) The host-storage rule for `mf_wspan` writers (F6).**
- The statement's `set` and `table_ref` point at storage the WRITER owns, `len` entries each.
- pcrec's writer `pcrec_memfn_wspan` (`memfn_sites.c:540-549`) gains the `Ctx` and allocates
  that storage from `cx->arena`. The `pcrec_memfn_wpos_*` writers (`:557-580`) store through
  the writer's own non-const pointer. The member stays `const`, so a writer that writes
  through it fails to COMPILE, which is loud.
- This path serves EVERY window site pcrec states (pre-check run spans, reseed alternatives,
  the cover), and it is not A1's.
- Test writers of the same shape are found the same way (compile errors), in
  `d27_frame.c:299-311, :344-345, :361, :1267-1268`, `arm_fixtures.c:324-327, :2228-2232`,
  `run_decide_check.c:136-139, :182-186`, `g2_pres_gen.c:509-513` and
  `g2_win_gen.c:612-616, :875-879` (with its local arrays `:126-127`).
- A KIT-INTERNAL writer [rev 3, F5 (1)]: `memfn/src/formhash.c`'s `fh_work` (`:410-415`, calloc'd
  at `:437`) holds an inline `mf_wspan sp`, written at `:496-502` (`fh_set` into `sp.set[0]`)
  and after, and an `mf_result res` whose rows now live in the scratch art's arena. `fh_work`
  gains `set`/`table_ref` arrays sized by the span's `len`. It is kit code (the form-hash
  renderer that measurement-set staleness reads), not a test.
- Reply HOLDERS sized by a fixed bound [rev 3, F6]: G2's own `g2w_reply`
  (`memfn/tests/g2/g2_win.h:46-61`, `plan`/`plan_term`/`plan_test[G2W_NOFF]`) is filled by copies
  bounded by the kit's `nplan` (`g2_win_gen.c:1145`, `:1290`); it grows with `G2W_REACH` (§3
  "Answers"), and the long rows get storage sized by their `nplan`.

**(f) Casts that truncate SILENTLY after the widening (F6).** Each is respelled to the widened
type, or declined above the row's contract:
- pcrec: `memfn_sites.c:544, :548, :553, :554` (`len`, `core_len`, `core_lo`, `core_len`);
- kit:
  - `window.c:1303` (`nplan`), `:1313` (`run_len`), `:3017` (`t->run_len = (uint8_t)(b - a)`:
    `mf_term.run_len` is already `uint32_t`, so this truncates TODAY past 255);
  - `presence.c:187, :208, :209, :241, :242, :261, :262` (`ver_lo`, `ver_len`, `scan`).
That is 14 lines. A surviving cast turns a 4095-position statement into 255 positions with no
warning, and a non-cover site has no B5 to catch it. The test casts on `len`/`core_*` sit in the
(e) list's lines and widen with them.

**(g) The mfind caveat (`memfn.h:1604-1615`, main only).** Under the `mfind` lever, the frame
reply is not updated: it still reports search NONE and stream RESTART. The caveat carries into
the new `mf_wreply` comment unchanged.

**(h) Doc readers of the changed names** (design tier; stale sentences, not contract breaks; found
by `git grep`). They are updated in the build or flagged in its report:
- `memfn/include/CLAUDE.md`;
- `docs/design/kit_proof.md` (§4.2's fixed range);
- `docs/design/memfn/window_site.md` (§1.1), `window_contract.md`, `plan_frame.md`
  (`MF_WPLAN_MAX`), `part_d.md`, `span_runs_sheet.md`;
- `docs/design/ctx_span.md`, `span_arms.md`, `run_pos_set_stage3_readiness.md`,
  `stream/approach.md`;
- `docs/dev/kvcensus.md`.
`docs/spec/` has none. `memfn.h`'s own comments (`:147-148`, `:297-316`, `:650-667`,
`:1320-1340`) are the contract text and move with the code.

### Stack and arena (pcrec's holders) [rev 2, F19; rev 3, F2, F4]

- **The 8 by-value `mf_class` stack holders** (7 CandScan locals in every build, plus 1 in the
  PCREC_CAND_TRACE build) take 13,120 B, down from 23,456 B.
- **The `mf_wreply` holders** are about 12: `UnanchStart.wr` (`emit_dfa.c:4670`), where
  `UnanchStart` is a stack local at about 10 sites plus the copy `rus = us`, and the locals at
  `:7757` and `:16318`. Each shrinks by 396 B.
  - A by-value copy shares the rows. Every holder lives within one compile's `cx->arena`, so no
    holder outlives its rows.
- **Arena** [rev 3, F2, F4: the cover ask's ceiling storage and the define's rows added]. pcrec's
  art arena IS `cx->arena` (`memfn_sites.c:187-189`), so it carries three kinds of rows:
  - ASK rows: `proof_n x 32` B per class ask at `mf_rows_need`'s minimum, EXCEPT the cover ask,
    which takes the ceiling, 4,104 x 32 = 131,328 B at EVERY `k`; plus 7 B per plan entry per
    window ask (28,728 B at 4095);
  - DEFINE rows: `proof_n x 32` B per define of a proving class (1,312-1,344 B at `k` = 32;
    131,328 B at 4095), 0 for a non-proving class (so the 5000-byte VM run compare adds none);
  - the statement's host arrays (§5 (e)): 36 B per position, 147,420 B at 4095.
  - Per compile attempt of a cover, that is about 291 KB of rows at `k` = 4095 (131,328 ask +
    131,328 define + 28,728 plan), and about 133 KB at `k` = 32 (131,328 ask + about 1,600
    define and plan), against today's class held inline (a 3,000 B `mf_result`). The short-cover
    growth is the price of the ceiling storage (r22 F2 (i)); it is main's to confirm (§7).
  - `cx->arena` is freed at Ctx teardown (`compile.c:332`), so these accumulate PER COMPILE,
    SUMMED OVER the size-ladder attempts.
- **For comparison**, an inline layout at 4095 would make the class 132,948 B: 8 x that is
  1.06 MB on the stack, against the 442,368 B budget. A by-value layout is not viable.
- **A sparse or run-length proof is designed, not built.**
  - It would list `(lo, len, set)` runs: about 40 B for a run of one class, and 9 runs for a
    uuid.
  - Its worst case is no better than dense: a 4095-position literal of alternating bytes is
    4095 runs.
  - TRIGGER: pcrec's stage-2 compile-cost record (cover_cap.md §11.1, `covcost2` on `a{4095}`
    and `[0-9a-f]{1000}`) shows the rows' share of max RSS is material. D77.

### The kit's own working state (internal, no seam event; most of the build)

- Every array sized by `WF_NPOS` / `MF_WPLAN_MAX` becomes sized by the alternative's stated
  extent, allocated per decision:
  - `wf_alt.p[]` (`window.c:183`);
  - `wf_dec.poff[]`/`pterm[]` (`:219-220`);
  - `struct wf_plan`'s `off`/`set`/`core`/`table`/`grp` (`:1323-1354`), and `offs` (`:1385`);
  - `wf_fpart.plan_test` (`:2556`);
  - the stack `int key[WF_NPOS]` in `find_groups` (`:1775`).
- They are allocated through the existing paths: the art arena at `:2475`, and `calloc` at
  `:2768` and `:2816`. This unit rides WITH or BEFORE the carrier: `WF_NPOS` derives from
  `MF_WPLAN_MAX`, so the carrier alone would make `wf_dec` about 644 KB per decision.
- **Why per extent.** Merely raising the constants would make `wf_dec` about 644 KB
  (`wf_pos` 76 B x 4,104 x 2 alternatives, plus the plan arrays), calloc'd and zeroed on EVERY
  window decision, short sites included. It would also make `find_groups`' stack array
  16,416 B, against the 4 KB bar.
- `wf_legacy` keeps `WF_LEGACY_POS` (§1).
- No new frame over 4 KB. `run_link_checks.sh` holds that, and the peak line in
  `memfn/CLAUDE.md` is re-read at the build.

### abi events

- **`MF_SITE_ABI` 29 -> 30**, which carries:
  - `mf_wspan`'s and `mf_wreply`'s layouts;
  - `mf_rows`, `mf_rows_need`, and the new parameter of `mf_ask` and `mf_wdecide` [rev 2, F3];
  - the new values of `MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD` and `MF_WPLAN_MAX`;
  - the retirement of `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD`;
  - `MF_WMAX_SPAN`'s own spelling.
  No reader pins 29 outside `memfn.h` (r20 PROBED-AND-HELD).
- **`MF_CLASS_V` 10 -> 11**, inside it: `proven[]` replaced by `proof_n`/`proof`, and
  `mf_run_reply` widened.
- **`MF_VOCAB` unchanged**: no op, handoff or term kind.
- **pcrec's `abi`.** The JOINT landing is ONE pcrec `abi` event, because pcrec's own stage 2
  moves emitted text (cover_cap.md §11.1 "abi events").
  - Under plan A (RULED), H(h\*) moves a window site's bytes only where the site is a
    possible mover at h\* (§3 "Which sites move": covers and non-cover window sites alike),
    which under the largest-head tie-break happens only on a measured win beyond the noise
    (§3), in the same commit: a kit byte move is a pcrec abi event (`memfn/CLAUDE.md`).
    Literal covers never move. The owner ruled keep-short-spans = NO, so spans of 32 or fewer
    are not exempt [rev 5].
  - Under plan A's fallback (forms built but off) and under plan B, no kit byte moves at
    today's widths; switching the forms on later is a second pcrec abi event.
  - The head lever and the option row's force read add no layout: they ride in the same
    commits, and no reader pins a lever name's count [rev 3, F12, F15].
- **Stamps.** L and H at SIMD-off are scalar forms, so `<PREFIX>_MEMFN_FORMS` reads `none` at
  SIMD-off as today (integration.md §18.1). A SIMD-on loop is a carried level like any vrun
  row.

## 6. The three standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: relevant.**
   - The cards of §3 name theirs: throughput on Linux, `taskset`-pinned, six subject regimes
     (cover_cap.md §11.4's five, NOT-WARM and `short-subject-search` included, by §11.4's
     methods, plus uniform random bytes) [rev 5, Q4/C6], both layers, gcc 15.2, on the kit's
     harness (§3 "The procedure").
   - A choice must hold in every regime its site can be in (K-1). That is why R1 takes the
     WORST cell over all regimes of C1-C2, and why near-miss is a column of every card and
     never a separate study. Since rev 5 R1's regimes include every regime §11.4's width rule
     reads, so a regime flips h before it can flip the width default (§3 "Why each choice").
   - Every number in this draft is a `sizeof`, a cited fact, or a labelled extrapolation. None
     is a timing.
2. **Independent control: relevant.**
   - **The forms' answers** are checked by G2 against the byte loop over a GENERATED span
     space whose lengths come from the DRAWS, not the twins [rev 3, F8]: the REPORT family at
     `1 .. 128`, a repeated-class shape straddling every finite grid h, straddle draws at heads
     16-64 in every other family [rev 4, R3-7], and 500 and 4095 as their own rows; G2-win's
     counted line per family and grid h fails at zero (K35). They are also
     checked by pcrec's answer-identity sweep with the force cell, against libpcre2 (§3 "The
     option"). Neither reads the kit's plan.
   - **The proof** is checked by pcrec's B5, against its OWN statement and `k`, and the cover
     ask's ceiling storage puts every over-read in B5's view [rev 3, F2]. The kit's R-short is
     the kit checking its own computation, and so shares a source with `proof_n`. That is why
     the pcrec row (b) of §1 bypasses it and expects B5's text on an after-unstated cover, while
     the kit row (a) only witnesses that R-short exists [rev 3, F1].
   - **The head** is tied to the shipped bytes by the lever's identity check (§3) [rev 3, F12],
     over every predicted mover at h\* as well as the cards and census covers [rev 6, R5-4].
   - **The movers** are predicted from pcrec's own statements (the new `MFWSTMT` record, §3
     "Which sites move"), never from the kit's plan; the sweep reds on a move outside the
     prediction [rev 6, R5-1, R5-5].
   - **The void step** shares no source with the timings: it reads only whether a cell has a
     reading, and a void cell never helps a head (§3 R1 step (5)) [rev 6, R5-2].
   - **Timing** is checked by pcrec's G1 (`no-span-loop`) and by the engine-route reference C5.
   - **Populations are counted.** G2's long rows are named rows; G2-win's per-family, per-h
     line counts the looped sites. The force cell's population is the whole corpus.
3. **What moves when data is regenerated: relevant if R3 fires.** The forms read no measured
   data. h is a MEASURED constant with its card ids. If R3 shows the death-depth reading, h
   becomes a derivation from the art's byte rate, which is pcrec's analysis object and already
   an input. A rate change could then move a kit byte, which is an abi event (integration.md
   §21.3). The build's card says so.

## 7. The questions, all RULED (2026-11-16) [rev 5; was "Open questions"]

Each keeps its bold plain-word slug, reused verbatim in §8 [rev 3, F16 (b)]. Rev 4's
recommendations were all taken; the record below says what each ruling settles.

**Main's five answers, each YES (main, 2026-11-16):**
- **other-sites-at-32**: RULED yes. pcrec keeps its other window sites at 32 positions and
  reach 64 by its own assertions: one `_Static_assert` per construction bound it owns
  (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`) at its own writers, not a site kind in
  `window_bounds_check`, which also replaces the now-loose `emit_dfa.c:1446`. It keeps pcrec's
  STATEMENTS at 32; it does not keep the kit's FORMS off those sites, which render H(h\*) like
  every span (§3 "Which sites move") [rev 5, C1]. Naming a pcrec bound for reach 64 is main's
  (r45read C2).
- **cover-ask-storage**: RULED yes. The cover ask passes 4,104 rows (about 131 KB per compile
  attempt at every width), so every over-read below 4096 reaches B5. The one edge (r23 R3-8 (b)):
  at `k` = 4095 with the after side stated, an over-read at 4096 is a bare refusal, a lost cover,
  never a wrong answer.
- **caller-storage**: RULED yes. The asks take caller storage; the cover ask passes the ceiling,
  the other asks `mf_rows_need`'s minimum.
- **row-memory**: RULED yes, until stage 2's compile-cost record (`covcost2`) says otherwise:
  about 291 KB of rows per attempt at 4095 (the statement's host arrays, 147,420 B, come on top,
  about 438 KB in all; r45read answer 4), about 133 KB at 32, summed over the size-ladder
  attempts.
- **night-order-edits**: RULED yes, unconditionally (forms now). The edits are §3's list; rev 5
  adds the regimes sentence (Q4), the (4a)/(4b) split (C11) and the prediction edit (C1).

**The owner's three (Frank, 2026-11-16, via main):**
- **forms-now-or-next**: RULED forms now, in one joint landing. What it means in the predicted
  outcome [rev 5, C5]: on a measured tie (drill (i)), h\* = 64, CHOSEN, so the landing ships
  today's bytes for every span of 64 or fewer positions and loops only past 64; the owner's
  default reaches the new long covers, and a shorter head ships only on a measured win. If the
  cards cannot run before the landing, main decides that with Frank, and the forms land built
  but OFF (all-inline), switched on in a later abi event (cover_cap.md §11.6.1's FALLBACK fires
  it too).
- **keep-short-spans**: RULED no. One measured rule at every length: spans of 32 or fewer move
  on a measured win, covers and non-cover window sites alike (§3 "Which sites move").
- **near-miss-fix-later**: RULED no fix in the first build until a timed card shows the loss
  (D77; §4). The option's documentation names dense near-miss text as the slow case. Its
  polarity, spelled out [rev 7, r35 F25]: the ruled answer is "the near-miss fix comes LATER, on
  a trigger, not in this build"; the slug's "no" answered "a fix in the first build?", so read
  the slug as "fix later: yes".
- **Their record [rev 7, r35 F25].** Main relayed them in `memfn/docs/requests.md` R-45,
  "RULINGS ON THE REPLY (2026-11-16, pcrec manager ...)": "Owner (Frank 2026-11-16, "agree with
  your leans on all three", the leans being the kit's own): forms-now-or-next = FORMS NOW, in the
  one joint landing; keep-short-spans = NO; near-miss-fix-later = NO fix in the first build until
  a timed card shows it." Main's journal (`docs/dev/dev_journal.md` on main at b1bcee85b, the "KIT R-45" entry) carries
  the same words: "Frank: "agree with your leans on all three" (forms now; no short-span exception;
  no near-miss fix in the first build)". A decisions.md row (or a D198 addendum) carrying them
  verbatim with the h = 64 interim (§3 "Scope") is main's (r35 F25, F21).

**The kit manager's:**
- **dominance-cycle**: RULED (2026-11-16): step (3) keeps the members of E
  dominated (faster beyond `f` in at least one cell and never slower beyond `f`) by the fewest others (§3 R1) [rev 5, Q2; rev 6, R5-6].

**Left with main (facts, not questions for the owner):**
- Whether step (4b), h\* compiled in and the identity check, takes a review of its own before
  the width night: it is a commit the code round (4) did not see (r45read C11).
- The cover_cap.md edits r45read lists beyond the reply's own (E6-E14: B4, B5's plant and
  §11.6.3's rows, §11.2's near-miss order, §11.3's sentence, §11.7 Q2/Q4).
- **A main-side BUILD item [rev 6, R5-5]:** the `MFWSTMT` trace record (fields in §3 "Which
  sites move"), the predictor reading it, and a trace-build pass in the stage-2 sweep. The
  sweep's prediction and the identity check's population (R5-4) both need it, so it lands
  before the cards' identity check runs.
- **A bench-only question, only if the regimes fallback fires [rev 6, R5-3]:** whether the
  bench can time its regime's card cells through the test-only `--harness=span-head=N` (§3
  "The regimes' methods").
- r45read Q1 (who respells pcrec's callers and tests on the kit's build branch) was outside rev
  5's brief and is not answered here.

**Answered earlier, no longer asked:**
- **When `MF_MAX_SPAN_POS` retires.** Now: A1 is delivered on `lane/covs2afix`, and the kit
  branch merges only onto A1.
- **The order of the timings** (ruling R1, AGREED WITH MAIN 2026-11-16, CONFIRMED with step 3's
  refinement [rev 5, Q5]). The form cards run first on the frozen combined-branch binary, h
  set through the lever, with h's rule committed before the run; h is frozen by that reading;
  h\* is compiled in and the identity check passes; then the width cells are measured on that
  REBUILT binary, never on the cards' binary: one night if both fit, the width cells
  not-before the cards' verdict; otherwise two nights (§3).
- **May the default itself be all-inline?** No, by the kit manager's ruling on r22: all-inline
  is the dial's option, never the rule's default; making it the default is the owner's own call.

## 8. responses.md-ready block (for the kit manager to post; facts only, D157)

```
## R-45 reply (2026-11-16, kit; rev 6 after reviews r20, r22, r23, r25 and your check r45read; rev 7 2026-11-17 after code round r35; rev 8 after its re-check r36; rev 9 after r37) — window spans up to 4095 positions
- READY; nothing open. Plan A (forms now, one joint landing) is the plan of record.
- (1) YES on EVERY window span: MF_WSPAN_POS 4095; MF_WREACH = MF_MAX_FWD = 4096. Proof rows
  only for proving classes (window plan, old-field FIND); others proof_n 0. Range [LO, end),
  end = max(last stated position + 2, last tested offset + 1). Kit refusals: tested offset out
  of range; rows past caller storage; range self-check (message via mf_define only).
  Your cover ask passes storage to the ceiling (4,104 rows): every over-read below 4096 reaches
  B5. Witnesses: a kit row (self-check by message); a pcrec row on [0-9a-f]{32}, nothing after,
  R-short removed (a cover at width 32, after side unstated; its REACH asserts both).
- (2) Decoupled: MF_MAX_TERM 32, MF_WMAX_SPAN 32 stay; MF_MAX_SPAN_POS/MF_MAX_AHEAD retire now
  (merge only onto A1). S526 stays on MF_MAX_TERM; B2's control is your §11.6.3 build.
- (3) Forms I/L/H(h) over the existing segmenter, at EVERY window span; literals stay one
  compare. Default H(h*), h* from FINITE heads: W(h) = worst C1-C2 cell of t(H(h))/t(I) in
  every regime (your §11.4 five by its methods + random bytes), t(I) the median over every arm
  whose built artifact is I's in that cell (rev 8); E = within the floor of the best W (rev 7:
  the A/A floor sized to the rule's comparison count; rev 8: each (regime, layer) at least its
  own launch noise; rev 9: and its own between-run noise, read from the arms already timed whose
  artifact is I's; a cell whose such arms disagree beyond f is void and re-run; a false pick
  <= 5 % of pure-noise nights, uneven and between-run noise included); keep the
  members of E dominated (faster beyond f in at least one cell and never slower beyond f) by
  the fewest others (RULED); then the LARGEST of those that beat I beyond f somewhere (rev 8).
  On a tie h* = 64, CHOSEN. A
  loss in any regime moves h, never your width default. Any C1-C2 cell void twice: h* = the
  largest head that passed R0 (64 when it passed), the read cells' pick recorded (a void never
  helps a head); the kit's approximations of NOT-WARM and short-subject-search are void by
  method until the bench's methods arrive (rev 7). Possible movers: every window
  alternative (covers, pre-check runs, reseed/prefix) with >= 2 consecutive offsets of one
  identical multi-member set (the per-offset meet, ACROSS span boundaries) whose last offset
  is >= h*. Witness: \w{32}\B (its after side continues \w to offset 32; in this build it moves
  at h* <= 29 and is byte-equal to the deny at 30-32, rev 8). At width 32, h* = 64 moves
  nothing; h* = 32 moves at most that kin. Predict from a NEW trace record of your own
  statements (MFWSTMT, your build; a superset; red = a move outside it). uuid: a width event.
  Test-only lever span-head=N (bench reads it only if a regime must run there); identity
  check over every predicted mover + cards + census covers. Option span-loop (pair; deny wins;
  the deny is the G1 arm, not the dial); memfn floor 13 -> 14. Night order (ruled): cards first via the lever; h*
  compiled in + identity check; then your width cells on that REBUILT binary. Your cover_cap
  edits: §11.4 (+ regimes), §11.6.1 (4a cards, 4b rebuild + identity; whether 4b gets its own
  review is yours), §11.6.4, §11.1 prediction + the MFWSTMT record.
- (4) Dense near miss is O(n*k) (16.5 tests/byte at k=32). No fix in the first build. The
  forms are not a near-miss fix (every form restarts one byte later).
- (5) Arrays leave the seam structs: mf_wspan 1,164 -> 32 B, mf_class 2,932 -> 1,640 B,
  mf_wreply 532 -> 136 B. Lists go into caller storage sized by mf_rows_need. 22 byte compares
  become deep compares; 14 uint8_t casts widen. MF_SITE_ABI 29 -> 30, MF_CLASS_V 10 -> 11.
  Rows per cover attempt: ~291 KB at 4095, ~133 KB at 32. The build starts from main.
- Rulings recorded: yours, YES on other-sites-at-32, cover-ask-storage, caller-storage,
  row-memory, night-order-edits (unconditional). The owner's: forms-now-or-next = forms now;
  keep-short-spans = no; near-miss-fix-later = no. Ours: dominance-cycle as above.
```
