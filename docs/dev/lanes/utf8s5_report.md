# [M5.0] STAGE 5 — SCRIPT PROPERTIES (lane `utf8s5`)

2026-09-09, opus, `worktrees/utf8s5`, branch `lane/utf8s5`, branch point
`37d5ed45`.

**Delivered: `\p{Greek}` compiles** — 171 script values, every spelling the UCD
declares, in three namespaces, both encodings, both polarities, in a class,
under `-i`.

**And the stage is not the one the design chartered.** `utf8_design.md` §3.4
budgets scripts as *"one more UCD file, ~160 names; nothing structural, purely
table weight"*. Three of those five claims are false, and §1 is about the one
that matters: **the bare spelling is not the Script property**, so a script
value carries TWO sets rather than one, the table needed a namespace column,
and a THIRD vendored file the design does not list turned out to be required.

---

## 1. THE FINDING, and it decides the whole shape

MEASURED over the whole code-point space against libpcre2 10.42, 10.46 (the
reference) and 10.48, all three agreeing:

```
\p{Greek}      ==  \p{scx=Greek}  ==  Script | Script_Extensions
\p{sc=Greek}                      ==  Script alone
```

The discriminating code point is **U+0342 COMBINING GREEK PERISPOMENI**, whose
`Script` is `Inherited` and whose `Script_Extensions` is `{Grek}`:
`\p{Greek}` matches it and `\p{sc=Greek}` does not.

It was found by measurement and only then confirmed in `man pcre2pattern`'s
"Script properties for \p and \P" section, which states it outright — *"If a
script name is given without a property type, for example, \p{Adlam}, it is
treated as \p{scx:Adlam}. Perl changed to this interpretation at release 5.26
and PCRE2 changed at release 10.40."* The same section defines the extended set
as the UNION this lane builds (*"matches, in addition, characters that have
Adlam in their extensions list"*), which independently confirms a second thing
measurement had already shown: **the extended set is not
`ScriptExtensions.txt`'s own value.** UAX #24 gives a listed code point an scx
set that deliberately EXCLUDES its own `Common`/`Inherited` Script — U+1CD3 is
`sc=Common`, `scx={Deva,Gran,Knda}` — and libpcre2 nonetheless matches
`\p{scx=Common}` against it.

**Why it matters more than a table row.** The build the design describes —
read `Scripts.txt`, wire every spelling to it — compiles every script name,
refuses none, passes every refusal pin, passes a name-set check in both
directions, and answers a SMALLER SET than PCRE2 on **151 of the 171 values**.
Nothing structural can see that. The instruments that can are the one
oracle-free cell §4 lists as required to DISAGREE, the membership differential,
and the corpus's first two blocks.

---

## 2. What landed

| | |
|---|---|
| `third_party/ucd-16.0.0/` | `Scripts.txt`, `ScriptExtensions.txt` **and `PropertyValueAliases.txt`** vendored, SHA-256 recorded; `PROVENANCE.md` derivation row extended |
| `generate.py` | family (4): the scripts. Two sets per value, the `Unknown` complement, the alias spellings, and the one MEASURED decline |
| `src/parse/uprops_tables.inc` | GENERATED: **717 rows over 312 distinct sets, 10,961 intervals, 104,896 bytes** (was 45 / 8,437 / 68,576) plus a NAMESPACE column |
| `src/parse/mod_uprops.c` | `uprops_namespace` — the one place a body's `=`/`:` prefix is read; `uprops_lookup` takes the namespace; three read-only table accessors for PC-3 |
| `src/core/internal.h` | those three accessors, declared with why they exist |
| `tests/uprops/uprops_names.py` | NEW — §2's promise side, set equality in both directions |
| `tests/uprops/run_uprops_tests.sh` | §2 rewritten, §3's population split per encoding, §4's spelling identities + the one required disagreement |
| `tests/uprops/uprops_compare.py` | the drift policy widened twice (scx revisions; a NAME the oracle lacks) |
| `tests/registry/pcre2_check.c` | `check_gated_uprops_space` sweeps **every name pcrec ships** (1,053) against the live oracle |
| `tests/utf8/axis12_scripts.rxt` | NEW — 26 blocks / 60 cases, oracled from the **10.46 reference** |
| `tests/known_fail/k53_uprops_oversize.rxt` | +4 blocks (the `\p{Unknown}` spellings) |
| `tests/mech/sabotages/S-U12_*.sh` | the bare-namespace row |
| pins re-pinned | reject census, PC-3 pass count, rxtsource census, the empty-engine manifest |
| docs | `docs/spec/cli.md` (D80), the compliance page + annotation, K53, four CLAUDE.md files, PROVENANCE/README |

**The 171 values**: every `sc` value `PropertyValueAliases.txt` declares except
`Katakana_Or_Hiragana`, each answering to its long name, its four-letter code
and any deprecated alias (`Greek`/`Grek`; `Inherited`/`Zinh`/`Qaai`), in the
bare, `sc=` and `scx=` namespaces, with either separator, loosely matched
through the PREFIX as well as the value.

---

## 3. Decisions the brief delegated, and what each was decided ON

**(a) Which name set ships — the full one, minus a measured exclusion.** The
reference accepts 1,032 of the 1,038 spellings the UCD declares across three
namespaces; the six it refuses are `Hrkt`/`Katakana_Or_Hiragana` in all three.
That is `\p{Assigned}`'s case in the other direction — a name the UCD has and
PCRE2 does not — and it is declined by NAME with its measurement, exactly as
stage 3 declined `Assigned`. There is no `gc=` namespace because libpcre2 has
none (measured error 147 for `gc=L`, `General_Category=L`, `gc:Lu`).

**(b) `scx` SHIPS rather than being a named non-goal.** The brief allowed it
to be declined with a reason; the finding in §1 removes the choice. `scx=` is
not a separate axis on top of the scripts — it is the SAME set the bare
spelling already denotes, so shipping bare names without it would mean building
the extended sets and then refusing the spelling that names them. The `sc=`
namespace is the one that costs a second set, and it is the one PCRE2 users
reach for when they mean the strict property.

**(c) Name normalization — measured, and the scanner already had it.** PCRE2's
loose matching drops space/tab/hyphen/underscore and folds case across the
WHOLE body including the prefix: `\p{S c r i p t _ Extensions = G-r-e-e-k}`
compiles on all three versions and is a live corpus cell. `mod_uprops.c`'s
streaming normaliser already produced exactly that form, so the only scanner
change was reading the first `=` or `:` as a prefix separator (both, measured
interchangeable). A SECOND separator needs no special case: `\p{sc=scx=Greek}`
leaves `SCX=GREEK` as the value, which is in no table.

**(d) The K53 interplay — counted, and the brief's expectation is REFUTED.**
Of 684 script patterns at default axes under `-e utf8` (171 values × the two
distinct sets × both polarities), **exactly two refuse**, and they are one set
under two names: `\p{Unknown}` and `\p{sc=Unknown}` at 1,019,008 bytes. Adding
the other spellings of that set gives six refusing names for one set; four
blocks are filed into `k53_uprops_oversize.rxt` with the same shape stage 3
used. Every other script compiles — the largest is `\P{Common}` at 358,339
bytes, a third of the cap. `\p{Unknown}` is the DERIVED complement of every
listed script (729 intervals), so it is the one script property with `\p{C}`'s
shape rather than a script's.

**(e) Caseless — measured exhaustively, not sampled, and stage 3's rule
survives.** A caseless set can only GAIN a case-fold partner of a member it
already has, so sweeping the 2,938 code points `CaseFolding.txt` names is
EXACT for detecting any difference rather than a sample of one: 171 values × 3
spellings = 513 sweeps, **zero differences**. So a script row carries the same
span twice and `\p` still never meets `cls_casefold`.

---

## 4. Acceptance, against the brief's shape

| the brief asked for | result |
|---|---|
| the membership differential extended over the script names, both encodings, oracle tier structure unchanged | DONE — §3's population split per encoding, and the tier structure gained the two drift widenings §5.2/§5.3 name rather than being relaxed |
| the gated-space check updated for the new names | DONE, and re-shaped: it sweeps every name pcrec ships (1,053) rather than a hand list — §5.7 |
| PC-3/PC-4 arms as stage 3 did them | PC-3 done (above). **PC-4 is deliberately untouched**: its pattern space is `options=0` byte-mode escape/POSIX classes, and a script property there is either empty or Latin-1 noise. The script name axis IS asked of libpcre2 — in PC-3's sweep — which is the question stage 3's PC-4 arm was for |
| the D65 `built` column flips for what ships | NO FLIP IS DUE, and that is the honest answer rather than an omission: `\p{...}`/`\P{...}` are ONE registry row each and both read `built` since stage 3. Scripts add names to a table, not rows to the registry, so the tally stays `138 = 110 + 12 + 16` — verified unmoved, not assumed |
| targeted suites green locally (uprops, utf8, encchk-250, codegen) | §7 |
| byte-encoding answer identity (scripts clamp exactly as categories do) | DONE and measured in both directions: `uprops_names.py` asserts exactly seventeen scripts have a Latin-1 member, and the empty-engine manifest (§5.4) is the same fact reaching a structural check |
| K53 counted and filed with the same shape | §3(d) — two refusing sets, four blocks |

---

## 5. Findings against the tree

**5.1 A vendored source arrived for a reason the design did not name.**
`utf8_design.md` §3.3 lists five UCD files and does not list
`PropertyValueAliases.txt`. Stage 5 needs it twice over: every script answers
to a four-letter code `Scripts.txt` does not carry, and `ScriptExtensions.txt`
names its scripts BY that code, so the code-to-name map is what makes the
second file readable at all. It also supplies the one value `Scripts.txt`
cannot (`Unknown`, the complement) and the one this stage declines (`Hrkt`).
The vendoring shape absorbed it with no re-plumbing — one more file, one more
`PROVENANCE.md` row, no change to `make gen-tables` — which is what §3.3.2's
"name the derivation generically" ruling was for, meeting its first test.

**5.2 The NAME axis drifts between Unicode versions and it did not before.**
Every name stage 3 shipped is a general category that has existed since Unicode
1.0. Unicode ADDS SCRIPTS, so an older oracle refuses `\p{Kawi}` outright —
measured: the system 10.42 (Unicode 14.0.0) rejects 17 of the spellings pcrec
ships, across 9 values. Two instruments needed a rule for that, and they got
different ones because they can see different things:

- `uprops_compare.py` (the membership differential) excuses a name the oracle
  lacks only when EVERY code point pcrec attributes to it is unassigned on the
  oracle's side, read out of the oracle's own `\p{Cn}` line in the same run. A
  name pcrec invented still fails, naming its addresses.
- PC-3 is byte-oriented and has no UTF sweep to ask that question with, so its
  rule is coarser and says so: exact agreement when the oracle IS at the pin,
  and otherwise a refused name must be a SCRIPT row — **a category may never
  drift** — with the count printed and the sharper question delegated by name.

**5.3 `RECLASSIFIED` needed widening from "category" to "property value", and
the drift runs in BOTH directions at once.** Unicode revises the
Script_Extensions of ALREADY-ASSIGNED code points between versions, so they sit
in neither side's `Cn` and the symmetric budget cannot reach them. Seventeen
entries: U+00B7 MIDDLE DOT against the OLDER oracle (its scx is just `Common`
at 14.0.0 and fifteen scripts at the 16.0.0 pin) and sixteen combining marks
against the NEWER one (17.0.0 attributes them to more scripts than 16.0.0
does). U+00B7 is the only one the byte arm can reach, and it is the reason
seventeen scripts are non-empty under `byte` at all.

**5.4 A structural check restated the finding without knowing what a script
is.** `run_dfa_stamps.sh`'s empty-engine manifest went 16 → 26, and the split
among the ten new members is §1 over again: `\p{sc=Greek}`, `\p{sc=Grek}` and
`\p{Script:Greek}` are in the bucket (the strict Greek set starts at U+0370 and
is empty in Latin-1) while **`\p{Greek}` is not** (U+00B7 carries Greek in its
scx list). Same script, same encoding, two buckets. `\p{Thaana}` and
`\p{sc=Thaana}` are both in it, which is the control saying the split is about
that one cell and not about `sc=` being empty in general.

**5.5 A BSD `paste` portability bug in that check, fixed here.** When the
manifest comparison fired, both its "only:" and "missing:" lists printed EMPTY
— `paste -sd' '` reading stdin needs an explicit `-` on BSD — so the check
reported that the population had moved and could not say how. It is the
`[MACPORT]` residual class `bat4triage` catalogued (`xargs -a`, `wc -l`
padding), met in a diagnostic that only runs when something is already wrong,
which is the worst place for it. One character each site.

**5.6 The corpus is oracled from the REFERENCE, and three cells prove that was
necessary.** Every expectation in `axis12_scripts.rxt` is 10.46's own answer,
obtained by bundling the cells into one stdin payload and driving them on the
reference over the tailnet (reading and writing nothing there). The two local
libraries were then asked the same 57 cells: Homebrew 10.48 agrees on all 57,
macOS's system 10.42 on 54. **The three it disagrees about are U+00B7 and
U+0300 under `\p{Greek}`/`\p{scx=Greek}`** — so a file oracled from `/usr/lib`
on this Mac, which is what every dlopen-based instrument here resolves, would
have pinned three cells against a Unicode version pcrec's tables are not at.
Stage 4's precedent was to pin locally and mark the reference confirmation
OWED; this stage did not have to, and the method is cheap enough to reuse.

**5.7 PC-3's name axis stopped scaling and had to change shape.** Stage 3's
`check_gated_uprops_space` probes a hand-written list. 171 values in four
spellings across three namespaces is not a list a human keeps right, and a
hand copy of the generator's output could only ever agree with it or be stale.
So the population is now read from pcrec's OWN table through three read-only
accessors and the ARBITER is libpcre2 — the one source the table did not come
from. That is `uprops_lookup`'s own independence argument one level up, and it
is why the accessors exist and say so at their definition.

---

## 6. What a reviewer should attack first

- **The extended-set derivation** (`build_scripts`). It is `Script ∪
  ScriptExtensions-file`, and the reason it is a union rather than the file's
  own value is a PCRE2 behaviour on `Common`/`Inherited` that the UCD's own
  data model contradicts. The whole-space comparison behind it is in §7.
- **The namespace column's collision rule.** The generator raises on two rows
  answering for one (name, namespace); nothing else stops a script value whose
  normalised name equals a category's from silently shadowing it.
- **The byte arm's population choice** (`BYTE_SCRIPTS` in
  `run_uprops_tests.sh`). Seventeen names plus a control, instead of all 171,
  is the one place this delivery trades coverage for `make test` minutes. The
  list is asserted in both directions by `uprops_names.py`, so it cannot go
  stale silently — but the argument for the trade is mine and is stated at the
  list.

---

## 7. Validation

**Every number below was measured on this branch's tree. The box carried a
concurrent `make test` (the 2d acceptance runs) for most of the lane's working
period, so the two long sections are marked with what that costs.**

| section | result |
|---|---|
| `make strict` (CC=gcc-16) | **clean** — whole tree, `-Werror -Wshadow` |
| `generate.py --check` | clean: the committed `.inc` is exactly what the generator produces from the vendored UCD |
| `tests/utf8/axis12_scripts.rxt` | **60 passed / 0 failed on the first run**, against the 10.46 reference's own answers |
| `tests/reject/` | **615 checks / 0 failed**; census re-pinned 286 / 108 / 0 / 93 |
| `registry_check.c` | **225 / 0** |
| PC-3 (`pcre2_check.c`) | **194 PASS / 119 FAIL** — the 119 are the PRE-EXISTING U13/U15 set (the `(?a)`/`(?r)` option-run family and the verb differential against this box's 10.42), unchanged in count and identity from the branch point. The uprops arm is wholly green: `1,053 shipped names asked of the oracle`, 1,002 accepted by both, 51 SCRIPT names this Unicode-14.0.0 oracle does not have and **no category drifted**; `118 probes, libpcre2 accepted 28 / rejected 90, pcrec accepted 28; 12 real-but-unshipped names refused` |
| `tests/codegen/run_dfa_stamps.sh` | **31 / 0** with the empty-engine manifest re-pinned 16 → 26 |
| `tests/rxtsource/` | census **PASS** at 211 / 3936 / 28943 (re-pinned). The section's other reds are the PRE-EXISTING BSD `xargs -a` and `wc -l`-padding failures `bat4triage` catalogued; not this lane's and unchanged |
| known-fail ratchet | **2 still failing / 0 now passing** — the legitimate state; K53's file is 16 distinct compile failures now (12 + this stage's 4) |
| compliance page | `--check`, `--names`, `--check-annotations` all PASS after the script row moved `REJECTED` → `OK-GATED` and its annotation was rewritten |

**OWED, and named with the exact command rather than described:**

| owed | why |
|---|---|
| `bash tests/harness/run.sh tests/utf8/` (clean) and `ENC=byte bash tests/uprops/run_uprops_tests.sh` and `make test-codegen` and `make test-encoding-checks` | launched as ONE background run at hand-off. **The clean `tests/utf8` figure is PREDICTED at 1773/0** and the prediction is not a guess: the S-U12 sabotage run measured 1763 passed / 10 failed over the same directory, and those are the same 1,773 cases. A different total is itself a finding (stage 4's §3.14 records the harness under-counting on a loaded box). Launched as ONE background run at hand-off — `bash <scratch>/s5_validate.sh`, log path in the handback, completion line `=== S5-VALIDATE COMPLETE ===`. The box has been carrying a concurrent `make test` all afternoon and stage 4's own report records the harness UNDER-COUNTING cases on a loaded box (its §3.14), so these are deliberately not read off a contended run |
| S-U12 through the MATRIX | its figure is MEASURED (1763/10, all ten in `axis12_scripts.rxt`) but by a direct harness run, not by `run_sabotage_matrix.sh S-U12` — the canonical driver, which this tree's own convention prefers. `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S-U12` reads FIELDS OK |
| `make test-uprops-utf8` (the whole-space arm) | opt-in and long even on a quiet box; it is the arm that sweeps all 171 values × 2 sets rather than the byte arm's 17 + controls |
| the 10.46 EXACT arm | `uprops_compare.py`'s tier (1) — exact agreement, no drift budget — runs only where the oracle IS the pin, i.e. on the Linux reference. That is the run that turns this stage's "51 names and 28,263 code points attributed to drift" into zeroes, and it is the executor channel's, with the same shape stage 3 owed |
| `make test` / `make san` / `make mech` | the manager's at merge, per BOILERPLATE. The four sabotage rows this stage touches were not run through the matrix |

---

## 8. Rulings received

None; no `utf8s5_rulings.md` was written during the lane's working period and
the lane asked for none. Every decision the brief delegated was answerable from
measurement, and §3 records what each was measured against.
