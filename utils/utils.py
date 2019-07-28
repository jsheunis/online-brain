import os

# Get a list of all files present in the source directory
def get_files_in_dir(TEST_DATA_DIR):
    files = []
    for r, d, f in os.walk(TEST_DATA_DIR):
        for file in f:
            if 'fanon-0007_' in file:
                files.append(os.path.join(r, file))