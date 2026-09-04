/* asm_evidence.c -- [FORM-CHAR] STEP 0's compiler-equivalence check.
 *
 * Three spellings of a caseless letter test, plus a non-fold-pair control.
 * `make asm` compiles this with `gcc -O2 -S` and the result is committed
 * at `results/three_spellings.s` -- the evidence behind
 * docs/dev/form_char_step0.md's claim that gcc folds every fold-pair
 * spelling to the SAME branchless mask+compare+sete, so the table-vs-
 * bit-array LATENCY argument does not apply to family A's fold-vs-array
 * comparison, only to family B (general classes) and family D (the atom
 * table). test_nonpair is the two-compare-plus-or control: a class whose
 * two members are NOT a case-fold pair still compiles branchless, but to
 * a longer chain -- which is exactly what a non-fold-pair scan-edge site
 * (the `nonpair` witness in family C) measures.
 */

int test_or(unsigned char c) { return c=='a' || c=='A'; }
int test_bitor(unsigned char c) { return (c=='a') | (c=='A'); }
int test_fold(unsigned char c) { return (c|0x20)=='a'; }
int test_nonpair(unsigned char c) { return c=='a' || c=='z'; }
