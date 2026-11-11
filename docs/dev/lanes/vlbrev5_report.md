# vlbrev5 report: `docs/design/vlookbehind.md` rev 5 (stage 2), review 2026-11-10 r3 vlb2 applied

Lane vlbrev5 (opus), 2026-11-10, branch `lane/vlbrev5` off main `eb83f0902`. Design text only:
no `src/` edits, no `docs/dev/plan.md` or `known_issues.md` edits (their rows are drafted below
for the manager). Evidence: `docs/dev/lanes/vlbrev5_evidence/`. Every libpcre2 cell was run by
this lane (10.46, the repo's ctypes binding plus `PCRE2_INFO_MAXLOOKBEHIND`). Every pcrec claim was
checked with the worktree's own `build/pcrec` at `eb83f0902`, and every code citation was grepped
at that commit.

## STATE AT HANDOFF

**Done, committed on `lane/vlbrev5`:**
- `docs/design/vlookbehind.md` rev 5:
  - the status line and a "REVISION 5 ... read first" block;
  - new §6.2 (stage 2: 6.2.1 the column, 6.2.2 refusals, 6.2.3 scoping, 6.2.4 the shape-5 split,
    6.2.5 a 47-row acceptance table, 6.2.6 gates, 6.2.7 sabotage SV1-SV11, 6.2.8 spec hunks re-cut
    from HEAD, 6.2.9 units V1-V7);
  - rev 1-4's stage-2 text kept under a SUPERSEDED banner;
  - edits to §0 G1/G2, §3, §5.2, §8, §9, §10 (banner), §11 (stage 2), §13 Q3 and §15, and the new
    §16e.
- `docs/design/vlb_d27_extract.md` (NEW): the stage-2 D27 author's input, the promise only.
- `docs/design/lookaround_design.md` and `docs/design/la_d27_extract.md`: the backreference lines
  re-cut IDENTICALLY in both (§2.5's banner and bullet, §7.1's G3 row, §10.1's refusal row).
- `docs/design/CLAUDE.md`: the note's entry (status, the new extract). 12,212 bytes, under the limit.
- Checks: `make test-plan-lint` and `make test-doc-lint` green (rc 0);
  `check_claudemd_size.sh --all` green.

**Per finding, where it was fixed** (the same map is §16e of the note):

| finding | fixed in |
|---|---|
| F1 (ruled: one fixpoint, a column of callgraph's table) | REVISION 5; §6.2.1 (keys, region roots lifted from `pcrec_callgraph_build`'s `groot`/`cg_roots`, edges = `cg_length_calls` widened, Kleene iteration as the cwmax loop, built at postresolve, nothing published on nodes); §6.2.2 (the separate rules collapse) |
| F2 (ruled: (a) in scope) | §6.2.1 "References through a call"; §6.2.5 rows "through a call" / "through a call, refused" / "through a call, cap" |
| F3 (ruled: lookbehind-scoped) | §6.2.3 (a walk parameter beside `cwmax_walk`'s `any`; the kind row stays ANY; `(a\|bc)\1$` control); §0 G2; §6.2.6 gate 8; SV4 |
| F4 | §5.2 note (what stage 1 shipped: rule 0, `LBW_NOTBUILT`); §6.2.4; §6.2.8; §10 banner |
| F5 | §0 G1 (false at HEAD, four witnesses); §6.2.1 (lexical bound `hb`); §6.2.2 re-entry (K127 widened, call-free); row below |
| F6 | §6.2.2 re-entry bullets; §6.2.5 "self, off the width path"; SV8 |
| F7 | §6.2.2 "The `(?\|` rule" (inside only, pattern-wide at the deferred pass, LATENT, cells to the branch-reset module) |
| F8 | §6.2.2 table (two new sentences); §6.2.6 gate 7 |
| F9 | §0 G1 ("a group CONTAINING one"); §6.2.5 ceiling/cap/quantified rows; §6.2.8 §7.4¶5 and §9¶2a clauses |
| F10 | §6.2.6 gate 3 (`rx_VALID_LB == PCRE2_INFO_MAXLOOKBEHIND`); SV2 |
| F11 | §6.2.9 (V1-V7 with readers, abi/identity, spec, tests, sabotage, measurement card: none) |
| F12 | §6 SUPERSEDED banner; §6.2.9 V1/V2 readers (mrl.c's "does not build that yet" header, `pcrec_cwmax_static` folded and deleted, internal.h's "for free" comment, callgraph.c's "safe" headers, `pcrec_cwmin`'s A_CALL comment) |
| F13 (ruled: charter the D27 author) | §9; `vlb_d27_extract.md`; the `la_`/`lookaround_design.md` re-cut |
| F14 | §6.2.9 "Sequencing" |
| F15 | §6.2.6 gate 1 (axes, floors); §8 recount |
| F16 | §6.2.1 (the family, joined); §6.2.3 (unlock 2); §16e (unlocks 3, 4); rows below |

**Findings of this lane that the review did not have (the manager should read these first):**
1. **The review's "order-dependent" cell is a SELF-reference.** In
   `(?(DEFINE)(?<g>\1))(a)(?<=(?&g))x`, `g` IS group 1, so its `\1` names itself (REJECT 125). Its
   twin with the reference moved to group 2, `(?(DEFINE)(?<g>\2))(a)(?<=(?&g))x`, is ACCEPTED by
   libpcre2 (lb 1, `aax` → [1-3)), and so are both orders of every other through-call cell. No
   order dependence was found. The ruled cell stays as a refusal control, under the cycle rule
   (`cells3.out`).
2. **PCRE2's boundedness is LEXICAL.** libpcre2 refuses `(a(?1){0})(?<=\1)x`, `(a+)(?<=\1{0}x)y`
   and even `(?<=(?:a+){0}x)y` (err 125), but accepts `(a)(?<=\1{0}x)y` (lb 1). So "cycles
   saturate to UNBOUNDED" holds only if the bound counts a `{0}` maximum as 1. Rev 5 adds that as
   the column's `hb` value (§6.2.1). Lengths themselves keep `{0}` = 0.
3. **F5's HEAD divergence has a STAGE-1 sibling.** pcrec at HEAD compiles `(?<=(?:a+){0}x)y`,
   `(?<=(a+){0}x)y`, `(?<=(?:a|b+){0}x)y` and `(?<=(?:(?:)*){0}x)y`, which have no reference and no
   call; libpcre2 refuses each one (`cells5.out`, `cells6.out`, `pcrec_head.out`). It is the same
   arithmetic (0 × UNBOUNDED = 0), and the same `hb` fixes it. It is in the known_issues draft
   below.
4. **Diagnostic timing moves with the deferral.** `(a)(?<=\2)x` will report the reference
   resolution error (libpcre2: 115) instead of today's lookbehind refusal, and
   `(a)(?<=\1|b+)x`'s refusal moves to postresolve (same text and offset) (§6.2.4).

### Drafted: known_issues row (K140, next free number at `eb83f0902`)

```
## K140 — OPEN (found by review 2026-11-10 r3 vlb2 F5, widened by lane vlbrev5, 2026-11-10) — a lookbehind whose length reaches an unbounded construct under `{0}` compiles; libpcre2 refuses it (err 125)

**Witness:** at main eb83f0902, pcrec compiles `(a(?1){0})(?<=(?1))x` (matches `aax` at 1..3),
`(?(DEFINE)(?<g>a(?&g){0}))(?<=(?&g))x`, `(a(?1)?)(?<=(?1){0}x)y`, and with no call
`(?<=(?:a+){0}x)y`, `(?<=(a+){0}x)y`, `(?<=(?:a|b+){0}x)y`, `(?<=(?:(?:)*){0}x)y`; libpcre2 10.46
refuses every one (err 125). docs/dev/lanes/vlbrev5_evidence/ (pcrec_head.out, cells*.out). An
ACCEPT-SET divergence (pcrec accepts more), not a wrong answer: each artifact's answers are those
of the pattern with the `{0}` item deleted. Cause: pcrec's lookbehind boundedness is arithmetic
(`pcrec_sat_mul(0, UNBOUNDED) == 0` in src/opt/mrl.c's `A_REP` arm, and the published callee
width of a recursive group under `{0}`), while PCRE2's is lexical. Gate 3's generator never
emitted the shape. **Fix:** rides [VLOOKBEHIND] stage 2 (docs/design/vlookbehind.md §6.2.1, the
lexical bound `hb`: a repeat maximum of 0 counted as 1 for the unbounded refusal only;
lengths keep 0). It refuses patterns that compile today (a G1-over-G2 exception, §0 G1);
the stage-2 build counts them in the corpus (0 expected). Sabotage SV3.
```

### Drafted: replacement for the [VLOOKBEHIND] plan row's "Stage-2 note"

Replace the line that begins `Stage-2 note (2026-11-07, vlbbuild review F4a)` with:

```
  Stage-2 note (2026-11-10, review r3 vlb2, ruled; supersedes the 2026-11-07 note): a backreference reached THROUGH A CALL is NOT a wording-tier item: libpcre2 ACCEPTS the bounded case (`(a)(\1)(?<=(?2))x` lb 1, `(a)(?(DEFINE)(?<g>\1b))(?<=(?&g))x` lb 2), so it is in stage 2's accept set (F2 (a), vlookbehind.md §6.2.1). `(a+)(?<=\1)x` moves from rule 0 (shape 5) to the unbounded refusal (shape 7, err 125 on both sides). Design: vlookbehind.md rev 5 §6.2 (lane vlbrev5); D27 extract docs/design/vlb_d27_extract.md; owner build go 2026-11-10 ("1. yes"); build lane after rev 5's fixes are checked.
```

Add to the row's `refs:` (F16, the promise in altcls.c's header and its comment near line 135,
"[VLOOKBEHIND]'s own row"): `src/opt/altcls.c (waits for this row: a lookbehind's
alternatives); docs/dev/reviews/2026-11-10-r3-vlb2.md; docs/dev/lanes/vlbrev5_report.md;
docs/design/vlb_d27_extract.md`.

### Drafted: PLAN row for F16 unlock 2

```
- [REF-WINDOW] STATE:not-started — a reference-aware end and start window: a backreference counts its group's width in the global width facts, so `(a|bc)\1$` gets an end window of 4 instead of "none"
  filed: 2026-11-10 lane vlbrev5 (review 2026-11-10 r3 vlb2 F16 unlock 2; manager ruling F3)
  status (2026-11-10): not built; [VLOOKBEHIND] stage 2 builds the group width column but reads it ONLY in the lookbehind rule (vlookbehind.md §6.2.3), so endwin/startanch keep today's answers (control: `--emit-facts '(a|bc)\1$'` prints RX_END_WINDOW "none"; `(a|bc)bc$` prints 5)
  trigger: a bench cell with a trailing-anchored backreference
  next: on the trigger, pass the stage-2 column to `pcrec_cwmax`'s non-lookbehind readers (src/facts/endwin.c `pcrec_end_window`, src/facts/startanch.c); it is an abi event and a G2 identity re-pin (every artifact with a backreference and an end/start fact moves); spec hunk in tuning/match_api as the facts dictate
  refs: docs/design/vlookbehind.md §6.2.3; docs/dev/reviews/2026-11-10-r3-vlb2.md F16; [VLOOKBEHIND]
```

**Not done / for the manager:**
- The rows above are DRAFTS. plan.md and known_issues.md were not edited (brief).
- The review's three "Lessons for the guide" are not this note's; filing them is the manager's.
- `la_d27_extract.md`'s §10.1 "single-branch variable body" refusal row is stale since stage 1.
  This lane left it, because the brief scoped the re-cut to backreference lines.
- The compliance page and annotation store quote the shape-5 sentence. They move at stage 2's
  landing through the compliance-refresh skill (§6.2.8 "Not spec").
- The "full 40-row table" the review could not locate was not chased. §8's recount is
  reproducible by grep and replaces it.
