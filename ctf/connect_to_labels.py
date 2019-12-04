import logging
import yaml


logger = logging.getLogger("content-test-filtering.connect_to_labels")
TEST_LABELS = "test_labels.yml"


def get_labels(diff_structure):
    with open(TEST_LABELS, "r") as labels_file:
        try:
            labels = yaml.safe_load(labels_file)
        except yaml.YAMLError as e:
            print(e)

    entities = diff_structure.affected_entities

    list_of_tests = []
    for x in traverse_dict(labels, entities):
        list_of_tests.extend(x)
    #traverse_dict(labels, entities, list_of_tests)

    return list_of_tests


def traverse_dict(labels, entities):
    for key in labels:
        if key in entities:
            if type(labels[key]) is dict:
                yield from traverse_dict(labels[key], entities[key])
                # list_of_tests.extend(tests)
            else:
                yield labels[key]
