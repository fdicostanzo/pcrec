# Lane inlinecrev1 — report: docs/design/inline_c.md rev 1

Lane: inlinecrev1 (opus), branch `lane/inlinecrev1` from main `86a0fed00`.
Task: rev 1 of the [INLINE-C] pattern-side design from review
`docs/dev/reviews/2026-10-26-r1-inline-c-design.md` (its MANAGER RULINGS bind)
and Frank's six rulings of 2026-10-26 on the plan row (cited in the note as
FR1-FR6; renamed from "F1-F6" because D36/D38 already use F5, F7 and F9).
Design only: nothing under `src/`, `tests/` or `docs/spec/` touched; no make;
one `build/pcrec --help` read to check the CLI mode list.

Files changed: `docs/design/inline_c.md` (rev 1, with a REVISION 1 block at the
top; changed text marked `[r1 <id>]`), `docs/design/CLAUDE.md` (the note's
index line), this report.

## Disposition by id

Every accepted finding is APPLIED; no objection to any ruling was needed.

| id | disposition | where in rev 1 |
|---|---|---|
| A1 | applied as SUPERSEDED by FR1: no reference flags define the answer; the `(?s).*` start-veto case is a named stage-1b shape; the NO_* survey now serves only the PCRE2-sensitivity filter | §1.7, goal 2, §9.1 stage 1b, §9.2 |
| A2 | applied: `ncap` = group count + 1 at every site; both probe shapes in stage 1b | §1.2, §1.3, §7 porting table, §9.1 |
| A3 | applied: `NFA_ERASED_CALLOUT`, a callout prefilter proves a start never an end; the FINISH row's own exactness on R; fallback with no window ceiling; sabotage S-IC33/S-IC34 | §1.8, §4.2, §9.1 stage 4 |
| A4 | applied: save / store / call / restore slot 0; `a\Kb(?C"see")c` + S-IC5; manual-vs-binary sentence | §1.2 step 3, §1.3, §7 |
| A5 | applied: A_CALLOUT `refs` unioned by `pcrec_bref_mark` (keep + publish); applicability row 4 reads the site's fact; `--no-captures` cases; S-IC25 | §1.1, §1.3, §4.3, §9.1 |
| A6 | applied: the FINISH row's scan is R with the tail REMOVED; §4.4 states the premise; S-IC35 | §4.2, §4.4, §9.1 stage 4 |
| A7 | applied: `RX_G_<name>` constant for unique ASCII names, run-walk for `(?J)` duplicates, none for non-ASCII or dotted | §3.2 |
| A8 | applied: includes after the matcher, an `#undef` block for internal macros, live-macro check over a corpus | §3.1, §3.2, §3.3 |
| A9 | applied: rows 9-10 apply to `ret >= 0`; emitted order and the `(size_t)` cast given | §1.6 |
| T1 | applied: GRANT column (`invoker-only`), outside `all`/named sets/every features text; `_CODE_LANGS` disclosure; refusal tests per door; S-IC28 | §5.1, §2.4, goal 1, §9.1 stage 2 |
| T2 | applied: the harness passes the opt-in only for entry-file blocks; from stage 3 fragment blocks with code compile through pcrec's FILE path; S-IC29 | §5.2, §5.7 |
| T3 | applied: `ext harness link` withdrawn; a test-owned harness manifest in `tests/callouts/`; `rxt_format.md` §1.12 unchanged | §3.6 |
| T4 | applied: ASCII-promise spec hunk; `--list-callouts` escapes and flags; bidi/format characters in segments REFUSED by default (the manager's call per the review; leaning applied, no opt-in until a need) | §2.4, §5.6, §8.2 stage 2 |
| T5 | applied: entry-point table derived from the CLI mode list (checked against `--help`: `--trace` writes C; `--explain`/`--probe-ask` take a construct) | §5.9, goal 1 |
| T6 | applied (narrowed form): the manifest carries opt-in + stubs into test-axes; counted floor of built-and-linked cases per axis | §3.6, goal 2(c) |
| T7 | applied (DOC): every chain must be pinned (order-independent); hash the parsed buffer, one read | §5.4, §5.5 |
| D1 | applied per ruling: `check-tail`, a FINISH row on `CR_VM` (veto → FIN3 `AT`, none → FIN4); compound U6 filed as end state; 10a conflict 4 gains reading (c) | §4.2, §4.6, §10a.4 |
| D2 | applied: one emitter, binding row × view source (`vm-slots` / `finish-hand`), caller edges; witnesses reach both callers | §1.2, §4.2 |
| D3 | applied per ruling: §1.8 rewritten as the per-kind attribute row (`text_width`, `path`, `reads`; A_LOOK/A_VAR analogs); stage split 1a/1b; one sabotage row per pass family (S-IC21..24 at 1a, S-IC3b/6b/25/33 at 1b/4) | §1.8, §9.1 |
| D4 | applied: `PF_KIND_CALLOUT`; RETIRE the callout half of conjunct (g) and the start-set seek with the superset + FR1 argument; S475/S496 re-scoped to verbs; ir_listing flip. Decline is offered as the manager's alternative | §1.8 |
| D5 | applied: `callsite_rows[]` is the one table, lifted to the shared emit layer with a `conv` column (part / matchfn); zero-mover check on the compound | §1.6 |
| D6 | applied (PLAN + FIX-NOW): stage 0, its own abi event before 1b; §8.1 states it | §1.6, §8.1, §9.1, §9.4 |
| D7 | applied: ownership rows (second `(?C` row per language with a `recognise` hook; `(?{` rows) generated from the language table | §1.1, §2.4 |
| D8 | applied: a callee's give-up does not escalate the outer tier (local bit); §10.9¶6/§4¶3 wording hunk; FRAMES test | §1.6, §8.2 |
| D9 | applied per ruling + FR4: per-fire step lands at 1b with no carrier; a pcrec callee charging the caller's meter needs `rx_ctx.session` ([IFACE-PUSH]); interim fresh-budget-per-fire row is explicitly TEMPORARY, bounded (fires ≤ outer budget) | §1.11, §10a.8 |
| D10 | applied as SUPERSEDED by FR1: the addendum does not decide it (PCRE2 has no single documented answer) | §1.7 |
| D11 | applied per ruling: stage 3 SCHEDULED; §1.9 rows split (3a stays refused, 3b/4 lifted at stage 3 with the definition's own view); `sha256 <hex64>` reused; §1.6¶8 hunk; the ONE SHA-256 moves to a leaf `shared/sha256.{c,h}` compiled into both binaries (alternative: libpcrec compiles `analyze/sha256.c`) | §1.9, §5.3-§5.5, §9.1 stage 3 |
| D12 | applied per ruling: stage 4 designed, briefed after a census of eligible shapes; UC-1b' the row's case, UC-1b the downgrade case | §4.6, §9.1 stage 4, §9.3 |
| D13 | applied: goal 3(b) inline twin, 3(c) verify twins + margin (5%, labelled UNMEASURED) + A/A source + consequence; stage-2 card uses the `--engine=vm` twin with counted fires and names its one decision; goal 2 floor (1,000 generated + named shapes) | goals, standing question 1 |
| D14 | applied: remodel-overlap table (wait/ride/none); deny-only axis; bit count (7 free, 6 after stage 4); abi-event list | §4.5, §8.1, §9.4 |
| D15 | applied: spec hunks found by grep, by stage; IR `callouts` section as the one row source | §5.6, §8.2 |
| D16 | applied: callout-artifact fixed-literal family (`RX_PASS`, `RX_FAIL`, `RX_CALLOUT_PCRE2`), home under `-o -`, `__` refused in binding names | §1.4, §1.5, §7, §8.1 |
| D17 | applied: malformed-`(?C` row + tests; PLAN: an independent parser fix filed | §2.4, §9.4 |
| D18 | applied: `#line` before every decoded `pattern-esc` line, no padding where columns cannot be right; goal 4 narrowed to the line | §3.1, §3.4, goal 4 |
| D19 | applied: unbound binding = link error (spec sentence), `--emit-main` refuses binding sites; PLAN: bench `[inbox]` note at 1b | §1.4, §9.4 |
| D20 | applied (PLAN): stage 2 lands on today's by-name shape; SCOPE row filed; GRANT is its first use | §5.1, §9.4 |
| D21 | applied (DOC): [POSTFACT], [BREF-SPAN], [MATCH-EVENTS] cited with what each decides | §9.4 |
| PREM-16a | applied | §1.6 cost paragraph |
| PREM-16c | applied | §5.5 |
| PREM-16f | applied | §3.1 |
| CON-15 | applied: statement expressions, slot-0 accessor rule, example tests `RX_CAP_SET` first | §3.1, §3.2 |
| CON-18 | applied | §6 |
| CON-19 / SLOT-18a | applied: `_CALLOUT_VERIFY` tokens are behaviour names (`checked-after-match`, `checked-inline:<reason>`); `_CODE` → `_CODE_LANGS` | §4.3, §5.1 |
| SLOT-18b | applied: `<PREFIX>_CALLOUT_BINDINGS` stamp (rx_info member stays [IFACE-PUSH]'s) | §1.4, §8.1 |
| SLOT-18c | applied: listed as 10a conflict 9 with the reason | §5.1, §10a.9 |
| SLOT-18d | applied: `PCREC_ERR_ABORT` −17 reserved in stage 1b's spec hunk | §7, §8.2 |
| SLOT-18e | applied | §2.1 |
| SIM-6 | applied | §1.3, §7 |
| FR1 | applied (see A1/D10); one READING flagged: libpcre2 kept as a filtered cross-check | §1.7, §9.2, §10a.11 |
| FR2 | applied: every callout `W_PRED` by default | §1.1, §1.5 |
| FR3 | applied: read-only context stated | §1.3, §3.5 |
| FR4 | applied (see D9) | §1.11 |
| FR5 | applied: one attribute grammar (`consume`, `once`, `verify`) for every binding row; numbered via a `callout N attrs` head line / `--callout`; library form waits for [IFACE-PUSH] | §1.4, §2.2, §6 |
| FR6 | applied: firing-class derivation (repeat; live choice point before the site, sealed by atomic/possessive/lookaround; tail) with an example table; `once` checked with a reason and a fix; class bound per attempt within one run (§10.9 replay stated); `verify`'s veto edge honours it (FIN4 for class 1-2); counting-binding control; S-IC19/S-IC27 | §1.10, §4.2, §5.6 |

## The revised stage plan

| stage | what | abi event | gate |
|---|---|---|---|
| 0 | the shared block's `rx_matchfn` INTERNAL comment says "propagates" | yes (every artifact, one line) | identity gate moves exactly that line |
| 1a | per-kind attribute row over today's kinds ([DEC-KINDATTR] + [POSS-CTX-TABLE] kind-level rows) | no | zero movers: `--emit-facts`, possessify marked/total, emit_sweep identity |
| 1b | the call site, extern-bound: node, one emitter, view, shared return table, firing classes + `once`, budget step, attribute grammar | yes (stage 5 may ride) | backtracker + filtered libpcre2 legs, test-axes floor, zero movers beyond the abi line |
| 2 | embedded C, local-only gate, GRANT column, harness provenance rule | yes | entry-point table tests, scanner table, UC-1a/UC-3 |
| 3 | pins + one SHA-256 + §1.9 rows 3b/4 lifted + `--list-callouts` (SCHEDULED) | only if it adds contract text | NIST/sha256sum, chain tests, definition-site view |
| 4 | `verify` as the FINISH row `check-tail` (designed; briefed after the census) | yes | test-axes deny flag, goal 3c card |
| 5 | PCRE2-convention wrapper | rides 1b | native vs wrapped equal |

Order: 0 and 1a before 1b; 1b → 2 → 3; 4 after 2 and its census; 5 with 1b.
Filed (PLAN) items for the manager: stage 0; the malformed-`(?C` parser fix
(lands on its own); the bench `[inbox]` note at 1b; the per-option SCOPE row.

## Manager choices left open in the note (each with the note's leaning)

- D4: retire (leaning) vs decline the callout half of the two conjuncts.
- D11: the SHA-256 leaf directory's name (`shared/`) vs libpcrec compiling
  `analyze/sha256.c` directly; a second copy is not proposed.
- 1a's scope: possessify's context record stays filed under [POSS-CTX-TABLE]
  (leaning) vs folded into 1a.
- FR1 reading: libpcre2 kept as a filtered cross-check (leaning) vs dropped.
- Spellings: `callout N attrs` / `--callout`, `check-tail`, the listing
  tokens, the harness manifest's name.

## Questions that are Frank's (plain words; also in the note's section 10)

1. **When a check is written inside a library definition, which group numbers
   does it see?** Example: `lib.rxt` defines `octet` as `(\d+)` then a check
   reading group 1; your pattern is `^(\w+)=(?&octet)$`. Leaning: the check
   sees the definition's own groups (group 1 = the `\d+`), because the library
   author cannot know the callers; the alternative makes a library check's
   meaning depend on every caller.
2. **What "once per match" means in the firing classes.** Leaning: a check at
   the very end of the pattern with nothing retryable before it (for example
   after an atomic group): it runs at most once per starting position and a
   pass IS the match. A check at the end after `\w+` can run several times at
   one start (each veto makes `\w+` give back), so it is "may fire
   repeatedly", with a note that it sits at the end. The alternative calls
   every end-of-pattern check "once per match" in the weaker sense "at most
   one PASSING run per match".

## STATE AT HANDOFF

- Branch `lane/inlinecrev1`, all work committed (rev 1 note, design
  CLAUDE.md line, this report).
- Rulings file `docs/dev/lanes/inlinecrev1_rulings.md` re-read before each
  commit and this report: "(none yet)"; last entry applied: none.
- Validation: design-only lane; no make, no suites (none owed). Checks run:
  no `docs/spec` line cites in the note (grep for `\.md:[0-9]` empty); the
  CLI mode list read from `build/pcrec --help` for §5.9; the commit hook's
  staged checks passed.
- OWED RUNS: none.
- Next (manager): rule the open choices above; relay the two Frank questions;
  file the four PLAN items; then brief stage 0 and stage 1a (1a waits on
  [DD-11.5]'s next landing per the overlap table). The review recommends a
  D27 spec-first test author once rev 1 lands.
