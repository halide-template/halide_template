import pandas as pd

def parse_dimension_txt(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    i = 0
    model_name = ""
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('ModelName:'):
            model_name = line.split(':')[1]
            i += 1
            continue

        if line.startswith('ModelInput') or line.startswith('ModelOutput'):
            i += 1
            dim_count = int(lines[i].strip())
            i += dim_count
        elif ',' in line:
            parts = line.split(',')
            block_name, port_type, port_number = parts[0], parts[1], int(parts[2])
            i += 1
            dim_count = int(lines[i].strip())
            dim_sizes = [lines[i+j+1].strip() for j in range(dim_count)]
            formatted_dims = 'x'.join(dim_sizes)

            parent_module, subsystem = (block_name.split('/', 1) + [''])[:2]

            if subsystem == '' or '/' not in subsystem or any(x in subsystem for x in ['In', 'Out']):
                i += dim_count
                continue

            data.append({
                "Parent Module": parent_module,
                "Subsystem": subsystem,
                "Port Type": port_type,
                "Port Number": port_number,
                "Dimensions": formatted_dims
            })
            i += dim_count
        i += 1

    return data

def reshape_data(data):
    df = pd.DataFrame(data)

    def get_column_name(row):
        if row['Port Type'] == 'IN':
            return f"input{row['Port Number'] - 1}" if row['Port Number'] > 1 else "input"
        else:
            return f"output{row['Port Number'] - 1}" if row['Port Number'] > 1 else "output"

    df['Port Column'] = df.apply(get_column_name, axis=1)
    pivot_df = df.pivot_table(index=['Parent Module', 'Subsystem'],
                              columns='Port Column',
                              values='Dimensions', aggfunc='first').reset_index()

    input_cols = sorted([col for col in pivot_df.columns if 'input' in col], key=lambda x: (len(x), x))
    output_cols = sorted([col for col in pivot_df.columns if 'output' in col], key=lambda x: (len(x), x))
    cols_order = ['Parent Module', 'Subsystem'] + input_cols + output_cols
    final_df = pivot_df[cols_order]

    return final_df

def main(input_file, output_file):
    data_rows = parse_dimension_txt(input_file)
    final_df = reshape_data(data_rows)
    final_df.to_excel(output_file, index=False)
    print(f"Dimension extraction complete. Data saved to {output_file}.")

if __name__ == "__main__":
    input_filename = 'dimensions.txt'
    output_filename = 'final_output_dimensions.xlsx'
    main(input_filename, output_filename)