# Brainfuck flavor

It would be better if you read about Brainfuck somewhere on the internet.

## What should I know

Program execution time is measured in cycles. Each instruction takes
one cycle. `]` is implemented as an unconditional jump to corresponding `[`,
which then checks loop condition, consuming two cycles in total.

Memory usage of a program is the largest cell number to which the
head was pointing to plus one.

If you go left of initial cell, you're gonna get Memory Limit Exceeded,
since current cell is stored as 64-bit unsigned integer.
Each cell is an unsigned 8-bit integer.
Characters that are not valid Brainfuck commands are ignored.

## Example

This program prints "hello world":

<pre>
+[-[<<[+[--->]-[<<<]]]>>>-]>-.---.>..>.<<<<-.<+.>>>>>.>.<<.<-.
</pre>