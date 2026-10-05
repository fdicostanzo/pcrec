/* memfn R1b: on Darwin/AArch64, (1) does __builtin_cpu_supports answer, and
 * (2) how does each clang lower function multiversioning on Mach-O?
 * Driven by fmvdarwin.sh (isa_selection.md §0 items 3-4). f() has a
 * dotprod version and a default one: f() == 1 means the dispatch picked
 * dotprod, which every M1 has (hw.optional.arm.FEAT_DotProd = 1). */
#include <stdio.h>
__attribute__((target_version("dotprod"))) int f(void) { return 1; }
__attribute__((target_version("default"))) int f(void) { return 0; }
int main(int argc, char **argv)
{
    (void)argv;
    printf("before f(): cpu_supports dotprod=%d simd=%d fp=%d\n",
           __builtin_cpu_supports("dotprod"), __builtin_cpu_supports("simd"),
           __builtin_cpu_supports("fp"));
    int r = argc > 5 ? 0 : f();
    printf("f()=%d; after f(): cpu_supports dotprod=%d simd=%d\n", r,
           __builtin_cpu_supports("dotprod"), __builtin_cpu_supports("simd"));
    return 0;
}
