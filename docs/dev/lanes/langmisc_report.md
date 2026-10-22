# langmisc: pattern_language.md vs the cell's build/pcrec (D27 blinded adversary)

Target: `docs/spec/pattern_language.md` in `worktrees/langmisc-cell`. Oracle: libpcre2-8 10.46 (system), at the option map of §1.2
(`-e utf8` = `PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`). Every probe compiled with `build/pcrec` (`--features all` unless the
probe is about the gate), linked with my own driver (`drv.c`, `rx_search`, all groups printed), `gcc -O1`, and compared
span-and-every-group with `p2probe.c`.

## Counts

| set | probes (pattern x options) | what |
|---|---|---|
| probes_base | 287 | braces, escapes, classes, quantifiers, preference, anchors x startpos, dot |
| probes_uni | 398 | ill-formed UTF-8 (subject and pattern), code-point boundaries, byte/utf8 folding, UCP byte+utf8, `\p` names, `\h\v` |
| probes_mods | 550 | extended mode, option letters, backref digit rule, lookaround, atomic, named groups, quoting, recursion, verbs |
| probes_lb | 135 | lookbehind body shapes, octal above `\377` under utf8, `\p` loose matching |
| probes_misc | 135 | startpos (incl. mid-character), NUL bytes, nesting 249-251, `-i` + inline, recursion inside lookbehind |
| probes_last / min1 | 108 | `\K`, `(?n)`+numbers, `(?J)`+calls, `(?U)`/`(?^)`, option-only groups, minimisation |
| probes_fuzz / fuzz2 | 1,100 | random grammar over {a,b,c,B,\n} (byte) and {é, k, U+212A, ß, ſ, ...} (utf8, 40% `-i`) |
| probes_engine | 2,042 | every accepted probe above replayed under `--engine=vm` and `--engine=dfa --no-captures` |
| shell gate probes | ~150 | `--features none/std1/lists`, `-i`/`--ucp` gating, `${`, §4.5 engine claims |

Total about 4,900 probes and 113,183 subject runs. Verdicts: AGREE 3,990; both refuse 230; pcrec-only refusals 390 (almost all
documented: §8.1 not-built constructs, shape 4/5 refusals, wide UCP sets); pcrec-only accepts 3; DIFF 83 and give-up
mismatches 57 (almost all libpcre2's recursion-loop error -52 against a pcrec answer, see F7); 2 timeouts (both honest
`PCREC_ERR_STEPS` after 6-66 s; not a language finding).

## Findings, by severity

| # | class | doc | probe | pcrec | libpcre2 |
|---|---|---|---|---|---|
| F1 | **BINARY-WRONG (wrong answer)** | §4.2¶3, §6.2 `U` row, §5.6 possessive row | `(?U)a*+` on `aaa`; `(?U)a{2,3}+` on `aaa`; `a(?U)\s{,2}+` on `a\nb`; `(?U)(a\|b)*+` on `ab`; `(?U)\s*+b` on `a\nb` | `[0,0)`; `[0,2)`; `[0,1)`; `[0,0)` g1 unset; `[2,3)` | `[0,3)`; `[0,3)`; `[0,2)`; `[0,1)` g1 `[0,1)`; `[1,3)` |
| F2 | **BINARY-WRONG (internal error on accepted syntax)** | §7.4¶5 (fixed-length alternatives compile) | `(?<=(?:ab\|cd))x`, `(?<=(?:a{2}\|b))x`, `(?<=(?:a\|b\|cd))x`, `(?<=(?:(a)\|(b)))x`, `(?<=(?i:a\|bc))x`, `(*plb:(?:a\|bc))x`, `(?<!(?:a\|bc))x`, `(?<=(?:a\|bc)\|d)x` | `internal error: a lookbehind body's alternation spine is longer than its reported branch count` (all engines) | accepts; e.g. `(?<=(?:ab\|cd))x` on `cdx` → `[2,3)` |
| F3 | BINARY-WRONG (refuses accepted syntax as grammar) | §5.6¶2 (`(^)*`, `(?:$)?` are quantifiable groups), §1.3¶2 | `(?:(?i))*a`, `((?s))?a`, `(?=(?m))+a`, `(?:(?-i)){2}a`, `(?:(?i)){0}a` | `quantifier does not follow a repeatable item` (shape 7). `(?:(?i)(?s))*a` and `(?:)*a` are accepted | accepts all |
| F4 | BINARY-WRONG (refuses accepted syntax) | §5.5¶5 ("a value above `\377` under byte is refused", so accepted under utf8), §5.2 | `-e utf8`: `\400`, `\777`, `[\400]`, `[\400-\777]`, `(a)\400`, `\400+` | `octal value is greater than \377 in 8-bit non-UTF-8 mode` (the byte-mode diagnostic) | U+0100 / U+01FF; `\400` on `Ā` → `[0,2)` |
| F5 | BINARY-WRONG (gate leak) / or DOC-WRONG | §6.2¶4 (`-i` is `(?i)` at pattern start), §2.3¶5 (`(?i)` refused under `none`) | `-i --features none --pattern ab` | accepted, and folds (`AB` → `[0,2)`); `(?i)ab` under `none` is refused naming `modifiers` | n/a |
| F6 | BINARY-WRONG (accepts what PCRE2 refuses) / DOC-SILENT | §1.3¶2, §7.4¶5, §7.7 | `(?<=(?R))x`, `x(?<=(?R))` | accepted; no match everywhere (`x(?<=(?R))` gives `PCREC_ERR_FRAMES` on 3 subjects) | `length of lookbehind assertion is not limited` |
| F7 | DOC-SILENT (§9) | §9¶3-¶4 list only "(?R) alone" and the give-up direction | `(?:a\|(?R))+` on `a`, `aa`; `((?1)?a)`-family; 15 fuzz patterns | answers a match (`[0,1)`, `[0,2)`) or no match | `PCRE2_ERROR_RECURSELOOP` (-52) |
| F8 | DOC-WRONG/BINARY-WRONG (refusal shape) | §2.4 shape 2 = "enabled and has no producer for this construct" (a real construct); shape 7 = "PCRE2 refuses it too" | `\p{Foo}`, `\p{InGreek}`, `\p{gc=L}`, `\p{Hrkt}`, `\p{Katakana_Or_Hiragana}`, `\c` at end, `[\c]`, `\N{U+41}` under byte | shape 2: `module '...' is enabled but ... is not implemented yet` | grammar errors (unknown property; `\c at end of pattern`; `\N{U+dddd} is supported only in UTF mode`) |
| F9 | BINARY-WRONG (loose matching) | cli.md §1.17.1¶2 (names "loosely matched"), referenced by §7.9¶1 | `\p{ ^Greek}`, `\p{ ^L}`, `[\p{ ^Greek}]` under utf8 | refused, shape 2 | accepted (`\p{ ^L}` = `\P{L}`) |
| F10 | DOC-SILENT (§6.2¶3) | "a letter whose module is not enabled is refused" | std1: `(?-m)a`; `--features modifiers`: `(?-J)a`; `-e utf8`: `(?-r)a` | accepted (only setting is refused: `(?m)`, `(?^m)`, `(?r)`, `(?^r)`, `(?r:a)` refuse) | n/a |
| F11 | DOC-SILENT (§9 / §2.1¶2) | §2.1¶2 (a `0x80`-`0xFF` byte is a literal) | `--pattern $'\xe9'` (raw high byte in argv) | exit 125, `error: invalid UTF-8 was detected in one or more arguments` (not exit 1, not pcrec's diagnostic form); works only through `--pattern-esc` | n/a |
| F12 | DOC-SILENT (§9) | §9¶5 lists only `startpos > n` | `-e utf8`, `.` on `éa` from startpos 1 | `PCREC_ERR_STARTPOS` (-7) | `[2,3)` (match_api.md §9.2 does state it; §9 here does not) |
| F13 | DOC-WRONG (cli.md, minor) | cli.md §1.11 "`--no-captures` ... forces the DFA engine" | `--engine=vm --no-captures --pattern '(a)(b)'` | accepted, `RX_ENGINE "vm"`, `RX_NCAPS 1` | n/a |
| F14 | DOC-SILENT (cli, minor) | §2.3¶2 list syntax | `--features classes,` vs `--features ,classes`; `--features=classes` | trailing comma accepted, leading comma refused; the `=` form is an unknown option (unlike `--encoding=`, `--engine=`) | n/a |

Notes on the top three:
- F1: the bug is specific to `(?U)` + a possessive suffix (`*+ ++ ?+ {n,m}+ {,m}+ {n,}+`). Both engines answer the same, so
  `--engine=vm` is not a cross-check here. Without `(?U)` every possessive probe agreed.
- F2: the trigger is a lookbehind alternative that is itself a non-capturing or scoped-option group with 2 or more
  alternatives, unless they collapse to one class (`(?<=(?:a|b))x` works). A capturing group (`(?<=(ab|cd))x`) and an
  atomic group work. When the group is not first (`(?<=d|(?:a|bc))x`) the varying case is refused correctly with shape 5.
- F3: only a group whose entire body is a single option setting. Two settings, or a setting plus an atom, compile.

## Attack families that found nothing (all agreed with libpcre2 or were refused as the doc says)

Brace/literal-brace grammar and `{,m}`/spaces/leading zeros/65535-65536; `\x` forms and errors; unknown escapes;
class edge syntax (`]` first, `-` placement, invalid/out-of-order ranges, POSIX names and errors, collating elements,
`&&`); preference order and capture-last-iteration rules (§4.2-§4.4 incl. the doc's examples); empty iterations;
`^ $ \A \Z \z \G \b \B` at every startpos and around `\n`/`\r\n`; dot/`\N`/`(?s)` on `\n \r \x85 NUL \xff`; NUL in subjects;
nesting 249/250/251; ill-formed UTF-8 subjects (overlong, surrogate, >10FFFF, truncated, lone continuation) under every
negated set; ill-formed UTF-8 patterns (offsets match); code-point boundary ranges; byte `-i` (ASCII only) and
`--ucp` Latin-1 folding incl. backrefs; utf8 simple folding (K/U+212A, ſ, σς, DŽ/Dž/dž, U+0345 four-way, ß/ẞ, İ/ı, Cherokee,
Deseret, Adlam) for literals, classes, negated classes, backrefs and lookbehind; UCP byte sets and `\b`; UCP utf8
narrow sets; `(?a…)` letters; `\h \v` lists; 100+ `\p` spellings (scripts, namespaces, case/underscore/space loose
matching other than F9, `\pL`, `\p{^X}`/`\P{^X}`); extended mode incl. Pattern_White_Space under utf8, `(?xx)`, comments,
whitespace inside tokens/braces; option scoping, `(?^)`, `(?n)`, `(?J)`, `(?r)` under byte; backref digit rule
(`\10 \11 \18 \19 \81 \012`), relative/named forms and their refusals; forward and self references; lookaround
atomicity, captures, quantified assertions, startpos-before lookbehind, utf8 lookbehind character counts; atomic and
possessive (without `(?U)`); named-group syntax, length limit, utf8 name characters; quoting incl. classes and braces;
recursion and DEFINE (except F6/F7); verbs and start options (refusal shapes all as §8); module gate refusals at
`none`/`std1`/lists (except F5/F10); `${` gating; the §4.5 engine claims; engine replay of 1,020 accepted probes under
`--engine=vm` and `--engine=dfa --no-captures`: no answer differences.

## Files

`/tmp/claude-1001/langmisc/`: `harness.py` (differential runner), `drv.c` (pcrec driver), `p2probe.c` (libpcre2 oracle),
`probes_*.py` (probe sources), `results/*.jsonl` (every probe: options, subjects, both answers, verdict), `out_*.txt`.

## Disclosure

Injected at spawn, not read by me and not used: `~/.claude/CLAUDE.md`, `/home/pcrec/projects/pcrec/CLAUDE.md` (the
repository root, outside the cell) and the memory index `MEMORY.md`. `docs/spec/CLAUDE.md` (inside the cell) was
auto-attached when I read the spec. A PreToolUse hook in the repo blocked two `cd` commands; I did not read the hook.
Nothing outside the cell under the repository was read, listed or queried.
