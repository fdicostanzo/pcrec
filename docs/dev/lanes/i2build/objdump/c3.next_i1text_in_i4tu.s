endbr64
push   %r15
push   %r14
push   %r13
push   %r12
push   %rbp
push   %rbx
sub    $0x28,%rsp
test   %rsi,%rsi
mov    %fs:0x28,%rbp
mov    %rbp,0x18(%rsp)
mov    %rdi,%rbp
mov    %rsp,%r12
cmovne %rsi,%r12
cmpl   $0x49540302,(%rdi)
jne    <rx_next+0x1e0>
mov    0x18(%rbp),%rdi
mov    0x20(%rbp),%rax
cmp    %rax,%rdi
jb     <rx_next+0x1c0>
mov    0x10(%rbp),%rsi
mov    %rax,%r14
xor    %ecx,%ecx
xor    %r15d,%r15d
mov    $0xffffffffffffffff,%r8
lea    0x0(%rip),%r13        # <rx_next+0x64>
			e0: R_X86_64_PC32	.rodata+0x45c
lea    0x0(%rip),%r11        # <rx_next+0x6b>
			e7: R_X86_64_PC32	.rodata+0x35c
lea    0x0(%rip),%r10        # <rx_next+0x72>
			ee: R_X86_64_PC32	.rodata+0x33c
lea    0x0(%rip),%rbx        # <rx_next+0x79>
			f5: R_X86_64_PC32	.rodata+0x55c
lea    0x0(%rip),%r9        # <rx_next+0x80>
			fc: R_X86_64_PC32	.rodata+0x23c
test   %cl,%cl
cmovne %rax,%r8
test   $0x1,%r15b
jne    <rx_next+0x96>
cmp    $0xffffffffffffffff,%r8
je     <rx_next+0x198>
cmp    %rdi,%rax
jae    <rx_next+0x150>
movzbl (%rsi,%rax,1),%ecx
lea    0x1(%rax),%rdx
movzbl (%r11,%rcx,1),%ecx
add    %r15d,%ecx
mov    %ecx,%ecx
movzwl (%r10,%rcx,2),%r15d
cmp    $0x1,%r15w
jbe    <rx_next+0xf0>
cmp    $0xffff,%r15d
je     <rx_next+0x150>
cmpb   $0x0,(%rbx,%r15,1)
cmovne %rdx,%r8
cmp    $0x2,%r15d
jne    <rx_next+0x141>
cmp    %rdi,%rdx
jae    <rx_next+0x150>
movzbl 0x1(%rsi,%rax,1),%ecx
cmpb   $0x0,(%r9,%rcx,1)
jne    <rx_next+0x100>
mov    %rdx,%rax
jmp    <rx_next+0x9f>
nop
movzbl (%rbx,%r15,1),%ecx
mov    %rdx,%rax
jmp    <rx_next+0x80>
nopw   0x0(%rax,%rax,1)
lea    0x2(%rax),%rdx
cmp    %rdi,%rdx
jb     <rx_next+0x12d>
jmp    <rx_next+0x1d0>
nopl   0x0(%rax)
data16 cs nopw 0x0(%rax,%rax,1)
add    $0x1,%rdx
cmp    %rdi,%rdx
jae    <rx_next+0x1d0>
movzbl (%rsi,%rdx,1),%eax
cmpb   $0x0,(%r9,%rax,1)
jne    <rx_next+0x120>
mov    %rdx,%r8
mov    $0x2,%r15d
cmp    %rdi,%rdx
jb     <rx_next+0xea>
cs nopw 0x0(%rax,%rax,1)
cmp    $0xffffffffffffffff,%r8
je     <rx_next+0x1c0>
lea    0x1(%r14),%rax
cmp    %r8,%r14
mov    %r8,0x8(%r12)
cmovge %rax,%r8
mov    %r14,(%r12)
mov    $0x1,%eax
mov    %r8,0x20(%rbp)
mov    0x18(%rsp),%rdx
sub    %fs:0x28,%rdx
jne    <rx_next+0x1f7>
add    $0x28,%rsp
pop    %rbx
pop    %rbp
pop    %r12
pop    %r13
pop    %r14
pop    %r15
ret
nopw   0x0(%rax,%rax,1)
cmp    %rdi,%rax
jb     <rx_next+0x1a9>
jmp    <rx_next+0x1c0>
nop
add    $0x1,%rax
cmp    %rax,%rdi
je     <rx_next+0x1c0>
movzbl (%rsi,%rax,1),%edx
cmpb   $0x0,0x0(%r13,%rdx,1)
je     <rx_next+0x1a0>
mov    %rax,%r14
jmp    <rx_next+0x96>
nopl   (%rax)
movq   $0x49540303,0x0(%rbp)
xor    %eax,%eax
jmp    <rx_next+0x173>
nopl   0x0(%rax)
mov    %rdx,%r8
cmp    $0xffffffffffffffff,%r8
jne    <rx_next+0x156>
jmp    <rx_next+0x1c0>
nop
mov    %rbp,%rdi
call   <rx__enter>
test   %eax,%eax
jne    <rx_next+0x39>
xor    %eax,%eax
jmp    <rx_next+0x173>
call   <rx_next+0x1fc>
			278: R_X86_64_PLT32	__stack_chk_fail-0x4
nopl   0x0(%rax)

