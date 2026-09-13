# lane w23implfix — the r59 FIX ROUND on `w23_impl.md` (revision 1.1)

**[DD-13b.W23] STEP 1.6, 2026-09-13, opus, docs-only.** Branch
`lane/w23implfix`, cut from `lane/w23impl` (not from main). Object:
`docs/design/dd13_format/w23_impl.md`, revision 1 → **revision 1.1**.
Review of record: `docs/dev/reviews/2026-09-13-r59-w23-impl.md` — three
read-only critics, **4 blockers, 13 must-fix groups, all FIX-NOW**, plus
manager rulings **R1-R4** on §7.3's open questions.

**Nothing under `src/`, `tests/` or `docs/spec/` moved. No `make`, no
compile, no suite, no battery.** Every MEASURED fact below is a read, a
grep or a line count taken against this branch's merge base.

---

## 1. What was applied

The note's own **§0.5 is the finding-by-finding record** and is the
canonical answer to "was every disposition applied". All four blockers,
all thirteen must-fix groups, the five folded notes (A-N4, A-N5, B-N5,
B-N6, B-N7) and all four rulings are in it with their section numbers.
This report is what the fixes REVEALED, which is the part §0.5 cannot
carry.

Commits, in order: `82d10572` (wave 1 — status, the six-merge
correction, §1.1's reconciliation, the arm count, the §1.2 citations),
`17084c8f` (blockers A1/A2/B2), `202340dd` (§2 staging + §3 checks),
`89a25a61` (§4 spec delta + the re-scoped absence check), `f407ad10`
(blocker B1 + §5), `d775bf77` (§6.2/§6.3 + the new §6.3a brief),
`2f9c08ca` (§6.4/§6.5), `85ffcc54` (§7/§8), `1c4be2ce` (§0.5 + the
`format_design.md` drive-by), `70fd80bb` (the self-sweep's own
corrections), `949911f1` (bookkeeping).

Size: the note went 1,241 → 1,983 lines.

---

## 2. Six things the review did not anticipate

### 2.1 §4.3's absence check grepped the WRONG FIVE TOKENS, and two of the withdrawn spellings are LIVE IN THE TREE

r59-B-M1 found that the check's landing condition is unsatisfiable —
`provides` and `capable` occur as ordinary English (*"structurally
incapable of moving"*, *"provides the names it intends to export"*),
seventeen hits across `src/` and `tests/`, so a grep for them can never
return 0. That is right and it is applied.

**The larger half is that revision 1 grepped `configs describe`,
`configs build`, `provides`, `capable` and `cross-scope` — and the
withdrawals are FOUR productions, the fourth being `config`-body
`testee`/`option` (D99 / N-42), which the grep never contained.**
MEASURED, at this branch's merge base, `testee` and `option` are LIVE
FORMAT SPELLINGS at three sites:

| site | what it is |
|---|---|
| `src/parse/rxt_source.c:149` | `config_vocab` carries `{ "testee", 3 }, { "option", 3 }` — leg A RECOGNISES both today and refuses them by name with their wave |
| `docs/spec/rxt_format.md:57-62` | the later-wave keyword paragraph names both among the keywords *"recognised and refused by name, as NOT IN THIS BUILD"* |
| `tests/rxtsource/run_rxtsource_tests.sh:1188` | `CENSUS_WORDS_32` lists both, and the list's LENGTH is asserted against the literal `32` at `:1200-1206`, whose failure message reads *"It is format_design §1.1's list verbatim; if it changed, say so there too"* |

So the note's *"Both mechanisms are design-note-only at this pin, which
is why the withdrawal costs a diff and nothing else"* is true of
`configs` and `provides` and **false of `testee`/`option`**, which cost
four sites (parser row, spec sentence, census word list, census count
`32 → 30`) plus the design's own §1.1 list that the census pin cites.
**And the removal carries a deliberate narrowing nobody had stated**: a
`.rxt` writing `testee` in a `config` body goes from *"NOT IN THIS
BUILD, the keyword is real"* to *"not a config directive"* — the K14
shape running in reverse. It is correct (the keyword is no longer
real), and it now has a sentence in SW19.

§4.3 is rebuilt as **three arms**, and the third is deliberately not a
grep: the DATA arm (no `.rxt`/`.rxtin` line's first token is one of the
five — **MEASURED 0 of 262 files**), the PARSER arm (**MEASURED 1
today**, and its landing value is that it must read 0 after W23.1 — a
check whose baseline is zero from the start proves nothing about the
change that was made), and the SPEC arm, which is a READ, because
`rxt_format.md:130`'s *"configs are three artifacts with three
prefixes and ONE …"* is legitimate English that no pattern separates
from a production's spelling.

**The general lesson the section now carries**: an absence check is only
as good as its TOKEN LIST, and a token list derived from the two
mechanisms somebody remembers withdrawing will miss the third. Derive it
from the ruling's own enumeration, not from the section that discusses
them.

### 2.2 Spec row S3 has never landed, and the wave LABEL is what made it look landed

r59-B2 named this as part of the include blocker and it is worth
separating, because the mechanism generalises past `include`.

Revision 1's §4.1 closes with *"The W1-era rows S1-S11 are already
landed"*. **MEASURED, S3 has not.** `format_design.md:5782` labels it
**W1** — *"'How the harness evaluates a block' gains the cell notion
and the `perr` one-cell rule; the summary's reported quantities grow
(entry files, fragments, cells, resolution failures)"* — while
`docs/spec/rxt_format.md`'s own harness-evaluation section (`:531-565`)
has no cell notion, no entry/fragment counts and no resolution-failure
class; its summary paragraph reports cases passed/failed, the per-file
breakdown, the compile-failure count and the pending-vm count, and
nothing else. A grep of `docs/spec/` for `entry file`,
`fragments spliced` and `resolution failure` returns **zero**.

**A wave label says when a row was SCHEDULED, never whether it
SHIPPED.** Revision 1 read the label, found W1, and booked the row
discharged — which is exactly how the obligation `include`'s harness
half needed came to be marked done. It is now **SW20**, scheduled at
W23.3a, and §4.1 says so in place rather than deleting the false
sentence.

### 2.3 The review's own citation for the discovery site is wrong, and it inherited it from the ruled record

r59-B2 cites *"run.sh's `find`-based discovery (:184-216, never named in
the note)"*. **MEASURED: `run.sh:184-216` is the `tests/lib` shim
sourcing (`assoc.sh`, `loadavg.sh`, `dispatch_gen.sh`) and the `CC`
resolution.** The discovery is **`:293-307`** — the no-argument
`find "$ROOT_DIR/tests" -name '*.rxt' -not -path "*/known_fail/*"` at
`:296-297` and the directory-argument `find` at `:302` — and the
per-file worker dispatch begins at `:309`.

**The provenance is the finding**: `format_design.md` §2.11 opens with
*"the accounting unit is the FILE, because `tests/harness/run.sh` runs
one worker per file (`tests/harness/run.sh:184-216`)"*, so the critic
read the range out of the ruled document it was checking the note
against. The note now cites the true spans. **`format_design.md` §2.11
is NOT edited** — the brief scoped the drive-by to SW12 — and it is
flagged in §4 below as a one-line correction for the manager.

### 2.4 Three of the four S200-S203 rows carry a stale count, not one

r59-A-M4 names S200's `SAB_DESC` as already stale. **MEASURED, three
are:**

| row | what its `SAB_DESC` says | what is true |
|---|---|---|
| S200 | *"16 fields where the header declares 15"* | the header declares **16** |
| S202 | *"14 columns … 15 fields"* | **15** and **16** |
| S203 | *"all 179 corpus files"* | **210** |

All three are the same class — a pinned number in prose, drifting
silently because nothing reads it — and it is the class §1.5's whole
survey is about, occurring in the sabotage rows whose detectors §1.5
repairs. §6.4 item 6 re-states all three in the same commit as the
re-run.

### 2.5 The review's own arm-count parenthetical is wrong where its total is right

r59-B-M7 says leg B's chain is *"22 arms (18 pinned + 5 appended, per
format_design §2.25.5's own ruled count)"*. The TOTAL is right and is
what matters. **The split is not: MEASURED, 17 pinned + 5 appended.**
`format_design.md` §0.7 gives exactly that derivation (*"The remaining
22 split 17 inside the hash-pinned arm region (`:1713` BEGIN .. `:1967`
END) and 5 appended after it"*), and counting the `^`-anchored `=~`
arms in the file reproduces it: `:1714`, `:1742`, `:1759`, `:1767`,
`:1778`, `:1781`, `:1792`, `:1798`, `:1801`, `:1827`, `:1843`, `:1859`,
`:1875`, `:1891`, `:1907`, `:1918`, `:1942` inside the region, and
`:1984`, `:2000`, `:2015`, `:2057`, `:2092` after it. The note carries
the derivation rather than the number, per that section's own rule.

Two smaller corrections of the same kind: the note's appended-arm range
`:1984-2104` runs past the last appended arm (`:2092`) into the
catch-all, and is replaced by the per-arm enumeration; and
`format_design.md` §9's correction table holds **nine live rows**
(ten, minus the `capable` → `provides` row deleted at 3.4), which is
what §5 now points at.

### 2.6 `format_design.md` §9's A1 row carries the same unverified reading A2 did

r59-B-M5 asked whether bench A1's *"`include` at head and block scope"*
parses. **It does not**: `format_design.md` §1.3's EBNF puts `include`
in `decl-line` only, with no `include` alternative anywhere in a block
line, so A1's probe exits 1 at the delivered pin and their fix is one
line (move it to the head).

**The part worth the report: `format_design.md` §9's OWN A1 row reads
SATISFIED and enumerates the same block-scoped `include` as landing.**
So this is not only a gap in the implementation note — it is the r58-B1
shape recurring one row up in the ruled record, and for the same reason
(the keyword list was checked against the delivery; the SCOPE the
fixture types was not). **This lane did not edit `format_design.md` §9**
— the brief scoped its drive-by to SW12 — and the correction is in §4
below.

---

## 3. The SW12 drive-by, and what it cost to verify

The brief authorised one correction in `format_design.md`: SW12's wrong
comment-site ranges. Applied at `1c4be2ce`, in two places:

- **The SW12 row itself** (`:5811`): `:280-291` → **`:269-297`**
  (`defname_ok`'s header; the function opens at `:298`) and
  `:1126-1130` → **`:1177-1180`** (the `name` arm's pointer; the arm
  opens at `:1175`). The correction is recorded in place with its
  reason rather than applied silently, house style.
- **The r57 C-M2 disposition row** (`:544`), which carries the same
  ranges as single lines `:288` / `:1129`. Annotated rather than
  rewritten: `:288` does fall inside the true header span, `:1129` does
  not fall inside anything related — it is the file-level
  duplicate-`description` refusal, **a different production entirely**.

**What the second wrong range actually pointed at is the sharp part.**
`:1126-1130` is `parse_prose`'s neighbourhood in the file-level
`description` arm — a refusal about duplicate descriptions. A reader
following SW12's citation would have found a comment about the wrong
rule and had no signal that anything was wrong, because a plausible
comment at a plausible offset reads as a hit. The `name` arm's real
pointer comment is fifty lines further down.

**One refinement against the review's own text**: r59-B-M2 gives the
name-arm site as `:1176-1180`. `:1176` is `const char *v =
value_trimmed(&p, l);` — the statement above the comment. The comment
proper is `:1177-1180`, and that is what both documents now cite. The
one-line difference is recorded here rather than silently absorbed,
because this round is about not carrying ranges.

---

## 4. OWED to the manager — three corrections in `format_design.md` this lane did NOT apply

Each is a one-line edit in the ruled design note, outside the brief's
authorised drive-by. Named with its evidence so the manager can rule.

1. **§2.11's opening citation, `tests/harness/run.sh:184-216`** →
   `:293-307` (discovery) and `:309`+ (the per-file worker dispatch).
   This is the range the r59 review inherited (§2.3 above), so leaving
   it will re-seed the same wrong citation into the next document that
   reads §2.11.
2. **§9's A1 row** (`:7464`), which reads SATISFIED and enumerates
   *"`include` at head and block scope"* as landing (§2.6 above). It
   needs A2's treatment: split out as a bench CORRECTION, and added to
   §9's head correction list — which is also Appendix A's body, so the
   outbox message moves with it.
3. **§1.1's 32-word keyword list** (`:990`) and the
   `CENSUS_WORDS_32`/`32` pin it is cited by, once `testee`/`option`
   leave (§2.1 above). Not urgent — it is W23.1's work by the note's
   own plan — but the design's list is the pin's declared source, so
   whoever moves one moves both.

Nothing else is owed. This lane took no measurement that needs a build,
and every acceptance number in the note's §6 is a target for its step
rather than a claim this lane made.

---

## 5. The three-pass residue sweep, re-run on this revision's own diff

The brief required the sweep and required it over the fix round's own
output, because that is where the class recurred last time.

**Pass 1 — forward grep, with r59-B-M1's corrected scoping**, over the
ADDED lines of `lane/w23impl..HEAD`. Every hit for `configs
build|describe`, `testee`, `option`, `provides`, `capable`,
`cross-scope`, `tag-prose` is in a WITHDRAWAL context — describing the
removal, tabulating the measured absence, or citing §9's correction
list. **One neutral hit, and it is a happy demonstration of the
section it sits under**: §1.10.1's *"in the entry's own option scope"*
is `option` as ordinary English, exactly the class §4.3's new spec arm
exists for.

**Pass 2 — mechanism check.** No withdrawn mechanism has an
implementation in any step. The two claims a re-entry would have to
contradict are both intact: **SEVEN** constraint kinds (nine statements,
no "eight" anywhere as a live claim) and **THREE** structure-layer
parameters over three columns (the only "two" is §0.4's explicit
warning not to carry a memory of it). The one step that touches a
withdrawn spelling REMOVES it (`config_vocab`'s two rows, W23.1).

**Pass 3 — read every claim this revision makes about another document,
against that document.** Twenty-three claims checked. **Twenty-one
held.** The two that did not were caught here and fixed in `70fd80bb`:

- The 22-arm derivation is `format_design.md` **§0.7** (the revision 3.1
  record), not §0.6 as first written.
- `utf8k53_report.md`'s census-catches-a-fixture-leak finding is
  **§5.2**, not §5.

The same pass caught four stale items in this revision's own text that
are not claims about other documents but would have read as ones: the
`src/opt/mrl.c` house-rule cite (`:18-24`, the two-units paragraph →
`:39-45`, the exhaustive-switch rule), the fixture-directory count
(46 → **49** files), four surviving "five merges" statements, and
§3.1's "Five new assertions" where the table now holds six.

**Net: TEN wrong `file:line` ranges and FOUR wrong counts corrected
across the revision.** The ranges: `Makefile:121-137`→`:118-146`,
`limits_dump.c:57`→`:55`, `cli/main.c:1230`→`:1216`,
`rxt_source.c:280-291`→`:269-297`, `:1126-1130`→`:1177-1180`,
`:826-830`→`:848-851`+`:856-861`, `:840`→`:863`,
`mrl.c:18-24`→`:39-45`, `run.sh:1984-2104`→ the per-arm enumeration
ending `:2092`, and `run_rxtsource_tests.sh:499-500`→`:499-505`. The
counts: 46→49 fixtures, 63→61 `rxt_fail` call sites, seventeen→22 arms,
and the Makefile comment's "twice"→"three times" (its third instance,
`uprops_tables.inc` at [M5.0] stage 3, is in the same comment and is
the one that made `gen-tables` a LIST rather than another hand-kept
line).

**The method note this round adds**, and it is why §7.1 gained item 6:
the previous rounds' residue class was DISPOSITION TEXT — a sentence
describing a withdrawn production as current. **This round's was
CITATION PROVENANCE** — a `file:line` correct on the day it was written,
carried forward through two documents, and read by a third as a fact
about today's tree. A forward grep cannot see it, an inverse mechanism
walk cannot see it, and the third pass sees it only if the pass opens
the file rather than comparing two documents to each other. Both of
SW12's ranges survived r57, r58 and r59's own citation lens in
`format_design.md`, and were only caught because r59-C went to the
source.

---

## 6. What a fresh agent resumes from

- The note is `docs/design/dd13_format/w23_impl.md` at **revision 1.1**
  on `lane/w23implfix`, branched from `lane/w23impl`. Docs-only.
- **§0.5 is the r59 record**; the design it implements is
  `format_design.md` **3.4.1** and wins on any disagreement.
- **The delivery is SIX merges** — W23.1, .2, .3, **.3a**, .4, .5 — and
  W23.3a (`include`'s harness half, §1.10 / §6.3a) is the one revision 1
  did not have.
- **The W23 Frank queue is EMPTY.** R1-R4 were the four open questions
  and the manager ruled all four; this revision adds none.
- §4 above is the only thing owed, and it is the manager's to rule, not
  a lane's to apply.
