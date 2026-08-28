# S186 (S-OPTK2) — [OPT-K] THE OFFSET-k SKIP LANDS WITHOUT RE-SEEDING THE
# MACHINE, AND `\b` THEN MATCHES AFTER A WORD CHARACTER.
#
# `docs/design/offset_k_skip.md` §2.1 and §5.4, and this is the ONE place in
# the whole mechanism where a wrong answer is reachable.
#
# `\b`'s truth reads the byte to the LEFT, and pcrec carries that in the DFA
# STATE'S IDENTITY rather than in a field — which is why the forward start
# state escapes on every word character, not because a match can begin there
# but because the machine must REMEMBER that the previous byte was one. The
# offset-k skip is the first scan-avoidance mechanism in this compiler that
# jumps over bytes which LEAVE the start state, so it is the first that has
# to put that context back: on landing it re-seeds from `s[cand-1]` through
# the same `<M>_seed_state` table the search's own initializer uses.
#
# Delete the reseed and the machine lands in the NO-CONTEXT start state, which
# is the state meaning "there is no byte to my left" — so a leading `\b`
# evaluates TRUE after a word character and the artifact reports a match PCRE2
# does not. It is a FALSE MATCH, the worst direction, and it is invisible to
# every `m` cell in the tree: a skip that lost its context still finds every
# match that is genuinely there.
#
# THE DETECTOR IS TWO INSTRUMENTS AND NEITHER IS REDUNDANT.
# `tests/offsetskip/offset_skip.rxt` §6 is four `n` rows whose subjects differ
# from a matching one by a single leading word character; they say an ANSWER
# is wrong. `tests/codegen/run_offset_skip.sh` §2b reads the emitted reseed
# line on a seeded machine; it says WHICH LINE. The corpus rows came first and
# are the ones that would survive a rewrite of the emitter.
SAB_ID="S186-ofsskip-no-reseed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/offset_skip.rxt"
SAB_DESC="the emitted offset-k skip does not re-seed the DFA state from s[cand-1] when it lands, so a machine carrying a word context (\\b) evaluates the assertion in the no-context start state and reports a FALSE MATCH after a word character"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-28, lane optk): DETECTED against a clean 19pass/0fail + 80pass/0fail baseline -- offsetskip:1fail/18pass (S2b alone, the check localising), corpus:1fail/79pass, and the corpus case is a FALSE MATCH."
SAB_COUNT=1
SAB_BEFORE='    if (!dfa_needs_seed(f->d)) return;'
SAB_AFTER='    if (1 || !dfa_needs_seed(f->d)) return;   /* SABOTAGE S186 */'
