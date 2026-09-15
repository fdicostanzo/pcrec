# [DD-13b.W23.3] — the fourteen productions (lane w233)

Branch `lane/w233`, from `54336bab`. Step brief:
`docs/design/dd13_format/w23_impl.md` REVISION 1.1 §6.3; design of record
`format_design.md` 3.4.2. Three commits: `c1042c00`, `e14d7458`,
`6d83fef5`.

Everything §6.3's build order names is built. What follows is what the
build MEASURED, the six places the note or the design disagrees with the
tree, and the two defects this step shipped and then found — both found
by measuring a production against all three legs rather than by reading
it, which is the transferable half.

---

## 1. What landed

| # | build order item | landed as |
|---|---|---|
| 1 | `pattern-esc` + the CLI decode flag; `\x00` refused citing K9 | `rxt_source.c`'s opener branch, `pcrec_rxt_decode_escaped` (one decoder, three callers), `cli/main.c`'s `--pattern-esc` |
| 2 | the CHILD-ADMITTING kinds — `provenance` (both parents), `variant` as a sub-block | the schema's `children` column routing three scopes through ONE arm in leg A; real child consumption in legs B and C |
| 3 | `ext`, the AUX production, at both scopes | nothing but a value check in leg A — which is the point |
| 4 | the head declarations `vocabulary`, `include`, `oracle`, `tag`, `use`, the `freq` block + `analysis` | leg A's head arms; `vocabulary` is the only one REMEMBERED (a `closed` constraint reads it) |
| 5 | the case-line work — `under`, `mc`, `@file:` + `as`/`sha256`, `driver.c`'s `@<path>` and find-all loop | legs B and C; `driver.c` gains an additive `@<path>` subject and a `count` mode transcribing `match_api.md` §3.1 |
| 6 | §2.22's derived-identifier repair + its two comment sites | `rxt_compose.c`'s `def_by_name`/`bound_by_name`; `rxt_source.c`'s two SW12 sites |
| 7 | the W23.3 fixtures + S240, S245 | eleven fixtures, one deleted, one re-aimed; two sabotage rows |
| 8 | SW1, SW3-SW10, SW12, SW15, SW18's rule half, SW14's flag half | `docs/spec/{rxt_format,cli,match_api}.md` |

`PCREC_RXT_WAVE_BUILT` 1 → 23.

## 2. Acceptance, MEASURED

| acceptance (§6.3) | measured |
|---|---|
| every production parses in all three legs where block-scoped, in leg A where head-scoped; C1 green | `bash tests/rxtsource/run_rxtsource_tests.sh` **175 passed / 1 recorded / 0 failed** |
| the corpus census does not move | **210 / 3,936 / 28,943**, leg B's **209 / 3,933 / 28,932** — both unmoved |
| `--list-source` unchanged over the corpus | **209 dispatched files, 0 differing**, against the branch-point binary (`build/pcrec` at `54336bab`, copied before the run) |
| `aux_arbitrary_keys` accepted by all three legs | **leg A only, and the reason is the SEAM** — see §3.1 |
| `aux_deep_tree` accepted with NO extra block, NO extra case, NO provenance record | **1 dump row** where 1 is correct; asserted as a number, not as acceptance |
| `aux_literal_pipe`: the `\|` row's value is one byte and the sibling is a SIBLING | **the VALUE half is W23.4's** — see §3.2 |
| `aux_subtree_extent`: the declaration after the block is a declaration, the `pattern` block is a block | **2 dump rows** where 2 is correct, positive on both halves |
| `derived_call_collision` refuses naming BOTH definitions and the shared identifier | green, and its ACCEPT half (`derived_call_bind`) too |
| the over-long definition name is refused BEFORE the mapping runs | **unreachable by construction here** — see §3.3 |
| S240 and S245 turn their named fixtures red; S245 on all THREE detectors | **FIELDS OK + hand-verified DETECTED on a scratch build**; detector 3's symptom is MASKED and the row says so — §3.4 |
| `make strict` clean | **clean** |
| `make test` green | **OWED** — see §6 |

Also run directly and green: `tests/codegen` **109 / 0** (SABANCHOR clean
over 251 rows / 265 anchor sites), `tests/cli` **0 failed**,
`make -j4 CC=gcc-16` clean.

**§1.9's no-abi claim, checked rather than restated**: `git diff --stat
54336bab..HEAD -- src/gen src/ir src/opt lib` is EMPTY. **§4.3's three
arms**: (a) 0 corpus/fixture files carry a withdrawn first token; (b) 0
withdrawn keywords have a schema row; (c) the spec arm is a READ, and all
ten `testee`/`provides`/`capable` occurrences in `rxt_format.md` are
ordinary English or the withdrawal's own sentence.

---

## 3. THE SIX PLACES THE TREE AND THE DOCUMENTS DISAGREE

### 3.1 Four aux fixtures had to become HEADLESS, and §3.2's table cannot have them otherwise

§3.2 writes `aux_arbitrary_keys.rxtin` as *"an `ext bench` block at FILE
scope … all three ACCEPT"*. **Those two clauses cannot both hold at any
point in W23.** `ext` at FILE scope is a HEAD declaration; the head has
exactly ONE parser by the seam ruling (`w1_impl.md` §1.1); leg B takes
the body's start line off `--list-source` and leg C refuses every
head-bearing file BY NAME. MEASURED: leg C answers
`[unknown-token-in-scope] … 'ext' line before any pattern block` and leg
B relays leg A's own diagnostic as a HARNESS FAILURE.

This is **r59-A2's disposition, one production over** — the finding that
`dup_head_description.rxtin` is head-bearing and so cannot carry a
three-leg assertion. Resolution taken: `aux_arbitrary_keys.rxtin` keeps
its FILE-scope `ext` and is leg A only WITH the reason stated at the
call, and the other four aux fixtures are headless on purpose so all
three legs answer. `aux_malformed_body` and `aux_subtree_extent` were
rewritten to block scope for this reason (`oracle` is a block kind too,
which is what let the extent fixture keep its shape).

### 3.2 `aux_literal_pipe`'s central assertion is not observable until W23.4

§3.2 asks for *"a row whose `value` is the single byte `\|`, and the
sibling below it is a SIBLING ROW"*. Both facts live in `#section aux`,
which **arrives at W23.4** — §2.2 forbids this step from touching the
dump's shape. At this pin the fixture asserts acceptance and three-leg
agreement, which is real but weaker than the row describes.

Stated rather than quietly deferred, because the row's own framing calls
it *"decision 3's falsification point"*: **at this pin it does not
falsify anything.** If S3 still opened inside an open subtree, all three
legs would still accept the file — inside a subtree nothing is dispatched
under either reading — and only the emitted rows tell the two apart. The
fixture is in place and its assertion activates with the section.

### 3.3 "Refuse before mapping" is unreachable by construction here, not by an ordering

§6.3's acceptance line asks that an over-long definition name be refused
before `pcrec_rxt_prefix_from_name` runs, because that function
**silently TRUNCATES at `dstsz`**. The hazard is real and is about the
mapping's OTHER consumer, which derives into a fixed `char
def[RXT_TARGET_DEF_MAX + 1]` and is safe only because `parse_target`
refuses an over-long name two refusals earlier — an order nobody had
written down as a rule.

**This consumer sizes the destination at `strlen(name) + 1`**, which is
the mapping's own documented contract, so there is no length at which two
names collide by being cut: truncation is not avoided by an ordering, it
is inexpressible. The 128-byte CALLABILITY bound is a separate, real fact
(`PCREC_MAX_GROUP_NAME`, PCRE2's error 148, inherited under D26) and IS
refused by name at the lookup. The spec states the order anyway, because
the next consumer does not inherit this one's buffer.

### 3.4 S245's third detector fires, and not for its own reason

§3.5 says the `children: tree` → named-scope flip *"RE-ARMS S2 and S3
inside the subtree, so `aux_literal_pipe.rxtin` sees it on a STRUCTURAL
axis as well"*. **MEASURED under the plant, the structural effect is
MASKED**: `separator |` inside a body dispatched as `provenance` is
refused as an unknown token before S3's trigger is consulted, so the
fixture goes red on the DISPATCH.

The detection is real; the row now says which of its three detectors is
showing its own mechanism (1 and 2 are, 3 is not) and records that
parameter 3's STRUCTURAL half has no plant in this table — re-arming S3
without also moving the dispatch would need a scope whose vocabulary
contains every aux key, and no scope does. An absence recorded is better
than one that looks like coverage.

### 3.5 Three schema-clause spellings the design leaves to the table

§2.25.3 names seven constraint kinds and one parser-code exception but
does not spell the clause TEXT, and three spellings had to be decided
here. All three are DECLARED in `rxt_schema.def`'s header so
`--list-schema` carries them and no reader has to remember a rule:

- **`closed <selector> [member…]`** — the selector NAMES the set and the
  remaining words are the FORMAT-declared members; NO members means the
  set is FILE-declared only (`vocabulary <selector>`), and with no such
  line the key keeps free-vocabulary behaviour. That is §2.15's *"ONE
  constraint kind whose members may come from either"* spelled so both
  halves READ the same: `closed fidelity verbatim adapted synthesized`
  against `closed kind`.
- **`closed per-key`** — the value is a LIST of `key=value` items and
  EACH ITEM'S OWN key selects the set (§2.15's *"any `vocabulary`-
  declared key checked at its own `tag` site"*). A per-row selector
  cannot express it: the set is chosen per item.
- **`required-if`/`forbidden-if <field> <op> [value]`** with `op` in
  `==` / `!=` / **`present`**, and `parent` as the ONE reserved field
  name. `present` is the third op and is admitted under §2.25.3's own
  membership rule: three rows in ONE scope need it (§2.23's
  `kind`/`groups`/`note` are legal only beside `text`) and the
  two-operand form cannot express PRESENCE of a line whose value is
  unconstrained.

`under`'s row also gained `closed convention`, on the reading that a
`qualified-line`'s QUALIFIER is what `closed` applies to — which keeps
§2.15's vocabulary-closes-`under`'s-convention rule declared rather than
adding a second parser-code exception to a schema that claims exactly
one. `unique-by` gained a second extractor name, `first-word`
(`vocabulary`'s key); the D77 trigger §2.25.3 states is a second
`qualified-line` production, which this is not.

### 3.6 Four design sentences the build measured FALSE

Each was written as SHIPPED and reported rather than silently followed:

- **`oracle none <reason>` did not exist** (§2.9 states it). Built: a
  counted, PRINTED skip whose reason is REQUIRED, because a skip with no
  stated reason is the silent pass the production replaces.
- **An oracle's ENGINE half was a strict `ident`**, so `oracle
  pcre2-dfa` was refused while `variant pcre2-dfa` was legal — two
  answers to one question. It is a `defname` now, for `variant`'s own
  reason (real engine names are hyphenated slugs).
- **`provenance` was not required on a `freq` data block** (§2.10: *"Provenance
  is required, because the exemplar is absent by design"*). Added.
- **§2.18 says `--list-source` validates a `sha256`'s 64-hex SYNTAX.** It
  does not and structurally cannot at this seam: leg A recognises every
  expectation kind as `value: case` and reads NONE of them. The
  `--list-schema` `surface` section already declares that non-coverage —
  and its reason string ENDED MID-CLAUSE (`"the 64-hex-digit SYNTAX is"`),
  about to claim the opposite. Corrected to the truth; both harness legs
  do check.

---

## 4. THE TWO DEFECTS THIS STEP SHIPPED, AND WHAT FOUND THEM

Both were found by MEASURING a production against all three legs. Neither
was visible to the checks written for it, and that is the point of both
entries.

### 4.1 `under`'s key tuple was collapsed, and the refusing fixture passed anyway

`under_key` read the convention with `strchr(v, ':')`. **The spelling has
no colon** — §2.17's own production is `under <convention> <case-line>`,
space-separated; leg B's arm has no colon and leg C REFUSES the colon
form by name. With no colon the convention came out EMPTY and every later
component slid one place left, so the tuple was
`("", <convention>, "", <kind>)`:

| two `under` lines differing only in | must | shipped |
|---|---|---|
| SUBJECT | accept | **REFUSED as duplicate** |
| STARTPOS | accept | **REFUSED as duplicate** |
| kind | accept | accepted |
| convention | accept | accepted |
| the EXPECTATION (the real duplicate) | refuse | refused |

**The refusing cell passed for the wrong reason**, which is why the
regression is the ACCEPT half (`under_key_distinct.rxtin`, four lines
differing in one component each) and not the refusing one. The
transferable form: *a refuse-only pair proves a refusal happened and
never that it happened for its rule* — the same shape as
`w231_report.md`'s cardinality arm, which had to become two-directional
before S241 had a detector at all.

### 4.2 `prose_value` read the whole line on an indented one

`tok_len` stops at the first whitespace byte, so on an INDENTED line it
measures ZERO and `line_value` hands back the line INCLUDING its kind.
Every W1 caller of `prose_value` sat at indent 0 and was structurally
unable to see it; a `variant`'s `note |` sits at indent 2, where the
region silently does not open and its own continuation reaches S1 as an
orphan. The fix is `line_value(L->v[*i] + indent)` and the general form
is that **a helper written when every caller shared one value of a
parameter has an untested branch the day a second value arrives.**

---

## 5. WHAT THE BUILD FOUND THAT NEITHER DOCUMENT NAMED

**THE ATTACHMENT BRANCH HELD THREE MISTAKES UNDER ONE SENTENCE, and an
aux body is what made the third reachable.** *"Indented line continues
nothing (the declaration above it takes no continuation)"* is TRUE of a
deeper indent under a childless kind, and false in two other ways: (a)
nothing is open at all — a blank line, a column-1 comment or the start of
the file closes every attachment, so there is no declaration above to
take or refuse anything; (b) a RAGGED DEDENT, a line closing back to a
depth NOBODY OPENED. Inside an OPEN SUBTREE, where no kind takes or
refuses continuation, the shared sentence named a rule the subtree does
not have. All three legs carry all three sentences now, word for word.
The test for whether two refusals want one sentence or two is whether
their REPAIRS differ; these do (delete the indent; match an enclosing
depth).

**THE OPEN SUBTREE'S ONLY STRUCTURAL ERROR IS A RAGGED DEDENT.**
`aux_malformed_body.rxtin`'s first version indented a line FURTHER than
its neighbour and was ACCEPTED — correctly: inside a subtree any deeper
indent is a legal child, because the subtree has no rows and therefore no
kind that "takes no continuation". A fixture for a free tree's
malformation has to close back to a level nobody opened, and there is no
other shape.

**THE WAVE TIER'S POPULATION WENT TO ZERO, AND THE STEP ATE ITS OWN
WITNESSES.** `refuse_wave`'s NOT-IN-THIS-BUILD branch fires for a row
whose wave sits strictly between this build's and the RESERVED sentinel;
every W23 row's wave IS this build's now, and no fixture can construct a
member because the table is compile-time. `format_design.md` §1.3 and
§2.3 both state that emptiness in advance, so it is staging rather than a
finding — but three checks and two fixtures had to move:

- `wave2_keyword.rxtin` DELETED (its keyword, `include`, shipped) and
  `include_head.rxtin` added, asserting the acceptance. A file named for
  the refusal it pinned, asserting the opposite, would be a lie about
  itself.
- `unknown_kind.rxtin`'s token moves `tag` → `no-such-kind`, chosen
  because it cannot graduate the way `tag` did.
- **W23-S3 arm 4 gains an EXTRACTOR-HEALTH assertion.** W23.1 wrote *"a
  population of ZERO is also a failure here"* and was right for its
  reason — the arm had read 0 rows out of a real population of 7 because
  `read` collapsed the dump's empty TAB fields. That rule CONFLATES TWO
  ZEROS, and W23.3 is the pin where they part. The repair runs the SAME
  awk with the threshold lowered to 0, which must find rows; a zero there
  is still the broken-extractor zero and still fails. **The general form:
  a population of zero is a failure only while you cannot tell it from a
  broken instrument — make the instrument's health a separate
  non-vacuous assertion and the honest zero becomes reportable.**

**TWO SABOTAGE ANCHORS WENT STALE and one of them changed its COUNT.**
S196's per-block reset sequence now exists TWICE, because `pattern-esc`
is S2's second block opener — `SAB_COUNT` 1 → 2, since a plant in one arm
would leave `pattern-esc` blocks resetting correctly, i.e. would plant
HALF the hazard the row describes. S204's anchor moved twice (W23.2 gave
leg C's catch-all a class tag, W23.3 grew the arms above it); its intent
was re-verified by planting it on a scratch tree, where leg C ACCEPTS
`unknown_kind.rxt` and the clean tree refuses it. Both re-derived from
the LIVE source, never from `git show HEAD:`.

**LEG B AND LEG C CANNOT AGREE WITH LEG A ON A `pattern-esc` ROW'S DUMP
VALUE AT THIS PIN** (reported by the legs-B/C author). Leg A reports the
DECODED bytes; leg B cannot decode (§2.19 forbids a bash decoder), so
both harness legs report the text AS WRITTEN — B == C verified
byte-identical, A differs, population ZERO (no corpus file carries the
keyword). W23.4's `esc` column settles it, or leg B needs a pcrec surface
that prints a decoded operand.

**LEG B's `rxt_escape` DID NOT ESCAPE `\n`** — harmless until now,
because no dumped value could contain a newline. A prose region's value
is the first that can, and an unescaped one breaks TSV framing. Fixed to
match leg A's `put_escaped` and leg C's `DUMP_CTRL`.

**W23.2's "child-consumption mechanism" was the parent's identity only**
— no push, no pop, no consumption branch. Its own report's *"re-verify
the branch against a real schema row with a named `children` scope before
assuming it works"* was well placed: given one, it would have refused
every body line.

---

## 6. OWED

- **`make test`** — not run. The box constraint in this lane's brief
  forbids it (`build/battery_20260915_022106` has been in flight for the
  lane's whole working period). Everything in §2 was measured with the
  allowed set.
- **`make mech`'s real DETECTED run** for S240, S245 and the two
  re-anchored rows (S196, S204). All four are `VALIDATE_ONLY=1` FIELDS
  OK, and S240/S245/S204 were hand-verified DETECTED by planting them on
  a scratch build and reverting; the matrix run rides the next battery.
- **`make test-axes`, `make san`, `make lint`** — same constraint.

## 7. What a fresh agent needs to know

- **Leg A is the oracle and the two harness legs were written against
  it**, by measurement. `build/pcrec --list-source FILE` on a fixture is
  how any disagreement is settled; the class tag (not the sentence) is
  what the differential compares.
- **The schema's `value` and `constraints` columns are read in three
  places and the split is forced**: `value` at the LINE (a shape is a
  property of the line's text), `constraints` at the FRAME CLOSE (every
  condition names a SIBLING and siblings arrive in any order; `required`
  cannot be answered before the scope ends), `closed`/`unique-by` at the
  LINE (their refusals name a VALUE, and a value has a line). A frame
  closes at THREE sites — a lesser indent pops it, a new group replaces
  its contents, end of file — and the third is the one a reader misses.
- **`--list-schema` is the contract surface for all of it.** Every value
  shape, cardinality and constraint clause is fetchable there; the spec's
  schema section renders it, and W23-S3 drives each row's BEHAVIOUR
  rather than comparing the dump to the table.
- **What W23.4 inherits**: `#section aux`/`#section cases` and the
  appended `tags`/`oracle`/`esc` columns; R5's AND R6's repairs BEFORE
  any section is emitted; `aux_literal_pipe`'s value-level assertion; the
  `pattern-esc` dump-value disagreement above; S242/S243/S246.
- **What W23.3a inherits**: `include`'s HARNESS half in full. This step
  landed only the GRAMMAR — a file-scope declaration taking a
  double-quoted path, opening nothing. Spec row SW20 is still unlanded
  and is W23.3a's.
