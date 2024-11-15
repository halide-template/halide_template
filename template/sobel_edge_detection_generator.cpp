#include "Halide.h"

using namespace Halide;

class SobelEdgeDetectionGenerator : public Halide::Generator<SobelEdgeDetectionGenerator> {
public:
    Input<Buffer<double>> input{"input", 2};
    Input<Buffer<double>> kernel_horizontal{"kernel_horizontal", 2};
    Input<Buffer<double>> kernel_vertical{"kernel_vertical", 2};
    Output<Buffer<double>> output{"output", 2};

    void generate() {
        Var x("x"), y("y");
        Expr zero = Expr(0.0);

        // Handle borders: extend input image with zero boundary
        Func PadBConst_uD = BoundaryConditions::constant_exterior(input, zero);

        // Define two convolution functions for horizontal and vertical kernels
        Func convolution_horizontal("convolution_horizontal");
        Func convolution_vertical("convolution_vertical");
        // 3x3 kernel index
        RDom r(0, 3, 0, 3); 

        // Apply horizontal kernel
        convolution_horizontal(x, y) = zero;
        convolution_horizontal(x, y) += kernel_horizontal(r.x, r.y) * PadBConst_uD(x + r.x - 1, y + r.y - 1);

        // Apply vertical kernel
        convolution_vertical(x, y) = zero;
        convolution_vertical(x, y) += kernel_vertical(r.x, r.y) * PadBConst_uD(x + r.x - 1, y + r.y - 1);

        output(x, y) = sqrt(pow(convolution_horizontal(x, y), 2) + pow(convolution_vertical(x, y), 2));
    }

    void schedule() {
        if (using_autoscheduler()) {
            input.set_estimates({{0, 100}, {0, 100}});
            kernel_horizontal.set_estimates({{0, 3}, {0, 3}});
            kernel_vertical.set_estimates({{0, 3}, {0, 3}});
            output.set_estimates({{0, 100}, {0, 100}});
        }
    }
};

HALIDE_REGISTER_GENERATOR(SobelEdgeDetectionGenerator, sobel_edge_detection)



