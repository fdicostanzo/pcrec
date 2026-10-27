/* tests/code/poison.h — S-IC30's witness (docs/design/inline_c.md §3.3,
 * [r1 A8]): a user header that would break the MATCHER if it were emitted
 * before it. It poisons identifiers generated matchers use and segments do
 * not, so an artifact compiles only when its `code-header` lines come after
 * the matcher. */
#pragma GCC poison memchr memcmp memcpy
