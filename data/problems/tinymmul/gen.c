#include "highplib.h"
#include <stdio.h>

int main()
{
    init_gen(MODE_BINARY);
    unsigned int n = atoi(get_var("N"));
    fwrite(&n, sizeof(n), 1, stdout);
    for (unsigned int i = 0; i < 2 * n * n; ++i) {
        unsigned int x = rand();
        fwrite(&x, sizeof(x), 1, stdout);
    }
    return 0;
}
