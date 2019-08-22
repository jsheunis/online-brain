import datetime
import os
import shutil
import sys
import threading

INITIAL_DIRECTORY = 'sample_data/'
DESTINATION_DIRECTORY = 'test_data/'


class MRIFileSimulator(object):
    source_dir = 'sample_data/'
    destination_dir = 'test_data/'

    def __init__(self, repetition_time, num_of_volumes):
        self.file_generation_time = float(repetition_time) / 1000
        self.num_of_volumes = num_of_volumes
        self.timer = None

    def copy_files(self, file_list):
        """
        Copy each file
        """
        self.timer = threading.Timer(self.file_generation_time,
                                     self.copy_files,
                                     [file_list])
        self.timer.start()
        if len(file_list) != 0:
            file_to_copy = file_list.pop(0)
            try:
                print("Copying file ", file_to_copy, " - ",
                      datetime.datetime.now())
                shutil.copy2(file_to_copy, self.destination_dir)
            except IOError as err:
                print(err)
        else:
            self.stop()
            print("Job finished - ", datetime.datetime.now())

    def run(self):
        # Get a list of all files present in the source directory
        files = []
        for r, d, f in os.walk(self.source_dir):
            for file in f:
                if '.nii' in file and 'fanon-0007_' in file:
                    files.append(os.path.join(r, file))

        # Sort files according to their name in order to preserve order of
        # generation
        files.sort()

        # Get only the first 'num_of_volumes' files
        files = files[:self.num_of_volumes]

        # Copy all files to DESTINATION_DIRECTORY
        self.copy_files(files)

    def stop(self):
        self.timer.cancel()

    @classmethod
    def set_source_directory(cls, source_directory):
        cls.source_dir = source_directory

    @classmethod
    def set_destination_directory(cls, destination_directory):
        cls.destination_dir = destination_directory

