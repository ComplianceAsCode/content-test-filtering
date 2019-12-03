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

    # print(diff_structure)
