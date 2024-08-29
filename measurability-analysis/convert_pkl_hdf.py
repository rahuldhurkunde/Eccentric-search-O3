import pandas as pd
import os
import h5py
import sys

# Function to convert .pkl file to .hdf file
def convert_pkl_to_hdf(pkl_file):
    # Load the pickle file
    try:
        data = pd.read_pickle(pkl_file)
    except Exception as e:
        print(f"Failed to load pickle file: {e}")
        return

    # Define the HDF5 file name based on the pickle file name
    hdf_file = os.path.splitext(pkl_file)[0] + '.hdf'

    try:
        with h5py.File(hdf_file, 'w') as hdf:
            if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
                data.to_hdf(hdf_file, key='data', mode='w')
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (pd.DataFrame, pd.Series)):
                        value.to_hdf(hdf_file, key=key, mode='w')
                    else:
                        hdf.create_dataset(key, data=value)
            else:
                # For any other object types, you might want to serialize them differently
                hdf.create_dataset('data', data=data)
                
        print(f"Successfully converted {pkl_file} to {hdf_file}")
    except Exception as e:
        print(f"Failed to save HDF5 file: {e}")

# Example usage
if __name__ == "__main__":
    # Replace 'file.pkl' with your actual file name
    convert_pkl_to_hdf(sys.argv[1])

