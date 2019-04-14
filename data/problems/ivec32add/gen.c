#include "highplib.h"
#include <stdio.h>

int main()
{
    init_gen(MODE_BINARY);
    unsigned int n = atoi(getenv("N"));
    fwrite(&n, sizeof(n), 1, stdout);
    for (unsigned int i = 0; i < n / 2; ++i) {
        unsigned int x[4];
        rand_sse(x);
        fwrite(x, sizeof(x), 1, stdout);
    }
    return 0;
}
