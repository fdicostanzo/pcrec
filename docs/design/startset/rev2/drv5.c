/* [START-SET] rev 2: five-artifact differential -- base (rx) against the
 * narrowed+re-seeded twins c_ (T = S & E, the r3 note's), a_ (T = S & E*),
 * b_ (T = S) and d_ (T = Tdfa, the machine's own floor) -- every subject
 * line, every startpos, the full capture vector.  It also accumulates THE
 * START-BYTE ORACLE: the byte at the start of every non-empty match base
 * reports (and, with -DWITH_PCRE2, every match local libpcre2 reports),
 * printed as a 256-bit hex set for the caller to check against each T.
 * Subjects: one per line, \xHH escapes decoded (so '\n' and high bytes reach). */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "rx.h"
#include "c_.h"
#include "a_.h"
#include "b_.h"
#include "d_.h"
#ifdef WITH_PCRE2
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#endif
int main(int argc, char **argv) { char line[512]; long cases = 0, m = 0, dc = 0, da = 0, db = 0, dd = 0, pd = 0; unsigned char obs[32] = {0}, pobs[32] = {0};
#ifdef WITH_PCRE2
  int utf = argc > 2 && !strncmp(argv[2], "utf8", 4); int en; PCRE2_SIZE eo;
  pcre2_code *re = pcre2_compile((PCRE2_SPTR)argv[1], PCRE2_ZERO_TERMINATED, utf ? (PCRE2_UTF | PCRE2_MATCH_INVALID_UTF) : 0, &en, &eo, NULL);
  if (!re) { printf("pcre2 compile fail %d\n", en); return 2; }
  pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
#else
  (void)argc; (void)argv;
#endif
  while (fgets(line, sizeof line, stdin)) { size_t n = strlen(line); if (n && line[n-1] == '\n') line[--n] = 0;
    unsigned char sb[512]; size_t k = 0; for (char *p = line; *p;) { if (p[0] == 0x5c && p[1] == 0x78) { unsigned v; sscanf(p+2, "%2x", &v); sb[k++] = v; p += 4; } else sb[k++] = (unsigned char)*p++; } n = k; const unsigned char *s = sb;
    for (size_t f = 0; f <= n; f++) { ptrdiff_t o[RX_NCAPS][2], c[RX_NCAPS][2], a[RX_NCAPS][2], b[RX_NCAPS][2], d[RX_NCAPS][2];
      memset(o, 0xff, sizeof o); memset(c, 0xff, sizeof c); memset(a, 0xff, sizeof a); memset(b, 0xff, sizeof b); memset(d, 0xff, sizeof d);
      int r0 = rx_search(s, n, f, o), rc = c__search(s, n, f, c), ra = a__search(s, n, f, a), rb = b__search(s, n, f, b), rd = d__search(s, n, f, d); cases++;
      if (r0 == 1) { m++; if (o[0][1] > o[0][0]) obs[s[o[0][0]] >> 3] |= 1u << (s[o[0][0]] & 7); }
#define CMP(r, x, cnt, tag) if (r0 != r || (r0 == 1 && memcmp(o, x, sizeof o))) { if (cnt < 2) printf("  %s [%s]@%zu base=%d(%td,%td) twin=%d(%td,%td)\n", tag, line, f, r0, o[0][0], o[0][1], r, x[0][0], x[0][1]); cnt++; }
      CMP(rc, c, dc, "cur") CMP(ra, a, da, "a") CMP(rb, b, db, "b") CMP(rd, d, dd, "dfa")
#ifdef WITH_PCRE2
      int pr = pcre2_match(re, s, n, f, 0, md, NULL); PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
      if (pr > 0 && ov[1] > ov[0]) pobs[s[ov[0]] >> 3] |= 1u << (s[ov[0]] & 7);
      if ((pr > 0) != (r0 == 1) || (pr > 0 && (o[0][0] != (ptrdiff_t)ov[0] || o[0][1] != (ptrdiff_t)ov[1]))) { if (pd < 2) printf("  PCRE2 [%s]@%zu base=%d pcre2=%d\n", line, f, r0, pr); pd++; }
#endif
    } }
  printf("cases=%ld matches=%ld cur_diffs=%ld a_diffs=%ld b_diffs=%ld dfa_diffs=%ld", cases, m, dc, da, db, dd);
#ifdef WITH_PCRE2
  printf(" pcre2_vs_base=%ld", pd);
#endif
  printf(" obs="); for (int i = 0; i < 32; i++) printf("%02x", obs[i]);
  printf(" pobs="); for (int i = 0; i < 32; i++) printf("%02x", pobs[i]);
  printf("\n"); return 0; }
