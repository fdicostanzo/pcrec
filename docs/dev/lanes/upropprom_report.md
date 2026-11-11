# upropprom report: promotion of the D27 blinded `\p` corpus

## STATE AT HANDOFF

STATE: delivered; the cloud run (`cloudrun --kind test --name upropprom`) is the owed full-suite verdict.

Corpus: `tests/uprops/d27/` (16 `.rxt`, 520 blocks, 12,935 case lines incl. `g` lines; authorship and the one promotion edit, a `# pcre2-only` line per block, in its CLAUDE.md). Checker: `tests/uprops/d27/d27_check.py`, wired as `make test-uprops` §8 with a planted-wrong-expectation control per arm (both caught).

### Verification counts, per oracle

| oracle | scope | result |
|---|---|---|
| pcrec itself (`tests/harness/run.sh tests/uprops/d27`) | all | 12,935 cases passed, 0 failed |
| UCD 16.0.0 FILES (`d27_check.py ucd`; PropList, DerivedCoreProperties, emoji-data, DerivedAge, Blocks, DerivedBidiClass + `@missing`, UnicodeData) | 370 blocks / 11,246 single-code-point cases (incl. 96 of the 101 Age/Block blocks) | 0 disagreements |
| libpcre2 10.46 (`d27_check.py pcre2`, p2probe) | 410 blocks agree (11,336 cases, spans and groups); 9 `perr` blocks libpcre2 accepts; 101 blocks (33 Age, 68 Block) have no oracle (libpcre2 error 147) | 0 disagreements |

Not independently covered by either arm: 150 blocks the UCD arm does not evaluate (classes, quantified, runs, `-i`, refusals; all but the Age/Block ones are libpcre2-covered) and 5 Age/Block blocks (byte-encoding and class forms); pcrec's own whole-space Block/Age check (`tests/uprops` §6) covers those sets.

### Findings

| # | finding | classification | disposition |
|---|---|---|---|
| 1 | Age of U+FDD0, U+FFFF, U+10FFFF (author changed them after seeing pcrec's answer) | author's FINAL values are right: DerivedAge.txt has `FDD0..FDEF ; 3.1`, `FFFE..FFFF ; 1.1`, `10FFFE..10FFFF ; 2.0`; the sets are Age=3.1, 1.1, 2.0 (not NA). libpcre2 has no Age (error 147), so DerivedAge is the only arbiter | none; ucd arm checks them (age.rxt) |
| 2 | 9 `perr` blocks (byte encoding, no `unicode-props` feature, e.g. `\p{Emoji}`) are accepted by libpcre2 | not a bug: pcrec's module gate (`\p requires module 'unicode-props'`, the documented capability refusal; cli.md §1.7¶3) | none; listed by the checker |
| 3 | refused names (`\p{Foo}`, `\p{Hyphen}`, `\p{gc=Lu}`, `\p{Age=99.0}`, long Bidi values) say "this Unicode property is not implemented yet" | wording tier (D26): behaviour is right (compile fails; libpcre2 refuses the same names). The wording can read as "coming later" for names deliberately refused; no `requires module` text applies because the module IS enabled | no change (D26: do not gold-plate wording); recorded here |
| 4 | `\p{}` / `\p{^}` say "not a one-letter Unicode property code" | wording tier (D26) | no change |
| 5 | loose matching of binary and Block/Age names accepted, spec stated it only for scripts | spec gap, behaviour correct: libpcre2 10.46 loosely matches every property name (checked: `emoji-presentation`, `White Space`, `WhiteSpace`); Block/Age loose matching is the extension following the same rule | spec hunk: docs/spec/cli.md §1.17.1¶2 and ¶5 |
| 6 | the "55" binary properties were not listed | spec gap | spec hunk: cli.md §1.17.1¶1 now names all 55 (list derived by compiling each PropertyAliases.txt binary long name in libpcre2: 55 of 73 accepted; plus `ASCII`) |
| 7 | the author's lowest-confidence claims (Pattern_Syntax gaps, Deprecated E0001, IDS ops, XID_Start exclusions, Soft_Dotted, LOE, Emoji_Component edges, Age examples) | all confirmed by the ucd/libpcre2 arms | none |

No pcrec bug, no author error that survived to the promoted files.

### Wiring and pins

`d27/` rides `test-corpus` (recursive) and `test-uprops` §8. `test-rxtsource` re-pinned by its own found values: CENSUS 336/7032/98198, RUNSH 312/7032/98198, C3_SKIP 75141, C3_SKIP_PCRE2ONLY 34885 (PASS and VERIFIABLE unchanged); passes (300 checks). Local sections run: see the last lines of this report for results.

### OWED
Full `make test` in the cloud (`cloudrun --owner main --kind test --name upropprom`); startset manifests, axes allowances and size tripwire are the sections that could move beyond rxtsource.
