import xml.etree.ElementTree as ET
import pandas as pd
import os
import sys

"""Input: XML file"""
"""Output: Excel spreadsheet data"""
"""This script is used to extract parameters from a composite model"""

def format_dimensions(dim_str):
    if dim_str:
        # Extract numbers and convert the format
        dimensions = dim_str.strip('[]').split()
        return 'x'.join(dimensions[1:]) if len(dimensions) > 2 else None
    return None

# Get the input XML file path from command line arguments
if len(sys.argv) != 2:
    print("Usage: python script.py <XML file path>")
    sys.exit(1)

file_path = sys.argv[1].strip()

# Parse the XML file
tree = ET.parse(file_path)
root = tree.getroot()
inport_blocks = root.findall(".//block[@blocktype='Inport']")
outport_blocks = root.findall(".//block[@blocktype='Outport']")
subsystem_blocks = root.findall(".//block[@blocktype='SubSystem']")

# Extract the 'name' attribute of 'sm:blocks' element
parent_module = root.attrib['name']
print(f"Parent Module: {parent_module}")

# Process Inport blocks
inport_data = []
for index, block in enumerate(inport_blocks, start=1):
    block_info = {
        "name": block.get("name"),
        "output_dimensions": block.find("./output").get("dimensions") if block.find("./output") is not None else None,
        "connect_block": block.find(".//connect").get("block") if block.find(".//connect") is not None else None,
        "input_value": block.get("name").replace(f"{parent_module}_", '')
    }
    inport_data.append(block_info)

# Process Outport blocks
outport_data = []
for index, block in enumerate(outport_blocks, start=1):
    block_info = {
        "name": block.get("name"),
        "output_dimensions": block.find("./output").get("dimensions") if block.find("./output") is not None else None,
        "output_value": block.get("name").replace(f"{parent_module}_", '')
    }
    outport_data.append(block_info)

# Process SubSystem blocks
subsystem_data = []
for block in subsystem_blocks:
    # Extract all input connections
    input_connections = [input_conn.find("./connect").get("block") for input_conn in block.findall("./input") if input_conn.find("./connect") is not None]

    block_info = {
        "name": block.get("name"),
        "output_dimensions": block.find("./output").get("dimensions") if block.find("./output") is not None else None,
        "input_connect_blocks": input_connections
    }
    subsystem_data.append(block_info)

# Combine data and label types
combined_data = []
for item in subsystem_data:
    modified_item = dict(item)
    modified_item['type'] = 'subsystem'
    combined_data.append(modified_item)

# Add Inport data
for item in inport_data:
    modified_item = {key: item[key] for key in item if key not in ['connect_block']}
    modified_item['input_connect_blocks'] = None
    modified_item['type'] = 'inport'
    combined_data.append(modified_item)

# Add Outport data
for item in outport_data:
    modified_item = {key: item[key] for key in item}
    modified_item['input_connect_blocks'] = None
    modified_item['type'] = 'outport'
    combined_data.append(modified_item)

final_data = []

# Create a dictionary keyed by name for easy lookup
name_to_data = {item['name']: item for item in combined_data}

# Build final_data
for item in combined_data:
    new_item = {
        'name': item['name'],
        'output_dimensions': item['output_dimensions'],
        'type': item['type']
    }

    # Add input_name and output_name (if applicable)
    if 'input_value' in item:
        new_item['input_value'] = item['input_value']
    if 'output_value' in item:
        new_item['output_value'] = item['output_value']

    # Process input_dimensions
    if item.get('input_connect_blocks'):
        input_dims = []
        for block_name in item['input_connect_blocks']:
            if block_name in name_to_data:
                input_dims.append(name_to_data[block_name]['output_dimensions'])
            else:
                input_dims.append(None)
        new_item['input_dimensions'] = input_dims
    else:
        new_item['input_dimensions'] = None

    final_data.append(new_item)

# Only keep SubSystem type data
final_data = [item for item in final_data if item['type'] == 'subsystem']

# Print final_data to check results
for item in final_data:
    print("Final data item (subsystem):", item)

print('***********************************************************')

new_list = []

# Generate lists of input_name and output_name
input_names = [block.get("name").replace(f"{parent_module}_", '') for block in inport_blocks]
output_names = [block.get("name").replace(f"{parent_module}_", '') for block in outport_blocks]

# Print generated input_names and output_names to check
print("Input Names:", input_names)
print("Output Names:", output_names)

for item in final_data:
    new_item = {}

    # Set parent_module
    new_item['parent_module'] = parent_module

    # Dynamically generate input_name fields
    for idx, name in enumerate(input_names, start=1):
        new_item[f'input{idx}_name'] = name

    # Dynamically generate output_name fields
    for idx, name in enumerate(output_names, start=1):
        new_item[f'output{idx}_name'] = name

    # Set sub_module
    new_item['sub_module'] = item['name'].replace(f"{parent_module}_", '')

    # Set input1 and input2
    if item['input_dimensions']:
        new_item['input1'] = format_dimensions(item['input_dimensions'][0]) if len(item['input_dimensions']) > 0 else None
        new_item['input2'] = format_dimensions(item['input_dimensions'][1]) if len(item['input_dimensions']) > 1 else None
    else:
        new_item['input1'] = None
        new_item['input2'] = None

    # Set output
    new_item['output'] = format_dimensions(item['output_dimensions'])

    # Set module_type
    sub_module = item['name'].replace(f"{parent_module}_", '').lower()
    if 'add' in sub_module:
        new_item['module_type'] = 'matrix_add'
    elif 'mul' in sub_module or 'multiply' in sub_module:
        new_item['module_type'] = 'matrix_multiply'
    elif 'transpose' in sub_module:
        new_item['module_type'] = 'matrix_transpose'
    elif 'sub' in sub_module:
        new_item['module_type'] = 'matrix_subtract'
    elif 'convolution' in sub_module:
        new_item['module_type'] = 'convolution_2D'
    elif 'fir' in sub_module:
        new_item['module_type'] = 'fir_filter'
    elif 'gaussian' in sub_module:
        new_item['module_type'] = 'gaussian_pyramid'
    elif 'sobel' in sub_module:
        new_item['module_type'] = 'sobel_edge_detection'
    else:
        new_item['module_type'] = 'unknown'

    # Print fields being added to new_list
    # Only print input_name and output_name
    input_output_fields = {key: new_item[key] for key in new_item if 'input' in key and 'name' in key or 'output' in key and 'name' in key}
    print("Adding to new_list:", {k: v for k, v in new_item.items() if k in ['parent_module', 'sub_module']} , input_output_fields)

    # Add to new_list
    new_list.append(new_item)

# Print new_list to check results
for item in new_list:
    print("New list item:", item)

# Create DataFrame and save as Excel file
df = pd.DataFrame(new_list)

# Define the order of columns, ensuring input_name and output_name follow right after parent_module
# Get all possible input_name and output_name fields
input_name_cols = [f'input{idx}_name' for idx in range(1, len(input_names)+1)]
output_name_cols = [f'output{idx}_name' for idx in range(1, len(output_names)+1)]

# Define the order of other columns
other_cols = ['parent_module'] + input_name_cols + output_name_cols + ['sub_module', 'input1', 'input2', 'output', 'module_type']

# Rearrange DataFrame columns to the defined order
df = df[other_cols]

# Save as Excel file
output_file_path = os.path.splitext(file_path)[0] + '.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Data saved to {output_file_path}")
