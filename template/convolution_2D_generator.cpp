#include "Halide.h"

using namespace Halide;

class Convolution2DGenerator: public Halide::Generator<Convolution2DGenerator> {
public:
    Input<Buffer<double>> input{"input", 2};
    Input<Buffer<double>> kernel{"kernel", 2};
    Output<Buffer<double>> output{"output", 2};

    void generate() {
        Var x("x"), y("y");
        Expr zero = Expr(0.0);
        Func PadBConst_uD = BoundaryConditions::constant_exterior(input, zero);
        Func convolution("convolution");
        RDom r(0, 3, 0, 3);  

        convolution(x, y) = zero; 
	    convolution(x, y) += kernel(r.x, r.y) * PadBConst_uD(x + r.x - 1, y + r.y - 1);
        output(x, y) = convolution(x, y);
    }
    void schedule() {
        if (using_autoscheduler()) {
	    input.set_estimates({{0, 100}, {0, 100}});
        kernel.set_estimates({{0, 3}, {0, 3}});
	    output.set_estimates({{0, 102}, {0, 102}});
        } 
   }
};
HALIDE_REGISTER_GENERATOR(Convolution2DGenerator, convolution_2D)


