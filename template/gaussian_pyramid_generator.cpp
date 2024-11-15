#include "Halide.h"

using namespace Halide;

class GaussianPyramidGenerator: public Halide::Generator<GaussianPyramidGenerator> {
public:
    Input<Buffer<double>> input{"input", 2};
    Input<Buffer<double>> kernel{"kernel", 1};
    Output<Buffer<double>> output{"output", 2};

    void generate() {
        Var x("x"), y("y");
        Func clamped = BoundaryConditions::mirror_image(input);
        Expr zero = Expr(0.0);

        Func blur_y("blur_y");
        RDom ry(-2, 5);
        blur_y(x, y) = zero;
	blur_y(x, y) += kernel(ry + 2) * clamped(x, y + ry);

        Func blur_x("blur_x");
        RDom rx(-2, 5);
        blur_x(x, y) = zero;
        blur_x(x, y) += kernel(rx + 2) * blur_y(x + rx, y);

        Func downsample("downsample");
        downsample(x, y) = blur_x(2 * x, 2 * y);
        output(x, y) = downsample(x, y);
    }
    void schedule() {
        if (using_autoscheduler()) {
	    input.set_estimates({{0, 100}, {0, 100}});
        kernel.set_estimates({{0, 5}});
	    output.set_estimates({{0, 50}, {0, 50}});
        } 
   }
};
HALIDE_REGISTER_GENERATOR(GaussianPyramidGenerator, gaussian_pyramid_gen)


