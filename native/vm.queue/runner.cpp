#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <queue>
#include <functional>
#include <cstdint>
#include <cstdlib>

enum verdict {
    IE = 0,
    TL,
    RL,
    ML,
    RE,
    OK
};

const char *verdict_s[] = {
    "IE",
    "TL",
    "RL",
    "ML",
    "RE",
    "OK"
};

struct instruction {
    std::string cmd = "NOP";
    std::vector<uint8_t> args;
};

verdict v = OK;

std::unordered_map<std::string, std::function<void()>> instructions;
std::vector<instruction> program(256);
std::queue<uint8_t> q;
std::vector<uint8_t> args;
size_t timelim, memlim;
size_t timeused, memused;
uint8_t pc;

void stop() {
    fprintf(stderr, "{\"verdict\": \"%s\", \"cpu\": %zu, \"mem\": %zu, \"real\": 0, \"exitcode\": 0}\n", verdict_s[v], timeused, memused);
    exit(0);
}

void n_args(size_t n) {
    if (args.size() != n) {
        v = RE;
        stop();
    }
}

void push(uint8_t x) {
    q.push(x);
    if (memused < q.size()) {
        memused = q.size();
    }
}

uint8_t pop() {
    if (q.empty()) {
        v = RE;
        stop();
    }
    uint8_t ret = q.front();
    q.pop();
    return ret;
}

uint8_t peek() {
    if (q.empty()) {
        v = RE;
        stop();
    }
    return q.front();
}

void setup() {
    pc = 0;
    timeused = 0;
    memused = 0;

    instructions["STOP"] = [&]() {
        n_args(0);
        stop();
    };

    instructions["NOP"] = [&]() {
        n_args(0);
    };

    instructions["READ"] = [&]() {
        n_args(0);
        size_t x;
        if (!(std::cin >> x)) {
            v = RE;
            stop();
        }
        push(x);
    };

    instructions["WRITE"] = [&]() {
        n_args(0);
        std::cout << static_cast<size_t>(pop()) << std::endl;
    };

    instructions["PUSH"] = [&]() {
        n_args(1);
        push(args[0]);
    };

    instructions["POP"] = [&]() {
        n_args(0);
        push(pop());
    };

    instructions["PEEK"] = [&]() {
        n_args(0);
        push(peek());
    };

    instructions["DROP"] = [&]() {
        n_args(0);
        pop();
    };

    instructions["ADD"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        push(a + b);
    };

    instructions["SUB"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        push(a - b);
    };

    instructions["MUL"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        push(a * b);
    };

    instructions["DIV"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        if (b == 0) { v = RE; stop(); }
        push(a / b);
    };

    instructions["MOD"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        if (b == 0) { v = RE; stop(); }
        push(a % b);
    };

    instructions["AND"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        push(a & b);
    };

    instructions["OR"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        push(a | b);
    };

    instructions["XOR"] = [&]() {
        n_args(0);
        uint8_t a = pop();
        uint8_t b = pop();
        push(a ^ b);
    };

    instructions["JMP"] = [&]() {
        n_args(1);
        pc = args[0] - 1;
    };

    instructions["JL"] = [&]() {
        n_args(2);
        uint8_t x = args[0];
        uint8_t a = args[1];
        if (peek() < x) pc = a - 1;
    };

    instructions["JLE"] = [&]() {
        n_args(2);
        uint8_t x = args[0];
        uint8_t a = args[1];
        if (peek() <= x) pc = a - 1;
    };

    instructions["JG"] = [&]() {
        n_args(2);
        uint8_t x = args[0];
        uint8_t a = args[1];
        if (peek() > x) pc = a - 1;
    };

    instructions["JGE"] = [&]() {
        n_args(2);
        uint8_t x = args[0];
        uint8_t a = args[1];
        if (peek() >= x) pc = a - 1;
    };

    instructions["JE"] = [&]() {
        n_args(2);
        uint8_t x = args[0];
        uint8_t a = args[1];
        if (peek() == x) pc = a - 1;
    };

    instructions["JN"] = [&]() {
        n_args(2);
        uint8_t x = args[0];
        uint8_t a = args[1];
        if (peek() != x) pc = a - 1;
    };
}

void run() {
    while (1) {
        auto i = program[pc];
        auto it = instructions.find(i.cmd);
        if (it == instructions.end()) {
            v = RE;
            stop();
        }
        args = i.args;
        it->second();
        ++pc;
        ++timeused;

        if (timeused > timelim) {
            v = TL;
            stop();
        }

        if (memused > memlim) {
            v = ML;
            stop();
        }
    }
}

int main(int argc, char **argv) {
    if (argc <= 4) return 1;
    std::string srcpath = argv[1];
    timelim = atoi(argv[3]);
    memlim = atoi(argv[4]);
    setup();

    {
        size_t i = 0;
        std::string line;
        std::ifstream f(srcpath);
        while (std::getline(f, line) && i < 256) {
            std::stringstream ss(line);
            ss >> program[i].cmd;
            size_t arg;
            while (ss >> arg) {
                program[i].args.push_back(arg);
            }
            i++;
        }
    }
    run();
    return 0;
}
