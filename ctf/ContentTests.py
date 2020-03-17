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

        profile = yaml_content["profile"]
        profile = self.translate_variable(profile, "%profile_name%", "ospp")
        tests.append(profile)

        rule = yaml_content["rule_bash"]
        rule = self.translate_variable(rule, "%rule_name%", "some_rule")
        tests.append(rule)

        return tests


class ProductTest(AbstractTest):
    def __init__(self, path, product):
        super().__init__(path, product)


    def get_tests(self, yaml_content):
        return []


class RulesTest(AbstractTest):
    def __init__(self, path, profile, product, rules_list, remediation="bash"):
        super().__init__(path, product)
        self.profile = profile
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
        if hasattr(diff_struct, "product") and diff_struct.product:
            self.add_product_build(diff_struct.absolute_path, diff_struct.product)
            if hasattr(diff_struct, "rule") and diff_struct.rule:
                if diff_struct.file_type == FileType.BASH:
                    remediation_type = "bash"
                elif diff_struct.file_type == FileType.YAML:
                    remediation_type = "ansible"
                self.add_rules_test(diff_struct.absolute_path, diff_struct.profile,
                                    diff_struct.product, [diff_struct.rule], remediation_type)
            if hasattr(diff_struct, "other_affected_files") and diff_struct.other_affected_files:
                self.add_rules_test(diff_struct.absolute_path, diff_struct.profile,
                                    diff_struct.product, diff_struct.other_affected_files)
            if hasattr(diff_struct, "profile") and diff_struct.profile:
                self.add_profile_test(diff_struct.absolute_path, diff_struct.profile,
                                      diff_struct.product)
            if hasattr(diff_struct, "extended_profiles") and diff_struct.extended_profiles:
                for extended in diff_struct.extended_profiles:
                    self.add_profile_test(None, extended, diff_struct.product)
            if hasattr(diff_struct, "added_rules") and diff_struct.added_rules:
                self.add_rules_test(diff_struct.absolute_path, diff_struct.profile,
                                    diff_struct.product, diff_struct.added_rules)
        if hasattr(diff_struct, "sanity") and diff_struct.sanity:
            self.add_python_test(diff_struct.absolute_path)


    def add_product_build(self, path, product):
        product_build = ProductTest(path, product)
        self.products_affected.add(product)
        self.test_classes.append(product_build)


    def add_profile_test(self, path, profile, product):
        profile_test = ProfileTest(path, profile, product)
        self.products_affected.add(product)
        self.test_classes.append(profile_test)


    def add_rules_test(self, path, profile, product, rules_list, remediation="bash"):
        rules_test = RulesTest(path, profile, product, rules_list, remediation)
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
