/* [START-SET] rev 2: THE START-BYTE ORACLE for the VM hat (review r4
 * checks-F2 (b)).  One artifact (rx), every subject line (\xHH decoded), every
 * startpos: the byte at the start of every non-empty match the artifact
 * reports, and (with -DWITH_PCRE2) every one local libpcre2 reports, as two
 * 256-bit hex sets, plus the artifact-vs-libpcre2 disagreement count. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "rx.h"
#ifdef WITH_PCRE2
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#endif
int main(int argc, char **argv) { char line[512]; long cases = 0, m = 0, pd = 0, gu = 0; unsigned char obs[32] = {0}, pobs[32] = {0};
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
    for (size_t f = 0; f <= n; f++) { ptrdiff_t o[RX_NCAPS][2]; memset(o, 0xff, sizeof o);
      int r0 = rx_search(s, n, f, o); cases++; if (r0 < 0) gu++;
      if (r0 == 1) { m++; if (o[0][1] > o[0][0]) obs[s[o[0][0]] >> 3] |= 1u << (s[o[0][0]] & 7); }
#ifdef WITH_PCRE2
      int pr = pcre2_match(re, s, n, f, 0, md, NULL); PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
      if (pr > 0 && ov[1] > ov[0]) pobs[s[ov[0]] >> 3] |= 1u << (s[ov[0]] & 7);
      if (r0 >= 0 && ((pr > 0) != (r0 == 1) || (pr > 0 && (o[0][0] != (ptrdiff_t)ov[0] || o[0][1] != (ptrdiff_t)ov[1])))) pd++;
#endif
    } }
  printf("cases=%ld matches=%ld giveups=%ld pcre2_vs_base=%ld obs=", cases, m, gu, pd);
  for (int i = 0; i < 32; i++) printf("%02x", obs[i]);
  printf(" pobs="); for (int i = 0; i < 32; i++) printf("%02x", pobs[i]);
  printf("\n"); return 0; }
