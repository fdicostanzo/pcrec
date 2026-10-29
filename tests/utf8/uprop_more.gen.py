HEAD='''# tests/utf8/uprop_more.rxt -- [UPROP-MORE] (lane upropb): `\\p{...}` takes the
# binary Unicode properties and Bidi_Class, exactly the names and spellings
# libpcre2 10.46 accepts for them (they were refused as "not implemented yet").
# The data is the vendored Unicode 16.0.0 files (third_party/ucd-16.0.0/).
#
# EVERY EXPECTATION WAS PRODUCED BY libpcre2 10.46 at PCRE2_UTF (tests/lib/
# p2gen.py over p2probe; spec: uprop_more.gen.py beside this file), except the
# byte-encoding blocks, which libpcre2 answers at options=0. The whole-space
# differential over every property is tests/uprops/run_uprops_tests.sh; these
# are the witnesses. Every block is `# pcre2-only` (python `re` has no \\p{}).
# The Bidi_Mirrored cells avoid the 126 code points libpcre2 omits
# (docs/dev/upstream_issues.md U22).
'''
U='unicode-props'
def blk(c,p,s,e='utf8',f=U,fl='',**k):
    d=dict(c=c,p=p,s=s,f=f,po=1)
    if e: d['e']=e
    if fl: d['fl']=fl
    d.update(k); return d
BLOCKS=[
 blk('THE EMOJI DIGIT GOTCHA: `Emoji` is a property of 0-9, # and * as well (emoji-data lists them as keycap bases).','\\p{Emoji}',['5','#','*','😀','a','é','\u00a9']),
 blk('`Emoji_Presentation`: what is an emoji by default; digits are not.','\\p{Emoji_Presentation}',['5','😀','\u231a','a','\u00a9']),
 blk('`Extended_Pictographic` (emoji-data), the property grapheme clustering uses.','\\p{Extended_Pictographic}',['5','😀','\u00a9','a','\u2122']),
 blk('The short alias is the same property.','\\p{ExtPict}',['😀','5']),
 blk('`Emoji_Modifier` (the five skin-tone modifiers) and `Emoji_Modifier_Base`.','\\p{Emoji_Modifier}',['\U0001f3fb','\U0001f3ff','😀']),
 blk('`Emoji_Modifier_Base`.','\\p{EBase}',['\U0001f44d','😀','a']),
 blk('`Emoji_Component`.','\\p{EComp}',['5','#','\u200d','a']),
 blk('`Regional_Indicator`.','\\p{RI}',['\U0001f1fa','\U0001f1f8','U']),
 blk('Negation, three spellings of the same set: `\\P`.','\\P{Emoji}',['5','a','😀','é']),
 blk('... `\\p{^}`.','\\p{^Emoji}',['5','a','😀']),
 blk('... and `\\P{^}` double-negates.','\\P{^Emoji}',['5','a','😀']),
 blk('Inside a class.','[\\p{Emoji}x]',['5','x','y','😀']),
 blk('A negated class holding a binary property.','[^\\p{Emoji}]',['5','a','😀','é']),
 blk('Quantified.','\\p{Emoji}+',['😀😀5','a']),
 blk('`Alphabetic` (derived: letters, letter numbers, Other_Alphabetic marks).','\\p{Alphabetic}',['a','é','5','_','\u00aa','\u2167','\u0345',' ']),
 blk('`Alpha` is `Alphabetic`; names are case/space/underscore/hyphen loose.','\\p{ aLpHa }',['a','5']),
 blk('Loose: underscores and hyphens in a long name.','\\p{Default-Ignorable_Code Point}',['\u00ad','a']),
 blk('`Lowercase` is NOT `Ll` (it adds Other_Lowercase).','\\p{Lowercase}',['a','A','\u00aa','\u2170','5']),
 blk('`Uppercase`.','\\p{Uppercase}',['A','a','\u2160','\u24b6']),
 blk('Under -i only Lu/Ll/Lt become L&; `Lowercase` is unchanged.','\\p{Lowercase}',['a','A','\u00aa'],fl='i'),
 blk('... `Uppercase` likewise.','\\p{Uppercase}',['a','A'],fl='i'),
 blk('... `Alphabetic` and `Emoji` likewise.','\\p{Alphabetic}',['a','A','5'],fl='i'),
 blk('... `Emoji`.','\\p{Emoji}',['5','a','😀'],fl='i'),
 blk('`Cased`.','\\p{Cased}',['a','A','\u01c5','5','\u00aa']),
 blk('`Case_Ignorable`.','\\p{CI}',['\'','.','\u0301','a']),
 blk('`Changes_When_Casefolded`.','\\p{CWCF}',['A','a','\u00df','5']),
 blk('`Changes_When_Titlecased`.','\\p{Changes_When_Titlecased}',['a','A','\u01c6']),
 blk('`Default_Ignorable_Code_Point`: soft hyphen, ZWSP, variation selectors, Hangul fillers.','\\p{Default_Ignorable_Code_Point}',['\u00ad','\u200b','\ufe0f','\u3164','a',' ']),
 blk('`DI`, the short alias.','\\p{DI}',['\u00ad','a']),
 blk('`Bidi_Control` (Trojan-Source detection): the explicit directional marks.','\\p{Bidi_Control}',['\u202e','\u2066','\u200f','a','\u200b']),
 blk('`Bidi_C`.','\\p{Bidi_C}',['\u202a','\u202e','a']),
 blk('`Bidi_Mirrored` (cells outside the 126 libpcre2 omits, U22).','\\p{Bidi_Mirrored}',['(',')','<','a','5']),
 blk('`Join_Control` (ZWNJ, ZWJ).','\\p{Join_C}',['\u200c','\u200d','a']),
 blk('`Variation_Selector`.','\\p{VS}',['\ufe0f','\U000e0100','a']),
 blk('`Noncharacter_Code_Point`.','\\p{NChar}',['\uffff','\ufdd0','\U0010ffff','a']),
 blk('`White_Space` and its alias `space`.','\\p{space}',[' ','\t','\u00a0','\u200b','a','\u2028']),
 blk('`Pattern_White_Space`.','\\p{Pat_WS}',[' ','\u200e','\u00a0','a']),
 blk('`ASCII` (PCRE2\'s own, U+0000-007F).','\\p{ASCII}',['a','\x00','\x7f','\u0080','é']),
 blk('`Hex_Digit` includes the fullwidth forms; `ASCII_Hex_Digit` does not.','\\p{Hex_Digit}',['f','F','\uff26','g','5']),
 blk('`ASCII_Hex_Digit`.','\\p{AHex}',['f','\uff26','g','5']),
 blk('`ID_Start` / `XID_Continue`.','\\p{ID_Start}',['a','5','_','\u2160']),
 blk('`XID_Continue`.','\\p{XIDC}',['a','5','_','-']),
 blk('`Math`.','\\p{Math}',['+','<','a','\u2211']),
 blk('`Dash` / `Quotation_Mark`.','\\p{Dash}',['-','\u2014','_','a']),
 blk('`Quotation_Mark`.','\\p{QMark}',['"','\'','\u201c','a']),
 blk('`Ideographic` / `Unified_Ideograph`.','\\p{Ideographic}',['\u4e2d','\u3007','a','\u3042']),
 blk('`Unified_Ideograph`.','\\p{UIdeo}',['\u4e2d','\u3007','a']),
 blk('`Modifier_Combining_Mark` (new in 16.0).','\\p{MCM}',['\u0654','a']),
 blk('`ID_Compat_Math_Start` (new in 15.1).','\\p{ID_Compat_Math_Start}',['\u2202','a']),
 blk('`Grapheme_Extend`, `Grapheme_Base`.','\\p{Gr_Ext}',['\u0301','\u200c','a']),
 blk('`Grapheme_Base`.','\\p{Gr_Base}',['a','\u0301','\u200b']),
 blk('`Soft_Dotted`, `Terminal_Punctuation`, `Sentence_Terminal`.','\\p{SD}',['i','j','a']),
 blk('`Terminal_Punctuation`.','\\p{Term}',['.',',','a','\u3002']),
 blk('`Sentence_Terminal`.','\\p{STerm}',['.','!',',','a']),
 # ---- Bidi_Class
 blk('`Bidi_Class` by short name, `=` separator.','\\p{bc=R}',['\u05d0','a','\u0627','5']),
 blk('`:` is the same separator.','\\p{bc:AL}',['\u0627','\u05d0','a']),
 blk('The long property name, loose.','\\p{Bidi Class = L}',['a','\u05d0','5']),
 blk('`BidiClass=EN` lower-case value, spaces.','\\p{bidiclass = en}',['5','a','\u0663']),
 blk('`AN` (Arabic-Indic digits).','\\p{bc=AN}',['\u0663','5']),
 blk('`NSM`.','\\p{bc=NSM}',['\u0301','a']),
 blk('`BN` includes unassigned noncharacters and default-ignorables.','\\p{bc=BN}',['\u00ad','\ufdd0','\u200b','a']),
 blk('`B` and `S` and `WS`.','\\p{bc=B}',['\n','\u2029',' ','a']),
 blk('`WS`.','\\p{bc=WS}',[' ','\u3000','\t','a']),
 blk('`ON` (other neutral).','\\p{bc=ON}',['!','(','a']),
 blk('Unassigned code points take the block default (U+05FF is in the Hebrew block: R; U+0870 is Arabic: AL). `bc=R`.','\\p{bc=R}',['\u05ff','\u0870']),
 blk('... `bc=AL`.','\\p{bc=AL}',['\u05ff','\u0870']),
 blk('`FSI`/`LRI` isolates.','\\p{bc=FSI}',['\u2068','\u2066']),
 blk('Negation and class.','\\P{bc=L}',['a','\u05d0','5']),
 blk('A class mixing two Bidi_Class values.','[\\p{bc=R}\\p{bc=AL}]',['\u05d0','\u0627','a']),
 # ---- refusals libpcre2 shares
 blk('PCRE2 takes Bidi_Class SHORT names only: the long value name is refused.','\\p{bc=Arabic_Letter}','perr'),
 blk('A binary property takes no `=Y`.','\\p{Alphabetic=Y}','perr'),
 blk('The UCD binary properties libpcre2 refuses stay refused: `Hyphen`.','\\p{Hyphen}','perr'),
 blk('... `Other_Alphabetic`.','\\p{Other_Alphabetic}','perr'),
 blk('... `Expands_On_NFC`.','\\p{XO_NFC}','perr'),
 blk('... `Assigned`.','\\p{Assigned}','perr'),
 blk('... other UCD axes: `gc=`.','\\p{gc=Lu}','perr'),
 blk('... `East_Asian_Width`.','\\p{ea=W}','perr'),
 # ---- byte encoding: the property is clamped to Latin-1
 blk('Under `byte` the property is clamped to the Latin-1 universe: `Alphabetic`.','\\p{Alphabetic}',[b'a',b'\xe9',b'5',b'\xaa',b'\xd7'],e=None),
 blk('... `Lowercase`.','\\p{Lowercase}',[b'a',b'A',b'\xaa',b'\xb5'],e=None),
 blk('... `Emoji` (the digits, #, *, (c), (r) are in Latin-1).','\\p{Emoji}',[b'5',b'#',b'\xa9',b'\xae',b'a'],e=None),
 blk('... `bc=L` is most of Latin-1.','\\p{bc=L}',[b'a',b'5',b'\xaa',b'\xd7'],e=None),
 blk('... `bc=R` is empty in Latin-1: the class matches nothing.','\\p{bc=R}',[b'a',b'\xe9'],e=None),
 blk('... `ASCII`.','\\p{ASCII}',[b'a',b'\x7f',b'\x80'],e=None),
]
