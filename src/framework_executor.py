import os
import sys
import re

import time
import logging
import hashlib
import random
import tarfile

import shutil

import globals

import alsio


INPUT_DATA = {}

logging.basicConfig(level=logging.INFO)


def format_selector_call(selector_executable_path, input_file_path, output_file_path):
    """
    Return the command line to execute the selector program
    """

    return "%s \"%s\" > \"%s\"" % (selector_executable_path, input_file_path, output_file_path)


def format_predictor_call(predictor_executable_path, input_file_path):
    """
    Return the command line command to execute the predictor program for a specific patient
    """

    return "%s \"%s\"" % (predictor_executable_path, input_file_path)


def check_output1(filename):
    """
    Check output1 file: format and the number of selected features

    The format is CSV.

    First line is: "cluster", cluster_number
    Then: feature_name, score
    """

    selected_features = {}

    with open(filename, "r") as fd:

        for line in fd:

            fields = [w.strip() for w in line.strip().split(",")]
            if fields[0].lower() == "cluster":
                cluster_number = fields[1]
            else:
                feature_name = fields[0]

                if len(fields) > 1:
                    score = float(fields[1])
                else:
                    score = None

                selected_features[feature_name] = score

    if len(selected_features) > globals.LIMIT_FEATURES:
        raise ValueError("The number of selected features is higher to the specified threshold (%s)" % (len(selected_features),
                                                                                                        globals.LIMIT_FEATURES))

    return selected_features


def recreate_input_file2(subjectId, selected_features, output_filename, randomize_numbers=False):
    """
    Create a valid input file for the predictor program, containing only selected_features

    if randomize_number is True, it modifies the feature value using a random refactoring
    """

    global INPUT_DATA

    if randomize_numbers is True:
        raise NotImplementedError("feature randomize_numbers functionality to implement")

    ofd = open(output_filename, "w")
    ofd.write("patientID|form name|feature name|feature value|feature unit|feature delta\n")

    for selected_feature in selected_features:
        if selected_feature in INPUT_DATA[subjectId]:
            ofd.write("%s\n" % "|".join(INPUT_DATA[subjectId][selected_feature.lower()]))

    ofd.close()


def create_prediction_file(predictions, output_filename):
    """
    Create a prediction file with all the predictions
    """

    ofd = open(output_filename, "w")
    ofd.write("\"SubjectID\",\"status\"\n")
    for subjectId, score in iter(predictions.items()):
        ofd.write("\"%s\",%s\n" % (subjectId, score))
    ofd.close()


def execute(user, selector_executable_path, predictor_executable_path):

    global INPUT_DATA

    subjectId_re = re.compile("(.+)\.txt")

    EXECUTION_MD5 = hashlib.md5(str(str(time.time())+str(user)+str(random.random())).encode("utf-8")).hexdigest()

    logging.info("### EXECUTION %s ###" % EXECUTION_MD5)
    logging.info(" Code: %s" % EXECUTION_MD5)
    logging.info(" User: %s" % user)
    logging.info(" Selector executable: %s" % selector_executable_path)
    logging.info(" Predictor executable: %s" % predictor_executable_path)

    temporal_directory = os.sep.join([globals.TEMPORAL_DIRECTORY, EXECUTION_MD5])

    os.mkdir(temporal_directory)

    predicted_values = {}

    # A specific execution for each input patient
    for patient_input_file in os.listdir(globals.INPUT_FILE_PATH):

        INPUT_DATA = alsio.read_input_file(os.sep.join([globals.INPUT_FILE_PATH, patient_input_file]))

        subjectId = subjectId_re.search(patient_input_file).group(1)

        INPUT1 = globals.INPUT_FILE_PATH+os.sep+patient_input_file
        OUTPUT1 = os.sep.join([temporal_directory, "output1.%s.txt" % subjectId])

        # CREATE THE SPECIFIC ENVIRONMENT WITH unshare
        # REMOVE THE NETWORK CAPABILITIES WITH unshare -n

        # Use the Python library to interact with it?
        # https://github.com/TheTincho/python-unshare/
        os.system(format_selector_call(selector_executable_path, INPUT1, OUTPUT1))

        # Check that the number of features is correct
        selected_features = check_output1(OUTPUT1)

        # Recreate input file 2
        INPUT2 = os.sep.join([temporal_directory, "input2.%s.txt" % subjectId])
        recreate_input_file2(subjectId, selected_features, INPUT2)

        # OUTPUT2 = os.sep.join([temporal_directory, "output2.%s.txt" % subjectId])  # Not necessary

        # CREATE THE SPECIFIC ENVIRONMENT WITH unshare
        # REMOVE THE NETWORK CAPABILITIES WITH unshare -n

        # Use the Python library to interact with it?
        # https://github.com/TheTincho/python-unshare/
        predicted_value = os.popen(format_predictor_call(predictor_executable_path, INPUT2)).read()

        predicted_value = float(predicted_value)

        predicted_values[subjectId] = float(predicted_value)

    # PUT ALL THE PREDICTIONS INTO A SINGLE FILE
    create_prediction_file(predicted_values, os.sep.join([globals.PREDICTION_DIRECTORY, "%s.pred" % EXECUTION_MD5]))

    # EXECUTE THE SCORING SCRIPT. Only once or for each execution?
    scoring_fd = os.popen("/soft/devel/perl-5.18.1/bin/perl SCORING_SCRIPTS/DREAM10_ALS_scoring.pl %s SCORING_SCRIPTS/tests/surv_response_clinical_trial.csv.gold 2> /dev/null" % globals.PREDICTION_DIRECTORY)

    for line in scoring_fd:
        m = re.match("%s\s+(\S+)\s+(\S+)" % EXECUTION_MD5, line)
        if m:
            ci, pcc = m.group(1), m.group(2)

    logging.info(" Score CI: %s" % ci)
    logging.info(" Score PCC: %s" % pcc)

    # TAR ALL FILES
    with tarfile.open(os.sep.join([globals.BACKUP_DIRECTORY, "%s.tar.gz" % EXECUTION_MD5]), "w:gz") as tar:
        tar.add(temporal_directory, arcname=os.path.basename(temporal_directory))

    # DELETE ALL TEMPORAL FILES
    shutil.rmtree(temporal_directory)

if __name__ == "__main__":

    # TO DO: Retrieve synapse new submissions

    execute(user="u123456",
            selector_executable_path="./selector.sh",
            predictor_executable_path="./predictor.sh")
