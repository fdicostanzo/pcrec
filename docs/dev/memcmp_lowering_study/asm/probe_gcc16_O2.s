	.arch armv8.5-a
	.build_version macos,  26, 0
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_1
_cmp_memcmp_1:
LFB0:
	add	x3, x1, 1
	cmp	x3, x2
	bhi	L3
	ldrb	w0, [x0, x1]
	cmp	w0, 97
	cset	w0, eq
	ret
	.p2align 2,,3
L3:
	mov	w0, 0
	ret
LFE0:
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_2
_cmp_memcmp_2:
LFB1:
	add	x3, x1, 2
	cmp	x3, x2
	bhi	L7
	ldrh	w1, [x0, x1]
	mov	w0, 25185
	cmp	w1, w0
	cset	w0, eq
	ret
	.p2align 2,,3
L7:
	mov	w0, 0
	ret
LFE1:
	.cstring
	.align	3
l.str.0:
	.ascii "abc\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_3
_cmp_memcmp_3:
LFB2:
	add	x3, x1, 3
	cmp	x3, x2
	bhi	L12
	add	x2, x0, x1
	ldrh	w1, [x0, x1]
	mov	w0, 25185
	cmp	w1, w0
	beq	L13
L10:
	mov	w0, 1
	eor	w0, w0, 1
L8:
	ret
	.p2align 2,,3
L12:
	mov	w0, 0
	ret
	.p2align 2,,3
L13:
	ldrb	w0, [x2, 2]
	cmp	w0, 99
	bne	L10
	mov	w0, 0
	eor	w0, w0, 1
	b	L8
LFE2:
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_4
_cmp_memcmp_4:
LFB3:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L16
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	cset	w0, eq
	ret
	.p2align 2,,3
L16:
	mov	w0, 0
	ret
LFE3:
	.cstring
	.align	3
l.str.1:
	.ascii "abcde\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_5
_cmp_memcmp_5:
LFB4:
	add	x3, x1, 5
	cmp	x3, x2
	bhi	L21
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	beq	L22
L19:
	mov	w0, 1
	eor	w0, w0, 1
L17:
	ret
	.p2align 2,,3
L21:
	mov	w0, 0
	ret
	.p2align 2,,3
L22:
	ldrb	w0, [x2, 4]
	cmp	w0, 101
	bne	L19
	mov	w0, 0
	eor	w0, w0, 1
	b	L17
LFE4:
	.cstring
	.align	3
l.str.2:
	.ascii "abcdef\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_6
_cmp_memcmp_6:
LFB5:
	add	x3, x1, 6
	cmp	x3, x2
	bhi	L27
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	beq	L28
L25:
	mov	w0, 1
	eor	w0, w0, 1
L23:
	ret
	.p2align 2,,3
L27:
	mov	w0, 0
	ret
	.p2align 2,,3
L28:
	ldrh	w1, [x2, 4]
	mov	w0, 26213
	cmp	w1, w0
	bne	L25
	mov	w0, 0
	eor	w0, w0, 1
	b	L23
LFE5:
	.cstring
	.align	3
l.str.3:
	.ascii "abcdefg\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_7
_cmp_memcmp_7:
LFB6:
	add	x3, x1, 7
	cmp	x3, x2
	bhi	L33
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	beq	L34
L31:
	mov	w0, 1
	eor	w0, w0, 1
L29:
	ret
	.p2align 2,,3
L33:
	mov	w0, 0
	ret
	.p2align 2,,3
L34:
	ldrh	w1, [x2, 4]
	mov	w0, 26213
	cmp	w1, w0
	bne	L31
	ldrb	w0, [x2, 6]
	cmp	w0, 103
	bne	L31
	mov	w0, 0
	eor	w0, w0, 1
	b	L29
LFE6:
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_8
_cmp_memcmp_8:
LFB7:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L37
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	cset	w0, eq
	ret
	.p2align 2,,3
L37:
	mov	w0, 0
	ret
LFE7:
	.cstring
	.align	3
l.str.4:
	.ascii "abcdefghi\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_9
_cmp_memcmp_9:
LFB8:
	add	x3, x1, 9
	cmp	x3, x2
	bhi	L42
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L43
L40:
	mov	w0, 1
	eor	w0, w0, 1
L38:
	ret
	.p2align 2,,3
L42:
	mov	w0, 0
	ret
	.p2align 2,,3
L43:
	ldrb	w0, [x2, 8]
	cmp	w0, 105
	bne	L40
	mov	w0, 0
	eor	w0, w0, 1
	b	L38
LFE8:
	.cstring
	.align	3
l.str.5:
	.ascii "abcdefghij\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_10
_cmp_memcmp_10:
LFB9:
	add	x3, x1, 10
	cmp	x3, x2
	bhi	L48
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L49
L46:
	mov	w0, 1
	eor	w0, w0, 1
L44:
	ret
	.p2align 2,,3
L48:
	mov	w0, 0
	ret
	.p2align 2,,3
L49:
	ldrh	w1, [x2, 8]
	mov	w0, 27241
	cmp	w1, w0
	bne	L46
	mov	w0, 0
	eor	w0, w0, 1
	b	L44
LFE9:
	.cstring
	.align	3
l.str.6:
	.ascii "abcdefghijk\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_11
_cmp_memcmp_11:
LFB10:
	add	x3, x1, 11
	cmp	x3, x2
	bhi	L54
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L55
L52:
	mov	w0, 1
	eor	w0, w0, 1
L50:
	ret
	.p2align 2,,3
L54:
	mov	w0, 0
	ret
	.p2align 2,,3
L55:
	ldrh	w1, [x2, 8]
	mov	w0, 27241
	cmp	w1, w0
	bne	L52
	ldrb	w0, [x2, 10]
	cmp	w0, 107
	bne	L52
	mov	w0, 0
	eor	w0, w0, 1
	b	L50
LFE10:
	.cstring
	.align	3
l.str.7:
	.ascii "abcdefghijkl\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_12
_cmp_memcmp_12:
LFB11:
	add	x3, x1, 12
	cmp	x3, x2
	bhi	L60
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L61
L58:
	mov	w0, 1
	eor	w0, w0, 1
L56:
	ret
	.p2align 2,,3
L60:
	mov	w0, 0
	ret
	.p2align 2,,3
L61:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L58
	mov	w0, 0
	eor	w0, w0, 1
	b	L56
LFE11:
	.cstring
	.align	3
l.str.8:
	.ascii "abcdefghijklm\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_13
_cmp_memcmp_13:
LFB12:
	add	x3, x1, 13
	cmp	x3, x2
	bhi	L66
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L67
L64:
	mov	w0, 1
	eor	w0, w0, 1
L62:
	ret
	.p2align 2,,3
L66:
	mov	w0, 0
	ret
	.p2align 2,,3
L67:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L64
	ldrb	w0, [x2, 12]
	cmp	w0, 109
	bne	L64
	mov	w0, 0
	eor	w0, w0, 1
	b	L62
LFE12:
	.cstring
	.align	3
l.str.9:
	.ascii "abcdefghijklmn\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_14
_cmp_memcmp_14:
LFB13:
	add	x3, x1, 14
	cmp	x3, x2
	bhi	L72
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L73
L70:
	mov	w0, 1
	eor	w0, w0, 1
L68:
	ret
	.p2align 2,,3
L72:
	mov	w0, 0
	ret
	.p2align 2,,3
L73:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L70
	ldrh	w1, [x2, 12]
	mov	w0, 28269
	cmp	w1, w0
	bne	L70
	mov	w0, 0
	eor	w0, w0, 1
	b	L68
LFE13:
	.cstring
	.align	3
l.str.10:
	.ascii "abcdefghijklmno\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_15
_cmp_memcmp_15:
LFB14:
	add	x3, x1, 15
	cmp	x3, x2
	bhi	L78
	add	x2, x0, x1
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	beq	L79
L76:
	mov	w0, 1
	eor	w0, w0, 1
L74:
	ret
	.p2align 2,,3
L78:
	mov	w0, 0
	ret
	.p2align 2,,3
L79:
	ldr	w1, [x2, 8]
	mov	w0, 27241
	movk	w0, 0x6c6b, lsl 16
	cmp	w1, w0
	bne	L76
	ldrh	w1, [x2, 12]
	mov	w0, 28269
	cmp	w1, w0
	bne	L76
	ldrb	w0, [x2, 14]
	cmp	w0, 111
	bne	L76
	mov	w0, 0
	eor	w0, w0, 1
	b	L74
LFE14:
	.cstring
	.align	3
l.str.11:
	.ascii "abcdefghijklmnop\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_16
_cmp_memcmp_16:
LFB15:
	add	x3, x1, 16
	cmp	x3, x2
	bhi	L84
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cmp	x0, 0
	cset	w0, eq
	ret
	.p2align 2,,3
L84:
	mov	w0, 0
	ret
LFE15:
	.cstring
	.align	3
l.str.13:
	.ascii "abcdefghijklmnopq\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_17
_cmp_memcmp_17:
LFB16:
	add	x3, x1, 17
	cmp	x3, x2
	bhi	L89
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L90
L87:
	mov	w0, 1
	eor	w0, w0, 1
L85:
	ret
	.p2align 2,,3
L89:
	mov	w0, 0
	ret
	.p2align 2,,3
L90:
	ldrb	w0, [x3, 16]
	cmp	w0, 113
	bne	L87
	mov	w0, 0
	eor	w0, w0, 1
	b	L85
LFE16:
	.cstring
	.align	3
l.str.14:
	.ascii "abcdefghijklmnopqrst\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_20
_cmp_memcmp_20:
LFB17:
	add	x3, x1, 20
	cmp	x3, x2
	bhi	L95
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L96
L93:
	mov	w0, 1
	eor	w0, w0, 1
L91:
	ret
	.p2align 2,,3
L95:
	mov	w0, 0
	ret
	.p2align 2,,3
L96:
	ldr	w1, [x3, 16]
	mov	w0, 29297
	movk	w0, 0x7473, lsl 16
	cmp	w1, w0
	bne	L93
	mov	w0, 0
	eor	w0, w0, 1
	b	L91
LFE17:
	.cstring
	.align	3
l.str.15:
	.ascii "abcdefghijklmnopqrstuvwx\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_24
_cmp_memcmp_24:
LFB18:
	add	x3, x1, 24
	cmp	x3, x2
	bhi	L101
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L102
L99:
	mov	w0, 1
	eor	w0, w0, 1
L97:
	ret
	.p2align 2,,3
L101:
	mov	w0, 0
	ret
	.p2align 2,,3
L102:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L99
	mov	w0, 0
	eor	w0, w0, 1
	b	L97
LFE18:
	.cstring
	.align	3
l.str.16:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDE\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_31
_cmp_memcmp_31:
LFB19:
	add	x3, x1, 31
	cmp	x3, x2
	bhi	L105
	add	x0, x0, x1
	adrp	x1, l.str.16@PAGE
	stp	x29, x30, [sp, -16]!
LCFI0:
	mov	x2, 31
	mov	x29, sp
LCFI1:
	add	x1, x1, l.str.16@PAGEOFF;
	bl	_memcmp
	cmp	w0, 0
	ldp	x29, x30, [sp], 16
LCFI2:
	cset	w0, eq
	ret
	.p2align 2,,3
L105:
	mov	w0, 0
	ret
LFE19:
	.cstring
	.align	3
l.str.17:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEF\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_32
_cmp_memcmp_32:
LFB20:
	add	x3, x1, 32
	cmp	x3, x2
	bhi	L114
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L115
	mov	w0, 1
L113:
	eor	w0, w0, 1
	ret
	.p2align 2,,3
L114:
	mov	w0, 0
	ret
	.p2align 2,,3
L115:
	adrp	x0, lC18@PAGE
	ldr	q28, [x3, 16]
	ldr	q29, [x0, #lC18@PAGEOFF]
	eor	v28.16b, v28.16b, v29.16b
	umaxp	v28.4s, v28.4s, v28.4s
	fmov	x0, d28
	cbz	x0, L113
	mov	w0, 1
	b	L113
LFE20:
	.cstring
	.align	3
l.str.19:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFG\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_33
_cmp_memcmp_33:
LFB21:
	add	x3, x1, 33
	cmp	x3, x2
	bhi	L120
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L121
L118:
	mov	w0, 1
	eor	w0, w0, 1
L116:
	ret
	.p2align 2,,3
L120:
	mov	w0, 0
	ret
	.p2align 2,,3
L121:
	adrp	x0, lC18@PAGE
	ldr	q28, [x3, 16]
	ldr	q29, [x0, #lC18@PAGEOFF]
	eor	v28.16b, v28.16b, v29.16b
	umaxp	v28.4s, v28.4s, v28.4s
	fmov	x0, d28
	cbnz	x0, L118
	ldrb	w0, [x3, 32]
	cmp	w0, 71
	bne	L118
	mov	w0, 0
	eor	w0, w0, 1
	b	L116
LFE21:
	.cstring
	.align	3
l.str.20:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_40
_cmp_memcmp_40:
LFB22:
	add	x3, x1, 40
	cmp	x3, x2
	bhi	L126
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L127
L124:
	mov	w0, 1
	eor	w0, w0, 1
L122:
	ret
	.p2align 2,,3
L126:
	mov	w0, 0
	ret
	.p2align 2,,3
L127:
	adrp	x0, lC18@PAGE
	ldr	q28, [x3, 16]
	ldr	q29, [x0, #lC18@PAGEOFF]
	eor	v28.16b, v28.16b, v29.16b
	umaxp	v28.4s, v28.4s, v28.4s
	fmov	x0, d28
	cbnz	x0, L124
	ldr	x1, [x3, 32]
	mov	x0, 18503
	movk	x0, 0x4a49, lsl 16
	movk	x0, 0x4c4b, lsl 32
	movk	x0, 0x4e4d, lsl 48
	cmp	x1, x0
	bne	L124
	mov	w0, 0
	eor	w0, w0, 1
	b	L122
LFE22:
	.cstring
	.align	3
l.str.21:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_48
_cmp_memcmp_48:
LFB23:
	add	x3, x1, 48
	cmp	x3, x2
	bhi	L132
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L133
L130:
	mov	w0, 1
L131:
	eor	w0, w0, 1
	ret
	.p2align 2,,3
L132:
	mov	w0, 0
	ret
	.p2align 2,,3
L133:
	adrp	x0, lC18@PAGE
	ldr	q28, [x3, 16]
	ldr	q29, [x0, #lC18@PAGEOFF]
	eor	v28.16b, v28.16b, v29.16b
	umaxp	v28.4s, v28.4s, v28.4s
	fmov	x0, d28
	cbnz	x0, L130
	adrp	x0, lC22@PAGE
	ldr	q26, [x3, 32]
	ldr	q27, [x0, #lC22@PAGEOFF]
	eor	v26.16b, v26.16b, v27.16b
	umaxp	v26.4s, v26.4s, v26.4s
	fmov	x0, d26
	cbz	x0, L131
	mov	w0, 1
	b	L131
LFE23:
	.cstring
	.align	3
l.str.23:
	.ascii "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_64
_cmp_memcmp_64:
LFB24:
	add	x3, x1, 64
	cmp	x3, x2
	bhi	L138
	adrp	x2, lC12@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC12@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L139
L136:
	mov	w0, 1
L137:
	eor	w0, w0, 1
	ret
	.p2align 2,,3
L138:
	mov	w0, 0
	ret
	.p2align 2,,3
L139:
	adrp	x0, lC18@PAGE
	ldr	q28, [x3, 16]
	ldr	q29, [x0, #lC18@PAGEOFF]
	eor	v28.16b, v28.16b, v29.16b
	umaxp	v28.4s, v28.4s, v28.4s
	fmov	x0, d28
	cbnz	x0, L136
	adrp	x0, lC22@PAGE
	ldr	q26, [x3, 32]
	ldr	q27, [x0, #lC22@PAGEOFF]
	eor	v26.16b, v26.16b, v27.16b
	umaxp	v26.4s, v26.4s, v26.4s
	fmov	x0, d26
	cbnz	x0, L136
	adrp	x0, lC24@PAGE
	ldr	q24, [x3, 48]
	ldr	q25, [x0, #lC24@PAGEOFF]
	eor	v24.16b, v24.16b, v25.16b
	umaxp	v24.4s, v24.4s, v24.4s
	fmov	x0, d24
	cbz	x0, L137
	mov	w0, 1
	b	L137
LFE24:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_1
_cmp_mask_1:
LFB25:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L142
	ldrb	w0, [x0, x1]
	cmp	w0, 97
	cset	w0, eq
	ret
	.p2align 2,,3
L142:
	mov	w0, 0
	ret
LFE25:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_2
_cmp_mask_2:
LFB26:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L145
	ldrh	w1, [x0, x1]
	mov	w0, 25185
	cmp	w1, w0
	cset	w0, eq
	ret
	.p2align 2,,3
L145:
	mov	w0, 0
	ret
LFE26:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_3
_cmp_mask_3:
LFB27:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L148
	ldr	w0, [x0, x1]
	and	w0, w0, 16777215
	sub	w0, w0, #6512640
	subs	w0, w0, #609
	cset	w0, eq
	ret
	.p2align 2,,3
L148:
	mov	w0, 0
	ret
LFE27:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_4
_cmp_mask_4:
LFB28:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L151
	ldr	w1, [x0, x1]
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	cmp	w1, w0
	cset	w0, eq
	ret
	.p2align 2,,3
L151:
	mov	w0, 0
	ret
LFE28:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_5
_cmp_mask_5:
LFB29:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L154
	ldr	x0, [x0, x1]
	mov	x1, 25185
	movk	x1, 0x6463, lsl 16
	movk	x1, 0x65, lsl 32
	and	x0, x0, 1099511627775
	cmp	x0, x1
	cset	w0, eq
	ret
	.p2align 2,,3
L154:
	mov	w0, 0
	ret
LFE29:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_6
_cmp_mask_6:
LFB30:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L157
	ldr	x0, [x0, x1]
	mov	x1, 25185
	movk	x1, 0x6463, lsl 16
	movk	x1, 0x6665, lsl 32
	and	x0, x0, 281474976710655
	cmp	x0, x1
	cset	w0, eq
	ret
	.p2align 2,,3
L157:
	mov	w0, 0
	ret
LFE30:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_7
_cmp_mask_7:
LFB31:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L160
	ldr	x0, [x0, x1]
	mov	x1, 25185
	movk	x1, 0x6463, lsl 16
	movk	x1, 0x6665, lsl 32
	movk	x1, 0x67, lsl 48
	and	x0, x0, 72057594037927935
	cmp	x0, x1
	cset	w0, eq
	ret
	.p2align 2,,3
L160:
	mov	w0, 0
	ret
LFE31:
	.align	2
	.p2align 5,,15
	.globl _cmp_mask_8
_cmp_mask_8:
LFB32:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L163
	ldr	x1, [x0, x1]
	mov	x0, 25185
	movk	x0, 0x6463, lsl 16
	movk	x0, 0x6665, lsl 32
	movk	x0, 0x6867, lsl 48
	cmp	x1, x0
	cset	w0, eq
	ret
	.p2align 2,,3
L163:
	mov	w0, 0
	ret
LFE32:
	.align	2
	.p2align 5,,15
	.globl _cmp_overlap_5
_cmp_overlap_5:
LFB33:
	add	x3, x1, 5
	cmp	x3, x2
	bhi	L166
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25442
	movk	w0, 0x6564, lsl 16
	ldr	w2, [x2, 1]
	cmp	w2, w0
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	ccmp	w1, w0, 0, eq
	cset	w0, eq
	ret
	.p2align 2,,3
L166:
	mov	w0, 0
	ret
LFE33:
	.align	2
	.p2align 5,,15
	.globl _cmp_overlap_6
_cmp_overlap_6:
LFB34:
	add	x3, x1, 6
	cmp	x3, x2
	bhi	L169
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25699
	movk	w0, 0x6665, lsl 16
	ldr	w2, [x2, 2]
	cmp	w2, w0
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	ccmp	w1, w0, 0, eq
	cset	w0, eq
	ret
	.p2align 2,,3
L169:
	mov	w0, 0
	ret
LFE34:
	.align	2
	.p2align 5,,15
	.globl _cmp_overlap_7
_cmp_overlap_7:
LFB35:
	add	x3, x1, 7
	cmp	x3, x2
	bhi	L172
	add	x2, x0, x1
	ldr	w1, [x0, x1]
	mov	w0, 25956
	movk	w0, 0x6766, lsl 16
	ldr	w2, [x2, 3]
	cmp	w2, w0
	mov	w0, 25185
	movk	w0, 0x6463, lsl 16
	ccmp	w1, w0, 0, eq
	cset	w0, eq
	ret
	.p2align 2,,3
L172:
	mov	w0, 0
	ret
LFE35:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_3
_cmp_ovmask_3:
LFB36:
	add	x3, x1, 3
	cmp	x3, x2
	bhi	L176
	ldrh	w2, [x0, x1]
	mov	w3, -8225
	mov	w4, 16961
	and	w2, w2, w3
	and	w2, w2, 65535
	cmp	w2, w4
	beq	L177
L176:
	mov	w0, 0
	ret
	.p2align 2,,3
L177:
	add	x0, x0, x1
	mov	w1, 17218
	ldrh	w0, [x0, 1]
	and	w0, w0, w3
	and	w0, w0, 65535
	cmp	w0, w1
	cset	w0, eq
	ret
LFE36:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_4
_cmp_ovmask_4:
LFB37:
	add	x3, x1, 4
	cmp	x3, x2
	bhi	L181
	ldrh	w2, [x0, x1]
	mov	w3, -8225
	mov	w4, 16961
	and	w2, w2, w3
	and	w2, w2, 65535
	cmp	w2, w4
	beq	L182
L181:
	mov	w0, 0
	ret
	.p2align 2,,3
L182:
	add	x0, x0, x1
	mov	w1, 17475
	ldrh	w0, [x0, 2]
	and	w0, w0, w3
	and	w0, w0, 65535
	cmp	w0, w1
	cset	w0, eq
	ret
LFE37:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_5
_cmp_ovmask_5:
LFB38:
	add	x3, x1, 5
	cmp	x3, x2
	bhi	L186
	ldr	w2, [x0, x1]
	mov	w3, 16961
	movk	w3, 0x4443, lsl 16
	and	w2, w2, -538976289
	cmp	w2, w3
	beq	L187
L186:
	mov	w0, 0
	ret
	.p2align 2,,3
L187:
	add	x0, x0, x1
	mov	w1, 17218
	ldr	w0, [x0, 1]
	movk	w1, 0x4544, lsl 16
	and	w0, w0, -538976289
	cmp	w0, w1
	cset	w0, eq
	ret
LFE38:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_6
_cmp_ovmask_6:
LFB39:
	add	x3, x1, 6
	cmp	x3, x2
	bhi	L191
	ldr	w2, [x0, x1]
	mov	w3, 16961
	movk	w3, 0x4443, lsl 16
	and	w2, w2, -538976289
	cmp	w2, w3
	beq	L192
L191:
	mov	w0, 0
	ret
	.p2align 2,,3
L192:
	add	x0, x0, x1
	mov	w1, 17475
	ldr	w0, [x0, 2]
	movk	w1, 0x4645, lsl 16
	and	w0, w0, -538976289
	cmp	w0, w1
	cset	w0, eq
	ret
LFE39:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_7
_cmp_ovmask_7:
LFB40:
	add	x3, x1, 7
	cmp	x3, x2
	bhi	L196
	ldr	w2, [x0, x1]
	mov	w3, 16961
	movk	w3, 0x4443, lsl 16
	and	w2, w2, -538976289
	cmp	w2, w3
	beq	L197
L196:
	mov	w0, 0
	ret
	.p2align 2,,3
L197:
	add	x0, x0, x1
	mov	w1, 17732
	ldr	w0, [x0, 3]
	movk	w1, 0x4746, lsl 16
	and	w0, w0, -538976289
	cmp	w0, w1
	cset	w0, eq
	ret
LFE40:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_8
_cmp_ovmask_8:
LFB41:
	add	x3, x1, 8
	cmp	x3, x2
	bhi	L201
	ldr	w2, [x0, x1]
	mov	w3, 16961
	movk	w3, 0x4443, lsl 16
	and	w2, w2, -538976289
	cmp	w2, w3
	beq	L202
L201:
	mov	w0, 0
	ret
	.p2align 2,,3
L202:
	add	x0, x0, x1
	mov	w1, 17989
	ldr	w0, [x0, 4]
	movk	w1, 0x4847, lsl 16
	and	w0, w0, -538976289
	cmp	w0, w1
	cset	w0, eq
	ret
LFE41:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_9
_cmp_ovmask_9:
LFB42:
	add	x3, x1, 9
	cmp	x3, x2
	bhi	L206
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L207
L206:
	mov	w0, 0
	ret
	.p2align 2,,3
L207:
	add	x0, x0, x1
	mov	x1, 17218
	ldr	x0, [x0, 1]
	movk	x1, 0x4544, lsl 16
	movk	x1, 0x4746, lsl 32
	movk	x1, 0x4948, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE42:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_10
_cmp_ovmask_10:
LFB43:
	add	x3, x1, 10
	cmp	x3, x2
	bhi	L211
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L212
L211:
	mov	w0, 0
	ret
	.p2align 2,,3
L212:
	add	x0, x0, x1
	mov	x1, 17475
	ldr	x0, [x0, 2]
	movk	x1, 0x4645, lsl 16
	movk	x1, 0x4847, lsl 32
	movk	x1, 0x4a49, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE43:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_11
_cmp_ovmask_11:
LFB44:
	add	x3, x1, 11
	cmp	x3, x2
	bhi	L216
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L217
L216:
	mov	w0, 0
	ret
	.p2align 2,,3
L217:
	add	x0, x0, x1
	mov	x1, 17732
	ldr	x0, [x0, 3]
	movk	x1, 0x4746, lsl 16
	movk	x1, 0x4948, lsl 32
	movk	x1, 0x4b4a, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE44:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_12
_cmp_ovmask_12:
LFB45:
	add	x3, x1, 12
	cmp	x3, x2
	bhi	L221
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L222
L221:
	mov	w0, 0
	ret
	.p2align 2,,3
L222:
	add	x0, x0, x1
	mov	x1, 17989
	ldr	x0, [x0, 4]
	movk	x1, 0x4847, lsl 16
	movk	x1, 0x4a49, lsl 32
	movk	x1, 0x4c4b, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE45:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_13
_cmp_ovmask_13:
LFB46:
	add	x3, x1, 13
	cmp	x3, x2
	bhi	L226
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L227
L226:
	mov	w0, 0
	ret
	.p2align 2,,3
L227:
	add	x0, x0, x1
	mov	x1, 18246
	ldr	x0, [x0, 5]
	movk	x1, 0x4948, lsl 16
	movk	x1, 0x4b4a, lsl 32
	movk	x1, 0x4d4c, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE46:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_14
_cmp_ovmask_14:
LFB47:
	add	x3, x1, 14
	cmp	x3, x2
	bhi	L231
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L232
L231:
	mov	w0, 0
	ret
	.p2align 2,,3
L232:
	add	x0, x0, x1
	mov	x1, 18503
	ldr	x0, [x0, 6]
	movk	x1, 0x4a49, lsl 16
	movk	x1, 0x4c4b, lsl 32
	movk	x1, 0x4e4d, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE47:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_15
_cmp_ovmask_15:
LFB48:
	add	x3, x1, 15
	cmp	x3, x2
	bhi	L236
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L237
L236:
	mov	w0, 0
	ret
	.p2align 2,,3
L237:
	add	x0, x0, x1
	mov	x1, 18760
	ldr	x0, [x0, 7]
	movk	x1, 0x4b4a, lsl 16
	movk	x1, 0x4d4c, lsl 32
	movk	x1, 0x4f4e, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE48:
	.align	2
	.p2align 5,,15
	.globl _cmp_ovmask_16
_cmp_ovmask_16:
LFB49:
	add	x3, x1, 16
	cmp	x3, x2
	bhi	L241
	ldr	x2, [x0, x1]
	mov	x3, 16961
	movk	x3, 0x4443, lsl 16
	movk	x3, 0x4645, lsl 32
	movk	x3, 0x4847, lsl 48
	and	x2, x2, -2314885530818453537
	cmp	x2, x3
	beq	L242
L241:
	mov	w0, 0
	ret
	.p2align 2,,3
L242:
	add	x0, x0, x1
	mov	x1, 19017
	ldr	x0, [x0, 8]
	movk	x1, 0x4c4b, lsl 16
	movk	x1, 0x4e4d, lsl 32
	movk	x1, 0x504f, lsl 48
	and	x0, x0, -2314885530818453537
	cmp	x0, x1
	cset	w0, eq
	ret
LFE49:
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
LSFDE73:
	.set L$set$76,LEFDE73-LASFDE73
	.long L$set$76
LASFDE73:
	.long	LASFDE73-EH_frame1
	.quad	LFB36-.
	.set L$set$77,LFE36-LFB36
	.quad L$set$77
	.uleb128 0
	.align	3
LEFDE73:
LSFDE75:
	.set L$set$78,LEFDE75-LASFDE75
	.long L$set$78
LASFDE75:
	.long	LASFDE75-EH_frame1
	.quad	LFB37-.
	.set L$set$79,LFE37-LFB37
	.quad L$set$79
	.uleb128 0
	.align	3
LEFDE75:
LSFDE77:
	.set L$set$80,LEFDE77-LASFDE77
	.long L$set$80
LASFDE77:
	.long	LASFDE77-EH_frame1
	.quad	LFB38-.
	.set L$set$81,LFE38-LFB38
	.quad L$set$81
	.uleb128 0
	.align	3
LEFDE77:
LSFDE79:
	.set L$set$82,LEFDE79-LASFDE79
	.long L$set$82
LASFDE79:
	.long	LASFDE79-EH_frame1
	.quad	LFB39-.
	.set L$set$83,LFE39-LFB39
	.quad L$set$83
	.uleb128 0
	.align	3
LEFDE79:
LSFDE81:
	.set L$set$84,LEFDE81-LASFDE81
	.long L$set$84
LASFDE81:
	.long	LASFDE81-EH_frame1
	.quad	LFB40-.
	.set L$set$85,LFE40-LFB40
	.quad L$set$85
	.uleb128 0
	.align	3
LEFDE81:
LSFDE83:
	.set L$set$86,LEFDE83-LASFDE83
	.long L$set$86
LASFDE83:
	.long	LASFDE83-EH_frame1
	.quad	LFB41-.
	.set L$set$87,LFE41-LFB41
	.quad L$set$87
	.uleb128 0
	.align	3
LEFDE83:
LSFDE85:
	.set L$set$88,LEFDE85-LASFDE85
	.long L$set$88
LASFDE85:
	.long	LASFDE85-EH_frame1
	.quad	LFB42-.
	.set L$set$89,LFE42-LFB42
	.quad L$set$89
	.uleb128 0
	.align	3
LEFDE85:
LSFDE87:
	.set L$set$90,LEFDE87-LASFDE87
	.long L$set$90
LASFDE87:
	.long	LASFDE87-EH_frame1
	.quad	LFB43-.
	.set L$set$91,LFE43-LFB43
	.quad L$set$91
	.uleb128 0
	.align	3
LEFDE87:
LSFDE89:
	.set L$set$92,LEFDE89-LASFDE89
	.long L$set$92
LASFDE89:
	.long	LASFDE89-EH_frame1
	.quad	LFB44-.
	.set L$set$93,LFE44-LFB44
	.quad L$set$93
	.uleb128 0
	.align	3
LEFDE89:
LSFDE91:
	.set L$set$94,LEFDE91-LASFDE91
	.long L$set$94
LASFDE91:
	.long	LASFDE91-EH_frame1
	.quad	LFB45-.
	.set L$set$95,LFE45-LFB45
	.quad L$set$95
	.uleb128 0
	.align	3
LEFDE91:
LSFDE93:
	.set L$set$96,LEFDE93-LASFDE93
	.long L$set$96
LASFDE93:
	.long	LASFDE93-EH_frame1
	.quad	LFB46-.
	.set L$set$97,LFE46-LFB46
	.quad L$set$97
	.uleb128 0
	.align	3
LEFDE93:
LSFDE95:
	.set L$set$98,LEFDE95-LASFDE95
	.long L$set$98
LASFDE95:
	.long	LASFDE95-EH_frame1
	.quad	LFB47-.
	.set L$set$99,LFE47-LFB47
	.quad L$set$99
	.uleb128 0
	.align	3
LEFDE95:
LSFDE97:
	.set L$set$100,LEFDE97-LASFDE97
	.long L$set$100
LASFDE97:
	.long	LASFDE97-EH_frame1
	.quad	LFB48-.
	.set L$set$101,LFE48-LFB48
	.quad L$set$101
	.uleb128 0
	.align	3
LEFDE97:
LSFDE99:
	.set L$set$102,LEFDE99-LASFDE99
	.long L$set$102
LASFDE99:
	.long	LASFDE99-EH_frame1
	.quad	LFB49-.
	.set L$set$103,LFE49-LFB49
	.quad L$set$103
	.uleb128 0
	.align	3
LEFDE99:
	.ident	"GCC: (Homebrew GCC 16.2.0) 16.2.0"
	.subsections_via_symbols
