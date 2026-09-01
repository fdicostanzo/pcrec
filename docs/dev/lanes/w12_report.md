# lane w12 — [DD-13b.W1.2] report

**Branch** `lane/w12`. **Status at time of writing: BUILT, NOT VALIDATED —
the box HOLD was in force for the lane's entire working period and no
`make`, no gcc and no `build/pcrec` run has happened.** Every acceptance
number below is marked OWED. The lane acked the hold in its first WIP
commit and has stayed inside it: reads, edits in this worktree, `git`,
`bash -n` (a parse, no execution), and one `python3 -c` used to
oracle-verify the new fixtures' expectations.

---

## 1. What landed, where

### `src/parse/rxt_source.c` — RESOLUTION (new section, ~300 lines)

`pcrec_rxt_source_resolve` answers the three questions `--source` must
answer before it can call `pcrec_compile` even once. It is a SECOND
SECTION below a banner, not a second pass over the rows: everything above
the banner still reports the file AS WRITTEN and touches no filesystem,
which is what keeps `--list-source` comparable against `run.sh`'s and
`verify_rxt.py`'s parses.

- **Which artifacts** — the `target` rows in file order; or, with no
  `target` and exactly ONE UNNAMED block, the implicit `target rx`
  (format_design §6.4). Anything else with no `target` builds NOTHING at
  exit 0 (§6.1's "a library ships nothing by itself"), which is a
  DIFFERENT observable from a refusal.
- **From which block** — a definition name is a block's `name`, in the
  FILE namespace (DECIDED (7)). No composer, no library contents read, so
  an undeclared name is a tier-2 refusal naming the name AND the `lib`
  chain searched.
- **Under which settings** — `cfg_merge` is the flat LATER-WINS rule and
  the ONLY rule `with` and `from` use (one struct, one function, so the
  two levels cannot acquire two implementations); the PER-KIND table is
  applied exactly ONCE, at the block. `pcrec <raw>` ACCUMULATES rather
  than replacing, because it is a line kind that may legitimately repeat
  and its later-wins is the option parser's own.
- **`lib`** — the `"path"` form is resolved as far as EXISTENCE (the
  source's own directory, then each `--lib-path` in order); `<store-name>`
  is refused as NOT IN THIS BUILD rather than searched for as a filename.

### `src/core/internal.h`

`RxtTarget` + `pcrec_rxt_source_resolve`'s declaration, with the
never-NULL `name` stated as a type contract.

### `cli/main.c` — ONE OPTION PARSER, and the three new flags

`main`'s argument loop became `cli_parse` over a `CliState`, because
§1.5 requires a `config` block's `pcrec <raw>` to be re-parsed by the
CLI's OWN parser. **The containment is one test over a SPAN**
(`cli_extras_clean`: the bytes past `opt` are all zero), not a list of
flag names — so a flag added tomorrow is covered with no edit, and
`saw_prefix` sits in the tail precisely because `-p` writes inside `opt`
where the span cannot see it.

`--source FILE`, `--target NAME`, `--lib-path DIR` (repeatable, order is
search order), and the `-o` naming rule: an existing DIRECTORY writes
`<dir>/<prefix>.c`+`.h` per target, anything else is a file and needs
exactly one target, `-` is stdout and needs exactly one. `-h` became a
FLAG so a config's `pcrec -h` cannot print usage and exit 0 mid-compile.

### `lib/pcrec.h` — `pcrec_options.name`

Appended; NULL means "use `prefix`", which IS Frank's §6.3 rule, so every
pre-existing caller stamps its own prefix with no edit.

### `src/gen/emit_dfa.c` — `rx_info.name`, `rx_info.nentries`, abi 13→14

Both members APPENDED after `match_form` (no offset moves). This is the
first bump since [OPT-1] that moves **no emitted PROGRAM byte at all**:
no table, state, label, macro value or offset changes on either engine.

### `tests/harness/driver.c` — F13, the prefix as a `-D`

`RXT_PREFIX`/`RXT_UPREFIX`, defaulting to `rx`/`RX`, with a paste pair.
TWO macros because C cannot case-convert a token; both derived from one
value in `run.sh`, and a mismatched half is a compile error rather than a
wrong answer. `rx_ctx` is deliberately NOT among them — it is a
fixed-literal ABI type.

### `tests/harness/run.sh` — H11

Reads the `target` rows off the SAME `--list-source` call it already
makes; builds each target naming a block through `--source --target` into
its own directory (so `#include "gen.h"` resolves off `-I` alone);
asserts per target that the artifact's `rx_info.name` equals the block's
`name`; and requires every target to answer each case IDENTICALLY to the
block's own compile — §6.3's "identity between them is a free control".
A per-file FLOOR fails a file that declares more targets than it built.
**All edits are outside the hash-pinned arm region**, so the pin does not
move.

### Tests

- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT=14` + ledger; F9's
  corpus sweep (every distinct `pattern` under `tests/base/`, floored at
  300); the four-prefix arm; the `nentries` presence/equality check.
- `tests/rxtsource/run_rxtsource_tests.sh`: a W1.2 section (targets, the
  three `-o` forms, `--target`, H11 through `run.sh` with the `--source`
  call count asserted, four resolution refusals, `--lib-path`'s cure, the
  library outcome, the compatibility default) and six new fixtures.

### Spec (D80, in the same change)

`docs/spec/cli.md` (S11: a `--source` section, §4's two bullets narrowed,
revision history), `docs/spec/rxt_format.md` (the `target` and `lib` head
rows stop saying "not yet built"/"not yet resolved"; a new "Building from
a source file" section), `docs/spec/match_api.md` §6 (S9: the two members,
the never-NULL rule, why `nentries` is not `nnames` restated, both `abi`
sentences 13→14).

### CLAUDE.md

`lib/`, `src/gen/`, `src/parse/`, `cli/`, `tests/harness/`,
`tests/rxtsource/`, `tests/codegen/`, `docs/spec/`.

---

## 2. Acceptance — MEASURED

Validated 2026-09-01 00:38-02:0x EDT, after the box hold lifted. `PROCS=4`,
async, serialized behind lane cc per the manager.

| item | measured |
|---|---|
| `make strict` | **CLEAN**, `-Werror -Wshadow`, FIRST attempt — ~500 lines of C written under the hold and never compiled until 00:38 |
| N targets → N artifacts, N prefixes, one `rx_info.name` | **PASS.** `--source three_configs.rxt -o <dir>` → `log_base`/`log_strict`/`log_big` `.c`+`.h`; each entry carries its own prefix (`int log_base_search`, …); all three stamp `.name = "level_filter"` |
| §6.3's three-config file compiles three ways and the three agree | **PASS (H11).** `run.sh` made exactly 3 `--source` calls and all three targets answered the block's 3 cases identically to its own compile |
| `features` UNION reaches the artifact | **PASS.** all three stamp `PCREC_FEATURE_MODULES "classes,named-groups"` (`classes` from `baseline`, `named-groups` from the block) |
| the four resolution refusals | **PASS**, each naming what §1.3 requires |
| library builds nothing / compatibility default | **PASS**, exit 0 with no artifact / implicit `target rx` naming itself `"rx"` |
| F9's `.name` assertion over the corpus | **PASS.** every distinct `pattern` under `tests/base/` stamps its own prefix (floor 300); plus 4 prefixes of different length and shape |
| `nentries` present and == `nnames` | **PASS** on 0- and 2-named-group artifacts |
| abi 14 at all four sites | **DONE.** sites 1-3 with the emitter change; **site 4 FILEPIN `dc2c8ef` → `0bc6884`** (commit `8979d23`), naming the step's LAST src-touching commit |
| identity gate (A) byte-identical | **PASS, 0 differing on all four axes** (same 2223 / 2228 / 2224 / 2228 vs the UNMOVED pre-module pin `ac4917d`) |
| identity gate (B) re-pinned | **PASS, 0 differing on all four axes** (same 2274 / 2275 / 2274 / 2274 vs the new pin `0bc6884`); refusal-mismatch 0, elided 0, stamp-moved 0. Gate wall 714 s, 16 checks / 0 failures |
| `make test-codegen` | see §2.1 — re-run on the FIXED tree |
| `tests/rxtsource` | **94 checks / 0 failures**, wall **40 s** |
| oracle-verified expectations | **DONE**, python3 `re`, all new cells |
| D26 tiering | **DONE** — every refusal names FILE, LINE and CONSTRUCT; none reproduces a PCRE2 message |

### 2.1 The `test-codegen` re-run, and why there is one

The first run was **4/5** — `run_size_term.sh` red (§3.7). After fixing it I
re-ran **only that script** (32/0). The other four were last run on the tree
BEFORE the emitter fix, and that fix MOVES EMITTED BYTES; three of the four
read emitted text. So the group was re-run in full on the fixed tree rather
than assembled from two different trees.

**`run_trie_identity` would not have caught it either way**, and that is
worth knowing rather than assuming the four are equally informative: it
compares two builds of the SAME tree, so a change present in both cancels.

### 2.2 §5.5's runtime delta, measured by ABLATION

The manager's baseline (8.2 s, `w11_report.md:63`) is **C1's runtime, not the
section wall** — its three legs ARE C1, and the section also ran C3, C0a, the
hash pin, the keyword census and the head fixtures. So "measured wall minus
8.2" would charge this lane for every non-C1 check W1.1 already had.

Two honest numbers instead:

- **C1 is UNCHANGED.** The section prints its own: leg A 0.8 s (189
  `--list-source`), leg B 7.4 s, leg C 0.2 s = **8.4 s**, against W1.1's
  8.2 s. This lane adds nothing to the parse differential.
- **H11's own cost, by ABLATION** — `run.sh` on the three-target fixture,
  then on the same fixture with its `target` lines stripped, everything else
  held constant:

  | | wall | cases |
  |---|---|---|
  | with 3 targets | 905 ms | 3 / 0 |
  | targets removed | 275 ms | 3 / 0 |
  | **H11's marginal cost** | **630 ms** | ~210 ms per target |

  An ablation measures the feature; a subtraction from a number that means
  something else measures the difference between two definitions.

Section wall **40 s** absolute; the whole W1.2 block is ≈1.5 s of it once its
~15 `pcrec` calls are added to H11's 630 ms.

## 3. Findings the manager should read

### 3.1 The `head_basic` fixture was FALSE and W1.1 could not see it

`tests/rxtsource/fixtures/head_basic.rxtin` declared `lib
"definitions/common.rxt"` (no such file anywhere in the tree) and `target
rx = greeting` (no block in it is named `greeting`). Under W1.1 a recorded
`lib` path is never opened and a parsed `target` is never resolved, so
both were inert and nothing in the tree could go red. W1.2 resolves both,
so the fixture had to become true: a real sibling library
(`common.rxtin`) and `target rx = plain_run`.

**The generalisable half**: a fixture written to witness one property can
be false about another, and it stops being merely unused the moment a step
downstream starts reading the declarations it carries. It is the same
shape as a stale citation that still reproduces its quoted output.

### 3.2 Two decisions the manager may want to reverse

- **The FILE wins over the command line.** A target's composed settings
  override a flag given on the command line. The in-tree precedent is
  `run.sh`'s own `RXTFLAGS` ("appended LAST so a directive on the same
  axis wins"), and the argument is that a `.rxt` source states the build
  its patterns are meant to have. §1.5 does not rule this; it is the
  lane's call and it is stated in `cli.md`.
- **A `lib` path is STAT'd.** W1.1's comment said "recorded, never
  opened". §1.3's refusal table demands a diagnostic naming an
  unresolvable `lib` path and the `--lib-path` list, which cannot be
  produced without resolving it, so `--source` now checks existence (never
  contents). `--list-source` still touches no filesystem, and that
  difference is asserted.

### 3.3 `features` UNION and the whole-spec words

`pcrec --features` accepts `all`/`none`/`std1` only as an ENTIRE spec, not
as a list member, so the union of a config's `features all` and a block's
`features classes` is not a legal spec. The lane did NOT restate that
vocabulary here (a second home for it): the join is handed to
`pcrec_enabled_set_spec`, which refuses it in its own words, and the CLI
appends one sentence naming `features only` as the way forward. If the
manager wants a sharper diagnostic it needs a vocabulary predicate
exported from `src/parse/enabled.c`, which is a new surface.

### 3.4 `nentries == nnames` today, on purpose

No composer exists, so `groups[]` holds the primary's rows and nothing
else. The field ships equal because it rides this `abi` bump; the
alternative is a second bump for one integer. `match_api.md` §6 says so in
those words, and the codegen check pins the equality rather than implying
a distinction with no producer.

### 3.5 A DIAMOND double-counted `pcrec` text, found by hand-tracing a fixture

`target rx = plain_run with dev, release` where `release from dev` expands
`dev` TWICE, and while every ordinary setting is idempotent under
later-wins, `pcrec <raw>` ACCUMULATES — so the joined flag text carried
`dev`'s line twice. Harmless for every flag pcrec has today (each is
last-wins) and resting entirely on that, which is the wrong thing to leave
standing. Fixed: a `seen` set spanning ONE target's whole `with`
composition, so a config materialises ONCE, which is what §1.5 says. Found
by hand-tracing `head_basic`'s own config cascade under the hold, not by a
run.

### 3.6 The `features` UNION had a population of ZERO — found by probing, in this lane's own new code

The manager's probe window was spent settling what this lane had inferred
about the surfaces it builds on (full table in `w12_log.md`). One probe —
confirming §3.3's claim that a whole-spec word cannot join a `features`
list — exposed that the UNION branch was reached by NO fixture:
`head_basic`'s config sets `features` and its block does not, and
`three_configs` set none at all. So §1.5's one genuinely composing
directive had a green check behind it and no population, which is the
exact failure this project records most often, committed by this lane in
the code it wrote to avoid it.

Closed: `three_configs` carries `features classes` on `baseline` (which
`strict` and `big` inherit through `from`) and `features named-groups` on
the block, and the section asserts all three artifacts stamp
`PCREC_FEATURE_MODULES "classes,named-groups"` — an artifact-side witness,
not a re-derivation. Neither module is reachable from `error|warn|fatal`,
so no answer moves and the agreement control stays strict.

### 3.7 `docs/dev/plan.md` was NOT touched

Three lanes may be editing the `[DD-13b.W1]` row. The lane left the STATE
tag to the manager rather than risk a merge conflict on a row it does not
own.

---

## 4. The abi ritual — SITE 4 IS OUTSTANDING

Re-measured in this worktree rather than read from `w1_impl.md`, which
predates [OPT-5]:

| # | site | before | after |
|---|---|---|---|
| 1 | `src/gen/emit_dfa.c`'s `.abi` | 13 | **14, DONE** |
| 2 | `tests/codegen/run_codegen_tests.sh:2707` `ABI_EXPECT` | 13 | **14, DONE** (+ the bump ledger) |
| 3 | `docs/spec/match_api.md` (two sentences, `:159` and `:1602`) | 13 | **14, DONE** |
| 4 | `tests/codegen/run_recursion_identity.sh`'s `FILEPIN` | `dc2c8ef` | **OWED** |

Site 4 must be this step's LAST src-touching commit (`run_recursion_
identity.sh:394-406`'s own rule: the pin moves with the LAST scaffolding
change of an abi, not the first), so it is deliberately not yet set. **The
manager assigns the FINAL abi number at merge** — other lanes carry bumps
and merges serialize; if this lands as 15 rather than 14, sites 1, 2 and 3
move together and site 4 is set to the merge's last src commit.

---

## 5. What the manager must decide

1. **The final abi number** (14 in this branch; reassign at merge).
2. **Site 4's pin value**, after the merge order is known.
3. §3.2's two lane calls (file-wins precedence; `lib` existence check).
4. The `docs/dev/plan.md` STATE update for W1.2.
5. Whether the `tests/rxtsource` section's new COMPILES (a handful of
   fixture targets) are acceptable in a section advertised as parse-only,
   or whether they should move to their own target.
