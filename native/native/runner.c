#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>
#include <signal.h>

pid_t pid;
struct rusage ru;
int rte = 0;

void alarmhandler(int dummy)
{
    rte = 1;
    kill(pid, SIGKILL);
}

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

int tv2msec(struct timeval tv) {
    return 1000 * tv.tv_sec + tv.tv_usec / 1000;
}

int main(int argc, char **argv)
{
    // Usage: ./runner <exe> <real time limit, s> <cpu time limit, ms> <mem limit, kb>
    if (argc <= 4) return 1;
    char *exe = argv[1];
    int reallim = atoi(argv[2]);
    int cpulim = atoi(argv[3]);
    int memlim = atoi(argv[4]);

    pid = fork();

    if (pid < 0) {
        fprintf(stderr, "{\"verdict\": \"IE\", \"error\": \"fork() failed: %s\"}\n", strerror(errno));
        return 1;
    }

    if (pid == 0) {
        char cpulimbuf[32];
        char memlimbuf[32];
        sprintf(cpulimbuf, "%d", (cpulim + 999) / 1000);
        sprintf(memlimbuf, "%lld", memlim * 1024);
        char* const args[4] = {exe, cpulimbuf, memlimbuf, NULL};
        execv(exe, args);
        return 0;
    }

    signal(SIGALRM, alarmhandler);
    alarm(reallim);

    int status;
    struct timeval t1, t2;
    gettimeofday(&t1, NULL);
    wait4(pid, &status, 0, &ru);
    gettimeofday(&t2, NULL);
    float rtmused;
    rtmused = (t2.tv_sec - t1.tv_sec) * 1000.0f;
    rtmused += (t2.tv_usec - t1.tv_usec) / 1000.0f;

    int exitcode = 0;
    enum verdict v = OK;

    if (rte) v = RL;

    if (WIFSIGNALED(status)) {
        if (WTERMSIG(status) == SIGXCPU) v = TL;
        exitcode = -WTERMSIG(status);
    } else if (WIFEXITED(status)) {
        exitcode = WEXITSTATUS(status);
    }

    int cpuused = tv2msec(ru.ru_utime) + tv2msec(ru.ru_stime);
    int memused = ru.ru_maxrss;
    if (cpuused > cpulim) v = TL;
    if (memused > memlim) v = ML;

    fprintf(stderr, "{\"verdict\": \"%s\", \"cpu\": %d, \"mem\": %d, \"real\": %f, \"exitcode\": %d}\n", verdict_s[v], cpuused, memused, rtmused, exitcode);

    return 0;
}
