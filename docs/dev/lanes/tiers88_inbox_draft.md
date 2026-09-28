# DRAFT — I-118, for the manager to commit into pcrec-bench's inbox_from_pcrec.md

(Lane tiers88: this is a DRAFT of the inbox item text only. It is not
committed to pcrec-bench — the manager is the sole writer there, D78. Next
free number checked against pcrec-bench/docs/dev/inbox_from_pcrec.md's tail
at draft time: last item is I-117, so this is I-118.)

---

## I-118 (2026-09-28, pcrec manager) — [FINDINGS-BENCH-TIERS]: four columns (DEFAULT/DECLARED/PROFILED/ORACLE-BEST), what's shipped on our side, and what we need from you

Frank's ruling on plan row [FINDINGS-BENCH-TIERS] (D125 phase-4 stock-take):
using measured subject data at compile time is part of an AOT compiler's
setup, not cheating, IF it is information a user has BEFORE seeing the
input and it is reported as its OWN column, never folded into the
headline. **The numbers come first** — you produce four columns as a
SCRATCH-tier measurement (this never enters `store/`, never ranks, never
changes a published pinned config) and we read them before anyone decides
whether to change anything published. This item is what pcrec's [FINDINGS]
row (B0-B6, all merged to main except B4, held — see §5) gives you to build
those four columns, plus what only you can answer.

### 1. The four columns, and what moves them

| column | what it is | pcrec-side mechanism |
|---|---|---|
| DEFAULT | today's headline, no hints | no `--analysis`, no `-I`; the chain is the built-in `default` bundle alone |
| DECLARED | a bundle named UP FRONT per subject CLASS, from a corpus DISJOINT from the bench subjects it's measured against | `--analysis NAME` naming a bundle sourced from a corpus the bundle's own subjects never touch |
| PROFILED | class data measured on a TRAINING split, tested on a held-out split of the SAME class | same mechanism, but the bundle is built from TRAIN subjects and measured only on TEST subjects (never the same instances) |
| ORACLE-BEST | per-cell max over pcrec's own generation-time configuration knobs, diagnostic only, never published | sweep `--engine=`, `--no-captures`, `--tune=` (see §4) |

The three deltas the plan row defines: `oracle-best − default` = selector
headroom (D119's measured gap; feeds pcrec's [SEL-COST]); `declared −
default` = what the findings data is worth; `oracle-best − declared` =
what hints cannot reach (engine/algorithm, not data).

### 2. DECLARED: naming a bundle from a disjoint corpus

The mechanism (`docs/spec/findings.md` §6-§7 on our tree, all merged to
main):

- **Building the bundle.** `build/pcrec-analyze --name NAME --retrieved
  DATE [--scan freq,cpfreq] [--source TOKEN] [--url U] [--ref R]
  [--license L] FILE | -` writes one `.rxt` bundle to stdout from a
  one-pass count over `FILE` (or stdin). `--scan` defaults to
  `freq,bigram`; ask for `cpfreq` too if you want the bundle to answer
  under `-e utf8` as well as `-e byte` (see the table below — `cpfreq`
  needs input that decodes as UTF-8, and is a hard error otherwise if
  requested). `--shard K/N` + `--merge` parallelize over a big corpus;
  `--check BUNDLE.rxt FILE` re-counts and confirms a bundle's rows.
  `analyze/` is a separate zero-dependency binary — it links nothing
  under `src/`/`cli/`/`lib/`, so it needs no pcrec build beyond `make`.
- **Naming it.** Save the printed bundle as `DIR/name.rxt` (the file's
  own directory entry must be exactly `<name>.rxt`) and compile with
  `-I DIR --analysis name` (or `pcrec-analyze`'s output composed by hand
  into a config's own `analysis name` line, `docs/spec/rxt_format.md`).
  Resolution is three stops in order (own file, then each `-I DIR`, then
  the built-in store) and always terminates at the built-in `default` by
  identity — `docs/spec/findings.md` §7 has the full table, including
  every refusal mode (bad name, cycle, oversize bundle, two bundles in
  one `-I` file).
- **Verifying what actually answered.** `pcrec --list-analysis NAME -I
  DIR` prints the resolved chain and, per (query, encoding), the exact
  digest a compile's `<PREFIX>_FINDINGS` stamp would carry — cross-check
  a DECLARED build's stamp against this before trusting the number.
  `rx_info.findings` (or the `<PREFIX>_FINDINGS` macro) on every compiled
  artifact names which bundle actually answered and its digest
  (`findings.md` §5) — this is how you prove a DECLARED cell consumed
  the bundle you meant, not silently the default.
- **Two shipped bundles already exist and may already fit a class you
  measure**: `weblog` (1 MB of Apache combined-format request lines,
  `elastic/examples`, Apache-2.0) and `log` (999,960 B of a SYNTHESIZED
  Hadoop-DataNode-shaped corpus — no licensable real one was found, and
  its provenance says so). Both declare `byte-rate` under `byte` (via
  `freq`) and under `utf8` (via `cpfreq`, `encode-utf8` — see below).
  `--analysis weblog` / `--analysis log` uses them with zero bundle
  authoring on your side. Neither was ever fit to any bench subject —
  RUNEST's (pcrec's own estimator-measurement lane) use of `weblog`-shaped
  data was evaluation-only, so if either corpus is a real fit for
  `bench/loglines`/`bench/email`-shaped subjects, it is DECLARED by
  construction, not PROFILED. Whether that's close enough, or you want a
  bench-authored corpus of the same shape instead, is your call (§6 Q4).
- **Disjointness proof.** The plan row asks for a bench-owned manifest
  proving DECLARED's corpus never touches the bench's own subject files.
  pcrec's own precedent for that proof shape (not a mechanism you inherit,
  just the argument form): a provenance review plus a grep of the corpus's
  own PROVENANCE record for any bench path. `pcrec-analyze`'s printed
  `provenance` block (source/url/ref/license/retrieved) is what a bundle
  already carries to make that grep possible.
- **`-e utf8` needs `cpfreq`, not `freq`.** A `freq`-only bundle declares
  `byte-rate` under `byte` alone; under `-e utf8` that bundle's answer is
  NONE (falls back to the default's own tie order, see §5). If any DECLARED
  or PROFILED class is measured under `-e utf8` (`bench/utf8`'s testees,
  or the `-utf8` engine siblings), scan `--scan freq,cpfreq` and make sure
  the source corpus actually contains non-ASCII bytes — an ASCII-only
  corpus makes `cpfreq`'s derived rates identical to `freq`'s (§0's own
  "on an ASCII-only sample this is exactly the freq view" fact), which
  answers the query but doesn't discriminate anything under utf8 (see the
  F3 gap in §5).

### 3. PROFILED: the train/test split

Mechanically identical to DECLARED (`pcrec-analyze` + `--analysis` + `-I`)
except WHERE the counted corpus comes from: a TRAIN split of the SAME
subject class the cell measures, with the bundle built ONLY from TRAIN and
the cell's timed subjects drawn ONLY from a disjoint TEST split — never the
same subject instance on both sides. This is the split discipline pcrec's
own [FINDINGS] design leaned on for its internal `markov1` acceptance
check (`docs/design/findings/design.md` §11.4 — four disjoint splits, the
accessor's ranking checked against an independent scorer on each), offered
here as the shape, not as a mechanism you inherit: your own subject
generators (`bench/loglines/gen_subjects.py`, `bench/email/gen_subjects.py`,
etc.) are what would produce two disjoint sets per class. We have no
opinion on how you split (held-out generator seed, held-out subject IDs,
a fresh generation run) — whatever you already have for cross-validation-
shaped work, if anything, is probably the right primitive (§6 Q1).

**No train-on-test, stated as the check**: the TEST subjects the cell
times must never appear in the corpus `pcrec-analyze` counted. The same
provenance-review-plus-grep proof from §2 applies, this time grepping
train corpus provenance against the TEST subject manifest rather than
against the bench's subject tree in general.

### 4. ORACLE-BEST: the configuration axes

Per-cell max over pcrec's own generation-time knobs — deliberately NOT
over which findings bundle is named (that's what DECLARED/PROFILED
measure; holding findings fixed there is what keeps `oracle-best −
declared` reading as "what hints cannot reach" rather than mixing the two
questions). We recommend holding the findings input fixed at whatever
DECLARED already named (or `default`, if none) for a given cell, and
sweeping only:

| axis | values | spec |
|---|---|---|
| engine | `--engine=dfa` \| `vm` \| `auto` (default) | `docs/spec/cli.md` §"--engine=E" |
| captures | default (captures-on) vs `--no-captures` | same section — only where the sub-bench's own expectations don't need captures; don't add this arm to a capture-bearing sub-bench, it isn't a legitimate config there |
| tune | `--tune=N`, N ∈ {-2,-1,0,1,2} (aliases `min-size`/`size`/`balanced`/`speed`/`max-speed`) | `docs/spec/tuning.md` §5 |

All three are ANSWER-IDENTITY-preserving by ruling (`--engine=dfa` refuses
outright rather than silently degrading when a pattern can't take it;
`--tune=` never changes an answer or a give-up, `docs/spec/limits.md`'s
K59 record) — so sweeping the full product on a cell that already passed
its own correctness gate carries no new correctness risk.

**Practical note**: `testees/pcrec/configs.toml` already has 31 pinned
configs covering much of the engine/captures/cflags product (`pcrec-auto`,
`-nocaps`, `-vm`, `-vm-in`, the deny-flag twins, the `-utf8` siblings), but
**none names `--tune=` yet** — ORACLE-BEST is the first customer for that
axis. Since this whole exercise is diagnostic and scratch-tier by the
plan row's own ruling, a `pcrecbench quick`/`pcrec-local`-shaped sweep (no
new pinned `configs.toml` rows, no `bench/capability` roster entries to
keep in sync) may be the cheaper way to get the numbers before deciding
whether any of this earns a permanent testee row (§6 Q3).

### 5. What's shipped today vs. what's still a gap

Shipped, merged to main, nothing further needed from us to run §2-§4 as
written: the analyzer (`build/pcrec-analyze`, B6), resolution + CLI +
listings (B2), the byte-rate accessor and its readers (B1), `cpfreq` +
`encode-utf8`/`encode-latin1` (B5), `--engine=`, `--no-captures`, `--tune=`
(all pre-date [FINDINGS] and are unaffected by it).

Gaps, filed rather than built (D77 — no measured need yet):

- **`run-rarity` (the `bigram` kind, `markov1`) has NO LIVE READER.**
  [FINDINGS] B4 is HELD (Frank's ruling, 2026-09-28: "no reader has a
  trigger yet" — the one designed customer needs an unbuilt row,
  [OPT-LITSCAN] S4). A bundle CAN carry a `bigram` block today (the
  analyzer's default `--scan` even produces one), and it will PARSE and
  resolve cleanly, but no compile decision consumes it — naming a bundle
  for its run-rarity data alone will move nothing measurable yet. If any
  DECLARED/PROFILED cell is built specifically to test run-rarity, hold
  it until B4 lands; the byte-rate kinds (`freq`/`cpfreq`) are the live
  ones today.
- **The default path has a known utf8 lottery, not yet fully fixed.**
  Under `-e utf8` with an ASCII-only bundle named (including the shipped
  `weblog`/`log` today — both are ASCII-only corpora), every non-ASCII
  byte ties at the rate floor, and the PICK reader's tie rule was fixed
  ([FIND-TIE], merged `72e3ae41`) but the underlying data still can't
  discriminate non-ASCII bytes from each other until a bundle sourced
  from real non-ASCII text exists ([FIND-UTF8-DEFAULT], filed, not
  scheduled). If a DECLARED/PROFILED cell is built under `-e utf8` against
  a corpus that is itself mostly ASCII, expect its byte-rate answer to be
  no more informative than DEFAULT's own tie order — a real effect, not a
  measurement bug, and worth calling out explicitly in whatever report
  reads these numbers.
- **No shipped bundle is sourced from a bench-subject-shaped corpus that
  ISN'T `weblog`/`log`.** `bench/capability`'s wild-imported patterns and
  `bench/altwide`'s synthetic alternations have no obvious matching
  corpus class; DECLARED/PROFILED for those probably needs a bench-
  authored corpus (§6 Q4) rather than one of pcrec's two shipped ones.

Nothing above blocks starting on `bench/loglines` and `bench/email` today.

### 6. Questions for the bench dev (pcrecdev2)

1. Do you already have a train/test subject-split primitive per
   sub-bench (for cross-validation-shaped work), or does PROFILED need
   fresh generator support? If the latter, is that small enough to fold
   into this pass, or its own row?
2. What existing report/reduce grain (`pcrecbench/reduce.py`'s set-grain
   shape, or a plainer per-pattern table) should the four-column output
   ride? Point us at the shape to reuse rather than have us invent one.
3. Is a `pcrec-local`/`pcrecbench quick`-style scratch sweep sufficient
   for a first numbers-only pass across the tune/engine/captures product,
   or do you want a dedicated scratch-store script given the cell count
   (4 columns × N patterns × several sub-benches × up to 5 tune notches
   for ORACLE-BEST)?
4. For DECLARED on `bench/loglines`/`bench/email`-shaped classes: is
   pcrec's shipped `weblog`/`log` close enough to count, or do you want a
   bench-authored, provably-disjoint corpus of the same shape (more
   honest, more work — your call, since you own the disjointness
   manifest)?
5. Where should the disjointness manifest and any bench-authored bundles
   live — beside each sub-bench (`bench/<name>/findings/`) or under one
   new top-level directory for this row specifically? We have no
   preference; whichever fits your existing layout.

Scheduling is yours; this is explicitly a "when it fits" charter item, not
a window request. Frank reads the four columns before any ruling on
whether this ever touches a published config.
