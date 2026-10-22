# The pcrec pattern language

This document defines the regular-expression language `pcrec` compiles: every construct it accepts, what each one matches, which captures it sets and in what preference order, which module gates it, how it is refused when it is not available, and how the encoding and the compile options change any of that. It is pcrec's own contract. `docs/pcre2_compliance.md` is the delta from PCRE2, construct by construct; `pcrec --list-syntax` is the generated construct index (`registry.md` §2) and §10 below is checked against it row for row. The match API that runs a compiled pattern is `match_api.md`; the command line is `cli.md`; the numeric limits are `limits.md`; the `.rxt` source format is `rxt_format.md`; module `vars` has its own document, `vars.md`. The history of this document is `docs/dev/history/syntax_record.md`, which is not normative.

Every sentence below that says what a pattern matches can be checked by compiling the pattern and running it. Examples are written `PATTERN` on `SUBJECT` → `[start, end)` for the whole-match span, followed by group spans where they matter; `-1` is an unset group (`match_api.md` §5). Subjects are written with the escapes of `rxt_format.md` (`\n`, `\xHH`). Unless an example names an option, it is compiled with the bare defaults: `-e byte`, no `-i`, `--features` absent (so `std1`, §2.3), `--engine=auto`, captures on.

## 1. Scope, reference and tiers

### 1.1 What this document defines

A pattern is a sequence of bytes given to one compile (`cli.md` §1.3, `match_api.md` §7) together with that compile's options. This document defines, for every pattern and option set, whether the compile is accepted, and for an accepted one, which spans and captures a search reports on every subject. It does not define the emitted C, the entry points, the give-up codes or the budgets; those are `match_api.md` and `limits.md`, and this document names them only where a construct's behaviour depends on them.

### 1.2 The reference semantics

For every construct this document describes as matching "as PCRE2", the answer is libpcre2's answer at the corresponding PCRE2 options, and the reference build is libpcre2 10.46 with its default compile-time configuration (newline LF, `\R` any Unicode newline, Unicode 16.0.0 tables in pcrec):

| pcrec compile | PCRE2 compile options | PCRE2 match options |
|---|---|---|
| `-e byte` (default) | `0` (8-bit, non-UTF) | `0` |
| `-e utf8` | `PCRE2_UTF` | `0`, with `PCRE2_MATCH_INVALID_UTF` semantics for an ill-formed subject (`match_api.md` §9.3) |
| `-i` | adds `PCRE2_CASELESS` | |
| `--ucp`, or `(*UCP)` | adds `PCRE2_UCP` | |

A search from `startpos` corresponds to `pcre2_match` at start offset `startpos`. Where pcrec's answer differs from libpcre2's at that mapping, the difference is stated where the construct is defined and collected in §9. A difference that is not stated is a defect.

### 1.3 The contract tiers

1. What an accepted pattern matches — the span, every group's span, and whether a search finds a match at all — is exact. A wrong answer is always a defect.
2. Whether a construct is accepted, and which module owns it, is exact: the module named in a refusal is the module that owns the construct, and a construct PCRE2 accepts is either accepted, or refused by one of the refusal shapes of §2.4, never accepted with a different meaning.
3. pcrec's own pattern offset in a diagnostic is exact under pcrec's own convention (`cli.md` §3.3¶4).
4. The wording of a diagnostic is not part of this contract, except the substring `requires module 'X'` and the other shape markers of §2.4. PCRE2's error numbers and offsets are never promised.

### 1.4 Reading a construct table

Each construct section has a table with these columns. `spelling` is the construct as written; where it is also a `--list-syntax` row's `syntax`, §10 names the section. `matches` is the meaning. `module` is the gate (§2.3): `base` means no module. `engines` is which engine can run the construct in general: `any` for either, `vm` for the backtracking VM only; a `vm` construct may still compile under `--engine=dfa` when the pattern is rewritten into an equivalent the DFA can run (§4.5). `quantifiable` says whether a quantifier may follow the construct (§5.6); a construct that cannot be quantified refuses `X*` with "quantifier does not follow a repeatable item".

## 2. What selects the language

### 2.1 The pattern text

The pattern is a byte string. It cannot contain a NUL byte, because the compile entry takes no pattern length (`cli.md` §1.4¶3); `\x00` is the spelling of a NUL character (§5.2).

Under `-e byte` every byte is one pattern character, and a byte `0x80`-`0xFF` is a literal character with that code point. Under `-e utf8` the pattern must be well-formed UTF-8: an ill-formed sequence is refused with "ill-formed UTF-8 in pattern" at the offset of the sequence (`\xff` refuses at offset 0; `a\xc3` refuses at offset 1), and a well-formed multi-byte sequence is one character.

### 2.2 The encoding

`-e byte` and `-e utf8` select what a CHARACTER of the subject is (`match_api.md` §9.1, `cli.md` §1.7):

| | `byte` | `utf8` |
|---|---|---|
| a character is | one byte, code point `0x00`-`0xFF` | one well-formed UTF-8 sequence, code point `U+0000`-`U+10FFFF` except surrogates |
| `.`, a class, `\N`, a negated escape match | one byte | one whole character, 1 to 4 bytes |
| `\x{h...}` above `0xFF` | refused, naming the encoding | accepted up to `10FFFF`; `D800`-`DFFF` refused |
| an ill-formed subject sequence | cannot occur | matched by nothing (`match_api.md` §9.3), or refused under `-futf-check` (`match_api.md` §9.4) |
| default meaning of `\d \s \w`, POSIX classes, `\b` | ASCII sets | ASCII sets |
| `\h \H \v \V` | `[\t \xa0]`, `[\n\x0b\f\r\x85]` and their complements | PCRE2_UTF's Unicode lists (`cli.md` §1.9¶3) |
| `-i` fold | the 52 ASCII letters | Unicode simple case folding (`cli.md` §1.8) |
| modules implied on | none | `unicode-props` and `ucp` (§2.3) |

So `.` on `é` (the bytes `\xc3\xa9`) is `[0, 1)` under `byte` and `[0, 2)` under `utf8`; `é+` under `byte` is `\xc3` followed by one or more `\xa9`, and under `utf8` one or more `é`.

### 2.3 The module gate

Every construct outside the base tier (§5) belongs to exactly one module, named in `--list-syntax`'s `module` column. A compile enables a set of modules; a construct whose module is not enabled is refused with `requires module 'X'`.

- The set is chosen by `--features LIST` (`cli.md` §1.17) or `pcrec_options.features` (`match_api.md` §8.2). `LIST` is either a comma-separated list of module names, or exactly one of `std1`, `all` or `none`; a named set does not combine with module names (`--features std1,quoting` is refused as an unknown module `std1`).
- With no `--features`, the set is `std1` = {`classes`, `modifiers`}. An explicit list REPLACES `std1`; it does not add to it: `--features named-groups` compiles `(?<n>a)` and refuses `\d` and `(?i)`.
- `-e utf8` enables `unicode-props` and `ucp` in addition to whatever the list names.
- `--features none` enables nothing: `\d`, `[[:digit:]]`, `[\d]` and `(?i)` are refused, naming `classes` and `modifiers`.

A module whose construct has no producer in this build refuses the construct even when enabled (§2.4, shape 2). §6 and §7 are the modules with producers; §8 lists the rest.

### 2.4 Refusals

A refused compile writes nothing and exits 1 (`cli.md` §3.1); the library entry returns its error (`match_api.md` §7). Every refusal names an offset into the pattern. The shapes, by the marker the diagnostic carries:

| shape | marker in the diagnostic | means |
|---|---|---|
| 1 gated | `requires module 'X'` | the construct is real and owned by module `X`, which this compile did not enable |
| 2 unbuilt | `module 'X' is enabled but ... is not implemented yet` | `X` is enabled and has no producer for this construct |
| 3 out of scope | `is outside pcrec's scope and no module will implement it` | real PCRE2 syntax pcrec excludes permanently (§8.2) |
| 4 engine | `requires the VM engine, which --engine=dfa excludes` | the construct (as rewritten, §4.5) needs the VM and `--engine=dfa` was requested |
| 5 capability | a sentence naming what is not implemented | the construct is accepted by PCRE2, pcrec owns it, and this instance is beyond what pcrec builds (variable-length lookbehind, §7.4; wide UCP sets, §7.8) |
| 6 resource | a sentence naming the budget and its raise flag | a compile-time budget was exceeded (`limits.md` §3.3) |
| 7 grammar | a PCRE2-like sentence | the pattern is not well-formed; PCRE2 refuses it too |

Shape 7's wording follows PCRE2's where pcrec has one to follow, and that is a courtesy, not a contract (§1.3).

### 2.5 Options that change meaning

These compile options change what a pattern means. Every other option (the `-f` family, `--tune`, `--part-*`, `--memfn`, the budgets) changes how the artifact is built and never an answer, except by moving where a give-up or a resource refusal happens.

| option | inline spelling | effect |
|---|---|---|
| `-i` | `(?i)` at pattern start | caseless matching, §6.2 and `cli.md` §1.8 |
| `--ucp` | `(*UCP)` at pattern start | Unicode semantics for `\d \s \w \b`, POSIX classes, §7.8 |
| `-e utf8` | `(*UTF)` / `(*UTF8)` confirm it; they cannot select it | §2.2 |
| `--features` | none | §2.3 |
| `--no-captures` | none | every group is reported as if non-capturing; only `[start, end)` is written (`cli.md` §1.11) |
| `--engine=dfa\|vm\|auto` | none | never an answer; a request the pattern cannot honour is refused (§4.5) |

`(?m)`, `(?s)`, `(?x)`, `(?xx)`, `(?n)`, `(?U)`, `(?J)`, `(?a…)` and `(?r)` have no command-line flag; a `.rxt` block's `flags` line (`rxt_format.md` §1.5¶4) carries the letters.

## 3. Grammar

### 3.1 Structure

The grammar below fixes structure and precedence; each terminal is defined by the section named beside it. Quantifiers bind tighter than concatenation, which binds tighter than `|`.

```
pattern      = { start-option } alternation ;                (* §7.8, §8.1 *)
alternation  = branch { "|" branch } ;                        (* §5.7 *)
branch       = { item } ;                                     (* may be empty *)
item         = atom [ quantifier ]                            (* §5.6 *)
             | option-setting ;                               (* (?i) and friends, §6.2 *)
quantifier   = ( "*" | "+" | "?" | braces ) [ "?" | "+" ] ;  (* "+" suffix: §7.2 *)
braces       = "{" sp digits sp "}"
             | "{" sp digits sp "," sp [ digits ] sp "}"
             | "{" sp "," sp digits sp "}" ;                  (* sp = zero or more space/tab *)
atom         = literal | escape | "." | class | group
             | "^" | "$" | ...                                (* every construct of §5-§8 *)
group        = "(" alternation ")"                            (* capturing, §5.7 *)
             | "(?:" alternation ")"                          (* non-capturing, §5.7 *)
             | "(?" option-letters ":" alternation ")"        (* scoped options, §6.2 *)
             | "(?" ... ")"                                   (* every other (? group, §7-§8 *)
```

A `{` that does not begin one of the three `braces` forms is a literal `{` (`a{`, `a{x}`, `a{,}` and `a{1 2}` match themselves), and `}` and `]` outside a class are literals. Some atoms are not quantifiable (§1.4), and a `quantifier` directly after another `quantifier` is refused ("multiple quantifiers on the same item": `a**`, `a{2}{3}`), except that the single `?` or `+` suffix is part of the first quantifier.

### 3.2 Extended mode

Under `(?x)` (§6.2), outside a class and outside `\Q…\E`, the whitespace characters `\t \n \x0b \f \r` and space, and under `-e byte` also `\x85`, are ignored, and `#` begins a comment that ends at the next `\n` (or the end of the pattern). Whitespace is ignored between items and between a quantifier and its `?`/`+` suffix (`(?x)a+ ?` is `a+?`), but not inside a token: `(?x)( ?:a)` is a group starting with a quantifier, refused, and `(?x)(? i)` is refused. Inside braces only space and tab are allowed in any mode (§3.1). An escaped space, `\ `, is a literal space. `(?xx)` additionally ignores space and tab inside a class (`(?xx)[ a]` matches `a` and not a space).

Under `-e utf8` and `(?x)`, pcrec ignores the same ASCII set and nothing else; PCRE2 also ignores U+0085, U+200E, U+200F, U+2028 and U+2029 there. This is a defect (§9, item 7): `(?x)a b` on `ab` is no match under pcrec and `[0, 2)` under PCRE2.

## 4. Matching

### 4.1 Which match a search reports

A search from `startpos` (`match_api.md` §3.1) reports the match at the smallest position `p >= startpos` at which the pattern matches, and at `p`, the first successful way of matching in the preference order of §4.2. That is the match PCRE2's backtracking matcher reports. It is not the longest match: `a|ab` on `ab` is `[0, 1)`, and `ab|a` is `[0, 2)`.

### 4.2 Preference order

The ways a pattern can match at one position are ordered, and the first that succeeds is the match:

1. Alternatives are tried left to right.
2. A greedy quantifier tries more iterations before fewer; a lazy one (`*?`, `+?`, `??`, `{n,m}?`) fewer before more. `(?U)` swaps the two spellings (§6.2).
3. A possessive quantifier and an atomic group (§7.2) keep the first way their body matched and never try another.
4. Concatenation orders lexicographically: an earlier item's choice is changed only after every choice of the later items has failed.

`(a|ab)(c|bcd)(d*)` on `abcd` → `[0, 4)`, group 1 `[0, 1)`, group 2 `[1, 4)`, group 3 `[4, 4)`. `a*?b` on `aaab` → `[0, 4)`. `a{2,3}?` on `aaaa` → `[0, 2)`.

### 4.3 Empty iterations

An iteration of a quantified item that matches the empty string ends the repetition: no further iteration is tried after it. `(a*)*b` on `b` → `[0, 1)`, group 1 `[0, 0)`; `(|a)+` on `aa` → `[0, 0)`, group 1 `[0, 0)`; `(|a)+$` on `aa` → `[0, 2)`, group 1 `[2, 2)`.

### 4.4 Captures

A capturing group is numbered by the position of its opening parenthesis, counting from 1, left to right through the whole pattern, including groups inside lookarounds and inside groups that never run. A group holds the span of its last execution on the reported path, and keeps a value from an earlier iteration of an enclosing quantifier when its own iteration did not run it (`match_api.md` §5.1): `((a)|(b))*` on `ab` → group 1 `[1, 2)`, group 2 `[0, 1)`, group 3 `[1, 2)`. A group that never ran on the reported path is unset. `(a)|b` on `b` → group 1 unset. `(a{0})b` on `b` → group 1 `[0, 0)`: a zero-count repeat inside the group still runs the group. How spans are delivered, and what `--no-captures` changes, is `match_api.md` §5 and `cli.md` §1.11; how named groups and library groups are numbered is §7.5 and `match_api.md` §5.4-§5.5.

### 4.5 Engines never change an answer

pcrec has two engines: a DFA, which cannot run captures or any `vm` construct, and a backtracking VM, which can run everything this document accepts (`cli.md` §1.13). `--engine=auto` (the default) chooses; the choice never changes an answer. Some `vm` constructs are rewritten when the pattern allows an exact equivalent the DFA can run, so whether a given pattern compiles under `--engine=dfa --no-captures` depends on the whole pattern, not only on its constructs: `(?=a)a` and `\w+(?=\d)` compile under `--engine=dfa --no-captures`, `(?=.*b)a` is refused with shape 4. The rewrites and their deny flags are `tuning.md` §2.8 and §2.9. A capture-bearing pattern under `--engine=dfa` without `--no-captures` is refused.

### 4.6 Give-ups

A VM artifact may return a give-up code instead of an answer when it exhausts a budget or a capacity (`limits.md` §2): `PCREC_ERR_STEPS`, `PCREC_ERR_FRAMES`, `PCREC_ERR_WORK`. A give-up is never a wrong answer and is not a difference from PCRE2 under this document's tiers; it says nothing about whether the subject matches. A DFA artifact never gives up.
