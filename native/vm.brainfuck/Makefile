all: bin/runner 

bin/runner: runner.c | bin
	$(CC) runner.c -O2 -g0 -o bin/runner

bin:
	mkdir -p bin

clean:
	rm -rf bin

.PHONY: all clean
