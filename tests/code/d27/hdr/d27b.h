/* d27 code-header fixture: must follow d27a.h ("in order", cli.md §1.22¶2). */
#ifndef D27A_SEVEN
#error "d27b.h included before d27a.h: code-header order not kept"
#endif
static inline int d27_b(void) { return D27A_SEVEN + 1; }
