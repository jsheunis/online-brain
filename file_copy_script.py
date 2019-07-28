import os
import shutil
import threading
import datetime

INITIAL_DIRECTORY = 'sample_data/'
DESTINATION_DIRECTORY = 'test_data/'

FILE_GENERATION_TIME = 4.0

# Get a list of all files present in the source directory
files = []
for r, d, f in os.walk(INITIAL_DIRECTORY):
    for file in f:
        if 'fanon-0007_' in file:
            files.append(os.path.join(r, file))

# Sort files according to their name in order to preserve order of generation
files.sort()

# Copy each file every two seconds
def copy_files():
    timer = threading.Timer(FILE_GENERATION_TIME, copy_files)
    timer.start()
    if len(files) != 0:
        file = files.pop(0)
        try:
            print("Copying file ", file, " - ", datetime.datetime.now())
            shutil.copy2(file, DESTINATION_DIRECTORY)
        except IOError as err:
            print(err)
    else:
        timer.cancel()
        print("Job finished - ", datetime.datetime.now())
        
copy_files()