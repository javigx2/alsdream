import os


BASEDIR = "/home/javi/DREAM_TEMP/"


# Stores all the temporal files during a submission execution
TEMPORAL_DIRECTORY = BASEDIR+os.sep+"EXECUTION_FILES/"

# Directory where input files are
INPUT_FILE_PATH = "/home/javi/DREAM_ALS_FINAL/data/data/all_forms_PROACT/"

# Directory where submission predictions are stored
PREDICTION_DIRECTORY = BASEDIR+os.sep+"PREDICTIONS"

# Directory where a tar.gz file is saved storing all the files generated during the execution
BACKUP_DIRECTORY = BASEDIR+os.sep+"BACKUPS"

# Where scoring script files are stored
SCORING_SCRIPTS_DIRECTORY = BASEDIR+os.sep+"SCORING"


SUBCHALLENGE_SCORING_SCRIPT = {
								"PROACT_survival": "DREAM10_ALS_scoring_survival.pl",
								"PROACT_progression:": "",
								"registries_survival": "",
								"registries_progression": ""
								}

SUBCHALLENGE_GOLD_STANDARD = {
								"PROACT_survival": "/home/javi/DREAM_ALS_FINAL/data/data/surv_response_PROACT.txt",
								"PROACT_progression": "/home/javi/DREAM_ALS_FINAL/data/data/ALSFRS_slope_PROACT.txt",
								"registries_survival": "",
								"registries_progression": ""
								}

# Number of maximum features to limit
LIMIT_FEATURES = 6

SELECTOR_TIMEOUT = 600
PREDICTOR_TIMEOUT = 600

