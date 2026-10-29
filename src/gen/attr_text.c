/* src/gen/attr_text.c — [ATTR-TABLE] THE ONE VALUE-TO-GUARDED-TEXT TABLE
 * (docs/dev/plan_completed.md [ATTR-TABLE]; review r1 of E1, F1/F2 and the family
 * lens L7).
 *
 * Every emitter that writes a function-linkage attribute into an artifact
 * asks this table for the TEXT and keeps its own DECISION:
 *
 *   A1  the VM entry chain (emit_vm.c `vm_plan_entry`): `en.ai` on the thin
 *       helpers, `en.ai_body` on the matcher body (`always_inline` on the
 *       copying rungs, `noinline` on the `shared` rung, none on `plain`);
 *   A2  [OPT-1]'s deep tier (emit_comb.c): `noinline` on `<name>_deep`;
 *   A3  K24's guarded `noclone` on every DFA search head (emit_dfa.c
 *       `emit_search_head`);
 *   A4  `unused` on a code segment's file-local binding (emit_code.c);
 *   A5  `cold noinline` on the VM's trail compaction (emit_vm.c
 *       `vm_emit_trail_compact`);
 *   the part-layout table (part_layout.c): a part row's layout, through
 *       `pcrec_part_attr`.
 *
 * A row is a VALUE, never a writer: two writers that write the same bytes
 * read the same row (A1's `always_inline` and the layout's `inline`; A1's
 * `noinline` and A2's), and two values that render the same bytes but mean
 * different things (`as-emitted`, `auto`, `none`) are distinct rows because
 * their tokens differ. A writer that needed other bytes would get its own
 * row; no spelling here was harmonized, so every artifact is byte-identical
 * to the writers' own text before the move.
 *
 * THE GUARD SHAPE IS STATED ONCE (`ATTR_GUARDED`): an attribute only some
 * compilers have is asked for by `__has_attribute`, with the `#ifndef`
 * fallback definition for a compiler that predates it, so a compiler
 * without the attribute never sees it rather than seeing it and warning
 * under `-Wattributes -Werror` (K24's [CC-CLANG] shape). `ALT` is the
 * `#else` arm's text, or "" for none. */
#include "core/internal.h"

#define ATTR_GUARD_PROLOGUE "#ifndef __has_attribute\n" \
                            "# define __has_attribute(x) 0\n" \
                            "#endif\n"
#define ATTR_GUARDED(attr, alt) ATTR_GUARD_PROLOGUE \
                                "#if __has_attribute(" #attr ")\n" \
                                "__attribute__((" #attr "))\n" \
                                alt \
                                "#endif\n"

/* For each value: its token (the part layout's `--emit-facts` cell), the
 * text its writer puts on the definition head, and what it writes (the
 * part layout's `--list-axes` writes cell). A text that opens a line
 * (`shared`, `noclone`) ends with one, so its writer's next text starts a
 * line. */
static const struct {
    const char *tok, *text, *writes;
} attr_texts[PCREC_ATTR_N] = {
    [PCREC_ATTR_AS_EMITTED] = { "as-emitted", "",
            "the head as its emitter wrote it, unchanged (no attribute added)" },
    [PCREC_ATTR_AUTO] = { "auto", "", "its default layout (no attribute added)" },
    /* `shared` is `noipa` (noinline + noclone + no interprocedural analysis)
     * where the compiler has it and `noinline` where it does not: clang has
     * no `noipa`, and an unguarded one fails its `-Werror`. With `noinline`
     * alone gcc -O1 still reads the body across the call and reports the
     * caller's `window` maybe-uninitialized (a false positive, e1_report.md
     * §7 Q1), and it deletes a part whose body is `return 0;`. It follows
     * the part head's `static `, which therefore ends its line. */
    [PCREC_ATTR_SHARED] = { "shared",
            "\n" ATTR_GUARDED(noipa, "#else\n__attribute__((noinline))\n"),
            "one out-of-line body: noipa where __has_attribute(noipa), else noinline" },
    [PCREC_ATTR_INLINE] = { "inline", "inline __attribute__((always_inline)) ",
            "always_inline into each caller" },
    [PCREC_ATTR_NONE] = { "none", "", "no attribute" },
    [PCREC_ATTR_NOINLINE] = { "noinline", "__attribute__((noinline)) ",
            "one out-of-line body (noinline)" },
    /* K24 (docs/dev/known_issues.md): denies gcc's partial-inlining pass the
     * `.part` clone of a search head. Above the definition, on lines of its
     * own. */
    [PCREC_ATTR_NOCLONE] = { "noclone", ATTR_GUARDED(noclone, ""),
            "no clone of the body: noclone where __has_attribute(noclone), else nothing" },
    /* A code segment's file-local binding (emit_code.c), which no call
     * reads when no match can reach its site (`{0}`, an uncalled DEFINE):
     * `-Wunused-const-variable` would otherwise break a `-Werror` build
     * (review 2026-10-27-r1-ic2 F9). gcc and clang both have it. */
    [PCREC_ATTR_UNUSED] = { "unused", "__attribute__((unused)) ",
            "no unused warning when nothing reads it" },
    /* The VM's trail compaction (emit_vm.c), called only where a full trail
     * would otherwise give up: `cold` sends the call and the function to the
     * unlikely section so the trail write's hot path keeps its shape, and
     * `noinline` keeps its body out of the matcher. gcc and clang both have
     * both. */
    [PCREC_ATTR_COLD] = { "cold", "__attribute__((cold, noinline)) ",
            "one out-of-line body off the hot path (cold, noinline)" },
};

const char *pcrec_attr_text(PcrecAttr a)
{
    return attr_texts[a].text;
}

const char *pcrec_attr_tok(PcrecAttr a)
{
    return attr_texts[a].tok;
}

const char *pcrec_attr_writes(PcrecAttr a)
{
    return attr_texts[a].writes;
}
