#!/usr/bin/env python3
"""gen_subjects.py -- reproducible subject generator for the email specimen
measurement. Writes each subject as its own binary file under subjects/,
plus a manifest.tsv (id, byte-length, description). Deterministic: no
randomness, so re-running reproduces the identical file set (diff empty).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "subjects")
os.makedirs(OUT, exist_ok=True)

subjects = []  # list of (desc, bytes)


def add(desc, b):
    if isinstance(b, str):
        b = b.encode("latin-1")
    subjects.append((desc, b))


# ---------------------------------------------------------------------
# valid: dotted local parts
# ---------------------------------------------------------------------
add("valid dot-atom simple", "user@example.com")
add("valid dot-atom multi-label domain", "a.b.c@sub.example.org")
add("valid dot-atom single-char local", "a@b.co")
add("valid dot-atom many dots", "a.b.c.d.e.f@example.com")
add("valid dot-atom with allowed specials", "u!#$%&'*+/=?^_`{|}~-x@example.com")
add("valid dot-atom two-label domain minimal", "x@e.co")
add("valid dot-atom single-char labels chained", "x@a.b.c.d.e.com")
add("valid dot-atom local with digits", "user123.456@example99.com")
add("valid dot-atom label with internal hyphen", "user@my-example.com")
add("valid dot-atom label with internal hyphens", "user@a-b-c.com")
add("valid dot-atom TLD single char label", "user@example.c")

# ---------------------------------------------------------------------
# valid: quoted local parts with escapes
# ---------------------------------------------------------------------
add("valid quoted simple", '"john doe"@example.com')
add("valid quoted with escaped quote", '"a\\"b"@example.com')
add("valid quoted with escaped backslash", '"a\\\\b"@example.com')
add("valid quoted empty", '""@example.com')
add("valid quoted with control char 0x01", '"a\x01b"@example.com')
add("valid quoted with tab 0x09 (in qchar range)", '"a\x09b"@example.com')
add("valid quoted with escaped 0x00-adjacent \\x09", '"a\\\x09b"@example.com')
add("valid quoted with 0x7f (DEL, in qchar range)", '"a\x7fb"@example.com')
add("valid quoted with escaped high byte \\xff", '"a\\\xffb"@example.com')
add("valid quoted with many escaped quotes", '"\\"\\"\\""@example.com')

# ---------------------------------------------------------------------
# valid: IPv4 address literals
# ---------------------------------------------------------------------
add("valid IPv4 literal all-zero", "user@[0.0.0.0]")
add("valid IPv4 literal max", "user@[255.255.255.255]")
add("valid IPv4 literal typical", "user@[192.168.1.1]")
add("valid IPv4 literal single-digit octets", "user@[1.2.3.4]")
add("valid IPv4 literal two-digit octets", "user@[10.20.30.40]")
add("valid IPv4 literal boundary 250-255", "user@[250.251.252.253]")
add("valid IPv4 literal 199 (2xx form)", "user@[199.199.199.199]")

# ---------------------------------------------------------------------
# valid: bracket general-address-literal form (label:chars)
# ---------------------------------------------------------------------
add("valid bracket general form ascii tag", "user@[abc:xyz]")
add("valid bracket general form IPv6-ish tag", "user@[IPv6:0102030405060708]".lower())
add("valid bracket general form single-char tag", "user@[a:bcdef]")
add("valid bracket general form with hyphen in tag", "user@[a-b-c:xyz123]")

# ---------------------------------------------------------------------
# invalid: near each boundary
# ---------------------------------------------------------------------
add("invalid IPv4 octet 256", "user@[256.1.1.1]")
add("invalid IPv4 octet 999", "user@[999.1.1.1]")
add("invalid IPv4 too few octets", "user@[1.2.3]")
add("invalid IPv4 too many octets", "user@[1.2.3.4.5]")
add("invalid label leading hyphen", "user@-example.com")
add("invalid label leading hyphen second label", "user@a.-b.com")
add("invalid label trailing hyphen", "user@example-.com")
add("invalid unescaped quote inside quoted string", '"a"b"@example.com')
add("invalid missing @ entirely", "userexample.com")
add("invalid empty local part", "@example.com")
add("invalid empty domain", "user@")
add("invalid double dot in local part", "user..name@example.com")
add("invalid leading dot in local part", ".user@example.com")
add("invalid trailing dot in local part", "user.@example.com")
add("invalid domain single label no dot", "user@example")
add("invalid bracket unclosed", "user@[1.2.3.4")
add("invalid bracket empty", "user@[]")
add("invalid space in local part unquoted", "user name@example.com")
add("invalid at-sign in domain", "user@ex@ample.com")
add("invalid control char 0x00 unquoted", "user\x00name@example.com")

# ---------------------------------------------------------------------
# near-miss address-literal / qchar-vs-other-class boundary
# ---------------------------------------------------------------------
add("bracket general form: byte 0x20 (excluded from both classes)",
    "user@[a:b c]")
add("bracket general form: byte 0x52 'R' (excluded from [\\x21-\\x5a\\x53-\\x7f])",
    "user@[a:" + chr(0x52) + "]")
add("bracket general form: byte 0x53 'S' (included, class boundary)",
    "user@[a:" + chr(0x53) + "]")
add("bracket general form: byte 0x5a 'Z' (included, class boundary)",
    "user@[a:" + chr(0x5a) + "]")
add("bracket general form: byte 0x21 '!' (included, class boundary)",
    "user@[a:" + chr(0x21) + "]")

# ---------------------------------------------------------------------
# pathological / long
# ---------------------------------------------------------------------
add("pathological: 10KB local part of atom chars", ("a" * 10240) + "@example.com")
add("pathological: 2000-deep dotted local part a.a.a...", ("a." * 2000)[:-1] + "@example.com")
add("pathological: 5KB quoted string of qchars", '"' + ("a" * 5120) + '"@example.com')
add("pathological: 10KB local part, no @ (forces full scan, nomatch)", "a" * 10240)
add("pathological: long domain, many labels", "user@" + ".".join(["lbl"] * 500) + ".com")
add("pathological: long IPv4-literal-shaped garbage", "user@[" + "9" * 500 + ".1.1.1]")
add("pathological: 5KB quoted string with trailing unescaped quote mid-string",
    '"' + ("a" * 2560) + '"' + ("b" * 2560) + '"@example.com')
add("pathological: alternating escaped chars in quoted string, 4KB",
    '"' + ("\\a" * 2048) + '"@example.com')

# ---------------------------------------------------------------------
# a few more valid/invalid variety for coverage (>=60 total)
# ---------------------------------------------------------------------
add("valid: mixed-case local+domain (pattern is lowercase-only class -> likely no match)",
    "User@Example.COM")
add("valid: uppercase inside quoted string (qchar allows 0x41-0x5a via 0x23-0x5b)",
    '"ABC"@example.com')
add("valid: digits-only domain labels", "user@123.456.com")
add("valid: single-char everything", "a@b.c")
add("invalid: two @ signs", "user@@example.com")
add("invalid: local part exactly one specials-only char", "!@example.com")
add("valid: local part all specials", "!#$%&'*+/=?^_`{|}~@example.com")
add("invalid: quoted string missing closing quote", '"unterminated@example.com')
add("invalid: bracket form missing tag colon", "user@[abcxyz]")
add("valid: bracket general form tag with digits", "user@[a1b2:tag99]")
add("boundary: IPv4 last octet 25x boundary (250)", "user@[1.1.1.250]")
add("boundary: IPv4 last octet exactly 255", "user@[1.1.1.255]")
add("boundary: IPv4 octet exactly 199", "user@[199.1.1.1]")
add("boundary: IPv4 octet 200 (2[0-4][0-9] branch)", "user@[200.1.1.1]")
add("boundary: IPv4 octet 249 (2[0-4][0-9] branch top)", "user@[249.1.1.1]")
add("boundary: IPv4 octet 260 invalid (exceeds all branches)", "user@[260.1.1.1]")
add("empty subject", "")
add("just @ sign", "@")
add("no match: random prose", "the quick brown fox jumps over the lazy dog")
add("no match: digits only", "1234567890")

manifest_path = os.path.join(OUT, "manifest.tsv")
with open(manifest_path, "w", encoding="latin-1") as mf:
    mf.write("id\tlen\tdescription\n")
    for i, (desc, b) in enumerate(subjects):
        fn = os.path.join(OUT, "%03d.bin" % i)
        with open(fn, "wb") as f:
            f.write(b)
        mf.write("%03d\t%d\t%s\n" % (i, len(b), desc))

print("wrote %d subjects to %s" % (len(subjects), OUT))
