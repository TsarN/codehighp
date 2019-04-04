#pragma GCC optimize("Os")
#define _GNU_SOURCE

#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>

int main()
{
    unsigned int n;
    syscall(SYS_read, 0, &n, sizeof(n));
    syscall(SYS_lseek, 0, n * n * sizeof(unsigned int), SEEK_CUR);
    unsigned int b[n*n];
    syscall(SYS_read, 0, b, n * n * sizeof(unsigned int));
    for (unsigned int i = 0; i < n; ++i) {
        unsigned int a[n];
        syscall(SYS_lseek, 0, (1 + i * n) * sizeof(unsigned int), SEEK_SET);
        syscall(SYS_read, 0, a, n * sizeof(unsigned int));
        for (unsigned int j = 0; j < n; ++j) {
            unsigned int c = 0;
            for (unsigned int k = 0; k < n; ++k) {
                c += a[k] * b[k * n + j];
            }
            syscall(SYS_write, 1, &c, sizeof(unsigned int));
        }
    }
    return 0;
}
