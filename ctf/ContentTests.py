import logging
from abc import abstractmethod
from ctf.constants import FileType

logger = logging.getLogger("content-test-filtering.ContentTests")


class AbstractTest:
    def __init__(self, path, product):
        self.absolute_path = path
        self.product = product

    @abstractmethod
    def get_tests(self, yaml_content):
        pass

    def translate_variable(self, replacement, placeholder, value):
        replaced = replacement.replace(placeholder, value)
        return replaced


class PythonTest(AbstractTest):
    def __init__(self, path, product):
        super().__init__(path, product)

    def get_tests(self, yaml_content):
        tests = []

        test_build = yaml_content["ctest_build"]
        tests.append(test_build)

        return tests


class ProductTest(AbstractTest):
    def __init__(self, path, product):
        super().__init__(path, product)

    def get_tests(self, yaml_content):
        return []


class RulesTest(AbstractTest):
    def __init__(self, path, product, rules_list, remediation="bash"):
        super().__init__(path, product)
        self.rules_list = rules_list
        self.remediation = remediation

    def get_tests(self, yaml_content):
        tests = []

        rule = yaml_content["rule_" + self.remediation]
        for r in self.rules_list:
            rule = self.translate_variable(rule, "%rule_name%", r)
            tests.append(rule)

        return tests


class ProfileTest(AbstractTest):
    def __init__(self, path, profile, product):
        super().__init__(path, product)
        self.profile = profile

    def get_tests(self, yaml_content):
        tests = []

        profile = yaml_content["profile"]
        profile = self.translate_variable(profile, "%profile_name%", self.profile)
        tests.append(profile)

        return tests


class LintTest(AbstractTest):
    TYPES = {
        FileType.NONE: "",
        FileType.PROFILE: "yamllint",
        FileType.PYTHON: "python",
        FileType.YAML: "yaml",
        FileType.BASH: "shell",
        FileType.OVAL: "oval",
        FileType.JINJA: "jinjalint"
    }

    def __init__(self, path, file_type):
        super().__init__(path, None)
        self.path = path
        self.type = self.TYPES[file_type]

    def get_tests(self, yaml_content):
        if self.type == FileType.NONE:
            return []
        tests = []

        analyzer = yaml_content[self.type]
        analyzer = self.translate_variable(analyzer, "%file_path%", self.path)
        tests.append(analyzer)

        return tests


class ContentTests:
    def __init__(self):
        self.products_affected = set()
        self.test_classes = []

        self.product_build = []
        self.rules = []
        self.profiles = []

    def fill_tests(self, diff_struct):
        remediation_types = set()
        if diff_struct.file_type == FileType.YAML:
            remediation_types.add("ansible")
        elif diff_struct.file_type == FileType.OVAL or diff_struct.file_type == FileType.JINJA:
            remediation_types.add("ansible")
            remediation_types.add("bash")
        else:
            remediation_types.add("bash")

        for product, rule in diff_struct.get_changed_rules_with_products():
            self.add_rule_test(diff_struct.absolute_path, product, rule,
                               remediation_type)

        for product, profile in diff_struct.get_changed_profiles_with_products():
            self.add_profile_test(diff_struct.absolute_path, product, profile)

        if diff_struct.funcionality_changed:
            self.add_python_test(diff_struct.absolute_path)

    def add_product_build(self, path, product):
        product_build = ProductTest(path, product)
        self.products_affected.add(product)
        self.test_classes.append(product_build)

    def add_profile_test(self, path, product, profile):
        profile_test = ProfileTest(path, profile, product)
        self.products_affected.add(product)
        self.test_classes.append(profile_test)

    def add_rule_test(self, path, product, rule, remediation="bash"):
        rule_test = RulesTest(path, product, [rule], remediation)
        self.products_affected.add(product)
        self.test_classes.append(rule_test)

    def add_rules_test(self, path, product, rules_list, remediation="bash"):
        rules_test = RulesTest(path, product, rules_list, remediation)
        self.products_affected.add(product)
        self.test_classes.append(rules_test)

    def add_python_test(self, path):
        product = "no_product"
        python_test = PythonTest(path, product)
        self.products_affected.add(product)
        self.test_classes.append(python_test)

    def get_product(self):
        for profile in self.profiles:
            yield profile.product
