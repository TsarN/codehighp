#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

void solve()
{
    unsigned int n;
    fread(&n, sizeof(n), 1, stdin);
    for (unsigned int i = 0; i < n; ++i) {
        for (unsigned int j = 0; j < n; ++j) {
            unsigned int c = 0;
            for (unsigned int k = 0; k < n; ++k) {
                unsigned int a, b;
                fseek(stdin, sizeof(n) * (1 + i * n + k), SEEK_SET);
                fread(&a, sizeof(a), 1, stdin);
                fseek(stdin, sizeof(n) * (1 + n * n + k * n + j), SEEK_SET);
                fread(&b, sizeof(a), 1, stdin);
                c += a * b;
            }
            fwrite(&c, sizeof(c), 1, stdout);
        }
    }
}
