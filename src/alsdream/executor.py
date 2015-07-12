import os
import sys
import re

import time
import logging
import hashlib
import random
import tarfile

import subprocess

import shutil

import globals

import alsio


REMOVE_TEMPORAL_FILES = False

logging.basicConfig(level=logging.INFO)


class ALSExecutor():

    def __init__(self, participantId, subchallenge, selector_executable_path, predictor_executable_path):

        self.participantId=participantId
        self.selector_executable_path=selector_executable_path
        self.predictor_executable_path=predictor_executable_path

        self.subchallenge = subchallenge

        self.execution_md5 = hashlib.md5(str(str(time.time())+str(participantId)+str(random.random())).encode("utf-8")).hexdigest()
        logging.info("EXECUTION CODE: exec_%s" %self.execution_md5)

        logging.info("Reading input data...")
        self.patient_data = alsio.read_input_file(globals.COMPLETE_DATASET_FILE[subchallenge], store_subjectId=True)

        self.temporal_directory = self.create_temporal_directory()

        self.complete_dataset = alsio.read_input_file(globals.COMPLETE_DATASET_FILE[subchallenge], store_subjectId=False)
        self.features2values = {}
        self._fill_feature_2_values()

        self.start()


    def start(self):

        self.print_log_header()

        self.execute()


    def _fill_feature_2_values(self):

        for patientId in self.complete_dataset:
            for feature_name in self.complete_dataset[patientId]:
                cfeature_list = self.complete_dataset[patientId][feature_name]
                self.features2values.setdefault(feature_name.lower(),[]).append(cfeature_list)


    def format_selector_call(self, input_file_path, output_file_path,format="list"):
        """
        Return the command line to execute the selector program
        """

        arguments = [
                    "sh", 
                    self.selector_executable_path,
                    input_file_path, 
                    output_file_path
                ]

        if format=="list":
            return arguments
        elif format=="str":
            return " ".join(arguments)
        else:
            raise ValueError("format argument should be list or str")

    def format_predictor_call(self, input_file_path, output_file_path):
        """
        Return the command line command to execute the predictor program for a specific patient
        """

        return [
                    "sh",
                    self.predictor_executable_path,
                    input_file_path,
                    output_file_path
                ]

    def format_scoring_call(self, input_file, format="str"):

        args = [
                    "perl",
                    globals.SCORING_SCRIPTS_DIRECTORY+os.sep+globals.SUBCHALLENGE_SCORING_SCRIPT[self.subchallenge],
                    input_file,
                    globals.SUBCHALLENGE_GOLD_STANDARD[self.subchallenge]
                ]

        if format=="list":
            return args
        elif format=="str":
            return " ".join(args)
        else:
            raise ValueError("format argument should be list or str")

    def check_output_selector(self, filename):
        """
        Check output1 file: format and the number of selected features

        First line is: "cluster", cluster_number
        Then: feature_name, score
        """

        if not os.path.exists(filename):
            raise IOError("The selector.sh output %s is not found" %filename)

        selected_features = {}

        with open(filename, "r") as fd:

            #First line should the the cluster number
            line = fd.readline()

            if not line.lower().startswith("cluster"):
                raise ValueError("The selector output file must start with the cluster number.")

            patients_dict = alsio._parse_input_file(fd, False)
            
            if len(patients_dict)>1:
                raise ValueError("The selector output file must contain data for a single patient.")

            if len(patients_dict)==0:
                raise ValueError("The selector output file must contain data for at least a single patient.")

            for patientId in patients_dict:
                pass

            for feature_name in patients_dict[patientId]:
                selected_features[feature_name] = 1.0

        if len(selected_features) > globals.LIMIT_FEATURES:
            raise ValueError("The number of selected features is higher to the specified threshold (%s)" % (len(selected_features),
                                                                                                        globals.LIMIT_FEATURES))

        return selected_features


    def recreate_input_file2(self, subjectId, selected_features, output_filename, randomize_numbers=False):
        """
        Create a valid input file for the predictor program, containing only selected_features

        if randomize_number is True, it modifies the feature value using a random refactoring
        """

        ofd = open(output_filename, "w")
        ofd.write("patientID|form name|feature name|feature value|feature unit|feature delta\n")

        if randomize_numbers is False:
            for selected_feature in selected_features:
                if selected_feature in self.patient_data[subjectId]:
                    ofd.write("%s\n" % "|".join(self.patient_data[subjectId][selected_feature.lower()]))
        else:
            for selected_feature in selected_features:
                if selected_feature in self.patient_data[subjectId]:
                    for line in random.choice(self.features2values[selected_feature.lower()]):
                        ofd.write("%s\n" %alsio.format_input_line(subjectId=subjectId, line=line))

        ofd.close()


    def create_prediction_file(self, predictions):
        """
        Create a prediction file with all the predictions
        """

        output_filename = os.sep.join([globals.PREDICTION_DIRECTORY, "%s.pred" % self.execution_md5])

        ofd = open(output_filename, "w")
        #ofd.write("\"SubjectID\",\"status\"\n")
        if self.subchallenge.endswith("survival"):
            for subjectId, scores in iter(predictions.items()):
                ofd.write("%s,%s,%s,%s\n" % (subjectId, scores[0], scores[1], scores[2]))
        ofd.close()

        return output_filename

    def create_temporal_directory(self):
        temporal_directory = os.sep.join([globals.TEMPORAL_DIRECTORY, self.execution_md5])
        os.mkdir(temporal_directory)
        return temporal_directory


    def print_log_header(self):
        logging.info("### EXECUTION %s ###" % self.execution_md5)
        logging.info(" Code: %s" % self.execution_md5)
        logging.info(" User: %s" % self.participantId)
        logging.info(" Selector executable: %s" % self.selector_executable_path)
        logging.info(" Predictor executable: %s" % self.predictor_executable_path)

    def execute(self):

        subjectId_re = re.compile("(.+)\.txt")        

        # A specific execution for each input patient

        # First, execute selector for each subject
        for patient_input_file in os.listdir(globals.INVIDIAL_DATASET_FILES[self.subchallenge]):

            #self.patient_data = alsio.read_input_file(os.sep.join([globals.INPUT_FILE_PATH, patient_input_file]))

            subjectId = subjectId_re.search(patient_input_file).group(1)

            #print(subjectId)

            #if int(subjectId) not in set([574500,149209,80140,533771,704508]):
            #    continue

            INPUT1 = globals.INVIDIAL_DATASET_FILES[self.subchallenge]+os.sep+patient_input_file
            OUTPUT1 = os.sep.join([self.temporal_directory, "output1.%s.txt" % subjectId])

            # CREATE THE SPECIFIC ENVIRONMENT WITH unshare
            # REMOVE THE NETWORK CAPABILITIES WITH unshare -n

            # Use the Python library to interact with it?
            # https://github.com/TheTincho/python-unshare/
            #os.system(format_selector_call(selector_executable_path, INPUT1, OUTPUT1))
            os.system(self.format_selector_call(INPUT1, OUTPUT1, "str"))

            try:
                subprocess.call(self.format_selector_call(input_file_path=INPUT1,
                                                          output_file_path=OUTPUT1))
                                #timeout=globals.SELECTOR_TIMEOUT)
            except subprocess.TimeoutExpired:
                raise ValueError("The selector program took too many time to be executed")

            # Check that the number of features is correct
            selected_features = self.check_output_selector(OUTPUT1)

            # Recreate input file 2
            INPUT2 = os.sep.join([self.temporal_directory, "input2.%s.txt" % subjectId])

        # Execute the predictor program for all the subjects, N times
        for repetition in range(11):

            #print("REP: ",repetition)

            predicted_values = {}

            for patient_input_file in os.listdir(globals.INVIDIAL_DATASET_FILES[self.subchallenge]):
                
                subjectId = subjectId_re.search(patient_input_file).group(1)

                #if int(subjectId) not in set([574500,149209,80140,533771,704508]):
                #    continue

                self.recreate_input_file2(subjectId=subjectId,
                                          selected_features=selected_features,
                                          output_filename=INPUT2,
                                          randomize_numbers=repetition>0)

                INPUT2 = os.sep.join([self.temporal_directory, "input2.%s.txt" % subjectId])
                OUTPUT2 = os.sep.join([self.temporal_directory, "output2.%s.txt" % subjectId])  # Not necessary

                subprocess.call(self.format_predictor_call(INPUT2,
                                                        OUTPUT2))
                                #timeout=globals.PREDICTOR_TIMEOUT)

                try:
                    pfd = open(OUTPUT2,"r")
                    patient_predicted_values = list(map(float,pfd.read().strip().split("|")))
                    pfd.close()
                except:
                    raise ValueError("The predictor output could not be processed. Check the output format")

                if REMOVE_TEMPORAL_FILES is True:
                    os.unlink(OUTPUT2)
                    os.unlink(INPUT2)

                predicted_values[subjectId] = patient_predicted_values
            
            # PUT ALL THE PREDICTIONS INTO A SINGLE FILE
            prediction_file = self.create_prediction_file(predicted_values)

            # EXECUTE THE SCORING SCRIPT. Only once or for each execution?
            #scoring_fd = os.popen("/soft/devel/perl-5.18.1/bin/perl SCORING_SCRIPTS/DREAM10_ALS_scoring.pl %s SCORING_SCRIPTS/tests/surv_response_clinical_trial.csv.gold 2> /dev/null" % globals.PREDICTION_DIRECTORY)
            #print("/soft/devel/perl-5.18.1/bin/perl SCORING_SCRIPTS/DREAM10_ALS_scoring.pl %s SCORING_SCRIPTS/tests/surv_response_clinical_trial.csv.gold 2> /dev/null" % globals.PREDICTION_DIRECTORY)

            print(self.format_scoring_call(input_file=prediction_file))
            scoring_fd = os.popen(self.format_scoring_call(input_file=prediction_file))
    
            ci=None
            pcc=None

            for line in scoring_fd:
                m = re.search("%s\s+(\S+)\s+(\S+)\s+(\S+)" % self.execution_md5, line)
                if m:
                    ci1, ci2, ci3 = m.group(1), m.group(2), m.group(3)
                    ##logging.info(" Score CI: %s" % ci)
                    ##logging.info(" Score PCC: %s" % pcc)

            print((repetition, ci1, ci2, ci3))

        # TAR ALL FILES
        with tarfile.open(os.sep.join([globals.BACKUP_DIRECTORY, "%s.tar.gz" % self.execution_md5]), "w:gz") as tar:
            tar.add(self.temporal_directory, arcname=os.path.basename(self.temporal_directory))

        # DELETE ALL TEMPORAL FILES
        if REMOVE_TEMPORAL_FILES is True:
            shutil.rmtree(self.temporal_directory)

        return 


if __name__ == "__main__":

    ALSExecutor(participantId="123456",
                subchallenge="PROACT_survival",
                selector_executable_path="/home/javi/DREAM_ALS_FINAL/selector.sh",
                predictor_executable_path="/home/javi/DREAM_ALS_FINAL/predictor.sh")

    
    