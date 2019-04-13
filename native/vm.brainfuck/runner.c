#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <errno.h>
#include <string.h>

#define MAX_SRC_SIZE 65536

char program[MAX_SRC_SIZE + 1];
int jump[MAX_SRC_SIZE + 1];
int timelim, memlim;
int timeused, memused;

enum verdict {
    IE = 0,
    TL,
    RL,
    ML,
    OK
};

const char *verdict_s[] = {
    "IE",
    "TL",
    "RL",
    "ML",
    "OK"
};

enum verdict v = OK;

void buildjumps(void) {
    memset(jump, -1, sizeof(jump));
    int stack[MAX_SRC_SIZE + 1];
    size_t spos = 0;
    for (char *c = program; *c; ++c) {
        if (*c == '[') {
            stack[spos++] = c - program;
        } else if (*c == ']') {
            jump[c - program] = stack[spos-1];
            jump[stack[spos-1]] = c - program;
            spos--;
        }
    }
}

void run(void) {
    size_t ma = 0; /* memory address */
    size_t pc = 0; /* program counter */
    unsigned char *mem = calloc(memlim, sizeof(unsigned char));

    while (pc <= MAX_SRC_SIZE) {
        char c = program[pc];
        if (!c) break;
        switch (c) {
            case '+': mem[ma]++; pc++; break;
            case '-': mem[ma]--; pc++; break;
            case '>': ma++; pc++; break;
            case '<': ma--; pc++; break;
            case '.': putchar(mem[ma]); pc++; break;
            case ',': mem[ma] = getchar(); pc++; break;
            case '[': if (!mem[ma]) pc = jump[pc]; pc++; break;
            case ']': pc = jump[pc]; break;
            default: pc++; break;
        }
        timeused++;
        if (timeused > timelim) {
            v = TL;
            break;
        }
        if (ma > memlim) {
            memused = memlim;
            v = ML;
            break;
        }
        if (ma > memused) memused = ma;
    }
}

int main(int argc, char **argv) {
    if (argc <= 4) return 1;
    char *srcpath = argv[1];
    timelim = atoi(argv[3]);
    memlim = atoi(argv[4]);

    FILE *f = fopen(srcpath, "rb");
    if (!f) {
        fprintf(stderr, "{\"verdict\": \"IE\", \"error\": \"fopen() failed: %s\"}\n", strerror(errno));
        return 1;
    }
    program[fread(program, 1, MAX_SRC_SIZE, f)] = '\0';
    fclose(f);

    buildjumps();
    run();
    memused++;

    fprintf(stderr, "{\"verdict\": \"%s\", \"cpu\": %d, \"mem\": %d, \"real\": 0, \"exitcode\": 0}\n", verdict_s[v], timeused, memused);
    return 0;
}
