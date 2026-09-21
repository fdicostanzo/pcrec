/* examples/makefile — a tiny consumer of the three matchers built from
 * src/*.rxt. Links against libmatchers.a; nothing here depends on pcrec
 * itself, only on the two generated headers. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>

#include "greet.h"
#include "digits.h"

static void try_greet(const char *s)
{
    size_t n = strlen(s);
    ptrdiff_t caps[GREET_NCAPS][2];
    int rc = greet_search((const unsigned char *)s, n, 0, caps);
    if (rc == 1)
        printf("greet:  %-20s -> match [%td,%td), name=[%td,%td)\n",
               s, caps[0][0], caps[0][1], caps[1][0], caps[1][1]);
    else
        printf("greet:  %-20s -> no match\n", s);
}

static void try_digits(const char *s)
{
    size_t n = strlen(s);
    int rc = digits_search((const unsigned char *)s, n, 0, NULL);
    printf("digits: %-20s -> %s\n", s, rc == 1 ? "match" : "no match");
}

int main(void)
{
    try_greet("hello, World!");
    try_greet("goodbye, World!");
    try_digits("12345");
    try_digits("abcde");
    return 0;
}
