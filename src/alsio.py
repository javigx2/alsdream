import sys


def read_input_file(filename):

    with open(filename, "r") as fd:

        return _parse_input_file(fd)


def _parse_input_file(line_iterator):
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
            input_data.setdefault(subject_id, {}).setdefault(feature_name.lower(), []).append(line.strip())

        except Exception as e:
            print(e)
            sys.stderr.write(line)


    return input_data