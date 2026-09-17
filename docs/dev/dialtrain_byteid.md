# [K59RUNG-BYTEID] — the dial+K59 train's byte-identity sweep (2026-09-17, lane byteid, sonnet)

Confirms, by corpus-wide measurement, `k59rung_report.md`'s structural claim
(§4): the dial+K59 train (merge `cf0962e3`, carrying lane/dialimpl's
`--tune`/`RX_TUNE`/abi-26 landing and lane/k59rung's premul drop-ladder rung)
changes no emitted byte for any artifact that already compiled at the branch
point, BEYOND the RX_TUNE stamp's own known, constant delta.

## Method

`cmtfix_report.md`'s corpus-wide emit-diff methodology, applied to this
train instead of that lane's fix:

- **Baseline compiler**: built from `git archive` of the train's branch
  point — the first parent of `cf0962e3` (`git log --format=%P -1 cf0962e3`
  → `fce0959d33396e16f75af0b5c3aba895ff198d47 b6b9f9fab664cfbb10a44a25890c2cc716be8a8b`;
  first parent `fce0959d` is "main immediately before this merge"). Built
  separately in a scratch checkout, never sharing an object tree with the
  worktree.
- **Fixed compiler**: the merged main, `cf0962e3`, built in
  `worktrees/byteid`.
- **Corpus**: every `pattern`/`pattern-esc` block in the shipped `tests/`
  tree, enumerated via `--list-source` per file (never hand-parsed against
  the `.rxt` escape grammar) and decoded through the format's own
  `\t \n \r \\ \xNN` vocabulary to raw bytes, passed to each compiler via
  `argv` directly (never a shell string — `tests/base/comment_escape.rxt`'s
  own witness is exactly why a shell-string pattern is the wrong instrument
  here). **211 files, 3,938 pattern lines** — this is the current census
  (210 files / 3,936 blocks per `w234_report.md`'s own count) plus the
  `pattern-esc` productions `--list-source`'s column 19 disambiguates,
  which the older `pattern`-only counts in the tree do not include.
- **Flags**: DEFAULT — `-p rx -o <out>.c -- <pattern>` and nothing else, no
  `--tune`, no `--features`, no `-i`, no `--engine`/`--encoding` override.
  Same simplified-driver shape `cmtfix_report.md` used, and for the same
  reason: a plain sweep cannot supply the flags a module-gated pattern's own
  `.rxt` block would carry, so those patterns refuse identically on both
  sides rather than being fed anything — noise this sweep is not chartered
  to eliminate, only to keep out of the "mover" bucket.
- Each pattern compiled by both binaries to distinct per-index output paths
  in two separate directories; outputs byte-diffed directly (not through any
  tool that infers identity from a shared basename — `run_trie_identity.sh`'s
  own documented trap for this comparison shape does not apply here since
  nothing besides a direct `diff`/byte-compare touches these files).

Driver: `docs/dev/dialtrain_byteid_evidence/byteid_sweep.py` (this lane's
own scratchpad tool, archived alongside its output for reproduction).

## Result

| bucket | count |
|---|---:|
| both compiled, byte-identical | 0 |
| both refused (module-gated, unrelated to this train) | 2,438 |
| newly fixed (refused at baseline, compiles at fixed) | 0 |
| newly broken (compiled at baseline, refuses at fixed) | 0 |
| **movers** (both compiled, bytes differ) | **1,500** |
| total pattern lines | 3,938 |

**Every one of the 1,500 movers moves by exactly +27 bytes, with zero
exceptions** — confirmed both by a delta histogram (a single bucket, `+27
x1500`) and by full-diff inspection of a sample spanning the corpus's whole
size range (35,277 B up to 665,254 B baseline size). The 0-identical bucket
is expected, not a red flag: `RX_TUNE` is stamped unconditionally
(`src/gen/emit_dfa.c:7188`), so every artifact that compiles on both sides
gains it — the brief's own framing anticipated exactly this before any
measurement.

**The +27 bytes are entirely and only the predicted stamp**, verified by
full diff (not just size) on multiple movers across the size range:

```
7a8
> #define RX_TUNE "balanced"
705c706
<     .abi = 25,
---
>     .abi = 26,
```

Two hunks, always in this shape: (1) the inserted line
`#define RX_TUNE "balanced"\n` — 27 bytes exactly
(`len("#define RX_TUNE \"balanced\"\n".encode())` == 27, matching
`emit_dfa.c:7186`'s own comment, "the delta is 23-28 bytes (by token) for
both" — 27 is `"balanced"`'s own token length, the value every compile in
this sweep takes since none passes `--tune`/`config tune`); (2) the `.abi`
initializer's digit text moving `25` → `26`, same character count, **0 net
bytes** — lane dialimpl's own abi bump (`dialimpl_report.md`), riding this
same train. No other line in any diffed pair differs. No mover in this
sweep used a non-default `--prefix`, so the per-reader `+23..+28`-byte
variance `dialimpl_report.md` §"findings" names (the real witness's `+31`,
whose prefix is longer than `rx`) is not reachable by this sweep's own
driver and is not claimed reconciled here — see "What this does not cover"
below.

## Reconciling against dialimpl's §5.3a figures

`dialimpl_report.md`'s own manifest work (`docs/design/opt_dial_design.md`
§5.3a) predicted a per-reader delta of **23-28 bytes**, and its own real
`EMITTED_BYTES` witness moved **+31 bytes** — outside that range — traced to
a longer-than-`rx` prefix inflating the `#define <PREFIX>_TUNE "..."`
line's own macro-name length. This sweep's own population is EXCLUSIVELY
`--prefix rx` (the driver's default, unforced), so it cannot reproduce that
+31 witness — it is not a discrepancy, it is a different corner of the same
population dialimpl's own report already reconciled by hand at its own
witness. What this sweep adds is **the corpus-wide, prefix-fixed case**:
every one of 1,500 artifacts at the default prefix takes EXACTLY the
predicted 27-byte figure (`"balanced"`'s own 8-character token length under
`rx`'s 2-character prefix), with no artifact-to-artifact variance at all —
the delta is genuinely a per-token/per-prefix CONSTANT here, not a range,
because nothing in this sweep varies either axis.

## K59's own rung: unreached by this corpus, consistent with its own report

`k59rung_report.md`'s premul drop-ladder rung requires
`cx.size_cap_refused` (`src/core/compile.c:1074`) — provable only on an
artifact whose FIRST attempt already failed the emitted-size cap
(`compile.c:1671` is the only writer of that field, on a `size-cap-retry`
event). None of this sweep's 3,938 pattern lines reaches that state at
default flags: every compiling artifact compiled on its first attempt (no
`ESEL_SIZE_CAP_RETRY` path was exercised — the rung has no way to fire
without it), so this sweep neither confirms nor needs to confirm K59's own
no-move claim beyond what `k59rung_report.md` §4 already argues
structurally. Its own filed witness (`[^\p{C}\p{M}\p{P}]` under `-e utf8
--features unicode-props`) is not in this corpus and was not added to it —
the rung's own report already measured it directly.

## Verdict

**The identity claim holds without qualification beyond the known,
constant RX_TUNE stamp.** Zero movers whose delta is not exactly +27 bytes;
zero movers whose diff carries any hunk beyond the RX_TUNE insertion and
the co-occurring `.abi` digit substitution; zero newly-fixed or
newly-broken patterns. This corroborates `k59rung_report.md`'s own
structural no-byte-move argument (§4, "OWED" — "a full corpus byte-identity
sweep... was NOT re-run here") over the corpus it did not itself sweep, and
extends `dialimpl_report.md`'s single-witness reconciliation
(`+23-28`/measured `+31`) to the corpus's full size range at the default
prefix.

## What this does not cover

- **No non-default `--prefix` build.** The `+23..+28`-byte range in
  `opt_dial_design.md` §5.3a is a PREFIX-dependent figure
  (`#define <PREFIX>_TUNE`); this sweep's driver never varies `--prefix`,
  so it confirms the default-prefix constant exactly and says nothing new
  about the range's other end (dialimpl's own `+31` witness already covers
  that corner by hand).
- **No non-default `--tune`.** Every compile in this sweep is `balanced`
  (the unset default); a `min-size`/`speed`/etc. build's `RX_TUNE` token has
  a different length and therefore a different (but still per-token
  constant, by the same emitted-line mechanism) delta — not measured here,
  not claimed here.
- **No `--features`/`-i`/`--engine`/`--encoding` variation** — the
  2,438-pattern "both refuse" bucket is exactly the population this would
  have reached; `cmtfix_report.md`'s own precedent for treating that bucket
  as out of scope is followed here rather than re-litigated.
- **K59's own rung's population** (a compile that hits the size-cap retry
  path) has zero members in this sweep's corpus, as noted above — this
  sweep corroborates the STRUCTURAL argument that the rung cannot move an
  already-compiling artifact; it does not independently exercise the rung
  itself.

## Reproduction

`docs/dev/dialtrain_byteid_evidence/` (own `CLAUDE.md`): the sweep driver
(`byteid_sweep.py`), the full mover list (`movers.tsv`, 1,500 rows, all
delta +27), and the sweep's own stdout log (`sweep.log`). Baseline and
fixed compiler binaries are not archived (rebuild from the two commits
named above); emitted `.c` artifacts for the 1,500 movers are archived
(kept by the driver for inspection) but not committed — regenerate with the
same two compilers if needed.
