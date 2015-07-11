import os
import sys
import re
import synapseclient
import synapseclient.utils as utils
from synapseclient.exceptions import *
from synapseclient import Activity
from synapseclient import Project, Folder, File
from synapseclient import Evaluation, Submission, SubmissionStatus
from synapseclient import Wiki
from synapseclient.dict_object import DictObject


class ALSStratificationChallenge(object):
	"""

	"""

	SUBMISSION_QUEUE = "ALS2 Submissions"
	

	PAGE_SIZE = 100
	BATCH_SIZE = 100


	def __init__(self):
		"""
		"""

		PAGE_SIZE = 100;
