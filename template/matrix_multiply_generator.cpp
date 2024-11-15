#include "Halide.h"

using namespace Halide;

class MatrixMultiplyGenerator : public Halide::Generator<MatrixMultiplyGenerator> {
public:
    Input<Buffer<double>> input{"input", 2};  
    Input<Buffer<double>> input1{"input1", 2}; 
    Output<Buffer<double>> output{"output", 2}; 

    void generate() {
        Var i("i"), i_0("i_0");
        RDom i_1(0, 100);

        Func multiply("multiply");
        Expr zero = Expr(0.0);  
        multiply(i, i_0) = zero;
        multiply(i, i_0) += input(i, i_1) * input1(i_1, i_0);

        output(i, i_0) = multiply(i, i_0);
    }
    void schedule() {
        if (using_autoscheduler()) {
            input.set_estimates({{0, 100}, {0, 100}});
            input1.set_estimates({{0, 100}, {0, 100}});
            output.set_estimates({{0, 100}, {0, 100}});
        } 
    }
};
HALIDE_REGISTER_GENERATOR(MatrixMultiplyGenerator, mat_mul_gen)

