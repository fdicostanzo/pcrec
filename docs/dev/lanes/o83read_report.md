# o83read — bench O-83 (round 1 on the wide bench), gap report 2, round-2 inputs (2026-10-05, opus)

Branch `lane/o83read`, from main `c0df458c`. Docs plus one instrument fix;
nothing under `src/`, `cli/`, `lib/` or `tests/` changed. Bench inputs were
read over the tailnet, read-only, at pcrec-bench `08b371a`. The Linux box
was running a pcrec `make mech`, so only a light `tar` of the reports,
ledger and sweep was taken, into the session scratchpad. The Mac copy of
pcrec-bench is stale: it is at `eb634d9d`, O-82, and has no O-83.

## Delivered

1. `docs/dev/summaries/2026-10-05-bench-o83-round1.md` — the exec summary:
   per change and per regime, absolute values, K81/K82/K83 status, the
   "new" movers attributed, and the S2 respelling identified.
2. `docs/dev/optloop/gapreport_2026-10-05.md` (rendered by
   `gapreport.sh --group round1-c4c70f2c`) and its judgement,
   `docs/dev/optloop/judgement_gapreport_2026-10-05.md`.
3. **Instrument fix**, `docs/dev/optloop/gapreport/extract.py`:
   - **The defect.** A cross-pin report group (every re-pin window)
     carries pcrec at two pins, and both mapped to one testee key. The last
     TSV row won, cell by cell, so the first render silently mixed
     `fc719ca4` and `c4c70f2c` values: union-select read 0.724 ns/B where
     the pin reads 0.338.
   - **The fix.** Only the newest pin is kept, named by the header's
     `null_band: pcrec OLD -> NEW`. Two pins without that line is an error.
     The report prints the dropped pins.
   - **Validation.** `gapreport.sh --check`: "check OK: fixture report
     identical to fixture/expected.md", before and after.
   - **Scope.** The first instance (single-pin groups) is unaffected.
   - **Also.** `gapconfig.SETS` gains `litrun`. `causes.tsv` gains 9 rows
     and 2 groups (SEL-LIT, K82-AT-PIN), so there are 0 unassigned cells.
4. CLAUDE.md entries in `summaries/`, `optloop/` and `optloop/gapreport/`.

## Findings a resuming agent needs

- **The bench reproduces every K82 alpha magnitude**, on auto, in ns/B:

  | cell | bench | alpha |
  |---|---|---|
  | userpass | +0.921 | +0.92..+0.95 |
  | union-select | −0.386 | −0.40..−0.52 |
  | ci-ascii-control | −0.444 | −0.45..−0.50 |
  | mod-i | +0.646 | +0.59..+0.70 |
  | cls-fold-pair | +0.396 | +0.32..+0.41 |
  | ci-strasse | +0.073 | +0.08..+0.10 |
  | alt-shared | +0.110 | +0.079..+0.112 |

  Unmeasured by any alpha:
  - userpass short search +6.6 ns per subject (auto; cause A, so abi 60
    should cure it);
  - utf8 short-search per-call terms on ci-strasse (+2.6),
    ci-ascii-control (+1.4) and alt-shared (+1.4), auto, ns per subject;
  - the cause-(B) forced-VM throughput loss, +0.64..+2.02 ns/B (the
    handoff does not reach it; that is [OPT-VMSEED]'s territory).
- **K81's short-call term IS on the bench.** `floor` whole-subject
  match-compliance reads +1.1..+1.6 ns per subject on bounded, syntax,
  altwide and email. That matches the alpha's +1.75. Its real-scale cells
  (`(?:P)\z` on mix4k/hex4k) have no bench counterpart. The bench scored
  plain-form throughput, which is a different program: the plain
  `cls-upto-1024` movement is the S2 respelling.
- **The S2 range respelling.** What it is:
  - D139 item 2's one shared range spelling (`ddfefeb7`, abi 53).
  - clss2 said the two spellings "compile the same". The bench's census
    says −4 B per site.
  - The sweep's 65 rows split by REGIME, not by chance: plain throughput
    is slower on every row (+0.2..+8%, `nest2-letters-6` +0.248 ns/B) and
    plain short search is faster on every row (−0.6..−8.7%).

  It is NOT a D144 item-4 violation. It predates D144, it is not an
  optimization, and D139 ruled one spelling. It is a gap in D139's
  "measured" clause, which was satisfied by emitted text only. Draft K row
  below.
- **SEL-LIT**, new in this gap report. On litrun, auto's DFA
  (`run-pinned`/`offset-set`) loses to pcrec's OWN forced VM on every
  literal length (x1.4-x4.7), and the VM beats jit on l7/l16/l31/l40. The
  densities are synthetic, so whether the sign holds on real text is open.
  It is a desk read of the existing vm-caps arms; no build.

## Draft K row (for the manager to file; K86 is the highest on main)

> **K87 — OPEN (2026-10-05, found by lane o83read's read of bench O-83 /
> its b122sweep) — [CLS-TREE] S2's unified scan-edge RANGE spelling
> (D139 item 2, abi 53) moves default DFA timing with a consistent regime
> split: plain throughput slower on every bounded/loglines row, plain
> short-search faster on every row.**
>
> Witness: bench ledger `2026-10-05-b122-round1-wide-c4c70f2c.md` §7.3,
> 65 real rows (30 improve / 35 regress) against the identical-program D119
> bar:
> - `nest2-letters-6` throughput 1.249 → 1.497 ns/B;
> - `cls-upto-1024` 1.290 → 1.343 ns/B;
> - the `cls-upto-*`/`dig-*` ladder +0.2..+8%;
> - short search −0.5..−2 ns per subject.
>
> The census attributes it to the respelling `(unsigned char)(b - lo) <=
> span` → `(unsigned)(b - lo) <= spanu`: −4 B per range test site, 56 DFA
> artifacts. `clss2_report.md` committed the change on its TEXT movers (79
> default artifacts), asserting that the two spellings "compile the same".
>
> No flag exists, by design: one emitter, one spelling (D139).
>
> Disposition (D144): an issue row, not a revert. The first step is a
> pcrec-side Linux twin of the two spellings with an alignment control, on
> `cls-upto-1024` and `nest2-letters-6` throughput and one short-search
> cell. That decides which spelling the shared emitter keeps, or whether
> the regime split is layout. Rides the next scratch_lx batch.

## Relay text for pcrec-bench (answers to O-83's questions)

> **"short-call +1-9 ns" (K81).** These are pcrec-side alpha cells, not bench
> cells (`docs/dev/optloop/alpha_vedge.sh`, Linux, gcc 15.2,
> `taskset -c 2`):
> - **Program and call.** Each bench pattern is WRAPPED as `(?:P)\z` and
>   called as ONE `rx_search` from offset 0 per call, in ns per call.
> - **Subjects.** Fixed-seed subjects that we generate: `short` = 40
>   random lowercase bytes, `dig40` = 40 digits, plus `l4k`, `prose64k`,
>   `mix4k` and `hex4k`.
> - **Cells**, base 74017b71 → new 8562ff3a, delta:
>   - bounded `floor` +1.74..+1.75 on all six subjects (4.75 → 6.49);
>   - `year4` +3.59 (short/l4k/prose64k), +5.67 (mix4k);
>   - `dig-exact-16` +3.38..+3.84;
>   - `hex32` +8.74 (short), +3.08 (l4k), +6.97 (prose64k);
>   - `cls-upto-4..4096` on `dig40` +0.89..+3.50.
>
>   Floors are 0.00-0.26 ns.
> - **Your nearest cells.** No bench regime runs the `\z`-search form on
>   non-matching text. Your nearest cells are whole-subject
>   match-compliance, and there your `floor` rows ARE this term: +1.1..+1.6
>   ns per subject on bounded (9.3 → 10.4), syntax (9.2 → 10.8), altwide
>   (9.5 → 10.8) and email (9.2 → 10.5), i.e. your 13-17% view-edge
>   regress rows. On year4/hex32/dig-exact-16 your whole-subject subjects
>   are field-shaped, and the edge's win dominates, as you measured.
> - **The real-scale cells.** K81's `base10num-grok`/`cls-upto-1024` cells
>   (+4-6.5 µs, +0.2-0.5 µs) are the same `(?:P)\z` program on our
>   `mix4k`/`hex4k`. Your plain-form throughput cells run a different
>   program; the plain `cls-upto-1024` movement is [CLS-TREE] S2's range
>   respelling, not view-edge. Nothing for you to re-run.
>
> **"short union-srch calls +2.4-4.4 ns" (K82).** These are
> `wild-waf-crs-942270-union-select` at default flags (auto, captures,
> byte), searched ONE call per subject, in ns per call. The subjects are
> exactly the 75 your `capability/expectations.tsv` names for that
> pattern's `search_short` regime (regenerated from your `gen_subjects`,
> sha-checked):
> - **Pins.** pcrec alpha `alpha_c3.sh`, BASE a588c668 → NEW 8562ff3a.
> - **Regressions.** About 35 subjects regress, mostly +2.4..+4.4 ns: the
>   ~43 that contain no `c`/`C` read a flat 10.06 ns against a 6.2-7.7 ns
>   BASE (two fresh `memchr` calls). The four gate-pass subjects are worst:
>   waf-dbnames +11.0, waf-union +8.7, waf-comment-obfuscation +7.6,
>   waf-concat.
> - **Wins.** About 40 subjects win, e.g. sec-github-pat −44, sd-empty-alt
>   −28, slack-webhook −17.5.
> - **Net.** About −127 ns summed over the 75.
>
> Your short-subject-search cell is the SUM over these same 75 subjects, so
> its improvement (auto −158.9 ns/set, ×1.16) is consistent with them. This
> is not a disagreement: the per-subject split is invisible at set grain.
> Our per-subject read is `docs/dev/lanes/k82diag_report.md` §2.
>
> **"Is that two-sided shape what the abi-60 fix expects?"** It is the shape
> our diagnosis expects, and abi 60 does not change it:
> - **Why two-sided.** On match-dense large subjects the caseless run gate
>   passes almost always and the engine rescans (cause B). On short
>   subjects without the run, the gate rejects before the engine runs: a
>   pure win on the forced VM, which had no prefilter before.
> - **What abi 60 fixes.** K82's (A) and (C): userpass and most of
>   alt-shared. It leaves the five fold-family patterns untouched.
> - **The next fix.** Their fix is the HANDOFF (abi 61, `-fno-req-handoff`,
>   built, Linux alpha pending). It is predicted to bring auto throughput
>   back to about pre-C3 and keep the short-search wins.
> - **The forced-VM throughput loss** (+0.64..+2.02 ns/B) is outside the
>   handoff and stays until a later VM-route change.
>
> **K83 clang arm:** not now. The first step is pcrec-side (a clang
> disassembly of the one cell). We will ask if that says the population is
> wider than one pattern.
>
> **A flag for the S2 range respelling:** none planned. It is one shared
> spelling by design. We will separate it with a pcrec-side twin rather
> than a deny flag.

**Bench-only questions (optional; nothing above depends on them):**

1. A capability subject-grain file for `union-select`'s
   short-subject-search, if it is cheap. It would show the per-subject
   split above on your own instrument.
2. At the next wide window, keep the `floor` whole-subject cells in the
   view: they are the bench's K81 witness.

## Round-2 INPUTS for Frank (D144 item 6) — candidates, not a schedule

| candidate | evidence | expected gain | recommendation |
|---|---|---|---|
| **K82 (B) handoff** | built on `lane/k82hbuild` (abi 61); 0 defects over 4.4M cells; bench confirms cause B at +0.39..+0.67 ns/B auto on 5 patterns | auto throughput back to pre-C3: mod-i/mod-r about −0.5..−0.6 ns/B, cls-fold-pair/cls-pair-ctl about −0.39, ci-strasse BASE or a small win (`litscan_k82h.md` §3.2); closes CI/DENSE's K82-made gap (mod-i x3.84 → about x2.3 vs jit) | **First, as already ruled.** Its Linux alpha (`alpha_k82h.sh`) is the next Linux slot. Add cls-n-uc (K85) and alt-shared's VM arm to that alpha. |
| **K85** set-leads per-call `memchr` | cls-n-uc +0.025..+0.031 ns/B (about 11.5 ns per call at 1 match / 380 B); the only K85 mover | about 0.03 ns/B on one synthetic cell | **Hold**, per K85's own text: re-measure after the handoff lands; design nothing specific. |
| **K81** VEDGE entry term + mix/hex | entry term confirmed on the bench (`floor` +1.1..+1.6 ns per subject, four sets); mix4k/hex4k +4.2/+6.6 µs alpha-only on `(?:P)\z` | about 1.5 ns per whole-subject call on short subjects; µs on mixed-run `\z` subjects (synthetic) | **Small analysis item, not a build**: read the emitted text to test the per-run re-entry hypothesis. Low rank against the gap groups. The bench cause nets 14/14. |
| **K83** A1 clang loss | 1 cell, clang only, 24 ns per pass; the bench has no clang arm | unknown population | **Low.** A pcrec-side disassembly first; no bench ask. |
| **S2 range respelling** (draft K87) | 65 bench rows, a consistent regime split; −4 B per site | about ±4% on bounded scan-edge loops (about 0.05-0.25 ns/B throughput, 0.5-2 ns per short call) | **A cheap pcrec-side twin** decides the one spelling. No flag. |
| **START-SET** (gap #1) | 18 cells; aws x43.9 vs jit (interp x18.8 faster); real text | the largest algorithmic gap on the bench | **The top new-work candidate** ([OPT-FIRSTSET] + [OPT-VMSEED], D124 shape), as on 10-03. |
| **CTX** (gap #2) | level-context x3.83 jit, x10.5 rust; loglines | realworld, algorithmic | **Profile first**, then pick among [OPT-VMLIT], [ENG-TACTICS] and [CTX-PREFILTER]. |
| **NULLABLE-ANCH / U8-PICK** (gaps #4/#5) | 2 cells x1081 re2 / 10 utf8 cells x5-x16 re2 | large ratios, narrow breadth | **File both rows** (still unfiled since 10-03). Each has a cheap first step (census / two-artifact twin). |
| **SEL-LIT** (new) | litrun: auto's DFA x1.4-x4.7 slower than pcrec's own VM; the VM beats jit on 4 of 5 | possibly selection-only, no new engine | **A desk read** of vm-beats-auto across all sets' existing arms, under [SEL-COST]. Closes as synthetic if the sign is litrun-only. |
| **utf8 movers** | ci-ascii-control ×2.77/×8.38 = C3's predicted customer; alt-shared ×2.06 = K82 (C), auto-cured at abi 60 (+0.013..+0.021 residual) | — | No new work. Add alt-shared's forced-VM arm and a `-fno-req-run-fold` arm to the handoff alpha (k82alpha §3's suggestion). |
| C1's syntax forced-VM tail | mod-n VM +0.288 ns/B, lit-cat whole-subject +13.8% | forced-VM only | Note only; C1 nets 68/28. |

## Validation

- `gapreport.sh --check`: OK, twice (after the extract fix and after
  adding litrun).
- The gap report rendered with 0 unassigned cells and 4 MANAGER
  JUDGEMENT markers.
- Every absolute number in the summary was computed from the fetched
  report TSVs (scratch `abs.py`; set-grain median ÷ the
  `gapreport/nmatch.py` bytes, or ÷ the subject count).
- K81's and K82's alpha numbers were read from
  `ubuntubudu:~/pcrec/scratch_lx/r1alpha/{vedge,c3}.out`.

## Not done

- No timing anywhere. The S2 twin is proposed, not run.
- The S2 machine-code claim (−4 B per site) is the bench's census. It was
  not re-derived here.
- No plan.md / known_issues.md edits: the K87 draft, the NULLABLE-ANCH and
  U8-PICK rows, and the SEL-LIT note are the manager's to file.
- No inbox write to pcrec-bench; the relay text above is for the manager.
