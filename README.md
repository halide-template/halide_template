### Halide Generator Templates
This folder primarily contains Halide generator templates for compute-intensive algorithms, including matrix multiplication, matrix addition, convolution, and Gaussian pyramids. These templates are parameterized by inputs and outputs to accommodate changes in hardware as well as input and output sizes.

### XML Examples and Scripts
This folder also includes two examples of XML files along with several scripts that serve different purposes:

- `get_single_xml_data.py` and `get_xml_data.py`: These scripts are used for extracting parameters from single and composite models, respectively. The extracted data is outputted into an Excel spreadsheet.

- `main.py`: This script modifies the main file generated by Simulink Coder, making necessary adjustments based on specific requirements.

- `single_module.py`: This script is designed to modify Simulink Coder function files and Halide generator templates. It automatically updates these elements based on the parameters obtained, ensuring that changes are applied consistently and accurately.

- `extractDimension.m` and `extractSignalDimension.m`: These scripts are used to extract data from Simulink models and output it in TXT file format. extractDimension.m is a script for mixed models, while extractSignalDimension.m is for single models. For example, to extract data from matrix_mul.slx, the extractSignalDimension.m script should be used with matrix_mul as the input parameter. The output will be saved as dimension.txt. Similarly, to extract data from matrix_mul_transpose.slx, the extractDimension.m script should be used with matrix_mul_transpose as the input parameter, and the output will also be saved as dimension.txt.

- `get_single_txt_data.py` and `get_txt_data.py`: These scripts are used for extracting parameters from single and composite models from TXT file, respectively. The extracted data is outputted into an Excel spreadsheet. When the Simulink model contains only a single module, the get_single_txt_data.py script should be used. When the model consists of multiple modules, the get_txt_data.py script should be used. By default, the input parameter is dimension.txt, and the output file is final_output_dimension.xlsx.
d
