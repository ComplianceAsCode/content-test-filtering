import logging
import jinja2
from ruamel.yaml import YAML


logger = logging.getLogger("content-test-filtering.connect_to_labels")
TEST_LABELS = "test_labels.yml"


def get_labels(diff_structure):
    yaml = YAML(typ="safe")
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)

    list_of_tests = []
    for struct in diff_structure:
        entity = struct.affected_entities
        yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
            product=entity["product"]))
        file_tests = yaml_content["prepare_product"]
        delete_list = []
        for key, value in entity.items():
            if isinstance(value, list):
                with_key = [s for s in file_tests if "%"+key+"%" in s]
                for x in value:
                    for y in with_key:
                        f = y.replace("%"+key+"%", x)
                        file_tests.append(f)
                delete_list.append(key)
        for item in delete_list:
            entity.pop(item)
        for x in traverse_dict(yaml_content, entity):
            file_tests.extend(x)

        list_of_tests.append(file_tests)
    
#     entities = diff_structure.affected_entities
# 
#     list_of_tests = []
#     for x in traverse_dict(yaml_content, entities):
#         list_of_tests.extend(x)
#     #traverse_dict(labels, entities, list_of_tests)

    return list_of_tests


def traverse_dict(labels, entities):
    for key in labels:
        if key in entities:
            if type(labels[key]) is dict:
                yield from traverse_dict(labels[key], entities[key])
                # list_of_tests.extend(tests)
            else:
                yield labels[key]
