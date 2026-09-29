# EXECUTIVE SUMMARY — [B115]: `[FINDINGS-BENCH-TIERS]`'s first four-column read (2026-09-29)

For Frank. pcrec-bench ran the four-column FINDINGS read
([FINDINGS-BENCH-TIERS]'s own charter — DEFAULT / DECLARED / PROFILED /
ORACLE-BEST) for the first time, scratch tier, on 2026-09-28 21:01 to
2026-09-29 04:55 EDT on ubuntubudu (pcrec `f7f5a143`, abi 44), over
`loglines@0.1` (34 arms) and `email-specimen@0.2` (17 arms), 51 records ×
5 trials, all `measured`, load1 0.9-1.1 throughout.

Sources:
- pcrec-bench's ledger
  `/Users/fdicostanzo/pcrec-bench/docs/dev/ledgers/2026-09-29-b115-findings-tiers-f7f5a143.md`;
- outbox O-74;
- the archived tables,
  `/Users/fdicostanzo/pcrec-bench/docs/dev/measurements/2026-09-29-b115-findings-tiers-{loglines,email}.tsv`;
- pcrec's own dispositions, `docs/dev/decisions.md` D131.

## 1. FINDINGS

- **Correctness and scope.** 758 compile rows stamp the intended bundle
  digest; the 20 stampless rows are `level-context`'s expected DFA
  refusals (`>32000 states`). No wrong answers are read here — this run
  measures speed, not correctness.
- **DECLARED is data that can mislead.** Naming `weblog` up front makes
  two loglines patterns SLOWER on loglines' own mixed-format text:
  `iso-ts` ×1.469 (throughput) / ×1.838 (search) and `kv-quoted` ×1.037 /
  ×1.313 — weblog is Apache access-log text, and its `-`/`"` frequencies
  differ from the bench's own text. `DECLARED-log` (the same-domain
  bundle) is mixed too: `iso-ts` ×0.911/×0.966 faster, `http-5xx`
  ×1.168/×1.100 slower. Even a same-class bundle is not a free win.
- **PROFILED never measurably regresses a cell, and wins on three.**
  `stack-frame` ×0.721/×0.782 (the prefilter changes from
  `offset-set-bounded` to `run-pinned-bounded`), `http-5xx`
  ×0.900/×0.908, `iso-ts` ×0.911/×0.965 (no read stamp moved, but
  `program_sha256` did — see §5 below). Every other loglines cell is
  within +0.4%; email PROFILED (prose-trained) is 0.994-1.001 everywhere
  (no effect).
- **ORACLE-BEST headroom is ~0 on loglines and real on email's
  whole-subject forms.** Loglines: every cell ×0.989-1.001 except one
  noise-floor outlier (`floor` search ×0.968). Email: `floor` compliance
  runs ×0.648 under `vm tune 0`, `orig` compliance ×0.856 under
  `vm tune 2`, `floor` search ×0.916 under `vm tune −2` — the forced-VM
  route beats what `auto` selects, on whole-subject email forms only.
  `factored` compliance's five forced-VM arms give up with
  `PCRE2_ERR_FRAMES` on four subjects (a standing outcome since
  35e1ab1, not new); excluding them its own ORACLE-BEST is 1.000.
- **`--tune` changes the program at only two positions on this
  population.** dfa/auto move at `−2` only (40/40, 44/44); vm moves at
  `+1`/`+2` only (8/44 each); DEFAULT is byte-identical to tune 0
  everywhere checked. Five notches, at most two distinct programs per
  route — direct evidence for the D131 item 1 λ re-proposal (see
  `docs/design/cls_tree_design.md` §1.7.5, applied at D131 to
  `docs/design/opt_dial_design.md` §4 and `docs/spec/tuning.md`).

## 2. SURPRISES

- **A bundle from the wrong domain actively costs time, not just
  "doesn't help."** The charter framed DECLARED as a data-quality
  question ("what is the findings data worth"); the ledger shows the
  answer can be negative, and by a meaningful margin (×1.84 on `iso-ts`
  search) — motivating [FIND-DOMAIN-CHECK] below.
- **The selector headroom the D119 optimization-loop rows were built to
  close is almost entirely ABSENT on loglines, and concentrated instead
  on email's whole-subject forms.** [SEL-COST] was filed from short
  syntax-subbench patterns; this is the first evidence outside that
  subbench, and it narrows the population rather than confirming a
  general effect.
- **PROFILED's `iso-ts` win has no attributed mechanism.** None of the
  six stamps the bench reads moved, yet `program_sha256` did — a
  data-driven compile decision outside today's read set. Filed as
  [LIST-TABLES]'s first open instance (below), not chased further here.

## 3. IMPACT

- **No correctness risk; this is a speed-only read.**
- **The four-column charter's own deliverable is discharged.** Every
  actionable finding now has an owner: DECLARED's domain-mismatch risk
  → [FIND-DOMAIN-CHECK] (filed); the email selector headroom →
  [SEL-COST] (pulled forward); the unattributed PROFILED program change
  → [LIST-TABLES] (noted). [FINDINGS-BENCH-TIERS] itself is CLOSED and
  archived (`docs/dev/plan_completed.md`, D131 item 9).
- **PROFILED is the run's one honest positive result** and stays the
  recommended default path for a caller who has training data — it is
  never measurably slower anywhere in this run.

## 4. NEXT STEPS (D131 — the next optimization cycle is HELD; recommend and file)

| item | recommendation | owner |
|---|---|---|
| DECLARED domain risk | **FILED as `[FIND-DOMAIN-CHECK]`** (D131 item 7): recommend a bundle only after a domain-match check against a sample of the caller's own traffic. Design not scheduled. | stock-take |
| email whole-subject selector gap | **PULLED FORWARD into `[SEL-COST]`'s queue** (D131 item 8): `×0.648`/`×0.856` forced-VM vs auto is the first measured input outside the syntax subbench, and it is class-specific (whole-subject email forms), not general. | stock-take |
| PROFILED's unattributed `iso-ts` program move | **NOTED in `[LIST-TABLES]`** (D131, this row filed 2026-09-28): a live instance for that row's own STEP 0 census once opened — today no `--list-*`/stamp surface names which table fired. | stock-take |
| further passes on this ledger | Not recommended now (`--extended` sets, the compile-time axis, the seven unread stamp families, run-rarity while `[FINDINGS]` B4 is held) — Frank's to re-open. | Frank |
| bench questions | None outstanding from this ledger; O-74 is fully read into D131. | — |

---

# EXECUTIVE SUMMARY (addendum) — `[CLS-TREE]` S0: the ubuntubudu calibration (O-76/O-77, 2026-09-29)

The same session's second piece of measured evidence, filed alongside
B115 because both land in D131 together and both come out of the same
manager ten-item status list.

## 1. FINDINGS

- **The pinned five-constant λ table predicted nothing, twice.** Lane
  `clsfit`'s replay of the ubuntubudu run (`docs/design/cls_tree_design.md`
  §1.7.1, O-76) re-confirms the earlier refutation: the old `λ·Σops` term
  reads member r = +0.08 (19/36 correct kit orderings) on the fresh data.
  A refitted per-probe model — `ns/char = 2.095 + 3.892·mispredicts +
  0.189·branches − 0.090·loads + 0.095·deploads` — reads r = +0.98 across
  all arms (30/36 kit orderings), including on a held-out 09-11 run it was
  never fitted on (30/36, vs the old term's 17/36 on the same data).
  Per-probe time is branch MISPREDICTS, ~3.9 ns each.
- **No multi-section kit sectioning beats the whole-set tables at any
  measured price of time against bytes.** The whole-set three-stage table
  (`page3w`) is 1.26-4.50× faster than the fastest kit policy on member
  subjects, and faster in 57 of 60 set×regime cells — 3.2× faster than
  today's pinned middle for +11% bytes.
- **The fair-dispatch CLSPACK re-run (O-77) reverses the earlier byte-tier
  size argument.** With the dispatch confound removed (`--dispatch
  switch`), the kit's byte tier is the SLOWEST of the three table-free
  forms at every N (+13/+16/+19% vs the bitmap) — D129 Q5's premise
  amended. The shared atom table ties the bitmap on time and is smaller
  from N ≈ 11 sites.

## 2. IMPACT

- **RULED (D131 item 1):** the λ table is replaced with one kit constant
  (λ=4) plus a first-match rule over `page3w`/`page2w`/`bitmap1` — applied
  to `docs/design/opt_dial_design.md` §4 and `docs/spec/tuning.md`'s λ row
  in this same change (lane adm131).
- **`[OPT-CLSPACK]` PROMOTED to build** (D131 item 6): the atom table
  becomes the default byte-class table from N ≈ 11 sites up, replacing
  per-site bitmaps there.
- **`[CLS-TREE]` S2 RE-SCOPED** (D131 item 5): the kit's byte forms are a
  size-leaning `--tune` position only; the default byte-class form stays a
  table.

## 3. NEXT STEPS

| item | recommendation | owner |
|---|---|---|
| `[CLS-TREE]` S1 | Chartered (lane clss1), runs alongside `[UCP]` U2. | in flight |
| `[OPT-CLSPACK]` build | Awaits a build lane; not started. | stock-take |

See `docs/dev/plan.md`'s `[CLS-TREE]`/`[OPT-CLSPACK]` rows (this change)
for the full disposition text.
