# `vars` — caller variables in a pattern

**The caller-observable contract for module `vars`.** What a pattern may
spell, what a caller must supply, what the artifact answers, and every way
the module can refuse. Design and reasoning live in
`docs/design/variables_common.md` and `docs/design/variables_pattern.md`;
this page is the promise.

Enable it with `--features vars` (or any set that names it). With the module
off, a pattern containing `${` is refused naming the module — see §6.

## 1. What it is

`^${prefix}-[0-9]+$` compiles **once**, and the caller supplies `prefix`'s
bytes per call. One artifact matches a family of patterns.

**A variable's bytes are matched as themselves. Always.** They are never
parsed as pattern syntax, under any flag, in any mode. A caller who
interpolates untrusted input into `^${prefix}-[0-9]+$` can rely on the user
not being able to write `.*` and widen the language. There is no opt-out, and
there will not be one: a value the caller supplies at MATCH time can never be
pattern syntax, because compiling it would mean running the compiler after
the artifact exists. (Composing a known sub-pattern at COMPILE time is a
different feature and is `--source`/`--lib-path`'s.)

## 2. The spelling

```
    ${ [!] name [ operator word ] }
```

- `name` is `[A-Za-z_][A-Za-z0-9_]*`, at most `PCREC_MAX_VAR_NAME_LEN` bytes
  (`docs/spec/limits.md` §3.6).
- `${!name}` means the same thing as `${name}` in a pattern, and is the
  spelling that means "the caller's variable" in a replacement template too.
- The five operators:

  | form | the value is |
  |---|---|
  | `${name}` | the variable; the call is REFUSED when it is unset (§5) |
  | `${name-w}` | `w` when the variable is UNSET, else the variable |
  | `${name:-w}` | `w` when it is UNSET **or EMPTY**, else the variable |
  | `${name+w}` | `w` when the variable is SET, else nothing |
  | `${name:+w}` | `w` when it is SET **and non-empty**, else nothing |
  | `${name:?w}` | REFUSE the call when it is UNSET or EMPTY |

  The `:` is what folds EMPTY in with UNSET. This is bash's rule unchanged.
- Inside a `word`, a backslash makes the next byte literal — which is how a
  `}` or a `$` is spelled there.
- A `word` may contain ONE nested `${...}` and nothing else, which is the
  fallback chain `${a:-${b}}`. A word that MIXES literal text with a nested
  reference, or nests two, is refused (§6); see the refusal's own text for
  why and what to write instead.
- Nesting is bounded by `PCREC_MAX_VAR_NEST_DEPTH` (`limits.md` §3.6).

A lone `$` is unchanged: it is still the end-of-line assertion, and `${`
becomes a variable only with the module enabled.

## 3. What a caller supplies

```c
typedef struct rx_var {
    const char          *name;  /* NUL-terminated */
    const unsigned char *p;     /* NULL == UNSET; len is then IGNORED */
    size_t               len;   /* bytes; 0 with p != NULL == EMPTY */
} rx_var;
```

**BY NAME, never by index.** An index is meaningful only inside the artifact
that assigned it, and two separately compiled artifacts composed alongside
each other cannot agree what index 0 means. A caller writes:

```c
rx_var vars[] = {
    { "prefix", buf,  n  },
    { "suffix", buf2, n2 },
};
```

and the artifact resolves its own mentioned names against that array, once
per call, before the match begins.

- **UNSET is `p == NULL`; EMPTY is `p != NULL && len == 0`.** They are two
  different states and the `:` operators are what distinguish them.
- A name the artifact does not mention is **ignored**.
- A name the artifact mentions and the array does not carry is **UNSET**.
- A duplicate name in the caller's array: **the first entry wins.**
- `p == NULL` implies `len` is never read.
- A value may contain `0x00`; the length is the contract.
- **Lifetime:** both `name` and `p` must stay valid for the duration of the
  call. Nothing in the generated code detects a violation.

## 4. Where it is passed

- `<prefix>_match` and `<prefix>_match_caps` take **no new parameter**: the
  array rides `rx_ctx` (`ctx->vars`, `ctx->nvars`), so these entries are still
  `rx_matchfn` and a matcher composed as a callout receives the outer call's
  environment because it already receives the outer `ctx`.
- `<prefix>_search` and its `_in` siblings are not `rx_ctx`-shaped, so **on a
  var-bearing artifact only** they gain a trailing `const rx_var *vars,
  size_t nvars` pair, before the `_in` descriptor.
- `rx_info.vars` / `rx_info.nvars` list the names this pattern mentions, in
  first-mention order, for a caller that wants to validate a name before
  calling. Nothing in the match path depends on that check running.
- `<PREFIX>_NVARS` stamps the count.

Concurrent calls are fine provided each has its own `rx_ctx` and its own
`vars` array reachable through it. The artifact holds nothing.

## 5. UNSET at a bare `${name}` is a REFUSED CALL

`PCREC_ERR_UNSET_VAR` is `-8`, **below `PCREC_ERR_FLOOR`**, and it is
`PCREC_ERR_STARTPOS`'s class rather than a give-up: nothing was attempted and
`caps` is untouched. Every give-up in `[PCREC_ERR_FLOOR, -2]` says the engine
tried and ran out; this one says it never started.

It is not an empty match, and the reason is a security boundary:
`^${prefix}-[0-9]+$` with `prefix` unset would silently become `^-[0-9]+$`
and match inputs the caller never authorized. The failure would be invisible
and it would WIDEN the language, so it gets the loud default. `${name:-}` is
the caller's explicit, reviewable opt-in to permissiveness.

**EMPTY is not UNSET.** A bare `${name}` bound to an empty value does not
refuse — it matches the empty string, so `^${v}$` with `v` empty matches only
the empty subject. `${name:?}` is how a caller asks for both to be refused.

Under an encoding with multi-byte characters, a resolved value that is not
well formed raises the same code, checked once per call before the match.

## 6. Every refusal

| situation | when | what it says |
|---|---|---|
| module `vars` off, pattern contains `${` | compile | `${...} requires module 'vars'` |
| `--engine=dfa` on a var-bearing pattern | compile | `${name} requires the VM engine, which --engine=dfa excludes` |
| `-fprefilter` on a var-bearing pattern | compile | names `${...} variable` as the construct whose erasure changes the language |
| a malformed `${...}` | compile | names the rule (the name's first byte, an unknown operator, an unterminated reference) |
| a name or a nesting depth past its limit | compile | names the limit; see `--list-limits` |
| a `word` mixing literal text with a nested `${...}` | compile | says so, and says to write the default as one nested reference or as literal text |
| UNSET value at a bare `${name}`, or at `${name:?}` | run | `PCREC_ERR_UNSET_VAR` |
| an ill-formed value under a multi-byte encoding | run | `PCREC_ERR_UNSET_VAR` |

A variable is independent of captures: `--no-captures` does not interact
with it.

## 7. Engine and caseless

A var-bearing pattern compiles to the **VM engine only**, and gets **no DFA
prefilter**: determinization cannot see bytes that do not exist until the
call. The DFA route for variables is a separate, unstarted effort.

A variable and a backreference share ONE encoding-seam compare
(`$_span_match` / `$_span_match_caseless`): both hand it a runtime span as a
pointer and a length, and the only difference is where those bytes live —
inside the subject for a backreference, in the caller's own buffer for a
variable. That is not a detail a caller can observe, and it is stated here
only because an artifact's emitted residual names it.

**Caseless works**, including the length-changing case. Under `-e utf8` a
value of `k` matches U+212A KELVIN SIGN, consuming three subject bytes
against one value byte, exactly as a caseless backreference does. The value
is not pre-folded, and could not be: a fold is a relation between two sides
and the subject side is not folded.

## 8. What is not here

`${name#pat}`, `${name%pat}`, `${name:off:len}`, `${name^^}`, `${#name}` and
the rest of the shell's operator suite are phased, not declined —
`docs/design/variables_roadmap.md` §3 carries each with what would open it.
A variable in a REPLACEMENT template is a different consumer and is not built.
