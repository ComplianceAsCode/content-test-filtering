import logging
import jinja2
from ruamel.yaml import YAML


logger = logging.getLogger("content-test-filtering.connect_to_labels")
TEST_LABELS = "test_labels.yml"


def get_labels(diff_structure):
    yaml = YAML(typ="safe")
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
        product=diff_structure.affected_entities["product"]))

    entities = diff_structure.affected_entities

    list_of_tests = []
    for x in traverse_dict(yaml_content, entities):
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
