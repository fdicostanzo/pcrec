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

## 2. Acceptance — OWED, every line

Nothing below has been run. The hold forbade it and the lane did not run
it anyway.

| item | status |
|---|---|
| N targets → N artifacts, N prefixes, one `rx_info.name` | OWED (`tests/rxtsource` W1.2 §1) |
| §6.3's three-config file compiles three ways, the three agree | OWED (`three_configs.rxtin` + H11) |
| abi 14 at all four sites | **THREE DONE, SITE 4 OWED** — see §4 |
| F9's `.name` assertion over the corpus's artifacts | OWED (`run_codegen_tests.sh`) |
| identity gate (A) byte-identical | OWED, and EXPECTED: the two bytes this change writes are `rx_info` initializer lines, emitted below (A)'s `prog_region` on every artifact |
| identity gate (B) re-pinned | OWED — the pin must be this step's LAST src commit, so it lands last |
| `make test-codegen` green (PROCS=4, async) | OWED |
| `make strict` clean | OWED |
| oracle-verified expectations for new cells | **DONE** — all four `three_configs` / `common` cells verified against python3 `re` in one invocation; transcript in the lane log |
| D26 tiering (no gold-plated diagnostics) | DONE by construction: every new refusal names a FILE, a LINE and a CONSTRUCT and none reproduces a PCRE2 message |

---

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

### 3.6 `docs/dev/plan.md` was NOT touched

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
