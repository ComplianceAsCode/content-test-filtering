import logging
import jinja2
import yaml
from pathlib import Path


logger = logging.getLogger("content-test-filtering.connect_to_labels")

TEST_LABELS = "test_labels.yml"


def get_labels(content_tests):
    template_loader = jinja2.FileSystemLoader(
                        searchpath=str(Path(__file__).parent / ".."))
    template_env = jinja2.Environment(loader=template_loader, autoescape=True)
    tests = []

    for product in content_tests.products_affected:
        yaml_content = yaml.safe_load(template_env.get_template(TEST_LABELS).render(
            product=product
        ))

        if product != "no_product":
            product_build = yaml_content["prepare_product"]
            tests.append(product_build)

        for test in content_tests.test_classes:
            if test.product == product:
                test_scenarios = test.get_tests(yaml_content)
                tests.extend(test_scenarios)

    return tests
