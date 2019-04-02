all: bin/runner bin/wrapper.o

bin/runner: runner.c | bin
	$(CC) runner.c -O2 -g0 -o bin/runner

bin/wrapper.o: wrapper.c | bin
	$(CC) -c wrapper.c -O2 -g0 -o bin/wrapper.o

bin:
	mkdir -p bin

clean:
	rm -rf bin

.PHONY: all clean
