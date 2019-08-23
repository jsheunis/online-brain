import datetime
import os
import shutil
import sys
import threading

INITIAL_DIRECTORY = 'sample_data/'
DESTINATION_DIRECTORY = 'test_data/'


def copy_files(file_list):
    """
    Copy each file
    """
    timer = threading.Timer(file_generation_time, copy_files, [file_list])
    timer.start()
    if len(file_list) != 0:
        file_to_copy = file_list.pop(0)
        try:
            print("Copying file ", file_to_copy, " - ",
                  datetime.datetime.now())
            shutil.copy2(file_to_copy, DESTINATION_DIRECTORY)
        except IOError as err:
            print(err)
    else:
        timer.cancel()
        print("Job finished - ", datetime.datetime.now())


if __name__ == '__main__':
    if len(sys.argv) == 2:

        if sys.argv[1].isdigit():
            if int(sys.argv[1]) >= 1000:
                file_generation_time = float(sys.argv[1]) / 1000
            else:
                print("Time interval must be greater than 1000 milliseconds")
                sys.exit(1)
        else:
            print("Argument must be an integer")
            sys.exit(1)
    else:
        print("Usage: python3 file_copy_script <time interval ",
              "(in milliseconds)>")
        sys.exit(1)

    # Get a list of all files present in the source directory
    files = []
    for r, d, f in os.walk(INITIAL_DIRECTORY):
        for file in f:
            if '.nii' in file and 'fanon-0007_' in file:
                files.append(os.path.join(r, file))

    # Sort files according to their name in order to preserve order of
    # generation
    files.sort()

    # Copy all files from INITIAL_DIRECTORY to DESTINATION_DIRECTORY
    copy_files(files)
