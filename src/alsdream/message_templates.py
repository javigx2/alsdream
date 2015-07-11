CHALLENGE_NAME = "Testing ALS2 DREAM Challenge" #"Synapse Challenge Template"

VALIDATION_TEMPLATE = """\
Hello {username},

Sorry, but we were unable to validate your submission to the """ + CHALLENGE_NAME + """ challenge.

Please refer to the challenge instructions which can be found at
http://foo.com/bar/bat and to the error message below:

submission name: {submission_name}
submission ID: {submission_id}

{message}

If you have questions, please ask on the forums at http://foo.com/fizz/buzz.

Sincerely,

the scoring script
"""

scoring_message_template = """\
Hello {username},

Your submission "{submission_name}" (ID: {submission_id}) to the """ + CHALLENGE_NAME + """ challenge has been scored:

{message}

If you have questions, please ask on the forums at http://foo.com/fizz/buzz.

Sincerely,

the scoring script
"""

scoring_error_message_template = """\
Hello {username},

Sorry, but we were unable to process your submission to the """ + CHALLENGE_NAME + """ challenge.

Please refer to the challenge instructions which can be found at
http://foo.com/bar/bat and to the error message below:

submission name: {submission_name}
submission ID: {submission_id}

{message}

If you have questions, please ask on the forums at http://foo.com/fizz/buzz.

Sincerely,

the scoring script
"""

error_notification_template = """\
Hello Challenge Administrator,

The scoring script for the """ + CHALLENGE_NAME + """ challenge encountered an error:

{message}

Sincerely,

the scoring script
"""

CHALLENGE_PROJECT_WIKI = """\
# {title}

Join button to register
${{jointeam?teamId={teamId}&showProfileForm=true&isMemberMessage=You have successfully joined the challenge&text=Join&successMessage=Invitation Accepted}}

|Launch date: ||
|Final Submission date: ||

## Challenge overview
High level summary of the Challenge including the Challenge questions and their significance

## Detailed information
Add these sections as separate wiki pages to give a full description of the challenge:
 * News
 * Data Description
 * Questions and Scoring
 * Submitting Results
 * Leaderboards
 * Computing Resources
 * Challenge Organizers

${{evalsubmit?subchallengeIdList={evalId}&unavailableMessage=Join the team to submit to the challenge}}

## Logos and graphics
 * Challenge Banner
 * DREAM/Sage logos in top left corner
 * Data Contributor institution logos
 * Challenge Funders and Sponsors logos

## Help
Link to [forum](http://support.sagebase.org/sagebase) where all questions about the Challenge should be posted.

For more information see [Creating a Challenge Space in Synapse](#!Synapse:syn2453886/wiki/).

This project was created by code in the Python edition of the [Synapse Challenge Templates](https://github.com/Sage-Bionetworks/SynapseChallengeTemplates).
"""

LEADERBOARD_MARKDOWN = """\
## {evaluation_name}

{supertable}

> A few words to explain our scoring method: it's totally random!
"""
