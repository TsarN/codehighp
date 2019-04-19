#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/prctl.h>
#include <sys/time.h>
#include <sys/syscall.h>
#include <sys/resource.h>
#include <linux/seccomp.h>
#include <linux/filter.h>

#define MAX_FILE_SIZE (1 << 30)

int _SolutionMain();

static const struct sock_filter strict_filter[] = {
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof (struct seccomp_data, nr))),

    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_lseek,        14, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_mmap,         13, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_munmap,       12, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_mremap,       11, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_mprotect,     10, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_ioctl,        9, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_brk,          8, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_fstat,        7, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_close,        6, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_rt_sigreturn, 5, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_read,         4, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_write,        3, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_exit,         2, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ, SYS_exit_group,   1, 0),

    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
};

static const struct sock_fprog strict = {
    .len = (unsigned short)( sizeof strict_filter / sizeof strict_filter[0] ),
    .filter = (struct sock_filter *)strict_filter
};

static double tvsec(struct timeval tv)
{
    return 1.0 * tv.tv_sec + 1e-6 * tv.tv_usec;
}

static void setlimit(enum __rlimit_resource limit, rlim_t soft, rlim_t hard)
{
    struct rlimit lim = {
            soft,
            hard,
    };
    setrlimit(limit, &lim);
}

int main(int argc, char **argv)
{
    // Usage: ./exe <cpu limit, sec> <mem limit, bytes>
    if (argc <= 2) {
        return 64;
    }

    freopen(NULL, "rb", stdin);
    freopen(NULL, "wb", stdout);
    fclose(stderr);

    setlimit(RLIMIT_CPU, atoll(argv[1]), RLIM_INFINITY);
    setlimit(RLIMIT_AS, atoll(argv[2]) * 2, atoll(argv[2]) * 2);
    setlimit(RLIMIT_FSIZE, MAX_FILE_SIZE, MAX_FILE_SIZE);

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {
        return 64;
    }

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &strict)) {
        return 64;
    }

    int ret = _SolutionMain();

    fclose(stdout);

    return ret;
}
