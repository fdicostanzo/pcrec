# [NEVER-MATCH] body (filed 2026-11-09)

Frank 2026-11-09: "Should we error rx that we can see won't match anything? Working on a 'best guess' basis" ... "I like your no match ideas. File".

**Ruled direction: never an error.** PCRE2 compiles these patterns and never matches them (D26: whether a pattern is accepted follows PCRE2). Some are written on purpose (`(?!)`, `(*FAIL)` in alternations and conditionals), and generated patterns carry dead branches. Detection is best-guess and grows over releases, so an error would make acceptance depend on the analysis's strength (an improved analysis would turn working builds into errors).

**What to build (when triggered):**
1. **Optimize.** A whole pattern proved never to match emits a constant "no match" matcher. The same proof inside a pattern drops the dead branch. The proof's home is the DEAD bit span_arms L1 adds to run values (span_arms §5.2), plus D168's context sets for pair conditions (`a\bb`: `\b` between two word characters; `(?:ab\b){2}`: a repeat whose body cannot follow itself, see [REWRITE-ADJ]'s 2026-11-09 note).
2. **Tell the caller, without failing.** A `--emit-facts` fact "never matches: <reason>". Optionally, a warning flag for callers who want their build to complain, batched into [IFACE-PUSH] with the other new options (memory: CLI options in one push).

A wrong guess costs only a missed optimization or a missed warning, never a rejected pattern.

**Trigger (D77):** a corpus count of patterns (or alternation branches) the analysis proves dead, large enough that the constant matcher or the dropped branches show in size or compile time; or L1's landing, whose DEAD bit makes the whole-pattern case nearly free.
