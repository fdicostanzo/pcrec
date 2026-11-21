# Predicates library (sample base file, lib)

## Names   [lib/names]

### Padded   [lib/names/padded]   ruled 2026-11-02
A padded name is the body with fixed-width padding applied.
needs: core/holes/class
by: core/principles/regex-default
module: text
default: yes
skeleton: yes

### Trimmed   [lib/names/trimmed]   open lib-trim-q 2026-11-04
A trimmed name removes leading and trailing blanks.
module: ?
WHOLE: t; SEARCHED: t; FIND-ALL: t.

### Word   [lib/names/word]   ?  2026-11-05
