# D27-blinded acceptance corpus: module `assertions`

Author: a D27-blinded test writer, working only inside
`worktrees/asrtd27-cell` (no `.git`, no `src/`, no `tests/`, no journal or
plan). Every expectation below was derived from PCRE2's documented
semantics for `\A \z \Z \b \B (?m) \G \K` and then measured against the
real `libpcre2-8` runtime on this box (10.46-1build1) — never copied from
memory, never taken from pcrec's own output. Where pcrec's *actual*
behavior was checked against these expectations (see "Verification against
pcrec" below), it matched on every single case. That is itself the
headline finding, stated plainly rather than left implicit.

## Files

| File | Blocks | m/n/ms/ns lines | g lines | perr | Focus |
|---|---|---|---|---|---|
| `anchors_abs.rxt` | 25 | 48 | 7 | 0 | `\A` `\z` `\Z`: placement, quantifier interaction, empty subject, boundary-of-subject, the `\Z`/`\z`/`$` trailing-newline triad |
| `word_boundary.rxt` | 12 | 27 | 2 | 0 | `\b` `\B`: subject edges, startpos>0 context-byte-before, composition with classes/alternation/quantifiers/groups |
| `multiline.rxt` | 16 | 28 | 2 | 0 | `(?m)`: scoped `(?m:...)`, `(?-m)`/`(?-m:...)` toggling, one- vs two-trailing-newline `^` carve-out, interaction with `\A`/`\Z` |
| `gstart.rxt` | 8 | 18 | 2 | 0 | `\G`: nonzero startpos, hand-replayed find-all loop (tokenizer behavior), composition with `\K` |
| `kreset.rxt` | 14 | 23 | 7 | 0 | `\K`: inside groups/alternation, multiple `\K`, `\K` under quantifiers, empty-report-after-consuming-bytes, find-all loop |
| `composition.rxt` | 7 | 14 | 1 | 0 | 2+ of the eight constructs together in one pattern |
| `syntax_errors.rxt` | 37 | 0 | 0 | 37 | genuine PCRE2 compile-time rejections (bare-assertion quantification, `\K` in lookaround) |
| `gating.rxt` | 26 | 8 | 0 | 18 (all gate-only) | `--features` refusal direction, both directions, for all eight constructs |
| **Total** | **145** | **166** | **21** | **55** | |

Counts above are grep-counted directly from the committed files
(`grep -c '^pattern '`, etc.) — not hand-tallied — and match `oracle.py`'s
own per-file pass counts exactly (below).

## Oracle verification

**`oracle.py`** (ships in this directory, imports `lib_pcre2.py`) is the
reusable, independent re-checker: it re-parses every `.rxt` file per the
grammar in `docs/testing.md`, and re-queries real libpcre2 for every `m` /
`n` / `ms` / `ns` / `g` / `gp` line and every non-gate-only `perr` block —
it does not trust or import the generator (`mkcorpus.py`) that first wrote
these files. Run it from the reviewer's checkout with:

```sh
python3 tests/assertions/d27/oracle.py tests/assertions/d27
```

(or from this cell: `python3 oracle.py .`). Latest run, this box:

```
anchors_abs.rxt: 55 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
composition.rxt: 15 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
gating.rxt: 8 passed, 0 failed, 18 gate-only skipped, 0 unverifiable skipped
gstart.rxt: 20 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
kreset.rxt: 30 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
multiline.rxt: 30 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
syntax_errors.rxt: 37 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
word_boundary.rxt: 29 passed, 0 failed, 0 gate-only skipped, 0 unverifiable skipped
---
TOTAL: 224 passed, 0 failed, 18 gate-only (pcrec-policy, not oracle-checkable), 0 unverifiable (excluded, see file comments)
```

**Every** m/n/ms/ns/g line in the corpus (224 of them) is oracle-checked;
there are **zero** `# unverifiable:`-excluded cells — nothing in this
corpus needed to fall back to an unverified guess. The only lines
`oracle.py` does not check are the 18 `perr` blocks in `gating.rxt` marked
`# pcrec-gate-only` immediately above their `pattern` line: those assert
pcrec's own module-gating *policy* ("refuse, naming module X"), which is
not a PCRE2 concept at all — real libpcre2 has no module system and
accepts all eight constructs unconditionally. `oracle.py` skips them by
design, counts them separately, and never silently folds them into the
pass total.

### Oracle mechanism: ctypes over the system `libpcre2-8`, not a compiled C probe

The brief's suggested default was a small `probe.c` linked
`-lpcre2-8`. This box has `libpcre2-8-0` (the runtime, 10.46-1build1)
but **no `libpcre2-dev`**: no `pcre2.h`, and no `libpcre2-8.so` developer
symlink (only `libpcre2-8.so.0` / `.so.0.14.0`), so `gcc probe.c
-lpcre2-8` cannot link on this box. `lib_pcre2.py` instead binds the
handful of needed entry points (`pcre2_compile_8`, `pcre2_match_8`,
`pcre2_get_ovector_pointer_8`, etc.) directly off `libpcre2-8.so.0` via
`ctypes`, by signature rather than by header — exactly the fallback the
brief names ("or python ctypes over libpcre2-8"). **`options` is `0` for
every compile and match call in the committed corpus, with no exception.**
`lib_pcre2.py`/`oracle.py` retain a `PCRE2_CASELESS` capability (`caseless=`
on `match`/`compiles`/`compile_error`, honouring a block's `flags i`
directive) for any future corpus that needs it, but nothing in this
directory currently exercises it — see the merge-review note below for
why.

**Merge-review fix (post-authoring):** the first submitted revision had
one `flags i` cell (`\bcat\b` on `"CAT"`, in `word_boundary.rxt`). Review
found that the in-tree libpcre2 checker which re-verifies this directory
on every `make test` is deliberately pinned at options=0 with no caseless
mode project-wide ("adopting any flag is a deliberate re-measurement
event") — so that cell was oracle-true (this corpus's own `oracle.py`
confirmed it via `PCRE2_CASELESS`) but unverifiable by the in-tree
checker, which would see it fail at options=0. Fixed by moving the
caselessness INTO the pattern instead: the cell is now
`(?i)\bcat\b` on `"CAT"` (module `modifiers`, already default-enabled via
`std1`, added explicitly to that block's `features` line), fully
verifiable by any options=0-pinned oracle. Same coverage intent (caseless
matching composed with `\b`), same case count, re-verified green by both
`oracle.py` (224/224) and against `build/pcrec` (224/224) after the
change.

**A methodological note, in the interest of not hiding a scare:** during
early exploratory probing (before any `.rxt` content existed), one
multi-call interactive script produced a single anomalous reading for
`(?m)^` on `"a\n"` at `startpos=1` — a match where every later, isolated
re-check (five independent fresh Python processes, plus the direct raw-
ctypes re-implementation used to sanity-check `lib_pcre2.py` itself)
consistently returned no match. It was never reproduced again despite
deliberately trying, was never used to derive a committed expectation
(the committed corpus was built afterward, case-by-case, from the
self-checking `mkcorpus.py` generator, which raises immediately if a
case's designed-in assumption disagrees with the live oracle), and
`oracle.py`'s final independent pass over the committed files — a
completely separate code path from generation — re-confirms every one of
them at 0 failures. Recorded here rather than quietly dropped, per the
project's own standing lesson about controls sharing a source with what
they control: the generator and the final checker are two different
programs precisely so this class of problem gets a second, independent
look before anything lands.

### `perr` / syntax-error oracle scope

`syntax_errors.rxt`'s 37 `perr` blocks are all genuine PCRE2 syntax
rejections, oracle-checked via `lib_pcre2.compile_error`: every bare
zero-width assertion in this module (`\A \z \Z \b \B \G \K`, and the
`(?m)` group itself) is unrepeatable — PCRE2 error 109 ("quantifier does
not follow a repeatable item"), checked in five quantifier shapes per
construct (`*`, `+`, `?`, `{2,3}`, lazy `*?`) — plus one construct-specific
case, `\K` inside a lookaround (PCRE2 error 199, "`\K` is not allowed in
lookarounds"), checked even though pcrec's `lookaround` module is not yet
implemented (pcrec refuses this pattern today for an unrelated reason —
see FINDINGS below).

## Coverage axes (per the brief)

- **Each construct alone**: every one of the eight has its own leading
  block(s) in its home file.
- **Composed with each other**: `composition.rxt`, plus incidental pairs
  inside the single-construct files (e.g. `\A` + `\Z` in `anchors_abs.rxt`,
  `\K` + `(?m)` in `kreset.rxt`, `\G` + `\K` in `gstart.rxt`).
- **Alternation, quantifiers, capturing groups, classes**: present in
  nearly every file — see e.g. `(\Aa)+`, `\b(cat|dog)\b`,
  `(?m)^(a|b)$`, `(a\K)+b`, `\A[a-c]+`.
- **Leading/mid/trailing placement**: explicit for `\A`/`\z`
  (`anchors_abs.rxt` — including the *unsatisfiable* mid/trailing `\A`
  and leading `\z` placements, which are real, deliberate coverage, not
  omissions).
- **Empty-subject and boundary-of-subject**: one dedicated block per
  construct across the relevant files (`\A`/`\z`/`\Z`/`\b`/`\B`/`\G`/`\K`
  each get an empty-subject case; `startpos == len(subject)` is covered
  for `\A`/`\z`/`\G`).
- **`\G` with nonzero startpos and find-all iteration**: `gstart.rxt`;
  the loop is `docs/spec/match_api.md` §3.1's exact algorithm, hand-
  replayed as a sequence of `ms`/`ns` cases (the `.rxt` format has no
  native find-all primitive) via `mkcorpus.py`'s `findall_loop`/
  `emit_loop`. This reproduces the spec's own worked example verbatim
  from a fresh measurement (`\G\w+` over `"ab ab ab"` — tokenizer, stops
  at the first gap) rather than copying the doc's numbers.
- **`\K` moving the reported start**, including inside groups/alternation,
  multiple `\K`, and under quantifiers: `kreset.rxt`, cross-checked
  against `docs/spec/match_api.md`'s own two worked find-all examples
  (`ab\K` over `"ababab"` → `2,2 6,6`; `a\Kb` over `"ababab"` →
  `1,2 3,4 5,6"`) — both reproduced here from fresh oracle measurements
  and both matched exactly.
- **`(?m)` scoped / off / mid-pattern**: `(?m:^a)$`, `^a(?m:$)`,
  `(?m)^a(?-m)^b`, `(?m)^a(?-m:^b)` in `multiline.rxt`.
- **`\b`/`\B` at subject edges and at startpos>0**: `word_boundary.rxt`,
  including the context-byte-BEFORE-startpos cells the brief specifically
  flagged (`\bcat` on `"xcat"` at startpos 1 fails; on `" cat"` at
  startpos 1 succeeds — the byte at `startpos-1`, outside the searched
  range, still governs the boundary test).
- **`\Z` vs `\z` vs `$`, with/without trailing newline(s)**: the explicit
  triad in `anchors_abs.rxt` (no newline / one / two trailing newlines,
  all three constructs, same subjects) plus the CRLF cell showing this
  build's libpcre2 default newline convention is LF-only (measured via
  `pcre2_config_8(PCRE2_CONFIG_NEWLINE)` → `2`/`LF`), so `\r\n` is not
  treated as one newline unit for the carve-out.
- **Syntax-error spellings**: `syntax_errors.rxt`, above.
- **Refusal direction (with/without `--features`)**: `gating.rxt`, both
  directions, all eight constructs — see FINDINGS for `(?m)`'s two-module
  shape.

## Verification against pcrec

Not part of the required deliverable, but run before hand-back per the
brief ("you may run pcrec freely... to record what pcrec DOES"): every
block in all eight files was compiled with the cell's `build/pcrec`
(passing each block's own `features`, and `-i` if a block ever carries
`flags i` — none currently do, per the merge-review fix above), linked against a small
driver synthesized from `docs/testing.md`'s documented protocol (this
cell has no access to the real `tests/harness/driver.c` — D27 blindness;
the synthesized driver implements the same documented contract: decode
nothing itself, take startpos as a second argument, print `match <pairs>`
or `nomatch`), and every case's actual output was compared against the
`.rxt` file's own recorded expectation.

**Result: 224/224 m/n/ms/ns/g checks passed, all 18 gate-only `perr`
blocks in `gating.rxt` refused exactly as expected (nonzero exit, correct
direction), 0 unexpected compile failures, 0 unexpected compile
successes, 0 divergences of any kind.** pcrec's `assertions` module
matches every oracle-derived expectation in this corpus, including every
subtle case: the one-vs-two-trailing-newline carve-out for both `\Z` and
`(?m)^`, `\K` resetting under quantifiers/alternation/multiple-`\K`
without disturbing group spans, `\G`'s tokenizer semantics under the
find-all loop, and the word-boundary context-byte-before-startpos rule.

## FINDINGS

1. **No pcrec/libpcre2 divergence found.** Every one of the 224
   oracle-verified expectations in this corpus, run against the real
   compiled artifact, matched. This is a genuine, actively-checked
   negative result, not an absence of testing — see "Verification
   against pcrec" above for the exact count and method.

2. **`(?m)` is gated by TWO pcrec modules, not one — a real,
   pcrec-specific fact worth the reviewer's attention, not a bug.** The
   brief's coverage list treats `(?m)` as one of the assertions module's
   eight constructs, and the general refusal-direction rule ("without
   `--features assertions`, refuse naming the module") holds for the
   other seven — but not cleanly for `(?m)`. Measured directly against
   `build/pcrec`:
   - Default features (`std1` = `classes,modifiers`): `pcrec: inline
     option 'm' (multiline) requires module 'assertions' (pattern offset
     2)` — the `(?m...)` GROUP SYNTAX parses fine (`modifiers` is already
     in `std1`), but the MULTILINE MATCHING EFFECT is refused, naming
     `assertions`.
   - `--features none`: `pcrec: (?m...) requires module 'modifiers'
     (pattern offset 0)` — now the group syntax itself is refused, naming
     a *different* module.
   - `--features modifiers` alone: same failure as the default-features
     case (effect refused, names `assertions`).
   - `--features assertions` alone: same failure as the `none` case
     (syntax refused, names `modifiers`).
   - `--features modifiers,assertions`: compiles and matches correctly.

   `gating.rxt` documents and exercises all four combinations explicitly.
   This is very likely intentional layering (the inline-option group is
   generic `modifiers` machinery; the specific multiline *effect* belongs
   to `assertions`), not a defect — but it means a reader treating "the
   assertions module" as a single gate for all eight constructs, as the
   brief's framing invites, will be surprised by `(?m)` specifically, and
   the two-module shape is easy to miss if only the default-features
   refusal is ever checked (which alone looks exactly like every other
   construct's single-module refusal, just naming a module that happens
   to already satisfy the OTHER half).

3. **This build's libpcre2 default newline convention is LF-only**
   (`pcre2_config_8(PCRE2_CONFIG_NEWLINE)` → `2`), confirmed directly
   rather than assumed — relevant to anyone re-deriving these
   expectations on a differently-configured libpcre2 build, where the
   `\Z`-under-CRLF cell in `anchors_abs.rxt` could read differently.

4. **Environment: no `libpcre2-dev` on this box.** No `pcre2.h`, no
   `libpcre2-8.so` symlink — a compiled C probe cannot link here. The
   oracle uses `ctypes` over `libpcre2-8.so.0` directly instead (see
   "Oracle mechanism" above); this is a box property, not a corpus defect,
   but worth flagging since the brief's default suggestion assumed the
   dev package.

## Unverifiable / excluded cases

None. Every `m`/`n`/`ms`/`ns`/`g` expectation in this corpus is
oracle-verified; there are zero `# unverifiable:`-marked cells. The only
exclusion mechanism used at all is `# pcrec-gate-only` (18 cells, all in
`gating.rxt`), which is not an *unverifiable* case in the sense the brief
means — it is a case that is correctly outside the oracle's domain by
construction (pcrec policy, not PCRE2 semantics), verified instead
directly against the real `build/pcrec` (see "Verification against
pcrec").

## Disclosure: injected content outside the cell allowlist

Per the D27 process rules, listing everything received at spawn time that
lay outside `$CELL` (`worktrees/asrtd27-cell`, containing only
`docs/testing.md`, `docs/spec/match_api.md`, and `build/`):

- **The session/project-root `CLAUDE.md`** (`/home/duxevents/pcrec/CLAUDE.md`)
  was injected in full as harness-level system context (the "claudeMd"
  block), describing pcrec's repository-scope mandate, build/test
  commands, the D26 compatibility standard, the doc map, and the D27/
  subagent-tiering conventions themselves. Not read from the cell; not
  acted on beyond the repository-scope mandate it restates (which the
  task brief also restates independently) and the general shape of the
  D27 process (also restated in the brief). No `src/`, `tests/`, plan, or
  journal content was in it.
- **The user's memory index**, `MEMORY.md`
  (`/home/duxevents/.claude/projects/-home-duxevents-pcrec/memory/MEMORY.md`),
  was injected as a three-line index: `pcrec process preferences`, `pcrec
  project status`, `pcrec check-design lessons` — one-line descriptions
  only, not the referenced files' bodies. Not fetched, not acted on.
- **`userEmail`** (`frank@dicostanzo.com`) and **`currentDate`**
  (2026-08-21) — standard session metadata, not pcrec-specific, not
  acted on beyond dating this document.
- **Harness-level tool/skill/agent-type listings** (available skills,
  deferred tools, subagent types) — infrastructure, not project content.
- No `git` command was run anywhere in this session (the cell has no
  `.git`, by design). No file outside `$CELL` and this session's own
  scratchpad directory was read, written, or executed.

## Allowlist gaps

None encountered. Every file this task needed (`docs/testing.md`,
`docs/spec/match_api.md`, `build/pcrec`, `build/libpcrec.a`) was present
in the cell as promised.

## Files in this directory

- `README.md` — this file.
- `lib_pcre2.py` — the ctypes binding onto the system `libpcre2-8` runtime.
- `oracle.py` — the reusable, independent `.rxt` re-checker (run this to
  re-verify everything; it is what a reviewer should trust, not
  `mkcorpus.py`).
- `mkcorpus.py` — the generator that first produced the `.rxt` files below,
  kept for transparency/provenance. Not required to re-verify anything
  (that is `oracle.py`'s job) and not imported by it.
- `anchors_abs.rxt`, `word_boundary.rxt`, `multiline.rxt`, `gstart.rxt`,
  `kreset.rxt`, `composition.rxt`, `syntax_errors.rxt`, `gating.rxt` — the
  corpus itself.

The reviewer places this whole directory at `tests/assertions/d27/` on
merge, per the brief.
