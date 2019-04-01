#!/bin/sh
mkdir -p bin
gcc runner.c -o bin/runner
gcc -c wrapper.c -o bin/wrapper.o
