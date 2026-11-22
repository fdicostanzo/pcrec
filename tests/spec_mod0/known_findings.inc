/* known_findings.inc — registry `quantifiable` values that DISAGREE with
 * libpcre2 once check10's probe is a real pattern. Included by check10.
 *
 * THIS IS A FINDING LIST, NOT A PIN OF A CORRECT VALUE. Each row below says
 * `quantifiable=no`, and libpcre2 compiles `<referents>a<syntax>*` (the
 * reference rows are probed with ten leading capture groups, see
 * probe_prelude() in check10). pcrec itself ACCEPTS the quantified form:
 * `(a)\1*`, `(?<n>a)\k<n>*`, `(?<n>a)(?P=n)*`, `(a)\g{-1}*` all compile under
 * `--features all`. So the registry value is a fact recorded against a bare
 * probe that named no group (where PCRE2 fails the pattern for an unrelated
 * reason, error 115), and the fix is a registry-data change in src/parse/ —
 * outside the lane that wired this suite in (STOP RULE: no src/ edits).
 * `(?(1)a|b)` is the one non-backreference row; its module (`conditionals`)
 * has no producer yet, so its value is unobservable in pcrec today.
 *
 * The suite stays runnable (it is part of `make test`) while the finding is
 * open, and the list fails in BOTH directions, like every *.inc here: a row
 * listed here that stops disagreeing (the registry was fixed) fails as stale
 * and must be deleted from this file; a NEW disagreement is not listed and
 * fails. Deleting this file's entries is the fix's acceptance test.
 */
"\\k<name>", "\\g{-1}", "\\1", "\\2", "\\3", "\\4", "\\5", "\\6", "\\7",
"\\8", "\\9", "(?P=n)", "(?(1)a|b)",
