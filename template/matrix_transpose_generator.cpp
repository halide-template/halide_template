#include "Halide.h"

using namespace Halide;

class MatrixTransposeGenerator : public Halide::Generator<MatrixTransposeGenerator> {
public:
    Input<Buffer<double>> input{"input", 2};
    Output<Buffer<double>> output{"output", 2};

    void generate() {
        Var i("i"), j("j");
        output(i, j) = input(j, i);
    }

    void schedule() {
        if (using_autoscheduler()) {
            input.set_estimates({{0, 100}, {0, 100}});
            output.set_estimates({{0, 100}, {0, 100}});
        }
    }
};

HALIDE_REGISTER_GENERATOR(MatrixTransposeGenerator, mat_transpose_gen)
