import argparse
import os
import re
#input: matrix_mul.cpp matrix_multiply input1:512x512 input2:512x512 output1:512x512
def is_valid_size(size_str):
    """Check if the string is valid (format: str:MxN)"""
    return re.match(r"^\w+:\d+x\d+$", size_str) is not None

def modify_generator_file(file_path, generator_type,module_type, input1, input2, output1):
    # Analyze the input and output sizes
    global m_input2, n_input2
    input1_name, input1_size = input1.split(':')
    output1_name, output1_size = output1.split(':')
    m_input1, n_input1 = input1_size.split('x')
    m_output1, n_output1 = output1_size.split('x')
    if module_type in [1, 2, 3]:
        input2_name, input2_size = input2.split(':')
        m_input2, n_input2 = input2_size.split('x')
    # Construct the filename
    generator_file = os.path.join(file_path, f"{generator_type}_generator.cpp")
    # Read the contents of the file
    with open(generator_file, 'r') as file:
        lines = file.readlines()
    # Modify the call to set_estimates within the schedule() method
    modified_lines = []
    set_estimates_count = 0
    if module_type in [1, 2, 3]:
        for line in lines:
            if ('input' in line or 'output' in line) and 'set_estimates' in line:
                set_estimates_count += 1
                if set_estimates_count == 1:
                    line = re.sub(r'\{\d+, \d+}', f'{{0, {m_input1}}}', line, 1)
                    line = re.sub(r'\{0, \d+}}\);', f'{{0, {n_input1}}}}});', line, 1)
                elif set_estimates_count == 2:
                    line = re.sub(r'\{\d+, \d+}', f'{{0, {m_input2}}}', line, 1)
                    line = re.sub(r'\{0, \d+}}\);', f'{{0, {n_input2}}}}});', line, 1)
                elif set_estimates_count == 3:
                    line = re.sub(r'\{\d+, \d+}', f'{{0, {m_output1}}}', line, 1)
                    line = re.sub(r'\{0, \d+}}\);', f'{{0, {n_output1}}}}});', line, 1)
            if module_type == 2 and 'RDom' in line:
                line = re.sub(r'RDom i_1\(0, \d+\);', f'RDom i_1(0, {n_input1});', line)
            modified_lines.append(line)
    else:
        for line in lines:
            if ('input' in line or 'output' in line) and 'set_estimates' in line:
                set_estimates_count += 1
                if set_estimates_count == 1:
                    line = re.sub(r'\{\d+, \d+}', f'{{0, {m_input1}}}', line, 1)
                    line = re.sub(r'\{0, \d+}}\);', f'{{0, {n_input1}}}}});', line, 1)
                elif set_estimates_count == 2:
                    line = re.sub(r'\{\d+, \d+}', f'{{0, {m_output1}}}', line, 1)
                    line = re.sub(r'\{0, \d+}}\);', f'{{0, {n_output1}}}}});', line, 1)
            modified_lines.append(line)


    # write back
    with open(generator_file, 'w') as file:
        file.writelines(modified_lines)

def modify_file(module_name, file_path, module_type, input1, input2, output1):
    global new_buffer1, new_buffer2, new_buffer3, input2_name
    print(module_name,file_path,module_type,input1,input2,output1)
    # Extract module name without extension
    base_module_name = os.path.splitext(module_name)[0]
    includes = [
        '#include "HalideBuffer.h"',
        '#include "Halide.h"',
        f'#include "{base_module_name}_step_true.h"'
    ]
    using_namespace = 'using namespace Halide;'
    # Parse input and output sizes
    input1_name, input1_size = input1.split(':')
    output1_name, output1_size = output1.split(':')

    m_input1, n_input1 = input1_size.split('x')
    m_output1, n_output1 = output1_size.split('x')
    if module_type in [1, 2, 3]:
        input2_name, input2_size = input2.split(':')
        m_input2, n_input2 = input2_size.split('x')
        new_buffer2 = f"  Buffer<double> {input2_name}({base_module_name}_U.{input2_name.capitalize()},{m_input2},{n_input2});\n"
        new_buffer1 = f"  Buffer<double> {input1_name}({base_module_name}_U.{input1_name.capitalize()},{m_input1},{n_input1});\n"
        new_buffer3 = f"  Buffer<double> {output1_name}({base_module_name}_Y.{output1_name.capitalize()},{m_output1},{n_output1});\n"
    else:
        new_buffer1 = f"  Buffer<double> {input1_name}({base_module_name}_U.{input1_name.capitalize()},{m_input1},{n_input1});\n"
        new_buffer3 = f"  Buffer<double> {output1_name}({base_module_name}_Y.{output1_name.capitalize()},{m_output1},{n_output1});\n"
    # Construct new strings
    if module_type in [1, 2, 3]:
        new_call = f"  {base_module_name}_step_true({input1_name}.raw_buffer(), {input2_name}.raw_buffer(), {output1_name}.raw_buffer());\n"
    else:
        new_call = f"  {base_module_name}_step_true({input1_name}.raw_buffer(), {output1_name}.raw_buffer());\n"
    # Construct file name
    file_name = os.path.join(file_path, module_name)

    # Read file content
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # Check and add missing includes and using namespace
    includes_found = [False] * len(includes)
    using_namespace_found = False
    modified_lines = []
    for line in lines:
        stripped_line = line.strip()
        for i, include in enumerate(includes):
            if stripped_line.startswith(include):
                includes_found[i] = True
        if stripped_line == using_namespace:
            using_namespace_found = True
    for include, found in zip(includes, includes_found):
        if not found:
            modified_lines.append(include + '\n')
    if not using_namespace_found:
        modified_lines.append(using_namespace + '\n')

    # Add the modified includes and using namespace to modified_lines
    modified_lines += lines
    # Update Buffer<double>
    buffer_lines_updated = False
    if module_type in [1, 2, 3]:
        for i, line in enumerate(modified_lines):
            if f"Buffer<double> {input1_name}(" in line:
                modified_lines[i] = new_buffer1
                buffer_lines_updated = True
            elif f"Buffer<double> {input2_name}(" in line:
                modified_lines[i] = new_buffer2
                buffer_lines_updated = True
            elif f"Buffer<double> {output1_name}(" in line:
                modified_lines[i] = new_buffer3
                buffer_lines_updated = True
    else:
        for i, line in enumerate(modified_lines):
            if f"Buffer<double> {input1_name}(" in line:
                modified_lines[i] = new_buffer1
                buffer_lines_updated = True
            elif f"Buffer<double> {output1_name}(" in line:
                modified_lines[i] = new_buffer3
                buffer_lines_updated = True
    # Add copy_to_host() for CUDA (.cu) files
    if module_name.endswith('.cu'):
        new_buffer4 = "  copy_to_host();\n"
        modified_lines.append(new_buffer4)
    # Check function call
    if new_call in ''.join(modified_lines) and buffer_lines_updated:
        with open(file_name, 'w') as file:
            file.writelines(modified_lines)
        return

    # Update step function
    final_lines = []
    inside_function = False
    bracket_counter = 0
    for line in modified_lines:
        if "void " + base_module_name + "::step()" in line:
            inside_function = True
            bracket_counter = 0
            final_lines.append(line)
            final_lines.append("{\n")
            final_lines.append(new_buffer1)
            if module_type in [1, 2, 3]:
                final_lines.append(new_buffer2)
            final_lines.append(new_buffer3)
            final_lines.append(new_call)
            continue

        if inside_function:
            if "{" in line:
                bracket_counter += line.count("{")  # count of "{"
            if "}" in line:
                bracket_counter -= line.count("}")  # count of "}"

            if bracket_counter == 0:
                final_lines.append("}\n")  # Add closing "}"
                inside_function = False
        else:
            final_lines.append(line)

    # write back
    with open(file_name, 'w') as file:
        file.writelines(final_lines)

def main():
    parser = argparse.ArgumentParser(description="Modify a specific file")
    parser.add_argument("module_name", type=str, help="Module name including file type (.cpp or .cu)")
    parser.add_argument("type", type=str,
                        choices=["matrix_add", "matrix_multiply", "matrix_subtract", "matrix_transpose", "fir_filter", "gaussian_pyramid", "sobel_edge_detection", "convolution_2D"],
                        help="Operation type, format: 'matrix_multiply'")
    parser.add_argument("input1", type=str, help="First input, format: 'str:MxN'")
    parser.add_argument("input2", type=str, nargs='?', default=None, help="Second input (if needed), format: 'str:MxN'")
    parser.add_argument("output1", type=str, help="First output, format: 'str:MxN'")
    parser.add_argument("--file_path", type=str, default=".",
                        help="Path to the directory containing the file, default is current directory")

    args = parser.parse_args()

    # Validate input and output size formats
    if not is_valid_size(args.input1) or not is_valid_size(args.output1):
        print("Error: The format for input/output size is incorrect. The correct format is: 'str:MxN'.")
        return

    if args.type == "matrix_transpose":
        module_type = 0
    elif args.type == "matrix_add":
        module_type = 1
    elif args.type == "matrix_multiply":
        module_type = 2
    elif args.type == "matrix_subtract":
        module_type = 3
    elif args.type == "fir_filter":
        module_type = 4
    elif args.type == "gaussian_pyramid":
        module_type = 5
    elif args.type == "sobel_edge_detection":
        module_type = 6
    elif args.type == "convolution_2D":
        module_type = 7
    else:
        module_type = 8
    print(module_type)
    # Modify the file
    if module_type in [1, 2, 3]:
        modify_generator_file(args.file_path, args.type,module_type, args.input1, args.input2, args.output1)
        modify_file(args.module_name, args.file_path, module_type, args.input1, args.input2, args.output1)
    else:
        modify_generator_file(args.file_path, args.type,module_type, args.input1, None, args.output1)
        modify_file(args.module_name, args.file_path, module_type, args.input1, None, args.output1)

    print("File modification completed")


if __name__ == "__main__":
    main()
