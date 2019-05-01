# Queue Machine

Queue Machine is an experimental computing device
developed by leading British computer scientists.

## Emulator

For your convenience, emulator written in C++ is available.
C++11 support is required. [**DOWNLOAD**](https://gist.github.com/TsarN/a953c05630a9adcdd606d32b518f2f46).

## Description

Queue Machine has following components:

 - Processor
 - Memory, in the form of queue of 8-bit unsigned numbers (hence the name)
 - Program memory, which stores the program that machine executes
 - Program counter, an 8-bit register which stores index of current instruction
 - Input/output module, which allows the Machine to communicate with the outside world.

Program is a series of no more than 256 instructions.
All arithmetic is performed modulo $2^8$.
Instructions themselves will be described further down.

When the Machine turns on, it initializes program counter (PC) to 0 and
memory (Q) to an empty queue. 
Then, program is loaded into program memory and starts executing:

1. Processor loads instruction with index equal to the value stored in PC
2. Processor executes the instruction
3. If the instruction didn't write to PC, then 
   the value stored in PC is incremented by 1.
4. If the instruction was `STOP`, then program terminates, otherwise 
   go to 1.
   
## Instructions

<table>
<thead>
    <tr>
        <th>Instruction</th>
        <th>Action</th>
    </tr>
</thead>
<tbody>
    <tr>
        <td style="font-family: monospace">STOP</td>
        <td>Stops the program execution</td>
    </tr>
    <tr>
        <td style="font-family: monospace">NOP</td>
        <td>Does nothing</td>
    </tr>
    <tr>
        <td style="font-family: monospace">READ</td>
        <td style="font-family: monospace">Q.push(read())</td>
    </tr>
    <tr>
        <td style="font-family: monospace">WRITE</td>
        <td style="font-family: monospace">write(Q.pop())</td>
    </tr>
    <tr>
        <td style="font-family: monospace">PUSH $x$</td>
        <td style="font-family: monospace">Q.push($x$)</td>
    </tr>
    <tr>
        <td style="font-family: monospace">POP</td>
        <td style="font-family: monospace">Q.push(Q.pop())</td>
    </tr>
    <tr>
        <td style="font-family: monospace">PEEK</td>
        <td style="font-family: monospace">Q.push(Q.peek())</td>
    </tr>
    <tr>
        <td style="font-family: monospace">DROP</td>
        <td style="font-family: monospace">Q.pop()</td>
    </tr>
    <tr>
        <td style="font-family: monospace">ADD</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a + b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">SUB</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a - b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">MUL</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a * b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">DIV</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(floor(a / b))
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">MOD</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a % b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">AND</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a & b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">OR</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a | b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">XOR</td>
        <td style="font-family: monospace">
            a := Q.pop(); b := Q.pop();
            Q.push(a ^ b)
        </td>
    </tr>
    <tr>
        <td style="font-family: monospace">JMP $a$</td>
        <td style="font-family: monospace">PC := $a$</td>
    </tr>
    <tr>
        <td style="font-family: monospace">JL $x$ $a$</td>
        <td style="font-family: monospace">if (Q.peek() < $x$) PC := $a$</td>
    </tr>
    <tr>
        <td style="font-family: monospace">JLE $x$ $a$</td>
        <td style="font-family: monospace">if (Q.peek() &le; $x$) PC := $a$</td>
    </tr>
    <tr>
        <td style="font-family: monospace">JG $x$ $a$</td>
        <td style="font-family: monospace">if (Q.peek() > $x$) PC := $a$</td>
    </tr>
    <tr>
        <td style="font-family: monospace">JGE $x$ $a$</td>
        <td style="font-family: monospace">if (Q.peek() &ge; $x$) PC := $a$</td>
    </tr>
    <tr>
        <td style="font-family: monospace">JE $x$ $a$</td>
        <td style="font-family: monospace">if (Q.peek() = $x$) PC := $a$</td>
    </tr>
    <tr>
        <td style="font-family: monospace">JN $x$ $a$</td>
        <td style="font-family: monospace">if (Q.peek() &ne; $x$) PC := $a$</td>
    </tr>
</tbody>
</table>

Meaning of operations:

 - `Q.push(x)` pushes `x` to the back of the queue.
 - `Q.pop()` pops and returns value from the front of the queue.
   If the queue is empty, Runtime Error occurs.
 - `Q.peek()` returns value at the front of the queue.
   If the queue is empty, Runtime Error occurs.

Note, that the instructions are numbered starting from zero.
This means that a jump to $a$ jumps to the instruction stored on
$(a+1)$-th line in the source code (if lines are numbered starting from 1).

## Example solution for A+B

<pre>
READ
READ
ADD
WRITE
</pre>
