# S-U12 ([M5.0] stage 5) -- THE BARE SPELLING IS NOT THE SCRIPT PROPERTY.
#
# THE CLAIM, measured three ways before it was built: `\p{Greek}` denotes
# `Script | Script_Extensions` and only `\p{sc=Greek}` denotes `Script` alone.
# libpcre2 10.42, 10.46 (the reference) and 10.48 all agree, and
# `man pcre2pattern`'s "Script properties for \p and \P" states it outright
# ("If a script name is given without a property type ... it is treated as
# \p{scx:Adlam}"). U+0342 COMBINING GREEK PERISPOMENI is the discriminating
# code point: `Script=Inherited`, `Script_Extensions={Grek}`.
#
# WHY THE ROW EXISTS. This is the ONE fact of stage 5 that an implementation
# can get wrong while looking entirely correct, and `utf8_design.md` §3.4
# predicts exactly the wrong build -- "one more UCD file, ~160 names; nothing
# structural, purely table weight" describes a generator that reads
# `Scripts.txt` and wires every spelling to it. That build compiles every
# script name, refuses none, passes every refusal pin, passes the name-set
# check in both directions, and answers a SMALLER SET than PCRE2 for 151 of
# the 171 values. Nothing structural can see it; only a membership cell over
# a code point whose scx differs from its sc can.
#
# THE SABOTAGE deletes the namespace test from `uprops_lookup`, which is the
# minimal edit with that effect rather than an invented one: the generated
# table is sorted by (name, namespace) and the `sc=` row (namespace 2) sorts
# before the bare/`scx=` row (namespace 5), so with the mask ignored the FIRST
# matching row wins and every bare spelling silently becomes the strict Script
# set. `\p{sc=X}` still answers correctly, which is what makes it silent: the
# two spellings simply stop disagreeing.
SAB_ID="S-U12-bare-namespace-is-script"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="uprops_lookup ignores the namespace mask, so a bare \\p{Greek} answers the strict Script set instead of Script|Script_Extensions and a code point whose scx names Greek stops matching"
SAB_DOC_FIGURE="MEASURED solo 2026-09-09 at the stage-5 landing: 1763 passed / 10 FAILED over tests/utf8/ -- 1,773 cases total, so the clean run is 1773/0 (DERIVED from this run's own two numbers; the lane's separate clean run is in its report) -- and all ten failures are in axis12_scripts.rxt -- no other file in the directory can see it, which is the point of the row. Zero compile failures: the sabotage changes a LANGUAGE, not a refusal."
# THE REACH QUESTION is whether the two namespaces can still DISAGREE at all:
# a tree where every script's two sets were equal would make this sabotage a
# no-op, and the probe asks the compiler directly rather than asserting it.
# `\p{Greek}` must compile and its artifact must NOT be the empty-language one
# `\p{sc=Greek}` produces under `byte` -- so the probe compiles the bare form
# under `byte`, where the ONLY member is U+00B7 and its presence is exactly
# the Script_Extensions contribution this row defends.
SAB_REACH='"$PCREC" --features unicode-props -e byte -p rx -o - -- "\p{Greek}"'
SAB_REACH_EXPECT='Pattern: \p{Greek} */'
SAB_REACH_POP='tests/utf8/axis12_scripts.rxt|^pattern \\p\{Greek\}|2'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!(pcrec_uprop_names[i].ns & ns)) continue;'
SAB_AFTER='        /* SABOTAGE S-U12: the namespace mask is ignored, so the
         * first row with this NAME wins whatever axis was asked for. */'
