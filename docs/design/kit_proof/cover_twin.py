"""SIZE-ONLY hand twin for kit_proof.md §2.3: rewrites an artifact's `rx_search` into
the `cover` entry (one kit candidate, then FIN2's report), keeping every other byte.

Usage: python3 -I cover_twin.py IN.c OUT.c SITE_FN WIDTH
  e.g. build/pcrec -p rx -o lit.c --pattern foobar
       python3 -I cover_twin.py lit.c lit_cover.c rx_ofsskip 6
Answer-correct only where the site already proves every position (foobar's run-pinned
site compares all six bytes today); never timed. Prefix `rx` only.
"""
import sys

src_path, out_path, site_fn, width = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
src = open(src_path).read()
head = 'int rx_search(const unsigned char *subject'
a = src.index(head)
b = src.index('\n}\n', a) + 3
body = f'''int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])
{{
    if (search_from > subject_length) return 0;
    size_t cand = {site_fn}(subject, subject_length, search_from);
    if (cand >= subject_length) return 0;
    if (capture_spans) {{ capture_spans[0][0] = (ptrdiff_t)cand; capture_spans[0][1] = (ptrdiff_t)(cand + {width}); }}
    return 1;
}}
'''
open(out_path, 'w').write(src[:a] + body + src[b:])
