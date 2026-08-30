# lane w11 — [DD-13b.W1.1] work log

Branch `lane/w11`, from main `1ac1405`. Manager: pcrecdev1 / team-lead.

## Session start (2026-08-30)

- **HOLD ACKED** at 06:17. `.hold_ack` written (uncommitted). No `make`,
  no `gcc`, no built binary, no `tests/**/run*.sh`, no corpus-wide
  python/bash pass until the manager sends LIFT.
- **Setup fix**: the worktree had been created NESTED, at
  `worktrees/admin1/worktrees/w11`, instead of `worktrees/w11`.
  Tree was clean at 1ac1405 on `lane/w11`, so `git worktree move`
  relocated it to the briefed path and the empty leftover dir was
  removed. Reported to the manager.
- **Brief correction**: the brief names `tests/harness/verify_pcre2.py`.
  That file does not exist. The pcre2 differential is
  `tests/assertions/verify_pcre2.py` — which is exactly where w1_impl
  §3.1.1's correction block says it is (`run_assertions_tests.sh:60`).
  `tests/harness/` holds `run.sh`, `verify_rxt.py`, `driver.c`,
  `giveup.rxt`, `CLAUDE.md`. No impact on the work; noted so the next
  reader does not hunt for it.

## Reading done under the hold

w1_impl.md §0, §1 (1.1-1.8), §3.0, §3.1, §3.1.1, §3.3, §3.4, §3.5, §4,
§5, §6, §7; `docs/spec/table_contract.md`; `docs/spec/rxt_format.md`.

## Item log

(appended as items land)

### Item 1 — `--list-source` + the head parser — CODE LANDED (uncompiled, hold)

`src/parse/rxt_source.c` (new), `RxtSource`/`RxtRow` in `src/core/internal.h`,
`--list-source FILE` in `cli/main.c`.

Deviations from the note, both deliberate, both for the manager:

1. **One `RxtRow`, not `RxtDef`/`RxtTarget`/`RxtConfig`** (§1.2 F2 names
   four types). All four are (kind, name, value, settings, a list), and
   the dump is FILE ORDER — which per-kind arrays cannot express without
   a fifth structure to interleave them. One discriminated row; typed
   lookup is a filter. W1.2's target BUILD / W1.3's composer are what
   earn a definition-shaped record (D77).
2. **W1.1's CLI surface is `--list-source` alone** — no `--source`,
   `--target`, `--lib-path`, `--emit-composed`. §5's prose lists
   `--source`/`--lib-path` under W1.1, but §7.1's build order, §7.2's
   acceptance and §4's spec-hunk table all name only `--list-source` for
   this step (S11 — the flag surface — is assigned to W1.2). W1.1 has no
   build path for `--source` and no store scan for `--lib-path`, so both
   would be flags whose only behaviour is to refuse: built ahead of a
   consumer, which D77 forbids.

### Item 2 — the rxt-escape — LANDED WITH ITEM 1

Columns 4/5/15, vocabulary `\t \n \r \\ \xNN` (§1.8 RULED). Built in the
same change as the dump, before any differential could pass while
silently comparing shifted columns.

### A grammar tension resolved, and it needs the manager's ratification

format_design §1.3 gives a pattern block's `description` the full
`prose-value` production, which includes the `|` BLOCK SCALAR. §1.2's
lexical rule says a pattern block's lines are NOT indented, and a block
scalar IS indented continuation. Both cannot hold in the body.

RESOLVED CONSERVATIVELY: `|` is a HEAD form; a block's `description`
takes the one-line form only, refused by NAME in both parsers with the
reason stated. Reasons: (a) the body's no-indent rule is the one
R-COMPAT-1 and 3,265 blocks depend on, and §1.2 calls the head/body
asymmetry "the only one"; (b) a body block scalar would need continuation
parsing in run.sh's per-line loop — putting head-shaped parsing back into
the harness, which is exactly what §1.1's seam ruling removed.
MEASURED FREE: 0 corpus lines are indented, 0 blocks carry a
`description`, so no existing file reaches either reading.

### Item 4 — run.sh — CODE LANDED (unrun, hold)

BEGIN/END pin markers around the existing arm chain; the `have_block`
guard generalised to `perr`/`m`/`n`/`ms`/`ns`/`gu` (was on 6 directive
arms + `g`/`gp` only); `features only`, `name`, `description`, `encoding`
appended AFTER the END marker; `encoding` routed to `--encoding=` in
flush_block; the three new directives reset with the block.

MEASURED (grep/awk only, under the hold), and it reproduces the census
from a third direction — first-token census over the corpus:

    m 10552  n 6780  g 3942  pattern 3265  ns 3167  features 2146
    ms 1603  perr 384  gp 240  flags 36  gu 23  frames-buffer= 9
    engine 5  budget 3

  files 179 / pattern 3265 / expectation lines (m,n,ms,ns,gu,perr,g,gp)
  = 26691 — matching §1.7 and §3.0 to the digit.
  `name`, `description`, `encoding` occur as a first token 0 times, so
  appending their arms cannot change any existing line's meaning.

MEASURED: 0 corpus DIRECTIVE lines carry trailing whitespace (3 files
carry it on other lines, where it is data). run.sh's arms all end
`[[:space:]]*$` and accepted it; pcrec would have refused it. Fixed in
pcrec (`value_trimmed`) so the two parsers agree on the GRAMMAR rather
than by luck of the corpus.

## Close (2026-08-30)

All seven items CODED. Nothing compiled or run — the hold was never
lifted. Full deliverable: `docs/dev/lanes/w11_report.md`.

Items 3 and 5-7 land in `tests/rxtsource/`; the spec hunks in `8a0a918`;
the sabotage rows as S194-S203 with a new `rxtsource` mech arm registered
ahead of them.

Nine commits, `da10212`..`e708753`.

## Resume (2026-08-30, after the bench window 07:10-10:45)

At `ab770e3`. Build green, `make strict` clean, C1 measured green three-way
(8.2 s: legA 0.74 / legB 7.32 / legC 0.17). Resuming at item 6.
