all: bin/runner bin/wrapper.a bin/wrapper_nostdlib.a

bin/runner: runner.c | bin
	$(CC) runner.c -O2 -g0 -o bin/runner

bin/wrapper.o: wrapper.c | bin
	$(CC) -c wrapper.c -O2 -g0 -o bin/wrapper.o

bin/wrapper_nostdlib.o: wrapper_nostdlib.c | bin
	$(CC) -c wrapper_nostdlib.c -O2 -g0 -o bin/wrapper_nostdlib.o

bin/syscall.o: syscall.S | bin
	$(CC) -c syscall.S -o bin/syscall.o

bin/wrapper_nostdlib.a: bin/wrapper_nostdlib.o bin/syscall.o
	$(AR) rcs bin/wrapper_nostdlib.a bin/wrapper_nostdlib.o bin/syscall.o

bin/wrapper.a: bin/wrapper.o
	$(AR) rcs bin/wrapper.a bin/wrapper.o

bin:
	mkdir -p bin

clean:
	rm -rf bin

.PHONY: all clean
