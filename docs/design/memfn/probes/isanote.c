/* memfn R1b loader probe (Linux x86-64 only): what does the dynamic loader
 * ENFORCE about an x86 ISA-level marker, GNU_PROPERTY_X86_ISA_1_NEEDED?
 * Driven by isanote.sh; see isa_selection.md §1.3.
 *
 *   -DNOTE_BITS=N   embed the marker from C source (top-level asm), the way
 *                   an emitted artifact could carry its own: ISA_1_NEEDED =
 *                   N, bit 0 baseline, 1 v2, 2 v3, 3 v4
 *   -DUSE_AVX512    execute one EVEX instruction first: the no-check control
 *                   (SIGILL on a CPU without AVX-512)
 *   -DLIB           build as a shared object exporting isanote_lib()
 *   -DDLOPEN        main dlopen()s argv[1] and reports the loader's verdict
 */
#include <stdio.h>
#define XSTR(x) STR(x)
#define STR(x) #x

#ifdef NOTE_BITS
__asm__(".pushsection .note.gnu.property,\"a\",@note\n\t"
        ".p2align 3\n\t"
        ".long 4\n\t"            /* n_namesz */
        ".long 16\n\t"           /* n_descsz: one 8-byte-padded property */
        ".long 5\n\t"            /* NT_GNU_PROPERTY_TYPE_0 */
        ".asciz \"GNU\"\n\t"
        ".long 0xc0008002\n\t"   /* GNU_PROPERTY_X86_ISA_1_NEEDED */
        ".long 4\n\t"
        ".long " XSTR(NOTE_BITS) "\n\t"
        ".long 0\n\t"
        ".popsection");
#endif

#ifdef LIB
int isanote_lib(void) { return 42; }
#else
#ifdef DLOPEN
#include <dlfcn.h>
#endif
int main(int argc, char **argv)
{
    (void)argc, (void)argv;
#ifdef USE_AVX512
    __asm__ volatile("vpxord %%zmm0, %%zmm0, %%zmm0" ::: "xmm0");
#endif
#ifdef DLOPEN
    void *h = dlopen(argv[1], RTLD_NOW);
    if (!h) {
        printf("dlopen refused: %s\n", dlerror());
        return 4;
    }
    printf("dlopen ok\n");
    return 0;
#else
    printf("ran\n");
    return 0;
#endif
}
#endif
