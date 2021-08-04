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
    def __init__(self, path, product, rules_list, output, remediations={"bash"}):
        super().__init__(path, product)
        self.output = output
        self.rules_list = rules_list
        self.remediations = remediations
        self.tests = None

    def get_tests(self, yaml_content):
        if self.output == "json":
            tests = self.test_json(yaml_content)
        else:
            tests = self.test_command(yaml_content)
        return tests

    def test_command(self, yaml_content):
        if self.tests is None:
            self.tests = []
        for rule in self.rules_list:
            for remediation_type in self.remediations:
                rule_test = yaml_content["rule_" + remediation_type]
                rule_test = self.translate_variable(rule_test, "%rule_name%", rule)
                self.tests.append(rule_test)
        return self.tests

    def test_json(self, yaml_content):
        rules_tests = yaml_content["json_rule"]
        rules = ", ".join('"' + rule + '"' for rule in self.rules_list)
        rules_tests = self.translate_variable(rules_tests, "%rule_name%", rules)
        for remediation_type in self.remediations:
            default_setting = '"{}": "False"'.format(remediation_type)
            new_setting = '"{}": "True"'.format(remediation_type)
            rules_tests = rules_tests.replace(default_setting, new_setting)
        import json
        rules = json.loads(rules_tests)
        self.tests = [rules]
        return self.tests

class ProfileTest(AbstractTest):
    def __init__(self, path, profile, product, output):
        super().__init__(path, product)
        self.output = output
        self.profiles_list = [profile]

    def get_tests(self, yaml_content):
        tests = []
        if self.output == "json":
            tests = self.test_json(yaml_content)
        else:
            tests = self.test_command(yaml_content)
        return tests

    def test_command(self, yaml_content):
        tests = []
        for profile_name in self.profiles_list:
            profile_test = yaml_content["profile"]
            profile = self.translate_variable(profile_test, "%profile_name%",
                                              profile_name)
            tests.append(profile)
        return tests

    def test_json(self, yaml_content):
        profiles_tests = yaml_content["json_profile"]
        profiles = ", ".join('"' + profile + '"' for profile in self.profiles_list)
        profiles_tests = self.translate_variable(profiles_tests,
                                                 "%profile_name%", profiles)
        import json
        profiles = json.loads(profiles_tests)
        tests = [profiles]
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
    def __init__(self, output="commands"):
        self.output = output
        self.products_affected = set()
        self.test_classes = []

        self.product_build = []
        self.rules = []
        self.profiles = []

    def fill_tests(self, diff_struct, only_profile=False, only_rule=False):
        remediation_types = set()
        if diff_struct.file_type == FileType.YAML:
            remediation_types.add("ansible")
        elif diff_struct.file_type == FileType.OVAL or diff_struct.file_type == FileType.JINJA:
            remediation_types.add("ansible")
            remediation_types.add("bash")
        else:
            remediation_types.add("bash")

        if only_rule:
            for product, rule in diff_struct.get_changed_rules_with_products():
                self.add_rule_test(diff_struct.absolute_path, product, rule,
                                   remediation_types)
        if only_profile:
            for product, profile in diff_struct.get_changed_profiles_with_products():
                self.add_profile_test(diff_struct.absolute_path, product, profile)
        if only_rule or only_profile:
            return

        for product, rule in diff_struct.get_changed_rules_with_products():
            self.add_rule_test(diff_struct.absolute_path, product, rule,
                               remediation_types)

        for product, profile in diff_struct.get_changed_profiles_with_products():
            self.add_profile_test(diff_struct.absolute_path, product, profile)

        if self.output == "json":
            return

        for product in diff_struct.changed_products:
            self.add_product_build(diff_struct.absolute_path, product)

        if diff_struct.funcionality_changed:
            self.add_python_test(diff_struct.absolute_path)

    def add_product_build(self, path, product):
        product_build = ProductTest(path, product)
        self.products_affected.add(product)
        self.test_classes.append(product_build)

    def add_profile_test(self, path, product, profile):
        for test_class in self.test_classes:
            if not isinstance(test_class, ProfileTest):
                continue
            if test_class.product == product:
                test_class.profiles_list.append(profile)
                return
        profile_test = ProfileTest(path, profile, product, self.output)
        self.products_affected.add(product)
        self.test_classes.append(profile_test)

    def add_rule_test(self, path, product, rule, remediation={"bash"}):
        for test_class in self.test_classes:
            if not isinstance(test_class, RulesTest):
                continue
            # Workaround to create only one JSON - use rhelX product if possible
            if test_class.product not in ["rhel9", "rhel8", "rhel7"] and \
                    product in ["rhel9", "rhel8", "rhel7"]:
                test_class.product = product
                self.products_affected.add(product)
            test_class.rules_list.append(rule)
            test_class.remediations.update(remediation)
            return
        rule_test = RulesTest(path, product, [rule], self.output, remediation)
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
