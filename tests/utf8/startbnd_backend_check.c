/* tests/utf8/startbnd_backend_check.c — [K50] THE BYTE-TAUTOLOGY CLAIM, AS A
 * CHECK RATHER THAN AS PROSE.
 *
 * The fix rests on a sentence that appears in six comments and a lane report:
 * *"under `byte` no gate node is built, no guard is emitted, and every byte
 * artifact is unmoved BY CONSTRUCTION."* The identity gate proves the
 * CONSEQUENCE — 0 differing over the whole corpus, four axes — and that is
 * strong evidence but it is not the claim: a gate could be built and then
 * happen to compile away, and the gate would read green. This file asserts
 * the CONSTRUCTION, at the one place it is decided, so a reviewer has
 * something to attack that is not an adjective.
 *
 * IT READS THE BACKEND ROWS DIRECTLY, which is what makes it independent of
 * everything downstream. `src/ir/nfa.c` builds the gate iff
 * `PcrecEnc.start_cls` is non-NULL and the emitters emit a guard iff
 * `start_guard` is non-NULL; every other statement of "byte pays nothing" is
 * DERIVED from those two pointers. So the honest check is on the pointers.
 *
 * FIVE ASSERTIONS, and each fails for a different reason:
 *
 *   1. `byte` restricts nothing — BOTH pointers NULL. This is the tautology
 *      claim itself. A backend that filled either one would build a gate the
 *      byte encoding has no use for.
 *   2. `utf8` restricts something — BOTH pointers non-NULL. The non-vacuity
 *      twin: without it, assertion 1 passes on a tree where the whole feature
 *      was deleted.
 *   3. THE TWO POINTERS AGREE PER BACKEND — `start_cls == NULL` iff
 *      `start_guard == NULL`, for EVERY backend in the registry, walked by id
 *      rather than named one at a time. This is the one a reader is most
 *      likely to think redundant and it is the sharpest: the IR reads the
 *      first and the emitters read the second, so a backend supplying one
 *      without the other would build a machine whose gate no entry guard
 *      matches, or emit a guard for a machine that never gates. Neither is a
 *      wrong ANSWER on any subject a corpus would think to try — the two
 *      halves cover different positions — which is exactly why it needs an
 *      assertion rather than a test case.
 *   4. THE utf8 SET IS EXACTLY THE COMPLEMENT OF 0x80..0xBF, checked byte by
 *      byte over all 256. Spelled as the RULE rather than as the table's
 *      contents, so it is an independent statement of the predicate and not a
 *      transcription of `enc_utf8.c`'s initializer.
 *   5. `pcrec_enc_start_cls_ok()` holds for every backend — the partition
 *      precondition the DFA's class axis depends on (`UPC_NOSTART`), asserted
 *      here as well as at the compile site, because a backend added later is
 *      checked at its first COMPILE and this file checks it at every RUN.
 *
 * Exit 0 with a one-line summary, or 1 with the failing assertion named.
 */
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "gen/enc/enc.h"

static int fails;

static void bad(const char *what)
{
    printf("FAIL: %s\n", what);
    fails++;
}

/* The rule, written out rather than read from the backend's table — the whole
 * point of assertion 4 is to be a SECOND statement of it. */
static int utf8_may_start_here(unsigned c)
{
    return (c & 0xC0u) != 0x80u;
}

int main(void)
{
    const PcrecEnc *b = pcrec_enc_by_id(PCREC_ENC_BYTE);
    const PcrecEnc *u = pcrec_enc_by_id(PCREC_ENC_UTF8);
    int checked_backends = 0, cls_bytes = 0;

    if (!b || !u) {
        printf("FAIL: the encoding registry did not resolve byte and utf8 — "
               "this check has lost its subject\n");
        return 1;
    }

    /* 1 — the tautology claim. */
    if (b->start_cls != NULL)
        bad("byte declares a character-start SET, so src/ir/nfa.c builds a "
            "boundary gate node under an encoding where every position is a "
            "character boundary — the byte artifact is no longer unmoved by "
            "construction and the identity gate is the only thing left "
            "standing between that and a shipped regression");
    if (b->start_guard != NULL)
        bad("byte declares a character-start GUARD, so every byte artifact's "
            "entries grow a startpos test for a condition that cannot fail");

    /* 2 — the non-vacuity twin. Without this, assertion 1 is green on a tree
     * with the whole mechanism removed. */
    if (u->start_cls == NULL)
        bad("utf8 declares NO character-start set — K50's IR gate is not "
            "built at all, and every assertion about `byte` above is vacuous");
    if (u->start_guard == NULL)
        bad("utf8 declares NO character-start guard — the caller-startpos "
            "half of K50 is not emitted at all");

    /* 3 — the two pointers agree, for EVERY backend the registry carries.
     * Walked by id so a backend added later is covered without an edit. */
    for (int id = 0; id < 64; id++) {
        const PcrecEnc *e = pcrec_enc_by_id(id);
        if (!e) continue;
        checked_backends++;
        if ((e->start_cls == NULL) != (e->start_guard == NULL))
            bad("a backend declares one of start_cls/start_guard and not the "
                "other: the IR reads the first and the emitters read the "
                "second, so the machine's gate and the entries' guard would "
                "disagree about whether this encoding restricts anything");
        if (!pcrec_enc_start_cls_ok(e))
            bad("a backend's character-start set overlaps the word or newline "
                "set, which the DFA class axis represents as ONE PARTITION "
                "(UPC_NOSTART) — a non-start byte would classify UPC_WORD, "
                "read as a character start to the gate, and re-open K50");
    }
    if (checked_backends < 2)
        bad("fewer than two backends were reachable through the registry — "
            "the walk above measured almost nothing");

    /* 4 — the utf8 set IS the rule, byte by byte over all 256. */
    if (u->start_cls) {
        for (unsigned c = 0; c < 256; c++) {
            int in_table = cls_has(u->start_cls, c) ? 1 : 0;
            int by_rule  = utf8_may_start_here(c);
            if (in_table != by_rule) {
                char msg[160];
                snprintf(msg, sizeof msg,
                         "utf8's character-start set disagrees with the rule "
                         "at byte 0x%02X: the table says %s, "
                         "\"not a continuation byte\" says %s",
                         c, in_table ? "startable" : "not startable",
                         by_rule ? "startable" : "not startable");
                bad(msg);
                break;      /* one witness is the finding; 64 is noise */
            }
            cls_bytes += in_table;
        }
        /* The count, so a reader can see the shape without trusting the loop:
         * 256 bytes minus the 64 continuation bytes. Stated as arithmetic
         * rather than as the literal 192 for the same reason the loop above
         * spells the rule. */
        if (cls_bytes != 256 - 64)
            bad("utf8's character-start set does not hold 256 - 64 bytes");
    }

    if (fails) {
        printf("startbnd-backend: %d assertion(s) FAILED\n", fails);
        return 1;
    }
    printf("byte declares neither start_cls nor start_guard (no gate is BUILT "
           "and no guard is EMITTED there, by construction); utf8 declares "
           "both; %d backend(s) agree on the pair and satisfy the UPC_NOSTART "
           "partition precondition; utf8's set is exactly the %d "
           "non-continuation bytes, checked against the rule over all 256\n",
           checked_backends, cls_bytes);
    return 0;
}
