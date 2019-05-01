all: bin/runner 

bin/runner: runner.cpp | bin
	$(CXX) runner.cpp -O2 -g0 -o bin/runner

bin:
	mkdir -p bin

clean:
	rm -rf bin

.PHONY: all clean
