#include "Halide.h"

using namespace Halide;

class TwoDFirFilter : public Halide::Generator<TwoDFirFilter> {
public:
    Input<Buffer<double>> input{"input", 2};
    Input<Buffer<double>> kernel{"kernel", 2};
    Output<Buffer<double>> output{"output", 2};

    void generate() {
        Var x("x"), y("y");
        Expr zero = Expr(0.0);
        Func clamped = BoundaryConditions::constant_exterior(input, 0);
        
        Func convolution("convolution");
        RDom r(0, 2, 0, 2);  
        convolution(x, y) = zero;

        convolution(x, y) += kernel(1 - r.x, 1 - r.y) * clamped(x + r.x - 1, y + r.y - 1);

        output(x, y) = convolution(x, y);
    }

    void schedule() {
        if (using_autoscheduler()) {
            input.set_estimates({{0, 100}, {0, 100}});
            kernel.set_estimates({{0, 2}, {0, 2}});
            output.set_estimates({{0, 100}, {0, 100}});
        }
    }
};

HALIDE_REGISTER_GENERATOR(TwoDFirFilter, two_d_fir_filter)


