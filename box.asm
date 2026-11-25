(POLL)
@KBD
D=M
@DRAW
D;JNE
@CLEAR
0;JMP

(DRAW)
@18464
D=A
@row
M=D
@20
D=A
@rows
M=D

(DRAWROW)
@row
D=M
@addr
M=D
@2
D=A
@cols
M=D

(DRAWCOL)
@addr
A=M
M=-1
@addr
M=M+1
@cols
MD=M-1
@DRAWCOL
D;JGT

@row
D=M
@32
D=D+A
@row
M=D
@rows
MD=M-1
@DRAWROW
D;JGT

@POLL
0;JMP

(CLEAR)
@18464
D=A
@row
M=D
@20
D=A
@rows
M=D

(CLEARROW)
@row
D=M
@addr
M=D
@2
D=A
@cols
M=D

(CLEARCOL)
@addr
A=M
M=0
@addr
M=M+1
@cols
MD=M-1
@CLEARCOL
D;JGT

@row
D=M
@32
D=D+A
@row
M=D
@rows
MD=M-1
@CLEARROW
D;JGT

@POLL
0;JMP