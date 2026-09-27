	.arch armv8.5-a
	.build_version macos,  26, 0
	.text
	.align	2
	.globl _cmp_memcmp_1
_cmp_memcmp_1:
LFB0:
	add	x3, x1, 1
	cmp	x3, x2
	bhi	L3
	ldrb	w0, [x0, x1]
	cmp	w0, 97
	cset	w0, eq
L1:
	ret
L3:
	mov	w0, 0
	b	L1
LFE0:
	.align	2
	.globl _cmp_memcmp_2
_cmp_memcmp_2:
LFB1:
	add	x3, x1, 2
	cmp	x3, x2
	bhi	L6
	ldrh	w1, [x0, x1]
	mov	w0, 25185
	cmp	w1, w0
	cset	w0, eq
L4:
	ret
L6:
	mov	w0, 0
	b	L4
LFE1:
	.cstring
	.align	3
l.str.0:
	.ascii "abc\0"
	.text
	.align	2
	.globl _cmp_memcmp_3
_cmp_memcmp_3:
LFB2:
	add	x3, x1, 3
	cmp	x3, x2
	bhi	L11
	add	x2, x0, x1
	ldrh	w1, [x0, x1]
	mov	w0, 25185
	cmp	w1, w0
	beq	L12
L9:
	mov	w0, 1
L10:
	eor	w0, w0, 1
L7:
	ret
L12:
	ldrb	w0, [x2, 2]
	cmp	w0, 99
	bne	L9
	mov	w0, 0
	b	L10
L11:
	mov	w0, 0
	b	L7
LFE2:
	.align	2
	.globl _cmp_memcmp_4
_cmp_memcmp_4:
LFB3:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L15
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	cset	w0, eq
L13:
	ret
L15:
	mov	w0, 0
	b	L13
LFE3:
	.cstring
	.align	3
l.str.1:
	.ascii "abcde\0"
	.text
	.align	2
	.globl _cmp_memcmp_5
_cmp_memcmp_5:
LFB4:
	add	x3, x1, 5
	cmp	x3, x2
	bhi	L20
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	beq	L21
L18:
	mov	w0, 1
L19:
	eor	w0, w0, 1
L16:
	ret
L21:
	ldrb	w0, [x2, 4]
	cmp	w0, 101
	bne	L18
	mov	w0, 0
	b	L19
L20:
	mov	w0, 0
	b	L16
LFE4:
	.cstring
	.align	3
l.str.2:
	.ascii "abcdef\0"
	.text
	.align	2
	.globl _cmp_memcmp_6
_cmp_memcmp_6:
LFB5:
	add	x3, x1, 6
	cmp	x3, x2
	bhi	L26
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	beq	L27
L24:
	mov	w0, 1
L25:
	eor	w0, w0, 1
L22:
	ret
L27:
	ldrh	w1, [x2, 4]
	mov	w0, 26213
	cmp	w1, w0
	bne	L24
	mov	w0, 0
	b	L25
L26:
	mov	w0, 0
	b	L22
LFE5:
	.cstring
	.align	3
l.str.3:
	.ascii "abcdefg\0"
	.text
	.align	2
	.globl _cmp_memcmp_7
_cmp_memcmp_7:
LFB6:
	add	x3, x1, 7
	cmp	x3, x2
	bhi	L32
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	beq	L33
L30:
	mov	w0, 1
L31:
	eor	w0, w0, 1
L28:
	ret
L33:
	ldrh	w1, [x2, 4]
	mov	w0, 26213
	cmp	w1, w0
	bne	L30
	ldrb	w0, [x2, 6]
	cmp	w0, 103
	bne	L30
	mov	w0, 0
	b	L31
L32:
	mov	w0, 0
	b	L28
LFE6:
	.align	2
	.globl _cmp_memcmp_8
_cmp_memcmp_8:
LFB7:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L36
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	cset	w0, eq
L34:
	ret
L36:
	mov	w0, 0
	b	L34
LFE7:
	.cstring
	.align	3
l.str.4:
	.ascii "abcdefghi\0"
	.text
	.align	2
	.globl _cmp_memcmp_9
_cmp_memcmp_9:
LFB8:
	add	x3, x1, 9
	cmp	x3, x2
	bhi	L41
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L42
L39:
	mov	w0, 1
L40:
	eor	w0, w0, 1
L37:
	ret
L42:
	ldrb	w0, [x2, 8]
	cmp	w0, 105
	bne	L39
	mov	w0, 0
	b	L40
L41:
	mov	w0, 0
	b	L37
LFE8:
	.cstring
	.align	3
l.str.5:
	.ascii "abcdefghij\0"
	.text
	.align	2
	.globl _cmp_memcmp_10
_cmp_memcmp_10:
LFB9:
	add	x3, x1, 10
	cmp	x3, x2
	bhi	L47
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L48
L45:
	mov	w0, 1
L46:
	eor	w0, w0, 1
L43:
	ret
L48:
	ldrh	w1, [x2, 8]
	mov	w0, 27241
	cmp	w1, w0
	bne	L45
	mov	w0, 0
	b	L46
L47:
	mov	w0, 0
	b	L43
LFE9:
	.cstring
	.align	3
l.str.6:
	.ascii "abcdefghijk\0"
	.text
	.align	2
	.globl _cmp_memcmp_11
_cmp_memcmp_11:
LFB10:
	add	x3, x1, 11
	cmp	x3, x2
	bhi	L53
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L54
L51:
	mov	w0, 1
L52:
	eor	w0, w0, 1
L49:
	ret
L54:
	ldrh	w1, [x2, 8]
	mov	w0, 27241
	cmp	w1, w0
	bne	L51
	ldrb	w0, [x2, 10]
	cmp	w0, 107
	bne	L51
	mov	w0, 0
	b	L52
L53:
	mov	w0, 0
	b	L49
LFE10:
	.cstring
	.align	3
l.str.7:
	.ascii "abcdefghijkl\0"
	.text
	.align	2
	.globl _cmp_memcmp_12
_cmp_memcmp_12:
LFB11:
	add	x3, x1, 12
	cmp	x3, x2
	bhi	L59
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L60
L57:
	mov	w0, 1
L58:
	eor	w0, w0, 1
L55:
	ret
L60:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L57
	mov	w0, 0
	b	L58
L59:
	mov	w0, 0
	b	L55
LFE11:
	.cstring
	.align	3
l.str.8:
	.ascii "abcdefghijklm\0"
	.text
	.align	2
	.globl _cmp_memcmp_13
_cmp_memcmp_13:
LFB12:
	add	x3, x1, 13
	cmp	x3, x2
	bhi	L65
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L66
L63:
	mov	w0, 1
L64:
	eor	w0, w0, 1
L61:
	ret
L66:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L63
	ldrb	w0, [x2, 12]
	cmp	w0, 109
	bne	L63
	mov	w0, 0
	b	L64
L65:
	mov	w0, 0
	b	L61
LFE12:
	.cstring
	.align	3
l.str.9:
	.ascii "abcdefghijklmn\0"
	.text
	.align	2
	.globl _cmp_memcmp_14
_cmp_memcmp_14:
LFB13:
	add	x3, x1, 14
	cmp	x3, x2
	bhi	L71
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L72
L69:
	mov	w0, 1
L70:
	eor	w0, w0, 1
L67:
	ret
L72:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L69
	ldrh	w1, [x2, 12]
	mov	w0, 28269
	cmp	w1, w0
	bne	L69
	mov	w0, 0
	b	L70
L71:
	mov	w0, 0
	b	L67
LFE13:
	.cstring
	.align	3
l.str.10:
	.ascii "abcdefghijklmno\0"
	.text
	.align	2
	.globl _cmp_memcmp_15
_cmp_memcmp_15:
LFB14:
	add	x3, x1, 15
	cmp	x3, x2
	bhi	L77
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L78
L75:
	mov	w0, 1
L76:
	eor	w0, w0, 1
L73:
	ret
L78:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L75
	ldrh	w1, [x2, 12]
	mov	w0, 28269
	cmp	w1, w0
	bne	L75
	ldrb	w0, [x2, 14]
	cmp	w0, 111
	bne	L75
	mov	w0, 0
	b	L76
L77:
	mov	w0, 0
	b	L73
LFE14:
	.cstring
	.align	3
l.str.11:
	.ascii "abcdefghijklmnop\0"
	.text
	.align	2
	.globl _cmp_memcmp_16
_cmp_memcmp_16:
LFB15:
	add	x3, x1, 16
	cmp	x3, x2
	bhi	L83
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cmp	x0, 0
	cset	w0, eq
L79:
	ret
L83:
	mov	w0, 0
	b	L79
LFE15:
	.cstring
	.align	3
l.str.13:
	.ascii "abcdefghijklmnopq\0"
	.text
	.align	2
	.globl _cmp_memcmp_17
_cmp_memcmp_17:
LFB16:
	add	x3, x1, 17
	cmp	x3, x2
	bhi	L88
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L86
	ldrb	w0, [x2, 16]
	cmp	w0, 113
	beq	L89
L86:
	mov	w0, 1
L87:
	eor	w0, w0, 1
L84:
	ret
L89:
	mov	w0, 0
	b	L87
L88:
	mov	w0, 0
	b	L84
LFE16:
	.cstring
	.align	3
l.str.14:
	.ascii "abcdefghijklmnopqrst\0"
	.text
	.align	2
	.globl _cmp_memcmp_20
_cmp_memcmp_20:
LFB17:
	add	x3, x1, 20
	cmp	x3, x2
	bhi	L94
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L92
	ldr	w1, [x2, 16]
	mov	w0, 29297
	movk	w0, 0x7473, lsl 16
	cmp	w1, w0
	beq	L95
L92:
	mov	w0, 1
L93:
	eor	w0, w0, 1
L90:
	ret
L95:
	mov	w0, 0
	b	L93
L94:
	mov	w0, 0
	b	L90
LFE17:
	.cstring
	.align	3
l.str.15:
	.ascii "abcdefghijklmnopqrstuvwx\0"
	.text
	.align	2
	.globl _cmp_memcmp_24
_cmp_memcmp_24:
LFB18:
	add	x3, x1, 24
	cmp	x3, x2
	bhi	L100
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L98
	ldr	x1, [x2, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	beq	L101
L98:
	mov	w0, 1
L99:
	eor	w0, w0, 1
L96:
	ret
L101:
	mov	w0, 0
	b	L99
L100:
	mov	w0, 0
	b	L96
LFE18:
	.cstring
	.align	3
l.str.16:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDE\0"
	.text
	.align	2
	.globl _cmp_memcmp_31
_cmp_memcmp_31:
LFB19:
	mov	x3, x1
	add	x1, x1, 31
	cmp	x1, x2
	bhi	L104
	stp	x29, x30, [sp, -16]!
LCFI0:
	mov	x29, sp
LCFI1:
	mov	x2, 31
	adrp	x1, l.str.16@PAGE
	add	x1, x1, l.str.16@PAGEOFF;
	add	x0, x0, x3
	bl	_memcmp
	cmp	w0, 0
	cset	w0, eq
	ldp	x29, x30, [sp], 16
LCFI2:
	ret
L104:
	mov	w0, 0
	ret
LFE19:
	.cstring
	.align	3
l.str.17:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEF\0"
	.text
	.align	2
	.globl _cmp_memcmp_32
_cmp_memcmp_32:
LFB20:
	add	x3, x1, 32
	cmp	x3, x2
	bhi	L113
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L111
	ldr	q31, [x2, 16]
	adrp	x0, lC18@PAGE
	ldr	q30, [x0, #lC18@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbz	x0, L112
L111:
	mov	w0, 1
L112:
	eor	w0, w0, 1
L109:
	ret
L113:
	mov	w0, 0
	b	L109
LFE20:
	.cstring
	.align	3
l.str.19:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFG\0"
	.text
	.align	2
	.globl _cmp_memcmp_33
_cmp_memcmp_33:
LFB21:
	add	x3, x1, 33
	cmp	x3, x2
	bhi	L118
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L116
	ldr	q31, [x2, 16]
	adrp	x0, lC18@PAGE
	ldr	q30, [x0, #lC18@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L116
	ldrb	w0, [x2, 32]
	cmp	w0, 71
	beq	L119
L116:
	mov	w0, 1
L117:
	eor	w0, w0, 1
L114:
	ret
L119:
	mov	w0, 0
	b	L117
L118:
	mov	w0, 0
	b	L114
LFE21:
	.cstring
	.align	3
l.str.20:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN\0"
	.text
	.align	2
	.globl _cmp_memcmp_40
_cmp_memcmp_40:
LFB22:
	add	x3, x1, 40
	cmp	x3, x2
	bhi	L124
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L122
	ldr	q31, [x2, 16]
	adrp	x0, lC18@PAGE
	ldr	q30, [x0, #lC18@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L122
	ldr	x1, [x2, 32]
	mov	x0, 18503
	movk	x0, 0x4a49, lsl 16
	movk	x0, 0x4c4b, lsl 32
	movk	x0, 0x4e4d, lsl 48
	cmp	x1, x0
	beq	L125
L122:
	mov	w0, 1
L123:
	eor	w0, w0, 1
L120:
	ret
L125:
	mov	w0, 0
	b	L123
L124:
	mov	w0, 0
	b	L120
LFE22:
	.cstring
	.align	3
l.str.21:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV\0"
	.text
	.align	2
	.globl _cmp_memcmp_48
_cmp_memcmp_48:
LFB23:
	add	x3, x1, 48
	cmp	x3, x2
	bhi	L130
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L128
	ldr	q31, [x2, 16]
	adrp	x0, lC18@PAGE
	ldr	q30, [x0, #lC18@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L128
	ldr	q31, [x2, 32]
	adrp	x0, lC22@PAGE
	ldr	q30, [x0, #lC22@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbz	x0, L129
L128:
	mov	w0, 1
L129:
	eor	w0, w0, 1
L126:
	ret
L130:
	mov	w0, 0
	b	L126
LFE23:
	.cstring
	.align	3
l.str.23:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab\0"
	.text
	.align	2
	.globl _cmp_memcmp_64
_cmp_memcmp_64:
LFB24:
	add	x3, x1, 64
	cmp	x3, x2
	bhi	L135
	add	x2, x0, x1
	ldr	q31, [x0, x1]
	adrp	x0, lC12@PAGE
	ldr	q30, [x0, #lC12@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L133
	ldr	q31, [x2, 16]
	adrp	x0, lC18@PAGE
	ldr	q30, [x0, #lC18@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L133
	ldr	q31, [x2, 32]
	adrp	x0, lC22@PAGE
	ldr	q30, [x0, #lC22@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbnz	x0, L133
	ldr	q31, [x2, 48]
	adrp	x0, lC24@PAGE
	ldr	q30, [x0, #lC24@PAGEOFF]
	eor	v31.16b, v31.16b, v30.16b
	umaxp	v31.4s, v31.4s, v31.4s
	fmov	x0, d31
	cbz	x0, L134
L133:
	mov	w0, 1
L134:
	eor	w0, w0, 1
L131:
	ret
L135:
	mov	w0, 0
	b	L131
LFE24:
	.align	2
	.globl _cmp_mask_1
_cmp_mask_1:
LFB25:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L138
	ldrb	w0, [x0, x1]
	cmp	w0, 97
	cset	w0, eq
L136:
	ret
L138:
	mov	w0, 0
	b	L136
LFE25:
	.align	2
	.globl _cmp_mask_2
_cmp_mask_2:
LFB26:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L141
	ldrh	w1, [x0, x1]
	mov	w0, 25185
	cmp	w1, w0
	cset	w0, eq
L139:
	ret
L141:
	mov	w0, 0
	b	L139
LFE26:
	.align	2
	.globl _cmp_mask_3
_cmp_mask_3:
LFB27:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L144
	ldr	w0, [x0, x1]
	and	w0, w0, 16777215
	sub	w0, w0, #6512640
	subs	w0, w0, #609
	cset	w0, eq
L142:
	ret
L144:
	mov	w0, 0
	b	L142
LFE27:
	.align	2
	.globl _cmp_mask_4
_cmp_mask_4:
LFB28:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L147
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	cset	w0, eq
L145:
	ret
L147:
	mov	w0, 0
	b	L145
LFE28:
	.align	2
	.globl _cmp_mask_5
_cmp_mask_5:
LFB29:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L150
	ldr	x0, [x0, x1]
	and	x0, x0, 1099511627775
	mov	x1, 25185
	movk	x1, 0x6463, lsl 16
	movk	x1, 0x65, lsl 32
	cmp	x0, x1
	cset	w0, eq
L148:
	ret
L150:
	mov	w0, 0
	b	L148
LFE29:
	.align	2
	.globl _cmp_mask_6
_cmp_mask_6:
LFB30:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L153
	ldr	x0, [x0, x1]
	and	x0, x0, 281474976710655
	mov	x1, 25185
	movk	x1, 0x6463, lsl 16
	movk	x1, 0x6665, lsl 32
	cmp	x0, x1
	cset	w0, eq
L151:
	ret
L153:
	mov	w0, 0
	b	L151
LFE30:
	.align	2
	.globl _cmp_mask_7
_cmp_mask_7:
LFB31:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L156
	ldr	x0, [x0, x1]
	and	x0, x0, 72057594037927935
	mov	x1, 25185
	movk	x1, 0x6463, lsl 16
	movk	x1, 0x6665, lsl 32
	movk	x1, 0x67, lsl 48
	cmp	x0, x1
	cset	w0, eq
L154:
	ret
L156:
	mov	w0, 0
	b	L154
LFE31:
	.align	2
	.globl _cmp_mask_8
_cmp_mask_8:
LFB32:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L159
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	cset	w0, eq
L157:
	ret
L159:
	mov	w0, 0
	b	L157
LFE32:
	.align	2
	.globl _cmp_overlap_5
_cmp_overlap_5:
LFB33:
	add	x3, x1, 5
	cmp	x3, x2
	bhi	L162
	add	x2, x0, x1
	ldr	w2, [x2, 1]
	ldr	w1, [x0, x1]
	mov	w0, 25442
	movk	w0, 0x6564, lsl 16
	cmp	w2, w0
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	ccmp	w1, w0, 0, eq
	cset	w0, eq
L160:
	ret
L162:
	mov	w0, 0
	b	L160
LFE33:
	.align	2
	.globl _cmp_overlap_6
_cmp_overlap_6:
LFB34:
	add	x3, x1, 6
	cmp	x3, x2
	bhi	L165
	add	x2, x0, x1
	ldr	w2, [x2, 2]
	ldr	w1, [x0, x1]
	mov	w0, 25699
	movk	w0, 0x6665, lsl 16
	cmp	w2, w0
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	ccmp	w1, w0, 0, eq
	cset	w0, eq
L163:
	ret
L165:
	mov	w0, 0
	b	L163
LFE34:
	.align	2
	.globl _cmp_overlap_7
_cmp_overlap_7:
LFB35:
	add	x3, x1, 7
	cmp	x3, x2
	bhi	L168
	add	x2, x0, x1
	ldr	w2, [x2, 3]
	ldr	w1, [x0, x1]
	mov	w0, 25956
	movk	w0, 0x6766, lsl 16
	cmp	w2, w0
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	ccmp	w1, w0, 0, eq
	cset	w0, eq
L166:
	ret
L168:
	mov	w0, 0
	b	L166
LFE35:
	.literal16
	.align	4
lC12:
	.byte	97
	.byte	98
	.byte	99
	.byte	100
	.byte	101
	.byte	102
	.byte	103
	.byte	104
	.byte	105
	.byte	106
	.byte	107
	.byte	108
	.byte	109
	.byte	110
	.byte	111
	.byte	112
	.align	4
lC18:
	.byte	113
	.byte	114
	.byte	115
	.byte	116
	.byte	117
	.byte	118
	.byte	119
	.byte	120
	.byte	121
	.byte	122
	.byte	65
	.byte	66
	.byte	67
	.byte	68
	.byte	69
	.byte	70
	.align	4
lC22:
	.byte	71
	.byte	72
	.byte	73
	.byte	74
	.byte	75
	.byte	76
	.byte	77
	.byte	78
	.byte	79
	.byte	80
	.byte	81
	.byte	82
	.byte	83
	.byte	84
	.byte	85
	.byte	86
	.align	4
lC24:
	.byte	87
	.byte	88
	.byte	89
	.byte	90
	.byte	48
	.byte	49
	.byte	50
	.byte	51
	.byte	52
	.byte	53
	.byte	54
	.byte	55
	.byte	56
	.byte	57
	.byte	97
	.byte	98
	.section __TEXT,__eh_frame,coalesced,no_toc+strip_static_syms+live_support
EH_frame1:
	.set L$set$0,LECIE1-LSCIE1
	.long L$set$0
LSCIE1:
	.long	0
	.byte	0x3
	.ascii "zR\0"
	.uleb128 0x1
	.sleb128 -8
	.uleb128 0x1e
	.uleb128 0x1
	.byte	0x10
	.byte	0xc
	.uleb128 0x1f
	.uleb128 0
	.align	3
LECIE1:
LSFDE1:
	.set L$set$1,LEFDE1-LASFDE1
	.long L$set$1
LASFDE1:
	.long	LASFDE1-EH_frame1
	.quad	LFB0-.
	.set L$set$2,LFE0-LFB0
	.quad L$set$2
	.uleb128 0
	.align	3
LEFDE1:
LSFDE3:
	.set L$set$3,LEFDE3-LASFDE3
	.long L$set$3
LASFDE3:
	.long	LASFDE3-EH_frame1
	.quad	LFB1-.
	.set L$set$4,LFE1-LFB1
	.quad L$set$4
	.uleb128 0
	.align	3
LEFDE3:
LSFDE5:
	.set L$set$5,LEFDE5-LASFDE5
	.long L$set$5
LASFDE5:
	.long	LASFDE5-EH_frame1
	.quad	LFB2-.
	.set L$set$6,LFE2-LFB2
	.quad L$set$6
	.uleb128 0
	.align	3
LEFDE5:
LSFDE7:
	.set L$set$7,LEFDE7-LASFDE7
	.long L$set$7
LASFDE7:
	.long	LASFDE7-EH_frame1
	.quad	LFB3-.
	.set L$set$8,LFE3-LFB3
	.quad L$set$8
	.uleb128 0
	.align	3
LEFDE7:
LSFDE9:
	.set L$set$9,LEFDE9-LASFDE9
	.long L$set$9
LASFDE9:
	.long	LASFDE9-EH_frame1
	.quad	LFB4-.
	.set L$set$10,LFE4-LFB4
	.quad L$set$10
	.uleb128 0
	.align	3
LEFDE9:
LSFDE11:
	.set L$set$11,LEFDE11-LASFDE11
	.long L$set$11
LASFDE11:
	.long	LASFDE11-EH_frame1
	.quad	LFB5-.
	.set L$set$12,LFE5-LFB5
	.quad L$set$12
	.uleb128 0
	.align	3
LEFDE11:
LSFDE13:
	.set L$set$13,LEFDE13-LASFDE13
	.long L$set$13
LASFDE13:
	.long	LASFDE13-EH_frame1
	.quad	LFB6-.
	.set L$set$14,LFE6-LFB6
	.quad L$set$14
	.uleb128 0
	.align	3
LEFDE13:
LSFDE15:
	.set L$set$15,LEFDE15-LASFDE15
	.long L$set$15
LASFDE15:
	.long	LASFDE15-EH_frame1
	.quad	LFB7-.
	.set L$set$16,LFE7-LFB7
	.quad L$set$16
	.uleb128 0
	.align	3
LEFDE15:
LSFDE17:
	.set L$set$17,LEFDE17-LASFDE17
	.long L$set$17
LASFDE17:
	.long	LASFDE17-EH_frame1
	.quad	LFB8-.
	.set L$set$18,LFE8-LFB8
	.quad L$set$18
	.uleb128 0
	.align	3
LEFDE17:
LSFDE19:
	.set L$set$19,LEFDE19-LASFDE19
	.long L$set$19
LASFDE19:
	.long	LASFDE19-EH_frame1
	.quad	LFB9-.
	.set L$set$20,LFE9-LFB9
	.quad L$set$20
	.uleb128 0
	.align	3
LEFDE19:
LSFDE21:
	.set L$set$21,LEFDE21-LASFDE21
	.long L$set$21
LASFDE21:
	.long	LASFDE21-EH_frame1
	.quad	LFB10-.
	.set L$set$22,LFE10-LFB10
	.quad L$set$22
	.uleb128 0
	.align	3
LEFDE21:
LSFDE23:
	.set L$set$23,LEFDE23-LASFDE23
	.long L$set$23
LASFDE23:
	.long	LASFDE23-EH_frame1
	.quad	LFB11-.
	.set L$set$24,LFE11-LFB11
	.quad L$set$24
	.uleb128 0
	.align	3
LEFDE23:
LSFDE25:
	.set L$set$25,LEFDE25-LASFDE25
	.long L$set$25
LASFDE25:
	.long	LASFDE25-EH_frame1
	.quad	LFB12-.
	.set L$set$26,LFE12-LFB12
	.quad L$set$26
	.uleb128 0
	.align	3
LEFDE25:
LSFDE27:
	.set L$set$27,LEFDE27-LASFDE27
	.long L$set$27
LASFDE27:
	.long	LASFDE27-EH_frame1
	.quad	LFB13-.
	.set L$set$28,LFE13-LFB13
	.quad L$set$28
	.uleb128 0
	.align	3
LEFDE27:
LSFDE29:
	.set L$set$29,LEFDE29-LASFDE29
	.long L$set$29
LASFDE29:
	.long	LASFDE29-EH_frame1
	.quad	LFB14-.
	.set L$set$30,LFE14-LFB14
	.quad L$set$30
	.uleb128 0
	.align	3
LEFDE29:
LSFDE31:
	.set L$set$31,LEFDE31-LASFDE31
	.long L$set$31
LASFDE31:
	.long	LASFDE31-EH_frame1
	.quad	LFB15-.
	.set L$set$32,LFE15-LFB15
	.quad L$set$32
	.uleb128 0
	.align	3
LEFDE31:
LSFDE33:
	.set L$set$33,LEFDE33-LASFDE33
	.long L$set$33
LASFDE33:
	.long	LASFDE33-EH_frame1
	.quad	LFB16-.
	.set L$set$34,LFE16-LFB16
	.quad L$set$34
	.uleb128 0
	.align	3
LEFDE33:
LSFDE35:
	.set L$set$35,LEFDE35-LASFDE35
	.long L$set$35
LASFDE35:
	.long	LASFDE35-EH_frame1
	.quad	LFB17-.
	.set L$set$36,LFE17-LFB17
	.quad L$set$36
	.uleb128 0
	.align	3
LEFDE35:
LSFDE37:
	.set L$set$37,LEFDE37-LASFDE37
	.long L$set$37
LASFDE37:
	.long	LASFDE37-EH_frame1
	.quad	LFB18-.
	.set L$set$38,LFE18-LFB18
	.quad L$set$38
	.uleb128 0
	.align	3
LEFDE37:
LSFDE39:
	.set L$set$39,LEFDE39-LASFDE39
	.long L$set$39
LASFDE39:
	.long	LASFDE39-EH_frame1
	.quad	LFB19-.
	.set L$set$40,LFE19-LFB19
	.quad L$set$40
	.uleb128 0
	.byte	0x4
	.set L$set$41,LCFI0-LFB19
	.long L$set$41
	.byte	0xe
	.uleb128 0x10
	.byte	0x9d
	.uleb128 0x2
	.byte	0x9e
	.uleb128 0x1
	.byte	0x4
	.set L$set$42,LCFI1-LCFI0
	.long L$set$42
	.byte	0xd
	.uleb128 0x1d
	.byte	0x4
	.set L$set$43,LCFI2-LCFI1
	.long L$set$43
	.byte	0xde
	.byte	0xdd
	.byte	0xc
	.uleb128 0x1f
	.uleb128 0
	.align	3
LEFDE39:
LSFDE41:
	.set L$set$44,LEFDE41-LASFDE41
	.long L$set$44
LASFDE41:
	.long	LASFDE41-EH_frame1
	.quad	LFB20-.
	.set L$set$45,LFE20-LFB20
	.quad L$set$45
	.uleb128 0
	.align	3
LEFDE41:
LSFDE43:
	.set L$set$46,LEFDE43-LASFDE43
	.long L$set$46
LASFDE43:
	.long	LASFDE43-EH_frame1
	.quad	LFB21-.
	.set L$set$47,LFE21-LFB21
	.quad L$set$47
	.uleb128 0
	.align	3
LEFDE43:
LSFDE45:
	.set L$set$48,LEFDE45-LASFDE45
	.long L$set$48
LASFDE45:
	.long	LASFDE45-EH_frame1
	.quad	LFB22-.
	.set L$set$49,LFE22-LFB22
	.quad L$set$49
	.uleb128 0
	.align	3
LEFDE45:
LSFDE47:
	.set L$set$50,LEFDE47-LASFDE47
	.long L$set$50
LASFDE47:
	.long	LASFDE47-EH_frame1
	.quad	LFB23-.
	.set L$set$51,LFE23-LFB23
	.quad L$set$51
	.uleb128 0
	.align	3
LEFDE47:
LSFDE49:
	.set L$set$52,LEFDE49-LASFDE49
	.long L$set$52
LASFDE49:
	.long	LASFDE49-EH_frame1
	.quad	LFB24-.
	.set L$set$53,LFE24-LFB24
	.quad L$set$53
	.uleb128 0
	.align	3
LEFDE49:
LSFDE51:
	.set L$set$54,LEFDE51-LASFDE51
	.long L$set$54
LASFDE51:
	.long	LASFDE51-EH_frame1
	.quad	LFB25-.
	.set L$set$55,LFE25-LFB25
	.quad L$set$55
	.uleb128 0
	.align	3
LEFDE51:
LSFDE53:
	.set L$set$56,LEFDE53-LASFDE53
	.long L$set$56
LASFDE53:
	.long	LASFDE53-EH_frame1
	.quad	LFB26-.
	.set L$set$57,LFE26-LFB26
	.quad L$set$57
	.uleb128 0
	.align	3
LEFDE53:
LSFDE55:
	.set L$set$58,LEFDE55-LASFDE55
	.long L$set$58
LASFDE55:
	.long	LASFDE55-EH_frame1
	.quad	LFB27-.
	.set L$set$59,LFE27-LFB27
	.quad L$set$59
	.uleb128 0
	.align	3
LEFDE55:
LSFDE57:
	.set L$set$60,LEFDE57-LASFDE57
	.long L$set$60
LASFDE57:
	.long	LASFDE57-EH_frame1
	.quad	LFB28-.
	.set L$set$61,LFE28-LFB28
	.quad L$set$61
	.uleb128 0
	.align	3
LEFDE57:
LSFDE59:
	.set L$set$62,LEFDE59-LASFDE59
	.long L$set$62
LASFDE59:
	.long	LASFDE59-EH_frame1
	.quad	LFB29-.
	.set L$set$63,LFE29-LFB29
	.quad L$set$63
	.uleb128 0
	.align	3
LEFDE59:
LSFDE61:
	.set L$set$64,LEFDE61-LASFDE61
	.long L$set$64
LASFDE61:
	.long	LASFDE61-EH_frame1
	.quad	LFB30-.
	.set L$set$65,LFE30-LFB30
	.quad L$set$65
	.uleb128 0
	.align	3
LEFDE61:
LSFDE63:
	.set L$set$66,LEFDE63-LASFDE63
	.long L$set$66
LASFDE63:
	.long	LASFDE63-EH_frame1
	.quad	LFB31-.
	.set L$set$67,LFE31-LFB31
	.quad L$set$67
	.uleb128 0
	.align	3
LEFDE63:
LSFDE65:
	.set L$set$68,LEFDE65-LASFDE65
	.long L$set$68
LASFDE65:
	.long	LASFDE65-EH_frame1
	.quad	LFB32-.
	.set L$set$69,LFE32-LFB32
	.quad L$set$69
	.uleb128 0
	.align	3
LEFDE65:
LSFDE67:
	.set L$set$70,LEFDE67-LASFDE67
	.long L$set$70
LASFDE67:
	.long	LASFDE67-EH_frame1
	.quad	LFB33-.
	.set L$set$71,LFE33-LFB33
	.quad L$set$71
	.uleb128 0
	.align	3
LEFDE67:
LSFDE69:
	.set L$set$72,LEFDE69-LASFDE69
	.long L$set$72
LASFDE69:
	.long	LASFDE69-EH_frame1
	.quad	LFB34-.
	.set L$set$73,LFE34-LFB34
	.quad L$set$73
	.uleb128 0
	.align	3
LEFDE69:
LSFDE71:
	.set L$set$74,LEFDE71-LASFDE71
	.long L$set$74
LASFDE71:
	.long	LASFDE71-EH_frame1
	.quad	LFB35-.
	.set L$set$75,LFE35-LFB35
	.quad L$set$75
	.uleb128 0
	.align	3
LEFDE71:
	.ident	"GCC: (Homebrew GCC 16.2.0) 16.2.0"
	.subsections_via_symbols
