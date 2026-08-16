/* cand_gen.c -- template instantiations of the broadcast matcher.
 *
 * Every matcher here is generated from bcast_gen.h; the per-position member
 * sets below are the single source of truth for what each function matches and
 * must stay in step with the pattern/ci pair registered in candidates.c.
 *
 * Axes covered: needle length (k = 2..32), non-alpha needle bytes, two
 * different case-insensitive strategies (OR-of-case-twins vs. fold-the-block),
 * and multi-member character classes.
 */

#include <stddef.h>

/* ---- exact, pure-alpha needles: the length axis ----------------------- */

#define GEN_FN   find_gen_do
#define GEN_K    2
#define GEN_SETS { "d", "o" }
#include "bcast_gen.h"

#define GEN_FN   find_gen_wolf
#define GEN_K    4
#define GEN_SETS { "w", "o", "l", "f" }
#include "bcast_gen.h"

#define GEN_FN   find_gen_backfire
#define GEN_K    8
#define GEN_SETS { "b", "a", "c", "k", "f", "i", "r", "e" }
#include "bcast_gen.h"

/* "incomprehensible" */
#define GEN_FN   find_gen_k16
#define GEN_K    16
#define GEN_SETS { "i", "n", "c", "o", "m", "p", "r", "e", \
                   "h", "e", "n", "s", "i", "b", "l", "e" }
#include "bcast_gen.h"

/* "thequickbrownfoxjumpsoverthelazy" */
#define GEN_FN   find_gen_k32
#define GEN_K    32
#define GEN_SETS { "t", "h", "e", "q", "u", "i", "c", "k", \
                   "b", "r", "o", "w", "n", "f", "o", "x", \
                   "j", "u", "m", "p", "s", "o", "v", "e", \
                   "r", "t", "h", "e", "l", "a", "z", "y" }
#include "bcast_gen.h"

/* ---- exact needle mixing letters, digits and punctuation -------------- */

/* "h3ll0_w9" */
#define GEN_FN   find_gen_h3ll0w9
#define GEN_K    8
#define GEN_SETS { "h", "3", "l", "l", "0", "_", "w", "9" }
#include "bcast_gen.h"

/* ---- case-insensitive via OR of the two case twins -------------------- */

/* "hello", ci */
#define GEN_FN   find_ci_hello_or
#define GEN_K    5
#define GEN_SETS { "hH", "eE", "lL", "lL", "oO" }
#include "bcast_gen.h"

/* "backfire", ci */
#define GEN_FN   find_ci_backfire
#define GEN_K    8
#define GEN_SETS { "bB", "aA", "cC", "kK", "fF", "iI", "rR", "eE" }
#include "bcast_gen.h"

/* "h3ll0_w9", ci: letters twinned, digits and '_' exact. */
#define GEN_FN   find_ci_h3ll0w9
#define GEN_K    8
#define GEN_SETS { "hH", "3", "lL", "lL", "0", "_", "wW", "9" }
#include "bcast_gen.h"

/* ---- case-insensitive via folding the haystack block ------------------ */

/* "hello", ci */
#define GEN_FN   find_ci_hello_fold
#define GEN_K    5
#define GEN_SETS { "h", "e", "l", "l", "o" }
#define GEN_FOLD 1
#include "bcast_gen.h"

/* "backfire", ci */
#define GEN_FN   find_ci_backfire_fold
#define GEN_K    8
#define GEN_SETS { "b", "a", "c", "k", "f", "i", "r", "e" }
#define GEN_FOLD 1
#include "bcast_gen.h"

/* "h3ll0_w9", ci: the fold leaves '3', '0' and '_' alone, so they still
 * compare exactly. */
#define GEN_FN   find_ci_h3ll0w9_fold
#define GEN_K    8
#define GEN_SETS { "h", "3", "l", "l", "0", "_", "w", "9" }
#define GEN_FOLD 1
#include "bcast_gen.h"

/* ---- multi-member character classes ----------------------------------- */

/* "[ab][cd]gh" */
#define GEN_FN   find_cls_abcdgh
#define GEN_K    4
#define GEN_SETS { "ab", "cd", "g", "h" }
#include "bcast_gen.h"

/* "[0369][0369]zz" -- four members per class, the widest OR chain here. */
#define GEN_FN   find_cls_digits
#define GEN_K    4
#define GEN_SETS { "0369", "0369", "z", "z" }
#include "bcast_gen.h"
