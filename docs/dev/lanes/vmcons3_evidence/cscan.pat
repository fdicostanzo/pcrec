(?x)
# pcrec scanner for the C (?{ ... }) segment: docs/design/inline_c.md 2.3.
# S = phase-2 splices (backslash-newline), skipped between any two characters.
\G \(\?\{ (?<body> (?&items) (?&sp) ) (?: \} | % (?&sp) > ) (?&sp) \)

(?(DEFINE)
  (?<sp> (?: \\ \n )*+ )

  # a run of tokens, stopping (without consuming) at the closing } or %> of the current depth
  (?<items> (?:
      (?&sp) (?:
          # identifier: an encoding prefix (L u U u8) is ordinary identifier text
          [A-Za-z_$\x80-\xff] (?: (?&sp) [\w$\x80-\xff] )*+
          # pp-number: a ' followed by an identifier character is a C23 digit separator
        | (?: \d | \. (?&sp) \d ) (?: (?&sp) (?: [eEpP][+-] | [\w.$\x80-\xff] | ' (?= (?&sp) \w ) ) )*+
          # string and character literals, backslash escapes, a raw newline never inside
        | " (?: [^"\\\n]++ | \\ \n | \\ (?&sp) [^\n] )*+ "
        | ' (?: [^'\\\n]++ | \\ \n | \\ (?&sp) [^\n] )*+ '
          # block comment, line comment (a spliced newline continues it)
        | / (?&sp) \* (?: [^*]++ | \* (?! (?&sp) / ) )*+ \* (?&sp) /
        | / (?&sp) / (?: [^\\\n]++ | \\ \n | \\ )*+
          # a nested block: { ... } or <% ... %>
        | (?: \{ | < (?&sp) % ) (?&items) (?&sp) (?: \} | % (?&sp) > )
          # everything else, one byte; < and % are plain unless they open a digraph
        | [^\w$\x80-\xff"'/{}<%] | / (?! (?&sp) [*/] ) | < (?! (?&sp) % ) | % (?! (?&sp) > )
      )
  )*+ )
)