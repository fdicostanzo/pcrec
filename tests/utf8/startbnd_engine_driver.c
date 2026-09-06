/* tests/utf8/startbnd_engine_driver.c — [K50] §5's single-cell driver.
 *
 * One artifact, one subject, one startpos, one line of output — the answer in
 * the same spelling `docs/design/utf8_measurements/out/startbnd.txt` prints,
 * so a cell's expectation in `run_startbnd_diff.sh` is COPIED from the
 * reference transcript rather than reworded on the way in.
 *
 * Deliberately separate from `startbnd_driver.c`: that one links TWO arms and
 * compares them to each other, which cannot check a fix that has no flag.
 * This one links ONE artifact and its expectations come from libpcre2 10.46.
 */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#include "engine.h"

int main(int argc, char **argv)
{
    unsigned char subj[512];
    size_t n = 0;
    ptrdiff_t caps[1][2];
    int rc;

    if (argc != 3) {
        fprintf(stderr, "usage: startbnd_engine_driver HEXSUBJECT STARTPOS\n");
        return 2;
    }
    for (const char *h = argv[1]; h[0] && h[1] && n < sizeof subj; h += 2) {
        char t[3];
        t[0] = h[0]; t[1] = h[1]; t[2] = 0;
        subj[n++] = (unsigned char)strtoul(t, NULL, 16);
    }

    rc = e_search(subj, n, (size_t)strtoul(argv[2], NULL, 10), caps);
    if (rc == 1)      printf("(%td,%td)\n", caps[0][0], caps[0][1]);
    else if (rc == 0) printf("no-match\n");
    else              printf("rc=%d\n", rc);
    return 0;
}
