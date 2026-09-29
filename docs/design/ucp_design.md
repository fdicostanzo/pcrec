# [UCP] — THE DESIGN NOTE: the UCP surface, one context node, and the character island

Lane `ucpdes` (opus), branch `lane/ucpdes`, on `main` at `4bb74bda`,
2026-09-28. **Design only**: nothing under `src/`, `cli/`, `lib/`, `tests/`,
`docs/spec/`. The plan row is `docs/dev/plan.md` [UCP] (design opened by
Frank 2026-09-28, D129 Q7). This note answers the eight things the lane brief
asks it to DECIDE (§1-§8). A light D6 panel reviewed it; findings and
dispositions are in `docs/dev/reviews/2026-09-28-r1-ucp-design.md`, and the
fixes are made inline, marked **[r1 ID]**.

**Status: PROPOSED.** Frank rules §8.

**Sources.** Every number names its file. Five kinds, not interchangeable:

| tag | what | where | citable for |
|---|---|---|---|
| **[O]** | NEW oracle probes, this lane: libpcre2 **10.46** (ubuntubudu, ssh-stdin, writes nothing remote) and 10.48 (local); identical on every relation and point, only set SIZES differ (Unicode version) | `docs/design/ucp_measurements/out/{ucp_sets,ucp_points}_10.4{6,8}.txt` | UCP semantics |
| **[M]** | NEW box-independent models/censuses, this lane (python, exhaustive, with failing-direction controls) | `ucp_measurements/out/{bottom_model_10.46,segment_sym,ctx_sets_9399d927,illformed_ctx_cells}.txt` | the ill-formed rule, the context-set population |
| **[S]** | the study (lane ucpthink) and the shape census (lane lacensus) | `docs/dev/ucp_study.md`, `docs/dev/lookaround_census.md` | demand, `\b` equivalence, sizes |
| **[C]** | [CLS-TREE]'s design note, its study and its ubuntubudu timing run | `docs/design/cls_tree_design.md`, `studies/cls_tree_study/results/bench_ubuntubudu_20260911.tsv` | the kit, its sizes and ns/char — the only citable timing here |
| **[P]** | a probe of the shipped compiler, `build/pcrec` at `4bb74bda`, `-e utf8 --features all` | quoted inline | what pcrec does today |

No darwin timing appears anywhere, and nothing here needed any.

---

## 0. The decisions, in one table

| # | question | DECISION | rests on |
|---|---|---|---|
| **UD-1** | UCP's semantic surface and spelling | a new module **`ucp`** owning the `(*UCP)` verb and a `--ucp` generation axis (plus an `.rxt` flag letter); **not** on by default under `-e utf8`. Its lowering is the **definitions table's `DEF_UCP` rows** (D85's chartered second row), one tag per PCRE2 ASCII-restriction family so `(?aD)/(?aS)/(?aW)/(?aP)/(?aT)` become real. Two caseless rules: POSIX `[:lower:]`/`[:upper:]` are **fold-inert** under UCP, and an ASCII-restricted set folds by the **ASCII** fold. UCP without UTF (`-e byte`) is the same definitions under the byte universe plus a Latin-1 fold. `-e utf8` ENABLES (does not switch on) `unicode-props` and `ucp` (O-71) | [O] 57 set relations + 20 points; §1 |
| **UD-2** | normalize-then-recognize (Frank's Q1-Q3) | **ADAPT.** Normalize to a **NODE**, not to text: `\b`, `\B` and every lookaround whose body's LANGUAGE is a set of single characters become ONE general zero-width **context-assertion node** (`A_CTX`: a set, a side, a truth function — `N_WORDB` generalized). The DFA implements it natively; `\b`'s producer builds it directly (byte-identical by construction for every shipped `\b`); lookarounds reach it by recognition. Q1 NO, Q2 YES, Q3 YES — **158 of 172** all-one-character lookaround patterns need no island | [S] §C, [M] `ctx_sets`; §2 |
| **UD-3** | the island | **a CHARACTER-STEPPED DFA MACHINE MODE**: ASCII bytes step the table as today; every non-ASCII byte class's cell is either an ordinary cell or an **island entry** reached through [OPT-EDGE]'s existing top-row stop test (zero added compare on the ASCII path). The island decodes ONE character (the `PCREC_ENCE_DECODE` entry, CT-5), computes the character's **membership vector** over the machine's non-ASCII sets, records the accept, and resumes at a target state — or consumes an ill-formed byte as the pseudo-character **⊥** (in no set, not a word character). UCP `\b` needs **no new view kind**: the consumed side stays in state identity, the next side is the island's vector. One mechanism serves UCP and [CLS-TREE]'s wide classes | [M] 209/0 + 3.37 M/0; §3 |
| **UD-4** | the predicate's forms | the island's interface is "the membership vector of one decoded character"; its producers are (i) one [CLS-TREE] kit predicate per set (built first), (ii) a multi-valued **atom map** (a proposed kit member: page-table leaves carry atom ids), (iii) the **[UCD-RECORD]** shared record, one probe for a bitmap of standard classes, linked once via **[XART-TABLES]**. (ii)/(iii) are dial choices with named D77 triggers, not built first | [C] [T]; §4 |
| **UD-5** | [CLS-TREE] interaction | the island (stage U3) needs **S1** (the kit in `src/`) and **S3** (`A_WCLASS`, a wide class arrives at the NFA as one node), and introduces `PCREC_ENCE_DECODE` itself if it lands before **S4**. U0, U1 and U2 start **now**, before any [CLS-TREE] stage | §5 |
| **UD-6** | staging | U0 registry/O-71 → U1 surface (small tier + byte tier; wide sets refused by name until a kit-sized route exists) → U2 `A_CTX` (byte-expressible sets; moves lookaround patterns VM → DFA) → U3 island (after a ubuntubudu hand-twin measurement) → U4 VM UCP `\b` (after S4). Checks, sabotage shapes and abi events per stage in §6 | §6 |
| **UD-8** | every selection as a table | eight first-match tables T1-T8 (§0.1): definitions, fold, lookaround lowering, machine form, state cell, vector producer, table linkage, VM context test; each row is data (name + one-line predicate) for [LIST-TABLES]; the one optimizer (the sectioning DP) lives inside T6's `kit` row | Frank 2026-09-28; §0.1 |
| **UD-7** | measurements owed | Mac: the `A_CTX` identity sweep, the per-state vector-width census, island twin correctness. ubuntubudu: the island-vs-all-byte per-char timing (the D77 trigger for U3), the U2 DFA-vs-VM throughput on the moved patterns | §7 |

---

## 0.1 Every selection in this note is a first-match TABLE (UD-8)

Frank's standing requirement (2026-09-28): a selection is an ORDERED list of
rows — name, deny flag, an `applies` predicate stated as a measurable fact,
an action — walked first-match, a non-applying or denied row transparent, the
last row always true. The precedent is `dfa_pfs[]` + `DFA_SELECT`
(`src/gen/emit_dfa.c:4544`, `:5804-5815`) and D122 addendum 4 ("one selector
decides every scan form"). An OPTIMIZER may live inside one row's action
(ruled); a nested if/else chain deciding a form or route may not. **Every
table below is DATA — each row carries its name and a one-line predicate
description — so `[LIST-TABLES]`'s future `--list-…` option and the
per-artifact "which row fired" stamp are plain reads of it** (the
definitions table already has such a listing, `--list-definitions`).

Deny flags are PROPOSED spellings; the implementer names them. A row whose
denial would change ANSWERS rather than form carries no deny flag (D125's
STRUCTURALLY INELIGIBLE bucket, opt_dial_inventory.md §2.25) — those are the
semantic tables T1-T2.

**T1 — a class construct's definition** (per construct, the D85 definitions
table; the rows ARE `RegDef` entries, walked by `pcrec_def_resolve`, which is
already first-match with a `DEF_ALWAYS` terminal — `definitions.c:66-99`).
Example: `\w`; every class escape and POSIX name has the same two-row shape,
its tag from §1.4's family column.

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `ucp` | — (semantic) | `DEF_UCP_W`: the node's resolved mods have UCP ∧ ¬`aW` | the UCP set (`\p{Xwd}`); for `[:lower:]`/`[:upper:]` the set is marked fold-inert |
| 2 | `ascii` | — | `DEF_ALWAYS` | today's set (`cls_bits.inc`) |

*Order*: UCP is the more specific condition; `DEF_ALWAYS` is the ruled
terminal. `\b`/`\B` are rows of the same table whose action is `A_CTX` with the
UCP or ASCII word set (§2.2).

**T2 — a class contribution's fold** (per contribution, at construction; one
table serving every class site — today this is a per-caller argument,
`parse.c:640-660`, and the table replaces the argument with rows).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `none` | — | `(?i)` is off | contribution unfolded |
| 2 | `inert` | — | UCP ∧ the contribution is `[:lower:]`/`[:upper:]` (§1.3 rule 1) | added unfolded |
| 3 | `ascii-named` | — | the contribution is a named/ASCII-restricted byte set (§1.3 rule 3; today's named-byte-set rule) | `pcrec_fold_ascii` |
| 4 | `latin1` | — | encoding `byte` ∧ UCP | Unicode simple fold restricted to Latin-1 pairs (§1.5) |
| 5 | `encoding` | — | always | the encoding's own fold (`PcrecEnc.fold`) |

*Order*: each row is a narrowing of the next one's population; rows 2-3 are
exceptions to 4-5 by measurement ([O] §1.3), so they precede them.

**T3 — a lookaround's lowering** (per `A_LOOK`, the recognition pass, §2.2).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `ctx-node` | `-fno-ctx-node` (the answer-identity axis) | body is capture-free and assertion-free and its LANGUAGE is a set of single characters | `A_CTX(set, side, fn)` |
| 2 | `lookaround` | — | always | today's `A_LOOK` lowering |

**T4 — the DFA machine's non-ASCII form** (per MACHINE, `-e utf8`; under
`-e byte` row 5 always fires). "Wide" and "byte-expressible" are the facts
§2.3 and §3.7 define; θ is a pinned `--tune` cell read by the predicate (the
dial lives in the row's predicate, D82's one decision point).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `island-forced` | `-fno-cls-island` | some CONTEXT set has a non-ASCII member (no all-byte form is exact, §2.3) | character-stepped mode (§3) |
| 2 | `bytes-under-theta` | `-fno-cls-bytes` (the island's identity axis: denying it forces row 3) | every CONSUMING non-ASCII set is byte-lowerable and their summed byte-automaton states ≤ θ | all-byte mode (today's lowering) |
| 3 | `island` | `-fno-cls-island` | some consuming non-ASCII set exists | character-stepped mode |
| 4 | `bytes` | — | no context set has a non-ASCII member | all-byte mode (the K53 ladder as today) |
| 5 | `decline` | — | always | the DFA route declines this machine: engine selection's own table routes the pattern to the VM (a `forces_registry`-style reason, stamped) |

*Order*: row 1 first because when it applies rows 2 and 4 would be WRONG, not
slower (§2.3's hazard cells); row 2 before 3 because it is the narrower
(dial-admitted) case; row 4 is what a denied island leaves when it is still
exact; row 5 is the always-true fallback — `-fno-cls-island` on a machine
with a non-ASCII context set lands here, never on a sampled answer. The
engine (DFA vs VM) is NOT re-decided here: row 5 is this table reporting "no
DFA form", read by the existing engine-selection table.

**T5 — a character-stepped state's non-ASCII cell** (per state, inside T4's
island action).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `dead` | — | every non-ASCII character and ⊥ lead to dead, and no accept depends on the next character | dead cell |
| 2 | `self-loop` | `-fno-island-fold` | every non-ASCII character and ⊥ lead back to this state with the same context (§3.3) | ordinary self-loop cells |
| 3 | `island` | — | always | an island token (§3.1) |

**T6 — the island's vector producer** (per island vector, §4; built rows 3
only at U3 — rows 1-2 are FILED rows whose predicates are false until their
producers exist, so the table's shape does not change when they land).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `ucd-record` | `-fno-ucd-record` | every set in the vector is a standard class the record carries ∧ vector width ≥ K_rec (a `limits.def`/tune cell set by §4's trigger measurement) | one [UCD-RECORD] probe, bits tested |
| 2 | `atom-map` | `-fno-atom-map` | vector width ≥ 2 ∧ the atom map's bytes ≤ the tune position's size budget | one multi-valued page-table lookup |
| 3 | `kit` | — | always | one kit predicate per set, OR'd into the vector; **each predicate's FORM is chosen by [CLS-TREE]'s sectioning DP inside this action** (CT-1/CT-2: kit members + whole-set tables) — an optimizer inside a row, not a table beside it |

*Order*: most amortizing first; the kit is always valid. The binary search
(`BSEARCH`) and the whole-set page table/bitmap are not rows here — they are
the DP's candidates inside row 3, priced by CT-2's per-probe model.

**T7 — a large table's LINKAGE** (per emitted table, [XART-TABLES]; FILED, not
built).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `shared` | `-fno-shared-tables` | the table's bytes ≥ a pinned floor ∧ its content is a general table (a `\p`/UCP set or the record) | content-hash-named COMDAT/weak definition, linked once per program |
| 2 | `static` | — | always | `static const` in the artifact (today) |

*Orthogonal to T6*: T6 picks WHAT the table is, T7 how it links — two
questions, two tables, never one nested chain.

**T8 — a VM `A_CTX` side's test** (per side, §6 U4).

| # | row | deny | applies | action |
|---|---|---|---|---|
| 1 | `byte` | — | the set is byte-expressible (§2.3) | today's byte read (`emit_vm.c:7902`'s shape with the node's set) |
| 2 | `decode` | — | always | `back_step`/`$_decode` + the set's T6 producer |

---

## 1. UCP's semantic surface (UD-1)

### 1.1 What `(*UCP)` / `PCRE2_UCP` changes, and what it does not

The study ([S] §B.1) measured the headline sets; this lane closed the rows it
left open and added the complements, the knobs and caseless. [O]
`ucp_sets_10.46.txt`, 57 rows, **0 differing from the stated expectation**
(the two rows whose expectation was a guess were wrong, and are kept as DIFF
rows that record the correction — §1.3):

| construct | under UTF\|UCP (10.46) | its definition, checked as a set equality |
|---|---|---|
| `\w`, `[[:word:]]` | 144,969 | `\p{Xwd}` |
| `\d`, `[[:digit:]]` | 760 | `\p{Nd}` |
| `\s`, `[[:space:]]` | 26 | `\p{Xsp}` = `\p{Xps}` |
| `[[:alpha:]]` / `[[:alnum:]]` | 141,028 / 142,939 | `\p{L}` / `\p{Xan}` |
| `[[:lower:]]` / `[[:upper:]]` | 2,258 / 1,858 | `\p{Ll}` / `\p{Lu}` |
| `[[:blank:]]` / `[[:cntrl:]]` | 19 / 65 | `\h` / `\p{Cc}` |
| `[[:xdigit:]]` | 44 | ASCII hex ∪ U+FF10-19, FF21-26, FF41-46 |
| **`[[:punct:]]`** | 864 | **`\p{P}` ∪ (`\p{S}` ∩ ASCII)** — study §B.1's formula, now a verified equality |
| **`[[:graph:]]`** | 154,973 | **`[^\p{Z}\p{C}]` ∪ (`\p{Cf}` minus U+061C, U+180E, U+2066-2069)** — NEW; the naive `[^\p{Z}\p{C}]` misses 164 (control row) |
| **`[[:print:]]`** | 154,991 | **`[^\p{Zl}\p{Zp}\p{C}]` ∪ (`\p{Cf}` minus U+061C, U+2066-2069)** — NEW (U+180E is IN `[:print:]` and OUT of `[:graph:]`) |
| `\W` `\D` `\S` `[\W]` `[^\w]` `[[:^alpha:]]` | complements | each equals the complement of its positive definition (6 rows) |
| `\h` `\v` `.` `\R` `\p{..}` | unchanged | `\h`/`\v` are already Unicode under UTF ([S] §B.1); `\p` sets are UCP-independent ([S]) |
| `\b` `\B` | read UCP `\w` | [S] §C: 579,195 subjects × 3 modes, 0 disagreements with the lookaround spelling |

Study open question 9 (`[:graph:]`/`[:print:]`) is therefore **closed by
derivation from the oracle**, as it asked: both are general-category formulas
with a four-code-point Cf carve-out, which `unicode-props`' tables can express.

### 1.2 The module, the axis, and the verbs (O-71)

**The module is `ucp`**, a drop-in module per the convention: parser hook (the
`(*UCP)` verb row, the `--ucp` axis, the `(?a…)` letters' UCP meaning),
lowering (§1.4), `tests/ucp/`. Until built, `(*UCP)` refuses **"requires module
'ucp'"** — today it says `verbs`, which `--features all` cannot satisfy
(O-71; the registry must name the right owner, D26's exact tier).

**UCP is a generation axis, not a default.** `--ucp` on the CLI, `(*UCP)` at
pattern start (PCRE2's own spelling, [S] §B.4: only at offset 0, combinable
with `(*UTF)` in either order), and an `.rxt` flags letter (spelling is the
manager's, memory `pcrec-dd13b-syntax-is-managers`). **Not UCP-by-default
under `-e utf8`**: PCRE2's `PCRE2_UTF` alone reads `\w`/`\b` as ASCII, and
D26 makes what a pattern MATCHES the exact tier — a default flip would change
the answer of every shipped `\w`/`\b` utf8 artifact against the source of
truth. The study's imported-pattern drift ([S] §A.3, ≥ 7 of 29 wild bench
imports come from Unicode-`\w` ecosystems) is a real cost of that choice, and
a diagnostic question (Q8's `-e utf8` note), not a semantic one. Q1.

**O-71, adopted as Frank suggested it**: under `-e utf8` the modules
`unicode-props` and `ucp` are **enabled** — a `\p` under a UTF-8 encoding is
the ordinary case, and `(*UCP)` is then accepted. Enabled is not ON: UCP
semantics apply only when `(*UCP)` or `--ucp` says so. **`(*UTF)`** under
`-e utf8` is accepted as a restatement; under `-e byte` it is **refused by
name** ("`(*UTF)` requires `--encoding=utf8`") rather than switching the
encoding from inside the pattern, because the encoding is a property of the
ARTIFACT's entry points (D18's per-compile axis), and a pattern that silently
re-typed its own subject would make `-e` a default rather than a declaration.
Q2.

### 1.3 The caseless rules — three, all construction-time

[O] rows, 10.46 = 10.48:

1. **Under UCP, `[:lower:]` and `[:upper:]` are FOLD-INERT.** `(?i)[[:lower:]]`
   ≡ `[[:lower:]]` (2,258 both), `(?i)[[:upper:]]` ≡ `[[:upper:]]`,
   `(?i)[^[:lower:]]` ≡ `[^[:lower:]]`; point probes: `(?i)[[:lower:]]` vs
   `A` nomatch, vs U+212A KELVIN nomatch, `(?i)[[:upper:]]` vs U+017F nomatch.
   Control: `(?i)\p{Ll}` is 4,147 ≠ 2,258 — the property spelling DOES fold.
2. **Folding is per CONTRIBUTION, and the inert one does not infect the
   class.** `(?i)[[:lower:]x]` ≡ `[[:lower:]xX]` (2,259) — the `x` still
   folds; `(?i)[\p{Ll}[:lower:]]` ≡ `(?i)\p{Ll}` (4,147) — the `\p{Ll}`
   contribution folds and swallows the inert one. This is stage 4's shipped
   per-contribution fold rule (utf8_design.md §4.2/§4.3) with one new
   contribution kind: *added unfolded*.
3. **An ASCII-RESTRICTED set folds by the ASCII fold**, even under UTF|UCP:
   `(?aW)(?i)\w` is exactly `[A-Za-z0-9_]` (63; NOT 65 with KELVIN and LONG
   S), `(?aP)(?i)[[:lower:]]` exactly `[A-Za-z]` (52). This lane's first
   guess (that the Unicode fold would cross into U+212A/U+017F) was WRONG,
   and the two rows are kept as DIFF rows recording it. It is the SAME rule
   `src/parse/parse.c:640-660` already applies to a named byte set without
   UCP ("a NAMED BYTE SET ... folds by `pcrec_fold_ascii` AT EVERY ENCODING"):
   an ASCII-restricted set IS the named byte set, so the rule is reused, not
   added.

Every other UCP set is **fold-closed** ([O]: `\w \W [:alpha:] [:alnum:]
[:graph:] [:punct:] [:xdigit:]` each equal under `(?i)`), so for them the
fold question does not arise. **Why this is construction-time only**: the
class node holds the folded set (CT-7), so rules 1-3 are rules about how the
set is BUILT, and the kit, the island and the VM never see caseless at all.

**Side finding (a comment, not a behaviour):** `src/parse/parse.c:652-657`
says `[[:lower:]]` "DO[ES] match [U+212A] once `PCRE2_UCP` is added". Measured,
it does not (`(?i)[[:lower:]]` vs U+212A under UTF|UCP: nomatch, [O] points).
The comment's conclusion — use the ASCII fold for named sets absent UCP — is
right and stays; its UCP clause is wrong and U1 corrects it.

### 1.4 The lowering: `DEF_UCP`, and the ASCII-restriction knobs

`src/parse/definitions.c` already carries a `DEF_UCP` tag with **no
producer** ("the FUTURE second row for a family this table already carries
(class escapes' UCP …)"), and `registry.c:190-200` names every class-escape
row's `DEF_UCP` entry as "each family's chartered second row". UCP IS that
producer. Building it any other way — an `if (ucp)` in each class-escape port —
is the parallel mechanism the general-mechanisms rule forbids.

**The tag splits by PCRE2's restriction family**, because PCRE2 10.43+ ships
partial UCP as five letters and pcrec already ACCEPTS them as no-ops
(`src/parse/mod_modifiers.c`, correct only while UCP does not exist). [O]
measured what each touches:

| tag (name is the implementer's) | answers true when | covers | [O] evidence |
|---|---|---|---|
| `DEF_UCP_D` | UCP ∧ ¬`aD` | `\d \D` | `(?aD)\d` = `[0-9]`; `(?aD)` leaves `[:digit:]` UCP |
| `DEF_UCP_S` | UCP ∧ ¬`aS` | `\s \S` | `(?aS)\s` = the 6 ASCII spaces |
| `DEF_UCP_W` | UCP ∧ ¬`aW` | `\w \W` **and `\b \B`** | `(?aW)\w` = 63; `(?aW:x\b)` on `xé` matches (ASCII `\b` inside the scope), `x\b` does not; `(?aW)` leaves `[:word:]` UCP |
| `DEF_UCP_P` | UCP ∧ ¬`aP` | POSIX classes except the digit pair | `(?aP)[[:alpha:]]` = `[A-Za-z]`, `(?aP)[[:word:]]` = 63; `(?aP)` leaves `\w` UCP |
| `DEF_UCP_T` | UCP ∧ ¬`aP` ∧ ¬`aT` | `[:digit:] [:xdigit:]` | `(?aT)[[:digit:]]` = `[0-9]`, `(?aT)[[:xdigit:]]` = 22; `(?aT)` leaves `[:alpha:]` UCP |

`(?a)` sets all five, `(?-aW)` unsets, `(?aW:…)` is scoped ([O] rows). Scoped
modifier state is resolved at parse time onto the node (assertions_design.md
§8's invariant) — so a `\b` inside `(?aW:…)` carries the ASCII word set as its
own datum, which is exactly what §2's node stores. The closed-enum tag with
one exhaustive no-`default:` switch is D85's ruled predicate shape (r43).

**The definitions**, one per row, are §1.1's right-hand column. Three details:

- `[:lower:]`/`[:upper:]`'s UCP definition is `\p{Ll}`/`\p{Lu}` **marked
  fold-inert** (§1.3 rule 1). It cannot be the textual `\p{Ll}` — that folds
  — so the definition is set-valued with the marker, not a string.
- `[:graph:]`/`[:print:]`/`[:punct:]` need unions/differences of property
  sets; the cpset algebra already has union/complement (stage 3), so these
  are compositions of existing tables, not new tables.
- **The definitions table is not yet wired into parsing** ([DD-11.5], gated on
  M6.6's exact lookbehind lowering, which has since shipped). U1 is its first
  wiring customer **for the class-escape family only**; the gate's hazard
  (DFA lookaround erasure) does not apply to a set-valued class definition.
  That scoping is a U1 claim the panel should check.

### 1.5 UCP WITHOUT UTF — the byte tier

Under `-e byte`, `(*UCP)` means PCRE2's `PCRE2_UCP` without `PCRE2_UTF`: the
bytes are Latin-1 code points. **It is §1.4's definitions evaluated under the
byte encoding's universe [0, 0xFF]** — pcrec's `\p` already works under
`-e byte` (utf8_design.md §3.2), so the same `\p{Xwd}` definition clamps to the
134 Latin-1 word bytes with no second table. [O]/[S] checks: `\w` has 0xB2
(No, in Xwd), `[:alpha:]` has 0xAA (Lo), `[:punct:]` has 0xA7 (Po) and lacks
0xA2 (Sc, non-ASCII — the `\p{S} ∩ ASCII` clause), `\d` is `[0-9]`, `\s` adds
0x85/0xA0 ([S] §B.3), `(?i)[[:lower:]]` vs `A` nomatch (rule 1 holds here too).

**The fold changes with it**: `UCP|CASELESS` without UTF folds the 30 Latin-1
pairs ([S] §B.3; utf8_design.md §4.5). So "which fold" becomes a function of
(encoding, UCP): byte = ASCII; byte+UCP = the Unicode simple fold restricted to
pairs inside Latin-1; utf8 (either) = Unicode simple. `(?r)` stays a no-op
under byte+UCP (`PcrecEnc.restrict_ok` stays true): no Latin-1 pair crosses the
ASCII boundary, and [O] confirms `(?i)(?r)\xe9` vs `\xc9` still matches.
Every byte-tier set is a 256-bit set, so **the byte tier needs no island and
no kit**: the existing class machinery, and `\b`'s existing byte mechanism with
a Latin-1 word set (§2), carry it entirely. Q4.

### 1.6 The oracle side

`docs/design/oracle_interface.md` scoped `OracleId.config` to answer-affecting
fields and **explicitly excluded `PCRE2_UCP` as having no producer**. U1 is the
producer, so `config` gains `UCP` — a store-format event under that design's
own fourth staleness claim (format versioning), taken in U1's change. The
membership kind then carries UCP sets exactly as it carries `\p` sets today
(387/387 at 10.46).

---

## 2. Normalize-then-recognize (UD-2): ADAPT — normalize to a node

### 2.1 Frank's three questions, answered

- **Q1 — does the VM's own conversion of the lookaround form help a UCP `\b`?
  NO.** The lookaround spelling over `\p{Xwd}` is REFUSED on every engine today
  (2,275,105 B of VM code against the 500,000 cap, [S] §C.3), and even with
  the kit it is two lookaround sub-matches (each a resume frame, a saved
  cursor, a decode and a class test) where the direct test is one decode and
  one kit call per side. A UCP `\b` on the VM is `back_step` + decode + kit
  and decode + kit (§6 U4); converting through the lookaround form buys
  nothing and costs frames.
- **Q2 — is the DFA's detection set larger than `\b`? YES.** Every lookaround
  whose body's language is a set of single characters is the same kind of
  thing as `\b`: a function of *the class of the character before* and *the
  class of the character after* the position. `(?=C)` is "next ∈ C" (false at
  the end), `(?!C)` its negation, `(?<=C)` "previous ∈ C" (false at the
  start), `(?<!C)` its negation; `\b` is `prev∈W ⊕ next∈W`. The DFA already
  implements exactly that shape for `W` (the class-axis views + the consumed
  class in state identity, internal.h:1682-1722) — generalizing the SET is the
  whole change.
- **Q3 — does it widen the DFA route? YES, measurably.** [S] lookaround census:
  of the 493 patterns that are VM-routed with lookaround as the ONLY excluding
  construct, **172 (34.9%)** have every lookaround one-character-shaped (bench
  44.4%, non-matrix corpus 49.2%). [M] `ctx_sets_9399d927.txt` over those 172:
  **171 read exactly ONE distinct context set** (one reads two), and **158 are
  servable WITHOUT the island** — 156 byte-encoded plus 2 utf8 whose sets are
  ASCII-only; the other 14 utf8 patterns read a set with non-ASCII members and
  need U3.

### 2.2 The decision: one context NODE, not a text rewrite

The literal form of the idea — rewrite `\b` to its lookaround TEXT and let each
engine re-detect — is **rejected as the production path**, for three measured
reasons: without perfect re-detection it moves 72-85% of `\b` patterns off the
DFA ([S] §C.3); every engine must then re-derive what the parser knew; and the
recognizer must cover every spelling the primitive covers or the normalization
regresses (the plan row's own named hazard). What is **adopted** is the
recognize half, generalized:

> **`A_CTX`** (name the implementer's): a zero-width node carrying a
> code-point SET `C`, and a truth function over the two booleans
> `(prev ∈ C, next ∈ C)` — with "absent" (start/end of subject) and "⊥"
> (an ill-formed side, §3.5) reading as NOT in `C`. `\b` is
> `A_CTX(W, prev⊕next)`, `\B` its complement, `(?<=C)` is `A_CTX(C, prev)`,
> `(?!C)` is `A_CTX(C, ¬next)`, and a position with several one-character
> assertions is several nodes in a row (the closure evaluates each).

- **`\b`/`\B`'s producer builds `A_CTX` directly**, carrying the word set its
  scope resolved (ASCII `W`, UCP `\p{Xwd}`, `(?aW)`'s ASCII `W`, or the Latin-1
  `W` of the byte tier). For the ASCII word set this is `N_WORDB`/`N_NWORDB`
  with its set made explicit, so every shipped `\b` artifact is **byte-identical
  by construction** — and the identity gate over every `\b` pattern in the
  corpus and bench (130 in [S] §C.3's census) is the control that says so.
- **Lookarounds reach `A_CTX` by a recognition pass** over the parsed tree,
  before engine selection: an `A_LOOK` whose body is capture-free,
  assertion-free and whose **language** is a set of single characters becomes
  `A_CTX`. The predicate is over the LANGUAGE, not the syntax — `(?<=a|b)`
  and `(?=[ab])` are the same node — which is [ENG-ISL] STEP 1's recorded
  lesson (the per-branch predicate was measured wrong there,
  alt_dispatch_study.md). Non-atomic `(?*C)` with a one-character body is the
  same node (no choice point exists inside it).
- **The textual definitions stay as the SELF-ORACLE.** D85's table already
  records `\b ≡ (?<=\w)(?!\w)|(?<!\w)(?=\w)`; the lookaround module's
  assertion-expansion corpus (lookaround_design.md §6, 8,495 cells) already
  runs `A == B == C`. With `A_CTX`, B becomes a DFA artifact instead of a VM
  one — the two-comparison oracle survives and gets stronger (it now compares
  two engines).
- **What stays a lookaround**: shapes (b)-(e) of the census (width ≥ 2,
  variable, unbounded, capture-bearing) keep today's VM lowering. Widening to
  (b, k ≤ 2) would need a TWO-character context, which a class view cannot
  express (it sees one byte/character); that is a predicate view of the
  [S] §D.2 kind, and D77 says wait for a measured customer (the census puts
  (b, k≤2) at a further 108 patterns — named, not designed).
- **(?m)^/$ and `\A \z \G`** are untouched (they are already views; folding
  `N_BOT_M`/`N_EOL_M` into `A_CTX(NL, …)` is possible later and not needed).

### 2.3 Where an `A_CTX` can be implemented, and the one hazard

**The all-byte DFA implements `A_CTX(C, ·)` exactly iff every character of `C`
is a single byte of the encoding** — any set under `-e byte`, an ASCII-only set
under `-e utf8`. That is the precondition `upc_of_class`'s representative-byte
test silently relies on today (utf8_design.md §5.4.1 LEG 2: the alphabet is
refined by the set, so a class is homogeneous). U2 turns the silent reliance
into a **checked precondition**: a machine whose context set fails it is not
built all-byte — it takes the island (U3) or the VM, never a sampled answer.

**The hazard it prevents is concrete** ([M] `illformed_ctx_cells.txt`):
`(?<=[^a])a` on `80 61` is **nomatch** on 10.46 (UTF|MIU) and on pcrec today
(VM lookbehind, `back_step` refuses the stray continuation byte); an all-byte
context would read the byte 0x80 as "in `[^a]`" and answer **(1,2)**.
`(?![^a])` on `E6 97 61` is the lookahead twin. A set with non-ASCII members
under UTF-8 is not homogeneous over bytes in EITHER direction, because the same
byte begins or ends both a valid character and an ill-formed run.

---

## 3. The island (UD-3)

### 3.1 What it is, in one paragraph

A DFA machine built in **character-stepped mode** has the same byte-class
columns for ASCII as today, and three columns for non-ASCII bytes (lead bytes,
continuation bytes, never-valid bytes — the partition `UPC_NOSTART` already
draws, internal.h:1697). A non-ASCII cell of state `q` is either an **ordinary
cell** (§3.3's fold) or an **island entry** for `q`. The walk takes the island
entry through [OPT-EDGE]'s existing stop test — island tokens live in the
reserved top range with the scan-edge heads and the dead sentinel, so
`(unsigned)s >= FLOOR` catches them with **no added compare on the ASCII path**
(`token_stop`, emit_dfa.c:4651; the layout is checked, emit_dfa.c:7016-7040).
The island then, for the character at the lead byte:

```c
/* shape, not final text: island entry for state Q, lead byte at p */
len = $_decode(s, n, p, &cp);           /* PCREC_ENCE_DECODE (CT-5); 0 = ill-formed */
if (len == 0) { v = V_BOTTOM; len = 1; } /* ⊥: one byte, in no set, not a word char */
else          v = $_vecQ(cp);           /* membership vector over Q's sets, §4 */
if (acc_Q[v]) last_accept = p;          /* the accept that depends on the NEXT char */
state = tgt_Q[v]; pos = p + len;        /* resume, or dead */
```

`tgt_Q[v]` is `δ*(Q, bytes(c))` for any character `c` with vector `v` — well
defined because the NFA's non-ASCII transitions are labelled by code-point
SETS (`A_WCLASS`, CT-4) and so δ* over a whole character depends only on which
sets it is in. Subset construction computes `tgt_Q` over the machine's **atoms**
(the realizable vectors, a cpset computation at compile time) instead of over
bytes: `\p{L}` is ONE column pair (in/out) instead of the ~100 byte classes and
299 forward / 453 reverse states of its byte automaton ([C] §3.1).

### 3.2 Why this and not the predicate view

The study sketched UCP `\b` as a **predicate view** ([S] §D.2: a `bvar` variant
state, the predicate decoding the character before AND the character after, per
position). The class-axis form above is chosen instead:

- **Each character is decoded ONCE.** The decode that steps the machine also
  answers the next-side context (the vector), and the consumed side is carried
  in state identity exactly as ASCII `\b` does today (internal.h:1713-1722) —
  the target of a word character and a non-word character intern apart
  wherever it matters. The predicate view decodes twice per position,
  including a `back_step` on the hot path ([S] H5).
- **No new view kind, no new minimization symbol.** `bvar` would be a third
  position-view kind beside `eolvar`/`endvar`, and scan edges refuse view
  states ([S] H2). The class axis is already folded into the transition row
  and the class-indexed accept table.
- **It is the same mechanism for classes and assertions.** A wide class and a
  UCP `\b` both need "which sets is this character in"; one island answers
  both. That is D129's "one mechanism" requirement, met by construction rather
  than by sharing a splice.

`back_step` is still needed, at three once-per-call places: the forward
machine's **seed** at `startpos > 0` (`Dfa.s1u[]` generalizes to one seed per
atom of the consumed side: the character ENDING at `startpos` is found by
`back_step` + decode + vector), the reverse machine's **termination boundary**
(assertions_design.md §3.8.3.1's N1 site, the character before `startpos`), and
`ENG_ATTEMPT`'s per-start seed (per start, not per byte — §3.7 H6).

### 3.3 The self-loop fold: most non-ASCII bytes never leave the table

A state `q` whose island would map EVERY non-ASCII character and ⊥ back to `q`
itself, with the same context, needs no island: its non-ASCII cells are
ordinary self-loop cells, and stepping the character's bytes one at a time
through `q` is exact (every intermediate position is `q`, and the
continuation-byte column keeps `UPC_NOSTART`'s no-new-thread view, so no
thread starts mid-character — [P]: `\B` on `a é` answers (3,3) today, threads
start only at character boundaries). This is the unanchored search's start state
for any pattern whose first atom rejects non-ASCII and reads no non-ASCII
context — i.e. the state the walk spends most of a non-ASCII subject in. **The
fold does not apply under UCP `\b`-at-start**: the consumed character's
word-ness must be known at the next position, so every non-ASCII character is
classified. That cost is intrinsic (any engine must classify the character
before a candidate) and is where a prefilter matters (§3.6).

### 3.4 Context under the island

For an `A_CTX(C, ·)` with non-ASCII members (UCP `\b`, `(?<=\p{Lu})`, a
`[^…]` context under utf8), `C` joins the machine's set list, so every vector
records `c ∈ C`. The next-side view for a non-ASCII next character is the
vector's `C` bit (for ASCII, the refined byte class as today); the consumed side
is identity. **The reverse machine is the same with the sides swapped** and its
island decoding BACKWARD: `back_step` to the lead byte, decode, vector, target;
⊥ consumes one byte backward.

### 3.5 Ill-formed input: the ⊥ rule, and the two measurements behind it

pcrec's ruled semantics under `-e utf8` is the automaton's: an ill-formed
sequence matches nothing (utf8_design.md §2.6), `PCRE2_MATCH_INVALID_UTF`'s
answer. The island's version of that rule is **⊥: one byte, in no set, not a
word character, and not a character start if it is a continuation byte**. Two
things must hold for it to be the SAME answer the automaton gives; both are
measured here with failing-direction controls:

1. **Context agrees with 10.46.** [M] `bottom_model_10.46.txt`: a model that
   finds the character ending at a position with pcrec's repaired `back_step`
   and the one starting there with the stage-4 decoder, reading ⊥/absent as
   non-word, is scored against 10.46's UCP|MIU answers for `\b`, `\B`,
   `(?<=\w)`, `(?!\w)` at every position a pcrec thread can occupy, over 14
   subjects built from ill-formed shapes (stray continuation, 0xFF, truncated
   2/3-byte, surrogate, overlong, combining marks and Pc next to ⊥): **209
   agree, 0 disagree** (83 not asked: continuation-byte positions and libpcre2's
   MIU re-positionings). Controls: ⊥-as-word **131 disagree**; the unrepaired
   `back_step` (utf8_design.md §5.2's first body) **6 disagree**.
2. **Forward and backward segment the subject identically**, so the forward and
   reverse islands see the same characters and the same ⊥ bytes. [M]
   `segment_sym.txt`: every string of length 0-5 over a 20-byte boundary
   alphabet, **3,368,421 strings, 0 disagreements**. Controls: the unrepaired
   `back_step` disagrees on 267,786; a forward decoder that skips a whole
   truncated run instead of one byte disagrees on 1,895,172.

The decoder is the stage-4 `$_span_ci_decode` body CT-5 adopts, whose
ill-formed set is "exactly the automaton's" (enc_utf8.c:187-214's own comment).
So the island adds no new ill-formed rule — it adds a place the existing one
must be applied, and U3's ill-formed matrix (§6) is that application's check.

### 3.6 The hybrid, the prefilter, and the VM

The VM hybrid's DFA prefilter is built by the same builder and so takes the same
mode. Candidate-start prefilters (memchr on a necessary byte, offset-k) run
BEFORE the DFA and are unchanged; the DFA then runs from the candidate with its
seed computed once (§3.2). The VM never uses the island: it decodes natively
(S4's `$_decode` + kit, CT-5), and a VM `A_CTX` is a direct test per side
(§6 U4).

### 3.7 The cost model, and when the dial chooses which

Per character, for a machine where the character's next state depends on a
non-ASCII set:

```
all-byte:  T_B = len · t_step                     (+ cache misses on large tables)
island:    T_I = t_stop + t_decode(len) + t_vec + t_row
```

What is known ([C], ubuntubudu): `t_step` ≈ 1.8 ns/byte with the
pre-multiplied table resident (opt3_dfa_scan_measurement.md: 3.27 → 1.80 ns),
so a 2-3-byte character costs **~3.6-5.4 ns all-byte**, while `\p{Xwd}`'s byte
tables are 197,685 B ([S] §E) — above a 32 KB L1D, so that figure is a floor,
not an expectation. `t_vec` for one set, as a membership loop behind an indirect
call ([T] medians, member subjects): **`bitmap1` 1.59 ns, kit λ0 10.2, λ16
11.7** on `\p{Xwd}`; `\p{L}` 1.61 / 10.2 / 11.4. **`t_decode` and `t_stop`
(the branch into the island, mispredicted on mixed text) are unmeasured**, and
[T]'s loop overhead (~5 ns on ASCII subjects for every arm) is not in-engine
cost. **So the honest reading is that the island is a SIZE and COMPILE-TIME
win (hundreds of KB → ~5 KB; K67's class share gone — no byte fan-out exists)
whose SPEED against a cache-resident all-byte machine is unknown, and at the
kit's middle policy on dense non-ASCII text plausibly a loss.** That is Frank's
D129 residual question, and it is why the choice is a dial — expressed as §0.1's table **T4**, whose rows are, in prose:

- **Forced island**: a machine with a context set that is not byte-expressible
  (§2.3) — UCP `\b`/`\B`, a non-ASCII lookaround context. No all-byte form
  exists in pcrec (the exact byte product of [S] §D.2 is not built and not
  proposed).
- **Forced all-byte**: every set byte-expressible (the byte tier, ASCII sets) —
  there is no island to take.
- **Dial choice**: wide consuming classes under utf8 (`\p{L}`, UCP `\w` as a
  consuming class, `[\x{100}-\x{2000}]`). The rule is per MACHINE: island
  when the byte lowering of the machine's non-ASCII sets exceeds a threshold
  θ (the sum of their byte-automaton states, which the cpset lowering knows
  before subset construction), all-byte below it. θ is a `--tune` cell,
  PROPOSED only after §7's b-island measurement, as a ruled diff (D103). A
  per-machine rule, not per class, because a state that mixes byte-stepped and
  character-stepped non-ASCII threads would need both an island and mid-character
  states at once.

### 3.8 Hazards

- **H1 — the stop branch.** On text alternating ASCII and non-ASCII, the island
  branch mispredicts. The ASCII path is untouched; the mixed-text cost is b1's
  `mixed`/`runs` regimes (§7).
- **H2 — skip loops.** Scan edges, stay skips and the offset-k skip assume a
  state's behaviour at a byte is a function of the byte's class. An island
  state violates that for non-ASCII bytes; like a view state today
  (scanedge.c precondition (3)), it is excluded. The self-loop fold (§3.3) is
  what keeps the common start state eligible.
- **H3 — ill-formed agreement.** §3.5; the check is U3's matrix.
- **H4 — vector width.** A state reading `k` non-ASCII sets has up to `2^k`
  vectors; only realizable atoms get columns. [M]: 171/172 of the one-character
  lookaround population read one set; the per-STATE width over wide-class
  patterns is not censused (§7 a2). A `limits.def` row bounds `k`; above it the
  machine takes the VM (a route, not a refusal).
- **H5 — premultiplied capacity.** Island tokens share the reserved top range
  with scan-edge heads; `PREMUL_MAX_ENTRIES` counts them.
- **H6 — `ENG_ATTEMPT`.** Its per-start seed needs the consumed character's
  vector: one `back_step` + decode per START position, not per byte. Carrying
  the previous character's vector forward across `next_pos` avoids it and is
  the implementer's call.
- **H7 — the accept column.** A state whose accept depends on the next
  character's class answers it in the island for non-ASCII next characters
  (`acc_Q[v]` above) and in the class-indexed accept table for ASCII; the
  table's non-ASCII column for such a state must never be read as an answer. A
  structural check pins it (§6 U3).

---

## 4. The predicate's forms (UD-4)

The island's test is **"the membership vector of one decoded character over the
machine's non-ASCII sets"**. [CLS-TREE]'s interface (cls_tree_design.md §3.4)
fixed the one-set case: `$_decode` + `$_clsN(cp)`. For a vector there are three
producers, and they are dial choices, not three mechanisms:

| form | what it is | cost shape | status |
|---|---|---|---|
| **(i) one kit predicate per set** | `v = cls1(cp) | cls2(cp)<<1 | …`, short-circuited per state | `k` kit probes; each set's form is the DP's pick (bitmap1 / page3w / kit sections / BSEARCH) | **built first** — it needs nothing but S1 |
| **(ii) an atom map** | ONE multi-valued lookup `cp → atom id` for all of a machine's sets — the kit's whole-set page table with atom-id leaves instead of bit leaves | one probe regardless of `k`; bytes grow with atom count | **proposed kit member**; D77 trigger: a machine with `k ≥ 2` in a real population (§7 a2) |
| **(iii) the shared record** | [UCD-RECORD]: `cp → record{gc, script, case data, bitmap of standard classes}`, PCRE2's `ucd.c` shape; linked ONCE per program via [XART-TABLES] | one two-stage probe answers every STANDARD class at once (`\p{..}`, UCP `\w \d \s`, POSIX); cannot answer an arbitrary class (`[\x{400}-\x{4FF}]`), so it mixes with (i) | **not built**; triggers below |

**On Frank's "why use a DFA to do a lookup? what about binary search?"** —
the island IS that answer for the DFA route, and binary search is in the kit
(`BSEARCH`, [CLS-TREE]'s seed). The measurement says it is the slowest member:
the flat binary search (`refbs`) is **21.2 ns** on `\p{Xwd}` member subjects
against **10.2** for the kit's λ0 sectioning and **1.59** for one whole-set
bitmap ([T] medians). So the DP will rarely pick it; it earns its place where
a set is small and sparse.

**The shared record (iii), evaluated as asked:** it is the right form when ONE
island or ONE program needs many standard classes — the probe cost is paid once
and each extra class is a bit test, and a program linking many artifacts pays
its bytes once. It is the wrong form for one class (a record table's size for Unicode 16 is
**not measured here** — PCRE2's own `ucd.c` suggests tens of KB, and
[UCD-RECORD] owes the number from `third_party/ucd-16.0.0`) against a ~5 KB kit matcher. Its
triggers (D77): (a) a real pattern population where an island reads ≥ 3
standard classes, or (b) a program-level size measurement showing duplicated
per-artifact class tables ([XART-TABLES]'s own trigger, "the first LARGE
GENERAL table ships in emitted artifacts" — which U3 and S4 cause). Neither is
met today; both are named so the record lands as a kit/predicate FORM when one
is, with no change to the island's interface.

---

## 5. Interaction with [CLS-TREE] (UD-5)

D129 ruled [CLS-TREE]'s order S0 → S1 → S3 → S4 → S2 and dropped S5 for the
island. UCP's stages (§6) against it:

| UCP stage | needs from [CLS-TREE] | why |
|---|---|---|
| U0 registry/O-71 | nothing | text rows |
| U1 surface | nothing for the small tier and the byte tier ([C] §9: 3-19 KB DFA per use today); **wide sets wait** (Q3) | `\p{Xwd}` is REFUSED on the VM today and 197 KB / 66 s compile on the DFA ([S] §E) |
| U2 `A_CTX` | nothing | byte-expressible sets only; the existing class-axis machinery |
| U3 island | **S1** (the kit in `src/`) and **S3** (`A_WCLASS`: the island builder's input is a set, not a byte chain); introduces `PCREC_ENCE_DECODE` if before S4 | the vector producer is the kit; the NFA must carry sets |
| U4 VM UCP `\b` | **S4** (VM decode + kit) | the VM test per side |

**So UCP starts now** (U0-U2) without waiting for any [CLS-TREE] stage, and the
island follows S3 — it does not wait for S4. Captured UCP `\w` (`(\w+)` under
UCP) becomes buildable at **S4** on the VM with no UCP-side work (U1's
definitions produce `A_WCLASS`, S4 compiles it), and on the DFA route at U3.

---

## 6. Staging, with per-stage checks (UD-6)

Each stage is one lane and merges alone. "Identity" means the house gates (the
four `.c` byte-identity gates, the recursion gate's pins, the `irsb` arm —
coding_guide.md §3), **abi readers found by grep at the time** (D94), never
from this list. Sabotage rows are numbered from main's highest S-id at the time.

| stage | what | answer checks | identity / abi | sabotage shapes |
|---|---|---|---|---|
| **U0** | registry: `(*UCP)` → module `ucp` (unbuilt: "requires module 'ucp'"); `(*UTF)` accepted under utf8, refused by name under byte; `-e utf8` enables `unicode-props`+`ucp`; `parse.c:652` comment corrected | PC-3 against 10.46 (compile-accept); reject-table rows for both verbs × both encodings | no artifact moves; no abi; D80 spec hunk (the verbs' tier in the compliance/limits spec, `-e utf8`'s implied modules) | `(*UCP)` answering module `verbs` again |
| **U1** | the surface: `ucp` built; `--ucp` + `(*UCP)` + `.rxt` letter; `DEF_UCP_{D,S,W,P,T}` producers for the class escapes and POSIX classes; fold-inert rule; the (encoding, UCP) fold; `(?a…)` real; the byte tier. **Wide sets under UCP -e utf8 (`\w`, `\W`, alpha/alnum/word/lower/upper/graph/print/punct) and `\b`/`\B` under UCP -e utf8 refused by name** until a kit-sized route exists (Q3) | `oracle_store` membership arm gains UCP config (§1.6): every UCP set × {byte, utf8} vs 10.46; §1.3's caseless cells and §1.4's knob cells as `.rxt` corpora oracle-verified against 10.46; the [S] §B.3 Latin-1 cells | UCP-free artifacts **byte-identical** (UCP is an axis; nothing moves without it); UCP artifacts are new, no abi; D80: `tuning.md` axis row, `match_api.md` if `rx_info.flags` gains a UCP bit (then an abi event, readers by grep) | a `DEF_UCP` tag answering true without UCP (every `\d` moves — the identity gate must catch it); `[:lower:]` folding under `(?i)` UCP; `(?aW)` not reaching `\b` |
| **U2** | `A_CTX`: `\b`/`\B` producers build it; the recognition pass for one-character lookarounds; the DFA class axis generalized from the fixed word/newline sets to the machine's context sets; the byte-expressibility precondition checked (§2.3); UCP `\b` under **`-e byte`** lands here | **identity over every `\b`/`\B` pattern** (corpus + bench, all encodings × features — the plan row's named control); the moved lookaround patterns: default vs `--engine=vm` answer identity over the whole corpus; 10.46 differential on the assertion-expansion corpus; the §2.3 hazard cells (`(?<=[^a])a` on `80 61` nomatch) | **abi bump** (the moved patterns' artifacts change VM → DFA; the refusal set does not move); the census of movers pinned by NAMED manifest, not count (r49's rule) | the recognizer accepting a two-character body (`(?<=ab)`); accepting a capture-bearing body; the precondition skipped for a non-ASCII set under utf8 (must be detected by the §2.3 cells, not by answers on ASCII subjects); an `A_CTX` whose "absent" side reads as in-set |
| **U3** | the island: character-stepped mode; the atom/vector builder over `A_WCLASS` + non-ASCII context sets; island tokens in the top range; the self-loop fold; seeds and reverse boundary via `back_step`; the dial's θ; UCP `\w`/`\b` and wide classes on the DFA route under utf8; U1's wide-set refusals lifted for the DFA route | whole-corpus answer identity island vs all-byte where both exist (a deny axis, `-fno-cls-island` or the kit deny Q2 of D129 extended — the implementer's spelling); 10.46 UCP differential (the [S] §C 579,195-subject `\b` stream, UCP mode, both engines); the **ill-formed matrix**: every set kind × {truncated, overlong, surrogate, >U+10FFFF, stray continuation, 0xFF} × {forward, reverse, seed, `ENG_ATTEMPT`} — [M]'s model is the expectation generator and 10.46 UCP|MIU its oracle | **abi bump** (utf8 artifacts with wide classes move; K53's ladder stops firing for them — a refusal/selection-set move recorded as the identity break it is); `PREMUL_MAX_ENTRIES` accounting | the decoder accepting `C0 80`; ⊥ read as a word character; the reverse island skipping a whole truncated run (the [M] control's shape); an island state not excluded from a scan edge (H2); the H7 accept column read on a non-ASCII byte — a STRUCTURAL check, since answers on well-formed ASCII subjects cannot see it |
| **U4** | the VM `A_CTX` with non-ASCII sets: `back_step` + decode + kit per side; UCP `\b` on the VM; U1's remaining VM refusals lifted | 10.46 UCP differential, `--engine=vm` and default; the mid-character `startpos` cells under `-fno-startpos-guard` (utf8_design.md §2.6.1's inversion) for a leading `\B` | **abi bump** (VM artifacts with UCP `\b`) | `back_step` returning the lead of a malformed run (the E4 shape); the test reading one byte instead of decoding |

**Before U3 is chartered** (D77): §7's b-island measurement, a hand-twin study
(the [FORM-CHAR]/[CC-DIFF] precedent: edit an emitted DFA artifact to add the
island, answer-check it against the original, time both on ubuntubudu). It
decides whether θ has a speed-leaning setting at all, and it can run before S1
lands because a twin needs no `src/` kit.

---

## 7. Measurements owed (UD-7)

### (a) The Mac can do these (counts, bytes, answers — box-independent)

- **a1. U2's mover census**: every corpus + bench pattern compiled before and
  after the recognizer in a scratch build; the named manifest of VM → DFA
  movers and the byte-identity list for every `\b`/`\B` pattern. (Sizes the
  abi event; the identity half IS the plan row's control.)
- **a2. The per-state vector-width census**: build the atom lists for every
  utf8 corpus/bench pattern with a non-ASCII set (a cpset-only computation, no
  DFA) and report the maximum realizable atoms per machine. Decides H4's
  `limits.def` value and form (ii)'s trigger.
- **a3. The island twin's correctness half**: the hand-twin artifacts of b-island
  answer-checked against their all-byte originals on the ill-formed matrix and
  on [S]'s 14-character `\b` alphabet (answers only; Mac-legal).
- **a4. The byte-tier Latin-1 fold**: the 30 pairs derived from
  `third_party/ucd-16.0.0` against 10.46's `UCP|CASELESS` over all 256×256
  byte pairs (an exhaustive relation sweep, stage 4's method).

### (b) ubuntubudu only — relayed to the pcrecdev2 executor

- **b-island — the D77 trigger for U3.** Hand-twin artifacts for `\p{L}+`,
  `\p{Xwd}+`, `\p{Nd}+`, and a UCP-`\b` pattern (`\b\p{Xwd}+\b` spelled so the
  all-byte original exists only for the classes), each in three arms —
  all-byte (today's artifact), island + kit λ-mid, island + `bitmap1`/`page3w`
  — over four subject regimes: ASCII prose, Latin-1-heavy prose, CJK, and
  mixed. ns/char, the bench harness's load gate. It answers: is `T_I` ≤ `T_B`
  anywhere, and how much `t_decode`/`t_stop` cost in-engine (what [T] could not
  see). Rides behind [B115] and [CLS-TREE] b1 in the queue (D129 point 1).
- **b-ctx — U2's customers.** The moved lookaround patterns (bench's 8 of 18
  all-(a) patterns in particular) DFA vs VM, search and find-all regimes, at
  U2's pin vs its parent — the bench's own AFTER run (memory
  `pcrec-bench-status`), relayed as an inbox item when U2 merges.

---

## 8. Questions for Frank, each with a recommendation

**Q1. UCP is an opt-in axis (`--ucp`, `(*UCP)`), not on by default under
`-e utf8`?** *Recommend YES (opt-in).* PCRE2's UTF default reads `\w`/`\b` as
ASCII and D26 makes the answer the exact tier; a default flip changes every
shipped utf8 `\w`/`\b` artifact's answers against the source of truth. The
imported-pattern drift ([S] §A.3) is better served by a diagnostic (a note when
a utf8 pattern uses `\w`/`\b`/`\d` with no UCP decision) — filed, not designed
here.

**Q2. O-71: `-e utf8` ENABLES `unicode-props` and `ucp`; `(*UTF)` accepted under
utf8 and refused by name under byte (not an in-pattern encoding switch)?**
*Recommend YES to all three.* Enabling is Frank's own suggestion; refusing the
switch keeps `-e` a declaration of the artifact's entry-point contract.

**Q3. At U1, refuse the WIDE UCP sets and UCP `\b` under `-e utf8` by name
until a kit-sized route exists (S4 for the VM, U3 for the DFA) — rather than
accept them at today's cost?** *Recommend REFUSE.* Accepting is correct but
`\w+` under UCP compiles to 330 KB in **66 s** and every captured form is
refused by size anyway ([S] §E) — a user would meet a minute-long compile for
the most common UCP pattern. The small tier (`\d`, `\s`, small POSIX) and the
whole byte tier ship at U1, which covers **46 of the bench's 91** UCP-sensitive
patterns ([S] §A.2).

**Q4. The byte tier (UCP without UTF, Latin-1) ships in U1?** *Recommend YES.*
It is §1.4's definitions under the byte universe plus a Latin-1 fold — no new
table, no island, no kit — and a `(*UCP)` under `-e byte` cannot be accepted
and ignored ([S] §B.3).

**Q5. The `(?aD)/(?aS)/(?aW)/(?aP)/(?aT)/(?a)` knobs become real in U1, as one
`DEF_UCP` tag per family?** *Recommend YES.* They are PCRE2's own partial-UCP
spelling; accepting them as no-ops under UCP would be a miscompile (study Q4),
and the five families are measured disjoint in what they touch (§1.4).

**Q6. U2 — the `A_CTX` node and the one-character-lookaround recognizer — ships
under the [UCP] row, before the island?** *Recommend YES.* It is Frank's Q2/Q3
answered, it moves up to 158 VM-only patterns to the DFA with no island and no
[CLS-TREE] dependency, and it builds the node U3 extends. The plan row's
identity control is its gate.

**Q7. U3's trigger is the b-island hand-twin measurement on ubuntubudu, and θ
(the per-machine island threshold) is proposed only after it, as a ruled diff?**
*Recommend YES.* The island's SIZE and COMPILE-TIME wins are certain (§3.7);
its speed against a cache-resident all-byte machine is not, and D129's own
residual question asks for exactly this measurement.

**Q8. [UCD-RECORD] and [XART-TABLES] stay unscheduled, with the island's
predicate interface admitting the record as a producer and the two triggers of
§4 named?** *Recommend YES.* Nothing measured needs the record yet; the
interface costs nothing to keep open, and U3/S4 are what will first ship large
general tables — [XART-TABLES]'s own trigger.

**Q9. The oracle store's `OracleId.config` gains `UCP` at U1 (a store-format
event under `oracle_interface.md`'s fourth staleness claim)?** *Recommend YES* —
the design excluded it only because it had no producer.

---

## 9. What this note leaves open, stated

- **The island's speed** — §7 b-island. Nothing here licenses a throughput
  claim for any island form.
- **(b, k ≤ 2) lookarounds** (a further 108 of the 493) need a two-character
  context; out of U2, D77.
- **The exact all-byte UCP `\b`** (the product with the `\p{Xwd}` byte
  automaton, [S] §D.2) is not proposed: it multiplies every `\b`-crossing
  state by the 197 KB automaton, and the island supersedes it.
- **`(?m)^/$`'s fold into `A_CTX(NL, …)`** — possible, not needed, not proposed.
- **The `-e utf8` UCP-drift diagnostic** (Q1) — filed, not designed.

---

## Appendix A. Reproduction

All in `docs/design/ucp_measurements/` (its `CLAUDE.md`):

| number | command | output |
|---|---|---|
| §1.1-§1.4 set relations (57 rows) | `ssh duxevents@100.69.121.107 python3 - /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 < probes/ucp_sets.py` | `out/ucp_sets_10.46.txt` (+ `_10.48` locally) |
| §1.3-§1.5 point cells, §3.5 streams | same, `probes/ucp_points.py` | `out/ucp_points_10.46.txt` (+ `_10.48`) |
| §3.5 (1) the ⊥ context model | `python3 probes/bottom_model.py out/ucp_points_10.46.txt [bottom-is-word\|unrepaired-back-step]` | `out/bottom_model_10.46.txt` |
| §3.5 (2) segmentation symmetry | `python3 probes/segment_sym.py 5` (~50 s) | `out/segment_sym.txt` |
| §2.1 context-set census | `python3 probes/ctx_sets.py docs/dev/lookaround_census/shapes_9399d927.tsv` | `out/ctx_sets_9399d927.txt` |
| §2.3 hazard cells | pcrec `-e utf8 --features all --emit-main` + a 10.46 UTF\|MIU match | `out/illformed_ctx_cells.txt` |
