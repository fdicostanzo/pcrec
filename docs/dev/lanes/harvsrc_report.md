# harvsrc report: sourcing plan for a real-world regex harvest ([UTF-RW]) (lane harvsrc, 2026-11-05, sonnet)

Facts only; Frank chooses. Nothing was downloaded; no source was opened beyond web search snippets (see "measured vs inferred"). Rulings file `harvsrc_rulings.md`: empty at every read.

## For the owner, in plain words

1. Nothing like a harvest exists in the tree. The only outside patterns are 32 "wild" ones in pcrec-bench (below): 5 OWASP CRS rules, 6 logstash grok patterns, 4 Nosey Parker secret patterns plus datefinder (rebar, Unlicense), 3 OWASP validation patterns, 4 VS Code JSON grammar patterns, moment.js ISO8601. All English-locale, all PCRE-ish, none uses a scoreboard gap construct.
2. Best first source: the OWASP Core Rule Set in FULL (Apache-2.0, PCRE by design, thousands of lines of `@rx`). Bench took 5 of its rules; the full set is the cheapest large PCRE-native population. It will probably still not contain variable-width lookbehind or `\X` (security patterns rarely do), so it tests "does the harvest look like the wild" more than the gaps.
2b. Second: the research regex corpora (Davis et al., FSE 2019: 537,806 regexes from 193,524 projects, 8 languages, with Perl and PHP among them; and the FSE 2018 npm/PyPI set on Zenodo). They are the only place with breadth, and they carry per-language tags so the Perl/PHP slice is near-PCRE. Their LICENSE is NOT confirmed by me; a regex string list may be storable only as a count and a re-derivation recipe. Needs a read of the Zenodo record's license field.
3. Third: i18n data that really contains non-English patterns with clear licenses: Google libaddressinput postal-code regexes (data CC-BY 4.0, Apache-2.0 code; ~240 regions), libphonenumber metadata (Apache-2.0; thousands of per-country number patterns, ASCII digits only), CLDR `postalCodeData.xml` (Unicode terms; about 158 countries; may be deprecated in current CLDR). These are validator-shaped (classes, counted repeats, alternation), NOT lookbehind/`\X`/conditionals shaped.
4. Honest finding: no candidate I found is likely to supply real use of the scoreboard gaps. Gap constructs (variable lookbehind, conditionals, `\X`, set ops, `\R`, verbs) live mostly in editor grammars (Oniguruma dialect, not PCRE), SpamAssassin/Perl-origin text rules, and hand-written Perl code. Expect the harvest to confirm "0 real use" for most gaps; its value is measured frequency, not discovery.
5. Frank must approve: each source entering the tree (home `third_party/<name>-<version>/` with `PROVENANCE.md`, shape in `third_party/README.md`), each download (this lane downloaded none), and whether a corpus whose license forbids storing may be COUNT-ONLY (patterns analysed in scratch, only counts committed).
6. The PCRE2 testdata files are excluded (D181) as instructed.

## Premise test: what exists

- `docs/dev/plan.md` [UTF-RW]: `not-started`, moved up 2026-11-05. No harvest directory in `third_party/` (the index lists `ucd-16.0.0`, `elastic-examples-apache-logs-bc53b584`, `synth-log-lines-v1`; none are pattern corpora).
- `docs/dev/lanes/scoreboard_report.md`: "NO real-world pattern harvest in the tree"; wild and realistic cells are 0 for every gap.
- pcrec-bench "wild" set (read-only: `bench/*/provenance.tsv`), 32 `wild-*.rx` files with a `source_url`:

| group | source | license | n |
|---|---|---|---|
| wild-waf | coreruleset REQUEST-942-APPLICATION-ATTACK-SQLI.conf (rules 942140, 942160, 942270, 942360, 942500) | Apache-2.0 | 5 |
| wild-logparse | logstash-patterns-core `patterns/legacy/grok-patterns` (BASE10NUM, QUOTEDSTRING, SYSLOGBASE, WINPATH; 2 "adapted" without atomic groups) | Apache-2.0 | 5 |
| wild-validator | OWASP Validation Regex Repository (email, IP, US zip) | CC-BY-SA-4.0 | 3 |
| wild-validator | grok UUID | Apache-2.0 | 1 |
| wild-secrets, wild-datetime | rebar `benchmarks/regexes/wild/noseyparker.txt` (4), `date.txt` (datefinder) | Unlicense | 5 |
| wild-datetime | moment.js `from-string.js` extendedIsoRegex | MIT | 1 |
| wild-codegrammar | VS Code `JSON.tmLanguage.json` (4 patterns) | MIT | 4 |
| wild-semdiv, wild-json-validate, wild-sexp | pcre2 doc semantics, JSON-validate (Oniguruma/PCRE twins), balanced sexp | not read | remainder |

  The remaining files include `wild-semdiv-*` and `wild-json-validate` whose provenance rows I did not trace (they are not in the `provenance.tsv` rows I saw; the count of 32 is the scoreboard's, not re-derived). Avoid duplicating the sources above: the full CRS, full grok-patterns, full rebar `wild/`, and the full VS Code grammar set are supersets, so harvesting them subsumes bench's 32; dedupe by pattern text.

## Candidate table

Dialect key: P = PCRE/Perl-native; O = Oniguruma/Onigmo (Ruby-like: `\h` is hex, `(?<n>)` ok, `\A`, absent operator; no `\K`/verbs); J = JS; Py = Python re; R = RE2/Rust (no lookaround); X = mixed per-language. Counts are approximate and, unless marked "measured", INFERRED from search snippets or prior knowledge.

| # | source | URL | license (storable?) | approx n | dialect | extraction | bias | gap-construct reach |
|---|---|---|---|---|---|---|---|---|
| 1 | OWASP CRS (full) | https://github.com/coreruleset/coreruleset | Apache-2.0; storable with NOTICE | order of 10^3 `@rx` patterns (not measured); also `.ra` assembly sources | P (PCRE, ModSecurity) | parse `SecRule ... "@rx PATTERN"` in `rules/*.conf`; join `\`-continued lines; handle `.ra` or take the assembled output only | security/WAF: alternations of keywords, `(?i)`, `(?:`, lookahead, few lookbehinds, English/ASCII | low-moderate: lookahead yes; conditionals/`\X` unlikely; some `(?<!` fixed-width |
| 2 | Research corpora: Davis et al. FSE 2019 (arXiv 2105.04397), 537,806 regexes, 193,524 projects, JS/Java/PHP/Python/Ruby/Go/Perl/Rust | paper: https://arxiv.org/abs/2105.04397 ; data via Zenodo DOI 10.5281/zenodo.3257777 (record lists a software repository; contents unconfirmed) | NOT CONFIRMED. Stop rule: treat as count-only until the Zenodo license field is read | ~5x10^5 total; unique count and per-language split in the paper | X; Perl and PHP slices near-PCRE, others need dialect filtering | public dataset file (JSON per language, per paper), filter by language tag, compile each with libpcre2 10.46 and keep accepts | github/npm/pypi skew toward web dev (validation, URL, path, whitespace trim); duplicates heavy; modules not recorded (security) | broad; the only candidate big enough to give meaningful lookbehind/conditional counts |
| 3 | Davis et al. FSE 2018 (ReDoS, npm + PyPI unique regex set, Zenodo record 1294301 "Version 1.0.0", Nov 2018) | https://zenodo.org/record/1294301 | NOT CONFIRMED (snippet: raw regexes released without source modules) | ~10^5 unique (paper figure not verified) | J and Py | JSON of unique patterns | JS and Python, so PCRE-fit is partial; no module context | moderate |
| 4 | Chapman and Stolee ISSTA 2016 (Python), Wang and Stolee FSE 2018 (15,000+ tested regexes, 1,225 Java projects; https://par.nsf.gov/servlets/purl/10100307), Michael et al. ASE 2019 "Regexes are Hard" (survey, not a corpus) | see links | no data location confirmed for 4 | 10^4 | Py / Java | per-paper artifact if any | Python and Java projects | Java regex is PCRE-adjacent; useful as a cross-check only |
| 5 | grok patterns (full): logstash-patterns-core | https://github.com/logstash-plugins/logstash-patterns-core | Apache-2.0; storable (bench already stores 6) | ~10^2 (grok-patterns file plus ECS/legacy per-app files; not measured) | P/O (Oniguruma in Logstash), mostly the PCRE common subset | parse `NAME regex` lines, expand `%{OTHER:field}` references (bench already did this once for SYSLOGBASE) | English log formats; atomic groups; no non-English | low |
| 6 | fluent-bit `conf/parsers.conf` (+ docs) | https://github.com/fluent/fluent-bit | license not verified here (believed Apache-2.0; check LICENSE) | ~10^1-10^2 | O (Onigmo, Ruby mode; named groups letters/digits/underscore) | ini-style `Regex` key | log formats | low |
| 7 | Editor grammars: VS Code bundled extensions (TextMate JSON/plist) and Linguist grammar repos | https://github.com/microsoft/vscode/tree/main/extensions ; https://github.com/github-linguist/linguist | MIT for VS Code's bundled grammars (bench cites MIT for JSON grammar; per-grammar upstream licenses differ, some are third-party MIT/Apache/other; check each) | 10^4-10^5 (rough; unmeasured) | O (Oniguruma), NOT PCRE: `\h` hex, `\G`, absent groups, possessive and `\K` differ | JSON walk for `match`/`begin`/`end`/`while` keys; `include` references are not regexes | programming-language lexing; Unicode property use in identifiers (`\p{L}`, `[[:alpha:]]`); heavy lookbehind and backrefs in `end` patterns | HIGH for lookaround, backreference-in-end; need dialect filter and libpcre2 oracle accept filter |
| 8 | Snort community rules (`pcre:"/.../flags"`) | https://snort.org/downloads (community) | GPL v2 for community rules (snort.org license page); GPL obligations apply if stored; subscriber rules are non-commercial/not storable | ~10^3 | P (Snort uses PCRE; flags in trailer) | parse `pcre:"/body/flags";` handling escapes | network payloads: `\x` bytes, `(?i)`, `\d`, binary shapes; byte-mode, not UTF | low |
| 9 | Suricata / Emerging Threats Open | https://rules.emergingthreats.net/open/ | BSD for most ET Open sids; some bundled third-party lists GPL or unclear (forum posts conflict on the sid boundaries: unverified); ET Pro commercial | ~10^4 pcre options (rule count not verified) | P | same as Snort plus `pcre` flags `R`/`U`/`P` etc | malware/C2 traffic; byte-oriented; some non-English domains in strings | low |
| 10 | Wikimedia Spam Blacklist (global) | https://meta.wikimedia.org/wiki/Spam_Blacklist | wiki text is CC BY-SA by default (not verified for this page); attribution/share-alike would apply to the derived corpus | ~10^4 lines (unverified) | P (PHP `preg`, delimiter-wrapped fragments) | line parse, one regex fragment per line | domain-name fragments; some non-Latin/IDN and CJK spam domains | low for gaps; moderate for UTF literals |
| 11 | Apache SpamAssassin rules | https://github.com/apache/spamassassin (trunk `rules/`) | Apache-2.0 (file headers confirmed for sampled files) | ~10^3 `body`/`header`/`rawbody` rules | P/Perl (real Perl code; uses `(?i)`, lookarounds, `\b`; some rules are Perl-only) | `.cf` parse `body NAME /re/flags` | English-spam heavy; third-party language rulesets (French, German, Italian) are separate and variably licensed | moderate (lookbehind, `\b`, UTF-8 literals) |
| 12 | Nmap `nmap-service-probes` (`match` lines) | https://github.com/nmap/nmap | NPSL: not storable here (nmap copyrights data files, restricts commercial redistribution) -> COUNT-ONLY | ~10^4 match lines (unverified) | P (Nmap embeds PCRE) | parse `match svc m|re|flags` with arbitrary delimiters | network banners, byte-oriented, `(?s)`; very regular | low |
| 13 | libphonenumber metadata | https://github.com/google/libphonenumber (`resources/PhoneNumberMetadata.xml`) | Apache-2.0 (mirror header confirmed; main repo not read) | ~10^3 patterns (per territory x type; unmeasured) | P-compatible subset (Java regex source) | XML `nationalNumberPattern`, `possibleLengths`, `leadingDigits` | phone numbers; ASCII digits; strongly class/alternation/counted-repeat | none for gaps; good census material for counted classes |
| 14 | Google libaddressinput / i18n address data | https://github.com/google/libaddressinput (C++ and Java; data from Google I18n Address Data Service) | code Apache-2.0, data CC-BY 4.0 (mirror statement; confirm upstream) | ~240 regions with `zip` regex, plus `sub_zips` (count unverified) | P-compatible (Java/JS) | JSON per region `zip` and `sub_zips` | postal codes, many non-English regions; mostly ASCII digits/Latin | none for gaps |
| 15 | CLDR `postalCodeData.xml` | https://github.com/unicode-org/cldr (`common/supplemental`) | Unicode License v3 / Terms of Use (third_party already vendors under it for UCD) | ~158 countries (2011 proposal; Google-contributed 2009) | P-compatible | XML `postCodeRegex territoryId` | postal codes only; file may be deprecated in favor of other data (unverified) | none |
| 16 | rebar `benchmarks/regexes/wild/*.txt` (full) | https://github.com/BurntSushi/rebar | Unlicense (bench already stores 5) | 10^2 (several files; unmeasured) | R-targeted but drawn from real tools; PCRE-acceptable subset | one pattern per line (bench has the extractor path) | curated for engine comparison; includes Nosey Parker secret patterns and datefinder | low |
| 17 | Perl `Regexp::Common`, validator.js, python-stdnum, Django localflavor | e.g. https://github.com/validatorjs/validator.js | validator.js MIT; python-stdnum LGPL; localflavor BSD; Regexp::Common Perl/Artistic (not verified here) | 10^2-10^3 | J / Py / Perl | source parse, no common format; hand curation | validators for many national ID/postal/phone formats; the closest to the [UTF-RW] "non-English locale" brief but in code, not data files | none to low; Perl Regexp::Common uses recursion and conditionals |
| 18 | i18n test suites (W3C i18n, Unicode UTS#18 conformance material) | https://www.w3.org/International/ | W3C docs license, not verified | small | mixed | hand extraction | RTL, combining marks; few patterns | `\X` and set-op demos likely |

## Ranking (lane judgement; inferred, see below)

Score key: (a) PCRE fit, (b) storable license, (c) construct breadth, (d) low effort. 3 = best.

| rank | source | a | b | c | d | note |
|---|---|---|---|---|---|---|
| 1 | CRS full (#1) | 3 | 3 | 1 | 3 | known license, known format, bench already proves the parse |
| 2 | Davis 2019 corpus (#2), Perl+PHP slice | 2 | ? | 3 | 2 | only breadth; blocked on license read |
| 3 | SpamAssassin rules (#11) | 3 | 3 | 2 | 2 | Perl-native, Apache-2.0; English-biased |
| 4 | Editor grammars (#7) | 1 | 2 | 3 | 2 | best construct breadth, wrong dialect; needs oracle-accept filter |
| 5 | libaddressinput + libphonenumber + CLDR (#13-15) | 3 | 3 | 0 | 3 | the only clear-license i18n pattern data; no gap reach |
| 6 | grok full, rebar wild full, fluent-bit (#5, #16, #6) | 2 | 3 | 1 | 3 | cheap supersets of bench |
| 7 | Snort, Suricata, Wikimedia (#8-10) | 3 | 1-2 | 1 | 2 | license friction (GPL, CC-BY-SA) |
| 8 | Nmap (#12) | 3 | 0 | 1 | 2 | count-only |
| 9 | validator libraries (#17), W3C i18n (#18) | 1-2 | 2 | 1 | 1 | manual curation |

## Recommendation

First three: (1) CRS full, (2) the Davis 2019 corpus filtered to Perl and PHP (and anything libpcre2 10.46 accepts), (3) editor grammars filtered to the libpcre2-accepting subset, with SpamAssassin as the fallback if (2)'s license blocks storage. For the i18n half of [UTF-RW] add libaddressinput + libphonenumber as a small fourth row; be aware they are validator-shaped and will answer the class-shape census ([UTF-RW] deliverable 2) better than the gap question.

Extraction method, one shape for all: a small per-source parser in `third_party/<name>-<version>/generate.py` writing a normalized TSV (source id, location, flags, pattern bytes); `make gen-tables` regenerates it, `--check` verifies; compile every row with pcrec (`--features all`) and libpcre2 10.46 (oracle) and record accept/refuse. The per-source dialect label is a column, so a JS or Oniguruma pattern is never counted as PCRE unless libpcre2 accepts it. Where a license forbids storing text, commit only the counts and the recipe (count-only).

Approvals Frank needs to give: (a) each source enters the tree under `third_party/<name>-<version>/` with `PROVENANCE.md` naming what derives from it (or an argued other home, e.g. `oracle_store/`-shaped if the data is answers, not source text); (b) the downloads themselves (none done); (c) a ruling on count-only handling; (d) for CC-BY-SA / GPL sources (OWASP validation repository is CC-BY-SA already in bench; Snort GPL v2; Wikimedia), whether share-alike obligations on a stored derived TSV are acceptable.

## Measured vs inferred

Measured (this lane read these directly): the plan row [UTF-RW], `scoreboard_report.md`, `third_party/README.md` and CLAUDE.md, `REFERENCES.md` (it has no regex-corpus papers: cite keys would be added at first use, suggested `[Dav19]`, `[Dav18]`), pcrec-bench `bench/*/provenance.tsv` rows (sources and licenses in the table above), the file names of the 32 wild patterns.

Inferred from web search snippets only (no page was fetched or opened; treat each as a lead to verify before Frank approves): Davis 2019 corpus size, languages, and the Zenodo DOI; Zenodo 1294301 content; Wang and Stolee numbers; Snort GPL v2 statement; ET Open BSD/GPL sid boundaries (sources conflicted); CRS Apache-2.0 and `.ra`/`.data` assembly workflow; SpamAssassin Apache-2.0 headers on sampled files; fluent-bit Onigmo; CLDR file structure and age; libphonenumber Apache-2.0 on a mirror; libaddressinput Apache-2.0/CC-BY 4.0 on a mirror; Nmap license summary from `service_scan.h` comments; rebar Unlicense.

Not measured at all: every pattern count in the table marked "~10^N" (my orders of magnitude, not counts), the per-source gap-construct reach (column "gap-construct reach" is a prediction from what each ecosystem tends to write), whether the Davis corpus can be stored, the licenses of fluent-bit, W3C material, validator libraries, the per-grammar licenses inside VS Code extensions, and ET Open's current rule count. The three "wild-semdiv/json-validate/sexp" bench provenance rows were not traced.
