# vlbrev51 report: `docs/design/vlookbehind.md` rev 5.1 (stage 2), review 2026-11-10 r5 vlb3 applied

Lane vlbrev51 (opus), 2026-11-10. Branch `lane/vlbrev51`, cut from `lane/vlbrev5` (rev 5,
`5a2595601`). DESIGN TEXT ONLY: no `src/` edits, and no `docs/dev/plan.md` or `known_issues.md`
edits (their rows are drafted below for the manager). Input: main's
`docs/dev/reviews/2026-11-10-r5-vlb3.md` and its RULINGS block (G1, G4, G9, G11, G14 ruled; the
other FIX-NOW items as proposed; G15 PLAN).

Evidence: `docs/dev/lanes/vlbrev51_evidence/`.
- Every libpcre2 claim rev 5.1 adds was run by this lane against libpcre2 10.46, through the
  repo's ctypes binding, with the refusal OFFSET (`ora2.py`, `cells51*.out`).
- Every pcrec claim was checked with a `build/pcrec` built in this worktree from source identical
  to main `3a190b8d7`: `git diff eb83f0902 main -- src cli lib tests docs/spec` is empty
  (`pcrec_head51*.out`; single compiles, `--features all`).
- Every "existing X does Y" was grepped at that source, by function name (the line numbers in
  the review had drifted by a few lines in places).

## STATE AT HANDOFF

**Done, committed on `lane/vlbrev51`:**
- `docs/design/vlookbehind.md` rev 5.1:
  - the status line and a "REVISION 5.1 ... read first" block;
  - §6.2.1-§6.2.9 rewritten in place, every change marked `[vlb3 Gn]`;
  - §0 G1 (the DEFINE exception and more F5 members; G4's stated divergence) and §0 G2;
  - §9 (the re-cut and the stage-0 spec text), §11 (the standing questions at rev 5.1), §15 (rev
    5.1's evidence) and the new §16f.
- `docs/design/vlb_d27_extract.md`: RE-CUT from rev 5.1 (G20).
- `docs/design/CLAUDE.md`: the note's entry now says "stage 2 rev 5.1".
- `docs/dev/lanes/vlbrev51_evidence/`.
- Checks: `make test-plan-lint` rc 0 (2 passed); `make test-doc-lint` rc 0 (7 passed); the
  pre-commit hook passed (52 checks, CLAUDE.md size within limits) on every commit. No suite
  was run (a full suite held the box; brief: single compiles and probes only).

**Per finding, where it was fixed** (the same map is §16f of the note):

| finding | fixed in |
|---|---|
| G1 (RULED: a DEFINE mark) | §6.2.1 (the mark: a field of the `A_REP` payload, set only by `pcrec_rcport_define`; edge walks do not enter it; `hs` counts it 0; region searches do look inside; atomic.c's predicate unchanged and re-argued); §6.2.2 (edges, re-entry, duplicate names); §6.2.5 (13 cells + controls); §6.2.7 SV12/SV13; §6.2.8 (¶5, ¶5c); §0 G1 |
| G2 | §6.2.2: the table is HEAD's `la_widths` control flow (order 4 reads `hs`; order 5 marks `hi` unbounded with `hs` finite; orders 6-7 on finite `hi`; order 8 rule 0); the emptiness drill column |
| G3 | §6.2.1 (`hb` dropped; three values), §6.2.3 (the lexical flag needs no table, so parse-time lookbehinds read `hs` too), SV3 re-aimed |
| G4 (RULED: state it) | §0 G1 (second stated divergence); §6.2.1; §6.2.5 (five cells); §6.2.6 gate 3 (own line); §6.2.8 (§7.4¶5, §9¶2a); unlock in §16f |
| G5 | §6.2.4 ("as libpcre2 does" withdrawn; four classes with predicted pcrec answers); §6.2.5; §6.2.6 gate 7; K-row drafted below |
| G6 | §6.2.4 (rule 0 by length; 7 → 5 moves); §6.2.5; §6.2.6 gate 7; §6.2.8 |
| G7 | §6.2.2 (post-order: an inner lookbehind first, the parse hook's own order; nested bodies off the outer's path for the bound and duplicate names, followed by re-entry); §6.2.5 (12 cells); SV16. See finding 1 below |
| G8 | §6.2.2 (re-entry from THIS lookbehind's body); §6.2.5 |
| G9 (RULED: new sentence) | §6.2.2 ("a lookbehind's length may not depend on a group that contains it"; K127's call arm too); §6.2.4; §6.2.5; §6.2.8 |
| G10 | §6.2.1 (finite values clamp at 65536); §6.2.5 (3-, 25- and call-25-step chains); SV15 |
| G11 (RULED: one table) | §6.2.1 (one table keyed by group number at `pcrec_callgraph_build`'s position; early return widened; own Ctx field; one loop function with the reference treatment as a parameter; the `cwmin` fixpoint, `cg_cwmin_publish`, `u.call.cwmin` and S-U10 RETIRED, listed as a simplification); §6.2.3; §6.2.7 SV14; §6.2.9 V1 |
| G12 | §6.2.6 gate 8; §6.2.7 (SV2 both reds; SV4 re-aimed to `(a\|bc)(?<=\1)\1$`, window "5"; SV8's witnesses replaced and folded into S1455; S171, S-U10, S1454, S1455, S1490, S170, S1981 and inlookaround_self listed) |
| G13 | §6.2.2 (the `(?\|` rule reads reached rows); §6.2.5; PLAN text below |
| G14 (RULED: run the checks) | §6.2.4 (`pcrec_count_groups` runs the passes through `pcrec_postresolve`; `want_caps` noted; the cost is measured and reported by the build; the fallback is the manager's call); §6.2.8 (the cli.md §2.13¶1 hunk); §6.2.9 V3/V4 |
| G15 (PLAN) | §6.2.5 (the latent cell); note drafted below |
| G16 | §6.2.1, §6.2.3, §6.2.6 gate 9 (`make test-recursion-lbsweep` owed by name), §6.2.9 (every reader list) |
| G17 | §6.2.2 (stated); §6.2.5; K-row drafted below |
| G18 | §6.2.6 gate 3 (EXTRA minus latent and pcrec-only rows; `pcre2only=1`) and gate 7 (four sentences, plus offset) |
| G19 | §6.2.8 (§7.4¶5's stage-1 lexical clause and the DEFINE fact; ¶5c duplicate name through a referenced group) |
| G20 | `vlb_d27_extract.md` re-cut: §0 carries the spec text, because the author works at stage 0; LB is promised as `max_lookbehind` via `_valid_upto` and not as the internal stamp; the dropped cells are restored; the UTF caseless cells are also in §6.2.5 now; the extract adds G1/G4/G7/G9's classes |
| G21 | §16f (general form; seven unlocks with triggers) |

**Per-unit readiness after these edits** (§6.2.9's new column). The review's recommendation
stands: ONE readiness critic on the rev 5.1 diff before the build lane is briefed.

| unit | readiness | what was blocking, and what changed |
|---|---|---|
| V1 the table | READY | G1 and G11 are chosen and specified; G16's reader list is corrected |
| V2 the scoped walk + the DEFINE mark | READY | G1's mark is specified; G3 drops `hb` |
| V3 the rule + the describe path | READY | G9 is ruled (sentence) and G14 is ruled (the build measures the cost); G2, G5-G7, G13 are text |
| V4 spec | READY | hunks drafted against HEAD's text, the cli.md hunk included |
| V5 corpus and pins | READY | the lbsweep run is owed by name |
| V6 checks | READY | SV1-SV16 and the moved rows are listed |
| V7 D27 (stage 0) | READY TO BRIEF | re-cut after G1/G4's choices (this lane) |

**Findings of this lane that the review did not have** (read these first):
1. **G7's literal fix would have broken K127.** The review proposed "nested lookbehind bodies OFF
   the outer's path". Taken alone, that makes `((?<=(?2)))(a(?<=(?1)))` compile. libpcre2 refuses
   it @1, and HEAD refuses it @1. Rev 5.1 splits the treatment:
   - the order is post-order (an inner lookbehind first);
   - nested bodies are off the outer's path for the bound and the duplicate-name rule;
   - the re-entry walk still follows them.
   Against libpcre2 that reproduces every nested and reached-lookbehind cell this lane ran (12
   cells, `cells51c.out`, `cells51d.out`). The model is checked by hand against the cells; it is
   not built.
2. **G5's callout offset is @12, not @14.** The review's "@14" for `(a)(?<=\1|b+(?C1))x` is the
   offset of the call twin `(a)(?<=(?1)|b+(?C1))x`. `\1` is two characters shorter than `(?1)`, so
   the reference cell's callout sits at 12. The same shift gives `(a)(?<=\1(?C"c,consume"))x` @9.
   Both are PREDICTED pcrec answers, labelled as predicted in the note.
3. **cli.md §2.13¶1 says "parse only" too.** G14's choice falsifies that clause, so the hunk
   rewrites it. The describe path also parses with `want_caps = false`, while the table's region
   roots are `A_CAP` nodes. The note says the front half must run on the compile's own tree, and
   leaves the mechanism to the build.
4. **The ceiling's DEFINE twin agrees with the mark.**
   `(a(?(DEFINE)(?<g>b{40000}c{40000})))(?<=\1)x` is ACCEPT, lb 1, in libpcre2. So libpcre2 skips
   a DEFINE body for the ceiling as well as for the bound, and the mark needs no ceiling clause.
5. **The `(*ACCEPT)` cell's span is right.** `(?=(a(*ACCEPT)bc))\w+(?<=\1)x` on `zzzax` → (3,5),
   group 1 (3,4): reproduced.
6. **The emptiness drill on the note's other rule tables.** §5.1b's two emission rows split on
   `lo == hi` against `lo < hi`, so neither is dead. §5.4's `reverse-dfa` row is HELD (declared
   empty), and `range` takes every branch. The one empty row in §6.2.2 is the latent branch-reset
   rule, declared as such.

### Drafted: known_issues row (precedence; next free number after K139 and the pending K140 → K141)

```
## K141 — OPEN (found by review 2026-11-10 r5 vlb3 G5; drafted by lane vlbrev51) — a deferred lookbehind width refusal loses to diagnostics raised before postresolve; libpcre2 reports the first lookbehind's fault

**Witness:** at main 3a190b8d7, call-bearing lookbehinds: `(a)(?<=(?1)|b+)(?<=c+)x` refuses @15 (libpcre2 125 @3); `(a)(?<=(?1)|b+)x\2` gives the `\2` resolution error @16 (libpcre2 125 @3); `(a)(?<=(?1)|b+(?C1))x` gives the callout sentence @14 (libpcre2 125 @3); under `--engine=dfa`, `(a)(?<=(?1)|b+)x` gives the VM-only refusal. docs/dev/lanes/vlbrev51_evidence/pcrec_head51_misc.out, cells51b.out. D26 tier 2 (which error, which offset); no answer moves. [VLOOKBEHIND] stage 2 widens the class to every reference-bearing lookbehind (vlookbehind.md §6.2.4; gate 7 pins the post-stage-2 answers). **Fix (not scheduled):** record the first parse-time fault's offset and let postresolve's refusal win when its lookbehind comes first.
```

### Drafted: known_issues row (branch order; G17)

```
## K142 — OPEN (found by review 2026-11-10 r5 vlb3 G17; drafted by lane vlbrev51) — a lookbehind's refusal reason follows pcrec's last-written-first branch order

**Witness:** `(?<=(?:b{60000}){2}|c+)x`: libpcre2 10.46 REJECT 187 @0 (the first branch's ceiling); pcrec at 3a190b8d7 prints the unbounded sentence (the last branch). Both sentences are true. cells51.out. D26 tier 2. **Fix:** flip `la_widths`' loop to first-written-first; a reject-table byte move (the manager's call).
```

### Drafted: K140 widened (G1's cells)

Add to the K140 draft (vlbrev5's report) after its witness list:
`((?<=x(?:\1){0})a)`, `(?J)(?<n>a)(?<n>b)?(?<=x(?:\k<n>){0})y` and `(?<=(?:\1+){0}x)(b)y` also
compile at HEAD, and libpcre2 refuses them (err 125 @1, @19, @0; `vlbrev51_evidence/`). The
fix's lexical bound must NOT reach a `(?(DEFINE)...)` body: libpcre2 skips it
(`(?<=a(?(DEFINE)(?<g>b+)))x` ACCEPT; vlookbehind.md §6.2.1's definition-only mark).

### Drafted: known_issues lines for the other HEAD divergences (the manager decides rows vs notes)

- `((?<=x(?(DEFINE)(?1)))a)`: pcrec refuses ("unbounded"), libpcre2 ACCEPTS (lb 1). Closed by
  stage 2's DEFINE mark.
- `(?<=(?:a{30000}b{35536}){0}x)y`, `(a{40000}b{40000})(?<=\1{0}x)y`: pcrec compiles, libpcre2
  187. This is the STATED divergence (G4 ruling), so a spec line rather than a K-row.
- The 25-step call doubling chain (`chain_call.txt`) prints "unbounded"; libpcre2 gives 187
  @292. Closed by stage 2's clamp.
- `(a(?<=b(?<=(?1))))x`: pcrec @2, libpcre2 @7. Closed by stage 2's post-order.
- `--count-groups` on `(a)(?<=(?1)|b+)x` prints `1`. Closed by stage 2's G14 choice.

### Drafted: [BRANCH-RESET] scope line (G13 PLAN)

```
  Lookbehind tie-in ([VLOOKBEHIND] stage 2, review 2026-11-10 r5 vlb3 G13): a duplicated group NUMBER needs one width row per `A_CAP` of that number (min of the mins, max of the maxes) wherever a reference reaches it; `cg_roots`' first-declaration-wins is right for CALLS only (`(?|(a)|(bc))(?<=(?1))x` lb 1, `(?|(bc)|(a))(?<=(?1))x` lb 2) and UNDER-estimates for references (`(?|(a)|(bc))(d\1)(?<=\2)x`, libpcre2 125). Until then stage 2's latent rule refuses every reference-bearing lookbehind in a `(?|` pattern; its cells (vlookbehind.md §6.2.2/§6.2.5) become this row's tests.
```

### Drafted: the verbs note (G15 PLAN)

No `verbs` plan row exists at main `3a190b8d7` (grep of plan.md: only possessify's "`verbs`
tripwire" mention). The note goes on whichever row charters `(*ACCEPT)`:

```
  Width tie-in (review 2026-11-10 r5 vlb3 G15): `(*ACCEPT)` cuts a group's capture below its body's minimum. libpcre2 10.46 gives `(?=(a(*ACCEPT)bc))\w+(?<=\1)x` lb 1 and matches `zzzax` at (3,5); a width that ignores the verb says [3,3], a false no-match. On the day `(*ACCEPT)` builds, [VLOOKBEHIND]'s group table (`lo`/`hi`) and callgraph's published `cwmax` must stop at the verb, and gate 3's VALID_LB compare is pointed at the cell.
```

### Drafted: unlock row for G4 (optional; the ruling says "state it")

If the manager wants the unlock recorded as a row (vlookbehind.md §16f unlock 4), BOONIES-style:
`[LB-ZERO-CEILING]` "a per-row largest `{0}` body (a max, not a sum), read by the ceiling rule,
closes the stated ceiling-under-`{0}` divergence; trigger: a decision to close G1's last `{0}`
class".

**Not done / for the manager:**
- Every row above is a DRAFT. plan.md and known_issues.md were not edited (brief).
- The review's three "Lessons for the guide" are the manager's to file. The process lesson is
  applied in the note (§6.2.2's emptiness drill), and the brief's note is restated here: every row
  of an ordered rule table needs a non-empty population that no earlier row takes. G2's rule 1
  read `hb`, which made rule 0 unreachable.
- `la_d27_extract.md` and `lookaround_design.md` were not re-cut again. Review r5 vlb3 found rev
  5's re-cut byte-identical between the two files, and rev 5.1 changes nothing they state (both
  only point at stage 2).
- G5's pcrec offsets are PREDICTED from the call twins. The build pins the real ones in gate 7.
- No suite was run. This was a design-text lane: lints only, plus single compiles and probes.
