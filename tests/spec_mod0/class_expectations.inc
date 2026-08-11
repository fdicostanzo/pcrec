/* class_expectations.inc — the measured class-position expectation of every
 * class-reachable registry row, plus the endpoint-adjacent delimiter-eater
 * probes. Included by check04_class_position.c.
 *
 * Vocabulary (two-valued, as the invariant states it):
 *   "err N"      the class does not compile, with this PCRE2 error number
 *   "char 0xNN"  it compiles and denotes exactly this one character
 *   "set N"      it compiles and denotes N of the 256 byte values
 *
 * Measured 2026-08-11 against libpcre2 10.46 by running the check with
 * --emit-pins. A row whose value moves fails in EITHER direction, so
 * regenerating this file is a deliberate act that a reviewer sees as a diff.
 * Censuses are 8-bit and non-UTF.
 *
 * Backslashes are doubled because this is C source; the emitter does that, so
 * regenerate with --emit-pins rather than hand-editing.
 */

/* --- the 44 class-reachable rows (41 esc + 3 class-bracket) ------------- */
{ "\\d", "set 10" },
{ "\\D", "set 246" },
{ "\\s", "set 6" },
{ "\\S", "set 250" },
{ "\\w", "set 63" },
{ "\\W", "set 193" },
{ "\\h", "set 3" },
{ "\\H", "set 253" },
{ "\\v", "set 5" },
{ "\\V", "set 251" },
{ "\\N", "err 171" },
{ "\\N{name}", "err 137" },
{ "\\N{U+0041}", "err 193" },
{ "\\b", "char 0x08" },
{ "\\B", "err 107" },
{ "\\A", "err 107" },
{ "\\Z", "err 107" },
{ "\\z", "err 107" },
{ "\\G", "err 107" },
{ "\\K", "err 107" },
{ "\\k<name>", "set 7" },
{ "\\g{-1}", "err 108" },
{ "\\p{L}", "set 117" },
{ "\\P{L}", "set 139" },
{ "\\Q", "err 106" },
{ "\\E", "err 106" },
{ "\\R", "err 107" },
{ "\\X", "err 107" },
{ "\\C", "err 107" },
{ "\\cX", "char 0x18" },
{ "\\o{101}", "char 0x41" },
{ "\\0", "char 0x00" },
{ "\\1", "char 0x01" },
{ "\\2", "char 0x02" },
{ "\\3", "char 0x03" },
{ "\\4", "char 0x04" },
{ "\\5", "char 0x05" },
{ "\\6", "char 0x06" },
{ "\\7", "char 0x07" },
{ "\\8", "char 0x38" },
{ "\\9", "char 0x39" },
{ "[:alpha:]", "set 52" },
{ "[.a.]", "err 113" },
{ "[=a=]", "err 113" },

/* --- endpoint-adjacent probes for the three delimiter-eaters ------------
 * Truncated and mis-delimited forms: this is where an unbounded scan for the
 * closing delimiter runs off the end of the class and swallows the ']'.
 * `[[.a.]~]` and `[~[.a.]]` are err 113 while `[[:alpha:]~]` is a 52-member
 * set, which is the collating-element rows being recognised-and-refused where
 * the POSIX-class row is recognised-and-supported. */
{ "[:alpha:", "err 106" },
{ "[:alpha", "set 6" },
{ "[:", "set 2" },
{ "[:]", "set 0" },
{ "[:alpha:]~", "set 53" },
{ "~[:alpha:]", "set 53" },
{ "[.a.", "err 113" },
{ "[.a", "set 3" },
{ "[.", "set 2" },
{ "[.]", "set 0" },
{ "[.a.]~", "err 113" },
{ "~[.a.]", "err 113" },
{ "[=a=", "err 113" },
{ "[=a", "set 3" },
{ "[=", "set 2" },
{ "[=]", "set 0" },
{ "[=a=]~", "err 113" },
{ "~[=a=]", "err 113" },
{ "[:^digit:]", "set 246" },
{ "[:<:]", "set 0" },
{ "[:foo:]", "err 130" },
{ "[:al:pha:]", "err 130" },
