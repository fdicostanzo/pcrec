/* src/facts/facts.h — THE PATTERN-FACTS RECORD's CONSUMER header
 * ([PATFACTS], docs/design/patfacts/design.md §2, §4.2.1).
 *
 * A consumer of a pattern fact reads it through this header and nothing
 * else: types, accessors and renderers, and never a derivation. The
 * derivations are declared in `facts_derive.h`, which only the files
 * `facts.def` names as OWNERS may include — `tests/codegen/
 * run_facts_checks.sh` enforces that from the include graph and the link
 * symbols (design §4.2.3).
 *
 * Step 3.0a (the `core/internal.h` split) creates this header empty: the
 * accessors land with step 3.0. `core/internal.h` includes it, so `Job`
 * can carry the record. */
#ifndef PCREC_FACTS_H
#define PCREC_FACTS_H

#endif /* PCREC_FACTS_H */
