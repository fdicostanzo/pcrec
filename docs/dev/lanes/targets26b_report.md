# targets26b report: optimization-targets table rev 1 on Zen 4 cross-engine data

Deliverable: `docs/dev/optloop/targets_2026-10-26.md` rev 1 (replaces rev 0 in full). Facts only; no build, no
make, nothing run on the box beyond python reading the bench's report files (scratch scripts in the worktree's
gitignored `build/`). Ratios are pcrec / peer, > 1 = pcrec slower. Sources: window A (pcrec 9ae59f5d4 vs 6b2dbd3e,
2026-10-26) and window B (2026-10-19/20 re-baseline at 6b2dbd3e with jit, interp, rust, re2, onig, tre; vectorscan
excluded everywhere). Method: B-direct where the row exists; chained x(9ae/6b, window A); capability cross-window
(pcrec auto from A against B's engines, joined on the same subject). Typical ratio uncertainty +-5%, chained +-7%
(measured: same-pin pcrec A/B median 1.00, p5-p95 0.87-1.04).

## What changed from rev 0 (the headline)

1. On Zen 4 the **short-subject regime is essentially won**: 6 set-grain short cells and 1 capability short cell are
   >= x1.3 vs the best peer. Every other loss is large-subject scan throughput.
2. Several rev 0 rows closed or shrank: loglines `kv-quoted` x24.6 -> x0.99, altwide `sfx-64` x3.71 -> x0.34 (pcrec
   3x faster), utf8 `lit-cyr-run` x18 -> x1.38, `level-context` x10.5 -> x3.78. Others grew: bounded `ctx-*` vs rust
   x7 -> x19, utf8 `alt-distinct-lead` x7.3 -> x14.1, altwide `w-8` x11.5 -> x25.
3. **Auto is slower than pcrec's own forced vm on specific rows**: litrun `lit-l40/l31/l16/aws` x3.9/3.7/2.1/2.0
   (and vm-caps beats jit there), bounded `ctx-*` x2.1-2.4, and capability's hazard subjects x62-183 (iso8601,
   email-owasp). Plan row [SEL-COST] has the family ("losses flip sign by subject or regime"); this is new measured
   members, same direction as its seed.

## Top 8 by loss x population (score = n cells >= x1.3 x geometric-mean loss vs best non-pcrec)

| rank | target | n | geomean | max | score | source |
|---|---|---|---|---|---|---|
| 1 | T1 landmark / start-set / prefix search on sparse or non-matching text (bounded `ctx-*` x19-19.7 vs rust, `json-constant` x20.2, `stack-frame` x3.08 jit, `level-context` x3.78 rust, `asr-*`) | 15 | x5.75 | x20.2 | 86 | B direct; capability A->B |
| 2 | T2 single-literal / boundary-literal throughput (syntax `lit-cat`/`esc-*`/`mod-*` x3.2 rust, x1.44 jit; `esc-nl` x5.35; litrun `lit-l*` x1.4-2.3 jit; `union-select` x7.7 jit) | 30 | x2.26 | x7.7 | 68 | B direct; A->B |
| 3 | T3 hazard-run subjects (capability: iso8601 x22.2 vs jit, email-owasp x7.5, trim-nested-star x4.0, evil-alt-nested x3.7, pwd-strength x3.4) | 6 | x7.22 | x137 (re2) | 43 | A->B |
| 4 | T4 wide alternations (altwide 17 cells, `w-8` x25 vs rust; utf8 `alt-distinct-lead` x14.1) | 18 | x2.30 | x25.0 | 41 | B direct, no window A |
| 5 | T5 utf8 literal pick / caseless (`lit-sharp-s` x13.9 re2, `ci-sigma` x8.0, `lit-offset-at-head` x6.4) | 12 | x3.33 | x13.9 | 40 | B direct |
| 6 | T6 two-way prefix-sharing alternations (`foo\|foobar` x8.0 rust, `file-ext-order` x4.7, `keyword-prefix-order` x3.6, `alt-foo-tails` x7.86 jit) | 8 | x3.95 | x8.0 | 32 | A->B; B |
| 7 | T7 lookaround on the VM route (`lka-*`/`lkb-*` x1.9-4.1 vs jit) | 6 | x2.93 | x4.1 | 18 | B direct |
| 8 | T8 length / end-window reject (`cls-atleast-4096` short x7.55 vs rust, `cls-dot-rep` x2.3) | 3 | x4.90 | x7.5 | 15 | B direct |

Not ranked: T9 other backtracking vs jit (`bak-k-named` 2.1, `mod-j-uc` 1.5, `qnt-poss-quest` 1.72 chained x2.13, `line-80` 2.0,
`pw-8-64` 1.57; decline candidates except `qnt-poss-quest`), T10 concat-sqli (x3.2 re2, x2.87 rust; sentinel x1.26).
Scores are a coarse ordering by the manager's own formula (loss x population), not a measured benefit; the families'
causes are hypotheses (no artifact read).

## The bench's own top list, checked against my reading

All eight items agree (altwide `w-8` x25.02, bounded `ctx-*` x19.0-19.7, utf8 `alt-distinct-lead` x14.11 /
`lit-sharp-s` x13.88, litrun `alt-foo-tails` x7.86, bounded `cls-atleast-4096` short x7.55 / mc x6.79, syntax `esc-nl`
x5.35, loglines `level-context` x3.78 / short x3.12). Added from my reading: capability `moment-iso8601` x22 vs jit,
`json-constant` x20 vs rust, and the litrun auto-vs-vm gap. DOMINATED-SET: **no target row has a single subject above
90%**; closest are `trim-nested-star` (t-trim-match-60k 88%) and the hazard rows where a 60 KiB subject plus its 16 KiB
twin are ~100% (iso8601: t-trim-match-60k 79% + t-trim-nearmiss-16k 21%; email-owasp: t-evil-match-60k 79% +
t-evil-nearmiss-16k 21%); `ctx-*` is 95% on two letters subjects (t-letters-064k 76%, -016k 19%).

## The Q2 answer (capability iso8601 and email-owasp)

Both losses are confined to the long-run hazard subjects; on ordinary prose pcrec is x4-6 FASTER than jit.
iso8601's losing subjects are 61,440 B of mixed `\s` bytes (space, tab, VT, FF, CR, LF) and its 16 KiB near-miss
(a whitespace-class union); email-owasp's are 61,440 B of random lowercase letters and its near-miss (the class
`[a-zA-Z0-9_+&*-]`). Per subject: iso8601 pcrec auto 68.4 us vs jit 1.46 us vs vm-caps 0.374 us (rust 68.2 us);
email-owasp 23.2 us vs 1.46 us vs 0.375 us. Auto's 1.11 ns/B on the `\s` subjects equals trimreg's per-byte-loop
rate (1.19 ns/B), so the `\s` cases fit the SCANEDGE-SET hypothesis; the jit/vm 0.37-1.46 us (a reject, not a scan:
neither subject holds the pattern's required `-` / `@`) says a scan-edge fix alone leaves iso8601 ~x8 above jit.

## SCANEDGE-SET hypothesis list (full table in the doc, section 3)

Strong: `tail-space-eol` (known), `moment-iso8601` (t-trim-*, 1.11 ns/B), `trim-nested-star` (t-trim-match-60k, 0.78
ns/B). Plausible: `email-owasp` (class union on letters, but 0.38 ns/B). Weak/no: `evil-alt-nested` (single class
`[a-z]`), `pwd-strength-chain`, `line-80`/`pw-8-64` (`.` is one class), syntax `cls-v`/`cls-s-lc` (1-byte runs on prose).
Shape-only, unmeasured: loglines `stack-frame` (`[A-Za-z0-9_$]*` runs). Residual if built: iso8601 x22 -> ~x8 vs jit;
`trim-nested-star` x4 -> ~x1.

## Unfiled-row proposals (names and ids only; nothing filed)

- [REQBYTE-REJECT]: auto rejects on a missing required byte or minimum length before scanning (replaces rev 0's
  ANCH-ATTEMPT; T3 and T8 evidence).
- [WIDE-ALT-SCAN]: wide-alternation search kernel for altwide and `alt-distinct-lead` (rev 0's WIDE-ALT; [OPT-ALTHASH]
  is the nearest row).
- [SEL-COST] (existing): three new measured members (litrun, bounded `ctx-*`, capability hazards).

## New bench-only questions

Q-a re-run the two capability pcrec auto records (inconclusive-spread) so auto ranks against engines in one window;
Q-b altwide at 9ae59f5d4 (pin delta unmeasured); Q-c sentinel same-pass check for concat-sqli x1.26 (bench Q4);
Q-d is re2's 56 ns on the `\s` hazard subjects an accepted valid answer (re2 `\s` excludes VT; it sets the x137 set-grain
"best"); Q-e per-row no-match subject list so vectorscan can be re-admitted there, marked. (Q-f is pcrec-side: why auto
trails vm-caps on litrun and the hazard subjects.)

## Not done / limits

No code, artifact or src/ read: every cause is a hypothesis from timings and pattern text. Vectorscan excluded
everywhere (on `json-constant` it would be the fastest at the set-grain sum). Altwide and part of bounded/syntax/utf8
have no window-A row, so their 9ae59f5d4 ratios assume pin delta 1.0. Capability is cross-window (flagged in every row).
The sentinel x1.26 is from passes the bench says are 6 h apart. Subst section unchanged from rev 0 (window A, same-window).
Not read: window B `.md`/interpretation sidecars, bench store, wake.md.

## STATE AT HANDOFF

Branch lane/targets26b, committed (table rev 1 + this report). Rulings file
`docs/dev/lanes/targets26b_rulings.md` re-read before the final commit: "(none yet)", so no ruling applied. Validation:
none owed (no runs). Scratch scripts: `build/` in the worktree (gitignored, not committed).
