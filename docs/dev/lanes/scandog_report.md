# scandog report

## Summary
The whole inline_c.md 2.3 C scanner (rules 1-5) is expressed as ONE pcrec
pattern; no rule is inexpressible. Corpus: tests/recursion/cscan.rxt (76
cases, 135 incl. g lines) + generator gen_cscan.py. Green under the main-tree
build. Placed in tests/recursion because balanced braces ARE the recursion
module's construct (needs recursion, named-groups, conditionals (DEFINE),
atomic-groups (possessive), lookaround, assertions (\G), modifiers ((?x))).

## The pattern
Anchored \G at `(?{`, group 1 `body` = text before the closing brace, no
match = refusal. (?x) form, as written in the file:

```
# pcrec scanner for the C (?{ ... }) segment: docs/design/inline_c.md 2.3.
# S = phase-2 splices (backslash-newline), skipped between any two characters.
\G \(\?\{ (?<body> (?&items) (?&sp) ) (?: \} | % (?&sp) > ) (?&sp) \)

(?(DEFINE)
  (?<sp> (?: \\ \n )*+ )

  # a run of tokens, stopping (without consuming) at the closing } or %> of the current depth
  (?<items> (?:
      (?&sp) (?:
          # identifier: an encoding prefix (L u U u8) is ordinary identifier text
          [A-Za-z_$\x80-\xff] (?: (?&sp) [\w$\x80-\xff] )*+
          # pp-number: a ' followed by an identifier character is a C23 digit separator
        | (?: \d | \. (?&sp) \d ) (?: (?&sp) (?: [eEpP][+-] | [\w.$\x80-\xff] | ' (?= (?&sp) \w ) ) )*+
          # string and character literals, backslash escapes, a raw newline never inside
        | " (?: [^"\\\n]++ | \\ \n | \\ (?&sp) [^\n] )*+ "
        | ' (?: [^'\\\n]++ | \\ \n | \\ (?&sp) [^\n] )*+ '
          # block comment, line comment (a spliced newline continues it)
        | / (?&sp) \* (?: [^*]++ | \* (?! (?&sp) / ) )*+ \* (?&sp) /
        | / (?&sp) / (?: [^\\\n]++ | \\ \n | \\ )*+
          # a nested block: { ... } or <% ... %>
        | (?: \{ | < (?&sp) % ) (?&items) (?&sp) (?: \} | % (?&sp) > )
          # everything else, one byte; < and % are plain unless they open a digraph
        | [^\w$\x80-\xff"'/{}<%] | / (?! (?&sp) [*/] ) | < (?! (?&sp) % ) | % (?! (?&sp) > )
      )
  )*+ )
)
```

Choices where 2.3 is silent (stated in the file header): a raw newline inside
a "..." or '...' literal refuses (unterminated); a // comment reaching the end
of the pattern refuses (depth > 0); the body includes a splice just before the
closing brace. Recursion depth bounds nesting depth (give-up code, not a
wrong answer, in pcrec; libpcre2 has its own limits).

## Corpus cases
Every 2.3 table row: "}", '}', /* } */, // } newline, <% %>, 1'000, u8"}",
} at depth 2 then }), plus splice cases (in block/line comment open and
close, in literals incl. \\ then splice, in digraphs, digit separators,
before the paren), digit separators (hex, float, after identifier digit),
non-ASCII identifier bytes, preprocessor braces (counted, so an unbalanced
#define refuses), 3 realistic multi-line bodies, and refusals (unterminated
literal/comment, newline in literal, depth>0 at EOF, } not followed by ),
}}, } at EOF, first } not followed by ) even if a later }) exists), plus
3 \G startpos cases.

## Oracle
libpcre2 10.46 through docs/design/eng_brep_measurements/probes/pcre2_ctypes.py.
python3 -I tests/recursion/gen_cscan.py [out.rxt] drives every case through
libpcre2 AND checks the hand-written rule expectation; it aborts on any
disagreement. 5 first-draft disagreements were all my rule expectations
(left-to-right splice reading: "\\" + newline is a lone backslash then a
splice; unbalanced brace on a # line counts) or a pattern bug (unterminated
comment fell back to a plain "/": fixed with a guard), never expectation
edits to fit pcre2. pcrec was never asked to produce an expectation.
Run: PCREC=build/pcrec bash scripts/boxlock run --label scandog-cscan -- bash tests/harness/run.sh tests/recursion/cscan.rxt
Result: cases passed 135, failed 0, compile failures 0.

## Bench handoff
PATTERN: tests/recursion/cscan.rxt (pattern-esc block; source in gen_cscan.py)
 on pcrec main. It is the C `(?{ ... })` end scanner of inline_c.md 2.3 as one
 recursive possessive pattern (group 1 = body); it will replace the
 hand-written scanner ([SCANNER-DOGFOOD]).
SUBJECTS: (1) a stream of N thousand `(?{...})` segments, 20 B - 5 KB each,
 concatenated, scanned one after another with startpos at each segment start
 (the compiler's access pattern); (2) real C function bodies (e.g. the Linux
 kernel or sqlite3.c, bodies wrapped as (?{ ... })) with heavy comments,
 strings, 1'000-style literals and #define splices; (3) pathologicals:
 5 MB of one comment, 100k-char string literal, nesting depth 1k/10k/100k
 of { and <% (recursion frames), 1 MB of identifiers, refusal inputs
 (unterminated comment at 5 MB).
MEASURE: MB/s of the generated matcher vs the hand-written scanner (and vs
 libpcre2 JIT/interpreter as reference); behaviour at deep nesting (frame
 give-up vs crash/time); engine route (VM vs other). Tells us whether pcrec
 can dogfood its own scanner without a speed or depth regression, and which
 constructs (recursion call, possessive loops, (?&sp) per char) cost most.

## STATE AT HANDOFF
Committed on lane/scandog: tests/recursion/{cscan.rxt,gen_cscan.py,CLAUDE.md}
and this report. Not pushed. Rulings file: no entries (last applied: none).
No src/ change; no make test run (corpus section only, harness run.sh).
