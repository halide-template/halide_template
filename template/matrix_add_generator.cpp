#include "Halide.h"

using namespace Halide;

class MatrixAddGenerator : public Halide::Generator<MatrixAddGenerator> {
public:
    Input<Buffer<double>> input{"input", 2};
    Input<Buffer<double>> input1{"input1", 2};
    Output<Buffer<double>> output{"output", 2};

    void generate() {
        Var i("i"), j("j");
        output(i, j) = input(i, j) + input1(i, j);
    }

    void schedule() {
        if (using_autoscheduler()) {
            input.set_estimates({{0, 100}, {0, 100}});
            input1.set_estimates({{0, 100}, {0, 100}});
            output.set_estimates({{0, 100}, {0, 100}});
        }
    }
};

HALIDE_REGISTER_GENERATOR(MatrixAddGenerator, mat_add_gen)
