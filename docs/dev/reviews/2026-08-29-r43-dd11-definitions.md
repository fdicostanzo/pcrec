# r43 — D6 panel on the [DD-11] design note (docs/design/definitions_table.md @ lane/dd11 86d8725)

Forty-fifth session, 2026-08-29 ~14:3x-15:xx EDT. Three read-only sonnet
critics with distinct lenses: r43-census (inventory + core set, file:line
truth), r43-sem (PCRE2 semantics vs libpcre2; the self-oracle), r43-checks
(placement, the predicate's representation, the checks). Critics ran only
the prebuilt build/pcrec, python3 and their own libpcre2 probes; no `make`.
Dispositions are the manager's; Frank's rulings are marked.

## Frank's ruling folded in before the panel returned (14:4x)

**The class escapes ARE rows.** Frank: "are we including `\d -> [0-9]`,
etc?" — the note had excluded `\w \d \s` as "already collapsed
(cls_bits.inc)". Ruled IN: the class-escape family (`\d \D \s \S \w \W \h
\H \v \V \N \R`, POSIX classes) are definition rows — today's byte
definitions with predicate `always`, the UTF/UCP predicate as their second
row when it exists; `\R` is `(?>\r\n|\n|\x0b|\f|\r|\x85)`, an atomic
alternation, a genuine replacement the note also missed; the bitmap should
be DERIVED from the definition string (one derivation), with PC-4's
libpcre2 re-measurement as the independent control. Plan row addendum (f)
already asked for "primitive vs binding, each binding's value measured".

**And the literal escapes (Frank, 14:5x: "there is also stuff like `\a`").**
The single-character escapes are bindings of the same kind: `\a` → `\x07`,
`\e` → `\x1b`, `\f \n \r \t`, `\0`, octal `\ddd`, `\xhh` / `\x{…}`,
`\cX`, `\N{U+…}`, and `\Q…\E` quoting — each a construct standing for a
literal byte. Under `--encoding=utf8` a code point above 0x7f stands for a
byte SEQUENCE, so the encoding is their predicate and they are a two-row
family from the day UTF lands ([DD-12]/[M5]) — D85's shape, not a special
case. Ruled IN as rows with today's byte definitions.

## r43-census (inventory / core set)

| # | sev | finding | disposition |
|---|---|---|---|
| C1 | BLOCKER | `(?n)` (no-auto-capture) is a fifth SHIPPED, WIRED replacement missing from §1: `parse.c:832` (`!cx->mods->nocap`), row `registry.c:958`, field `mod_modifiers.c:422/429`; live: `(?n)(a)(b)` compiles byte-identically to `(?:a)(?:b)` — under D85's test, `(...)` scoped by `(?n)` IS `(?:...)`. | FIX: add the row (predicate `nocap`, definition `(?:…)` — a builder, it has an operand), recount. |
| C2 | MAJOR | citation drift: `mod_assertions.c:444` does not exist (file is 214 lines); the fact is at `mod_assertions.c:175`; `src/parse/CLAUDE.md:444` is the likely mix-up. | FIX the citation. |
| C3 | MAJOR | "decisions.md line ~1238" for `(?=\n)\|\z` is D24 text; D62 is at ~4978 and the definition is the note's paraphrase, not a quote. | FIX: retarget, label as paraphrase. |
| C4 | MEDIUM | §2's optimizer-pass census undercounts sites keyed on node/NFA kinds a full reduction would remove: `altcls.c:381-387,488`; `revdet.c` (~10 sites); `select_engine.c:231-232,254,256,508`; `prefix_k.c:195-202` (a no-default switch listing N_BOT_M/N_EOL_M/N_WORDB/N_NWORDB as "every assertion"). None read `.multiline`, so [DD-11.1]-.4 are unaffected. | FIX: scope §2's claim explicitly (field-reads vs kind-keyed sites) and list the kind-keyed sites as [DD-11.5]'s customers. |
| C5 | MINOR | `(?U)`/ungreedy (`parse.c:1112/1114`) is an option-scoped construction parameter absent from the table and the exclusion paragraph. | FIX: add as parameter-excluded, stated. |
| C6 | NIT | "8 primitives" labels parameters as primitives; 5 primitive + 3 parameter + 1 generation axis. | FIX wording. |

Verified and held: parse.c:899/901/880-890/1141-1160; mod_assertions.c:75/76;
nfa.c:538-539; registry.c:1185-1205; internal.h:2224/2331/2474-2517;
emit_dfa.c:1991-1998; dfa.c:147 (±2); possessify.c:308 reads `.multiline`;
`(?m)$ ≡ (?=\n)|\z` at "x\n" positions 0/1/2 (F/T/T, python `(?m)$`);
`\R`/newline verbs unbuilt (mod_verbs.c:175-180, registry.c:618).

## r43-sem (PCRE2 semantics vs libpcre2 10.46 via ctypes; the self-oracle)

| # | sev | finding | disposition |
|---|---|---|---|
| S1 | MAJOR | §3 item 3 names only the D66 `A==B` self-oracle; its own source, lookaround_design.md §6.3, RULES that A==B alone is satisfiable by a consistently-wrong compiler — libpcre2 (A==C) is co-equal. §6/[DD-11.3] says it; §3 does not. | FIX: §3 item 3 states both legs inline, citing §6.3. |
| S2 | MAJOR | What A==B structurally cannot see: a bug in a substrate both sides share through pcrec's front end — `\w`'s byte table (cls_bits.inc), `\n`'s value, the VM's generic lookaround sub-program. | Same fix as S1; it is the concrete instance. (Frank's class-escape ruling makes cls_bits.inc a DERIVED artifact checked by PC-4 — the third leg.) |
| S3 | MAJOR | The DFA-erasure safety net is a per-call-site DISCIPLINE: `a->reg` (read by `forces_registry`, select_engine.c:229,304, to exclude the DFA) is set only by an explicit `pcrec_ast_stamp` (parse.c:57, D67; the possessive builder calls it at parse.c:1152). A table-driven builder for a lookaround-shaped definition that omits it, or stamps the wrong row, lets the DFA run `A_LOOK`→`N_EPS` (nfa.c:621) AS THE ANSWER — a silent miscompile, not §4's perf-only story. Confirms the hazard is DFA-only (the VM's lowering never takes the erasure). | FIX: [DD-11.5]'s gate gains "`pcrec_ast_stamp` with the correct row" as a precondition + a sabotage row (an unstamped/bypassed build; SR-8 must still catch it). Name it in §4. |
| S4 | MEDIUM | §3 item 4 "untestable today" is over-pessimistic: plant a SYNTHETIC second `\w`-shaped row behind a never-true feature flag (item 2's own "swap the definition" shape) and exercise the resolver's context-sensitivity now. | FIX: [DD-11.4] un-parked from Unicode; the synthetic row is its test. (Frank's class-escape ruling makes `\w` a real row anyway.) |
| S5 | MINOR | §3 item 1's core-set allowlist is hand-authored from §2's prose; nothing pins it to `AKind` as it grows. | FIX: express it as an exhaustive no-default switch over `AKind` (mrl.c's rule). |

Could NOT refute (libpcre2 direct, no python): `(?m)^ ≡ \A|(?<=\n)(?!\z)`,
`(?m)$ ≡ (?=\n)|\z` (`\z`, not `\Z`), `\Z ≡ (?=\n?\z)`, `\b`/`\B` ≡ their
lookaround forms — 0 disagreements at every zero-width position over 6-8
subjects each incl. `""`/`"\n"`/`"\n\n"`; the vacuity control (dropping
`(?!\z)`) diverged on 4-6 cells, so the checks are falsifiable. The full
possessive family incl. capture-carrying bodies, numbering, zero-iteration
captures and backreference interaction: 0 disagreements over ~90 cells vs
`(?>…)`. nfa.c:538-539/:621 and D62/D66/D67/D85 citations exact.

## r43-checks (placement, the predicate's representation, the checks)

| # | sev | finding | disposition |
|---|---|---|---|
| K1 | BLOCKER | The "type hazard" is technically wrong: `ParseMods` is forward-declared at internal.h:27, internal.h never includes parse_mods.h, and `Ctx.mods` (internal.h:1472) is already a pointer-to-incomplete field — `bool (*)(const ParseMods *)` compiles everywhere. `Ctx *` may still be right (ExtPortFn parity, internal.h:2192; [LIB]'s non-mods predicate) but not for the stated reason. | FIX the argument; see the ruling below (predicate as a TAG). |
| K2 | BLOCKER | The real gap: any stored callable in RegRow is callable from src/opt, src/gen, cli given a `Ctx *` — the deref lives in the callee. ExtPortFn's ports are today called only from src/parse by CONVENTION. parse_mods.h wants "physically cannot compile"; a stored predicate downgrades it to convention — possessify.c's D62/wave-A defect shape. | FIX: containment check on assertions_design.md §8.4's grep precedent — predicate/builder evaluation sites appear only in the resolver and the dump. Subsumed by the TAG ruling (one exhaustive-switch evaluator in src/parse is the only deref site by construction; the grep check pins it). |
| K3 | BLOCKER | §5 check (a) ("fn ptr reachable ONLY through the dump and the producer") is not a buildable C check. | FIX: replace with K2's grep check. |
| K4 | BLOCKER | §5's predicate-swap sabotage is NOT detected by the structural check (it parses definition strings; nothing evaluates predicates before [DD-11.5]). | FIX: [DD-11.3]'s self-oracle iterates the OPTION MATRIX (multiline on/off, nocap on/off, …), selecting the definition through the real predicate and comparing to the shipped lowering under that option — a never-firing predicate then shows as identity-vs-multiline mismatch. That row is detected THERE; say so, and mark what remains undetectable until [DD-11.5]. |
| K5 | MAJOR | `family` is NULL on 90/128 rows (38 non-null; `--list-syntax` field 17; registry.md §5), not 116/128. | FIX the number; the sparsity argument survives. |
| K6 | MAJOR | §7 Q3: the wrong precedent. `--list-definitions` walks the same RegRows `--list-syntax` prints and RegRow carries a per-row `flavours` mask; an unfiltered dump would print a definition `--list-syntax --flavour=X` says does not exist. | RULED (manager): YES, `--flavour`, filtered identically to `--list-syntax`. Flagged to Frank. |
| K7 | MAJOR | `builtin` column is zero-information (every printed row reads "no"); violates the "no dead accessor" rule the note cites. | FIX: drop it. |
| K8 | MAJOR | §3 never confronts D82 rule 4 (≥2 real forms) for the unconditional rows (`\b`, possessive; now the class-escape and literal-escape families too). | RULED (manager): D82 rule 4 governs EMITTER axes (candidate representations). D85's table is a different object — Frank ruled "the last row always applies (the identity)" and "the core rx set is what remains after replacement": a binding IS a row even with one entry because the LISTING is the point (expose the process; the core set is DEFINED by the table's complement), and most one-row families have their second row chartered (UTF/UCP for `\d\w\s`, encoding for `\x{}`, newline convention for `\N`/`$`). State this argument in §3 explicitly; the "one-entry list is not a boolean" sentence is not it. |
| K9 | MINOR | Predicate-as-data ({mask,value} over ParseMods) cannot express [LIB]'s "name is bound" or D64's newline convention, and a raw offset is LESS contained than a fn (evaluable from any TU). | Accepted; it motivates the TAG ruling below. |
| K10 | MINOR | The spec hunk should name table_contract.md conformance (resolve-by-name, ignore trailing columns) explicitly. | FIX. |
| K11 | NIT | "~4-6 rows" undercounts: the possessive family is 4 RegRows (registry.c:1185-1192) + `\b` `\B` `(?m)^` `(?m)$` = 8 before the panel; more after C1 and Frank's two families. | FIX the count from the revised census. |

Could NOT refute: Option A over B (D24's "five places" quote accurate; sparsity holds after K5); ExtPortFn's `Ctx *` signature (internal.h:2192).

## The manager's ruling on the predicate's representation (K1/K2/K3/K9 + the prose-drift question the panel was asked)

The note's `bool (*)(const Ctx *)` beside a HAND-AUTHORED English
`predicate` column is two derivations of one fact (learnings §3), and
K2 shows a stored callable also weakens D62's containment. Predicate-as-
data over ParseMods (K9) cannot express the named future customers.
**The predicate is a TAG from a closed enum** — `DEF_ALWAYS`,
`DEF_MULTILINE`, `DEF_NOCAP`, `DEF_UCP`, `DEF_ENCODING_UTF8`,
`DEF_NEWLINE_CONV(x)`, `DEF_LIB_NAME_BOUND` — with ONE evaluator in
src/parse (an exhaustive no-default `switch`, mrl.c's rule: a new tag
without an arm fails to compile) and a name table the dump prints. One
derivation: the row holds the tag; the parser evaluates it through the
single switch (the only deref site — containment by construction, pinned
by K2's grep check); `--list-definitions` prints the tag's name, never
prose. The definition stays `{kind, str | builder}` per the note (Q1).

## Frank's §7 questions — manager rulings, flagged for override

- Q1 string vs builder: KEEP the split (bodyless rows are strings and the
  string IS the probe pattern; operand-taking rows — possessive, `(?n)`'s
  `(?:…)`, [LIB] splices — are builders).
- Q2: CLOSE [DD-11] after [DD-11.1]-[DD-11.4]; charter [DD-11.5]/[DD-11.6]
  as a follow-on row (name at charter) opened when M6.6 lands, with S3's
  precondition on it. [DD-11.4] is un-parked (S4: a synthetic row tests
  the resolver now).
- Q3: `--flavour` YES (K6).

## Triage summary

BLOCKERS 5 (C1, K1-K4), MAJOR 9, MEDIUM 2, MINOR 4, NIT 2 — all FIX or
RULED; no finding refutes the note's equivalences, its Option A
placement, or its [DD-11.1]-[DD-11.4]/[DD-11.5] split. One revision
round to lane dd11 carries: Frank's two families (class escapes, literal
escapes) + `(?n)` + `(?U)` into the census; the TAG ruling; the
[DD-11.3] option-matrix self-oracle with libpcre2 as the co-equal leg;
S3's `pcrec_ast_stamp` precondition; K2's containment check; the
corrected citations, numbers and columns. Re-check by the manager, not a
second panel, unless the census changes shape again.
