import logging
import jinja2
from pathlib import Path
from ruamel.yaml import YAML


logger = logging.getLogger("content-test-filtering.connect_to_labels")

TEST_LABELS = "test_labels.yml"


def get_labels(content_tests):
    yaml = YAML(typ="safe")
    template_loader = jinja2.FileSystemLoader(
                        searchpath=str(Path(__file__).parent / ".."))
    template_env = jinja2.Environment(loader=template_loader)
    tests = []

    for product in content_tests.products_affected:
        yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
            product=product
        ))

        if product != "no_product":
            product_build = yaml_content["prepare_product"]
            tests.append(product_build)

        for test in content_tests.test_classes:
            if test.product == product:
                test_scenarios = test.get_tests(yaml_content)
                tests.extend(test_scenarios)

    # for product in content_tests.product_build:
    #     yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
    #         product=product.product)
    #     )
    #     build = yaml_content["prepare_product"]
    #     tests.append(build)

    # for profile in content_tests.profiles:
    #     yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
    #         product=profile.product))

    #     build = yaml_content["prepare_product"]
    #     tests.append(build)

    #     profile_test = yaml_content["profile"]
    #     profile_test = profile_test.replace("%profile_name%", profile.profile)
    #     tests.append(profile_test)
    #     # if the absolute_path is defined, check the syntax
    #     # otherwise we don't need to check the syntax (e.g. profile extends the changed one)
    #     if profile.absolute_path:
    #         yaml_test = yaml_content["yaml"]
    #         yaml_test = yaml_test.replace("%file_path%", profile.absolute_path)
    #         tests.append(yaml_test)

    # for rule in content_tests.rules:
    #     yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
    #         product=rule.product)
    #     )
    #     build = yaml_content["prepare_product"]
    #     tests.append(build)
    #     remediation_type = "rule_ansible" if rule.remediation is "ansible" else "rule_bash"
    #     rule_test_base = yaml_content[remediation_type]
    #     for rule_name in rule.rules_list:
    #         rule_test = rule_test_base.replace("%rule_name%", rule_name)
    #         tests.append(rule_test)
    #     yaml_test = yaml_content

    #list_of_tests = []
    #for struct in diff_structure:
    #    entity = struct.affected_entities
    #    yaml_content = yaml.load(template_env.get_template(TEST_LABELS).render(
    #        product=entity["product"]))
    #    file_tests = yaml_content["prepare_product"]
    #    delete_list = []
    #    for key, value in entity.items():
    #        if isinstance(value, list):
    #            with_key = [s for s in file_tests if "%"+key+"%" in s]
    #            for x in value:
    #                for y in with_key:
    #                    f = y.replace("%"+key+"%", x)
    #                    file_tests.append(f)
    #            delete_list.append(key)
    #    for item in delete_list:
    #        entity.pop(item)
    #    for x in traverse_dict(yaml_content, entity):
    #        file_tests.extend(x)

    #    list_of_tests.append(file_tests)
    
#     entities = diff_structure.affected_entities
# 
#     list_of_tests = []
#     for x in traverse_dict(yaml_content, entities):
#         list_of_tests.extend(x)
#     #traverse_dict(labels, entities, list_of_tests)

    return tests


def traverse_dict(labels, entities):
    for key in labels:
        if key in entities:
            if type(labels[key]) is dict:
                yield from traverse_dict(labels[key], entities[key])
                # list_of_tests.extend(tests)
            else:
                yield labels[key]
