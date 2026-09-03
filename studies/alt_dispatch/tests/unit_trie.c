/* unit_trie.c -- adversarial exactness tests for (c), the sorted trie with
 * priority-tagged accepts, AND (e), the VM-native trie walk (ruling R1,
 * Frank 2026-09-03). Both counter-examples are src/ir/nfa.c:192's own
 * (M2.8's rule 1 and rule 2 hazards, oracle-confirmed there against python
 * `re`); this file re-confirms them against THIS study's independent
 * implementation, and adds the decline-path case the charter's exactness
 * argument owes ("what a class branch would need").
 *
 * Every case asserts trie_dispatch(...) == trie_dispatch_vm(...) ==
 * serial_try(...) (this study's own oracle) AND, where nfa.c's comment
 * states the PCRE answer explicitly, cross-checks that literal span too.
 * The rule-1 case (abc|a|abd) is also (e)'s own DEFER/COMMIT worked
 * example: "a" (index 1) is not its node's subtree_min against "abc"
 * (index 0) reachable deeper, so it DEFERS; "abc" and "abd" (indices 0, 2)
 * are each their own subtree's minimum among what remains, so whichever
 * the subject selects COMMITS -- see the stderr trace this test prints.
 */
#include "../src/common.h"
#include "../src/algo_serial.h"
#include "../src/algo_trie.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

static int failures = 0;

static void check_case(const char *label, BranchSet *bs, const char *subject)
{
    size_t slen = strlen(subject);
    const unsigned char *subj = (const unsigned char *)subject;
    Trie *t = trie_build_from(bs);
    long long total_frames = 0;
    int max_deferred = 0;

    for (size_t pos = 0; pos <= slen; pos++) {
        Cost ca = {0,0,0,0}, cc = {0,0,0,0}, ce = {0,0,0,0};
        Answer oracle = serial_try(bs, subj, slen, pos, &ca);
        int cand[64], ncand;
        Answer got = trie_dispatch(t, bs, subj, slen, pos, &cc, cand, 64, &ncand);
        Answer gote = trie_dispatch_vm(t, bs, subj, slen, pos, &ce);
        total_frames += ce.frames;
        if (ce.deferred_seen > max_deferred) max_deferred = ce.deferred_seen;

        bool ok = (got.hit == oracle.hit) &&
                  (!oracle.hit || (got.index == oracle.index && got.match_len == oracle.match_len));
        bool oke = (gote.hit == oracle.hit) &&
                  (!oracle.hit || (gote.index == oracle.index && gote.match_len == oracle.match_len));
        if (!ok) {
            failures++;
            fprintf(stderr, "FAIL(c) %s pos=%zu: oracle hit=%d idx=%d len=%d, trie hit=%d idx=%d len=%d\n",
                    label, pos, oracle.hit, oracle.index, oracle.match_len,
                    got.hit, got.index, got.match_len);
        }
        if (!oke) {
            failures++;
            fprintf(stderr, "FAIL(e) %s pos=%zu: oracle hit=%d idx=%d len=%d, vm-walk hit=%d idx=%d len=%d frames=%lld deferred=%d\n",
                    label, pos, oracle.hit, oracle.index, oracle.match_len,
                    gote.hit, gote.index, gote.match_len, ce.frames, ce.deferred_seen);
        }
    }
    trie_free(t);
    fprintf(stderr, "ok  %s (%s) checked %zu positions [(e): total_frames=%lld max_deferred=%d]\n",
            label, subject, slen + 1, total_frames, max_deferred);
}

/* Build a BranchSet directly (bypassing the file loader) so we can give
 * branch 0 and 2 a genuine 2-member, non-fold class ([ab]) that partially
 * OVERLAPS branch 1's [bc] -- rule 2's hazard, never produced by this
 * study's bench-derived literal/ci inputs. */
static BranchSet *build_overlap_case(void)
{
    BranchSet *bs = calloc(1, sizeof *bs);
    bs->n = 3;
    bs->br = calloc(3, sizeof(Branch));
    strcpy(bs->name, "overlap");
    strcpy(bs->mode, "literal");

    /* branch 0: [ab]p */
    bs->br[0].index = 0; bs->br[0].len = 2;
    bs->br[0].seq = calloc(2, sizeof(ByteSet));
    bs_add(&bs->br[0].seq[0], 'a'); bs_add(&bs->br[0].seq[0], 'b');
    bs_add(&bs->br[0].seq[1], 'p');

    /* branch 1: [bc]x */
    bs->br[1].index = 1; bs->br[1].len = 2;
    bs->br[1].seq = calloc(2, sizeof(ByteSet));
    bs_add(&bs->br[1].seq[0], 'b'); bs_add(&bs->br[1].seq[0], 'c');
    bs_add(&bs->br[1].seq[1], 'x');

    /* branch 2: [ab]xy */
    bs->br[2].index = 2; bs->br[2].len = 3;
    bs->br[2].seq = calloc(3, sizeof(ByteSet));
    bs_add(&bs->br[2].seq[0], 'a'); bs_add(&bs->br[2].seq[0], 'b');
    bs_add(&bs->br[2].seq[1], 'x');
    bs_add(&bs->br[2].seq[2], 'y');

    return bs;
}

int main(void)
{
    /* nfa.c:192 counter-example 1 (rule 1): abc|a|abd on "abd" -> [0,1) --
     * the "a" branch (index 1) wins even though "abd" (index 2) also
     * matches and is longer, because index 1 < index 2 and leftmost-first
     * is about INDEX, not length. */
    {
        BranchSet *bs = bset_load("tests/patterns/case1_abc_a_abd.branches");
        check_case("nfa.c rule1 (abc|a|abd)", bs, "abd");
        /* cross-check the literal nfa.c-stated span, both (c) and (e) */
        Cost c = {0,0,0,0}, ce = {0,0,0,0}; int cand[64], ncand;
        Trie *t = trie_build_from(bs);
        Answer a = trie_dispatch(t, bs, (const unsigned char *)"abd", 3, 0, &c, cand, 64, &ncand);
        if (!(a.hit && a.index == 1 && a.match_len == 1)) {
            failures++;
            fprintf(stderr, "FAIL nfa.c rule1 span: expected index=1 len=1, got hit=%d index=%d len=%d\n",
                    a.hit, a.index, a.match_len);
        }
        Answer ae = trie_dispatch_vm(t, bs, (const unsigned char *)"abd", 3, 0, &ce);
        if (!(ae.hit && ae.index == 1 && ae.match_len == 1)) {
            failures++;
            fprintf(stderr, "FAIL(e) nfa.c rule1 span: expected index=1 len=1, got hit=%d index=%d len=%d\n",
                    ae.hit, ae.index, ae.match_len);
        }
        fprintf(stderr, "    (e) on \"abd\": frames=%lld deferred_seen=%d (expect: defer \"a\"@depth1 index1, "
                "commit \"abd\"@depth3 index2 fails subtree_min so it ALSO defers here since branch \"abc\" "
                "index0 is not on this subject's path -- the walk dies at depth3 with only deferred candidates, "
                "so the post-walk fallback fires: min({1,2})=1)\n", ce.frames, ce.deferred_seen);
        trie_free(t);
        check_case("nfa.c rule1 (abc|a|abd) on abc", bs, "abc");
        check_case("nfa.c rule1 (abc|a|abd) on abx", bs, "abx");
        bset_free(bs);
    }

    /* nfa.c:192 counter-example 2 (rule 2): [ab]p|[bc]x|[ab]xy on "bxy" ->
     * [0,2) -- [ab] and [bc] OVERLAP on 'b', so they cannot be reordered or
     * merged; this study's trie DECLINES this node (see algo_trie.c) and
     * the decline fallback must still answer exactly. */
    {
        BranchSet *bs = build_overlap_case();
        check_case("nfa.c rule2 ([ab]p|[bc]x|[ab]xy) on bxy", bs, "bxy");
        Cost c = {0,0,0,0}; int cand[64], ncand;
        Trie *t = trie_build_from(bs);
        Answer a = trie_dispatch(t, bs, (const unsigned char *)"bxy", 3, 0, &c, cand, 64, &ncand);
        if (!(a.hit && a.index == 1 && a.match_len == 2)) {
            failures++;
            fprintf(stderr, "FAIL nfa.c rule2 span: expected index=1 len=2, got hit=%d index=%d len=%d\n",
                    a.hit, a.index, a.match_len);
        }
        trie_free(t);
        check_case("nfa.c rule2 case on axy", bs, "axy");
        check_case("nfa.c rule2 case on cx", bs, "cx");
        bset_free(bs);
    }

    /* a wide, ordinary case: sh1-64 (bench-derived, all sharing 'k') over
     * its own field-hit subject plus a synthetic sweep, to catch anything
     * the two hand-picked adversarial cases miss. */
    {
        BranchSet *bs = bset_load("patterns/sh1-64.branches");
        check_case("sh1-64 over its own words joined", bs, "kszkukugrerswjkbslpglukneNOPE");
        bset_free(bs);
    }

    if (failures) {
        fprintf(stderr, "\n%d FAILURE(S)\n", failures);
        return 1;
    }
    fprintf(stderr, "\nall unit_trie checks passed\n");
    return 0;
}
