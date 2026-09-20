# [TOUR-3] — one member reader, p_class_range extraction, comment pruning

Lane `tour3`, sonnet, opus review scoped to the K12 endpoint-rule claim
ordering. Branch `lane/tour3` from `c37d7338` (wave 2, per
`docs/dev/reviews/2026-09-20-frank-tour.md` [TOUR-3]). Three commits, one
per part of the brief, in order:

1. `1106dbca` — `cls_read_member`, one member reader for both endpoints.
2. `752cc049` — `p_class_range`, the range arm extracted.
3. `592e5687` — comment pruning, comment-only.

## Part 1: the claim sequences (before), and the helper (after)

### Before — LOW endpoint (`p_class`'s item-loop top, ~lines 1089-1110 at the
branch point)

1. `c = peekc(cx)` at the loop top; `if (c < 0) pcrec_ctx_fail(...)` (the
   class's own truncation check).
2. `quoted = cx->in_quote` captured — used again for the close-bracket
   check, `at_content_start`, and doorway 4b's guard, all of which run
   BEFORE the decode.
3. Doorway 4b (`[` inside the class) runs and, on decline, leaves `cx->pos`
   unmoved (`EXT_NOT_MINE: carry on, cursor unmoved`).
4. `cx->pos++` consumes the already-peeked `c`.
5. Decode: `!quoted && c=='\\'` → `lo = esc_class_value(cx, &loclaim)`
   (may set `loclaim` to `EXT_REFUSAL` with `ep_set_certain`, or
   `EXT_MEMBERS`, or leave it `EXT_NOT_MINE`); else `c>=0x80` →
   `cx->pos--; lo = lit_next_cp(cx)` (`loclaim` untouched); else
   `lo = c` (`loclaim` untouched).

### Before — HIGH endpoint (the range arm, ~lines 1171-1208 at the branch
point)

1. Quote-open MIRROR: `if (!cx->in_quote && live \Q) { pos+=2;
   in_quote=true; cls_skip(cx); }` — a hand copy of the loop-top's own
   open check, needed because this position is not at an item boundary.
2. Truncation check, gated `cx->in_quote && peekc(cx)<0` (narrower than
   the low endpoint's unconditional one, with its own comment explaining
   why: at the loop top an unquoted truncation is already caught by the
   `c<0` check that runs first there; at this position it cannot be,
   since there is no earlier check at all).
3. `hi_quoted = cx->in_quote`; `hc = nextc(cx)` (peek and consume fused).
4. Decode: the identical four-way rule as the low endpoint, into `hi`/
   `hiclaim`, with its own comment stating it decodes "exactly as the low
   member above does".

Both endpoints then feed `loclaim`/`hiclaim` into the SAME five K12 steps
(1: low's own refusal: `if (loclaim.what==REFUSAL && !ep_set_certain)
pcrec_ext_finish`; 3: high's own refusal, identical shape; 4:
`loclaim.what!=NOT_MINE || hiclaim.what!=NOT_MINE` → invalid range) —
all five checks (including step 2, the pair_opens short-circuit, and step 5, the scalar ordering) are untouched by this lane; only how `lo`/`loclaim` and
`hi`/`hiclaim` get PRODUCED changed.

### After — `cls_read_member(cx, opening, claim, quoted)`

```c
static int cls_read_member(Ctx *cx, size_t opening, ExtResult *claim, bool *quoted)
{
    if (!cx->in_quote && pcrec_feature_enabled(FEAT_QUOTING) &&
        peekc(cx) == '\\' && peekc2(cx) == 'Q') {
        cx->pos += 2;
        cx->in_quote = true;
        cls_skip(cx);   /* an immediately-empty quote dissolves too */
    }
    if (cx->in_quote && peekc(cx) < 0)
        pcrec_ctx_fail(cx, opening, "missing terminating ] for character class");
    *quoted = cx->in_quote;
    int c = nextc(cx);
    if (!*quoted && c == '\\')
        return esc_class_value(cx, claim);
    if (c >= 0x80) { cx->pos--; return (int)lit_next_cp(cx); }
    return c;
}
```

It performs its own quote-open+dissolve and its own (conditional on `cx->in_quote`, but now run at BOTH sites)
truncation check, then the four-way decode, unconditionally — at both call
sites. The low-endpoint call site (`lo = cls_read_member(cx, opening,
&loclaim, &quoted)`, reusing the loop's own `quoted` local) reaches these
two checks only AFTER the loop-top's own quote-open-continue and `c<0`
check have already run and nothing has moved `cx->pos` or `cx->in_quote`
in between (doorway 4b's decline is a documented no-move outcome) — so
both of `cls_read_member`'s own checks are PROVABLY NO-OPS there, not a
second, unreconciled copy of the same logic: same mechanism, one call site
where its own precondition is already established by the caller. At the
high endpoint (now inside `p_class_range`) there is no such earlier check,
so both fire live, replacing the removed mirror and truncation check
exactly. `nextc(cx)` at both sites is exactly `peekc(cx)` followed by
`cx->pos++` given the position is not at end (established either by the
loop's own `c<0` check, low endpoint, or by `cls_read_member`'s own
truncation check, high endpoint), so the decode's actual bytes and
`cx->pos` movement are unchanged in both directions.

Claim/return ordering is therefore identical to before: `loclaim`/
`hiclaim` are set (or left `NOT_MINE`) at the same relative point in the
surrounding code that steps 1/3/4 of the K12 rule already read them at —
nothing about WHEN a claim becomes visible to those four checks moved.

## Part 2: `p_class_range`

The dash lookahead itself (`cls_peek_past_dash`'s own `\E`-transparent
check, deciding whether to enter a range at all) stays in `p_class` — it
needs to run BEFORE committing to a range, on the low endpoint's already-
decoded `lo`. Everything from the dash onward — high-endpoint decode, the
K12 five-step comment and its steps 1/2/3/4/5, the interval add — moved
verbatim into `p_class_range(cx, opening, lo, &loclaim, &set)`, a `void`
function with a plain-first header (HDR-2: "Parses a class range's high
endpoint and adds the resulting interval to `set`…", then the invariant
and the K12 citation after).

## Part 3: pruning

Every measured PCRE2 cell in the function is kept **verbatim**, including
the four named in the brief:

| cell | kept where |
|---|---|
| `[a\t-\tz]` is a-z | `p_class`, the "xx: deletion precedes RANGE PARSING" comment right before the dash-lookahead `if` |
| `[\Q^\E]` does not negate | `p_class`'s loop-top `[M4-QUOTING]` quote-open comment |
| `[[:alpha:]-z]` is error 150 | two places: doorway 4b's K12 low-side comment, and the MOD-0.3c produced-members comment right below it |
| `[\Qa-b\E]` is `{a,-,b}` | `p_class`, the `!cx->in_quote` load-bearing comment right before the dash-lookahead `if` |

Plus every other measured cell already in the function (K12's own five —
`[\A-z]`/`[[.a.]-z]`/`[0-[:digit:]]`/`[\d-\A]`/`[0-\d]`/`[\d-z]`/`[\d-\w]`/
`[z-a]`/`[0-\p{Foo}]`, now in `p_class_range`'s header; `[\Qa]b\E]`/
`[\Q[:alpha:]\E]`; `[\p{Lu}k]`/`[\p{Lu}x]`; `[^k]` caseless; `[x[:alpha:]-z]`)
— none of these blocks were touched by the pruning commit.

**Pruned** (commit 3), all three genuinely comparative-to-a-prior-state
narrative rather than a stated current invariant:

- The `[M5.0 stage 4]` "produced members accumulate separately" comment's
  second paragraph: `"the fold that used to run over the merged set was
  the ASCII one…"` → trimmed to the current-state fact (`UNDER byte THIS
  CHANGES NOTHING: every produced set reaching the union is already
  either ASCII-closed…`). First paragraph (the measured `\p{Lu}k`/
  `\p{Lu}x` cells) untouched.
- The `[M5.0 stage 1]` negation comment: `"the ONLY thing that moved is
  what 'everything else' means… instead of within a bitmap's implicit
  0..255"` → trimmed to state the current rule (`the complement is taken
  within [0, MAXCP(enc)] (§2.7.1) — under --encoding=byte that is the
  same function on the same set as a bitmap's implicit 0..255`), keeping
  the sabotage row S08 citation.
- The `[M5.0 stage 4]` fold-order comment: `"the ORDER of the last two is
  unchanged… what moved is that the union now happens between them
  instead of before both"` → trimmed to state the order plainly, keeping
  the `§4.3`/`[^k]` measured cell and the `prod` cross-reference.

**One deviation from the brief's exact sequencing, reported honestly**:
the R9/SPEC-FA range-endpoint comment (`"A RANGE ENDPOINT MAY NOT BE A
CLASS-OPENING CONSTRUCT… 546 instances in a 1,530-pattern sweep… It
survived every suite because…"`) is the sharpest wave-narrative block in
the function, and I trimmed it to its invariant + the existing `(R9/
SPEC-FA)` citation while writing `p_class_range` in commit 2 (the
extraction), rather than carrying it over verbatim and trimming it
separately in commit 3. The three-commit boundary is therefore not
perfectly clean on this one block; every other block was untouched until
its own designated commit. Net result across all three commits is
unaffected — I flag it because the brief was explicit about one-commit-
each and I did not fully hold that line here.

## Function list, line ranges, code/comment counts

At branch point `1994eab9`: `p_class`, lines 980-1265, **111 code / 167
comment** lines (24 comment blocks, per the brief's own measurement).

Current tree (after all three commits), `src/parse/parse.c`:

| function | lines | code | comment | blank |
|---|---|---|---|---|
| `cls_read_member` | 972-1012 (41) | 17 | 24 | 0 |
| `p_class_range` | 1014-1073 (60) | 23 | 37 | 0 |
| `p_class` | 1075-1257 (183) | 74 | 101 | 8 |
| **total** | **284** | **114** | **162** | **8** |

(Line-split counted by the same simple in-comment-block heuristic as the
brief's own 111/167 figure; small discrepancies against a hand count are
expected at the boundary lines.) Code lines are roughly flat (111→114,
the three new function signatures/braces accounting for the difference);
comment lines drop modestly (167→162, all three from part 3's pruning);
the real change is that the previous 286-line single function is now
three focused units, the largest 183 lines — `p_class`'s own loop, with
the four-way decode and the range mechanics both read from their own
named, single-purpose functions rather than inline.

## Re-aimed anchors

None. `python3 scripts/m6read_check_sab_anchors.py` reports **285/285
anchor sites resolving** on this branch (269 sabotage rows) with zero
re-aims needed — no `SAB_BEFORE` text in `tests/mech/sabotages/` lands
inside the specific lines this lane relocated or re-indented (confirmed
by the script itself; per `docs/dev/coding_guide.md` §3.4, a
re-indentation would have broken an anchor whose planted text includes
it, and none did).

## Validation

All commands run from `/Users/fdicostanzo/pcrec/worktrees/tour3`.

- `make -j4 CC=gcc-16` — clean, after every commit.
- `make strict CC=gcc-16` — `strict: whole tree compiles clean with
  -Werror -Wshadow`, after every commit.
- Four contract cells, both compile-shape and match-shape:
  - `[a<TAB>-<TAB>z]` under `(?xx)` (extended in-class whitespace
    deletion — the escaped `\t` two-character spelling is NOT what this
    cell measures; that decodes to a literal tab byte via
    `esc_class_value` and does not participate in `xx` deletion at all):
    matches `a`, `m`, `z`; not `A`, `0`.
  - `[\Q^\E]` (`--features quoting`): compiles; the class is the single
    member `^`, not a negated empty class.
  - `[[:alpha:]-z]`: `pcrec: invalid range in character class` (error
    150), `rc=1`.
  - `[\Qa-b\E]` (`--features quoting`): compiles; matches `a`, `-`, `b`;
    not `c`, `5` — the three literal members, not the range a-b.
- `bash tests/harness/run.sh tests/classes/` — **75 passed, 0 failed**
  (2 entry files, 0 pattern-compile failures).
- `bash tests/reject/run_reject_tests.sh` — **615 checks passed, 0
  failed** (286 rejections checked, 127 rows iterated, 108 accept
  controls, 0 known-wrong pinned, no pattern asserted twice).
- `bash tests/registry/run_registry_tests.sh` (includes PC-3 against
  libpcre2) — log: `build/tour3/registry.log` (973 lines). Five
  `== Summary ==` sections, **620 checks passed / 0 failed** total
  (225 + 209 PC-3 + 108 + 24 + 54), zero `FAIL` lines anywhere in the
  log. PC-3 green on this box as expected.
- `python3 scripts/m6read_check_sab_anchors.py` — **285/285 anchor sites
  resolve** (269 sabotage rows).
- `make test-codegen CC=gcc-16` — **9/10 scripts passed** (65 checks
  passed, 0 failed within the passing 9), the standing darwin `nm
  arm_a.o` probe red as the sole failure — pre-existing per
  `docs/dev/wake.md`-era notes, unrelated to this diff (nothing in
  `test-codegen`'s 65 passing checks touches `src/parse/`).
- `scripts/emit_sweep.py --ref 78058db7` — **launched in the background
  as this lane's last act**, per BOILERPLATE's DO-THEN-FINISH: an
  unchanged AST should emit identical C, across all five streams (corpus
  `.c` at default engine, corpus `.c` forced VM, corpus `--emit-ir` at
  forced VM, composition, registry dumps). **OWED**: log at
  `/Users/fdicostanzo/pcrec/worktrees/tour3/build/tour3/emit_sweep.log`.
  Launched with `timeout 900`; completion trailer is the `elapsed: N.Ns`
  line preceded by the `population: argv=… composition_files=…` line and
  the five per-stream summary lines (`t1`..`t5`, each stating its own
  mover/asymmetric count) — expect **0 movers / 0 asymmetric** on all
  five, an unchanged-AST result, since nothing in this lane touches what
  gets emitted, only how the parser reads a class.

## Summary

VALIDATION COMPLETE except `scripts/emit_sweep.py`, which is OWED — log
path and expected completion shape above. Everything else in the brief's
proof list is green: build, strict, the four contract cells (compile AND
match), tests/classes (75/0), the reject table (615/0), the registry
checks including PC-3 (620/0 across five sections), and the sabotage
anchor re-verification (285/285, zero re-aims). `test-codegen` is 9/10
with the standing pre-existing darwin red, matching the brief's stated
known state exactly.

## Manager/review addendum (2026-09-20, lane tour3rev, opus, read-only)

VERDICT: ordering PRESERVED. Path enumeration BEFORE vs AFTER at both
sites diffs empty; 93 curated patterns x 4 feature configurations (372
cells) and a generated sweep of 6,790 patterns x 6 configurations (40,740
cells, 984 distinct answers) are byte-identical between the pre-tour3 and
post-tour3 binaries. Three report inaccuracies corrected above (five K12
steps, not four; the helper's truncation check is conditional on
`cx->in_quote`, what is unconditional is that it runs at both sites; a
typo). One latent point now stated in `cls_read_member`'s header: at the
low site the loop's `quoted` local is overwritten by the read-time value,
dead after the call on every path today. One OUT-OF-SCOPE pre-existing
divergence found and CONFIRMED by the manager against local libpcre2
10.48: `[0-\E]` under `--features quoting` — see known_issues.md K62.
