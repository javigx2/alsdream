import sys


def read_input_file(filename, store_subjectId=True):

    with open(filename, "r") as fd:

        return _parse_input_file(fd, store_subjectId)


def _parse_input_file(line_iterator, store_subjectId=True):
    """
    Parse the input file

    Return the input as a dictionary: { subject_id: { feature_name: content }}
    """

    input_data = {}

    for line in line_iterator:

        try:
            subject_id, form_name, feature_name, feature_value, feature_unit, feature_delta = [x.strip("\"") for x in line.strip().split("|")]

            if subject_id == "SubjectID":
                continue

            #input_data.setdefault(subject_id, {}).setdefault(feature_name.lower(), []).append(line.strip().split(","))
            if store_subjectId is True:
                input_data.setdefault(subject_id, {}).setdefault(feature_name.lower(), []).append(line.strip())
            else:
                input_data.setdefault(subject_id, {}).setdefault(feature_name.lower(), []).append("|".join(line.strip().split("|")[1:]))

        except Exception as e:
            print(e)
            sys.stderr.write(line)


    return input_data


def format_input_line(line, subjectId):

    return "%s|%s" %(subjectId, line)

