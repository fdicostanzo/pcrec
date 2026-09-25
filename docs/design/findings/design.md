# `[FINDINGS]` — design note (step 2 of 3: think → DESIGN → critique)

**Lane `findesign`, opus, 2026-09-25, from main `f94b9dd8`. PROPOSED,
PANELED (r2, three critics) AND REVISED (lane `findrev`, same day, from
main `5a2094e7`).** Design only: nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/` changes in these lanes. §14 lists the spec hunks
the build owes (D80), and §13 orders the build.

> **PANEL OUTCOME (r2, `../../dev/reviews/2026-09-25-r2-findings-design.md`).
> Read §R, the one disposition table, before any other section.** Three
> read-only critics (fcrit-model: data model and surfaces; fcrit-sound:
> answer soundness and checks; fcrit-analyzer: the analyzer and the store
> build). No finding refuted the mechanism — bundles, per-query single-block
> answers, declared applicability, counts-not-ppm, the one accessor, the
> text-embedded store. What moved: **(1)** D123 addendum 8 reversed three
> of this note's choices — `--analysis` is FILL-ONLY (D93 keeps its single
> exception), the first resolution stop is the compiling FILE only, and a
> `-I` file lacking the bundle FALLS THROUGH; **(2)** the answer-identity
> invariant widens to GIVE-UP identity, because the panel found **K65** (the
> necessary-byte pick decides whether a no-DFA-front VM call gives up), and
> B2 now depends on K65's fix; **(3)** a bundle may not carry two blocks
> serving one (query, encoding) pair, and the digest's treatment of
> kind/via is settled; **(4)** the abi number is no longer a literal (main
> is at 33 after K64, and K65's fix takes the next). Every edit below is
> marked `[r2 <id>]` where it lands.

**Binding inputs.** Every one is cited by short name below.

| short name | what |
|---|---|
| **REQ** | `requirements.md` (R1–R41, customers C1–C11), step 1 |
| **D83**, **D83-A1..A4** | the findings-file ruling and its 2026-09-22 addendum |
| **D123**, **D123-1..7** (+**3a**) | Frank's rulings on REQ §3 Q1–Q10 (the body is Q1/Q2, the addenda are numbered as in `decisions.md`) |
| **D123-8** | Frank's rulings on the r2 panel's asks: K65's fix shape, `--analysis` fill-only, first stop = own file, one include, names/`-I` files, this note's §16 |
| **D124** | organize by QUESTION; one table per question, the engine a row predicate and a consumer hat |
| **K65** | `known_issues.md`: the necessary-byte pick decides a no-DFA-front VM give-up |
| **RUNEST** | `docs/dev/findings_measure/estimator_report.md`: the run-level kind is a per-class BIGRAM chain |
| **D122**, **D122-2..3** | one literal-search kit; the accessor is the ONE seam; row predicates read findings only through it; row ORDER is findings-independent |
| **PFI** | `docs/design/patfacts/inventory.md`: the prior's call sites and their gates |
| D76 / D94 | abi + identity-gate pins; the bump ritual |
| D80 | the spec hunk ships in the same change |
| D26 | diagnostic tiers |
| D77 | build only under measurement |

Findings come first (§0). Decisions come with their reasons (§1). Then come
the mechanism (§2–§11), the migration and the build plan (§12–§13), and the
spec hunks, the R-disposition table, the open questions and the not-built
list (§14–§17).

---

## R. Panel r2: the disposition table

One row per finding. Prefix `M` = fcrit-model, `S` = fcrit-sound, `A` =
fcrit-analyzer. Severity: **B** blocking, **S** should-fix, **N** note.
"Ruled" cites D123-8 where Frank ruled the panel's ask. The review record
(`../../dev/reviews/2026-09-25-r2-findings-design.md`) carries the same
rows plus what is still open to Frank.

| id | sev | finding (essentials) | disposition | applied in |
|---|---|---|---|---|
| M-B1 | B | two blocks of one bundle can both serve one (query, enc): which answers was an accident of kind order; the analyzer's own defaults collided (`freq` and `cpfreq` both `when byte,utf8`); §7 said kind/via are in the digest AND that `freq`/`cpfreq` give the same digest | ACCEPT. At most one block per (query, enc) per bundle, a PARSE error otherwise; analyzer defaults made collision-free; digest settled: `byte-rate` digests the derived values only (no kind/via), `run-rarity` digests `via` + rows | §2.4, §3.1, §7, §10.2 |
| M-B2 | B | `--analysis` REPLACING a config's name broke D93 (file wins; `--engine` the single exception) | RULED (D123-8 item 2): FILL-ONLY; an experiment is a config VARIANT in the file; `--analysis` in a config's `pcrec` line is refused | §1 row 11, §5.1, §9, §11.2 F-8, §11.5 #12, §15 R10 |
| M-B3 | B | S1 as the whole include closure is a second resolution walk over files the compile opened for another reason | RULED (D123-8 item 3): S1 = the compiling FILE only; boonies row `[FINDINGS-S1-REVISIT]` | §1 row 8, §4.1, §4.2, §9 |
| M-S4 | S | a `-I` dir serving `lib` may hold `<name>.rxt` that is a library, not a bundle: a hard error there punishes an unrelated file | RULED (D123-8 item 5): FALL THROUGH to the next stop with a note | §4.1, §4.3, §9, §11.5 #7 |
| M-S5 | S | one S2 file carrying several bundles makes "which bundle" depend on file contents, not on the name | RULED (D123-8 item 5): ONE bundle per `-I` file | §4.1, §9 |
| M-S6 | S | name → file on a case-insensitive filesystem opens `Log.rxt` for `log` | RULED (D123-8 item 5): lowercase-only names, matched by EXACT directory-entry name | §3.1, §4.1 |
| M-S7 | S | "a one-line un-refusal" of `-I` understated: the lift touches every query mode, the CLI mode tables and the lib-dirs lifecycle | ACCEPT; enumerated as B2 scope | §0.2, §13 B2 |
| M-S8 | S | `--list-analysis NAME` shows a name's chain, not what each TARGET of a file resolves to | ACCEPT; a per-target resolution view | §5.2 |
| M-S9 | S | one include vs several; selective include's scope | RULED (D123-8 item 4): one `include` now; several only later, with `kinds=` on every line; boonies row `[FINDINGS-SELINC]` | §1 row 2, §3.3 |
| M-S10 | S | the two `--list-*` producers were "table contract at birth" with no enrolment or escaping stated | ACCEPT | §5.2, §14 |
| M-S11 | S | five spec hunks missing from §14: `cli.md` file-wins + `-I` on queries; `match_api.md`'s `REQ_BYTE` prior sentence (~:2755); `rxt_format.md` `--list-source` rows for `analysis`/`include`, the `analysis` line, and the stale `lib` row (:54) | ACCEPT | §14 |
| M-S12 | S | the store and `analysis_source` are BUFFERS; the `.rxt` reader opens files (`include` realpath, `lib` existence) | ACCEPT; a no-filesystem parse mode | §5.3, §8.2, §13 B1 |
| M-N13..19 | N | seven notes | NOTED ONLY. The relayed essentials did not carry their content and this lane cannot reconstruct them from the tree; they are recorded as not dispositioned, never as applied | review record |
| S-F1 | B | **K65**: on no-DFA-front VM routes the necessary-byte PICK decides give-up vs NOMATCH, so every user bundle becomes a give-up switch; "answers identical" as checked counts a one-sided give-up as budget-bound | ACCEPT. The invariant is answers identical AND no give-up TRANSITION, counted as its own population (GIVEUP1); K65's witness is a REACH row; B2 depends on K65's fix (D123-8 item 1) and GIVEUP1 on main | §11 head, §11.1, §11.2 F-12, §13 B2 |
| S-F2 | B | C3 (`req_byte_dominated_by`) lets a rate decide whether a pre-check is emitted; no soundness argument covered it | ACCEPT; the argument written, per reader, plus a sabotage row | §6.2a, §11.2 F-13 |
| S-F3 | S | one `fire-all` bundle cannot show that EACH reader moved | ACCEPT; one adversarial bundle per reader, each REACH-counted | §11.1 |
| S-F5 | S | an exact-rational `L(x)` reference disagrees with the squaring algorithm in the last bit by design; the reference must be the ALGORITHM, re-implemented independently | ACCEPT; `L(x)` is DEFINED by its algorithm | §2.6, §11.4 |
| S-F6 | S | empty sets and ties undefined in `markov1` / `set_mass` | ACCEPT; guards and a tie rule | §2.6, §6.1 |
| S-F8 | S | the `utf8` mover manifest counted per READER; C4's movement changes the scan byte G1 compares, so C3 moves on the same artifacts | ACCEPT; the manifest is per ARTIFACT, with each moved stamp named | §11.3 |
| S-F9 | S | "program region: 0 movers" names no gate | ACCEPT; whole-file diff minus the NAMED lines | §7, §11.3 |
| S-F10 | S | "consumed" = "asked", and whether a reader asks can depend on deny flags and reader order, so the stamp would differ across axis builds | ACCEPT; readers ask deny-independently; the stamp is written after the last reader; the named-lines exemption is the fallback | §6.4, §7 |
| S-F11 | S | "abi 32 → 33" is stale (main is 33 after K64; K65's fix takes the next) | ACCEPT; "the next abi number at landing" everywhere, both CLAUDE.md files included | §1 row 14, §7, §13 B1, §14, §15 R21; `CLAUDE.md` ×2 |
| S-F13 | S | gates | APPLIED AS: every B-step's acceptance names the suite whose `*** [test-X] Error` line is its verdict. The relayed text was one word; if the critic meant more, it is open | §13 |
| S-F4, F7, F12 | — | not in the relayed essentials | NOT DISPOSITIONED (unknown content) | review record |
| A-1 | S | shard 1 has no preceding byte: a uniform "first read byte is the overlap" undercounts `freq` by one | ACCEPT; the k = 1 exception + fixture | §10.4, §11.8 |
| A-2 | S | the `cpfreq` seam rule "move forward to the next lead byte" needs an exact formula both neighbours compute alone | ACCEPT; ownership by LEAD byte, ≤ 3-byte reach + fixture | §10.4, §11.8 |
| A-3 | S | nothing checks the embedded text equals its committed source | ACCEPT; a digest check per embedded bundle | §8.1, §11.5 #19 |
| A-4 | S | `log`'s source | RULED (D123-8 item 6): one sourcing-lane attempt, then a labelled synthesized corpus | §0.9, §13 B5, §16 |
| A-5 | S | `generate.py --check` on a manifest-only source (no sample in tree) cannot recount; it must not skip silently | ACCEPT; a loud, counted skip in `make test`, and a fetch-and-check target that fails closed | §8.1, §11.8 |
| A-6 | S | B5 never wires the new generator into `GEN_TABLES` | ACCEPT | §13 B5 |
| A-7 | S | the bundle NAME in every stamp is a privacy surface | ACCEPT; documented. Whether to offer a redaction is OPEN to Frank (it touches D123-2's "stamp the source name") | §7, §10.5 |
| A-8 | N | `od`'s output differs between BSD and GNU unless the invocation is pinned | ACCEPT; the invocation pinned | §8.1 |

---

## 0. Findings first

Found while designing. Each one either changed the design or stops a later
lane from assuming the wrong thing.

1. **RUNEST's "fixed 128 KB, 2-byte ppm entries" cannot hold conditional
   ppm.** A conditional rate `P(b|a)` often exceeds 65,535 ppm, because a
   byte can have a dominant successor.
   - MEASURED from RUNEST's own `data/tables/*.json`: **226–317 cells per
     class exceed 65,535 ppm** (json 312, log 226, prose 317, web 296), and
     the maximum is 1,000,000 in every class.
   - A dense 2-byte ppm table would therefore saturate on hundreds of
     cells.
   - The same measurement shows the table is **SPARSE**: 471–3,288 nonzero
     pairs per class (of 65,536). As text rows (`row a b count`) that is
     6.5–42 KB.
   - **Consequence (§2.3, §2.6):** a block stores **COUNTS**, sparse and
     keyed. It never stores ppm or rarity. The compiler derives those with
     ONE integer function. Counts are also the only form that merges
     losslessly (finding 5).
2. **`-I` is refused without a file operand today.** `cli/main.c:1600`
   says "`--lib-path` applies to a file operand only".
   - Resolving through `-I` (Route I, §4.2) therefore changes a CLI
     surface: `-I` becomes legal beside `--pattern`, as the analysis
     search path.
   - `-I` is already repeatable and ordered, and it is already the `.rxt`
     library search path.
   - **[r2 M-S7] The lift is NOT one line.** It touches every query mode
     that can resolve a bundle (`--list-analysis`, a `--pattern` compile,
     the per-target view of §5.2), the CLI's per-mode accepted-flag tables,
     and the lifecycle of the lib-dirs list, which today exists only for a
     file operand and must now exist, be validated and be freed for a
     `--pattern` compile and for a library call (`analysis_dirs`). §13 B2
     carries it as scope.
3. **Per-kind fall-through lets a query's inputs come from two
   sources.** D123's chain resolves each KIND independently.
   - Suppose a run estimate read `P(first byte)` from the chain's `freq`
     and `P(b|a)` from the chain's `bigram`. A user bundle carrying only
     `freq` would then silently pair its unigram with a shipped bundle's
     bigram.
   - **Rule (§2.1): every query is answered from EXACTLY ONE block, and a
     block is self-contained for every query it serves.** The `bigram`
     block reads its first-byte marginals from its own row totals.
   - This strengthens R9 from "per value" to "per query".
4. **The most common customization is a self-reference, and naive name
   resolution loops on it.** The copy-edit-shadow case (D123-1/2) is: "my
   `log` is the shipped `log` plus my own run table".
   - The user writes `analysis log` with `include <log>` inside.
   - Resolved by name from the top, that include finds ITSELF.
   - gcc's answer is `#include_next`, and it is adopted here (§4.3): **a
     bundle's `include <N>`, where N is its own name, resolves starting at
     the stop AFTER the one where the including bundle was found.** Any
     other cycle is a hard error.
5. **A process-parallel bigram merge is order-DEPENDENT at shard seams
   unless shards overlap.**
   - A bigram spanning two shards belongs to neither shard's count.
   - Adding the seam pairs back needs shard ORDER, and D123-3a demands an
     order-independent merge.
   - **Fix (§10.4):** shard *k* also reads the single byte before its
     start. It counts that byte into the pair it opens but not into the
     unigram. The merge is then plain addition: commutative, associative
     and deterministic.
6. **The chain's implicit terminal must be the BUILT-IN `default`, not
   the name `default` resolved.**
   - If it were resolved by name, any `-I` directory holding a
     `default.rxt` would silently move every artifact built with that
     `-I`. That includes compiles that name no analysis and passed `-I`
     only for `lib`.
   - So (§4.3) the terminal is the embedded default by identity.
   - A user who wants a different default NAMES their bundle, which is
     the one selection mechanism.
   - An explicit `include <default>` IS name-resolved like any other
     include. That is how a user extends the default.
7. **The default stays byte-identical by construction, not by testing
   alone.**
   - The default's entries are all ≥ 2 and sum to exactly 1,000,000
     (`run_offset_skip.sh` §1).
   - Read as COUNTS through §2.5's normalization, that gives `N =
     1,000,000`, no zeros, a scale factor of 1 and a residue of 0. So
     `ppm(b) = count(b)` exactly.
   - D123-5's byte-identity is therefore a property of the arithmetic. The
     census (§12) confirms it and does not establish it.
8. **`prefix_k.c`'s reader has no "none" fallback today, and the gate
   move forces one.**
   - The reader is currently UNGATED (PFI R9).
   - Once the gate lives in the accessor (D122-2(3)), a `-e utf8` compile
     under the default gets NONE. Offset-k selection needs *some* per-byte
     cost.
   - **Decided (§6.3): set CARDINALITY (a uniform rate) is this reader's
     NONE fallback.** It is the no-information prior for choosing among
     SETS.
   - This is what "offset-k selections move under utf8" (D122-2(3), cost
     accepted) concretely means. R37's zero-movers control becomes "zero
     movers except this named manifest".
9. **The first-shipped `log` class has no licensable source yet.**
   - RUNEST's `log_lines` (loghub HDFS) is manifest-only. Its licence is
     "freely available for research or academic work", which is not
     redistribution (R29, D123-6).
   - `web_request` (elastic/examples, Apache-2.0) is committable but was
     fetched from a `master` URL. D123-6 prefers a pinned commit.
   - MEASURED: the committed 1,000,000-byte `web_request` sample is **pure
     ASCII**. For it, `cpfreq` derives the identical byte view `freq`
     would give (R5's own test holds trivially).
   - **RULED (D123-8 item 6, [r2 A-4]):** one sourcing-lane attempt for a
     licensable, stably retrievable log corpus; failing that, a
     `fidelity synthesized` corpus, labelled as such.
10. **The provenance record's DATA-parent requirements do not fit two
    kinds of shipped data.** The schema (`rxt_schema.def:253-263`, the PROVENANCE rows)
    requires three things of a data block:
    - `bytes` and `sha256` are required-if parent == data;
    - `url` and `ref` are required-if `source != authored`.

    Two cases break this:
    - (a) The authored `default` has no exemplar, so it can supply neither
      `bytes` nor `sha256`.
    - (b) A user's private exemplar has no `url`.

    The constraint language has no conjunction, so `required-if parent ==
    data` and `forbidden-if source == authored` would contradict each
    other. That is a `[DD-13b]` item, scheduled in §13 step B0:
    `bytes`/`sha256` become required-if parent == data **and** source !=
    authored, and `url`/`ref` become optional under a data parent.
11. **The embedded store can be the `.rxt` TEXT itself, parsed by the
    same reader as a user file.** R7 ("four sources, one shape, one reader
    consumes them") is then literally true rather than true by agreement
    check.
    - It needs no second parser (for example python emitting C tables) and
      no second representation that could drift.
    - A library caller without a filesystem still gets every shipped name.
    - The cost is parse time on use: ≈3 KB for the default, ≤≈45 KB for a
      shipped bundle with a bigram. §13 step B1 measures it (D77).

---

## 1. The design in one table

| # | decision | choice | reason (cite) |
|---|---|---|---|
| 1 | unit `analysis <name>` selects | a **BUNDLE**: one textual `analysis <name>` block at file scope, holding at most one data block per KIND | D123-1. One textual unit gives an unambiguous owner for the bundle's `include` and one thing for the details listing to show (§3.1) |
| 2 | composition | `include <other>` INSIDE a bundle, at most one per bundle, making a linear chain. Per-QUERY, first block found along the chain. The built-in `default` is the implicit terminal | D123-2, D123-8 item 4. A single parent keeps the chain a chain, since a list of parents would be a precedence list. Several includes come only later, with `kinds=` on every line (`[FINDINGS-SELINC]`) |
| 3 | selective include | NOT built. The `include` line's value grammar leaves room for `include <n> kinds=a,b` | D123-3, "must not preclude" (§3.3) |
| 4 | kinds | `freq` (byte counts), `cpfreq` (code-point counts), `bigram` (byte-pair counts). Nothing else (§17) | R2, RUNEST, R5 |
| 5 | stored form | **COUNTS**, sparse, one `row <key…> <count>` per nonzero key, ascending, hex keys | §0.1, R3/R4, lossless merge |
| 6 | applicability | declared per block: `serves <query> when <enc,…> via <derivation>`, from CLOSED vocabularies. `encoding <x>` describes the data only. **At most one block per (query, enc) in a bundle** [r2 M-B1] | D123-4: no hidden rules |
| 7 | query ↔ block | each query is answered from EXACTLY ONE block | §0.3 |
| 8 | resolution route | **Route I (hybrid)**: (S1) bundles in the compiling `.rxt` FILE itself, then (S2) `-I DIR/<name>.rxt`, then (S3) the embedded store | D83-A4, D123 addendum, D123-8 item 3, §4.2 |
| 9 | self-include | `#include_next` semantics | §0.4 |
| 10 | embedded store | the shipped bundles' `.rxt` TEXT, generated in-tree, embedded as string literals, parsed by the ONE reader | §0.11, R7, R14 |
| 11 | CLI | `--analysis NAME` (**FILL-ONLY**: applies where a target's config names no analysis, never overrides one), `-I` legal with `--pattern`, `--list-analyses`, `--list-analysis NAME` | D123-8 item 2 (supersedes D123-2's "CLI replaces"); D93 |
| 12 | library | `pcrec_options` gains `analysis`, `analysis_dirs`, `analysis_source` (in-memory `.rxt`, stop S1) | R17 |
| 13 | accessor | `src/core/findings.c`: `pcrec_find_byte_rate`, `pcrec_find_set_mass`, `pcrec_find_run_rarity`. Integer only. Each call is recorded for the stamp | D122 seam, R23, R3 |
| 14 | stamp | `#define <P>_FINDINGS "…"` in every artifact, plus `rx_info.findings`; ONE abi bump (**the next abi number at landing**), shared with the gate move | D123-2, D43, D94 |
| 15 | digest | FNV-1a-64 over what the reader CONSUMED: `byte-rate` = the derived values; `run-rarity` = `via` + the rows [r2 M-B1] | D123-2, R19/R20 |
| 16 | analyzer | `pcrec-analyze`, a separate zero-dependency C binary (end state). Python prototype first. Stdin streaming, `--scan` switches, `--shard k/N` + `--merge` | D123-3/3a, R27a–d |
| 17 | counting vs normalizing | COUNTING lives in the analyzer only (the generators call it). NORMALIZING lives in the compiler only | R27b: one of each, never two |
| 18 | first shipped | `default` (authored, byte-identical); `log` and `weblog` as their censuses earn them | D123-5/7, R31 |

---

## 2. The data model

### 2.1 Terms

| term | meaning |
|---|---|
| **bundle** | the named analysis. One `analysis <name>` block; at most one data block per kind; an optional `include <other>` |
| **block** | one data block inside a bundle, headed by its KIND keyword (`freq` / `cpfreq` / `bigram`), holding counts plus declarations plus provenance |
| **query** | what a compiler READER asks (§2.4). Closed set: `byte-rate`, `run-rarity` |
| **derivation** | the named arithmetic that turns a block's counts into a query's answer (§2.4). Closed set, and each derivation is legal only on its kinds |
| **stop** | a place a bundle name is looked up: S1 the compiling file itself, S2 `-I` directories, S3 the embedded store (§4.1) |
| **chain** | the selected bundle, then its `include`, then that bundle's `include`, …, then the built-in `default` |
| **answer** | for (query, compile encoding): the FIRST block along the chain that has a `serves` line for that query listing that encoding. Otherwise **NONE** |

### 2.2 Kinds

| kind | counts | key | derivations it may declare | one-pass (analyzer) | first reader | admitted at |
|---|---|---|---|---|---|---|
| `freq` | occurrences of each byte | `HH` (byte, hex) | `byte-rate via unigram` | yes, 256 counters | C1–C4 (today's four sites) | B1 (the default) |
| `cpfreq` | occurrences of each code point in DECODED text | `U+HHHH`…`U+HHHHHH` | `byte-rate via encode-utf8` \| `encode-latin1` | yes, UTF-8 decoder (≤3 bytes carry) + sparse map. **Refuses input that does not decode** (R26) | same byte-rate readers, through the derivation | B5, the first shipped bundle (R5) |
| `bigram` | occurrences of each adjacent byte pair `(a,b)` | `HH HH` | `run-rarity via markov1` | yes, 65,536 counters + the previous byte | C6 S4(a) (or whichever of C2-window / C3-widening lands first, §13 B4) | B4, WITH its first reader (R2) |

**Declined as kinds, with triggers (§17):** trigram, top-K token, gap /
burstiness, set-membership run length, line length. `bigram` block
FORMAT would widen to `trigram` as a new kind and a new `markov2`
derivation. It would never be a new mechanism (R1).

### 2.3 Row encoding (R4, decided)

```
row <key>… <count>
```

- **Keys are hex:** `HH` for a byte, `HH HH` for a pair, `U+HHHH` for a
  code point. Hex is unambiguous for every byte, including space, `#` and
  control bytes, which a literal-character key would have to escape. The
  key arity is fixed per kind.
- **Counts are decimal non-negative integers** ≤ `PCREC_MAX_FIND_COUNT`
  (2^40, §9). Zero counts are written by omission, so absent means 0.
- **Rows are strictly ascending by key.** This makes the text canonical
  (the analyzer's output diffs cleanly across re-runs), makes a duplicate
  key a local parse error, and lets the reader validate in one pass.
- This is R4's `byte count` candidate, generalized to every kind. The
  16×16 offset-labelled form is declined because it fits exactly one kind
  and makes zeros explicit.

### 2.4 Declared applicability (D123-4, "no hidden rules")

Two lines per block. Only the second is operative.

| line | shape | cardinality | meaning | read by the compiler? |
|---|---|---|---|---|
| `encoding <e>` | closed: `ascii` \| `utf8` \| `latin1` \| `bytes` (opaque, mixed or invalid) | exactly one, required | what the COUNTED DATA was: a description of the data (D123-4) | validated (closed set) and shown in the details listing. **Never** consulted for selection |
| `serves <query> when <enc>[,<enc>…] via <derivation>` | `query` ∈ {`byte-rate`, `run-rarity`}; `enc` ∈ the compile encodings (`byte`, `utf8`); `derivation` ∈ §2.2's per-kind set | repeatable, at least one; unique per query | "this block answers `query` for a compile with `-e` in this list, computed by `derivation`" | **yes**. This IS the applicability rule. The compiler's only fixed rule is "use what the data declares" |

**The compiler's whole selection rule:** to answer (query Q, compile
encoding E), walk the chain and take the first block with a `serves Q when
…E… via D` line. Compute the answer with D over that block's counts. If no
block qualifies, the answer is NONE. There is no other rule. In
particular, nothing in `src/` tests `-e` next to a findings read (R23).

**[r2 M-B1] One block per (query, encoding) per bundle.** Within ONE
bundle, at most one block may list a given encoding on a `serves` line for
a given query. Two blocks of one bundle both declaring `serves byte-rate
when …utf8…` is a **parse error** naming both lines. Without this rule,
"the first block with a matching line" inside one bundle would be decided
by the order the kinds are written or checked in, which is exactly a hidden
rule (D123-4). With it, a bundle is a total function from (query, encoding)
to at most one of its own blocks, and the chain walk is the only ordering
there is. Across bundles, the chain order decides, as before.

**The closed derivation vocabulary.** Each derivation is compiler code
with a spec-stated definition (§2.5, §2.6). Adding one is a spec change
plus one function (R1):

| derivation | kind | answers | definition |
|---|---|---|---|
| `unigram` | `freq` | `byte-rate` | §2.5 normalization of the 256 counts |
| `encode-utf8` | `cpfreq` | `byte-rate` | `count(b) = Σ_cp count(cp) × occ(b, utf8(cp))`, then §2.5. Reuses the enc seam's UTF-8 encoder (R5) |
| `encode-latin1` | `cpfreq` | `byte-rate` | code points ≤ U+00FF map to their byte. **Larger code points are dropped, and the details listing says how many** |
| `markov1` | `bigram` | `run-rarity` | §2.6 |

Where the declarations come from:

- **The analyzer writes them from what it observed (§10.2).** Pure ASCII
  or valid UTF-8 gets `when byte,utf8`. Invalid UTF-8 gets `when byte`.
  When it writes BOTH `freq` and `cpfreq`, it splits the encodings between
  them so the two can never collide (§10.2's table, [r2 M-B1]). The
  declaration is visible and editable in the output, and an edit that
  creates a collision is refused at parse.
- **The shipped default declares `serves byte-rate when byte via
  unigram`.** This is its byte-only restriction (D123-4/5), written where
  `--list-analysis default` shows it.
- **A user who disagrees overrides it by COPY** (§3.3): a bundle with its
  own `freq` block whose `serves` line lists `utf8`.

### 2.5 Normalization: counts → byte-rate ppm (R3; ONE function, `src/core/findings.c`)

Given 256 counts `c(b)`, with `N = Σ c(b)` and `z` = the number of zero
entries, and `FLOOR` = 2 ppm (today's floor, a named limit):

1. If `N == 0`, this is a hard error (§9). If any `c(b) > PCREC_MAX_FIND_COUNT`,
   also a hard error.
2. Let `M = 1,000,000 − FLOOR·z`.
3. For each `b`:
   - if `c(b) == 0`, then `ppm(b) = FLOOR`;
   - otherwise `ppm(b) = max(FLOOR, ⌊c(b)·M / N⌋)`. The product is
     ≤ 2^60, so `uint64_t` suffices.
4. Let `R = 1,000,000 − Σ ppm(b)`, which may be negative. Add `R` to the
   LARGEST `ppm` entry, with ties going to the lowest byte.
5. Postconditions (asserted): `Σ ppm = 1,000,000` and every
   `ppm(b) ≥ FLOOR`.

- **Default identity (§0.7):** `N = 10^6`, `z = 0`, `M = 10^6`, so
  `ppm(b) = c(b)` and `R = 0`.
- **Test vectors are owed in the spec (§14):** the default, an all-equal
  table, a one-nonzero table, and a table whose floors force a negative
  `R`.

### 2.6 Run rarity: `bigram` + `markov1` (integer only; R3)

**Query:** a sequence of byte SETS `S_0 … S_{L−1}`. An exact run uses
singleton sets. A caseless run uses fold pairs (S4(a)'s `union`). A class
run uses its class. **Answer:** `rarity`, which is `−log2` of the
estimated occurrences per subject position, in Q16 (1/65,536 bit). Larger
means rarer, and comparing two rarities ranks the runs.

From the block's counts `c(a,b)`, define `r(a) = Σ_b c(a,b)` and
`N = Σ_a r(a)`. Smoothing is add-one over the 256 successors, which is
RUNEST's estimator exactly:

```
U(S)      = Σ_{a∈S} (r(a) + 1)                      first-byte mass
D(S)      = Σ_{a∈S} (r(a) + 256)                    pooled transition denominator
T(S, S')  = Σ_{a∈S} Σ_{b∈S'} (c(a,b) + 1)           pooled transition numerator
rarity    = [L(N+256) − L(U(S_0))] + Σ_{i≥1} [L(D(S_{i−1})) − L(T(S_{i−1}, S_i))]
```

- **`L(x)`**, for integer `x ≥ 1`, **is DEFINED BY ITS ALGORITHM**
  [r2 S-F5]: normalize `x` to a 32-bit mantissa, then do 16 rounds of
  "square, shift, take the carry bit". It approximates `⌊log2(x)·2^16⌋`
  and may differ from it in the last Q16 bit, because each round truncates
  its square; that is acceptable, since only COMPARISONS between rarities
  are read, and both sides go through the same function. What is not
  acceptable is two implementations of `L` that disagree, so the spec
  states the algorithm (not the real-valued formula) and a test vector
  table (§14). It is bit-exact on every box and uses no libm. `L(0)` is
  never evaluated (the guards below).
- **Empty sets and ties** [r2 S-F6]:
  - A run query with any EMPTY set `S_i` is a caller error, asserted in
    the accessor. It cannot arise from a necessary run, whose every
    position is non-empty by construction. The guard exists so that the
    add-one smoothing never hides it: `U(∅) = 0` and `L(0)` has no value.
  - With the smoothing, every other term is `≥ 1`: `U(S) ≥ |S|`,
    `T(S, S') ≥ |S|·|S'|`, `D(S) ≥ 256·|S|`, `N + 256 ≥ 256`. So `L` is
    never asked for zero on a non-empty query.
  - **Ties.** Two runs of equal `rarity` are a tie. The accessor never
    breaks one: it returns the number, and the READER applies its own
    pre-findings rule as the tiebreak (for C6, the letter argmin's own
    order). That keeps each reader's choice a pure function of (rarity,
    its own stated order), with no hidden order inside the accessor.
- **Bounds:** counts are ≤ 2^40 and sums are ≤ 2^48, so `uint64_t`
  suffices. Each term is ≤ ~48 bits of Q16, so the sum of a
  `PCREC_MAX_FIND_RUN`-long run fits in `uint64_t`.
- **Why sets and not strings:** the pooled form handles C6's caseless run
  and C5's class runs with the same arithmetic. An exact run is the
  singleton case.
- **Self-contained (§0.3):** `P(first)` comes from the block's own row
  totals. No other block is read.
- **Acceptance (§11.4):** on RUNEST's four train/test splits, the
  accessor's ranking of the 14 runs must equal RUNEST's bigram scorer's
  ranking, including the WAF order `union < select < from` on
  `web_request`.

### 2.7 Exhibits

**The shipped default** (`src/findings/default.rxt`, authored; 256 `row`
lines, abbreviated):

```
analysis default
    description The shipped static prior: prefix_k.c's hand-assigned byte table, byte-identical (D123-5)
    freq
        question How often does each byte occur in machine-written line-oriented text?
        reader byte-rate (docs/spec/findings.md §4)
        analyzer authored: two-significant-figure citable priors, normalised to 1,000,000 (prefix_k.c header, 2026-08-28)
        encoding ascii
        serves byte-rate when byte via unigram
        row 00 2
        row 01 2
        …
        row 20 124561
        …
        row 61 54163
        …
        row ff 2
        provenance
            source authored
            retrieved 2026-08-28
            attribution etaoin-shrdlu letter ordering; prose whitespace share; machine-line punctuation raised
```

`serves … when byte` IS the restriction D123-4 required to be written into
the data: the flat 0x80–0xFF half is not usable outside `byte`.

**A user bundle extending a shipped one with their own run table**
(`./findings/log.rxt`, found through `-I ./findings`):

```
analysis log
    include <log>                      # include_next: the SHIPPED log (§4.3)
    bigram
        question How often does each adjacent byte pair occur in our gateway logs?
        reader run-rarity
        analyzer pcrec-analyze 0.1 --scan bigram
        encoding utf8
        serves run-rarity when byte,utf8 via markov1
        row 09 20 1822
        …
        provenance
            source exemplar
            retrieved 2026-09-25
            bytes 104857600
            sha256 3f…
```

Here `byte-rate` answers from the shipped `log`'s block (fall-through),
`run-rarity` answers from the user's block, and anything the shipped
`log` lacks falls to `default`.

---

## 3. The `.rxt` surface

### 3.1 Schema rows

Per `rxt_schema.def`'s column set. These are proposals; spelling is the
manager's call under `[DD-13b]` (memory `pcrec-dd13b-syntax-is-managers`).

| scope | kind | value | children | cardinality | constraints | change |
|---|---|---|---|---|---|---|
| FILE | `analysis` | TOKEN (defname, **lowercase only** [r2 M-S6]) | BUNDLE | REPEAT | unique-by value; `[a-z][a-z0-9_-]*` | **NEW**: opens a bundle |
| FILE | `freq` | TOKEN | DATA | — | — | **WITHDRAWN**: moves under BUNDLE with no name. MEASURED: no `.rxt` under `tests/` or `examples/` carries a `freq` line |
| BUNDLE | `include` | ANGLE-NAME (`<defname>`) | NONE | AT_MOST_ONE | — | **NEW**: C's search spelling. FILE-scope `include "path"` is unchanged and `include <x>` stays refused THERE |
| BUNDLE | `description` | PROSE | PROSE | AT_MOST_ONE | — | NEW |
| BUNDLE | `freq` / `cpfreq` / `bigram` | NONE | DATA | AT_MOST_ONE each | — | NEW (`cpfreq` at B5, `bigram` at B4: R2) |
| DATA | `encoding` | TOKEN | NONE | ONE | `closed data-encoding ascii utf8 latin1 bytes` | **NEW** (R25's key; describes the data) |
| DATA | `serves` | LIST | NONE | REPEAT, ≥1 | per-kind derivation check (§2.4); unique-by query within the block; **no (query, enc) pair claimed by two blocks of one bundle** [r2 M-B1] | **NEW** (operative) |
| DATA | `row` | LIST | NONE | REPEAT | key shape per kind, strictly ascending | CHANGED: value grammar fixed (§2.3) |
| DATA | `question`, `reader`, `analyzer`, `provenance` | as today | | | | unchanged. `reader` stays prose; `serves` is the machine-checked version of "a block nobody reads is not emitted" |
| PROVENANCE | `bytes`, `sha256` | as today | | | required-if parent == data **and** source != authored | CHANGED (§0.10; needs a conjunctive condition clause) |
| PROVENANCE | `url`, `ref` | as today | | | optional under a data parent | CHANGED (§0.10) |
| CONFIG | `analysis` | **TOKEN** (was LIST) | NONE | **AT_MOST_ONE** (was REPEAT) | lowercase defname | CHANGED: names ONE bundle (D123-1/2) |
| CONFIG | `pcrec` (raw CLI) | as today | | | refuses `--analysis` inside it [r2 M-B2] | CHANGED: a config names its analysis with the `analysis` line only (D123-8 item 2) |

`--list-schema` gains a `bundle` scope. That makes three nesting levels
(`analysis` → kind → `provenance`). `freq` → `provenance` already nests
two, and the build confirms the structure layer's frame stack takes a
third (B0).

### 3.2 The `analysis` line's new meaning

- **CONFIG `analysis <name>`** now names ONE bundle. D123's consequence
  text makes the spec sentence "names one analysis (a bundle)".
- **Config join (`from`, `with c1,c2`):** later-wins, which is
  `cfg_merge`'s existing rule for `engine`/`encoding`
  (`rxt_source.c:~3237`). It is one inherited scalar, not a list, so the
  "no precedence list" ruling holds.
- **No `analysis` anywhere** means the chain is just `default`: today's
  behaviour, byte-identical.
- **An experiment is a config VARIANT, in the file** [r2 M-B2, D123-8
  item 2]. To try `waf` under the `prose` analysis, the file says:

  ```
  config waf-prose from waf
      analysis prose
  target waf_prose = waf with waf-prose
  ```

  and the build selects that target. The experiment is then in the
  contract, visible to `--list-source`, and never an invisible CLI
  override of what the file says. `--analysis` on the command line only
  FILLS a target whose config names no analysis (§5.1).
- **Pattern-BLOCK-scope `analysis` is DECLINED** (R16's open point). An
  analysis describes the SUBJECTS a build will see, which is a build
  configuration fact. R11's use case (one pattern built against two
  exemplars) is already two `target` lines with two configs. A block-level
  line would be a second place to say the same thing.

### 3.3 Bundle `include`, and the deferred extension points

- **`include <name>`**: at most one, resolved by §4.3. Its value is an
  angle-bracketed defname, which is exactly the spelling `rxt_format.md`
  reserves for store lookups. **RULED (D123-8 item 4, [r2 M-S9]): one
  `include` per bundle now**, so the chain stays linear and readable at
  the line. Several includes come only LATER, together with selective
  include, and only when every line names its kinds (`include <json>
  kinds=freq`), so that disjointness is visible at the include lines
  without opening the included files. The notes, and the open scope
  question (does `kinds=` filter one link or the whole onward chain?), are
  kept in the boonies row `[FINDINGS-SELINC]`.
- **SELECTIVE include (D123-3, deferred, not precluded).** A future
  `include <json> kinds=freq` adds one optional `kinds=` item to this
  line's value. The resolution algorithm (§4.4) is already per-kind, so
  selective include is a FILTER on which kinds a link contributes. It is
  not a new mechanism. Nothing in this design reads the `include` line
  beyond its first token, so the item can be added without re-plumbing.
- **Overriding an included block's declarations without copying its rows**
  (for example "default's table, but also under utf8") would be a `rows
  <name>` reference inside a block. It is NOT built. Copy satisfies
  D123-4's "a user bundle can override it", and the D123-2 helper script
  makes copying mechanical. The trigger is a user ask.

---

## 4. Resolution

### 4.1 The stops

| stop | what is searched | how a NAME maps to a bundle | present when |
|---|---|---|---|
| **S1** own file | the bundles defined in the compiling `.rxt` FILE ITSELF, or `pcrec_options.analysis_source` for a library call. **Not** its `include "path"` fragments and not its `lib` closure [r2 M-B3, D123-8 item 3] | the bundle whose `analysis` line carries the name. **A name defined twice in the file is a parse error** (`unique-by value`) | a file-operand compile, or a library call with `analysis_source` |
| **S2** `-I DIR`, in order | the file `DIR/<name>.rxt`, whose directory entry is EXACTLY `<name>.rxt`, byte for byte [r2 M-S6] | the file's ONE bundle, if it is named `<name>`. A file that exists but defines no bundle, or a bundle of another name, **FALLS THROUGH** to the next stop with a note (a `lib` library in the same directory is the common case) [r2 M-S4]. A file defining MORE THAN ONE bundle is a hard error naming the file [r2 M-S5] | `-I` given (now legal with `--pattern`, §0.2), or `pcrec_options.analysis_dirs` |
| **S3** embedded store | the shipped bundles compiled into `libpcrec` | by name | always |

- **Nothing else is read (R13).** There is no environment variable, no
  cwd-relative path other than paths given explicitly, and no home
  directory.
- **S2 never DISCOVERS by enumeration.** It asks for `DIR/<name>.rxt` only,
  which is what keeps `-I` order the entire ordering rule. To make the
  match exact on a case-insensitive filesystem (where opening `log.rxt`
  succeeds on `Log.rxt`), it confirms the directory holds an entry whose
  name is byte-equal to `<name>.rxt`. That reads the directory's entries
  for an EQUALITY test, never to find bundles; names are lowercase-only
  (§3.1), so a `Log.rxt` can never be the answer to any lookup.
- **A bundle inside an `include "path"` fragment** is not an S1
  definition. It is refused at parse, naming the rule ("bundles resolve
  from the compiling file, `-I`, or the store"), rather than accepted as
  text no lookup can reach. This is this revision's own call, small and
  reversible; the review lists it for Frank's confirmation. The boonies
  row `[FINDINGS-S1-REVISIT]` re-examines S1 under its stated triggers (a
  real include splice for patterns; users keeping bundles beside `lib`
  libraries; `[LIB]`'s store sharing the `<name>` namespace).

### 4.2 The route decision (D83-A4's weighing, decided)

**DECIDED: Route I, in its hybrid form (REQ R14's allowance).** Names
resolve through the `.rxt` source, then `-I`, then a built-in last stop.
There is no dedicated `--findings FILE` loader.

| criterion | Route I (chosen) | Route D (`--findings FILE`, dedicated namespace) |
|---|---|---|
| mechanisms | ONE search path (`-I`) for everything a compile draws on: `lib` definitions today, analyses now, `[LIB]`'s store later. General-mechanism memory; D83-A4's own suggestion | a second loader with its own ordering rule (flag order), beside `-I` |
| "a user's findings file is just another include" | a bundle in the compiling file is S1; any other file is found by `-I` as `name.rxt` (S1 is the file itself only, D123-8 item 3 — the first draft's claim that `include "my.rxt"` puts its bundles in S1 is withdrawn [r2 M-B3]) | needs its own flag even inside a `.rxt` build |
| `--pattern` compiles (R12) | `-I DIR --analysis NAME` (after §0.2's one-line un-refusal) | `--findings FILE --analysis NAME` |
| built-in names | S3, the last stop. D123's addendum shape exactly, with shadowing for free | the same store, reached by a separate lookup |
| namespace vs `[LIB]` | per PRODUCTION: `lib <x>` reads definitions, `analysis x` / `include <x>` reads bundles. One file may carry both, and neither reads the other's blocks | separate by construction, but at the cost of a second path concept |
| ambient state (R13) | none: explicit `-I` only | none |
| cost | lift the `-I`-needs-a-file-operand refusal (every query mode, the mode tables, the lib-dirs lifecycle: §0.2 [r2 M-S7]); add the `DIR/<name>.rxt` probe | a new flag, a new loader, a new ordering rule |

**R15 changes because of this** (§15): there is no flag taking a findings
FILE. A one-off file is `-I "$(dirname F)" --analysis "$(basename F .rxt)"`.
The name→file convention is what lets `-I` stay the only path concept. A
path-accepting spelling of `--analysis` would be sugar, and it is not
built (§16 Q3, RULED by D123-8 item 6).

### 4.3 The chain algorithm

```
find(name, from_stop):                         # first stop ≥ from_stop defining `name`
    for s in stops[from_stop:]:                # S1, S2 (each -I DIR in order), S3
        if s defines name: return (bundle, s)
        if s is an S2 file that exists but lacks `name`:
            note "DIR/name.rxt defines no bundle 'name'; continuing"   (§9, [r2 M-S4])
    fail "unknown analysis 'name'" listing the stops searched          (§9)

chain(selected_name):
    (b, s) = find(selected_name, S1)
    links = [(b, s)]
    while b has `include <n>`:
        start = (n == b.name) ? next(s) : S1   # §0.4: include_next on self-reference
        (b, s) = find(n, start)
        if (b, s) already in links: fail "analysis include cycle: a → b → … → a"
        if len(links) == PCREC_MAX_FIND_CHAIN: fail "analysis include chain exceeds N"
        links.append((b, s))
    links.append((BUILTIN_DEFAULT, S3))        # §0.6: by identity, never by name
    return links
```

Properties, each a fixture in §11:

- **Self-shadow works.** A user `log` with `include <log>` gets the
  shipped `log`.
- **The terminal default cannot be shadowed by accident.** A `-I` dir
  with `default.rxt` does not affect a compile that does not name it.
- **Duplicate terminal.** A chain that already contains the built-in
  default, for example through an explicit `include <default>` that
  reaches S3, does not add it again.
- **Timing.** The chain is resolved ONCE per target, before the compile.
  Every name is resolved eagerly, so a bad name fails even when the pattern
  would never ask a query. This is predictability over laziness.

### 4.4 Answering a query

```
answer(Q, E):   # E = this compile's -e
    for (b, s) in chain:
        k = the block in b whose `serves` line names Q and lists E
        if k: return derive(k.via, k.rows)     # §2.5/§2.6, memoized per (Q, E) per compile
    return NONE
```

The answer is memoized per compile, so four `byte-rate` readers derive
once. The derived values (a 256-entry ppm table for `byte-rate`, or the
block pointer plus its row totals for `run-rarity`) live in the per-compile
`Ctx`. There is no mutable static (TS-1), and each compile owns its
parses.

---

## 5. The CLI and library surfaces

### 5.1 Flags

| flag | effect | notes |
|---|---|---|
| `--analysis NAME` | **FILL-ONLY** [r2 M-B2, D123-8 item 2]: selects bundle `NAME` for the one `--pattern` artifact, and for every target of a file operand whose joined config names NO analysis | **It never overrides a config's `analysis`** — D93's file-wins rule keeps its single exception (`--engine`). For a target whose config names a DIFFERENT bundle, a non-fatal note in `--tune`'s shape (`cli.md`'s file-wins section): `pcrec: FILE:LINE: target 'T': CLI --analysis X and this file's analysis Y disagree; using the file's value (--analysis is fill-only)`. The same name gives no note. An experiment is a config VARIANT in the file (§3.2). **`--analysis` inside a config's `pcrec` line is REFUSED**: a config names its analysis with its `analysis` line |
| `-I DIR`, `--lib-path DIR` | unchanged meaning (search path, repeatable, ordered), **now also legal with `--pattern`** | §0.2. For a `--pattern` compile it serves only analysis lookup, since there is no `lib` line to serve |
| `--list-analyses` | the NAME LIST (§5.2) | a query: no pattern, no `-o` |
| `--list-analysis NAME` | the DETAILS and RESOLUTION view (§5.2). Honours `-I` and `-e` | a query |

No flag takes raw exemplar text (D83: pcrec never reads an exemplar).

### 5.2 The `--list-*` producers (table contract at birth)

**`--list-analyses`**: one row per EMBEDDED bundle (D123 addendum: "one
row per built-in analysis"). `-I` directories are not enumerated (§4.1).

| column | content |
|---|---|
| `name` | bundle name |
| `kinds` | comma list, canonical order `freq,cpfreq,bigram` |
| `serves` | comma list of `query@enc` this bundle's OWN blocks answer, for example `byte-rate@byte,byte-rate@utf8,run-rarity@byte` |
| `include` | its `include` name, or empty |
| `source` | provenance `source` of its first block (`authored` / `exemplar` / …) |
| `license` | provenance `license`, or empty |
| `retrieved` | provenance `retrieved` |
| `rows_digest` | FNV-1a-64 of the bundle's canonical row data (all blocks). This is NOT the stamp's digest, which covers consumed values only (§7, where `#section resolution` carries that one) |
| `bytes` | embedded text size |

**`--list-analysis NAME [-I DIR…] [-e ENC]`**: the chain as THIS
invocation would resolve it, then the named bundle's own contents. Its
sections:

| section | rows | columns |
|---|---|---|
| `#section chain` | one per link, in order | `link`, `bundle`, `stop` (`source` / `-I` / `store` / `store-default`), `location` (a path for S2, empty otherwise), `include` |
| `#section resolution` | one per (query × every compile encoding) | `query`, `encoding`, `link`, `bundle`, `kind`, `via`, `digest` (**the exact digest a stamp would carry**, §7), or `none` |
| `#section freq` / `cpfreq` / `bigram` | the NAMED bundle's own blocks, one row per nonzero key | `key`, `count`, plus for `freq` the normalized `ppm` |
| `#section declarations` | one per block | `kind`, `encoding`, `serves` (verbatim), `question`, `reader`, `analyzer` |
| `#section provenance` | one per block × field | `kind`, `field`, `value` |

- **R18** ("show which source each consumed kind resolved to, before
  anything is compiled") is `#section resolution`. The post-compile truth
  is the stamp.
- **[r2 M-S8] The per-TARGET view.** `--list-analysis NAME` answers for a
  name; a user building a file wants to know what each TARGET resolves to,
  after config joins and the fill-only `--analysis`. So `--list-analysis`
  also takes a FILE operand in place of `NAME` (`pcrec --list-analysis
  [-I DIR…] [--analysis X] FILE`) and emits:

  | section | rows | columns |
  |---|---|---|
  | `#section targets` | one per target | `target`, `configs` (the joined list), `analysis` (the name, or empty), `named_by` (`config` / `cli-fill` / `none`), `config_line` |
  | `#section resolution` | one per (target × query × compile encoding) | `target` plus the name-view's `resolution` columns |

  The chain and block sections are the name view's, one per distinct
  bundle. Spelling is the manager's under `[DD-13b]`; the content is the
  finding.
- **[r2 M-S10] Table-contract enrolment.** Both producers join
  `docs/spec/table_contract.md`'s Scope table at birth (B2) and its
  conformance check, not only its prose. Every free-text column
  (`question`, `reader`, `analyzer`, provenance `value`, `description`,
  paths) passes through the contract's own field escaping, since a user
  bundle's prose can carry a TAB or a newline; the hex `key` and decimal
  `count` columns need none by grammar.
- **The copy-edit-shadow round trip (D123-2)** is a later helper script
  reading `#section declarations`, the kind sections and
  `#section provenance`. It is not a compiler feature.

### 5.3 Library (R17)

`pcrec_options` gains three fields. They are appended, and the D80 hunk is
in `lib/pcrec.h`'s own contract comment plus `findings.md`:

```c
const char *analysis;             /* bundle name; NULL = none (chain is just `default`) */
const char *const *analysis_dirs; /* NULL-terminated S2 search list; NULL = none */
const char *analysis_source;      /* in-memory .rxt text defining bundles (S1); NULL = none */
size_t      analysis_source_len;
```

- **The library PARSES** (R17's choice). There is one reader, and a caller
  hands text rather than parsed values, because parsed values would be a
  second input shape to validate.
- **A caller with no filesystem** passes `analysis_source` and/or relies
  on S3.
- **[r2 M-S12] The buffer parse opens nothing.** The embedded store and
  `analysis_source` are BUFFERS, while the `.rxt` reader today resolves
  head lines against the filesystem (`include "path"` by `realpath` at
  parse time, `lib "path"` by existence). The reader gains a
  NO-FILESYSTEM mode for buffer input: a head line that would open a file
  (`include "…"`, `lib "…"`) is refused in a buffer, by name, and nothing
  else changes. The store's bundles never carry such lines (a `tests/`
  check parses every one in this mode, §11.5), and a library caller's
  `analysis_source` gets the same refusal rather than a relative path
  resolved against the process cwd (R13). Owed at B1, where the store is
  first parsed.

---

## 6. The accessor: the ONE seam (D122, R23, R39)

### 6.1 Signatures (`src/core/findings.h`, internal; `src/core/findings.c`)

```c
/* byte-rate for THIS compile: 256 ppm entries, Σ = 1,000,000, each >= FLOOR,
 * from the ONE block §4.4 selects — or NULL (NONE: no block along the chain
 * declares byte-rate under this compile's encoding). Derived once per compile
 * and memoized in Ctx; the call records the consumption for the stamp (§7). */
const uint32_t *pcrec_find_byte_rate(Ctx *cx);

/* Σ rate[b] over the set, capped at 1,000,000 — prefix_k.c's private set_ppm,
 * published (RFP §2.3's own recommendation). rate == NULL is the
 * CARDINALITY fallback: ⌊|set|·10^6/256⌋ (§0.8, C4's declared NONE rule).
 * An EMPTY set returns 0 under both arms [r2 S-F6]; a caller comparing
 * masses breaks ties by its own pre-findings order, never inside here. */
uint32_t pcrec_find_set_mass(const uint32_t *rate, const uint8_t set[256]);

/* run-rarity (§2.6) of a run of byte SETS (house class bitmaps, one per
 * position; an exact run is singletons), in Q16 bits of -log2(density per
 * position). Returns false for NONE. Records consumption. len <=
 * PCREC_MAX_FIND_RUN. */
bool pcrec_find_run_rarity(Ctx *cx, const uint8_t (*const sets)[32], int len,
                           uint64_t *rarity_q16);
```

**D124's lens** ("is this a question both emissions share? then one
table, engine hats"): yes, and the accessor already has that shape. The
queries are engine-neutral; C1/C2 feed both engines' pre-checks, C3 and C4
feed the DFA scan that the VM hybrid also runs. No reader holds an
engine-local copy of a rate. What each reader's choice may and may not
change for each CONSUMER is §6.2a's table (D124 item 3: every shared row
states what it guarantees to each consumer).

These three are the whole surface. `pcrec_byte_freq_ppm` and
`byte_freq_ppm_tbl` are DELETED at B1: the default's values now live in
`src/findings/default.rxt`. Every reader reaches findings only through the
accessor, with `Ctx` carrying the resolved chain. `DfaSel` keeps no table
pointer (R39), and a row predicate calls the accessor through `DfaSel.cx`.

### 6.2 Customers → query → NONE fallback (C1–C11)

The NONE fallback is each READER's own rule, stated in the spec (R24).
These fallbacks are code; APPLICABILITY is data (§2.4).

| # | reader (site) | query | NONE fallback | lands |
|---|---|---|---|---|
| C1 | `rb_pick` (`reqbyte.c`) | `byte-rate` | PCRE2's rightmost member (today's non-`byte` answer) | B1 (migrated, byte-identical) |
| C2 | `rn_scan_index`, `rn_window_start` (`reqbyte.c`) | `byte-rate` (argmin; Σ over the 8-byte window) | leftmost / leftmost window | B1 (migrated). Moving the WINDOW choice to `run-rarity` is its own row, with its trigger: a measured window mis-pick |
| C3 | `req_byte_dominated_by` (`emit_dfa.c:5495`), G1 | `byte-rate` | identity only (`p == q`) | B1 (migrated). The WIDENING (scan run rate vs prefilter byte rate, B2R §6) reads `run-rarity` + `byte-rate` and stays D77-held (I-103) |
| C4 | `set_ppm` → `pcrec_find_set_mass` (`prefix_k.c`) | `byte-rate` | **cardinality** (§0.8). NEW: today it is ungated | B1. **Moves** under `utf8` + default (named manifest, §11.3) |
| C5 | `[OPT-LITSCAN]` form rows (`DfaSel` predicates) | `byte-rate` (hit rate); `run-rarity` (restart arm) | the list's total fallback row | with those rows (D122-2(4)) |
| C6 | S4(a) caseless run pick | `run-rarity` over fold-pair sets | letter argmin (REQ C6: known wrong in deployment) | **B4**, which admits `bigram` (R2) |
| C7 | `dfa_scans[]` stay/skip | `byte-rate` set mass + a run-length kind (not built) | today's dispatch | conditional (REQ C7). The kind is not built (§17) |
| C8 | `[OPT-A]` rarest-byte start scan | `byte-rate` | `cand_from_escapes` | with its row |
| C9 | `[OPT-FIRSTSET]` density | `pcrec_find_set_mass` | no decline arm | no customer now (REQ §0.1) |
| C10 | `[OPT-4]` | — | — | retired (REQ) |
| C11 | `[ENG-PGO]` | — | — | out of scope: D83 (2), a separate shape |

### 6.2a Why no reader's choice can move an answer OR a give-up [r2 S-F1, S-F2]

The invariant is stronger than the first draft stated: for ANY rate table,
the compile must give the same answers AND the same give-up behaviour
(`docs/spec/limits.md` §1 makes a give-up honest, but a give-up that a
user's bundle can switch on or off is a speed decision moving an outcome,
which is K64's and K65's class). Per reader:

| reader | what the rate chooses | why the choice cannot move an answer or a give-up | premise the build must keep |
|---|---|---|---|
| C1 `rb_pick` | WHICH necessary byte the whole-window pre-check scans | Any member's absence proves NOMATCH, so the answer is pick-independent. The GIVE-UP was not: on a VM route with no DFA in front, only the picked byte's `memchr` proves absence, so a subject lacking a different member reaches the backtracker (**K65**). K65's ruled fix (D123-8 item 1, (a)) pre-checks EVERY member on those routes, which makes the give-up pick-independent too | K65's fix is on main before any non-default rate reaches C1 (B2's dependency, §13) |
| C2a `rn_scan_index` | which member of the (emitted) run the run pre-check's `memchr` scans | The run pre-check compares the WHOLE emitted run at each hit, so the subjects it rejects are the subjects lacking that run, whichever member is scanned | the run compare stays whole-run (REQ_RUN's P4); a sabotage that verified only the scanned member would be F-1's class |
| C2b `rn_window_start` | WHICH 8-byte window of a longer necessary run is emitted | **NOT covered — K65's shape, found by this revision (argued from K65's mechanism, not measured).** Any window's absence proves NOMATCH, so the answer is window-independent; but on a VM route with no DFA in front, a subject lacking window B and holding window A reaches the backtracker only when A is the one emitted. So the window choice can switch a give-up exactly as C1's pick did | ruled fix needed: extend K65 (a) to runs (pre-check every necessary window on those routes) OR take the window findings-blind there. Listed OPEN in the review; until ruled, B1 migrates C2b's rate read but B2's non-default bundles must not reach it on no-DFA-front VM routes |
| C3 `req_byte_dominated_by` (G1) | whether the byte pre-check is EMITTED or ELIDED as dominated by the candidate scan | G1 can only elide where `dfa_cand_scan_byte` returns `p ≥ 0`, which requires `pcrec_artifact_has_dfa_scan` (`emit_dfa.c:5507`, `dfa_cand_scan_byte` just above it): a DFA route, or the VM hybrid's inlined DFA prefilter. On the DFA the search is linear. On the hybrid, every reqbyte-necessary byte is necessary to the prefilter's language as well — the r1 S1 panel's argument (`../../dev/reviews/2026-09-25-r1-litscan-s1.md` S1-2: `A_LOOK`/`A_BREF`/`A_VAR`/`A_CALL` decline, `A_ATOMIC` is transparent on both sides, count-collapse keeps `rmin ≥ 1`) — so a subject lacking `q` is rejected by a linear machine before any VM attempt. Hence for every rate table the elided and the emitted forms answer and give up identically; the rate chooses cost only. On a VM route with NO DFA scan, `p = -1` and the pre-check is always kept | the `p < 0 → false` guard and the "every necessary byte is prefilter-necessary" property. Sabotage F-13 breaks the first |
| C4 `set_ppm` (offset-k) | which offset SETS the `ofsskip` filter scans and verifies | offset-k is a DFA prefilter: every (offset, set) it tests is necessary for every match, so any selection is a sound filter in front of a linear machine | the derivation, not the rate, decides necessity (the rate only ranks sets) |

**What this does NOT cover.** A future reader on a VM route with no DFA
front must bring its own row here before it reads a rate. That is the
place the next K65 would enter.

### 6.3 What changes at each of today's sites (B1)

| site | today | after |
|---|---|---|
| `reqbyte.c:585` | `bool bytekey = cx->opt->encoding == PCREC_ENC_BYTE` | `const uint32_t *rate = pcrec_find_byte_rate(cx)`. `rb_pick`/`rn_*` take `rate` and treat `rate == NULL` exactly as they treat `!bytekey` today |
| `emit_dfa.c:5498` | `if (cx->opt->encoding != PCREC_ENC_BYTE) return false;` then two `pcrec_byte_freq_ppm` reads | `rate = pcrec_find_byte_rate(cx); if (!rate) return false;` then `rate[p] <= rate[q]` |
| `prefix_k.c:302` `set_ppm` | reads `byte_freq_ppm_tbl` ungated | `pcrec_find_set_mass(pcrec_find_byte_rate(cx), set)`: NULL gives cardinality |
| `prefix_k.c:89-137` | the table + `pcrec_byte_freq_total_ppm` | deleted. `run_offset_skip.sh` §1's sum assertion moves to `tests/findings/` over the NORMALIZED default (§11.4) |

Under `-e byte` with no analysis named, all four read the default's
normalized table. §0.7 makes it equal to today's table entry for entry, so
the program region is byte-identical.

### 6.4 The consumption record

`Ctx.find.used[Q]` holds the answering (link, block) or NONE, and is set
on the first accessor call for Q. The stamp (§7) reads it after emission.
**The record must belong to the FINAL compile attempt**: the
`compile_driver` engine-selection retry ladder re-runs readers, so the
record resets per attempt, like every `Job` field. This is an
implementation obligation with a sabotage row (§11.2 F-9).

**[r2 S-F10] "Consumed" means ASKED, so asking must not depend on deny
flags or on reader order.** If a reader called the accessor only when its
own deny flag was off (or only after an earlier short-circuit), then
`-fno-req-byte` would drop `byte-rate` from the stamp and the axis builds
would differ from the default in the stamp alone, for no answer reason.
Rules:

1. **Deny-independent asking.** Each reader asks at its ANALYSIS, before
   and regardless of any deny or emission decision. The analyses already
   run under their deny flags ("a declined artifact keeps `Job.req_byte`
   … the analysis ran", `emit_dfa.c`'s `req_admit` header); the ask moves
   with the analysis, not with the emission. So the asked set is a
   function of (pattern, encoding, engine route, resolved chain) only.
2. **The stamp is written after the last reader.** The `<P>_FINDINGS`
   line and the `rx_info.findings` initializer are rendered from the
   FINAL attempt's record after emission completes (the header text is
   assembled last, or the line is back-filled); a reader running after the
   stamp is written would be an unstamped consumption.
3. **Fallback, only where rule 1 cannot hold for some reader:** the axis
   answer-identity sweep and the identity gates exempt exactly the
   `<P>_FINDINGS` line and the `rx_info.findings` initializer (F9's
   named-lines gate, §11.3), and the exemption is listed by name in the
   gate. This is a fallback, not the design: the build first tries rule 1
   everywhere and names any reader it could not arrange.

---

## 7. Stamps and the digest (D123-2, D76/D94, R19–R22)

**The stamp**, always present in every artifact, next to `RX_REQ_BYTE`'s
family:

```c
#define <P>_FINDINGS "byte-rate=default:1f0e2d3c4b5a6978;run-rarity=weblog:0a1b2c3d4e5f6071"
```

- **One `query=bundle:digest` item per query the compile ASKED**, in the
  fixed query order (`byte-rate`, `run-rarity`), `;`-joined.
- **Asked but unanswered:** `query=none`, for example `-e utf8` under the
  default gives `byte-rate=none`.
- **Nothing asked:** the empty string. A pattern whose readers never ran
  (no required byte, anchored DFA) carries `""`, and that is still a stamp.
- **`bundle`** is the name of the bundle whose block ANSWERED. It is not
  the selected head and not the stop. A user's byte-identical copy of a
  shipped bundle therefore gives a byte-identical artifact (R7), and the
  digest tells a reader which one it was (compare it with
  `--list-analysis`'s `resolution.digest`).
- **`rx_info.findings`** (`const char *`, appended, a layout event) mirrors
  the macro. D43 makes `rx_info` the canonical machine-readable record, and
  a macro-only stamp would be invisible to a linked binary.
  `docs/spec/match_api.md` §6 gets the field and the change-log line.
- **The bundle NAME is a privacy surface** [r2 A-7]. Every artifact built
  under a user bundle carries that bundle's name in plain text, in the
  macro and in `rx_info`, so a shipped binary discloses it (`acme-gateway`
  says whose traffic was analyzed). `findings.md` and the analyzer's
  `--help` state this beside §10.5's per-kind disclosure table; the
  mitigation today is to name bundles neutrally. Whether pcrec should offer
  a redaction (digest only) is OPEN to Frank, because D123-2 rules "the
  source name per consumed kind" into the stamp.

**The digest** is FNV-1a-64, rendered as 16 lowercase hex characters, over
a canonical byte string of exactly what the reader consumed:

| query | tag | digested bytes after the tag |
|---|---|---|
| `byte-rate` | `pcrec-find-1\0byte-rate\0` | the 256 DERIVED ppm values, `uint32` little-endian, byte order. **No kind and no `via`** [r2 M-B1]: the reader consumes the derived table and nothing else, so the same values from a `freq` block (`unigram`) or a `cpfreq` block (`encode-utf8`) give the SAME digest and a byte-identical artifact (R19) |
| `run-rarity` | `pcrec-find-1\0run-rarity\0<via>\0` | the block's nonzero `(a, b, count)` rows ascending, as `u8, u8, u64le`. Here the digest covers the reader's INPUT (the rows), not a derived table, so the derivation that will read them is part of what was consumed and `via` is in the tag. Today `markov1` is the only one |

The rule, stated once: **the digest covers exactly the bytes whose change
could change what a reader sees.** For `byte-rate` that is the derived
table; for `run-rarity` it is (derivation, rows). The first draft put
`<kind>\0<via>` in every tag while also claiming `freq` and `cpfreq` give
one digest; the two could not both hold.

- **Excluded:** provenance, `question`/`reader`/`analyzer`, `encoding`,
  the `when` list beyond the fact that it matched, other kinds, and
  queries not asked. That satisfies D123-2's "a pattern that never reads a
  kind does not move when that kind's table changes; provenance edits move
  nothing".
- **Why FNV-1a-64 and not SHA-256:** this is identity against accidental
  change, not an adversarial setting. FNV is ~10 lines in `src/core` and
  leaves `libpcrec` dependency-free. Collisions between two consumed tables
  would need adversarial construction, and would cost a stale identity pin
  at worst, never an answer.
- **The `--list-analyses` `digest` column is a different hash** (over the
  bundle's rows) and is renamed **`rows_digest`** so the two cannot be
  confused (§5.2).

**The abi event:** ONE bump, to **the next abi number at landing**
[r2 S-F11], carrying the `<P>_FINDINGS` line, the `rx_info.findings` field
and D122-2(3)'s gate move (R21, D123-2). The first draft said 32 → 33;
main is already at 33 (K64's fix, `src/gen/emit_dfa.c:51`), and K65's fix
is expected to take the next number, so no literal is written here. The
D94 ritual applies (readers found by grep for the CURRENT number at
landing, `make test-codegen`, then registry/codegen/rxtsource). The
whole-file pin re-pins.

**The identity gate is whole-file minus NAMED lines** [r2 S-F9]. "Program
region unchanged" named no check. The gate is: the whole-file diff of each
artifact against its pre-change twin, after deleting exactly these lines
and no others, must be EMPTY for every `-e byte` artifact — (1) the abi
stamp line(s) the D94 grep finds, (2) the `<P>_FINDINGS` line, (3) the
`rx_info.findings` initializer line. Under `-e utf8` it must be empty
except on the artifacts §11.3's per-artifact manifest names. The list of
deleted lines lives in the gate script, by name, so a fourth line moving
is a red gate rather than a silent widening.

**R22 (a shipped-data change is a visible event):** regenerating a shipped
bundle, or editing `default.rxt`, changes the digest of every artifact
that consumed it. Pinned artifacts then fail the whole-file identity gate,
and the stamp diff NAMES the bundle. No abi bump is needed, and the change
is never silent.

---

## 8. The embedded store build

### 8.1 Layout

| path | what | written by | checked by |
|---|---|---|---|
| `third_party/<source>-<version>/` (for example `elastic-examples-apache-logs-<commit8>/`) | the vendored sample UNMODIFIED + `LICENSE` + `PROVENANCE.md` (naming `src/findings/<name>.rxt` as what derives from it) + `generate.py` | a sourcing lane (§13 B5) | the existing `make test` `generate.py --check` loop. **A manifest-only source** (no redistributable sample in tree, D123-6) cannot be recounted there: its `--check` prints a named `SKIP (manifest-only: <source>)`, the loop counts and prints skips at its end (PC-3's "skips loudly" shape), and a separate opt-in target re-fetches by the manifest's url/sha256 and then runs `--check` FAILING CLOSED on any fetch or hash mismatch [r2 A-5] |
| `src/findings/default.rxt` | the authored default (§2.7) | hand. It is `source authored`, the one bundle with no generator | `tests/findings/`: normalizes to the pinned `default_ppm.tsv` (the dump RUNEST already made, `data/byte_freq_ppm.tsv`) |
| `src/findings/<name>.rxt` | a shipped bundle's SOURCE OF TRUTH (R14), committed so it diffs and reviews | `third_party/<src>/generate.py` running **the analyzer** (R27b) over the sample | `generate.py --check` (drift = red) |
| `build/gen/findings_store.inc` | every `src/findings/*.rxt` as a C string literal plus a name index | a Makefile rule (`scripts/embed_text.sh`, POSIX sh + `od`), at BUILD time. **The invocation is pinned** [r2 A-8]: `LC_ALL=C od -An -v -tx1`, whose output (hex pairs, `-v` so repeated lines are not collapsed to `*`) is the same bytes under BSD and GNU `od`; the script consumes only the hex pairs, never `od`'s column spacing | never committed (§8.2). **Checked** [r2 A-3]: `tests/findings/` compares, for every name in `--list-analyses`, a digest of the embedded text (read back through the library) against the same digest of the committed `src/findings/<name>.rxt`, so an embed that drops, truncates or mis-escapes a byte is red |
| `src/findings/CLAUDE.md` | directory charter | the build lane | convention |

### 8.2 Why TEXT and why build-time (§0.11)

- **Embedding the `.rxt` text means S3 is read by the same parser as S1
  and S2.** There is no second representation to agree with, and no
  generated C table to `--check`.
- **The `.inc` is a mechanical ENCODING of committed text, not a
  derivation.** It is produced at build time into `build/` like an object
  file. A committed `.inc` would be a second copy of the committed `.rxt`
  and would need its own drift check. The embed is still CHECKED (§8.1's
  digest comparison, [r2 A-3]), because "mechanical" is a claim about the
  script and the check is about its output.
- **The embedded text is parsed in the reader's NO-FILESYSTEM mode**
  (§5.3, [r2 M-S12]): a store bundle carrying an `include "…"` or `lib
  "…"` head line is refused, so S3 can never open a file.
- **This does not break the `third_party/` rule** ("a data source compiles
  to generated tables"): the source → `generate.py` → committed derived
  artifact chain is intact, and the derived artifact is `src/findings/<name>.rxt`.

### 8.3 Size bounds (R32, R33)

| item | estimate (MEASURED where marked) | bound (proposed limits rows) |
|---|---|---|
| `default` | 256 rows ≈ 3.3 KB text | — |
| `weblog` (freq + cpfreq + bigram) | freq ≈ 3 KB, cpfreq (86 code points MEASURED on RUNEST's sample) ≈ 1.5 KB, bigram **3,288 pairs ≈ 42 KB MEASURED** | — |
| `log` | bigram **471 pairs ≈ 6.5 KB MEASURED** on HDFS; the real source is TBD (§16 Q2) | — |
| whole store | ≈ 55–75 KB | `PCREC_MAX_FIND_STORE_BYTES` 256 KiB, checked at gen time and in `make test` |
| any one bundle (user files too) | worst dense bigram ≈ 65,536 × ~16 B ≈ 1 MB | `PCREC_MAX_FIND_BUNDLE_BYTES` 1 MiB, refused by name |
| rows per kind | freq 256, bigram 65,536 (structural); cpfreq | `PCREC_MAX_FIND_CPFREQ_ROWS` 65,536 |
| a single count | — | `PCREC_MAX_FIND_COUNT` 2^40 (keeps §2.5/§2.6 in `uint64_t`) |
| chain length | — | `PCREC_MAX_FIND_CHAIN` 8 |
| run length for `run-rarity` | — | `PCREC_MAX_FIND_RUN` 64 |

A DENSE kind would need its own D77 justification (R33). Counts are stored
sparse, so the text is proportional to what the corpus observed.

---

## 9. Failure modes and diagnostic tiers (D26; R33a: name the thing and the reason, nothing more)

| failure | tier | behaviour |
|---|---|---|
| unknown analysis name (config, `--analysis`, or a bundle `include`) | **hard error** | refuse the compile, naming the name and the stops searched (the unknown-`lib` class) |
| `-I DIR/<name>.rxt` exists but defines no bundle, or a bundle of another name | **non-fatal note, FALL THROUGH** to the next stop [r2 M-S4, D123-8 item 5] | naming the file; the lookup continues (a `lib` library in a shared `-I` dir is the common case) |
| `-I DIR/<name>.rxt` defines MORE THAN ONE bundle | hard error [r2 M-S5] | naming the file: one bundle per `-I` file |
| an `analysis` name with an uppercase letter (config, bundle, `include`, `--analysis`) | parse error / usage error [r2 M-S6] | naming the rule: names are lowercase |
| an `analysis` block inside an `include "path"` fragment | parse error [r2 M-B3] | naming the rule: bundles resolve from the compiling file, `-I`, or the store |
| `include "…"` or `lib "…"` in a BUFFER-parsed bundle (store, `analysis_source`) | parse error [r2 M-S12] | a buffer opens nothing |
| two blocks of one bundle serving one (query, encoding) | parse error [r2 M-B1] | naming both `serves` lines |
| `--analysis` inside a config's `pcrec` line | parse error [r2 M-B2] | naming the rule: a config names its analysis with its `analysis` line |
| an include cycle (not self-reference) / chain over `PCREC_MAX_FIND_CHAIN` | hard error | naming the chain |
| a bundle name defined twice in the compiling file | **parse error** (schema `unique-by`) | the existing `rxt_fail` machinery, naming both lines |
| a malformed block, a row key out of range or not ascending, a `serves` naming a derivation illegal for its kind, an unknown `encoding` | parse error | same |
| a block with all-zero counts, a count over `PCREC_MAX_FIND_COUNT`, a bundle over `PCREC_MAX_FIND_BUNDLE_BYTES`, cpfreq over its row limit | hard error, by limit name | never truncated, never a silent fallback |
| the same name at two stops | **not an error** | shadowing is the rule (D123 addendum), visible in `#section chain` |
| `--analysis X` where a target's config names `Y ≠ X` | **non-fatal note** (stderr); the FILE's `Y` is used [r2 M-B2, D123-8 item 2] | per target, in `--tune`'s conflict shape (§5.1) |
| the SELECTED chain declares no query at all under this compile's `-e` (for example a `bytes`-only user bundle on a `-e utf8` compile) | **non-fatal note** | computed at resolution, independent of the pattern. The user's evident intent is unmet and a correct fallback exists (RFP §3.3 precedent) |
| a query unanswered for this compile | **silent** | the stamp records `query=none` and the reader takes its NONE fallback (§6.2). The normal case |
| stale findings (the exemplar changed since analysis) | **not pcrec's** | pcrec never sees the exemplar. `pcrec-analyze --check` compares |
| an embedded bundle fails to parse | **internal error** (abort) | made unreachable by `make test`'s parse-every-store-bundle check (§11.5) |

---

## 10. The analyzer contract (`pcrec-analyze`; D83, D123-3/3a, R26–R27d)

### 10.1 Where it lives

| tier | location | status |
|---|---|---|
| prototype | `scripts/pcrec_analyze.py`, graduated from RUNEST's `ngram_count.py`: same CLI, same output BYTES as the end state | B3 |
| end state | `analyze/` (a new top-level directory: `main.c`, `count.c`, `sha256.c`, `CLAUDE.md`), built by `make` into **`build/pcrec-analyze`**, a separate zero-dependency binary. **NOT** in `libpcrec` or `pcrec` (R27a) | B6. Implement-then-replace: the python version is deleted once §11.8's agreement holds |
| the ONE counter (R27b) | `analyze/count.c` (python: the prototype's `Counts`) | shipped `generate.py`s invoke the analyzer. They never count themselves |

### 10.2 Command line (pattern-blind: there is no pattern argument, R27c)

```
pcrec-analyze --name NAME --retrieved DATE [--scan freq,cpfreq,bigram]
              [--source TOKEN] [--url U] [--ref R] [--license L]
              [--shard K/N] [FILE | -]          → one bundle (.rxt) on stdout
pcrec-analyze --merge --name NAME PART.rxt…     → the merged bundle on stdout
pcrec-analyze --digest-only [FILE | -]           → bytes + sha256 (for --merge)
pcrec-analyze --check BUNDLE.rxt [FILE | -]      → exit 0 iff a recount reproduces the rows
```

- **Switches.** `--scan` selects kinds, default `freq,bigram`. A requested
  scan that cannot run is a hard error. The main case is `cpfreq` on input
  that does not decode as UTF-8 (R26). The analyzer never silently skips a
  requested scan (D123-3).
- **No clock.** `--retrieved` is required, so the same input and flags give
  byte-identical output (R27c).
- **Written declarations (§2.4)**, from what the pass observed:

  | observed | `encoding` | `bigram` | `freq` (no `cpfreq` scanned) | `freq` + `cpfreq` both scanned |
  |---|---|---|---|---|
  | every byte < 0x80 | `ascii` | `run-rarity when byte,utf8` | `byte-rate when byte,utf8` | `freq`: `byte-rate when byte`; `cpfreq`: `byte-rate when utf8 via encode-utf8` |
  | valid UTF-8 with non-ASCII | `utf8` | `run-rarity when byte,utf8` | `byte-rate when byte,utf8` | same split |
  | invalid UTF-8 | `bytes` | `run-rarity when byte` | `byte-rate when byte` | `cpfreq` refused (hard error if requested) |

  **[r2 M-B1] The defaults can never collide.** The first draft gave
  `freq` and `cpfreq` both `when byte,utf8`, which §2.4's rule now refuses
  at parse. When both are scanned, the `byte` compile reads `freq` and the
  `utf8` compile reads `cpfreq`. On input that decodes, the two derived
  tables are IDENTICAL (decoding valid UTF-8 and re-encoding it is the
  identity on bytes, so `encode-utf8`'s counts equal `freq`'s), and by
  §7's digest rule so are their digests; the split is therefore a choice
  of which block is SHOWN answering, not of the answer. It gives the
  `utf8` compile the block whose applicability the data declares
  per-code-point (D123-4), and it leaves `freq` the one block a `bytes`
  exemplar can have.

  These are the analyzer's defaults, written into its output where the
  user can see and edit them. The compiler applies whatever the file says,
  and refuses a file whose edits create a collision.
- **Output.** §2.7's shape: kinds in canonical order, rows ascending,
  provenance in schema order, `bytes` and `sha256` filled, and `analyzer
  pcrec-analyze <version> --scan <canonical list>`.

### 10.3 One-pass, per analysis (D123-3: "stated per analysis")

| scan | one-pass? | state | stdin streaming |
|---|---|---|---|
| `freq` | yes | 256 × u64 | yes |
| `bigram` | yes | 65,536 × u64 (512 KB) + the previous byte | yes |
| `cpfreq` | yes | UTF-8 decoder carry (≤ 3 bytes) + a sparse code-point map (≤ 1,114,112 keys worst case) | yes |
| sha256 + bytes (always) | yes | 32 B + u64 | yes |
| *(not built)* trigram | yes | sparse contexts, unbounded | — |
| *(not built)* top-K tokens | **NO**: exact top-K needs the full dictionary, which means buffering proportional to the vocabulary. It would have to declare itself not-one-pass | — | — |

### 10.4 Parallelism (D123-3a: processes, order-independent)

- **Per scan:** one process per `--scan` kind over the same file, then
  `--merge`. The merge is a UNION of disjoint kinds.
- **Per shard:** `--shard K/N` covers the nominal range `[start_K, end_K)`
  of a seekable FILE, `start_K = ⌊(K−1)·size/N⌋`, `end_K = ⌊K·size/N⌋`.
  - **`bigram` seam (§0.5).** Shard K > 1 also reads the one byte at
    `start_K − 1` and counts it ONLY as the first element of the pair it
    opens — never into `freq`, `cpfreq` or `bytes`. **Shard 1 has no such
    byte** [r2 A-1]: it reads from offset 0 and counts its first byte into
    `freq` like any other. An implementation that treats "the first byte
    read" as the overlap byte uniformly drops byte 0 from `freq`; the
    k = 1 exception is stated so it cannot.
  - **`cpfreq` seam** [r2 A-2]. Shard K owns exactly the code points whose
    LEAD byte lies in `[start_K, end_K)`. So shard K skips the continuation
    bytes (`10xxxxxx`) at its start — at most 3 on valid input — and reads
    past `end_K` to finish the code point whose lead byte is before
    `end_K` — at most 3 more bytes. Each shard computes its cut from the
    file alone, the two neighbours' cuts are the same byte offset, and no
    code point is counted twice or missed. More than 3 continuation bytes
    in a row is invalid UTF-8, which `cpfreq` refuses anyway (R26), so the
    reach never exceeds 3 bytes on any input `cpfreq` accepts.
- **Merge rules.** Counts ADD. `encoding` combines by the lattice
  `ascii < utf8 < bytes`, and `serves` is recomputed from it by §10.2's
  table. `bytes` and `sha256` come from a `--digest-only` run over the
  whole input (sha256 is sequential), and `--merge` checks that the
  shards' byte total equals it. Every rule is commutative and associative,
  so the result does not depend on part order.
- **stdin** cannot be sharded. Per-scan parallelism over stdin is the
  shell's business (`tee`).

### 10.5 Disclosure: what each kind reveals (REQ §4 privacy risk)

| kind | reveals | stated where |
|---|---|---|
| `freq` | charset and language mix, structural punctuation density | analyzer `--help`, `findings.md` |
| `cpfreq` | script mix, rare characters (possibly identifying for a small corpus) | same |
| `bigram` | adjacent byte-pair rates. It cannot reconstruct strings longer than 2 bytes, but chaining frequent pairs hints at frequent tokens | same, and it is why `trigram`/tokens stay unbuilt without a customer and a privacy statement (§17) |
| the bundle NAME [r2 A-7] | whatever the name says (a customer, a product, a site); it is stamped into EVERY artifact built under the bundle (§7) | same; the advice is to name bundles neutrally. A redaction option is OPEN to Frank |

---

## 11. Test and oracle plan: findings may change SPEED, NEVER ANSWERS

New test directory `tests/findings/` (with its own CLAUDE.md) and a
`make test` section `test-findings`. Sabotage ids below are provisional:
at landing they are renumbered from main's highest, which is **S273** at
`f94b9dd8` (BOILERPLATE), with anchors copied from `git show HEAD:<path>`.

### 11.1 Answer identity under adversarial findings (R34)

| bundle (`tests/findings/adversarial/*.rxt`) | shape | serves |
|---|---|---|
| `uniform` | every byte and every pair equal | byte-rate and run-rarity, `when byte,utf8` |
| `inverted` | the default's ranks reversed | same |
| `onehot-e`, `onehot-80` | all mass on `e` / on 0x80, every other byte at the floor | same |
| `floor-but-one` | 255 bytes at the floor, the remainder on `/` | same |
| `random-<seed>` | seeded; the seed is in the file | same |
| `fire-all` | derived by `tests/findings/gen_adversarial.py` from §11.3's per-reader census, so that every reader whose choice CAN differ from the default's DOES | same |

- **Every adversarial bundle declares `when byte,utf8`.** Readers are
  therefore exercised under both encodings, including the `utf8` arms that
  the default leaves at NONE.
- **Oracle:** the corpus's existing expectations (libpcre2 / python `re`),
  unchanged. This is legitimate because a prior is "a prior and not a
  promise" (`prefix_k.c`).
- **Where it runs:**
  - `make test-axes` runs a new FINDINGS axis: the whole corpus × each
    bundle, via `AXES="-I tests/findings/adversarial --analysis <b>"`
    (multi-hour on darwin, per BOILERPLATE).
  - `make test` runs a fixed sampled slice of the corpus × every bundle,
    plus all of `tests/findings/`'s own cases.
- **Row order (R40):** the `DfaSel` lists are `static const`, and a grep
  check asserts that no findings read sits in a list definition.

### 11.2 Sabotage rows

| id | sabotage | detector |
|---|---|---|
| F-1 | a reader lets a rate decide SOUNDNESS (for example it skips a verify when `rate[b] < 10`) | `onehot-e`/`floor-but-one` answer-identity. Needs a witness whose skipped verify changes an answer (REACH) |
| F-2 | the accessor ignores the `when` list | the `utf8` + default control: `byte-rate=none` expected, and a witness pattern whose C1 pick moves if the default leaks into `utf8` |
| F-3 | the digest covers provenance | the provenance-edit fixture: editing `retrieved` must move no artifact byte |
| F-4 | self-`include` resolves from S1 rather than the next stop | the self-shadow fixture: the stamp must name the shipped `log`'s digest, and the compile must not loop (watchdog-wrapped) |
| F-5 | `run-rarity` reads `P(first)` from another block along the chain | the cross-source fixture (user `freq` + `include <weblog>`): the digest must equal weblog's bigram digest and the ranking weblog's alone |
| F-6 | normalization: residue to the wrong entry / zero floor | §2.5 vectors + the sum/floor assertion |
| F-7 | shard merge without the seam overlap | §11.8 shard-merge equality |
| F-8 | `--analysis` replacement without the note | the CLI fixture's stderr expectation |
| F-9 | the consumption record is not reset per compile attempt | a fixture forcing the `[SEL-1]` ladder: its stamp must list only the final attempt's queries |
| F-10 | a reader reads a rate table directly (re-adds a private table) | the structural grep (§11.7) |
| F-11 | the chain terminal resolves `default` by name | the `-I` dir with a planted `default.rxt`: an unnamed compile must stay byte-identical |

Every row ships with `SAB_REACH`. A row with no reachable witness ships
declared `UNREACHED` with its reason, never silently.

### 11.3 Census: what moves (R35, R37; NAMED MANIFESTS, not counts; learnings §3)

| event | population | expected | form |
|---|---|---|---|
| B1, `-e byte`, default | corpus + bench patterns (bench read-only) | program region: **0 movers**; whole file: all (abi + stamp) | `tests/findings/manifests/b1_byte_movers.txt`, asserted EMPTY, with a REACH count of how many artifacts consumed `byte-rate` (so "0 movers" is not vacuous) |
| B1, `-e utf8`, default | same | movers = **exactly** the C4 (`prefix_k`) population; C1–C3 0 | `b1_utf8_prefixk.txt`, the named list, answer-identical |
| each shipped bundle vs default | same | per reader (via `RX_REQ_BYTE`, `RX_REQ_RUN`, `RX_DFA_PREFILTER_OFFSETS`, …) | `ship_<name>_movers.txt`. **Empty means not earned (R31)**. An empty population is reported as empty, never as "no hazard" (K59) |
| B4 (`bigram` + first reader) | that reader's population | the reader's own row decides | its row's manifest |

### 11.4 Value correctness (oracles for the NUMBERS)

- **§2.5 normalization vectors** (four tables). The DEFAULT normalizes to
  `default_ppm.tsv` exactly. This replaces `run_offset_skip.sh` §1's sum
  check.
- **`L(x)` vectors** (§2.6) against an independent python reference using
  exact rationals rather than floats.
- **`markov1` acceptance:** over RUNEST's four train/test splits and 14
  runs, the accessor's rank order must equal RUNEST's bigram scorer's,
  including `union < select < from` on `web_request`. This is the design's
  headline customer, reproduced through pcrec's own arithmetic.
- **`cpfreq` (R5):**
  - on an ASCII-only sample, `encode-utf8` gives exactly the `freq` view
    (MEASURED true for `web_request` by construction, §0.9);
  - a known Latin-1-text sample comes out `0xC3`-heavy under `encode-utf8`;
  - `encode-latin1` reports its drop count.

### 11.5 Resolution and surface fixtures (R7, R8, R12, R13, R18, R20)

1. S1 over S2 over S3.
2. `-I` order.
3. Self-shadow (F-4).
4. The non-self cycle error.
5. The depth limit.
6. Unknown name (the stops are listed).
7. A file found by name that does not define the bundle.
8. A duplicate name in S1.
9. A planted `default.rxt` (F-11).
10. Explicit `include <default>`.
11. **R8 fall-through:** user `bigram` only + `include <weblog>`. `byte-rate`
    must come from weblog and `run-rarity` from the user.
12. The CLI replacement note (F-8).
13. **R13:** the same invocation from two cwds with explicit paths gives
    identical bytes.
14. **R20:** a provenance edit moves nothing, and a one-row edit moves the
    stamp.
15. **R7:** a shipped bundle copied into `-I` gives an identical artifact.
16. `--pattern` + `-I` + `--analysis` (R12).
17. **R18:** `#section resolution`'s digest equals the compiled
    artifact's stamp. The comparison uses an INDEPENDENT python digest
    implementation (`tests/findings/digest_ref.py`), because two readings
    of one C function would share a source (learnings §3).
18. **Every embedded bundle** parses and normalizes: `--list-analysis
    <each name from --list-analyses>` exits 0.

### 11.6 Stamp checks

- `<P>_FINDINGS` is present in every artifact the corpus builds.
- It equals `rx_info.findings`.
- Its items appear in query order.
- `none` appears exactly when the resolution section says `none` for this
  `-e`.

### 11.7 Structural checks (R23, R39)

- No `PCREC_ENC_` comparison inside any function in `src/opt`/`src/gen`
  that calls a `pcrec_find_*`.
- No rate table outside `src/core/findings.c`.
- No table pointer in any `*Sel` struct.

These are grep checks, each with a sabotage row (F-10).

### 11.8 Analyzer checks

| check | method |
|---|---|
| determinism (R27c) | run twice, byte-compare |
| stdin ≡ file | same input both ways |
| shard/merge (F-7, D123-3a) | N = 1..7 shards, merged in every permutation for N ≤ 4 and in seeded shuffles above that. Each must equal the whole-file output byte for byte |
| python ≡ C (implement-then-replace) | the in-tree samples + seeded random byte strings (invalid UTF-8 included). Byte-identical output |
| `--check` | a positive case, and a one-byte-changed negative case |
| R26 | `--scan cpfreq` on invalid UTF-8 is a hard error; `freq` on the same input succeeds |
| R27a | analyzer output → `pcrec --list-analysis NAME -I <dir>` parses clean |

### 11.9 Witnesses (R36)

Each reader gets one constructed pattern + one named bundle under
`tests/findings/witness/` whose choice moves against the default. Each is
REACH-checked, so a witness that stops reaching its site turns red
([MECH-REACH]). C1–C4 are owed at B2. C6 is owed at B4.

---

## 12. Migration: implement-then-replace (today's gates → declared data)

| today | step | after | proof it did not move |
|---|---|---|---|
| hand table `byte_freq_ppm_tbl` in `prefix_k.c` | B1 | `src/findings/default.rxt`, authored, embedded, normalized by §2.5 | §0.7 arithmetic + §11.4 (default normalizes to the pinned dump) + §11.3 (0 `byte` movers) |
| three gate spellings (`bytekey` in `reqbyte.c`, `!= PCREC_ENC_BYTE` in `emit_dfa.c`, none in `prefix_k.c`) | B1 | ONE rule, "use what the data declares", plus the default's `serves byte-rate when byte` | §11.3 (`utf8` movers = exactly C4's manifest) + §11.7 grep |
| `config … analysis <list>` parsed and skipped (`rxt_source.c:2756`) | B0/B2 | `analysis <name>`, AT_MOST_ONE, resolved | B0 changes the row (no corpus user, MEASURED), and B2 wires resolution |
| file-level `freq <name>` row (no reader, no user) | B0 | a kind block inside `analysis <name>` | `--list-schema` diff; no `.rxt` in the tree carries it |
| `run_offset_skip.sh` §1 (sum of the C table) | B1 | `tests/findings/` normalization check over `default.rxt` | the same assertion over the new source; the old check is deleted in the same change, not left reading a deleted table |

Each replacement deletes the old form in the SAME change once the new form
proves identity. Two priors, or two gates, never coexist on main (the
general-mechanisms memory).

---

## 13. Build plan (ordered, lane-sized; each gated by a measurement, D77)

| step | scope | tier | gating measurement / acceptance | depends |
|---|---|---|---|---|
| **B0** format (`[DD-13b]` wave) | §3.1's schema rows: the `analysis` bundle opener + BUNDLE scope, DATA `encoding`/`serves`, the `row` key grammar, CONFIG `analysis` → AT_MOST_ONE TOKEN, `freq <name>` withdrawn, §0.10's provenance conditions (a conjunctive `required-if`). The `bigram`/`cpfreq` rows are NOT in B0 (R2). Parse + `--list-schema` only; nothing consumed. Spec: `rxt_format.md` | sonnet | `--list-schema` diff reviewed; parse fixtures for every new row incl. refusals; confirm the structure layer nests three levels; `tests/rxtsource` green | — |
| **B1** the accessor + default + gate move (**abi 32→33**) | `src/core/findings.c` (§2.5 normalization, S3-only chain `[default]`, `pcrec_find_byte_rate`/`set_mass`, the consumption record), `src/findings/default.rxt` + build-time embed, the four sites migrated (§6.3), prefix_k's cardinality fallback, `<P>_FINDINGS` + `rx_info.findings`, D94 ritual. Spec: `findings.md` (new), `match_api.md` §6, `tuning.md` §2.27 & neighbours, `limits.md` | **opus** | **(1)** `b1_byte_movers` EMPTY with a nonzero REACH count; **(2)** `b1_utf8_prefixk` manifest named and answer-identical; **(3)** the compile-time cost of parsing `default.rxt` per compile, measured against a minimal compile. Above noise, a pre-parsed table is generated FROM the same text at build time with an agreement check, not a second source. **(4)** codegen/registry/rxtsource suites (D94 addendum) | B0 |
| **B2** resolution + CLI + library | S1/S2 stops, the chain algorithm (§4.3), config `analysis` resolution, `--analysis`, `-I` with `--pattern`, `--list-analyses`/`--list-analysis`, the `pcrec_options` fields, §9's diagnostics, §11.5 fixtures, the FINDINGS axis + adversarial bundles (§11.1), witnesses C1–C4 (§11.9), sabotage F-2..F-6, F-8, F-9, F-11. Spec: `cli.md`, `table_contract.md`, `findings.md` | opus | all §11.5 fixtures; the sampled answer-identity slice green on every adversarial bundle; the full FINDINGS axis run once (owed/background, per BOILERPLATE); no default-path mover vs B1 | B1 |
| **B3** analyzer prototype | `scripts/pcrec_analyze.py` (from `ngram_count.py`): §10's CLI incl. shards/merge/check, the output format, §10.2's declarations | sonnet | §11.8 determinism/shard-merge/`--check`/R26/R27a; its output for RUNEST's `web_request` sample normalizes (through B1's function) to RUNEST's unigram | B2 (R27a needs `--list-analysis`) |
| **B5** first shipped bundle(s) + `cpfreq` | a sourcing pass for licensable, stably retrievable samples (§16 Q2); `third_party/<src>/` + `generate.py` via the analyzer; `src/findings/{log,weblog}.rxt` carrying `freq`+`cpfreq` (R5); the `cpfreq` schema row + `encode-utf8`/`encode-latin1` derivations; §11.4 cpfreq checks | sonnet (sourcing) + sonnet (build) | **R35 census** `ship_<name>_movers`: a bundle whose byte-rate census is EMPTY does not ship yet (R31). `log`'s predicted mover is C4's iso-ts (OKS C2). If `weblog`'s byte census is empty, it waits for B4 | B3 |
| **B4** `bigram` + `run-rarity` + its first reader | the `bigram` schema row, `markov1` (§2.6, `L(x)`), `pcrec_find_run_rarity`, bigram blocks regenerated into the shipped bundles, and **in the same change** the first reader: S4(a)'s run pick (C6) if its row is ready, otherwise whichever of C2-window / C3-widening has a measured trigger first. Witness C6, sabotage F-5 | opus | §11.4 markov1 acceptance (RUNEST rank equality + the WAF sign); the reader's own row's measured bench cell with `analysis weblog` (R38: names the analysis; disjoint subject, R30) | B5, and the reader's own row |
| **B6** analyzer in C (end state) | `analyze/` → `build/pcrec-analyze`; generators switch to it; python ≡ C agreement; then the python prototype is DELETED | sonnet | §11.8 python ≡ C on in-tree samples + seeded random input; `make gen-tables` byte-identical before/after the switch | B3 (can run in parallel with B4/B5) |

- **After B6:** the D123-2 round-trip helper script (reading
  `--list-analysis` sections, writing an includable bundle) is a separate
  small row.
- **Default regeneration** from a corpus is its own row (D123-5), measured
  against RUNEST's data and B5's shipped bundles. It is never folded into
  any step above.

---

## 14. Spec hunks owed (D80), by step

| spec document | hunk | step |
|---|---|---|
| `docs/spec/rxt_format.md` | head table: the `analysis <name>` bundle opener replaces file-level `freq <name>`; a new "`analysis` — the bundle" section (BUNDLE scope, `include <name>` in the SEARCH spelling, include_next, AT_MOST_ONE per kind); the DATA section rewritten (`encoding`, `serves`, `row` key grammar per kind, rows ascending); CONFIG `analysis` becomes "names ONE analysis (a bundle)" (D123's consequence text); provenance's data-parent conditions (§0.10). Also REQ §4's two noted spec drifts: `lib` contents being read since W1.3, and `provenance`'s `required` flag | B0 (format), B2 (resolution semantics) |
| **`docs/spec/findings.md` (NEW)** | the contract: terms (§2.1); kinds and key grammars; the closed query/derivation/encoding vocabularies; §2.5 normalization with test vectors; §2.6 `markov1` + the `L(x)` algorithm and vectors; resolution stops + chain algorithm + include_next + terminal; per-reader NONE fallbacks (§6.2); stamp grammar + digest byte layout; the analyzer's CLI, one-pass table, merge rules, declaration defaults and disclosure table | B1 (core), B2 (resolution), B3/B6 (analyzer), B4 (`markov1`), B5 (`cpfreq`) |
| `docs/spec/cli.md` | `--analysis`; `-I`/`--lib-path` legal with `--pattern`; §2 "Listing surfaces" count EIGHT → TEN with `--list-analyses`/`--list-analysis`; §3 the two notes and the new hard errors | B2 |
| `docs/spec/table_contract.md` | two rows in the Scope table | B2 |
| `docs/spec/match_api.md` | §6 `rx_info.findings`; the §6.3 observability macro `<P>_FINDINGS`; the §6 abi change-log line 32 → 33 | B1 |
| `docs/spec/tuning.md` | §2.27 and the `[OPT-REQPOS]`/G1/offset-k paragraphs: "the prior is read only under `byte`" becomes "the rates are whatever the resolved analysis declares; the default declares `byte` only"; offset-k's cardinality NONE fallback | B1 |
| `docs/spec/limits.md` | rows for `PCREC_MAX_FIND_{CHAIN,BUNDLE_BYTES,STORE_BYTES,COUNT,CPFREQ_ROWS,RUN}` and `PCREC_FIND_FLOOR_PPM` (§8.3) | B1/B2 |
| `lib/pcrec.h` contract comment | the `pcrec_options` fields (§5.3) | B2 |

---

## 15. Requirements disposition (R1–R41)

✓ = honoured as written. **CHANGED** = changed, with the reason given.

| R | status | where / why |
|---|---|---|
| R1 open set | ✓ | a kind = one schema row + one derivation entry + an accessor path. Resolution, merge and stamp never change (§2.2, §2.4) |
| R2 membership | ✓ | `cpfreq` lands with B5's shipped bundle (existing byte-rate readers), `bigram` with B4's reader. Every `serves` query has a `src/` reader (the §11.7 grep) |
| R3 integer | ✓ | §2.5, §2.6, integer `L(x)` |
| R4 row shape | ✓ decided | keyed hex rows of counts (§2.3) |
| R5 cpfreq | ✓ | `encode-utf8`/`encode-latin1` (§2.4), §11.4 |
| R6 run kind by measurement | ✓ | RUNEST → `bigram` + `markov1` |
| R7 four sources, one shape | ✓ strengthened | one READER too (text-embedded store, §0.11) |
| R8 resolution unit (name, kind) | ✓ | per-kind along the chain (§4.4), sharpened to per-QUERY from one block (§0.3) |
| R9 no blending | ✓ strengthened | one query, one block, and derivations never read two blocks |
| R10 precedence | **CHANGED** by D123 | there is no config list. Chain order is the bundle's own `include`. The CLI replaces the one name, with a note |
| R11 per target | ✓ | configs per target |
| R12 `--pattern` | ✓ | `-I` + `--analysis` (§0.2) |
| R13 no ambient state | ✓ | §4.1 |
| R14 in-tree source of truth | ✓ | `src/findings/*.rxt` |
| R15 two flags | **CHANGED** | one naming flag. A FILE is reached through `-I` + name = file, so `-I` stays the only path concept (§4.2). §16 Q3 asks about path sugar |
| R16 `.rxt` | ✓ | config resolves; block scope DECLINED with its reason (§3.2) |
| R17 library | ✓ | three fields; the library parses (§5.3) |
| R18 introspection | ✓ | `#section resolution` + the stamp |
| R19 deterministic | ✓ | equal consumed values give an equal digest, so an identical artifact |
| R20 stamp over values | ✓ | §7 |
| R21 one abi event | ✓ | 32 → 33 carries the stamp, the field and the gate move |
| R22 data change visible | ✓ | the digest in the stamp (§7) |
| R23 gate in accessor | ✓ | §6.3, §11.7 |
| R24 NONE explicit | ✓ | per-reader fallbacks (§6.2). C4's fallback is cardinality, deliberately and censused (§0.8) |
| R25 encoding key | **CHANGED** by D123-4 | `encoding` DESCRIBES the data. Applicability is the separate, operative `serves … when` line |
| R26 invalid bytes | ✓ | `freq` from anything; `cpfreq` refused on undecodable input |
| R27a outside | ✓ | a separate binary |
| R27b one counter | ✓ | counting in the analyzer only, normalization in the compiler only |
| R27c deterministic, pattern-blind | ✓ | no clock (`--retrieved` flag), no pattern argument |
| R27d only writer | **CHANGED** by D123-4 ("user visible and editable") | SHIPPED generated bundles are analyzer-only (`--check` makes a hand edit red). USER bundles are editable by design. `default` is `authored` |
| R28 third_party shape | ✓ | §8.1 |
| R29 licence | ✓ | §8.1, §16 Q2 |
| R30 bench independence | ✓ | PROVENANCE review + a grep for bench paths in findings PROVENANCE. RUNEST's bench use was evaluation-only |
| R31 earned | ✓ | an empty census does not ship (B5) |
| R32 limits | ✓ | §8.3 |
| R33 footprint | ✓ | sparse counts; ≈55–75 KB total (§8.3) |
| R33a wording | ✓ | §9 |
| R34 answer identity | ✓ | §11.1 |
| R35 census | ✓ | §11.3, named manifests |
| R36 witnesses | ✓ | §11.9 |
| R37 gate control | **CHANGED** by D122-2(3) | "zero movers under `utf8`" becomes "zero movers except the named C4 manifest" |
| R38 perf claims name the analysis | ✓ | B4's acceptance |
| R39–R41 rows | ✓ | §6.1, §11.1, §11.7 |

---

## 16. Open questions for Frank

1. **The chain's implicit terminal is the BUILT-IN `default`, by identity,
   not by name (§0.6).** A user changes "the default" only by naming their
   own bundle. The alternative, resolving `default` by name so a `-I` dir
   can shadow it globally, is more "editable" but lets a directory added
   for `lib` silently move every artifact. **Rec: by identity**, as
   designed.
2. **`log`'s licensable source (§0.9).** RUNEST's HDFS sample cannot be
   redistributed. Options:
   - (a) a sourcing lane looks for a permissively licensed, stably
     retrievable real log corpus (pinned commit / DOI);
   - (b) a `fidelity synthesized` generator, labelled as such (D123-6
     allows it only where nothing is licensable);
   - (c) ship `weblog` alone first.

   **Rec: (a), with (b) as its declared fallback.** `weblog`'s source
   (elastic/examples, Apache-2.0) needs only re-pinning to a commit.
3. **Path sugar for `--analysis`?** `--analysis ./dir/x.rxt` would mean
   `-I ./dir --analysis x`. It is convenient, but it is a second spelling,
   and it would decide by the value's SHAPE whether a name or a path was
   meant. **Rec: no**; revisit on a user ask.

(Deliberately NOT asked, because the design decides them with reasons:
Route I (§4.2); text embedding (§0.11); the `rx_info` mirror (§7, D43);
cardinality as C4's NONE fallback (§0.8, D122-2(3) accepted the movement);
no block-scope `analysis` (§3.2). The critique loop may reopen any of
them.)

---

## 17. Not built (D77), each with the measurement that would build it

| item | trigger |
|---|---|
| `trigram` kind / `markov2` | RUNEST §0.3: a repeat of the estimator measurement on a ≥10× larger licensable exemplar per class shows trigram's ranking edge survives, with no sign inversion |
| top-K token table | a customer run that IS a word and a measured bigram mis-rank on it (RUNEST §0.4: 3 of 14 runs are word-shaped). It also needs a privacy statement (§10.5) and is not one-pass (§10.3) |
| gap / burstiness, set-membership run length | C5's "restarts pay" arm or C7 (conditional on the plainloop twin, REQ C7) landing with a measured cell |
| line-length / chunk statistics (D83 (1)) | any customer (REQ: none) |
| selective include (`kinds=`) | D123-3: its own effort. The extension point is §3.3 |
| `rows <name>` block reference | a user ask to change a block's declarations without copying it (§3.3) |
| `independence` derivation (`freq` → `run-rarity`) | none: RUNEST measured it wrong-signed (ρ ≈ 0 on web). Listed so its absence is on purpose |
| C2 window choice / C3 widening on `run-rarity` | their own rows' measured cells (B2R §6, I-103) |
| pattern-specific findings | D83 (2): a separate shape and a separate build |
| the round-trip helper script | after B6 (D123-2) |
| default regeneration from a corpus | its own row (D123-5) |
