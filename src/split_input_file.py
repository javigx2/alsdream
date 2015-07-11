"""
Splits ALS Stratification challenge input file into multiple files

One file by patient
"""

import sys
import os

import alsio


if __name__ == "__main__":

    input_file = sys.argv[1]
    output_directory = sys.argv[2]

    input_data_dict = alsio.read_input_file(input_file)

    for subjectId in input_data_dict:

        ofd = open(os.path.join(output_directory, subjectId+".txt"), "w")

        for feature in input_data_dict[subjectId]:
            for line in input_data_dict[subjectId][feature]:
                ofd.write("%s\n" %line)

        ofd.close()
